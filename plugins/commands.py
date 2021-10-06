import os
import random
import math 
import json
import time
import shutil
import heroku3
import requests

from pyrogram import filters
from pyrogram import Client as trojanz
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config

from script import Script
from plugins.helpers import humanbytes
from database.filters_mdb import filter_stats
from database.users_mdb import add_user, find_user, all_users
IMAGES = ["https://telegra.ph/file/314393aaed1b03f957409.jpg",
          "https://telegra.ph/file/6823951eaa6f22cf298e2.jpg",
          "https://telegra.ph/file/10d8e871deefae4dec1e0.jpg",
          "https://telegra.ph/file/f0d9ee6132bf24c80d367.jpg",
          "https://telegra.ph/file/5859fbb8cc806ed7e10fa.jpg",
          "https://telegra.ph/file/73e6c7f3f4b2b8960f917.jpg",
          "https://telegra.ph/file/0cd8cb678e8f4150f2e8f.jpg",
          "https://telegra.ph/file/d3855c9acc95d75beea62.jpg",
          "https://telegra.ph/file/4121acd67fecd03290f69.jpg",
          "https://telegra.ph/file/a90421aba858f3ddef70b.jpg",
          "https://telegra.ph/file/18105df34ec9194b10e4e.jpg",
          "https://telegra.ph/file/354adf112b69fe24c7e62.jpg",
          "https://telegra.ph/file/4f8b55f91cf71f34f4f97.jpg",
          "https://telegra.ph/file/43269746d95a9a6b8e659.jpg",
          "https://telegra.ph/file/0030564889c33f0994890.jpg",
          "https://telegra.ph/file/8fc2426b7379b45f8728a.jpg",
          "https://telegra.ph/file/f8230d6ca88f3552bc5f3.jpg",
          "https://telegra.ph/file/5c9a1632b55c106129923.jpg",
          "https://telegra.ph/file/c2e18f839d4947eef20fa.jpg",
          "https://telegra.ph/file/2c4a22e7eb6e5235b8060.jpg",
          "https://telegra.ph/file/2b1e0c393308d36e7dfb5.jpg",
          "https://telegra.ph/file/fe69ef822ac9a2407f627.jpg",
          "https://telegra.ph/file/55f047d6e44f65fe2a42d.jpg",
          "https://telegra.ph/file/e9e29826122ba9e65729b.jpg",
          "https://telegra.ph/file/48f6119b69c282bc897a0.jpg",
          "https://telegra.ph/file/912a344c89ef3202312bf.jpg",
          "https://telegra.ph/file/12800b3ab63524dd2d050.jpg",
          "https://telegra.ph/file/cf59ce50400a93ec39cc8.jpg",
          "https://telegra.ph/file/e6d7699c9f87da2d2b703.jpg",
          "https://telegra.ph/file/051536aac58cb87279783.jpg",]

@trojanz.on_message(filters.command('id') & (filters.private | filters.group))
async def showid(client, message):
    chat_type = message.chat.type

    if chat_type == "private":
        user_id = message.chat.id
        await message.reply_text(
            f"Your ID : `{user_id}`",
            parse_mode="md",
            quote=True
        )
    elif (chat_type == "group") or (chat_type == "supergroup"):
        user_id = message.from_user.id
        chat_id = message.chat.id
        if message.reply_to_message:
            reply_id = f"Replied User ID : `{message.reply_to_message.from_user.id}`"
        else:
            reply_id = ""
        await message.reply_text(
            f"Your ID : `{user_id}`\nThis Group ID : `{chat_id}`\n\n{reply_id}",
            parse_mode="md",
            quote=True
        )   


@trojanz.on_message(filters.command('info') & (filters.private | filters.group))
async def showinfo(client, message):
    try:
        cmd, id = message.text.split(" ", 1)
    except:
        id = False
        pass

    if id:
        if (len(id) == 10 or len(id) == 9):
            try:
                checkid = int(id)
            except:
                await message.reply_text("__Enter a valid USER ID__", quote=True, parse_mode="md")
                return
        else:
            await message.reply_text("__Enter a valid USER ID__", quote=True, parse_mode="md")
            return           

        if Config.SAVE_USER == "yes":
            name, username, dcid = await find_user(str(id))
        else:
            try:
                user = await client.get_users(int(id))
                name = str(user.first_name + (user.last_name or ""))
                username = user.username
                dcid = user.dc_id
            except:
                name = False
                pass

        if not name:
            await message.reply_text("__USER Details not found!!__", quote=True, parse_mode="md")
            return
    else:
        if message.reply_to_message:
            name = str(message.reply_to_message.from_user.first_name\
                    + (message.reply_to_message.from_user.last_name or ""))
            id = message.reply_to_message.from_user.id
            username = message.reply_to_message.from_user.username
            dcid = message.reply_to_message.from_user.dc_id
        else:
            name = str(message.from_user.first_name\
                    + (message.from_user.last_name or ""))
            id = message.from_user.id
            username = message.from_user.username
            dcid = message.from_user.dc_id
    
    if not str(username) == "None":
        user_name = f"@{username}"
    else:
        user_name = "none"

    await message.reply_text(
        f"<b>Name</b> : {name}\n\n"
        f"<b>User ID</b> : <code>{id}</code>\n\n"
        f"<b>Username</b> : {user_name}\n\n"
        f"<b>Permanant USER link</b> : <a href='tg://user?id={id}'>Click here!</a>\n\n"
        f"<b>DC ID</b> : {dcid}\n\n",
        quote=True,
        parse_mode="html"
    )


