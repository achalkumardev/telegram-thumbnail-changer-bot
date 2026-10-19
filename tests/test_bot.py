"""
Comprehensive unit tests for Telegram Video Cover Changer Bot handlers.
Verifies message routing, unsupported media filtering, pointer swap payload creation, and commands.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.types import Chat, Message, PhotoSize, User, Video, Document, MessageEntity

import config
from bot import (
    handle_addthumb,
    handle_broadcast,
    handle_delthumb,
    handle_help,
    handle_mythumb,
    handle_photo,
    handle_restart,
    handle_setting,
    handle_start,
    handle_status,
    handle_unsupported_media,
    handle_video,
    UNSUPPORTED_MEDIA_REPLY,
)
from storage import ThumbnailStorage


@pytest.mark.asyncio
async def test_start_command_handler():
    """Verify that start command returns the welcome message."""
    user = User(id=777, is_bot=False, first_name="StartTester")
    chat = Chat(id=777, type="private")
    message = MagicMock(spec=Message)
    message.from_user = user
    message.chat = chat
    message.reply = AsyncMock()

    await handle_start(message)

    message.reply.assert_called_once()
    assert config.BOT_NAME in message.reply.call_args[0][0]
    assert "4GB" in message.reply.call_args[0][0]


@pytest.mark.asyncio
async def test_help_command_handler():
    """Verify that help command returns user instructions."""
    user = User(id=777, is_bot=False, first_name="HelpTester")
    chat = Chat(id=777, type="private")
    message = MagicMock(spec=Message)
    message.from_user = user
    message.chat = chat
    message.reply = AsyncMock()

    await handle_help(message)

    message.reply.assert_called_once()
    assert "User Guide & Commands" in message.reply.call_args[0][0]


@pytest.mark.asyncio
async def test_restart_command_handler():
    """Verify /restart resets session and returns status."""
    user = User(id=777, is_bot=False, first_name="RestartTester")
    chat = Chat(id=777, type="private")
    message = MagicMock(spec=Message)
    message.from_user = user
    message.chat = chat
    message.reply = AsyncMock()

    await handle_restart(message)

    message.reply.assert_called_once()
    assert "Bot Session Refreshed!" in message.reply.call_args[0][0]


@pytest.mark.asyncio
async def test_setting_command_handler():
    """Verify /setting displays user configuration."""
    user = User(id=777, is_bot=False, first_name="SettingTester")
    chat = Chat(id=777, type="private")
    message = MagicMock(spec=Message)
    message.from_user = user
    message.chat = chat
    message.reply = AsyncMock()

    await handle_setting(message)

    message.reply.assert_called_once()
    assert "Settings & Config" in message.reply.call_args[0][0]


@pytest.mark.asyncio
async def test_addthumb_command_handler():
    """Verify /addthumb guide message."""
    user = User(id=777, is_bot=False, first_name="AddTester")
    chat = Chat(id=777, type="private")
    message = MagicMock(spec=Message)
    message.from_user = user
    message.chat = chat
    message.reply_to_message = None
    message.reply = AsyncMock()

    await handle_addthumb(message)

    message.reply.assert_called_once()
    assert "Add Custom Video Thumbnail" in message.reply.call_args[0][0]


@pytest.mark.asyncio
async def test_mythumb_command_handler():
    """Verify /mythumb sends active photo or informative message."""
    mock_storage = ThumbnailStorage()
    with patch("bot.storage", mock_storage):
        user = User(id=888, is_bot=False, first_name="MyThumbTester")
        chat = Chat(id=888, type="private")
        message = MagicMock(spec=Message)
        message.from_user = user
        message.chat = chat
        message.message_id = 42
        message.reply = AsyncMock()
        mock_bot = AsyncMock()

        # No thumbnail initially
        await handle_mythumb(message, mock_bot)
        message.reply.assert_called_once()
        assert "No Thumbnail Set" in message.reply.call_args[0][0]

        # Set thumbnail and test
        mock_storage.set_thumbnail(888, "saved_photo_id")
        await handle_mythumb(message, mock_bot)
        mock_bot.send_photo.assert_called_once_with(
            chat_id=888,
            photo="saved_photo_id",
            caption=mock_bot.send_photo.call_args.kwargs["caption"],
            parse_mode="HTML",
            reply_to_message_id=42,
        )


@pytest.mark.asyncio
async def test_delthumb_command_handler():
    """Verify /delthumb removes saved thumbnail from storage."""
    mock_storage = ThumbnailStorage()
    with patch("bot.storage", mock_storage):
        user = User(id=555, is_bot=False, first_name="DelTester")
        chat = Chat(id=555, type="private")
        message = MagicMock(spec=Message)
        message.from_user = user
        message.chat = chat
        message.reply = AsyncMock()

        # Delete when none set
        await handle_delthumb(message)
        assert "No saved thumbnail found" in message.reply.call_args[0][0]

        # Delete when set
        mock_storage.set_thumbnail(555, "thumb_to_delete")
        message.reply.reset_mock()
        await handle_delthumb(message)
        assert "Thumbnail Deleted Successfully!" in message.reply.call_args[0][0]
        assert mock_storage.get_thumbnail(555) is None


@pytest.mark.asyncio
async def test_status_command_handler():
    """Verify /status displays bot diagnostics."""
    user = User(id=777, is_bot=False, first_name="StatusTester")
    chat = Chat(id=777, type="private")
    message = MagicMock(spec=Message)
    message.from_user = user
    message.chat = chat
    message.reply = AsyncMock()

    await handle_status(message)

    message.reply.assert_called_once()
    assert "System Status" in message.reply.call_args[0][0]


@pytest.mark.asyncio
async def test_broadcast_command_handler():
    """Verify admin-only broadcast command."""
    mock_storage = ThumbnailStorage()
    mock_storage.register_user(101)
    mock_storage.register_user(102)

    with patch("bot.storage", mock_storage), patch.object(config, "ADMIN_ID", 7437014244):
        # Non-admin attempt
        non_admin_user = User(id=999, is_bot=False, first_name="NonAdmin")
        message = MagicMock(spec=Message)
        message.from_user = non_admin_user
        message.reply = AsyncMock()
        mock_bot = AsyncMock()

        await handle_broadcast(message, mock_bot)
        assert "Access Denied" in message.reply.call_args[0][0]

        # Admin attempt
        admin_user = User(id=7437014244, is_bot=False, first_name="Admin")
        message.from_user = admin_user
        message.text = "/broadcast Important update!"
        message.reply_to_message = None
        message.reply.reset_mock()

        await handle_broadcast(message, mock_bot)
        assert mock_bot.send_message.call_count >= 2
        assert "Broadcast Completed!" in message.reply.call_args[0][0]


@pytest.mark.asyncio
async def test_photo_handler():
    """Verify that photo handler extracts highest res file_id and replies with exact message."""
    mock_storage = ThumbnailStorage()
    with patch("bot.storage", mock_storage):
        user = User(id=111, is_bot=False, first_name="Tester")
        chat = Chat(id=111, type="private")

        small_photo = PhotoSize(file_id="small_id", file_unique_id="s1", width=100, height=100)
        large_photo = PhotoSize(file_id="large_id_best", file_unique_id="l1", width=1280, height=720)

        message = MagicMock(spec=Message)
        message.from_user = user
        message.chat = chat
        message.photo = [small_photo, large_photo]
        message.reply = AsyncMock()

        await handle_photo(message)

        # Stored in RAM
        assert mock_storage.get_thumbnail(111) == "large_id_best"
        # Reply message
        assert "Thumbnail Saved!" in message.reply.call_args[0][0]


@pytest.mark.asyncio
async def test_unsupported_media_handler():
    """Verify that document/audio/etc. are blocked with exact required error message."""
    message = MagicMock(spec=Message)
    message.from_user = User(id=111, is_bot=False, first_name="Tester")
    message.chat = Chat(id=111, type="private")
    message.document = MagicMock(spec=Document)
    message.audio = None
    message.reply = AsyncMock()

    await handle_unsupported_media(message)

    message.reply.assert_called_once()
    assert "Unsupported File Type" in message.reply.call_args[0][0]


@pytest.mark.asyncio
async def test_video_handler_no_saved_thumbnail():
    """Verify prompt when sending video without prior thumbnail in RAM."""
    mock_storage = ThumbnailStorage()
    with patch("bot.storage", mock_storage):
        message = MagicMock(spec=Message)
        message.from_user = User(id=222, is_bot=False, first_name="NoThumbUser")
        message.chat = Chat(id=222, type="private")
        message.video = MagicMock(spec=Video)
        message.reply = AsyncMock()
        mock_bot = AsyncMock()

        await handle_video(message, mock_bot)

        message.reply.assert_called_once()
        assert "Please send a thumbnail photo first" in message.reply.call_args[0][0]
        mock_bot.send_video.assert_not_called()


@pytest.mark.asyncio
async def test_video_handler_pointer_swap():
    """Verify pointer swap calls send_video with video.file_id and cover=photo_file_id without download."""
    mock_storage = ThumbnailStorage()
    user_id = 333
    saved_cover_id = "AgACAgIAAxkBAAIC_PHOTO_COVER"
    mock_storage.set_thumbnail(user_id, saved_cover_id)

    with patch("bot.storage", mock_storage):
        user = User(id=user_id, is_bot=False, first_name="VideoUser")
        chat = Chat(id=user_id, type="private")

        video = Video(
            file_id="BAACAgIAAxkBAAIC_4GB_STREAMING_VIDEO",
            file_unique_id="v_unique",
            width=1920,
            height=1080,
            duration=3600,
            file_size=4294967296,  # 4GB
        )

        caption_entity = MessageEntity(type="bold", offset=0, length=5)

        message = MagicMock(spec=Message)
        message.from_user = user
        message.chat = chat
        message.video = video
        message.caption = "Awesome Video"
        message.caption_entities = [caption_entity]
        message.has_media_spoiler = True
        message.reply = AsyncMock()

        mock_bot = AsyncMock()

        await handle_video(message, mock_bot)

        # Ensure bot.send_video was called with the exact pointer swap parameters
        mock_bot.send_video.assert_called_once()
        kwargs = mock_bot.send_video.call_args.kwargs

        assert kwargs["chat_id"] == user_id
        assert kwargs["video"] == "BAACAgIAAxkBAAIC_4GB_STREAMING_VIDEO"
        assert kwargs["cover"] == saved_cover_id
        assert kwargs["supports_streaming"] is True
        assert kwargs["caption"] == "Awesome Video"
        assert kwargs["caption_entities"] == [caption_entity]
        assert kwargs["duration"] == 3600
        assert kwargs["width"] == 1920
        assert kwargs["height"] == 1080
        assert kwargs["has_spoiler"] is True
