# File Hosting Service

## Instructions

Your task is to implement a simplified version of a file hosting service. All operations that should be supported are listed below. Partial credit will be granted for each test passed, so run the tests often to receive partial credit for passed tests. Please check the tests for requirements and argument types.

Solving this task consists of several levels. A subsequent level is opened when the current level is correctly solved. You always have access to the data for the current and all previous levels.

### Implementation tips

Read the question all the way through before you start coding, but implement the operations and complete the levels one by one, not all together, keeping in mind that you will need to refactor to support additional functionality. Please, do not change the existing method signatures.

## Requirements

Your task is to implement a simplified version of a file hosting service. Plan your design according to the level specifications below:

*   **Level 1:** Initial design and basic functions: upload, get and copy files.
*   **Level 2:** Data structures and data processing: search files by prefix.
*   **Level 3:** Refactoring and encapsulation: timestamped versions of every operation, with optional time-to-live for files.
*   **Level 4:** Extending design and functionality: roll the storage back to an earlier point in time.

To move to the next level, you need to pass all the tests at this level.

## Note

Some operations should raise a `RuntimeError` instead of returning a value; the tests use `assertRaises` for those. From Level 3 on, all timestamped operations are given in order of strictly increasing timestamps.

Implement your solution in `file_hosting_impl.py`. Your class inherits the interface in `file_hosting.py`; the tests for each unlocked level are in `tests/`. Run them with:

```
python3 practice.py test file_hosting_ttl
```
