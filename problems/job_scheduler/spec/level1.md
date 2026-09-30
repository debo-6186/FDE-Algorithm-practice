## Level 1

Initially, the scheduler contains no jobs. Implement operations to add jobs, start the next job by priority, complete jobs, and check the status of a job.

*   `add_job(self, job_id: str, priority: int) -> bool` — should add a new job with status `"queued"`. Returns `False` if a job with this id already exists (in any status).

*   `next_job(self) -> str | None` — should start the queued job with the **highest priority** (in case of a tie, the job that was added **first**): its status becomes `"running"`. Returns its id, or `None` if there is no queued job.

*   `complete_job(self, job_id: str) -> bool` — should mark a running job as `"done"`. Returns `False` if the job doesn't exist or isn't running.

*   `get_status(self, job_id: str) -> str | None` — should return the job's status (`"queued"`, `"running"` or `"done"`), or `None` if the job doesn't exist.

### Examples

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
| --- | --- |
| `add_job("build", 5)` | returns True |
| `add_job("test", 3)` | returns True |
| `add_job("lint", 5)` | returns True |
| `add_job("build", 1)` | returns False; already exists |
| `next_job()` | returns "build"; priority 5, added before `lint` |
| `get_status("build")` | returns "running" |
| `complete_job("test")` | returns False; not running |
| `complete_job("build")` | returns True |
| `get_status("build")` | returns "done" |
| `next_job()` | returns "lint" |
| `next_job()` | returns "test" |
| `next_job()` | returns None; queue is empty |
| `get_status("deploy")` | returns None |

### Input/Output

*   **[execution time limit]** 3 seconds
*   **[memory limit]** 1 GB
