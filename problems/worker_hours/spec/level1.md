## Level 1

Introduce operations for adding workers, registering when they enter or leave the office, and retrieving the amount of time they have spent there.

*   `add_worker(self, worker_id: str, position: str, compensation: int) -> bool` — should add the worker with their position and compensation (pay per time unit). Returns `False` if `worker_id` already exists (nothing changes), `True` otherwise.

*   `register(self, worker_id: str, timestamp: int) -> str` — should register the time when the worker entered or left the office. If the worker is not in the office, this registers an **entry**; if the worker is in the office, it registers an **exit**. Returns `"registered"`, or `"invalid_request"` if `worker_id` doesn't exist. `register` calls are given in increasing order of `timestamp`.

*   `get(self, worker_id: str) -> int | None` — should return the total time the worker spent in the office, counting **finished** sessions only (an entry without an exit yet doesn't count). Returns `None` if the worker doesn't exist.

### Examples

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
| --- | --- |
| `add_worker("Ann", "Middle Developer", 150)` | returns True |
| `add_worker("Ann", "Junior Developer", 100)` | returns False; already exists |
| `register("Ann", 10)` | returns "registered"; Ann enters |
| `register("Ann", 25)` | returns "registered"; Ann leaves: 15 time units |
| `get("Ann")` | returns 15 |
| `register("Ann", 40)` | returns "registered"; enters again |
| `get("Ann")` | returns 15; the current visit is not finished |
| `register("Ann", 67)` | returns "registered"; leaves |
| `get("Ann")` | returns 42; (25 - 10) + (67 - 40) |
| `get("Walter")` | returns None |
| `register("Walter", 120)` | returns "invalid_request" |

### Input/Output

*   **[execution time limit]** 3 seconds
*   **[memory limit]** 1 GB
