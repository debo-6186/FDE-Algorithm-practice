# Banking System

## Instructions

Your task is to implement a simplified version of a banking system. All operations that should be supported are listed below. Partial credit will be granted for each test passed, so run the tests often to receive partial credit for passed tests. Please check the tests for requirements and argument types.

Solving this task consists of several levels. A subsequent level is opened when the current level is correctly solved. You always have access to the data for the current and all previous levels.

### Implementation tips

Read the question all the way through before you start coding, but implement the operations and complete the levels one by one, not all together, keeping in mind that you will need to refactor to support additional functionality. Please, do not change the existing method signatures.

## Requirements

Your task is to implement a simplified version of a banking system. Plan your design according to the level specifications below:

*   **Level 1:** The banking system should support creating new accounts, depositing money into accounts, and transferring money between two accounts.
*   **Level 2:** The banking system should support ranking accounts based on outgoing transactions.
*   **Level 3:** The banking system should allow scheduling payments and canceling scheduled payments.
*   **Level 4:** The banking system should support merging two accounts while retaining both accounts' balances and transaction histories.

To move to the next level, you need to pass all the tests at this level.

## Note

All operations have a `timestamp` parameter — an integer number of milliseconds. It is guaranteed that all timestamps are unique and are in a range from `1` to `10^9`, and that operations are given in order of strictly increasing timestamps. All `amount` values are positive integers.

Implement your solution in `banking_system_impl.py`. Your class inherits the interface in `banking_system.py`; the tests for each unlocked level are in `tests/`. Run them with:

```
python3 practice.py test banking_scheduled
```
