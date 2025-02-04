# وارد کردن کتابخانه‌های مورد نیاز
import random
import asyncio
from pymongo import MongoClient
from pyrogram import Client, filters
from pyrogram.enums import ChatAction
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from deep_translator import GoogleTranslator 
from config import MONGO_URL
from nexichat import nexichat
from nexichat.modules.helpers import CHATBOT_ON
from pyrogram.enums import ChatMemberStatus as CMS
from pyrogram.types import CallbackQuery

import config
from nexichat import LOGGER, nexichat
from nexichat.modules.helpers import (
    ABOUT_BTN, ABOUT_READ, ADMIN_READ, BACK,
    CHATBOT_BACK, CHATBOT_READ, DEV_OP,
    HELP_BTN, HELP_READ, MUSIC_BACK_BTN,
    SOURCE_READ, START, TOOLS_DATA_READ,
)

# تنظیم اتصال‌های دیتابیس
WORD_MONGO_URL = "mongodb+srv://AbhiModszYT:AbhiModszYT@abhimodszyt.flmdtda.mongodb.net/?retryWrites=true&w=majority"
chatdb = MongoClient(MONGO_URL)
worddb = MongoClient(WORD_MONGO_URL)

# تنظیم کالکشن‌های دیتابیس
status_db = chatdb["ChatBotStatusDb"]["StatusCollection"]
chatai = worddb["Word"]["WordDb"]
lang_db = chatdb["ChatLangDb"]["LangCollection"]
bad_words_db = chatdb["BadWordsDb"]["WordsCollection"]

# راه‌اندازی مترجم
translator = GoogleTranslator()

# تعریف زبان‌های پشتیبانی شده
languages = {
    'Persian': 'fa',
    'English': 'en',
    'Arabic': 'ar',
    'Turkish': 'tr',
    'Spanish': 'es',
    'Russian': 'ru',
    'Indonesian': 'id',
    'Italian': 'it',
    'Hindi': 'hi',
    'German': 'de',
    'French': 'fr',
    'Portuguese': 'pt',
    'Polish': 'pl',
    'Ukrainian': 'uk',
    'Uzbek': 'uz',
    'Korean': 'ko',
    'Japanese': 'ja',
    'Chinese': 'zh',
    'Dutch': 'nl',
    'Vietnamese': 'vi'
}

# لیست پیش‌فرض کلمات نامناسب
DEFAULT_BAD_WORDS = [
    # کلمات نامناسب پیش‌فرض را اینجا اضافه کنید
]

# کش پاسخ‌ها
replies_cache = []

# توابع کمکی
def generate_language_buttons(languages):
    """تولید دکمه‌های انتخاب زبان"""
    buttons = []
    current_row = []
    for lang, code in languages.items():
        current_row.append(InlineKeyboardButton(lang.capitalize(), callback_data=f'setlang_{code}'))
        if len(current_row) == 4:
            buttons.append(current_row)
            current_row = []
    if current_row:
        buttons.append(current_row)
    return InlineKeyboardMarkup(buttons)

async def check_bad_words(text: str, chat_id: int) -> tuple[bool, str]:
    """بررسی متن برای کلمات نامناسب"""
    if not text:
        return False, text
        
    chat_filters = await bad_words_db.find_one({"chat_id": chat_id})
    bad_words = set(chat_filters["words"] if chat_filters else DEFAULT_BAD_WORDS)
    
    has_bad_word = False
    words = text.split()
    
    for i, word in enumerate(words):
        if word.lower() in bad_words:
            words[i] = "❌" * len(word)
            has_bad_word = True
            
    return has_bad_word, " ".join(words)

async def get_chat_language(chat_id):
    """دریافت زبان تنظیم شده برای چت"""
    chat_lang = await lang_db.find_one({"chat_id": chat_id})
    return chat_lang["language"] if chat_lang and "language" in chat_lang else None

async def load_replies_cache():
    """بارگذاری پاسخ‌ها در کش"""
    global replies_cache
    replies_cache = await chatai.find().to_list(length=None)

async def get_reply(word: str):
    """یافتن پاسخ مناسب برای یک کلمه"""
    global replies_cache
    if not replies_cache:
        await load_replies_cache()
        
    relevant_replies = [reply for reply in replies_cache if reply['word'] == word]
    if not relevant_replies:
        relevant_replies = replies_cache
    return random.choice(relevant_replies) if relevant_replies else None

