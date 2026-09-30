# Task Management System

## Instructions

Your task is to implement a simplified task management system. All operations that should be supported are listed below. Partial credit will be granted for each test passed, so run the tests often to receive partial credit for passed tests. Please check the tests for requirements and argument types.

Solving this task consists of several levels. A subsequent level is opened when the current level is correctly solved. You always have access to the data for the current and all previous levels.

### Implementation tips

Read the question all the way through before you start coding, but implement the operations and complete the levels one by one, not all together, keeping in mind that you will need to refactor to support additional functionality. Please, do not change the existing method signatures.

## Requirements

Your task is to implement a simplified task management system. Plan your design according to the level specifications below:

*   **Level 1:** The system should support adding, updating and retrieving tasks.
*   **Level 2:** The system should support searching tasks by name and listing tasks sorted by priority.
*   **Level 3:** The system should support users with quotas and assigning tasks to users for a limited time.
*   **Level 4:** The system should support completing assignments and listing overdue assignments.

To move to the next level, you need to pass all the tests at this level.

## Note

All operations have a `timestamp` parameter — an integer. It is guaranteed that all timestamps are unique and that operations are given in order of strictly increasing timestamps.

Implement your solution in `task_manager_impl.py`. Your class inherits the interface in `task_manager.py`; the tests for each unlocked level are in `tests/`. Run them with:

```
python3 practice.py test task_manager
```