@trojanz.on_message((filters.private | filters.group) & filters.command('status'))
async def bot_status(client,message):
    if str(message.from_user.id) not in Config.AUTH_USERS:
        return

    chats, filters = await filter_stats()

    if Config.SAVE_USER == "yes":
        users = await all_users()
        userstats = f"> __**{users} users have interacted with your bot!**__\n\n"
    else:
        userstats = ""

    if Config.HEROKU_API_KEY:
        try:
            server = heroku3.from_key(Config.HEROKU_API_KEY)

            user_agent = (
                'Mozilla/5.0 (Linux; Android 10; SM-G975F) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/80.0.3987.149 Mobile Safari/537.36'
            )
            accountid = server.account().id
            headers = {
            'User-Agent': user_agent,
            'Authorization': f'Bearer {Config.HEROKU_API_KEY}',
            'Accept': 'application/vnd.heroku+json; version=3.account-quotas',
            }

            path = "/accounts/" + accountid + "/actions/get-quota"

            request = requests.get("https://api.heroku.com" + path, headers=headers)

            if request.status_code == 200:
                result = request.json()

                total_quota = result['account_quota']
                quota_used = result['quota_used']

                quota_left = total_quota - quota_used
                
                total = math.floor(total_quota/3600)
                used = math.floor(quota_used/3600)
                hours = math.floor(quota_left/3600)
                minutes = math.floor(quota_left/60 % 60)
                days = math.floor(hours/24)

                usedperc = math.floor(quota_used / total_quota * 100)
                leftperc = math.floor(quota_left / total_quota * 100)

                quota_details = f"""

**Heroku Account Status**

> __You have **{total} hours** of free dyno quota available each month.__

> __Dyno hours used this month__ ;
        - **{used} hours**  ( {usedperc}% )

> __Dyno hours remaining this month__ ;
        - **{hours} hours**  ( {leftperc}% )
        - **Approximately {days} days!**


"""
            else:
                quota_details = ""
        except:
            print("Check your Heroku API key")
            quota_details = ""
    else:
        quota_details = ""

    uptime = time.strftime("%Hh %Mm %Ss", time.gmtime(time.time() - Config.BOT_START_TIME))

    try:
        t, u, f = shutil.disk_usage(".")
        total = humanbytes(t)
        used = humanbytes(u)
        free = humanbytes(f)

        disk = "\n**Disk Details**\n\n" \
            f"> USED  :  {used} / {total}\n" \
            f"> FREE  :  {free}\n\n"
    except:
        disk = ""

    await message.reply_text(
        "**Current status of your bot!**\n\n"
        f"> __**{filters}** filters across **{chats}** chats__\n\n"
        f"{userstats}"
        f"> __BOT Uptime__ : **{uptime}**\n\n"
        f"{quota_details}"
        f"{disk}",
        quote=True,
        parse_mode="md"
    )


@trojanz.on_message(filters.command('start') & filters.private)
async def start(client, message):
    await message.reply_photo(
        photo = random.choice(IMAGES),
        caption=Script.START_MSG.format(message.from_user.mention),
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                   InlineKeyboardButton("❥︎ 𝑯𝒆𝒍𝒑", callback_data="help_data")
                ],
                [
                   InlineKeyboardButton("🥵 𝑮𝒓𝒐𝒖𝒑", url="https://t.me/dmx_chating_2_0"),
                   InlineKeyboardButton("🤢 𝑺𝒐𝒖𝒓𝒄𝒆", url="https://t.me/dmx_chating_2_0")
                ],
                [

                ]
            ]
        ),
        reply_to_message_id=message.message_id
    )
    if Config.SAVE_USER == "yes":
        try:
            await add_user(
                str(message.from_user.id),
                str(message.from_user.username),
                str(message.from_user.first_name + " " + (message.from_user.last_name or "")),
                str(message.from_user.dc_id)
            )
        except:
            pass


@trojanz.on_message(filters.command('help') & filters.private)
async def help(client, message):
    await message.reply_text(
        text=Script.HELP_MSG,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🥶 𝑮𝒓𝒐𝒖𝒑", url="https://t.me/dmx_chating_2_0"),
                    InlineKeyboardButton("🤢 𝑨𝒃𝒐𝒖𝒕 𝒎𝒆", callback_data="about_data")
                ],
                [
                    InlineKeyboardButton("☠︎︎ ᴍʏ ᴄʀᴇᴀᴛᴏʀ", url="https://t.me/basildmx2")
                ]
            ]
        ),
        reply_to_message_id=message.message_id
    )


@trojanz.on_message(filters.command('about') & filters.private)
async def about(client, message):
    await message.reply_text(
        text=Script.ABOUT_MSG,
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "❍ 𝑺𝒐𝒖𝒄𝒓𝒆 𝒄𝒐𝒅𝒆 ❍", url="https://t.me/dmx_chating_2_0")
                ],
                [
                    InlineKeyboardButton("🔙 𝙱𝚊𝚌𝚔", callback_data="help_data"),
                    InlineKeyboardButton("𝙲𝚕𝚘𝚜𝚎 🔐", callback_data="close_data")
                ]                
            ]
        ),
        reply_to_message_id=message.message_id
    )
