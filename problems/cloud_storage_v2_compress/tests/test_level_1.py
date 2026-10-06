"""
Level 1 tests for Cloud Storage v2.

Each test replays a sequence of calls on a fresh CloudStorageV2Impl() and checks
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


class TestLevel1(unittest.TestCase):
    def setUp(self):
        self.impl = CloudStorageV2Impl()

    def test_level_1_case_01_example_from_spec(self):
        """The Level 1 example table."""
        run_steps(self, self.impl, [
            ('add_file', ('/report.pdf', 500), True),
            ('add_file', ('/report.pdf', 200), False),
            ('get_file_size', ('/report.pdf',), 500),
            ('get_file_size', ('/missing.txt',), None),
            ('copy_file', ('/report.pdf', '/backup/report.pdf'), True),
            ('get_file_size', ('/backup/report.pdf',), 500),
            ('copy_file', ('/ghost.txt', '/out.txt'), False),
            ('copy_file', ('/report.pdf', '/backup/report.pdf'), False),
        ])

    def test_level_1_case_02_copy_does_not_overwrite(self):
        run_steps(self, self.impl, [
            ('add_file', ('/a', 1), True),
            ('add_file', ('/b', 2), True),
            ('copy_file', ('/a', '/b'), False),
            ('get_file_size', ('/b',), 2),
            ('copy_file', ('/b', '/c'), True),
            ('copy_file', ('/c', '/d'), True),
            ('get_file_size', ('/d',), 2),
        ])

    def test_level_1_case_03_copy_onto_itself_fails(self):
        run_steps(self, self.impl, [
            ('add_file', ('/a', 5), True),
            ('copy_file', ('/a', '/a'), False),
            ('get_file_size', ('/a',), 5),
        ])

    def test_level_1_case_04_copy_missing_source(self):
        run_steps(self, self.impl, [
            ('copy_file', ('/x', '/y'), False),
            ('get_file_size', ('/y',), None),
            ('add_file', ('/y', 3), True),
            ('copy_file', ('/x', '/y'), False),
            ('get_file_size', ('/y',), 3),
        ])

    def test_level_1_case_05_randomized_sequence_14(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('add_file', ('/b', 20), True),
            ('add_file', ('/a.txt', 20), True),
            ('copy_file', ('/b.txt.COMPRESSED', '/a.txt'), False),
            ('add_file', ('/a.COMPRESSED', 20), True),
            ('add_file', ('/ab', 20), True),
            ('add_file', ('/a.txt', 20), False),
            ('add_file', ('/b.txt', 25), True),
            ('add_file', ('/c.bin', 3), True),
            ('copy_file', ('/a.COMPRESSED', '/a.txt'), False),
            ('get_file_size', ('/c.bin',), 3),
            ('add_file', ('/b', 20), False),
            ('copy_file', ('/a.txt', '/a.txt'), False),
            ('add_file', ('/a.txt', 10), False),
            ('get_file_size', ('/a.txt',), 20),
            ('add_file', ('/ab', 25), False),
            ('add_file', ('/c.bin', 25), False),
            ('copy_file', ('/a.txt', '/c.bin'), False),
            ('add_file', ('/c.bin', 3), False),
            ('copy_file', ('/c.bin', '/c.bin'), False),
            ('add_file', ('/b.txt.COMPRESSED', 3), True),
            ('add_file', ('/a.COMPRESSED', 20), False),
            ('add_file', ('/b', 25), False),
            ('get_file_size', ('/a.txt',), 20),
            ('add_file', ('/b', 3), False),
            ('get_file_size', ('/b.txt',), 25),
            ('get_file_size', ('/a.txt',), 20),
            ('get_file_size', ('/b',), 20),
            ('add_file', ('/b.txt', 10), False),
            ('add_file', ('/a.COMPRESSED', 20), False),
            ('add_file', ('/ab', 20), False),
            ('copy_file', ('/b', '/a.COMPRESSED'), False),
            ('copy_file', ('/a', '/b.txt.COMPRESSED'), False),
            ('copy_file', ('/a.COMPRESSED', '/b.txt'), False),
            ('get_file_size', ('/ab',), 20),
            ('add_file', ('/ab', 20), False),
            ('copy_file', ('/ab', '/a'), True),
            ('get_file_size', ('/b.txt',), 25),
            ('copy_file', ('/b.txt.COMPRESSED', '/c.bin'), False),
            ('add_file', ('/ab', 10), False),
            ('add_file', ('/b', 3), False),
        ])


if __name__ == "__main__":
    unittest.main()
