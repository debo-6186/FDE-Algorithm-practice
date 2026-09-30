from dataclasses import dataclass

from interface import CloudStorage

ADMIN = "admin"

@dataclass
class File:
    name: str
    size: int
    owner: str
    compresed_size_saved: int = 0

class User:
    def __init__(self, user_id: str, capacity: int):
        self.userid: str = user_id
        self.capacity: int = capacity
        self.used: int = 0
        self.user_files: dict[str, File] = {}

class CloudStorageV2Impl(CloudStorage):
    def __init__(self):
        self.files: dict[str, File] = {}
        self.users: dict[str, User] = {ADMIN: User(ADMIN, 10000000)}

    def add_file(self, name: str, size: int):
        return self._add_file(name, size, ADMIN)

    def _add_file(self, name: str, size: int, user_id: str, compressed_file_saved: int = 0) -> bool:
        """
        Should add a new file `name` to the storage. `size` is the amount of
        memory required in bytes. Fails if a file with the same `name` already
        exists. Returns `True` if the file was added, `False` otherwise.
        """
        if name in self.files:
            return False
        self.files[name] = File(name, size, user_id, compressed_file_saved)
        return True

    def copy_file(self, name_from: str, name_to: str) -> bool:
        """
        Should copy file `name_from` to a new file `name_to`. Returns `False`
        if `name_from` doesn't exist or `name_to` already exists.
        """
        source_file = self.files.get(name_from, None)
        if source_file is None or name_to in self.files:
            return False
        user = self.users[source_file.owner]
        if source_file.size + user.used > user.capacity:
            return False
        if ".COMPRESSED" in name_to:
            self.add_file_by(user.userid, name_to, source_file.size, source_file.compresed_size_saved)
        else:
            self.add_file_by(user.userid, name_to, source_file.size)
        return True

    def get_file_size(self, name: str) -> int | None:
        """
        Should return the size of the file `name` if it exists, `None` otherwise.
        """
        if name not in self.files:
            return None
        return self.files.get(name).size

    def add_user(self, user_id: str, capacity: int) -> bool:
        """
        Should add a new user with a storage limit of `capacity` bytes.
        Returns `False` if the user already exists.
        """
        if user_id in self.users:
            return False
        self.users[user_id] = User(user_id, capacity)
        return True

    # @@LEVEL 2@@
    def find_file(self, prefix: str, suffix: str) -> list[str]:
        """
        Should return files whose names start with `prefix` and end with
        `suffix` as "<name>(<size>)", sorted by size descending, ties by name.
        """
        matches = [f for f in self.files.values() if f.name.startswith(prefix) and f.name.endswith(suffix)]
        matches = sorted(matches, key=lambda a: (-a.size, a.name))
        return [f"{f.name}({f.size})" for f in matches]

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

    def add_file_by(self, user_id: str, name: str, size: int, compressed_file_saved: int = 0) -> int | None:
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
        self._add_file(name, size, user_id, compressed_file_saved)
        user.used = updated_size
        return (user.capacity - user.used)

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

    def update_capacity(self, user_id: str, capacity: int) -> int | None:
        """
        Should set the user's capacity, deleting the user's largest files
        (ties: lexicographically smaller name first) until they fit. Returns
        the number of deleted files, or `None` if the user doesn't exist.
        """
        user = self.users.get(user_id, None)
        if user is None:
            return None
        if capacity >= user.capacity:
            user.capacity = capacity
            return 0
        user_files: list[File] = []
        for file_name, file in self.files.items():
            if file.owner == user_id:
                user_files.append(file)
        user_files = sorted(user_files, key=lambda f: (-f.size, f.name))
        number_of_deleted_files = 0
        for file in user_files:
            if user.used <= capacity:
                break
            self.delete_file(file.name)
            number_of_deleted_files += 1
        user.capacity = capacity
        return number_of_deleted_files

# @@LEVEL 4@@
    def compress_file(self, user_id: str, name: str) -> int | None:
        """
        Should replace `name` with `name + ".COMPRESSED"` at half the size.
        Returns the user's remaining capacity, or `None` on failure.
        """
        user = self.users.get(user_id, None)
        file = self.files.get(name, None)
        if user is None or file is None or ".COMPRESSED" in file.name or file.owner != user.userid:
            return None
        file.name = f"{file.name}.COMPRESSED"
        if file.name in self.files:
            return None
        self.files[file.name] = file
        freed_size = (file.size + 1) // 2
        file.compresed_size_saved = freed_size
        file.size -= freed_size
        new_file = File(file.name, file.size, user_id, freed_size)
        del self.files[name]
        self.files[new_file.name] = new_file
        user.used -= freed_size
        return user.capacity - user.used

    def decompress_file(self, user_id: str, name: str) -> int | None:
        """
        Should reverse `compress_file`. Returns the user's remaining capacity,
        or `None` on failure.
        """
        user = self.users.get(user_id, None)
        file = self.files.get(name, None) 
        if user is None or file is None or ".COMPRESSED" not in file.name or file.owner != user.userid:
            return None
        increased_size = file.size + file.compresed_size_saved
        print(f"user used: {user.used}")
        print(f"increased_size: {increased_size}")
        print(f"increased_size: {increased_size}")
        # This file is not compressed by the program
        if file.compresed_size_saved == 0:
            return None
        if (user.used + file.compresed_size_saved) > user.capacity:
            print("Size exceed")
            return None
        file.name = file.name.rsplit(".", 1)[0]
        if file.name in self.files:
            return None
        file.size += file.compresed_size_saved
        new_file = File(file.name, file.size, user_id)     
        self.files[new_file.name] = new_file
        user.used += file.compresed_size_saved
        del self.files[name]
        print(user.capacity)
        return (user.capacity - user.used)