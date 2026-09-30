"""
Level 4 tests for Job Scheduler.

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


class TestLevel4(unittest.TestCase):
    def setUp(self):
        self.impl = JobSchedulerImpl()

    def test_level_4_case_01_example_from_spec(self):
        """The Level 4 example table."""
        run_steps(self, self.impl, [
            ('add_job', ('a', 1), True),
            ('add_job', ('b', 1), True),
            ('add_job', ('c', 1), True),
            ('add_job', ('d', 1), True),
            ('add_dependency', ('b', 'a'), True),
            ('add_dependency', ('c', 'b'), True),
            ('add_dependency', ('d', 'a'), True),
            ('cancel_job', ('b',), ['b', 'c']),
            ('get_status', ('c',), 'canceled'),
            ('cancel_job', ('c',), []),
            ('next_job', (), 'a'),
            ('cancel_job', ('a',), []),
            ('complete_job', ('a',), True),
            ('next_job', (), 'd'),
            ('add_job', ('e', 2), True),
            ('add_dependency', ('e', 'b'), False),
            ('jobs_with_status', ('canceled',), ['b', 'c']),
        ])

    def test_level_4_case_02_cancel_unknown_or_done(self):
        run_steps(self, self.impl, [
            ('cancel_job', ('x',), []),
            ('add_job', ('x', 1), True),
            ('next_job', (), 'x'),
            ('complete_job', ('x',), True),
            ('cancel_job', ('x',), []),
        ])

    def test_level_4_case_03_diamond_cancels_each_job_once(self):
        run_steps(self, self.impl, [
            ('add_job', ('top', 1), True),
            ('add_job', ('l', 1), True),
            ('add_job', ('r', 1), True),
            ('add_job', ('bottom', 1), True),
            ('add_dependency', ('l', 'top'), True),
            ('add_dependency', ('r', 'top'), True),
            ('add_dependency', ('bottom', 'l'), True),
            ('add_dependency', ('bottom', 'r'), True),
            ('cancel_job', ('top',), ['bottom', 'l', 'r', 'top']),
            ('peek_jobs', (5,), []),
        ])

    def test_level_4_case_04_cancel_blocked_leaves_prerequisite(self):
        run_steps(self, self.impl, [
            ('add_job', ('a', 1), True),
            ('add_job', ('b', 1), True),
            ('add_dependency', ('b', 'a'), True),
            ('cancel_job', ('b',), ['b']),
            ('get_status', ('a',), 'queued'),
            ('next_job', (), 'a'),
            ('next_job', (), None),
        ])

    def test_level_4_case_05_canceled_jobs_never_start(self):
        run_steps(self, self.impl, [
            ('add_job', ('a', 5), True),
            ('add_job', ('b', 1), True),
            ('cancel_job', ('a',), ['a']),
            ('peek_jobs', (5,), ['b']),
            ('next_job', (), 'b'),
            ('next_job', (), None),
            ('add_dependency', ('a', 'b'), False),
        ])

    def test_level_4_case_06_randomized_sequence_68(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('add_job', ('f', 3), True),
            ('add_job', ('f', 0), False),
            ('add_job', ('e', 1), True),
            ('get_status', ('c',), None),
            ('add_dependency', ('f', 'c'), False),
            ('get_status', ('e',), 'queued'),
            ('complete_job', ('e',), False),
            ('jobs_with_status', ('queued',), ['e', 'f']),
            ('add_job', ('f', 3), False),
            ('add_job', ('c', 0), True),
            ('add_job', ('e', 1), False),
            ('next_job', (), 'f'),
            ('add_job', ('g', 3), True),
            ('get_status', ('d',), None),
            ('peek_jobs', (5,), ['g', 'e', 'c']),
            ('add_dependency', ('a', 'e'), False),
            ('cancel_job', ('b',), []),
            ('jobs_with_status', ('running',), ['f']),
            ('add_dependency', ('a', 'a'), False),
            ('cancel_job', ('d',), []),
            ('complete_job', ('e',), False),
            ('add_dependency', ('a', 'b'), False),
            ('get_status', ('d',), None),
            ('get_status', ('f',), 'running'),
            ('next_job', (), 'g'),
            ('jobs_with_status', ('queued',), ['c', 'e']),
            ('cancel_job', ('d',), []),
            ('complete_job', ('b',), False),
            ('add_dependency', ('a', 'g'), False),
            ('add_dependency', ('f', 'c'), False),
            ('add_dependency', ('g', 'g'), False),
            ('next_job', (), 'e'),
            ('add_dependency', ('e', 'b'), False),
            ('get_status', ('d',), None),
            ('get_status', ('e',), 'running'),
            ('peek_jobs', (3,), ['c']),
            ('add_dependency', ('c', 'g'), True),
            ('add_job', ('f', 0), False),
            ('get_status', ('b',), None),
            ('peek_jobs', (4,), []),
            ('add_dependency', ('b', 'g'), False),
            ('complete_job', ('g',), True),
            ('complete_job', ('a',), False),
            ('add_dependency', ('a', 'e'), False),
            ('complete_job', ('g',), False),
            ('next_job', (), 'c'),
            ('complete_job', ('c',), True),
            ('add_job', ('d', 3), True),
            ('cancel_job', ('g',), []),
            ('complete_job', ('c',), False),
            ('add_job', ('c', 3), False),
            ('complete_job', ('f',), True),
            ('next_job', (), 'd'),
            ('add_dependency', ('c', 'f'), False),
            ('next_job', (), None),
            ('get_status', ('d',), 'running'),
            ('add_dependency', ('e', 'c'), False),
            ('get_status', ('a',), None),
            ('cancel_job', ('c',), []),
            ('cancel_job', ('d',), []),
            ('add_job', ('b', 0), True),
            ('next_job', (), 'b'),
            ('complete_job', ('f',), False),
            ('add_job', ('a', 3), True),
            ('add_dependency', ('f', 'e'), False),
            ('next_job', (), 'a'),
            ('next_job', (), None),
            ('complete_job', ('g',), False),
            ('complete_job', ('a',), True),
            ('add_job', ('e', 2), False),
            ('get_status', ('c',), 'done'),
            ('cancel_job', ('g',), []),
            ('add_dependency', ('b', 'e'), False),
            ('cancel_job', ('c',), []),
            ('add_dependency', ('d', 'a'), False),
            ('add_job', ('d', 0), False),
            ('complete_job', ('d',), True),
            ('complete_job', ('d',), False),
            ('next_job', (), None),
            ('jobs_with_status', ('canceled',), []),
            ('cancel_job', ('d',), []),
            ('complete_job', ('d',), False),
            ('jobs_with_status', ('done',), ['a', 'c', 'd', 'f', 'g']),
            ('add_job', ('a', 2), False),
            ('next_job', (), None),
            ('peek_jobs', (2,), []),
            ('next_job', (), None),
            ('add_dependency', ('e', 'a'), False),
            ('cancel_job', ('b',), []),
            ('jobs_with_status', ('running',), ['b', 'e']),
        ])

    def test_level_4_case_07_randomized_sequence_69(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('add_job', ('f', 0), True),
            ('add_job', ('a', 1), True),
            ('add_job', ('a', 2), False),
            ('complete_job', ('g',), False),
            ('add_dependency', ('g', 'e'), False),
            ('get_status', ('g',), None),
            ('get_status', ('d',), None),
            ('add_dependency', ('c', 'e'), False),
            ('peek_jobs', (1,), ['a']),
            ('get_status', ('d',), None),
            ('add_job', ('c', 1), True),
            ('next_job', (), 'a'),
            ('next_job', (), 'c'),
            ('cancel_job', ('f',), ['f']),
            ('peek_jobs', (0,), []),
            ('add_job', ('e', 0), True),
            ('next_job', (), 'e'),
            ('add_dependency', ('c', 'a'), False),
            ('add_job', ('b', 0), True),
            ('next_job', (), 'b'),
            ('complete_job', ('d',), False),
            ('jobs_with_status', ('done',), []),
            ('jobs_with_status', ('canceled',), ['f']),
            ('get_status', ('c',), 'running'),
            ('add_job', ('a', 2), False),
            ('complete_job', ('f',), False),
            ('add_dependency', ('c', 'b'), False),
            ('jobs_with_status', ('blocked',), []),
            ('next_job', (), None),
            ('next_job', (), None),
            ('jobs_with_status', ('running',), ['a', 'b', 'c', 'e']),
            ('jobs_with_status', ('blocked',), []),
            ('add_dependency', ('c', 'f'), False),
            ('peek_jobs', (2,), []),
            ('jobs_with_status', ('canceled',), ['f']),
            ('complete_job', ('a',), True),
            ('add_dependency', ('f', 'd'), False),
            ('add_job', ('f', 2), False),
            ('get_status', ('b',), 'running'),
            ('add_job', ('g', 3), True),
            ('complete_job', ('b',), True),
            ('jobs_with_status', ('running',), ['c', 'e']),
            ('add_job', ('a', 0), False),
            ('get_status', ('d',), None),
            ('peek_jobs', (4,), ['g']),
            ('add_dependency', ('g', 'c'), True),
            ('add_job', ('d', 1), True),
            ('add_dependency', ('e', 'a'), False),
            ('add_dependency', ('a', 'g'), False),
            ('add_dependency', ('g', 'd'), True),
            ('add_dependency', ('e', 'd'), False),
            ('add_dependency', ('f', 'e'), False),
            ('add_dependency', ('c', 'a'), False),
            ('complete_job', ('e',), True),
            ('next_job', (), 'd'),
            ('get_status', ('g',), 'blocked'),
            ('add_dependency', ('g', 'b'), True),
            ('add_job', ('c', 0), False),
            ('add_dependency', ('a', 'f'), False),
            ('jobs_with_status', ('running',), ['c', 'd']),
            ('add_job', ('g', 1), False),
            ('complete_job', ('e',), False),
            ('peek_jobs', (0,), []),
            ('peek_jobs', (2,), []),
            ('add_job', ('e', 3), False),
            ('complete_job', ('e',), False),
            ('complete_job', ('d',), True),
            ('add_dependency', ('d', 'd'), False),
            ('jobs_with_status', ('blocked',), ['g']),
            ('cancel_job', ('b',), []),
            ('add_job', ('g', 1), False),
            ('complete_job', ('f',), False),
            ('jobs_with_status', ('canceled',), ['f']),
            ('cancel_job', ('d',), []),
            ('complete_job', ('c',), True),
            ('complete_job', ('d',), False),
            ('add_job', ('b', 2), False),
            ('next_job', (), 'g'),
            ('next_job', (), None),
            ('get_status', ('c',), 'done'),
            ('complete_job', ('d',), False),
            ('next_job', (), None),
            ('next_job', (), None),
            ('jobs_with_status', ('blocked',), []),
            ('complete_job', ('f',), False),
            ('cancel_job', ('a',), []),
            ('next_job', (), None),
            ('cancel_job', ('g',), []),
            ('add_job', ('a', 1), False),
            ('next_job', (), None),
        ])

    def test_level_4_case_08_randomized_sequence_70(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('add_job', ('a', 2), True),
            ('add_job', ('f', 3), True),
            ('add_job', ('d', 1), True),
            ('complete_job', ('a',), False),
            ('next_job', (), 'f'),
            ('jobs_with_status', ('blocked',), []),
            ('add_dependency', ('b', 'd'), False),
            ('jobs_with_status', ('done',), []),
            ('add_dependency', ('d', 'g'), False),
            ('add_dependency', ('g', 'a'), False),
            ('add_job', ('d', 2), False),
            ('complete_job', ('b',), False),
            ('add_job', ('d', 0), False),
            ('get_status', ('g',), None),
            ('add_dependency', ('g', 'a'), False),
            ('add_job', ('e', 1), True),
            ('jobs_with_status', ('queued',), ['a', 'd', 'e']),
            ('peek_jobs', (0,), []),
            ('add_dependency', ('g', 'f'), False),
            ('complete_job', ('e',), False),
            ('add_dependency', ('a', 'b'), False),
            ('add_dependency', ('e', 'g'), False),
            ('peek_jobs', (5,), ['a', 'd', 'e']),
            ('complete_job', ('a',), False),
            ('next_job', (), 'a'),
            ('add_dependency', ('e', 'e'), False),
            ('add_dependency', ('b', 'f'), False),
            ('add_job', ('c', 2), True),
            ('add_dependency', ('f', 'b'), False),
            ('jobs_with_status', ('blocked',), []),
            ('cancel_job', ('a',), []),
            ('add_job', ('b', 2), True),
            ('add_dependency', ('c', 'f'), True),
            ('jobs_with_status', ('blocked',), ['c']),
            ('add_dependency', ('a', 'd'), False),
            ('complete_job', ('a',), True),
            ('next_job', (), 'b'),
            ('peek_jobs', (4,), ['d', 'e']),
            ('jobs_with_status', ('done',), ['a']),
            ('add_job', ('c', 0), False),
            ('add_job', ('a', 0), False),
            ('get_status', ('c',), 'blocked'),
            ('get_status', ('b',), 'running'),
            ('get_status', ('g',), None),
            ('add_job', ('f', 3), False),
            ('complete_job', ('f',), True),
            ('peek_jobs', (4,), ['c', 'd', 'e']),
            ('cancel_job', ('b',), []),
            ('jobs_with_status', ('queued',), ['c', 'd', 'e']),
            ('get_status', ('e',), 'queued'),
            ('add_dependency', ('a', 'e'), False),
            ('add_job', ('d', 3), False),
            ('complete_job', ('c',), False),
            ('next_job', (), 'c'),
            ('jobs_with_status', ('done',), ['a', 'f']),
            ('get_status', ('f',), 'done'),
            ('add_dependency', ('b', 'd'), False),
            ('complete_job', ('b',), True),
            ('complete_job', ('g',), False),
            ('peek_jobs', (4,), ['d', 'e']),
            ('add_dependency', ('c', 'g'), False),
            ('add_dependency', ('d', 'g'), False),
            ('jobs_with_status', ('done',), ['a', 'b', 'f']),
            ('next_job', (), 'd'),
            ('jobs_with_status', ('blocked',), []),
            ('add_dependency', ('a', 'g'), False),
            ('add_dependency', ('e', 'g'), False),
            ('next_job', (), 'e'),
            ('add_dependency', ('f', 'a'), False),
            ('jobs_with_status', ('queued',), []),
            ('jobs_with_status', ('running',), ['c', 'd', 'e']),
            ('add_job', ('f', 0), False),
            ('peek_jobs', (5,), []),
            ('get_status', ('c',), 'running'),
            ('complete_job', ('f',), False),
            ('get_status', ('c',), 'running'),
            ('complete_job', ('c',), True),
            ('add_dependency', ('f', 'c'), False),
            ('add_job', ('e', 3), False),
            ('add_dependency', ('b', 'b'), False),
            ('next_job', (), None),
            ('add_job', ('c', 3), False),
            ('add_dependency', ('e', 'b'), False),
            ('peek_jobs', (1,), []),
            ('peek_jobs', (1,), []),
            ('next_job', (), None),
            ('jobs_with_status', ('canceled',), []),
            ('complete_job', ('d',), True),
            ('complete_job', ('c',), False),
            ('add_job', ('b', 1), False),
        ])


if __name__ == "__main__":
    unittest.main()
