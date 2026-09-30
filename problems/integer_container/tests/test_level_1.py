"""
Level 1 tests for Integer Container.

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


class TestLevel1(unittest.TestCase):
    def setUp(self):
        self.impl = IntegerContainerImpl()

    def test_level_1_case_01_example_from_spec(self):
        """The Level 1 example table."""
        run_steps(self, self.impl, [
            ('add', (5,), 1),
            ('add', (10,), 2),
            ('add', (5,), 3),
            ('delete', (10,), True),
            ('delete', (1,), False),
            ('add', (1,), 3),
            ('delete', (5,), True),
            ('add', (-4,), 3),
        ])

    def test_level_1_case_02_delete_from_empty(self):
        """Deleting from an empty container fails."""
        run_steps(self, self.impl, [
            ('delete', (0,), False),
            ('delete', (7,), False),
            ('add', (0,), 1),
            ('delete', (0,), True),
            ('delete', (0,), False),
        ])

    def test_level_1_case_03_duplicates_removed_one_at_a_time(self):
        run_steps(self, self.impl, [
            ('add', (2,), 1),
            ('add', (2,), 2),
            ('add', (2,), 3),
            ('delete', (2,), True),
            ('delete', (2,), True),
            ('add', (3,), 2),
            ('delete', (2,), True),
            ('delete', (2,), False),
            ('delete', (3,), True),
            ('add', (2,), 1),
        ])

    def test_level_1_case_04_negative_and_zero_values(self):
        run_steps(self, self.impl, [
            ('add', (-1,), 1),
            ('add', (0,), 2),
            ('add', (-1000000,), 3),
            ('delete', (1,), False),
            ('delete', (-1,), True),
            ('delete', (-1000000,), True),
            ('add', (1000000,), 2),
        ])

    def test_level_1_case_05_size_counts_after_mixed_ops(self):
        run_steps(self, self.impl, [
            ('add', (10,), 1),
            ('add', (20,), 2),
            ('delete', (10,), True),
            ('add', (30,), 2),
            ('add', (10,), 3),
            ('delete', (20,), True),
            ('delete', (40,), False),
            ('add', (40,), 3),
            ('add', (40,), 4),
        ])

    def test_level_1_case_06_randomized_sequence_101(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('delete', (-2,), False),
            ('delete', (0,), False),
            ('add', (-5,), 1),
            ('delete', (3,), False),
            ('add', (4,), 2),
            ('add', (-1,), 3),
            ('add', (-2,), 4),
            ('add', (2,), 5),
            ('add', (-1,), 6),
            ('add', (-3,), 7),
            ('add', (2,), 8),
            ('delete', (0,), False),
            ('add', (2,), 9),
            ('add', (-2,), 10),
            ('delete', (1,), False),
            ('add', (-2,), 11),
            ('add', (1,), 12),
            ('add', (-1,), 13),
            ('add', (-4,), 14),
            ('delete', (4,), True),
            ('delete', (0,), False),
            ('delete', (-1,), True),
            ('add', (1,), 13),
            ('add', (1,), 14),
            ('add', (1,), 15),
            ('delete', (5,), False),
            ('add', (-5,), 16),
            ('add', (-2,), 17),
            ('delete', (-4,), True),
            ('add', (-5,), 17),
            ('add', (0,), 18),
            ('add', (-1,), 19),
            ('delete', (-3,), True),
            ('add', (1,), 19),
            ('add', (-1,), 20),
            ('add', (-3,), 21),
            ('add', (5,), 22),
            ('delete', (0,), True),
            ('delete', (4,), False),
            ('add', (-3,), 22),
        ])


if __name__ == "__main__":
    unittest.main()
