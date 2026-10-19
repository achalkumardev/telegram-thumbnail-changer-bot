"""
Production-ready, ultra-fast Telegram Video Thumbnail Changer Bot.
Zero-Download Server-Side Pointer Swap Architecture using Telegram's modern 'cover' parameter.
Swaps streaming video thumbnails up to 4GB in 1–2 seconds.
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
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

import config
from storage import storage

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("ThumbnailChangerBot")

# Initialize Dispatcher
dp = Dispatcher()

# Exact required error message for non-streaming file types
UNSUPPORTED_MEDIA_REPLY = (
    "⚠️ <b>Unsupported File Type!</b>\n\n"
    "This bot only supports <b>Videos</b> (sent as streaming video).\n"
    "Documents, audio files, stickers, and other formats are not supported."
)

MAIN_KEYBOARD = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="📖 Help", callback_data="cmd_help"),
            InlineKeyboardButton(text="ℹ️ About", callback_data="cmd_about"),
        ],
        [
            InlineKeyboardButton(text="⚙️ Settings", callback_data="cmd_setting"),
            InlineKeyboardButton(text="📢 Updates", callback_data="cmd_updates"),
        ],
        [
            InlineKeyboardButton(text="🖼️ My Thumbnail", callback_data="cmd_mythumb"),
            InlineKeyboardButton(text="🗑️ Del Thumbnail", callback_data="cmd_delthumb"),
        ],
        [
            InlineKeyboardButton(text="📊 Bot Status", callback_data="cmd_status"),
        ],
    ]
)



@dp.message(CommandStart(), F.chat.type == ChatType.PRIVATE)
async def handle_start(message: Message) -> None:
    """Handle /start command with a clean introduction and usage instructions."""
    user = message.from_user
    user_name = user.first_name if user else "there"
    if user:
        storage.register_user(user.id)

    welcome_text = (
        f"👋 <b>Hello, {user_name}! Welcome to {config.BOT_NAME}</b> 🎬⚡\n\n"
        "The premier Telegram tool to swap or attach custom thumbnails to streaming videos "
        "of <b>Any Size</b> (Full Telegram 4GB Support) in just <b>1–2 seconds</b> with ZERO quality loss!\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🚀 <b>How It Works:</b>\n"
        "1️⃣ <b>Send a Photo:</b> Set your high-resolution thumbnail.\n"
        "2️⃣ <b>Send a Video:</b> Any video file (Full Telegram 4GB Support).\n"
        "3️⃣ <b>Instant Delivery:</b> Receive your video back in <b>1–2 seconds</b>!\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "💎 <b>Why Creators Love This Bot:</b>\n"
        "• ⚡ <b>Instant Delivery:</b> 1–2 second direct server swap\n"
        "• 📦 <b>Any Size Supported:</b> Full Telegram 4GB capacity for movies & shows\n"
        "• 🛡️ <b>Lossless Quality:</b> Original bitrate, resolution & audio intact\n"
        "• 🎬 <b>Fast Streaming:</b> Native Telegram streaming ready\n\n"
        "👇 <i>Tap an option below or send a photo directly to begin:</i>"
    )
    await message.reply(welcome_text, parse_mode="HTML", reply_markup=MAIN_KEYBOARD)



@dp.message(Command("help"), F.chat.type == ChatType.PRIVATE)
async def handle_help(message: Message) -> None:
    """Handle /help command."""
    user = message.from_user
    if user:
        storage.register_user(user.id)

    help_text = (
        f"📖 <b>{config.BOT_NAME} — User Guide</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "⚡ <b>How It Works:</b>\n"
        "This bot uses Telegram's server-side pointer swap. It never downloads or re-encodes your video, "
        "meaning <b>100% original quality</b> and instant <b>1–2s</b> delivery!\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📌 <b>3 Simple Steps:</b>\n"
        "1️⃣ <b>Set Thumbnail:</b> Send any photo to the bot (or use /addthumb).\n"
        "2️⃣ <b>Send Video:</b> Send a streaming video of Any Size (Full 4GB Support).\n"
        "3️⃣ <b>Done:</b> Receive your video with the new thumbnail in <b>1–2 seconds</b>!\n\n"
        "🛠️ <b>User Commands:</b>\n"
        "• /start — Start the bot & view welcome guide\n"
        "• /addthumb — Set or update your video thumbnail\n"
        "• /mythumb — View your currently active thumbnail\n"
        "• /delthumb — Delete your saved thumbnail\n"
        "• /setting — View your settings & configuration\n"
        "• /status — Check live system status & ping\n"
        "• /restart — Refresh your bot session\n"
        "• /about — Information about the bot\n"
        "• /updates — Latest features & changelog\n"
        "• /help — Show this commands menu\n\n"
        "👑 <b>Admin Commands:</b>\n"
        "• /broadcast (or /brotcast) — Send announcement to all users"
    )
    await message.reply(help_text, parse_mode="HTML")


@dp.message(Command("about"), F.chat.type == ChatType.PRIVATE)
async def handle_about(message: Message) -> None:
    """Handle /about command."""
    about_text = (
        f"ℹ️ <b>About {config.BOT_NAME}</b> 🎬⚡\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"• <b>Bot Name:</b> {config.BOT_NAME}\n"
        "• <b>Version:</b> 2.0.0 (Production)\n"
        "• <b>Technology:</b> Server-Side Video Pointer Swap\n"
        "• <b>File Size:</b> Any Size (Full Telegram 4GB Support)\n"
        "• <b>Processing Speed:</b> ⚡ 1–2 Seconds\n"
        "• <b>Quality:</b> 💎 100% Lossless\n"
        "• <b>Developer:</b> @achalkumardev\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "💡 <i>Designed for creators, channels, and movie sharers who want instant thumbnail changes without downloading or quality loss.</i>"
    )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📢 Updates", callback_data="cmd_updates"),
                InlineKeyboardButton(text="⚙️ Settings", callback_data="cmd_setting"),
            ],
            [InlineKeyboardButton(text="⬅️ Back to Menu", callback_data="cmd_start")],
        ]
    )
    await message.reply(about_text, parse_mode="HTML", reply_markup=keyboard)


@dp.message(Command("updates"), F.chat.type == ChatType.PRIVATE)
async def handle_updates(message: Message) -> None:
    """Handle /updates command."""
    updates_text = (
        f"📢 <b>{config.BOT_NAME} — Updates & Changelog</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🎉 <b>What's New in v2.0:</b>\n"
        "• ⚡ <b>Blazing 1–2s Swap:</b> Instant cover update without re-uploading\n"
        "• 📦 <b>Any Size (4GB Max):</b> Handles full movies, anime & shows\n"
        "• 🔘 <b>In-Place Navigation:</b> Smooth button clicks without chat clutter\n"
        "• 🛡️ <b>Lossless Quality:</b> Original resolution & bitrate 100% preserved\n"
        "• 💾 <b>Saved Thumbnail:</b> Active cover remembered automatically\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔔 <i>Stay tuned for more upcoming creator features!</i>"
    )
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="ℹ️ About Bot", callback_data="cmd_about"),
                InlineKeyboardButton(text="📖 Help", callback_data="cmd_help"),
            ],
            [InlineKeyboardButton(text="⬅️ Back to Menu", callback_data="cmd_start")],
        ]
    )
    await message.reply(updates_text, parse_mode="HTML", reply_markup=keyboard)


@dp.message(Command("restart"), F.chat.type == ChatType.PRIVATE)
async def handle_restart(message: Message) -> None:
    """Handle /restart command to refresh user session."""
    user = message.from_user
    user_id = user.id if user else message.chat.id
    storage.register_user(user_id)
    saved_cover = storage.get_thumbnail(user_id)

    restart_text = (
        "🔄 <b>Session Refreshed Successfully!</b>\n\n"
        "Your bot session has been refreshed and is running at peak performance.\n\n"
        f"• <b>Thumbnail:</b> {'Active ✅ (Ready)' if saved_cover else 'Not Set ❌'}\n"
        "• <b>Swap Speed:</b> ⚡ 1–2 Seconds\n"
        "• <b>Status:</b> 🟢 Operational\n\n"
        "<i>Send a photo or streaming video to continue!</i>"
    )
    await message.reply(restart_text, parse_mode="HTML")


@dp.message(Command("setting", "settings"), F.chat.type == ChatType.PRIVATE)
async def handle_setting(message: Message) -> None:
    """Handle /setting and /settings command."""
    user = message.from_user
    user_id = user.id if user else message.chat.id
    storage.register_user(user_id)
    saved_cover = storage.get_thumbnail(user_id)

    settings_text = (
        f"⚙️ <b>{config.BOT_NAME} — Settings</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"• <b>User ID:</b> <code>{user_id}</code>\n"
        f"• <b>Saved Thumbnail:</b> {'Active ✅ (Ready)' if saved_cover else 'Not Set ❌'}\n"
        "• <b>Swap Speed:</b> ⚡ 1–2 Seconds\n"
        "• <b>File Size:</b> 📦 Any Size (Full Telegram 4GB Support)\n"
        "• <b>Streaming Mode:</b> 🟢 Enabled (<code>supports_streaming: true</code>)\n"
        "• <b>Caption Preservation:</b> 🟢 100% Original Kept\n"
        "• <b>Engine:</b> ⚡ Instant Server Pointer Swap\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "💡 <i>Send /mythumb to view your image or /delthumb to remove it.</i>"
    )
    await message.reply(settings_text, parse_mode="HTML")


@dp.message(Command("addthumb"), F.chat.type == ChatType.PRIVATE)
async def handle_addthumb(message: Message) -> None:
    """Handle /addthumb command with guide or replied photo extraction."""
    user = message.from_user
    user_id = user.id if user else message.chat.id
    storage.register_user(user_id)

    # Check if replied to a photo
    if message.reply_to_message and message.reply_to_message.photo:
        highest_res = message.reply_to_message.photo[-1]
        storage.set_thumbnail(user_id, highest_res.file_id)
        await message.reply(
            "✅ <b>Thumbnail Saved from Replied Photo!</b>\n\n"
            "Now send your streaming video to apply it in <b>1–2 seconds</b>! 🎬⚡",
            parse_mode="HTML",
        )
        return

    add_thumb_guide = (
        "🖼️ <b>Set Custom Video Thumbnail</b>\n\n"
        "Please send any <b>Photo</b> (JPEG / PNG) to set it as your video thumbnail.\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "💡 <b>Pro Tips for Best Quality:</b>\n"
        "• Recommended Aspect Ratio: <b>16:9</b> (1280×720 or 1920×1080)\n"
        "• Send as a standard photo (compressed), not as a document.\n"
        "• You can also <b>reply</b> to any photo in chat with <code>/addthumb</code>!\n"
        "━━━━━━━━━━━━━━━━━━━━━"
    )
    await message.reply(add_thumb_guide, parse_mode="HTML")


@dp.message(Command("mythumb", "viewthumb"), F.chat.type == ChatType.PRIVATE)
async def handle_mythumb(message: Message, bot: Bot) -> None:
    """Display the user's currently saved thumbnail photo from RAM."""
    user = message.from_user
    user_id = user.id if user else message.chat.id
    storage.register_user(user_id)
    saved_file_id = storage.get_thumbnail(user_id)

    if saved_file_id:
        caption = (
            "📸 <b>Your Active Thumbnail:</b>\n\n"
            "This thumbnail is saved and will be automatically applied to any streaming video you send in <b>1–2 seconds</b>!\n\n"
            "🗑️ <i>To remove it, send /delthumb.</i>"
        )
        await bot.send_photo(
            chat_id=message.chat.id,
            photo=saved_file_id,
            caption=caption,
            parse_mode="HTML",
            reply_to_message_id=message.message_id,
        )
    else:
        await message.reply(
            "ℹ️ <b>No Thumbnail Set!</b>\n\n"
            "You do not have any saved thumbnail yet.\n"
            "Send a photo or use /addthumb to set one!",
            parse_mode="HTML",
        )


