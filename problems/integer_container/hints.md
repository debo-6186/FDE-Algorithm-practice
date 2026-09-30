# Hints: Integer Container

## Level 1
- A plain Python list is enough. `list.remove(v)` removes one occurrence and raises `ValueError` if missing, so check `v in self.values` first.
- Return `len(...)` after the add, not before.

## Level 2
- Sort a copy (`sorted(self.values)`) or keep the list sorted with `bisect.insort`.
- Leftmost middle index for size n is `(n - 1) // 2`. It works for odd and even n.
- Empty container returns `None`, not `0`.

## Level 3
- With a sorted list: `bisect_right(values, high) - bisect_left(values, low)`.
- `k` is 1-based, so the answer is `values[k - 1]`. Guard both ends: `1 <= k <= len(values)`.

## Level 4
- Keep two stacks of operations: `undo_stack` and `redo_stack`, each holding `(op, value)` pairs.
- Push to `undo_stack` only when `add` / `delete` actually changed something, and clear `redo_stack` at the same time.
- `undo`: pop from `undo_stack`, apply the inverse, push onto `redo_stack`. `redo`: pop from `redo_stack`, apply the operation again, push back onto `undo_stack`.
- Route every mutation through small private helpers (`_insert`, `_remove`) so undo/redo don't re-record history.
