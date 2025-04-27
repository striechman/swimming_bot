# agents/michal_agent.py

import openai
import os
from utils.whatsapp import send_whatsapp
from utils.sheets import get_sheet
from datetime import datetime

openai.api_key = os.getenv("OPENAI_API_KEY")

# מיכל - דיאטנית ספורט
MICHAL_SYSTEM_PROMPT = """
את מיכל, דיאטנית ספורט מוסמכת ומדריכת בריאות.
התפקיד שלך:
- לתת טיפים קצרים ובריאים לשתייה, אכילה ושמירה על אנרגיה גבוהה.
- לעקוב אחרי שתיית מים יומית (200 מ"ל כל כוס).
- לעודד הרגלים חיוביים ולא לנזוף.
- לשדר טון אישי, נעים ומקצועי.
- לעזור בבניית תפריטים אישיים קצרים אם מתבקשת.
"""

def michal_generate_response(user_message):
    """פונקציה שמחזירה תשובה מהמומחית מיכל"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": MICHAL_SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ]
        )
        reply = response['choices'][0]['message']['content'].strip()
        return reply
    except Exception as e:
        print(f"Error in michal_generate_response: {e}")
        return "מצטערת, הייתה תקלה זמנית. תוכל לנסות שוב בעוד כמה דקות."

def michal_daily_nutrition_tip():
    message = (
        "היי ערן! כאן מיכל הדיאטנית 🌿\n"
        "טיפ יומי: תתחיל את היום עם כוס מים חמימים ולימון 🍋.\n"
        "זה עוזר לעיכול ואנרגיה! רוצה שאשלח עוד רעיונות?"
    )
    send_whatsapp(message)

def michal_request_water_and_food():
    message = (
        "ערן, כמה מים שתית היום? 💧\n"
        "ומה אכלת אחרי האימון? 🍽️\n"
        "שלח לי:\n"
        "- כמה כוסות מים (200 מ\"ל כל כוס)\n"
        "- מה הייתה הארוחה."
    )
    send_whatsapp(message)

def michal_send_water_reminder():
    message = (
        "תזכורת 💧: אל תשכח לשתות כוס מים (200 מ\"ל)! שתית כבר? ענה לי 'שתיתי' או 'לא'."
    )
    send_whatsapp(message)

def michal_log_water_intake(user_message):
    """עדכון שתיית מים בגליון"""
    try:
        sheet = get_sheet()
        today = datetime.now().strftime("%d/%m/%Y")
        cells = sheet.findall(today)

        if not cells:
            sheet.append_row([today, "", "", "", "", "", ""])
            cells = sheet.findall(today)
        
        row = cells[0].row
        current_water = sheet.cell(row, 6).value

        if not current_water:
            current_water = 0
        else:
            current_water = float(current_water)

        current_water += 0.2  # 200 מ"ל = 0.2 ליטר
        sheet.update_cell(row, 6, str(round(current_water, 2)))
    except Exception as e:
        print(f"Error in michal_log_water_intake: {e}")

def michal_send_weekly_summary_request():
    message = (
        "💬 סיכום שבועי!\n"
        "ערן, כמה ימים עמדת ביעדי השתייה והאכילה?\n"
        "- כמה ימים ✔️?\n"
        "- מה האתגרים שהיו השבוע? 🤔"
    )
    send_whatsapp(message)
