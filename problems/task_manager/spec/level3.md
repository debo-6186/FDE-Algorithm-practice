## Level 3

Introduce users who can be assigned tasks for a limited time.

*   `add_user(self, timestamp: int, user_id: str, quota: int) -> bool` — should add a user. `quota` is the maximum number of assignments the user can have **active at the same time**. Returns `False` if the user already exists.

*   `assign_task(self, timestamp: int, task_id: str, user_id: str, finish_time: int) -> bool` — should assign the task to the user. The assignment is **active** during `[timestamp, finish_time)` (`finish_time > timestamp`). Returns `False` (and assigns nothing) if the task or the user doesn't exist, or if the user already has `quota` active assignments at `timestamp`. A task can be assigned to several users, and even to the same user more than once.

*   `get_user_tasks(self, timestamp: int, user_id: str) -> list[str]` — should return the task ids of the user's assignments that are active at `timestamp`, sorted by `finish_time` ascending, then by the time the assignment was made. Returns `[]` if the user doesn't exist or has no active assignments.

### Examples

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
| --- | --- |
| `add_task(1, "A", 1)` | returns "task_id_1" |
| `add_task(2, "B", 2)` | returns "task_id_2" |
| `add_user(3, "ann", 2)` | returns True |
| `add_user(4, "ann", 5)` | returns False; already exists |
| `assign_task(5, "task_id_1", "ann", 20)` | returns True; active during [5, 20) |
| `assign_task(6, "task_id_2", "ann", 10)` | returns True; active during [6, 10) |
| `assign_task(7, "task_id_1", "ann", 30)` | returns False; ann already has 2 active assignments |
| `assign_task(8, "task_id_9", "ann", 30)` | returns False; no such task |
| `assign_task(9, "task_id_1", "bob", 30)` | returns False; no such user |
| `get_user_tasks(10, "ann")` | returns ["task_id_1"]; the task_id_2 assignment ended at 10 |
| `assign_task(11, "task_id_2", "ann", 15)` | returns True |
| `get_user_tasks(12, "ann")` | returns ["task_id_2", "task_id_1"]; finish times 15 and 20 |
| `get_user_tasks(13, "zoe")` | returns [] |

### Input/Output

*   **[execution time limit]** 3 seconds
*   **[memory limit]** 1 GB
