## Level 3

Implement operations for undoing and redoing changes to the document.

*   `undo(self) -> str` — should revert the most recent change to the document text: the text **and the cursor** go back to what they were right before that change was made (or re-made by `redo`). Returns the document text (unchanged if there is nothing to undo).

*   `redo(self) -> str` — should re-apply the most recently undone change: the text and the cursor go back to what they were right before that `undo`. Returns the document text (unchanged if there is nothing to redo).

*   **Notes:**
    *   A change is an `insert`, `paste`, `delete_forward` or `backspace` that actually modified the text. Operations that leave the text as it was (e.g. `backspace` at position 0, pasting an empty clipboard with no selection) are not changes.
    *   `move_cursor`, `select` and `copy` are not changes and cannot be undone.
    *   Any new change clears the redo history. `undo` and `redo` clear the selection.

### Examples

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
| --- | --- |
| `insert("one")` | returns "one" |
| `insert(" two")` | returns "one two" |
| `undo()` | returns "one"; cursor back to 3 |
| `undo()` | returns "" |
| `undo()` | returns ""; nothing to undo |
| `redo()` | returns "one" |
| `get_cursor()` | returns 3 |
| `move_cursor(0)` | returns "one"; not a change |
| `insert(">")` | returns ">one"; a new change clears the redo history |
| `redo()` | returns ">one"; nothing to redo |
| `select(1, 4)` | returns "one"; cursor 4 |
| `backspace()` | returns ">" |
| `undo()` | returns ">one"; cursor restored to 4 |
| `get_cursor()` | returns 4 |
| `undo()` | returns "one"; before `insert(">")` the cursor was at 0 |
| `get_cursor()` | returns 0 |

### Input/Output

*   **[execution time limit]** 3 seconds
*   **[memory limit]** 1 GB
