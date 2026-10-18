"""
Production-ready, ultra-fast Telegram Video Cover/Thumbnail Changer Bot.
Zero-Download Server-Side Pointer Swap Architecture using Telegram's modern 'cover' parameter.
"""

import asyncio
import logging
import sys
import time
from pathlib import Path
from typing import Optional

# Ensure src/ and parent directory are on sys.path for robust imports
_SRC_DIR = Path(__file__).resolve().parent
_ROOT_DIR = _SRC_DIR.parent
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))
if str(_ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(_ROOT_DIR))

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ChatAction, ChatType
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

import config
from storage import storage

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("CoverBot")

# Initialize Dispatcher
dp = Dispatcher()

# Exact required error message for non-streaming file types
UNSUPPORTED_MEDIA_REPLY = (
    "⚠️ Unsupported File Type!\n"
    "This bot only supports Videos (sent as streaming video).\n"
    "Documents, audio files, and other formats are not supported."
)


@dp.message(CommandStart(), F.chat.type == ChatType.PRIVATE)
async def handle_start(message: Message) -> None:
    """Handle /start command with a clean introduction and usage instructions."""
    user = message.from_user
    user_name = user.first_name if user else "there"
    welcome_text = (
        f"👋 <b>Welcome, {user_name}, to {config.BOT_NAME}!</b> 🎬⚡\n\n"
        "I can instantly replace the cover / thumbnail of any streaming video "
        "(up to <b>4GB</b>) in 1–5 seconds using Telegram's server-side pointer swap.\n\n"
        "<b>📌 How it works:</b>\n"
        "1️⃣ <b>Send a Photo:</b> The bot will save it in RAM as your new cover.\n"
        "2️⃣ <b>Send a Streaming Video:</b> The bot will instantly return your video with the new cover applied!\n\n"
        "✨ <b>Features:</b>\n"
        "• <b>Zero Download & Zero Re-upload:</b> Instant round-trip (1–5 seconds)\n"
        "• <b>100% Quality Retention:</b> Original bitrate, resolution, audio & streaming flags preserved\n"
        "• <b>Caption Preservation:</b> Original caption and formatting are kept intact\n\n"
        "Send your thumbnail photo to get started! 🖼️"
    )
    await message.reply(welcome_text, parse_mode="HTML")


@dp.message(Command("help"), F.chat.type == ChatType.PRIVATE)
async def handle_help(message: Message) -> None:
    """Handle /help command."""
    help_text = (
        f"📖 <b>{config.BOT_NAME} - User Guide</b>\n\n"
        "<b>Step 1:</b> Send a photo you want to use as your thumbnail.\n"
        "<b>Step 2:</b> Send a video as a <i>Streaming Video</i> (not as a document/file).\n"
        "<b>Step 3:</b> Receive your video back within seconds with the new thumbnail!\n\n"
        "<b>Available Commands:</b>\n"
        "/start - Start the bot & show welcome message\n"
        "/help - Display this guide\n"
        "/viewthumb - View your currently saved thumbnail\n"
        "/clear - Delete your saved thumbnail from RAM"
    )
    await message.reply(help_text, parse_mode="HTML")


@dp.message(Command("viewthumb"), F.chat.type == ChatType.PRIVATE)
async def handle_view_thumb(message: Message, bot: Bot) -> None:
    """Display the user's currently saved thumbnail photo from RAM."""
    user_id = message.from_user.id
    saved_file_id = storage.get_thumbnail(user_id)
    if saved_file_id:
        await bot.send_photo(
            chat_id=message.chat.id,
            photo=saved_file_id,
            caption="📸 Here is your currently saved thumbnail photo in RAM.",
            reply_to_message_id=message.message_id,
        )
    else:
        await message.reply(
            "ℹ️ You do not have any saved thumbnail yet.\n"
            "Send a photo to save it as your new thumbnail!"
        )


@dp.message(Command("clear", "delthumb"), F.chat.type == ChatType.PRIVATE)
async def handle_clear_thumb(message: Message) -> None:
    """Clear the user's saved thumbnail from RAM."""
    user_id = message.from_user.id
    if storage.delete_thumbnail(user_id):
        await message.reply("🗑️ Saved thumbnail removed from RAM. Send a new photo anytime!")
    else:
        await message.reply("ℹ️ No saved thumbnail found to clear.")


@dp.message(F.photo, F.chat.type == ChatType.PRIVATE)
async def handle_photo(message: Message) -> None:
    """
    Step 1 — Receiving a Photo:
    Extract the highest-resolution photo.file_id, store it in RAM for that user,
    and immediately reply with the confirmation message.
    """
    user_id = message.from_user.id
    highest_res_photo = message.photo[-1]
    photo_file_id = highest_res_photo.file_id

    storage.set_thumbnail(user_id, photo_file_id)
    logger.info(
        "User %s stored thumbnail file_id: %s... (resolution %sx%s)",
        user_id,
        photo_file_id[:16],
        highest_res_photo.width,
        highest_res_photo.height,
    )

    await message.reply("✅ Thumbnail Saved! Send your streaming video now.")


