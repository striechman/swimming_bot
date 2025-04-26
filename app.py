from fastapi import FastAPI, Request
import openai
import os
import gspread
import json
from google.oauth2.service_account import Credentials
from twilio.rest import Client
from datetime import datetime

app = FastAPI()

# Load credentials from environment variable
credentials_info = json.loads(os.getenv('GOOGLE_CREDENTIALS_JSON'))
creds = Credentials.from_service_account_info(credentials_info)

# Authorize Google Sheets
gc = gspread.authorize(creds)
sh = gc.open('FitnessTracker').sheet1

# Twilio setup
twilio_client = Client(os.getenv('TWILIO_SID'), os.getenv('TWILIO_TOKEN'))
from_whatsapp = os.getenv('TWILIO_FROM')
to_whatsapp = os.getenv('TWILIO_TO')

# OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Helper function to send WhatsApp messages
def send_whatsapp(message):
    twilio_client.messages.create(body=message, from_=from_whatsapp, to=to_whatsapp)

# Endpoint to push morning message
@app.get("/push/morning")
async def push_morning():
    today = datetime.now().strftime("%d/%m/%Y")
       sh.append_row([today, "שחייה קלה", "", "תפריט יומי", "", "", ""])

