## Level 2

The database should support displaying data based on filters.

*   `scan(self, key: str) -> list[str]` — should return the fields of record `key` as `["<field_1>(<value_1>)", "<field_2>(<value_2>)", ...]`, sorted **lexicographically** by field. Returns an empty list if the record doesn't exist.

*   `scan_by_prefix(self, key: str, prefix: str) -> list[str]` — same as `scan`, but only fields that **start with** `prefix` are included (same format and order).

### Examples

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
| --- | --- |
| `set("cfg", "db.port", "5432")` | returns None |
| `set("cfg", "db.host", "local")` | returns None |
| `set("cfg", "log.level", "info")` | returns None |
| `scan("cfg")` | returns ["db.host(local)", "db.port(5432)", "log.level(info)"] |
| `scan_by_prefix("cfg", "db.")` | returns ["db.host(local)", "db.port(5432)"] |
| `scan_by_prefix("cfg", "x")` | returns [] |
| `scan("other")` | returns []; no such record |

### Input/Output

*   **[execution time limit]** 3 seconds
*   **[memory limit]** 1 GB
