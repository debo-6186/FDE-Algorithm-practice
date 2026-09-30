"""
Level 4 tests for Task Manager.

Each test replays a sequence of calls on a fresh TaskManagerImpl() and checks
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

from task_manager_impl import TaskManagerImpl

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
        self.impl = TaskManagerImpl()

    def test_level_4_case_01_example_from_spec(self):
        """The Level 4 example table."""
        run_steps(self, self.impl, [
            ('add_task', (1, 'A', 1), 'task_id_1'),
            ('add_task', (2, 'B', 1), 'task_id_2'),
            ('add_user', (3, 'ann', 1), True),
            ('assign_task', (4, 'task_id_1', 'ann', 10), True),
            ('assign_task', (5, 'task_id_2', 'ann', 10), False),
            ('complete_task', (6, 'task_id_1', 'ann'), True),
            ('complete_task', (7, 'task_id_1', 'ann'), False),
            ('assign_task', (8, 'task_id_2', 'ann', 12), True),
            ('get_overdue_assignments', (11, 'ann'), []),
            ('get_overdue_assignments', (12, 'ann'), ['task_id_2']),
            ('complete_task', (13, 'task_id_2', 'ann'), False),
            ('assign_task', (14, 'task_id_1', 'ann', 20), True),
            ('get_user_tasks', (15, 'ann'), ['task_id_1']),
        ])

    def test_level_4_case_02_complete_unknown(self):
        run_steps(self, self.impl, [
            ('add_task', (1, 'A', 1), 'task_id_1'),
            ('add_user', (2, 'u', 1), True),
            ('complete_task', (3, 'task_id_1', 'u'), False),
            ('complete_task', (4, 'task_id_1', 'ghost'), False),
            ('get_overdue_assignments', (5, 'ghost'), []),
        ])

    def test_level_4_case_03_complete_picks_earliest_finishing(self):
        run_steps(self, self.impl, [
            ('add_task', (1, 'A', 1), 'task_id_1'),
            ('add_user', (2, 'u', 5), True),
            ('assign_task', (3, 'task_id_1', 'u', 40), True),
            ('assign_task', (4, 'task_id_1', 'u', 20), True),
            ('complete_task', (5, 'task_id_1', 'u'), True),
            ('get_overdue_assignments', (30, 'u'), []),
            ('get_overdue_assignments', (40, 'u'), ['task_id_1']),
        ])

    def test_level_4_case_04_overdue_sorted_by_finish_then_assignment(self):
        run_steps(self, self.impl, [
            ('add_task', (1, 'A', 1), 'task_id_1'),
            ('add_task', (2, 'B', 1), 'task_id_2'),
            ('add_task', (3, 'C', 1), 'task_id_3'),
            ('add_user', (4, 'u', 5), True),
            ('assign_task', (5, 'task_id_3', 'u', 15), True),
            ('assign_task', (6, 'task_id_1', 'u', 10), True),
            ('assign_task', (7, 'task_id_2', 'u', 15), True),
            ('get_overdue_assignments', (20, 'u'), ['task_id_1', 'task_id_3', 'task_id_2']),
        ])

    def test_level_4_case_05_completed_assignment_frees_quota_immediately(self):
        run_steps(self, self.impl, [
            ('add_task', (1, 'A', 1), 'task_id_1'),
            ('add_task', (2, 'B', 1), 'task_id_2'),
            ('add_user', (3, 'u', 1), True),
            ('assign_task', (4, 'task_id_1', 'u', 100), True),
            ('complete_task', (5, 'task_id_1', 'u'), True),
            ('assign_task', (6, 'task_id_2', 'u', 100), True),
            ('get_user_tasks', (7, 'u'), ['task_id_2']),
            ('get_overdue_assignments', (200, 'u'), ['task_id_2']),
        ])

    def test_level_4_case_06_randomized_sequence_62(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('add_task', (5, 'Fix bug', 3), 'task_id_1'),
            ('add_task', (8, 'fix docs', 1), 'task_id_2'),
            ('add_task', (10, 'review', 1), 'task_id_3'),
            ('add_task', (11, 'fix bug', 2), 'task_id_4'),
            ('assign_task', (16, 'task_id_2', 'u3', 19), False),
            ('assign_task', (19, 'task_id_5', 'u1', 39), False),
            ('get_overdue_assignments', (23, 'u2'), []),
            ('assign_task', (26, 'task_id_1', 'u2', 36), False),
            ('add_user', (31, 'u2', 1), True),
            ('assign_task', (33, 'task_id_1', 'u3', 52), False),
            ('get_task', (38, 'task_id_2'), '{"name": "fix docs", "priority": 1}'),
            ('add_task', (40, 'deploy', 2), 'task_id_5'),
            ('list_tasks_sorted', (42, 5), ['task_id_1', 'task_id_4', 'task_id_5', 'task_id_2', 'task_id_3']),
            ('list_tasks_sorted', (44, 5), ['task_id_1', 'task_id_4', 'task_id_5', 'task_id_2', 'task_id_3']),
            ('assign_task', (48, 'task_id_3', 'u3', 65), False),
            ('add_task', (49, 'review', 3), 'task_id_6'),
            ('get_user_tasks', (50, 'u3'), []),
            ('search_tasks', (55, 'Fix', 2), ['task_id_1']),
            ('get_user_tasks', (56, 'u1'), []),
            ('get_overdue_assignments', (60, 'u2'), []),
            ('search_tasks', (65, 'fix', 2), ['task_id_4', 'task_id_2']),
            ('list_tasks_sorted', (68, 2), ['task_id_1', 'task_id_6']),
            ('assign_task', (70, 'task_id_6', 'u1', 91), False),
            ('search_tasks', (74, 'docs', 0), []),
            ('add_task', (75, 'fix bug', 2), 'task_id_7'),
            ('get_task', (80, 'task_id_1'), '{"name": "Fix bug", "priority": 3}'),
            ('search_tasks', (85, 'x', 1), ['task_id_1']),
            ('list_tasks_sorted', (89, 8), ['task_id_1', 'task_id_6', 'task_id_4', 'task_id_5', 'task_id_7', 'task_id_2', 'task_id_3']),
            ('assign_task', (93, 'task_id_8', 'u1', 104), False),
            ('add_user', (97, 'u1', 2), True),
            ('list_tasks_sorted', (98, 5), ['task_id_1', 'task_id_6', 'task_id_4', 'task_id_5', 'task_id_7']),
            ('update_task', (103, 'task_id_7', 'Fix bug', 4), True),
            ('assign_task', (107, 'task_id_6', 'u3', 111), False),
            ('get_user_tasks', (112, 'u3'), []),
            ('get_user_tasks', (114, 'u2'), []),
            ('assign_task', (116, 'task_id_1', 'u2', 125), True),
            ('get_overdue_assignments', (118, 'u1'), []),
            ('search_tasks', (122, 'docs', 5), ['task_id_2']),
            ('update_task', (123, 'task_id_6', 'review', 4), True),
            ('update_task', (128, 'task_id_3', 'fix bug', 2), True),
            ('assign_task', (133, 'task_id_8', 'u2', 135), False),
            ('get_overdue_assignments', (135, 'u3'), []),
            ('assign_task', (138, 'task_id_5', 'u2', 142), True),
            ('update_task', (141, 'task_id_5', 'fix docs', 4), True),
            ('complete_task', (144, 'task_id_4', 'u1'), False),
            ('assign_task', (146, 'task_id_8', 'u1', 165), False),
            ('get_overdue_assignments', (149, 'u1'), []),
            ('get_task', (154, 'task_id_8'), None),
            ('get_overdue_assignments', (159, 'u1'), []),
            ('add_task', (161, 'fix docs', 1), 'task_id_8'),
            ('get_overdue_assignments', (164, 'u3'), []),
            ('get_user_tasks', (169, 'u3'), []),
            ('assign_task', (173, 'task_id_5', 'u2', 184), True),
            ('get_user_tasks', (175, 'u1'), []),
            ('get_task', (180, 'task_id_1'), '{"name": "Fix bug", "priority": 3}'),
            ('assign_task', (184, 'task_id_7', 'u1', 185), True),
            ('get_overdue_assignments', (188, 'u2'), ['task_id_1', 'task_id_5', 'task_id_5']),
            ('get_task', (190, 'task_id_8'), '{"name": "fix docs", "priority": 1}'),
            ('get_user_tasks', (191, 'u1'), []),
            ('search_tasks', (195, 'docs', -1), []),
            ('add_task', (200, 'review', 2), 'task_id_9'),
            ('update_task', (201, 'task_id_4', 'review', 2), True),
            ('get_task', (205, 'task_id_9'), '{"name": "review", "priority": 2}'),
            ('add_task', (206, 'deploy', 0), 'task_id_10'),
            ('complete_task', (210, 'task_id_1', 'u2'), False),
            ('get_overdue_assignments', (211, 'u1'), ['task_id_7']),
            ('get_user_tasks', (214, 'u3'), []),
            ('update_task', (218, 'task_id_8', 'fix docs', 2), True),
            ('assign_task', (223, 'task_id_9', 'u2', 238), True),
            ('assign_task', (225, 'task_id_11', 'u2', 250), False),
            ('list_tasks_sorted', (229, 1), ['task_id_5']),
            ('search_tasks', (234, 'x', 4), ['task_id_5', 'task_id_7', 'task_id_1', 'task_id_3']),
            ('assign_task', (239, 'task_id_11', 'u2', 257), False),
            ('get_overdue_assignments', (240, 'u3'), []),
            ('complete_task', (244, 'task_id_9', 'u1'), False),
            ('assign_task', (247, 'task_id_7', 'u1', 258), True),
            ('complete_task', (250, 'task_id_6', 'u3'), False),
            ('get_overdue_assignments', (255, 'u2'), ['task_id_1', 'task_id_5', 'task_id_5', 'task_id_9']),
            ('assign_task', (256, 'task_id_10', 'u1', 271), True),
            ('assign_task', (257, 'task_id_3', 'u3', 277), False),
            ('get_user_tasks', (261, 'u2'), []),
            ('complete_task', (262, 'task_id_9', 'u1'), False),
            ('complete_task', (266, 'task_id_11', 'u3'), False),
            ('list_tasks_sorted', (268, 4), ['task_id_5', 'task_id_6', 'task_id_7', 'task_id_1']),
            ('list_tasks_sorted', (273, 8), ['task_id_5', 'task_id_6', 'task_id_7', 'task_id_1', 'task_id_3', 'task_id_4', 'task_id_8', 'task_id_9']),
            ('search_tasks', (276, '', 0), []),
            ('add_task', (281, 'review', 4), 'task_id_11'),
            ('get_overdue_assignments', (282, 'u3'), []),
            ('list_tasks_sorted', (284, 1), ['task_id_5']),
            ('get_overdue_assignments', (286, 'u3'), []),
        ])

    def test_level_4_case_07_randomized_sequence_63(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('add_task', (4, 'write docs', 3), 'task_id_1'),
            ('add_task', (5, 'fix bug', 0), 'task_id_2'),
            ('add_task', (7, 'review', 2), 'task_id_3'),
            ('add_task', (12, 'Fix bug', 2), 'task_id_4'),
            ('get_user_tasks', (17, 'u3'), []),
            ('get_task', (19, 'task_id_5'), None),
            ('add_user', (23, 'u2', 1), True),
            ('get_overdue_assignments', (24, 'u2'), []),
            ('search_tasks', (29, 'x', 0), []),
            ('add_task', (34, 'fix bug', 2), 'task_id_5'),
            ('list_tasks_sorted', (35, 1), ['task_id_1']),
            ('get_overdue_assignments', (38, 'u3'), []),
            ('add_task', (43, 'fix docs', 3), 'task_id_6'),
            ('update_task', (47, 'task_id_7', 'write docs', 1), False),
            ('get_user_tasks', (51, 'u3'), []),
            ('search_tasks', (53, 'Fix', 5), ['task_id_4']),
            ('update_task', (56, 'task_id_3', 'deploy', 1), True),
            ('add_task', (57, 'deploy', 2), 'task_id_7'),
            ('assign_task', (62, 'task_id_5', 'u1', 81), False),
            ('add_task', (66, 'review', 0), 'task_id_8'),
            ('assign_task', (71, 'task_id_8', 'u1', 74), False),
            ('assign_task', (76, 'task_id_8', 'u2', 90), True),
            ('get_task', (78, 'task_id_8'), '{"name": "review", "priority": 0}'),
            ('list_tasks_sorted', (80, 8), ['task_id_1', 'task_id_6', 'task_id_4', 'task_id_5', 'task_id_7', 'task_id_3', 'task_id_2', 'task_id_8']),
            ('get_overdue_assignments', (81, 'u2'), []),
            ('list_tasks_sorted', (83, 8), ['task_id_1', 'task_id_6', 'task_id_4', 'task_id_5', 'task_id_7', 'task_id_3', 'task_id_2', 'task_id_8']),
            ('list_tasks_sorted', (86, 5), ['task_id_1', 'task_id_6', 'task_id_4', 'task_id_5', 'task_id_7']),
            ('list_tasks_sorted', (90, 1), ['task_id_1']),
            ('assign_task', (92, 'task_id_8', 'u3', 103), False),
            ('update_task', (94, 'task_id_5', 'fix docs', 0), True),
            ('get_overdue_assignments', (95, 'u1'), []),
            ('list_tasks_sorted', (98, 6), ['task_id_1', 'task_id_6', 'task_id_4', 'task_id_7', 'task_id_3', 'task_id_2']),
            ('assign_task', (103, 'task_id_9', 'u3', 107), False),
            ('get_overdue_assignments', (107, 'u2'), ['task_id_8']),
            ('complete_task', (110, 'task_id_4', 'u1'), False),
            ('get_overdue_assignments', (111, 'u1'), []),
            ('search_tasks', (115, 'Fix', 3), ['task_id_4']),
            ('add_user', (119, 'u1', 3), True),
            ('assign_task', (122, 'task_id_8', 'u2', 135), True),
            ('get_user_tasks', (124, 'u2'), ['task_id_8']),
            ('assign_task', (127, 'task_id_2', 'u2', 151), False),
            ('update_task', (131, 'task_id_5', 'deploy', 1), True),
            ('add_user', (135, 'u3', 1), True),
            ('assign_task', (139, 'task_id_9', 'u2', 148), False),
            ('complete_task', (140, 'task_id_4', 'u2'), False),
            ('assign_task', (143, 'task_id_2', 'u2', 159), True),
            ('complete_task', (147, 'task_id_3', 'u3'), False),
            ('assign_task', (151, 'task_id_7', 'u1', 172), True),
            ('get_user_tasks', (156, 'u1'), ['task_id_7']),
            ('add_task', (158, 'deploy', 0), 'task_id_9'),
            ('get_overdue_assignments', (159, 'u2'), ['task_id_8', 'task_id_8', 'task_id_2']),
            ('search_tasks', (164, 'x', 1), ['task_id_6']),
            ('list_tasks_sorted', (167, 5), ['task_id_1', 'task_id_6', 'task_id_4', 'task_id_7', 'task_id_3']),
            ('assign_task', (170, 'task_id_5', 'u1', 187), True),
            ('update_task', (171, 'task_id_5', 'Fix bug', 3), True),
            ('search_tasks', (175, '', 1), ['task_id_1']),
            ('assign_task', (176, 'task_id_10', 'u2', 198), False),
            ('assign_task', (178, 'task_id_2', 'u2', 194), True),
            ('complete_task', (183, 'task_id_3', 'u2'), False),
            ('get_task', (184, 'task_id_6'), '{"name": "fix docs", "priority": 3}'),
            ('add_user', (185, 'u3', 2), False),
            ('assign_task', (186, 'task_id_10', 'u1', 204), False),
            ('get_overdue_assignments', (187, 'u1'), ['task_id_7', 'task_id_5']),
            ('search_tasks', (188, 'fix', 2), ['task_id_6', 'task_id_2']),
            ('add_task', (192, 'review', 0), 'task_id_10'),
            ('add_user', (193, 'u1', 1), False),
            ('assign_task', (195, 'task_id_6', 'u2', 198), True),
            ('assign_task', (199, 'task_id_2', 'u3', 220), True),
            ('get_task', (200, 'task_id_7'), '{"name": "deploy", "priority": 2}'),
            ('get_task', (201, 'task_id_8'), '{"name": "review", "priority": 0}'),
            ('add_user', (206, 'u2', 1), False),
            ('complete_task', (207, 'task_id_5', 'u2'), False),
            ('complete_task', (209, 'task_id_8', 'u3'), False),
            ('get_overdue_assignments', (211, 'u1'), ['task_id_7', 'task_id_5']),
            ('list_tasks_sorted', (212, 8), ['task_id_1', 'task_id_5', 'task_id_6', 'task_id_4', 'task_id_7', 'task_id_3', 'task_id_2', 'task_id_8']),
            ('assign_task', (215, 'task_id_3', 'u2', 225), True),
            ('get_overdue_assignments', (218, 'u2'), ['task_id_8', 'task_id_8', 'task_id_2', 'task_id_2', 'task_id_6']),
            ('assign_task', (220, 'task_id_10', 'u2', 245), False),
            ('assign_task', (223, 'task_id_9', 'u3', 232), True),
            ('assign_task', (226, 'task_id_3', 'u2', 246), True),
            ('get_task', (227, 'task_id_4'), '{"name": "Fix bug", "priority": 2}'),
            ('complete_task', (229, 'task_id_2', 'u1'), False),
            ('add_task', (232, 'deploy', 3), 'task_id_11'),
            ('get_user_tasks', (236, 'u3'), []),
            ('add_user', (238, 'u2', 0), False),
            ('get_task', (241, 'task_id_6'), '{"name": "fix docs", "priority": 3}'),
            ('update_task', (243, 'task_id_11', 'Fix bug', 1), True),
            ('complete_task', (246, 'task_id_10', 'u2'), False),
            ('update_task', (249, 'task_id_10', 'review', 3), True),
            ('assign_task', (253, 'task_id_1', 'u2', 272), True),
        ])

    def test_level_4_case_08_randomized_sequence_64(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('add_task', (4, 'fix docs', 3), 'task_id_1'),
            ('add_task', (9, 'write docs', 1), 'task_id_2'),
            ('add_task', (11, 'deploy', 1), 'task_id_3'),
            ('add_task', (12, 'Fix bug', 0), 'task_id_4'),
            ('add_task', (17, 'Fix bug', 4), 'task_id_5'),
            ('add_task', (19, 'deploy', 1), 'task_id_6'),
            ('get_user_tasks', (22, 'u2'), []),
            ('assign_task', (25, 'task_id_6', 'u2', 48), False),
            ('assign_task', (29, 'task_id_1', 'u1', 37), False),
            ('update_task', (33, 'task_id_2', 'review', 2), True),
            ('get_user_tasks', (35, 'u1'), []),
            ('complete_task', (38, 'task_id_1', 'u1'), False),
            ('get_task', (41, 'task_id_7'), None),
            ('get_overdue_assignments', (43, 'u3'), []),
            ('get_overdue_assignments', (45, 'u3'), []),
            ('add_user', (48, 'u2', 2), True),
            ('search_tasks', (50, 'docs', -1), []),
            ('add_task', (52, 'fix bug', 1), 'task_id_7'),
            ('get_overdue_assignments', (55, 'u2'), []),
            ('add_task', (59, 'review', 4), 'task_id_8'),
            ('add_task', (60, 'review', 1), 'task_id_9'),
            ('assign_task', (61, 'task_id_5', 'u3', 78), False),
            ('complete_task', (63, 'task_id_7', 'u2'), False),
            ('search_tasks', (65, 'fix', 1), ['task_id_1']),
            ('get_user_tasks', (70, 'u1'), []),
            ('get_user_tasks', (75, 'u2'), []),
            ('add_user', (80, 'u2', 2), False),
            ('add_user', (81, 'u3', 0), True),
            ('assign_task', (82, 'task_id_6', 'u3', 98), False),
            ('add_task', (83, 'fix bug', 4), 'task_id_10'),
            ('assign_task', (88, 'task_id_7', 'u2', 92), True),
            ('update_task', (92, 'task_id_3', 'write docs', 4), True),
            ('get_task', (93, 'task_id_1'), '{"name": "fix docs", "priority": 3}'),
            ('get_overdue_assignments', (95, 'u1'), []),
            ('assign_task', (97, 'task_id_3', 'u1', 107), False),
            ('list_tasks_sorted', (100, 0), []),
            ('assign_task', (103, 'task_id_5', 'u2', 127), True),
            ('get_user_tasks', (108, 'u1'), []),
            ('assign_task', (110, 'task_id_6', 'u2', 128), True),
            ('assign_task', (112, 'task_id_3', 'u1', 123), False),
            ('get_user_tasks', (117, 'u3'), []),
            ('get_task', (119, 'task_id_5'), '{"name": "Fix bug", "priority": 4}'),
            ('search_tasks', (123, '', 1), ['task_id_3']),
            ('get_overdue_assignments', (127, 'u1'), []),
            ('list_tasks_sorted', (128, 0), []),
            ('get_user_tasks', (130, 'u2'), []),
            ('get_overdue_assignments', (134, 'u3'), []),
            ('assign_task', (139, 'task_id_7', 'u2', 154), True),
            ('add_user', (143, 'u2', 2), False),
            ('assign_task', (148, 'task_id_3', 'u1', 170), False),
            ('add_user', (150, 'u3', 1), False),
            ('add_task', (154, 'fix docs', 1), 'task_id_11'),
            ('get_overdue_assignments', (159, 'u2'), ['task_id_7', 'task_id_5', 'task_id_6', 'task_id_7']),
            ('search_tasks', (164, 'docs', 3), ['task_id_3', 'task_id_1', 'task_id_11']),
            ('complete_task', (169, 'task_id_9', 'u1'), False),
            ('get_overdue_assignments', (173, 'u1'), []),
            ('add_task', (178, 'write docs', 1), 'task_id_12'),
            ('assign_task', (182, 'task_id_9', 'u3', 193), False),
            ('search_tasks', (186, 'x', 3), ['task_id_5', 'task_id_10', 'task_id_1']),
            ('assign_task', (190, 'task_id_7', 'u1', 202), False),
            ('assign_task', (195, 'task_id_12', 'u2', 198), True),
            ('assign_task', (196, 'task_id_2', 'u1', 198), False),
            ('assign_task', (201, 'task_id_9', 'u2', 224), True),
            ('get_user_tasks', (202, 'u2'), ['task_id_9']),
            ('update_task', (206, 'task_id_11', 'Fix bug', 0), True),
            ('assign_task', (208, 'task_id_4', 'u1', 213), False),
            ('get_overdue_assignments', (212, 'u2'), ['task_id_7', 'task_id_5', 'task_id_6', 'task_id_7', 'task_id_12']),
            ('get_task', (217, 'task_id_7'), '{"name": "fix bug", "priority": 1}'),
            ('update_task', (219, 'task_id_7', 'fix bug', 0), True),
            ('get_overdue_assignments', (224, 'u2'), ['task_id_7', 'task_id_5', 'task_id_6', 'task_id_7', 'task_id_12', 'task_id_9']),
            ('search_tasks', (226, '', 2), ['task_id_3', 'task_id_5']),
            ('get_task', (230, 'task_id_1'), '{"name": "fix docs", "priority": 3}'),
            ('add_user', (232, 'u3', 0), False),
            ('get_task', (235, 'task_id_3'), '{"name": "write docs", "priority": 4}'),
            ('update_task', (239, 'task_id_4', 'review', 2), True),
            ('get_task', (241, 'task_id_8'), '{"name": "review", "priority": 4}'),
            ('get_overdue_assignments', (242, 'u2'), ['task_id_7', 'task_id_5', 'task_id_6', 'task_id_7', 'task_id_12', 'task_id_9']),
            ('get_task', (246, 'task_id_8'), '{"name": "review", "priority": 4}'),
            ('complete_task', (250, 'task_id_10', 'u2'), False),
            ('update_task', (251, 'task_id_3', 'Fix bug', 4), True),
            ('get_task', (254, 'task_id_3'), '{"name": "Fix bug", "priority": 4}'),
            ('assign_task', (257, 'task_id_7', 'u2', 274), True),
            ('get_overdue_assignments', (262, 'u3'), []),
            ('get_overdue_assignments', (265, 'u1'), []),
            ('add_user', (266, 'u3', 1), False),
            ('assign_task', (267, 'task_id_13', 'u1', 292), False),
            ('assign_task', (272, 'task_id_13', 'u1', 284), False),
            ('assign_task', (277, 'task_id_3', 'u2', 297), True),
            ('add_user', (281, 'u1', 3), True),
            ('update_task', (286, 'task_id_12', 'fix docs', 1), True),
        ])


if __name__ == "__main__":
    unittest.main()
