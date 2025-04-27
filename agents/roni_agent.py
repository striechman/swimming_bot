# agents/roni_agent.py

import openai
import os
from utils.whatsapp import send_whatsapp

openai.api_key = os.getenv("OPENAI_API_KEY")

# רוני - מאמנת מיינדפולנס
RONI_SYSTEM_PROMPT = """
את רוני, מאמנת מיינדפולנס מוסמכת.
התפקיד שלך:
- לתת תרגילי נשימה פשוטים (1-5 דקות).
- להציע מדיטציות קצרות לשיפור רוגע, שינה ואנרגיה.
- להמליץ משפטים חיוביים ליום.
- לעזור לערן להיות נינוח ומפוקס.
- להשתמש בטון אישי, מרגיע, חם ותומך.
"""

def roni_generate_response(user_message):
    """פונקציה שמחזירה תשובה חכמה מרוני"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": RONI_SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ]
        )
        reply = response['choices'][0]['message']['content'].strip()
        return reply
    except Exception as e:
        print(f"Error in roni_generate_response: {e}")
        return "מצטערת, הייתה תקלה זמנית. תוכל לנסות שוב בעוד כמה דקות."

def roni_send_daily_mindfulness_tip():
    """שליחת טיפ יומי קצר"""
    message = (
        "🌿 טיפ יומי מרוני 🌿\n"
        "עצור לרגע. קח 3 נשימות עמוקות.\n"
        "בכל נשיפה תחשוב על משהו טוב שקרה היום. ☀️\n"
        "תרצה שאשלח גם תרגיל קצר למיקוד?"
    )
    send_whatsapp(message)

def roni_send_evening_relaxation_tip():
    """שליחת תרגול קצר לפני שינה"""
    message = (
        "🌙 רוגע לשינה טובה:\n"
        "1. שב או שכב בנוחות.\n"
        "2. קח 10 נשימות עמוקות ואיטיות.\n"
        "3. בכל נשימה תגיד לעצמך בשקט: 'אני רגוע. אני נרגע.'\n"
        "לילה טוב ערן! 😴"
    )
    send_whatsapp(message)

def roni_send_mindfulness_exercise():
    """שליחת תרגיל מיינדפולנס קצר (בלילה למשל)"""
    message = (
        "🌙 תרגיל רוגע לפני שינה:\n"
        "1. קח נשימה עמוקה לאט דרך האף.\n"
        "2. החזק 3 שניות.\n"
        "3. נשוף באיטיות דרך הפה.\n"
        "חזור על זה 5 פעמים.\n"
        "לילה רגוע ונפלא, ערן! 🌟"
    )
    send_whatsapp(message)
