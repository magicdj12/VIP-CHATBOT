from pyrogram.types import InlineKeyboardButton
from config import SUPPORT_GRP, UPDATE_CHNL
from nexichat import OWNER, nexichat

START_BOT = [
    [
        InlineKeyboardButton(
            text="😍 افزودن به گروه 😍",
            url=f"https://t.me/{nexichat.username}?startgroup=true",
        ),
    ],
    [
        InlineKeyboardButton(text="🥀 سازنده 🥀", user_id=OWNER),
        InlineKeyboardButton(text="✨ پشتیبانی ✨", url=f"https://t.me/{SUPPORT_GRP}"),
    ],
    [
        InlineKeyboardButton(text="« امکانات »", callback_data="HELP"),
    ],
]

DEV_OP = [
    [
        InlineKeyboardButton(text="🥀 سازنده 🥀", user_id=OWNER),
        InlineKeyboardButton(text="✨ پشتیبانی ✨", url=f"https://t.me/{SUPPORT_GRP}"),
    ],
    [
        InlineKeyboardButton(
            text="✦ افزودن به گروه ✦",
            url=f"https://t.me/{nexichat.username}?startgroup=true",
        ),
    ],
    [
        InlineKeyboardButton(text="« راهنما »", callback_data="HELP"),
    ],
    [
        InlineKeyboardButton(text="☁️ درباره ما ☁️", callback_data="ABOUT"),
    ],
]

PNG_BTN = [
    [
        InlineKeyboardButton(
            text="😍 افزودن به گروه 😍",
            url=f"https://t.me/{nexichat.username}?startgroup=true",
        ),
    ],
    [
        InlineKeyboardButton(
            text="⦿ بستن ⦿",
            callback_data="CLOSE",
        ),
    ],
]

BACK = [
    [
        InlineKeyboardButton(text="⦿ بازگشت ⦿", callback_data="BACK"),
    ],
]

HELP_BTN = [
    [
        InlineKeyboardButton(text="🐳 چت‌بات 🐳", callback_data="CHATBOT_CMD"),
        InlineKeyboardButton(text="🎄 ابزارها 🎄", callback_data="TOOLS_DATA"),
    ],
    [
        InlineKeyboardButton(text="⦿ بستن ⦿", callback_data="CLOSE"),
    ],
]

CLOSE_BTN = [
    [
        InlineKeyboardButton(text="⦿ بستن ⦿", callback_data="CLOSE"),
    ],
]

CHATBOT_ON = [
    [
        InlineKeyboardButton(text="فعال کردن", callback_data="enable_chatbot"),
        InlineKeyboardButton(text="غیرفعال کردن", callback_data="disable_chatbot"),
    ],
]

MUSIC_BACK_BTN = [
    [
        InlineKeyboardButton(text="به زودی", callback_data=f"soom"),
    ],
]

S_BACK = [
    [
        InlineKeyboardButton(text="⦿ بازگشت ⦿", callback_data="SBACK"),
        InlineKeyboardButton(text="⦿ بستن ⦿", callback_data="CLOSE"),
    ],
]

CHATBOT_BACK = [
    [
        InlineKeyboardButton(text="⦿ بازگشت ⦿", callback_data="CHATBOT_BACK"),
        InlineKeyboardButton(text="⦿ بستن ⦿", callback_data="CLOSE"),
    ],
]

HELP_START = [
    [
        InlineKeyboardButton(text="« راهنما »", callback_data="HELP"),
        InlineKeyboardButton(text="🐳 بستن 🐳", callback_data="CLOSE"),
    ],
]

HELP_BUTN = [
    [
        InlineKeyboardButton(
            text="« راهنما »", url=f"https://t.me/{nexichat.username}?start=help"
        ),
        InlineKeyboardButton(text="⦿ بستن ⦿", callback_data="CLOSE"),
    ],
]

ABOUT_BTN = [
    [
        InlineKeyboardButton(text="🎄 پشتیبانی 🎄", url=f"https://t.me/{SUPPORT_GRP}"),
        InlineKeyboardButton(text="« راهنما »", callback_data="HELP"),
    ],
    [
        InlineKeyboardButton(text="🍾 سازنده 🍾", user_id=OWNER),
    ],
    [
        InlineKeyboardButton(text="🐳 کانال 🐳", url=f"https://t.me/{UPDATE_CHNL}"),
        InlineKeyboardButton(text="⦿ بازگشت ⦿", callback_data="BACK"),
    ],
]
