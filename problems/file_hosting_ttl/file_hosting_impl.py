import bisect
from dataclasses import dataclass
from interface import FileHosting

@dataclass
class File:
    name: str
    size: int
    expiry: int | None = None

class FileHostingImpl(FileHosting):
    
    def __init__(self):
        self.files: dict[str, File] = {}
        self.snap_times: list[int] = []
        self.snapshot: list[dict[str, File]] = []

    def _snapshot_save(self, timestamp: int):
        self.snap_times.append(timestamp)
        self.snapshot.append(dict(self.files))

    # @@LEVEL 1@@
    def file_upload(self, file_name: str, size: int) -> None:
        """
        Should upload the file. Raises `RuntimeError` if a file with the same
        name already exists.
        """
        if file_name in self.files:
            raise RuntimeError()
        self.files[file_name] = File(file_name, size)
        return size

    def file_get(self, file_name: str) -> int | None:
        """
        Should return the size of the file, or `None` if it doesn't exist.
        """
        if file_name not in self.files:
            return None
        return self.files[file_name].size

    def file_copy(self, source: str, dest: str) -> None:
        """
        Should copy `source` to `dest` (overwriting `dest`). Raises
        `RuntimeError` if `source` doesn't exist.
        """
        if source not in self.files:
            raise RuntimeError()
        if source == dest:
            return True
        if dest in self.files:
            del self.files[dest]
        source_file = self.files[source]
        self.files[dest] = File(dest, source_file.size)
        return source_file.size

    # @@LEVEL 2@@
    def file_search(self, prefix: str) -> list[str]:
        """
        Should return the names of the top 10 files starting with `prefix`,
        ordered by size descending, ties by name ascending.
        """
        result_list = [f for f in self.files.values() if f.name.startswith(prefix)]
        result_list = sorted(result_list, key=lambda f: (-f.size, f.name))
        return [f.name for f in result_list[:10]]

    # @@LEVEL 3@@
    def _is_alive(self, file_name: str, timestamp: int):
        file = self.files.get(file_name)
        if file is None:
            return False
        if file.expiry is not None and file.expiry < timestamp:
            return False
        return True

    def file_upload_at(self, timestamp: int, file_name: str, file_size: int, ttl: int | None = None) -> None:
        """
        Timestamped upload. With `ttl`, the file is alive during
        [timestamp, timestamp + ttl). Raises `RuntimeError` if a live file with
        the same name exists.
        """
        if self._is_alive(file_name, timestamp):
            raise RuntimeError()
        self.files[file_name] = File(file_name, file_size, (timestamp + ttl - 1) if ttl is not None else None)
        self._snapshot_save(timestamp)
        return file_size
        

    def file_get_at(self, timestamp: int, file_name: str) -> int | None:
        """
        Timestamped get: `None` if missing or expired.
        """
        if self._is_alive(file_name, timestamp) is False:
            return None
        return self.files[file_name].size

    def file_copy_at(self, timestamp: int, source: str, dest: str) -> None:
        """
        Timestamped copy. The copy expires together with the source. Raises
        `RuntimeError` if `source` is missing or expired.
        """
        if self._is_alive(source, timestamp) is False:
            raise RuntimeError()
        if source == dest:
            return True
        source_file = self.files[source]
        self.files[dest] = File(dest, source_file.size, source_file.expiry)
        self._snapshot_save(timestamp)
        return source_file.size

    def file_search_at(self, timestamp: int, prefix: str) -> list[str]:
        """
        Timestamped search over files alive at `timestamp`.
        """
        result_list = [f for f in self.files.values() if self._is_alive(f.name, timestamp) and f.name.startswith(prefix)]
        result_list = sorted(result_list, key=lambda f: (-f.size, f.name))
        return [f.name for f in result_list[:10]]

    # @@LEVEL 4@@
    def rollback(self, timestamp: int, time_to: int) -> None:
        """
        At `timestamp`, restore the storage to its state at `time_to`, keeping
        each restored file's remaining lifetime.
        """
        idx = bisect.bisect_right(self.snap_times, time_to)
        # Get the snapshot
        snapshot_files = self.snapshot[idx - 1] if idx else {}
        restored_files: dict[str, File] = {}
        for file_name, file in snapshot_files.items():
            if file.expiry is None:
                restored_files[file_name] = File(file_name, file.size)
            elif file.expiry > time_to:
                restored_files[file_name] = File(file_name, file.size, timestamp + (file.expiry - time_to))
        self.files = restored_files
        self._snapshot_save(timestamp)
