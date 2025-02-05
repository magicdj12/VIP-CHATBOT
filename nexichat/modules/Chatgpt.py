import requests
from MukeshAPI import api
from pyrogram import filters, Client
from pyrogram.enums import ChatAction
from nexichat import nexichat as app

# Define both English and Persian commands
COMMANDS = ["gemini", "ai", "ask", "chatgpt", "هوش_مصنوعی", "جمینی", "بپرس"]

@app.on_message(filters.command(COMMANDS) | filters.regex(r'^(جمینی|بپرس|هوش مصنوعی)'))
async def gemini_handler(client, message):
    try:
        # Get user input
        user_input = ""
        
        # Handle command with bot username
        if message.text and message.text.startswith(f"/gemini@{client.me.username}"):
            if len(message.text.split(" ", 1)) > 1:
                user_input = message.text.split(" ", 1)[1]
            else:
                await message.reply_text("مثال: `بپرس نارندرا مودی کیست؟` یا `/ask who is Narendra Modi`")
                return
                
        # Handle reply to message
        elif message.reply_to_message and message.reply_to_message.text:
            user_input = message.reply_to_message.text
            
        # Handle direct command
        elif message.text.startswith('/'):
            if len(message.command) > 1:
                user_input = " ".join(message.command[1:])
            else:
                await message.reply_text("مثال: `بپرس نارندرا مودی کیست؟` یا `/ask who is Narendra Modi`")
                return
                
        # Handle Persian text without slash
        else:
            text_parts = message.text.split(maxsplit=1)
            if len(text_parts) > 1:
                user_input = text_parts[1]
            else:
                await message.reply_text("لطفا سوال خود را بعد از دستور وارد کنید")
                return

        if not user_input:
            await message.reply_text("لطفا یک سوال یا متن وارد کنید")
            return

        # Send typing action
        await client.send_chat_action(message.chat.id, ChatAction.TYPING)

        # Try Gemini API first
        try:
            response = api.gemini(user_input)
            if response and response.get("results"):
                await message.reply_text(response["results"], quote=True)
                return
        except Exception as e:
            print(f"Gemini API Error: {str(e)}")

        # If Gemini fails, try the alternative API
        try:
            base_url = "https://open.wiki-api.ir/apis-2/ChatGPT4/?chat="
            response = requests.get(base_url + user_input, timeout=30)
            response.raise_for_status()  # Raise exception for bad status codes
            
            if response.text.strip():
                await message.reply_text(response.text.strip(), quote=True)
            else:
                raise Exception("Empty response")
                
        except Exception as e:
            print(f"Alternative API Error: {str(e)}")
            await message.reply_text(
                "**در حال حاضر هر دو سرویس Gemini و Chat با AI در دسترس نیستند**\n\n"
                "**Both Gemini and Chat with AI are currently unavailable**"
            )

    except Exception as e:
        print(f"Main Handler Error: {str(e)}")
        await message.reply_text(
            "**خطایی رخ داد. لطفا دوباره تلاش کنید**\n\n"
            "**An error occurred. Please try again.**"
        )
