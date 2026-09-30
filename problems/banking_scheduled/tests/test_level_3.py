"""
Level 3 tests for Banking System (scheduled payments).

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


class TestLevel3(unittest.TestCase):
    def setUp(self):
        self.impl = BankingSystemImpl()

    def test_level_3_case_01_example_from_spec(self):
        """The Level 3 example table."""
        run_steps(self, self.impl, [
            ('create_account', (1, 'alice'), True),
            ('create_account', (2, 'bob'), True),
            ('deposit', (3, 'alice', 1000), 1000),
            ('schedule_payment', (4, 'alice', 300, 10), 'payment1'),
            ('schedule_payment', (5, 'carol', 100, 5), None),
            ('schedule_payment', (6, 'bob', 50, 8), 'payment2'),
            ('schedule_payment', (7, 'alice', 200, 20), 'payment3'),
            ('cancel_payment', (8, 'bob', 'payment1'), False),
            ('cancel_payment', (9, 'alice', 'payment9'), False),
            ('deposit', (13, 'alice', 10), 1010),
            ('deposit', (14, 'bob', 100), 100),
            ('cancel_payment', (15, 'bob', 'payment2'), False),
            ('cancel_payment', (16, 'alice', 'payment3'), True),
            ('cancel_payment', (17, 'alice', 'payment3'), False),
            ('top_spenders', (30, 2), ['alice(300)', 'bob(0)']),
            ('deposit', (31, 'alice', 1), 711),
        ])

    def test_level_3_case_02_payment_runs_before_operation_at_due_time(self):
        run_steps(self, self.impl, [
            ('create_account', (1, 'a'), True),
            ('create_account', (2, 'b'), True),
            ('deposit', (3, 'a', 100), 100),
            ('schedule_payment', (4, 'a', 60, 6), 'payment1'),
            ('transfer', (10, 'a', 'b', 50), None),
            ('transfer', (11, 'a', 'b', 40), 0),
            ('top_spenders', (12, 2), ['a(100)', 'b(0)']),
        ])

    def test_level_3_case_03_same_due_time_processed_in_creation_order(self):
        """payment1 drains the account, so payment2 is skipped."""
        run_steps(self, self.impl, [
            ('create_account', (1, 'a'), True),
            ('deposit', (2, 'a', 100), 100),
            ('schedule_payment', (3, 'a', 80, 7), 'payment1'),
            ('schedule_payment', (4, 'a', 30, 6), 'payment2'),
            ('deposit', (10, 'a', 5), 25),
            ('cancel_payment', (11, 'a', 'payment2'), False),
            ('top_spenders', (12, 1), ['a(80)']),
        ])

    def test_level_3_case_04_skipped_payment_is_not_retried(self):
        run_steps(self, self.impl, [
            ('create_account', (1, 'a'), True),
            ('schedule_payment', (2, 'a', 50, 3), 'payment1'),
            ('deposit', (4, 'a', 10), 10),
            ('deposit', (5, 'a', 100), 110),
            ('deposit', (100, 'a', 1), 111),
            ('top_spenders', (101, 1), ['a(0)']),
        ])

    def test_level_3_case_05_cancel_rules(self):
        """Wrong owner, unknown id, already canceled, and too late (due at the cancel time)."""
        run_steps(self, self.impl, [
            ('create_account', (1, 'a'), True),
            ('create_account', (2, 'b'), True),
            ('deposit', (3, 'a', 500), 500),
            ('schedule_payment', (4, 'a', 100, 10), 'payment1'),
            ('schedule_payment', (5, 'a', 100, 20), 'payment2'),
            ('cancel_payment', (6, 'b', 'payment2'), False),
            ('cancel_payment', (7, 'a', 'payment3'), False),
            ('cancel_payment', (14, 'a', 'payment1'), False),
            ('cancel_payment', (15, 'a', 'payment2'), True),
            ('cancel_payment', (16, 'a', 'payment2'), False),
            ('deposit', (30, 'a', 1), 401),
        ])

    def test_level_3_case_06_ids_count_scheduled_payments_across_accounts(self):
        run_steps(self, self.impl, [
            ('create_account', (1, 'x'), True),
            ('create_account', (2, 'y'), True),
            ('schedule_payment', (3, 'y', 1, 1000), 'payment1'),
            ('schedule_payment', (4, 'nobody', 1, 1000), None),
            ('schedule_payment', (5, 'x', 1, 1000), 'payment2'),
            ('schedule_payment', (6, 'x', 1, 1000), 'payment3'),
            ('cancel_payment', (7, 'x', 'payment1'), False),
            ('cancel_payment', (8, 'y', 'payment1'), True),
        ])

    def test_level_3_case_07_lazy_processing_many_payments(self):
        """No operation at the due times; a later query must see all of them."""
        run_steps(self, self.impl, [
            ('create_account', (1, 'a'), True),
            ('create_account', (2, 'b'), True),
            ('deposit', (3, 'a', 1000), 1000),
            ('deposit', (4, 'b', 100), 100),
            ('schedule_payment', (5, 'a', 100, 5), 'payment1'),
            ('schedule_payment', (6, 'b', 150, 5), 'payment2'),
            ('schedule_payment', (7, 'a', 200, 1), 'payment3'),
            ('top_spenders', (1000, 2), ['a(300)', 'b(0)']),
            ('deposit', (1001, 'a', 1), 701),
            ('deposit', (1002, 'b', 1), 101),
        ])

    def test_level_3_case_08_randomized_sequence_33(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('create_account', (19, 'acc2'), True),
            ('create_account', (40, 'acc2'), False),
            ('create_account', (67, 'acc10'), True),
            ('top_spenders', (83, 4), ['acc10(0)', 'acc2(0)']),
            ('cancel_payment', (89, 'bob', 'payment1'), False),
            ('transfer', (111, 'alice', 'acc10', 690), None),
            ('create_account', (132, 'alice'), True),
            ('transfer', (142, 'acc1', 'bob', 694), None),
            ('schedule_payment', (156, 'acc10', 328, 119), 'payment1'),
            ('schedule_payment', (174, 'acc2', 58, 16), 'payment2'),
            ('cancel_payment', (185, 'acc10', 'payment1'), True),
            ('create_account', (214, 'acc10'), False),
            ('top_spenders', (218, 4), ['acc10(0)', 'acc2(0)', 'alice(0)']),
            ('deposit', (227, 'acc10', 538), 538),
            ('deposit', (249, 'alice', 399), 399),
            ('schedule_payment', (255, 'acc1', 643, 47), None),
            ('schedule_payment', (279, 'acc1', 153, 9), None),
            ('deposit', (282, 'acc10', 4), 542),
            ('transfer', (284, 'acc10', 'acc2', 198), 344),
            ('top_spenders', (306, 4), ['acc10(198)', 'acc2(0)', 'alice(0)']),
            ('schedule_payment', (322, 'bob', 466, 69), None),
            ('schedule_payment', (348, 'alice', 10, 9), 'payment3'),
            ('transfer', (364, 'acc10', 'acc1', 684), None),
            ('deposit', (392, 'bob', 650), None),
            ('schedule_payment', (407, 'acc2', 507, 117), 'payment4'),
            ('top_spenders', (431, 5), ['acc10(198)', 'alice(10)', 'acc2(0)']),
            ('schedule_payment', (434, 'acc10', 287, 60), 'payment5'),
            ('cancel_payment', (448, 'alice', 'payment5'), False),
            ('schedule_payment', (464, 'alice', 22, 50), 'payment6'),
            ('transfer', (489, 'acc10', 'acc2', 109), 235),
            ('cancel_payment', (495, 'acc10', 'payment10'), False),
            ('cancel_payment', (505, 'acc2', 'payment6'), False),
            ('transfer', (532, 'acc10', 'acc10', 601), None),
            ('transfer', (554, 'acc1', 'acc2', 493), None),
            ('schedule_payment', (557, 'bob', 587, 11), None),
            ('deposit', (561, 'acc2', 204), 511),
            ('create_account', (581, 'acc1'), True),
            ('transfer', (600, 'bob', 'acc10', 7), None),
            ('cancel_payment', (628, 'alice', 'payment1'), False),
            ('create_account', (658, 'acc2'), False),
            ('create_account', (673, 'acc1'), False),
            ('schedule_payment', (692, 'bob', 693, 30), None),
            ('transfer', (696, 'acc1', 'alice', 317), None),
            ('schedule_payment', (697, 'acc1', 7, 104), 'payment7'),
            ('schedule_payment', (713, 'bob', 335, 43), None),
            ('deposit', (730, 'acc10', 101), 336),
            ('transfer', (741, 'alice', 'acc10', 208), 159),
            ('create_account', (769, 'acc2'), False),
            ('deposit', (796, 'acc1', 178), 178),
            ('transfer', (810, 'acc2', 'alice', 558), None),
            ('transfer', (825, 'acc2', 'acc1', 24), 487),
            ('create_account', (826, 'acc10'), False),
            ('transfer', (832, 'acc10', 'acc2', 314), 230),
            ('schedule_payment', (852, 'acc1', 460, 64), 'payment8'),
            ('transfer', (872, 'acc10', 'acc10', 230), None),
            ('create_account', (897, 'acc2'), False),
            ('cancel_payment', (910, 'acc10', 'payment2'), False),
            ('schedule_payment', (914, 'acc2', 393, 83), 'payment9'),
            ('deposit', (925, 'alice', 43), 202),
            ('deposit', (953, 'acc2', 529), 1330),
            ('schedule_payment', (959, 'alice', 770, 79), 'payment10'),
            ('schedule_payment', (962, 'alice', 799, 25), 'payment11'),
            ('schedule_payment', (969, 'alice', 726, 110), 'payment12'),
            ('deposit', (979, 'alice', 930), 1132),
            ('top_spenders', (989, 4), ['alice(1039)', 'acc10(621)', 'acc2(24)', 'acc1(7)']),
            ('schedule_payment', (1011, 'alice', 465, 103), 'payment13'),
            ('top_spenders', (1026, 2), ['alice(1039)', 'acc10(621)']),
            ('transfer', (1051, 'acc10', 'acc2', 34), 196),
            ('deposit', (1055, 'alice', 338), 671),
            ('cancel_payment', (1071, 'alice', 'payment5'), False),
        ])

    def test_level_3_case_09_randomized_sequence_34(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('create_account', (17, 'acc10'), True),
            ('create_account', (36, 'acc1'), True),
            ('create_account', (63, 'acc2'), True),
            ('create_account', (92, 'alice'), True),
            ('cancel_payment', (104, 'acc1', 'payment1'), False),
            ('transfer', (114, 'bob', 'bob', 159), None),
            ('deposit', (118, 'bob', 2), None),
            ('deposit', (143, 'bob', 89), None),
            ('create_account', (169, 'acc10'), False),
            ('transfer', (193, 'acc1', 'alice', 171), None),
            ('schedule_payment', (212, 'acc10', 391, 38), 'payment1'),
            ('deposit', (223, 'alice', 549), 549),
            ('top_spenders', (229, 5), ['acc1(0)', 'acc10(0)', 'acc2(0)', 'alice(0)']),
            ('transfer', (242, 'acc2', 'acc2', 115), None),
            ('schedule_payment', (261, 'acc1', 456, 104), 'payment2'),
            ('transfer', (270, 'bob', 'acc10', 203), None),
            ('deposit', (296, 'acc10', 462), 462),
            ('cancel_payment', (324, 'bob', 'payment3'), False),
            ('cancel_payment', (351, 'alice', 'payment2'), False),
            ('deposit', (363, 'acc10', 144), 606),
            ('deposit', (371, 'acc10', 71), 677),
            ('deposit', (401, 'acc1', 599), 599),
            ('deposit', (418, 'acc2', 418), 418),
            ('deposit', (446, 'bob', 941), None),
            ('schedule_payment', (475, 'acc10', 625, 96), 'payment3'),
            ('schedule_payment', (502, 'acc1', 752, 10), 'payment4'),
            ('transfer', (504, 'acc10', 'acc2', 191), 486),
            ('transfer', (528, 'alice', 'acc10', 679), None),
            ('create_account', (537, 'bob'), True),
            ('deposit', (558, 'bob', 807), 807),
            ('deposit', (560, 'acc1', 514), 1113),
            ('cancel_payment', (569, 'bob', 'payment4'), False),
            ('deposit', (594, 'acc2', 480), 1089),
            ('deposit', (624, 'acc10', 756), 1242),
            ('transfer', (651, 'acc2', 'acc1', 476), 613),
            ('top_spenders', (662, 2), ['acc2(476)', 'acc10(191)']),
            ('schedule_payment', (686, 'bob', 619, 95), 'payment5'),
            ('transfer', (705, 'alice', 'acc1', 417), 132),
            ('transfer', (732, 'alice', 'alice', 174), None),
            ('create_account', (737, 'alice'), False),
            ('deposit', (754, 'acc2', 853), 1466),
            ('transfer', (771, 'acc2', 'alice', 594), 872),
            ('deposit', (794, 'acc10', 772), 2014),
            ('top_spenders', (812, 5), ['acc2(1070)', 'bob(619)', 'alice(417)', 'acc10(191)', 'acc1(0)']),
            ('deposit', (820, 'bob', 651), 839),
            ('schedule_payment', (830, 'acc10', 123, 1), 'payment6'),
            ('transfer', (855, 'alice', 'bob', 310), 416),
            ('transfer', (863, 'bob', 'acc10', 111), 1038),
            ('transfer', (893, 'acc10', 'acc10', 699), None),
            ('create_account', (914, 'acc10'), False),
            ('transfer', (920, 'alice', 'acc1', 9), 407),
            ('schedule_payment', (923, 'bob', 619, 111), 'payment7'),
            ('transfer', (943, 'acc1', 'bob', 268), 1747),
            ('cancel_payment', (971, 'bob', 'payment1'), False),
            ('schedule_payment', (977, 'alice', 653, 13), 'payment8'),
            ('top_spenders', (992, 5), ['acc2(1070)', 'alice(736)', 'bob(730)', 'acc10(314)', 'acc1(268)']),
            ('create_account', (998, 'bob'), False),
            ('schedule_payment', (1026, 'alice', 794, 45), 'payment9'),
            ('deposit', (1033, 'acc1', 795), 2542),
            ('transfer', (1048, 'acc2', 'acc2', 75), None),
            ('top_spenders', (1071, 0), []),
            ('cancel_payment', (1093, 'acc10', 'payment6'), False),
            ('deposit', (1101, 'acc10', 380), 2382),
            ('schedule_payment', (1129, 'acc2', 311, 72), 'payment10'),
            ('transfer', (1148, 'bob', 'bob', 634), None),
            ('deposit', (1174, 'alice', 241), 648),
            ('create_account', (1177, 'acc2'), False),
            ('transfer', (1185, 'alice', 'alice', 115), None),
            ('cancel_payment', (1207, 'bob', 'payment8'), False),
            ('schedule_payment', (1213, 'acc10', 137, 86), 'payment11'),
        ])


if __name__ == "__main__":
    unittest.main()
