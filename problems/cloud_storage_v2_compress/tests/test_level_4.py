"""
Level 4 tests for Cloud Storage v2.

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


class TestLevel4(unittest.TestCase):
    def setUp(self):
        self.impl = CloudStorageV2Impl()

    def test_level_4_case_01_example_from_spec(self):
        """The Level 4 example table."""
        run_steps(self, self.impl, [
            ('add_user', ('alice', 1000), True),
            ('add_file_by', ('alice', '/video.mp4', 800), 200),
            ('compress_file', ('alice', '/video.mp4'), 600),
            ('get_file_size', ('/video.mp4',), None),
            ('get_file_size', ('/video.mp4.COMPRESSED',), 400),
            ('compress_file', ('alice', '/video.mp4.COMPRESSED'), None),
            ('add_user', ('bob', 100), True),
            ('decompress_file', ('bob', '/video.mp4.COMPRESSED'), None),
            ('add_file_by', ('alice', '/notes.txt', 500), 100),
            ('decompress_file', ('alice', '/video.mp4.COMPRESSED'), None),
            ('update_capacity', ('alice', 1300), 0),
            ('decompress_file', ('alice', '/video.mp4.COMPRESSED'), 0),
            ('get_file_size', ('/video.mp4',), 800),
            ('compress_file', ('alice', '/notes.txt'), 250),
        ])

    def test_level_4_case_02_odd_size_round_trip(self):
        """5 bytes compress to 2 and decompress back to exactly 5."""
        run_steps(self, self.impl, [
            ('add_user', ('u', 10), True),
            ('add_file_by', ('u', '/odd', 5), 5),
            ('compress_file', ('u', '/odd'), 8),
            ('get_file_size', ('/odd.COMPRESSED',), 2),
            ('decompress_file', ('u', '/odd.COMPRESSED'), 5),
            ('get_file_size', ('/odd',), 5),
        ])

    def test_level_4_case_03_compress_failures(self):
        run_steps(self, self.impl, [
            ('add_user', ('u', 100), True),
            ('add_file', ('/admin.txt', 10), True),
            ('compress_file', ('u', '/admin.txt'), None),
            ('compress_file', ('ghost', '/admin.txt'), None),
            ('compress_file', ('u', '/nope'), None),
            ('add_file_by', ('u', '/x', 10), 90),
            ('add_file_by', ('u', '/x.COMPRESSED', 4), 86),
            ('compress_file', ('u', '/x'), None),
            ('get_file_size', ('/x',), 10),
        ])

    def test_level_4_case_04_decompress_failures(self):
        run_steps(self, self.impl, [
            ('add_user', ('u', 100), True),
            ('add_file_by', ('u', '/fake.COMPRESSED', 10), 90),
            ('decompress_file', ('u', '/fake.COMPRESSED'), None),
            ('add_file_by', ('u', '/real', 20), 70),
            ('compress_file', ('u', '/real'), 80),
            ('add_file', ('/real', 1), True),
            ('decompress_file', ('u', '/real.COMPRESSED'), None),
            ('decompress_file', ('u', '/real'), None),
            ('get_file_size', ('/real.COMPRESSED',), 10),
        ])

    def test_level_4_case_05_compressed_files_are_searchable_and_evictable(self):
        run_steps(self, self.impl, [
            ('add_user', ('u', 100), True),
            ('add_file_by', ('u', '/a', 60), 40),
            ('add_file_by', ('u', '/b', 30), 10),
            ('compress_file', ('u', '/a'), 40),
            ('find_file', ('/', ''), ['/a.COMPRESSED(30)', '/b(30)']),
            ('update_capacity', ('u', 40), 1),
            ('get_file_size', ('/a.COMPRESSED',), None),
            ('get_file_size', ('/b',), 30),
        ])

    def test_level_4_case_06_copy_of_compressed_file_can_be_decompressed(self):
        run_steps(self, self.impl, [
            ('add_user', ('u', 100), True),
            ('add_file_by', ('u', '/p', 40), 60),
            ('compress_file', ('u', '/p'), 80),
            ('copy_file', ('/p.COMPRESSED', '/q.COMPRESSED'), True),
            ('decompress_file', ('u', '/q.COMPRESSED'), 40),
            ('get_file_size', ('/q',), 40),
            ('decompress_file', ('u', '/p.COMPRESSED'), 20),
            ('get_file_size', ('/p',), 40),
        ])

    def test_level_4_case_07_randomized_sequence_50(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('add_file_by', ('u2', '/b.txt', 10), None),
            ('update_capacity', ('u1', 150), None),
            ('find_file', ('/a', ''), []),
            ('decompress_file', ('u1', '/a.COMPRESSED'), None),
            ('get_file_size', ('/a.COMPRESSED',), None),
            ('add_file_by', ('u2', '/a.txt', 25), None),
            ('add_file', ('/a.COMPRESSED', 25), True),
            ('update_capacity', ('u1', 80), None),
            ('find_file', ('/a', '.COMPRESSED'), ['/a.COMPRESSED(25)']),
            ('get_file_size', ('/a.txt',), None),
            ('update_capacity', ('u2', 80), None),
            ('decompress_file', ('u2', '/ab'), None),
            ('add_file_by', ('u1', '/b.txt', 20), None),
            ('compress_file', ('u1', '/ab'), None),
            ('add_user', ('u2', 100), True),
            ('compress_file', ('u1', '/b'), None),
            ('compress_file', ('u1', '/a.txt'), None),
            ('find_file', ('', '.COMPRESSED'), ['/a.COMPRESSED(25)']),
            ('add_file', ('/a.txt', 20), True),
            ('add_file_by', ('u2', '/c.bin', 25), 75),
            ('add_file_by', ('u1', '/b.txt.COMPRESSED', 20), None),
            ('add_file', ('/a', 25), True),
            ('update_capacity', ('u2', 40), 0),
            ('compress_file', ('u1', '/c.bin'), None),
            ('find_file', ('', ''), ['/a(25)', '/a.COMPRESSED(25)', '/c.bin(25)', '/a.txt(20)']),
            ('add_file', ('/ab', 10), True),
            ('add_file', ('/a.COMPRESSED', 10), False),
            ('add_file_by', ('u2', '/b', 40), None),
            ('add_file', ('/c.bin', 25), False),
            ('find_file', ('', '.COMPRESSED'), ['/a.COMPRESSED(25)']),
            ('add_file_by', ('u2', '/a.COMPRESSED', 20), None),
            ('add_file', ('/c.bin', 10), False),
            ('compress_file', ('u2', '/a.COMPRESSED'), None),
            ('update_capacity', ('u1', 0), None),
            ('add_file_by', ('u1', '/a', 20), None),
            ('add_file_by', ('u2', '/c.bin', 20), None),
            ('compress_file', ('u2', '/b'), None),
            ('compress_file', ('u1', '/b'), None),
            ('find_file', ('/b', '.txt'), []),
            ('get_file_size', ('/b.txt',), None),
            ('compress_file', ('u1', '/b.txt'), None),
            ('compress_file', ('u1', '/b.txt.COMPRESSED'), None),
            ('add_file_by', ('u2', '/a', 25), None),
            ('copy_file', ('/ab', '/b'), True),
            ('add_file', ('/b', 20), False),
            ('update_capacity', ('u1', 20), None),
            ('decompress_file', ('u1', '/a.COMPRESSED'), None),
            ('decompress_file', ('u1', '/a.txt'), None),
            ('copy_file', ('/c.bin', '/b.txt'), False),
            ('compress_file', ('u1', '/b'), None),
            ('add_user', ('u1', 30), True),
            ('decompress_file', ('u2', '/a.COMPRESSED'), None),
            ('add_file_by', ('u1', '/a', 25), None),
            ('add_file_by', ('u2', '/a.COMPRESSED', 3), None),
            ('add_file_by', ('u1', '/c.bin', 25), None),
            ('add_file_by', ('u1', '/a.txt', 10), None),
            ('update_capacity', ('u2', 40), 0),
            ('compress_file', ('u2', '/b.txt'), None),
            ('compress_file', ('u1', '/b.txt.COMPRESSED'), None),
            ('add_file_by', ('u1', '/a', 25), None),
            ('add_user', ('u2', 60), False),
            ('find_file', ('/', ''), ['/a(25)', '/a.COMPRESSED(25)', '/c.bin(25)', '/a.txt(20)', '/ab(10)', '/b(10)']),
            ('add_file', ('/a.COMPRESSED', 25), False),
            ('add_file_by', ('u2', '/a', 10), None),
            ('copy_file', ('/b.txt', '/a.COMPRESSED'), False),
            ('add_file', ('/b', 10), False),
            ('add_file_by', ('u2', '/a', 10), None),
            ('add_file', ('/b.txt.COMPRESSED', 20), True),
            ('add_file_by', ('u2', '/a.COMPRESSED', 20), None),
            ('add_file_by', ('u1', '/b', 40), None),
            ('add_file_by', ('u2', '/b.txt.COMPRESSED', 20), None),
            ('find_file', ('/b', 'D'), ['/b.txt.COMPRESSED(20)']),
            ('update_capacity', ('u1', 150), 0),
            ('find_file', ('/a', '.COMPRESSED'), ['/a.COMPRESSED(25)']),
            ('add_file_by', ('u2', '/b.txt', 25), None),
            ('compress_file', ('u1', '/b'), None),
            ('decompress_file', ('u2', '/a.txt'), None),
            ('compress_file', ('u2', '/a.COMPRESSED'), None),
            ('decompress_file', ('u1', '/a.COMPRESSED'), None),
            ('add_file', ('/a.txt', 25), False),
            ('decompress_file', ('u1', '/a.txt'), None),
            ('add_file_by', ('u1', '/b.txt.COMPRESSED', 40), None),
            ('decompress_file', ('u1', '/ab'), None),
            ('find_file', ('/a', 'b'), ['/ab(10)']),
            ('compress_file', ('u1', '/c.bin'), None),
            ('add_file', ('/ab', 20), False),
            ('find_file', ('/', '.COMPRESSED'), ['/a.COMPRESSED(25)', '/b.txt.COMPRESSED(20)']),
            ('add_file_by', ('u2', '/c.bin', 10), None),
            ('add_file_by', ('u2', '/b.txt', 40), None),
            ('add_file_by', ('u1', '/b', 40), None),
        ])

    def test_level_4_case_08_randomized_sequence_51(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('get_file_size', ('/ab',), None),
            ('compress_file', ('u2', '/b'), None),
            ('decompress_file', ('u2', '/b.txt.COMPRESSED'), None),
            ('compress_file', ('u2', '/a.COMPRESSED'), None),
            ('add_user', ('u2', 100), True),
            ('decompress_file', ('u1', '/a.txt'), None),
            ('add_file_by', ('u2', '/a', 10), 90),
            ('find_file', ('/b', '.txt'), []),
            ('compress_file', ('u2', '/a'), 95),
            ('decompress_file', ('u2', '/ab'), None),
            ('add_file', ('/a', 3), True),
            ('copy_file', ('/c.bin', '/b.txt.COMPRESSED'), False),
            ('decompress_file', ('u2', '/b'), None),
            ('copy_file', ('/ab', '/c.bin'), False),
            ('add_file_by', ('u1', '/c.bin', 25), None),
            ('compress_file', ('u2', '/a'), None),
            ('decompress_file', ('u2', '/a.txt'), None),
            ('decompress_file', ('u1', '/c.bin'), None),
            ('find_file', ('/a', '.txt'), []),
            ('decompress_file', ('u2', '/c.bin'), None),
            ('get_file_size', ('/a',), 3),
            ('add_file_by', ('u1', '/c.bin', 40), None),
            ('find_file', ('/b', '.txt'), []),
            ('add_file_by', ('u1', '/b.txt.COMPRESSED', 3), None),
            ('find_file', ('/b', ''), []),
            ('add_file_by', ('u2', '/b.txt', 25), 70),
            ('add_file_by', ('u2', '/a', 10), None),
            ('compress_file', ('u2', '/b.txt.COMPRESSED'), None),
            ('decompress_file', ('u2', '/b.txt.COMPRESSED'), None),
            ('find_file', ('/b', '.COMPRESSED'), []),
            ('compress_file', ('u2', '/a.COMPRESSED'), None),
            ('add_file_by', ('u1', '/a', 25), None),
            ('decompress_file', ('u2', '/b'), None),
            ('find_file', ('', '.COMPRESSED'), ['/a.COMPRESSED(5)']),
            ('find_file', ('/a', 'b'), []),
            ('add_file', ('/c.bin', 20), True),
            ('compress_file', ('u1', '/b.txt'), None),
            ('compress_file', ('u1', '/a'), None),
            ('update_capacity', ('u1', 0), None),
            ('decompress_file', ('u1', '/a'), None),
            ('decompress_file', ('u1', '/c.bin'), None),
            ('copy_file', ('/b.txt.COMPRESSED', '/b'), False),
            ('add_file_by', ('u2', '/a', 25), None),
            ('add_user', ('u1', 60), True),
            ('add_file_by', ('u1', '/b', 3), 57),
            ('add_file_by', ('u2', '/b', 20), None),
            ('get_file_size', ('/c.bin',), 20),
            ('add_file', ('/a.txt', 10), True),
            ('copy_file', ('/b.txt.COMPRESSED', '/b'), False),
            ('copy_file', ('/a.txt', '/c.bin'), False),
            ('add_file_by', ('u1', '/a', 3), None),
            ('find_file', ('', '.txt'), ['/b.txt(25)', '/a.txt(10)']),
            ('add_file_by', ('u1', '/b.txt', 10), None),
            ('add_file', ('/a', 20), False),
            ('add_file', ('/b.txt.COMPRESSED', 3), True),
            ('add_file_by', ('u2', '/b.txt.COMPRESSED', 40), None),
            ('add_file', ('/ab', 3), True),
            ('find_file', ('', 'b'), ['/ab(3)', '/b(3)']),
            ('add_file_by', ('u2', '/b', 25), None),
            ('compress_file', ('u2', '/b.txt.COMPRESSED'), None),
            ('add_file', ('/b.txt', 10), False),
            ('add_file', ('/b.txt.COMPRESSED', 10), False),
            ('add_file_by', ('u2', '/a.txt', 20), None),
            ('compress_file', ('u1', '/a.txt'), None),
            ('copy_file', ('/b.txt', '/b'), False),
            ('find_file', ('', ''), ['/b.txt(25)', '/c.bin(20)', '/a.txt(10)', '/a.COMPRESSED(5)', '/a(3)', '/ab(3)', '/b(3)', '/b.txt.COMPRESSED(3)']),
            ('get_file_size', ('/b.txt.COMPRESSED',), 3),
            ('compress_file', ('u1', '/a.COMPRESSED'), None),
            ('copy_file', ('/b.txt', '/b'), False),
            ('get_file_size', ('/a.txt',), 10),
            ('add_file_by', ('u2', '/a.COMPRESSED', 3), None),
            ('find_file', ('/a', '.txt'), ['/a.txt(10)']),
            ('find_file', ('/b', 'D'), ['/b.txt.COMPRESSED(3)']),
            ('add_file', ('/b', 3), False),
            ('compress_file', ('u2', '/b.txt'), None),
            ('add_user', ('u2', 30), False),
            ('add_file', ('/c.bin', 3), False),
            ('find_file', ('', '.COMPRESSED'), ['/a.COMPRESSED(5)', '/b.txt.COMPRESSED(3)']),
            ('compress_file', ('u2', '/b'), None),
            ('find_file', ('/b', ''), ['/b.txt(25)', '/b(3)', '/b.txt.COMPRESSED(3)']),
            ('find_file', ('/', '.COMPRESSED'), ['/a.COMPRESSED(5)', '/b.txt.COMPRESSED(3)']),
            ('add_user', ('u1', 100), False),
            ('get_file_size', ('/b.txt',), 25),
            ('update_capacity', ('u2', 0), 2),
            ('add_file', ('/a.txt', 20), False),
            ('update_capacity', ('u2', 80), 0),
            ('update_capacity', ('u1', 0), 1),
            ('decompress_file', ('u2', '/c.bin'), None),
            ('compress_file', ('u2', '/a.COMPRESSED'), None),
            ('copy_file', ('/b', '/a.txt'), False),
        ])

    def test_level_4_case_09_randomized_sequence_52(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('decompress_file', ('u2', '/a'), None),
            ('compress_file', ('u2', '/a.COMPRESSED'), None),
            ('add_file', ('/ab', 25), True),
            ('compress_file', ('u2', '/a.COMPRESSED'), None),
            ('add_file_by', ('u2', '/a', 25), None),
            ('add_file', ('/a.txt', 10), True),
            ('add_file_by', ('u2', '/b.txt', 25), None),
            ('add_user', ('u2', 30), True),
            ('add_file_by', ('u1', '/a.COMPRESSED', 10), None),
            ('add_user', ('u2', 30), False),
            ('find_file', ('', '.txt'), ['/a.txt(10)']),
            ('add_file', ('/c.bin', 10), True),
            ('copy_file', ('/a.txt', '/a.txt'), False),
            ('copy_file', ('/b', '/b'), False),
            ('add_file_by', ('u1', '/b.txt.COMPRESSED', 40), None),
            ('copy_file', ('/b', '/b'), False),
            ('compress_file', ('u1', '/c.bin'), None),
            ('compress_file', ('u2', '/b'), None),
            ('add_file_by', ('u1', '/b', 10), None),
            ('add_file', ('/a', 20), True),
            ('add_file', ('/a', 10), False),
            ('add_file', ('/b.txt.COMPRESSED', 10), True),
            ('find_file', ('/', '.txt'), ['/a.txt(10)']),
            ('copy_file', ('/b', '/b'), False),
            ('add_user', ('u1', 30), True),
            ('compress_file', ('u1', '/b.txt'), None),
            ('compress_file', ('u1', '/b'), None),
            ('add_file_by', ('u2', '/a.COMPRESSED', 20), 10),
            ('find_file', ('/a', ''), ['/ab(25)', '/a(20)', '/a.COMPRESSED(20)', '/a.txt(10)']),
            ('add_file_by', ('u2', '/a', 10), None),
            ('compress_file', ('u2', '/b.txt'), None),
            ('add_user', ('u2', 100), False),
            ('add_file', ('/c.bin', 3), False),
            ('add_file_by', ('u2', '/a.txt', 25), None),
            ('get_file_size', ('/a.txt',), 10),
            ('decompress_file', ('u2', '/a'), None),
            ('compress_file', ('u1', '/b.txt'), None),
            ('compress_file', ('u1', '/a.COMPRESSED'), None),
            ('get_file_size', ('/a.COMPRESSED',), 20),
            ('add_file', ('/a.COMPRESSED', 3), False),
            ('add_file', ('/ab', 20), False),
            ('compress_file', ('u2', '/b.txt'), None),
            ('decompress_file', ('u2', '/a.txt'), None),
            ('copy_file', ('/a', '/b'), True),
            ('find_file', ('', '.txt'), ['/a.txt(10)']),
            ('copy_file', ('/c.bin', '/ab'), False),
            ('copy_file', ('/b.txt.COMPRESSED', '/b'), False),
            ('add_file', ('/b.txt.COMPRESSED', 25), False),
            ('update_capacity', ('u2', 80), 0),
            ('decompress_file', ('u1', '/b.txt.COMPRESSED'), None),
            ('update_capacity', ('u2', 0), 1),
            ('find_file', ('/a', 'b'), ['/ab(25)']),
            ('compress_file', ('u2', '/b.txt.COMPRESSED'), None),
            ('copy_file', ('/b.txt', '/c.bin'), False),
            ('get_file_size', ('/c.bin',), 10),
            ('copy_file', ('/b', '/c.bin'), False),
            ('add_file_by', ('u2', '/b.txt', 3), None),
            ('copy_file', ('/a.COMPRESSED', '/b.txt.COMPRESSED'), False),
            ('add_file', ('/b', 20), False),
            ('copy_file', ('/c.bin', '/ab'), False),
            ('update_capacity', ('u2', 80), 0),
            ('add_file', ('/a.txt', 10), False),
            ('find_file', ('/a', '.txt'), ['/a.txt(10)']),
            ('decompress_file', ('u1', '/b'), None),
            ('decompress_file', ('u1', '/a.txt'), None),
            ('copy_file', ('/b.txt.COMPRESSED', '/ab'), False),
            ('decompress_file', ('u2', '/b.txt.COMPRESSED'), None),
            ('add_file_by', ('u2', '/a.txt', 40), None),
            ('find_file', ('/', 'D'), ['/b.txt.COMPRESSED(10)']),
            ('add_file_by', ('u1', '/a', 40), None),
            ('find_file', ('/a', 'b'), ['/ab(25)']),
            ('find_file', ('', '.txt'), ['/a.txt(10)']),
            ('add_file_by', ('u2', '/ab', 25), None),
            ('compress_file', ('u1', '/a'), None),
            ('copy_file', ('/b.txt.COMPRESSED', '/b.txt.COMPRESSED'), False),
            ('add_file_by', ('u1', '/c.bin', 10), None),
            ('copy_file', ('/b.txt', '/b.txt.COMPRESSED'), False),
            ('add_file_by', ('u1', '/b.txt', 40), None),
            ('add_file_by', ('u2', '/a.COMPRESSED', 20), 60),
            ('update_capacity', ('u1', 80), 0),
            ('decompress_file', ('u1', '/a'), None),
            ('add_file_by', ('u1', '/a', 20), None),
            ('add_file', ('/a.txt', 3), False),
            ('compress_file', ('u2', '/b.txt.COMPRESSED'), None),
            ('get_file_size', ('/c.bin',), 10),
            ('copy_file', ('/b', '/a.COMPRESSED'), False),
            ('decompress_file', ('u2', '/a.txt'), None),
            ('compress_file', ('u1', '/a.COMPRESSED'), None),
            ('find_file', ('', '.txt'), ['/a.txt(10)']),
            ('decompress_file', ('u2', '/a.COMPRESSED'), None),
        ])


if __name__ == "__main__":
    unittest.main()
