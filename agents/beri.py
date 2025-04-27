from utils.whatsapp import send_whatsapp
from utils.sheets import get_sheet, find_today_row, update_cell
from datetime import datetime
import openai
import os

def beri_daily_update():
    sheet = get_sheet()
    today = datetime.now().strftime("%d/%m/%Y")
    row = find_today_row(sheet)

    # יצירת הודעת אימון יומית מבר
    exercise_message = (
        f"אהלן ערן! 🏊‍♂️\n"
        f"היום {today}, יש לנו אימון שחייה.\n"
        f"- סגנון עיקרי: חזה + חתירה\n"
        f"- משך כללי: 50 דקות\n"
        f"- מטרות דופק: 140-155 פעימות לדקה\n"
        f"- חימום: 10 דקות שחייה קלה\n"
        f"- סטים עיקריים: \n"
        f"  * 4x100 מטר בקצב בינוני עם 30 שניות מנוחה\n"
        f"  * 4x50 מטר מהיר עם 20 שניות מנוחה\n"
        f"- שחרור: 5 דקות שחייה רגועה\n\n"
        f"איך אתה מרגיש הבוקר? תכתוב לי בסוף האימון איך הלך ומה הרגשת! 💬"
    )

    send_whatsapp(exercise_message)

def beri_feedback_request():
    message = (
        "ערן, סיימת את האימון? 🏊‍♂️\n"
        "שלח לי:\n"
        "- איך הרגשת? 🤔\n"
        "- מה היה לך הכי קשה? 💪\n"
        "- כמה זמן לקח לך כל סט?\n"
        "- האם שמרת על הדופק המומלץ?\n"
        "אני פה ללמוד ולשפר אותך! ✨"
    )
    send_whatsapp(message)

def beri_encouragement():
    message = (
        "תזכור ערן, כל אימון מקרב אותך למטרה! 🏆\n"
        "גם אם קשה — תמשיך. אני גאה בך! 💙"
    )
    send_whatsapp(message)
