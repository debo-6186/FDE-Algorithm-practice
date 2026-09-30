## Level 2 - Data structures and data processing

Implement an operation for retrieving statistics about files with a specific prefix.

*   `file_search(self, prefix: str) -> list[str]` — should find the **top 10** files whose names start with `prefix` and return their **names** (sizes are not included). Order the results by size in **descending** order and, in case of a tie, by file name (ascending). If fewer than 10 files match, return all of them; if none match, return `[]`.

### Examples

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
| --- | --- |
| `file_upload("/logs/1.log", 10)` | returns None |
| `file_upload("/logs/2.log", 30)` | returns None |
| `file_upload("/logs/3.log", 20)` | returns None |
| `file_upload("/lib/x.so", 30)` | returns None |
| `file_search("/lo")` | returns ["/logs/2.log", "/logs/3.log", "/logs/1.log"] |
| `file_search("/l")` | returns ["/lib/x.so", "/logs/2.log", "/logs/3.log", "/logs/1.log"]; tie at 30 sorted by name |
| `file_search("/z")` | returns [] |

### Input/Output

*   **[execution time limit]** 3 seconds
*   **[memory limit]** 1 GB
