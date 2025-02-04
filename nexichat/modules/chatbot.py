# وارد کردن کتابخانه‌های مورد نیاز
import random
import asyncio
from pymongo import MongoClient
from pyrogram import Client, filters
from pyrogram.enums import ChatAction
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from deep_translator import GoogleTranslator 
from config import MONGO_URL, OWNER_ID
from nexichat import nexichat
from nexichat.modules.helpers import CHATBOT_ON
from pyrogram.enums import ChatMemberStatus as CMS
from pyrogram.types import CallbackQuery
from pyrogram.errors import FloodWait
import logging

# تنظیم لاگر
logger = logging.getLogger(__name__)

# تنظیم متغیرهای گلوبال
broadcast_lock = asyncio.Lock()
IS_BROADCASTING = False
banned_users = {}

# تنظیم اتصال‌های دیتابیس
WORD_MONGO_URL = "mongodb+srv://ranger:mohaMmoha900@cluster2.24a45.mongodb.net/?retryWrites=true&w=majority&appName=Cluster2"
chatdb = MongoClient(MONGO_URL)
worddb = MongoClient(WORD_MONGO_URL)

# تنظیم کالکشن‌های دیتابیس
status_db = chatdb["ChatBotStatusDb"]["StatusCollection"]
chatai = worddb["Word"]["WordDb"]
lang_db = chatdb["ChatLangDb"]["LangCollection"]
bad_words_db = chatdb["BadWordsDb"]["WordsCollection"]
users_db = chatdb["UsersDb"]["UsersCollection"]
chats_db = chatdb["ChatsDb"]["ChatsCollection"]

