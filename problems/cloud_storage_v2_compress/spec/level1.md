## Level 1

Initially, the cloud storage system is empty. Implement operations to add files, copy files, and retrieve file sizes.

*   `add_file(self, name: str, size: int) -> bool` — should add a new file `name` of `size` bytes. Fails if a file named `name` already exists. Returns `True` if the file was added, `False` otherwise.

*   `copy_file(self, name_from: str, name_to: str) -> bool` — should create a new file `name_to` that is an exact copy of `name_from` (same size). Fails if `name_from` doesn't exist or if a file named `name_to` already exists. Returns `True` if the file was copied, `False` otherwise.

*   `get_file_size(self, name: str) -> int | None` — should return the size of the file `name`, or `None` if it doesn't exist.

### Examples

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
| --- | --- |
| `add_file("/report.pdf", 500)` | returns True |
| `add_file("/report.pdf", 200)` | returns False; already exists |
| `get_file_size("/report.pdf")` | returns 500 |
| `get_file_size("/missing.txt")` | returns None |
| `copy_file("/report.pdf", "/backup/report.pdf")` | returns True |
| `get_file_size("/backup/report.pdf")` | returns 500 |
| `copy_file("/ghost.txt", "/out.txt")` | returns False; source doesn't exist |
| `copy_file("/report.pdf", "/backup/report.pdf")` | returns False; destination already exists |

### Input/Output

*   **[execution time limit]** 3 seconds
*   **[memory limit]** 1 GB
