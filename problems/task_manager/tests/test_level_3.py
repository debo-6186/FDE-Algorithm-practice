"""
Level 3 tests for Task Manager.

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


class TestLevel3(unittest.TestCase):
    def setUp(self):
        self.impl = TaskManagerImpl()

    def test_level_3_case_01_example_from_spec(self):
        """The Level 3 example table."""
        run_steps(self, self.impl, [
            ('add_task', (1, 'A', 1), 'task_id_1'),
            ('add_task', (2, 'B', 2), 'task_id_2'),
            ('add_user', (3, 'ann', 2), True),
            ('add_user', (4, 'ann', 5), False),
            ('assign_task', (5, 'task_id_1', 'ann', 20), True),
            ('assign_task', (6, 'task_id_2', 'ann', 10), True),
            ('assign_task', (7, 'task_id_1', 'ann', 30), False),
            ('assign_task', (8, 'task_id_9', 'ann', 30), False),
            ('assign_task', (9, 'task_id_1', 'bob', 30), False),
            ('get_user_tasks', (10, 'ann'), ['task_id_1']),
            ('assign_task', (11, 'task_id_2', 'ann', 15), True),
            ('get_user_tasks', (12, 'ann'), ['task_id_2', 'task_id_1']),
            ('get_user_tasks', (13, 'zoe'), []),
        ])

    def test_level_3_case_02_same_task_to_many_users(self):
        run_steps(self, self.impl, [
            ('add_task', (1, 'A', 1), 'task_id_1'),
            ('add_user', (2, 'u1', 1), True),
            ('add_user', (3, 'u2', 1), True),
            ('assign_task', (4, 'task_id_1', 'u1', 10), True),
            ('assign_task', (5, 'task_id_1', 'u2', 10), True),
            ('get_user_tasks', (6, 'u1'), ['task_id_1']),
            ('get_user_tasks', (7, 'u2'), ['task_id_1']),
        ])

    def test_level_3_case_03_same_task_twice_to_one_user(self):
        run_steps(self, self.impl, [
            ('add_task', (1, 'A', 1), 'task_id_1'),
            ('add_user', (2, 'u', 3), True),
            ('assign_task', (3, 'task_id_1', 'u', 50), True),
            ('assign_task', (4, 'task_id_1', 'u', 20), True),
            ('get_user_tasks', (5, 'u'), ['task_id_1', 'task_id_1']),
        ])

    def test_level_3_case_04_ties_on_finish_time_use_assignment_order(self):
        run_steps(self, self.impl, [
            ('add_task', (1, 'A', 1), 'task_id_1'),
            ('add_task', (2, 'B', 1), 'task_id_2'),
            ('add_user', (3, 'u', 5), True),
            ('assign_task', (4, 'task_id_2', 'u', 30), True),
            ('assign_task', (5, 'task_id_1', 'u', 30), True),
            ('get_user_tasks', (6, 'u'), ['task_id_2', 'task_id_1']),
        ])

    def test_level_3_case_05_quota_frees_when_assignment_ends(self):
        run_steps(self, self.impl, [
            ('add_task', (1, 'A', 1), 'task_id_1'),
            ('add_user', (2, 'u', 1), True),
            ('assign_task', (3, 'task_id_1', 'u', 5), True),
            ('assign_task', (4, 'task_id_1', 'u', 9), False),
            ('assign_task', (5, 'task_id_1', 'u', 9), True),
            ('get_user_tasks', (8, 'u'), ['task_id_1']),
            ('get_user_tasks', (9, 'u'), []),
        ])

    def test_level_3_case_06_zero_quota_user(self):
        run_steps(self, self.impl, [
            ('add_task', (1, 'A', 1), 'task_id_1'),
            ('add_user', (2, 'u', 0), True),
            ('assign_task', (3, 'task_id_1', 'u', 5), False),
        ])

    def test_level_3_case_07_randomized_sequence_45(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('add_task', (3, 'write docs', 0), 'task_id_1'),
            ('add_task', (6, 'fix bug', 3), 'task_id_2'),
            ('add_task', (7, 'fix bug', 2), 'task_id_3'),
            ('get_user_tasks', (8, 'u1'), []),
            ('assign_task', (11, 'task_id_2', 'u1', 36), False),
            ('add_task', (15, 'review', 0), 'task_id_4'),
            ('update_task', (16, 'task_id_3', 'review', 2), True),
            ('search_tasks', (17, 'docs', 5), ['task_id_1']),
            ('assign_task', (21, 'task_id_5', 'u3', 39), False),
            ('assign_task', (26, 'task_id_3', 'u3', 48), False),
            ('list_tasks_sorted', (27, 5), ['task_id_2', 'task_id_3', 'task_id_1', 'task_id_4']),
            ('assign_task', (29, 'task_id_1', 'u1', 45), False),
            ('search_tasks', (34, '', 5), ['task_id_2', 'task_id_3', 'task_id_1', 'task_id_4']),
            ('add_task', (38, 'fix bug', 4), 'task_id_5'),
            ('add_task', (42, 'fix bug', 4), 'task_id_6'),
            ('assign_task', (47, 'task_id_5', 'u2', 58), False),
            ('update_task', (50, 'task_id_1', 'write docs', 0), True),
            ('get_user_tasks', (54, 'u1'), []),
            ('get_user_tasks', (59, 'u2'), []),
            ('get_task', (64, 'task_id_4'), '{"name": "review", "priority": 0}'),
            ('get_task', (67, 'task_id_2'), '{"name": "fix bug", "priority": 3}'),
            ('get_user_tasks', (72, 'u2'), []),
            ('add_task', (73, 'write docs', 3), 'task_id_7'),
            ('update_task', (74, 'task_id_4', 'fix bug', 0), True),
            ('get_user_tasks', (76, 'u1'), []),
            ('get_user_tasks', (80, 'u3'), []),
            ('search_tasks', (83, 'Fix', 4), []),
            ('get_user_tasks', (88, 'u2'), []),
            ('assign_task', (93, 'task_id_7', 'u1', 104), False),
            ('search_tasks', (96, 'x', 3), ['task_id_5', 'task_id_6', 'task_id_2']),
            ('assign_task', (97, 'task_id_1', 'u3', 112), False),
            ('assign_task', (102, 'task_id_4', 'u3', 110), False),
            ('add_task', (104, 'write docs', 4), 'task_id_8'),
            ('assign_task', (107, 'task_id_8', 'u3', 130), False),
            ('add_user', (111, 'u3', 3), True),
            ('add_user', (115, 'u1', 3), True),
            ('add_task', (116, 'fix docs', 1), 'task_id_9'),
            ('get_task', (120, 'task_id_1'), '{"name": "write docs", "priority": 0}'),
            ('assign_task', (123, 'task_id_2', 'u3', 143), True),
            ('assign_task', (127, 'task_id_2', 'u3', 145), True),
            ('assign_task', (129, 'task_id_4', 'u1', 153), True),
            ('get_user_tasks', (130, 'u2'), []),
            ('assign_task', (135, 'task_id_3', 'u3', 154), True),
            ('search_tasks', (138, 'Fix', -1), []),
            ('add_task', (140, 'deploy', 0), 'task_id_10'),
            ('search_tasks', (145, '', 4), ['task_id_5', 'task_id_6', 'task_id_8', 'task_id_2']),
            ('get_task', (150, 'task_id_5'), '{"name": "fix bug", "priority": 4}'),
            ('get_user_tasks', (154, 'u2'), []),
            ('get_task', (159, 'task_id_2'), '{"name": "fix bug", "priority": 3}'),
            ('list_tasks_sorted', (164, 1), ['task_id_5']),
            ('list_tasks_sorted', (169, 3), ['task_id_5', 'task_id_6', 'task_id_8']),
            ('get_task', (174, 'task_id_3'), '{"name": "review", "priority": 2}'),
            ('assign_task', (175, 'task_id_9', 'u2', 196), False),
            ('assign_task', (177, 'task_id_7', 'u1', 190), True),
            ('get_user_tasks', (179, 'u3'), []),
            ('search_tasks', (180, 'x', 4), ['task_id_5', 'task_id_6', 'task_id_2', 'task_id_9']),
            ('list_tasks_sorted', (184, 2), ['task_id_5', 'task_id_6']),
            ('add_task', (187, 'Fix bug', 1), 'task_id_11'),
            ('get_task', (192, 'task_id_5'), '{"name": "fix bug", "priority": 4}'),
            ('get_user_tasks', (197, 'u1'), []),
            ('add_user', (200, 'u2', 0), True),
            ('assign_task', (202, 'task_id_2', 'u3', 215), True),
            ('assign_task', (206, 'task_id_5', 'u2', 210), False),
            ('assign_task', (208, 'task_id_7', 'u2', 233), False),
            ('get_user_tasks', (210, 'u3'), ['task_id_2']),
            ('search_tasks', (214, '', 0), []),
            ('add_task', (218, 'fix bug', 2), 'task_id_12'),
            ('add_task', (221, 'fix docs', 1), 'task_id_13'),
            ('get_user_tasks', (224, 'u1'), []),
            ('search_tasks', (225, 'x', 2), ['task_id_5', 'task_id_6']),
        ])

    def test_level_3_case_08_randomized_sequence_46(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('add_task', (1, 'fix docs', 4), 'task_id_1'),
            ('add_task', (3, 'fix docs', 0), 'task_id_2'),
            ('add_task', (4, 'review', 0), 'task_id_3'),
            ('add_task', (5, 'write docs', 0), 'task_id_4'),
            ('get_user_tasks', (9, 'u2'), []),
            ('list_tasks_sorted', (11, 8), ['task_id_1', 'task_id_2', 'task_id_3', 'task_id_4']),
            ('add_task', (16, 'fix docs', 3), 'task_id_5'),
            ('update_task', (19, 'task_id_5', 'fix bug', 4), True),
            ('list_tasks_sorted', (22, 6), ['task_id_1', 'task_id_5', 'task_id_2', 'task_id_3', 'task_id_4']),
            ('search_tasks', (25, 'x', 0), []),
            ('assign_task', (30, 'task_id_6', 'u3', 41), False),
            ('assign_task', (31, 'task_id_1', 'u2', 49), False),
            ('search_tasks', (33, 'x', 5), ['task_id_1', 'task_id_5', 'task_id_2']),
            ('assign_task', (35, 'task_id_2', 'u1', 48), False),
            ('assign_task', (36, 'task_id_3', 'u1', 55), False),
            ('assign_task', (37, 'task_id_2', 'u2', 50), False),
            ('assign_task', (42, 'task_id_1', 'u3', 63), False),
            ('update_task', (43, 'task_id_2', 'fix bug', 0), True),
            ('search_tasks', (47, '', 3), ['task_id_1', 'task_id_5', 'task_id_2']),
            ('assign_task', (50, 'task_id_4', 'u2', 73), False),
            ('assign_task', (52, 'task_id_6', 'u2', 65), False),
            ('search_tasks', (54, 'Fix', -1), []),
            ('assign_task', (58, 'task_id_3', 'u3', 78), False),
            ('get_user_tasks', (63, 'u2'), []),
            ('get_task', (65, 'task_id_4'), '{"name": "write docs", "priority": 0}'),
            ('add_user', (68, 'u1', 2), True),
            ('get_task', (72, 'task_id_1'), '{"name": "fix docs", "priority": 4}'),
            ('list_tasks_sorted', (77, 5), ['task_id_1', 'task_id_5', 'task_id_2', 'task_id_3', 'task_id_4']),
            ('assign_task', (80, 'task_id_5', 'u1', 83), True),
            ('assign_task', (82, 'task_id_5', 'u3', 105), False),
            ('add_task', (84, 'review', 0), 'task_id_6'),
            ('assign_task', (85, 'task_id_6', 'u3', 108), False),
            ('add_task', (89, 'fix bug', 4), 'task_id_7'),
            ('assign_task', (92, 'task_id_1', 'u2', 113), False),
            ('update_task', (94, 'task_id_6', 'Fix bug', 3), True),
            ('search_tasks', (97, 'fix', 0), []),
            ('update_task', (100, 'task_id_5', 'write docs', 4), True),
            ('assign_task', (105, 'task_id_2', 'u2', 125), False),
            ('list_tasks_sorted', (109, 6), ['task_id_1', 'task_id_5', 'task_id_7', 'task_id_6', 'task_id_2', 'task_id_3']),
            ('assign_task', (113, 'task_id_7', 'u3', 127), False),
            ('get_user_tasks', (115, 'u1'), []),
            ('update_task', (119, 'task_id_2', 'fix bug', 2), True),
            ('assign_task', (124, 'task_id_2', 'u1', 144), True),
            ('add_task', (127, 'fix docs', 1), 'task_id_8'),
            ('search_tasks', (130, '', 5), ['task_id_1', 'task_id_5', 'task_id_7', 'task_id_6', 'task_id_2']),
            ('get_user_tasks', (134, 'u2'), []),
            ('search_tasks', (137, 'Fix', 0), []),
            ('assign_task', (140, 'task_id_4', 'u3', 165), False),
            ('assign_task', (144, 'task_id_3', 'u2', 147), False),
            ('get_task', (146, 'task_id_9'), None),
            ('add_task', (148, 'Fix bug', 1), 'task_id_9'),
            ('add_task', (151, 'deploy', 2), 'task_id_10'),
            ('assign_task', (153, 'task_id_10', 'u2', 170), False),
            ('search_tasks', (156, 'fix', 5), ['task_id_1', 'task_id_7', 'task_id_2', 'task_id_8']),
            ('assign_task', (159, 'task_id_2', 'u1', 173), True),
            ('add_task', (161, 'Fix bug', 0), 'task_id_11'),
            ('get_task', (164, 'task_id_6'), '{"name": "Fix bug", "priority": 3}'),
            ('add_task', (167, 'write docs', 2), 'task_id_12'),
            ('add_task', (171, 'deploy', 4), 'task_id_13'),
            ('get_task', (173, 'task_id_7'), '{"name": "fix bug", "priority": 4}'),
            ('get_user_tasks', (177, 'u3'), []),
            ('assign_task', (182, 'task_id_5', 'u2', 202), False),
            ('get_task', (185, 'task_id_1'), '{"name": "fix docs", "priority": 4}'),
            ('add_task', (188, 'write docs', 0), 'task_id_14'),
            ('get_task', (190, 'task_id_1'), '{"name": "fix docs", "priority": 4}'),
            ('search_tasks', (191, 'fix', 1), ['task_id_1']),
            ('search_tasks', (194, '', 4), ['task_id_1', 'task_id_5', 'task_id_7', 'task_id_13']),
            ('search_tasks', (197, 'x', 1), ['task_id_1']),
            ('list_tasks_sorted', (202, 3), ['task_id_1', 'task_id_5', 'task_id_7']),
            ('get_task', (203, 'task_id_6'), '{"name": "Fix bug", "priority": 3}'),
        ])


if __name__ == "__main__":
    unittest.main()
