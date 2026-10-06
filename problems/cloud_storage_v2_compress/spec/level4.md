## Level 4

Implement compression of user-owned files.

*   `compress_file(self, user_id: str, name: str) -> int | None` — should compress the file `name` owned by `user_id`: the file `name` is replaced by a file named `name + ".COMPRESSED"` whose size is half of the original size (rounded down). Returns the user's remaining capacity after the operation, or `None` if:
    *   the user doesn't exist, or the file doesn't exist, or it isn't owned by `user_id`;
    *   the file is already compressed (its name ends with `".COMPRESSED"`);
    *   a file named `name + ".COMPRESSED"` already exists.

*   `decompress_file(self, user_id: str, name: str) -> int | None` — should reverse `compress_file`: the compressed file `name` is replaced by a file with the original name (`name` without the `".COMPRESSED"` ending) and the original size. Returns the user's remaining capacity after the operation, or `None` if:
    *   the user doesn't exist, or the file doesn't exist, or it isn't owned by `user_id`;
    *   the file is not a compressed file created by `compress_file` (or a copy of one);
    *   a file with the original name already exists;
    *   the user's capacity would be exceeded after decompression.

*   **Notes:**
    *   `copy_file` copies a compressed file as a compressed file (it can be decompressed later if its name ends with `".COMPRESSED"`).
    *   `update_capacity` works on current sizes (compressed files count at their compressed size).

### Examples

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
| --- | --- |
| `add_user("alice", 1000)` | returns True |
| `add_file_by("alice", "/video.mp4", 800)` | returns 200 |
| `compress_file("alice", "/video.mp4")` | returns 600; 800 bytes become 400 |
| `get_file_size("/video.mp4")` | returns None |
| `get_file_size("/video.mp4.COMPRESSED")` | returns 400 |
| `compress_file("alice", "/video.mp4.COMPRESSED")` | returns None; already compressed |
| `add_user("bob", 100)` | returns True |
| `decompress_file("bob", "/video.mp4.COMPRESSED")` | returns None; not bob's file |
| `add_file_by("alice", "/notes.txt", 500)` | returns 100 |
| `decompress_file("alice", "/video.mp4.COMPRESSED")` | returns None; needs 400 more bytes, only 100 free |
| `update_capacity("alice", 1300)` | returns 0; nothing deleted; 400 free now |
| `decompress_file("alice", "/video.mp4.COMPRESSED")` | returns 0; back to 800 bytes |
| `get_file_size("/video.mp4")` | returns 800 |
| `compress_file("alice", "/notes.txt")` | returns 250; 500 becomes 250 |

### Input/Output

*   **[execution time limit]** 3 seconds
*   **[memory limit]** 1 GB
