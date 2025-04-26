import os
import json
import openai
import gspread
from fastapi import FastAPI, Request
from google.oauth2.service_account import Credentials
from twilio.rest import Client
from datetime import datetime

app = FastAPI()

# Load credentials directly from environment variable
google_creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
if google_creds_json is None:
    raise Exception("GOOGLE_CREDENTIALS_JSON environment variable not set")
credentials_info = json.loads(google_creds_json)
creds = Credentials.from_service_account_info(credentials_info)

gc = gspread.authorize(creds)
sh = gc.open('FitnessTracker').sheet1

# Twilio setup
twilio_client = Client(os.getenv('TWILIO_SID'), os.getenv('TWILIO_TOKEN'))
from_whatsapp = os.getenv('TWILIO_FROM')
to_whatsapp = os.getenv('TWILIO_TO')

openai.api_key = os.getenv('OPENAI_API_KEY')

def send_whatsapp(message):
    twilio_client.messages.create(body=message, from_=from_whatsapp, to=to_whatsapp)

@app.get("/push/morning")
async def push_morning():
    today = datetime.now().strftime("%d/%m/%Y")
    sh.append_row([today, "שחייה קלה", "", "תפריט יומי", "", "", ""])
    send_whatsapp("🌅 בוקר טוב! היום: שחייה קלה. תזונה: שייק חלבון אחרי אימון.")
    return {"status": "morning push sent"}

@app.get("/push/night")
async def push_night():
    today = datetime.now().strftime("%d/%m/%Y")
    cells = sh.findall(today)
    if not cells:
        return {"error": "No row for today"}
    row = cells[0].row
    vals = sh.row_values(row)

    prompt = f"""
    המשתמש ביצע אימון: {vals[2]}.
    תזונה: {vals[4]}.
    שתה {vals[5]} ליטר מים.
    תן לו פידבק חיובי קצר בעברית עם טיפ אחד לשיפור מחר.
    """
    res = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    feedback = res['choices'][0]['message']['content'].strip()
    sh.update_cell(row, 7, feedback)
    send_whatsapp(feedback)
    return {"status": "night feedback sent"}

@app.post("/wa")
async def receive_whatsapp(request: Request):
    form = await request.form()
    body = form.get('Body').strip()

    today = datetime.now().strftime("%d/%m/%Y")
    cells = sh.findall(today)
    if not cells:
        sh.append_row([today, "שחייה קלה", "", "תפריט יומי", "", "", ""])
        row = cells[0].row
    else:
        row = cells[0].row

    if body.startswith("אימון"):
        sh.update_cell(row, 3, body[6:])
        send_whatsapp("✔️ עודכן! איך הייתה הארוחה?")
    elif body.startswith("אכלתי"):
        sh.update_cell(row, 5, body[7:])
        send_whatsapp("🥤 כמה ליטר מים שתית היום?")
    elif body.replace(".", "").isdigit():
        sh.update_cell(row, 6, body)
        send_whatsapp("מעולה! נדבר בערב עם פידבק 🙌")
    return {"status": "ok"}
