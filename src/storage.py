"""
In-Memory RAM Storage for Telegram Video Cover Changer Bot.
Maps user_id -> saved photo file_id directly in memory without any disk I/O.
Also tracks registered user IDs for broadcasts and status reporting.
"""

from typing import Dict, List, Optional, Set


class ThumbnailStorage:
    def __init__(self) -> None:
        # Maps user_id (int) -> photo file_id (str)
        self._cache: Dict[int, str] = {}
        # Set of known registered user IDs
        self._users: Set[int] = set()

    def register_user(self, user_id: int) -> None:
        """Register a user ID into the in-memory user registry."""
        self._users.add(user_id)

    def get_all_users(self) -> List[int]:
        """Return list of all registered user IDs."""
        return list(self._users)

    def total_users(self) -> int:
        """Return count of registered users."""
        return len(self._users)

    def set_thumbnail(self, user_id: int, file_id: str) -> None:
        """Save user's photo file_id in RAM."""
        self._cache[user_id] = file_id
        self._users.add(user_id)

    def get_thumbnail(self, user_id: int) -> Optional[str]:
        """Retrieve user's saved photo file_id from RAM."""
        return self._cache.get(user_id)

    def delete_thumbnail(self, user_id: int) -> bool:
        """Remove user's saved photo file_id from RAM."""
        return self._cache.pop(user_id, None) is not None

    def has_thumbnail(self, user_id: int) -> bool:
        """Check if user has a saved photo file_id in RAM."""
        return user_id in self._cache

    def count(self) -> int:
        """Return total number of users with saved thumbnails in RAM."""
        return len(self._cache)


# Global in-memory storage instance
storage = ThumbnailStorage()
