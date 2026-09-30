## Level 2

Introduce an operation to retrieve ordered statistics about the workers.

*   `top_n_workers(self, n: int, position: str) -> list[str]` — should return the top `n` workers whose current position is `position`, sorted by time spent in the office (finished sessions only) in **descending** order; in case of a tie, by `worker_id` in **ascending** (alphabetical) order. Format: `["<worker_id_1>(<time_1>)", ...]`. Workers with the position but no finished sessions are included with `0`. If fewer than `n` such workers exist, return all of them; if none, return `[]`.

### Examples

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
| --- | --- |
| `add_worker("John", "Junior Developer", 120)` | returns True |
| `add_worker("Jason", "Junior Developer", 120)` | returns True |
| `add_worker("Ashley", "Junior Developer", 120)` | returns True |
| `add_worker("Maria", "Senior Developer", 200)` | returns True |
| `register("John", 100)` | returns "registered" |
| `register("John", 150)` | returns "registered"; John: 50 |
| `register("Jason", 200)` | returns "registered" |
| `register("Jason", 250)` | returns "registered"; Jason: 50 |
| `register("Jason", 275)` | returns "registered"; Jason enters again |
| `top_n_workers(5, "Junior Developer")` | returns ["Jason(50)", "John(50)", "Ashley(0)"]; Jason before John alphabetically |
| `top_n_workers(1, "Junior Developer")` | returns ["Jason(50)"] |
| `register("Ashley", 400)` | returns "registered" |
| `register("Ashley", 500)` | returns "registered"; Ashley: 100 |
| `register("Jason", 575)` | returns "registered"; Jason: 50 + 300 = 350 |
| `top_n_workers(3, "Junior Developer")` | returns ["Jason(350)", "Ashley(100)", "John(50)"] |
| `top_n_workers(3, "Senior Developer")` | returns ["Maria(0)"] |
| `top_n_workers(3, "Intern")` | returns [] |

### Input/Output

*   **[execution time limit]** 3 seconds
*   **[memory limit]** 1 GB
