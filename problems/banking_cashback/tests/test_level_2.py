"""
Level 2 tests for Banking System (cashback).

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

    def test_level_2_case_07_randomized_sequence_21(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('create_account', (1352, 'alice'), True),
            ('create_account', (4777, 'acc10'), True),
            ('create_account', (8702, 'acc2'), True),
            ('transfer', (12591, 'bob', 'acc2', 518), None),
            ('deposit', (16913, 'acc1', 15), None),
            ('top_spenders', (19953, 0), []),
            ('transfer', (21141, 'acc2', 'acc2', 44), None),
            ('top_spenders', (24720, 4), ['acc10(0)', 'acc2(0)', 'alice(0)']),
            ('create_account', (28340, 'acc10'), False),
            ('deposit', (32765, 'acc1', 665), None),
            ('create_account', (35784, 'acc1'), True),
            ('transfer', (36807, 'acc1', 'alice', 165), None),
            ('transfer', (41330, 'alice', 'alice', 155), None),
            ('transfer', (42862, 'alice', 'acc2', 77), None),
            ('deposit', (44479, 'bob', 748), None),
            ('create_account', (45061, 'alice'), False),
            ('transfer', (49640, 'acc2', 'acc10', 150), None),
            ('deposit', (54030, 'acc10', 978), 978),
            ('transfer', (57728, 'acc10', 'alice', 396), 582),
            ('create_account', (59905, 'acc1'), False),
            ('transfer', (61208, 'alice', 'acc1', 504), None),
            ('transfer', (61783, 'bob', 'acc2', 586), None),
            ('deposit', (66772, 'bob', 116), None),
            ('transfer', (68253, 'acc10', 'acc10', 355), None),
            ('top_spenders', (73146, 0), []),
            ('create_account', (74528, 'acc2'), False),
            ('deposit', (78041, 'acc1', 693), 693),
            ('top_spenders', (82299, 3), ['acc10(396)', 'acc1(0)', 'acc2(0)']),
            ('top_spenders', (83636, 0), []),
            ('deposit', (86476, 'alice', 683), 1079),
            ('top_spenders', (88502, 1), ['acc10(396)']),
            ('create_account', (93105, 'alice'), False),
            ('create_account', (97064, 'acc10'), False),
            ('top_spenders', (97492, 0), []),
            ('deposit', (100929, 'alice', 72), 1151),
            ('transfer', (103699, 'acc2', 'acc2', 491), None),
            ('deposit', (104104, 'bob', 934), None),
            ('create_account', (108029, 'acc2'), False),
            ('transfer', (111026, 'acc10', 'bob', 437), None),
            ('transfer', (114995, 'alice', 'acc10', 143), 1008),
            ('transfer', (119373, 'acc2', 'acc1', 392), None),
            ('top_spenders', (120405, 2), ['acc10(396)', 'alice(143)']),
            ('deposit', (125269, 'acc2', 873), 873),
            ('deposit', (130056, 'alice', 770), 1778),
            ('create_account', (131191, 'acc1'), False),
            ('create_account', (134443, 'acc1'), False),
            ('transfer', (138104, 'acc1', 'acc1', 672), None),
            ('create_account', (140409, 'bob'), True),
            ('deposit', (143066, 'acc2', 637), 1510),
            ('deposit', (144427, 'alice', 207), 1985),
        ])

    def test_level_2_case_08_randomized_sequence_22(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('create_account', (1150, 'acc2'), True),
            ('create_account', (1344, 'bob'), True),
            ('create_account', (5007, 'acc2'), False),
            ('transfer', (5995, 'acc10', 'acc1', 238), None),
            ('top_spenders', (8201, 4), ['acc2(0)', 'bob(0)']),
            ('top_spenders', (9669, 5), ['acc2(0)', 'bob(0)']),
            ('transfer', (10066, 'acc1', 'bob', 271), None),
            ('deposit', (12612, 'acc2', 871), 871),
            ('transfer', (13526, 'bob', 'acc1', 335), None),
            ('deposit', (16269, 'alice', 320), None),
            ('create_account', (20491, 'acc10'), True),
            ('deposit', (22007, 'acc10', 545), 545),
            ('deposit', (22272, 'acc10', 519), 1064),
            ('transfer', (24601, 'alice', 'alice', 677), None),
            ('deposit', (26116, 'acc10', 407), 1471),
            ('create_account', (30889, 'bob'), False),
            ('transfer', (35769, 'bob', 'alice', 690), None),
            ('deposit', (40097, 'acc1', 455), None),
            ('create_account', (43011, 'alice'), True),
            ('top_spenders', (43487, 4), ['acc10(0)', 'acc2(0)', 'alice(0)', 'bob(0)']),
            ('deposit', (45443, 'acc1', 470), None),
            ('deposit', (47028, 'bob', 386), 386),
            ('deposit', (49889, 'acc10', 645), 2116),
            ('deposit', (51456, 'acc1', 549), None),
            ('transfer', (52559, 'acc2', 'acc1', 54), None),
            ('deposit', (54157, 'acc2', 944), 1815),
            ('deposit', (58967, 'acc1', 511), None),
            ('create_account', (63260, 'acc10'), False),
            ('deposit', (67136, 'acc1', 659), None),
            ('top_spenders', (70035, 6), ['acc10(0)', 'acc2(0)', 'alice(0)', 'bob(0)']),
            ('deposit', (75020, 'acc1', 19), None),
            ('transfer', (76551, 'acc1', 'acc10', 100), None),
            ('transfer', (77955, 'bob', 'alice', 276), 110),
            ('create_account', (79408, 'acc2'), False),
            ('transfer', (82294, 'acc2', 'bob', 262), 1553),
            ('top_spenders', (86281, 0), []),
            ('transfer', (88545, 'bob', 'alice', 634), None),
            ('deposit', (90247, 'acc1', 753), None),
            ('top_spenders', (94546, 1), ['bob(276)']),
            ('top_spenders', (97641, 0), []),
            ('deposit', (99322, 'alice', 651), 927),
            ('create_account', (102455, 'alice'), False),
            ('deposit', (106260, 'acc2', 116), 1669),
            ('top_spenders', (108442, 1), ['bob(276)']),
            ('top_spenders', (109903, 0), []),
            ('deposit', (110149, 'bob', 287), 659),
            ('top_spenders', (110496, 2), ['bob(276)', 'acc2(262)']),
            ('deposit', (110530, 'alice', 867), 1794),
            ('deposit', (112442, 'alice', 144), 1938),
            ('deposit', (115352, 'acc1', 720), None),
        ])


if __name__ == "__main__":
    unittest.main()
