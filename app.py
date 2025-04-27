from fastapi import FastAPI, Request
import openai
import os
import gspread
import json
from google.oauth2.service_account import Credentials
from twilio.rest import Client
from datetime import datetime

app = FastAPI()

# קריאה של מפתחות מהסביבה
twilio_client = Client(os.getenv('TWILIO_SID'), os.getenv('TWILIO_TOKEN'))
from_whatsapp = os.getenv('TWILIO_FROM')
to_whatsapp = os.getenv('TWILIO_TO')
openai.api_key = os.getenv('OPENAI_API_KEY')

# הגדרת הסוכנים
agents = {
    "ברי": {
        "role": "מאמן שחיה וכושר מקצועי",
        "style": "מקצועי וחברי, מדויק עם זמני אימון, דופק יעד, טכניקה"
    },
    "מיכל": {
        "role": "דיאטנית ספורט",
        "style": "עוקבת אחרי אוכל, שתייה ומדדים"
    },
    "רוני": {
        "role": "מאמנת מיינדפולנס",
        "style": "מעבירה מדיטציות קצרות, עידוד חשיבה חיובית"
    }
}

# פונקציה להתחברות לגוגל שיטס
def get_sheet():
    credentials_info = json.loads(os.getenv('GOOGLE_CREDENTIALS_JSON'))
    creds = Credentials.from_service_account_info(credentials_info)
    gc = gspread.authorize(creds)
    sheet = gc.open_by_key(os.getenv('SHEET_ID')).sheet1
    return sheet

# שליחת הודעת וואטסאפ
def send_whatsapp(message):
    twilio_client.messages.create(body=message, from_=from_whatsapp, to=to_whatsapp)

# שליחת הודעה מהסוכן המתאים
def send_agent_message(agent_name, user_message):
    agent = agents.get(agent_name)
    if not agent:
        return "סוכן לא קיים."
    prompt = f"""אתה {agent['role']} בשם {agent_name}.
    סגנון הדיבור שלך הוא {agent['style']}.
    הודעת המשתמש: {user_message}
    """
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6
    )
    reply = response['choices'][0]['message']['content'].strip()
    send_whatsapp(reply)
    return reply

# נקודת פתיחה - דחיפת בוקר
@app.get("/push/morning")
async def push_morning():
    sheet = get_sheet()
    today = datetime.now().strftime("%d/%m/%Y")
    sheet.append_row([today, "שחייה קלה", "", "תפריט יומי", "", "", ""])
    send_agent_message("ברי", "כתוב לי הודעת בוקר עם תכנית אימון ליום כולל זמני תרגילים ודופק יעד")
    return {"status": "morning push sent"}

# נקודת פתיחה - דחיפת ערב
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

# קבלת הודעות משתמש
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

    # זיהוי למי ההודעה מיועדת
    body_lower = body.lower()
    if "ברי" in body_lower:
        clean_msg = body.replace("ברי", "").strip()
        reply = send_agent_message("ברי", clean_msg)
    elif "מיכל" in body_lower:
        clean_msg = body.replace("מיכל", "").strip()
        reply = send_agent_message("מיכל", clean_msg)
    elif "רוני" in body_lower:
        clean_msg = body.replace("רוני", "").strip()
        reply = send_agent_message("רוני", clean_msg)
    else:
        send_whatsapp("בבקשה תתייג את הסוכן: ברי, מיכל או רוני.")
        return {"status": "tag missing"}

    return {"reply": reply}
