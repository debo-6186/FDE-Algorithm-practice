"""
Level 2 tests for Task Manager.

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


class TestLevel2(unittest.TestCase):
    def setUp(self):
        self.impl = TaskManagerImpl()

    def test_level_2_case_01_example_from_spec(self):
        """The Level 2 example table."""
        run_steps(self, self.impl, [
            ('add_task', (1, 'Fix login bug', 5), 'task_id_1'),
            ('add_task', (2, 'Write docs', 2), 'task_id_2'),
            ('add_task', (3, 'Fix typo in docs', 5), 'task_id_3'),
            ('add_task', (4, 'Deploy', 9), 'task_id_4'),
            ('search_tasks', (5, 'Fix', 10), ['task_id_1', 'task_id_3']),
            ('search_tasks', (6, 'docs', 1), ['task_id_3']),
            ('search_tasks', (7, 'fix', 10), []),
            ('list_tasks_sorted', (8, 3), ['task_id_4', 'task_id_1', 'task_id_3']),
            ('update_task', (9, 'task_id_2', 'Write docs', 10), True),
            ('list_tasks_sorted', (10, 10), ['task_id_2', 'task_id_4', 'task_id_1', 'task_id_3']),
        ])

    def test_level_2_case_02_creation_order_not_string_order(self):
        """task_id_10 was created after task_id_2, so it comes later on ties."""
        run_steps(self, self.impl, [
            ('add_task', (1, 'same', 1), 'task_id_1'),
            ('add_task', (2, 'same', 1), 'task_id_2'),
            ('add_task', (3, 'same', 1), 'task_id_3'),
            ('add_task', (4, 'same', 1), 'task_id_4'),
            ('add_task', (5, 'same', 1), 'task_id_5'),
            ('add_task', (6, 'same', 1), 'task_id_6'),
            ('add_task', (7, 'same', 1), 'task_id_7'),
            ('add_task', (8, 'same', 1), 'task_id_8'),
            ('add_task', (9, 'same', 1), 'task_id_9'),
            ('add_task', (10, 'same', 1), 'task_id_10'),
            ('add_task', (11, 'same', 1), 'task_id_11'),
            ('list_tasks_sorted', (12, 4), ['task_id_1', 'task_id_2', 'task_id_3', 'task_id_4']),
            ('update_task', (13, 'task_id_10', 'same', 2), True),
            ('update_task', (14, 'task_id_2', 'same', 2), True),
            ('list_tasks_sorted', (15, 3), ['task_id_2', 'task_id_10', 'task_id_1']),
        ])

    def test_level_2_case_03_max_results_zero_or_negative(self):
        run_steps(self, self.impl, [
            ('add_task', (1, 'a', 1), 'task_id_1'),
            ('search_tasks', (2, 'a', 0), []),
            ('search_tasks', (3, 'a', -1), []),
            ('list_tasks_sorted', (4, 0), []),
        ])

    def test_level_2_case_04_empty_filter_matches_all(self):
        run_steps(self, self.impl, [
            ('add_task', (1, 'a', 1), 'task_id_1'),
            ('add_task', (2, 'b', 2), 'task_id_2'),
            ('search_tasks', (3, '', 5), ['task_id_2', 'task_id_1']),
        ])

    def test_level_2_case_05_search_uses_current_name(self):
        run_steps(self, self.impl, [
            ('add_task', (1, 'old name', 1), 'task_id_1'),
            ('update_task', (2, 'task_id_1', 'new name', 1), True),
            ('search_tasks', (3, 'old', 5), []),
            ('search_tasks', (4, 'new', 5), ['task_id_1']),
        ])

    def test_level_2_case_06_no_tasks_then_one(self):
        run_steps(self, self.impl, [
            ('list_tasks_sorted', (1, 5), []),
            ('search_tasks', (2, 'x', 5), []),
            ('add_task', (3, 'x', 1), 'task_id_1'),
            ('search_tasks', (4, 'x', 5), ['task_id_1']),
        ])

    def test_level_2_case_07_randomized_sequence_35(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('add_task', (5, 'review', 2), 'task_id_1'),
            ('add_task', (7, 'write docs', 4), 'task_id_2'),
            ('add_task', (8, 'write docs', 2), 'task_id_3'),
            ('list_tasks_sorted', (13, 0), []),
            ('add_task', (18, 'review', 0), 'task_id_4'),
            ('search_tasks', (21, 'Fix', 1), []),
            ('add_task', (22, 'fix bug', 3), 'task_id_5'),
            ('add_task', (25, 'fix bug', 1), 'task_id_6'),
            ('search_tasks', (30, 'docs', 2), ['task_id_2', 'task_id_3']),
            ('update_task', (35, 'task_id_3', 'deploy', 4), True),
            ('search_tasks', (40, 'docs', 3), ['task_id_2']),
            ('add_task', (44, 'Fix bug', 3), 'task_id_7'),
            ('search_tasks', (48, 'Fix', 0), []),
            ('search_tasks', (53, 'fix', -1), []),
            ('list_tasks_sorted', (54, 2), ['task_id_2', 'task_id_3']),
            ('get_task', (58, 'task_id_1'), '{"name": "review", "priority": 2}'),
            ('get_task', (62, 'task_id_3'), '{"name": "deploy", "priority": 4}'),
            ('get_task', (65, 'task_id_7'), '{"name": "Fix bug", "priority": 3}'),
            ('list_tasks_sorted', (69, 8), ['task_id_2', 'task_id_3', 'task_id_5', 'task_id_7', 'task_id_1', 'task_id_6', 'task_id_4']),
            ('update_task', (71, 'task_id_8', 'deploy', 0), False),
            ('search_tasks', (74, 'x', 5), ['task_id_5', 'task_id_7', 'task_id_6']),
            ('search_tasks', (77, '', 3), ['task_id_2', 'task_id_3', 'task_id_5']),
            ('add_task', (81, 'fix docs', 1), 'task_id_8'),
            ('add_task', (85, 'Fix bug', 3), 'task_id_9'),
            ('update_task', (86, 'task_id_8', 'review', 0), True),
            ('get_task', (88, 'task_id_2'), '{"name": "write docs", "priority": 4}'),
            ('search_tasks', (91, 'x', 0), []),
            ('list_tasks_sorted', (96, 3), ['task_id_2', 'task_id_3', 'task_id_5']),
            ('add_task', (100, 'fix docs', 4), 'task_id_10'),
            ('update_task', (104, 'task_id_4', 'deploy', 0), True),
            ('list_tasks_sorted', (108, 0), []),
            ('list_tasks_sorted', (113, 4), ['task_id_2', 'task_id_3', 'task_id_10', 'task_id_5']),
            ('search_tasks', (115, 'docs', -1), []),
            ('add_task', (120, 'write docs', 0), 'task_id_11'),
            ('update_task', (121, 'task_id_12', 'fix docs', 0), False),
            ('list_tasks_sorted', (122, 5), ['task_id_2', 'task_id_3', 'task_id_10', 'task_id_5', 'task_id_7']),
            ('add_task', (125, 'review', 3), 'task_id_12'),
            ('add_task', (129, 'deploy', 3), 'task_id_13'),
            ('add_task', (130, 'Fix bug', 2), 'task_id_14'),
            ('update_task', (135, 'task_id_13', 'fix bug', 1), True),
            ('list_tasks_sorted', (138, 5), ['task_id_2', 'task_id_3', 'task_id_10', 'task_id_5', 'task_id_7']),
            ('search_tasks', (142, 'fix', 3), ['task_id_10', 'task_id_5', 'task_id_6']),
            ('update_task', (147, 'task_id_1', 'Fix bug', 3), True),
            ('add_task', (149, 'review', 0), 'task_id_15'),
            ('get_task', (152, 'task_id_5'), '{"name": "fix bug", "priority": 3}'),
            ('update_task', (156, 'task_id_7', 'deploy', 2), True),
            ('search_tasks', (157, '', 0), []),
            ('list_tasks_sorted', (160, 6), ['task_id_2', 'task_id_3', 'task_id_10', 'task_id_1', 'task_id_5', 'task_id_9']),
            ('search_tasks', (162, 'docs', 3), ['task_id_2', 'task_id_10', 'task_id_11']),
            ('add_task', (164, 'write docs', 3), 'task_id_16'),
        ])

    def test_level_2_case_08_randomized_sequence_36(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('add_task', (3, 'write docs', 0), 'task_id_1'),
            ('add_task', (4, 'write docs', 3), 'task_id_2'),
            ('add_task', (7, 'fix docs', 0), 'task_id_3'),
            ('update_task', (12, 'task_id_4', 'write docs', 3), False),
            ('update_task', (14, 'task_id_1', 'deploy', 1), True),
            ('update_task', (19, 'task_id_4', 'fix docs', 2), False),
            ('add_task', (24, 'Fix bug', 1), 'task_id_4'),
            ('list_tasks_sorted', (28, 4), ['task_id_2', 'task_id_1', 'task_id_4', 'task_id_3']),
            ('add_task', (33, 'review', 4), 'task_id_5'),
            ('update_task', (36, 'task_id_6', 'Fix bug', 2), False),
            ('get_task', (38, 'task_id_2'), '{"name": "write docs", "priority": 3}'),
            ('list_tasks_sorted', (40, 8), ['task_id_5', 'task_id_2', 'task_id_1', 'task_id_4', 'task_id_3']),
            ('get_task', (41, 'task_id_3'), '{"name": "fix docs", "priority": 0}'),
            ('get_task', (43, 'task_id_6'), None),
            ('add_task', (44, 'Fix bug', 2), 'task_id_6'),
            ('search_tasks', (46, 'x', 4), ['task_id_6', 'task_id_4', 'task_id_3']),
            ('get_task', (47, 'task_id_7'), None),
            ('update_task', (50, 'task_id_5', 'review', 4), True),
            ('update_task', (51, 'task_id_4', 'fix bug', 3), True),
            ('update_task', (52, 'task_id_4', 'write docs', 2), True),
            ('add_task', (54, 'fix bug', 1), 'task_id_7'),
            ('add_task', (55, 'fix docs', 3), 'task_id_8'),
            ('get_task', (56, 'task_id_7'), '{"name": "fix bug", "priority": 1}'),
            ('update_task', (57, 'task_id_8', 'write docs', 0), True),
            ('update_task', (61, 'task_id_6', 'write docs', 0), True),
            ('get_task', (65, 'task_id_7'), '{"name": "fix bug", "priority": 1}'),
            ('update_task', (69, 'task_id_2', 'fix docs', 4), True),
            ('list_tasks_sorted', (74, 0), []),
            ('search_tasks', (75, 'fix', 4), ['task_id_2', 'task_id_7', 'task_id_3']),
            ('search_tasks', (77, 'fix', 2), ['task_id_2', 'task_id_7']),
            ('get_task', (82, 'task_id_1'), '{"name": "deploy", "priority": 1}'),
            ('get_task', (87, 'task_id_2'), '{"name": "fix docs", "priority": 4}'),
            ('get_task', (91, 'task_id_3'), '{"name": "fix docs", "priority": 0}'),
            ('get_task', (92, 'task_id_4'), '{"name": "write docs", "priority": 2}'),
            ('search_tasks', (96, 'Fix', 0), []),
            ('search_tasks', (100, 'x', 0), []),
            ('search_tasks', (101, 'docs', 5), ['task_id_2', 'task_id_4', 'task_id_3', 'task_id_6', 'task_id_8']),
            ('update_task', (102, 'task_id_3', 'fix bug', 2), True),
            ('add_task', (105, 'review', 1), 'task_id_9'),
            ('search_tasks', (106, '', 0), []),
            ('search_tasks', (107, 'Fix', 0), []),
            ('update_task', (110, 'task_id_6', 'write docs', 4), True),
            ('update_task', (111, 'task_id_8', 'Fix bug', 3), True),
            ('update_task', (112, 'task_id_9', 'fix bug', 4), True),
            ('add_task', (115, 'deploy', 1), 'task_id_10'),
            ('update_task', (120, 'task_id_3', 'fix bug', 1), True),
            ('list_tasks_sorted', (125, 6), ['task_id_2', 'task_id_5', 'task_id_6', 'task_id_9', 'task_id_8', 'task_id_4']),
            ('search_tasks', (128, '', 4), ['task_id_2', 'task_id_5', 'task_id_6', 'task_id_9']),
            ('add_task', (131, 'fix docs', 0), 'task_id_11'),
            ('add_task', (135, 'review', 2), 'task_id_12'),
        ])


if __name__ == "__main__":
    unittest.main()
