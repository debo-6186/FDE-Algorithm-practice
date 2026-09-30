"""
Level 4 tests for Integer Container.

Each test replays a sequence of calls on a fresh IntegerContainerImpl() and checks
every return value, in order.  A failure message tells you which step failed, e.g.
    step 4: transfer(6, 'a', 'b', 50) returned 10, expected None
ANY means the return value of that call is not checked.
Raises(SomeError) means the call must raise that exception.
"""
from __future__ import annotations

import os
import sys
import traceback
import unittest

from integer_container_impl import IntegerContainerImpl

ANY = object()


class Raises:
    def __init__(self, exc):
        self.exc = exc


def _describe(exc):
    frames = traceback.extract_tb(exc.__traceback__)
    mine = [f for f in frames if not f.filename.startswith(sys.base_prefix) and "site-packages" not in f.filename]
    frame = (mine or frames or [None])[-1]
    where = f"  [{os.path.basename(frame.filename)} line {frame.lineno}: {frame.line}]" if frame else ""
    return f"{type(exc).__name__}: {exc}{where}"


def run_steps(tc, obj, steps):
    for i, (method, args, expected) in enumerate(steps, 1):
        call = f"{method}({', '.join(repr(a) for a in args)})"
        try:
            result = getattr(obj, method)(*args)
        except Exception as exc:  # noqa: BLE001
            if isinstance(expected, Raises) and isinstance(exc, expected.exc):
                continue
            tc.fail(f"step {i}: {call} raised {_describe(exc)}")
        if isinstance(expected, Raises):
            tc.fail(f"step {i}: {call} returned {result!r}, expected it to raise {expected.exc.__name__}")
        if expected is not ANY and result != expected:
            tc.fail(f"step {i}: {call} returned {result!r}, expected {expected!r}")


