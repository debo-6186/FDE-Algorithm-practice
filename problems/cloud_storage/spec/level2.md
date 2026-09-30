## Level 2

Implement an operation for retrieving statistics about files with a specific prefix.

*   `get_n_largest(self, prefix: str, n: int) -> list[str]` — should return the names of the top `n` largest files whose names start with `prefix`, in the format `["<name_1>(<size_1>)", "<name_2>(<size_2>)", ...]`. Files are sorted by size in **descending** order; in case of a tie, by name in **lexicographical** (ascending) order. If there are no such files, return an empty list. If there are fewer than `n` such files, return all of them.

### Examples

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
| --- | --- |
| `add_file("/photos/cat.png", 300)` | returns True |
| `add_file("/photos/dog.png", 500)` | returns True |
| `add_file("/photos/2024/beach.jpg", 450)` | returns True |
| `add_file("/music/song.mp3", 500)` | returns True |
| `get_n_largest("/photos", 2)` | returns ["/photos/dog.png(500)", "/photos/2024/beach.jpg(450)"] |
| `get_n_largest("/photos/c", 5)` | returns ["/photos/cat.png(300)"]; only one match |
| `get_n_largest("/videos", 3)` | returns []; no matches |
| `get_n_largest("/", 3)` | returns ["/music/song.mp3(500)", "/photos/dog.png(500)", "/photos/2024/beach.jpg(450)"]; tie at 500: names in lexicographical order |

### Input/Output

*   **[execution time limit]** 3 seconds
*   **[memory limit]** 1 GB
