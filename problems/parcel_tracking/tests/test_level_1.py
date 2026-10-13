"""
Level 1 tests for Parcel Tracking System.

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


class TestLevel1(unittest.TestCase):
    def setUp(self):
        self.impl = ParcelTrackingSystemImpl()

    def test_level_1_case_01_example_from_spec(self):
        """The Level 1 example table."""
        run_steps(self, self.impl, [
            ('set_tag', ('parcel1', 'status', 'in-transit'), ANY),
            ('get_tag', ('parcel1', 'status'), 'in-transit'),
            ('set_tag', ('parcel1', 'status', 'delivered'), ANY),
            ('get_tag', ('parcel1', 'status'), 'delivered'),
            ('remove_tag', ('parcel1', 'status'), True),
            ('get_tag', ('parcel1', 'status'), None),
            ('remove_tag', ('parcel1', 'status'), False),
        ])

    def test_level_1_case_02_set_returns_none(self):
        run_steps(self, self.impl, [
            ('set_tag', ('p', 't', 'v'), None),
            ('get_tag', ('p', 't'), 'v'),
        ])

    def test_level_1_case_03_parcels_are_independent(self):
        run_steps(self, self.impl, [
            ('set_tag', ('a', 't', '1'), ANY),
            ('set_tag', ('b', 't', '2'), ANY),
            ('remove_tag', ('a', 't'), True),
            ('get_tag', ('b', 't'), '2'),
            ('get_tag', ('a', 't'), None),
        ])

    def test_level_1_case_04_unknown_parcel_and_unknown_tag(self):
        run_steps(self, self.impl, [
            ('get_tag', ('nobody', 't'), None),
            ('remove_tag', ('nobody', 't'), False),
            ('set_tag', ('p', 'a', '1'), ANY),
            ('get_tag', ('p', 'b'), None),
            ('remove_tag', ('p', 'b'), False),
            ('get_tag', ('p', 'a'), '1'),
        ])

    def test_level_1_case_05_overwrite_keeps_other_tags(self):
        run_steps(self, self.impl, [
            ('set_tag', ('p', 'a', '1'), ANY),
            ('set_tag', ('p', 'b', '2'), ANY),
            ('set_tag', ('p', 'a', '3'), ANY),
            ('get_tag', ('p', 'a'), '3'),
            ('get_tag', ('p', 'b'), '2'),
        ])

    def test_level_1_case_06_remove_last_tag_then_reuse_parcel(self):
        run_steps(self, self.impl, [
            ('set_tag', ('p', 'only', 'x'), ANY),
            ('remove_tag', ('p', 'only'), True),
            ('get_tag', ('p', 'only'), None),
            ('remove_tag', ('p', 'only'), False),
            ('set_tag', ('p', 'again', 'y'), ANY),
            ('get_tag', ('p', 'again'), 'y'),
        ])

    def test_level_1_case_07_values_are_strings_kept_verbatim(self):
        run_steps(self, self.impl, [
            ('set_tag', ('p', 'n', '007'), ANY),
            ('set_tag', ('p', 's', ' spaced '), ANY),
            ('get_tag', ('p', 'n'), '007'),
            ('get_tag', ('p', 's'), ' spaced '),
        ])

    def test_level_1_case_08_randomized_sequence_16(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('set_tag', ('P2', 'b', '53'), ANY),
            ('set_tag', ('P1', 'B', '84'), ANY),
            ('get_tag', ('P1', 'c'), None),
            ('set_tag', ('P2', 'b', '42'), ANY),
            ('get_tag', ('P3', 'ba'), None),
            ('set_tag', ('P1', 'ba', '32'), ANY),
            ('set_tag', ('P1', 'ba', '85'), ANY),
            ('get_tag', ('P2', 'B'), None),
            ('get_tag', ('P3', 'b'), None),
            ('remove_tag', ('P2', 'b'), True),
            ('set_tag', ('P1', 'b', '63'), ANY),
            ('set_tag', ('P3', 'ab', '72'), ANY),
            ('set_tag', ('P1', 'b', '10'), ANY),
            ('remove_tag', ('P1', 'ba'), True),
            ('set_tag', ('P2', 'ab', '39'), ANY),
            ('set_tag', ('P2', 'B', '8'), ANY),
            ('set_tag', ('P2', 'c', '1'), ANY),
            ('set_tag', ('P2', 'a', '60'), ANY),
            ('get_tag', ('P1', 'B'), '84'),
            ('remove_tag', ('P1', 'B'), True),
            ('get_tag', ('P1', 'c'), None),
            ('set_tag', ('P2', 'b', '4'), ANY),
            ('get_tag', ('P3', 'c'), None),
            ('set_tag', ('P2', 'B', '65'), ANY),
            ('get_tag', ('P3', 'c'), None),
            ('remove_tag', ('P1', 'ab'), False),
            ('set_tag', ('P3', 'a', '69'), ANY),
            ('set_tag', ('P1', 'B', '80'), ANY),
            ('set_tag', ('P1', 'c', '87'), ANY),
            ('set_tag', ('P2', 'ab', '81'), ANY),
            ('get_tag', ('P1', 'ab'), None),
            ('get_tag', ('P1', 'ba'), None),
            ('set_tag', ('P1', 'a', '82'), ANY),
            ('set_tag', ('P2', 'B', '4'), ANY),
            ('set_tag', ('P3', 'B', '58'), ANY),
            ('set_tag', ('P1', 'a', '90'), ANY),
            ('set_tag', ('P3', 'b', '64'), ANY),
            ('set_tag', ('P1', 'a', '53'), ANY),
            ('get_tag', ('P2', 'a'), '60'),
            ('get_tag', ('P1', 'B'), '80'),
        ])

    def test_level_1_case_09_randomized_sequence_17(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('get_tag', ('P2', 'b'), None),
            ('set_tag', ('P3', 'c', '69'), ANY),
            ('get_tag', ('P1', 'a'), None),
            ('set_tag', ('P3', 'B', '32'), ANY),
            ('remove_tag', ('P2', 'c'), False),
            ('remove_tag', ('P3', 'B'), True),
            ('set_tag', ('P3', 'a', '17'), ANY),
            ('remove_tag', ('P1', 'ab'), False),
            ('remove_tag', ('P3', 'ba'), False),
            ('remove_tag', ('P3', 'ab'), False),
            ('set_tag', ('P1', 'c', '81'), ANY),
            ('set_tag', ('P2', 'a', '64'), ANY),
            ('remove_tag', ('P2', 'c'), False),
            ('remove_tag', ('P1', 'c'), True),
            ('remove_tag', ('P3', 'b'), False),
            ('set_tag', ('P2', 'ba', '6'), ANY),
            ('remove_tag', ('P3', 'b'), False),
            ('set_tag', ('P2', 'b', '74'), ANY),
            ('remove_tag', ('P2', 'ab'), False),
            ('set_tag', ('P1', 'ab', '67'), ANY),
            ('remove_tag', ('P1', 'b'), False),
            ('set_tag', ('P2', 'ab', '95'), ANY),
            ('get_tag', ('P3', 'ba'), None),
            ('get_tag', ('P1', 'b'), None),
            ('get_tag', ('P2', 'b'), '74'),
            ('set_tag', ('P1', 'ba', '74'), ANY),
            ('remove_tag', ('P2', 'a'), True),
            ('set_tag', ('P2', 'a', '59'), ANY),
            ('remove_tag', ('P2', 'c'), False),
            ('set_tag', ('P1', 'b', '33'), ANY),
            ('set_tag', ('P3', 'B', '2'), ANY),
            ('get_tag', ('P3', 'c'), '69'),
            ('set_tag', ('P2', 'c', '75'), ANY),
            ('remove_tag', ('P1', 'ab'), True),
            ('remove_tag', ('P1', 'c'), False),
            ('set_tag', ('P1', 'a', '68'), ANY),
            ('set_tag', ('P2', 'b', '6'), ANY),
            ('set_tag', ('P2', 'a', '88'), ANY),
            ('remove_tag', ('P2', 'c'), True),
            ('remove_tag', ('P2', 'a'), True),
        ])


if __name__ == "__main__":
    unittest.main()
