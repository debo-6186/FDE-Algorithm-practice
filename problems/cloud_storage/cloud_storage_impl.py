from ctypes import sizeof
from dataclasses import dataclass
from interface import CloudStorage

ADMIN = "admin"

@dataclass
class File:
    name: str
    size: int
    owner: str

class User:
    def __init__(self, user_id: str, capacity: int):
        self.userid: str = user_id
        self.capacity: int = capacity
        self.used: int = 0
        self.user_files: dict[str, File] = {}

class CloudStorageImpl(CloudStorage):

    def __init__(self):
        self.files: dict[str, File] = {}
        self.users: dict[str, User] = {ADMIN: User(ADMIN, None)}

    def add_file(self, name: str, size: int):
        return self._add_file(name, size, ADMIN)

    def _add_file(self, name: str, size: int, user_id: str) -> bool:
        """
        Should add a new file `name` to the storage. `size` is the amount of
        memory required in bytes. Fails if a file with the same `name` already
        exists. Returns `True` if the file was added, `False` otherwise.
        """
        if name in self.files:
            return False
        self.files[name] = File(name, size, user_id)
        return True

    def get_file_size(self, name: str) -> int | None:
        """
        Should return the size of the file `name` if it exists, `None` otherwise.
        """
        if name not in self.files:
            return None
        return self.files.get(name).size

    def delete_file(self, name: str) -> int | None:
        """
        Should delete the file `name`. Returns the deleted file's size, or
        `None` if the file does not exist.
        """
        if name not in self.files:
            return None
        file_size = self.files[name].size
        user = self.users[self.files[name].owner]
        user.used -= file_size
        del self.files[name]
        return file_size

    def get_n_largest(self, prefix: str, n: int) -> list[str]:
        """
        Should return the top `n` largest files whose names start with
        `prefix`, formatted as "<name>(<size>)", sorted by size descending,
        ties by name ascending. Empty list if none.
        """
        matches = [f for f in self.files.values() if f.name.startswith(prefix)]
        matches.sort(key=lambda f: (-f.size, f.name))
        return [f"{f.name}({f.size})" for f in matches[:n]]

    # @@LEVEL 3@@
    def add_user(self, user_id: str, capacity: int) -> bool:
        """
        Should add a new user with a storage limit of `capacity` bytes.
        Returns `False` if the user already exists.
        """
        if user_id in self.users:
            return False
        self.users[user_id] = User(user_id, capacity)
        return True

    def add_file_by(self, user_id: str, name: str, size: int) -> int | None:
        """
        Should add a file owned by `user_id`. Returns the user's remaining
        capacity, or `None` if the user doesn't exist, the name is taken, or
        the capacity would be exceeded.
        """
        if user_id not in self.users or name in self.files:
            return None
        user = self.users[user_id]
        updated_size = user.used + size
        if updated_size > user.capacity:
            return None
        self._add_file(name, size, user_id)
        user.used = updated_size
        return (user.capacity - user.used)

    def merge_user(self, user_id_1: str, user_id_2: str) -> int | None:
        """
        Should merge `user_id_2` into `user_id_1` (files + capacity) and delete
        `user_id_2`. Returns the remaining capacity of `user_id_1`, or `None`
        if either user doesn't exist or the ids are equal.
        """
        user_1 = self.users.get(user_id_1, None)
        user_2 = self.users.get(user_id_2, None)        
        if user_1 is None or user_2 is None or \
            user_1.userid == user_2.userid:
            return None
        user_2 = self.users.pop(user_id_2, None)
        user_1.used += user_2.used
        user_1.capacity += user_2.capacity
        for file in self.files.values():
            if file.owner == user_id_2:
                file.owner = user_id_1
        return (user_1.capacity - user_1.used)

    def backup_user(self, user_id: str) -> int | None:
        """
        Should back up all files owned by `user_id` (overwriting any previous
        backup). Returns the number of backed-up files, or `None` if the user
        doesn't exist.
        """
        user = self.users.get(user_id, None)
        if user is None:
            return None
        user.user_files = {}
        for file in self.files.values():
            if file.owner == user_id:
                # Store a copy so later mutations (size changes, ownership
                # transfers) don't leak into the snapshot.
                user.user_files[file.name] = File(file.name, file.size, file.owner)
        return len(user.user_files)

    def restore_user(self, user_id: str) -> int | None:
        """
        Should replace the user's files with the latest backup (skipping names
        now used by other owners). Returns the number of restored files, or
        `None` if the user doesn't exist.
        """
        user = self.users.get(user_id, None)
        if user is None:
            return None
        backup = user.user_files
        # Delete files currently owned by the user that aren't in the backup.
        for file_name in [f.name for f in self.files.values()
                           if f.owner == user_id and f.name not in backup]:
            self.delete_file(file_name)
        restored_files_count = 0
        for name, snapshot in backup.items():
            current = self.files.get(name)
            if current is not None:
                if current.owner != user_id:
                    # Name now taken by another user: skip it.
                    continue
                if current.size != snapshot.size:
                    user.used += snapshot.size - current.size
                    current.size = snapshot.size
                restored_files_count += 1
            else:
                self.add_file_by(user_id, name, snapshot.size)
                restored_files_count += 1
        return restored_files_count