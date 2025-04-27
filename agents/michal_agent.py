# agents/michal_agent.py

import openai
import os
from utils.whatsapp import send_whatsapp
from utils.sheets import get_sheet, find_today_row, update_cell
from datetime import datetime

openai.api_key = os.getenv("OPENAI_API_KEY")

# פרומפט של מיכל - הדיאטנית החכמה
MICHAL_SYSTEM_PROMPT = """
את מיכל, דיאטנית ספורט מוסמכת.
התפקיד שלך:
- להדריך את ערן בשתיית מים נכונה (לפחות 2 ליטר ביום).
- לעקוב אחרי תזונה: חלבונים, פחמימות, ירקות, תוספים.
- לתת טיפים יומיים לתזונה נכונה.
- להזכיר לשתות מים לאורך היום כל שעתיים.
- לבקש פידבק: כמה מים שתה וכמה אכל.
- לעודד בעדינות ולא לנזוף, תמיד בסגנון חיובי.
- לבצע סיכום שבועי מפורט על מים ואכילה.
"""

def michal_generate_response(user_message):
    """ מייצרת תשובה מהמומחית מיכל לפי הודעת המשתמש """
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
        return "מצטערת, הייתה תקלה טכנית. תוכל לנסות שוב בעוד כמה דקות."

def michal_send_water_reminder():
    """ שולחת תזכורת לשתות מים """
    message = "תזכורת 💧: אל תשכח לשתות כוס מים (200 מ"ל)! שתית כבר? ענה לי 'שתיתי' או 'לא'."
    send_whatsapp(message)

def michal_log_water_intake(user_response):
    """ רושמת שתיית מים בגליון """
    if "שתיתי" in user_response:
        sheet = get_sheet()
        today = datetime.now().strftime("%d/%m/%Y")
        cells = sheet.findall(today)
        if not cells:
            sheet.append_row([today, "", "", "", "", "200", ""])  # הוספת שתייה ראשונית
        else:
            row = cells[0].row
            current_value = sheet.cell(row, 6).value
            if current_value == "":
                current_value = 0
            else:
                current_value = int(current_value)
            updated_value = current_value + 200
            update_cell(row, 6, updated_value)
        send_whatsapp("מעולה! ✅ עוד כוס מים נרשמה. תמשיך ככה!")

def michal_send_weekly_summary_request():
    """ שולחת בקשה לסיכום שתייה ותזונה שבועי """
    message = (
        "✨ סיכום שבועי ✨\n"
        "- בכמה ימים שתית מספיק מים?\n"
        "- האם עמדת ביעדי התזונה?\n"
        "ספר לי במספרים ואעזור לך להשתפר!"
    )
    send_whatsapp(message)
