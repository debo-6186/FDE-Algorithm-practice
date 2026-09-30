## Level 4

Implement an operation for canceling jobs that have not started yet.

*   `cancel_job(self, job_id: str) -> list[str]` — should cancel a job that hasn't started (`"queued"` or `"blocked"`), together with **every** job that depends on it directly or indirectly and hasn't started. Canceled jobs get status `"canceled"` and never start. Returns the ids of all jobs canceled by this call, sorted alphabetically, or `[]` if the job doesn't exist or can't be canceled (it is running, done or already canceled).

*   **Changes to earlier operations:**
    *   `add_dependency` also returns `False` if `prerequisite_id` is canceled.

### Examples

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
| --- | --- |
| `add_job("a", 1)` | returns True |
| `add_job("b", 1)` | returns True |
| `add_job("c", 1)` | returns True |
| `add_job("d", 1)` | returns True |
| `add_dependency("b", "a")` | returns True |
| `add_dependency("c", "b")` | returns True |
| `add_dependency("d", "a")` | returns True |
| `cancel_job("b")` | returns ["b", "c"]; `c` depends on `b` |
| `get_status("c")` | returns "canceled" |
| `cancel_job("c")` | returns []; already canceled |
| `next_job()` | returns "a" |
| `cancel_job("a")` | returns []; running jobs can't be canceled |
| `complete_job("a")` | returns True |
| `next_job()` | returns "d" |
| `add_job("e", 2)` | returns True |
| `add_dependency("e", "b")` | returns False; `b` is canceled |
| `jobs_with_status("canceled")` | returns ["b", "c"] |

### Input/Output

*   **[execution time limit]** 3 seconds
*   **[memory limit]** 1 GB
