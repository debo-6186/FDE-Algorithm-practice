"""
Level 1 tests for Cloud Storage.

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

from cloud_storage_impl import CloudStorageImpl

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
        self.impl = CloudStorageImpl()

    def test_level_1_case_01_example_from_spec(self):
        """The Level 1 example table."""
        run_steps(self, self.impl, [
            ('add_file', ('/a.txt', 10), True),
            ('add_file', ('/a.txt', 5), False),
            ('get_file_size', ('/a.txt',), 10),
            ('get_file_size', ('/b.txt',), None),
            ('delete_file', ('/b.txt',), None),
            ('delete_file', ('/a.txt',), 10),
            ('get_file_size', ('/a.txt',), None),
            ('add_file', ('/a.txt', 7), True),
        ])

    def test_level_1_case_02_names_are_case_sensitive_plain_strings(self):
        run_steps(self, self.impl, [
            ('add_file', ('/Dir/File', 1), True),
            ('add_file', ('/dir/file', 2), True),
            ('add_file', ('/dir/file ', 3), True),
            ('get_file_size', ('/dir/file',), 2),
            ('get_file_size', ('/Dir/File',), 1),
            ('get_file_size', ('/dir/file ',), 3),
            ('get_file_size', ('/dir',), None),
        ])

    def test_level_1_case_03_delete_twice(self):
        run_steps(self, self.impl, [
            ('add_file', ('/x', 42), True),
            ('delete_file', ('/x',), 42),
            ('delete_file', ('/x',), None),
            ('get_file_size', ('/x',), None),
        ])

    def test_level_1_case_04_failed_add_keeps_original_size(self):
        run_steps(self, self.impl, [
            ('add_file', ('/data.bin', 100), True),
            ('add_file', ('/data.bin', 999), False),
            ('get_file_size', ('/data.bin',), 100),
        ])

    def test_level_1_case_05_many_files(self):
        run_steps(self, self.impl, [
            ('add_file', ('/f1', 1), True),
            ('add_file', ('/f2', 2), True),
            ('add_file', ('/f3', 3), True),
            ('delete_file', ('/f2',), 2),
            ('get_file_size', ('/f1',), 1),
            ('get_file_size', ('/f3',), 3),
            ('add_file', ('/f2', 20), True),
            ('get_file_size', ('/f2',), 20),
        ])

    def test_level_1_case_06_randomized_sequence_13(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('add_file', ('/a/b.txt', 10), True),
            ('get_file_size', ('/a/c',), None),
            ('add_file', ('/a/b', 10), True),
            ('get_file_size', ('/a',), None),
            ('delete_file', ('/c/d/e',), None),
            ('delete_file', ('/a/b',), 10),
            ('get_file_size', ('/a/b.txt',), 10),
            ('delete_file', ('/ba',), None),
            ('delete_file', ('/b',), None),
            ('add_file', ('/a/b', 25), True),
            ('delete_file', ('/ab',), None),
            ('get_file_size', ('/a/b.txt',), 10),
            ('get_file_size', ('/c.txt',), None),
            ('add_file', ('/c.txt', 10), True),
            ('add_file', ('/ab', 10), True),
            ('add_file', ('/a/b.txt', 20), False),
            ('get_file_size', ('/c/d/e',), None),
            ('get_file_size', ('/a/b.txt',), 10),
            ('get_file_size', ('/ba',), None),
            ('get_file_size', ('/a',), None),
            ('add_file', ('/ba', 10), True),
            ('add_file', ('/b/a', 10), True),
            ('delete_file', ('/b',), None),
            ('delete_file', ('/b',), None),
            ('get_file_size', ('/c/d/e',), None),
            ('add_file', ('/c/d/e', 25), True),
            ('get_file_size', ('/a',), None),
            ('get_file_size', ('/b',), None),
            ('add_file', ('/c.txt', 10), False),
            ('add_file', ('/b/a', 25), False),
            ('get_file_size', ('/c.txt',), 10),
            ('delete_file', ('/b',), None),
            ('get_file_size', ('/a/b.txt',), 10),
            ('add_file', ('/ab', 25), False),
            ('get_file_size', ('/ba',), 10),
            ('delete_file', ('/a',), None),
            ('add_file', ('/ba', 25), False),
            ('get_file_size', ('/ba',), 10),
            ('add_file', ('/a', 25), True),
            ('get_file_size', ('/a/b.txt',), 10),
        ])


if __name__ == "__main__":
    unittest.main()
