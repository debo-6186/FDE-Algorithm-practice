# Text Editor

## Instructions

Your task is to implement a simplified text editor. All operations that should be supported are listed below. Partial credit will be granted for each test passed, so run the tests often to receive partial credit for passed tests. Please check the tests for requirements and argument types.

Solving this task consists of several levels. A subsequent level is opened when the current level is correctly solved. You always have access to the data for the current and all previous levels.

### Implementation tips

Read the question all the way through before you start coding, but implement the operations and complete the levels one by one, not all together, keeping in mind that you will need to refactor to support additional functionality. Please, do not change the existing method signatures.

## Requirements

Your task is to implement a simplified text editor. Plan your design according to the level specifications below:

*   **Level 1:** The editor should support inserting text at a cursor, moving the cursor, and deleting characters.
*   **Level 2:** The editor should support selecting text, copying it, and pasting it.
*   **Level 3:** The editor should support undoing and redoing changes.
*   **Level 4:** The editor should support several documents with a shared clipboard.

To move to the next level, you need to pass all the tests at this level.

## Note

The editor starts with one empty document named `"untitled"` and the cursor at position 0. Positions are character indexes: position `p` sits between character `p - 1` and character `p`.

Implement your solution in `text_editor_impl.py`. Your class inherits the interface in `text_editor.py`; the tests for each unlocked level are in `tests/`. Run them with:

```
python3 practice.py test text_editor
```
