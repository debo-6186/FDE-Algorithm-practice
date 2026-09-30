"""
Level 3 tests for File Hosting (TTL + rollback).

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


class TestLevel3(unittest.TestCase):
    def setUp(self):
        self.impl = FileHostingImpl()

    def test_level_3_case_01_example_from_spec(self):
        """The Level 3 example table."""
        run_steps(self, self.impl, [
            ('file_upload_at', (1, '/a.txt', 100), ANY),
            ('file_upload_at', (2, '/b.txt', 200, 10), ANY),
            ('file_get_at', (11, '/b.txt'), 200),
            ('file_get_at', (12, '/b.txt'), None),
            ('file_upload_at', (13, '/b.txt', 50, 5), ANY),
            ('file_upload_at', (14, '/a.txt', 1), Raises(RuntimeError)),
            ('file_copy_at', (15, '/b.txt', '/c.txt'), ANY),
            ('file_search_at', (16, '/'), ['/a.txt', '/b.txt', '/c.txt']),
            ('file_search_at', (18, '/'), ['/a.txt']),
            ('file_copy_at', (19, '/b.txt', '/d.txt'), Raises(RuntimeError)),
            ('file_get_at', (20, '/c.txt'), None),
        ])

    def test_level_3_case_02_ttl_window_is_half_open(self):
        run_steps(self, self.impl, [
            ('file_upload_at', (100, '/x', 1, 1), ANY),
            ('file_get_at', (101, '/x'), None),
            ('file_upload_at', (102, '/y', 2, 3), ANY),
            ('file_get_at', (104, '/y'), 2),
            ('file_get_at', (105, '/y'), None),
        ])

    def test_level_3_case_03_copy_of_permanent_file_is_permanent(self):
        run_steps(self, self.impl, [
            ('file_upload_at', (1, '/p', 4), ANY),
            ('file_copy_at', (2, '/p', '/q'), ANY),
            ('file_get_at', (1000000000, '/q'), 4),
        ])

    def test_level_3_case_04_copy_overwrites_live_destination_and_its_ttl(self):
        run_steps(self, self.impl, [
            ('file_upload_at', (1, '/long', 1), ANY),
            ('file_upload_at', (2, '/short', 2, 5), ANY),
            ('file_copy_at', (3, '/short', '/long'), ANY),
            ('file_get_at', (6, '/long'), 2),
            ('file_get_at', (7, '/long'), None),
            ('file_upload_at', (8, '/long', 9), ANY),
            ('file_get_at', (9, '/long'), 9),
        ])

    def test_level_3_case_05_copy_expired_source_raises(self):
        run_steps(self, self.impl, [
            ('file_upload_at', (1, '/s', 1, 2), ANY),
            ('file_copy_at', (3, '/s', '/d'), Raises(RuntimeError)),
            ('file_get_at', (4, '/d'), None),
        ])

    def test_level_3_case_06_search_ignores_expired_and_limits_to_ten(self):
        run_steps(self, self.impl, [
            ('file_upload_at', (1, '/k01', 1, 30), ANY),
            ('file_upload_at', (2, '/k02', 2, None), ANY),
            ('file_upload_at', (3, '/k03', 3, 30), ANY),
            ('file_upload_at', (4, '/k04', 4, None), ANY),
            ('file_upload_at', (5, '/k05', 5, 30), ANY),
            ('file_upload_at', (6, '/k06', 6, None), ANY),
            ('file_upload_at', (7, '/k07', 7, 30), ANY),
            ('file_upload_at', (8, '/k08', 8, None), ANY),
            ('file_upload_at', (9, '/k09', 9, 30), ANY),
            ('file_upload_at', (10, '/k10', 10, None), ANY),
            ('file_upload_at', (11, '/k11', 11, 30), ANY),
            ('file_upload_at', (12, '/k12', 12, None), ANY),
            ('file_upload_at', (13, '/k13', 13, 30), ANY),
            ('file_upload_at', (14, '/k14', 14, None), ANY),
            ('file_search_at', (20, '/k'), ['/k14', '/k13', '/k12', '/k11', '/k10', '/k09', '/k08', '/k07', '/k06', '/k05']),
            ('file_search_at', (40, '/k'), ['/k14', '/k13', '/k12', '/k11', '/k10', '/k08', '/k06', '/k04', '/k02']),
            ('file_search_at', (50, '/k'), ['/k14', '/k12', '/k10', '/k08', '/k06', '/k04', '/k02']),
        ])

    def test_level_3_case_07_randomized_sequence_39(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('file_upload_at', (2, '/ab', 2), ANY),
            ('file_copy_at', (6, '/a', '/d.txt'), Raises(RuntimeError)),
            ('file_copy_at', (9, '/d.txt', '/ab'), Raises(RuntimeError)),
            ('file_upload_at', (10, '/b', 1), ANY),
            ('file_get_at', (11, '/b/c'), None),
            ('file_search_at', (12, '/a'), ['/ab']),
            ('file_copy_at', (15, '/b/c', '/b/c'), Raises(RuntimeError)),
            ('file_copy_at', (18, '/c', '/a'), Raises(RuntimeError)),
            ('file_copy_at', (24, '/a', '/d.txt'), Raises(RuntimeError)),
            ('file_search_at', (26, '/b'), ['/b']),
            ('file_copy_at', (31, '/b/c', '/e'), Raises(RuntimeError)),
            ('file_search_at', (34, '/a'), ['/ab']),
            ('file_copy_at', (38, '/b/c', '/ab'), Raises(RuntimeError)),
            ('file_get_at', (43, '/ab'), 2),
            ('file_search_at', (46, '/a'), ['/ab']),
            ('file_search_at', (48, ''), ['/ab', '/b']),
            ('file_search_at', (52, '/b'), ['/b']),
            ('file_upload_at', (57, '/a', 5), ANY),
            ('file_search_at', (58, '/b'), ['/b']),
            ('file_upload_at', (64, '/c', 2, 25), ANY),
            ('file_get_at', (65, '/d.txt'), None),
            ('file_get_at', (67, '/e'), None),
            ('file_search_at', (69, '/'), ['/a', '/ab', '/c', '/b']),
            ('file_get_at', (71, '/c'), 2),
            ('file_upload_at', (75, '/b', 2, 10), Raises(RuntimeError)),
            ('file_search_at', (80, '/'), ['/a', '/ab', '/c', '/b']),
            ('file_search_at', (82, '/a'), ['/a', '/ab']),
            ('file_upload_at', (85, '/a', 2), Raises(RuntimeError)),
            ('file_upload_at', (90, '/a', 1), Raises(RuntimeError)),
            ('file_search_at', (96, ''), ['/a', '/ab', '/b']),
            ('file_search_at', (100, '/b'), ['/b']),
            ('file_upload_at', (103, '/ab', 3), Raises(RuntimeError)),
            ('file_upload_at', (105, '/e', 1), ANY),
            ('file_upload_at', (109, '/c', 1), ANY),
            ('file_upload_at', (111, '/d.txt', 5), ANY),
            ('file_upload_at', (113, '/d.txt', 2), Raises(RuntimeError)),
            ('file_search_at', (117, '/'), ['/a', '/d.txt', '/ab', '/b', '/c', '/e']),
            ('file_upload_at', (120, '/b', 1, 5), Raises(RuntimeError)),
            ('file_upload_at', (124, '/a', 5, 3), Raises(RuntimeError)),
            ('file_search_at', (129, ''), ['/a', '/d.txt', '/ab', '/b', '/c', '/e']),
            ('file_search_at', (132, ''), ['/a', '/d.txt', '/ab', '/b', '/c', '/e']),
            ('file_search_at', (137, '/a'), ['/a', '/ab']),
            ('file_get_at', (138, '/ab'), 2),
            ('file_search_at', (144, '/b'), ['/b']),
            ('file_upload_at', (149, '/c', 1), Raises(RuntimeError)),
            ('file_search_at', (155, '/a'), ['/a', '/ab']),
            ('file_search_at', (160, '/b'), ['/b']),
            ('file_upload_at', (165, '/a', 2, 25), Raises(RuntimeError)),
            ('file_upload_at', (171, '/b', 3), Raises(RuntimeError)),
            ('file_search_at', (172, '/a'), ['/a', '/ab']),
            ('file_get_at', (177, '/ab'), 2),
            ('file_search_at', (178, '/a'), ['/a', '/ab']),
            ('file_copy_at', (180, '/c', '/ab'), ANY),
            ('file_upload_at', (186, '/a', 1, 5), Raises(RuntimeError)),
            ('file_copy_at', (187, '/d.txt', '/d.txt'), ANY),
            ('file_get_at', (193, '/b'), 1),
            ('file_get_at', (195, '/c'), 1),
            ('file_upload_at', (201, '/ab', 5, 3), Raises(RuntimeError)),
            ('file_upload_at', (204, '/d.txt', 5), Raises(RuntimeError)),
            ('file_upload_at', (209, '/d.txt', 5), Raises(RuntimeError)),
        ])

    def test_level_3_case_08_randomized_sequence_40(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('file_copy_at', (4, '/c', '/a'), Raises(RuntimeError)),
            ('file_upload_at', (6, '/d.txt', 2, 25), ANY),
            ('file_copy_at', (8, '/b', '/d.txt'), Raises(RuntimeError)),
            ('file_search_at', (12, '/'), ['/d.txt']),
            ('file_copy_at', (13, '/c', '/d.txt'), Raises(RuntimeError)),
            ('file_search_at', (17, ''), ['/d.txt']),
            ('file_search_at', (19, '/a'), []),
            ('file_upload_at', (20, '/ab', 1, 3), ANY),
            ('file_search_at', (24, '/a'), []),
            ('file_copy_at', (30, '/ab', '/d.txt'), Raises(RuntimeError)),
            ('file_upload_at', (32, '/b', 3, 10), ANY),
            ('file_copy_at', (36, '/ab', '/c'), Raises(RuntimeError)),
            ('file_get_at', (38, '/c'), None),
            ('file_upload_at', (39, '/c', 1), ANY),
            ('file_get_at', (40, '/b'), 3),
            ('file_upload_at', (41, '/b/c', 5), ANY),
            ('file_get_at', (42, '/d.txt'), None),
            ('file_copy_at', (45, '/b/c', '/b'), ANY),
            ('file_search_at', (50, '/'), ['/b', '/b/c', '/c']),
            ('file_search_at', (51, '/'), ['/b', '/b/c', '/c']),
            ('file_get_at', (56, '/e'), None),
            ('file_get_at', (62, '/e'), None),
            ('file_get_at', (68, '/c'), 1),
            ('file_get_at', (69, '/c'), 1),
            ('file_search_at', (71, '/b'), ['/b', '/b/c']),
            ('file_upload_at', (77, '/b', 3), Raises(RuntimeError)),
            ('file_upload_at', (83, '/ab', 2, 3), ANY),
            ('file_upload_at', (84, '/e', 2), ANY),
            ('file_get_at', (86, '/b/c'), 5),
            ('file_upload_at', (90, '/ab', 1, 10), ANY),
            ('file_copy_at', (96, '/e', '/a'), ANY),
            ('file_copy_at', (98, '/ab', '/b'), ANY),
            ('file_upload_at', (99, '/d.txt', 5, 5), ANY),
            ('file_get_at', (102, '/a'), 2),
            ('file_search_at', (107, '/a'), ['/a']),
            ('file_get_at', (112, '/d.txt'), None),
            ('file_search_at', (118, ''), ['/b/c', '/a', '/e', '/c']),
            ('file_search_at', (123, ''), ['/b/c', '/a', '/e', '/c']),
            ('file_get_at', (128, '/d.txt'), None),
            ('file_upload_at', (129, '/c', 1, 10), Raises(RuntimeError)),
            ('file_upload_at', (132, '/ab', 2), ANY),
            ('file_get_at', (137, '/a'), 2),
            ('file_upload_at', (143, '/b', 5), ANY),
            ('file_upload_at', (147, '/ab', 3, 25), Raises(RuntimeError)),
            ('file_get_at', (148, '/ab'), 2),
            ('file_search_at', (152, '/a'), ['/a', '/ab']),
            ('file_get_at', (158, '/b/c'), 5),
            ('file_search_at', (163, '/a'), ['/a', '/ab']),
            ('file_search_at', (168, '/b'), ['/b', '/b/c']),
            ('file_search_at', (174, '/b'), ['/b', '/b/c']),
            ('file_upload_at', (175, '/d.txt', 2, 3), ANY),
            ('file_get_at', (179, '/c'), 1),
            ('file_search_at', (181, ''), ['/b', '/b/c', '/a', '/ab', '/e', '/c']),
            ('file_copy_at', (182, '/d.txt', '/c'), Raises(RuntimeError)),
            ('file_upload_at', (188, '/c', 3), Raises(RuntimeError)),
            ('file_copy_at', (192, '/b', '/a'), ANY),
            ('file_search_at', (194, ''), ['/a', '/b', '/b/c', '/ab', '/e', '/c']),
            ('file_upload_at', (196, '/d.txt', 1, 5), ANY),
            ('file_upload_at', (202, '/b/c', 1, 5), Raises(RuntimeError)),
            ('file_search_at', (203, '/a'), ['/a', '/ab']),
        ])


if __name__ == "__main__":
    unittest.main()
