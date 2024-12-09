from os import getenv

from dotenv import load_dotenv

load_dotenv()

API_ID = "20262586"
# -------------------------------------------------------------
API_HASH = "7c331e3751b606fdffe1fad18f0065b6"
# --------------------------------------------------------------
BOT_TOKEN = getenv("BOT_TOKEN", None)
MONGO_URL = getenv("MONGO_URL", None)
OWNER_ID = int(getenv("OWNER_ID", "6663026922"))
SUPPORT_GRP = "TORONTO_TM"
UPDATE_CHNL = "Panel_Tornado"
OWNER_USERNAME = "OWNER_ROYAL"
