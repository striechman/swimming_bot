from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Request
import openai
import os
import gspread
import json
from google.oauth2.service_account import Credentials


# ייבוא סוכנים ומנהל
from manager import route_message_to_agent
from agents.beri_agent import beri_generate_response
from agents.michal_agent import (
    michal_generate_response,
    michal_send_water_reminder,
    michal_log_water_intake,
    michal_daily_nutrition_tip,
    michal_request_water_and_food
)
from agents.roni_agent import (
    roni_generate_response,
    roni_send_mindfulness_exercise
)

# שליחת וואטסאפ
from utils.whatsapp import send_whatsapp

# ---- התחלה ----

app = FastAPI()

openai.api_key = os.getenv('OPENAI_API_KEY')

def get_sheet():
with open(os.getenv('GOOGLE_CREDENTIALS_JSON_PATH')) as f:
    credentials_info = json.load(f)
    creds = Credentials.from_service_account_info(credentials_info)
    gc = gspread.authorize(creds)
    return gc.open_by_key(os.getenv('SHEET_ID')).sheet1


# ---- מסלולים ----

@app.post("/wa")
async def receive_whatsapp(request: Request):
    form = await request.form()
    body = form.get('Body', '').strip()

    if not body:
        return {"error": "Empty message received"}

    reply = route_message_to_agent(body)
    send_whatsapp(reply)
    return {"reply": reply}

@app.post("/beri")
async def chat_with_beri(request: Request):
    form = await request.form()
    user_message = form.get('Body', '')
    if not user_message:
        return {"error": "No message received"}
    reply = beri_generate_response(user_message)
    send_whatsapp(reply)
    return {"reply": reply}

@app.post("/michal")
async def chat_with_michal(request: Request):
    form = await request.form()
    user_message = form.get('Body', '')
    if not user_message:
        return {"error": "No message received"}
    
    if "שתיתי" in user_message:
        michal_log_water_intake(user_message)
        send_whatsapp("מעולה! עדכנתי את כמות השתייה שלך 💧")
        return {"reply": "Water intake updated!"}

    reply = michal_generate_response(user_message)
    send_whatsapp(reply)
    return {"reply": reply}

@app.post("/roni")
async def chat_with_roni(request: Request):
    form = await request.form()
    user_message = form.get('Body', '')
    if not user_message:
        return {"error": "No message received"}
    reply = roni_generate_response(user_message)
    send_whatsapp(reply)
    return {"reply": reply}
@app.get("/push/roni-exercise")
async def send_roni_exercise():
    roni_send_mindfulness_exercise()
    return {"status": "Mindfulness exercise sent"}


# דחיפת בוקר
@app.get("/push/morning")
async def push_morning():
    sheet = get_sheet()
    today = datetime.now().strftime("%d/%m/%Y")
    sheet.append_row([today, "שחייה קלה", "", "תפריט יומי", "", "", ""])
    message = beri_generate_response("תכתוב לי הודעת בוקר עם תוכנית אימון מפורטת להיום.")
    send_whatsapp(message)
    return {"status": "Morning push sent"}

# דחיפת ערב
@app.get("/push/night")
async def push_night():
    sheet = get_sheet()
    today = datetime.now().strftime("%d/%m/%Y")
    cells = sheet.findall(today)
    if not cells:
        return {"error": "No row for today"}
    row = cells[0].row
    vals = sheet.row_values(row)

    prompt = f"""
    סכם את האימון של ערן:
    אימון: {vals[2]}
    תזונה: {vals[4]}
    מים: {vals[5]} ליטר
    תן לו פידבק בעברית, מקצועי, חברי ומוטיבציוני.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    feedback = response['choices'][0]['message']['content'].strip()
    sheet.update_cell(row, 7, feedback)
    send_whatsapp(feedback)
    return {"status": "Night push sent"}

# טיפ יומי ממיכל
@app.get("/push/michal-tip")
async def send_michal_tip():
    michal_daily_nutrition_tip()
    return {"status": "Daily nutrition tip sent"}

# בקשת עדכון שתייה ואוכל ממיכל
@app.get("/push/michal-request")
async def send_michal_request():
    michal_request_water_and_food()
    return {"status": "Water and food request sent"}

# ---- תזמונים ----

scheduler = BackgroundScheduler()

def schedule_jobs():
    scheduler.add_job(lambda: send_whatsapp(beri_generate_response("תכתוב לי הודעת בוקר עם תוכנית אימון מפורטת להיום.")), 'cron', hour=7, minute=0)
    scheduler.add_job(michal_send_water_reminder, 'cron', hour=10, minute=0)
    scheduler.add_job(michal_send_water_reminder, 'cron', hour=13, minute=0)
    scheduler.add_job(michal_send_water_reminder, 'cron', hour=16, minute=0)
    scheduler.add_job(roni_send_mindfulness_exercise, 'cron', hour=21, minute=0)
    scheduler.start()

schedule_jobs()
