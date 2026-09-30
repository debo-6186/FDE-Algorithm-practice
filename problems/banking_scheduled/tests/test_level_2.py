"""
Level 2 tests for Banking System (scheduled payments).

Each test replays a sequence of calls on a fresh BankingSystemImpl() and checks
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

from banking_system_impl import BankingSystemImpl

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
        self.impl = BankingSystemImpl()

    def test_level_2_case_01_example_from_spec(self):
        """The Level 2 example table."""
        run_steps(self, self.impl, [
            ('create_account', (1, 'acc3'), True),
            ('create_account', (2, 'acc2'), True),
            ('create_account', (3, 'acc1'), True),
            ('deposit', (4, 'acc3', 2000), 2000),
            ('deposit', (5, 'acc2', 3000), 3000),
            ('deposit', (6, 'acc3', 4000), 6000),
            ('top_spenders', (7, 3), ['acc1(0)', 'acc2(0)', 'acc3(0)']),
            ('transfer', (8, 'acc3', 'acc2', 500), 5500),
            ('transfer', (9, 'acc3', 'acc1', 1000), 4500),
            ('transfer', (10, 'acc1', 'acc2', 700), 300),
            ('top_spenders', (11, 3), ['acc3(1500)', 'acc1(700)', 'acc2(0)']),
            ('top_spenders', (12, 1), ['acc3(1500)']),
            ('top_spenders', (13, 5), ['acc3(1500)', 'acc1(700)', 'acc2(0)']),
        ])

    def test_level_2_case_02_no_accounts_then_one(self):
        run_steps(self, self.impl, [
            ('top_spenders', (1, 3), []),
            ('top_spenders', (2, 0), []),
            ('create_account', (3, 'a'), True),
            ('top_spenders', (4, 3), ['a(0)']),
        ])

    def test_level_2_case_03_ties_sorted_alphabetically_not_numerically(self):
        """'acc10' < 'acc2' as strings."""
        run_steps(self, self.impl, [
            ('create_account', (1, 'acc2'), True),
            ('create_account', (2, 'acc10'), True),
            ('create_account', (3, 'acc1'), True),
            ('deposit', (4, 'acc2', 100), 100),
            ('deposit', (5, 'acc10', 100), 100),
            ('transfer', (6, 'acc2', 'acc1', 40), 60),
            ('transfer', (7, 'acc10', 'acc1', 40), 60),
            ('top_spenders', (8, 3), ['acc10(40)', 'acc2(40)', 'acc1(0)']),
        ])

    def test_level_2_case_04_failed_transfers_do_not_count(self):
        run_steps(self, self.impl, [
            ('create_account', (1, 'a'), True),
            ('create_account', (2, 'b'), True),
            ('deposit', (3, 'a', 10), 10),
            ('transfer', (4, 'a', 'b', 11), None),
            ('transfer', (5, 'a', 'a', 5), None),
            ('top_spenders', (6, 2), ['a(0)', 'b(0)']),
            ('transfer', (7, 'a', 'b', 10), 0),
            ('transfer', (8, 'b', 'a', 3), 7),
            ('top_spenders', (9, 2), ['a(10)', 'b(3)']),
        ])

    def test_level_2_case_05_incoming_money_is_not_spending(self):
        run_steps(self, self.impl, [
            ('create_account', (1, 'rich'), True),
            ('create_account', (2, 'poor'), True),
            ('deposit', (3, 'rich', 10000), 10000),
            ('transfer', (4, 'rich', 'poor', 1), 9999),
            ('top_spenders', (5, 2), ['rich(1)', 'poor(0)']),
            ('transfer', (6, 'poor', 'rich', 1), 0),
            ('top_spenders', (7, 2), ['poor(1)', 'rich(1)']),
        ])

    def test_level_2_case_06_n_zero_returns_empty(self):
        run_steps(self, self.impl, [
            ('create_account', (1, 'a'), True),
            ('top_spenders', (2, 0), []),
            ('top_spenders', (3, 1), ['a(0)']),
        ])

    def test_level_2_case_07_randomized_sequence_23(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('create_account', (30, 'acc10'), True),
            ('create_account', (59, 'acc1'), True),
            ('create_account', (60, 'bob'), True),
            ('deposit', (70, 'bob', 367), 367),
            ('transfer', (75, 'acc10', 'alice', 15), None),
            ('transfer', (83, 'acc1', 'acc1', 88), None),
            ('deposit', (106, 'acc1', 525), 525),
            ('transfer', (127, 'acc10', 'acc1', 211), None),
            ('create_account', (153, 'acc10'), False),
            ('deposit', (175, 'acc2', 995), None),
            ('deposit', (199, 'acc10', 992), 992),
            ('deposit', (218, 'acc10', 587), 1579),
            ('transfer', (221, 'acc2', 'alice', 605), None),
            ('deposit', (247, 'acc2', 187), None),
            ('deposit', (273, 'acc10', 690), 2269),
            ('transfer', (300, 'bob', 'acc1', 85), 282),
            ('deposit', (304, 'bob', 283), 565),
            ('deposit', (323, 'bob', 339), 904),
            ('deposit', (327, 'acc10', 556), 2825),
            ('top_spenders', (337, 4), ['bob(85)', 'acc1(0)', 'acc10(0)']),
            ('deposit', (344, 'acc1', 635), 1245),
            ('create_account', (370, 'alice'), True),
            ('deposit', (378, 'acc2', 941), None),
            ('transfer', (402, 'alice', 'acc2', 461), None),
            ('create_account', (404, 'alice'), False),
            ('create_account', (417, 'acc2'), True),
            ('create_account', (439, 'acc2'), False),
            ('transfer', (465, 'acc1', 'bob', 456), 789),
            ('create_account', (489, 'acc1'), False),
            ('deposit', (515, 'acc2', 38), 38),
            ('deposit', (518, 'bob', 202), 1562),
            ('top_spenders', (543, 1), ['acc1(456)']),
            ('create_account', (546, 'bob'), False),
            ('deposit', (567, 'bob', 572), 2134),
            ('deposit', (594, 'acc1', 432), 1221),
            ('top_spenders', (600, 6), ['acc1(456)', 'bob(85)', 'acc10(0)', 'acc2(0)', 'alice(0)']),
            ('transfer', (611, 'alice', 'acc2', 632), None),
            ('transfer', (634, 'acc1', 'acc2', 559), 662),
            ('deposit', (644, 'acc10', 791), 3616),
            ('transfer', (672, 'bob', 'acc1', 292), 1842),
            ('create_account', (676, 'acc2'), False),
            ('top_spenders', (687, 1), ['acc1(1015)']),
            ('top_spenders', (693, 2), ['acc1(1015)', 'bob(377)']),
            ('transfer', (711, 'acc1', 'acc2', 575), 379),
            ('transfer', (727, 'acc10', 'acc1', 347), 3269),
            ('create_account', (740, 'acc2'), False),
            ('top_spenders', (764, 6), ['acc1(1590)', 'bob(377)', 'acc10(347)', 'acc2(0)', 'alice(0)']),
            ('create_account', (786, 'alice'), False),
            ('deposit', (810, 'acc1', 431), 1157),
            ('deposit', (833, 'bob', 706), 2548),
        ])

    def test_level_2_case_08_randomized_sequence_24(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('create_account', (23, 'alice'), True),
            ('create_account', (50, 'bob'), True),
            ('create_account', (56, 'acc2'), True),
            ('deposit', (62, 'acc1', 723), None),
            ('top_spenders', (87, 5), ['acc2(0)', 'alice(0)', 'bob(0)']),
            ('transfer', (117, 'alice', 'alice', 651), None),
            ('create_account', (121, 'acc2'), False),
            ('transfer', (137, 'alice', 'acc10', 512), None),
            ('transfer', (140, 'acc10', 'bob', 162), None),
            ('deposit', (162, 'acc10', 77), None),
            ('transfer', (180, 'acc1', 'acc2', 324), None),
            ('top_spenders', (191, 2), ['acc2(0)', 'alice(0)']),
            ('deposit', (195, 'bob', 819), 819),
            ('transfer', (200, 'alice', 'acc10', 273), None),
            ('transfer', (218, 'acc2', 'acc1', 591), None),
            ('transfer', (234, 'acc2', 'acc10', 492), None),
            ('transfer', (241, 'acc2', 'alice', 518), None),
            ('top_spenders', (250, 4), ['acc2(0)', 'alice(0)', 'bob(0)']),
            ('deposit', (276, 'acc2', 268), 268),
            ('transfer', (287, 'acc2', 'alice', 212), 56),
            ('deposit', (313, 'acc1', 481), None),
            ('transfer', (325, 'acc10', 'acc2', 589), None),
            ('deposit', (352, 'acc2', 927), 983),
            ('create_account', (364, 'alice'), False),
            ('deposit', (387, 'alice', 806), 1018),
            ('create_account', (412, 'acc1'), True),
            ('transfer', (423, 'alice', 'bob', 510), 508),
            ('transfer', (442, 'alice', 'acc2', 289), 219),
            ('deposit', (452, 'acc2', 345), 1617),
            ('top_spenders', (476, 5), ['alice(799)', 'acc2(212)', 'acc1(0)', 'bob(0)']),
            ('create_account', (502, 'acc10'), True),
            ('transfer', (532, 'alice', 'alice', 648), None),
            ('top_spenders', (545, 3), ['alice(799)', 'acc2(212)', 'acc1(0)']),
            ('transfer', (558, 'acc10', 'acc10', 9), None),
            ('top_spenders', (571, 3), ['alice(799)', 'acc2(212)', 'acc1(0)']),
            ('create_account', (597, 'acc2'), False),
            ('create_account', (625, 'bob'), False),
            ('top_spenders', (632, 1), ['alice(799)']),
            ('create_account', (659, 'acc1'), False),
            ('deposit', (661, 'acc1', 571), 571),
            ('deposit', (684, 'acc2', 930), 2547),
            ('transfer', (695, 'acc1', 'acc2', 114), 457),
            ('transfer', (700, 'acc1', 'bob', 536), None),
            ('transfer', (716, 'acc10', 'acc10', 670), None),
            ('deposit', (746, 'alice', 421), 640),
            ('top_spenders', (776, 2), ['alice(799)', 'acc2(212)']),
            ('deposit', (779, 'acc2', 186), 2847),
            ('deposit', (784, 'acc10', 289), 289),
            ('top_spenders', (812, 1), ['alice(799)']),
            ('create_account', (820, 'bob'), False),
        ])


if __name__ == "__main__":
    unittest.main()
