## Level 3

Introduce operations for worker promotion and salary calculation.

*   `promote(self, worker_id: str, new_position: str, new_compensation: int, start_timestamp: int) -> str` — should register a promotion. The new position and compensation become active at the worker's **first entry into the office at or after `start_timestamp`**. Returns `"success"`, or `"invalid_request"` if the worker doesn't exist or already has a promotion that has not become active yet (nothing changes in that case). `start_timestamp` is greater than the timestamp of every `register` call made so far.

*   `calc_salary(self, worker_id: str, start_timestamp: int, end_timestamp: int) -> int | None` — should return the salary the worker earned between `start_timestamp` and `end_timestamp` (`0 <= start_timestamp < end_timestamp`). Workers are paid only for time in the office, finished sessions only: for each session, the part that overlaps `[start_timestamp, end_timestamp]` is paid at the compensation the worker had during that session. Returns `None` if the worker doesn't exist.

*   **Changes to earlier operations:**
    *   `top_n_workers` considers only each worker's **current** position, and counts only the time spent in sessions that started after the current position became active.
    *   `get` still returns the total time across all positions.

### Examples

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
| --- | --- |
| `add_worker("John", "Middle Developer", 200)` | returns True |
| `register("John", 100)` | returns "registered"; enters |
| `register("John", 125)` | returns "registered"; leaves: 25 units at 200 |
| `promote("John", "Senior Developer", 500, 200)` | returns "success"; active from John's first entry at or after 200 |
| `register("John", 150)` | returns "registered"; enters: 150 < 200, still Middle Developer |
| `promote("John", "Senior Developer", 350, 250)` | returns "invalid_request"; a promotion is already pending |
| `register("John", 300)` | returns "registered"; leaves: 150 units at 200 |
| `register("John", 325)` | returns "registered"; enters at 325 >= 200: now Senior Developer at 500 |
| `calc_salary("John", 0, 500)` | returns 35000; 25 * 200 + 150 * 200 (the current visit is unfinished) |
| `top_n_workers(3, "Senior Developer")` | returns ["John(0)"]; no finished time in the new position yet |
| `top_n_workers(3, "Middle Developer")` | returns []; John isn't a Middle Developer anymore |
| `register("John", 400)` | returns "registered"; leaves: 75 units at 500 |
| `get("John")` | returns 250; 25 + 150 + 75 |
| `top_n_workers(10, "Senior Developer")` | returns ["John(75)"] |
| `calc_salary("John", 110, 350)` | returns 45500; 15 * 200 + 150 * 200 + 25 * 500 |
| `calc_salary("John", 900, 1400)` | returns 0 |
| `promote("John", "Lead", 900, 500)` | returns "success"; the previous promotion is active, so a new one is allowed |
| `calc_salary("Nobody", 0, 10)` | returns None |

### Input/Output

*   **[execution time limit]** 3 seconds
*   **[memory limit]** 1 GB
