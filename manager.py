# manager.py

from agents.beri_agent import beri_generate_response
from agents.michal_agent import michal_generate_response
from agents.roni_agent import roni_generate_response

def route_message_to_agent(message_body: str):
    """ מנתב את ההודעה לסוכן המתאים """
    body_lower = message_body.lower()

    if "ברי" in body_lower:
        clean_msg = message_body.replace("ברי", "").strip()
        return beri_generate_response(clean_msg)
    
    elif "מיכל" in body_lower:
        clean_msg = message_body.replace("מיכל", "").strip()
        return michal_generate_response(clean_msg)
    
    elif "רוני" in body_lower:
        clean_msg = message_body.replace("רוני", "").strip()
        return roni_generate_response(clean_msg)
    
    else:
        return "בבקשה תתייג את אחד הסוכנים: ברי, מיכל או רוני."
