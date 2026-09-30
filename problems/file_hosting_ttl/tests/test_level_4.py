"""
Level 4 tests for File Hosting (TTL + rollback).

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


class TestLevel4(unittest.TestCase):
    def setUp(self):
        self.impl = FileHostingImpl()

    def test_level_4_case_01_example_from_spec(self):
        """The Level 4 example table."""
        run_steps(self, self.impl, [
            ('file_upload_at', (10, '/a', 1), ANY),
            ('file_upload_at', (20, '/b', 2, 100), ANY),
            ('file_upload_at', (30, '/c', 3, 15), ANY),
            ('file_copy_at', (40, '/a', '/b'), ANY),
            ('rollback', (50, 35), ANY),
            ('file_get_at', (51, '/b'), 2),
            ('file_get_at', (59, '/c'), 3),
            ('file_get_at', (60, '/c'), None),
            ('file_get_at', (134, '/b'), 2),
            ('file_get_at', (135, '/b'), None),
            ('rollback', (140, 25), ANY),
            ('file_search_at', (141, '/'), ['/b', '/a']),
            ('file_get_at', (142, '/c'), None),
        ])

    def test_level_4_case_02_rollback_to_before_anything(self):
        run_steps(self, self.impl, [
            ('file_upload_at', (5, '/a', 1), ANY),
            ('rollback', (6, 4), ANY),
            ('file_get_at', (7, '/a'), None),
            ('file_search_at', (8, ''), []),
            ('file_upload_at', (9, '/a', 2), ANY),
            ('file_get_at', (10, '/a'), 2),
        ])

    def test_level_4_case_03_rollback_to_exact_operation_time_includes_it(self):
        run_steps(self, self.impl, [
            ('file_upload_at', (5, '/a', 1), ANY),
            ('file_upload_at', (6, '/b', 1), ANY),
            ('rollback', (7, 5), ANY),
            ('file_get_at', (8, '/a'), 1),
            ('file_get_at', (9, '/b'), None),
        ])

    def test_level_4_case_04_expired_by_target_time_do_not_return(self):
        run_steps(self, self.impl, [
            ('file_upload_at', (1, '/e', 1, 5), ANY),
            ('file_upload_at', (7, '/f', 1), ANY),
            ('rollback', (8, 6), ANY),
            ('file_get_at', (9, '/e'), None),
            ('file_get_at', (10, '/f'), None),
            ('rollback', (11, 5), ANY),
            ('file_get_at', (12, '/e'), None),
            ('rollback', (13, 4), ANY),
            ('file_get_at', (14, '/e'), 1),
            ('file_get_at', (15, '/e'), None),
        ])

    def test_level_4_case_05_rollback_undoes_overwrite_by_copy(self):
        run_steps(self, self.impl, [
            ('file_upload_at', (1, '/x', 10), ANY),
            ('file_upload_at', (2, '/y', 20), ANY),
            ('file_copy_at', (3, '/x', '/y'), ANY),
            ('file_get_at', (4, '/y'), 10),
            ('rollback', (5, 2), ANY),
            ('file_get_at', (6, '/y'), 20),
        ])

    def test_level_4_case_06_rollback_to_a_time_after_a_previous_rollback(self):
        """The state at 55 is the result of the rollback at 50."""
        run_steps(self, self.impl, [
            ('file_upload_at', (10, '/a', 1), ANY),
            ('file_upload_at', (20, '/b', 2, 100), ANY),
            ('file_upload_at', (30, '/c', 3, 15), ANY),
            ('rollback', (50, 35), ANY),
            ('file_upload_at', (70, '/d', 4), ANY),
            ('rollback', (200, 55), ANY),
            ('file_get_at', (201, '/d'), None),
            ('file_get_at', (204, '/c'), 3),
            ('file_get_at', (205, '/c'), None),
            ('file_get_at', (279, '/b'), 2),
            ('file_get_at', (280, '/b'), None),
            ('file_get_at', (281, '/a'), 1),
        ])

    def test_level_4_case_07_rollback_target_between_operations(self):
        run_steps(self, self.impl, [
            ('file_upload_at', (10, '/a', 5, 20), ANY),
            ('file_upload_at', (20, '/b', 6), ANY),
            ('rollback', (100, 15), ANY),
            ('file_get_at', (101, '/b'), None),
            ('file_get_at', (114, '/a'), 5),
            ('file_get_at', (115, '/a'), None),
        ])

    def test_level_4_case_08_randomized_sequence_53(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('file_search_at', (5, '/'), []),
            ('file_copy_at', (9, '/b/c', '/d.txt'), Raises(RuntimeError)),
            ('file_get_at', (14, '/b/c'), None),
            ('file_upload_at', (20, '/ab', 3), ANY),
            ('file_upload_at', (26, '/a', 2, 25), ANY),
            ('file_get_at', (27, '/b/c'), None),
            ('file_upload_at', (29, '/b', 3), ANY),
            ('file_copy_at', (34, '/a', '/b'), ANY),
            ('file_upload_at', (37, '/c', 5, 25), ANY),
            ('file_get_at', (41, '/ab'), 3),
            ('file_search_at', (47, ''), ['/c', '/ab', '/a', '/b']),
            ('file_copy_at', (51, '/b/c', '/ab'), Raises(RuntimeError)),
            ('file_copy_at', (54, '/e', '/ab'), Raises(RuntimeError)),
            ('file_upload_at', (56, '/a', 1, 25), ANY),
            ('rollback', (60, 35), ANY),
            ('file_upload_at', (63, '/b/c', 5), ANY),
            ('file_search_at', (65, '/'), ['/b/c', '/ab', '/a', '/b']),
            ('rollback', (67, 42), ANY),
            ('file_get_at', (73, '/ab'), 3),
            ('file_upload_at', (77, '/b', 2, 5), ANY),
            ('file_upload_at', (81, '/a', 5, 3), ANY),
            ('file_get_at', (82, '/a'), 5),
            ('file_upload_at', (85, '/b/c', 2, 25), ANY),
            ('file_copy_at', (89, '/b', '/ab'), Raises(RuntimeError)),
            ('file_search_at', (91, '/b'), ['/b/c']),
            ('file_get_at', (95, '/ab'), 3),
            ('file_copy_at', (97, '/ab', '/e'), ANY),
            ('file_upload_at', (99, '/b', 5, 5), ANY),
            ('rollback', (100, 1), ANY),
            ('rollback', (102, 10), ANY),
            ('file_copy_at', (108, '/e', '/b/c'), Raises(RuntimeError)),
            ('file_upload_at', (111, '/e', 3, 25), ANY),
            ('file_copy_at', (116, '/e', '/e'), ANY),
            ('file_get_at', (122, '/ab'), None),
            ('file_search_at', (124, '/a'), []),
            ('file_upload_at', (125, '/b/c', 5, 10), ANY),
            ('file_search_at', (126, '/b'), ['/b/c']),
            ('file_get_at', (131, '/ab'), None),
            ('file_copy_at', (137, '/b/c', '/d.txt'), Raises(RuntimeError)),
            ('file_copy_at', (139, '/b', '/a'), Raises(RuntimeError)),
            ('file_upload_at', (141, '/e', 1, 10), ANY),
            ('file_copy_at', (146, '/b', '/a'), Raises(RuntimeError)),
            ('file_upload_at', (149, '/d.txt', 1, 5), ANY),
            ('file_search_at', (155, ''), []),
            ('file_get_at', (160, '/e'), None),
            ('file_copy_at', (166, '/d.txt', '/b/c'), Raises(RuntimeError)),
            ('file_copy_at', (172, '/b', '/c'), Raises(RuntimeError)),
            ('file_get_at', (173, '/b/c'), None),
            ('file_search_at', (179, ''), []),
            ('file_copy_at', (183, '/b/c', '/ab'), Raises(RuntimeError)),
            ('file_copy_at', (188, '/e', '/a'), Raises(RuntimeError)),
            ('file_upload_at', (192, '/ab', 5), ANY),
            ('file_upload_at', (195, '/c', 5), ANY),
            ('file_search_at', (197, ''), ['/ab', '/c']),
            ('file_copy_at', (202, '/d.txt', '/b/c'), Raises(RuntimeError)),
            ('file_upload_at', (205, '/d.txt', 3, 5), ANY),
            ('file_get_at', (209, '/d.txt'), 3),
            ('file_upload_at', (215, '/ab', 2, 5), Raises(RuntimeError)),
            ('file_copy_at', (220, '/ab', '/c'), ANY),
            ('file_get_at', (221, '/d.txt'), None),
            ('file_upload_at', (225, '/d.txt', 3), ANY),
            ('file_upload_at', (228, '/c', 1), Raises(RuntimeError)),
            ('file_get_at', (231, '/b/c'), None),
            ('file_copy_at', (232, '/e', '/e'), Raises(RuntimeError)),
            ('file_upload_at', (238, '/e', 3, 10), ANY),
            ('file_get_at', (239, '/b'), None),
            ('file_copy_at', (243, '/e', '/ab'), ANY),
            ('file_upload_at', (249, '/b/c', 5, 25), ANY),
            ('file_upload_at', (254, '/e', 3, 3), ANY),
            ('rollback', (256, 66), ANY),
            ('file_copy_at', (262, '/a', '/b'), ANY),
            ('file_upload_at', (265, '/e', 1, 25), ANY),
            ('file_upload_at', (266, '/c', 2, 3), ANY),
            ('file_get_at', (270, '/b/c'), 5),
            ('file_copy_at', (275, '/c', '/d.txt'), Raises(RuntimeError)),
            ('file_get_at', (279, '/d.txt'), None),
            ('rollback', (280, 18), ANY),
            ('file_copy_at', (281, '/d.txt', '/ab'), Raises(RuntimeError)),
            ('rollback', (283, 166), ANY),
            ('file_upload_at', (285, '/d.txt', 2, 3), ANY),
        ])

    def test_level_4_case_09_randomized_sequence_54(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('file_get_at', (2, '/b'), None),
            ('rollback', (6, 3), ANY),
            ('file_upload_at', (10, '/c', 5, 3), ANY),
            ('file_search_at', (12, ''), ['/c']),
            ('rollback', (16, 14), ANY),
            ('file_upload_at', (21, '/c', 3, 3), ANY),
            ('file_upload_at', (25, '/a', 3), ANY),
            ('rollback', (28, 18), ANY),
            ('file_get_at', (29, '/a'), None),
            ('file_upload_at', (32, '/d.txt', 1), ANY),
            ('rollback', (34, 8), ANY),
            ('file_upload_at', (38, '/d.txt', 2), ANY),
            ('file_get_at', (42, '/ab'), None),
            ('file_upload_at', (46, '/c', 1, 25), ANY),
            ('file_get_at', (52, '/ab'), None),
            ('rollback', (55, 26), ANY),
            ('file_get_at', (59, '/b'), None),
            ('file_upload_at', (64, '/e', 5, 5), ANY),
            ('file_upload_at', (67, '/e', 3, 5), Raises(RuntimeError)),
            ('rollback', (68, 64), ANY),
            ('file_upload_at', (72, '/ab', 5, 5), ANY),
            ('file_get_at', (77, '/b'), None),
            ('file_upload_at', (80, '/a', 3), Raises(RuntimeError)),
            ('file_get_at', (84, '/b/c'), None),
            ('file_get_at', (86, '/b'), None),
            ('file_get_at', (90, '/d.txt'), None),
            ('file_search_at', (95, '/'), ['/a']),
            ('file_copy_at', (100, '/b/c', '/e'), Raises(RuntimeError)),
            ('file_copy_at', (103, '/d.txt', '/ab'), Raises(RuntimeError)),
            ('file_get_at', (107, '/d.txt'), None),
            ('file_search_at', (109, '/a'), ['/a']),
            ('file_upload_at', (115, '/e', 1, 5), ANY),
            ('file_copy_at', (117, '/ab', '/ab'), Raises(RuntimeError)),
            ('file_upload_at', (123, '/ab', 2, 3), ANY),
            ('file_copy_at', (125, '/b', '/b'), Raises(RuntimeError)),
            ('file_upload_at', (128, '/b', 1, 5), ANY),
            ('file_search_at', (133, ''), ['/a']),
            ('file_upload_at', (134, '/b', 5), ANY),
            ('rollback', (138, 113), ANY),
            ('file_search_at', (141, '/'), ['/a']),
            ('rollback', (142, 98), ANY),
            ('rollback', (146, 54), ANY),
            ('file_get_at', (147, '/e'), None),
            ('file_upload_at', (152, '/c', 2, 25), Raises(RuntimeError)),
            ('file_search_at', (155, ''), ['/d.txt', '/c']),
            ('file_copy_at', (160, '/b/c', '/a'), Raises(RuntimeError)),
            ('file_upload_at', (164, '/b/c', 1, 10), ANY),
            ('file_upload_at', (165, '/b/c', 3), Raises(RuntimeError)),
            ('file_search_at', (171, ''), ['/d.txt', '/b/c']),
            ('file_search_at', (173, ''), ['/d.txt', '/b/c']),
            ('file_copy_at', (177, '/d.txt', '/b'), ANY),
            ('file_upload_at', (182, '/d.txt', 1), Raises(RuntimeError)),
            ('file_copy_at', (187, '/ab', '/b/c'), Raises(RuntimeError)),
            ('file_copy_at', (188, '/b', '/b/c'), ANY),
            ('file_copy_at', (189, '/b/c', '/e'), ANY),
            ('file_copy_at', (195, '/ab', '/b'), Raises(RuntimeError)),
            ('rollback', (199, 45), ANY),
            ('file_search_at', (204, '/b'), []),
            ('file_search_at', (208, '/a'), []),
            ('file_get_at', (209, '/e'), None),
            ('file_get_at', (213, '/b'), None),
            ('rollback', (215, 48), ANY),
            ('file_copy_at', (218, '/e', '/a'), Raises(RuntimeError)),
            ('file_search_at', (222, '/a'), []),
            ('file_upload_at', (223, '/c', 3, 3), Raises(RuntimeError)),
            ('rollback', (226, 97), ANY),
            ('file_get_at', (229, '/b'), None),
            ('file_copy_at', (232, '/ab', '/b/c'), Raises(RuntimeError)),
            ('file_upload_at', (234, '/ab', 1, 10), ANY),
            ('file_upload_at', (238, '/d.txt', 1, 10), ANY),
            ('rollback', (242, 27), ANY),
            ('file_copy_at', (247, '/a', '/a'), ANY),
            ('file_copy_at', (248, '/c', '/a'), Raises(RuntimeError)),
            ('file_search_at', (249, '/'), ['/a']),
            ('rollback', (253, 142), ANY),
            ('file_copy_at', (256, '/e', '/b'), Raises(RuntimeError)),
            ('file_search_at', (261, '/'), ['/a']),
            ('file_upload_at', (264, '/a', 1, 5), Raises(RuntimeError)),
            ('file_upload_at', (266, '/d.txt', 1, 5), ANY),
            ('rollback', (270, 199), ANY),
        ])

    def test_level_4_case_10_randomized_sequence_55(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('rollback', (1, 0), ANY),
            ('rollback', (3, 1), ANY),
            ('file_search_at', (4, '/a'), []),
            ('file_get_at', (5, '/d.txt'), None),
            ('file_get_at', (11, '/b/c'), None),
            ('file_copy_at', (15, '/b', '/d.txt'), Raises(RuntimeError)),
            ('rollback', (19, 1), ANY),
            ('file_upload_at', (25, '/c', 1), ANY),
            ('file_get_at', (30, '/ab'), None),
            ('file_get_at', (31, '/a'), None),
            ('file_copy_at', (36, '/b/c', '/ab'), Raises(RuntimeError)),
            ('file_search_at', (38, '/b'), []),
            ('file_upload_at', (40, '/a', 5), ANY),
            ('file_get_at', (43, '/c'), 1),
            ('file_upload_at', (45, '/e', 2), ANY),
            ('file_upload_at', (47, '/b/c', 2), ANY),
            ('file_copy_at', (50, '/e', '/d.txt'), ANY),
            ('file_get_at', (56, '/b/c'), 2),
            ('file_copy_at', (61, '/a', '/b/c'), ANY),
            ('rollback', (67, 32), ANY),
            ('file_search_at', (68, '/a'), []),
            ('file_get_at', (71, '/ab'), None),
            ('file_copy_at', (72, '/e', '/b/c'), Raises(RuntimeError)),
            ('file_get_at', (76, '/b/c'), None),
            ('file_copy_at', (79, '/a', '/b'), Raises(RuntimeError)),
            ('file_get_at', (81, '/b/c'), None),
            ('file_copy_at', (85, '/d.txt', '/b'), Raises(RuntimeError)),
            ('rollback', (86, 81), ANY),
            ('rollback', (92, 53), ANY),
            ('file_search_at', (95, ''), ['/a', '/b/c', '/d.txt', '/e', '/c']),
            ('file_get_at', (96, '/d.txt'), 2),
            ('file_get_at', (98, '/b/c'), 2),
            ('file_upload_at', (103, '/b/c', 3, 10), Raises(RuntimeError)),
            ('file_get_at', (109, '/d.txt'), 2),
            ('file_upload_at', (111, '/d.txt', 3), Raises(RuntimeError)),
            ('file_copy_at', (115, '/b/c', '/a'), ANY),
            ('rollback', (121, 71), ANY),
            ('file_copy_at', (122, '/b', '/ab'), Raises(RuntimeError)),
            ('file_upload_at', (126, '/b/c', 1, 25), ANY),
            ('file_upload_at', (130, '/e', 1), ANY),
            ('file_copy_at', (136, '/b/c', '/e'), ANY),
            ('file_get_at', (141, '/e'), 1),
            ('file_search_at', (143, ''), ['/b/c', '/c', '/e']),
            ('file_get_at', (146, '/a'), None),
            ('file_get_at', (150, '/c'), 1),
            ('rollback', (154, 83), ANY),
            ('file_upload_at', (155, '/b/c', 2), ANY),
            ('file_upload_at', (156, '/d.txt', 1, 10), ANY),
            ('file_search_at', (162, '/a'), []),
            ('file_search_at', (168, '/a'), []),
            ('file_search_at', (169, ''), ['/b/c', '/c']),
            ('file_copy_at', (173, '/ab', '/d.txt'), Raises(RuntimeError)),
            ('file_copy_at', (174, '/a', '/a'), Raises(RuntimeError)),
            ('file_get_at', (177, '/e'), None),
            ('file_search_at', (178, '/'), ['/b/c', '/c']),
            ('file_upload_at', (181, '/e', 3, 10), ANY),
            ('file_copy_at', (186, '/c', '/d.txt'), ANY),
            ('file_copy_at', (189, '/a', '/b/c'), Raises(RuntimeError)),
            ('file_copy_at', (193, '/b', '/a'), Raises(RuntimeError)),
            ('rollback', (198, 27), ANY),
            ('file_copy_at', (204, '/d.txt', '/e'), Raises(RuntimeError)),
            ('file_upload_at', (210, '/ab', 1), ANY),
            ('rollback', (214, 199), ANY),
            ('file_upload_at', (218, '/d.txt', 5), ANY),
            ('file_search_at', (219, '/'), ['/d.txt', '/c']),
            ('file_get_at', (223, '/b'), None),
            ('file_search_at', (227, ''), ['/d.txt', '/c']),
            ('file_upload_at', (228, '/e', 1, 10), ANY),
            ('file_upload_at', (232, '/b', 2, 25), ANY),
            ('file_get_at', (237, '/a'), None),
            ('file_upload_at', (239, '/b/c', 3, 3), ANY),
            ('file_upload_at', (243, '/b', 5), Raises(RuntimeError)),
            ('file_copy_at', (248, '/b', '/d.txt'), ANY),
            ('file_copy_at', (249, '/c', '/e'), ANY),
            ('file_search_at', (254, '/b'), ['/b']),
            ('file_upload_at', (257, '/d.txt', 5, 3), ANY),
            ('file_copy_at', (258, '/e', '/e'), ANY),
            ('file_upload_at', (260, '/a', 2, 10), ANY),
            ('file_upload_at', (263, '/c', 2, 5), Raises(RuntimeError)),
            ('file_get_at', (269, '/d.txt'), None),
        ])


if __name__ == "__main__":
    unittest.main()
