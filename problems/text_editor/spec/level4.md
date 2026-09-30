## Level 4

Implement operations for working with several documents at once.

*   `create_document(self, name: str) -> bool` — should create a new empty document called `name` without switching to it. Returns `False` if a document with that name exists (the initial document is called `"untitled"`).

*   `switch_document(self, name: str) -> str | None` — should make `name` the current document and return its text, or return `None` (and stay in the current document) if it doesn't exist.

*   **Notes:**
    *   Every document keeps its **own** text, cursor, selection and undo/redo history. All previous operations act on the current document.
    *   The clipboard is **shared** by all documents.

### Examples

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
| --- | --- |
| `insert("draft")` | returns "draft"; in `"untitled"` |
| `create_document("notes")` | returns True |
| `create_document("notes")` | returns False; already exists |
| `switch_document("notes")` | returns "" |
| `insert("todo")` | returns "todo" |
| `switch_document("untitled")` | returns "draft" |
| `select(0, 5)` | returns "draft" |
| `copy()` | returns "draft" |
| `switch_document("notes")` | returns "todo"; its cursor is still at 4 |
| `paste()` | returns "tododraft"; the clipboard is shared |
| `undo()` | returns "todo"; each document has its own history |
| `switch_document("untitled")` | returns "draft" |
| `undo()` | returns ""; undoes `insert("draft")` |
| `switch_document("missing")` | returns None |
| `get_cursor()` | returns 0; still in `"untitled"` |

### Input/Output

*   **[execution time limit]** 3 seconds
*   **[memory limit]** 1 GB
