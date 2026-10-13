# Parcel Tracking System

## Instructions

Your task is to implement a simplified version of a parcel tracking system. All operations that should be supported are listed below. Partial credit will be granted for each test passed, so run the tests often to receive partial credit for passed tests. Please check the tests for requirements and argument types.

Solving this task consists of several levels. A subsequent level is opened when the current level is correctly solved. You always have access to the data for the current and all previous levels.

### Implementation tips

Read the question all the way through before you start coding, but implement the operations and complete the levels one by one, not all together, keeping in mind that you will need to refactor to support additional functionality. Please, do not change the existing method signatures.

## Requirements

Your task is to implement a simplified version of a parcel tracking system. Plan your design according to the level specifications below:

*   **Level 1:** The parcel tracking system should support basic tag operations: setting, getting, and removing string tags on parcels.
*   **Level 2:** The parcel tracking system should support listing tags on parcels.
*   **Level 3:** The parcel tracking system should support timestamped tag operations with optional time-to-live (TTL) expiry.
*   **Level 4:** The parcel tracking system should support checkpoints for saving and restoring the state of parcels.

To move to the next level, you need to pass all the tests at this level when submitting the solution.

## Note

Implement your solution in `parcel_tracking_system.py`. Your class inherits the interface in `parcel_tracking_system_interface.py`; the tests for each unlocked level are in `tests/`. Run them with:

```
python3 practice.py test parcel_tracking
```
