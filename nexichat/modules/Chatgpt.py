import requests
from MukeshAPI import api
from pyrogram import filters, Client
from pyrogram.enums import ChatAction
from nexichat import nexichat as app


@Client.on_message(filters.command(["gemini", "ai", "ask", "chatgpt"]))
async def gemini_handler(client, message):
    # بررسی نوع ورودی پیام
    if (
        message.text.startswith(f"/gemini@{client.me.username}")
        and len(message.text.split(" ", 1)) > 1
    ):
        user_input = message.text.split(" ", 1)[1]
    elif message.reply_to_message and message.reply_to_message.text:
        user_input = message.reply_to_message.text
    else:
        if len(message.command) > 1:
            user_input = " ".join(message.command[1:])
        else:
            await message.reply_text("مثال: `/ask نخست وزیر هند کیست؟`")
            return

    # تلاش برای استفاده از API جمینی
    try:
        response = api.gemini(user_input)
        await client.send_chat_action(message.chat.id, ChatAction.TYPING)
        result = response.get("results")
        if result:
            await message.reply_text(result, quote=True)
            return
    except Exception as e:
        print(f"خطا در API جمینی: {str(e)}")
        pass

    # اگر جمینی کار نکرد، از Chat with AI استفاده می‌کنیم
    try:
        base_url = "https://chatwithai.codesearch.workers.dev/?chat="
        response = requests.get(base_url + user_input)
        if response and response.text.strip():
            await message.reply_text(response.text.strip(), quote=True)
        else:
            await message.reply_text("**در حال حاضر هر دو سرویس جمینی و Chat with AI در دسترس نیستند**")
    except Exception as e:
        print(f"خطا در Chat with AI: {str(e)}")
        await message.reply_text("**چت‌جی‌پی‌تی در حال حاضر در دسترس نیست. لطفاً بعداً تلاش کنید.**")


# کانال: @atrinmusic_tm
# مالک: @beblnn