# تعریف زبان‌های پشتیبانی شده
languages = {
    'فارسی': 'fa',
    'انگلیسی': 'en',
    'عربی': 'ar',
    'ترکی': 'tr',
    'اسپانیایی': 'es',
    'روسی': 'ru',
    'اندونزیایی': 'id',
    'ایتالیایی': 'it',
    'هندی': 'hi',
    'آلمانی': 'de',
    'فرانسوی': 'fr',
    'پرتغالی': 'pt',
    'لهستانی': 'pl',
    'اوکراینی': 'uk',
    'ازبکی': 'uz',
    'کره‌ای': 'ko',
    'ژاپنی': 'ja',
    'چینی': 'zh',
    'هلندی': 'nl',
    'ویتنامی': 'vi'
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
        current_row.append(InlineKeyboardButton(lang, callback_data=f'setlang_{code}'))
        if len(current_row) == 3:
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
        logger.error(f"خطا در ذخیره پاسخ: {e}")

async def get_served_chats():
    """دریافت لیست گروه‌های ثبت شده"""
    chats = await chats_db.find().to_list(length=None)
    return chats

async def get_served_users():
    """دریافت لیست کاربران ثبت شده"""
    users = await users_db.find().to_list(length=None)
    return users

# دستورات ربات
@nexichat.on_message(filters.command(["بن", "ban"], ""))
async def ban_user(client, message):
    """بن کردن کاربر از گروه"""
    try:
        if not message.reply_to_message and len(message.command) < 2:
            return await message.reply_text("لطفاً روی پیام کاربر ریپلای کنید یا آیدی کاربر را وارد کنید")

        user_id = message.reply_to_message.from_user.id if message.reply_to_message else int(message.command[1])
        
        chat_member = await message.chat.get_member(message.from_user.id)
        if chat_member.status not in [CMS.OWNER, CMS.ADMINISTRATOR]:
            return await message.reply_text("❌ شما دسترسی لازم برای بن کردن کاربران را ندارید!")

        bot_member = await message.chat.get_member(client.me.id)
        if not bot_member.can_restrict_members:
            return await message.reply_text("❌ من دسترسی لازم برای بن کردن کاربران را ندارم!")

        try:
            await message.chat.ban_member(user_id)
            banned_users[user_id] = message.chat.id
            await message.reply_text(f"✅ کاربر با موفقیت از گروه بن شد!")
        except Exception as e:
            await message.reply_text(f"❌ خطا در بن کردن کاربر: {str(e)}")

    except Exception as e:
        await message.reply_text(f"❌ خطا: {str(e)}")

@nexichat.on_message(filters.command(["بن_ال", "banall"], ""))
async def ban_all(client, message):
    """بن کردن همه کاربران از گروه"""
    try:
        chat_member = await message.chat.get_member(message.from_user.id)
        if chat_member.status != CMS.OWNER:
            return await message.reply_text("❌ فقط مالک گروه می‌تواند از این دستور استفاده کند!")

        confirm = await message.reply_text(
            "⚠️ آیا مطمئن هستید می‌خواهید همه کاربران را بن کنید؟\n"
            "برای تأیید 'بله' و برای لغو 'خیر' را بفرستید."
        )

        try:
            response = await client.wait_for_message(
                filters.chat(message.chat.id) & 
                filters.user(message.from_user.id) & 
                filters.text & 
                filters.create(lambda _, __, m: m.text.lower() in ["بله", "خیر"]),
                timeout=30
            )
        except TimeoutError:
            return await confirm.edit_text("❌ عملیات به دلیل عدم پاسخ لغو شد.")

        if response.text.lower() == "خیر":
            return await confirm.edit_text("✅ عملیات لغو شد.")

        status_message = await message.reply_text("⏳ در حال بن کردن همه کاربران...")
        count = 0

        async for member in message.chat.get_members():
            if member.status not in [CMS.OWNER, CMS.ADMINISTRATOR]:
                try:
                    await message.chat.ban_member(member.user.id)
                    count += 1
                    if count % 10 == 0:
                        await status_message.edit_text(f"⏳ {count} کاربر تا الان بن شدند...")
                except Exception:
                    continue

        await status_message.edit_text(f"✅ عملیات کامل شد. {count} کاربر بن شدند.")

    except Exception as e:
        await message.reply_text(f"❌ خطا: {str(e)}")

@nexichat.on_message(filters.command(["زبان", "تنظیم_زبان"], ""))
async def set_language(client, message):
    """تنظیم زبان چت"""
    await message.reply_text(
        "لطفاً زبان مورد نظر خود را انتخاب کنید:",
        reply_markup=generate_language_buttons(languages)
    )

@nexichat.on_message(filters.command(["حذف_زبان", "بازنشانی_زبان"], ""))
async def reset_language(client, message):
    """بازنشانی زبان چت"""
    chat_id = message.chat.id
    await lang_db.update_one(
        {"chat_id": chat_id},
        {"$set": {"language": "nolang"}},
        upsert=True
    )
    await message.reply_text("✅ زبان ربات در این گروه بازنشانی شد.")

@nexichat.on_message(filters.command(["فیلتر", "کلمه_ممنوع"], ""))
async def add_bad_word(client, message):
    """اضافه کردن کلمه به لیست فیلتر"""
    try:
        user_status = await message.chat.get_member(message.from_user.id)
        if user_status.status not in [CMS.OWNER, CMS.ADMINISTRATOR]:
            return await message.reply_text("❌ فقط ادمین‌ها می‌توانند کلمات نامناسب را مدیریت کنند!")

        if len(message.command) < 2:
            return await message.reply_text("❌ لطفاً کلمه مورد نظر را وارد کنید!\n\nمثال: فیلتر کلمه")

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

@nexichat.on_message(filters.command(["حذف_فیلتر", "حذف_کلمه"], ""))
async def remove_bad_word(client, message):
    """حذف کلمه از لیست فیلتر"""
    try:
        user_status = await message.chat.get_member(message.from_user.id)
        if user_status.status not in [CMS.OWNER, CMS.ADMINISTRATOR]:
            return await message.reply_text("❌ فقط ادمین‌ها می‌توانند کلمات نامناسب را مدیریت کنند!")

        if len(message.command) < 2:
            return await message.reply_text("❌ لطفاً کلمه مورد نظر را وارد کنید!\n\nمثال: حذف_فیلتر کلمه")

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

@nexichat.on_message(filters.command(["لیست_فیلتر", "کلمات_ممنوع"], ""))
async def list_bad_words(client, message):
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

@nexichat.on_message(filters.command(["ربات", "چت_ربات"], ""))
async def chatbot_settings(client, message):
    """تنظیمات چت‌بات"""
    await message.reply_text(
        f"💬 گروه: {message.chat.title}\n**لطفاً یک گزینه را برای فعال/غیرفعال کردن چت‌بات انتخاب کنید.**",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ فعال", callback_data="chatbot_on"),
             InlineKeyboardButton("❌ غیرفعال", callback_data="chatbot_off")]
        ])
    )

