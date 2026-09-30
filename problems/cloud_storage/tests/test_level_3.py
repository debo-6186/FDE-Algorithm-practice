"""
Level 3 tests for Cloud Storage.

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


class TestLevel3(unittest.TestCase):
    def setUp(self):
        self.impl = CloudStorageImpl()

    def test_level_3_case_01_example_from_spec(self):
        """The Level 3 example table."""
        run_steps(self, self.impl, [
            ('add_user', ('user1', 200), True),
            ('add_user', ('user1', 100), False),
            ('add_file_by', ('user1', '/dir/file.med', 50), 150),
            ('add_file_by', ('user1', '/big.blob', 140), 10),
            ('add_file_by', ('user1', '/file-small', 20), None),
            ('add_file', ('/dir/admin_file', 300), True),
            ('add_user', ('user2', 110), True),
            ('add_file_by', ('user2', '/dir/file.med', 45), None),
            ('add_file_by', ('user2', '/new_file', 50), 60),
            ('merge_user', ('user1', 'user2'), 70),
            ('add_file_by', ('user2', '/x', 1), None),
            ('add_file_by', ('user1', '/y', 70), 0),
            ('delete_file', ('/big.blob',), 140),
            ('add_file_by', ('user1', '/z', 100), 40),
        ])

    def test_level_3_case_02_exact_capacity_is_allowed(self):
        run_steps(self, self.impl, [
            ('add_user', ('u', 100), True),
            ('add_file_by', ('u', '/a', 100), 0),
            ('add_file_by', ('u', '/b', 1), None),
            ('delete_file', ('/a',), 100),
            ('add_file_by', ('u', '/b', 1), 99),
        ])

    def test_level_3_case_03_unknown_user(self):
        run_steps(self, self.impl, [
            ('add_file_by', ('ghost', '/a', 1), None),
            ('get_file_size', ('/a',), None),
            ('merge_user', ('ghost', 'ghost2'), None),
            ('add_user', ('real', 5), True),
            ('add_file_by', ('real', '/a', 5), 0),
            ('merge_user', ('real', 'ghost'), None),
            ('merge_user', ('ghost', 'real'), None),
        ])

    def test_level_3_case_04_admin_is_unlimited_and_reserved(self):
        run_steps(self, self.impl, [
            ('add_user', ('admin', 10), False),
            ('add_file', ('/huge', 1000000000000), True),
            ('add_user', ('u', 5), True),
            ('add_file_by', ('u', '/huge', 1), None),
            ('get_n_largest', ('/', 5), ['/huge(1000000000000)']),
        ])

    def test_level_3_case_05_merge_failures(self):
        run_steps(self, self.impl, [
            ('add_user', ('a', 10), True),
            ('merge_user', ('a', 'a'), None),
            ('merge_user', ('a', 'b'), None),
            ('merge_user', ('b', 'a'), None),
            ('add_file_by', ('a', '/f', 10), 0),
        ])

    def test_level_3_case_06_merge_adds_capacity_and_files(self):
        """After the merge, deleting a former user2 file frees user1's capacity."""
        run_steps(self, self.impl, [
            ('add_user', ('a', 100), True),
            ('add_user', ('b', 50), True),
            ('add_file_by', ('a', '/a1', 60), 40),
            ('add_file_by', ('b', '/b1', 50), 0),
            ('merge_user', ('a', 'b'), 40),
            ('add_user', ('b', 1), True),
            ('delete_file', ('/b1',), 50),
            ('add_file_by', ('a', '/a2', 90), 0),
            ('add_file_by', ('b', '/b2', 1), 0),
        ])

    def test_level_3_case_07_failed_add_does_not_use_capacity(self):
        run_steps(self, self.impl, [
            ('add_user', ('u', 10), True),
            ('add_file', ('/taken', 3), True),
            ('add_file_by', ('u', '/taken', 3), None),
            ('add_file_by', ('u', '/big', 11), None),
            ('add_file_by', ('u', '/ok', 10), 0),
        ])

    def test_level_3_case_08_stats_include_all_owners(self):
        run_steps(self, self.impl, [
            ('add_user', ('u', 100), True),
            ('add_file_by', ('u', '/u/file', 30), 70),
            ('add_file', ('/admin/file', 30), True),
            ('get_n_largest', ('/', 5), ['/admin/file(30)', '/u/file(30)']),
        ])

    def test_level_3_case_09_randomized_sequence_35(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('get_n_largest', ('/z', 1), []),
            ('get_file_size', ('/ab',), None),
            ('add_file_by', ('u3', '/ab', 10), None),
            ('add_file_by', ('u1', '/c/d/e', 10), None),
            ('add_file', ('/c.txt', 5), True),
            ('add_file_by', ('u3', '/b', 5), None),
            ('delete_file', ('/ba',), None),
            ('get_file_size', ('/b',), None),
            ('delete_file', ('/c/d/e',), None),
            ('add_file_by', ('u2', '/a/b', 10), None),
            ('add_user', ('admin', 100), False),
            ('delete_file', ('/c/d/e',), None),
            ('get_file_size', ('/c/d/e',), None),
            ('add_user', ('u3', 100), True),
            ('add_file', ('/b/a', 10), True),
            ('get_n_largest', ('/c', 1), ['/c.txt(5)']),
            ('get_file_size', ('/c/d/e',), None),
            ('merge_user', ('u1', 'u3'), None),
            ('add_file', ('/a/b.txt', 20), True),
            ('add_user', ('u2', 80), True),
            ('get_n_largest', ('/a/', 4), ['/a/b.txt(20)']),
            ('add_file_by', ('u3', '/ab', 25), 75),
            ('add_file', ('/c/d/e', 10), True),
            ('get_n_largest', ('', 4), ['/ab(25)', '/a/b.txt(20)', '/b/a(10)', '/c/d/e(10)']),
            ('add_user', ('admin', 30), False),
            ('get_n_largest', ('', 1), ['/ab(25)']),
            ('add_file_by', ('u3', '/b', 25), 50),
            ('add_file', ('/ba', 10), True),
            ('add_file_by', ('u1', '/ab', 10), None),
            ('get_n_largest', ('/a/', 4), ['/a/b.txt(20)']),
            ('add_file_by', ('u3', '/a/b.txt', 40), None),
            ('add_file', ('/b', 5), False),
            ('add_file_by', ('u1', '/c.txt', 40), None),
            ('add_file_by', ('u1', '/ba', 10), None),
            ('get_file_size', ('/a/c',), None),
            ('get_file_size', ('/c.txt',), 5),
            ('get_n_largest', ('', 3), ['/ab(25)', '/b(25)', '/a/b.txt(20)']),
            ('merge_user', ('u1', 'u3'), None),
            ('add_file', ('/c/d/e', 40), False),
            ('get_n_largest', ('/c', 1), ['/c/d/e(10)']),
            ('delete_file', ('/b',), 25),
            ('add_file', ('/ba', 10), False),
            ('add_file', ('/b/a', 40), False),
            ('get_n_largest', ('/z', 3), []),
            ('get_n_largest', ('/', 5), ['/ab(25)', '/a/b.txt(20)', '/b/a(10)', '/ba(10)', '/c/d/e(10)']),
            ('add_file_by', ('u2', '/ba', 5), None),
            ('delete_file', ('/b',), None),
            ('add_file', ('/c/d/e', 5), False),
            ('add_file', ('/c.txt', 25), False),
            ('add_file_by', ('u1', '/c/d/e', 10), None),
            ('add_file_by', ('u3', '/ba', 40), None),
            ('delete_file', ('/b/a',), 10),
            ('add_file', ('/c/d/e', 5), False),
            ('add_file', ('/a/c', 10), True),
            ('add_file', ('/b/a', 40), True),
            ('add_file', ('/b', 10), True),
            ('add_file_by', ('u2', '/ab', 10), None),
            ('add_file', ('/ba', 10), False),
            ('add_file', ('/ba', 40), False),
            ('get_n_largest', ('/b', 1), ['/b/a(40)']),
            ('add_user', ('u2', 50), False),
            ('get_file_size', ('/a/c',), 10),
            ('add_file', ('/ab', 10), False),
            ('add_file_by', ('u3', '/ab', 10), None),
            ('get_n_largest', ('/c', 2), ['/c/d/e(10)', '/c.txt(5)']),
            ('delete_file', ('/ba',), 10),
            ('get_file_size', ('/c/d/e',), 10),
            ('merge_user', ('u2', 'u1'), None),
            ('add_user', ('u2', 50), False),
            ('add_file', ('/ab', 20), False),
        ])

    def test_level_3_case_10_randomized_sequence_36(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('delete_file', ('/a',), None),
            ('add_file', ('/a/b.txt', 10), True),
            ('add_file_by', ('u2', '/b/a', 25), None),
            ('get_file_size', ('/a/b',), None),
            ('add_file_by', ('u2', '/b/a', 20), None),
            ('add_file_by', ('u1', '/b/a', 5), None),
            ('get_n_largest', ('/', 3), ['/a/b.txt(10)']),
            ('add_file_by', ('u3', '/b', 25), None),
            ('add_file', ('/c/d/e', 20), True),
            ('add_file', ('/a/c', 10), True),
            ('add_file_by', ('u3', '/ba', 10), None),
            ('add_user', ('admin', 80), False),
            ('get_n_largest', ('/', 4), ['/c/d/e(20)', '/a/b.txt(10)', '/a/c(10)']),
            ('add_file', ('/a/b', 10), True),
            ('merge_user', ('u3', 'u1'), None),
            ('add_user', ('u3', 30), True),
            ('add_file', ('/ba', 10), True),
            ('add_file_by', ('u1', '/b', 10), None),
            ('add_file_by', ('u3', '/a/b.txt', 40), None),
            ('add_file', ('/ab', 10), True),
            ('add_file', ('/ab', 25), False),
            ('merge_user', ('u2', 'u2'), None),
            ('add_file_by', ('u3', '/b/a', 5), 25),
            ('delete_file', ('/b/a',), 5),
            ('delete_file', ('/a/c',), 10),
            ('get_n_largest', ('', 1), ['/c/d/e(20)']),
            ('get_n_largest', ('/a/', 0), []),
            ('add_user', ('u1', 80), True),
            ('get_file_size', ('/a/c',), None),
            ('get_n_largest', ('/a', 0), []),
            ('get_n_largest', ('/a/', 3), ['/a/b(10)', '/a/b.txt(10)']),
            ('add_file_by', ('u3', '/a/b.txt', 25), None),
            ('merge_user', ('u3', 'u1'), 110),
            ('add_file_by', ('u3', '/a/b', 25), None),
            ('add_file_by', ('u1', '/ab', 40), None),
            ('add_user', ('u1', 100), True),
            ('add_file', ('/c.txt', 25), True),
            ('add_file', ('/c.txt', 20), False),
            ('add_file', ('/b/a', 40), True),
            ('add_file_by', ('u1', '/b/a', 25), None),
            ('get_n_largest', ('/c', 1), ['/c.txt(25)']),
            ('add_file', ('/a/b.txt', 20), False),
            ('add_file_by', ('u2', '/b/a', 25), None),
            ('add_file', ('/a/b', 40), False),
            ('get_n_largest', ('/a/', 4), ['/a/b(10)', '/a/b.txt(10)']),
            ('add_user', ('u3', 80), False),
            ('add_file', ('/c.txt', 40), False),
            ('merge_user', ('u2', 'u2'), None),
            ('get_file_size', ('/ab',), 10),
            ('get_file_size', ('/b',), None),
            ('delete_file', ('/ab',), 10),
            ('add_file', ('/b/a', 20), False),
            ('add_file_by', ('u1', '/b/a', 20), None),
            ('add_user', ('u3', 30), False),
            ('add_file', ('/ba', 40), False),
            ('add_file_by', ('u2', '/c/d/e', 40), None),
            ('add_file', ('/c.txt', 10), False),
            ('get_n_largest', ('/a/', 5), ['/a/b(10)', '/a/b.txt(10)']),
            ('add_file_by', ('u3', '/b/a', 40), None),
            ('add_file', ('/b/a', 10), False),
            ('add_file', ('/b/a', 25), False),
            ('add_file', ('/ba', 10), False),
            ('get_n_largest', ('/a', 5), ['/a/b(10)', '/a/b.txt(10)']),
            ('add_file', ('/c/d/e', 5), False),
            ('add_file', ('/c/d/e', 20), False),
            ('delete_file', ('/b',), None),
            ('get_file_size', ('/ab',), None),
            ('delete_file', ('/a/c',), None),
            ('add_file_by', ('u1', '/ba', 40), None),
            ('add_file', ('/b/a', 20), False),
        ])


if __name__ == "__main__":
    unittest.main()
