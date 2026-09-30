from __future__ import annotations

from abc import ABC


class InMemoryDB(ABC):
    """
    `InMemoryDB` interface.
    Default implementations return placeholder values; override every method
    in `InMemoryDBImpl` (in_memory_db_impl.py).
    """

# @@LEVEL 1@@
    def set(self, key: str, field: str, value: str) -> None:
        """
        Should insert a field-value pair into the record `key` (overwriting an
        existing field; creating the record if needed).
        """
        # default implementation
        return None

    def get(self, key: str, field: str) -> str | None:
        """
        Should return the value of `field` in record `key`, or `None`.
        """
        # default implementation
        return None

    def delete(self, key: str, field: str) -> bool:
        """
        Should remove `field` from record `key`. Returns `True` if it existed.
        """
        # default implementation
        return False

# @@LEVEL 2@@
    def scan(self, key: str) -> list[str]:
        """
        Should return ["<field>(<value>)", ...] for record `key`, sorted by field.
        """
        # default implementation
        return []

    def scan_by_prefix(self, key: str, prefix: str) -> list[str]:
        """
        Same as `scan`, only fields starting with `prefix`.
        """
        # default implementation
        return []

# @@LEVEL 3@@
    def set_at(self, key: str, field: str, value: str, timestamp: int) -> None:
        """
        Timestamped `set`; the pair never expires.
        """
        # default implementation
        return None

    def set_at_with_ttl(self, key: str, field: str, value: str, timestamp: int, ttl: int) -> None:
        """
        Timestamped `set`; the pair lives during [timestamp, timestamp + ttl).
        """
        # default implementation
        return None

    def delete_at(self, key: str, field: str, timestamp: int) -> bool:
        """
        Timestamped `delete`; expired fields count as missing.
        """
        # default implementation
        return False

    def get_at(self, key: str, field: str, timestamp: int) -> str | None:
        """
        Timestamped `get`.
        """
        # default implementation
        return None

    def scan_at(self, key: str, timestamp: int) -> list[str]:
        """
        Timestamped `scan`.
        """
        # default implementation
        return []

    def scan_by_prefix_at(self, key: str, prefix: str, timestamp: int) -> list[str]:
        """
        Timestamped `scan_by_prefix`.
        """
        # default implementation
        return []

# @@LEVEL 4@@
    def backup(self, timestamp: int) -> int:
        """
        Should save the state with remaining TTLs; returns the number of
        non-empty non-expired records.
        """
        # default implementation
        return 0

    def restore(self, timestamp: int, timestamp_to_restore: int) -> None:
        """
        Should restore the latest backup made at or before
        `timestamp_to_restore`, recalculating expirations from `timestamp`.
        """
        # default implementation
        return None
