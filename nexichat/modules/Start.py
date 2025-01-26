import asyncio
import logging
import random
from pyrogram.enums import ParseMode
from nexichat import nexichat
from datetime import datetime
from pymongo import MongoClient
from pyrogram.enums import ChatType
from pyrogram import Client, filters
from config import OWNER_ID, MONGO_URL, OWNER_USERNAME
from pyrogram.errors import FloodWait, ChatAdminRequired
from nexichat.database.chats import get_served_chats, add_served_chat
from nexichat.database.users import get_served_users, add_served_user
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from nexichat.modules.helpers import (
    START,
    START_BOT,
    PNG_BTN,
    CLOSE_BTN,
    HELP_BTN,
    HELP_BUTN,
    HELP_READ,
    HELP_START,
    SOURCE_READ,
)

STICKER = [
    "CAACAgUAAx0CYlaJawABBy4vZaieO6T-Ayg3mD-JP-f0yxJngIkAAv0JAALVS_FWQY7kbQSaI-geBA",
    "CAACAgUAAx0CYlaJawABBy4rZaid77Tf70SV_CfjmbMgdJyVD8sAApwLAALGXCFXmCx8ZC5nlfQeBA",
    "CAACAgUAAx0CYlaJawABBy4jZaidvIXNPYnpAjNnKgzaHmh3cvoAAiwIAAIda2lVNdNI2QABHuVVHgQ",
]


EMOJIOS = [
    "💣",
    "💥",
    "🪄",
    "🧨",
    "⚡",
    "🤡",
    "👻",
    "🎃",
    "🎩",
    "🕊",
]

BOT = "https://envs.sh/IL_.jpg"
IMG = [
    "https://graph.org/file/210751796ff48991b86a3.jpg",
    "https://graph.org/file/7b4924be4179f70abcf33.jpg",
    "https://graph.org/file/f6d8e64246bddc26b4f66.jpg",
    "https://graph.org/file/63d3ec1ca2c965d6ef210.jpg",
    "https://graph.org/file/9f12dc2a668d40875deb5.jpg",
    "https://graph.org/file/0f89cd8d55fd9bb5130e1.jpg",
    "https://graph.org/file/e5eb7673737ada9679b47.jpg",
    "https://graph.org/file/2e4dfe1fa5185c7ff1bfd.jpg",
    "https://graph.org/file/36af423228372b8899f20.jpg",
    "https://graph.org/file/c698fa9b221772c2a4f3a.jpg",
    "https://graph.org/file/61b08f41855afd9bed0ab.jpg",
    "https://graph.org/file/744b1a83aac76cb3779eb.jpg",
    "https://graph.org/file/814cd9a25dd78480d0ce1.jpg",
    "https://graph.org/file/e8b472bcfa6680f6c6a5d.jpg",
]



chatdb = MongoClient(MONGO_URL)
status_db = chatdb["ChatBotStatusDb"]["StatusCollection"]

async def set_default_status(chat_id):
    try:
        if not await status_db.find_one({"chat_id": chat_id}):
            await status_db.insert_one({"chat_id": chat_id, "status": "enabled"})
    except Exception as e:
        print(f"خطا در تنظیم وضعیت پیش‌فرض برای چت {chat_id}: {e}")

