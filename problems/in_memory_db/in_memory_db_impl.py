import bisect
from dataclasses import dataclass
from typing import Any
from interface import InMemoryDB

@dataclass
class ColumnValue:
    val: Any
    expiry: int = None
    timestamp: int = None

@dataclass
class BackupColumn:
    val: Any
    remaining_ttl: int

class Record:
    def __init__(self):
        self.row: dict[str, Any] = {}

    def set_value(self, key: str, value: Any):
        self.row[key] = value

class InMemoryDBImpl(InMemoryDB):

    def __init__(self) -> None:
        self.in_memory_db: dict[str: Record] = {}
        self.backuptimes: list[int] = []
        self.backups: list[dict[str: Record]] = []
        
    # @@LEVEL 1@@
    def set(self, key: str, field: str, value: str) -> None:
        """
        Should insert a field-value pair into the record `key` (overwriting an
        existing field; creating the record if needed).
        """
        row = self.in_memory_db.setdefault(key, Record())
        row.set_value(field, ColumnValue(value))
        return None

    def get(self, key: str, field: str) -> str | None:
        """
        Should return the value of `field` in record `key`, or `None`.
        """
        record = self.in_memory_db.get(key, None)
        if record is None:
            return None
        columnValue = record.row.get(field)
        if columnValue is None:
            return None
        return columnValue.val

    def delete(self, key: str, field: str) -> bool:
        """
        Should remove `field` from record `key`. Returns `True` if it existed.
        """
        record = self.in_memory_db.get(key, None)
        if record is None or field not in record.row:
            return False
        del record.row[field]
        if len(record.row) == 0:
            del self.in_memory_db[key]
        return True

    # @@LEVEL 2@@
    def scan(self, key: str) -> list[str]:
        """
        Should return ["<field>(<value>)", ...] for record `key`, sorted by field.
        """
        result_set = []
        record = self.in_memory_db.get(key, None)
        if record is None:
            return result_set
        for key, column_value in record.row.items():
            result_set.append(f"{key}({column_value.val})")
        result_set = sorted(result_set)
        return result_set

    def scan_by_prefix(self, key: str, prefix: str) -> list[str]:
        """
        Same as `scan`, only fields starting with `prefix`.
        """
        result_set = []
        record = self.in_memory_db.get(key, None)
        if record is None:
            return result_set
        for key, column_value in record.row.items():
            if key.startswith(prefix):
                result_set.append(f"{key}({column_value.val})")
        result_set = sorted(result_set)
        return result_set

    # @@LEVEL 3@@
    def set_at(self, key: str, field: str, value: str, timestamp: int) -> None:
        """
        Timestamped `set`; the pair never expires.
        """
        row = self.in_memory_db.setdefault(key, Record())
        row.set_value(field, ColumnValue(value, None, timestamp))
        return None

    def set_at_with_ttl(self, key: str, field: str, value: str, timestamp: int, ttl: int) -> None:
        """
        Timestamped `set`; the pair lives during [timestamp, timestamp + ttl).
        """
        row = self.in_memory_db.setdefault(key, Record())
        expiry = timestamp + ttl
        row.set_value(field, ColumnValue(value, expiry, timestamp))
        return None

    def delete_at(self, key: str, field: str, timestamp: int) -> bool:
        """
        Timestamped `delete`; expired fields count as missing.
        """
        record = self.in_memory_db.get(key, None)
        if record is None or field not in record.row or \
            (record.row[field].expiry is not None and timestamp >= record.row[field].expiry):
            return False
        del record.row[field]
        if len(record.row) == 0:
            del self.in_memory_db[key]
        return True

    def get_at(self, key: str, field: str, timestamp: int) -> str | None:
        """
        Timestamped `get`.
        """
        record = self.in_memory_db.get(key, None)
        if record is None:
            return None
        column_value = record.row.get(field)
        if column_value is None or \
            (column_value.expiry is not None  and timestamp >= column_value.expiry):
            return None
        return column_value.val

    def scan_at(self, key: str, timestamp: int) -> list[str]:
        """
        Timestamped `scan`.
        """
        result_set = []
        record = self.in_memory_db.get(key, None)
        if record is None:
            return result_set
        for key, column_value in record.row.items():
            if column_value.expiry is not None and timestamp >= column_value.expiry:
                continue
            result_set.append(f"{key}({column_value.val})")
        result_set = sorted(result_set)
        return result_set

    def scan_by_prefix_at(self, key: str, prefix: str, timestamp: int) -> list[str]:
        """
        Timestamped `scan_by_prefix`.
        """
        result_set = []
        record = self.in_memory_db.get(key, None)
        if record is None:
            return result_set
        for key, column_value in record.row.items():
            if column_value.expiry is not None and timestamp >= column_value.expiry:
                continue
            if key.startswith(prefix):
                result_set.append(f"{key}({column_value.val})")
        result_set = sorted(result_set)
        return result_set

    # @@LEVEL 4@@
    def backup(self, timestamp: int) -> int:
        """
        Should save the state with remaining TTLs; returns the number of
        non-empty non-expired records.
        """
        self.backuptimes.append(timestamp)
        current_memory_db = {}
        backup_count = 0
        for row_key, record in self.in_memory_db.items():
            each_row = record.row
            row = {}
            for column_key, column_value in each_row.items():
                if column_value.expiry is not None and timestamp >= column_value.expiry:
                    continue
                remaining_ttl = None if column_value.expiry is None else column_value.expiry - timestamp
                row[column_key] = BackupColumn(column_value.val, remaining_ttl)
            if row:
                current_memory_db[row_key] = row
                backup_count += 1
        self.backups.append(current_memory_db)
        return backup_count

    def restore(self, timestamp: int, timestamp_to_restore: int) -> None:
        """
        Should restore the latest backup made at or before
        `timestamp_to_restore`, recalculating expirations from `timestamp`.
        """
        idx = bisect.bisect_right(self.backuptimes, timestamp_to_restore)
        backup = self.backups[idx - 1]
        new_db = {}
        for row_key, row in backup.items():
            record = Record()
            for column_key, backup_column in row.items():
                expiry = None if backup_column.remaining_ttl is None else timestamp + backup_column.remaining_ttl
                record.set_value(column_key, ColumnValue(backup_column.val, expiry, timestamp))
            new_db[row_key] = record
        self.in_memory_db = new_db
        return None
        