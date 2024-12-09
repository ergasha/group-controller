import asyncio
from datetime import datetime, timedelta

from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions

from data.config import CHANNELS
from loader import bot, dp

restricted_permissions = ChatPermissions(
    can_send_messages=False,
    can_send_media_messages=False,
    can_send_other_messages=False,
    can_add_web_page_previews=False
)

unrestricted_permissions = ChatPermissions(
    can_send_messages=True,
    can_send_media_messages=True,
    can_send_other_messages=True,
    can_add_web_page_previews=True
)

# Define banned keywords
BAN_KEYWORDS = [
    "bio", "bio yimda", "bio da", "bioda", "kanalim", "obuna", "kiring",
    "kanalimga", "profilimda", "lic", "lich", "licga", "lichga", "kanalimni",
    "kirin", "kirila", "kirilar", "profilda", "smm", "darslari", "tel", "http",
    "@", "zaybal", "gandon", "pizdes"
]


# Helper functions
async def restrict_user(chat_id: int, user_id: int, duration_in_seconds: int):
    until_date = datetime.now() + timedelta(seconds=duration_in_seconds)
    await bot.restrict_chat_member(
        chat_id=chat_id,
        user_id=user_id,
        permissions=restricted_permissions,
        until_date=until_date
    )


async def unrestrict_user(chat_id: int, user_id: int):
    await bot.restrict_chat_member(
        chat_id=chat_id,
        user_id=user_id,
        permissions=unrestricted_permissions
    )


async def is_user_in_channels(user_id: int) -> bool:
    for channel_id in CHANNELS:
        member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        if member.status in ["member", "administrator", "creator"]:
            return True
    return False


async def send_subscription_prompt(chat_id: int, user_id: int, user_name: str):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton("📡 Kanalga kirish", url="https://t.me/+6YL0hlAod1FkMGJi")]
        ]
    )
    await bot.send_message(
        chat_id=chat_id,
        text=f"*Assalomu alaykum!* [{user_name}](tg://user?id={user_id}), "
             f"*siz guruhda yozish uchun* [PSIXOLOGIK TEST](https://t.me/+6YL0hlAod1FkMGJi) "
             f"*kanaliga obuna bo'lishingiz kerak. Shundan so'ng bemalol guruhda yozavering ☺️*",
        parse_mode="markdown",
        reply_markup=keyboard,
        disable_web_page_preview=True
    )


async def handle_banned_words_or_links(message: types.Message):
    text = message.text.lower()
    chat_id = message.chat.id
    if message.sender_chat and message.sender_chat.id == int('-1001367202452'):
        print(message.sender_chat.id)
        return
    if any(keyword in text for keyword in BAN_KEYWORDS) or "http" in text or "@" in text:
        await bot.delete_message(chat_id=chat_id, message_id=message.message_id)
        await restrict_user(chat_id, message.from_user.id, 60)
        await asyncio.sleep(60)
        await unrestrict_user(chat_id, message.from_user.id)


async def handle_messages_from_channels(message: types.Message):
    if message.sender_chat and message.sender_chat.id not in map(int, CHANNELS):
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


# Handlers
@dp.message_handler(Command("start"))
async def send_welcome(message: types.Message):
    if message.chat.type == "private":
        await message.answer("Salom bu bot faqat guruhlarda ishlaydi!")


@dp.message_handler(content_types=["text"])
async def handle_group_message(message: types.Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    # 1. Check if the user is subscribed to required channels
    if not message.sender_chat and not await is_user_in_channels(user_id):
        await bot.delete_message(chat_id=chat_id, message_id=message.message_id)
        await restrict_user(chat_id, user_id, 60)
        await send_subscription_prompt(chat_id, user_id, user_name)
        return  # Exit after asking for subscription

    # 2. Check if the user is an admin or owner
    user_status = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
    if user_status.status in ["administrator", "creator"]:
        # Skip further checks for admins/owners
        return

    # 3. Check for banned keywords or links in the message
    await handle_banned_words_or_links(message)

    # 4. Check if the message is sent by a channel
    if message.sender_chat:
        if message.sender_chat.id not in map(int, CHANNELS):
            # Delete messages from unapproved channels
            await handle_messages_from_channels(message)
