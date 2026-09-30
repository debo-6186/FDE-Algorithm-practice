"""
Level 3 tests for Job Scheduler.

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


class TestLevel3(unittest.TestCase):
    def setUp(self):
        self.impl = JobSchedulerImpl()

    def test_level_3_case_01_example_from_spec(self):
        """The Level 3 example table."""
        run_steps(self, self.impl, [
            ('add_job', ('compile', 1), True),
            ('add_job', ('test', 9), True),
            ('add_job', ('deploy', 9), True),
            ('add_dependency', ('test', 'compile'), True),
            ('add_dependency', ('deploy', 'test'), True),
            ('add_dependency', ('compile', 'deploy'), False),
            ('add_dependency', ('test', 'test'), False),
            ('get_status', ('deploy',), 'blocked'),
            ('peek_jobs', (5,), ['compile']),
            ('next_job', (), 'compile'),
            ('next_job', (), None),
            ('complete_job', ('compile',), True),
            ('get_status', ('test',), 'queued'),
            ('next_job', (), 'test'),
            ('add_dependency', ('test', 'compile'), False),
            ('jobs_with_status', ('blocked',), ['deploy']),
        ])

    def test_level_3_case_02_dependency_on_done_job_is_not_blocking(self):
        run_steps(self, self.impl, [
            ('add_job', ('a', 1), True),
            ('next_job', (), 'a'),
            ('complete_job', ('a',), True),
            ('add_job', ('b', 1), True),
            ('add_dependency', ('b', 'a'), True),
            ('get_status', ('b',), 'queued'),
            ('next_job', (), 'b'),
        ])

    def test_level_3_case_03_duplicate_and_unknown(self):
        run_steps(self, self.impl, [
            ('add_job', ('a', 1), True),
            ('add_job', ('b', 1), True),
            ('add_dependency', ('b', 'a'), True),
            ('add_dependency', ('b', 'a'), False),
            ('add_dependency', ('b', 'zzz'), False),
            ('add_dependency', ('zzz', 'a'), False),
        ])

    def test_level_3_case_04_indirect_cycle_rejected(self):
        run_steps(self, self.impl, [
            ('add_job', ('a', 1), True),
            ('add_job', ('b', 1), True),
            ('add_job', ('c', 1), True),
            ('add_job', ('d', 1), True),
            ('add_dependency', ('b', 'a'), True),
            ('add_dependency', ('c', 'b'), True),
            ('add_dependency', ('d', 'c'), True),
            ('add_dependency', ('a', 'd'), False),
            ('add_dependency', ('a', 'c'), False),
            ('add_dependency', ('d', 'a'), True),
        ])

    def test_level_3_case_05_multiple_prerequisites(self):
        run_steps(self, self.impl, [
            ('add_job', ('x', 1), True),
            ('add_job', ('y', 1), True),
            ('add_job', ('z', 10), True),
            ('add_dependency', ('z', 'x'), True),
            ('add_dependency', ('z', 'y'), True),
            ('next_job', (), 'x'),
            ('complete_job', ('x',), True),
            ('get_status', ('z',), 'blocked'),
            ('next_job', (), 'y'),
            ('peek_jobs', (5,), []),
            ('complete_job', ('y',), True),
            ('peek_jobs', (5,), ['z']),
        ])

    def test_level_3_case_06_running_job_can_be_a_prerequisite(self):
        run_steps(self, self.impl, [
            ('add_job', ('a', 1), True),
            ('next_job', (), 'a'),
            ('add_job', ('b', 1), True),
            ('add_dependency', ('b', 'a'), True),
            ('get_status', ('b',), 'blocked'),
            ('add_dependency', ('a', 'b'), False),
        ])

    def test_level_3_case_07_randomized_sequence_49(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('add_job', ('a', 2), True),
            ('add_job', ('d', 0), True),
            ('add_job', ('c', 0), True),
            ('jobs_with_status', ('done',), []),
            ('next_job', (), 'a'),
            ('add_job', ('e', 1), True),
            ('add_dependency', ('e', 'c'), True),
            ('peek_jobs', (0,), []),
            ('next_job', (), 'd'),
            ('add_job', ('f', 3), True),
            ('complete_job', ('c',), False),
            ('next_job', (), 'f'),
            ('add_dependency', ('e', 'e'), False),
            ('add_job', ('d', 1), False),
            ('peek_jobs', (4,), ['c']),
            ('next_job', (), 'c'),
            ('get_status', ('b',), None),
            ('get_status', ('b',), None),
            ('complete_job', ('e',), False),
            ('complete_job', ('e',), False),
            ('get_status', ('f',), 'running'),
            ('get_status', ('d',), 'running'),
            ('next_job', (), None),
            ('jobs_with_status', ('canceled',), []),
            ('add_dependency', ('a', 'b'), False),
            ('add_dependency', ('g', 'g'), False),
            ('complete_job', ('a',), True),
            ('jobs_with_status', ('queued',), []),
            ('complete_job', ('c',), True),
            ('add_dependency', ('d', 'b'), False),
            ('add_dependency', ('c', 'f'), False),
            ('get_status', ('c',), 'done'),
            ('complete_job', ('a',), False),
            ('add_job', ('d', 3), False),
            ('add_dependency', ('f', 'a'), False),
            ('add_dependency', ('e', 'a'), True),
            ('peek_jobs', (1,), ['e']),
            ('complete_job', ('e',), False),
            ('peek_jobs', (5,), ['e']),
            ('next_job', (), 'e'),
            ('add_dependency', ('e', 'g'), False),
            ('jobs_with_status', ('canceled',), []),
            ('next_job', (), None),
            ('add_dependency', ('a', 'c'), False),
            ('add_dependency', ('c', 'f'), False),
            ('jobs_with_status', ('running',), ['d', 'e', 'f']),
            ('get_status', ('a',), 'done'),
            ('add_dependency', ('d', 'g'), False),
            ('peek_jobs', (5,), []),
            ('complete_job', ('a',), False),
            ('next_job', (), None),
            ('complete_job', ('e',), True),
            ('complete_job', ('d',), True),
            ('add_dependency', ('f', 'f'), False),
            ('get_status', ('g',), None),
            ('get_status', ('b',), None),
            ('add_job', ('a', 2), False),
            ('add_job', ('d', 2), False),
            ('add_dependency', ('g', 'e'), False),
            ('add_job', ('d', 2), False),
            ('add_dependency', ('d', 'b'), False),
            ('add_dependency', ('a', 'd'), False),
            ('peek_jobs', (2,), []),
            ('complete_job', ('c',), False),
            ('add_dependency', ('b', 'g'), False),
            ('next_job', (), None),
            ('peek_jobs', (2,), []),
            ('add_dependency', ('a', 'a'), False),
            ('complete_job', ('f',), True),
            ('add_job', ('a', 3), False),
        ])

    def test_level_3_case_08_randomized_sequence_50(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('add_job', ('d', 2), True),
            ('add_job', ('c', 1), True),
            ('add_job', ('f', 3), True),
            ('add_dependency', ('c', 'a'), False),
            ('get_status', ('b',), None),
            ('jobs_with_status', ('running',), []),
            ('complete_job', ('a',), False),
            ('add_dependency', ('c', 'b'), False),
            ('next_job', (), 'f'),
            ('complete_job', ('e',), False),
            ('add_dependency', ('d', 'f'), True),
            ('add_job', ('a', 2), True),
            ('add_dependency', ('f', 'g'), False),
            ('complete_job', ('b',), False),
            ('complete_job', ('g',), False),
            ('add_dependency', ('f', 'a'), False),
            ('next_job', (), 'a'),
            ('next_job', (), 'c'),
            ('peek_jobs', (2,), []),
            ('peek_jobs', (4,), []),
            ('add_job', ('f', 0), False),
            ('add_dependency', ('f', 'g'), False),
            ('add_dependency', ('d', 'd'), False),
            ('add_dependency', ('g', 'e'), False),
            ('add_dependency', ('b', 'd'), False),
            ('peek_jobs', (2,), []),
            ('add_job', ('c', 1), False),
            ('add_job', ('a', 3), False),
            ('get_status', ('g',), None),
            ('add_dependency', ('g', 'e'), False),
            ('add_dependency', ('b', 'b'), False),
            ('jobs_with_status', ('running',), ['a', 'c', 'f']),
            ('next_job', (), None),
            ('next_job', (), None),
            ('peek_jobs', (0,), []),
            ('peek_jobs', (2,), []),
            ('get_status', ('d',), 'blocked'),
            ('peek_jobs', (3,), []),
            ('get_status', ('d',), 'blocked'),
            ('add_job', ('a', 0), False),
            ('add_job', ('f', 0), False),
            ('complete_job', ('g',), False),
            ('complete_job', ('f',), True),
            ('jobs_with_status', ('queued',), ['d']),
            ('complete_job', ('d',), False),
            ('next_job', (), 'd'),
            ('jobs_with_status', ('running',), ['a', 'c', 'd']),
            ('add_job', ('b', 0), True),
            ('complete_job', ('f',), False),
            ('add_dependency', ('c', 'a'), False),
            ('next_job', (), 'b'),
            ('next_job', (), None),
            ('add_dependency', ('f', 'e'), False),
            ('add_job', ('d', 3), False),
            ('complete_job', ('e',), False),
            ('next_job', (), None),
            ('add_job', ('e', 2), True),
            ('add_dependency', ('c', 'd'), False),
            ('complete_job', ('b',), True),
            ('get_status', ('g',), None),
            ('add_dependency', ('c', 'b'), False),
            ('add_dependency', ('c', 'g'), False),
            ('complete_job', ('g',), False),
            ('next_job', (), 'e'),
            ('get_status', ('a',), 'running'),
            ('peek_jobs', (0,), []),
            ('complete_job', ('d',), True),
            ('add_dependency', ('c', 'c'), False),
            ('add_dependency', ('e', 'b'), False),
            ('add_dependency', ('c', 'g'), False),
        ])


if __name__ == "__main__":
    unittest.main()
