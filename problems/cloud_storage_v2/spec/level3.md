## Level 3

Introduce users. All users share one namespace of file names, but each user has a storage capacity limit.

*   `add_user(self, user_id: str, capacity: int) -> bool` — should add a new user with a storage limit of `capacity` bytes. Returns `False` if the user already exists.

*   `add_file_by(self, user_id: str, name: str, size: int) -> int | None` — should add a file owned by `user_id`. Returns the user's remaining capacity after the operation, or `None` if the user doesn't exist, the name is taken, or the user's total file size would exceed their capacity.

*   `update_capacity(self, user_id: str, capacity: int) -> int | None` — should change the user's capacity. If the user's files now take more space than `capacity`, the user's **largest** files are deleted one by one (in case of a tie in size, the lexicographically **smaller** name is deleted first) until the total size fits. Returns the number of deleted files, or `None` if the user doesn't exist.

*   **Notes:**
    *   Files added with Level 1 `add_file` belong to `"admin"`, who has unlimited capacity. Level 3+ operations are never called with `"admin"`.
    *   `copy_file`: the copy belongs to the owner of `name_from`. If that owner is a user whose capacity would be exceeded by the copy, `copy_file` fails and returns `False`.
    *   `find_file` and `get_file_size` still see every file.

### Examples

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
| --- | --- |
| `add_user("alice", 100)` | returns True |
| `add_file_by("alice", "/a.txt", 40)` | returns 60 |
| `add_file_by("alice", "/b.txt", 40)` | returns 20 |
| `add_file_by("alice", "/c.txt", 10)` | returns 10 |
| `copy_file("/c.txt", "/c-copy.txt")` | returns True; alice owns the copy; 0 bytes left |
| `copy_file("/a.txt", "/a-copy.txt")` | returns False; would exceed alice's capacity |
| `add_file("/admin.bin", 1000)` | returns True; admin: unlimited |
| `copy_file("/admin.bin", "/admin-copy.bin")` | returns True |
| `update_capacity("alice", 50)` | returns 2; alice uses 100: delete `/a.txt` (40, tie broken by name), then `/b.txt` (40); 20 left |
| `get_file_size("/a.txt")` | returns None |
| `get_file_size("/c-copy.txt")` | returns 10 |
| `add_file_by("alice", "/d.txt", 30)` | returns 0 |
| `update_capacity("bob", 10)` | returns None; no such user |
| `update_capacity("alice", 1000)` | returns 0; nothing to delete |
| `add_file_by("alice", "/e.txt", 950)` | returns 0 |

### Input/Output

*   **[execution time limit]** 3 seconds
*   **[memory limit]** 1 GB
