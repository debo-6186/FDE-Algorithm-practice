## Level 3 - Refactoring and encapsulation

Files may now have a time to live (TTL). Implement timestamped versions of the existing operations. They behave like the Level 1-2 operations, plus:

*   `file_upload_at(self, timestamp: int, file_name: str, file_size: int, ttl: int | None = None) -> None` — uploads the file at `timestamp`. If `ttl` is given, the file is available only during `[timestamp, timestamp + ttl)`: at `timestamp + ttl` it has expired and is treated as if it didn't exist. Without `ttl` the file never expires. Raise a `RuntimeError` if a file with the same name exists **and has not expired** at `timestamp` (an expired file's name can be reused).

*   `file_get_at(self, timestamp: int, file_name: str) -> int | None` — the size of the file, or `None` if it doesn't exist or has expired at `timestamp`.

*   `file_copy_at(self, timestamp: int, source: str, dest: str) -> None` — copies `source` to `dest` (overwriting `dest`). Raise a `RuntimeError` if `source` doesn't exist or has expired. The copy has the same size and **expires at the same moment** as the source (a copy of a file without TTL never expires).

*   `file_search_at(self, timestamp: int, prefix: str) -> list[str]` — like `file_search`, but only files that are still alive at `timestamp` are considered.

*   **Notes:**
    *   Timestamps are integers and strictly increase from one operation to the next.
    *   A test uses either the Level 1-2 operations or the timestamped operations, never both, but the Level 1-2 operations must keep working exactly as before.

### Examples

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
| --- | --- |
| `file_upload_at(1, "/a.txt", 100)` | returns None; never expires |
| `file_upload_at(2, "/b.txt", 200, 10)` | returns None; alive during [2, 12) |
| `file_get_at(11, "/b.txt")` | returns 200 |
| `file_get_at(12, "/b.txt")` | returns None; expired |
| `file_upload_at(13, "/b.txt", 50, 5)` | returns None; the old file expired, so the name is free; alive during [13, 18) |
| `file_upload_at(14, "/a.txt", 1)` | raises `RuntimeError`; `/a.txt` is alive |
| `file_copy_at(15, "/b.txt", "/c.txt")` | returns None; the copy also expires at 18 |
| `file_search_at(16, "/")` | returns ["/a.txt", "/b.txt", "/c.txt"]; sizes 100, 50, 50 |
| `file_search_at(18, "/")` | returns ["/a.txt"] |
| `file_copy_at(19, "/b.txt", "/d.txt")` | raises `RuntimeError`; `/b.txt` expired |
| `file_get_at(20, "/c.txt")` | returns None |

### Input/Output

*   **[execution time limit]** 3 seconds
*   **[memory limit]** 1 GB
