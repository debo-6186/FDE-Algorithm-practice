"""
Level 1 tests for Job Scheduler.

Each test replays a sequence of calls on a fresh JobSchedulerImpl() and checks
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

from job_scheduler_impl import JobSchedulerImpl

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
        self.impl = JobSchedulerImpl()

    def test_level_1_case_01_example_from_spec(self):
        """The Level 1 example table."""
        run_steps(self, self.impl, [
            ('add_job', ('build', 5), True),
            ('add_job', ('test', 3), True),
            ('add_job', ('lint', 5), True),
            ('add_job', ('build', 1), False),
            ('next_job', (), 'build'),
            ('get_status', ('build',), 'running'),
            ('complete_job', ('test',), False),
            ('complete_job', ('build',), True),
            ('get_status', ('build',), 'done'),
            ('next_job', (), 'lint'),
            ('next_job', (), 'test'),
            ('next_job', (), None),
            ('get_status', ('deploy',), None),
        ])

    def test_level_1_case_02_empty_scheduler(self):
        run_steps(self, self.impl, [
            ('next_job', (), None),
            ('complete_job', ('x',), False),
            ('get_status', ('x',), None),
            ('add_job', ('x', 1), True),
            ('get_status', ('x',), 'queued'),
        ])

    def test_level_1_case_03_complete_twice(self):
        run_steps(self, self.impl, [
            ('add_job', ('a', 1), True),
            ('next_job', (), 'a'),
            ('complete_job', ('a',), True),
            ('complete_job', ('a',), False),
            ('add_job', ('a', 9), False),
        ])

    def test_level_1_case_04_negative_priorities_and_ties(self):
        run_steps(self, self.impl, [
            ('add_job', ('x', -1), True),
            ('add_job', ('y', -1), True),
            ('add_job', ('z', -5), True),
            ('next_job', (), 'x'),
            ('next_job', (), 'y'),
            ('next_job', (), 'z'),
        ])

    def test_level_1_case_05_several_running_at_once(self):
        run_steps(self, self.impl, [
            ('add_job', ('a', 1), True),
            ('add_job', ('b', 2), True),
            ('next_job', (), 'b'),
            ('next_job', (), 'a'),
            ('complete_job', ('a',), True),
            ('get_status', ('b',), 'running'),
            ('get_status', ('a',), 'done'),
        ])

    def test_level_1_case_06_randomized_sequence_20(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('add_job', ('f', 1), True),
            ('add_job', ('c', 0), True),
            ('add_job', ('g', 2), True),
            ('complete_job', ('b',), False),
            ('add_job', ('d', 0), True),
            ('add_job', ('c', 3), False),
            ('get_status', ('d',), 'queued'),
            ('next_job', (), 'g'),
            ('next_job', (), 'f'),
            ('next_job', (), 'c'),
            ('add_job', ('e', 3), True),
            ('next_job', (), 'e'),
            ('complete_job', ('a',), False),
            ('add_job', ('a', 1), True),
            ('add_job', ('g', 2), False),
            ('next_job', (), 'a'),
            ('add_job', ('a', 0), False),
            ('add_job', ('b', 1), True),
            ('complete_job', ('a',), True),
            ('add_job', ('f', 2), False),
            ('next_job', (), 'b'),
            ('complete_job', ('e',), True),
            ('complete_job', ('b',), True),
            ('get_status', ('c',), 'running'),
            ('complete_job', ('d',), False),
            ('add_job', ('d', 0), False),
            ('complete_job', ('g',), True),
            ('complete_job', ('c',), True),
            ('add_job', ('e', 0), False),
            ('next_job', (), 'd'),
            ('add_job', ('b', 0), False),
            ('add_job', ('c', 0), False),
            ('complete_job', ('g',), False),
            ('next_job', (), None),
            ('next_job', (), None),
            ('next_job', (), None),
            ('complete_job', ('g',), False),
            ('complete_job', ('a',), False),
            ('get_status', ('e',), 'done'),
            ('next_job', (), None),
        ])


if __name__ == "__main__":
    unittest.main()