@nexichat.on_message(filters.command(["پخش", "ارسال_همگانی"], "") & filters.user(int(OWNER_ID)))
async def broadcast_message(client, message):
    """پخش پیام به همه گروه‌ها و کاربران"""
    global IS_BROADCASTING
    async with broadcast_lock:
        if IS_BROADCASTING:
            return await message.reply_text(
                "یک پخش همگانی در حال انجام است. لطفاً صبر کنید تا تمام شود."
            )

        IS_BROADCASTING = True
        try:
            query = message.text.split(None, 1)[1].strip()
        except IndexError:
            query = message.text.strip()
        except Exception as eff:
            return await message.reply_text(
                f"**خطا**: {eff}"
            )

        try:
            if message.reply_to_message:
                broadcast_content = message.reply_to_message
                broadcast_type = "reply"
                flags = {
                    "-pin": "-pin" in query,
                    "-pinloud": "-pinloud" in query,
                    "-nogroup": "-nogroup" in query,
                    "-user": "-user" in query,
                }
            else:
                if len(message.command) < 2:
                    return await message.reply_text(
                        "**لطفاً متن مورد نظر را بعد از دستور وارد کنید یا روی یک پیام ریپلای کنید.**"
                    )
                
                flags = {
                    "-pin": "-pin" in query,
                    "-pinloud": "-pinloud" in query,
                    "-nogroup": "-nogroup" in query,
                    "-user": "-user" in query,
                }

                for flag in flags:
                    query = query.replace(flag, "").strip()

                if not query:
                    return await message.reply_text(
                        "لطفاً یک پیام متنی معتبر یا یکی از پرچم‌های زیر را وارد کنید: -pin, -nogroup, -pinloud, -user"
                    )

                broadcast_content = query
                broadcast_type = "text"

            await message.reply_text("**شروع پخش همگانی...**")

            if not flags.get("-nogroup", False):
                sent = 0
                pin_count = 0
                chats = await get_served_chats()

                for chat in chats:
                    chat_id = int(chat["chat_id"])
                    if chat_id == message.chat.id:
                        continue
                    try:
                        if broadcast_type == "reply":
                            m = await nexichat.forward_messages(
                                chat_id, message.chat.id, [broadcast_content.id]
                            )
                        else:
                            m = await nexichat.send_message(
                                chat_id, text=broadcast_content
                            )
                        sent += 1

                        if flags.get("-pin", False) or flags.get("-pinloud", False):
                            try:
                                await m.pin(
                                    disable_notification=flags.get("-pin", False)
                                )
                                pin_count += 1
                            except Exception as e:
                                logger.error(
                                    f"خطا در پین کردن پیام در گروه {chat_id}: {e}"
                                )

                    except FloodWait as e:
                        flood_time = int(e.value)
                        logger.warning(
                            f"محدودیت فلود {flood_time} ثانیه برای گروه {chat_id}."
                        )
                        if flood_time > 200:
                            logger.info(
                                f"رد کردن گروه {chat_id} به دلیل محدودیت فلود زیاد."
                            )
                            continue
                        await asyncio.sleep(flood_time)
                    except Exception as e:
                        logger.error(f"خطا در ارسال به گروه {chat_id}: {e}")
                        continue

                await message.reply_text(
                    f"**پیام به {sent} گروه ارسال شد و در {pin_count} گروه پین شد.**"
                )

            if flags.get("-user", False):
                susr = 0
                users = await get_served_users()

                for user in users:
                    user_id = int(user["user_id"])
                    try:
                        if broadcast_type == "reply":
                            m = await nexichat.forward_messages(
                                user_id, message.chat.id, [broadcast_content.id]
                            )
                        else:
                            m = await nexichat.send_message(
                                user_id, text=broadcast_content
                            )
                        susr += 1

                    except FloodWait as e:
                        flood_time = int(e.value)
                        logger.warning(
                            f"محدودیت فلود {flood_time} ثانیه برای کاربر {user_id}."
                        )
                        if flood_time > 200:
                            logger.info(
                                f"رد کردن کاربر {user_id} به دلیل محدودیت فلود زیاد."
                            )
                            continue
                        await asyncio.sleep(flood_time)
                    except Exception as e:
                        logger.error(f"خطا در ارسال به کاربر {user_id}: {e}")
                        continue

                await message.reply_text(f"**پیام به {susr} کاربر ارسال شد.**")

        finally:
            IS_BROADCASTING = False

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
                except Exception as e:
                    logger.error(f"خطا در ارسال پاسخ: {e}")
                    await message.reply_text("متأسفانه در ارسال پاسخ مشکلی پیش آمد!")

        # ذخیره پیام و پاسخ اگر پیام ریپلای شده باشد
        if message.reply_to_message and not message.reply_to_message.from_user.is_bot:
            await save_reply(message.reply_to_message, message)

    except Exception as e:
        logger.error(f"خطا در پردازش پیام: {e}")

