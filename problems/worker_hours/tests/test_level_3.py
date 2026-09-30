"""
Level 3 tests for Worker Hours & Payroll.

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


class TestLevel3(unittest.TestCase):
    def setUp(self):
        self.impl = WorkerRegistryImpl()

    def test_level_3_case_01_example_from_spec(self):
        """The Level 3 example table."""
        run_steps(self, self.impl, [
            ('add_worker', ('John', 'Middle Developer', 200), True),
            ('register', ('John', 100), 'registered'),
            ('register', ('John', 125), 'registered'),
            ('promote', ('John', 'Senior Developer', 500, 200), 'success'),
            ('register', ('John', 150), 'registered'),
            ('promote', ('John', 'Senior Developer', 350, 250), 'invalid_request'),
            ('register', ('John', 300), 'registered'),
            ('register', ('John', 325), 'registered'),
            ('calc_salary', ('John', 0, 500), 35000),
            ('top_n_workers', (3, 'Senior Developer'), ['John(0)']),
            ('top_n_workers', (3, 'Middle Developer'), []),
            ('register', ('John', 400), 'registered'),
            ('get', ('John',), 250),
            ('top_n_workers', (10, 'Senior Developer'), ['John(75)']),
            ('calc_salary', ('John', 110, 350), 45500),
            ('calc_salary', ('John', 900, 1400), 0),
            ('promote', ('John', 'Lead', 900, 500), 'success'),
            ('calc_salary', ('Nobody', 0, 10), None),
        ])

    def test_level_3_case_02_promote_unknown_worker(self):
        run_steps(self, self.impl, [
            ('promote', ('ghost', 'P', 1, 10), 'invalid_request'),
        ])

    def test_level_3_case_03_promotion_applies_on_entry_not_on_exit(self):
        """Worker is inside when start_timestamp passes; the new rate starts at the NEXT entry."""
        run_steps(self, self.impl, [
            ('add_worker', ('w', 'Old', 10), True),
            ('register', ('w', 5), 'registered'),
            ('promote', ('w', 'New', 20, 6), 'success'),
            ('register', ('w', 10), 'registered'),
            ('top_n_workers', (5, 'Old'), ['w(5)']),
            ('register', ('w', 12), 'registered'),
            ('register', ('w', 15), 'registered'),
            ('calc_salary', ('w', 0, 100), 110),
            ('top_n_workers', (5, 'New'), ['w(3)']),
            ('top_n_workers', (5, 'Old'), []),
        ])

    def test_level_3_case_04_salary_window_clips_sessions(self):
        run_steps(self, self.impl, [
            ('add_worker', ('w', 'P', 7), True),
            ('register', ('w', 10), 'registered'),
            ('register', ('w', 20), 'registered'),
            ('calc_salary', ('w', 12, 15), 21),
            ('calc_salary', ('w', 0, 10), 0),
            ('calc_salary', ('w', 20, 30), 0),
            ('calc_salary', ('w', 19, 21), 7),
            ('calc_salary', ('w', 0, 100), 70),
        ])

    def test_level_3_case_05_salary_ignores_unfinished_session(self):
        run_steps(self, self.impl, [
            ('add_worker', ('w', 'P', 3), True),
            ('register', ('w', 1), 'registered'),
            ('calc_salary', ('w', 0, 100), 0),
        ])

    def test_level_3_case_06_get_counts_all_positions_but_top_counts_current(self):
        run_steps(self, self.impl, [
            ('add_worker', ('a', 'Junior', 1), True),
            ('add_worker', ('b', 'Senior', 1), True),
            ('register', ('a', 1), 'registered'),
            ('register', ('a', 11), 'registered'),
            ('promote', ('a', 'Senior', 2, 12), 'success'),
            ('register', ('b', 20), 'registered'),
            ('register', ('b', 23), 'registered'),
            ('register', ('a', 30), 'registered'),
            ('register', ('a', 32), 'registered'),
            ('get', ('a',), 12),
            ('top_n_workers', (5, 'Senior'), ['b(3)', 'a(2)']),
            ('calc_salary', ('a', 0, 100), 14),
        ])

    def test_level_3_case_07_second_promotion_after_first_is_active(self):
        run_steps(self, self.impl, [
            ('add_worker', ('w', 'A', 1), True),
            ('promote', ('w', 'B', 2, 5), 'success'),
            ('register', ('w', 5), 'registered'),
            ('register', ('w', 6), 'registered'),
            ('promote', ('w', 'A', 3, 10), 'success'),
            ('register', ('w', 20), 'registered'),
            ('register', ('w', 25), 'registered'),
            ('top_n_workers', (5, 'A'), ['w(5)']),
            ('calc_salary', ('w', 0, 30), 17),
            ('get', ('w',), 6),
        ])

    def test_level_3_case_08_randomized_sequence_43(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('add_worker', ('cal', 'Ops', 2), True),
            ('add_worker', ('cal', 'Ops', 1), False),
            ('add_worker', ('dee', 'Ops', 1), True),
            ('register', ('zed', 12), 'invalid_request'),
            ('get', ('zed',), None),
            ('calc_salary', ('dee', 25, 71), 0),
            ('add_worker', ('amy', 'QA', 2), True),
            ('add_worker', ('dee', 'Dev', 10), False),
            ('get', ('zed',), None),
            ('register', ('bob', 25), 'invalid_request'),
            ('add_worker', ('amy', 'Dev', 1), False),
            ('promote', ('cal', 'QA', 3, 59), 'success'),
            ('get', ('zed',), None),
            ('top_n_workers', (0, 'Ops'), []),
            ('register', ('cal', 36), 'registered'),
            ('get', ('dee',), 0),
            ('register', ('amy', 47), 'registered'),
            ('add_worker', ('cal', 'QA', 2), False),
            ('top_n_workers', (4, 'Ops'), ['cal(0)', 'dee(0)']),
            ('register', ('dee', 59), 'registered'),
            ('top_n_workers', (3, 'QA'), ['amy(0)']),
            ('get', ('amy',), 0),
            ('register', ('amy', 64), 'registered'),
            ('get', ('cal',), 0),
            ('register', ('zed', 78), 'invalid_request'),
            ('register', ('amy', 83), 'registered'),
            ('add_worker', ('bob', 'Ops', 1), True),
            ('calc_salary', ('cal', 15, 199), 0),
            ('get', ('cal',), 0),
            ('calc_salary', ('dee', 43, 142), 0),
            ('add_worker', ('amy', 'Ops', 2), False),
            ('calc_salary', ('dee', 24, 200), 0),
            ('calc_salary', ('dee', 33, 186), 0),
            ('get', ('cal',), 0),
            ('register', ('amy', 89), 'registered'),
            ('get', ('bob',), 0),
            ('top_n_workers', (5, 'Dev'), []),
            ('calc_salary', ('bob', 44, 93), 0),
            ('promote', ('dee', 'QA', 3, 93), 'success'),
            ('register', ('amy', 93), 'registered'),
            ('add_worker', ('amy', 'Ops', 5), False),
            ('register', ('bob', 108), 'registered'),
            ('promote', ('bob', 'Dev', 3, 115), 'success'),
            ('top_n_workers', (4, 'Ops'), ['bob(0)', 'cal(0)', 'dee(0)']),
            ('register', ('dee', 122), 'registered'),
            ('register', ('bob', 135), 'registered'),
            ('register', ('cal', 144), 'registered'),
            ('get', ('zed',), None),
            ('get', ('bob',), 27),
            ('register', ('amy', 147), 'registered'),
            ('register', ('cal', 150), 'registered'),
            ('register', ('cal', 155), 'registered'),
            ('register', ('amy', 162), 'registered'),
            ('register', ('bob', 172), 'registered'),
            ('get', ('dee',), 63),
            ('register', ('dee', 187), 'registered'),
            ('register', ('zed', 203), 'invalid_request'),
            ('calc_salary', ('zed', 109, 295), None),
            ('register', ('zed', 206), 'invalid_request'),
            ('register', ('bob', 226), 'registered'),
            ('promote', ('amy', 'Ops', 20, 232), 'success'),
            ('calc_salary', ('bob', 48, 99), 0),
            ('get', ('zed',), None),
            ('add_worker', ('dee', 'QA', 10), False),
            ('register', ('cal', 241), 'registered'),
            ('register', ('cal', 257), 'registered'),
            ('register', ('cal', 269), 'registered'),
            ('register', ('amy', 282), 'registered'),
            ('top_n_workers', (2, 'QA'), ['amy(197)', 'cal(21)']),
            ('promote', ('bob', 'Dev', 7, 294), 'success'),
        ])

    def test_level_3_case_09_randomized_sequence_44(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('add_worker', ('amy', 'Dev', 10), True),
            ('add_worker', ('cal', 'Dev', 2), True),
            ('add_worker', ('amy', 'Dev', 2), False),
            ('promote', ('cal', 'Ops', 20, 25), 'success'),
            ('get', ('cal',), 0),
            ('register', ('cal', 10), 'registered'),
            ('get', ('amy',), 0),
            ('register', ('zed', 14), 'invalid_request'),
            ('register', ('cal', 18), 'registered'),
            ('calc_salary', ('cal', 2, 91), 16),
            ('register', ('dee', 34), 'invalid_request'),
            ('calc_salary', ('bob', 8, 75), None),
            ('promote', ('amy', 'Dev', 20, 62), 'success'),
            ('top_n_workers', (2, 'QA'), []),
            ('get', ('zed',), None),
            ('promote', ('bob', 'Dev', 7, 64), 'invalid_request'),
            ('calc_salary', ('cal', 39, 228), 0),
            ('add_worker', ('amy', 'Dev', 1), False),
            ('get', ('zed',), None),
            ('top_n_workers', (2, 'QA'), []),
            ('get', ('dee',), None),
            ('register', ('cal', 38), 'registered'),
            ('promote', ('zed', 'Ops', 3, 66), 'invalid_request'),
            ('promote', ('zed', 'QA', 3, 48), 'invalid_request'),
            ('register', ('amy', 58), 'registered'),
            ('top_n_workers', (2, 'Dev'), ['amy(0)']),
            ('add_worker', ('bob', 'Ops', 2), True),
            ('calc_salary', ('amy', 35, 159), 0),
            ('calc_salary', ('cal', 8, 140), 16),
            ('promote', ('zed', 'QA', 20, 90), 'invalid_request'),
            ('add_worker', ('cal', 'QA', 10), False),
            ('register', ('dee', 61), 'invalid_request'),
            ('register', ('bob', 66), 'registered'),
            ('top_n_workers', (3, 'QA'), []),
            ('top_n_workers', (0, 'QA'), []),
            ('calc_salary', ('bob', 35, 226), 0),
            ('get', ('cal',), 8),
            ('register', ('bob', 84), 'registered'),
            ('register', ('zed', 93), 'invalid_request'),
            ('calc_salary', ('bob', 57, 122), 36),
            ('register', ('zed', 105), 'invalid_request'),
            ('get', ('cal',), 8),
            ('calc_salary', ('dee', 18, 20), None),
            ('add_worker', ('dee', 'QA', 10), True),
            ('register', ('bob', 110), 'registered'),
            ('top_n_workers', (2, 'QA'), ['dee(0)']),
            ('add_worker', ('bob', 'Dev', 2), False),
            ('get', ('amy',), 0),
            ('register', ('dee', 128), 'registered'),
            ('register', ('cal', 141), 'registered'),
            ('register', ('bob', 161), 'registered'),
            ('top_n_workers', (4, 'Ops'), ['cal(103)', 'bob(69)']),
            ('calc_salary', ('zed', 73, 78), None),
            ('add_worker', ('amy', 'Dev', 1), False),
            ('register', ('bob', 179), 'registered'),
            ('register', ('bob', 193), 'registered'),
            ('top_n_workers', (3, 'QA'), ['dee(0)']),
            ('register', ('cal', 198), 'registered'),
            ('register', ('dee', 204), 'registered'),
            ('top_n_workers', (3, 'Dev'), ['amy(0)']),
            ('register', ('dee', 220), 'registered'),
            ('register', ('cal', 239), 'registered'),
            ('calc_salary', ('dee', 193, 317), 110),
            ('register', ('cal', 258), 'registered'),
            ('register', ('bob', 274), 'registered'),
            ('calc_salary', ('bob', 176, 187), 16),
            ('register', ('dee', 288), 'registered'),
            ('register', ('cal', 306), 'registered'),
            ('calc_salary', ('dee', 49, 51), 0),
            ('register', ('zed', 316), 'invalid_request'),
        ])


if __name__ == "__main__":
    unittest.main()
