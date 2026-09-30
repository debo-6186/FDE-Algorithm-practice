"""
Level 2 tests for Worker Hours & Payroll.

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


class TestLevel2(unittest.TestCase):
    def setUp(self):
        self.impl = WorkerRegistryImpl()

    def test_level_2_case_01_example_from_spec(self):
        """The Level 2 example table."""
        run_steps(self, self.impl, [
            ('add_worker', ('John', 'Junior Developer', 120), True),
            ('add_worker', ('Jason', 'Junior Developer', 120), True),
            ('add_worker', ('Ashley', 'Junior Developer', 120), True),
            ('add_worker', ('Maria', 'Senior Developer', 200), True),
            ('register', ('John', 100), 'registered'),
            ('register', ('John', 150), 'registered'),
            ('register', ('Jason', 200), 'registered'),
            ('register', ('Jason', 250), 'registered'),
            ('register', ('Jason', 275), 'registered'),
            ('top_n_workers', (5, 'Junior Developer'), ['Jason(50)', 'John(50)', 'Ashley(0)']),
            ('top_n_workers', (1, 'Junior Developer'), ['Jason(50)']),
            ('register', ('Ashley', 400), 'registered'),
            ('register', ('Ashley', 500), 'registered'),
            ('register', ('Jason', 575), 'registered'),
            ('top_n_workers', (3, 'Junior Developer'), ['Jason(350)', 'Ashley(100)', 'John(50)']),
            ('top_n_workers', (3, 'Senior Developer'), ['Maria(0)']),
            ('top_n_workers', (3, 'Intern'), []),
        ])

    def test_level_2_case_02_position_match_is_exact(self):
        run_steps(self, self.impl, [
            ('add_worker', ('a', 'Dev', 1), True),
            ('add_worker', ('b', 'dev', 1), True),
            ('add_worker', ('c', 'Dev ', 1), True),
            ('top_n_workers', (5, 'Dev'), ['a(0)']),
            ('top_n_workers', (5, 'dev'), ['b(0)']),
        ])

    def test_level_2_case_03_unfinished_session_does_not_count(self):
        run_steps(self, self.impl, [
            ('add_worker', ('a', 'P', 1), True),
            ('add_worker', ('b', 'P', 1), True),
            ('register', ('a', 1), 'registered'),
            ('register', ('b', 2), 'registered'),
            ('register', ('b', 4), 'registered'),
            ('top_n_workers', (2, 'P'), ['b(2)', 'a(0)']),
        ])

    def test_level_2_case_04_n_zero(self):
        run_steps(self, self.impl, [
            ('add_worker', ('a', 'P', 1), True),
            ('top_n_workers', (0, 'P'), []),
        ])

    def test_level_2_case_05_randomized_sequence_33(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('add_worker', ('bob', 'Ops', 2), True),
            ('add_worker', ('dee', 'Ops', 2), True),
            ('add_worker', ('cal', 'Ops', 10), True),
            ('register', ('amy', 10), 'invalid_request'),
            ('register', ('zed', 26), 'invalid_request'),
            ('top_n_workers', (5, 'Ops'), ['bob(0)', 'cal(0)', 'dee(0)']),
            ('register', ('cal', 37), 'registered'),
            ('register', ('bob', 41), 'registered'),
            ('top_n_workers', (2, 'Dev'), []),
            ('top_n_workers', (5, 'QA'), []),
            ('add_worker', ('bob', 'Ops', 5), False),
            ('register', ('cal', 58), 'registered'),
            ('register', ('zed', 71), 'invalid_request'),
            ('register', ('amy', 73), 'invalid_request'),
            ('register', ('zed', 77), 'invalid_request'),
            ('add_worker', ('amy', 'QA', 1), True),
            ('add_worker', ('cal', 'Dev', 2), False),
            ('register', ('dee', 92), 'registered'),
            ('register', ('cal', 111), 'registered'),
            ('register', ('cal', 127), 'registered'),
            ('add_worker', ('dee', 'QA', 5), False),
            ('add_worker', ('amy', 'Ops', 10), False),
            ('get', ('bob',), 0),
            ('top_n_workers', (3, 'Dev'), []),
            ('register', ('zed', 137), 'invalid_request'),
            ('register', ('dee', 154), 'registered'),
            ('register', ('dee', 174), 'registered'),
            ('top_n_workers', (3, 'Dev'), []),
            ('get', ('cal',), 37),
            ('get', ('cal',), 37),
            ('register', ('bob', 185), 'registered'),
            ('register', ('cal', 205), 'registered'),
            ('register', ('cal', 219), 'registered'),
            ('register', ('cal', 231), 'registered'),
            ('get', ('zed',), None),
            ('register', ('amy', 232), 'registered'),
            ('register', ('amy', 241), 'registered'),
            ('get', ('amy',), 9),
            ('register', ('bob', 248), 'registered'),
            ('register', ('zed', 251), 'invalid_request'),
            ('add_worker', ('dee', 'Ops', 5), False),
            ('add_worker', ('dee', 'Dev', 1), False),
            ('get', ('bob',), 144),
            ('register', ('amy', 270), 'registered'),
            ('get', ('zed',), None),
            ('register', ('amy', 281), 'registered'),
            ('register', ('dee', 291), 'registered'),
            ('top_n_workers', (0, 'QA'), []),
            ('top_n_workers', (2, 'QA'), ['amy(20)']),
            ('register', ('cal', 295), 'registered'),
        ])

    def test_level_2_case_06_randomized_sequence_34(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('add_worker', ('cal', 'Ops', 1), True),
            ('add_worker', ('amy', 'QA', 5), True),
            ('add_worker', ('dee', 'QA', 5), True),
            ('add_worker', ('bob', 'Dev', 5), True),
            ('register', ('amy', 5), 'registered'),
            ('get', ('amy',), 0),
            ('get', ('cal',), 0),
            ('register', ('zed', 7), 'invalid_request'),
            ('get', ('bob',), 0),
            ('register', ('cal', 17), 'registered'),
            ('register', ('bob', 24), 'registered'),
            ('register', ('bob', 44), 'registered'),
            ('add_worker', ('dee', 'Dev', 2), False),
            ('register', ('amy', 63), 'registered'),
            ('register', ('amy', 78), 'registered'),
            ('register', ('amy', 97), 'registered'),
            ('register', ('bob', 103), 'registered'),
            ('register', ('cal', 118), 'registered'),
            ('top_n_workers', (4, 'Ops'), ['cal(101)']),
            ('get', ('dee',), 0),
            ('register', ('dee', 130), 'registered'),
            ('add_worker', ('bob', 'Dev', 2), False),
            ('register', ('amy', 140), 'registered'),
            ('register', ('zed', 157), 'invalid_request'),
            ('register', ('bob', 171), 'registered'),
            ('top_n_workers', (4, 'Ops'), ['cal(101)']),
            ('get', ('zed',), None),
            ('get', ('dee',), 0),
            ('add_worker', ('cal', 'QA', 5), False),
            ('register', ('bob', 185), 'registered'),
            ('register', ('cal', 194), 'registered'),
            ('add_worker', ('cal', 'Ops', 1), False),
            ('register', ('amy', 211), 'registered'),
            ('register', ('amy', 229), 'registered'),
            ('register', ('bob', 238), 'registered'),
            ('register', ('bob', 253), 'registered'),
            ('top_n_workers', (5, 'QA'), ['amy(148)', 'dee(0)']),
            ('top_n_workers', (0, 'QA'), []),
            ('register', ('bob', 258), 'registered'),
            ('register', ('dee', 276), 'registered'),
            ('get', ('zed',), None),
            ('register', ('dee', 277), 'registered'),
            ('register', ('dee', 297), 'registered'),
            ('register', ('dee', 303), 'registered'),
            ('register', ('dee', 316), 'registered'),
            ('top_n_workers', (1, 'Ops'), ['cal(101)']),
            ('register', ('bob', 330), 'registered'),
            ('top_n_workers', (3, 'Ops'), ['cal(101)']),
            ('register', ('zed', 350), 'invalid_request'),
            ('get', ('bob',), 146),
        ])


if __name__ == "__main__":
    unittest.main()
