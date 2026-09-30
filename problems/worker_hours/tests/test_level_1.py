"""
Level 1 tests for Worker Hours & Payroll.

Each test replays a sequence of calls on a fresh WorkerRegistryImpl() and checks
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

from worker_registry_impl import WorkerRegistryImpl

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
        self.impl = WorkerRegistryImpl()

    def test_level_1_case_01_example_from_spec(self):
        """The Level 1 example table."""
        run_steps(self, self.impl, [
            ('add_worker', ('Ann', 'Middle Developer', 150), True),
            ('add_worker', ('Ann', 'Junior Developer', 100), False),
            ('register', ('Ann', 10), 'registered'),
            ('register', ('Ann', 25), 'registered'),
            ('get', ('Ann',), 15),
            ('register', ('Ann', 40), 'registered'),
            ('get', ('Ann',), 15),
            ('register', ('Ann', 67), 'registered'),
            ('get', ('Ann',), 42),
            ('get', ('Walter',), None),
            ('register', ('Walter', 120), 'invalid_request'),
        ])

    def test_level_1_case_02_new_worker_has_zero(self):
        run_steps(self, self.impl, [
            ('add_worker', ('a', 'p', 1), True),
            ('get', ('a',), 0),
            ('register', ('a', 5), 'registered'),
            ('get', ('a',), 0),
        ])

    def test_level_1_case_03_workers_are_tracked_separately(self):
        run_steps(self, self.impl, [
            ('add_worker', ('a', 'p', 1), True),
            ('add_worker', ('b', 'p', 1), True),
            ('register', ('a', 1), 'registered'),
            ('register', ('b', 2), 'registered'),
            ('register', ('a', 10), 'registered'),
            ('register', ('b', 30), 'registered'),
            ('get', ('a',), 9),
            ('get', ('b',), 28),
        ])

    def test_level_1_case_04_many_sessions(self):
        run_steps(self, self.impl, [
            ('add_worker', ('w', 'p', 1), True),
            ('register', ('w', 1), 'registered'),
            ('register', ('w', 2), 'registered'),
            ('register', ('w', 3), 'registered'),
            ('register', ('w', 5), 'registered'),
            ('register', ('w', 8), 'registered'),
            ('register', ('w', 13), 'registered'),
            ('get', ('w',), 8),
        ])

    def test_level_1_case_05_failed_add_keeps_original(self):
        run_steps(self, self.impl, [
            ('add_worker', ('x', 'Dev', 10), True),
            ('register', ('x', 1), 'registered'),
            ('add_worker', ('x', 'Dev', 99), False),
            ('register', ('x', 4), 'registered'),
            ('get', ('x',), 3),
        ])

    def test_level_1_case_06_randomized_sequence_17(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('add_worker', ('dee', 'QA', 5), True),
            ('add_worker', ('bob', 'Ops', 5), True),
            ('add_worker', ('amy', 'Dev', 10), True),
            ('register', ('dee', 9), 'registered'),
            ('get', ('cal',), None),
            ('register', ('dee', 14), 'registered'),
            ('get', ('amy',), 0),
            ('add_worker', ('bob', 'Ops', 2), False),
            ('register', ('amy', 17), 'registered'),
            ('register', ('amy', 34), 'registered'),
            ('get', ('dee',), 5),
            ('register', ('zed', 39), 'invalid_request'),
            ('register', ('dee', 56), 'registered'),
            ('get', ('amy',), 17),
            ('register', ('zed', 58), 'invalid_request'),
            ('get', ('cal',), None),
            ('add_worker', ('cal', 'Ops', 1), True),
            ('get', ('bob',), 0),
            ('add_worker', ('bob', 'Ops', 5), False),
            ('add_worker', ('cal', 'Dev', 2), False),
            ('register', ('cal', 70), 'registered'),
            ('register', ('cal', 74), 'registered'),
            ('get', ('zed',), None),
            ('register', ('cal', 75), 'registered'),
            ('add_worker', ('amy', 'QA', 5), False),
            ('register', ('amy', 82), 'registered'),
            ('register', ('amy', 98), 'registered'),
            ('add_worker', ('bob', 'QA', 10), False),
            ('register', ('zed', 111), 'invalid_request'),
            ('register', ('cal', 116), 'registered'),
            ('register', ('bob', 118), 'registered'),
            ('get', ('zed',), None),
            ('register', ('cal', 129), 'registered'),
            ('add_worker', ('amy', 'Ops', 5), False),
            ('get', ('dee',), 5),
            ('register', ('zed', 132), 'invalid_request'),
            ('register', ('bob', 140), 'registered'),
            ('register', ('cal', 159), 'registered'),
            ('add_worker', ('amy', 'Ops', 10), False),
            ('register', ('dee', 167), 'registered'),
        ])


if __name__ == "__main__":
    unittest.main()