async def save_reply(original_message: Message, reply_message: Message):
    """ذخیره پیام و پاسخ در دیتابیس"""
    try:
        reply_data = {
            "word": original_message.text,
            "text": None,
            "check": "none",
        }

        if reply_message.sticker:
            reply_data["text"] = reply_message.sticker.file_id
            reply_data["check"] = "sticker"
        elif reply_message.photo:
            reply_data["text"] = reply_message.photo.file_id
            reply_data["check"] = "photo"
        elif reply_message.video:
            reply_data["text"] = reply_message.video.file_id
            reply_data["check"] = "video"
        elif reply_message.audio:
            reply_data["text"] = reply_message.audio.file_id
            reply_data["check"] = "audio"
        elif reply_message.animation:
            reply_data["text"] = reply_message.animation.file_id
            reply_data["check"] = "gif"
        elif reply_message.voice:
            reply_data["text"] = reply_message.voice.file_id
            reply_data["check"] = "voice"
        elif reply_message.text:
            reply_data["text"] = reply_message.text
            reply_data["check"] = "none"

        is_chat = await chatai.find_one(reply_data)
        if not is_chat:
            await chatai.insert_one(reply_data)
            replies_cache.append(reply_data)

    except Exception as e:
        LOGGER.error(f"خطا در ذخیره پاسخ: {e}")

# دستورات ربات
@nexichat.on_message(filters.command(["lang", "language", "setlang"]))
async def set_language(client: Client, message: Message):
    """تنظیم زبان چت"""
    await message.reply_text(
        "ᴘʟᴇᴀsᴇ sᴇʟᴇᴄᴛ ʏᴏᴜʀ ᴄʜᴀᴛ ʟᴀɴɢᴜᴀɢᴇ:",
        reply_markup=generate_language_buttons(languages))

@nexichat.on_message(filters.command(["resetlang", "nolang"]))
async def reset_language(client: Client, message: Message):
    """بازنشانی زبان چت"""
    chat_id = message.chat.id
    await lang_db.update_one(
        {"chat_id": chat_id},
        {"$set": {"language": "nolang"}},
        upsert=True
    )
    await message.reply_text("**Bot language has been reset in this chat, now mix language is using.**")

@nexichat.on_message(filters.command(["addbadword", "badword"]) & filters.group)
async def add_bad_word(client, message: Message):
    """اضافه کردن کلمه به لیست فیلتر"""
    try:
        user_status = await message.chat.get_member(message.from_user.id)
        if user_status.status not in [CMS.OWNER, CMS.ADMINISTRATOR]:
            return await message.reply_text("❌ فقط ادمین‌ها می‌توانند کلمات نامناسب را مدیریت کنند!")

        if len(message.command) < 2:
            return await message.reply_text("❌ لطفاً کلمه مورد نظر را وارد کنید!\n\nمثال: /badword کلمه")

        word = message.command[1].lower()
        chat_id = message.chat.id

        await bad_words_db.update_one(
            {"chat_id": chat_id},
            {"$addToSet": {"words": word}},
            upsert=True
        )
        
        await message.reply_text(f"✅ کلمه '{word}' به لیست فیلتر اضافه شد.")
        
    except Exception as e:
        await message.reply_text(f"❌ خطا: {str(e)}")

@nexichat.on_message(filters.command(["rmbadword", "unbadword"]) & filters.group)
async def remove_bad_word(client, message: Message):
    """حذف کلمه از لیست فیلتر"""
    try:
        user_status = await message.chat.get_member(message.from_user.id)
        if user_status.status not in [CMS.OWNER, CMS.ADMINISTRATOR]:
            return await message.reply_text("❌ فقط ادمین‌ها می‌توانند کلمات نامناسب را مدیریت کنند!")

        if len(message.command) < 2:
            return await message.reply_text("❌ لطفاً کلمه مورد نظر را وارد کنید!\n\nمثال: /unbadword کلمه")

        word = message.command[1].lower()
        chat_id = message.chat.id

        result = await bad_words_db.update_one(
            {"chat_id": chat_id},
            {"$pull": {"words": word}}
        )
        
        if result.modified_count > 0:
            await message.reply_text(f"✅ کلمه '{word}' از لیست فیلتر حذف شد.")
        else:
            await message.reply_text("❌ این کلمه در لیست فیلتر وجود ندارد!")
            
    except Exception as e:
        await message.reply_text(f"❌ خطا: {str(e)}")

