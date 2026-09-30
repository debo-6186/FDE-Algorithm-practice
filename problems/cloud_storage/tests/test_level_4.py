"""
Level 4 tests for Cloud Storage.

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


class TestLevel4(unittest.TestCase):
    def setUp(self):
        self.impl = CloudStorageImpl()

    def test_level_4_case_01_example_from_spec(self):
        """The Level 4 example table."""
        run_steps(self, self.impl, [
            ('add_user', ('user', 100), True),
            ('add_file_by', ('user', '/dir/file1', 50), 50),
            ('add_file_by', ('user', '/file2.txt', 30), 20),
            ('restore_user', ('user',), 0),
            ('get_file_size', ('/dir/file1',), None),
            ('add_file_by', ('user', '/file3.mp4', 60), 40),
            ('add_file_by', ('user', '/file4.txt', 10), 30),
            ('backup_user', ('user',), 2),
            ('delete_file', ('/file3.mp4',), 60),
            ('delete_file', ('/file4.txt',), 10),
            ('add_file', ('/file3.mp4', 5), True),
            ('add_file_by', ('user', '/dir/file5.new', 20), 80),
            ('restore_user', ('user',), 1),
            ('get_file_size', ('/dir/file5.new',), None),
            ('get_file_size', ('/file4.txt',), 10),
            ('get_file_size', ('/file3.mp4',), 5),
            ('add_file_by', ('user', '/f', 90), 0),
            ('backup_user', ('nobody',), None),
            ('restore_user', ('nobody',), None),
        ])

    def test_level_4_case_02_backup_is_a_snapshot(self):
        """Changes after the backup must not leak into it."""
        run_steps(self, self.impl, [
            ('add_user', ('u', 100), True),
            ('add_file_by', ('u', '/a', 10), 90),
            ('backup_user', ('u',), 1),
            ('delete_file', ('/a',), 10),
            ('add_file_by', ('u', '/a', 99), 1),
            ('restore_user', ('u',), 1),
            ('get_file_size', ('/a',), 10),
            ('add_file_by', ('u', '/b', 90), 0),
        ])

    def test_level_4_case_03_new_backup_overwrites_old(self):
        run_steps(self, self.impl, [
            ('add_user', ('u', 100), True),
            ('add_file_by', ('u', '/a', 10), 90),
            ('backup_user', ('u',), 1),
            ('add_file_by', ('u', '/b', 20), 70),
            ('backup_user', ('u',), 2),
            ('delete_file', ('/a',), 10),
            ('delete_file', ('/b',), 20),
            ('restore_user', ('u',), 2),
            ('get_file_size', ('/b',), 20),
        ])

    def test_level_4_case_04_restore_can_be_repeated(self):
        run_steps(self, self.impl, [
            ('add_user', ('u', 100), True),
            ('add_file_by', ('u', '/a', 10), 90),
            ('backup_user', ('u',), 1),
            ('restore_user', ('u',), 1),
            ('delete_file', ('/a',), 10),
            ('restore_user', ('u',), 1),
            ('get_file_size', ('/a',), 10),
        ])

    def test_level_4_case_05_empty_backup_restores_nothing(self):
        run_steps(self, self.impl, [
            ('add_user', ('u', 100), True),
            ('backup_user', ('u',), 0),
            ('add_file_by', ('u', '/a', 10), 90),
            ('restore_user', ('u',), 0),
            ('get_file_size', ('/a',), None),
            ('add_file_by', ('u', '/b', 100), 0),
        ])

    def test_level_4_case_06_merged_user_backup_is_deleted(self):
        """user2's backup goes away with user2; user1's backup is unchanged."""
        run_steps(self, self.impl, [
            ('add_user', ('a', 100), True),
            ('add_user', ('b', 100), True),
            ('add_file_by', ('a', '/a1', 10), 90),
            ('add_file_by', ('b', '/b1', 20), 80),
            ('backup_user', ('a',), 1),
            ('backup_user', ('b',), 1),
            ('merge_user', ('a', 'b'), 170),
            ('restore_user', ('b',), None),
            ('add_user', ('b', 5), True),
            ('restore_user', ('b',), 0),
            ('restore_user', ('a',), 1),
            ('get_file_size', ('/b1',), None),
            ('get_file_size', ('/a1',), 10),
            ('add_file_by', ('a', '/big', 190), 0),
        ])

    def test_level_4_case_07_recreated_user_does_not_inherit_old_backup(self):
        """A new user with a merged user's id starts without a backup."""
        run_steps(self, self.impl, [
            ('add_user', ('a', 100), True),
            ('add_user', ('b', 100), True),
            ('add_file_by', ('b', '/old', 10), 90),
            ('backup_user', ('b',), 1),
            ('merge_user', ('a', 'b'), 190),
            ('delete_file', ('/old',), 10),
            ('add_user', ('b', 50), True),
            ('restore_user', ('b',), 0),
            ('get_file_size', ('/old',), None),
        ])

    def test_level_4_case_08_restore_skips_names_taken_by_other_users(self):
        run_steps(self, self.impl, [
            ('add_user', ('a', 100), True),
            ('add_user', ('b', 100), True),
            ('add_file_by', ('a', '/shared', 10), 90),
            ('add_file_by', ('a', '/mine', 5), 85),
            ('backup_user', ('a',), 2),
            ('delete_file', ('/shared',), 10),
            ('add_file_by', ('b', '/shared', 40), 60),
            ('restore_user', ('a',), 1),
            ('get_file_size', ('/shared',), 40),
            ('get_n_largest', ('/', 5), ['/shared(40)', '/mine(5)']),
        ])

    def test_level_4_case_09_randomized_sequence_47(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('get_n_largest', ('/b', 2), []),
            ('delete_file', ('/b/a',), None),
            ('add_file', ('/b/a', 5), True),
            ('restore_user', ('u2',), None),
            ('add_file_by', ('u2', '/a', 25), None),
            ('get_n_largest', ('/a', 3), []),
            ('restore_user', ('u3',), None),
            ('add_file_by', ('u3', '/b', 10), None),
            ('add_file_by', ('u1', '/a/c', 40), None),
            ('backup_user', ('u1',), None),
            ('add_file', ('/c/d/e', 25), True),
            ('add_user', ('u2', 80), True),
            ('get_file_size', ('/a/b',), None),
            ('get_n_largest', ('/a', 2), []),
            ('add_user', ('admin', 80), False),
            ('restore_user', ('u1',), None),
            ('add_file', ('/a/c', 20), True),
            ('delete_file', ('/c/d/e',), 25),
            ('get_n_largest', ('/z', 0), []),
            ('add_file', ('/c.txt', 25), True),
            ('add_user', ('u3', 100), True),
            ('backup_user', ('u1',), None),
            ('get_file_size', ('/b',), None),
            ('get_file_size', ('/ba',), None),
            ('add_file', ('/c/d/e', 25), True),
            ('get_n_largest', ('/c', 0), []),
            ('get_n_largest', ('', 1), ['/c.txt(25)']),
            ('get_file_size', ('/c.txt',), 25),
            ('add_file_by', ('u3', '/ba', 20), 80),
            ('add_file_by', ('u3', '/a', 5), 75),
            ('get_file_size', ('/a/b.txt',), None),
            ('add_file_by', ('u3', '/a', 10), None),
            ('add_file_by', ('u1', '/b/a', 5), None),
            ('add_file', ('/a', 10), False),
            ('get_file_size', ('/c.txt',), 25),
            ('add_file_by', ('u3', '/ab', 25), 50),
            ('add_file', ('/ba', 25), False),
            ('add_file', ('/a/b', 20), True),
            ('get_n_largest', ('/b', 1), ['/ba(20)']),
            ('add_file', ('/c.txt', 20), False),
            ('add_file_by', ('u1', '/ba', 20), None),
            ('merge_user', ('u1', 'u3'), None),
            ('add_user', ('u3', 50), False),
            ('add_user', ('admin', 100), False),
            ('restore_user', ('u3',), 0),
            ('add_file_by', ('u3', '/a', 10), 90),
            ('merge_user', ('u1', 'u3'), None),
            ('add_user', ('admin', 80), False),
            ('add_file_by', ('u3', '/b/a', 10), None),
            ('add_file_by', ('u1', '/a/b', 25), None),
            ('merge_user', ('u2', 'u2'), None),
            ('backup_user', ('u3',), 1),
            ('get_n_largest', ('/z', 0), []),
            ('restore_user', ('u2',), 0),
            ('delete_file', ('/ba',), None),
            ('get_n_largest', ('', 1), ['/c.txt(25)']),
            ('add_file_by', ('u1', '/a', 20), None),
            ('backup_user', ('u2',), 0),
            ('merge_user', ('u2', 'u2'), None),
            ('add_file', ('/a/b.txt', 10), True),
            ('add_user', ('u3', 80), False),
            ('add_file_by', ('u3', '/c/d/e', 20), None),
            ('backup_user', ('u3',), 1),
            ('add_file_by', ('u2', '/c/d/e', 25), None),
            ('add_file_by', ('u1', '/b/a', 10), None),
            ('add_file_by', ('u3', '/a/b.txt', 5), None),
            ('add_user', ('u2', 100), False),
            ('add_file', ('/a/b.txt', 5), False),
            ('add_file_by', ('u2', '/a', 20), None),
            ('add_file_by', ('u3', '/b', 5), 85),
            ('add_user', ('admin', 30), False),
            ('backup_user', ('u3',), 2),
            ('add_user', ('u3', 100), False),
            ('add_file_by', ('u2', '/a/c', 20), None),
            ('backup_user', ('u3',), 2),
            ('delete_file', ('/a/b',), 20),
            ('add_file_by', ('u2', '/a/b', 5), 75),
            ('get_n_largest', ('/b', 5), ['/b(5)', '/b/a(5)']),
            ('get_file_size', ('/ab',), None),
            ('add_user', ('u3', 50), False),
            ('add_user', ('admin', 30), False),
            ('add_file_by', ('u3', '/b/a', 10), None),
            ('add_file_by', ('u2', '/c.txt', 5), None),
            ('get_n_largest', ('/', 1), ['/c.txt(25)']),
            ('add_file', ('/c.txt', 40), False),
            ('add_file', ('/a/b', 25), False),
            ('get_n_largest', ('/a', 4), ['/a/c(20)', '/a(10)', '/a/b.txt(10)', '/a/b(5)']),
            ('add_file_by', ('u1', '/b', 40), None),
            ('delete_file', ('/a',), 10),
            ('add_file', ('/b', 10), False),
        ])

    def test_level_4_case_10_randomized_sequence_48(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('add_file_by', ('u3', '/a/b.txt', 40), None),
            ('add_user', ('admin', 50), False),
            ('add_file', ('/a/b', 40), True),
            ('get_file_size', ('/c.txt',), None),
            ('add_file', ('/a/c', 5), True),
            ('get_n_largest', ('/', 1), ['/a/b(40)']),
            ('add_file', ('/c.txt', 10), True),
            ('add_file_by', ('u1', '/a/b', 10), None),
            ('delete_file', ('/a',), None),
            ('add_file_by', ('u3', '/b', 20), None),
            ('get_file_size', ('/b/a',), None),
            ('add_file', ('/a/b', 25), False),
            ('delete_file', ('/ba',), None),
            ('add_file_by', ('u1', '/a/c', 10), None),
            ('add_user', ('u1', 80), True),
            ('get_n_largest', ('/c', 5), ['/c.txt(10)']),
            ('get_n_largest', ('/', 2), ['/a/b(40)', '/c.txt(10)']),
            ('get_file_size', ('/c/d/e',), None),
            ('merge_user', ('u1', 'u1'), None),
            ('add_file', ('/c/d/e', 40), True),
            ('get_n_largest', ('/b', 3), []),
            ('add_file_by', ('u2', '/a', 25), None),
            ('delete_file', ('/a/b',), 40),
            ('add_file_by', ('u2', '/b', 5), None),
            ('add_file_by', ('u2', '/c/d/e', 25), None),
            ('backup_user', ('u1',), 0),
            ('backup_user', ('u2',), None),
            ('get_file_size', ('/a/b',), None),
            ('add_file_by', ('u2', '/a/c', 5), None),
            ('get_n_largest', ('/a', 4), ['/a/c(5)']),
            ('add_file', ('/b', 40), True),
            ('get_n_largest', ('/z', 0), []),
            ('add_file_by', ('u1', '/a/b', 10), 70),
            ('backup_user', ('u1',), 1),
            ('get_file_size', ('/b',), 40),
            ('add_file_by', ('u1', '/b/a', 5), 65),
            ('add_file_by', ('u2', '/a/b', 25), None),
            ('add_file', ('/ab', 25), True),
            ('add_file', ('/a/b', 5), False),
            ('add_file', ('/b/a', 25), False),
            ('get_n_largest', ('/c', 2), ['/c/d/e(40)', '/c.txt(10)']),
            ('add_file_by', ('u1', '/ba', 10), 55),
            ('add_file', ('/ba', 10), False),
            ('add_file_by', ('u1', '/a/b', 5), None),
            ('get_file_size', ('/a/b',), 10),
            ('add_file', ('/c.txt', 25), False),
            ('add_file', ('/b', 10), False),
            ('add_user', ('u1', 30), False),
            ('get_n_largest', ('/a', 0), []),
            ('add_file', ('/a', 5), True),
            ('add_file_by', ('u2', '/a/c', 5), None),
            ('add_file', ('/ba', 40), False),
            ('get_file_size', ('/a/b',), 10),
            ('delete_file', ('/c.txt',), 10),
            ('delete_file', ('/b',), 40),
            ('add_file_by', ('u2', '/c.txt', 10), None),
            ('backup_user', ('u2',), None),
            ('add_file_by', ('u3', '/c.txt', 10), None),
            ('get_n_largest', ('/', 3), ['/c/d/e(40)', '/ab(25)', '/a/b(10)']),
            ('add_user', ('u2', 80), True),
            ('get_n_largest', ('/b', 3), ['/ba(10)', '/b/a(5)']),
            ('get_n_largest', ('', 3), ['/c/d/e(40)', '/ab(25)', '/a/b(10)']),
            ('add_file', ('/c/d/e', 5), False),
            ('get_n_largest', ('/a', 5), ['/ab(25)', '/a/b(10)', '/a(5)', '/a/c(5)']),
            ('backup_user', ('u3',), None),
            ('backup_user', ('u3',), None),
            ('restore_user', ('u1',), 1),
            ('restore_user', ('u2',), 0),
            ('add_file', ('/ab', 20), False),
            ('add_file', ('/a/b.txt', 10), True),
            ('add_user', ('u2', 30), False),
            ('add_user', ('u3', 100), True),
            ('add_file_by', ('u1', '/b', 25), 45),
            ('add_file', ('/b/a', 40), True),
            ('get_file_size', ('/b/a',), 40),
            ('add_user', ('u2', 30), False),
            ('get_n_largest', ('/b', 5), ['/b/a(40)', '/b(25)']),
            ('add_file_by', ('u1', '/b', 10), None),
            ('get_file_size', ('/b/a',), 40),
            ('add_file', ('/b', 25), False),
            ('get_file_size', ('/a/b',), 10),
            ('add_file', ('/ba', 10), True),
            ('restore_user', ('u3',), 0),
            ('delete_file', ('/ba',), 10),
            ('backup_user', ('u1',), 2),
            ('add_file', ('/ba', 40), True),
            ('add_file_by', ('u1', '/ba', 5), None),
            ('get_n_largest', ('/c', 2), ['/c/d/e(40)']),
            ('add_user', ('admin', 30), False),
            ('backup_user', ('u1',), 2),
        ])

    def test_level_4_case_11_randomized_sequence_49(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('add_file', ('/b/a', 10), True),
            ('add_file_by', ('u1', '/c.txt', 40), None),
            ('add_file', ('/ab', 20), True),
            ('add_file_by', ('u3', '/c.txt', 10), None),
            ('backup_user', ('u2',), None),
            ('get_n_largest', ('/', 0), []),
            ('get_n_largest', ('/a', 5), ['/ab(20)']),
            ('get_n_largest', ('/c', 3), []),
            ('add_file_by', ('u1', '/c/d/e', 40), None),
            ('add_file_by', ('u3', '/a/b', 10), None),
            ('add_user', ('admin', 50), False),
            ('delete_file', ('/c/d/e',), None),
            ('add_user', ('u1', 50), True),
            ('add_file', ('/a/b', 5), True),
            ('add_file', ('/b', 40), True),
            ('add_file', ('/b', 20), False),
            ('get_file_size', ('/b/a',), 10),
            ('add_user', ('u1', 30), False),
            ('add_file_by', ('u2', '/ba', 40), None),
            ('add_file', ('/c/d/e', 40), True),
            ('restore_user', ('u2',), None),
            ('add_user', ('u3', 80), True),
            ('backup_user', ('u3',), 0),
            ('get_file_size', ('/ab',), 20),
            ('add_file', ('/b', 40), False),
            ('add_file_by', ('u3', '/c.txt', 10), 70),
            ('get_n_largest', ('/z', 4), []),
            ('add_file', ('/b/a', 5), False),
            ('delete_file', ('/a/b',), 5),
            ('add_file_by', ('u3', '/b/a', 40), None),
            ('add_user', ('u1', 50), False),
            ('add_file', ('/a/b', 20), True),
            ('delete_file', ('/c.txt',), 10),
            ('add_file_by', ('u2', '/c.txt', 5), None),
            ('get_n_largest', ('/', 2), ['/b(40)', '/c/d/e(40)']),
            ('get_n_largest', ('/z', 1), []),
            ('backup_user', ('u2',), None),
            ('restore_user', ('u1',), 0),
            ('add_file', ('/a/b', 5), False),
            ('add_user', ('u3', 80), False),
            ('get_file_size', ('/ba',), None),
            ('delete_file', ('/a',), None),
            ('add_file_by', ('u3', '/a/b.txt', 40), 40),
            ('add_file_by', ('u1', '/a/c', 5), 45),
            ('add_file', ('/b', 25), False),
            ('restore_user', ('u1',), 0),
            ('get_file_size', ('/c.txt',), None),
            ('restore_user', ('u3',), 0),
            ('backup_user', ('u1',), 0),
            ('add_file', ('/ba', 40), True),
            ('get_file_size', ('/b',), 40),
            ('delete_file', ('/a/c',), None),
            ('add_file', ('/ba', 20), False),
            ('add_file', ('/a/b', 20), False),
            ('get_file_size', ('/a/b.txt',), None),
            ('restore_user', ('u3',), 0),
            ('add_file_by', ('u2', '/a/b.txt', 5), None),
            ('add_file_by', ('u2', '/a/b.txt', 10), None),
            ('restore_user', ('u2',), None),
            ('add_file', ('/ab', 25), False),
            ('add_file_by', ('u1', '/ab', 10), None),
            ('add_file_by', ('u1', '/c/d/e', 20), None),
            ('add_file', ('/ab', 20), False),
            ('add_file', ('/c.txt', 10), True),
            ('backup_user', ('u1',), 0),
            ('restore_user', ('u1',), 0),
            ('add_file', ('/a', 5), True),
            ('delete_file', ('/c.txt',), 10),
            ('add_file_by', ('u3', '/c/d/e', 40), None),
            ('add_user', ('u3', 50), False),
            ('add_user', ('admin', 100), False),
            ('add_user', ('u3', 50), False),
            ('add_file_by', ('u1', '/a/c', 10), 40),
            ('add_file', ('/c/d/e', 25), False),
            ('get_file_size', ('/c.txt',), None),
            ('add_file', ('/c.txt', 10), True),
            ('add_file', ('/a', 20), False),
            ('add_file_by', ('u1', '/a/b.txt', 10), 30),
            ('add_file_by', ('u3', '/b/a', 40), None),
            ('add_user', ('u2', 50), True),
            ('backup_user', ('u1',), 2),
            ('add_user', ('u3', 80), False),
            ('merge_user', ('u3', 'u1'), 110),
            ('delete_file', ('/b',), 40),
            ('add_file_by', ('u1', '/b', 10), None),
            ('add_file_by', ('u2', '/c.txt', 10), None),
            ('add_file_by', ('u2', '/b/a', 40), None),
            ('merge_user', ('u1', 'u2'), None),
            ('add_file_by', ('u3', '/ab', 10), None),
            ('get_n_largest', ('/c', 4), ['/c/d/e(40)', '/c.txt(10)']),
        ])


if __name__ == "__main__":
    unittest.main()
