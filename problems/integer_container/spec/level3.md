## Level 3

Introduce operations for querying the stored numbers by order: how many of them fall into a range, and which number sits at a given position.

*   `count_in_range(self, low: int, high: int) -> int` — should return how many stored integers `v` satisfy `low <= v <= high` (duplicates count separately). If `low > high`, return `0`.

*   `get_kth_smallest(self, k: int) -> int | None` — should return the `k`-th smallest stored integer, where `k` is 1-based (`k = 1` is the minimum). Duplicates count separately. Return `None` if `k < 1` or `k` is larger than the number of stored integers.

### Examples

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
| --- | --- |
| `add(4)` | returns 1 |
| `add(1)` | returns 2 |
| `add(7)` | returns 3 |
| `add(4)` | returns 4; duplicates are counted separately |
| `add(9)` | returns 5; sorted: [1, 4, 4, 7, 9] |
| `count_in_range(4, 7)` | returns 3; 4, 4 and 7 |
| `count_in_range(5, 6)` | returns 0 |
| `count_in_range(9, 1)` | returns 0; low > high |
| `get_kth_smallest(1)` | returns 1 |
| `get_kth_smallest(3)` | returns 4 |
| `get_kth_smallest(6)` | returns None; only 5 integers |
| `get_kth_smallest(0)` | returns None; k must be at least 1 |

### Input/Output

*   **[execution time limit]** 3 seconds
*   **[memory limit]** 1 GB
