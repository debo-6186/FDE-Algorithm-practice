## Level 4

Implement support for users to back up their files.

*   `backup_user(self, user_id: str) -> int | None` — should back up the current state of all files owned by `user_id` (file names and sizes). The backup is stored separately and is not affected by later file operations. A new backup overwrites the user's previous backup. Returns the number of backed-up files, or `None` if `user_id` doesn't exist.

*   `restore_user(self, user_id: str) -> int | None` — should restore `user_id`'s files to the latest backup: all files the user currently owns are deleted, then the files from the backup are added back (owned by `user_id`). If there was no backup, all of the user's files are simply deleted. If a file can't be restored because another user (or admin) now owns a file with the same name, it is skipped. Returns the number of files that were restored, or `None` if `user_id` doesn't exist.

*   **Notes:**
    *   `merge_user` does not change `user_id_1`'s backup; `user_id_2` is deleted together with its backup.
    *   `restore_user` does not change the user's capacity limit. The backup remains available, so the same backup can be restored again.

### Examples

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
| --- | --- |
| `add_user("user", 100)` | returns True |
| `add_file_by("user", "/dir/file1", 50)` | returns 50 |
| `add_file_by("user", "/file2.txt", 30)` | returns 20 |
| `restore_user("user")` | returns 0; no backup: all of user's files are deleted |
| `get_file_size("/dir/file1")` | returns None |
| `add_file_by("user", "/file3.mp4", 60)` | returns 40 |
| `add_file_by("user", "/file4.txt", 10)` | returns 30 |
| `backup_user("user")` | returns 2 |
| `delete_file("/file3.mp4")` | returns 60 |
| `delete_file("/file4.txt")` | returns 10 |
| `add_file("/file3.mp4", 5)` | returns True; admin now owns this name |
| `add_file_by("user", "/dir/file5.new", 20)` | returns 80 |
| `restore_user("user")` | returns 1; `/file4.txt` restored, `/file3.mp4` skipped, `/dir/file5.new` deleted |
| `get_file_size("/dir/file5.new")` | returns None |
| `get_file_size("/file4.txt")` | returns 10 |
| `get_file_size("/file3.mp4")` | returns 5; still admin's file |
| `add_file_by("user", "/f", 90)` | returns 0; only `/file4.txt` (10) is used |
| `backup_user("nobody")` | returns None |
| `restore_user("nobody")` | returns None |

### Input/Output

*   **[execution time limit]** 3 seconds
*   **[memory limit]** 1 GB
