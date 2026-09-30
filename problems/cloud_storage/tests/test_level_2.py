"""
Level 2 tests for Cloud Storage.

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


class TestLevel2(unittest.TestCase):
    def setUp(self):
        self.impl = CloudStorageImpl()

    def test_level_2_case_01_example_from_spec(self):
        """The Level 2 example table."""
        run_steps(self, self.impl, [
            ('add_file', ('/photos/cat.png', 300), True),
            ('add_file', ('/photos/dog.png', 500), True),
            ('add_file', ('/photos/2024/beach.jpg', 450), True),
            ('add_file', ('/music/song.mp3', 500), True),
            ('get_n_largest', ('/photos', 2), ['/photos/dog.png(500)', '/photos/2024/beach.jpg(450)']),
            ('get_n_largest', ('/photos/c', 5), ['/photos/cat.png(300)']),
            ('get_n_largest', ('/videos', 3), []),
            ('get_n_largest', ('/', 3), ['/music/song.mp3(500)', '/photos/dog.png(500)', '/photos/2024/beach.jpg(450)']),
        ])

    def test_level_2_case_02_empty_storage_then_one_file(self):
        run_steps(self, self.impl, [
            ('get_n_largest', ('', 5), []),
            ('get_n_largest', ('/', 1), []),
            ('add_file', ('/x', 1), True),
            ('get_n_largest', ('/', 1), ['/x(1)']),
        ])

    def test_level_2_case_03_empty_prefix_matches_everything(self):
        run_steps(self, self.impl, [
            ('add_file', ('b', 1), True),
            ('add_file', ('a', 1), True),
            ('add_file', ('c', 2), True),
            ('get_n_largest', ('', 10), ['c(2)', 'a(1)', 'b(1)']),
        ])

    def test_level_2_case_04_prefix_is_not_substring(self):
        """'/dir' must be at the start of the name."""
        run_steps(self, self.impl, [
            ('add_file', ('/dir/a', 5), True),
            ('add_file', ('/x/dir/b', 50), True),
            ('add_file', ('/dirty', 7), True),
            ('get_n_largest', ('/dir', 5), ['/dirty(7)', '/dir/a(5)']),
            ('get_n_largest', ('/dir/', 5), ['/dir/a(5)']),
        ])

    def test_level_2_case_05_deleted_files_disappear_from_stats(self):
        run_steps(self, self.impl, [
            ('add_file', ('/a', 10), True),
            ('add_file', ('/b', 20), True),
            ('delete_file', ('/b',), 20),
            ('get_n_largest', ('/', 2), ['/a(10)']),
            ('add_file', ('/b', 5), True),
            ('get_n_largest', ('/', 2), ['/a(10)', '/b(5)']),
        ])

    def test_level_2_case_06_n_zero(self):
        run_steps(self, self.impl, [
            ('add_file', ('/a', 1), True),
            ('get_n_largest', ('/', 0), []),
        ])

    def test_level_2_case_07_randomized_sequence_25(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('get_file_size', ('/a',), None),
            ('delete_file', ('/a',), None),
            ('add_file', ('/b/a', 25), True),
            ('get_n_largest', ('/z', 1), []),
            ('get_file_size', ('/c/d/e',), None),
            ('delete_file', ('/c.txt',), None),
            ('add_file', ('/a/b', 25), True),
            ('add_file', ('/b', 40), True),
            ('add_file', ('/ba', 5), True),
            ('get_file_size', ('/a/b',), 25),
            ('add_file', ('/a', 10), True),
            ('add_file', ('/c/d/e', 20), True),
            ('get_n_largest', ('/b', 4), ['/b(40)', '/b/a(25)', '/ba(5)']),
            ('delete_file', ('/ba',), 5),
            ('add_file', ('/a', 20), False),
            ('delete_file', ('/ba',), None),
            ('get_n_largest', ('/a', 0), []),
            ('get_n_largest', ('/c', 1), ['/c/d/e(20)']),
            ('get_n_largest', ('/z', 2), []),
            ('add_file', ('/c/d/e', 25), False),
            ('get_file_size', ('/b',), 40),
            ('get_file_size', ('/ba',), None),
            ('get_file_size', ('/b/a',), 25),
            ('get_n_largest', ('/a', 0), []),
            ('delete_file', ('/c/d/e',), 20),
            ('delete_file', ('/a/b.txt',), None),
            ('add_file', ('/a/b', 10), False),
            ('delete_file', ('/a',), 10),
            ('get_n_largest', ('/b', 2), ['/b(40)', '/b/a(25)']),
            ('add_file', ('/b/a', 25), False),
            ('delete_file', ('/a/b.txt',), None),
            ('add_file', ('/a/b', 5), False),
            ('delete_file', ('/a/c',), None),
            ('get_n_largest', ('/b', 0), []),
            ('add_file', ('/a/b.txt', 10), True),
            ('add_file', ('/a/b', 5), False),
            ('add_file', ('/ba', 10), True),
            ('get_n_largest', ('/a', 0), []),
            ('get_n_largest', ('/b', 2), ['/b(40)', '/b/a(25)']),
            ('add_file', ('/ab', 40), True),
            ('delete_file', ('/a/b.txt',), 10),
            ('get_n_largest', ('/a', 4), ['/ab(40)', '/a/b(25)']),
            ('add_file', ('/ba', 10), False),
            ('get_n_largest', ('', 1), ['/ab(40)']),
            ('add_file', ('/a/b', 25), False),
            ('get_file_size', ('/a',), None),
            ('delete_file', ('/b',), 40),
            ('get_n_largest', ('', 0), []),
            ('get_n_largest', ('/c', 5), []),
            ('get_n_largest', ('/z', 0), []),
        ])

    def test_level_2_case_08_randomized_sequence_26(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('get_n_largest', ('/a/', 4), []),
            ('get_file_size', ('/a/b.txt',), None),
            ('get_n_largest', ('/c', 3), []),
            ('get_n_largest', ('/z', 5), []),
            ('get_n_largest', ('/', 1), []),
            ('add_file', ('/ba', 10), True),
            ('add_file', ('/c/d/e', 5), True),
            ('get_n_largest', ('', 4), ['/ba(10)', '/c/d/e(5)']),
            ('add_file', ('/a', 25), True),
            ('delete_file', ('/b',), None),
            ('get_file_size', ('/a/c',), None),
            ('add_file', ('/c/d/e', 20), False),
            ('delete_file', ('/a/b.txt',), None),
            ('add_file', ('/c.txt', 40), True),
            ('get_n_largest', ('/a', 4), ['/a(25)']),
            ('get_n_largest', ('', 3), ['/c.txt(40)', '/a(25)', '/ba(10)']),
            ('get_n_largest', ('/b', 0), []),
            ('add_file', ('/a/b', 10), True),
            ('get_n_largest', ('/a', 4), ['/a(25)', '/a/b(10)']),
            ('get_n_largest', ('/a/', 4), ['/a/b(10)']),
            ('get_file_size', ('/a',), 25),
            ('delete_file', ('/c.txt',), 40),
            ('get_n_largest', ('/', 4), ['/a(25)', '/a/b(10)', '/ba(10)', '/c/d/e(5)']),
            ('add_file', ('/a', 5), False),
            ('add_file', ('/b/a', 5), True),
            ('add_file', ('/a/b', 25), False),
            ('get_n_largest', ('/b', 0), []),
            ('get_n_largest', ('/c', 5), ['/c/d/e(5)']),
            ('delete_file', ('/b/a',), 5),
            ('add_file', ('/a/c', 10), True),
            ('add_file', ('/a/b.txt', 25), True),
            ('get_n_largest', ('/c', 0), []),
            ('get_file_size', ('/a/b',), 10),
            ('get_n_largest', ('/a/', 1), ['/a/b.txt(25)']),
            ('add_file', ('/a/c', 10), False),
            ('get_file_size', ('/a/c',), 10),
            ('add_file', ('/c.txt', 5), True),
            ('add_file', ('/a/c', 5), False),
            ('add_file', ('/a/b.txt', 25), False),
            ('get_n_largest', ('/b', 0), []),
            ('add_file', ('/ba', 5), False),
            ('get_file_size', ('/a/c',), 10),
            ('add_file', ('/c.txt', 10), False),
            ('add_file', ('/a/c', 25), False),
            ('get_file_size', ('/c/d/e',), 5),
            ('add_file', ('/ab', 40), True),
            ('add_file', ('/c/d/e', 5), False),
            ('get_n_largest', ('/b', 2), ['/ba(10)']),
            ('add_file', ('/ab', 10), False),
            ('delete_file', ('/c.txt',), 5),
        ])


if __name__ == "__main__":
    unittest.main()
