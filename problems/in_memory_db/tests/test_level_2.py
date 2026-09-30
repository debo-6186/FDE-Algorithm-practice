"""
Level 2 tests for In-Memory Database.

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


class TestLevel2(unittest.TestCase):
    def setUp(self):
        self.impl = InMemoryDBImpl()

    def test_level_2_case_01_example_from_spec(self):
        """The Level 2 example table."""
        run_steps(self, self.impl, [
            ('set', ('cfg', 'db.port', '5432'), ANY),
            ('set', ('cfg', 'db.host', 'local'), ANY),
            ('set', ('cfg', 'log.level', 'info'), ANY),
            ('scan', ('cfg',), ['db.host(local)', 'db.port(5432)', 'log.level(info)']),
            ('scan_by_prefix', ('cfg', 'db.'), ['db.host(local)', 'db.port(5432)']),
            ('scan_by_prefix', ('cfg', 'x'), []),
            ('scan', ('other',), []),
        ])

    def test_level_2_case_02_lexicographic_order_is_case_sensitive(self):
        """Uppercase letters sort before lowercase; '10' < '9'."""
        run_steps(self, self.impl, [
            ('set', ('k', 'b', '1'), ANY),
            ('set', ('k', 'B', '2'), ANY),
            ('set', ('k', 'a', '3'), ANY),
            ('set', ('k', '10', '4'), ANY),
            ('set', ('k', '9', '5'), ANY),
            ('scan', ('k',), ['10(4)', '9(5)', 'B(2)', 'a(3)', 'b(1)']),
        ])

    def test_level_2_case_03_scan_reflects_updates_and_deletes(self):
        run_steps(self, self.impl, [
            ('set', ('k', 'x', '1'), ANY),
            ('set', ('k', 'y', '2'), ANY),
            ('set', ('k', 'x', '3'), ANY),
            ('delete', ('k', 'y'), True),
            ('scan', ('k',), ['x(3)']),
            ('delete', ('k', 'x'), True),
            ('scan', ('k',), []),
        ])

    def test_level_2_case_04_empty_prefix_equals_scan(self):
        run_steps(self, self.impl, [
            ('set', ('k', 'q', '1'), ANY),
            ('set', ('k', 'p', '2'), ANY),
            ('scan_by_prefix', ('k', ''), ['p(2)', 'q(1)']),
        ])

    def test_level_2_case_05_prefix_equal_to_whole_field_matches(self):
        run_steps(self, self.impl, [
            ('set', ('k', 'ab', '1'), ANY),
            ('set', ('k', 'abc', '2'), ANY),
            ('set', ('k', 'a', '3'), ANY),
            ('scan_by_prefix', ('k', 'ab'), ['ab(1)', 'abc(2)']),
            ('scan_by_prefix', ('k', 'abcd'), []),
        ])

    def test_level_2_case_06_randomized_sequence_31(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('set', ('A', 'B', '18'), ANY),
            ('delete', ('A', 'a'), False),
            ('delete', ('C', 'ab'), False),
            ('set', ('C', 'a', '84'), ANY),
            ('set', ('A', 'ba', '93'), ANY),
            ('get', ('B', 'ab'), None),
            ('scan_by_prefix', ('A', ''), ['B(18)', 'ba(93)']),
            ('scan', ('B',), []),
            ('set', ('B', 'B', '46'), ANY),
            ('delete', ('A', 'ab'), False),
            ('delete', ('B', 'ba'), False),
            ('delete', ('A', 'a'), False),
            ('scan', ('B',), ['B(46)']),
            ('set', ('B', 'a', '11'), ANY),
            ('scan', ('B',), ['B(46)', 'a(11)']),
            ('scan', ('A',), ['B(18)', 'ba(93)']),
            ('delete', ('A', 'b'), False),
            ('delete', ('A', 'B'), True),
            ('set', ('B', 'b', '42'), ANY),
            ('delete', ('B', 'c'), False),
            ('delete', ('B', 'ab'), False),
            ('scan_by_prefix', ('A', 'a'), []),
            ('delete', ('C', 'c'), False),
            ('set', ('A', 'ab', '3'), ANY),
            ('scan_by_prefix', ('C', ''), ['a(84)']),
            ('delete', ('B', 'b'), True),
            ('delete', ('A', 'a'), False),
            ('get', ('B', 'B'), '46'),
            ('get', ('A', 'ba'), '93'),
            ('delete', ('B', 'a'), True),
            ('scan_by_prefix', ('C', 'a'), ['a(84)']),
            ('set', ('A', 'c', '19'), ANY),
            ('get', ('B', 'ba'), None),
            ('scan', ('B',), ['B(46)']),
            ('scan_by_prefix', ('B', 'x'), []),
            ('set', ('A', 'B', '17'), ANY),
            ('scan', ('C',), ['a(84)']),
            ('get', ('A', 'b'), None),
            ('get', ('B', 'b'), None),
            ('set', ('A', 'B', '74'), ANY),
            ('set', ('A', 'a', '16'), ANY),
            ('set', ('C', 'a', '78'), ANY),
            ('scan_by_prefix', ('A', 'a'), ['a(16)', 'ab(3)']),
            ('delete', ('C', 'c'), False),
            ('get', ('C', 'ba'), None),
            ('get', ('C', 'ab'), None),
            ('delete', ('B', 'b'), False),
            ('delete', ('B', 'b'), False),
            ('set', ('A', 'ba', '44'), ANY),
            ('scan', ('B',), ['B(46)']),
        ])

    def test_level_2_case_07_randomized_sequence_32(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('set', ('A', 'ab', '38'), ANY),
            ('delete', ('A', 'B'), False),
            ('set', ('A', 'a', '41'), ANY),
            ('get', ('A', 'ba'), None),
            ('delete', ('B', 'b'), False),
            ('delete', ('C', 'ab'), False),
            ('get', ('B', 'c'), None),
            ('scan', ('A',), ['a(41)', 'ab(38)']),
            ('scan_by_prefix', ('A', ''), ['a(41)', 'ab(38)']),
            ('get', ('A', 'ba'), None),
            ('set', ('A', 'B', '2'), ANY),
            ('get', ('A', 'ba'), None),
            ('get', ('A', 'B'), '2'),
            ('set', ('B', 'ab', '68'), ANY),
            ('scan', ('C',), []),
            ('delete', ('C', 'a'), False),
            ('scan', ('C',), []),
            ('set', ('B', 'a', '31'), ANY),
            ('delete', ('B', 'B'), False),
            ('delete', ('B', 'a'), True),
            ('scan', ('B',), ['ab(68)']),
            ('delete', ('A', 'a'), True),
            ('set', ('B', 'a', '70'), ANY),
            ('set', ('B', 'a', '24'), ANY),
            ('delete', ('B', 'a'), True),
            ('get', ('C', 'c'), None),
            ('set', ('B', 'B', '61'), ANY),
            ('scan_by_prefix', ('A', 'b'), []),
            ('get', ('C', 'ab'), None),
            ('set', ('B', 'ba', '92'), ANY),
            ('get', ('C', 'ab'), None),
            ('delete', ('B', 'c'), False),
            ('get', ('C', 'ab'), None),
            ('scan_by_prefix', ('B', ''), ['B(61)', 'ab(68)', 'ba(92)']),
            ('scan_by_prefix', ('C', 'b'), []),
            ('scan', ('B',), ['B(61)', 'ab(68)', 'ba(92)']),
            ('get', ('A', 'b'), None),
            ('get', ('B', 'b'), None),
            ('set', ('C', 'ba', '99'), ANY),
            ('set', ('C', 'ba', '33'), ANY),
            ('get', ('B', 'B'), '61'),
            ('set', ('A', 'ba', '23'), ANY),
            ('scan_by_prefix', ('A', 'a'), ['ab(38)']),
            ('delete', ('B', 'B'), True),
            ('set', ('B', 'b', '24'), ANY),
            ('scan_by_prefix', ('A', 'x'), []),
            ('get', ('B', 'c'), None),
            ('scan_by_prefix', ('A', 'b'), ['ba(23)']),
            ('set', ('A', 'ab', '44'), ANY),
            ('set', ('A', 'ba', '28'), ANY),
        ])


if __name__ == "__main__":
    unittest.main()
