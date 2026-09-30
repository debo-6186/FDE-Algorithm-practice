from __future__ import annotations

from abc import ABC


class CloudStorage(ABC):
    """
    `CloudStorage` interface.
    Default implementations return placeholder values; override every method
    in `CloudStorageImpl` (cloud_storage_impl.py).
    """

# @@LEVEL 1@@
    def add_file(self, name: str, size: int, user_id: str) -> bool:
        """
        Should add a new file `name` to the storage. `size` is the amount of
        memory required in bytes. Fails if a file with the same `name` already
        exists. Returns `True` if the file was added, `False` otherwise.
        """
        # default implementation
        return False

    def get_file_size(self, name: str) -> int | None:
        """
        Should return the size of the file `name` if it exists, `None` otherwise.
        """
        # default implementation
        return None

    def delete_file(self, name: str) -> int | None:
        """
        Should delete the file `name`. Returns the deleted file's size, or
        `None` if the file does not exist.
        """
        # default implementation
        return None

# @@LEVEL 2@@
    def get_n_largest(self, prefix: str, n: int) -> list[str]:
        """
        Should return the top `n` largest files whose names start with
        `prefix`, formatted as "<name>(<size>)", sorted by size descending,
        ties by name ascending. Empty list if none.
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
        Should add a file owned by `user_id`. Returns the user's remaining
        capacity, or `None` if the user doesn't exist, the name is taken, or
        the capacity would be exceeded.
        """
        # default implementation
        return None

    def merge_user(self, user_id_1: str, user_id_2: str) -> int | None:
        """
        Should merge `user_id_2` into `user_id_1` (files + capacity) and delete
        `user_id_2`. Returns the remaining capacity of `user_id_1`, or `None`
        if either user doesn't exist or the ids are equal.
        """
        # default implementation
        return None

# @@LEVEL 4@@
    def backup_user(self, user_id: str) -> int | None:
        """
        Should back up all files owned by `user_id` (overwriting any previous
        backup). Returns the number of backed-up files, or `None` if the user
        doesn't exist.
        """
        # default implementation
        return None

    def restore_user(self, user_id: str) -> int | None:
        """
        Should replace the user's files with the latest backup (skipping names
        now used by other owners). Returns the number of restored files, or
        `None` if the user doesn't exist.
        """
        # default implementation
        return None
