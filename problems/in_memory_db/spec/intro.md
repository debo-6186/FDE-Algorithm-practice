# In-memory Database

## Instructions

Your task is to implement a simplified version of an in-memory database. All operations that should be supported are listed below. Partial credit will be granted for each test passed, so run the tests often to receive partial credit for passed tests. Please check the tests for requirements and argument types.

Solving this task consists of several levels. A subsequent level is opened when the current level is correctly solved. You always have access to the data for the current and all previous levels.

### Implementation tips

Read the question all the way through before you start coding, but implement the operations and complete the levels one by one, not all together, keeping in mind that you will need to refactor to support additional functionality. Please, do not change the existing method signatures.

## Requirements

Your task is to implement a simplified version of an in-memory database. Plan your design according to the level specifications below:

*   **Level 1:** The in-memory database should support basic operations to manipulate records, fields, and values within fields.
*   **Level 2:** The in-memory database should support displaying a record's fields based on a filter.
*   **Level 3:** The in-memory database should support TTL (Time-To-Live) configurations on database records.
*   **Level 4:** The in-memory database should support backup and restore functionality.

To move to the next level, you need to pass all the tests at this level.

## Note

Keys, fields and values are non-empty strings. From Level 3 on, note the parameter order: `timestamp` comes **after** the other arguments, and timestamps are given in strictly increasing order.

Implement your solution in `in_memory_db_impl.py`. Your class inherits the interface in `in_memory_db.py`; the tests for each unlocked level are in `tests/`. Run them with:

```
python3 practice.py test in_memory_db
```
