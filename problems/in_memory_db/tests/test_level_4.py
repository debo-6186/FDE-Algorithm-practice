"""
Level 4 tests for In-Memory Database.

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


class TestLevel4(unittest.TestCase):
    def setUp(self):
        self.impl = InMemoryDBImpl()

    def test_level_4_case_01_example_from_spec(self):
        """The Level 4 example table."""
        run_steps(self, self.impl, [
            ('set_at_with_ttl', ('A', 'B', 'C', 1, 10), ANY),
            ('backup', (3,), 1),
            ('set_at', ('A', 'D', 'E', 4), ANY),
            ('backup', (5,), 1),
            ('delete_at', ('A', 'B', 8), True),
            ('backup', (9,), 1),
            ('restore', (10, 7), ANY),
            ('set_at', ('B', 'C', 'D', 11), ANY),
            ('backup', (12,), 2),
            ('scan_at', ('A', 15), ['B(C)', 'D(E)']),
            ('scan_at', ('A', 16), ['D(E)']),
            ('scan_at', ('B', 17), ['C(D)']),
            ('restore', (18, 3), ANY),
            ('scan_at', ('A', 25), ['B(C)']),
            ('scan_at', ('B', 25), []),
            ('get_at', ('A', 'B', 26), None),
            ('backup', (27,), 0),
        ])

    def test_level_4_case_02_backup_counts_only_non_empty_live_records(self):
        run_steps(self, self.impl, [
            ('set_at', ('a', 'f', '1', 1), ANY),
            ('set_at_with_ttl', ('b', 'f', '1', 2, 3), ANY),
            ('set_at', ('c', 'f', '1', 3), ANY),
            ('delete_at', ('c', 'f', 4), True),
            ('backup', (5,), 1),
            ('backup', (6,), 1),
        ])

    def test_level_4_case_03_restore_uses_backup_at_exact_time(self):
        run_steps(self, self.impl, [
            ('set_at', ('k', 'f', 'old', 1), ANY),
            ('backup', (2,), 1),
            ('set_at', ('k', 'f', 'new', 3), ANY),
            ('backup', (4,), 1),
            ('restore', (5, 4), ANY),
            ('get_at', ('k', 'f', 6), 'new'),
            ('restore', (7, 3), ANY),
            ('get_at', ('k', 'f', 8), 'old'),
        ])

    def test_level_4_case_04_restore_discards_later_writes(self):
        run_steps(self, self.impl, [
            ('set_at', ('k', 'a', '1', 1), ANY),
            ('backup', (2,), 1),
            ('set_at', ('k', 'b', '2', 3), ANY),
            ('set_at', ('z', 'z', 'z', 4), ANY),
            ('restore', (5, 2), ANY),
            ('scan_at', ('k', 6), ['a(1)']),
            ('scan_at', ('z', 7), []),
        ])

    def test_level_4_case_05_restored_data_is_independent_of_backup(self):
        """Writing after a restore must not change the stored backup."""
        run_steps(self, self.impl, [
            ('set_at', ('k', 'a', '1', 1), ANY),
            ('backup', (2,), 1),
            ('restore', (3, 2), ANY),
            ('set_at', ('k', 'a', 'changed', 4), ANY),
            ('set_at', ('k', 'b', 'extra', 5), ANY),
            ('restore', (6, 2), ANY),
            ('scan_at', ('k', 7), ['a(1)']),
        ])

    def test_level_4_case_06_ttl_recalculated_from_restore_time(self):
        run_steps(self, self.impl, [
            ('set_at_with_ttl', ('k', 'f', 'v', 100, 50), ANY),
            ('backup', (120,), 1),
            ('restore', (1000, 130), ANY),
            ('get_at', ('k', 'f', 1029), 'v'),
            ('get_at', ('k', 'f', 1030), None),
        ])

    def test_level_4_case_07_fields_expired_at_backup_are_not_saved(self):
        run_steps(self, self.impl, [
            ('set_at_with_ttl', ('k', 'f', 'v', 1, 2), ANY),
            ('set_at', ('k', 'g', 'w', 2), ANY),
            ('backup', (3,), 1),
            ('restore', (4, 3), ANY),
            ('scan_at', ('k', 5), ['g(w)']),
        ])

    def test_level_4_case_08_restore_twice_from_same_backup(self):
        run_steps(self, self.impl, [
            ('set_at_with_ttl', ('k', 'f', 'v', 1, 10), ANY),
            ('backup', (5,), 1),
            ('restore', (20, 5), ANY),
            ('get_at', ('k', 'f', 25), 'v'),
            ('get_at', ('k', 'f', 26), None),
            ('restore', (30, 6), ANY),
            ('get_at', ('k', 'f', 35), 'v'),
            ('get_at', ('k', 'f', 36), None),
        ])

    def test_level_4_case_09_randomized_sequence_56(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('get_at', ('C', 'b', 1), None),
            ('scan_by_prefix_at', ('A', '', 5), []),
            ('scan_at', ('C', 8), []),
            ('scan_by_prefix_at', ('A', 'a', 9), []),
            ('scan_at', ('A', 13), []),
            ('set_at_with_ttl', ('C', 'ab', '71', 15, 4), ANY),
            ('set_at_with_ttl', ('B', 'ab', '85', 19, 2), ANY),
            ('delete_at', ('A', 'ab', 21), False),
            ('set_at', ('B', 'c', '81', 23), ANY),
            ('set_at', ('C', 'a', '74', 26), ANY),
            ('set_at', ('C', 'c', '0', 29), ANY),
            ('scan_at', ('B', 30), ['c(81)']),
            ('get_at', ('B', 'ab', 33), None),
            ('delete_at', ('C', 'a', 37), True),
            ('set_at_with_ttl', ('C', 'B', '18', 39, 1), ANY),
            ('set_at_with_ttl', ('C', 'b', '59', 41, 1), ANY),
            ('set_at', ('B', 'ba', '20', 43), ANY),
            ('set_at', ('C', 'c', '36', 44), ANY),
            ('set_at_with_ttl', ('A', 'ba', '61', 48, 11), ANY),
            ('scan_at', ('A', 51), ['ba(61)']),
            ('set_at', ('A', 'c', '79', 55), ANY),
            ('delete_at', ('C', 'c', 57), True),
            ('set_at', ('C', 'c', '62', 58), ANY),
            ('set_at', ('A', 'a', '32', 61), ANY),
            ('scan_by_prefix_at', ('C', '', 63), ['c(62)']),
            ('backup', (67,), 3),
            ('scan_by_prefix_at', ('A', 'a', 68), ['a(32)']),
            ('restore', (69, 67), ANY),
            ('scan_by_prefix_at', ('B', '', 71), ['ba(20)', 'c(81)']),
            ('set_at', ('C', 'B', '68', 73), ANY),
            ('restore', (76, 69), ANY),
            ('scan_by_prefix_at', ('C', 'b', 78), []),
            ('backup', (82,), 3),
            ('set_at', ('B', 'ab', '55', 85), ANY),
            ('get_at', ('A', 'ba', 88), None),
            ('scan_by_prefix_at', ('B', 'B', 89), []),
            ('set_at_with_ttl', ('C', 'c', '29', 90, 1), ANY),
            ('backup', (94,), 2),
            ('restore', (97, 82), ANY),
            ('delete_at', ('A', 'b', 101), False),
            ('scan_by_prefix_at', ('A', 'a', 102), ['a(32)']),
            ('scan_by_prefix_at', ('C', 'a', 106), []),
            ('get_at', ('C', 'B', 109), None),
            ('restore', (112, 82), ANY),
            ('set_at_with_ttl', ('C', 'c', '84', 116, 8), ANY),
            ('scan_at', ('A', 120), ['a(32)', 'c(79)']),
            ('backup', (124,), 2),
            ('scan_at', ('B', 126), ['ba(20)', 'c(81)']),
            ('scan_at', ('C', 127), []),
            ('backup', (129,), 2),
            ('set_at', ('B', 'a', '68', 130), ANY),
            ('scan_at', ('A', 133), ['a(32)', 'c(79)']),
            ('scan_by_prefix_at', ('C', 'b', 136), []),
            ('set_at_with_ttl', ('B', 'ab', '96', 138, 9), ANY),
            ('set_at_with_ttl', ('A', 'c', '38', 140, 11), ANY),
            ('scan_by_prefix_at', ('B', 'B', 144), []),
            ('restore', (147, 82), ANY),
            ('get_at', ('A', 'a', 150), '32'),
            ('set_at_with_ttl', ('B', 'ab', '4', 152, 2), ANY),
            ('set_at_with_ttl', ('B', 'a', '66', 153, 12), ANY),
            ('get_at', ('B', 'c', 154), '81'),
            ('backup', (158,), 3),
            ('scan_by_prefix_at', ('A', 'a', 159), ['a(32)']),
            ('set_at', ('C', 'ab', '74', 162), ANY),
            ('scan_at', ('A', 165), ['a(32)', 'c(79)']),
            ('backup', (167,), 3),
            ('scan_at', ('A', 168), ['a(32)', 'c(79)']),
            ('set_at', ('C', 'ba', '54', 170), ANY),
            ('get_at', ('B', 'c', 172), '81'),
            ('set_at_with_ttl', ('C', 'b', '98', 173, 7), ANY),
            ('set_at', ('A', 'B', '81', 174), ANY),
            ('set_at', ('B', 'a', '90', 176), ANY),
            ('set_at_with_ttl', ('C', 'a', '55', 177, 9), ANY),
            ('delete_at', ('A', 'ab', 179), False),
            ('restore', (183, 167), ANY),
            ('set_at_with_ttl', ('C', 'B', '63', 186, 1), ANY),
            ('scan_at', ('B', 188), ['ba(20)', 'c(81)']),
            ('scan_by_prefix_at', ('A', 'B', 190), []),
            ('set_at', ('A', 'ba', '15', 192), ANY),
            ('scan_at', ('A', 194), ['a(32)', 'ba(15)', 'c(79)']),
            ('set_at', ('C', 'b', '66', 195), ANY),
            ('restore', (196, 67), ANY),
            ('scan_at', ('B', 198), ['ba(20)', 'c(81)']),
            ('scan_by_prefix_at', ('A', '', 199), ['a(32)', 'c(79)']),
            ('set_at_with_ttl', ('B', 'B', '79', 201, 9), ANY),
            ('get_at', ('A', 'ba', 203), None),
            ('scan_by_prefix_at', ('A', '', 206), ['a(32)', 'c(79)']),
            ('set_at_with_ttl', ('C', 'b', '31', 207, 8), ANY),
            ('set_at_with_ttl', ('B', 'b', '25', 211, 5), ANY),
            ('set_at_with_ttl', ('C', 'c', '30', 213, 11), ANY),
        ])

    def test_level_4_case_10_randomized_sequence_57(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('get_at', ('C', 'a', 1), None),
            ('delete_at', ('B', 'b', 3), False),
            ('scan_at', ('B', 7), []),
            ('delete_at', ('C', 'b', 9), False),
            ('get_at', ('A', 'c', 13), None),
            ('delete_at', ('C', 'ba', 17), False),
            ('delete_at', ('A', 'B', 19), False),
            ('backup', (21,), 0),
            ('delete_at', ('B', 'ba', 23), False),
            ('set_at_with_ttl', ('B', 'B', '85', 25, 4), ANY),
            ('get_at', ('C', 'B', 29), None),
            ('set_at', ('B', 'a', '79', 33), ANY),
            ('get_at', ('A', 'c', 36), None),
            ('delete_at', ('A', 'b', 40), False),
            ('restore', (41, 22), ANY),
            ('get_at', ('A', 'ab', 42), None),
            ('scan_at', ('B', 43), []),
            ('set_at', ('C', 'B', '31', 45), ANY),
            ('delete_at', ('A', 'c', 47), False),
            ('restore', (48, 21), ANY),
            ('backup', (50,), 0),
            ('delete_at', ('A', 'a', 51), False),
            ('set_at_with_ttl', ('C', 'B', '68', 52, 3), ANY),
            ('get_at', ('C', 'ba', 53), None),
            ('backup', (57,), 0),
            ('set_at_with_ttl', ('B', 'ab', '91', 61, 2), ANY),
            ('set_at_with_ttl', ('A', 'a', '3', 62, 8), ANY),
            ('set_at', ('C', 'c', '33', 63), ANY),
            ('get_at', ('B', 'B', 65), None),
            ('get_at', ('B', 'ab', 69), None),
            ('scan_by_prefix_at', ('B', 'B', 73), []),
            ('get_at', ('C', 'a', 75), None),
            ('delete_at', ('A', 'B', 79), False),
            ('scan_at', ('B', 80), []),
            ('set_at_with_ttl', ('C', 'a', '0', 81, 11), ANY),
            ('scan_at', ('C', 82), ['a(0)', 'c(33)']),
            ('scan_at', ('A', 86), []),
            ('restore', (87, 57), ANY),
            ('set_at', ('C', 'a', '51', 91), ANY),
            ('set_at_with_ttl', ('C', 'ba', '95', 93, 11), ANY),
            ('backup', (97,), 1),
            ('restore', (101, 21), ANY),
            ('scan_at', ('C', 105), []),
            ('delete_at', ('C', 'c', 108), False),
            ('set_at_with_ttl', ('B', 'b', '23', 112, 2), ANY),
            ('delete_at', ('A', 'ab', 115), False),
            ('get_at', ('A', 'a', 117), None),
            ('get_at', ('A', 'ab', 119), None),
            ('set_at_with_ttl', ('C', 'ba', '38', 122, 4), ANY),
            ('backup', (124,), 1),
            ('set_at_with_ttl', ('A', 'c', '37', 126, 12), ANY),
            ('delete_at', ('A', 'B', 128), False),
            ('get_at', ('B', 'b', 132), None),
            ('scan_at', ('B', 133), []),
            ('set_at_with_ttl', ('C', 'B', '88', 134, 5), ANY),
            ('scan_by_prefix_at', ('C', 'b', 136), []),
            ('scan_at', ('B', 138), []),
            ('scan_by_prefix_at', ('A', 'b', 141), []),
            ('backup', (143,), 0),
            ('delete_at', ('B', 'c', 147), False),
            ('scan_by_prefix_at', ('C', 'a', 149), []),
            ('scan_at', ('C', 151), []),
            ('set_at', ('B', 'ab', '65', 152), ANY),
            ('scan_at', ('A', 155), []),
            ('delete_at', ('A', 'b', 158), False),
            ('set_at', ('A', 'c', '63', 161), ANY),
            ('get_at', ('C', 'a', 163), None),
            ('set_at', ('A', 'B', '34', 167), ANY),
            ('set_at_with_ttl', ('A', 'ba', '33', 169, 3), ANY),
            ('set_at_with_ttl', ('B', 'b', '70', 173, 8), ANY),
            ('scan_by_prefix_at', ('B', 'B', 174), []),
            ('scan_at', ('B', 177), ['ab(65)', 'b(70)']),
            ('get_at', ('C', 'b', 181), None),
            ('get_at', ('C', 'ab', 182), None),
            ('set_at', ('A', 'ba', '40', 186), ANY),
            ('restore', (188, 58), ANY),
            ('get_at', ('C', 'a', 189), None),
            ('restore', (191, 21), ANY),
            ('set_at', ('C', 'ab', '19', 193), ANY),
            ('set_at', ('A', 'b', '87', 195), ANY),
            ('set_at_with_ttl', ('B', 'B', '12', 197, 9), ANY),
            ('scan_at', ('B', 200), ['B(12)']),
            ('restore', (203, 125), ANY),
            ('set_at', ('C', 'B', '59', 207), ANY),
            ('scan_at', ('C', 210), ['B(59)']),
            ('set_at_with_ttl', ('C', 'b', '45', 214, 3), ANY),
            ('set_at', ('A', 'b', '18', 217), ANY),
            ('set_at_with_ttl', ('C', 'c', '8', 220, 12), ANY),
            ('scan_by_prefix_at', ('B', 'b', 223), []),
            ('delete_at', ('A', 'a', 226), False),
        ])

    def test_level_4_case_11_randomized_sequence_58(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('set_at_with_ttl', ('C', 'ab', '5', 2, 4), ANY),
            ('get_at', ('B', 'b', 6), None),
            ('backup', (10,), 0),
            ('set_at', ('A', 'B', '96', 11), ANY),
            ('get_at', ('C', 'B', 12), None),
            ('set_at', ('C', 'ab', '38', 15), ANY),
            ('set_at_with_ttl', ('B', 'b', '22', 16, 10), ANY),
            ('scan_by_prefix_at', ('A', 'a', 18), []),
            ('set_at', ('A', 'c', '29', 22), ANY),
            ('set_at_with_ttl', ('B', 'c', '92', 23, 2), ANY),
            ('delete_at', ('C', 'ba', 27), False),
            ('delete_at', ('C', 'b', 30), False),
            ('set_at', ('B', 'ab', '59', 34), ANY),
            ('scan_at', ('B', 36), ['ab(59)']),
            ('set_at_with_ttl', ('A', 'B', '92', 37, 5), ANY),
            ('scan_at', ('B', 40), ['ab(59)']),
            ('set_at', ('C', 'a', '16', 44), ANY),
            ('delete_at', ('A', 'b', 45), False),
            ('set_at', ('C', 'a', '15', 46), ANY),
            ('get_at', ('C', 'c', 47), None),
            ('scan_at', ('C', 50), ['a(15)', 'ab(38)']),
            ('set_at_with_ttl', ('A', 'b', '9', 53, 3), ANY),
            ('set_at_with_ttl', ('A', 'c', '47', 55, 7), ANY),
            ('scan_by_prefix_at', ('B', 'a', 56), ['ab(59)']),
            ('scan_by_prefix_at', ('A', '', 58), ['c(47)']),
            ('scan_by_prefix_at', ('B', '', 61), ['ab(59)']),
            ('restore', (64, 12), ANY),
            ('set_at', ('A', 'ba', '82', 68), ANY),
            ('scan_by_prefix_at', ('A', '', 70), ['ba(82)']),
            ('restore', (72, 10), ANY),
            ('set_at', ('B', 'c', '30', 74), ANY),
            ('scan_by_prefix_at', ('B', 'B', 77), []),
            ('set_at_with_ttl', ('A', 'ba', '39', 78, 2), ANY),
            ('backup', (82,), 1),
            ('scan_by_prefix_at', ('C', 'B', 83), []),
            ('backup', (86,), 1),
            ('restore', (88, 11), ANY),
            ('get_at', ('A', 'c', 92), None),
            ('get_at', ('B', 'ba', 94), None),
            ('get_at', ('B', 'c', 97), None),
            ('set_at', ('B', 'ab', '10', 100), ANY),
            ('delete_at', ('C', 'ab', 103), False),
            ('set_at_with_ttl', ('A', 'b', '28', 107, 3), ANY),
            ('restore', (108, 88), ANY),
            ('get_at', ('A', 'ab', 110), None),
            ('scan_at', ('C', 112), []),
            ('set_at_with_ttl', ('C', 'ba', '79', 114, 11), ANY),
            ('get_at', ('B', 'B', 117), None),
            ('set_at', ('B', 'c', '1', 121), ANY),
            ('backup', (122,), 2),
            ('backup', (126,), 1),
            ('backup', (128,), 1),
            ('delete_at', ('B', 'b', 131), False),
            ('set_at_with_ttl', ('A', 'ab', '27', 135, 8), ANY),
            ('get_at', ('A', 'a', 136), None),
            ('delete_at', ('C', 'a', 140), False),
            ('scan_by_prefix_at', ('A', 'B', 142), []),
            ('get_at', ('B', 'b', 145), None),
            ('backup', (146,), 1),
            ('restore', (150, 86), ANY),
            ('set_at_with_ttl', ('B', 'b', '20', 152, 8), ANY),
            ('get_at', ('B', 'ab', 154), None),
            ('restore', (157, 122), ANY),
            ('get_at', ('B', 'b', 161), None),
            ('get_at', ('B', 'a', 163), None),
            ('delete_at', ('C', 'ab', 164), False),
            ('get_at', ('C', 'c', 165), None),
            ('set_at_with_ttl', ('B', 'a', '50', 167, 5), ANY),
            ('get_at', ('A', 'b', 170), None),
            ('get_at', ('B', 'ba', 172), None),
            ('set_at', ('C', 'B', '18', 176), ANY),
            ('set_at', ('A', 'B', '94', 179), ANY),
            ('scan_by_prefix_at', ('A', '', 183), ['B(94)']),
            ('set_at_with_ttl', ('C', 'ba', '59', 187, 12), ANY),
            ('get_at', ('A', 'b', 188), None),
            ('set_at_with_ttl', ('A', 'B', '98', 189, 1), ANY),
            ('delete_at', ('C', 'b', 190), False),
            ('set_at', ('A', 'b', '8', 193), ANY),
            ('get_at', ('C', 'a', 197), None),
            ('set_at_with_ttl', ('A', 'a', '65', 200, 12), ANY),
            ('scan_by_prefix_at', ('C', '', 201), ['B(18)']),
            ('get_at', ('A', 'b', 202), '8'),
            ('scan_at', ('B', 206), ['c(1)']),
            ('set_at_with_ttl', ('B', 'ba', '57', 207, 10), ANY),
            ('backup', (211,), 3),
            ('get_at', ('B', 'c', 213), '1'),
            ('scan_at', ('C', 217), ['B(18)']),
            ('scan_by_prefix_at', ('A', 'B', 220), []),
            ('set_at_with_ttl', ('C', 'ab', '1', 222, 5), ANY),
            ('set_at_with_ttl', ('B', 'a', '58', 224, 10), ANY),
        ])


if __name__ == "__main__":
    unittest.main()
