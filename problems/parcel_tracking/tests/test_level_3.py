"""
Level 3 tests for Parcel Tracking System.

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


class TestLevel3(unittest.TestCase):
    def setUp(self):
        self.impl = ParcelTrackingSystemImpl()

    def test_level_3_case_01_example_from_spec(self):
        """The first Level 3 example table."""
        run_steps(self, self.impl, [
            ('set_tag_with_hold', ('parcel1', 'status', 'held', 100, 50), ANY),
            ('get_tag_at', ('parcel1', 'status', 120), 'held'),
            ('get_tag_at', ('parcel1', 'status', 150), None),
            ('get_tag_at', ('parcel1', 'status', 180), None),
        ])

    def test_level_3_case_02_example_remove_tag_at(self):
        """The remove_tag_at example table."""
        run_steps(self, self.impl, [
            ('set_tag_with_hold', ('parcel2', 'status', 'held', 200, 40), ANY),
            ('set_tag_at', ('parcel2', 'fragile', 'yes', 210), ANY),
            ('remove_tag_at', ('parcel2', 'fragile', 220), True),
            ('remove_tag_at', ('parcel2', 'fragile', 225), False),
            ('remove_tag_at', ('parcel2', 'status', 240), False),
            ('list_tags_at', ('parcel2', 240), []),
        ])

    def test_level_3_case_03_ttl_boundary(self):
        run_steps(self, self.impl, [
            ('set_tag_with_hold', ('p', 't', 'v', 10, 5), ANY),
            ('get_tag_at', ('p', 't', 14), 'v'),
            ('get_tag_at', ('p', 't', 15), None),
        ])

    def test_level_3_case_04_ttl_zero_never_expires(self):
        run_steps(self, self.impl, [
            ('set_tag_with_hold', ('p', 't', 'v', 1, 0), ANY),
            ('get_tag_at', ('p', 't', 2), 'v'),
            ('get_tag_at', ('p', 't', 1000000), 'v'),
            ('list_tags_at', ('p', 2000000), ['t(v)']),
        ])

    def test_level_3_case_05_set_tag_at_never_expires(self):
        run_steps(self, self.impl, [
            ('set_tag_at', ('p', 't', 'v', 5), ANY),
            ('get_tag_at', ('p', 't', 5), 'v'),
            ('get_tag_at', ('p', 't', 1000000000), 'v'),
        ])

    def test_level_3_case_06_set_tag_at_makes_tag_permanent_again(self):
        run_steps(self, self.impl, [
            ('set_tag_with_hold', ('p', 't', 'v1', 1, 3), ANY),
            ('set_tag_at', ('p', 't', 'v2', 2), ANY),
            ('get_tag_at', ('p', 't', 1000), 'v2'),
        ])

    def test_level_3_case_07_overwrite_hold_replaces_expiration(self):
        run_steps(self, self.impl, [
            ('set_tag_with_hold', ('p', 't', 'a', 1, 100), ANY),
            ('set_tag_with_hold', ('p', 't', 'b', 5, 3), ANY),
            ('get_tag_at', ('p', 't', 7), 'b'),
            ('get_tag_at', ('p', 't', 8), None),
        ])

    def test_level_3_case_08_expired_tag_can_be_set_again(self):
        run_steps(self, self.impl, [
            ('set_tag_with_hold', ('p', 't', 'old', 1, 1), ANY),
            ('get_tag_at', ('p', 't', 2), None),
            ('set_tag_with_hold', ('p', 't', 'new', 3, 4), ANY),
            ('get_tag_at', ('p', 't', 6), 'new'),
            ('remove_tag_at', ('p', 't', 7), False),
        ])

    def test_level_3_case_09_remove_tag_at_last_valid_moment(self):
        run_steps(self, self.impl, [
            ('set_tag_with_hold', ('p', 't', 'v', 1, 10), ANY),
            ('remove_tag_at', ('p', 't', 10), True),
            ('get_tag_at', ('p', 't', 10), None),
        ])

    def test_level_3_case_10_remove_tag_at_first_expired_moment(self):
        run_steps(self, self.impl, [
            ('set_tag_with_hold', ('p', 't', 'v', 1, 10), ANY),
            ('remove_tag_at', ('p', 't', 11), False),
            ('remove_tag_at', ('p', 't', 12), False),
        ])

    def test_level_3_case_11_remove_tag_at_unknown_parcel_or_tag(self):
        run_steps(self, self.impl, [
            ('remove_tag_at', ('nobody', 't', 1), False),
            ('set_tag_at', ('p', 'a', '1', 2), ANY),
            ('remove_tag_at', ('p', 'b', 3), False),
            ('remove_tag_at', ('p', 'a', 4), True),
            ('remove_tag_at', ('p', 'a', 5), False),
            ('get_tag_at', ('nobody', 't', 6), None),
        ])

    def test_level_3_case_12_remove_before_expiry_then_nothing_listed(self):
        run_steps(self, self.impl, [
            ('set_tag_with_hold', ('p', 't', 'v', 1, 100), ANY),
            ('remove_tag_at', ('p', 't', 50), True),
            ('get_tag_at', ('p', 't', 51), None),
            ('list_tags_at', ('p', 52), []),
        ])

    def test_level_3_case_13_list_mixes_live_and_expired(self):
        run_steps(self, self.impl, [
            ('set_tag_at', ('p', 'c', '3', 1), ANY),
            ('set_tag_with_hold', ('p', 'a', '1', 2, 5), ANY),
            ('set_tag_with_hold', ('p', 'b', '2', 3, 10), ANY),
            ('list_tags_at', ('p', 6), ['a(1)', 'b(2)', 'c(3)']),
            ('list_tags_at', ('p', 7), ['b(2)', 'c(3)']),
            ('list_tags_by_prefix_at', ('p', 'b', 13), []),
            ('list_tags_at', ('p', 13), ['c(3)']),
        ])

    def test_level_3_case_14_list_by_prefix_at(self):
        run_steps(self, self.impl, [
            ('set_tag_with_hold', ('p', 'box', '1', 1, 5), ANY),
            ('set_tag_at', ('p', 'boy', '2', 2), ANY),
            ('set_tag_at', ('p', 'cat', '3', 3), ANY),
            ('list_tags_by_prefix_at', ('p', 'bo', 5), ['box(1)', 'boy(2)']),
            ('list_tags_by_prefix_at', ('p', 'bo', 6), ['boy(2)']),
            ('list_tags_by_prefix_at', ('p', 'ca', 6), ['cat(3)']),
            ('list_tags_by_prefix_at', ('p', 'z', 6), []),
        ])

    def test_level_3_case_15_equal_timestamps_are_allowed(self):
        """Timestamps are non-decreasing, so several operations can share one."""
        run_steps(self, self.impl, [
            ('set_tag_at', ('p', 'a', '1', 5), ANY),
            ('get_tag_at', ('p', 'a', 5), '1'),
            ('set_tag_with_hold', ('p', 'b', '2', 5, 3), ANY),
            ('list_tags_at', ('p', 5), ['a(1)', 'b(2)']),
            ('get_tag_at', ('p', 'b', 7), '2'),
            ('get_tag_at', ('p', 'b', 8), None),
        ])

    def test_level_3_case_16_parcel_with_only_expired_tags_lists_nothing(self):
        run_steps(self, self.impl, [
            ('set_tag_with_hold', ('p', 'a', '1', 1, 2), ANY),
            ('set_tag_with_hold', ('p', 'b', '2', 1, 3), ANY),
            ('list_tags_at', ('p', 3), ['b(2)']),
            ('list_tags_at', ('p', 4), []),
        ])

    def test_level_3_case_17_parcels_expire_independently(self):
        run_steps(self, self.impl, [
            ('set_tag_with_hold', ('a', 't', '1', 1, 4), ANY),
            ('set_tag_with_hold', ('b', 't', '2', 2, 4), ANY),
            ('get_tag_at', ('a', 't', 5), None),
            ('get_tag_at', ('b', 't', 5), '2'),
            ('get_tag_at', ('b', 't', 6), None),
        ])

    def test_level_3_case_18_randomized_sequence_41(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('set_tag_with_hold', ('P1', 'B', '73', 3, 8), ANY),
            ('get_tag_at', ('P2', 'c', 5), None),
            ('set_tag_at', ('P1', 'c', '2', 9), ANY),
            ('list_tags_by_prefix_at', ('P1', 'b', 12), []),
            ('set_tag_with_hold', ('P3', 'ba', '74', 13, 0), ANY),
            ('list_tags_at', ('P1', 13), ['c(2)']),
            ('list_tags_at', ('P1', 15), ['c(2)']),
            ('remove_tag_at', ('P1', 'ba', 17), False),
            ('set_tag_at', ('P1', 'c', '22', 17), ANY),
            ('set_tag_with_hold', ('P1', 'ba', '3', 17, 5), ANY),
            ('set_tag_at', ('P1', 'b', '51', 21), ANY),
            ('set_tag_at', ('P1', 'B', '2', 22), ANY),
            ('list_tags_at', ('P1', 25), ['B(2)', 'b(51)', 'c(22)']),
            ('set_tag_at', ('P2', 'c', '51', 25), ANY),
            ('get_tag_at', ('P2', 'ba', 28), None),
            ('list_tags_by_prefix_at', ('P3', 'b', 28), ['ba(74)']),
            ('set_tag_at', ('P1', 'c', '5', 29), ANY),
            ('list_tags_by_prefix_at', ('P3', 'B', 29), []),
            ('get_tag_at', ('P2', 'ba', 29), None),
            ('list_tags_by_prefix_at', ('P1', 'B', 29), ['B(2)']),
            ('remove_tag_at', ('P3', 'c', 31), False),
            ('list_tags_at', ('P1', 34), ['B(2)', 'b(51)', 'c(5)']),
            ('get_tag_at', ('P3', 'ab', 36), None),
            ('set_tag_with_hold', ('P3', 'b', '79', 38, 3), ANY),
            ('list_tags_at', ('P3', 40), ['b(79)', 'ba(74)']),
            ('get_tag_at', ('P1', 'a', 41), None),
            ('set_tag_at', ('P3', 'ab', '8', 42), ANY),
            ('get_tag_at', ('P3', 'ab', 43), '8'),
            ('set_tag_with_hold', ('P1', 'B', '86', 46, 8), ANY),
            ('list_tags_at', ('P2', 46), ['c(51)']),
            ('get_tag_at', ('P2', 'B', 47), None),
            ('list_tags_by_prefix_at', ('P2', 'a', 49), []),
            ('remove_tag_at', ('P1', 'c', 53), True),
            ('get_tag_at', ('P3', 'ab', 54), '8'),
            ('remove_tag_at', ('P1', 'a', 57), False),
            ('remove_tag_at', ('P3', 'b', 61), False),
            ('remove_tag_at', ('P2', 'b', 62), False),
            ('set_tag_with_hold', ('P2', 'ba', '29', 63, 12), ANY),
            ('list_tags_at', ('P2', 63), ['ba(29)', 'c(51)']),
            ('set_tag_with_hold', ('P2', 'B', '88', 67, 12), ANY),
            ('set_tag_at', ('P2', 'ba', '56', 68), ANY),
            ('get_tag_at', ('P2', 'b', 69), None),
            ('set_tag_with_hold', ('P2', 'ba', '48', 69, 0), ANY),
            ('list_tags_at', ('P3', 73), ['ab(8)', 'ba(74)']),
            ('set_tag_at', ('P3', 'ab', '52', 77), ANY),
            ('set_tag_with_hold', ('P2', 'ba', '22', 80, 3), ANY),
            ('set_tag_with_hold', ('P3', 'ba', '51', 80, 1), ANY),
            ('remove_tag_at', ('P3', 'B', 80), False),
            ('set_tag_with_hold', ('P2', 'ba', '3', 80, 5), ANY),
            ('remove_tag_at', ('P2', 'c', 84), True),
            ('set_tag_at', ('P2', 'ba', '65', 85), ANY),
            ('get_tag_at', ('P3', 'ba', 86), None),
            ('set_tag_with_hold', ('P1', 'b', '62', 86, 0), ANY),
            ('set_tag_at', ('P2', 'a', '38', 89), ANY),
            ('list_tags_at', ('P3', 92), ['ab(52)']),
            ('list_tags_at', ('P2', 95), ['a(38)', 'ba(65)']),
            ('set_tag_at', ('P2', 'B', '44', 96), ANY),
            ('list_tags_at', ('P1', 97), ['b(62)']),
            ('list_tags_by_prefix_at', ('P1', 'b', 98), ['b(62)']),
            ('list_tags_by_prefix_at', ('P2', '', 100), ['B(44)', 'a(38)', 'ba(65)']),
            ('set_tag_at', ('P2', 'c', '15', 101), ANY),
            ('list_tags_by_prefix_at', ('P3', 'b', 101), []),
            ('list_tags_by_prefix_at', ('P2', 'B', 103), ['B(44)']),
            ('remove_tag_at', ('P3', 'c', 106), False),
            ('get_tag_at', ('P2', 'ba', 110), '65'),
            ('list_tags_by_prefix_at', ('P1', 'b', 111), ['b(62)']),
            ('set_tag_at', ('P3', 'b', '36', 115), ANY),
            ('set_tag_with_hold', ('P2', 'b', '36', 117, 0), ANY),
            ('list_tags_at', ('P3', 117), ['ab(52)', 'b(36)']),
            ('set_tag_with_hold', ('P3', 'ba', '96', 118, 8), ANY),
        ])

    def test_level_3_case_19_randomized_sequence_42(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('set_tag_at', ('P2', 'ab', '28', 0), ANY),
            ('remove_tag_at', ('P3', 'c', 1), False),
            ('set_tag_at', ('P2', 'a', '3', 5), ANY),
            ('set_tag_with_hold', ('P3', 'ba', '3', 5, 5), ANY),
            ('remove_tag_at', ('P3', 'ba', 6), True),
            ('set_tag_with_hold', ('P3', 'b', '0', 9, 12), ANY),
            ('remove_tag_at', ('P2', 'b', 10), False),
            ('set_tag_with_hold', ('P2', 'a', '11', 11, 3), ANY),
            ('set_tag_with_hold', ('P2', 'ba', '33', 11, 12), ANY),
            ('remove_tag_at', ('P3', 'a', 11), False),
            ('set_tag_at', ('P2', 'c', '79', 14), ANY),
            ('get_tag_at', ('P3', 'a', 16), None),
            ('remove_tag_at', ('P2', 'a', 16), False),
            ('list_tags_at', ('P2', 17), ['ab(28)', 'ba(33)', 'c(79)']),
            ('remove_tag_at', ('P2', 'ab', 20), True),
            ('set_tag_with_hold', ('P3', 'b', '89', 22, 8), ANY),
            ('get_tag_at', ('P1', 'ba', 22), None),
            ('set_tag_at', ('P2', 'b', '81', 23), ANY),
            ('set_tag_with_hold', ('P2', 'a', '29', 27, 12), ANY),
            ('list_tags_at', ('P2', 27), ['a(29)', 'b(81)', 'c(79)']),
            ('set_tag_with_hold', ('P3', 'c', '40', 27, 1), ANY),
            ('set_tag_with_hold', ('P3', 'B', '18', 30, 2), ANY),
            ('set_tag_with_hold', ('P3', 'ba', '33', 31, 8), ANY),
            ('set_tag_with_hold', ('P3', 'B', '46', 35, 1), ANY),
            ('get_tag_at', ('P1', 'a', 36), None),
            ('set_tag_at', ('P1', 'c', '54', 36), ANY),
            ('set_tag_at', ('P2', 'ba', '59', 40), ANY),
            ('set_tag_with_hold', ('P3', 'a', '87', 44, 8), ANY),
            ('remove_tag_at', ('P3', 'b', 44), False),
            ('set_tag_at', ('P2', 'ab', '58', 46), ANY),
            ('list_tags_by_prefix_at', ('P3', 'a', 46), ['a(87)']),
            ('list_tags_by_prefix_at', ('P3', 'a', 50), ['a(87)']),
            ('set_tag_with_hold', ('P1', 'ba', '99', 51, 5), ANY),
            ('get_tag_at', ('P2', 'a', 51), None),
            ('list_tags_by_prefix_at', ('P2', '', 51), ['ab(58)', 'b(81)', 'ba(59)', 'c(79)']),
            ('list_tags_by_prefix_at', ('P1', 'B', 52), []),
            ('list_tags_by_prefix_at', ('P3', 'a', 52), []),
            ('list_tags_by_prefix_at', ('P1', 'B', 55), []),
            ('list_tags_by_prefix_at', ('P3', 'a', 56), []),
            ('set_tag_with_hold', ('P3', 'c', '47', 58, 3), ANY),
            ('get_tag_at', ('P1', 'ab', 62), None),
            ('set_tag_with_hold', ('P3', 'ba', '29', 62, 5), ANY),
            ('set_tag_at', ('P3', 'c', '7', 63), ANY),
            ('set_tag_at', ('P1', 'b', '9', 64), ANY),
            ('set_tag_with_hold', ('P3', 'B', '27', 68, 5), ANY),
            ('remove_tag_at', ('P3', 'ba', 69), False),
            ('set_tag_with_hold', ('P2', 'B', '24', 72, 0), ANY),
            ('remove_tag_at', ('P2', 'B', 72), True),
            ('get_tag_at', ('P3', 'a', 75), None),
            ('set_tag_at', ('P3', 'b', '13', 75), ANY),
            ('set_tag_with_hold', ('P3', 'B', '17', 76, 3), ANY),
            ('set_tag_with_hold', ('P1', 'a', '56', 77, 12), ANY),
            ('set_tag_at', ('P3', 'ba', '1', 81), ANY),
            ('list_tags_by_prefix_at', ('P1', 'B', 81), []),
            ('get_tag_at', ('P2', 'a', 84), None),
            ('set_tag_with_hold', ('P2', 'b', '58', 85, 2), ANY),
            ('remove_tag_at', ('P3', 'ba', 88), True),
            ('set_tag_at', ('P2', 'ab', '7', 91), ANY),
            ('remove_tag_at', ('P1', 'c', 95), True),
            ('set_tag_at', ('P3', 'B', '64', 97), ANY),
            ('set_tag_at', ('P3', 'a', '23', 101), ANY),
            ('get_tag_at', ('P3', 'ab', 101), None),
            ('set_tag_at', ('P3', 'ab', '74', 104), ANY),
            ('set_tag_at', ('P1', 'B', '84', 108), ANY),
            ('get_tag_at', ('P2', 'b', 112), None),
            ('remove_tag_at', ('P2', 'ab', 113), True),
            ('set_tag_with_hold', ('P3', 'c', '38', 115, 3), ANY),
            ('list_tags_by_prefix_at', ('P1', 'B', 117), ['B(84)']),
            ('list_tags_by_prefix_at', ('P1', 'a', 121), []),
            ('set_tag_with_hold', ('P2', 'a', '31', 125, 2), ANY),
        ])


if __name__ == "__main__":
    unittest.main()
