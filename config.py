from os import getenv

from dotenv import load_dotenv

load_dotenv()

API_ID = "29520741"
# -------------------------------------------------------------
API_HASH = "08ff9d218934611c95b896ede0fdfdcd"
# --------------------------------------------------------------
BOT_TOKEN = getenv("BOT_TOKEN", None)
MONGO_URL = getenv("MONGO_URL", None)
OWNER_ID = int(getenv("OWNER_ID", "6663026922"))
SUPPORT_GRP = "TORONTO_TM"
UPDATE_CHNL = "Panel_Tornado"
OWNER_USERNAME = "OWNER_ROYAL"
