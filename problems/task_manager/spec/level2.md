## Level 2

Tasks are ordered by **priority descending**; tasks with equal priority are ordered by **creation order** (the task added first comes first).

*   `search_tasks(self, timestamp: int, name_filter: str, max_results: int) -> list[str]` — should return the ids of tasks whose name **contains** `name_filter` (case-sensitive substring), in the order above, at most `max_results` of them. Returns `[]` if nothing matches or `max_results <= 0`.

*   `list_tasks_sorted(self, timestamp: int, limit: int) -> list[str]` — should return the ids of all tasks in the order above, at most `limit` of them.

### Examples

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
| --- | --- |
| `add_task(1, "Fix login bug", 5)` | returns "task_id_1" |
| `add_task(2, "Write docs", 2)` | returns "task_id_2" |
| `add_task(3, "Fix typo in docs", 5)` | returns "task_id_3" |
| `add_task(4, "Deploy", 9)` | returns "task_id_4" |
| `search_tasks(5, "Fix", 10)` | returns ["task_id_1", "task_id_3"]; same priority: created first comes first |
| `search_tasks(6, "docs", 1)` | returns ["task_id_3"]; priority 5 beats 2 |
| `search_tasks(7, "fix", 10)` | returns []; case-sensitive |
| `list_tasks_sorted(8, 3)` | returns ["task_id_4", "task_id_1", "task_id_3"] |
| `update_task(9, "task_id_2", "Write docs", 10)` | returns True |
| `list_tasks_sorted(10, 10)` | returns ["task_id_2", "task_id_4", "task_id_1", "task_id_3"] |

### Input/Output

*   **[execution time limit]** 3 seconds
*   **[memory limit]** 1 GB
