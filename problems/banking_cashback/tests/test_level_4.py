"""
Level 4 tests for Banking System (cashback).

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
            ('deposit', (3, 'alice', 2000), 2000),
            ('deposit', (4, 'bob', 2000), 2000),
            ('pay', (5, 'alice', 500), 'payment1'),
            ('transfer', (6, 'alice', 'bob', 500), 1000),
            ('merge_accounts', (7, 'alice', 'carol'), False),
            ('merge_accounts', (8, 'alice', 'alice'), False),
            ('merge_accounts', (9, 'alice', 'bob'), True),
            ('get_balance', (10, 'alice', 9), 3500),
            ('get_balance', (11, 'bob', 8), 2500),
            ('get_balance', (12, 'bob', 9), None),
            ('get_balance', (13, 'bob', 1), None),
            ('get_payment_status', (14, 'alice', 'payment1'), 'IN_PROGRESS'),
            ('get_payment_status', (15, 'bob', 'payment1'), None),
            ('top_spenders', (16, 3), ['alice(1000)']),
            ('get_balance', (17, 'alice', 6), 1000),
            ('deposit', (86400005, 'alice', 100), 3610),
            ('get_balance', (86400006, 'alice', 86400004), 3500),
            ('get_balance', (86400007, 'alice', 86400005), 3610),
        ])

    def test_level_4_case_02_pending_cashback_follows_merge(self):
        """bob's cashback is refunded to alice; the payment is now alice's."""
        run_steps(self, self.impl, [
            ('create_account', (1, 'alice'), True),
            ('create_account', (2, 'bob'), True),
            ('deposit', (3, 'bob', 1000), 1000),
            ('pay', (4, 'bob', 1000), 'payment1'),
            ('merge_accounts', (5, 'alice', 'bob'), True),
            ('get_payment_status', (6, 'alice', 'payment1'), 'IN_PROGRESS'),
            ('get_payment_status', (7, 'bob', 'payment1'), None),
            ('deposit', (86400004, 'alice', 1), 21),
            ('get_payment_status', (86400005, 'alice', 'payment1'), 'CASHBACK_RECEIVED'),
            ('top_spenders', (86400006, 5), ['alice(1000)']),
        ])

    def test_level_4_case_03_balance_history_basics(self):
        """Balance after all operations at time_at; None before creation."""
        run_steps(self, self.impl, [
            ('create_account', (10, 'a'), True),
            ('deposit', (20, 'a', 100), 100),
            ('deposit', (30, 'a', 50), 150),
            ('get_balance', (40, 'a', 9), None),
            ('get_balance', (41, 'a', 10), 0),
            ('get_balance', (42, 'a', 19), 0),
            ('get_balance', (43, 'a', 20), 100),
            ('get_balance', (44, 'a', 29), 100),
            ('get_balance', (45, 'a', 30), 150),
            ('get_balance', (46, 'a', 45), 150),
            ('get_balance', (47, 'zzz', 45), None),
        ])

    def test_level_4_case_04_cashback_counts_at_due_time_in_history(self):
        run_steps(self, self.impl, [
            ('create_account', (1, 'a'), True),
            ('deposit', (2, 'a', 1000), 1000),
            ('pay', (3, 'a', 500), 'payment1'),
            ('get_balance', (259200000, 'a', 86400002), 500),
            ('get_balance', (259200001, 'a', 86400003), 510),
            ('get_balance', (259200002, 'a', 259200000), 510),
        ])

    def test_level_4_case_05_merge_failures_change_nothing(self):
        run_steps(self, self.impl, [
            ('create_account', (1, 'a'), True),
            ('create_account', (2, 'b'), True),
            ('deposit', (3, 'a', 10), 10),
            ('merge_accounts', (4, 'a', 'a'), False),
            ('merge_accounts', (5, 'a', 'c'), False),
            ('merge_accounts', (6, 'c', 'a'), False),
            ('get_balance', (7, 'a', 6), 10),
            ('get_balance', (8, 'b', 6), 0),
            ('top_spenders', (9, 5), ['a(0)', 'b(0)']),
        ])

    def test_level_4_case_06_merged_id_can_be_created_again(self):
        """After the merge the old id is free; the new account starts from zero."""
        run_steps(self, self.impl, [
            ('create_account', (1, 'a'), True),
            ('create_account', (2, 'b'), True),
            ('deposit', (3, 'b', 70), 70),
            ('merge_accounts', (4, 'a', 'b'), True),
            ('deposit', (5, 'b', 1), None),
            ('create_account', (6, 'b'), True),
            ('deposit', (7, 'b', 5), 5),
            ('get_balance', (8, 'b', 3), 70),
            ('get_balance', (9, 'b', 4), None),
            ('get_balance', (10, 'b', 5), None),
            ('get_balance', (11, 'b', 7), 5),
            ('get_balance', (12, 'a', 7), 70),
            ('top_spenders', (13, 2), ['a(0)', 'b(0)']),
        ])

    def test_level_4_case_07_chain_of_merges(self):
        """c -> b, then b -> a: everything ends up in a."""
        run_steps(self, self.impl, [
            ('create_account', (1, 'a'), True),
            ('create_account', (2, 'b'), True),
            ('create_account', (3, 'c'), True),
            ('deposit', (4, 'c', 300), 300),
            ('pay', (5, 'c', 100), 'payment1'),
            ('transfer', (6, 'c', 'b', 50), 150),
            ('merge_accounts', (7, 'b', 'c'), True),
            ('merge_accounts', (8, 'a', 'b'), True),
            ('get_payment_status', (9, 'a', 'payment1'), 'IN_PROGRESS'),
            ('top_spenders', (10, 3), ['a(150)']),
            ('get_balance', (11, 'a', 8), 200),
            ('get_balance', (12, 'b', 7), 200),
            ('get_balance', (13, 'c', 6), 150),
            ('deposit', (86400005, 'a', 1), 203),
            ('get_balance', (86400006, 'a', 86400005), 203),
        ])

    def test_level_4_case_08_randomized_sequence_41(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('create_account', (1891, 'acc2'), True),
            ('create_account', (5051, 'bob'), True),
            ('create_account', (7374, 'bob'), False),
            ('create_account', (12097, 'acc2'), False),
            ('transfer', (12248, 'acc2', 'acc2', 327), None),
            ('create_account', (17031, 'bob'), False),
            ('merge_accounts', (33545455, 'acc2', 'acc1'), False),
            ('deposit', (33549348, 'acc1', 127), None),
            ('pay', (64758364, 'acc2', 55), None),
            ('pay', (64760210, 'bob', 592), None),
            ('transfer', (64760681, 'acc2', 'acc1', 684), None),
            ('pay', (93921420, 'alice', 405), None),
            ('deposit', (93922124, 'alice', 969), None),
            ('top_spenders', (93925612, 4), ['acc2(0)', 'bob(0)']),
            ('pay', (122964657, 'acc10', 181), None),
            ('pay', (122965196, 'acc1', 677), None),
            ('pay', (122968582, 'acc1', 624), None),
            ('merge_accounts', (122973508, 'acc2', 'acc2'), False),
            ('pay', (122977274, 'alice', 461), None),
            ('transfer', (162993478, 'acc2', 'acc2', 284), None),
            ('get_payment_status', (162996147, 'bob', 'payment7'), None),
            ('get_payment_status', (162998562, 'acc1', 'payment4'), None),
            ('create_account', (163000314, 'acc2'), False),
            ('create_account', (163002287, 'acc2'), False),
            ('top_spenders', (163003558, 1), ['acc2(0)']),
            ('merge_accounts', (163004529, 'alice', 'bob'), False),
            ('pay', (163006111, 'alice', 403), None),
            ('merge_accounts', (163008331, 'acc1', 'acc2'), False),
            ('pay', (163009595, 'bob', 531), None),
            ('transfer', (163011046, 'acc1', 'acc1', 523), None),
            ('deposit', (163013930, 'alice', 945), None),
            ('transfer', (163016452, 'acc10', 'alice', 627), None),
            ('get_balance', (163017460, 'acc10', 163006110), None),
            ('pay', (163021487, 'acc2', 100), None),
            ('transfer', (163026355, 'alice', 'acc2', 486), None),
            ('top_spenders', (163028379, 6), ['acc2(0)', 'bob(0)']),
            ('create_account', (163032763, 'acc2'), False),
            ('transfer', (163036848, 'acc10', 'bob', 177), None),
            ('deposit', (163036982, 'bob', 527), 527),
            ('pay', (163037200, 'bob', 385), 'payment1'),
            ('merge_accounts', (205654742, 'bob', 'acc1'), False),
            ('pay', (205659048, 'alice', 744), None),
            ('transfer', (205663365, 'bob', 'acc2', 502), None),
            ('pay', (243488885, 'acc2', 379), None),
            ('create_account', (243492854, 'alice'), True),
            ('deposit', (277500378, 'alice', 826), 826),
            ('get_balance', (320314266, 'acc10', 86405051), None),
            ('transfer', (355332266, 'acc2', 'alice', 178), None),
            ('create_account', (355332999, 'acc1'), True),
            ('transfer', (355335564, 'acc1', 'acc2', 54), None),
            ('get_balance', (355336534, 'acc2', 209373507), 0),
            ('get_payment_status', (355337912, 'alice', 'payment13'), None),
            ('top_spenders', (355341223, 5), ['bob(385)', 'acc1(0)', 'acc2(0)', 'alice(0)']),
            ('pay', (355345584, 'bob', 709), None),
            ('get_payment_status', (355347599, 'acc1', 'payment13'), None),
            ('deposit', (355348034, 'acc10', 289), None),
            ('deposit', (355350429, 'acc1', 69), 69),
            ('transfer', (355355121, 'alice', 'bob', 561), 265),
            ('transfer', (355355222, 'acc2', 'acc10', 425), None),
            ('transfer', (355358910, 'acc2', 'acc1', 208), None),
            ('transfer', (394410589, 'acc2', 'alice', 432), None),
            ('pay', (394414767, 'alice', 637), None),
            ('get_payment_status', (437399934, 'alice', 'payment15'), None),
            ('get_balance', (437404441, 'acc1', 249426355), None),
            ('pay', (477648914, 'alice', 442), None),
            ('deposit', (477649193, 'bob', 660), 1370),
            ('get_balance', (520121799, 'bob', 249417459), 142),
            ('get_payment_status', (520124835, 'bob', 'payment3'), None),
            ('pay', (520129094, 'acc2', 704), None),
            ('deposit', (520130787, 'acc10', 818), None),
            ('get_payment_status', (520134821, 'acc2', 'payment17'), None),
            ('merge_accounts', (520135035, 'acc1', 'acc1'), False),
            ('get_balance', (520137237, 'acc10', 437404441), None),
            ('deposit', (520139306, 'acc10', 598), None),
            ('create_account', (557227092, 'acc1'), False),
            ('get_payment_status', (557228008, 'acc2', 'payment3'), None),
            ('transfer', (557230303, 'acc1', 'acc2', 307), None),
            ('get_payment_status', (588733893, 'acc2', 'payment15'), None),
            ('deposit', (588735635, 'acc2', 299), 299),
            ('merge_accounts', (626082733, 'alice', 'acc10'), False),
            ('get_payment_status', (626085573, 'bob', 'payment10'), None),
            ('create_account', (626086355, 'acc2'), False),
            ('top_spenders', (626090248, 3), ['alice(561)', 'bob(385)', 'acc1(0)']),
            ('deposit', (626092861, 'acc10', 85), None),
            ('transfer', (659752891, 'acc2', 'acc10', 219), None),
            ('pay', (659757112, 'bob', 540), 'payment2'),
            ('transfer', (659761967, 'acc1', 'bob', 516), None),
            ('pay', (659762779, 'acc2', 416), None),
            ('get_balance', (659767289, 'acc1', 564048914), 69),
            ('get_balance', (659770087, 'alice', 209373509), None),
        ])

    def test_level_4_case_09_randomized_sequence_42(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('create_account', (205, 'acc10'), True),
            ('create_account', (1349, 'acc1'), True),
            ('create_account', (5817, 'acc1'), False),
            ('create_account', (6078, 'acc2'), True),
            ('create_account', (11010, 'acc2'), False),
            ('transfer', (15475, 'alice', 'bob', 285), None),
            ('get_payment_status', (15529, 'acc2', 'payment2'), None),
            ('deposit', (16803, 'acc10', 105), 105),
            ('transfer', (30439434, 'acc10', 'bob', 271), None),
            ('top_spenders', (30443198, 0), []),
            ('pay', (30446161, 'acc1', 47), None),
            ('get_balance', (30448532, 'acc2', 1350), None),
            ('deposit', (30451521, 'acc10', 215), 320),
            ('pay', (30452106, 'acc2', 547), None),
            ('top_spenders', (30453445, 5), ['acc1(0)', 'acc10(0)', 'acc2(0)']),
            ('pay', (30455245, 'acc1', 235), None),
            ('transfer', (30457830, 'acc1', 'acc2', 581), None),
            ('deposit', (30460408, 'alice', 406), None),
            ('deposit', (30464167, 'acc2', 253), 253),
            ('deposit', (30468583, 'bob', 439), None),
            ('transfer', (30471855, 'acc2', 'bob', 506), None),
            ('merge_accounts', (60062336, 'acc2', 'acc2'), False),
            ('pay', (60065795, 'alice', 391), None),
            ('top_spenders', (60069630, 6), ['acc1(0)', 'acc10(0)', 'acc2(0)']),
            ('pay', (60070569, 'bob', 769), None),
            ('deposit', (60073356, 'alice', 162), None),
            ('get_balance', (60075514, 'acc2', 6077), None),
            ('pay', (60079673, 'acc2', 383), None),
            ('get_balance', (60084092, 'bob', 30468582), None),
            ('get_balance', (60085009, 'acc10', 1349), 0),
            ('create_account', (60085655, 'alice'), True),
            ('get_payment_status', (60090019, 'acc2', 'payment6'), None),
            ('deposit', (60094523, 'bob', 894), None),
            ('get_balance', (60096259, 'acc2', 30468584), 253),
            ('transfer', (60099319, 'bob', 'alice', 124), None),
            ('transfer', (60099844, 'bob', 'bob', 236), None),
            ('create_account', (60099903, 'acc1'), False),
            ('merge_accounts', (60100161, 'acc1', 'bob'), False),
            ('deposit', (60104138, 'acc2', 741), 994),
            ('pay', (60108816, 'acc2', 485), 'payment1'),
            ('deposit', (60110376, 'alice', 363), 363),
            ('get_balance', (60114202, 'acc1', 45188730), 0),
            ('transfer', (101131598, 'acc1', 'acc2', 197), None),
            ('deposit', (101135274, 'acc2', 286), 795),
            ('transfer', (101135892, 'bob', 'acc1', 52), None),
            ('merge_accounts', (101140321, 'acc1', 'acc2'), True),
            ('top_spenders', (101144300, 0), []),
            ('get_balance', (101144318, 'acc10', 30464168), 320),
            ('pay', (101148871, 'alice', 159), 'payment2'),
            ('get_balance', (101150655, 'bob', 60099319), None),
            ('create_account', (101151124, 'alice'), False),
            ('deposit', (101155475, 'bob', 83), None),
            ('pay', (101156037, 'acc2', 414), None),
            ('deposit', (139513604, 'bob', 41), None),
            ('pay', (139517039, 'bob', 536), None),
            ('deposit', (139519176, 'acc10', 245), 565),
            ('pay', (139520249, 'acc10', 469), 'payment3'),
            ('create_account', (139520844, 'bob'), True),
            ('create_account', (139521664, 'acc2'), True),
            ('get_balance', (139522750, 'acc1', 101144317), 795),
            ('pay', (139527201, 'bob', 670), None),
            ('transfer', (139531745, 'acc1', 'acc2', 271), 524),
            ('get_payment_status', (170127510, 'acc2', 'payment5'), None),
            ('pay', (170129236, 'acc2', 704), None),
            ('top_spenders', (170131399, 6), ['acc1(756)', 'acc10(469)', 'alice(159)', 'acc2(0)', 'bob(0)']),
            ('transfer', (209572926, 'acc10', 'acc1', 4), 92),
            ('pay', (209573998, 'acc10', 166), None),
            ('pay', (209578518, 'bob', 10), None),
            ('get_balance', (249971903, 'bob', 146475514), 0),
            ('transfer', (249972246, 'acc1', 'acc10', 216), 321),
            ('transfer', (249973089, 'bob', 'alice', 636), None),
            ('get_balance', (249975029, 'acc2', 146499319), 271),
            ('get_payment_status', (249977751, 'alice', 'payment8'), None),
            ('transfer', (249978637, 'acc1', 'alice', 228), 93),
            ('transfer', (249982408, 'acc2', 'acc2', 25), None),
            ('transfer', (249985673, 'acc1', 'acc10', 360), None),
            ('pay', (249988948, 'bob', 340), None),
            ('get_balance', (249989893, 'acc10', 209578518), 92),
            ('transfer', (286080663, 'acc10', 'alice', 621), None),
            ('transfer', (286081611, 'bob', 'acc2', 261), None),
            ('create_account', (322197442, 'bob'), False),
            ('transfer', (322199057, 'acc1', 'acc10', 639), None),
            ('pay', (322200078, 'acc10', 520), None),
            ('transfer', (322203424, 'acc10', 'bob', 131), 186),
            ('pay', (322206530, 'acc2', 631), None),
            ('pay', (322209857, 'acc1', 312), None),
            ('get_payment_status', (322213379, 'bob', 'payment11'), None),
            ('pay', (322217002, 'bob', 485), None),
            ('pay', (322218393, 'acc10', 528), None),
            ('deposit', (322221139, 'acc2', 689), 960),
        ])

    def test_level_4_case_10_randomized_sequence_43(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('create_account', (40480705, 'acc2'), True),
            ('create_account', (40483736, 'acc1'), True),
            ('create_account', (40487818, 'bob'), True),
            ('pay', (76542098, 'bob', 561), None),
            ('transfer', (76545654, 'acc1', 'acc1', 128), None),
            ('deposit', (76546439, 'alice', 132), None),
            ('get_balance', (76551332, 'acc10', 76542098), None),
            ('deposit', (106378276, 'acc1', 860), 860),
            ('get_balance', (106380532, 'bob', 40483736), None),
            ('top_spenders', (145628504, 2), ['acc1(0)', 'acc2(0)']),
            ('deposit', (145632099, 'acc1', 800), 1660),
            ('deposit', (145636944, 'acc2', 689), 689),
            ('pay', (145641466, 'acc10', 507), None),
            ('pay', (145644428, 'acc1', 485), 'payment1'),
            ('get_payment_status', (145649359, 'acc10', 'payment2'), None),
            ('pay', (145650622, 'acc10', 112), None),
            ('transfer', (145654102, 'acc1', 'acc2', 3), 1172),
            ('get_balance', (187732352, 'acc1', 162951332), 1172),
            ('deposit', (187735118, 'bob', 511), 511),
            ('merge_accounts', (187738856, 'alice', 'acc1'), False),
            ('pay', (187739618, 'alice', 199), None),
            ('transfer', (187744334, 'bob', 'bob', 419), None),
            ('transfer', (187747016, 'acc1', 'acc2', 551), 621),
            ('pay', (187748555, 'acc1', 686), None),
            ('deposit', (187751012, 'acc2', 796), 2039),
            ('merge_accounts', (187754156, 'alice', 'acc2'), False),
            ('create_account', (224966380, 'acc1'), False),
            ('merge_accounts', (264054993, 'bob', 'bob'), False),
            ('transfer', (264059736, 'acc2', 'acc2', 460), None),
            ('deposit', (264061003, 'acc1', 717), 1347),
            ('pay', (264065642, 'acc2', 386), 'payment2'),
            ('deposit', (264065763, 'acc1', 337), 1684),
            ('deposit', (264070173, 'bob', 156), 667),
            ('deposit', (264071809, 'acc1', 275), 1959),
            ('merge_accounts', (264074048, 'acc1', 'alice'), False),
            ('transfer', (264075214, 'acc1', 'acc2', 487), 1472),
            ('transfer', (264076446, 'alice', 'acc10', 493), None),
            ('get_balance', (264078970, 'bob', 130683288), 0),
            ('get_payment_status', (264083214, 'acc1', 'payment4'), None),
            ('pay', (264084477, 'acc1', 662), 'payment3'),
            ('pay', (303585303, 'acc2', 193), 'payment4'),
            ('create_account', (303589535, 'acc2'), False),
            ('transfer', (303593321, 'acc1', 'acc10', 470), None),
            ('top_spenders', (303595507, 6), ['acc1(2188)', 'acc2(579)', 'bob(0)']),
            ('transfer', (303598234, 'alice', 'alice', 335), None),
            ('deposit', (303599961, 'alice', 187), None),
            ('deposit', (303603521, 'bob', 301), 968),
            ('get_balance', (303603920, 'acc10', 187738856), None),
            ('top_spenders', (303608743, 2), ['acc1(2188)', 'acc2(579)']),
            ('get_balance', (303611926, 'acc2', 145644427), 689),
            ('transfer', (303615495, 'acc10', 'acc1', 158), None),
            ('transfer', (303619738, 'alice', 'bob', 450), None),
            ('top_spenders', (303624341, 0), []),
            ('top_spenders', (303628328, 2), ['acc1(2188)', 'acc2(579)']),
            ('deposit', (344557309, 'acc1', 698), 1508),
            ('top_spenders', (344560802, 2), ['acc1(2188)', 'acc2(579)']),
            ('transfer', (377808142, 'acc1', 'acc1', 570), None),
            ('create_account', (377809659, 'acc10'), True),
            ('transfer', (377810666, 'acc1', 'acc1', 650), None),
            ('get_balance', (377812461, 'acc2', 264054993), 2039),
            ('create_account', (413273049, 'acc1'), False),
            ('create_account', (442516195, 'bob'), False),
            ('deposit', (442518035, 'alice', 623), None),
            ('pay', (442519414, 'acc10', 504), None),
            ('get_balance', (442522776, 'alice', 303593322), None),
            ('transfer', (442524447, 'alice', 'acc1', 536), None),
            ('transfer', (442525714, 'bob', 'acc2', 116), 852),
            ('top_spenders', (472625053, 0), []),
            ('get_balance', (472627113, 'bob', 350470173), 968),
            ('deposit', (472627204, 'acc10', 105), 105),
            ('create_account', (472628264, 'bob'), False),
            ('get_balance', (472629199, 'acc1', 145654102), 1172),
            ('pay', (472630042, 'alice', 522), None),
            ('pay', (472632969, 'bob', 329), 'payment5'),
            ('top_spenders', (472636456, 5), ['acc1(2188)', 'acc2(579)', 'bob(445)', 'acc10(0)']),
            ('pay', (472636692, 'acc1', 21), 'payment6'),
            ('merge_accounts', (472638763, 'bob', 'acc10'), True),
            ('transfer', (508998020, 'acc1', 'alice', 310), None),
            ('create_account', (509000581, 'acc1'), False),
            ('top_spenders', (509002354, 2), ['acc1(2209)', 'acc2(579)']),
            ('transfer', (509006029, 'acc1', 'alice', 366), None),
            ('get_balance', (509007560, 'alice', 350461004), None),
            ('pay', (509012470, 'acc10', 507), None),
            ('get_balance', (509013306, 'acc10', 264054994), None),
            ('get_payment_status', (509017253, 'alice', 'payment13'), None),
            ('create_account', (509017543, 'acc1'), False),
            ('get_payment_status', (509019102, 'bob', 'payment11'), None),
            ('pay', (509023343, 'alice', 424), None),
            ('get_balance', (509025558, 'acc2', 509006028), 2073),
            ('pay', (509025633, 'bob', 177), 'payment7'),
        ])


if __name__ == "__main__":
    unittest.main()
