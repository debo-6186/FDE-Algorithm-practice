"""
Level 3 tests for Banking System (cashback).

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
            ('deposit', (3, 'alice', 2000), 2000),
            ('pay', (4, 'alice', 1000), 'payment1'),
            ('pay', (5, 'bob', 10), None),
            ('pay', (6, 'carol', 10), None),
            ('pay', (100, 'alice', 500), 'payment2'),
            ('get_payment_status', (101, 'carol', 'payment1'), None),
            ('get_payment_status', (102, 'bob', 'payment1'), None),
            ('get_payment_status', (103, 'alice', 'payment3'), None),
            ('get_payment_status', (104, 'alice', 'payment1'), 'IN_PROGRESS'),
            ('top_spenders', (105, 2), ['alice(1500)', 'bob(0)']),
            ('deposit', (86400003, 'alice', 100), 600),
            ('get_payment_status', (86400004, 'alice', 'payment1'), 'CASHBACK_RECEIVED'),
            ('deposit', (86400005, 'alice', 100), 720),
            ('deposit', (86400099, 'alice', 100), 820),
            ('deposit', (86400100, 'alice', 100), 930),
            ('top_spenders', (86400101, 1), ['alice(1500)']),
        ])

    def test_level_3_case_02_cashback_rounds_down(self):
        """2% of 149 = 2.98 -> 2; 2% of 49 = 0.98 -> 0."""
        run_steps(self, self.impl, [
            ('create_account', (1, 'a'), True),
            ('deposit', (2, 'a', 1000), 1000),
            ('pay', (3, 'a', 149), 'payment1'),
            ('pay', (4, 'a', 49), 'payment2'),
            ('deposit', (5, 'a', 1), 803),
            ('deposit', (86400003, 'a', 1), 806),
            ('get_payment_status', (86400004, 'a', 'payment2'), 'CASHBACK_RECEIVED'),
            ('deposit', (86400005, 'a', 1), 807),
        ])

    def test_level_3_case_03_payment_ids_count_only_successful_payments(self):
        run_steps(self, self.impl, [
            ('create_account', (1, 'a'), True),
            ('create_account', (2, 'b'), True),
            ('pay', (3, 'a', 5), None),
            ('deposit', (4, 'b', 100), 100),
            ('pay', (5, 'b', 30), 'payment1'),
            ('pay', (6, 'x', 1), None),
            ('deposit', (7, 'a', 100), 100),
            ('pay', (8, 'a', 101), None),
            ('pay', (9, 'a', 100), 'payment2'),
            ('pay', (10, 'b', 70), 'payment3'),
            ('get_payment_status', (11, 'b', 'payment3'), 'IN_PROGRESS'),
            ('get_payment_status', (12, 'a', 'payment3'), None),
            ('get_payment_status', (13, 'b', 'payment2'), None),
        ])

    def test_level_3_case_04_cashback_applied_before_same_timestamp_operation(self):
        """A pay at the exact refund time can use the refunded money."""
        run_steps(self, self.impl, [
            ('create_account', (1, 'a'), True),
            ('deposit', (2, 'a', 100), 100),
            ('pay', (3, 'a', 100), 'payment1'),
            ('pay', (86400003, 'a', 2), 'payment2'),
            ('get_payment_status', (86400004, 'a', 'payment1'), 'CASHBACK_RECEIVED'),
            ('get_payment_status', (86400005, 'a', 'payment2'), 'IN_PROGRESS'),
            ('top_spenders', (86400006, 1), ['a(102)']),
        ])

    def test_level_3_case_05_cashback_applied_lazily_by_later_operation(self):
        """No operation at the due time: the next operation must still see the refund."""
        run_steps(self, self.impl, [
            ('create_account', (1, 'a'), True),
            ('create_account', (2, 'b'), True),
            ('deposit', (3, 'a', 5000), 5000),
            ('pay', (4, 'a', 5000), 'payment1'),
            ('transfer', (864000000, 'a', 'b', 100), 0),
            ('top_spenders', (864000001, 2), ['a(5100)', 'b(0)']),
            ('get_payment_status', (864000002, 'a', 'payment1'), 'CASHBACK_RECEIVED'),
        ])

    def test_level_3_case_06_transfer_uses_refunded_cashback(self):
        run_steps(self, self.impl, [
            ('create_account', (1, 'a'), True),
            ('create_account', (2, 'b'), True),
            ('deposit', (3, 'a', 1000), 1000),
            ('pay', (4, 'a', 1000), 'payment1'),
            ('transfer', (5, 'a', 'b', 1), None),
            ('transfer', (86400004, 'a', 'b', 20), 0),
            ('top_spenders', (86400005, 2), ['a(1020)', 'b(0)']),
        ])

    def test_level_3_case_07_status_one_ms_before_due(self):
        run_steps(self, self.impl, [
            ('create_account', (1, 'a'), True),
            ('deposit', (2, 'a', 50), 50),
            ('pay', (7, 'a', 50), 'payment1'),
            ('get_payment_status', (86400006, 'a', 'payment1'), 'IN_PROGRESS'),
            ('get_payment_status', (86400007, 'a', 'payment1'), 'CASHBACK_RECEIVED'),
        ])

    def test_level_3_case_08_randomized_sequence_31(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('create_account', (30685739, 'alice'), True),
            ('create_account', (30686094, 'acc2'), True),
            ('create_account', (30690479, 'acc2'), False),
            ('deposit', (30691623, 'acc1', 679), None),
            ('transfer', (63369998, 'alice', 'bob', 423), None),
            ('create_account', (63374857, 'acc1'), True),
            ('transfer', (63378158, 'acc2', 'acc10', 402), None),
            ('deposit', (63380178, 'acc2', 427), 427),
            ('create_account', (63384663, 'acc1'), False),
            ('deposit', (63387576, 'acc2', 857), 1284),
            ('create_account', (63390660, 'bob'), True),
            ('deposit', (63392449, 'alice', 748), 748),
            ('top_spenders', (63395158, 3), ['acc1(0)', 'acc2(0)', 'alice(0)']),
            ('deposit', (97832471, 'bob', 406), 406),
            ('get_payment_status', (97835063, 'acc1', 'payment2'), None),
            ('top_spenders', (97839650, 6), ['acc1(0)', 'acc2(0)', 'alice(0)', 'bob(0)']),
            ('deposit', (97840417, 'acc1', 944), 944),
            ('pay', (97843487, 'acc1', 686), 'payment1'),
            ('top_spenders', (97845991, 0), []),
            ('transfer', (97848727, 'acc1', 'bob', 121), 137),
            ('get_payment_status', (97849705, 'acc2', 'payment2'), None),
            ('transfer', (97850950, 'alice', 'bob', 525), 223),
            ('get_payment_status', (97854001, 'alice', 'payment1'), None),
            ('deposit', (97857978, 'bob', 710), 1762),
            ('deposit', (97858180, 'alice', 358), 581),
            ('transfer', (97858973, 'acc10', 'alice', 181), None),
            ('deposit', (97860056, 'bob', 52), 1814),
            ('pay', (97861748, 'acc10', 706), None),
            ('top_spenders', (97865475, 4), ['acc1(807)', 'alice(525)', 'acc2(0)', 'bob(0)']),
            ('transfer', (97869600, 'bob', 'acc2', 630), 1184),
            ('deposit', (97873425, 'acc10', 127), None),
            ('pay', (97876267, 'acc10', 707), None),
            ('create_account', (97877629, 'acc1'), False),
            ('deposit', (97879331, 'alice', 904), 1485),
            ('get_payment_status', (97882817, 'acc10', 'payment2'), None),
            ('pay', (97885025, 'acc1', 34), 'payment2'),
            ('deposit', (97887271, 'acc2', 446), 2360),
            ('deposit', (97890252, 'acc1', 838), 941),
            ('deposit', (97891878, 'acc10', 354), None),
            ('deposit', (97894895, 'acc2', 68), 2428),
            ('pay', (97898824, 'alice', 668), 'payment3'),
            ('transfer', (97900312, 'acc1', 'alice', 158), 783),
            ('pay', (97904194, 'acc1', 284), 'payment4'),
            ('deposit', (97906523, 'acc2', 594), 3022),
            ('deposit', (97908434, 'acc2', 867), 3889),
            ('pay', (97911054, 'bob', 725), 'payment5'),
            ('get_payment_status', (97914112, 'alice', 'payment5'), None),
            ('get_payment_status', (97918367, 'acc10', 'payment5'), None),
            ('pay', (97921628, 'bob', 227), 'payment6'),
            ('pay', (97922024, 'acc2', 723), 'payment7'),
            ('pay', (97925394, 'acc10', 280), None),
            ('create_account', (97929895, 'acc2'), False),
            ('deposit', (97933398, 'acc1', 317), 816),
            ('get_payment_status', (97933766, 'acc2', 'payment9'), None),
            ('deposit', (97938240, 'acc1', 506), 1322),
            ('deposit', (97941845, 'alice', 684), 1659),
            ('deposit', (97944622, 'acc1', 477), 1799),
            ('get_payment_status', (97945089, 'alice', 'payment6'), None),
            ('transfer', (97946746, 'acc1', 'alice', 40), 1759),
            ('transfer', (97950123, 'alice', 'acc2', 529), 1170),
            ('deposit', (97953631, 'acc10', 804), None),
            ('deposit', (127690466, 'bob', 315), 547),
            ('deposit', (127692073, 'alice', 480), 1650),
            ('transfer', (127694867, 'alice', 'acc10', 280), None),
            ('transfer', (127698310, 'acc2', 'acc2', 267), None),
            ('deposit', (127699699, 'acc1', 726), 2485),
            ('top_spenders', (127701878, 3), ['alice(1722)', 'bob(1582)', 'acc1(1323)']),
            ('create_account', (127706052, 'bob'), False),
            ('transfer', (127709958, 'alice', 'alice', 160), None),
            ('deposit', (166592525, 'acc10', 563), None),
        ])

    def test_level_3_case_09_randomized_sequence_32(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('create_account', (32383895, 'acc2'), True),
            ('create_account', (32385844, 'alice'), True),
            ('create_account', (61832610, 'acc1'), True),
            ('pay', (61835317, 'bob', 708), None),
            ('transfer', (61839158, 'acc1', 'bob', 130), None),
            ('pay', (61843135, 'acc2', 295), None),
            ('transfer', (61844788, 'acc10', 'acc1', 37), None),
            ('pay', (61845705, 'alice', 21), None),
            ('transfer', (61846019, 'acc2', 'acc2', 480), None),
            ('deposit', (61850053, 'acc10', 583), None),
            ('pay', (61850728, 'bob', 298), None),
            ('create_account', (61853428, 'alice'), False),
            ('transfer', (61855799, 'acc1', 'alice', 10), None),
            ('deposit', (61859449, 'acc1', 885), 885),
            ('deposit', (101761694, 'bob', 310), None),
            ('deposit', (101762153, 'acc1', 502), 1387),
            ('pay', (139362007, 'acc10', 504), None),
            ('top_spenders', (139364053, 4), ['acc1(0)', 'acc2(0)', 'alice(0)']),
            ('transfer', (139365900, 'bob', 'acc10', 200), None),
            ('deposit', (139370077, 'acc10', 662), None),
            ('get_payment_status', (139372107, 'alice', 'payment1'), None),
            ('top_spenders', (168191395, 6), ['acc1(0)', 'acc2(0)', 'alice(0)']),
            ('get_payment_status', (168194810, 'alice', 'payment4'), None),
            ('transfer', (202337270, 'acc10', 'acc10', 85), None),
            ('get_payment_status', (202341385, 'acc2', 'payment2'), None),
            ('deposit', (202346173, 'acc10', 387), None),
            ('create_account', (244012036, 'acc2'), False),
            ('pay', (244012432, 'acc2', 692), None),
            ('transfer', (244015069, 'acc1', 'alice', 326), 1061),
            ('deposit', (244016348, 'alice', 60), 386),
            ('create_account', (244016562, 'acc10'), True),
            ('deposit', (273964606, 'acc1', 745), 1806),
            ('deposit', (273968726, 'acc10', 771), 771),
            ('top_spenders', (273971225, 4), ['acc1(326)', 'acc10(0)', 'acc2(0)', 'alice(0)']),
            ('deposit', (273972051, 'acc1', 18), 1824),
            ('transfer', (273974660, 'bob', 'acc10', 190), None),
            ('top_spenders', (273974735, 0), []),
            ('create_account', (311337426, 'acc2'), False),
            ('pay', (351572561, 'acc2', 386), None),
            ('top_spenders', (351572997, 1), ['acc1(326)']),
            ('pay', (351574686, 'acc10', 91), 'payment1'),
            ('pay', (351576483, 'acc1', 330), 'payment2'),
            ('pay', (351581019, 'acc10', 666), 'payment3'),
            ('deposit', (351585706, 'acc10', 548), 562),
            ('transfer', (351585929, 'alice', 'acc2', 262), 124),
            ('deposit', (351588385, 'acc2', 3), 265),
            ('deposit', (351589639, 'acc2', 432), 697),
            ('get_payment_status', (351594633, 'bob', 'payment11'), None),
            ('deposit', (351595242, 'acc2', 309), 1006),
            ('transfer', (351599257, 'bob', 'acc1', 578), None),
            ('get_payment_status', (351603292, 'acc10', 'payment3'), 'IN_PROGRESS'),
            ('transfer', (351606156, 'acc10', 'alice', 617), None),
            ('top_spenders', (351606926, 0), []),
            ('top_spenders', (351611635, 4), ['acc10(757)', 'acc1(656)', 'alice(262)', 'acc2(0)']),
            ('deposit', (351612228, 'alice', 290), 414),
            ('top_spenders', (351612370, 6), ['acc10(757)', 'acc1(656)', 'alice(262)', 'acc2(0)']),
            ('create_account', (351612879, 'bob'), True),
            ('deposit', (387403471, 'acc2', 125), 1131),
            ('pay', (387404098, 'bob', 725), None),
            ('pay', (387404749, 'bob', 637), None),
            ('deposit', (387406203, 'alice', 563), 977),
            ('deposit', (387407702, 'acc2', 452), 1583),
            ('deposit', (387407900, 'acc2', 750), 2333),
            ('deposit', (387410637, 'acc2', 354), 2687),
            ('transfer', (387415185, 'acc1', 'acc10', 421), 1073),
            ('deposit', (387416999, 'acc2', 687), 3374),
            ('top_spenders', (387417996, 3), ['acc1(1077)', 'acc10(757)', 'alice(262)']),
            ('deposit', (387420807, 'acc1', 240), 1313),
            ('create_account', (387423454, 'bob'), False),
            ('transfer', (387424118, 'acc2', 'acc1', 31), 3343),
        ])


if __name__ == "__main__":
    unittest.main()