@nexichat.on_message(filters.new_chat_members)
async def welcomejej(client, message: Message):
    await add_served_chat(message.chat.id)
    await set_default_status(message.chat.id)
    users = len(await get_served_users())
    chats = len(await get_served_chats())
    try:
        for member in message.new_chat_members:
            if member.id == nexichat.id:
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(f"انتخاب زبان", callback_data="choose_lang")]])    
                await message.reply_photo(photo=random.choice(IMG), caption=START.format(nexichat.mention or "غیرقابل منشن", users, chats), reply_markup=reply_markup)
                chat = message.chat   
                try:
                    invitelink = await nexichat.export_chat_invite_link(message.chat.id)
                    link = f"[دریافت لینک]({invitelink})"
                except ChatAdminRequired:
                    link = "بدون لینک"
                    
                try:
                    groups_photo = await nexichat.download_media(
                        chat.photo.big_file_id, file_name=f"chatpp{chat.id}.png"
                    )
                    chat_photo = (
                        groups_photo if groups_photo else "https://envs.sh/IL_.jpg"
                    )
                except AttributeError:
                    chat_photo = "https://envs.sh/IL_.jpg"
                
                count = await nexichat.get_chat_members_count(chat.id)
                chats = len(await get_served_chats())
                username = chat.username if chat.username else "گروه خصوصی"
                msg = (
                    f"**📝 ربات به یک #گروه_جدید اضافه شد**\n\n"
                    f"**📌نام گروه:** {chat.title}\n"
                    f"**🍂شناسه گروه:** `{chat.id}`\n"
                    f"**🔐نام کاربری گروه:** @{username}\n"
                    f"**🖇️لینک گروه:** {link}\n"
                    f"**📈تعداد اعضا:** {count}\n"
                    f"**🤔اضافه شده توسط:** {message.from_user.mention}\n\n"
                    f"**تعداد کل گروه‌ها:** {chats}"
                )

                try:
                    owner_username = True
                    
                    if owner_username:
                        await nexichat.send_photo(
                            int(OWNER_ID),
                            photo=chat_photo,
                            caption=msg,
                            reply_markup=InlineKeyboardMarkup(
                                [
                                    [
                                        InlineKeyboardButton(
                                            f"{message.from_user.first_name}",
                                            user_id=message.from_user.id)]]))
                    else:
                        await nexichat.send_photo(
                            int(OWNER_ID),
                            photo=chat_photo,
                            caption=msg,
                            reply_markup=InlineKeyboardMarkup(
                                [
                                    [
                                        InlineKeyboardButton(
                                            f"{message.from_user.first_name}",
                                            user_id=message.from_user.id)]]))
                except Exception as e:
                    logging.info(f"Error fetching owner username: {e}")
                    await nexichat.send_photo(
                        int(OWNER_ID),
                        photo=chat_photo,
                        caption=msg,
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton(
                                        f"{message.from_user.first_name}",
                                        user_id=message.from_user.id)]]))

    except Exception as e:
        logging.info(f"Error: {e}")


@nexichat.on_cmd(["start", "aistart"])
async def start(_, m: Message):
    users = len(await get_served_users())
    chats = len(await get_served_chats())
    if m.chat.type == ChatType.PRIVATE:
        accha = await m.reply_text(
            text=random.choice(EMOJIOS),
        )
        await asyncio.sleep(0.5)
        
        # Animation text in Persian
        animations = [
            "**__در__**", "**__درح__**", "**__درحا__**", "**__درحال__**",
            "**__درحال ر__**", "**__درحال را__**", "**__درحال راه__**",
            "**__درحال راه ا__**", "**__درحال راه ان__**", "**__درحال راه اند__**",
            "**__درحال راه اندا__**", "**__درحال راه انداز__**", "**__درحال راه اندازی__**",
            "**__درحال راه اندازی...__**"
        ]
        
        for animation in animations:
            await accha.edit(animation)
            await asyncio.sleep(0.1)
        
        await accha.delete()
        
        umm = await m.reply_sticker(sticker=random.choice(STICKER))
        chat_photo = BOT  
        if m.chat.photo:
            try:
                userss_photo = await nexichat.download_media(m.chat.photo.big_file_id)
                await umm.delete()
                if userss_photo:
                    chat_photo = userss_photo
            except AttributeError:
                chat_photo = BOT  

        users = len(await get_served_users())
        chats = len(await get_served_chats())
        await m.reply_photo(photo=chat_photo, caption=START.format(nexichat.mention or "can't mention", users, chats), reply_markup=InlineKeyboardMarkup(START_BOT))
        await add_served_user(m.chat.id)
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(f"{m.chat.first_name}", user_id=m.chat.id)]])
        await nexichat.send_photo(int(OWNER_ID), photo=chat_photo, caption=f"{m.from_user.mention} ʜᴀs sᴛᴀʀᴛᴇᴅ ʙᴏᴛ. \n\n**ɴᴀᴍᴇ :** {m.chat.first_name}\n**ᴜsᴇʀɴᴀᴍᴇ :** @{m.chat.username}\n**ɪᴅ :** {m.chat.id}\n\n**ᴛᴏᴛᴀʟ ᴜsᴇʀs :** {users}", reply_markup=keyboard)
        
    else:
        await m.reply_photo(
            photo=random.choice(IMG),
            caption=START.format(nexichat.mention or "can't mention", users, chats),
            reply_markup=InlineKeyboardMarkup(HELP_START),
        )
        await add_served_chat(m.chat.id)


@nexichat.on_cmd("help")
async def help(client: nexichat, m: Message):
    if m.chat.type == ChatType.PRIVATE:
        hmm = await m.reply_photo(
            photo=random.choice(IMG),
            caption=HELP_READ,
            reply_markup=InlineKeyboardMarkup(HELP_BTN),
        )
    else:
        await m.reply_photo(
            photo=random.choice(IMG),
            caption="**برای دریافت راهنما به من پیام خصوصی بدهید!**",
            reply_markup=InlineKeyboardMarkup(HELP_BUTN),
        )
        await add_served_chat(m.chat.id)


