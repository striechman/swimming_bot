# agents/beri_agent.py

import openai
from settings import user_profile

def beri_generate_response(user_message):
    prompt = f"""
אתה ברי, מאמן השחייה והכושר האישי של {user_profile['name']} (גיל {user_profile['age']}, רמת כושר {user_profile['fitness_level']}, משקל {user_profile['weight_kg']} ק"ג).
תפקידך: לאמן אותו מקצועית ומדויקת בהתאם ליכולותיו ולמצבו הנוכחי.

כאשר הוא כותב לך הודעה, תן לו מענה:
- פרטי
- מקצועי מאוד
- כולל תוכנית אימון יומית אם צריך
- זמנים, מספר חזרות, סטים, דופק יעד
- ותזכיר לו לשתות מים ולהתאושש בסיום.

ענה בעברית רהוטה ומעודדת.

ההודעה שקיבלת:
\"{user_message}\"
"""
    completion = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return completion['choices'][0]['message']['content'].strip()
