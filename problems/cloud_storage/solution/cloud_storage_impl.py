from __future__ import annotations

from cloud_storage import CloudStorage

ADMIN = "admin"


class File:
    def __init__(self, name: str, size: int, owner: str):
        self.name = name
        self.size = size
        self.owner = owner


class User:
    def __init__(self, user_id: str, capacity: int | None):
        self.id = user_id
        self.capacity = capacity            # None = unlimited (admin)
        self.used = 0
        self.files: set[str] = set()
        self.backup: dict[str, int] | None = None

    def remaining(self) -> int | None:
        return None if self.capacity is None else self.capacity - self.used


class CloudStorageImpl(CloudStorage):

    def __init__(self):
        self.files: dict[str, File] = {}
        self.users: dict[str, User] = {ADMIN: User(ADMIN, None)}

    # ---- primitives shared by every level -----------------------------------
    def _add(self, user_id: str, name: str, size: int) -> bool:
        user = self.users.get(user_id)
        if user is None or name in self.files:
            return False
        if user.capacity is not None and user.used + size > user.capacity:
            return False
        self.files[name] = File(name, size, user_id)
        user.used += size
        user.files.add(name)
        return True

    def _delete(self, name: str) -> int | None:
        f = self.files.pop(name, None)
        if f is None:
            return None
        owner = self.users[f.owner]
        owner.used -= f.size
        owner.files.discard(name)
        return f.size

    # ---- Level 1 -------------------------------------------------------------
    def add_file(self, name: str, size: int) -> bool:
        return self._add(ADMIN, name, size)

    def get_file_size(self, name: str) -> int | None:
        f = self.files.get(name)
        return f.size if f else None

    def delete_file(self, name: str) -> int | None:
        return self._delete(name)

    # ---- Level 2 -------------------------------------------------------------
    def get_n_largest(self, prefix: str, n: int) -> list[str]:
        matches = [f for f in self.files.values() if f.name.startswith(prefix)]
        matches.sort(key=lambda f: (-f.size, f.name))
        return [f"{f.name}({f.size})" for f in matches[:n]]

    # ---- Level 3 -------------------------------------------------------------
    def add_user(self, user_id: str, capacity: int) -> bool:
        if user_id in self.users:
            return False
        self.users[user_id] = User(user_id, capacity)
        return True

    def add_file_by(self, user_id: str, name: str, size: int) -> int | None:
        if not self._add(user_id, name, size):
            return None
        return self.users[user_id].remaining()

    def merge_user(self, user_id_1: str, user_id_2: str) -> int | None:
        if user_id_1 == user_id_2 or user_id_1 not in self.users or user_id_2 not in self.users:
            return None
        u1 = self.users[user_id_1]
        u2 = self.users.pop(user_id_2)          # its backup disappears with it
        for name in u2.files:
            self.files[name].owner = user_id_1
        u1.files |= u2.files
        u1.used += u2.used
        u1.capacity += u2.capacity
        return u1.remaining()

    # ---- Level 4 -------------------------------------------------------------
    def backup_user(self, user_id: str) -> int | None:
        user = self.users.get(user_id)
        if user is None:
            return None
        user.backup = {name: self.files[name].size for name in user.files}   # copy, not a reference
        return len(user.backup)

    def restore_user(self, user_id: str) -> int | None:
        user = self.users.get(user_id)
        if user is None:
            return None
        for name in list(user.files):            # copy: _delete mutates user.files
            self._delete(name)
        restored = 0
        for name, size in sorted((user.backup or {}).items()):
            if name in self.files:               # taken by someone else meanwhile
                continue
            self.files[name] = File(name, size, user_id)
            user.used += size
            user.files.add(name)
            restored += 1
        return restored
