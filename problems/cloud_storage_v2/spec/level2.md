## Level 2

Implement an operation for searching files by name.

*   `find_file(self, prefix: str, suffix: str) -> list[str]` — should return all files whose names start with `prefix` **and** end with `suffix`, formatted as `["<name_1>(<size_1>)", "<name_2>(<size_2>)", ...]`. Sort by size in **descending** order; in case of a tie, by name in **lexicographical** (ascending) order. Return an empty list if nothing matches.
    *   Use normal "starts with" / "ends with" semantics: an empty `prefix` or `suffix` matches everything, and the prefix and suffix may overlap (name `"ab"` matches prefix `"ab"` with suffix `"b"`).

### Examples

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
| --- | --- |
| `add_file("/reports/2024.pdf", 500)` | returns True |
| `add_file("/reports/2025.pdf", 300)` | returns True |
| `add_file("/reports/notes.txt", 100)` | returns True |
| `add_file("/readme.txt", 300)` | returns True |
| `find_file("/reports", ".pdf")` | returns ["/reports/2024.pdf(500)", "/reports/2025.pdf(300)"] |
| `find_file("/", ".txt")` | returns ["/readme.txt(300)", "/reports/notes.txt(100)"] |
| `find_file("/re", "")` | returns ["/reports/2024.pdf(500)", "/readme.txt(300)", "/reports/2025.pdf(300)", "/reports/notes.txt(100)"]; tie at 300 sorted by name |
| `find_file("/x", "")` | returns [] |

### Input/Output

*   **[execution time limit]** 3 seconds
*   **[memory limit]** 1 GB