# پردازش کال‌بک‌های دکمه‌ها
@nexichat.on_callback_query()
async def callback_query(client: Client, callback: CallbackQuery):
    """پردازش کال‌بک‌های دکمه‌ها"""
    try:
        if callback.data.startswith("setlang_"):
            lang_code = callback.data.split("_")[1]
            chat_id = callback.message.chat.id
            
            await lang_db.update_one(
                {"chat_id": chat_id},
                {"$set": {"language": lang_code}},
                upsert=True
            )
            
            lang_name = next((name for name, code in languages.items() if code == lang_code), "نامشخص")
            await callback.message.edit_text(f"✅ زبان چت به {lang_name} تغییر کرد.")
            
        elif callback.data == "chatbot_on":
            chat_id = callback.message.chat.id
            await status_db.update_one(
                {"chat_id": chat_id},
                {"$set": {"status": "enabled"}},
                upsert=True
            )
            await callback.message.edit_text("✅ چت‌بات فعال شد!")
            
        elif callback.data == "chatbot_off":
            chat_id = callback.message.chat.id
            await status_db.update_one(
                {"chat_id": chat_id},
                {"$set": {"status": "disabled"}},
                upsert=True
            )
            await callback.message.edit_text("❌ چت‌بات غیرفعال شد!")
            
    except Exception as e:
        logger.error(f"خطا در پردازش کال‌بک: {e}")
        await callback.answer("خطایی رخ داد!", show_alert=True)

# راه‌اندازی اولیه
async def setup_chatbot():
    """راه‌اندازی اولیه چت‌بات"""
    try:
        await load_replies_cache()
        logger.info("کش پاسخ‌ها با موفقیت بارگذاری شد")
    except Exception as e:
        logger.error(f"خطا در راه‌اندازی چت‌بات: {e}")

# اجرای راه‌اندازی اولیه
nexichat.loop.create_task(setup_chatbot())
