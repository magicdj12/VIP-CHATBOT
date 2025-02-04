import os
import requests
from pyrogram import filters, Client
from pyrogram.enums import ChatAction
from nexichat import nexichat

# استفاده از متغیرهای محیطی برای API keys
GEMINI_API = os.getenv("GEMINI_API", "AIzaSyDJR7hR9xqB4f0sPDVJBCbXDORAp7yuCQE")
RAPID_API = os.getenv("RAPID_API", "2a3a6d89c2msh19b7d65a0cd4dc9p1c7255jsn36aa05d28b63")

async def get_ai_response(query):
    try:
        url = "https://chatgpt-gpt4-ai-chatbot.p.rapidapi.com/ask"
        headers = {
            "content-type": "application/json",
            "X-RapidAPI-Key": RAPID_API,
            "X-RapidAPI-Host": "chatgpt-gpt4-ai-chatbot.p.rapidapi.com"
        }
        payload = {"query": query}
        response = requests.post(url, json=payload, headers=headers)
        return response.json().get('response', '')
    except Exception:
        # استفاده از API جایگزین اگر RapidAPI کار نکرد
        backup_url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={GEMINI_API}"
        payload = {
            "contents": [{"parts":[{"text": query}]}]
        }
        response = requests.post(backup_url, json=payload)
        return response.json().get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')

@nexichat.on_message(filters.command(["ask", "ai", "gpt"]))
async def ai_handler(client, message):
    try:
        if len(message.command) < 2 and not message.reply_to_message:
            return await message.reply_text(
                "**🤖 راهنمای استفاده:**\n"
                "**برای پرسیدن سوال:**\n"
                "`/ask سوال شما`\n\n"
                "**یا روی پیام مورد نظر ریپلای کنید و**\n"
                "`/ask` **را بفرستید**"
            )

        await client.send_chat_action(message.chat.id, ChatAction.TYPING)
        
        if message.reply_to_message:
            query = message.reply_to_message.text
        else:
            query = " ".join(message.command[1:])

        processing_msg = await message.reply_text("**🤖 در حال پردازش...**")
        
        response = await get_ai_response(query)
        
        if response:
            await processing_msg.edit_text(
                f"**💭 سوال:** {query}\n\n"
                f"**🤖 پاسخ:** {response}\n\n"
                "**👨‍💻 @Panel_Tornado**"
            )
        else:
            await processing_msg.edit_text("**❌ متأسفانه نتونستم پاسخی پیدا کنم!**")
            
    except Exception as e:
        await message.reply_text("**⚠️ مشکلی پیش اومد! لطفاً دوباره تلاش کنید.**")
