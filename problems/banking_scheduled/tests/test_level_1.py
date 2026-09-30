"""
Level 1 tests for Banking System (scheduled payments).

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

    def test_level_1_case_07_randomized_sequence_12(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('create_account', (16, 'acc10'), True),
            ('create_account', (38, 'bob'), True),
            ('create_account', (60, 'acc10'), False),
            ('deposit', (65, 'acc10', 495), 495),
            ('transfer', (74, 'alice', 'bob', 234), None),
            ('create_account', (92, 'bob'), False),
            ('transfer', (97, 'acc10', 'acc2', 348), None),
            ('deposit', (126, 'bob', 839), 839),
            ('create_account', (133, 'acc10'), False),
            ('deposit', (155, 'acc1', 20), None),
            ('create_account', (185, 'bob'), False),
            ('create_account', (193, 'alice'), True),
            ('create_account', (208, 'alice'), False),
            ('deposit', (213, 'bob', 572), 1411),
            ('transfer', (219, 'acc1', 'bob', 176), None),
            ('transfer', (236, 'alice', 'bob', 429), None),
            ('deposit', (258, 'alice', 624), 624),
            ('deposit', (271, 'acc1', 991), None),
            ('transfer', (278, 'acc10', 'acc10', 372), None),
            ('transfer', (306, 'acc10', 'acc1', 259), None),
            ('deposit', (314, 'acc10', 524), 1019),
            ('transfer', (333, 'bob', 'acc2', 29), None),
            ('transfer', (346, 'alice', 'acc1', 532), None),
            ('deposit', (347, 'alice', 45), 669),
            ('deposit', (360, 'bob', 106), 1517),
            ('deposit', (385, 'acc2', 80), None),
            ('deposit', (408, 'alice', 284), 953),
            ('deposit', (424, 'acc1', 527), None),
            ('deposit', (439, 'acc10', 289), 1308),
            ('deposit', (454, 'alice', 246), 1199),
            ('deposit', (460, 'bob', 373), 1890),
            ('create_account', (466, 'acc2'), True),
            ('transfer', (496, 'acc10', 'acc10', 184), None),
            ('transfer', (504, 'bob', 'acc1', 254), None),
            ('create_account', (524, 'acc10'), False),
            ('deposit', (542, 'acc1', 950), None),
            ('transfer', (553, 'acc10', 'acc1', 236), None),
            ('deposit', (579, 'alice', 502), 1701),
            ('deposit', (600, 'alice', 916), 2617),
            ('create_account', (624, 'acc10'), False),
        ])


if __name__ == "__main__":
    unittest.main()
