# Working Hours Register

## Instructions

Your task is to implement a simplified version of a program registering the working hours of contract workers at a facility. All operations that should be supported are listed below. Partial credit will be granted for each test passed, so run the tests often to receive partial credit for passed tests. Please check the tests for requirements and argument types.

Solving this task consists of several levels. A subsequent level is opened when the current level is correctly solved. You always have access to the data for the current and all previous levels.

### Implementation tips

Read the question all the way through before you start coding, but implement the operations and complete the levels one by one, not all together, keeping in mind that you will need to refactor to support additional functionality. Please, do not change the existing method signatures.

## Requirements

Your task is to implement a simplified version of a program registering the working hours of contract workers. Plan your design according to the level specifications below:

*   **Level 1:** The program should support adding workers, registering when workers enter or leave the office, and retrieving the time they spent in the office.
*   **Level 2:** The program should support retrieving statistics about the time workers spent in the office.
*   **Level 3:** The program should support promoting workers (new position and compensation) and calculating a worker's salary for a given period.
*   **Level 4:** The program should support setting time periods to be double-paid.

To move to the next level, you need to pass all the tests at this level.

## Note

`register` operations are given in increasing order of the `timestamp` parameter. Compensation is an integer amount paid per unit of time.

Implement your solution in `worker_registry_impl.py`. Your class inherits the interface in `worker_registry.py`; the tests for each unlocked level are in `tests/`. Run them with:

```
python3 practice.py test worker_hours
```
