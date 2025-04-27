from utils.whatsapp import send_whatsapp
from utils.sheets import get_sheet, find_today_row, update_cell
from datetime import datetime

def may_daily_nutrition_tip():
    message = (
        "היי ערן! כאן מאי התזונאית שלך 🌱\n"
        "טיפ להיום: אל תשכח לשתות לפחות 2 ליטר מים 💧\n"
        "ולאכול חטיף חלבון קטן אחרי האימון 💪.\n"
        "רוצה עזרה בבניית תפריט אישי? שלח לי 'תפריט'."
    )
    send_whatsapp(message)

def may_request_water_and_food():
    message = (
        "ערן, כמה מים שתית היום? 💧\n"
        "ומה אכלת אחרי האימון? 🍽️\n"
        "שלח לי מספר ליטרים ואת הארוחה בקצרה!"
    )
    send_whatsapp(message)

def may_weekly_summary():
    message = (
        "סיכום שבועי 📋:\n"
        "כמה ימים עמדת ביעד השתייה והאכילה?\n"
        "שלח לי:\n"
        "- מספר ימים שהתמדת ✅\n"
        "- אם היו פספוסים - מה היה האתגר 🤔"
    )
    send_whatsapp(message)
