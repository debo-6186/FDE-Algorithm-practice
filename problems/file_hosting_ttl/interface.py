from __future__ import annotations

from abc import ABC


class FileHosting(ABC):
    """
    `FileHosting` interface.
    Default implementations return placeholder values; override every method
    in `FileHostingImpl` (file_hosting_impl.py).
    """

# @@LEVEL 1@@
    def file_upload(self, file_name: str, size: int) -> None:
        """
        Should upload the file. Raises `RuntimeError` if a file with the same
        name already exists.
        """
        # default implementation
        return None

    def file_get(self, file_name: str) -> int | None:
        """
        Should return the size of the file, or `None` if it doesn't exist.
        """
        # default implementation
        return None

    def file_copy(self, source: str, dest: str) -> None:
        """
        Should copy `source` to `dest` (overwriting `dest`). Raises
        `RuntimeError` if `source` doesn't exist.
        """
        # default implementation
        return None

# @@LEVEL 2@@
    def file_search(self, prefix: str) -> list[str]:
        """
        Should return the names of the top 10 files starting with `prefix`,
        ordered by size descending, ties by name ascending.
        """
        # default implementation
        return []

# @@LEVEL 3@@
    def file_upload_at(self, timestamp: int, file_name: str, file_size: int, ttl: int | None = None) -> None:
        """
        Timestamped upload. With `ttl`, the file is alive during
        [timestamp, timestamp + ttl). Raises `RuntimeError` if a live file with
        the same name exists.
        """
        # default implementation
        return None

    def file_get_at(self, timestamp: int, file_name: str) -> int | None:
        """
        Timestamped get: `None` if missing or expired.
        """
        # default implementation
        return None

    def file_copy_at(self, timestamp: int, source: str, dest: str) -> None:
        """
        Timestamped copy. The copy expires together with the source. Raises
        `RuntimeError` if `source` is missing or expired.
        """
        # default implementation
        return None

    def file_search_at(self, timestamp: int, prefix: str) -> list[str]:
        """
        Timestamped search over files alive at `timestamp`.
        """
        # default implementation
        return []

# @@LEVEL 4@@
    def rollback(self, timestamp: int, time_to: int) -> None:
        """
        At `timestamp`, restore the storage to its state at `time_to`, keeping
        each restored file's remaining lifetime.
        """
        # default implementation
        return None
