import os
from twilio.rest import Client

twilio_client = Client(os.getenv('TWILIO_SID'), os.getenv('TWILIO_TOKEN'))
from_whatsapp = os.getenv('TWILIO_FROM')
to_whatsapp = os.getenv('TWILIO_TO')

def send_whatsapp(message):
    twilio_client.messages.create(
        body=message,
        from_=from_whatsapp,
        to=to_whatsapp
    )