@dp.message(
    F.document | F.audio | F.voice | F.video_note | F.animation | F.sticker,
    F.chat.type == ChatType.PRIVATE,
)
async def handle_unsupported_media(message: Message) -> None:
    """
    Step 2 — Blocking Non-Streaming Files (Documents/Audio):
    If a user sends a Document (such as a raw .mkv or .zip file sent as a document),
    Audio, or any non-streaming media type, do not process it.
    Immediately reply with the exact required message.
    """
    media_type = "document" if message.document else ("audio" if message.audio else "other media")
    logger.info(
        "User %s sent unsupported media type (%s). Rejecting.",
        message.from_user.id,
        media_type,
    )
    await message.reply(UNSUPPORTED_MEDIA_REPLY)


@dp.message(F.video, F.chat.type == ChatType.PRIVATE)
async def handle_video(message: Message, bot: Bot) -> None:
    """
    Step 3 — Instant 1–5s Cover Swap on Streaming Video:
    When a user sends a streaming video (message.video), check if they have a saved
    photo file_id in RAM. If not, prompt them to send a photo first.
    If a saved photo exists, immediately call Telegram's sendVideo endpoint passing
    the incoming video.file_id as the video parameter, the user's saved photo.file_id
    as the cover parameter, preserve the original caption if present, and keep
    supports_streaming enabled.
    """
    user_id = message.from_user.id
    saved_cover_file_id = storage.get_thumbnail(user_id)

    if not saved_cover_file_id:
        await message.reply("⚠️ Please send a thumbnail photo first before sending a video!")
        return

    start_time = time.monotonic()
    video = message.video

    logger.info(
        "Initiating pointer swap for user %s: video_file_id=%s... (%sx%s, %ss, size=%s bytes)",
        user_id,
        video.file_id[:16],
        video.width,
        video.height,
        video.duration,
        video.file_size,
    )

    # Indicate upload action in Telegram chat
    try:
        await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.UPLOAD_VIDEO)
    except Exception as e:
        logger.warning("Could not send chat action: %s", e)

    # Build payload parameters for sendVideo
    send_video_kwargs = {
        "chat_id": message.chat.id,
        "video": video.file_id,
        "cover": saved_cover_file_id,
        "supports_streaming": True,
    }

    # Preserve original caption and caption_entities if present
    if message.caption:
        send_video_kwargs["caption"] = message.caption
        if message.caption_entities:
            send_video_kwargs["caption_entities"] = message.caption_entities

    # Preserve duration and dimensions if available
    if video.duration:
        send_video_kwargs["duration"] = video.duration
    if video.width:
        send_video_kwargs["width"] = video.width
    if video.height:
        send_video_kwargs["height"] = video.height
    if message.has_media_spoiler:
        send_video_kwargs["has_spoiler"] = True

    try:
        # Zero-download pointer swap: only sends JSON pointers back to Telegram DC
        await bot.send_video(**send_video_kwargs)
        elapsed = time.monotonic() - start_time
        logger.info(
            "Successfully swapped cover for user %s in %.2f seconds (Zero bytes downloaded/re-uploaded)",
            user_id,
            elapsed,
        )
    except TelegramAPIError as e:
        logger.error("Telegram API Error during send_video for user %s: %s", user_id, e)
        await message.reply(
            f"❌ <b>Failed to update thumbnail:</b> {e.message}\n"
            "Please ensure your thumbnail is a valid image and try again.",
            parse_mode="HTML",
        )
    except Exception as e:
        logger.exception("Unexpected error during send_video for user %s: %s", user_id, e)
        await message.reply(
            "❌ An unexpected error occurred while processing your video. Please try again."
        )


@dp.message(F.text, F.chat.type == ChatType.PRIVATE)
async def handle_other_text(message: Message) -> None:
    """Handle general text messages with a friendly prompt."""
    await message.reply(
        "ℹ️ Send me a <b>Photo</b> first to save your thumbnail, "
        "then send a <b>Streaming Video</b> to instantly apply it!",
        parse_mode="HTML",
    )


async def main() -> None:
    """Initialize bot instance and start long polling."""
    logger.info("Starting %s with Zero-Download Pointer Swap Architecture...", config.BOT_NAME)
    
    bot = Bot(token=config.BOT_TOKEN)

    me = await bot.get_me()
    logger.info("Bot authenticated successfully: @%s (ID: %s)", me.username, me.id)

    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Dropped pending updates. Commencing polling...")

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()
        logger.info("Bot session closed.")


def main_entry() -> None:
    """Synchronous entry point for CLI command (coverbot) and __main__."""
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped cleanly.")


if __name__ == "__main__":
    main_entry()
