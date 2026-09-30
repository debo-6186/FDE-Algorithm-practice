"""
Level 4 tests for Worker Hours & Payroll.

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


class TestLevel4(unittest.TestCase):
    def setUp(self):
        self.impl = WorkerRegistryImpl()

    def test_level_4_case_01_example_from_spec(self):
        """The Level 4 example table."""
        run_steps(self, self.impl, [
            ('add_worker', ('Ann', 'Engineer', 100), True),
            ('set_double_paid', (5, 10), ANY),
            ('register', ('Ann', 1), 'registered'),
            ('register', ('Ann', 15), 'registered'),
            ('calc_salary', ('Ann', 0, 20), 1900),
            ('set_double_paid', (8, 12), ANY),
            ('calc_salary', ('Ann', 0, 20), 2100),
            ('calc_salary', ('Ann', 9, 11), 400),
            ('set_double_paid', (100, 200), ANY),
            ('register', ('Ann', 150), 'registered'),
            ('register', ('Ann', 250), 'registered'),
            ('calc_salary', ('Ann', 0, 1000), 17100),
        ])

    def test_level_4_case_02_nested_periods_do_not_stack(self):
        run_steps(self, self.impl, [
            ('add_worker', ('w', 'P', 10), True),
            ('register', ('w', 0), 'registered'),
            ('register', ('w', 10), 'registered'),
            ('set_double_paid', (0, 10), ANY),
            ('set_double_paid', (2, 4), ANY),
            ('set_double_paid', (0, 10), ANY),
            ('calc_salary', ('w', 0, 10), 200),
        ])

    def test_level_4_case_03_touching_periods(self):
        run_steps(self, self.impl, [
            ('add_worker', ('w', 'P', 1), True),
            ('set_double_paid', (0, 5), ANY),
            ('set_double_paid', (5, 10), ANY),
            ('register', ('w', 3), 'registered'),
            ('register', ('w', 12), 'registered'),
            ('calc_salary', ('w', 0, 20), 16),
        ])

    def test_level_4_case_04_double_period_outside_window_is_ignored(self):
        run_steps(self, self.impl, [
            ('add_worker', ('w', 'P', 5), True),
            ('register', ('w', 10), 'registered'),
            ('register', ('w', 20), 'registered'),
            ('set_double_paid', (0, 100), ANY),
            ('calc_salary', ('w', 12, 14), 20),
            ('calc_salary', ('w', 30, 40), 0),
        ])

    def test_level_4_case_05_double_pay_with_promotion(self):
        run_steps(self, self.impl, [
            ('add_worker', ('w', 'Jr', 10), True),
            ('register', ('w', 0), 'registered'),
            ('register', ('w', 10), 'registered'),
            ('promote', ('w', 'Sr', 30, 11), 'success'),
            ('register', ('w', 20), 'registered'),
            ('register', ('w', 30), 'registered'),
            ('set_double_paid', (5, 25), ANY),
            ('calc_salary', ('w', 0, 30), 600),
            ('calc_salary', ('w', 8, 22), 160),
        ])

    def test_level_4_case_06_randomized_sequence_59(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('add_worker', ('amy', 'Ops', 10), True),
            ('add_worker', ('bob', 'QA', 1), True),
            ('add_worker', ('amy', 'QA', 10), False),
            ('get', ('zed',), None),
            ('register', ('bob', 19), 'registered'),
            ('register', ('bob', 36), 'registered'),
            ('set_double_paid', (95, 101), ANY),
            ('calc_salary', ('cal', 5, 17), None),
            ('register', ('amy', 55), 'registered'),
            ('top_n_workers', (2, 'QA'), ['bob(17)']),
            ('add_worker', ('amy', 'QA', 2), False),
            ('top_n_workers', (0, 'QA'), []),
            ('register', ('zed', 63), 'invalid_request'),
            ('register', ('dee', 73), 'invalid_request'),
            ('top_n_workers', (0, 'Ops'), []),
            ('set_double_paid', (154, 212), ANY),
            ('get', ('cal',), None),
            ('register', ('zed', 78), 'invalid_request'),
            ('get', ('bob',), 17),
            ('register', ('dee', 86), 'invalid_request'),
            ('get', ('dee',), None),
            ('register', ('zed', 97), 'invalid_request'),
            ('get', ('amy',), 0),
            ('register', ('amy', 108), 'registered'),
            ('set_double_paid', (151, 202), ANY),
            ('promote', ('amy', 'Ops', 7, 113), 'success'),
            ('register', ('dee', 110), 'invalid_request'),
            ('calc_salary', ('dee', 39, 115), None),
            ('promote', ('zed', 'QA', 7, 117), 'invalid_request'),
            ('calc_salary', ('amy', 76, 200), 380),
            ('promote', ('amy', 'QA', 3, 125), 'invalid_request'),
            ('register', ('zed', 114), 'invalid_request'),
            ('calc_salary', ('cal', 104, 286), None),
            ('set_double_paid', (59, 75), ANY),
            ('set_double_paid', (56, 136), ANY),
            ('add_worker', ('dee', 'QA', 10), True),
            ('add_worker', ('bob', 'Dev', 2), False),
            ('add_worker', ('bob', 'QA', 2), False),
            ('register', ('amy', 117), 'registered'),
            ('top_n_workers', (5, 'Ops'), ['amy(0)']),
            ('top_n_workers', (2, 'Dev'), []),
            ('promote', ('bob', 'Dev', 20, 148), 'success'),
            ('top_n_workers', (4, 'Dev'), []),
            ('register', ('dee', 118), 'registered'),
            ('register', ('bob', 126), 'registered'),
            ('add_worker', ('bob', 'Ops', 2), False),
            ('register', ('zed', 143), 'invalid_request'),
            ('register', ('bob', 149), 'registered'),
            ('get', ('zed',), None),
            ('get', ('bob',), 40),
            ('calc_salary', ('amy', 67, 71), 80),
            ('promote', ('cal', 'Dev', 7, 186), 'invalid_request'),
            ('register', ('bob', 162), 'registered'),
            ('top_n_workers', (4, 'Dev'), ['bob(0)']),
            ('set_double_paid', (204, 235), ANY),
            ('register', ('dee', 168), 'registered'),
            ('add_worker', ('dee', 'Ops', 5), False),
            ('promote', ('amy', 'Ops', 7, 197), 'success'),
            ('register', ('cal', 172), 'invalid_request'),
            ('promote', ('bob', 'Ops', 7, 188), 'success'),
            ('calc_salary', ('dee', 169, 298), 0),
            ('register', ('amy', 183), 'registered'),
            ('register', ('bob', 186), 'registered'),
            ('get', ('dee',), 50),
            ('set_double_paid', (127, 193), ANY),
            ('get', ('zed',), None),
            ('get', ('dee',), 50),
            ('register', ('amy', 200), 'registered'),
            ('calc_salary', ('dee', 86, 219), 1000),
            ('add_worker', ('dee', 'Ops', 2), False),
            ('register', ('dee', 207), 'registered'),
            ('top_n_workers', (0, 'Dev'), []),
            ('add_worker', ('amy', 'Dev', 10), False),
            ('register', ('zed', 226), 'invalid_request'),
            ('set_double_paid', (275, 280), ANY),
            ('calc_salary', ('bob', 95, 136), 20),
            ('top_n_workers', (5, 'QA'), ['dee(50)']),
            ('set_double_paid', (258, 304), ANY),
            ('register', ('cal', 236), 'invalid_request'),
            ('set_double_paid', (222, 282), ANY),
            ('top_n_workers', (0, 'Ops'), []),
            ('set_double_paid', (202, 236), ANY),
            ('set_double_paid', (10, 32), ANY),
            ('get', ('bob',), 64),
            ('register', ('bob', 244), 'registered'),
            ('register', ('dee', 245), 'registered'),
            ('set_double_paid', (272, 305), ANY),
            ('calc_salary', ('bob', 206, 285), 0),
            ('calc_salary', ('dee', 253, 394), 0),
            ('calc_salary', ('zed', 58, 110), None),
        ])

    def test_level_4_case_07_randomized_sequence_60(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('add_worker', ('cal', 'Ops', 2), True),
            ('add_worker', ('bob', 'QA', 10), True),
            ('add_worker', ('amy', 'Dev', 2), True),
            ('register', ('amy', 8), 'registered'),
            ('top_n_workers', (3, 'Ops'), ['cal(0)']),
            ('register', ('cal', 28), 'registered'),
            ('top_n_workers', (4, 'Ops'), ['cal(0)']),
            ('get', ('zed',), None),
            ('add_worker', ('amy', 'QA', 2), False),
            ('add_worker', ('bob', 'QA', 2), False),
            ('get', ('amy',), 0),
            ('set_double_paid', (65, 92), ANY),
            ('promote', ('bob', 'Ops', 20, 36), 'success'),
            ('get', ('dee',), None),
            ('register', ('amy', 45), 'registered'),
            ('top_n_workers', (0, 'Ops'), []),
            ('promote', ('amy', 'Dev', 7, 66), 'success'),
            ('get', ('dee',), None),
            ('set_double_paid', (139, 161), ANY),
            ('register', ('cal', 60), 'registered'),
            ('set_double_paid', (151, 201), ANY),
            ('add_worker', ('bob', 'Dev', 2), False),
            ('register', ('amy', 78), 'registered'),
            ('register', ('zed', 94), 'invalid_request'),
            ('set_double_paid', (27, 32), ANY),
            ('top_n_workers', (0, 'Dev'), []),
            ('register', ('dee', 110), 'invalid_request'),
            ('register', ('bob', 129), 'registered'),
            ('set_double_paid', (85, 117), ANY),
            ('add_worker', ('dee', 'QA', 1), True),
            ('calc_salary', ('cal', 87, 147), 0),
            ('promote', ('zed', 'Ops', 20, 140), 'invalid_request'),
            ('set_double_paid', (68, 76), ANY),
            ('register', ('dee', 145), 'registered'),
            ('set_double_paid', (81, 106), ANY),
            ('get', ('amy',), 37),
            ('promote', ('bob', 'Dev', 3, 180), 'success'),
            ('register', ('amy', 153), 'registered'),
            ('get', ('zed',), None),
            ('register', ('bob', 172), 'registered'),
            ('calc_salary', ('dee', 143, 246), 0),
            ('get', ('cal',), 32),
            ('add_worker', ('cal', 'QA', 10), False),
            ('register', ('dee', 178), 'registered'),
            ('top_n_workers', (0, 'QA'), []),
            ('top_n_workers', (1, 'Ops'), ['bob(43)']),
            ('register', ('zed', 182), 'invalid_request'),
            ('add_worker', ('bob', 'Ops', 2), False),
            ('get', ('bob',), 43),
            ('calc_salary', ('zed', 86, 111), None),
            ('add_worker', ('bob', 'Dev', 2), False),
            ('set_double_paid', (131, 146), ANY),
            ('top_n_workers', (1, 'Ops'), ['bob(43)']),
            ('promote', ('amy', 'Ops', 20, 210), 'success'),
            ('calc_salary', ('bob', 0, 200), 1680),
            ('register', ('amy', 201), 'registered'),
            ('add_worker', ('dee', 'Dev', 2), False),
            ('get', ('zed',), None),
            ('register', ('zed', 218), 'invalid_request'),
            ('register', ('cal', 236), 'registered'),
            ('add_worker', ('bob', 'QA', 2), False),
            ('calc_salary', ('bob', 215, 336), 0),
            ('add_worker', ('bob', 'QA', 2), False),
            ('register', ('dee', 237), 'registered'),
            ('register', ('cal', 243), 'registered'),
            ('register', ('zed', 261), 'invalid_request'),
            ('register', ('zed', 277), 'invalid_request'),
            ('register', ('cal', 289), 'registered'),
            ('register', ('zed', 291), 'invalid_request'),
            ('register', ('dee', 304), 'registered'),
            ('calc_salary', ('dee', 160, 170), 20),
            ('top_n_workers', (0, 'Ops'), []),
            ('get', ('dee',), 100),
            ('set_double_paid', (114, 164), ANY),
            ('promote', ('bob', 'Ops', 3, 340), 'invalid_request'),
            ('register', ('cal', 306), 'registered'),
            ('add_worker', ('cal', 'Ops', 2), False),
            ('top_n_workers', (5, 'Ops'), ['cal(56)', 'bob(43)']),
            ('top_n_workers', (5, 'Dev'), ['amy(75)']),
            ('register', ('dee', 310), 'registered'),
            ('register', ('dee', 317), 'registered'),
            ('register', ('cal', 337), 'registered'),
            ('register', ('zed', 341), 'invalid_request'),
            ('add_worker', ('cal', 'Ops', 1), False),
            ('top_n_workers', (5, 'Ops'), ['cal(56)', 'bob(43)']),
            ('get', ('cal',), 56),
            ('add_worker', ('dee', 'QA', 10), False),
            ('calc_salary', ('cal', 3, 72), 72),
            ('add_worker', ('cal', 'Ops', 5), False),
            ('add_worker', ('bob', 'Ops', 1), False),
        ])

    def test_level_4_case_08_randomized_sequence_61(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('add_worker', ('bob', 'Ops', 2), True),
            ('add_worker', ('cal', 'QA', 1), True),
            ('add_worker', ('cal', 'QA', 1), False),
            ('register', ('cal', 6), 'registered'),
            ('register', ('amy', 23), 'invalid_request'),
            ('promote', ('bob', 'QA', 3, 51), 'success'),
            ('calc_salary', ('bob', 25, 101), 0),
            ('set_double_paid', (56, 97), ANY),
            ('top_n_workers', (5, 'Ops'), ['bob(0)']),
            ('register', ('dee', 31), 'invalid_request'),
            ('register', ('amy', 49), 'invalid_request'),
            ('register', ('amy', 67), 'invalid_request'),
            ('register', ('cal', 68), 'registered'),
            ('register', ('amy', 83), 'invalid_request'),
            ('register', ('amy', 96), 'invalid_request'),
            ('register', ('zed', 108), 'invalid_request'),
            ('top_n_workers', (3, 'QA'), ['cal(62)']),
            ('register', ('dee', 115), 'invalid_request'),
            ('register', ('dee', 131), 'invalid_request'),
            ('register', ('cal', 147), 'registered'),
            ('top_n_workers', (0, 'QA'), []),
            ('promote', ('cal', 'Dev', 20, 177), 'success'),
            ('set_double_paid', (223, 237), ANY),
            ('promote', ('bob', 'Dev', 20, 149), 'invalid_request'),
            ('promote', ('bob', 'Ops', 3, 164), 'invalid_request'),
            ('calc_salary', ('zed', 116, 221), None),
            ('register', ('amy', 156), 'invalid_request'),
            ('calc_salary', ('bob', 27, 71), 0),
            ('register', ('bob', 167), 'registered'),
            ('calc_salary', ('bob', 151, 222), 0),
            ('add_worker', ('bob', 'Dev', 5), False),
            ('register', ('bob', 183), 'registered'),
            ('calc_salary', ('dee', 71, 183), None),
            ('register', ('dee', 202), 'invalid_request'),
            ('register', ('zed', 205), 'invalid_request'),
            ('promote', ('bob', 'Ops', 20, 227), 'success'),
            ('promote', ('dee', 'Dev', 20, 214), 'invalid_request'),
            ('promote', ('zed', 'Ops', 3, 209), 'invalid_request'),
            ('get', ('dee',), None),
            ('calc_salary', ('cal', 199, 372), 0),
            ('get', ('dee',), None),
            ('promote', ('bob', 'Ops', 7, 240), 'invalid_request'),
            ('top_n_workers', (5, 'QA'), ['cal(62)', 'bob(16)']),
            ('register', ('zed', 211), 'invalid_request'),
            ('register', ('zed', 225), 'invalid_request'),
            ('calc_salary', ('bob', 130, 330), 48),
            ('register', ('cal', 240), 'registered'),
            ('register', ('zed', 252), 'invalid_request'),
            ('register', ('dee', 269), 'invalid_request'),
            ('get', ('bob',), 16),
            ('register', ('dee', 274), 'invalid_request'),
            ('register', ('zed', 277), 'invalid_request'),
            ('register', ('bob', 294), 'registered'),
            ('add_worker', ('amy', 'Ops', 5), True),
            ('register', ('cal', 300), 'registered'),
            ('add_worker', ('cal', 'Dev', 10), False),
            ('calc_salary', ('dee', 1, 130), None),
            ('register', ('cal', 309), 'registered'),
            ('top_n_workers', (4, 'Ops'), ['amy(0)', 'bob(0)']),
            ('get', ('bob',), 16),
            ('register', ('bob', 311), 'registered'),
            ('top_n_workers', (2, 'Dev'), ['cal(9)']),
            ('register', ('cal', 331), 'registered'),
            ('top_n_workers', (1, 'Ops'), ['bob(17)']),
            ('set_double_paid', (321, 384), ANY),
            ('add_worker', ('dee', 'QA', 5), True),
            ('register', ('bob', 344), 'registered'),
            ('set_double_paid', (14, 24), ANY),
            ('calc_salary', ('bob', 111, 274), 48),
            ('add_worker', ('amy', 'Dev', 2), False),
            ('top_n_workers', (0, 'Ops'), []),
            ('calc_salary', ('bob', 10, 17), 0),
            ('get', ('bob',), 33),
            ('calc_salary', ('bob', 355, 509), 0),
            ('get', ('zed',), None),
            ('add_worker', ('bob', 'Dev', 2), False),
            ('register', ('amy', 352), 'registered'),
            ('calc_salary', ('amy', 5, 140), 0),
            ('top_n_workers', (4, 'Ops'), ['bob(17)', 'amy(0)']),
            ('register', ('amy', 355), 'registered'),
            ('add_worker', ('bob', 'QA', 2), False),
            ('register', ('dee', 364), 'registered'),
            ('set_double_paid', (286, 315), ANY),
            ('promote', ('bob', 'QA', 7, 379), 'success'),
            ('register', ('amy', 369), 'registered'),
            ('calc_salary', ('bob', 318, 481), 0),
            ('register', ('bob', 378), 'registered'),
            ('top_n_workers', (3, 'Dev'), ['cal(9)']),
            ('calc_salary', ('cal', 62, 187), 52),
            ('register', ('cal', 384), 'registered'),
        ])


if __name__ == "__main__":
    unittest.main()
