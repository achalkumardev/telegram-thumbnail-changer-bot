"""Tests for in-memory RAM storage."""

from storage import ThumbnailStorage


def test_storage_lifecycle():
    """Verify in-memory RAM storage lifecycle operations."""
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
    assert st.count() == 0
