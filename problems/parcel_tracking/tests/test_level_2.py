"""
Level 2 tests for Parcel Tracking System.

Each test replays a sequence of calls on a fresh ParcelTrackingSystemImpl() and checks
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

from parcel_tracking_system import ParcelTrackingSystemImpl

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
        self.impl = ParcelTrackingSystemImpl()

    def test_level_2_case_01_example_from_spec(self):
        """The Level 2 example table."""
        run_steps(self, self.impl, [
            ('set_tag', ('parcel1', 'city', 'London'), ANY),
            ('set_tag', ('parcel1', 'carrier', 'FastShip'), ANY),
            ('set_tag', ('parcel1', 'weight', '2kg'), ANY),
            ('list_tags_by_prefix', ('parcel1', 'c'), ['carrier(FastShip)', 'city(London)']),
            ('list_tags', ('parcel1',), ['carrier(FastShip)', 'city(London)', 'weight(2kg)']),
        ])

    def test_level_2_case_02_unknown_parcel_lists_nothing(self):
        run_steps(self, self.impl, [
            ('list_tags', ('nobody',), []),
            ('list_tags_by_prefix', ('nobody', 'a'), []),
            ('set_tag', ('p', 'a', '1'), ANY),
            ('list_tags_by_prefix', ('p', 'z'), []),
        ])

    def test_level_2_case_03_lexicographic_order_is_case_sensitive(self):
        """Uppercase sorts before lowercase; '10' < '9'."""
        run_steps(self, self.impl, [
            ('set_tag', ('p', 'b', '1'), ANY),
            ('set_tag', ('p', 'B', '2'), ANY),
            ('set_tag', ('p', 'a', '3'), ANY),
            ('set_tag', ('p', '10', '4'), ANY),
            ('set_tag', ('p', '9', '5'), ANY),
            ('list_tags', ('p',), ['10(4)', '9(5)', 'B(2)', 'a(3)', 'b(1)']),
        ])

    def test_level_2_case_04_sort_by_tag_name_not_by_formatted_entry(self):
        """'a' < 'a!' by tag, but 'a!(2)' < 'a(1)' as strings."""
        run_steps(self, self.impl, [
            ('set_tag', ('p', 'a', '1'), ANY),
            ('set_tag', ('p', 'a!', '2'), ANY),
            ('list_tags', ('p',), ['a(1)', 'a!(2)']),
            ('list_tags_by_prefix', ('p', 'a'), ['a(1)', 'a!(2)']),
        ])

    def test_level_2_case_05_list_reflects_updates_and_removals(self):
        run_steps(self, self.impl, [
            ('set_tag', ('p', 'x', '1'), ANY),
            ('set_tag', ('p', 'y', '2'), ANY),
            ('set_tag', ('p', 'x', '3'), ANY),
            ('remove_tag', ('p', 'y'), True),
            ('list_tags', ('p',), ['x(3)']),
            ('remove_tag', ('p', 'x'), True),
            ('list_tags', ('p',), []),
        ])

    def test_level_2_case_06_empty_prefix_equals_list_tags(self):
        run_steps(self, self.impl, [
            ('set_tag', ('p', 'q', '1'), ANY),
            ('set_tag', ('p', 'p', '2'), ANY),
            ('list_tags_by_prefix', ('p', ''), ['p(2)', 'q(1)']),
        ])

    def test_level_2_case_07_prefix_equal_to_whole_tag_matches(self):
        run_steps(self, self.impl, [
            ('set_tag', ('p', 'ab', '1'), ANY),
            ('set_tag', ('p', 'abc', '2'), ANY),
            ('set_tag', ('p', 'a', '3'), ANY),
            ('list_tags_by_prefix', ('p', 'ab'), ['ab(1)', 'abc(2)']),
            ('list_tags_by_prefix', ('p', 'abcd'), []),
        ])

    def test_level_2_case_08_values_may_contain_parentheses(self):
        run_steps(self, self.impl, [
            ('set_tag', ('p', 'note', '(fragile)'), ANY),
            ('list_tags', ('p',), ['note((fragile))']),
        ])

    def test_level_2_case_09_parcels_listed_separately(self):
        run_steps(self, self.impl, [
            ('set_tag', ('a', 't', '1'), ANY),
            ('set_tag', ('b', 't', '2'), ANY),
            ('list_tags', ('a',), ['t(1)']),
            ('list_tags', ('b',), ['t(2)']),
        ])

    def test_level_2_case_10_randomized_sequence_31(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('set_tag', ('P1', 'B', '18'), ANY),
            ('remove_tag', ('P1', 'a'), False),
            ('remove_tag', ('P3', 'ab'), False),
            ('set_tag', ('P3', 'a', '84'), ANY),
            ('set_tag', ('P1', 'ba', '93'), ANY),
            ('get_tag', ('P2', 'ab'), None),
            ('list_tags_by_prefix', ('P1', ''), ['B(18)', 'ba(93)']),
            ('list_tags', ('P2',), []),
            ('set_tag', ('P2', 'B', '46'), ANY),
            ('remove_tag', ('P1', 'ab'), False),
            ('remove_tag', ('P2', 'ba'), False),
            ('remove_tag', ('P1', 'a'), False),
            ('list_tags', ('P2',), ['B(46)']),
            ('set_tag', ('P2', 'a', '11'), ANY),
            ('list_tags', ('P2',), ['B(46)', 'a(11)']),
            ('list_tags', ('P1',), ['B(18)', 'ba(93)']),
            ('remove_tag', ('P1', 'b'), False),
            ('remove_tag', ('P1', 'B'), True),
            ('set_tag', ('P2', 'b', '42'), ANY),
            ('remove_tag', ('P2', 'c'), False),
            ('remove_tag', ('P2', 'ab'), False),
            ('list_tags_by_prefix', ('P1', 'a'), []),
            ('remove_tag', ('P3', 'c'), False),
            ('set_tag', ('P1', 'ab', '3'), ANY),
            ('list_tags_by_prefix', ('P3', ''), ['a(84)']),
            ('remove_tag', ('P2', 'b'), True),
            ('remove_tag', ('P1', 'a'), False),
            ('get_tag', ('P2', 'B'), '46'),
            ('get_tag', ('P1', 'ba'), '93'),
            ('remove_tag', ('P2', 'a'), True),
            ('list_tags_by_prefix', ('P3', 'a'), ['a(84)']),
            ('set_tag', ('P1', 'c', '19'), ANY),
            ('get_tag', ('P2', 'ba'), None),
            ('list_tags', ('P2',), ['B(46)']),
            ('list_tags_by_prefix', ('P2', 'x'), []),
            ('set_tag', ('P1', 'B', '17'), ANY),
            ('list_tags', ('P3',), ['a(84)']),
            ('get_tag', ('P1', 'b'), None),
            ('get_tag', ('P2', 'b'), None),
            ('set_tag', ('P1', 'B', '74'), ANY),
            ('set_tag', ('P1', 'a', '16'), ANY),
            ('set_tag', ('P3', 'a', '78'), ANY),
            ('list_tags_by_prefix', ('P1', 'a'), ['a(16)', 'ab(3)']),
            ('remove_tag', ('P3', 'c'), False),
            ('get_tag', ('P3', 'ba'), None),
            ('get_tag', ('P3', 'ab'), None),
            ('remove_tag', ('P2', 'b'), False),
            ('remove_tag', ('P2', 'b'), False),
            ('set_tag', ('P1', 'ba', '44'), ANY),
            ('list_tags', ('P2',), ['B(46)']),
        ])

    def test_level_2_case_11_randomized_sequence_32(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('set_tag', ('P1', 'ab', '38'), ANY),
            ('remove_tag', ('P1', 'B'), False),
            ('set_tag', ('P1', 'a', '41'), ANY),
            ('get_tag', ('P1', 'ba'), None),
            ('remove_tag', ('P2', 'b'), False),
            ('remove_tag', ('P3', 'ab'), False),
            ('get_tag', ('P2', 'c'), None),
            ('list_tags', ('P1',), ['a(41)', 'ab(38)']),
            ('list_tags_by_prefix', ('P1', ''), ['a(41)', 'ab(38)']),
            ('get_tag', ('P1', 'ba'), None),
            ('set_tag', ('P1', 'B', '2'), ANY),
            ('get_tag', ('P1', 'ba'), None),
            ('get_tag', ('P1', 'B'), '2'),
            ('set_tag', ('P2', 'ab', '68'), ANY),
            ('list_tags', ('P3',), []),
            ('remove_tag', ('P3', 'a'), False),
            ('list_tags', ('P3',), []),
            ('set_tag', ('P2', 'a', '31'), ANY),
            ('remove_tag', ('P2', 'B'), False),
            ('remove_tag', ('P2', 'a'), True),
            ('list_tags', ('P2',), ['ab(68)']),
            ('remove_tag', ('P1', 'a'), True),
            ('set_tag', ('P2', 'a', '70'), ANY),
            ('set_tag', ('P2', 'a', '24'), ANY),
            ('remove_tag', ('P2', 'a'), True),
            ('get_tag', ('P3', 'c'), None),
            ('set_tag', ('P2', 'B', '61'), ANY),
            ('list_tags_by_prefix', ('P1', 'b'), []),
            ('get_tag', ('P3', 'ab'), None),
            ('set_tag', ('P2', 'ba', '92'), ANY),
            ('get_tag', ('P3', 'ab'), None),
            ('remove_tag', ('P2', 'c'), False),
            ('get_tag', ('P3', 'ab'), None),
            ('list_tags_by_prefix', ('P2', ''), ['B(61)', 'ab(68)', 'ba(92)']),
            ('list_tags_by_prefix', ('P3', 'b'), []),
            ('list_tags', ('P2',), ['B(61)', 'ab(68)', 'ba(92)']),
            ('get_tag', ('P1', 'b'), None),
            ('get_tag', ('P2', 'b'), None),
            ('set_tag', ('P3', 'ba', '99'), ANY),
            ('set_tag', ('P3', 'ba', '33'), ANY),
            ('get_tag', ('P2', 'B'), '61'),
            ('set_tag', ('P1', 'ba', '23'), ANY),
            ('list_tags_by_prefix', ('P1', 'a'), ['ab(38)']),
            ('remove_tag', ('P2', 'B'), True),
            ('set_tag', ('P2', 'b', '24'), ANY),
            ('list_tags_by_prefix', ('P1', 'x'), []),
            ('get_tag', ('P2', 'c'), None),
            ('list_tags_by_prefix', ('P1', 'b'), ['ba(23)']),
            ('set_tag', ('P1', 'ab', '44'), ANY),
            ('set_tag', ('P1', 'ba', '28'), ANY),
        ])


if __name__ == "__main__":
    unittest.main()
