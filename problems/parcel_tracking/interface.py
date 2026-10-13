from __future__ import annotations

from abc import ABC


class ParcelTrackingSystem(ABC):
    """
    `ParcelTrackingSystem` interface.
    Default implementations return placeholder values; override every method
    in `ParcelTrackingSystemImpl` (parcel_tracking_system.py).
    """

# @@LEVEL 1@@
    def set_tag(self, parcel_id: str, tag: str, value: str) -> None:
        """
        Should set or overwrite `tag` to `value` for the parcel `parcel_id`.
        """
        # default implementation
        return None

    def get_tag(self, parcel_id: str, tag: str) -> str | None:
        """
        Should return the value of `tag` for the parcel `parcel_id`,
        or `None` if the parcel or the tag does not exist.
        """
        # default implementation
        return None

    def remove_tag(self, parcel_id: str, tag: str) -> bool:
        """
        Should remove `tag` from the parcel `parcel_id`.
        Returns `True` if the tag was removed, `False` if it did not exist.
        """
        # default implementation
        return False

# @@LEVEL 2@@
    def list_tags(self, parcel_id: str) -> list[str]:
        """
        Should return ["<tag>(<value>)", ...] for the parcel, sorted by tag name.
        Empty list if the parcel does not exist.
        """
        # default implementation
        return []

    def list_tags_by_prefix(self, parcel_id: str, prefix: str) -> list[str]:
        """
        Same as `list_tags`, only tags that start with `prefix`.
        """
        # default implementation
        return []

# @@LEVEL 3@@
    def set_tag_at(self, parcel_id: str, tag: str, value: str, timestamp: int) -> None:
        """
        Timestamped `set_tag`; a tag set this way does not expire unless overwritten.
        """
        # default implementation
        return None

    def get_tag_at(self, parcel_id: str, tag: str, timestamp: int) -> str | None:
        """
        Should return the value of `tag` as it was at `timestamp`;
        `None` if the tag did not exist or had expired.
        """
        # default implementation
        return None

    def remove_tag_at(self, parcel_id: str, tag: str, timestamp: int) -> bool:
        """
        Should remove `tag` only if it is valid at `timestamp`.
        """
        # default implementation
        return False

    def set_tag_with_hold(self, parcel_id: str, tag: str, value: str, timestamp: int, ttl: int) -> None:
        """
        Like `set_tag_at`, but the tag expires at `timestamp + ttl`.
        A `ttl` of 0 means the tag does not expire.
        """
        # default implementation
        return None

    def list_tags_at(self, parcel_id: str, timestamp: int) -> list[str]:
        """
        Timestamped `list_tags`: only tags valid at `timestamp`.
        """
        # default implementation
        return []

    def list_tags_by_prefix_at(self, parcel_id: str, prefix: str, timestamp: int) -> list[str]:
        """
        Timestamped `list_tags_by_prefix`.
        """
        # default implementation
        return []

# @@LEVEL 4@@
    def checkpoint(self, timestamp: int) -> int:
        """
        Should save the state of all parcels at `timestamp`.
        Returns the number of parcels that are alive (have at least one valid tag).
        """
        # default implementation
        return 0

    def restore_checkpoint(self, timestamp: int, timestamp_to_restore: int) -> None:
        """
        Should restore the latest checkpoint at or before `timestamp_to_restore`,
        shifting every finite expiration by `timestamp - checkpoint_timestamp`.
        """
        # default implementation
        return None
