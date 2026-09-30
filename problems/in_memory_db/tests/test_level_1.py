"""
Level 1 tests for In-Memory Database.

Each test replays a sequence of calls on a fresh InMemoryDBImpl() and checks
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

from in_memory_db_impl import InMemoryDBImpl

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
        self.impl = InMemoryDBImpl()

    def test_level_1_case_01_example_from_spec(self):
        """The Level 1 example table."""
        run_steps(self, self.impl, [
            ('set', ('user:1', 'name', 'Ann'), ANY),
            ('set', ('user:1', 'city', 'Paris'), ANY),
            ('get', ('user:1', 'name'), 'Ann'),
            ('get', ('user:1', 'email'), None),
            ('get', ('user:2', 'name'), None),
            ('set', ('user:1', 'name', 'Anna'), ANY),
            ('get', ('user:1', 'name'), 'Anna'),
            ('delete', ('user:1', 'city'), True),
            ('delete', ('user:1', 'city'), False),
            ('delete', ('user:9', 'x'), False),
        ])

    def test_level_1_case_02_set_returns_none(self):
        run_steps(self, self.impl, [
            ('set', ('k', 'f', 'v'), None),
            ('get', ('k', 'f'), 'v'),
        ])

    def test_level_1_case_03_records_are_independent(self):
        run_steps(self, self.impl, [
            ('set', ('a', 'f', '1'), ANY),
            ('set', ('b', 'f', '2'), ANY),
            ('delete', ('a', 'f'), True),
            ('get', ('b', 'f'), '2'),
            ('get', ('a', 'f'), None),
        ])

    def test_level_1_case_04_delete_last_field_then_reuse_record(self):
        run_steps(self, self.impl, [
            ('set', ('k', 'only', 'x'), ANY),
            ('delete', ('k', 'only'), True),
            ('get', ('k', 'only'), None),
            ('delete', ('k', 'only'), False),
            ('set', ('k', 'again', 'y'), ANY),
            ('get', ('k', 'again'), 'y'),
        ])

    def test_level_1_case_05_values_are_strings_kept_verbatim(self):
        run_steps(self, self.impl, [
            ('set', ('k', 'n', '007'), ANY),
            ('set', ('k', 's', ' spaced '), ANY),
            ('get', ('k', 'n'), '007'),
            ('get', ('k', 's'), ' spaced '),
        ])

    def test_level_1_case_06_randomized_sequence_16(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('set', ('B', 'b', '53'), ANY),
            ('set', ('A', 'B', '84'), ANY),
            ('get', ('A', 'c'), None),
            ('set', ('B', 'b', '42'), ANY),
            ('get', ('C', 'ba'), None),
            ('set', ('A', 'ba', '32'), ANY),
            ('set', ('A', 'ba', '85'), ANY),
            ('get', ('B', 'B'), None),
            ('get', ('C', 'b'), None),
            ('delete', ('B', 'b'), True),
            ('set', ('A', 'b', '63'), ANY),
            ('set', ('C', 'ab', '72'), ANY),
            ('set', ('A', 'b', '10'), ANY),
            ('delete', ('A', 'ba'), True),
            ('set', ('B', 'ab', '39'), ANY),
            ('set', ('B', 'B', '8'), ANY),
            ('set', ('B', 'c', '1'), ANY),
            ('set', ('B', 'a', '60'), ANY),
            ('get', ('A', 'B'), '84'),
            ('delete', ('A', 'B'), True),
            ('get', ('A', 'c'), None),
            ('set', ('B', 'b', '4'), ANY),
            ('get', ('C', 'c'), None),
            ('set', ('B', 'B', '65'), ANY),
            ('get', ('C', 'c'), None),
            ('delete', ('A', 'ab'), False),
            ('set', ('C', 'a', '69'), ANY),
            ('set', ('A', 'B', '80'), ANY),
            ('set', ('A', 'c', '87'), ANY),
            ('set', ('B', 'ab', '81'), ANY),
            ('get', ('A', 'ab'), None),
            ('get', ('A', 'ba'), None),
            ('set', ('A', 'a', '82'), ANY),
            ('set', ('B', 'B', '4'), ANY),
            ('set', ('C', 'B', '58'), ANY),
            ('set', ('A', 'a', '90'), ANY),
            ('set', ('C', 'b', '64'), ANY),
            ('set', ('A', 'a', '53'), ANY),
            ('get', ('B', 'a'), '60'),
            ('get', ('A', 'B'), '80'),
        ])


if __name__ == "__main__":
    unittest.main()
