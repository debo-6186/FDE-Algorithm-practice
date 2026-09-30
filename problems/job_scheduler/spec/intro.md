# Job Scheduler

## Instructions

Your task is to implement a simplified job scheduler. All operations that should be supported are listed below. Partial credit will be granted for each test passed, so run the tests often to receive partial credit for passed tests. Please check the tests for requirements and argument types.

Solving this task consists of several levels. A subsequent level is opened when the current level is correctly solved. You always have access to the data for the current and all previous levels.

### Implementation tips

Read the question all the way through before you start coding, but implement the operations and complete the levels one by one, not all together, keeping in mind that you will need to refactor to support additional functionality. Please, do not change the existing method signatures.

## Requirements

Your task is to implement a simplified job scheduler. Plan your design according to the level specifications below:

*   **Level 1:** The scheduler should support adding jobs, starting the next job by priority, completing jobs, and checking a job's status.
*   **Level 2:** The scheduler should support previewing the queue and listing jobs by status.
*   **Level 3:** The scheduler should support dependencies between jobs.
*   **Level 4:** The scheduler should support canceling jobs, including every job that depends on them.

To move to the next level, you need to pass all the tests at this level.

## Note

Job ids are unique strings and priorities are integers (higher runs first). There are no timestamps in this problem.

Implement your solution in `job_scheduler_impl.py`. Your class inherits the interface in `job_scheduler.py`; the tests for each unlocked level are in `tests/`. Run them with:

```
python3 practice.py test job_scheduler
```
