## Level 2

Implement operations for inspecting the queue without changing it, and for listing jobs by status.

*   `peek_jobs(self, n: int) -> list[str]` — should return the ids of the next `n` jobs that `next_job` would start, in that order, **without** starting them. Returns fewer if fewer jobs are queued.

*   `jobs_with_status(self, status: str) -> list[str]` — should return the ids of all jobs with the given status, sorted alphabetically (`[]` if none).

### Examples

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
| --- | --- |
| `add_job("a", 1)` | returns True |
| `add_job("b", 3)` | returns True |
| `add_job("c", 3)` | returns True |
| `peek_jobs(2)` | returns ["b", "c"] |
| `peek_jobs(10)` | returns ["b", "c", "a"] |
| `next_job()` | returns "b" |
| `jobs_with_status("queued")` | returns ["a", "c"]; alphabetical |
| `jobs_with_status("running")` | returns ["b"] |
| `jobs_with_status("done")` | returns [] |

### Input/Output

*   **[execution time limit]** 3 seconds
*   **[memory limit]** 1 GB
