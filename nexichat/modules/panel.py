# در فایل nexichat/modules/panel.py

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from nexichat import nexichat, OWNER

# پنل راهنما
@nexichat.on_message(filters.command("panel") & filters.user(OWNER))
async def show_panel(_, message):
    panel_text = """**🔰 پنل راهنمای ربات نکسی**

⚡️ به پنل راهنمای ربات خوش آمدید
📍 برای استفاده از دستورات، روی دکمه‌های زیر کلیک کنید

🔸 وضعیت فعلی ربات: آنلاین ✅"""

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
async def panel_callback(_, callback_query):
    if callback_query.from_user.id != OWNER:
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
            print(f"Error in edit message: {e}")

    elif callback_query.data == "back_to_panel":
        await show_panel(_, callback_query.message)

    await callback_query.answer()
