import asyncio
import importlib

from pyrogram import idle
from pyrogram.types import BotCommand
from config import OWNER_ID
from nexichat import LOGGER, nexichat
from nexichat.modules import ALL_MODULES


async def anony_boot():
    try:
        await nexichat.start()
        LOGGER.info("ربات با موفقیت راه‌اندازی شد.")
    except Exception as ex:
        LOGGER.error(f"خطا در راه‌اندازی ربات: {ex}")
        quit(1)

    # ماژول‌ها را وارد می‌کنیم
    for all_module in ALL_MODULES:
        try:
            importlib.import_module("nexichat.modules." + all_module)
            LOGGER.info(f"ماژول با موفقیت بارگذاری شد: {all_module}")
        except Exception as ex:
            LOGGER.error(f"خطا در بارگذاری ماژول {all_module}: {ex}")

    # تنظیم دستورات ربات
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
    ]

    try:
        await nexichat.set_bot_commands(commands=bot_commands)
        LOGGER.info("دستورات ربات با موفقیت تنظیم شدند.")
    except Exception as ex:
        LOGGER.error(f"خطا در تنظیم دستورات ربات: {ex}")

    # اعلام راه‌اندازی به مالک
    try:
        start_message = f"ربات {nexichat.mention} با موفقیت راه‌اندازی شد."
        await nexichat.send_message(int(OWNER_ID), start_message)
        LOGGER.info(f"@{nexichat.username} شروع به کار کرد.")
    except Exception as ex:
        LOGGER.warning(f"نتوانستم به مالک پیام بدهم: {ex}")
        LOGGER.info(f"@{nexichat.first_name} راه‌اندازی شد. لطفاً ربات را از آیدی مالک استارت کنید.")
    
    await idle()


if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(anony_boot())
    except KeyboardInterrupt:
        pass
    finally:
        LOGGER.info("ربات nexichat در حال خاموش شدن...")

# کانال: @atrinmusic_tm
# مالک: @beblnn
