## Level 1

The database contains records. Each record is identified by a unique string `key`. A record contains field-value pairs; both fields and values are strings.

*   `set(self, key: str, field: str, value: str) -> None` — should insert the field-value pair into the record `key`. If the field already exists, replace its value. If the record doesn't exist, create it.

*   `get(self, key: str, field: str) -> str | None` — should return the value of `field` in record `key`, or `None` if the record or the field doesn't exist.

*   `delete(self, key: str, field: str) -> bool` — should remove `field` from record `key`. Returns `True` if the field existed and was deleted, `False` if the record or the field doesn't exist. A record whose last field is deleted no longer exists.

### Examples

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
| --- | --- |
| `set("user:1", "name", "Ann")` | returns None; `{"user:1": {"name": "Ann"}}` |
| `set("user:1", "city", "Paris")` | returns None |
| `get("user:1", "name")` | returns "Ann" |
| `get("user:1", "email")` | returns None; no such field |
| `get("user:2", "name")` | returns None; no such record |
| `set("user:1", "name", "Anna")` | returns None; overwrite |
| `get("user:1", "name")` | returns "Anna" |
| `delete("user:1", "city")` | returns True |
| `delete("user:1", "city")` | returns False; already deleted |
| `delete("user:9", "x")` | returns False; no such record |

### Input/Output

*   **[execution time limit]** 3 seconds
*   **[memory limit]** 1 GB