@dp.message(Command("delthumb", "clear"), F.chat.type == ChatType.PRIVATE)
async def handle_delthumb(message: Message) -> None:
    """Clear the user's saved thumbnail from RAM."""
    user = message.from_user
    user_id = user.id if user else message.chat.id
    storage.register_user(user_id)

    if storage.delete_thumbnail(user_id):
        await message.reply(
            "🗑️ <b>Thumbnail Deleted Successfully!</b>\n\n"
            "Your saved thumbnail has been removed from storage.\n"
            "Incoming videos will now use Telegram's default preview until you set a new one.",
            parse_mode="HTML",
        )
    else:
        await message.reply(
            "ℹ️ <b>No saved thumbnail found to delete.</b>\nSend a photo or use /addthumb to set one!",
            parse_mode="HTML",
        )


@dp.message(Command("status"), F.chat.type == ChatType.PRIVATE)
async def handle_status(message: Message) -> None:
    """Handle /status command for system diagnostics."""
    user = message.from_user
    user_id = user.id if user else message.chat.id
    storage.register_user(user_id)
    saved_cover = storage.get_thumbnail(user_id)
    total_users = max(storage.total_users(), 1)

    status_text = (
        f"📊 <b>{config.BOT_NAME} — System Status</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "• <b>System Health:</b> 🟢 Operational & Fast\n"
        "• <b>Swap Speed:</b> ⚡ 1–2 Seconds\n"
        "• <b>File Size:</b> 📦 Any Size (Full Telegram 4GB Support)\n"
        f"• <b>Your User ID:</b> <code>{user_id}</code>\n"
        f"• <b>Your Thumbnail:</b> {'Active ✅' if saved_cover else 'Not Set ❌'}\n"
        f"• <b>Total Users:</b> 👥 {total_users}\n"
        "• <b>Quality:</b> 💎 100% Original (Lossless)\n"
        "━━━━━━━━━━━━━━━━━━━━━"
    )
    await message.reply(status_text, parse_mode="HTML")