@nexichat.on_message(filters.command(["badwords", "listbadwords"]) & filters.group)
async def list_bad_words(client, message: Message):
    """نمایش لیست کلمات فیلتر شده"""
    try:
        chat_id = message.chat.id
        
        chat_filters = await bad_words_db.find_one({"chat_id": chat_id})
        words = list(chat_filters["words"]) if chat_filters else DEFAULT_BAD_WORDS
        
        if not words:
            return await message.reply_text("❌ لیست کلمات فیلتر شده خالی است!")
            
        text = "📋 لیست کلمات فیلتر شده:\n\n"
        for i, word in enumerate(words, 1):
            text += f"{i}. {word}\n"
            
        await message.reply_text(text)
        
    except Exception as e:
        await message.reply_text(f"❌ خطا: {str(e)}")

@nexichat.on_message(filters.command("chatbot"))
async def chatbot_settings(client: Client, message: Message):
    """تنظیمات چت‌بات"""
    await message.reply_text(
        f"ᴄʜᴀᴛ: {message.chat.title}\n**ᴄʜᴏᴏsᴇ ᴀɴ ᴏᴘᴛɪᴏɴ ᴛᴏ ᴇɴᴀʙʟᴇ/ᴅɪsᴀʙʟᴇ ᴄʜᴀᴛʙᴏᴛ.**",
        reply_markup=InlineKeyboardMarkup(CHATBOT_ON),
    )

# پردازش پیام‌های ورودی
@nexichat.on_message((filters.text | filters.sticker | filters.photo | filters.video | filters.audio))
async def chatbot_response(client: Client, message: Message):
    """پردازش پیام‌های ورودی و ارسال پاسخ"""
    try:
        chat_id = message.chat.id
        
        # بررسی وضعیت فعال/غیرفعال بودن ربات
        chat_status = await status_db.find_one({"chat_id": chat_id})
        if chat_status and chat_status.get("status") == "disabled":
            return

        # بررسی و فیلتر کلمات نامناسب
        if message.text:
            has_bad_word, filtered_text = await check_bad_words(message.text, chat_id)
            if has_bad_word:
                try:
                    await message.delete()
                    warning_msg = await message.reply_text(
                        f"⚠️ {message.from_user.mention} لطفاً از کلمات نامناسب استفاده نکنید!"
                    )
                    await asyncio.sleep(5)
                    await warning_msg.delete()
                    return
                except:
                    pass
            message.text = filtered_text

        if message.text and any(message.text.startswith(prefix) for prefix in ["!", "/", ".", "?", "@", "#"]):
            return

        if (message.reply_to_message and message.reply_to_message.from_user.id == client.me.id) or not message.reply_to_message:
            await client.send_chat_action(message.chat.id, ChatAction.TYPING)

            reply_data = await get_reply(message.text if message.text else "")
            
            if reply_data:
                response_text = reply_data["text"]
                chat_lang = await get_chat_language(chat_id)

                if not chat_lang or chat_lang == "nolang":
                    translated_text = response_text
                else:
                    translated_text = GoogleTranslator(source='auto', target=chat_lang).translate(response_text)
                    if not translated_text:
                        translated_text = response_text

                try:
                    if reply_data["check"] == "sticker":
                        await message.reply_sticker(reply_data["text"])
                    elif reply_data["check"] == "photo":
                        await message.reply_photo(reply_data["text"])
                    elif reply_data["check"] == "video":
                        await message.reply_video(reply_data["text"])
                    elif reply_data["check"] == "audio":
                        await message.reply_audio(reply_data["text"])
                    elif reply_data["check"] == "gif":
                        await message.reply_animation(reply_data["text"])
                    elif reply_data["check"] == "voice":
                        await message.reply_voice(reply_data["text"])
                    else:
                        await message.reply_text(translated_text)
                except:
                    pass
            else:
                try:
                    await message.reply_text("**what??**")
                except:
                    pass

        if message.reply_to_message:
            await save_reply(message.reply_to_message, message)

    except Exception as e:
        LOGGER.error(f"خطا در پردازش پیام: {e}")
        return