class TestLevel4(unittest.TestCase):
    def setUp(self):
        self.impl = IntegerContainerImpl()

    def test_level_4_case_01_example_from_spec(self):
        """The Level 4 example table."""
        run_steps(self, self.impl, [
            ('add', (5,), 1),
            ('add', (7,), 2),
            ('delete', (5,), True),
            ('delete', (100,), False),
            ('undo', (), True),
            ('get_median', (), 5),
            ('undo', (), True),
            ('redo', (), True),
            ('add', (1,), 3),
            ('redo', (), False),
            ('undo', (), True),
            ('undo', (), True),
            ('undo', (), True),
            ('undo', (), False),
            ('get_median', (), None),
        ])

    def test_level_4_case_02_nothing_to_undo_or_redo(self):
        run_steps(self, self.impl, [
            ('undo', (), False),
            ('redo', (), False),
            ('delete', (3,), False),
            ('undo', (), False),
            ('add', (3,), 1),
            ('undo', (), True),
            ('redo', (), True),
            ('get_median', (), 3),
        ])

    def test_level_4_case_03_undo_redo_round_trip(self):
        run_steps(self, self.impl, [
            ('add', (1,), 1),
            ('add', (2,), 2),
            ('add', (3,), 3),
            ('undo', (), True),
            ('undo', (), True),
            ('undo', (), True),
            ('get_median', (), None),
            ('redo', (), True),
            ('redo', (), True),
            ('redo', (), True),
            ('redo', (), False),
            ('get_median', (), 2),
            ('count_in_range', (1, 3), 3),
        ])

    def test_level_4_case_04_undo_delete_of_duplicate(self):
        run_steps(self, self.impl, [
            ('add', (4,), 1),
            ('add', (4,), 2),
            ('delete', (4,), True),
            ('count_in_range', (4, 4), 1),
            ('undo', (), True),
            ('count_in_range', (4, 4), 2),
            ('redo', (), True),
            ('count_in_range', (4, 4), 1),
        ])

    def test_level_4_case_05_new_change_clears_redo_but_not_undo(self):
        run_steps(self, self.impl, [
            ('add', (10,), 1),
            ('add', (20,), 2),
            ('undo', (), True),
            ('delete', (10,), True),
            ('redo', (), False),
            ('undo', (), True),
            ('get_kth_smallest', (1,), 10),
            ('undo', (), True),
            ('get_median', (), None),
            ('undo', (), False),
        ])

    def test_level_4_case_06_queries_do_not_affect_history(self):
        run_steps(self, self.impl, [
            ('add', (6,), 1),
            ('get_median', (), 6),
            ('count_in_range', (0, 10), 1),
            ('get_kth_smallest', (1,), 6),
            ('undo', (), True),
            ('get_median', (), None),
            ('undo', (), False),
        ])

    def test_level_4_case_07_randomized_sequence_401(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('get_kth_smallest', (1,), None),
            ('redo', (), False),
            ('undo', (), False),
            ('redo', (), False),
            ('get_kth_smallest', (5,), None),
            ('delete', (-1,), False),
            ('get_kth_smallest', (2,), None),
            ('add', (5,), 1),
            ('add', (-1,), 2),
            ('add', (3,), 3),
            ('add', (5,), 4),
            ('get_kth_smallest', (1,), -1),
            ('undo', (), True),
            ('add', (5,), 4),
            ('add', (-3,), 5),
            ('undo', (), True),
            ('get_median', (), 3),
            ('redo', (), True),
            ('delete', (2,), False),
            ('undo', (), True),
            ('redo', (), True),
            ('undo', (), True),
            ('add', (1,), 5),
            ('delete', (4,), False),
            ('undo', (), True),
            ('delete', (4,), False),
            ('add', (2,), 5),
            ('get_median', (), 3),
            ('undo', (), True),
            ('undo', (), True),
            ('undo', (), True),
            ('undo', (), True),
            ('get_kth_smallest', (5,), None),
            ('undo', (), True),
            ('add', (4,), 1),
            ('redo', (), False),
            ('add', (-5,), 2),
            ('redo', (), False),
            ('delete', (-1,), False),
            ('undo', (), True),
            ('add', (4,), 2),
            ('add', (4,), 3),
            ('undo', (), True),
            ('redo', (), True),
            ('get_median', (), 4),
            ('delete', (0,), False),
            ('delete', (3,), False),
            ('add', (-5,), 4),
            ('delete', (2,), False),
            ('undo', (), True),
            ('get_kth_smallest', (6,), None),
            ('add', (3,), 4),
            ('add', (-5,), 5),
            ('add', (-5,), 6),
            ('undo', (), True),
            ('get_median', (), 4),
            ('get_kth_smallest', (7,), None),
            ('add', (0,), 6),
            ('delete', (3,), True),
            ('add', (0,), 6),
            ('get_kth_smallest', (1,), -5),
            ('add', (2,), 7),
            ('get_median', (), 2),
            ('get_median', (), 2),
            ('add', (-3,), 8),
            ('add', (1,), 9),
            ('add', (2,), 10),
            ('add', (-3,), 11),
            ('add', (2,), 12),
            ('undo', (), True),
        ])

    def test_level_4_case_08_randomized_sequence_402(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('get_kth_smallest', (1,), None),
            ('redo', (), False),
            ('redo', (), False),
            ('undo', (), False),
            ('get_kth_smallest', (6,), None),
            ('redo', (), False),
            ('delete', (-5,), False),
            ('get_kth_smallest', (7,), None),
            ('delete', (-3,), False),
            ('undo', (), False),
            ('get_kth_smallest', (1,), None),
            ('delete', (4,), False),
            ('get_kth_smallest', (0,), None),
            ('delete', (5,), False),
            ('undo', (), False),
            ('get_kth_smallest', (4,), None),
            ('undo', (), False),
            ('add', (4,), 1),
            ('add', (4,), 2),
            ('undo', (), True),
            ('undo', (), True),
            ('undo', (), False),
            ('get_median', (), None),
            ('undo', (), False),
            ('get_median', (), None),
            ('delete', (1,), False),
            ('get_median', (), None),
            ('redo', (), True),
            ('get_median', (), 4),
            ('delete', (2,), False),
            ('get_median', (), 4),
            ('get_median', (), 4),
            ('undo', (), True),
            ('add', (-2,), 1),
            ('delete', (5,), False),
            ('redo', (), False),
            ('undo', (), True),
            ('delete', (2,), False),
            ('delete', (5,), False),
            ('add', (-3,), 1),
            ('add', (-2,), 2),
            ('redo', (), False),
            ('undo', (), True),
            ('undo', (), True),
            ('delete', (-5,), False),
            ('delete', (-3,), False),
            ('redo', (), True),
            ('add', (4,), 2),
            ('get_kth_smallest', (1,), -3),
            ('redo', (), False),
            ('delete', (3,), False),
            ('redo', (), False),
            ('add', (-3,), 3),
            ('redo', (), False),
            ('redo', (), False),
            ('delete', (0,), False),
            ('delete', (-2,), False),
            ('get_median', (), -3),
            ('undo', (), True),
            ('add', (-5,), 3),
            ('redo', (), False),
            ('redo', (), False),
            ('undo', (), True),
            ('get_kth_smallest', (8,), None),
            ('undo', (), True),
            ('get_kth_smallest', (2,), None),
            ('undo', (), True),
            ('delete', (3,), False),
            ('add', (-4,), 1),
            ('add', (-4,), 2),
        ])

    def test_level_4_case_09_randomized_sequence_403(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('get_median', (), None),
            ('undo', (), False),
            ('add', (-3,), 1),
            ('undo', (), True),
            ('get_kth_smallest', (2,), None),
            ('redo', (), True),
            ('undo', (), True),
            ('redo', (), True),
            ('delete', (-4,), False),
            ('undo', (), True),
            ('delete', (-3,), False),
            ('delete', (2,), False),
            ('delete', (-2,), False),
            ('redo', (), True),
            ('get_kth_smallest', (0,), None),
            ('get_kth_smallest', (8,), None),
            ('redo', (), False),
            ('get_median', (), -3),
            ('add', (4,), 2),
            ('delete', (0,), False),
            ('undo', (), True),
            ('add', (0,), 2),
            ('undo', (), True),
            ('add', (0,), 2),
            ('redo', (), False),
            ('add', (3,), 3),
            ('redo', (), False),
            ('get_kth_smallest', (2,), 0),
            ('get_kth_smallest', (1,), -3),
            ('delete', (-4,), False),
            ('add', (-3,), 4),
            ('redo', (), False),
            ('add', (-2,), 5),
            ('add', (-1,), 6),
            ('undo', (), True),
            ('get_kth_smallest', (6,), None),
            ('undo', (), True),
            ('get_kth_smallest', (0,), None),
            ('undo', (), True),
            ('get_median', (), 0),
            ('undo', (), True),
            ('get_median', (), -3),
            ('undo', (), True),
            ('delete', (2,), False),
            ('delete', (-4,), False),
            ('undo', (), True),
            ('add', (-3,), 1),
            ('delete', (-2,), False),
            ('undo', (), True),
            ('delete', (0,), False),
            ('delete', (4,), False),
            ('add', (5,), 1),
            ('add', (5,), 2),
            ('undo', (), True),
            ('undo', (), True),
            ('get_median', (), None),
            ('undo', (), False),
            ('get_kth_smallest', (4,), None),
            ('undo', (), False),
            ('redo', (), True),
            ('get_median', (), 5),
            ('delete', (-3,), False),
            ('redo', (), True),
            ('undo', (), True),
            ('add', (2,), 2),
            ('get_median', (), 2),
            ('get_median', (), 2),
            ('add', (-5,), 3),
            ('undo', (), True),
            ('undo', (), True),
        ])


if __name__ == "__main__":
    unittest.main()
