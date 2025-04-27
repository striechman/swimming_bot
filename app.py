from fastapi import FastAPI, Request
import openai
import os
import gspread
import json
from google.oauth2.service_account import Credentials
from twilio.rest import Client
from datetime import datetime

# סוכנים
from manager import route_message_to_agent
from agents.beri_agent import beri_generate_response
from agents.michal_agent import michal_generate_response, michal_send_water_reminder, michal_log_water_intake
from agents.michal import (
    michal_daily_nutrition_tip,
    michal_request_water_and_food,
    michal_weekly_summary
)
from agents.roni_agent import roni_generate_response


app = FastAPI()

# קריאת משתנים מהסביבה
twilio_client = Client(os.getenv('TWILIO_SID'), os.getenv('TWILIO_TOKEN'))
from_whatsapp = os.getenv('TWILIO_FROM')
to_whatsapp = os.getenv('TWILIO_TO')
openai.api_key = os.getenv('OPENAI_API_KEY')

# התחברות ל-Google Sheets
def get_sheet():
    credentials_info = json.loads(os.getenv('GOOGLE_CREDENTIALS_JSON'))
    creds = Credentials.from_service_account_info(credentials_info)
    gc = gspread.authorize(creds)
    sheet = gc.open_by_key(os.getenv('SHEET_ID')).sheet1
    return sheet

# שליחת הודעה בוואטסאפ
def send_whatsapp(message):
    twilio_client.messages.create(body=message, from_=from_whatsapp, to=to_whatsapp)

# --- נתיבים (Routes) ---

# מסלול לברִי
@app.post("/beri")
async def chat_with_beri(request: Request):
    form = await request.form()
    user_message = form.get('Body', '')
    if not user_message:
        return {"error": "No message received"}

    reply = beri_generate_response(user_message)
    send_whatsapp(reply)
    return {"reply": reply}

# מסלול למיכל
@app.post("/michal")
async def chat_with_michal(request: Request):
    form = await request.form()
    user_message = form.get('Body', '')
    if not user_message:
        return {"error": "No message received"}

    if "שתיתי" in user_message or "שתיתי מים" in user_message:
        michal_log_water_intake(user_message)
        return {"reply": "מים עודכנו בגליון!"}
    
    reply = michal_generate_response(user_message)
    send_whatsapp(reply)
    return {"reply": reply}

# מסלול לרוני (בהמשך נוסיף רוני)
@app.post("/roni")
async def chat_with_roni(request: Request):
    form = await request.form()
    user_message = form.get('Body', '')
    if not user_message:
        return {"error": "No message received"}

    reply = roni_generate_response(user_message)
    send_whatsapp(reply)
    return {"reply": reply}

# קבלת הודעות כלליות מוואטסאפ
@app.post("/wa")
async def receive_whatsapp(request: Request):
    form = await request.form()
    body = form.get('Body', '').strip()

    if not body:
        return {"error": "Empty message received"}

    body_lower = body.lower()

    if "ברי" in body_lower:
        clean_msg = body.replace("ברי", "").strip()
        reply = beri_generate_response(clean_msg)
    elif "מיכל" in body_lower:
        clean_msg = body.replace("מיכל", "").strip()
        reply = michal_generate_response(clean_msg)
    elif "רוני" in body_lower:
        clean_msg = body.replace("רוני", "").strip()
        reply = roni_generate_response(clean_msg)
    else:
        reply = "בבקשה תתייג את אחד הסוכנים: ברי, מיכל או רוני."

    send_whatsapp(reply)
    return {"reply": reply}

# דחיפת בוקר
@app.get("/push/morning")
async def push_morning():
    sheet = get_sheet()
    today = datetime.now().strftime("%d/%m/%Y")
    sheet.append_row([today, "שחייה קלה", "", "תפריט יומי", "", "", ""])
    reply = beri_generate_response("תכתוב לי הודעת בוקר עם תוכנית אימון מפורטת להיום.")
    send_whatsapp(reply)
    return {"status": "morning push sent"}

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
    return {"status": "night feedback sent"}

# שליחת טיפ יומי ממיכל
@app.get("/push/michal-tip")
async def send_michal_tip():
    michal_daily_nutrition_tip()
    return {"status": "daily nutrition tip sent"}

# בקשת עדכון שתייה ואוכל ממיכל
@app.get("/push/michal-request")
async def send_michal_request():
    michal_request_water_and_food()
    return {"status": "water and food request sent"}

# סיכום שבועי ממיכל
@app.get("/push/michal-summary")
async def send_michal_summary():
    michal_weekly_summary()
    return {"status": "weekly summary request sent"}

from apscheduler.schedulers.background import BackgroundScheduler

# תזמון של משימות
scheduler = BackgroundScheduler()

# תזמון שליחת אימון בוקר מברי
from agents.beri_agent import beri_generate_response
from utils.whatsapp import send_whatsapp

def send_morning_training():
    message = beri_generate_response("תכתוב לי הודעת בוקר עם תוכנית אימון מפורטת להיום.")
    send_whatsapp(message)

# תזמון שליחת תזכורת מים ממיכל
from agents.michal_agent import michal_send_water_reminder

def send_water_reminder():
    michal_send_water_reminder()

# תזמון שליחת תרגול נשימה מרוני
from agents.roni_agent import roni_send_mindfulness_exercise

def send_mindfulness_exercise():
    roni_send_mindfulness_exercise()

# הגדרת התזמונים
scheduler.add_job(send_morning_training, 'cron', hour=7, minute=0)     # כל יום ב-07:00 בבוקר
scheduler.add_job(send_water_reminder, 'cron', hour=10, minute=0)       # כל יום ב-10:00 בבוקר
scheduler.add_job(send_water_reminder, 'cron', hour=13, minute=0)       # כל יום ב-13:00 בצהריים
scheduler.add_job(send_water_reminder, 'cron', hour=16, minute=0)       # כל יום ב-16:00
scheduler.add_job(send_mindfulness_exercise, 'cron', hour=21, minute=0) # כל יום ב-21:00 בערב

# להתחיל את הסקדולר
scheduler.start()
