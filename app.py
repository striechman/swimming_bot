from fastapi import FastAPI, Request
import openai
import os
import gspread
import json
from google.oauth2.service_account import Credentials
from twilio.rest import Client
from datetime import datetime

app = FastAPI()

# הגדרות טוויליו
twilio_client = Client(os.getenv('TWILIO_SID'), os.getenv('TWILIO_TOKEN'))
from_whatsapp = os.getenv('TWILIO_FROM')
to_whatsapp = os.getenv('TWILIO_TO')

# הגדרות OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# קבועים
SHEET_ID = os.getenv('SHEET_ID')  # ה-ID של הגוגל שיטס שלך

# התחברות לשיט
def get_sheet():
    credentials_info = json.loads(os.getenv('GOOGLE_CREDENTIALS_JSON'))
    creds = Credentials.from_service_account_info(credentials_info)
    gc = gspread.authorize(creds)
    return gc.open_by_key(SHEET_ID).sheet1

# שליחת הודעה בוואטסאפ
def send_whatsapp(message):
    twilio_client.messages.create(body=message, from_=from_whatsapp, to=to_whatsapp)

# זיהוי סוכן לפי התגית
def detect_agent(message):
    message = message.lower()
    if message.startswith("[ברי]"):
        return "beri"
    elif message.startswith("[לינוי]"):
        return "linoy"
    elif message.startswith("[רוני]"):
        return "roni"
    else:
        return "default"

# תסריטים לכל סוכן
async def beri_agent(message):
    sh = get_sheet()
    today = datetime.now().strftime("%d/%m/%Y")
    cells = sh.findall(today)
    if not cells:
        sh.append_row([today, "", "", "", "", "", ""])

    prompt = f"""
    אתה מאמן כושר ושחייה בשם ברי. ענה בעברית, בסגנון מקצועי-חברי.
    היום המשתמש כתב: "{message}"
    תן לו מענה אמיתי, מקצועי, עם תרגילים מדויקים, סגנונות שחייה, זמנים לכל סט, דופק יעד וכו'.
    אל תמציא עובדות אלא כתוב טיפים אמיתיים של מאמן.
    """

    res = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )

    feedback = res['choices'][0]['message']['content'].strip()
    send_whatsapp(f"ברי אומר:\n{feedback}")
    return {"status": "beri response sent"}

async def linoy_agent(message):
    prompt = f"""
    את דיאטנית ספורט בשם לינוי. עני בעברית בסגנון מקצועי וחברי.
    המשתמש עדכן: "{message}"
    תני לו משוב אמיתי על תזונה, שתייה, המלצות לאכילה נכונה אחרי אימון, הצעות לארוחות וכו'.
    """

    res = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )

    feedback = res['choices'][0]['message']['content'].strip()
    send_whatsapp(f"לינוי אומרת:\n{feedback}")
    return {"status": "linoy response sent"}

async def roni_agent(message):
    prompt = f"""
    את מאמנת מיינדפולנס בשם רוני. עני בעברית, ברוגע ובחמימות.
    המשתמש כתב: "{message}"
    תני לו תרגילי נשימה, הרפיה, מדיטציה קצרה ל-5 דקות, משפטי השראה.
    """

    res = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )

    feedback = res['choices'][0]['message']['content'].strip()
    send_whatsapp(f"רוני אומרת:\n{feedback}")
    return {"status": "roni response sent"}

# דחיפת הודעה יומית בבוקר
@app.get("/push/morning")
async def push_morning():
    sh = get_sheet()
    today = datetime.now().strftime("%d/%m/%Y")
    sh.append_row([today, "שחייה קלה", "", "תפריט יומי", "", "", ""])
    send_whatsapp("🌅 בוקר טוב! ברוך הבא ליום חדש! היום: שחייה קלה. זכרו לאכול נכון ולשתות מים.")
    return {"status": "morning push sent"}

# קבלת הודעות מוואטסאפ
@app.post("/wa")
async def receive_whatsapp(request: Request):
    form = await request.form()
    body = form.get('Body').strip()

    agent = detect_agent(body)

    if agent == "beri":
        return await beri_agent(body[5:].strip())
    elif agent == "linoy":
        return await linoy_agent(body[6:].strip())
    elif agent == "roni":
        return await roni_agent(body[6:].strip())
    else:
        send_whatsapp("❓ אנא תתחיל את ההודעה בתגית מתאימה: [ברי] או [לינוי] או [רוני]")
        return {"status": "unknown agent"}
