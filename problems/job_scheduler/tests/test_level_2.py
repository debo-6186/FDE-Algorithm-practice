"""
Level 2 tests for Job Scheduler.

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


class TestLevel2(unittest.TestCase):
    def setUp(self):
        self.impl = JobSchedulerImpl()

    def test_level_2_case_01_example_from_spec(self):
        """The Level 2 example table."""
        run_steps(self, self.impl, [
            ('add_job', ('a', 1), True),
            ('add_job', ('b', 3), True),
            ('add_job', ('c', 3), True),
            ('peek_jobs', (2,), ['b', 'c']),
            ('peek_jobs', (10,), ['b', 'c', 'a']),
            ('next_job', (), 'b'),
            ('jobs_with_status', ('queued',), ['a', 'c']),
            ('jobs_with_status', ('running',), ['b']),
            ('jobs_with_status', ('done',), []),
        ])

    def test_level_2_case_02_peek_does_not_start(self):
        run_steps(self, self.impl, [
            ('add_job', ('a', 1), True),
            ('peek_jobs', (1,), ['a']),
            ('get_status', ('a',), 'queued'),
            ('peek_jobs', (0,), []),
            ('next_job', (), 'a'),
            ('peek_jobs', (3,), []),
        ])

    def test_level_2_case_03_status_lists_are_alphabetical(self):
        run_steps(self, self.impl, [
            ('add_job', ('zeta', 9), True),
            ('add_job', ('alpha', 1), True),
            ('add_job', ('Mid', 5), True),
            ('jobs_with_status', ('queued',), ['Mid', 'alpha', 'zeta']),
            ('peek_jobs', (3,), ['zeta', 'Mid', 'alpha']),
        ])

    def test_level_2_case_04_unknown_status(self):
        run_steps(self, self.impl, [
            ('add_job', ('a', 1), True),
            ('jobs_with_status', ('paused',), []),
        ])

    def test_level_2_case_05_randomized_sequence_39(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('add_job', ('b', 2), True),
            ('add_job', ('d', 0), True),
            ('add_job', ('b', 1), False),
            ('next_job', (), 'b'),
            ('add_job', ('g', 2), True),
            ('get_status', ('f',), None),
            ('add_job', ('g', 0), False),
            ('next_job', (), 'g'),
            ('add_job', ('a', 0), True),
            ('complete_job', ('d',), False),
            ('peek_jobs', (3,), ['d', 'a']),
            ('complete_job', ('c',), False),
            ('next_job', (), 'd'),
            ('complete_job', ('c',), False),
            ('complete_job', ('e',), False),
            ('add_job', ('f', 0), True),
            ('get_status', ('e',), None),
            ('jobs_with_status', ('canceled',), []),
            ('peek_jobs', (2,), ['a', 'f']),
            ('jobs_with_status', ('blocked',), []),
            ('get_status', ('d',), 'running'),
            ('add_job', ('d', 0), False),
            ('add_job', ('f', 2), False),
            ('next_job', (), 'a'),
            ('get_status', ('g',), 'running'),
            ('add_job', ('g', 3), False),
            ('jobs_with_status', ('queued',), ['f']),
            ('complete_job', ('a',), True),
            ('get_status', ('f',), 'queued'),
            ('complete_job', ('e',), False),
            ('complete_job', ('f',), False),
            ('next_job', (), 'f'),
            ('jobs_with_status', ('canceled',), []),
            ('get_status', ('a',), 'done'),
            ('complete_job', ('f',), True),
            ('next_job', (), None),
            ('peek_jobs', (5,), []),
            ('next_job', (), None),
            ('add_job', ('g', 3), False),
            ('next_job', (), None),
            ('next_job', (), None),
            ('jobs_with_status', ('canceled',), []),
            ('jobs_with_status', ('canceled',), []),
            ('add_job', ('b', 2), False),
            ('next_job', (), None),
            ('add_job', ('b', 0), False),
            ('jobs_with_status', ('queued',), []),
            ('get_status', ('a',), 'done'),
            ('jobs_with_status', ('blocked',), []),
            ('jobs_with_status', ('blocked',), []),
        ])

    def test_level_2_case_06_randomized_sequence_40(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('add_job', ('d', 0), True),
            ('add_job', ('b', 2), True),
            ('add_job', ('f', 1), True),
            ('add_job', ('c', 2), True),
            ('jobs_with_status', ('queued',), ['b', 'c', 'd', 'f']),
            ('complete_job', ('f',), False),
            ('add_job', ('f', 1), False),
            ('get_status', ('d',), 'queued'),
            ('peek_jobs', (1,), ['b']),
            ('peek_jobs', (0,), []),
            ('next_job', (), 'b'),
            ('add_job', ('e', 0), True),
            ('complete_job', ('a',), False),
            ('peek_jobs', (5,), ['c', 'f', 'd', 'e']),
            ('peek_jobs', (5,), ['c', 'f', 'd', 'e']),
            ('add_job', ('b', 2), False),
            ('get_status', ('c',), 'queued'),
            ('complete_job', ('b',), True),
            ('jobs_with_status', ('blocked',), []),
            ('complete_job', ('a',), False),
            ('add_job', ('b', 0), False),
            ('add_job', ('e', 2), False),
            ('add_job', ('g', 1), True),
            ('complete_job', ('a',), False),
            ('complete_job', ('f',), False),
            ('jobs_with_status', ('canceled',), []),
            ('jobs_with_status', ('canceled',), []),
            ('jobs_with_status', ('running',), []),
            ('add_job', ('a', 1), True),
            ('get_status', ('b',), 'done'),
            ('peek_jobs', (3,), ['c', 'f', 'g']),
            ('add_job', ('f', 3), False),
            ('add_job', ('a', 3), False),
            ('complete_job', ('b',), False),
            ('jobs_with_status', ('running',), []),
            ('add_job', ('c', 2), False),
            ('get_status', ('b',), 'done'),
            ('peek_jobs', (1,), ['c']),
            ('add_job', ('b', 0), False),
            ('peek_jobs', (1,), ['c']),
            ('complete_job', ('d',), False),
            ('jobs_with_status', ('done',), ['b']),
            ('complete_job', ('a',), False),
            ('peek_jobs', (3,), ['c', 'f', 'g']),
            ('jobs_with_status', ('running',), []),
            ('get_status', ('b',), 'done'),
            ('next_job', (), 'c'),
            ('add_job', ('c', 3), False),
            ('get_status', ('g',), 'queued'),
            ('complete_job', ('e',), False),
        ])


if __name__ == "__main__":
    unittest.main()
