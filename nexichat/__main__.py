import asyncio
import importlib

from pyrogram import filters, idle
from pyrogram.types import BotCommand, InlineKeyboardMarkup, InlineKeyboardButton
from config import OWNER_ID
from nexichat import LOGGER, nexichat
from nexichat.modules import ALL_MODULES

@nexichat.on_message(filters.command("panel") & filters.user(int(OWNER_ID)))
async def show_panel(client, message):
    panel_text = f"""**🔰 پنل راهنمای {nexichat.name}**

⚡️ به پنل راهنمای ربات خوش آمدید
📍 برای استفاده از دستورات، روی دکمه‌های زیر کلیک کنید

🤖 نام ربات: {nexichat.mention}
👤 شناسه ربات: `{nexichat.id}`
📝 یوزرنیم: @{nexichat.username}
⚡️ وضعیت: آنلاین ✅"""

    buttons = [
        [
            InlineKeyboardButton("⚜️ استارت ربات", callback_data="cmd_start"),
            InlineKeyboardButton("🔰 راهنمای دستورات", callback_data="cmd_help")
        ],
        [
            InlineKeyboardButton("🌐 تنظیم زبان", callback_data="cmd_lang"),
            InlineKeyboardButton("🔄 ریست زبان", callback_data="cmd_resetlang")
        ],
        [
            InlineKeyboardButton("📊 دریافت شناسه", callback_data="cmd_id"),
            InlineKeyboardButton("📢 ارسال همگانی", callback_data="cmd_gcast")
        ],
        [
            InlineKeyboardButton("🤖 چت‌بات", callback_data="cmd_chatbot"),
            InlineKeyboardButton("📝 متن زیبا", callback_data="cmd_shayri")
        ],
        [
            InlineKeyboardButton("❓ پرسش از هوش مصنوعی", callback_data="cmd_ask")
        ],
        [
            InlineKeyboardButton("👨‍💻 پشتیبانی", url="https://t.me/beblnn"),
            InlineKeyboardButton("📣 کانال ما", url="https://t.me/atrinmusic_tm")
        ],
        [
            InlineKeyboardButton("❌ بستن پنل", callback_data="close_panel")
        ]
    ]

    await message.reply_text(
        panel_text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@nexichat.on_callback_query()
async def panel_callback(client, callback_query):
    if callback_query.from_user.id != int(OWNER_ID):
        await callback_query.answer("شما دسترسی به این بخش را ندارید!", show_alert=True)
        return

    if callback_query.data == "cmd_start":
        text = """**🤖 دستور استارت**
• دستور: /start
• عملکرد: شروع کار با ربات
• توضیحات: با این دستور می‌توانید ربات را فعال کنید"""

    elif callback_query.data == "cmd_help":
        text = """**📚 دستور راهنما**
• دستور: /help
• عملکرد: نمایش راهنمای دستورات
• توضیحات: لیست تمام دستورات قابل استفاده"""

    elif callback_query.data == "cmd_lang":
        text = """**🌐 دستور تنظیم زبان**
• دستور: /lang
• عملکرد: تغییر زبان ربات
• توضیحات: انتخاب زبان مورد نظر برای ربات"""

    elif callback_query.data == "cmd_resetlang":
        text = """**🔄 دستور ریست زبان**
• دستور: /resetlang
• عملکرد: بازگشت به زبان پیش‌فرض
• توضیحات: تنظیم مجدد زبان به حالت اولیه"""

    elif callback_query.data == "cmd_id":
        text = """**📊 دستور شناسه**
• دستور: /id
• عملکرد: نمایش اطلاعات کاربر
• توضیحات: نمایش شناسه و مشخصات شما"""

    elif callback_query.data == "cmd_gcast":
        text = """**📢 دستور ارسال همگانی**
• دستور: /gcast
• عملکرد: ارسال پیام به تمام کاربران
• توضیحات: مخصوص مدیر ربات"""

    elif callback_query.data == "cmd_chatbot":
        text = """**🤖 دستور چت‌بات**
• دستور: /chatbot
• عملکرد: فعال/غیرفعال کردن ربات چت
• توضیحات: تنظیم وضعیت چت خودکار"""

    elif callback_query.data == "cmd_shayri":
        text = """**📝 دستور متن زیبا**
• دستور: /shayri
• عملکرد: دریافت متن‌های زیبا
• توضیحات: ارسال متن‌های تصادفی زیبا"""

    elif callback_query.data == "cmd_ask":
        text = """**❓ دستور پرسش از هوش مصنوعی**
• دستور: /ask یا /gemini
• عملکرد: پرسش از هوش مصنوعی
• توضیحات: پاسخ به سوالات شما با کمک AI"""

    elif callback_query.data == "close_panel":
        await callback_query.message.delete()
        return

    if callback_query.data != "close_panel":
        buttons = [
            [
                InlineKeyboardButton("🔙 برگشت به پنل", callback_data="back_to_panel"),
                InlineKeyboardButton("❌ بستن", callback_data="close_panel")
            ]
        ]
        try:
            await callback_query.message.edit_text(
                text,
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        except Exception as e:
            LOGGER.error(f"خطا در ویرایش پیام: {e}")

    elif callback_query.data == "back_to_panel":
        await show_panel(client, callback_query.message)

    await callback_query.answer()

async def anony_boot():
    try:
        await nexichat.start()
        LOGGER.info("ربات با موفقیت راه‌اندازی شد.")
    except Exception as ex:
        LOGGER.error(f"خطا در راه‌اندازی ربات: {ex}")
        quit(1)

    for all_module in ALL_MODULES:
        try:
            importlib.import_module("nexichat.modules." + all_module)
            LOGGER.info(f"ماژول با موفقیت بارگذاری شد: {all_module}")
        except Exception as ex:
            LOGGER.error(f"خطا در بارگذاری ماژول {all_module}: {ex}")

    bot_commands = [
        BotCommand("start", "استارت ربات"),
        BotCommand("help", "راهنمای دستورات"),
        BotCommand("lang", "انتخاب زبان ربات"),
        BotCommand("resetlang", "بازنشانی زبان به حالت پیش‌فرض"),
        BotCommand("id", "نمایش مشخصات و شناسه"),
        BotCommand("gcast", "ارسال پیام به همه گروه‌ها و کانال‌ها"),
        BotCommand("chatbot", "فعال/غیرفعال کردن ربات چت"),
        BotCommand("shayri", "دریافت متن‌های زیبا"),
        BotCommand("ask", "پرسش از هوش مصنوعی"),
        BotCommand("panel", "نمایش پنل راهنما")
    ]

    try:
        await nexichat.set_bot_commands(commands=bot_commands)
        LOGGER.info("دستورات ربات با موفقیت تنظیم شدند.")
    except Exception as ex:
        LOGGER.error(f"خطا در تنظیم دستورات ربات: {ex}")

    try:
        start_message = f"ربات {nexichat.mention} با موفقیت راه‌اندازی شد."
        await nexichat.send_message(int(OWNER_ID), start_message)
        LOGGER.info(f"@{nexichat.username} شروع به کار کرد.")
    except Exception as ex:
        LOGGER.warning(f"نتوانستم به مالک پیام بدهم: {ex}")
        LOGGER.info(f"@{nexichat.name} راه‌اندازی شد. لطفاً ربات را از آیدی مالک استارت کنید.")
    
    await idle()

if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(anony_boot())
    except KeyboardInterrupt:
        pass
    finally:
        LOGGER.info("ربات nexichat در حال خاموش شدن...")
