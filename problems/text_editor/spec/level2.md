## Level 2

Implement operations for selecting text, copying it to the clipboard, and pasting it back into the document.

*   `select(self, left: int, right: int) -> str` — should select the text between positions `left` and `right`. Both are clamped to `[0, len(document)]`; if `left > right` they are swapped. The cursor moves to `right` (after clamping/swapping). If the two positions are equal, nothing is selected. Returns the selected text (`""` if none).

*   `copy(self) -> str` — should copy the selected text to the clipboard. If nothing is selected, the clipboard doesn't change. Returns the clipboard content.

*   `paste(self) -> str` — should insert the clipboard content exactly like `insert`. Returns the document text.

*   **Changes to Level 1 operations:**
    *   `insert` / `paste` with an active selection **replace** the selected text; the cursor ends right after the inserted text.
    *   `delete_forward` / `backspace` with an active selection delete the selected text; the cursor ends where the selection started.
    *   `move_cursor` and every edit clear the selection. The clipboard starts empty.

### Examples

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
| --- | --- |
| `insert("abcdef")` | returns "abcdef" |
| `select(1, 4)` | returns "bcd"; cursor 4 |
| `copy()` | returns "bcd" |
| `insert("X")` | returns "aXef"; replaces the selection; cursor 2 |
| `paste()` | returns "aXbcdef"; cursor 5 |
| `select(6, 2)` | returns "bcde"; bounds swapped |
| `backspace()` | returns "aXf"; deletes the selection; cursor 2 |
| `get_cursor()` | returns 2 |
| `select(-5, 1)` | returns "a"; clamped to (0, 1) |
| `move_cursor(3)` | returns "aXf"; clears the selection |
| `paste()` | returns "aXfbcd"; clipboard still holds "bcd" |
| `select(2, 2)` | returns ""; nothing selected |
| `copy()` | returns "bcd"; nothing selected: clipboard unchanged |

### Input/Output

*   **[execution time limit]** 3 seconds
*   **[memory limit]** 1 GB
