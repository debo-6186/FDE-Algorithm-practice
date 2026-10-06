"""
Level 2 tests for Cloud Storage v2.

Each test replays a sequence of calls on a fresh CloudStorageImpl() and checks
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

from cloud_storage_v2_impl import CloudStorageV2Impl

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
        self.impl = CloudStorageV2Impl()

    def test_level_2_case_01_example_from_spec(self):
        """The Level 2 example table."""
        run_steps(self, self.impl, [
            ('add_file', ('/reports/2024.pdf', 500), True),
            ('add_file', ('/reports/2025.pdf', 300), True),
            ('add_file', ('/reports/notes.txt', 100), True),
            ('add_file', ('/readme.txt', 300), True),
            ('find_file', ('/reports', '.pdf'), ['/reports/2024.pdf(500)', '/reports/2025.pdf(300)']),
            ('find_file', ('/', '.txt'), ['/readme.txt(300)', '/reports/notes.txt(100)']),
            ('find_file', ('/re', ''), ['/reports/2024.pdf(500)', '/readme.txt(300)', '/reports/2025.pdf(300)', '/reports/notes.txt(100)']),
            ('find_file', ('/x', ''), []),
        ])

    def test_level_2_case_02_prefix_and_suffix_may_overlap(self):
        run_steps(self, self.impl, [
            ('add_file', ('ab', 1), True),
            ('add_file', ('abb', 2), True),
            ('add_file', ('b', 3), True),
            ('find_file', ('ab', 'b'), ['abb(2)', 'ab(1)']),
            ('find_file', ('abb', 'abb'), ['abb(2)']),
            ('find_file', ('ab', 'bab'), []),
        ])

    def test_level_2_case_03_empty_filters_match_all(self):
        run_steps(self, self.impl, [
            ('add_file', ('/z', 1), True),
            ('add_file', ('/y', 1), True),
            ('find_file', ('', ''), ['/y(1)', '/z(1)']),
        ])

    def test_level_2_case_04_copies_are_found_too(self):
        run_steps(self, self.impl, [
            ('add_file', ('/a.log', 10), True),
            ('copy_file', ('/a.log', '/b.log'), True),
            ('find_file', ('/', '.log'), ['/a.log(10)', '/b.log(10)']),
        ])

    def test_level_2_case_05_nothing_stored_then_one(self):
        run_steps(self, self.impl, [
            ('find_file', ('', ''), []),
            ('add_file', ('/a', 1), True),
            ('find_file', ('', ''), ['/a(1)']),
        ])

    def test_level_2_case_06_randomized_sequence_27(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('get_file_size', ('/b.txt',), None),
            ('add_file', ('/a.txt', 20), True),
            ('add_file', ('/b.txt.COMPRESSED', 10), True),
            ('find_file', ('', '.COMPRESSED'), ['/b.txt.COMPRESSED(10)']),
            ('find_file', ('/b', 'D'), ['/b.txt.COMPRESSED(10)']),
            ('add_file', ('/c.bin', 10), True),
            ('get_file_size', ('/a.COMPRESSED',), None),
            ('find_file', ('/b', 'D'), ['/b.txt.COMPRESSED(10)']),
            ('find_file', ('/', 'b'), []),
            ('find_file', ('/', ''), ['/a.txt(20)', '/b.txt.COMPRESSED(10)', '/c.bin(10)']),
            ('copy_file', ('/ab', '/b.txt.COMPRESSED'), False),
            ('add_file', ('/c.bin', 20), False),
            ('add_file', ('/ab', 10), True),
            ('copy_file', ('/a', '/ab'), False),
            ('add_file', ('/c.bin', 20), False),
            ('copy_file', ('/a', '/a.COMPRESSED'), False),
            ('get_file_size', ('/b.txt',), None),
            ('find_file', ('/b', 'b'), []),
            ('add_file', ('/a.txt', 20), False),
            ('add_file', ('/c.bin', 3), False),
            ('get_file_size', ('/a.COMPRESSED',), None),
            ('add_file', ('/a.txt', 25), False),
            ('copy_file', ('/c.bin', '/ab'), False),
            ('find_file', ('/', '.txt'), ['/a.txt(20)']),
            ('copy_file', ('/a.COMPRESSED', '/a.txt'), False),
            ('copy_file', ('/a', '/a.txt'), False),
            ('find_file', ('/', 'b'), ['/ab(10)']),
            ('get_file_size', ('/c.bin',), 10),
            ('add_file', ('/a.COMPRESSED', 3), True),
            ('get_file_size', ('/ab',), 10),
            ('get_file_size', ('/b',), None),
            ('find_file', ('/a', '.COMPRESSED'), ['/a.COMPRESSED(3)']),
            ('get_file_size', ('/b',), None),
            ('copy_file', ('/a.txt', '/b.txt.COMPRESSED'), False),
            ('copy_file', ('/a', '/a.txt'), False),
            ('copy_file', ('/a.txt', '/b'), True),
            ('add_file', ('/a', 25), True),
            ('find_file', ('/', 'D'), ['/b.txt.COMPRESSED(10)', '/a.COMPRESSED(3)']),
            ('find_file', ('/b', 'D'), ['/b.txt.COMPRESSED(10)']),
            ('copy_file', ('/b', '/b'), False),
            ('add_file', ('/a.COMPRESSED', 10), False),
            ('find_file', ('/a', ''), ['/a(25)', '/a.txt(20)', '/ab(10)', '/a.COMPRESSED(3)']),
            ('add_file', ('/a.txt', 10), False),
            ('add_file', ('/c.bin', 25), False),
            ('add_file', ('/ab', 25), False),
            ('find_file', ('/a', '.COMPRESSED'), ['/a.COMPRESSED(3)']),
            ('find_file', ('/a', 'D'), ['/a.COMPRESSED(3)']),
            ('find_file', ('/', '.COMPRESSED'), ['/b.txt.COMPRESSED(10)', '/a.COMPRESSED(3)']),
            ('find_file', ('/', 'D'), ['/b.txt.COMPRESSED(10)', '/a.COMPRESSED(3)']),
            ('add_file', ('/b.txt', 25), True),
        ])

    def test_level_2_case_07_randomized_sequence_28(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('add_file', ('/ab', 10), True),
            ('add_file', ('/c.bin', 10), True),
            ('add_file', ('/b.txt.COMPRESSED', 10), True),
            ('get_file_size', ('/b',), None),
            ('copy_file', ('/a.txt', '/b.txt.COMPRESSED'), False),
            ('find_file', ('/', '.COMPRESSED'), ['/b.txt.COMPRESSED(10)']),
            ('get_file_size', ('/b.txt',), None),
            ('find_file', ('/', ''), ['/ab(10)', '/b.txt.COMPRESSED(10)', '/c.bin(10)']),
            ('find_file', ('', '.COMPRESSED'), ['/b.txt.COMPRESSED(10)']),
            ('get_file_size', ('/b.txt',), None),
            ('get_file_size', ('/ab',), 10),
            ('copy_file', ('/a', '/c.bin'), False),
            ('copy_file', ('/b.txt.COMPRESSED', '/b.txt.COMPRESSED'), False),
            ('find_file', ('/', 'D'), ['/b.txt.COMPRESSED(10)']),
            ('find_file', ('', '.txt'), []),
            ('add_file', ('/a.COMPRESSED', 25), True),
            ('add_file', ('/ab', 10), False),
            ('get_file_size', ('/c.bin',), 10),
            ('add_file', ('/b.txt.COMPRESSED', 25), False),
            ('find_file', ('/', '.txt'), []),
            ('find_file', ('/b', '.COMPRESSED'), ['/b.txt.COMPRESSED(10)']),
            ('add_file', ('/ab', 25), False),
            ('copy_file', ('/a.COMPRESSED', '/b'), True),
            ('copy_file', ('/a.txt', '/a.txt'), False),
            ('get_file_size', ('/b.txt',), None),
            ('add_file', ('/b', 3), False),
            ('copy_file', ('/a.COMPRESSED', '/b.txt.COMPRESSED'), False),
            ('copy_file', ('/b.txt.COMPRESSED', '/a.COMPRESSED'), False),
            ('add_file', ('/a.COMPRESSED', 3), False),
            ('find_file', ('/a', 'b'), ['/ab(10)']),
            ('find_file', ('/b', '.txt'), []),
            ('find_file', ('/b', '.txt'), []),
            ('add_file', ('/ab', 3), False),
            ('copy_file', ('/b', '/a.txt'), True),
            ('find_file', ('', 'D'), ['/a.COMPRESSED(25)', '/b.txt.COMPRESSED(10)']),
            ('copy_file', ('/a.COMPRESSED', '/b.txt.COMPRESSED'), False),
            ('copy_file', ('/a', '/b'), False),
            ('add_file', ('/a.txt', 20), False),
            ('add_file', ('/b', 20), False),
            ('get_file_size', ('/b.txt.COMPRESSED',), 10),
            ('find_file', ('/a', 'b'), ['/ab(10)']),
            ('get_file_size', ('/b',), 25),
            ('add_file', ('/c.bin', 20), False),
            ('copy_file', ('/b.txt', '/a.COMPRESSED'), False),
            ('get_file_size', ('/b.txt.COMPRESSED',), 10),
            ('add_file', ('/a.COMPRESSED', 20), False),
            ('get_file_size', ('/ab',), 10),
            ('find_file', ('/b', ''), ['/b(25)', '/b.txt.COMPRESSED(10)']),
            ('find_file', ('/a', '.COMPRESSED'), ['/a.COMPRESSED(25)']),
            ('add_file', ('/b.txt', 20), True),
        ])


if __name__ == "__main__":
    unittest.main()
