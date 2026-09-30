## Level 3

Support the timeline of operations and TTL (Time-To-Live) settings for fields. Each operation from the previous levels now has a version with a `timestamp` parameter that says when the operation was executed. For each field-value pair, the TTL determines how long it persists before it is treated as removed.

*   `set_at(self, key: str, field: str, value: str, timestamp: int) -> None` — like `set`; the pair never expires.

*   `set_at_with_ttl(self, key: str, field: str, value: str, timestamp: int, ttl: int) -> None` — like `set`, and the pair is available only during `[timestamp, timestamp + ttl)`. Overwriting a field replaces both its value and its expiration.

*   `delete_at(self, key: str, field: str, timestamp: int) -> bool` — like `delete`; returns `False` if the field doesn't exist or has already expired.

*   `get_at(self, key: str, field: str, timestamp: int) -> str | None` — like `get`.

*   `scan_at(self, key: str, timestamp: int) -> list[str]` — like `scan`.

*   `scan_by_prefix_at(self, key: str, prefix: str, timestamp: int) -> list[str]` — like `scan_by_prefix`.

*   **Notes:**
    *   Time only moves forward: timestamps strictly increase from one operation to the next.
    *   A test uses either the old operations or the timestamped ones, never both, but the old operations must keep working exactly as before.
    *   Expired pairs behave exactly as if they didn't exist.

### Examples

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
| --- | --- |
| `set_at_with_ttl("A", "BC", "E", 1, 9)` | returns None; expires at 10 |
| `set_at_with_ttl("A", "BC", "E", 5, 10)` | returns None; overwritten: now expires at 15 |
| `set_at("A", "BD", "F", 6)` | returns None; never expires |
| `scan_by_prefix_at("A", "B", 14)` | returns ["BC(E)", "BD(F)"] |
| `scan_by_prefix_at("A", "B", 15)` | returns ["BD(F)"]; BC expired at 15 |
| `get_at("A", "BC", 16)` | returns None |
| `delete_at("A", "BC", 17)` | returns False; already expired |
| `set_at_with_ttl("X", "Y", "Z", 18, 2)` | returns None; expires at 20 |
| `get_at("X", "Y", 19)` | returns "Z" |
| `scan_at("X", 20)` | returns [] |
| `delete_at("A", "BD", 21)` | returns True |
| `scan_at("A", 22)` | returns [] |

### Input/Output

*   **[execution time limit]** 3 seconds
*   **[memory limit]** 1 GB
