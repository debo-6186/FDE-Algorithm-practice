"""
Level 3 tests for Integer Container.

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


class TestLevel3(unittest.TestCase):
    def setUp(self):
        self.impl = IntegerContainerImpl()

    def test_level_3_case_01_example_from_spec(self):
        """The Level 3 example table."""
        run_steps(self, self.impl, [
            ('add', (4,), 1),
            ('add', (1,), 2),
            ('add', (7,), 3),
            ('add', (4,), 4),
            ('add', (9,), 5),
            ('count_in_range', (4, 7), 3),
            ('count_in_range', (5, 6), 0),
            ('count_in_range', (9, 1), 0),
            ('get_kth_smallest', (1,), 1),
            ('get_kth_smallest', (3,), 4),
            ('get_kth_smallest', (6,), None),
            ('get_kth_smallest', (0,), None),
        ])

    def test_level_3_case_02_queries_on_empty_container(self):
        run_steps(self, self.impl, [
            ('count_in_range', (-100, 100), 0),
            ('get_kth_smallest', (1,), None),
            ('get_kth_smallest', (-1,), None),
            ('add', (5,), 1),
            ('count_in_range', (-100, 100), 1),
            ('get_kth_smallest', (1,), 5),
        ])

    def test_level_3_case_03_inclusive_bounds(self):
        run_steps(self, self.impl, [
            ('add', (1,), 1),
            ('add', (2,), 2),
            ('add', (3,), 3),
            ('count_in_range', (1, 3), 3),
            ('count_in_range', (2, 2), 1),
            ('count_in_range', (3, 3), 1),
            ('count_in_range', (4, 10), 0),
            ('count_in_range', (-5, 0), 0),
        ])

    def test_level_3_case_04_kth_after_deletes(self):
        run_steps(self, self.impl, [
            ('add', (8,), 1),
            ('add', (3,), 2),
            ('add', (8,), 3),
            ('add', (1,), 4),
            ('get_kth_smallest', (4,), 8),
            ('delete', (8,), True),
            ('get_kth_smallest', (3,), 8),
            ('get_kth_smallest', (4,), None),
            ('count_in_range', (8, 8), 1),
        ])

    def test_level_3_case_05_randomized_sequence_301(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('get_median', (), None),
            ('get_kth_smallest', (7,), None),
            ('count_in_range', (1, 4), 0),
            ('add', (5,), 1),
            ('count_in_range', (-2, -5), 0),
            ('add', (3,), 2),
            ('add', (-4,), 3),
            ('get_median', (), 3),
            ('count_in_range', (5, 4), 0),
            ('delete', (-5,), False),
            ('get_kth_smallest', (2,), 3),
            ('delete', (3,), True),
            ('delete', (2,), False),
            ('add', (4,), 3),
            ('get_kth_smallest', (7,), None),
            ('add', (-5,), 4),
            ('add', (2,), 5),
            ('delete', (-2,), False),
            ('delete', (-3,), False),
            ('count_in_range', (3, 3), 0),
            ('add', (4,), 6),
            ('delete', (-5,), True),
            ('add', (0,), 6),
            ('add', (1,), 7),
            ('add', (-5,), 8),
            ('get_median', (), 1),
            ('get_kth_smallest', (4,), 1),
            ('get_median', (), 1),
            ('add', (5,), 9),
            ('add', (-4,), 10),
            ('delete', (1,), True),
            ('add', (4,), 10),
            ('delete', (4,), True),
            ('add', (-1,), 10),
            ('count_in_range', (0, -2), 0),
            ('get_kth_smallest', (2,), -4),
            ('count_in_range', (-4, 0), 4),
            ('get_median', (), 0),
            ('add', (-4,), 11),
            ('get_median', (), 0),
            ('add', (-4,), 12),
            ('count_in_range', (5, -3), 0),
            ('add', (-1,), 13),
            ('delete', (-1,), True),
            ('get_kth_smallest', (4,), -4),
            ('add', (4,), 13),
            ('get_median', (), 0),
            ('count_in_range', (-1, 0), 2),
            ('get_kth_smallest', (2,), -4),
            ('delete', (-1,), True),
            ('add', (0,), 13),
            ('delete', (-3,), False),
            ('delete', (2,), True),
            ('add', (2,), 13),
            ('add', (5,), 14),
            ('get_kth_smallest', (3,), -4),
            ('get_median', (), 0),
            ('get_kth_smallest', (8,), 2),
            ('add', (5,), 15),
            ('count_in_range', (-6, -4), 5),
        ])

    def test_level_3_case_06_randomized_sequence_302(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('count_in_range', (2, 2), 0),
            ('get_median', (), None),
            ('get_median', (), None),
            ('add', (-5,), 1),
            ('get_median', (), -5),
            ('get_median', (), -5),
            ('add', (3,), 2),
            ('get_median', (), -5),
            ('delete', (5,), False),
            ('add', (5,), 3),
            ('get_kth_smallest', (8,), None),
            ('add', (5,), 4),
            ('add', (4,), 5),
            ('add', (3,), 6),
            ('add', (5,), 7),
            ('count_in_range', (-5, -1), 1),
            ('get_median', (), 4),
            ('get_median', (), 4),
            ('delete', (3,), True),
            ('get_kth_smallest', (7,), None),
            ('get_median', (), 4),
            ('get_kth_smallest', (4,), 5),
            ('get_kth_smallest', (2,), 3),
            ('add', (-5,), 7),
            ('delete', (-2,), False),
            ('get_median', (), 4),
            ('delete', (-2,), False),
            ('delete', (3,), True),
            ('get_median', (), 4),
            ('get_kth_smallest', (3,), 4),
            ('add', (-5,), 7),
            ('add', (-5,), 8),
            ('add', (2,), 9),
            ('get_median', (), 2),
            ('add', (3,), 10),
            ('get_kth_smallest', (7,), 4),
            ('add', (-1,), 11),
            ('add', (2,), 12),
            ('add', (4,), 13),
            ('get_kth_smallest', (2,), -5),
            ('add', (-1,), 14),
            ('add', (-2,), 15),
            ('count_in_range', (2, -4), 0),
            ('get_median', (), 2),
            ('get_kth_smallest', (8,), 2),
            ('add', (-1,), 16),
            ('add', (-5,), 17),
            ('get_kth_smallest', (7,), -1),
            ('add', (0,), 18),
            ('get_median', (), -1),
            ('delete', (-3,), False),
            ('delete', (4,), True),
            ('get_kth_smallest', (4,), -5),
            ('get_median', (), -1),
            ('get_median', (), -1),
            ('add', (5,), 18),
            ('add', (-1,), 19),
            ('get_median', (), -1),
            ('delete', (2,), True),
            ('get_kth_smallest', (2,), -5),
        ])


if __name__ == "__main__":
    unittest.main()
