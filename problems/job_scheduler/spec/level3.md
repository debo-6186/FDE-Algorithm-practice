## Level 3

Jobs can now depend on other jobs.

*   `add_dependency(self, job_id: str, prerequisite_id: str) -> bool` — `job_id` may only start after `prerequisite_id` is `"done"`. Returns `True` if the dependency was added. Returns `False` (and changes nothing) if:
    *   either job doesn't exist, or the two ids are equal;
    *   `job_id` has already started (it must be `"queued"` or `"blocked"`);
    *   the same dependency already exists;
    *   the dependency would create a cycle (`prerequisite_id` already depends on `job_id`, directly or indirectly).

*   **Changes to earlier operations:**
    *   A job that hasn't started and has at least one prerequisite that isn't `"done"` has status `"blocked"`; it becomes `"queued"` again once all its prerequisites are done.
    *   `next_job` and `peek_jobs` only consider `"queued"` jobs (never `"blocked"` ones).

### Examples

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
| --- | --- |
| `add_job("compile", 1)` | returns True |
| `add_job("test", 9)` | returns True |
| `add_job("deploy", 9)` | returns True |
| `add_dependency("test", "compile")` | returns True |
| `add_dependency("deploy", "test")` | returns True |
| `add_dependency("compile", "deploy")` | returns False; would create a cycle |
| `add_dependency("test", "test")` | returns False |
| `get_status("deploy")` | returns "blocked" |
| `peek_jobs(5)` | returns ["compile"]; only ready jobs |
| `next_job()` | returns "compile" |
| `next_job()` | returns None; `test` waits until `compile` is done |
| `complete_job("compile")` | returns True |
| `get_status("test")` | returns "queued" |
| `next_job()` | returns "test" |
| `add_dependency("test", "compile")` | returns False; `test` already started |
| `jobs_with_status("blocked")` | returns ["deploy"] |

### Input/Output

*   **[execution time limit]** 3 seconds
*   **[memory limit]** 1 GB
