"""
Level 3 tests for In-Memory Database.

Each test replays a sequence of calls on a fresh InMemoryDBImpl() and checks
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

from in_memory_db_impl import InMemoryDBImpl

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
        self.impl = InMemoryDBImpl()

    def test_level_3_case_01_example_from_spec(self):
        """The Level 3 example table."""
        run_steps(self, self.impl, [
            ('set_at_with_ttl', ('A', 'BC', 'E', 1, 9), ANY),
            ('set_at_with_ttl', ('A', 'BC', 'E', 5, 10), ANY),
            ('set_at', ('A', 'BD', 'F', 6), ANY),
            ('scan_by_prefix_at', ('A', 'B', 14), ['BC(E)', 'BD(F)']),
            ('scan_by_prefix_at', ('A', 'B', 15), ['BD(F)']),
            ('get_at', ('A', 'BC', 16), None),
            ('delete_at', ('A', 'BC', 17), False),
            ('set_at_with_ttl', ('X', 'Y', 'Z', 18, 2), ANY),
            ('get_at', ('X', 'Y', 19), 'Z'),
            ('scan_at', ('X', 20), []),
            ('delete_at', ('A', 'BD', 21), True),
            ('scan_at', ('A', 22), []),
        ])

    def test_level_3_case_02_ttl_boundary(self):
        run_steps(self, self.impl, [
            ('set_at_with_ttl', ('k', 'f', 'v', 10, 5), ANY),
            ('get_at', ('k', 'f', 14), 'v'),
            ('get_at', ('k', 'f', 15), None),
        ])

    def test_level_3_case_03_set_at_makes_field_permanent_again(self):
        run_steps(self, self.impl, [
            ('set_at_with_ttl', ('k', 'f', 'v1', 1, 3), ANY),
            ('set_at', ('k', 'f', 'v2', 2), ANY),
            ('get_at', ('k', 'f', 1000), 'v2'),
        ])

    def test_level_3_case_04_expired_field_can_be_set_again(self):
        run_steps(self, self.impl, [
            ('set_at_with_ttl', ('k', 'f', 'old', 1, 1), ANY),
            ('get_at', ('k', 'f', 2), None),
            ('set_at_with_ttl', ('k', 'f', 'new', 3, 4), ANY),
            ('get_at', ('k', 'f', 6), 'new'),
            ('delete_at', ('k', 'f', 7), False),
        ])

    def test_level_3_case_05_delete_before_expiry(self):
        run_steps(self, self.impl, [
            ('set_at_with_ttl', ('k', 'f', 'v', 1, 100), ANY),
            ('delete_at', ('k', 'f', 50), True),
            ('get_at', ('k', 'f', 51), None),
            ('scan_at', ('k', 52), []),
        ])

    def test_level_3_case_06_scan_mixes_live_and_expired(self):
        run_steps(self, self.impl, [
            ('set_at', ('k', 'c', '3', 1), ANY),
            ('set_at_with_ttl', ('k', 'a', '1', 2, 5), ANY),
            ('set_at_with_ttl', ('k', 'b', '2', 3, 10), ANY),
            ('scan_at', ('k', 6), ['a(1)', 'b(2)', 'c(3)']),
            ('scan_at', ('k', 7), ['b(2)', 'c(3)']),
            ('scan_by_prefix_at', ('k', 'b', 13), []),
            ('scan_at', ('k', 13), ['c(3)']),
        ])

    def test_level_3_case_07_randomized_sequence_41(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('set_at_with_ttl', ('A', 'B', '73', 4, 12), ANY),
            ('get_at', ('B', 'c', 7), None),
            ('scan_at', ('C', 8), []),
            ('scan_by_prefix_at', ('A', 'b', 12), []),
            ('set_at_with_ttl', ('C', 'ba', '74', 14, 1), ANY),
            ('scan_at', ('A', 15), ['B(73)']),
            ('scan_at', ('A', 18), []),
            ('delete_at', ('A', 'ba', 21), False),
            ('set_at', ('A', 'c', '22', 22), ANY),
            ('set_at_with_ttl', ('A', 'ba', '3', 23, 10), ANY),
            ('set_at_with_ttl', ('A', 'b', '51', 25, 3), ANY),
            ('delete_at', ('B', 'a', 26), False),
            ('scan_at', ('A', 30), ['ba(3)', 'c(22)']),
            ('set_at', ('B', 'c', '51', 31), ANY),
            ('get_at', ('B', 'ba', 35), None),
            ('scan_by_prefix_at', ('C', 'b', 36), []),
            ('set_at', ('A', 'c', '5', 38), ANY),
            ('scan_by_prefix_at', ('C', 'B', 39), []),
            ('get_at', ('B', 'ba', 40), None),
            ('scan_by_prefix_at', ('A', 'B', 41), []),
            ('delete_at', ('C', 'c', 44), False),
            ('scan_at', ('A', 48), ['c(5)']),
            ('get_at', ('C', 'ab', 51), None),
            ('set_at_with_ttl', ('C', 'b', '79', 54, 7), ANY),
            ('scan_at', ('C', 57), ['b(79)']),
            ('get_at', ('A', 'a', 59), None),
            ('set_at', ('C', 'ab', '8', 61), ANY),
            ('get_at', ('C', 'ab', 63), '8'),
            ('set_at_with_ttl', ('A', 'B', '86', 67, 12), ANY),
            ('scan_at', ('B', 68), ['c(51)']),
            ('get_at', ('B', 'B', 70), None),
            ('scan_by_prefix_at', ('B', 'a', 73), []),
            ('delete_at', ('C', 'ba', 75), False),
            ('set_at_with_ttl', ('A', 'a', '65', 77, 11), ANY),
            ('set_at_with_ttl', ('B', 'b', '36', 80, 3), ANY),
            ('scan_at', ('C', 83), ['ab(8)']),
            ('scan_at', ('B', 84), ['c(51)']),
            ('set_at_with_ttl', ('B', 'c', '30', 88, 2), ANY),
            ('get_at', ('A', 'B', 92), None),
            ('scan_by_prefix_at', ('B', 'a', 94), []),
            ('get_at', ('C', 'B', 98), None),
            ('get_at', ('C', 'c', 99), None),
            ('scan_at', ('C', 100), ['ab(8)']),
            ('scan_at', ('B', 104), []),
            ('set_at_with_ttl', ('A', 'ab', '21', 106, 10), ANY),
            ('set_at', ('C', 'ba', '67', 110), ANY),
            ('set_at', ('B', 'ba', '3', 114), ANY),
            ('set_at_with_ttl', ('A', 'a', '67', 116, 6), ANY),
            ('get_at', ('C', 'ba', 118), '67'),
            ('set_at_with_ttl', ('A', 'b', '62', 119, 2), ANY),
            ('set_at', ('B', 'a', '38', 123), ANY),
            ('scan_at', ('C', 127), ['ab(8)', 'ba(67)']),
            ('scan_at', ('B', 131), ['a(38)', 'ba(3)']),
            ('set_at', ('B', 'B', '44', 133), ANY),
            ('scan_at', ('A', 135), ['c(5)']),
            ('scan_by_prefix_at', ('A', 'b', 137), []),
            ('scan_by_prefix_at', ('B', '', 140), ['B(44)', 'a(38)', 'ba(3)']),
            ('set_at', ('B', 'c', '15', 142), ANY),
            ('scan_by_prefix_at', ('C', 'b', 143), ['ba(67)']),
            ('scan_by_prefix_at', ('B', 'B', 146), ['B(44)']),
            ('delete_at', ('C', 'c', 150), False),
            ('get_at', ('A', 'ab', 153), None),
            ('scan_at', ('C', 154), ['ab(8)', 'ba(67)']),
            ('scan_at', ('B', 156), ['B(44)', 'a(38)', 'ba(3)', 'c(15)']),
            ('set_at_with_ttl', ('B', 'b', '36', 159, 2), ANY),
            ('scan_at', ('C', 160), ['ab(8)', 'ba(67)']),
            ('set_at_with_ttl', ('C', 'ba', '96', 162, 12), ANY),
            ('set_at_with_ttl', ('A', 'b', '53', 163, 10), ANY),
            ('set_at_with_ttl', ('A', 'a', '25', 167, 1), ANY),
            ('get_at', ('A', 'ab', 170), None),
        ])

    def test_level_3_case_08_randomized_sequence_42(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('set_at', ('B', 'ab', '28', 1), ANY),
            ('delete_at', ('C', 'c', 3), False),
            ('get_at', ('A', 'a', 4), None),
            ('set_at_with_ttl', ('C', 'ba', '3', 5, 9), ANY),
            ('delete_at', ('C', 'ba', 7), True),
            ('set_at_with_ttl', ('C', 'b', '0', 11, 3), ANY),
            ('set_at_with_ttl', ('A', 'ab', '97', 15, 6), ANY),
            ('set_at', ('A', 'b', '44', 16), ANY),
            ('scan_at', ('C', 19), []),
            ('scan_by_prefix_at', ('B', 'b', 20), []),
            ('get_at', ('C', 'a', 23), None),
            ('delete_at', ('B', 'a', 24), False),
            ('scan_at', ('B', 26), ['ab(28)']),
            ('delete_at', ('B', 'ab', 30), True),
            ('set_at_with_ttl', ('C', 'b', '89', 33, 11), ANY),
            ('get_at', ('A', 'ba', 34), None),
            ('set_at', ('B', 'b', '81', 36), ANY),
            ('delete_at', ('A', 'ab', 38), False),
            ('scan_at', ('B', 39), ['b(81)']),
            ('set_at_with_ttl', ('C', 'c', '40', 40, 4), ANY),
            ('set_at_with_ttl', ('C', 'B', '18', 44, 5), ANY),
            ('set_at_with_ttl', ('C', 'ba', '33', 46, 12), ANY),
            ('scan_by_prefix_at', ('B', 'a', 50), []),
            ('get_at', ('A', 'a', 52), None),
            ('set_at', ('A', 'c', '54', 53), ANY),
            ('set_at_with_ttl', ('C', 'B', '67', 54, 5), ANY),
            ('delete_at', ('A', 'c', 55), True),
            ('scan_at', ('B', 58), ['b(81)']),
            ('set_at_with_ttl', ('B', 'a', '92', 61, 12), ANY),
            ('scan_by_prefix_at', ('A', '', 64), ['b(44)']),
            ('scan_at', ('C', 67), []),
            ('set_at', ('A', 'ba', '99', 69), ANY),
            ('get_at', ('B', 'a', 70), '92'),
            ('scan_by_prefix_at', ('B', '', 71), ['a(92)', 'b(81)']),
            ('scan_by_prefix_at', ('A', 'B', 73), []),
            ('scan_by_prefix_at', ('C', 'a', 74), []),
            ('scan_by_prefix_at', ('A', 'B', 78), []),
            ('scan_by_prefix_at', ('C', 'a', 80), []),
            ('set_at_with_ttl', ('C', 'c', '47', 83, 8), ANY),
            ('set_at', ('A', 'a', '43', 87), ANY),
            ('get_at', ('A', 'ba', 88), '99'),
            ('set_at', ('C', 'c', '7', 90), ANY),
            ('set_at', ('A', 'b', '9', 92), ANY),
            ('set_at_with_ttl', ('B', 'ab', '69', 94, 3), ANY),
            ('set_at_with_ttl', ('B', 'B', '24', 98, 2), ANY),
            ('delete_at', ('B', 'B', 99), True),
            ('get_at', ('C', 'a', 103), None),
            ('set_at', ('C', 'b', '13', 104), ANY),
            ('set_at_with_ttl', ('C', 'B', '17', 106, 7), ANY),
            ('set_at_with_ttl', ('A', 'a', '56', 108, 9), ANY),
            ('set_at', ('C', 'a', '11', 109), ANY),
            ('set_at', ('B', 'B', '27', 111), ANY),
            ('scan_by_prefix_at', ('A', '', 115), ['a(56)', 'b(9)', 'ba(99)']),
            ('set_at_with_ttl', ('B', 'b', '54', 119, 12), ANY),
            ('set_at', ('B', 'ab', '7', 123), ANY),
            ('delete_at', ('A', 'a', 124), False),
            ('get_at', ('C', 'ab', 128), None),
            ('scan_by_prefix_at', ('A', '', 129), ['b(9)', 'ba(99)']),
            ('delete_at', ('A', 'B', 130), False),
            ('scan_by_prefix_at', ('C', '', 131), ['a(11)', 'b(13)', 'c(7)']),
            ('set_at_with_ttl', ('C', 'ba', '66', 132, 6), ANY),
            ('set_at_with_ttl', ('C', 'b', '30', 135, 5), ANY),
            ('set_at', ('C', 'b', '58', 139), ANY),
            ('scan_by_prefix_at', ('A', 'B', 142), []),
            ('set_at', ('A', 'ba', '33', 143), ANY),
            ('scan_by_prefix_at', ('A', 'b', 145), ['b(9)', 'ba(33)']),
            ('set_at', ('C', 'c', '38', 148), ANY),
            ('delete_at', ('C', 'b', 149), True),
            ('scan_by_prefix_at', ('A', '', 150), ['b(9)', 'ba(33)']),
            ('delete_at', ('A', 'b', 151), True),
        ])


if __name__ == "__main__":
    unittest.main()
