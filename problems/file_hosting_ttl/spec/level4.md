## Level 4 - Extending design and functionality

Implement an operation for restoring the state of the file storage to an earlier point in time.

*   `rollback(self, timestamp: int, time_to: int) -> None` — performed at `timestamp`; should roll the storage back to the state it had at time `time_to` (`time_to < timestamp`), that is, right after all operations at `time_to` were processed.
    *   Every change made after `time_to` is undone (uploads, copies, overwrites).
    *   Only files that were alive at `time_to` come back.
    *   **TTLs are recalculated:** a restored file keeps the lifetime it had left at `time_to`. If it would have expired at `E`, it now expires at `timestamp + (E - time_to)`. Files without TTL still never expire.
    *   The rollback itself is an operation at `timestamp`; later operations (and later rollbacks) see its result. A later rollback to a time `T` restores whatever the storage actually contained at `T` (which may be before or after an earlier rollback).

### Examples

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
| --- | --- |
| `file_upload_at(10, "/a", 1)` | returns None; never expires |
| `file_upload_at(20, "/b", 2, 100)` | returns None; expires at 120 |
| `file_upload_at(30, "/c", 3, 15)` | returns None; expires at 45 |
| `file_copy_at(40, "/a", "/b")` | returns None; `/b` is overwritten by a copy of `/a` |
| `rollback(50, 35)` | returns None; state at 35: `/a`; `/b` (size 2, 85 left, so it now expires at 135); `/c` (10 left, now expires at 60) |
| `file_get_at(51, "/b")` | returns 2; the copy was undone |
| `file_get_at(59, "/c")` | returns 3 |
| `file_get_at(60, "/c")` | returns None |
| `file_get_at(134, "/b")` | returns 2 |
| `file_get_at(135, "/b")` | returns None |
| `rollback(140, 25)` | returns None; state at 25: `/a` and `/b` (95 left, now expires at 235) |
| `file_search_at(141, "/")` | returns ["/b", "/a"]; sizes 2 and 1 |
| `file_get_at(142, "/c")` | returns None; `/c` did not exist yet at 25 |

### Input/Output

*   **[execution time limit]** 3 seconds
*   **[memory limit]** 1 GB
