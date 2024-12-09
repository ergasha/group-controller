from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from aiogram.utils import executor
import asyncio
from loader import bot
from loader import dp
from aiogram.types import chat_permissions
# Define restricted permissions
from aiogram.types import ChatPermissions
from data.config import CHANNELS
# Restrict permissions (no messages, media, or previews)
restricted_permissions = ChatPermissions(
    can_send_messages=False,
    can_send_media_messages=False,
    can_send_other_messages=False,
    can_add_web_page_previews=False
)

async def restrict_user(chat_id: int, user_id: int, duration_in_seconds: int):
    # Calculate restriction duration
    from datetime import datetime, timedelta
    until_date = datetime.now() + timedelta(seconds=duration_in_seconds)

    # Restrict the user
    await bot.restrict_chat_member(
        chat_id=chat_id,
        user_id=user_id,
        permissions=restricted_permissions,
        until_date=until_date
    )


unrestricted_permissions = ChatPermissions(
    can_send_messages=True,
    can_send_media_messages=True,
    can_send_other_messages=True,
    can_add_web_page_previews=True
)

async def unrestrict_user(chat_id: int, user_id: int):
    await bot.restrict_chat_member(
        chat_id=chat_id,
        user_id=user_id,
        permissions=unrestricted_permissions
    )


ban_keywords = [
    "bio", "bio yimda", "bio da", "bioda", "kanalim", "obuna", "kiring",
    "kanalimga", "profilimda", "lic", "lich", "licga", "lichga", "kanalimni",
    "kirin", "kirila", "kirilar", "profilda", "smm", "darslari", "tel", "http",
    "@", "zaybal", "gandon", "pizdes"
]

# Welcome message
@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    if message.chat.type == "private":
        await message.answer("Salom bu bot faqat guruhlarda ishlaydi!")

# Message handler for groups
@dp.message_handler(content_types=["text"])
async def handle_group_message(message: types.Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text.lower()
    if any(ban in text for ban in ban_keywords) and str(chat_id) not in CHANNELS:
        await bot.delete_message(chat_id=chat_id, message_id=message.message_id)
        await restrict_user(chat_id,user_id=message.from_user.id,duration_in_seconds=20)

    await asyncio.sleep(20)
    await unrestrict_user(chat_id=chat_id, user_id=message.from_user.id)
    if str(chat_id) not in CHANNELS:
        for channel_id in CHANNELS:
            member_status = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
            if member_status.status in ["member", "administrator", "creator"]:
                break
        else:
            await bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user_id,
                permissions=restricted_permissions,
                until_date=int(message.date.timestamp()) + 60
            )
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton("📡 Kanalga kirish", url="https://t.me/+6YL0hlAod1FkMGJi")]
                ]
            )
            await bot.send_message(
                chat_id=chat_id,
                text=f"*Assalomu alaykum!* [{message.from_user.first_name}](tg://user?id={user_id}), "
                     f"*siz guruhda yozish uchun* [PSIXOLOGIK TEST](https://t.me/+6YL0hlAod1FkMGJi) "
                     f"*kanaliga obuna bo'lishingiz kerak. Shundan so'ng bemalol guruhda yozavering ☺️*",
                parse_mode="markdown",
                reply_markup=keyboard,
                disable_web_page_preview=True
            )
            await bot.delete_message(chat_id=chat_id, message_id=message.message_id)


