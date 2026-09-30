## Level 4

The database should be backed up from time to time. Introduce operations to back up and restore the database state. When restoring, TTL expirations are recalculated.

*   `backup(self, timestamp: int) -> int` — should save the database state at `timestamp`, including the **remaining** TTL of every field (the time left until it expires, measured from `timestamp`). Expired fields are not saved. Returns the number of non-empty, non-expired records in the database.

*   `restore(self, timestamp: int, timestamp_to_restore: int) -> None` — should restore the database from the **latest backup made at or before** `timestamp_to_restore`. A backup at or before that time is guaranteed to exist. Everything in the current state is replaced. Because time only moves forward, restored fields expire relative to the restore: a field with remaining TTL `r` in the backup now expires at `timestamp + r`. Fields without TTL still never expire.

### Examples

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
| --- | --- |
| `set_at_with_ttl("A", "B", "C", 1, 10)` | returns None; expires at 11 |
| `backup(3)` | returns 1; saved: A.B with 8 left |
| `set_at("A", "D", "E", 4)` | returns None |
| `backup(5)` | returns 1; saved: A.B with 6 left, A.D (no TTL); still one record |
| `delete_at("A", "B", 8)` | returns True |
| `backup(9)` | returns 1 |
| `restore(10, 7)` | returns None; latest backup at or before 7 is from 5; A.B now expires at 10 + 6 = 16 |
| `set_at("B", "C", "D", 11)` | returns None |
| `backup(12)` | returns 2 |
| `scan_at("A", 15)` | returns ["B(C)", "D(E)"] |
| `scan_at("A", 16)` | returns ["D(E)"] |
| `scan_at("B", 17)` | returns ["C(D)"] |
| `restore(18, 3)` | returns None; backup from 3: A.B with 8 left, so it expires at 26; record B did not exist |
| `scan_at("A", 25)` | returns ["B(C)"] |
| `scan_at("B", 25)` | returns [] |
| `get_at("A", "B", 26)` | returns None |
| `backup(27)` | returns 0; the only field expired, so no non-empty records |

### Input/Output

*   **[execution time limit]** 3 seconds
*   **[memory limit]** 1 GB
