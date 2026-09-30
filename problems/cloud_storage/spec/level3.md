## Level 3

Implement support for queries from different users. All users share a common filesystem (one namespace of file names), but each user has a storage capacity limit.

*   `add_user(self, user_id: str, capacity: int) -> bool` — should add a new user with `capacity` as their storage limit in bytes. The total size of all files owned by `user_id` cannot exceed `capacity`. Fails if a user with `user_id` already exists. Returns `True` if the user was created, or `False` otherwise.

*   `add_file_by(self, user_id: str, name: str, size: int) -> int | None` — should behave like `add_file` from Level 1, but the added file is owned by `user_id`. The file cannot be added if doing so would exceed the user's capacity. Returns the user's **remaining** capacity if the file was added, or `None` otherwise (unknown user, name already taken by any file, or not enough capacity).

*   `merge_user(self, user_id_1: str, user_id_2: str) -> int | None` — should merge the account of `user_id_2` into `user_id_1`. Ownership of all of `user_id_2`'s files moves to `user_id_1`, and `user_id_2`'s capacity is added to `user_id_1`'s capacity (so the remaining capacities add up). `user_id_2` is then deleted. Returns the remaining capacity of `user_id_1` after the merge, or `None` if either user doesn't exist or `user_id_1` equals `user_id_2`.

*   **Notes:**
    *   Files added with Level 1 `add_file` are owned by the user `"admin"`, who always exists and has **unlimited** capacity. `add_user("admin", ...)` returns `False`. `add_file_by`, `merge_user` (and Level 4 operations) are never called with `"admin"`.
    *   `delete_file` works on any file and frees the owner's capacity.
    *   `get_n_largest` still considers all files, whoever owns them.

### Examples

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
| --- | --- |
| `add_user("user1", 200)` | returns True |
| `add_user("user1", 100)` | returns False; already exists |
| `add_file_by("user1", "/dir/file.med", 50)` | returns 150 |
| `add_file_by("user1", "/big.blob", 140)` | returns 10 |
| `add_file_by("user1", "/file-small", 20)` | returns None; not enough capacity |
| `add_file("/dir/admin_file", 300)` | returns True; owned by admin (unlimited) |
| `add_user("user2", 110)` | returns True |
| `add_file_by("user2", "/dir/file.med", 45)` | returns None; name already taken by user1's file |
| `add_file_by("user2", "/new_file", 50)` | returns 60 |
| `merge_user("user1", "user2")` | returns 70; capacity 310, used 240 |
| `add_file_by("user2", "/x", 1)` | returns None; user2 no longer exists |
| `add_file_by("user1", "/y", 70)` | returns 0 |
| `delete_file("/big.blob")` | returns 140; frees 140 bytes of user1's capacity |
| `add_file_by("user1", "/z", 100)` | returns 40 |

### Input/Output

*   **[execution time limit]** 3 seconds
*   **[memory limit]** 1 GB
