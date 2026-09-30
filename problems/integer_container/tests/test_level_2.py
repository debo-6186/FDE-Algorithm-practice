"""
Level 2 tests for Integer Container.

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


class TestLevel2(unittest.TestCase):
    def setUp(self):
        self.impl = IntegerContainerImpl()

    def test_level_2_case_01_example_from_spec(self):
        """The Level 2 example table."""
        run_steps(self, self.impl, [
            ('get_median', (), None),
            ('add', (3,), 1),
            ('get_median', (), 3),
            ('add', (1,), 2),
            ('get_median', (), 1),
            ('add', (8,), 3),
            ('get_median', (), 3),
            ('add', (2,), 4),
            ('get_median', (), 2),
            ('delete', (2,), True),
            ('get_median', (), 3),
        ])

    def test_level_2_case_02_median_with_duplicates(self):
        run_steps(self, self.impl, [
            ('add', (5,), 1),
            ('add', (5,), 2),
            ('add', (1,), 3),
            ('get_median', (), 5),
            ('add', (1,), 4),
            ('get_median', (), 1),
            ('add', (9,), 5),
            ('get_median', (), 5),
        ])

    def test_level_2_case_03_median_after_emptying(self):
        run_steps(self, self.impl, [
            ('add', (4,), 1),
            ('delete', (4,), True),
            ('get_median', (), None),
            ('add', (-2,), 1),
            ('get_median', (), -2),
        ])

    def test_level_2_case_04_even_count_uses_left_middle(self):
        """[10, 20, 30, 40] -> 20, not 25 and not 30."""
        run_steps(self, self.impl, [
            ('add', (40,), 1),
            ('add', (10,), 2),
            ('add', (30,), 3),
            ('add', (20,), 4),
            ('get_median', (), 20),
        ])

    def test_level_2_case_05_insertion_order_does_not_matter(self):
        run_steps(self, self.impl, [
            ('add', (100,), 1),
            ('add', (-5,), 2),
            ('add', (50,), 3),
            ('add', (0,), 4),
            ('add', (75,), 5),
            ('get_median', (), 50),
            ('delete', (50,), True),
            ('get_median', (), 0),
            ('delete', (-5,), True),
            ('get_median', (), 75),
        ])

    def test_level_2_case_06_randomized_sequence_201(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('add', (0,), 1),
            ('get_median', (), 0),
            ('add', (-1,), 2),
            ('delete', (5,), False),
            ('get_median', (), -1),
            ('delete', (2,), False),
            ('get_median', (), -1),
            ('get_median', (), -1),
            ('add', (4,), 3),
            ('get_median', (), 0),
            ('add', (3,), 4),
            ('add', (-2,), 5),
            ('add', (-5,), 6),
            ('delete', (-4,), False),
            ('add', (3,), 7),
            ('delete', (-3,), False),
            ('get_median', (), 0),
            ('add', (4,), 8),
            ('add', (5,), 9),
            ('get_median', (), 3),
            ('delete', (2,), False),
            ('add', (4,), 10),
            ('delete', (3,), True),
            ('delete', (3,), True),
            ('get_median', (), 0),
            ('add', (-5,), 9),
            ('get_median', (), 0),
            ('get_median', (), 0),
            ('add', (1,), 10),
            ('delete', (-5,), True),
            ('add', (1,), 10),
            ('add', (-2,), 11),
            ('add', (-1,), 12),
            ('delete', (-4,), False),
            ('delete', (0,), True),
            ('add', (-1,), 12),
            ('add', (-3,), 13),
            ('get_median', (), -1),
            ('get_median', (), -1),
            ('delete', (4,), True),
            ('add', (-4,), 13),
            ('delete', (3,), False),
            ('add', (-4,), 14),
            ('add', (-5,), 15),
            ('delete', (2,), False),
            ('get_median', (), -1),
            ('add', (-5,), 16),
            ('add', (2,), 17),
            ('get_median', (), -1),
            ('delete', (0,), False),
        ])

    def test_level_2_case_07_randomized_sequence_202(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('get_median', (), None),
            ('get_median', (), None),
            ('get_median', (), None),
            ('add', (-2,), 1),
            ('get_median', (), -2),
            ('add', (1,), 2),
            ('get_median', (), -2),
            ('get_median', (), -2),
            ('add', (3,), 3),
            ('delete', (-2,), True),
            ('add', (2,), 3),
            ('add', (1,), 4),
            ('delete', (2,), True),
            ('add', (1,), 4),
            ('get_median', (), 1),
            ('add', (3,), 5),
            ('add', (-1,), 6),
            ('get_median', (), 1),
            ('get_median', (), 1),
            ('get_median', (), 1),
            ('delete', (-5,), False),
            ('add', (5,), 7),
            ('add', (-5,), 8),
            ('get_median', (), 1),
            ('delete', (-5,), True),
            ('add', (-2,), 8),
            ('add', (-4,), 9),
            ('delete', (-3,), False),
            ('add', (5,), 10),
            ('add', (1,), 11),
            ('add', (-1,), 12),
            ('delete', (-2,), True),
            ('delete', (-1,), True),
            ('delete', (2,), False),
            ('add', (0,), 11),
            ('add', (4,), 12),
            ('add', (1,), 13),
            ('get_median', (), 1),
            ('delete', (0,), True),
            ('get_median', (), 1),
            ('add', (-2,), 13),
            ('delete', (0,), False),
            ('add', (-2,), 14),
            ('delete', (-5,), False),
            ('add', (5,), 15),
            ('get_median', (), 1),
            ('delete', (-4,), True),
            ('delete', (-3,), False),
            ('delete', (4,), True),
            ('get_median', (), 1),
        ])


if __name__ == "__main__":
    unittest.main()
