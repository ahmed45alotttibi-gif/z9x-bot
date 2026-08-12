import os
from dotenv import load_dotenv

load_dotenv("settings.env")

def _int(name, default=0):
    try:
        return int(os.getenv(name, default))
    except (TypeError, ValueError):
        return default

TOKEN = os.getenv("TOKEN")

GUILD_ID = _int("GUILD_ID")
TICKET_CATEGORY_ID = _int("TICKET_CATEGORY_ID")
STAFF_ROLE_ID = _int("STAFF_ROLE_ID")
LOG_CHANNEL_ID = _int("LOG_CHANNEL_ID")
WELCOME_CHANNEL_ID = _int("WELCOME_CHANNEL_ID")
GOODBYE_CHANNEL_ID = _int("GOODBYE_CHANNEL_ID")
AUTO_ROLE_ID = _int("AUTO_ROLE_ID")
LEVEL_UP_CHANNEL_ID = _int("LEVEL_UP_CHANNEL_ID")

SERVER_NAME = "Z9X"
EMBED_COLOR = 0x2B2D31
BRAND_COLOR = 0x5865F2

TICKET_CATEGORIES = {
    "support": {"label": "الدعم الفني", "emoji": "🛠️", "prefix": "support"},
    "purchase": {"label": "الشراء", "emoji": "💰", "prefix": "purchase"},
    "report": {"label": "شكوى / إبلاغ", "emoji": "⚠️", "prefix": "report"},
}
