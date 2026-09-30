"""
Level 1 tests for Banking System (cashback).

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


class TestLevel1(unittest.TestCase):
    def setUp(self):
        self.impl = BankingSystemImpl()

    def test_level_1_case_01_example_from_spec(self):
        """The Level 1 example table."""
        run_steps(self, self.impl, [
            ('create_account', (1, 'alice'), True),
            ('create_account', (2, 'alice'), False),
            ('create_account', (3, 'bob'), True),
            ('deposit', (4, 'carol', 500), None),
            ('deposit', (5, 'alice', 1000), 1000),
            ('transfer', (6, 'alice', 'bob', 1001), None),
            ('transfer', (7, 'alice', 'alice', 10), None),
            ('transfer', (8, 'alice', 'bob', 300), 700),
            ('deposit', (9, 'bob', 50), 350),
        ])

    def test_level_1_case_02_deposits_accumulate(self):
        run_steps(self, self.impl, [
            ('create_account', (1, 'acc1'), True),
            ('deposit', (2, 'acc1', 500), 500),
            ('deposit', (3, 'acc1', 300), 800),
            ('deposit', (4, 'acc2', 100), None),
            ('create_account', (5, 'acc2'), True),
            ('deposit', (6, 'acc2', 100), 100),
        ])

    def test_level_1_case_03_transfer_missing_accounts(self):
        """Either side missing -> None, and nothing changes."""
        run_steps(self, self.impl, [
            ('create_account', (1, 'a'), True),
            ('deposit', (2, 'a', 100), 100),
            ('transfer', (3, 'a', 'zzz', 10), None),
            ('transfer', (4, 'zzz', 'a', 10), None),
            ('transfer', (5, 'x', 'y', 10), None),
            ('deposit', (6, 'a', 1), 101),
        ])

    def test_level_1_case_04_transfer_exact_balance_and_one_over(self):
        run_steps(self, self.impl, [
            ('create_account', (1, 'a'), True),
            ('create_account', (2, 'b'), True),
            ('deposit', (3, 'a', 50), 50),
            ('transfer', (4, 'a', 'b', 51), None),
            ('transfer', (5, 'a', 'b', 50), 0),
            ('transfer', (6, 'a', 'b', 1), None),
            ('transfer', (7, 'b', 'a', 20), 30),
            ('deposit', (8, 'a', 5), 25),
        ])

    def test_level_1_case_05_failed_transfer_changes_nothing(self):
        run_steps(self, self.impl, [
            ('create_account', (10, 'x'), True),
            ('create_account', (20, 'y'), True),
            ('deposit', (30, 'x', 70), 70),
            ('transfer', (40, 'x', 'y', 71), None),
            ('deposit', (50, 'y', 5), 5),
            ('transfer', (60, 'x', 'x', 1), None),
            ('deposit', (70, 'x', 5), 75),
        ])

    def test_level_1_case_06_create_account_is_idempotent_per_id(self):
        run_steps(self, self.impl, [
            ('create_account', (1, 'A'), True),
            ('create_account', (2, 'a'), True),
            ('create_account', (3, 'A'), False),
            ('deposit', (4, 'A', 10), 10),
            ('deposit', (5, 'a', 20), 20),
            ('create_account', (6, 'a'), False),
            ('deposit', (7, 'a', 1), 21),
        ])

    def test_level_1_case_07_randomized_sequence_11(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('create_account', (3706, 'bob'), True),
            ('create_account', (7521, 'alice'), True),
            ('create_account', (11682, 'bob'), False),
            ('create_account', (13238, 'bob'), False),
            ('transfer', (17136, 'acc2', 'acc1', 458), None),
            ('create_account', (19622, 'bob'), False),
            ('deposit', (19966, 'alice', 988), 988),
            ('transfer', (23677, 'bob', 'acc2', 639), None),
            ('transfer', (23800, 'acc1', 'acc1', 37), None),
            ('transfer', (25359, 'bob', 'acc1', 476), None),
            ('deposit', (28032, 'acc2', 532), None),
            ('transfer', (29947, 'alice', 'acc1', 679), None),
            ('deposit', (30644, 'acc10', 417), None),
            ('transfer', (35160, 'acc1', 'acc10', 323), None),
            ('deposit', (37042, 'acc1', 72), None),
            ('transfer', (41656, 'alice', 'acc1', 298), None),
            ('create_account', (44823, 'acc1'), True),
            ('deposit', (44828, 'acc1', 482), 482),
            ('transfer', (47904, 'alice', 'alice', 75), None),
            ('transfer', (52543, 'acc10', 'acc10', 90), None),
            ('deposit', (55093, 'alice', 777), 1765),
            ('create_account', (56060, 'acc1'), False),
            ('create_account', (56150, 'alice'), False),
            ('transfer', (57606, 'acc2', 'alice', 522), None),
            ('transfer', (59169, 'acc2', 'alice', 660), None),
            ('create_account', (62313, 'alice'), False),
            ('create_account', (64057, 'bob'), False),
            ('transfer', (66549, 'acc1', 'acc2', 192), None),
            ('transfer', (69779, 'bob', 'bob', 103), None),
            ('transfer', (70124, 'acc2', 'alice', 265), None),
            ('transfer', (70203, 'acc10', 'acc10', 396), None),
            ('create_account', (70805, 'acc2'), True),
            ('transfer', (75579, 'acc1', 'bob', 378), 104),
            ('transfer', (78624, 'acc2', 'bob', 496), None),
            ('create_account', (83331, 'alice'), False),
            ('transfer', (84829, 'acc10', 'acc2', 626), None),
            ('transfer', (86873, 'acc2', 'bob', 202), None),
            ('transfer', (90054, 'bob', 'acc1', 432), None),
            ('create_account', (90443, 'acc1'), False),
            ('transfer', (94641, 'acc2', 'alice', 264), None),
        ])


if __name__ == "__main__":
    unittest.main()
