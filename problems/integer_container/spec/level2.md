## Level 2

Introduce an operation for retrieving the median of the numbers stored in the container.

*   `get_median(self) -> int | None` — should return the median integer: the integer in the middle of the **sorted** sequence of all integers stored in the container. If the number of integers is even, return the **leftmost** (smaller) of the two middle integers. If the container is empty, return `None`.

### Examples

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
| --- | --- |
| `get_median()` | returns None; container is empty |
| `add(3)` | returns 1 |
| `get_median()` | returns 3; sorted: [3] |
| `add(1)` | returns 2 |
| `get_median()` | returns 1; sorted: [1, 3]; even size, leftmost middle is 1 |
| `add(8)` | returns 3 |
| `get_median()` | returns 3; sorted: [1, 3, 8] |
| `add(2)` | returns 4 |
| `get_median()` | returns 2; sorted: [1, 2, 3, 8] |
| `delete(2)` | returns True |
| `get_median()` | returns 3; sorted: [1, 3, 8] |

### Input/Output

*   **[execution time limit]** 3 seconds
*   **[memory limit]** 1 GB
