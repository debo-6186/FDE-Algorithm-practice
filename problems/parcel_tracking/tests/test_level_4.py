"""
Level 4 tests for Parcel Tracking System.

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


class TestLevel4(unittest.TestCase):
    def setUp(self):
        self.impl = ParcelTrackingSystemImpl()

    def test_level_4_case_01_example_from_spec(self):
        """The first Level 4 example table."""
        run_steps(self, self.impl, [
            ('set_tag_with_hold', ('parcel1', 'status', 'held', 100, 100), ANY),
            ('checkpoint', (120,), 1),
            ('checkpoint', (150,), 1),
            ('checkpoint', (200,), 0),
            ('restore_checkpoint', (250, 120), ANY),
            ('get_tag_at', ('parcel1', 'status', 300), 'held'),
            ('get_tag_at', ('parcel1', 'status', 329), 'held'),
            ('get_tag_at', ('parcel1', 'status', 330), None),
        ])

    def test_level_4_case_02_example_shift_uses_checkpoint_timestamp(self):
        """The second Level 4 example table."""
        run_steps(self, self.impl, [
            ('set_tag_with_hold', ('parcel1', 'route_east', 'active', 30, 70), ANY),
            ('checkpoint', (31,), 1),
            ('set_tag_with_hold', ('parcel1', 'route_west', 'queued', 35, 25), ANY),
            ('checkpoint', (41,), 1),
            ('restore_checkpoint', (110, 35), ANY),
            ('get_tag_at', ('parcel1', 'route_west', 115), None),
            ('get_tag_at', ('parcel1', 'route_east', 115), 'active'),
        ])

    def test_level_4_case_03_checkpoint_counts_only_alive_parcels(self):
        run_steps(self, self.impl, [
            ('set_tag_at', ('a', 't', '1', 1), ANY),
            ('set_tag_with_hold', ('b', 't', '1', 2, 3), ANY),
            ('set_tag_at', ('c', 't', '1', 3), ANY),
            ('remove_tag_at', ('c', 't', 4), True),
            ('checkpoint', (4,), 2),
            ('checkpoint', (5,), 1),
            ('checkpoint', (6,), 1),
        ])

    def test_level_4_case_04_checkpoint_with_no_parcels(self):
        run_steps(self, self.impl, [
            ('checkpoint', (1,), 0),
            ('checkpoint', (2,), 0),
        ])

    def test_level_4_case_05_restore_uses_latest_checkpoint_at_or_before(self):
        run_steps(self, self.impl, [
            ('set_tag_at', ('k', 'v', 'one', 1), ANY),
            ('checkpoint', (2,), 1),
            ('set_tag_at', ('k', 'v', 'two', 3), ANY),
            ('checkpoint', (4,), 1),
            ('set_tag_at', ('k', 'v', 'three', 5), ANY),
            ('restore_checkpoint', (6, 4), ANY),
            ('get_tag_at', ('k', 'v', 7), 'two'),
            ('restore_checkpoint', (8, 3), ANY),
            ('get_tag_at', ('k', 'v', 9), 'one'),
        ])

    def test_level_4_case_06_restore_target_between_checkpoints(self):
        """No checkpoint at exactly the target: take the latest one before it."""
        run_steps(self, self.impl, [
            ('set_tag_at', ('k', 'v', 'one', 1), ANY),
            ('checkpoint', (2,), 1),
            ('set_tag_at', ('k', 'v', 'two', 5), ANY),
            ('checkpoint', (8,), 1),
            ('restore_checkpoint', (9, 7), ANY),
            ('get_tag_at', ('k', 'v', 10), 'one'),
        ])

    def test_level_4_case_07_restore_before_first_checkpoint_has_no_effect(self):
        run_steps(self, self.impl, [
            ('set_tag_at', ('k', 'v', 'x', 1), ANY),
            ('checkpoint', (5,), 1),
            ('set_tag_at', ('k', 'w', 'y', 6), ANY),
            ('restore_checkpoint', (7, 4), ANY),
            ('list_tags_at', ('k', 8), ['v(x)', 'w(y)']),
        ])

    def test_level_4_case_08_restore_discards_later_changes(self):
        run_steps(self, self.impl, [
            ('set_tag_at', ('k', 'a', '1', 1), ANY),
            ('set_tag_at', ('k', 'b', '2', 2), ANY),
            ('checkpoint', (3,), 1),
            ('remove_tag_at', ('k', 'a', 4), True),
            ('set_tag_at', ('k', 'c', '3', 5), ANY),
            ('set_tag_at', ('z', 'z', 'z', 6), ANY),
            ('checkpoint', (7,), 2),
            ('restore_checkpoint', (8, 3), ANY),
            ('list_tags_at', ('k', 9), ['a(1)', 'b(2)']),
            ('list_tags_at', ('z', 10), []),
        ])

    def test_level_4_case_09_restore_empty_checkpoint_clears_everything(self):
        run_steps(self, self.impl, [
            ('checkpoint', (1,), 0),
            ('set_tag_at', ('k', 'a', '1', 2), ANY),
            ('restore_checkpoint', (3, 1), ANY),
            ('list_tags_at', ('k', 4), []),
        ])

    def test_level_4_case_10_permanent_tags_stay_permanent(self):
        run_steps(self, self.impl, [
            ('set_tag_at', ('k', 'p', 'perm', 1), ANY),
            ('set_tag_with_hold', ('k', 'h', 'held', 2, 5), ANY),
            ('checkpoint', (3,), 1),
            ('restore_checkpoint', (100, 3), ANY),
            ('list_tags_at', ('k', 103), ['h(held)', 'p(perm)']),
            ('list_tags_at', ('k', 104), ['p(perm)']),
            ('get_tag_at', ('k', 'p', 1000000), 'perm'),
        ])

    def test_level_4_case_11_hold_with_ttl_zero_survives_restore(self):
        run_steps(self, self.impl, [
            ('set_tag_with_hold', ('k', 'f', 'v', 1, 0), ANY),
            ('checkpoint', (2,), 1),
            ('restore_checkpoint', (1000, 2), ANY),
            ('get_tag_at', ('k', 'f', 5000), 'v'),
        ])

    def test_level_4_case_12_shift_uses_checkpoint_timestamp_not_target(self):
        """delta = timestamp - checkpoint_timestamp (500 - 20), not 500 - 49 and not 500 - 50."""
        run_steps(self, self.impl, [
            ('set_tag_with_hold', ('k', 'f', 'v', 10, 100), ANY),
            ('checkpoint', (20,), 1),
            ('checkpoint', (50,), 1),
            ('restore_checkpoint', (500, 49), ANY),
            ('get_tag_at', ('k', 'f', 589), 'v'),
            ('get_tag_at', ('k', 'f', 590), None),
        ])

    def test_level_4_case_13_restore_target_equal_to_checkpoint_timestamp(self):
        run_steps(self, self.impl, [
            ('set_tag_at', ('k', 'a', '1', 1), ANY),
            ('checkpoint', (5,), 1),
            ('set_tag_at', ('k', 'a', '2', 6), ANY),
            ('restore_checkpoint', (7, 5), ANY),
            ('get_tag_at', ('k', 'a', 8), '1'),
        ])

    def test_level_4_case_14_restore_at_checkpoint_time_shifts_by_zero(self):
        run_steps(self, self.impl, [
            ('set_tag_with_hold', ('k', 'f', 'v', 1, 9), ANY),
            ('checkpoint', (5,), 1),
            ('restore_checkpoint', (5, 5), ANY),
            ('get_tag_at', ('k', 'f', 9), 'v'),
            ('get_tag_at', ('k', 'f', 10), None),
        ])

    def test_level_4_case_15_restore_twice_from_same_checkpoint(self):
        run_steps(self, self.impl, [
            ('set_tag_with_hold', ('k', 'f', 'v', 1, 10), ANY),
            ('checkpoint', (5,), 1),
            ('restore_checkpoint', (20, 5), ANY),
            ('get_tag_at', ('k', 'f', 25), 'v'),
            ('get_tag_at', ('k', 'f', 26), None),
            ('restore_checkpoint', (30, 6), ANY),
            ('get_tag_at', ('k', 'f', 35), 'v'),
            ('get_tag_at', ('k', 'f', 36), None),
        ])

    def test_level_4_case_16_checkpoints_are_kept_after_a_restore(self):
        run_steps(self, self.impl, [
            ('set_tag_at', ('k', 'a', '1', 1), ANY),
            ('checkpoint', (2,), 1),
            ('set_tag_at', ('k', 'b', '2', 3), ANY),
            ('checkpoint', (4,), 1),
            ('restore_checkpoint', (5, 2), ANY),
            ('list_tags_at', ('k', 6), ['a(1)']),
            ('restore_checkpoint', (7, 4), ANY),
            ('list_tags_at', ('k', 8), ['a(1)', 'b(2)']),
        ])

    def test_level_4_case_17_checkpoint_excludes_expired_tags(self):
        run_steps(self, self.impl, [
            ('set_tag_with_hold', ('gone', 't', 'x', 1, 1), ANY),
            ('set_tag_with_hold', ('k', 'old', 'x', 1, 2), ANY),
            ('set_tag_at', ('k', 'keep', 'y', 2), ANY),
            ('checkpoint', (5,), 1),
            ('restore_checkpoint', (6, 5), ANY),
            ('list_tags_at', ('k', 7), ['keep(y)']),
            ('list_tags_at', ('gone', 8), []),
        ])

    def test_level_4_case_18_same_timestamp_checkpoints_latest_wins(self):
        run_steps(self, self.impl, [
            ('set_tag_at', ('k', 'a', '1', 5), ANY),
            ('checkpoint', (5,), 1),
            ('set_tag_at', ('k', 'b', '2', 5), ANY),
            ('checkpoint', (5,), 1),
            ('restore_checkpoint', (10, 5), ANY),
            ('list_tags_at', ('k', 11), ['a(1)', 'b(2)']),
        ])

    def test_level_4_case_19_overwritten_tag_returns_with_old_value_and_expiry(self):
        run_steps(self, self.impl, [
            ('set_tag_with_hold', ('k', 'f', 'v1', 1, 10), ANY),
            ('checkpoint', (2,), 1),
            ('set_tag_at', ('k', 'f', 'v2', 3), ANY),
            ('restore_checkpoint', (4, 2), ANY),
            ('get_tag_at', ('k', 'f', 12), 'v1'),
            ('get_tag_at', ('k', 'f', 13), None),
        ])

    def test_level_4_case_20_restored_data_is_independent_of_checkpoint(self):
        """Writing after a restore must not change the stored checkpoint."""
        run_steps(self, self.impl, [
            ('set_tag_at', ('k', 'a', '1', 1), ANY),
            ('checkpoint', (2,), 1),
            ('restore_checkpoint', (3, 2), ANY),
            ('set_tag_at', ('k', 'a', 'changed', 4), ANY),
            ('set_tag_at', ('k', 'b', 'extra', 5), ANY),
            ('restore_checkpoint', (6, 2), ANY),
            ('list_tags_at', ('k', 7), ['a(1)']),
        ])

    def test_level_4_case_21_randomized_sequence_56(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('set_tag_at', ('P3', 'ba', '38', 4), ANY),
            ('checkpoint', (8,), 1),
            ('set_tag_at', ('P3', 'a', '43', 9), ANY),
            ('restore_checkpoint', (11, 5), ANY),
            ('remove_tag_at', ('P2', 'c', 15), False),
            ('restore_checkpoint', (15, 5), ANY),
            ('set_tag_with_hold', ('P1', 'B', '23', 19, 8), ANY),
            ('set_tag_at', ('P3', 'a', '99', 22), ANY),
            ('remove_tag_at', ('P1', 'ab', 23), False),
            ('set_tag_at', ('P2', 'c', '81', 24), ANY),
            ('set_tag_at', ('P3', 'a', '74', 26), ANY),
            ('set_tag_at', ('P3', 'c', '0', 28), ANY),
            ('remove_tag_at', ('P3', 'B', 32), False),
            ('list_tags_at', ('P2', 35), ['c(81)']),
            ('remove_tag_at', ('P3', 'B', 36), False),
            ('list_tags_at', ('P1', 36), []),
            ('list_tags_by_prefix_at', ('P2', '', 38), ['c(81)']),
            ('set_tag_with_hold', ('P3', 'b', '59', 39, 0), ANY),
            ('set_tag_at', ('P2', 'ba', '20', 40), ANY),
            ('set_tag_at', ('P3', 'c', '36', 44), ANY),
            ('list_tags_by_prefix_at', ('P1', '', 48), []),
            ('get_tag_at', ('P3', 'ba', 52), '38'),
            ('list_tags_at', ('P1', 54), []),
            ('set_tag_at', ('P1', 'c', '79', 57), ANY),
            ('list_tags_by_prefix_at', ('P1', '', 61), ['c(79)']),
            ('set_tag_at', ('P3', 'B', '33', 61), ANY),
            ('remove_tag_at', ('P1', 'b', 61), False),
            ('list_tags_by_prefix_at', ('P3', '', 62), ['B(33)', 'a(74)', 'b(59)', 'ba(38)', 'c(36)']),
            ('restore_checkpoint', (65, 8), ANY),
            ('remove_tag_at', ('P3', 'ba', 66), True),
            ('restore_checkpoint', (66, 10), ANY),
            ('set_tag_with_hold', ('P1', 'b', '13', 66, 12), ANY),
            ('list_tags_at', ('P1', 70), ['b(13)']),
            ('list_tags_at', ('P2', 70), []),
            ('restore_checkpoint', (72, 8), ANY),
            ('list_tags_by_prefix_at', ('P3', 'b', 73), ['ba(38)']),
            ('checkpoint', (76,), 1),
            ('set_tag_with_hold', ('P2', 'ab', '55', 80, 12), ANY),
            ('get_tag_at', ('P2', 'ab', 84), '55'),
            ('list_tags_at', ('P1', 88), []),
            ('set_tag_at', ('P1', 'b', '33', 91), ANY),
            ('list_tags_at', ('P1', 95), ['b(33)']),
            ('set_tag_with_hold', ('P2', 'ba', '14', 96, 12), ANY),
            ('set_tag_at', ('P3', 'ab', '45', 98), ANY),
            ('list_tags_by_prefix_at', ('P1', 'a', 98), []),
            ('list_tags_by_prefix_at', ('P3', 'a', 101), ['ab(45)']),
            ('get_tag_at', ('P3', 'B', 103), None),
            ('restore_checkpoint', (105, 77), ANY),
            ('restore_checkpoint', (105, 10), ANY),
            ('get_tag_at', ('P1', 'ab', 108), None),
            ('checkpoint', (111,), 1),
            ('list_tags_at', ('P2', 112), []),
            ('list_tags_at', ('P3', 112), ['ba(38)']),
            ('checkpoint', (113,), 1),
            ('set_tag_at', ('P1', 'B', '5', 117), ANY),
            ('get_tag_at', ('P3', 'a', 121), None),
            ('remove_tag_at', ('P3', 'b', 123), False),
            ('set_tag_with_hold', ('P2', 'b', '19', 125, 12), ANY),
            ('set_tag_with_hold', ('P1', 'c', '38', 129, 8), ANY),
            ('list_tags_by_prefix_at', ('P2', 'B', 132), []),
            ('restore_checkpoint', (134, 75), ANY),
            ('get_tag_at', ('P1', 'a', 136), None),
            ('set_tag_with_hold', ('P2', 'ab', '4', 137, 0), ANY),
            ('set_tag_with_hold', ('P2', 'a', '66', 137, 8), ANY),
            ('set_tag_at', ('P1', 'B', '90', 141), ANY),
            ('checkpoint', (144,), 3),
            ('list_tags_by_prefix_at', ('P1', 'a', 144), []),
            ('set_tag_with_hold', ('P3', 'ab', '74', 148, 2), ANY),
            ('checkpoint', (151,), 3),
            ('checkpoint', (152,), 3),
            ('list_tags_at', ('P1', 152), ['B(90)']),
            ('set_tag_at', ('P3', 'ba', '54', 153), ANY),
            ('get_tag_at', ('P2', 'c', 154), None),
            ('list_tags_at', ('P1', 158), ['B(90)']),
            ('list_tags_by_prefix_at', ('P2', '', 160), ['ab(4)']),
            ('set_tag_with_hold', ('P3', 'ab', '6', 161, 2), ANY),
            ('checkpoint', (161,), 3),
            ('list_tags_by_prefix_at', ('P1', 'a', 162), []),
            ('list_tags_at', ('P1', 166), ['B(90)']),
            ('restore_checkpoint', (169, 112), ANY),
            ('set_tag_with_hold', ('P3', 'B', '63', 171, 0), ANY),
            ('list_tags_at', ('P2', 172), []),
            ('list_tags_by_prefix_at', ('P1', 'B', 173), []),
            ('set_tag_at', ('P1', 'ba', '15', 174), ANY),
            ('list_tags_at', ('P1', 175), ['ba(15)']),
            ('set_tag_at', ('P3', 'b', '66', 175), ANY),
            ('restore_checkpoint', (175, 5), ANY),
            ('list_tags_at', ('P2', 176), []),
            ('restore_checkpoint', (180, 75), ANY),
            ('set_tag_at', ('P2', 'B', '79', 182), ANY),
        ])

    def test_level_4_case_22_randomized_sequence_57(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('get_tag_at', ('P3', 'a', 0), None),
            ('remove_tag_at', ('P2', 'b', 1), False),
            ('list_tags_at', ('P2', 4), []),
            ('remove_tag_at', ('P3', 'b', 5), False),
            ('get_tag_at', ('P1', 'c', 8), None),
            ('list_tags_at', ('P3', 12), []),
            ('set_tag_at', ('P1', 'ab', '48', 16), ANY),
            ('checkpoint', (20,), 1),
            ('list_tags_by_prefix_at', ('P3', 'b', 24), []),
            ('remove_tag_at', ('P1', 'ab', 28), True),
            ('get_tag_at', ('P1', 'B', 30), None),
            ('set_tag_at', ('P2', 'B', '2', 33), ANY),
            ('set_tag_at', ('P2', 'B', '66', 36), ANY),
            ('list_tags_by_prefix_at', ('P3', '', 36), []),
            ('set_tag_at', ('P2', 'b', '46', 38), ANY),
            ('list_tags_at', ('P3', 40), []),
            ('get_tag_at', ('P1', 'ab', 40), None),
            ('list_tags_at', ('P2', 40), ['B(66)', 'b(46)']),
            ('set_tag_at', ('P3', 'B', '31', 41), ANY),
            ('remove_tag_at', ('P1', 'c', 42), False),
            ('restore_checkpoint', (42, 19), ANY),
            ('checkpoint', (43,), 2),
            ('remove_tag_at', ('P1', 'a', 43), False),
            ('set_tag_with_hold', ('P3', 'B', '68', 43, 1), ANY),
            ('get_tag_at', ('P3', 'ba', 43), None),
            ('checkpoint', (46,), 1),
            ('list_tags_by_prefix_at', ('P2', 'B', 50), ['B(66)']),
            ('list_tags_by_prefix_at', ('P1', 'a', 51), []),
            ('checkpoint', (51,), 1),
            ('remove_tag_at', ('P3', 'c', 51), False),
            ('list_tags_at', ('P1', 53), []),
            ('get_tag_at', ('P2', 'ba', 55), None),
            ('set_tag_with_hold', ('P3', 'b', '47', 58, 8), ANY),
            ('set_tag_with_hold', ('P3', 'ba', '0', 61, 8), ANY),
            ('remove_tag_at', ('P1', 'B', 64), False),
            ('list_tags_at', ('P2', 64), ['B(66)', 'b(46)']),
            ('set_tag_with_hold', ('P3', 'a', '0', 64, 8), ANY),
            ('list_tags_at', ('P3', 64), ['a(0)', 'b(47)', 'ba(0)']),
            ('list_tags_at', ('P1', 67), []),
            ('restore_checkpoint', (67, 43), ANY),
            ('set_tag_at', ('P1', 'B', '84', 67), ANY),
            ('set_tag_with_hold', ('P3', 'ba', '95', 68, 8), ANY),
            ('checkpoint', (72,), 3),
            ('get_tag_at', ('P1', 'ab', 72), None),
            ('set_tag_at', ('P3', 'ab', '71', 72), ANY),
            ('restore_checkpoint', (72, 72), ANY),
            ('set_tag_with_hold', ('P2', 'b', '23', 75, 0), ANY),
            ('remove_tag_at', ('P1', 'ab', 77), False),
            ('get_tag_at', ('P1', 'a', 78), None),
            ('get_tag_at', ('P1', 'ab', 79), None),
            ('set_tag_with_hold', ('P3', 'ba', '38', 81, 1), ANY),
            ('restore_checkpoint', (85, 50), ANY),
            ('set_tag_with_hold', ('P1', 'c', '37', 86, 8), ANY),
            ('remove_tag_at', ('P1', 'B', 87), False),
            ('get_tag_at', ('P2', 'b', 90), '46'),
            ('list_tags_at', ('P2', 90), ['B(66)', 'b(46)']),
            ('set_tag_with_hold', ('P3', 'B', '88', 90, 2), ANY),
            ('list_tags_by_prefix_at', ('P3', 'b', 91), []),
            ('list_tags_at', ('P2', 92), ['B(66)', 'b(46)']),
            ('list_tags_by_prefix_at', ('P1', 'b', 94), []),
            ('checkpoint', (95,), 1),
            ('remove_tag_at', ('P2', 'c', 98), False),
            ('list_tags_by_prefix_at', ('P3', 'a', 99), []),
            ('list_tags_at', ('P3', 100), []),
            ('set_tag_at', ('P2', 'ab', '65', 100), ANY),
            ('list_tags_at', ('P1', 102), []),
            ('restore_checkpoint', (106, 20), ANY),
            ('set_tag_at', ('P1', 'c', '63', 108), ANY),
            ('get_tag_at', ('P3', 'a', 109), None),
            ('list_tags_at', ('P3', 113), []),
            ('set_tag_at', ('P1', 'B', '34', 116), ANY),
            ('set_tag_with_hold', ('P1', 'ba', '33', 117, 1), ANY),
            ('set_tag_with_hold', ('P2', 'b', '70', 120, 3), ANY),
            ('list_tags_by_prefix_at', ('P2', 'B', 120), []),
            ('set_tag_with_hold', ('P2', 'b', '50', 124, 3), ANY),
            ('checkpoint', (127,), 1),
            ('get_tag_at', ('P3', 'ab', 127), None),
            ('set_tag_at', ('P1', 'ba', '40', 130), ANY),
            ('restore_checkpoint', (131, 47), ANY),
            ('restore_checkpoint', (133, 52), ANY),
            ('checkpoint', (137,), 1),
            ('list_tags_at', ('P1', 137), []),
            ('set_tag_with_hold', ('P2', 'ba', '17', 138, 12), ANY),
            ('set_tag_with_hold', ('P3', 'ab', '46', 139, 8), ANY),
            ('set_tag_with_hold', ('P2', 'B', '12', 140, 5), ANY),
            ('list_tags_at', ('P2', 142), ['B(12)', 'b(46)', 'ba(17)']),
            ('restore_checkpoint', (144, 95), ANY),
            ('get_tag_at', ('P3', 'B', 144), None),
            ('list_tags_at', ('P3', 147), []),
            ('remove_tag_at', ('P1', 'ba', 148), False),
        ])

    def test_level_4_case_23_randomized_sequence_58(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('set_tag_with_hold', ('P3', 'c', '25', 4, 0), ANY),
            ('get_tag_at', ('P2', 'b', 5), None),
            ('checkpoint', (7,), 1),
            ('checkpoint', (9,), 1),
            ('set_tag_with_hold', ('P1', 'B', '70', 12, 8), ANY),
            ('list_tags_at', ('P1', 15), ['B(70)']),
            ('set_tag_with_hold', ('P1', 'b', '39', 16, 1), ANY),
            ('list_tags_at', ('P1', 20), []),
            ('set_tag_with_hold', ('P2', 'ab', '16', 20, 1), ANY),
            ('set_tag_at', ('P2', 'c', '92', 21), ANY),
            ('get_tag_at', ('P3', 'ba', 21), None),
            ('remove_tag_at', ('P3', 'b', 23), False),
            ('get_tag_at', ('P2', 'b', 27), None),
            ('get_tag_at', ('P1', 'ba', 28), None),
            ('get_tag_at', ('P3', 'a', 29), None),
            ('restore_checkpoint', (30, 9), ANY),
            ('get_tag_at', ('P3', 'B', 33), None),
            ('list_tags_by_prefix_at', ('P3', 'a', 34), []),
            ('remove_tag_at', ('P1', 'b', 34), False),
            ('set_tag_at', ('P3', 'a', '15', 34), ANY),
            ('get_tag_at', ('P3', 'c', 34), '25'),
            ('list_tags_at', ('P3', 36), ['a(15)', 'c(25)']),
            ('set_tag_with_hold', ('P1', 'b', '9', 38, 12), ANY),
            ('set_tag_at', ('P3', 'ab', '84', 39), ANY),
            ('get_tag_at', ('P3', 'B', 41), None),
            ('set_tag_with_hold', ('P3', 'ba', '27', 42, 12), ANY),
            ('set_tag_at', ('P3', 'a', '46', 42), ANY),
            ('get_tag_at', ('P2', 'a', 45), None),
            ('restore_checkpoint', (47, 9), ANY),
            ('set_tag_at', ('P1', 'ba', '82', 50), ANY),
            ('list_tags_by_prefix_at', ('P1', '', 51), ['ba(82)']),
            ('restore_checkpoint', (52, 4), ANY),
            ('set_tag_at', ('P2', 'c', '30', 53), ANY),
            ('list_tags_by_prefix_at', ('P2', 'B', 55), []),
            ('checkpoint', (59,), 3),
            ('remove_tag_at', ('P1', 'B', 59), False),
            ('get_tag_at', ('P1', 'c', 59), None),
            ('set_tag_with_hold', ('P2', 'a', '46', 63, 2), ANY),
            ('restore_checkpoint', (64, 7), ANY),
            ('get_tag_at', ('P1', 'c', 67), None),
            ('get_tag_at', ('P2', 'ba', 68), None),
            ('get_tag_at', ('P2', 'c', 70), None),
            ('restore_checkpoint', (74, 7), ANY),
            ('restore_checkpoint', (75, 59), ANY),
            ('set_tag_with_hold', ('P3', 'ab', '61', 79, 1), ANY),
            ('get_tag_at', ('P1', 'a', 80), None),
            ('remove_tag_at', ('P2', 'ba', 83), False),
            ('get_tag_at', ('P1', 'ab', 84), None),
            ('set_tag_at', ('P2', 'ba', '8', 88), ANY),
            ('set_tag_with_hold', ('P3', 'ba', '79', 89, 8), ANY),
            ('get_tag_at', ('P2', 'B', 91), None),
            ('set_tag_at', ('P2', 'c', '1', 94), ANY),
            ('list_tags_by_prefix_at', ('P2', '', 98), ['ba(8)', 'c(1)']),
            ('checkpoint', (101,), 3),
            ('checkpoint', (102,), 3),
            ('remove_tag_at', ('P2', 'b', 104), False),
            ('set_tag_with_hold', ('P1', 'ab', '27', 107, 3), ANY),
            ('set_tag_at', ('P2', 'ab', '1', 111), ANY),
            ('remove_tag_at', ('P3', 'a', 114), False),
            ('list_tags_by_prefix_at', ('P1', 'B', 115), []),
            ('get_tag_at', ('P2', 'b', 117), None),
            ('set_tag_at', ('P1', 'a', '51', 121), ANY),
            ('restore_checkpoint', (124, 56), ANY),
            ('restore_checkpoint', (128, 59), ANY),
            ('get_tag_at', ('P1', 'b', 129), None),
            ('restore_checkpoint', (132, 6), ANY),
            ('checkpoint', (135,), 3),
            ('set_tag_with_hold', ('P2', 'a', '47', 138, 0), ANY),
            ('remove_tag_at', ('P3', 'ab', 138), False),
            ('get_tag_at', ('P3', 'c', 138), '25'),
            ('set_tag_with_hold', ('P2', 'a', '50', 139, 2), ANY),
            ('get_tag_at', ('P1', 'b', 141), None),
            ('get_tag_at', ('P2', 'ba', 142), None),
            ('set_tag_at', ('P3', 'B', '18', 145), ANY),
            ('set_tag_at', ('P1', 'B', '94', 147), ANY),
            ('restore_checkpoint', (151, 132), ANY),
            ('set_tag_at', ('P1', 'B', '29', 152), ANY),
            ('checkpoint', (156,), 3),
            ('get_tag_at', ('P1', 'b', 156), None),
            ('set_tag_with_hold', ('P1', 'B', '98', 156, 0), ANY),
            ('remove_tag_at', ('P3', 'b', 156), False),
            ('set_tag_at', ('P1', 'b', '8', 158), ANY),
            ('get_tag_at', ('P3', 'a', 161), None),
            ('set_tag_with_hold', ('P1', 'a', '65', 163, 8), ANY),
            ('list_tags_by_prefix_at', ('P3', '', 163), ['c(25)']),
            ('get_tag_at', ('P1', 'b', 163), '8'),
            ('list_tags_at', ('P2', 166), ['ba(8)', 'c(1)']),
            ('set_tag_with_hold', ('P2', 'ba', '57', 166, 5), ANY),
            ('checkpoint', (169,), 3),
            ('remove_tag_at', ('P3', 'ab', 173), False),
        ])


if __name__ == "__main__":
    unittest.main()