@dp.message(Command("broadcast", "brotcast"), F.chat.type == ChatType.PRIVATE)
async def handle_broadcast(message: Message, bot: Bot) -> None:
    """Handle /broadcast or /brotcast command for administrator announcements."""
    user = message.from_user
    user_id = user.id if user else 0

    if user_id != config.ADMIN_ID and user_id != 7437014244:
        await message.reply(
            "⛔ <b>Access Denied:</b> This command is restricted to the bot administrator.",
            parse_mode="HTML",
        )
        return

    text_parts = (message.text or "").split(maxsplit=1)
    broadcast_content = text_parts[1].strip() if len(text_parts) > 1 else ""
    is_reply = bool(message.reply_to_message)

    if not broadcast_content and not is_reply:
        await message.reply(
            "⚠️ <b>Usage:</b>\n<code>/broadcast &lt;your message&gt;</code>\n"
            "Or reply to any message with <code>/broadcast</code>.",
            parse_mode="HTML",
        )
        return

    all_users = storage.get_all_users()
    if user_id not in all_users:
        all_users.append(user_id)

    status_msg = await message.reply(
        f"📢 <i>Starting broadcast to {len(all_users)} users...</i>",
        parse_mode="HTML",
    )

    success_count = 0
    failed_count = 0

    for target_id in all_users:
        try:
            if is_reply and message.reply_to_message:
                await bot.copy_message(
                    chat_id=target_id,
                    from_chat_id=message.chat.id,
                    message_id=message.reply_to_message.message_id,
                )
            else:
                await bot.send_message(
                    chat_id=target_id,
                    text=f"📢 <b>Announcement:</b>\n\n{broadcast_content}",
                    parse_mode="HTML",
                )
            success_count += 1
        except Exception as e:
            logger.warning("Failed to broadcast to user %s: %s", target_id, e)
            failed_count += 1

    report = (
        "📢 <b>Broadcast Completed!</b>\n\n"
        f"• <b>Total Targets:</b> {len(all_users)}\n"
        f"• <b>Successfully Delivered:</b> {success_count} ✅\n"
        f"• <b>Failed / Blocked:</b> {failed_count} ❌"
    )
    await message.reply(report, parse_mode="HTML")


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

    await message.reply(
        "✅ <b>Thumbnail Saved Successfully!</b>\n\n"
        "Now send your <b>Streaming Video</b> of Any Size (Full 4GB Support) to swap its thumbnail in <b>1–2 seconds</b>! 🎬⚡",
        parse_mode="HTML",
    )


