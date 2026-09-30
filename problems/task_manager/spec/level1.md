## Level 1

Initially, the task management system contains no tasks. Implement operations to add tasks, update them, and retrieve them.

*   `add_task(self, timestamp: int, name: str, priority: int) -> str` — should add a new task and return its unique id `"task_id_<k>"`, where `k` is the ordinal number of the task among all tasks added so far (`"task_id_1"`, `"task_id_2"`, ...). Task names don't need to be unique.

*   `update_task(self, timestamp: int, task_id: str, name: str, priority: int) -> bool` — should replace the name and priority of the task. Returns `True` if the task exists, `False` otherwise.

*   `get_task(self, timestamp: int, task_id: str) -> str | None` — should return the task as a JSON string with exactly this shape: `{"name": "<name>", "priority": <priority>}` (what `json.dumps({"name": name, "priority": priority})` produces). Returns `None` if the task doesn't exist.

### Examples

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
| --- | --- |
| `add_task(1, "Write report", 3)` | returns "task_id_1" |
| `add_task(2, "Review PR", 5)` | returns "task_id_2" |
| `get_task(3, "task_id_1")` | returns '{"name": "Write report", "priority": 3}' |
| `get_task(4, "task_id_9")` | returns None |
| `update_task(5, "task_id_1", "Write final report", 4)` | returns True |
| `update_task(6, "task_id_9", "x", 1)` | returns False |
| `get_task(7, "task_id_1")` | returns '{"name": "Write final report", "priority": 4}' |
| `add_task(8, "Write report", 3)` | returns "task_id_3"; names can repeat |

### Input/Output

*   **[execution time limit]** 3 seconds
*   **[memory limit]** 1 GB
