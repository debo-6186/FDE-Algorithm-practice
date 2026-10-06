from __future__ import annotations

from cloud_storage import CloudStorage

ADMIN = "admin"
SUFFIX = ".COMPRESSED"


class File:
    def __init__(self, name: str, size: int, owner: str, original_size: int | None = None):
        self.name = name
        self.size = size
        self.owner = owner
        self.original_size = original_size    # set only for compressed files


class User:
    def __init__(self, user_id: str, capacity: int | None):
        self.id = user_id
        self.capacity = capacity              # None = unlimited (admin)
        self.used = 0

    def fits(self, extra: int) -> bool:
        return self.capacity is None or self.used + extra <= self.capacity

    def remaining(self) -> int | None:
        return None if self.capacity is None else self.capacity - self.used


class CloudStorageImpl(CloudStorage):

    def __init__(self):
        self.files: dict[str, File] = {}
        self.users: dict[str, User] = {ADMIN: User(ADMIN, None)}

    # ---- primitives ----------------------------------------------------------
    def _put(self, f: File) -> None:
        self.files[f.name] = f
        self.users[f.owner].used += f.size

    def _remove(self, name: str) -> File:
        f = self.files.pop(name)
        self.users[f.owner].used -= f.size
        return f

    def _owned(self, user_id: str, name: str) -> File | None:
        f = self.files.get(name)
        if user_id not in self.users or f is None or f.owner != user_id:
            return None
        return f

    # ---- Level 1 -------------------------------------------------------------
    def add_file(self, name: str, size: int) -> bool:
        if name in self.files:
            return False
        self._put(File(name, size, ADMIN))
        return True

    def copy_file(self, name_from: str, name_to: str) -> bool:
        src = self.files.get(name_from)
        if src is None or name_to in self.files:
            return False
        if not self.users[src.owner].fits(src.size):
            return False
        self._put(File(name_to, src.size, src.owner, src.original_size))
        return True

    def get_file_size(self, name: str) -> int | None:
        f = self.files.get(name)
        return f.size if f else None

    # ---- Level 2 -------------------------------------------------------------
    def find_file(self, prefix: str, suffix: str) -> list[str]:
        matches = [f for f in self.files.values() if f.name.startswith(prefix) and f.name.endswith(suffix)]
        matches.sort(key=lambda f: (-f.size, f.name))
        return [f"{f.name}({f.size})" for f in matches]

    # ---- Level 3 -------------------------------------------------------------
    def add_user(self, user_id: str, capacity: int) -> bool:
        if user_id in self.users:
            return False
        self.users[user_id] = User(user_id, capacity)
        return True

    def add_file_by(self, user_id: str, name: str, size: int) -> int | None:
        user = self.users.get(user_id)
        if user is None or name in self.files or not user.fits(size):
            return None
        self._put(File(name, size, user_id))
        return user.remaining()

    def update_capacity(self, user_id: str, capacity: int) -> int | None:
        user = self.users.get(user_id)
        if user is None:
            return None
        user.capacity = capacity
        mine = sorted((f for f in self.files.values() if f.owner == user_id), key=lambda f: (-f.size, f.name))
        removed = 0
        for f in mine:
            if user.used <= capacity:
                break
            self._remove(f.name)
            removed += 1
        return removed

    # ---- Level 4 -------------------------------------------------------------
    def compress_file(self, user_id: str, name: str) -> int | None:
        f = self._owned(user_id, name)
        if f is None or name.endswith(SUFFIX) or name + SUFFIX in self.files:
            return None
        self._remove(name)
        self._put(File(name + SUFFIX, f.size // 2, user_id, original_size=f.size))
        return self.users[user_id].remaining()

    def decompress_file(self, user_id: str, name: str) -> int | None:
        f = self._owned(user_id, name)
        if f is None or not name.endswith(SUFFIX) or f.original_size is None:
            return None
        original = name[: -len(SUFFIX)]
        user = self.users[user_id]
        if original in self.files or not user.fits(f.original_size - f.size):
            return None
        self._remove(name)
        self._put(File(original, f.original_size, user_id))
        return user.remaining()
