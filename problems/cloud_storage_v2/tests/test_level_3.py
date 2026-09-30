"""
Level 3 tests for Cloud Storage v2.

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


class TestLevel3(unittest.TestCase):
    def setUp(self):
        self.impl = CloudStorageV2Impl()

    def test_level_3_case_01_example_from_spec(self):
        """The Level 3 example table."""
        run_steps(self, self.impl, [
            ('add_user', ('alice', 100), True),
            ('add_file_by', ('alice', '/a.txt', 40), 60),
            ('add_file_by', ('alice', '/b.txt', 40), 20),
            ('add_file_by', ('alice', '/c.txt', 10), 10),
            ('copy_file', ('/c.txt', '/c-copy.txt'), True),
            ('copy_file', ('/a.txt', '/a-copy.txt'), False),
            ('add_file', ('/admin.bin', 1000), True),
            ('copy_file', ('/admin.bin', '/admin-copy.bin'), True),
            ('update_capacity', ('alice', 50), 2),
            ('get_file_size', ('/a.txt',), None),
            ('get_file_size', ('/c-copy.txt',), 10),
            ('add_file_by', ('alice', '/d.txt', 30), 0),
            ('update_capacity', ('bob', 10), None),
            ('update_capacity', ('alice', 1000), 0),
            ('add_file_by', ('alice', '/e.txt', 950), 0),
        ])

    def test_level_3_case_02_add_user_twice(self):
        run_steps(self, self.impl, [
            ('add_user', ('u', 1), True),
            ('add_user', ('u', 5), False),
            ('add_file_by', ('u', '/f', 2), None),
        ])

    def test_level_3_case_03_update_capacity_to_zero_deletes_everything(self):
        run_steps(self, self.impl, [
            ('add_user', ('u', 100), True),
            ('add_file_by', ('u', '/a', 1), 99),
            ('add_file_by', ('u', '/b', 2), 97),
            ('add_file', ('/admin', 50), True),
            ('update_capacity', ('u', 0), 2),
            ('find_file', ('', ''), ['/admin(50)']),
            ('add_file_by', ('u', '/c', 1), None),
        ])

    def test_level_3_case_04_eviction_stops_as_soon_as_it_fits(self):
        """Deleting the 60 is enough; the 30 and 10 stay."""
        run_steps(self, self.impl, [
            ('add_user', ('u', 100), True),
            ('add_file_by', ('u', '/big', 60), 40),
            ('add_file_by', ('u', '/mid', 30), 10),
            ('add_file_by', ('u', '/small', 10), 0),
            ('update_capacity', ('u', 45), 1),
            ('find_file', ('/', ''), ['/mid(30)', '/small(10)']),
            ('add_file_by', ('u', '/x', 5), 0),
        ])

    def test_level_3_case_05_eviction_tie_breaks_by_smaller_name(self):
        run_steps(self, self.impl, [
            ('add_user', ('u', 90), True),
            ('add_file_by', ('u', '/b', 30), 60),
            ('add_file_by', ('u', '/a', 30), 30),
            ('add_file_by', ('u', '/c', 30), 0),
            ('update_capacity', ('u', 60), 1),
            ('get_file_size', ('/a',), None),
            ('update_capacity', ('u', 30), 1),
            ('get_file_size', ('/b',), None),
            ('get_file_size', ('/c',), 30),
        ])

    def test_level_3_case_06_eviction_only_touches_that_user(self):
        run_steps(self, self.impl, [
            ('add_user', ('a', 100), True),
            ('add_user', ('b', 100), True),
            ('add_file_by', ('a', '/a1', 50), 50),
            ('add_file_by', ('b', '/b1', 90), 10),
            ('update_capacity', ('a', 10), 1),
            ('get_file_size', ('/b1',), 90),
            ('add_file_by', ('a', '/a2', 10), 0),
        ])

    def test_level_3_case_07_copy_charges_source_owner(self):
        run_steps(self, self.impl, [
            ('add_user', ('u', 50), True),
            ('add_file_by', ('u', '/f', 20), 30),
            ('copy_file', ('/f', '/g'), True),
            ('add_file_by', ('u', '/h', 11), None),
            ('add_file_by', ('u', '/h', 10), 0),
            ('copy_file', ('/g', '/i'), False),
            ('update_capacity', ('u', 20), 2),
        ])

    def test_level_3_case_08_randomized_sequence_37(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('add_file_by', ('u1', '/a.txt', 20), None),
            ('find_file', ('/a', 'b'), []),
            ('update_capacity', ('u2', 20), None),
            ('update_capacity', ('u1', 80), None),
            ('add_file', ('/b.txt', 25), True),
            ('add_file_by', ('u1', '/a.COMPRESSED', 40), None),
            ('add_file_by', ('u1', '/b.txt.COMPRESSED', 3), None),
            ('add_file', ('/a.COMPRESSED', 10), True),
            ('add_file', ('/a.COMPRESSED', 3), False),
            ('add_file_by', ('u2', '/b', 10), None),
            ('add_user', ('u1', 60), True),
            ('get_file_size', ('/b',), None),
            ('add_file', ('/b.txt', 25), False),
            ('find_file', ('/', ''), ['/b.txt(25)', '/a.COMPRESSED(10)']),
            ('find_file', ('/a', ''), ['/a.COMPRESSED(10)']),
            ('add_file', ('/ab', 10), True),
            ('add_file_by', ('u2', '/b', 25), None),
            ('add_file', ('/ab', 10), False),
            ('copy_file', ('/ab', '/a'), True),
            ('find_file', ('/', '.txt'), ['/b.txt(25)']),
            ('find_file', ('/', ''), ['/b.txt(25)', '/a(10)', '/a.COMPRESSED(10)', '/ab(10)']),
            ('update_capacity', ('u1', 20), 0),
            ('add_file_by', ('u2', '/c.bin', 40), None),
            ('get_file_size', ('/a',), 10),
            ('add_file_by', ('u1', '/b.txt', 20), None),
            ('add_user', ('u2', 100), True),
            ('update_capacity', ('u2', 150), 0),
            ('find_file', ('', 'D'), ['/a.COMPRESSED(10)']),
            ('find_file', ('/', '.COMPRESSED'), ['/a.COMPRESSED(10)']),
            ('add_file_by', ('u2', '/b.txt', 3), None),
            ('find_file', ('/b', '.COMPRESSED'), []),
            ('add_user', ('u1', 30), False),
            ('add_file_by', ('u1', '/b', 10), 10),
            ('copy_file', ('/a.COMPRESSED', '/ab'), False),
            ('update_capacity', ('u2', 80), 0),
            ('copy_file', ('/a', '/a.COMPRESSED'), False),
            ('add_user', ('u2', 100), False),
            ('find_file', ('/a', '.txt'), []),
            ('find_file', ('/b', 'D'), []),
            ('update_capacity', ('u2', 150), 0),
            ('add_file_by', ('u1', '/b', 10), None),
            ('copy_file', ('/c.bin', '/a.COMPRESSED'), False),
            ('copy_file', ('/ab', '/ab'), False),
            ('add_user', ('u2', 100), False),
            ('find_file', ('/', '.COMPRESSED'), ['/a.COMPRESSED(10)']),
            ('find_file', ('', '.COMPRESSED'), ['/a.COMPRESSED(10)']),
            ('add_file_by', ('u1', '/a', 40), None),
            ('get_file_size', ('/b.txt',), 25),
            ('copy_file', ('/b.txt', '/b.txt.COMPRESSED'), True),
            ('find_file', ('', '.COMPRESSED'), ['/b.txt.COMPRESSED(25)', '/a.COMPRESSED(10)']),
            ('add_file_by', ('u2', '/b', 25), None),
            ('add_file_by', ('u1', '/a.COMPRESSED', 40), None),
            ('find_file', ('/b', 'b'), ['/b(10)']),
            ('find_file', ('/', '.txt'), ['/b.txt(25)']),
            ('add_file_by', ('u1', '/c.bin', 20), None),
            ('add_file', ('/a', 3), False),
            ('add_file', ('/b.txt', 3), False),
            ('add_user', ('u1', 100), False),
            ('find_file', ('/a', ''), ['/a(10)', '/a.COMPRESSED(10)', '/ab(10)']),
            ('add_file_by', ('u1', '/ab', 25), None),
            ('copy_file', ('/a.COMPRESSED', '/b'), False),
            ('get_file_size', ('/a.COMPRESSED',), 10),
            ('add_file_by', ('u2', '/b', 25), None),
            ('update_capacity', ('u2', 0), 0),
            ('add_file_by', ('u2', '/ab', 40), None),
            ('add_user', ('u1', 30), False),
            ('add_user', ('u1', 100), False),
            ('add_file_by', ('u1', '/a', 10), None),
            ('find_file', ('/', 'b'), ['/ab(10)', '/b(10)']),
            ('find_file', ('/', 'b'), ['/ab(10)', '/b(10)']),
        ])

    def test_level_3_case_09_randomized_sequence_38(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('add_file_by', ('u1', '/b.txt.COMPRESSED', 3), None),
            ('find_file', ('', '.COMPRESSED'), []),
            ('add_file_by', ('u2', '/a.COMPRESSED', 20), None),
            ('add_file_by', ('u2', '/b.txt', 40), None),
            ('find_file', ('/', 'b'), []),
            ('add_user', ('u2', 60), True),
            ('add_file_by', ('u1', '/a', 25), None),
            ('add_file', ('/a.txt', 25), True),
            ('add_file', ('/b.txt.COMPRESSED', 10), True),
            ('find_file', ('/a', 'D'), []),
            ('copy_file', ('/b.txt', '/a.COMPRESSED'), False),
            ('add_file', ('/b', 3), True),
            ('add_file', ('/b.txt.COMPRESSED', 20), False),
            ('add_file_by', ('u2', '/a', 40), 20),
            ('update_capacity', ('u2', 20), 1),
            ('add_file_by', ('u1', '/a.txt', 40), None),
            ('add_user', ('u1', 30), True),
            ('find_file', ('', 'D'), ['/b.txt.COMPRESSED(10)']),
            ('add_file_by', ('u1', '/a', 25), 5),
            ('add_file_by', ('u2', '/b', 20), None),
            ('add_file', ('/ab', 20), True),
            ('add_file_by', ('u1', '/b.txt.COMPRESSED', 3), None),
            ('add_user', ('u2', 100), False),
            ('find_file', ('/a', 'b'), ['/ab(20)']),
            ('add_file_by', ('u2', '/c.bin', 20), 0),
            ('copy_file', ('/b.txt.COMPRESSED', '/a.COMPRESSED'), True),
            ('add_file_by', ('u1', '/ab', 40), None),
            ('add_file_by', ('u1', '/b', 40), None),
            ('get_file_size', ('/ab',), 20),
            ('find_file', ('', '.COMPRESSED'), ['/a.COMPRESSED(10)', '/b.txt.COMPRESSED(10)']),
            ('find_file', ('/', '.COMPRESSED'), ['/a.COMPRESSED(10)', '/b.txt.COMPRESSED(10)']),
            ('find_file', ('/a', 'D'), ['/a.COMPRESSED(10)']),
            ('add_file_by', ('u1', '/a.txt', 3), None),
            ('update_capacity', ('u2', 40), 0),
            ('find_file', ('', 'b'), ['/ab(20)', '/b(3)']),
            ('find_file', ('/', '.COMPRESSED'), ['/a.COMPRESSED(10)', '/b.txt.COMPRESSED(10)']),
            ('update_capacity', ('u1', 80), 0),
            ('add_file_by', ('u2', '/b.txt', 20), 0),
            ('copy_file', ('/b.txt.COMPRESSED', '/a.txt'), False),
            ('add_file_by', ('u2', '/c.bin', 20), None),
            ('add_user', ('u1', 30), False),
            ('add_file', ('/a.COMPRESSED', 3), False),
            ('add_file', ('/a', 3), False),
            ('add_file_by', ('u2', '/a.txt', 10), None),
            ('find_file', ('/', 'D'), ['/a.COMPRESSED(10)', '/b.txt.COMPRESSED(10)']),
            ('update_capacity', ('u1', 0), 1),
            ('copy_file', ('/b.txt.COMPRESSED', '/c.bin'), False),
            ('add_file_by', ('u2', '/a', 40), None),
            ('add_file_by', ('u1', '/ab', 20), None),
            ('update_capacity', ('u1', 150), 0),
            ('add_file_by', ('u2', '/a', 20), None),
            ('update_capacity', ('u1', 40), 0),
            ('add_file_by', ('u1', '/a.txt', 25), None),
            ('find_file', ('/a', '.txt'), ['/a.txt(25)']),
            ('copy_file', ('/ab', '/b'), False),
            ('find_file', ('', 'D'), ['/a.COMPRESSED(10)', '/b.txt.COMPRESSED(10)']),
            ('get_file_size', ('/ab',), 20),
            ('update_capacity', ('u2', 40), 0),
            ('update_capacity', ('u2', 40), 0),
            ('add_file_by', ('u1', '/a.COMPRESSED', 3), None),
            ('add_file', ('/a', 10), True),
            ('add_file', ('/a', 20), False),
            ('add_file', ('/ab', 10), False),
            ('add_user', ('u2', 100), False),
            ('get_file_size', ('/a',), 10),
            ('find_file', ('/', 'b'), ['/ab(20)', '/b(3)']),
            ('add_file_by', ('u1', '/a', 25), None),
            ('add_file_by', ('u1', '/c.bin', 3), None),
            ('find_file', ('/', 'D'), ['/a.COMPRESSED(10)', '/b.txt.COMPRESSED(10)']),
            ('add_file_by', ('u1', '/b', 3), None),
        ])


if __name__ == "__main__":
    unittest.main()
