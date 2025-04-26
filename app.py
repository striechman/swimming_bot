from fastapi import FastAPI, Request
import openai
import os
import gspread
import json
from google.oauth2.service_account import Credentials
from twilio.rest import Client
from datetime import datetime

app = FastAPI()

# Twilio setup
twilio_client = Client(os.getenv('TWILIO_SID'), os.getenv('TWILIO_TOKEN'))
from_whatsapp = os.getenv('TWILIO_FROM')
to_whatsapp = os.getenv('TWILIO_TO')

openai.api_key = os.getenv('OPENAI_API_KEY')

def get_sheet():
    credentials_info = json.loads(os.getenv('GOOGLE_CREDENTIALS_JSON'))
    creds = Credentials.from_service_account_info(credentials_info)
    gc = gspread.authorize(creds)
    sheet = gc.open('FitnessTracker').sheet1
    return sheet

def send_whatsapp(message):
    twilio_client.messages.create(body=message, from_=from_whatsapp, to=to_whatsapp)

@app.get("/push/morning")
async def push_morning():
    sheet = get_sheet()
    today = datetime.now().strftime("%d/%m/%Y")
    sheet.append_row([today, "שחייה קלה", "", "תפריט יומי", "", "", ""])
    send_whatsapp("🌅 בוקר טוב! היום: שחייה קלה. תזונה: שייק חלבון אחרי אימון.")
    return {"status": "morning push sent"}

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
    sheet.update_cell(row, 7, feedback)
    send_whatsapp(feedback)
    return {"status": "night feedback sent"}

@app.post("/wa")
async def receive_whatsapp(request: Request):
    sheet = get_sheet()
    form = await request.form()
    body = form.get('Body').strip()

    today = datetime.now().strftime("%d/%m/%Y")
    cells = sheet.findall(today)
    if not cells:
        sheet.append_row([today, "שחייה קלה", "", "תפריט יומי", "", "", ""])
    row = cells[0].row

    if body.startswith("אימון"):
        sheet.update_cell(row, 3, body[6:])
        send_whatsapp("✔️ עודכן! איך הייתה הארוחה?")
    elif body.startswith("אכלתי"):
        sheet.update_cell(row, 5, body[7:])
        send_whatsapp("🥤 כמה ליטר מים שתית היום?")
    elif body.replace(".", "").isdigit():
        sheet.update_cell(row, 6, body)
        send_whatsapp("מעולה! נדבר בערב עם פידבק 🙌")
    return {"status": "ok"}
