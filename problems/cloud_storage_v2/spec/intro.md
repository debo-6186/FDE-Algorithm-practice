# Cloud Storage

## Instructions

Your task is to implement a simple cloud storage system that maps objects (files) to their meta-information. All operations that should be supported are listed below. Partial credit will be granted for each test passed, so run the tests often to receive partial credit for passed tests. Please check the tests for requirements and argument types.

Solving this task consists of several levels. A subsequent level is opened when the current level is correctly solved. You always have access to the data for the current and all previous levels.

### Implementation tips

Read the question all the way through before you start coding, but implement the operations and complete the levels one by one, not all together, keeping in mind that you will need to refactor to support additional functionality. Please, do not change the existing method signatures.

## Requirements

Your task is to implement a simple cloud storage system. Plan your design according to the level specifications below:

*   **Level 1:** The cloud storage system should support adding new files, copying files, and retrieving file sizes.
*   **Level 2:** The cloud storage system should support searching files by prefix and suffix.
*   **Level 3:** The cloud storage system should support users with storage capacity limits, including changing a user's capacity.
*   **Level 4:** The cloud storage system should support compressing and decompressing files.

To move to the next level, you need to pass all the tests at this level.

## Note

The system keeps meta-information only (names and sizes); nothing is written to a real filesystem. File names are case-sensitive plain strings and all sizes are positive integers.

Implement your solution in `cloud_storage_impl.py`. Your class inherits the interface in `cloud_storage.py`; the tests for each unlocked level are in `tests/`. Run them with:

```
python3 practice.py test cloud_storage_v2
```
