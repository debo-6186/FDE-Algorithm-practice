"""
Level 4 tests for Banking System (scheduled payments).

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


class TestLevel4(unittest.TestCase):
    def setUp(self):
        self.impl = BankingSystemImpl()

    def test_level_4_case_01_example_from_spec(self):
        """The Level 4 example table."""
        run_steps(self, self.impl, [
            ('create_account', (1, 'alice'), True),
            ('create_account', (2, 'bob'), True),
            ('deposit', (3, 'alice', 500), 500),
            ('deposit', (4, 'bob', 800), 800),
            ('schedule_payment', (5, 'bob', 300, 10), 'payment1'),
            ('transfer', (6, 'bob', 'alice', 100), 700),
            ('merge_accounts', (7, 'alice', 'bob'), True),
            ('cancel_payment', (8, 'bob', 'payment1'), False),
            ('get_balance', (9, 'bob', 6), 700),
            ('get_balance', (10, 'alice', 6), 600),
            ('get_balance', (11, 'alice', 7), 1300),
            ('deposit', (15, 'alice', 1), 1001),
            ('top_spenders', (16, 2), ['alice(400)']),
            ('get_balance', (17, 'alice', 15), 1001),
            ('get_balance', (18, 'alice', 14), 1300),
        ])

    def test_level_4_case_02_merged_payment_can_be_canceled_by_new_owner(self):
        run_steps(self, self.impl, [
            ('create_account', (1, 'a'), True),
            ('create_account', (2, 'b'), True),
            ('deposit', (3, 'b', 50), 50),
            ('schedule_payment', (4, 'b', 50, 100), 'payment1'),
            ('merge_accounts', (5, 'a', 'b'), True),
            ('cancel_payment', (6, 'a', 'payment1'), True),
            ('deposit', (200, 'a', 1), 51),
            ('top_spenders', (201, 1), ['a(0)']),
        ])

    def test_level_4_case_03_merge_failures(self):
        run_steps(self, self.impl, [
            ('create_account', (1, 'a'), True),
            ('merge_accounts', (2, 'a', 'a'), False),
            ('merge_accounts', (3, 'a', 'b'), False),
            ('merge_accounts', (4, 'b', 'a'), False),
            ('get_balance', (5, 'a', 4), 0),
            ('get_balance', (6, 'b', 4), None),
        ])

    def test_level_4_case_04_history_records_payment_at_due_time(self):
        run_steps(self, self.impl, [
            ('create_account', (1, 'a'), True),
            ('deposit', (2, 'a', 300), 300),
            ('schedule_payment', (3, 'a', 100, 47), 'payment1'),
            ('get_balance', (500, 'a', 49), 300),
            ('get_balance', (501, 'a', 50), 200),
            ('get_balance', (502, 'a', 499), 200),
            ('get_balance', (503, 'a', 2), 300),
            ('get_balance', (504, 'a', 1), 0),
            ('get_balance', (505, 'a', 1), 0),
        ])

    def test_level_4_case_05_recreated_id_has_fresh_history(self):
        run_steps(self, self.impl, [
            ('create_account', (1, 'a'), True),
            ('create_account', (2, 'b'), True),
            ('deposit', (3, 'b', 30), 30),
            ('merge_accounts', (4, 'a', 'b'), True),
            ('create_account', (5, 'b'), True),
            ('deposit', (6, 'b', 7), 7),
            ('get_balance', (7, 'b', 3), 30),
            ('get_balance', (8, 'b', 4), None),
            ('get_balance', (9, 'b', 5), 0),
            ('get_balance', (10, 'b', 6), 7),
            ('get_balance', (11, 'a', 6), 30),
            ('top_spenders', (12, 5), ['a(0)', 'b(0)']),
        ])

    def test_level_4_case_06_outgoing_totals_are_combined(self):
        run_steps(self, self.impl, [
            ('create_account', (1, 'a'), True),
            ('create_account', (2, 'b'), True),
            ('create_account', (3, 'c'), True),
            ('deposit', (4, 'a', 100), 100),
            ('deposit', (5, 'b', 100), 100),
            ('transfer', (6, 'a', 'c', 30), 70),
            ('transfer', (7, 'b', 'c', 50), 50),
            ('top_spenders', (8, 3), ['b(50)', 'a(30)', 'c(0)']),
            ('merge_accounts', (9, 'c', 'b'), True),
            ('top_spenders', (10, 3), ['c(50)', 'a(30)']),
            ('merge_accounts', (11, 'a', 'c'), True),
            ('top_spenders', (12, 3), ['a(80)']),
            ('get_balance', (13, 'a', 12), 200),
        ])

    def test_level_4_case_07_randomized_sequence_44(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('create_account', (14, 'bob'), True),
            ('create_account', (32, 'acc1'), True),
            ('create_account', (38, 'alice'), True),
            ('transfer', (46, 'acc2', 'acc1', 583), None),
            ('deposit', (47, 'bob', 706), 706),
            ('schedule_payment', (57, 'alice', 415, 76), 'payment1'),
            ('schedule_payment', (82, 'acc10', 76, 46), None),
            ('merge_accounts', (93, 'bob', 'acc2'), False),
            ('top_spenders', (97, 0), []),
            ('get_balance', (106, 'acc1', 47), 0),
            ('transfer', (118, 'alice', 'alice', 196), None),
            ('deposit', (125, 'acc2', 796), None),
            ('create_account', (127, 'alice'), False),
            ('create_account', (150, 'acc10'), True),
            ('merge_accounts', (162, 'alice', 'bob'), True),
            ('top_spenders', (188, 3), ['acc1(0)', 'acc10(0)', 'alice(0)']),
            ('get_balance', (203, 'acc10', 31), None),
            ('create_account', (209, 'acc1'), False),
            ('cancel_payment', (228, 'bob', 'payment3'), False),
            ('get_balance', (238, 'acc10', 83), None),
            ('transfer', (242, 'acc1', 'acc2', 622), None),
            ('create_account', (265, 'alice'), False),
            ('create_account', (290, 'bob'), True),
            ('deposit', (306, 'acc2', 955), None),
            ('cancel_payment', (327, 'acc1', 'payment3'), False),
            ('transfer', (348, 'acc1', 'acc10', 77), None),
            ('transfer', (349, 'acc2', 'bob', 642), None),
            ('deposit', (371, 'acc1', 287), 287),
            ('get_balance', (387, 'acc10', 202), 0),
            ('cancel_payment', (405, 'acc1', 'payment2'), False),
            ('transfer', (421, 'alice', 'acc10', 561), 145),
            ('get_balance', (450, 'acc1', 203), 0),
            ('schedule_payment', (455, 'acc1', 453, 119), 'payment2'),
            ('schedule_payment', (468, 'alice', 281, 11), 'payment3'),
            ('schedule_payment', (497, 'acc2', 764, 36), None),
            ('top_spenders', (515, 1), ['alice(561)']),
            ('schedule_payment', (517, 'bob', 75, 63), 'payment4'),
            ('deposit', (534, 'alice', 709), 854),
            ('get_balance', (539, 'alice', 97), 0),
            ('schedule_payment', (569, 'bob', 327, 15), 'payment5'),
            ('get_balance', (580, 'acc2', 58), None),
            ('schedule_payment', (601, 'alice', 589, 49), 'payment6'),
            ('cancel_payment', (622, 'bob', 'payment8'), False),
            ('deposit', (630, 'acc2', 754), None),
            ('transfer', (631, 'acc1', 'bob', 217), 70),
            ('deposit', (651, 'acc2', 557), None),
            ('create_account', (652, 'acc1'), False),
            ('top_spenders', (665, 5), ['alice(1150)', 'acc1(217)', 'acc10(0)', 'bob(0)']),
            ('transfer', (694, 'acc2', 'acc10', 648), None),
            ('schedule_payment', (700, 'acc1', 555, 42), 'payment7'),
            ('get_balance', (719, 'bob', 32), 0),
            ('deposit', (745, 'acc2', 17), None),
            ('create_account', (751, 'bob'), False),
            ('merge_accounts', (755, 'acc2', 'alice'), False),
            ('get_balance', (778, 'alice', 449), 145),
            ('transfer', (783, 'alice', 'acc2', 676), None),
            ('top_spenders', (789, 3), ['alice(1150)', 'acc1(217)', 'acc10(0)']),
            ('get_balance', (819, 'alice', 540), 854),
            ('get_balance', (835, 'alice', 161), 0),
            ('deposit', (854, 'acc2', 492), None),
            ('schedule_payment', (883, 'acc2', 43, 45), None),
            ('deposit', (895, 'alice', 314), 579),
            ('get_balance', (897, 'bob', 783), 217),
            ('deposit', (898, 'bob', 309), 526),
            ('deposit', (899, 'acc2', 681), None),
            ('transfer', (921, 'acc10', 'alice', 510), 51),
            ('schedule_payment', (922, 'acc1', 173, 38), 'payment8'),
            ('deposit', (943, 'bob', 349), 875),
            ('schedule_payment', (970, 'acc10', 62, 22), 'payment9'),
            ('schedule_payment', (996, 'acc1', 75, 89), 'payment10'),
            ('transfer', (1006, 'acc2', 'alice', 266), None),
            ('get_balance', (1008, 'bob', 651), 217),
            ('create_account', (1034, 'acc1'), False),
            ('cancel_payment', (1052, 'bob', 'payment6'), False),
            ('schedule_payment', (1079, 'acc1', 340, 70), 'payment11'),
            ('deposit', (1094, 'bob', 499), 1374),
            ('create_account', (1095, 'alice'), False),
            ('merge_accounts', (1096, 'bob', 'acc1'), True),
            ('get_balance', (1100, 'bob', 575), 0),
            ('schedule_payment', (1118, 'alice', 605, 62), 'payment12'),
            ('schedule_payment', (1135, 'acc2', 546, 10), None),
            ('deposit', (1148, 'bob', 793), 2237),
            ('deposit', (1178, 'acc1', 262), None),
            ('transfer', (1207, 'acc2', 'bob', 352), None),
            ('schedule_payment', (1210, 'alice', 562, 90), 'payment13'),
            ('transfer', (1211, 'alice', 'acc1', 460), None),
            ('deposit', (1224, 'alice', 253), 737),
            ('deposit', (1231, 'bob', 327), 2224),
            ('transfer', (1245, 'acc10', 'acc1', 401), None),
            ('top_spenders', (1256, 4), ['alice(1755)', 'bob(557)', 'acc10(510)']),
        ])

    def test_level_4_case_08_randomized_sequence_45(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('create_account', (9, 'alice'), True),
            ('create_account', (25, 'acc10'), True),
            ('create_account', (28, 'acc10'), False),
            ('create_account', (39, 'alice'), False),
            ('deposit', (40, 'acc1', 980), None),
            ('merge_accounts', (50, 'acc1', 'bob'), False),
            ('deposit', (53, 'acc2', 217), None),
            ('cancel_payment', (81, 'alice', 'payment1'), False),
            ('transfer', (101, 'acc1', 'acc1', 177), None),
            ('deposit', (112, 'acc10', 97), 97),
            ('create_account', (126, 'acc10'), False),
            ('cancel_payment', (137, 'bob', 'payment1'), False),
            ('schedule_payment', (156, 'alice', 383, 117), 'payment1'),
            ('deposit', (186, 'acc2', 642), None),
            ('create_account', (212, 'alice'), False),
            ('schedule_payment', (235, 'acc10', 425, 27), 'payment2'),
            ('merge_accounts', (248, 'acc2', 'bob'), False),
            ('schedule_payment', (263, 'bob', 64, 50), None),
            ('top_spenders', (292, 4), ['acc10(0)', 'alice(0)']),
            ('top_spenders', (320, 6), ['acc10(0)', 'alice(0)']),
            ('transfer', (330, 'acc2', 'acc2', 11), None),
            ('transfer', (350, 'alice', 'acc1', 4), None),
            ('get_balance', (370, 'acc10', 102), 0),
            ('deposit', (385, 'acc10', 995), 1092),
            ('schedule_payment', (393, 'bob', 231, 85), None),
            ('create_account', (409, 'acc1'), True),
            ('get_balance', (429, 'alice', 50), 0),
            ('create_account', (455, 'acc1'), False),
            ('schedule_payment', (458, 'alice', 618, 102), 'payment3'),
            ('create_account', (464, 'alice'), False),
            ('merge_accounts', (492, 'alice', 'acc10'), True),
            ('cancel_payment', (505, 'alice', 'payment2'), False),
            ('top_spenders', (528, 0), []),
            ('schedule_payment', (539, 'alice', 330, 30), 'payment4'),
            ('transfer', (551, 'bob', 'acc2', 402), None),
            ('top_spenders', (581, 5), ['alice(948)', 'acc1(0)']),
            ('schedule_payment', (595, 'alice', 602, 84), 'payment5'),
            ('create_account', (617, 'bob'), True),
            ('get_balance', (625, 'acc1', 49), None),
            ('schedule_payment', (644, 'acc10', 539, 58), None),
            ('schedule_payment', (671, 'bob', 735, 7), 'payment6'),
            ('transfer', (696, 'alice', 'alice', 580), None),
            ('transfer', (698, 'alice', 'acc1', 86), 58),
            ('get_balance', (710, 'acc10', 581), None),
            ('transfer', (723, 'acc1', 'alice', 336), None),
            ('deposit', (747, 'acc1', 606), 692),
            ('cancel_payment', (767, 'alice', 'payment10'), False),
            ('cancel_payment', (786, 'bob', 'payment3'), False),
            ('cancel_payment', (807, 'acc2', 'payment2'), False),
            ('create_account', (831, 'acc2'), True),
            ('transfer', (852, 'bob', 'acc2', 639), None),
            ('cancel_payment', (871, 'alice', 'payment10'), False),
            ('get_balance', (896, 'alice', 25), 0),
            ('deposit', (900, 'acc1', 864), 1556),
            ('create_account', (916, 'alice'), False),
            ('transfer', (934, 'alice', 'bob', 272), None),
            ('deposit', (943, 'acc1', 830), 2386),
            ('get_balance', (957, 'acc2', 595), None),
            ('deposit', (981, 'acc2', 676), 676),
            ('top_spenders', (1001, 0), []),
            ('get_balance', (1004, 'bob', 899), 0),
            ('get_balance', (1011, 'acc10', 293), 97),
            ('cancel_payment', (1015, 'bob', 'payment8'), False),
            ('deposit', (1036, 'alice', 195), 253),
            ('deposit', (1049, 'acc10', 639), None),
            ('create_account', (1070, 'acc1'), False),
            ('merge_accounts', (1074, 'bob', 'alice'), True),
            ('schedule_payment', (1091, 'acc10', 375, 18), None),
            ('transfer', (1093, 'acc10', 'bob', 193), None),
            ('deposit', (1122, 'acc10', 44), None),
            ('get_balance', (1132, 'bob', 702), 0),
            ('schedule_payment', (1143, 'acc10', 101, 55), None),
            ('merge_accounts', (1149, 'acc1', 'alice'), False),
            ('cancel_payment', (1162, 'acc10', 'payment5'), False),
            ('deposit', (1189, 'alice', 378), None),
            ('cancel_payment', (1214, 'bob', 'payment8'), False),
            ('transfer', (1237, 'bob', 'bob', 391), None),
            ('top_spenders', (1242, 0), []),
            ('get_balance', (1251, 'acc10', 112), 97),
            ('create_account', (1280, 'bob'), False),
            ('schedule_payment', (1286, 'acc10', 40, 3), None),
            ('schedule_payment', (1289, 'acc1', 245, 56), 'payment7'),
            ('transfer', (1314, 'alice', 'acc2', 514), None),
            ('schedule_payment', (1331, 'acc10', 659, 64), None),
            ('create_account', (1353, 'acc2'), False),
            ('merge_accounts', (1382, 'alice', 'alice'), False),
            ('merge_accounts', (1400, 'bob', 'acc2'), True),
            ('top_spenders', (1429, 2), ['bob(1034)', 'acc1(245)']),
            ('get_balance', (1452, 'acc2', 852), 0),
            ('transfer', (1482, 'acc2', 'acc2', 669), None),
        ])

    def test_level_4_case_09_randomized_sequence_46(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('create_account', (29, 'acc1'), True),
            ('create_account', (42, 'acc1'), False),
            ('create_account', (61, 'bob'), True),
            ('get_balance', (89, 'bob', 29), None),
            ('cancel_payment', (92, 'acc1', 'payment1'), False),
            ('schedule_payment', (97, 'acc10', 338, 68), None),
            ('get_balance', (120, 'acc1', 98), 0),
            ('deposit', (132, 'alice', 851), None),
            ('top_spenders', (135, 4), ['acc1(0)', 'bob(0)']),
            ('transfer', (139, 'acc10', 'bob', 455), None),
            ('schedule_payment', (164, 'acc2', 610, 14), None),
            ('get_balance', (176, 'bob', 133), 0),
            ('transfer', (182, 'acc10', 'acc2', 118), None),
            ('deposit', (201, 'bob', 734), 734),
            ('schedule_payment', (224, 'acc10', 775, 9), None),
            ('cancel_payment', (234, 'acc10', 'payment2'), False),
            ('top_spenders', (246, 5), ['acc1(0)', 'bob(0)']),
            ('merge_accounts', (265, 'bob', 'acc2'), False),
            ('transfer', (268, 'acc10', 'acc2', 586), None),
            ('schedule_payment', (269, 'acc2', 309, 112), None),
            ('schedule_payment', (282, 'acc1', 666, 67), 'payment1'),
            ('create_account', (306, 'acc2'), True),
            ('get_balance', (318, 'acc1', 224), 0),
            ('cancel_payment', (323, 'bob', 'payment3'), False),
            ('schedule_payment', (347, 'alice', 153, 91), None),
            ('transfer', (373, 'acc10', 'alice', 136), None),
            ('create_account', (386, 'acc1'), False),
            ('get_balance', (393, 'alice', 264), None),
            ('transfer', (395, 'acc10', 'alice', 508), None),
            ('transfer', (405, 'acc1', 'acc2', 4), None),
            ('schedule_payment', (434, 'alice', 768, 35), None),
            ('schedule_payment', (436, 'bob', 63, 63), 'payment2'),
            ('cancel_payment', (459, 'acc10', 'payment7'), False),
            ('get_balance', (477, 'acc1', 92), 0),
            ('cancel_payment', (498, 'bob', 'payment4'), False),
            ('transfer', (499, 'acc10', 'acc2', 692), None),
            ('create_account', (500, 'bob'), False),
            ('schedule_payment', (524, 'alice', 623, 12), None),
            ('cancel_payment', (532, 'acc1', 'payment10'), False),
            ('cancel_payment', (544, 'acc1', 'payment7'), False),
            ('deposit', (565, 'acc1', 350), 350),
            ('deposit', (585, 'alice', 262), None),
            ('schedule_payment', (598, 'acc10', 122, 120), None),
            ('transfer', (604, 'acc10', 'acc10', 340), None),
            ('schedule_payment', (616, 'bob', 691, 83), 'payment3'),
            ('top_spenders', (619, 4), ['bob(63)', 'acc1(0)', 'acc2(0)']),
            ('schedule_payment', (628, 'bob', 426, 117), 'payment4'),
            ('cancel_payment', (644, 'alice', 'payment9'), False),
            ('deposit', (658, 'bob', 815), 1486),
            ('get_balance', (661, 'alice', 135), None),
            ('transfer', (687, 'acc10', 'bob', 684), None),
            ('deposit', (690, 'acc10', 109), None),
            ('top_spenders', (718, 6), ['bob(754)', 'acc1(0)', 'acc2(0)']),
            ('deposit', (737, 'acc10', 501), None),
            ('schedule_payment', (747, 'alice', 152, 114), None),
            ('transfer', (755, 'alice', 'acc10', 350), None),
            ('deposit', (767, 'acc10', 666), None),
            ('get_balance', (768, 'alice', 120), None),
            ('get_balance', (779, 'acc1', 500), 0),
            ('transfer', (797, 'acc1', 'acc2', 226), 124),
            ('deposit', (803, 'acc2', 894), 1120),
            ('get_balance', (828, 'acc10', 29), None),
            ('top_spenders', (839, 5), ['bob(1180)', 'acc1(226)', 'acc2(0)']),
            ('schedule_payment', (866, 'bob', 295, 83), 'payment5'),
            ('schedule_payment', (879, 'acc10', 108, 42), None),
            ('transfer', (907, 'acc10', 'acc1', 247), None),
            ('transfer', (937, 'acc1', 'acc1', 188), None),
            ('create_account', (944, 'acc10'), True),
            ('transfer', (956, 'acc10', 'acc1', 61), None),
            ('deposit', (980, 'acc10', 394), 394),
            ('create_account', (981, 'alice'), True),
            ('top_spenders', (1006, 4), ['bob(1475)', 'acc1(226)', 'acc10(0)', 'acc2(0)']),
            ('get_balance', (1019, 'alice', 908), None),
            ('top_spenders', (1029, 2), ['bob(1475)', 'acc1(226)']),
            ('create_account', (1058, 'acc10'), False),
            ('deposit', (1060, 'acc2', 329), 1449),
            ('get_balance', (1088, 'acc1', 543), 0),
            ('schedule_payment', (1090, 'acc10', 195, 56), 'payment6'),
            ('schedule_payment', (1110, 'acc10', 332, 87), 'payment7'),
            ('schedule_payment', (1122, 'alice', 370, 84), 'payment8'),
            ('get_balance', (1135, 'bob', 980), 74),
            ('schedule_payment', (1162, 'acc1', 344, 43), 'payment9'),
            ('schedule_payment', (1179, 'acc10', 722, 91), 'payment10'),
            ('transfer', (1208, 'bob', 'acc2', 157), None),
            ('get_balance', (1219, 'acc10', 1198), 199),
            ('get_balance', (1244, 'alice', 956), None),
            ('schedule_payment', (1252, 'alice', 623, 63), 'payment11'),
            ('transfer', (1282, 'alice', 'bob', 287), None),
            ('cancel_payment', (1286, 'bob', 'payment16'), False),
            ('schedule_payment', (1289, 'acc10', 432, 78), 'payment12'),
        ])


if __name__ == "__main__":
    unittest.main()
