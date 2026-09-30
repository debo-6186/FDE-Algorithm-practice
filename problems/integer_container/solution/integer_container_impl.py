from __future__ import annotations

import bisect

from integer_container import IntegerContainer


class IntegerContainerImpl(IntegerContainer):
    """Sorted list + bisect. Every change goes through _insert/_remove so undo/redo reuse them."""

    def __init__(self):
        self._values: list[int] = []          # always kept sorted
        self._undo: list[tuple[str, int]] = []  # ("add" | "delete", value)
        self._redo: list[tuple[str, int]] = []

    # ---- primitives (no history bookkeeping) ------------------------------
    def _insert(self, value: int) -> None:
        bisect.insort(self._values, value)

    def _remove(self, value: int) -> bool:
        i = bisect.bisect_left(self._values, value)
        if i < len(self._values) and self._values[i] == value:
            self._values.pop(i)
            return True
        return False

    def _record(self, op: str, value: int) -> None:
        self._undo.append((op, value))
        self._redo.clear()                    # a new change invalidates redo

    # ---- Level 1 ------------------------------------------------------------
    def add(self, value: int) -> int:
        self._insert(value)
        self._record("add", value)
        return len(self._values)

    def delete(self, value: int) -> bool:
        if not self._remove(value):
            return False                      # failed ops are not recorded
        self._record("delete", value)
        return True

    # ---- Level 2 ------------------------------------------------------------
    def get_median(self) -> int | None:
        if not self._values:
            return None
        return self._values[(len(self._values) - 1) // 2]   # leftmost middle

    # ---- Level 3 ------------------------------------------------------------
    def count_in_range(self, low: int, high: int) -> int:
        if low > high:
            return 0
        return bisect.bisect_right(self._values, high) - bisect.bisect_left(self._values, low)

    def get_kth_smallest(self, k: int) -> int | None:
        if 1 <= k <= len(self._values):
            return self._values[k - 1]
        return None

    # ---- Level 4 ------------------------------------------------------------
    def undo(self) -> bool:
        if not self._undo:
            return False
        op, value = self._undo.pop()
        if op == "add":
            self._remove(value)
        else:
            self._insert(value)
        self._redo.append((op, value))
        return True

    def redo(self) -> bool:
        if not self._redo:
            return False
        op, value = self._redo.pop()
        if op == "add":
            self._insert(value)
        else:
            self._remove(value)
        self._undo.append((op, value))
        return True
