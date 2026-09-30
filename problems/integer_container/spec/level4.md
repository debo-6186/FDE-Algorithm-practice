## Level 4

Changes can now be undone and redone.

*   `undo(self) -> bool` — should revert the most recent **successful** `add` or `delete` that has not been undone yet (undoing `add(v)` removes one `v`; undoing `delete(v)` puts one `v` back). Returns `True` if something was undone, `False` if there is nothing to undo.

*   `redo(self) -> bool` — should re-apply the most recently undone change. Returns `True` if something was redone, `False` otherwise.

*   **Notes:**
    *   A failed `delete` (value not present) is not a change and is not recorded.
    *   Any new successful `add` or `delete` clears everything that could be redone.
    *   Queries (`get_median`, `count_in_range`, `get_kth_smallest`) are not changes.
    *   `undo` and `redo` can be chained: several `undo` calls walk back through history; several `redo` calls walk forward again.

### Examples

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
| --- | --- |
| `add(5)` | returns 1; [5] |
| `add(7)` | returns 2; [5, 7] |
| `delete(5)` | returns True; [7] |
| `delete(100)` | returns False; failed, not recorded |
| `undo()` | returns True; undoes `delete(5)`: [5, 7] |
| `get_median()` | returns 5 |
| `undo()` | returns True; undoes `add(7)`: [5] |
| `redo()` | returns True; re-applies `add(7)`: [5, 7] |
| `add(1)` | returns 3; a new change clears the redo history |
| `redo()` | returns False; nothing to redo |
| `undo()` | returns True; removes the 1: [5, 7] |
| `undo()` | returns True; removes the 7: [5] |
| `undo()` | returns True; removes the 5: [] |
| `undo()` | returns False; nothing left to undo |
| `get_median()` | returns None |

### Input/Output

*   **[execution time limit]** 3 seconds
*   **[memory limit]** 1 GB
