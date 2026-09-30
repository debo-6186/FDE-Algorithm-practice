"""
Level 2 tests for File Hosting (TTL + rollback).

Each test replays a sequence of calls on a fresh FileHostingImpl() and checks
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

from file_hosting_impl import FileHostingImpl

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
        self.impl = FileHostingImpl()

    def test_level_2_case_01_example_from_spec(self):
        """The Level 2 example table."""
        run_steps(self, self.impl, [
            ('file_upload', ('/logs/1.log', 10), ANY),
            ('file_upload', ('/logs/2.log', 30), ANY),
            ('file_upload', ('/logs/3.log', 20), ANY),
            ('file_upload', ('/lib/x.so', 30), ANY),
            ('file_search', ('/lo',), ['/logs/2.log', '/logs/3.log', '/logs/1.log']),
            ('file_search', ('/l',), ['/lib/x.so', '/logs/2.log', '/logs/3.log', '/logs/1.log']),
            ('file_search', ('/z',), []),
        ])

    def test_level_2_case_02_at_most_ten_results(self):
        """12 matching files: only the 10 largest are returned."""
        run_steps(self, self.impl, [
            ('file_upload', ('/f01', 1), ANY),
            ('file_upload', ('/f02', 2), ANY),
            ('file_upload', ('/f03', 3), ANY),
            ('file_upload', ('/f04', 4), ANY),
            ('file_upload', ('/f05', 5), ANY),
            ('file_upload', ('/f06', 6), ANY),
            ('file_upload', ('/f07', 7), ANY),
            ('file_upload', ('/f08', 8), ANY),
            ('file_upload', ('/f09', 9), ANY),
            ('file_upload', ('/f10', 10), ANY),
            ('file_upload', ('/f11', 11), ANY),
            ('file_upload', ('/f12', 12), ANY),
            ('file_search', ('/f',), ['/f12', '/f11', '/f10', '/f09', '/f08', '/f07', '/f06', '/f05', '/f04', '/f03']),
            ('file_search', ('/f0',), ['/f09', '/f08', '/f07', '/f06', '/f05', '/f04', '/f03', '/f02', '/f01']),
        ])

    def test_level_2_case_03_copies_show_up_in_search(self):
        run_steps(self, self.impl, [
            ('file_upload', ('/a', 5), ANY),
            ('file_copy', ('/a', '/b'), ANY),
            ('file_upload', ('/c', 9), ANY),
            ('file_search', ('/',), ['/c', '/a', '/b']),
            ('file_copy', ('/c', '/a'), ANY),
            ('file_search', ('/',), ['/a', '/c', '/b']),
        ])

    def test_level_2_case_04_empty_prefix_and_no_files(self):
        run_steps(self, self.impl, [
            ('file_search', ('',), []),
            ('file_upload', ('x', 1), ANY),
            ('file_search', ('',), ['x']),
        ])

    def test_level_2_case_05_randomized_sequence_29(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('file_copy', ('/n11', '/d.txt'), Raises(RuntimeError)),
            ('file_search', ('/n',), []),
            ('file_upload', ('/n11', 5), ANY),
            ('file_get', ('/n1',), None),
            ('file_upload', ('/a', 2), ANY),
            ('file_search', ('',), ['/n11', '/a']),
            ('file_search', ('/n',), ['/n11']),
            ('file_search', ('/a',), ['/a']),
            ('file_get', ('/n6',), None),
            ('file_get', ('/n5',), None),
            ('file_upload', ('/n13', 8), ANY),
            ('file_get', ('/b/c',), None),
            ('file_copy', ('/n9', '/n8'), Raises(RuntimeError)),
            ('file_get', ('/n7',), None),
            ('file_search', ('/n1',), ['/n13', '/n11']),
            ('file_get', ('/n9',), None),
            ('file_copy', ('/c', '/e'), Raises(RuntimeError)),
            ('file_get', ('/d.txt',), None),
            ('file_search', ('',), ['/n13', '/n11', '/a']),
            ('file_copy', ('/n11', '/n4'), ANY),
            ('file_upload', ('/n10', 1), ANY),
            ('file_copy', ('/n5', '/n13'), Raises(RuntimeError)),
            ('file_copy', ('/n13', '/a'), ANY),
            ('file_upload', ('/d.txt', 2), ANY),
            ('file_upload', ('/e', 2), ANY),
            ('file_copy', ('/n0', '/n0'), Raises(RuntimeError)),
            ('file_get', ('/n13',), 8),
            ('file_search', ('/',), ['/a', '/n13', '/n11', '/n4', '/d.txt', '/e', '/n10']),
            ('file_get', ('/n9',), None),
            ('file_search', ('',), ['/a', '/n13', '/n11', '/n4', '/d.txt', '/e', '/n10']),
            ('file_copy', ('/e', '/n9'), ANY),
            ('file_upload', ('/e', 8), Raises(RuntimeError)),
            ('file_search', ('',), ['/a', '/n13', '/n11', '/n4', '/d.txt', '/e', '/n9', '/n10']),
            ('file_get', ('/n0',), None),
            ('file_upload', ('/a', 3), Raises(RuntimeError)),
            ('file_upload', ('/n0', 2), ANY),
            ('file_upload', ('/n0', 2), Raises(RuntimeError)),
            ('file_upload', ('/n5', 1), ANY),
            ('file_copy', ('/n12', '/n7'), Raises(RuntimeError)),
            ('file_upload', ('/e', 8), Raises(RuntimeError)),
            ('file_upload', ('/n10', 2), Raises(RuntimeError)),
            ('file_search', ('',), ['/a', '/n13', '/n11', '/n4', '/d.txt', '/e', '/n0', '/n9', '/n10', '/n5']),
            ('file_copy', ('/c', '/n8'), Raises(RuntimeError)),
            ('file_upload', ('/n13', 1), Raises(RuntimeError)),
            ('file_search', ('/n1',), ['/n13', '/n11', '/n10']),
            ('file_upload', ('/n5', 3), Raises(RuntimeError)),
            ('file_get', ('/n3',), None),
            ('file_get', ('/n12',), None),
            ('file_get', ('/n0',), 2),
            ('file_copy', ('/n12', '/n4'), Raises(RuntimeError)),
        ])

    def test_level_2_case_06_randomized_sequence_30(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('file_copy', ('/n9', '/d.txt'), Raises(RuntimeError)),
            ('file_upload', ('/e', 2), ANY),
            ('file_search', ('',), ['/e']),
            ('file_get', ('/e',), 2),
            ('file_upload', ('/n2', 5), ANY),
            ('file_upload', ('/b', 2), ANY),
            ('file_upload', ('/n5', 8), ANY),
            ('file_get', ('/n12',), None),
            ('file_search', ('/b',), ['/b']),
            ('file_upload', ('/n2', 5), Raises(RuntimeError)),
            ('file_upload', ('/c', 3), ANY),
            ('file_copy', ('/c', '/n3'), ANY),
            ('file_copy', ('/e', '/b/c'), ANY),
            ('file_search', ('',), ['/n5', '/n2', '/c', '/n3', '/b', '/b/c', '/e']),
            ('file_copy', ('/n9', '/n4'), Raises(RuntimeError)),
            ('file_search', ('/n',), ['/n5', '/n2', '/n3']),
            ('file_upload', ('/n2', 2), Raises(RuntimeError)),
            ('file_upload', ('/n10', 1), ANY),
            ('file_search', ('/n1',), ['/n10']),
            ('file_search', ('/a',), []),
            ('file_upload', ('/b', 2), Raises(RuntimeError)),
            ('file_get', ('/n10',), 1),
            ('file_get', ('/n10',), 1),
            ('file_get', ('/n2',), 5),
            ('file_upload', ('/e', 1), Raises(RuntimeError)),
            ('file_get', ('/ab',), None),
            ('file_upload', ('/ab', 3), ANY),
            ('file_copy', ('/n5', '/n5'), ANY),
            ('file_search', ('/a',), ['/ab']),
            ('file_upload', ('/n7', 2), ANY),
            ('file_get', ('/n13',), None),
            ('file_search', ('/a',), ['/ab']),
            ('file_upload', ('/n12', 5), ANY),
            ('file_upload', ('/e', 5), Raises(RuntimeError)),
            ('file_upload', ('/b', 2), Raises(RuntimeError)),
            ('file_copy', ('/n9', '/b'), Raises(RuntimeError)),
            ('file_search', ('',), ['/n5', '/n12', '/n2', '/ab', '/c', '/n3', '/b', '/b/c', '/e', '/n7']),
            ('file_copy', ('/n3', '/n10'), ANY),
            ('file_copy', ('/c', '/b/c'), ANY),
            ('file_search', ('/n1',), ['/n12', '/n10']),
            ('file_copy', ('/e', '/b/c'), ANY),
            ('file_upload', ('/a', 1), ANY),
            ('file_upload', ('/d.txt', 5), ANY),
            ('file_copy', ('/n11', '/n8'), Raises(RuntimeError)),
            ('file_get', ('/b',), 2),
            ('file_upload', ('/n12', 8), Raises(RuntimeError)),
            ('file_upload', ('/n10', 1), Raises(RuntimeError)),
            ('file_upload', ('/c', 5), Raises(RuntimeError)),
            ('file_upload', ('/n13', 1), ANY),
            ('file_upload', ('/n9', 3), ANY),
        ])


if __name__ == "__main__":
    unittest.main()
