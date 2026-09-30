from __future__ import annotations

import bisect

from in_memory_db import InMemoryDB

# A field is stored as (value, expires_at) where expires_at is None for "never".
Entry = tuple


class InMemoryDBImpl(InMemoryDB):

    def __init__(self):
        self.data: dict[str, dict[str, Entry]] = {}
        self.backup_times: list[int] = []
        self.backups: list[dict[str, dict[str, tuple[str, int | None]]]] = []   # remaining TTLs

    # ---- core helpers (timestamp None = "ignore expiry", used by Level 1-2) --
    @staticmethod
    def _alive(entry: Entry, timestamp: int | None) -> bool:
        expires = entry[1]
        return timestamp is None or expires is None or timestamp < expires

    def _set(self, key: str, field: str, value: str, expires: int | None) -> None:
        self.data.setdefault(key, {})[field] = (value, expires)

    def _get(self, key: str, field: str, timestamp: int | None) -> str | None:
        entry = self.data.get(key, {}).get(field)
        if entry is None or not self._alive(entry, timestamp):
            return None
        return entry[0]

    def _delete(self, key: str, field: str, timestamp: int | None) -> bool:
        if self._get(key, field, timestamp) is None:
            return False
        record = self.data[key]
        del record[field]
        if not record:
            del self.data[key]
        return True

    def _scan(self, key: str, prefix: str, timestamp: int | None) -> list[str]:
        record = self.data.get(key, {})
        fields = sorted(f for f, e in record.items() if f.startswith(prefix) and self._alive(e, timestamp))
        return [f"{f}({record[f][0]})" for f in fields]

    # ---- Level 1 ---------------------------------------------------------------
    def set(self, key: str, field: str, value: str) -> None:
        self._set(key, field, value, None)

    def get(self, key: str, field: str) -> str | None:
        return self._get(key, field, None)

    def delete(self, key: str, field: str) -> bool:
        return self._delete(key, field, None)

    # ---- Level 2 ---------------------------------------------------------------
    def scan(self, key: str) -> list[str]:
        return self._scan(key, "", None)

    def scan_by_prefix(self, key: str, prefix: str) -> list[str]:
        return self._scan(key, prefix, None)

    # ---- Level 3 ---------------------------------------------------------------
    def set_at(self, key: str, field: str, value: str, timestamp: int) -> None:
        self._set(key, field, value, None)

    def set_at_with_ttl(self, key: str, field: str, value: str, timestamp: int, ttl: int) -> None:
        self._set(key, field, value, timestamp + ttl)

    def delete_at(self, key: str, field: str, timestamp: int) -> bool:
        return self._delete(key, field, timestamp)

    def get_at(self, key: str, field: str, timestamp: int) -> str | None:
        return self._get(key, field, timestamp)

    def scan_at(self, key: str, timestamp: int) -> list[str]:
        return self._scan(key, "", timestamp)

    def scan_by_prefix_at(self, key: str, prefix: str, timestamp: int) -> list[str]:
        return self._scan(key, prefix, timestamp)

    # ---- Level 4 ---------------------------------------------------------------
    def backup(self, timestamp: int) -> int:
        snapshot: dict[str, dict[str, tuple[str, int | None]]] = {}
        for key, record in self.data.items():
            saved = {}
            for field, (value, expires) in record.items():
                if self._alive((value, expires), timestamp):
                    saved[field] = (value, None if expires is None else expires - timestamp)
            if saved:
                snapshot[key] = saved
        self.backup_times.append(timestamp)
        self.backups.append(snapshot)
        return len(snapshot)

    def restore(self, timestamp: int, timestamp_to_restore: int) -> None:
        i = bisect.bisect_right(self.backup_times, timestamp_to_restore) - 1   # latest backup <= target
        snapshot = self.backups[i]
        self.data = {
            key: {field: (value, None if remaining is None else timestamp + remaining)
                  for field, (value, remaining) in record.items()}
            for key, record in snapshot.items()
        }
