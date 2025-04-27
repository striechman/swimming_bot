from utils.whatsapp import send_whatsapp
from datetime import datetime

def roni_daily_mindfulness():
    message = (
        "שלום ערן! 🌸 כאן רוני, מאמנת המיינדפולנס שלך.\n"
        "הצעה להפסקה קצרה:\n"
        "עצום עיניים ל-3 דקות.\n"
        "נשימות עמוקות: שאיפה 4 שניות, נשיפה 6 שניות.\n"
        "תחשוב על משהו אחד שאתה מודה עליו היום 🙏.\n"
        "מוכן לנסות? כתוב לי 'עשיתי'."
    )
    send_whatsapp(message)

def roni_evening_relaxation():
    message = (
        "לפני השינה... 🌙\n"
        "5 דקות דמיון מודרך:\n"
        "דמיין ים רגוע, גל קטן מגיע ונעלם.\n"
        "כל נשימה שלך - גלים עדינים יותר.\n"
        "תישן טוב חלום מתוק 😴✨"
    )
    send_whatsapp(message)

def roni_weekly_checkin():
    message = (
        "ערן, איך הייתה הרגשת השבוע? 💬\n"
        "שלח לי:\n"
        "- האם עשית מדיטציות? 🧘‍♂️\n"
        "- האם הרגשת שיפור באנרגיה או ברוגע?\n"
        "אני פה ללוות אותך במסע הזה 💙."
    )
    send_whatsapp(message)