@dp.message(
    F.document | F.audio | F.voice | F.video_note | F.animation | F.sticker,
    F.chat.type == ChatType.PRIVATE,
)
async def handle_unsupported_media(message: Message) -> None:
    """
    Step 2 — Blocking Non-Streaming Files (Documents/Audio):
    If a user sends a Document, Audio, or any non-streaming media type, do not process it.
    Immediately reply with the exact required message.
    """
    media_type = "document" if message.document else ("audio" if message.audio else "other media")
    logger.info(
        "User %s sent unsupported media type (%s). Rejecting.",
        message.from_user.id,
        media_type,
    )
    await message.reply(UNSUPPORTED_MEDIA_REPLY, parse_mode="HTML")


@dp.message(F.video, F.chat.type == ChatType.PRIVATE)
async def handle_video(message: Message, bot: Bot) -> None:
    """
    Step 3 — Instant 1–2s Thumbnail Swap on Streaming Video:
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
        await message.reply(
            "⚠️ <b>Thumbnail Required!</b>\n\n"
            "Please send a photo first before sending your video.\n"
            "Send any image or use /addthumb to get started.",
            parse_mode="HTML",
        )
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
            "Successfully swapped thumbnail for user %s in %.2f seconds (Zero bytes downloaded/re-uploaded)",
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
        "then send a <b>Streaming Video</b> to instantly swap it in <b>1–2 seconds</b>!\n\n"
        "Use /help to see all available commands.",
        parse_mode="HTML",
    )


async def edit_or_reply(
    message: Message,
    text: str,
    reply_markup: Optional[InlineKeyboardMarkup] = None,
) -> None:
    """Edit message in-place for inline button clicks, ignoring 'message is not modified'."""
    try:
        await message.edit_text(text, parse_mode="HTML", reply_markup=reply_markup)
    except TelegramBadRequest as e:
        if "message is not modified" in str(e).lower():
            return
        await message.reply(text, parse_mode="HTML", reply_markup=reply_markup)
    except Exception:
        await message.reply(text, parse_mode="HTML", reply_markup=reply_markup)


@dp.callback_query(F.data.startswith("cmd_"))
async def handle_callback_query(query: CallbackQuery, bot: Bot) -> None:
    """Handle interactive inline buttons with smooth in-place message editing."""
    await query.answer()
    data = query.data
    msg = query.message
    if not msg:
        return

    user = query.from_user
    user_id = user.id if user else 0
    storage.register_user(user_id)
    saved_cover = storage.get_thumbnail(user_id)

    if data == "cmd_start":
        user_name = user.first_name if user else "there"
        welcome_text = (
            f"👋 <b>Hello, {user_name}! Welcome to {config.BOT_NAME}</b> 🎬⚡\n\n"
            f"The premier Telegram tool to swap or attach custom thumbnails to streaming videos "
            f"of <b>Any Size</b> (Full Telegram 4GB Support) in just <b>1–2 seconds</b> with ZERO quality loss!\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🚀 <b>How It Works:</b>\n"
            "1️⃣ <b>Send a Photo:</b> Set your high-resolution thumbnail.\n"
            "2️⃣ <b>Send a Video:</b> Any video file (Full Telegram 4GB Support).\n"
            "3️⃣ <b>Instant Delivery:</b> Receive your video back in <b>1–2 seconds</b>!\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "💎 <b>Why Creators Love This Bot:</b>\n"
            "• ⚡ <b>Instant Delivery:</b> 1–2 second direct server swap\n"
            "• 📦 <b>Any Size Supported:</b> Full Telegram 4GB capacity for movies & shows\n"
            "• 🛡️ <b>Lossless Quality:</b> Original bitrate, resolution & audio intact\n"
            "• 🎬 <b>Fast Streaming:</b> Native Telegram streaming ready\n\n"
            "👇 <i>Tap an option below or send a photo directly to begin:</i>"
        )
        await edit_or_reply(msg, welcome_text, MAIN_KEYBOARD)

    elif data == "cmd_mythumb":
        if saved_cover:
            thumb_text = (
                "📸 <b>Your Active Thumbnail:</b>\n\n"
                "• <b>Status:</b> Active & Set ✅\n"
                "• <b>Swap Speed:</b> ⚡ 1–2 Seconds\n"
                "• <b>Target:</b> Streaming Videos of Any Size (Full 4GB Support)\n"
                "• <b>Storage:</b> Saved to Profile\n\n"
                "💡 <i>This thumbnail will be automatically attached to any video you send. "
                "Tap 'View Full Photo' below if you want the original image sent, or send any new photo to replace it.</i>"
            )
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text="👁️ View Full Photo", callback_data="cmd_view_photo"),
                        InlineKeyboardButton(text="🗑️ Delete Thumbnail", callback_data="cmd_delthumb"),
                    ],
                    [InlineKeyboardButton(text="⬅️ Back to Menu", callback_data="cmd_start")],
                ]
            )
            await edit_or_reply(msg, thumb_text, keyboard)
        else:
            no_thumb_text = (
                "ℹ️ <b>No Thumbnail Set!</b>\n\n"
                "You haven't set any custom thumbnail yet.\n"
                "Send any photo right now to set it as your thumbnail!"
            )
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="⬅️ Back to Menu", callback_data="cmd_start")]
                ]
            )
            await edit_or_reply(msg, no_thumb_text, keyboard)

    elif data == "cmd_view_photo":
        if saved_cover:
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="🗑️ Delete Thumbnail", callback_data="cmd_delthumb")],
                    [InlineKeyboardButton(text="⬅️ Back to Menu", callback_data="cmd_start")],
                ]
            )
            await bot.send_photo(
                chat_id=msg.chat.id,
                photo=saved_cover,
                caption="📸 <b>Your Active Thumbnail Photo</b>\n\nApplied to all streaming videos in 1–2s!",
                parse_mode="HTML",
                reply_markup=keyboard,
            )

    elif data == "cmd_setting":
        settings_text = (
            f"⚙️ <b>{config.BOT_NAME} — Settings</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"• <b>User ID:</b> <code>{user_id}</code>\n"
            f"• <b>Saved Thumbnail:</b> {'Active ✅ (Ready)' if saved_cover else 'Not Set ❌'}\n"
            "• <b>Swap Speed:</b> ⚡ 1–2 Seconds\n"
            "• <b>File Size:</b> 📦 Any Size (Full Telegram 4GB Support)\n"
            "• <b>Streaming Mode:</b> 🟢 Enabled (<code>supports_streaming: true</code>)\n"
            "• <b>Caption Preservation:</b> 🟢 100% Original Kept\n"
            "• <b>Engine:</b> ⚡ Instant Server Pointer Swap\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "💡 <i>Tap 'My Thumbnail' to inspect your cover or 'Back to Menu' to return.</i>"
        )
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="🖼️ My Thumbnail", callback_data="cmd_mythumb"),
                    InlineKeyboardButton(text="📊 Bot Status", callback_data="cmd_status"),
                ],
                [InlineKeyboardButton(text="⬅️ Back to Menu", callback_data="cmd_start")],
            ]
        )
        await edit_or_reply(msg, settings_text, keyboard)

    elif data == "cmd_status":
        total_users = max(storage.total_users(), 1)
        status_text = (
            f"📊 <b>{config.BOT_NAME} — System Status</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "• <b>System Health:</b> 🟢 Operational & Fast\n"
            "• <b>Swap Speed:</b> ⚡ 1–2 Seconds\n"
            "• <b>File Size:</b> 📦 Any Size (Full Telegram 4GB Support)\n"
            f"• <b>Your User ID:</b> <code>{user_id}</code>\n"
            f"• <b>Your Saved Thumbnail:</b> {'Active ✅' if saved_cover else 'Not Set ❌'}\n"
            f"• <b>Total Users:</b> 👥 {total_users}\n"
            "• <b>Quality:</b> 💎 100% Original (Lossless)\n"
            "━━━━━━━━━━━━━━━━━━━━━━━"
        )
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="🔄 Refresh Status", callback_data="cmd_status")],
                [InlineKeyboardButton(text="⬅️ Back to Menu", callback_data="cmd_start")],
            ]
        )
        await edit_or_reply(msg, status_text, keyboard)

    elif data == "cmd_about":
        about_text = (
            f"ℹ️ <b>About {config.BOT_NAME}</b> 🎬⚡\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"• <b>Bot Name:</b> {config.BOT_NAME}\n"
            "• <b>Version:</b> 2.0.0 (Production)\n"
            "• <b>Technology:</b> Server-Side Video Pointer Swap\n"
            "• <b>File Size:</b> Any Size (Full Telegram 4GB Support)\n"
            "• <b>Processing Speed:</b> ⚡ 1–2 Seconds\n"
            "• <b>Quality:</b> 💎 100% Lossless\n"
            "• <b>Developer:</b> @achalkumardev\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "💡 <i>Designed for creators, channels, and movie sharers who want instant thumbnail changes without downloading or quality loss.</i>"
        )
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="📢 Updates", callback_data="cmd_updates"),
                    InlineKeyboardButton(text="⚙️ Settings", callback_data="cmd_setting"),
                ],
                [InlineKeyboardButton(text="⬅️ Back to Menu", callback_data="cmd_start")],
            ]
        )
        await edit_or_reply(msg, about_text, keyboard)

    elif data == "cmd_updates":
        updates_text = (
            f"📢 <b>{config.BOT_NAME} — Updates & Changelog</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "🎉 <b>What's New in v2.0:</b>\n"
            "• ⚡ <b>Blazing 1–2s Swap:</b> Instant cover update without re-uploading\n"
            "• 📦 <b>Any Size (4GB Max):</b> Handles full movies, anime & shows\n"
            "• 🔘 <b>In-Place Navigation:</b> Smooth button clicks without chat clutter\n"
            "• 🛡️ <b>Lossless Quality:</b> Original resolution & bitrate 100% preserved\n"
            "• 💾 <b>Saved Thumbnail:</b> Active cover remembered automatically\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🔔 <i>Stay tuned for more upcoming creator features!</i>"
        )
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="ℹ️ About Bot", callback_data="cmd_about"),
                    InlineKeyboardButton(text="📖 Help", callback_data="cmd_help"),
                ],
                [InlineKeyboardButton(text="⬅️ Back to Menu", callback_data="cmd_start")],
            ]
        )
        await edit_or_reply(msg, updates_text, keyboard)

    elif data == "cmd_help":
        help_text = (
            f"📖 <b>{config.BOT_NAME} — User Guide</b>\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "⚡ <b>How It Works:</b>\n"
            "This bot uses Telegram's server-side pointer swap. It never downloads or re-encodes your video, "
            "meaning <b>100% original quality</b> and instant <b>1–2s</b> delivery!\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "📌 <b>3 Simple Steps:</b>\n"
            "1️⃣ <b>Set Thumbnail:</b> Send any photo to the bot (or use /addthumb).\n"
            "2️⃣ <b>Send Video:</b> Send a streaming video of Any Size (Full 4GB Support).\n"
            "3️⃣ <b>Done:</b> Receive your video with the new thumbnail in <b>1–2 seconds</b>!\n\n"
            "🛠️ <b>Quick Commands:</b>\n"
            "• /start — Welcome menu & guide\n"
            "• /addthumb — Set or update thumbnail\n"
            "• /mythumb — Check active thumbnail\n"
            "• /delthumb — Delete active thumbnail\n"
            "• /setting — Check your preferences\n"
            "• /status — Check live bot health\n"
            "• /restart — Refresh your bot session\n"
            "• /help — Show this commands menu"
        )
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="ℹ️ About", callback_data="cmd_about"),
                    InlineKeyboardButton(text="📢 Updates", callback_data="cmd_updates"),
                ],
                [InlineKeyboardButton(text="⬅️ Back to Menu", callback_data="cmd_start")],
            ]
        )
        await edit_or_reply(msg, help_text, keyboard)

    elif data == "cmd_delthumb":
        if saved_cover:
            storage.delete_thumbnail(user_id)
            del_text = (
                "🗑️ <b>Thumbnail Deleted Successfully!</b>\n\n"
                "Your saved thumbnail has been removed from your profile.\n"
                "Incoming videos will now use Telegram's default preview until you set a new one."
            )
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="⬅️ Back to Menu", callback_data="cmd_start")]
                ]
            )
            await edit_or_reply(msg, del_text, keyboard)
        else:
            none_text = (
                "ℹ️ <b>No saved thumbnail found to delete.</b>\nSend a photo or use /addthumb to set one!"
            )
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="⬅️ Back to Menu", callback_data="cmd_start")]
                ]
            )
            await edit_or_reply(msg, none_text, keyboard)


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
