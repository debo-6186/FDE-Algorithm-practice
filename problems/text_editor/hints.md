# Hints: Text Editor

## Level 1
- Keep `text: str` and `cursor: int`. Every edit is "replace text[start:end] with new": write ONE helper and express insert, delete_forward and backspace through it.
- Clamp with `max(0, min(p, len(text)))`.

## Level 2
- Store the selection as `(start, end)` or `None`. When a selection exists, insert, delete and backspace all become "replace the selection".
- `select` sorts the two clamped positions, and the cursor goes to the right one.
- `copy` with no selection must keep the old clipboard.

## Level 3
- Snapshot-based undo (the memento pattern) is the simplest correct approach: before a change, push `(text, cursor)` onto the undo stack and clear the redo stack.
- Undo: push the current `(text, cursor)` onto redo, pop from undo. Redo is the mirror image.
- Only push when the text actually changes. Compare the old and new text in your single replace helper.

## Level 4
- Move text, cursor, selection and both stacks into a `Document` class. Keep a dict of documents and a `current` name. The clipboard stays on the editor.
- If Level 1-3 code reads `self.doc.<field>` (a property returning the current document), the refactor is mechanical.
