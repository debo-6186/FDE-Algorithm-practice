from __future__ import annotations

from bisect import bisect_right

from parcel_tracking_system_interface import ParcelTrackingSystem

# A tag is stored as (value, expires_at) where expires_at is None for "never".
Entry = tuple


class ParcelTrackingSystemImpl(ParcelTrackingSystem):

    def __init__(self):
        self.parcels: dict[str, dict[str, Entry]] = {}
        # checkpoints in creation order (timestamps never decrease)
        self._cp_times: list[int] = []
        self._cp_states: list[dict[str, dict[str, Entry]]] = []

    # ---- core helpers (timestamp None = "ignore expiry", used by Level 1-2) --
    @staticmethod
    def _valid(entry: Entry, timestamp: int | None) -> bool:
        expires_at = entry[1]
        return timestamp is None or expires_at is None or timestamp < expires_at

    def _set(self, parcel_id: str, tag: str, value: str, expires_at: int | None) -> None:
        self.parcels.setdefault(parcel_id, {})[tag] = (value, expires_at)

    def _get(self, parcel_id: str, tag: str, timestamp: int | None) -> str | None:
        entry = self.parcels.get(parcel_id, {}).get(tag)
        if entry is None or not self._valid(entry, timestamp):
            return None
        return entry[0]

    def _remove(self, parcel_id: str, tag: str, timestamp: int | None) -> bool:
        tags = self.parcels.get(parcel_id)
        if tags is None or tag not in tags:
            return False
        was_valid = self._valid(tags[tag], timestamp)
        del tags[tag]
        if not tags:                         # a parcel with no tags no longer exists
            del self.parcels[parcel_id]
        return was_valid                     # removing an expired tag reports False

    def _list(self, parcel_id: str, prefix: str, timestamp: int | None) -> list[str]:
        tags = self.parcels.get(parcel_id, {})
        return [
            f"{tag}({tags[tag][0]})"
            for tag in sorted(tags)
            if tag.startswith(prefix) and self._valid(tags[tag], timestamp)
        ]

    # ---- Level 1 ------------------------------------------------------------
    def set_tag(self, parcel_id: str, tag: str, value: str) -> None:
        self._set(parcel_id, tag, value, None)

    def get_tag(self, parcel_id: str, tag: str) -> str | None:
        return self._get(parcel_id, tag, None)

    def remove_tag(self, parcel_id: str, tag: str) -> bool:
        return self._remove(parcel_id, tag, None)

    # ---- Level 2 ------------------------------------------------------------
    def list_tags(self, parcel_id: str) -> list[str]:
        return self._list(parcel_id, "", None)

    def list_tags_by_prefix(self, parcel_id: str, prefix: str) -> list[str]:
        return self._list(parcel_id, prefix, None)

    # ---- Level 3 ------------------------------------------------------------
    def set_tag_at(self, parcel_id: str, tag: str, value: str, timestamp: int) -> None:
        self._set(parcel_id, tag, value, None)

    def set_tag_with_hold(self, parcel_id: str, tag: str, value: str, timestamp: int, ttl: int) -> None:
        expires_at = timestamp + ttl if ttl > 0 else None    # ttl 0 = never expires
        self._set(parcel_id, tag, value, expires_at)

    def get_tag_at(self, parcel_id: str, tag: str, timestamp: int) -> str | None:
        return self._get(parcel_id, tag, timestamp)

    def remove_tag_at(self, parcel_id: str, tag: str, timestamp: int) -> bool:
        return self._remove(parcel_id, tag, timestamp)

    def list_tags_at(self, parcel_id: str, timestamp: int) -> list[str]:
        return self._list(parcel_id, "", timestamp)

    def list_tags_by_prefix_at(self, parcel_id: str, prefix: str, timestamp: int) -> list[str]:
        return self._list(parcel_id, prefix, timestamp)

    # ---- Level 4 ------------------------------------------------------------
    def checkpoint(self, timestamp: int) -> int:
        snapshot: dict[str, dict[str, Entry]] = {}
        for parcel_id, tags in self.parcels.items():
            alive = {t: e for t, e in tags.items() if self._valid(e, timestamp)}
            if alive:                        # only parcels with a valid tag are saved
                snapshot[parcel_id] = alive
        self._cp_times.append(timestamp)
        self._cp_states.append(snapshot)
        return len(snapshot)

    def restore_checkpoint(self, timestamp: int, timestamp_to_restore: int) -> None:
        i = bisect_right(self._cp_times, timestamp_to_restore) - 1   # latest at or before
        if i < 0:
            return                           # no checkpoint that early: no effect
        delta = timestamp - self._cp_times[i]
        # NEW dicts: later writes must never touch the stored checkpoint
        self.parcels = {
            parcel_id: {
                tag: (value, None if exp is None else exp + delta)
                for tag, (value, exp) in tags.items()
            }
            for parcel_id, tags in self._cp_states[i].items()
        }
