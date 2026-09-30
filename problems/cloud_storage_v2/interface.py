from __future__ import annotations

from abc import ABC


class CloudStorage(ABC):
    """
    `CloudStorage` interface.
    Default implementations return placeholder values; override every method
    in `CloudStorageImpl` (cloud_storage_impl.py).
    """

# @@LEVEL 1@@
    def add_file(self, name: str, size: int) -> bool:
        """
        Should add a new file `name` of `size` bytes. Returns `False` if a file
        with that name already exists.
        """
        # default implementation
        return False

    def copy_file(self, name_from: str, name_to: str) -> bool:
        """
        Should copy file `name_from` to a new file `name_to`. Returns `False`
        if `name_from` doesn't exist or `name_to` already exists.
        """
        # default implementation
        return False

    def get_file_size(self, name: str) -> int | None:
        """
        Should return the size of file `name`, or `None` if it doesn't exist.
        """
        # default implementation
        return None

# @@LEVEL 2@@
    def find_file(self, prefix: str, suffix: str) -> list[str]:
        """
        Should return files whose names start with `prefix` and end with
        `suffix` as "<name>(<size>)", sorted by size descending, ties by name.
        """
        # default implementation
        return []

# @@LEVEL 3@@
    def add_user(self, user_id: str, capacity: int) -> bool:
        """
        Should add a new user with a storage limit of `capacity` bytes.
        Returns `False` if the user already exists.
        """
        # default implementation
        return False

    def add_file_by(self, user_id: str, name: str, size: int) -> int | None:
        """
        Should add a file owned by `user_id`. Returns remaining capacity, or
        `None` if the user doesn't exist, the name is taken, or the capacity
        would be exceeded.
        """
        # default implementation
        return None

    def update_capacity(self, user_id: str, capacity: int) -> int | None:
        """
        Should set the user's capacity, deleting the user's largest files
        (ties: lexicographically smaller name first) until they fit. Returns
        the number of deleted files, or `None` if the user doesn't exist.
        """
        # default implementation
        return None

# @@LEVEL 4@@
    def compress_file(self, user_id: str, name: str) -> int | None:
        """
        Should replace `name` with `name + ".COMPRESSED"` at half the size.
        Returns the user's remaining capacity, or `None` on failure.
        """
        # default implementation
        return None

    def decompress_file(self, user_id: str, name: str) -> int | None:
        """
        Should reverse `compress_file`. Returns the user's remaining capacity,
        or `None` on failure.
        """
        # default implementation
        return None
