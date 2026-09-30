## Level 1

The editor starts with one empty document and the cursor at position 0. Implement operations to insert text at the cursor, move the cursor, and delete characters.

*   `insert(self, text: str) -> str` — should insert `text` at the cursor; the cursor moves to the end of the inserted text. Returns the whole document text.

*   `move_cursor(self, position: int) -> str` — should move the cursor to `position`, clamped to `[0, len(document)]`. Returns the document text.

*   `delete_forward(self) -> str` — should delete the character right after the cursor (nothing happens at the end of the document). The cursor doesn't move. Returns the document text.

*   `backspace(self) -> str` — should delete the character right before the cursor and move the cursor one position left (nothing happens at position 0). Returns the document text.

*   `get_cursor(self) -> int` — should return the cursor position.

### Examples

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
| --- | --- |
| `insert("Hello")` | returns "Hello"; cursor 5 |
| `insert(" world")` | returns "Hello world"; cursor 11 |
| `move_cursor(5)` | returns "Hello world" |
| `insert(",")` | returns "Hello, world"; cursor 6 |
| `get_cursor()` | returns 6 |
| `delete_forward()` | returns "Hello,world"; removes the space after the cursor |
| `backspace()` | returns "Helloworld"; removes the comma; cursor 5 |
| `move_cursor(100)` | returns "Helloworld"; clamped to 10 |
| `delete_forward()` | returns "Helloworld"; nothing after the cursor |
| `move_cursor(-3)` | returns "Helloworld"; clamped to 0 |
| `backspace()` | returns "Helloworld"; nothing before the cursor |
| `get_cursor()` | returns 0 |

### Input/Output

*   **[execution time limit]** 3 seconds
*   **[memory limit]** 1 GB
