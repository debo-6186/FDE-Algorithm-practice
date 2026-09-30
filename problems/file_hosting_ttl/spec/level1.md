## Level 1 - Initial design and basic functions

Initially, the file hosting service contains no files. Implement operations to upload files to the server, retrieve their sizes, and copy them. Note that some operations should throw a runtime exception instead of returning a value.

*   `file_upload(self, file_name: str, size: int) -> None` — should upload the file to the storage. If a file with the same name already exists, raise a `RuntimeError`.

*   `file_get(self, file_name: str) -> int | None` — should return the size of the file, or `None` if the file doesn't exist.

*   `file_copy(self, source: str, dest: str) -> None` — should copy the `source` file to `dest`. If `source` doesn't exist, raise a `RuntimeError`. If `dest` already exists, it is **overwritten**.

### Examples

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
| --- | --- |
| `file_upload("/docs/cv.pdf", 300)` | returns None |
| `file_upload("/docs/cv.pdf", 100)` | raises `RuntimeError`; already exists |
| `file_get("/docs/cv.pdf")` | returns 300 |
| `file_get("/nope")` | returns None |
| `file_copy("/docs/cv.pdf", "/backup/cv.pdf")` | returns None |
| `file_get("/backup/cv.pdf")` | returns 300 |
| `file_upload("/tmp.txt", 5)` | returns None |
| `file_copy("/tmp.txt", "/backup/cv.pdf")` | returns None; overwrites the destination |
| `file_get("/backup/cv.pdf")` | returns 5 |
| `file_copy("/nope", "/x")` | raises `RuntimeError`; source doesn't exist |

### Input/Output

*   **[execution time limit]** 3 seconds
*   **[memory limit]** 1 GB
