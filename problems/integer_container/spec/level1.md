## Level 1

Implement two operations for adding and removing numbers from the container. Initially, the container is empty.

*   `add(self, value: int) -> int` — should add the specified integer `value` to the container and return the number of integers in the container after the addition. The same value may be added several times.

*   `delete(self, value: int) -> bool` — should attempt to remove **one** occurrence of `value` from the container. If `value` is present, remove it and return `True`; otherwise return `False`.

### Examples

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
| --- | --- |
| `add(5)` | returns 1; container: [5] |
| `add(10)` | returns 2; container: [5, 10] |
| `add(5)` | returns 3; duplicates are allowed: [5, 10, 5] |
| `delete(10)` | returns True; container: [5, 5] |
| `delete(1)` | returns False; 1 is not in the container |
| `add(1)` | returns 3; container: [5, 5, 1] |
| `delete(5)` | returns True; only one 5 is removed: [5, 1] |
| `add(-4)` | returns 3; negative values are allowed |

### Input/Output

*   **[execution time limit]** 3 seconds
*   **[memory limit]** 1 GB
