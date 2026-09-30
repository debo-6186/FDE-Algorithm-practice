"""
Level 1 tests for Task Manager.

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


class TestLevel1(unittest.TestCase):
    def setUp(self):
        self.impl = TaskManagerImpl()

    def test_level_1_case_01_example_from_spec(self):
        """The Level 1 example table."""
        run_steps(self, self.impl, [
            ('add_task', (1, 'Write report', 3), 'task_id_1'),
            ('add_task', (2, 'Review PR', 5), 'task_id_2'),
            ('get_task', (3, 'task_id_1'), '{"name": "Write report", "priority": 3}'),
            ('get_task', (4, 'task_id_9'), None),
            ('update_task', (5, 'task_id_1', 'Write final report', 4), True),
            ('update_task', (6, 'task_id_9', 'x', 1), False),
            ('get_task', (7, 'task_id_1'), '{"name": "Write final report", "priority": 4}'),
            ('add_task', (8, 'Write report', 3), 'task_id_3'),
        ])

    def test_level_1_case_02_ids_keep_counting(self):
        run_steps(self, self.impl, [
            ('add_task', (1, 't1', 1), 'task_id_1'),
            ('add_task', (2, 't2', 2), 'task_id_2'),
            ('add_task', (3, 't3', 3), 'task_id_3'),
            ('add_task', (4, 't4', 4), 'task_id_4'),
            ('add_task', (5, 't5', 5), 'task_id_5'),
            ('add_task', (6, 't6', 6), 'task_id_6'),
            ('add_task', (7, 't7', 7), 'task_id_7'),
            ('add_task', (8, 't8', 8), 'task_id_8'),
            ('add_task', (9, 't9', 9), 'task_id_9'),
            ('add_task', (10, 't10', 10), 'task_id_10'),
            ('add_task', (11, 't11', 11), 'task_id_11'),
            ('add_task', (12, 't12', 12), 'task_id_12'),
            ('get_task', (13, 'task_id_12'), '{"name": "t12", "priority": 12}'),
            ('get_task', (14, 'task_id_0'), None),
        ])

    def test_level_1_case_03_negative_and_zero_priority(self):
        run_steps(self, self.impl, [
            ('add_task', (1, 'a', 0), 'task_id_1'),
            ('add_task', (2, 'b', -3), 'task_id_2'),
            ('get_task', (3, 'task_id_2'), '{"name": "b", "priority": -3}'),
        ])

    def test_level_1_case_04_update_keeps_id(self):
        run_steps(self, self.impl, [
            ('add_task', (1, 'x', 1), 'task_id_1'),
            ('update_task', (2, 'task_id_1', 'y', 2), True),
            ('update_task', (3, 'task_id_1', 'z', 3), True),
            ('get_task', (4, 'task_id_1'), '{"name": "z", "priority": 3}'),
            ('add_task', (5, 'w', 1), 'task_id_2'),
        ])

    def test_level_1_case_05_randomized_sequence_18(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('add_task', (2, 'deploy', 2), 'task_id_1'),
            ('add_task', (4, 'review', 3), 'task_id_2'),
            ('add_task', (6, 'deploy', 2), 'task_id_3'),
            ('add_task', (8, 'fix docs', 1), 'task_id_4'),
            ('add_task', (10, 'write docs', 4), 'task_id_5'),
            ('add_task', (15, 'Fix bug', 2), 'task_id_6'),
            ('add_task', (18, 'review', 3), 'task_id_7'),
            ('add_task', (23, 'fix docs', 2), 'task_id_8'),
            ('add_task', (28, 'fix docs', 1), 'task_id_9'),
            ('update_task', (32, 'task_id_3', 'Fix bug', 3), True),
            ('add_task', (34, 'fix bug', 1), 'task_id_10'),
            ('add_task', (39, 'fix docs', 3), 'task_id_11'),
            ('update_task', (40, 'task_id_8', 'deploy', 0), True),
            ('update_task', (42, 'task_id_9', 'Fix bug', 3), True),
            ('get_task', (47, 'task_id_11'), '{"name": "fix docs", "priority": 3}'),
            ('get_task', (48, 'task_id_3'), '{"name": "Fix bug", "priority": 3}'),
            ('update_task', (49, 'task_id_7', 'deploy', 3), True),
            ('add_task', (51, 'review', 2), 'task_id_12'),
            ('add_task', (53, 'write docs', 1), 'task_id_13'),
            ('get_task', (57, 'task_id_9'), '{"name": "Fix bug", "priority": 3}'),
            ('add_task', (62, 'fix docs', 3), 'task_id_14'),
            ('update_task', (63, 'task_id_9', 'fix docs', 0), True),
            ('get_task', (64, 'task_id_13'), '{"name": "write docs", "priority": 1}'),
            ('get_task', (68, 'task_id_8'), '{"name": "deploy", "priority": 0}'),
            ('update_task', (73, 'task_id_7', 'Fix bug', 1), True),
            ('get_task', (75, 'task_id_12'), '{"name": "review", "priority": 2}'),
            ('update_task', (78, 'task_id_13', 'write docs', 4), True),
            ('get_task', (80, 'task_id_9'), '{"name": "fix docs", "priority": 0}'),
            ('add_task', (82, 'fix docs', 1), 'task_id_15'),
            ('get_task', (84, 'task_id_4'), '{"name": "fix docs", "priority": 1}'),
            ('add_task', (87, 'fix docs', 2), 'task_id_16'),
            ('get_task', (90, 'task_id_13'), '{"name": "write docs", "priority": 4}'),
            ('get_task', (94, 'task_id_14'), '{"name": "fix docs", "priority": 3}'),
            ('get_task', (99, 'task_id_1'), '{"name": "deploy", "priority": 2}'),
            ('get_task', (103, 'task_id_2'), '{"name": "review", "priority": 3}'),
            ('add_task', (106, 'write docs', 1), 'task_id_17'),
            ('add_task', (109, 'fix bug', 2), 'task_id_18'),
            ('get_task', (112, 'task_id_18'), '{"name": "fix bug", "priority": 2}'),
            ('update_task', (117, 'task_id_8', 'fix bug', 3), True),
            ('add_task', (120, 'write docs', 4), 'task_id_19'),
        ])


if __name__ == "__main__":
    unittest.main()
