import os
import json
from google.oauth2.service_account import Credentials
from twilio.rest import Client

# Twilio
TWILIO_SID = os.getenv('TWILIO_SID')
TWILIO_TOKEN = os.getenv('TWILIO_TOKEN')
TWILIO_FROM = os.getenv('TWILIO_FROM')
TWILIO_TO = os.getenv('TWILIO_TO')

# OpenAI
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Google Sheets
GOOGLE_CREDENTIALS_JSON = os.getenv('GOOGLE_CREDENTIALS_JSON')
credentials_info = json.loads(GOOGLE_CREDENTIALS_JSON)
GOOGLE_CREDS = Credentials.from_service_account_info(credentials_info)

# Initialize clients
twilio_client = Client(TWILIO_SID, TWILIO_TOKEN)
