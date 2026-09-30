# Integer Container

## Instructions

Your task is to implement a simple container of integers. All operations that should be supported are listed below. Partial credit will be granted for each test passed, so run the tests often to receive partial credit for passed tests. Please check the tests for requirements and argument types.

Solving this task consists of several levels. A subsequent level is opened when the current level is correctly solved. You always have access to the data for the current and all previous levels.

### Implementation tips

Read the question all the way through before you start coding, but implement the operations and complete the levels one by one, not all together, keeping in mind that you will need to refactor to support additional functionality. Please, do not change the existing method signatures.

## Requirements

Your task is to implement a simple container of integers. Plan your design according to the level specifications below:

*   **Level 1:** The container should support adding and removing integers.
*   **Level 2:** The container should support retrieving the median of its values.
*   **Level 3:** The container should support order-statistics queries (counting values in a range, k-th smallest).
*   **Level 4:** The container should support undoing and redoing changes.

To move to the next level, you need to pass all the tests at this level.

## Note

The container starts empty. Values are integers and may be negative; the same value may be stored several times.

Levels 1 and 2 follow CodeSignal's public practice question; levels 3 and 4 were added for this kit so you can rehearse the full four-level flow.

Implement your solution in `integer_container_impl.py`. Your class inherits the interface in `integer_container.py`; the tests for each unlocked level are in `tests/`. Run them with:

```
python3 practice.py test integer_container
```
