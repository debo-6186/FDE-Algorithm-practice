## Level 1

The cloud storage system should support file manipulation.

*   `add_file(self, name: str, size: int) -> bool` — should add a new file `name` to the storage. `size` is the amount of memory required in bytes. The operation fails if a file with the same `name` already exists. Returns `True` if the file was added, or `False` otherwise.

*   `get_file_size(self, name: str) -> int | None` — should return the size of the file `name` if it exists, or `None` otherwise.

*   `delete_file(self, name: str) -> int | None` — should delete the file `name`. Returns the size of the deleted file if the deletion was successful, or `None` if the file does not exist.

### Examples

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
| --- | --- |
| `add_file("/a.txt", 10)` | returns True |
| `add_file("/a.txt", 5)` | returns False; the file already exists |
| `get_file_size("/a.txt")` | returns 10 |
| `get_file_size("/b.txt")` | returns None; no such file |
| `delete_file("/b.txt")` | returns None; no such file |
| `delete_file("/a.txt")` | returns 10 |
| `get_file_size("/a.txt")` | returns None; deleted |
| `add_file("/a.txt", 7)` | returns True; the name is free again |

### Input/Output

*   **[execution time limit]** 3 seconds
*   **[memory limit]** 1 GB
