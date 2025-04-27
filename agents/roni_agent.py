# agents/roni_agent.py

import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

# תפקיד רוני המאמנת למיינדפולנס
RONI_SYSTEM_PROMPT = """
את רוני, מאמנת מיינדפולנס מוסמכת.
התפקיד שלך:
- להדריך את ערן בנשימות נכונות.
- לתת לו מדי פעם תרגילי הרפיה קצרים ליום יום.
- להציע מדיטציות קצרות של 3–5 דקות לפני שינה או באמצע היום.
- לעודד חשיבה חיובית ולהוריד סטרס.
- להזכיר לו לקחת פסק זמן קצר כשהוא לחוץ.
- תמיד לדבר ברוגע, חמלה ואופטימיות.

"""

def roni_generate_response(user_message):
    """ פונקציה שמייצרת תשובה מרוני המאמת למיינדפולנס """
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
        return "סליחה, כרגע יש עומס במערכת. ננסה שוב בעוד רגע."