@nexichat.on_cmd("repo")
async def repo(_, m: Message):
    await m.reply_text(
        text=SOURCE_READ,
        reply_markup=InlineKeyboardMarkup(CLOSE_BTN),
        disable_web_page_preview=True,
    )

@nexichat.on_cmd("ping")
async def ping(_, message: Message):
    start = datetime.now()
    loda = await message.reply_photo(
        photo=random.choice(IMG),
        caption="در حال بررسی...",
    )

    ms = (datetime.now() - start).microseconds / 1000
    await loda.edit_text(
        text=f"سلام عزیزم!!\n{nexichat.name} فعال است 🥀 و با پینگ\n➥ `{ms}` میلی‌ثانیه کار می‌کند\n\n<b>|| ساخته شده با ❣️ توسط [سازنده](https://t.me/{OWNER_USERNAME}) ||</b>",
        reply_markup=InlineKeyboardMarkup(PNG_BTN),
    )
    if message.chat.type == ChatType.PRIVATE:
        await add_served_user(message.from_user.id)
    else:
        await add_served_chat(message.chat.id)

@nexichat.on_message(filters.command("stats"))
async def stats(cli: Client, message: Message):
    users = len(await get_served_users())
    chats = len(await get_served_chats())
    await message.reply_text(
        f"""{(await cli.get_me()).mention} آمار ربات:

➻ **گروه‌ها:** {chats}
➻ **کاربران:** {users}"""
    )




@nexichat.on_cmd("id")
async def getid(client, message):
    chat = message.chat
    your_id = message.from_user.id
    message_id = message.id
    reply = message.reply_to_message

    text = f"**[شناسه پیام:]({message.link})** `{message_id}`\n"
    text += f"**[شناسه شما:](tg://user?id={your_id})** `{your_id}`\n"

    if not message.command:
        message.command = message.text.split()

    if len(message.command) == 2:
        try:
            split = message.text.split(None, 1)[1].strip()
            user_id = (await client.get_users(split)).id
            text += f"**[شناسه کاربر:](tg://user?id={user_id})** `{user_id}`\n"

        except Exception:
            return await message.reply_text("این کاربر وجود ندارد.", quote=True)

    text += f"**[شناسه گروه:](https://t.me/{chat.username})** `{chat.id}`\n\n"
    
    
    


@nexichat.on_message(
    filters.command(["broadcast", "gcast"]) & filters.user(int(OWNER_ID))
)
async def broadcast_message(client, message):
    global IS_BROADCASTING
    async with broadcast_lock:
        if IS_BROADCASTING:
            return await message.reply_text(
                "A broadcast is already in progress. Please wait for it to complete."
            )

        IS_BROADCASTING = True
        try:
            query = message.text.split(None, 1)[1].strip()
        except IndexError:
            query = message.text.strip()
        except Exception as eff:
            return await message.reply_text(
                f"**Error**: {eff}"
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
                        "**Please provide text after the command or reply to a message for broadcasting.**"
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
                        "Please provide a valid text message or a flag: -pin, -nogroup, -pinloud, -user"
                    )

                
                broadcast_content = query
                broadcast_type = "text"
            

            await message.reply_text("**Started broadcasting...**")

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
                                    f"Failed to pin message in chat {chat_id}: {e}"
                                )

                    except FloodWait as e:
                        flood_time = int(e.value)
                        logger.warning(
                            f"FloodWait of {flood_time} seconds encountered for chat {chat_id}."
                        )
                        if flood_time > 200:
                            logger.info(
                                f"Skipping chat {chat_id} due to excessive FloodWait."
                            )
                            continue
                        await asyncio.sleep(flood_time)
                    except Exception as e:
                        logger.error(f"Error broadcasting to chat {chat_id}: {e}")
                        continue

                await message.reply_text(
                    f"**Broadcasted to {sent} chats and pinned in {pin_count} chats.**"
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
                            f"FloodWait of {flood_time} seconds encountered for user {user_id}."
                        )
                        if flood_time > 200:
                            logger.info(
                                f"Skipping user {user_id} due to excessive FloodWait."
                            )
                            continue
                        await asyncio.sleep(flood_time)
                    except Exception as e:
                        logger.error(f"Error broadcasting to user {user_id}: {e}")
                        continue

                await message.reply_text(f"**Broadcasted to {susr} users.**")

        finally:
            IS_BROADCASTING = False
            
            
