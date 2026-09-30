from __future__ import annotations

import bisect

from file_hosting import FileHosting

SEARCH_LIMIT = 10


class FileHostingImpl(FileHosting):
    """
    State: name -> (size, expires_at or None).
    Every timestamped change also appends a snapshot (time, copy of state) so
    rollback can find "the state at time T" with a binary search.
    """

    def __init__(self):
        self.files: dict[str, tuple[int, int | None]] = {}
        self.snap_times: list[int] = []
        self.snaps: list[dict[str, tuple[int, int | None]]] = []

    # ---- helpers ---------------------------------------------------------------
    def _alive(self, name: str, timestamp: int | None) -> tuple[int, int | None] | None:
        rec = self.files.get(name)
        if rec is None:
            return None
        expires = rec[1]
        if timestamp is not None and expires is not None and timestamp >= expires:
            return None
        return rec

    def _save(self, timestamp: int) -> None:
        self.snap_times.append(timestamp)
        self.snaps.append(dict(self.files))       # values are immutable tuples -> shallow copy is enough

    def _search(self, prefix: str, timestamp: int | None) -> list[str]:
        hits = []
        for name in self.files:
            rec = self._alive(name, timestamp)
            if rec is not None and name.startswith(prefix):
                hits.append((rec[0], name))
        hits.sort(key=lambda sn: (-sn[0], sn[1]))
        return [name for _, name in hits[:SEARCH_LIMIT]]

    # ---- Level 1 ---------------------------------------------------------------
    def file_upload(self, file_name: str, size: int) -> None:
        if file_name in self.files:
            raise RuntimeError(f"file {file_name} already exists")
        self.files[file_name] = (size, None)

    def file_get(self, file_name: str) -> int | None:
        rec = self.files.get(file_name)
        return rec[0] if rec else None

    def file_copy(self, source: str, dest: str) -> None:
        if source not in self.files:
            raise RuntimeError(f"file {source} not found")
        self.files[dest] = self.files[source]

    # ---- Level 2 ---------------------------------------------------------------
    def file_search(self, prefix: str) -> list[str]:
        return self._search(prefix, None)

    # ---- Level 3 ---------------------------------------------------------------
    def file_upload_at(self, timestamp: int, file_name: str, file_size: int, ttl: int | None = None) -> None:
        if self._alive(file_name, timestamp) is not None:
            raise RuntimeError(f"file {file_name} already exists")
        self.files[file_name] = (file_size, None if ttl is None else timestamp + ttl)
        self._save(timestamp)

    def file_get_at(self, timestamp: int, file_name: str) -> int | None:
        rec = self._alive(file_name, timestamp)
        return rec[0] if rec else None

    def file_copy_at(self, timestamp: int, source: str, dest: str) -> None:
        rec = self._alive(source, timestamp)
        if rec is None:
            raise RuntimeError(f"file {source} not found")
        self.files[dest] = rec                     # same size, same expiry moment
        self._save(timestamp)

    def file_search_at(self, timestamp: int, prefix: str) -> list[str]:
        return self._search(prefix, timestamp)

    # ---- Level 4 ---------------------------------------------------------------
    def rollback(self, timestamp: int, time_to: int) -> None:
        i = bisect.bisect_right(self.snap_times, time_to)   # last snapshot taken at or before time_to
        base = self.snaps[i - 1] if i else {}
        restored: dict[str, tuple[int, int | None]] = {}
        for name, (size, expires) in base.items():
            if expires is None:
                restored[name] = (size, None)
            elif expires > time_to:                           # alive at time_to
                restored[name] = (size, timestamp + (expires - time_to))
        self.files = restored
        self._save(timestamp)
