"""
Comprehensive test suite for Telegram Video Cover Changer Bot.
Verifies storage, handler behavior, zero-download architecture, and Telegram API payload formatting.
"""

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiogram.types import Chat, Message, PhotoSize, User, Video, Document, Audio, MessageEntity

from bot import dp, handle_photo, handle_unsupported_media, handle_video, UNSUPPORTED_MEDIA_REPLY
from storage import ThumbnailStorage


def test_storage():
    """Verify in-memory RAM storage operations."""
    st = ThumbnailStorage()
    user_id = 999888
    file_id = "AgACAgIAAxkBAAIC123456"

    assert st.get_thumbnail(user_id) is None
    assert not st.has_thumbnail(user_id)
    assert st.count() == 0

    st.set_thumbnail(user_id, file_id)
    assert st.has_thumbnail(user_id)
    assert st.get_thumbnail(user_id) == file_id
    assert st.count() == 1

    # Overwrite with new photo
    new_file_id = "AgACAgIAAxkBAAIC789012"
    st.set_thumbnail(user_id, new_file_id)
    assert st.get_thumbnail(user_id) == new_file_id
    assert st.count() == 1

    # Delete
    assert st.delete_thumbnail(user_id) is True
    assert st.get_thumbnail(user_id) is None
    assert st.delete_thumbnail(user_id) is False


@pytest.mark.asyncio
async def test_photo_handler():
    """Verify that photo handler extracts highest res file_id and replies with exact message."""
    mock_storage = ThumbnailStorage()
    with patch("bot.storage", mock_storage):
        user = User(id=111, is_bot=False, first_name="Tester")
        chat = Chat(id=111, type="private")
        
        # Two resolutions: small and large
        small_photo = PhotoSize(file_id="small_id", file_unique_id="s1", width=100, height=100)
        large_photo = PhotoSize(file_id="large_id_best", file_unique_id="l1", width=1280, height=720)

        message = MagicMock(spec=Message)
        message.from_user = user
        message.chat = chat
        message.photo = [small_photo, large_photo]
        message.reply = AsyncMock()

        await handle_photo(message)

        # Check stored in RAM
        assert mock_storage.get_thumbnail(111) == "large_id_best"
        # Check reply message
        message.reply.assert_called_once_with("✅ Thumbnail Saved! Send your streaming video now.")


@pytest.mark.asyncio
async def test_unsupported_media_handler():
    """Verify that document/audio/etc. are blocked with exact error message."""
    message = MagicMock(spec=Message)
    message.from_user = User(id=111, is_bot=False, first_name="Tester")
    message.chat = Chat(id=111, type="private")
    message.document = MagicMock(spec=Document)
    message.audio = None
    message.reply = AsyncMock()

    await handle_unsupported_media(message)

    expected_msg = (
        "⚠️ Unsupported File Type!\n"
        "This bot only supports Videos (sent as streaming video).\n"
        "Documents, audio files, and other formats are not supported."
    )
    message.reply.assert_called_once_with(expected_msg)
    assert message.reply.call_args[0][0] == UNSUPPORTED_MEDIA_REPLY


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

        message.reply.assert_called_once_with(
            "⚠️ Please send a thumbnail photo first before sending a video!"
        )
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
            file_size=4294967296, # 4GB
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

        # Verify no file download or disk operation occurred
        assert not hasattr(mock_bot, "download_file") or not mock_bot.download_file.called


@pytest.mark.asyncio
async def test_start_command_handler():
    """Verify that start command returns the welcome message."""
    user = User(id=777, is_bot=False, first_name="StartTester")
    chat = Chat(id=777, type="private")
    message = MagicMock(spec=Message)
    message.from_user = user
    message.chat = chat
    message.reply = AsyncMock()

    from bot import handle_start
    await handle_start(message)

    message.reply.assert_called_once()
    assert "Thumbnail Changer Bot" in message.reply.call_args[0][0]
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

    from bot import handle_help
    await handle_help(message)

    message.reply.assert_called_once()
    assert "User Guide" in message.reply.call_args[0][0]




if __name__ == "__main__":
    import pytest
    pytest.main(["-v", __file__])
