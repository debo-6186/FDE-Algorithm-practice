"""
Level 3 tests for Text Editor.

Each test replays a sequence of calls on a fresh TextEditorImpl() and checks
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

from text_editor_impl import TextEditorImpl

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
        self.impl = TextEditorImpl()

    def test_level_3_case_01_example_from_spec(self):
        """The Level 3 example table."""
        run_steps(self, self.impl, [
            ('insert', ('one',), 'one'),
            ('insert', (' two',), 'one two'),
            ('undo', (), 'one'),
            ('undo', (), ''),
            ('undo', (), ''),
            ('redo', (), 'one'),
            ('get_cursor', (), 3),
            ('move_cursor', (0,), 'one'),
            ('insert', ('>',), '>one'),
            ('redo', (), '>one'),
            ('select', (1, 4), 'one'),
            ('backspace', (), '>'),
            ('undo', (), '>one'),
            ('get_cursor', (), 4),
            ('undo', (), 'one'),
            ('get_cursor', (), 0),
        ])

    def test_level_3_case_02_no_op_edits_are_not_recorded(self):
        run_steps(self, self.impl, [
            ('insert', ('a',), 'a'),
            ('delete_forward', (), 'a'),
            ('move_cursor', (0,), 'a'),
            ('backspace', (), 'a'),
            ('paste', (), 'a'),
            ('undo', (), ''),
            ('undo', (), ''),
        ])

    def test_level_3_case_03_redo_all_the_way(self):
        run_steps(self, self.impl, [
            ('insert', ('a',), 'a'),
            ('insert', ('b',), 'ab'),
            ('insert', ('c',), 'abc'),
            ('undo', (), 'ab'),
            ('undo', (), 'a'),
            ('undo', (), ''),
            ('redo', (), 'a'),
            ('redo', (), 'ab'),
            ('redo', (), 'abc'),
            ('redo', (), 'abc'),
            ('get_cursor', (), 3),
        ])

    def test_level_3_case_04_undo_restores_cursor_before_change(self):
        """redo returns to the state right before the undo (cursor 5)."""
        run_steps(self, self.impl, [
            ('insert', ('abcdef',), 'abcdef'),
            ('move_cursor', (2,), 'abcdef'),
            ('delete_forward', (), 'abdef'),
            ('move_cursor', (5,), 'abdef'),
            ('undo', (), 'abcdef'),
            ('get_cursor', (), 2),
            ('redo', (), 'abdef'),
            ('get_cursor', (), 5),
        ])

    def test_level_3_case_05_undo_paste_over_selection(self):
        run_steps(self, self.impl, [
            ('insert', ('cat dog',), 'cat dog'),
            ('select', (0, 3), 'cat'),
            ('copy', (), 'cat'),
            ('select', (4, 7), 'dog'),
            ('paste', (), 'cat cat'),
            ('undo', (), 'cat dog'),
            ('get_cursor', (), 7),
            ('copy', (), 'cat'),
        ])

    def test_level_3_case_06_undo_with_nothing_done(self):
        run_steps(self, self.impl, [
            ('undo', (), ''),
            ('redo', (), ''),
            ('get_cursor', (), 0),
        ])

    def test_level_3_case_07_randomized_sequence_47(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('delete_forward', (), ''),
            ('backspace', (), ''),
            ('backspace', (), ''),
            ('delete_forward', (), ''),
            ('get_cursor', (), 0),
            ('delete_forward', (), ''),
            ('insert', ('',), ''),
            ('copy', (), ''),
            ('redo', (), ''),
            ('insert', ('',), ''),
            ('paste', (), ''),
            ('insert', ('xyz',), 'xyz'),
            ('select', (1, 1), ''),
            ('select', (3, 5), ''),
            ('redo', (), 'xyz'),
            ('insert', ('xyz',), 'xyzxyz'),
            ('copy', (), ''),
            ('delete_forward', (), 'xyzxyz'),
            ('delete_forward', (), 'xyzxyz'),
            ('select', (1, 1), ''),
            ('paste', (), 'xyzxyz'),
            ('paste', (), 'xyzxyz'),
            ('redo', (), 'xyzxyz'),
            ('insert', ('a',), 'xayzxyz'),
            ('delete_forward', (), 'xazxyz'),
            ('delete_forward', (), 'xaxyz'),
            ('select', (2, -1), 'xa'),
            ('copy', (), 'xa'),
            ('undo', (), 'xazxyz'),
            ('redo', (), 'xaxyz'),
            ('undo', (), 'xazxyz'),
            ('move_cursor', (9,), 'xazxyz'),
            ('insert', ('',), 'xazxyz'),
            ('select', (8, 11), ''),
            ('move_cursor', (10,), 'xazxyz'),
            ('undo', (), 'xayzxyz'),
            ('undo', (), 'xyzxyz'),
            ('redo', (), 'xayzxyz'),
            ('delete_forward', (), 'xazxyz'),
            ('select', (5, 2), 'zxy'),
            ('select', (4, 2), 'zx'),
            ('redo', (), 'xazxyz'),
            ('get_cursor', (), 4),
            ('move_cursor', (-1,), 'xazxyz'),
            ('select', (1, 4), 'azx'),
            ('get_cursor', (), 4),
            ('redo', (), 'xazxyz'),
            ('redo', (), 'xazxyz'),
            ('select', (5, -2), 'xazxy'),
            ('redo', (), 'xazxyz'),
            ('select', (10, 10), ''),
            ('insert', ('xyz',), 'xazxyzxyz'),
            ('get_cursor', (), 9),
            ('select', (5, 10), 'zxyz'),
            ('undo', (), 'xazxyz'),
            ('delete_forward', (), 'xazxyz'),
            ('paste', (), 'xazxyzxa'),
            ('select', (12, 8), ''),
            ('select', (8, 12), ''),
            ('backspace', (), 'xazxyzx'),
            ('copy', (), 'xa'),
            ('paste', (), 'xazxyzxxa'),
            ('move_cursor', (-2,), 'xazxyzxxa'),
            ('select', (1, 3), 'az'),
            ('backspace', (), 'xxyzxxa'),
            ('redo', (), 'xxyzxxa'),
            ('undo', (), 'xazxyzxxa'),
            ('insert', ('',), 'xazxyzxxa'),
            ('redo', (), 'xxyzxxa'),
            ('insert', ('bc',), 'xbcxyzxxa'),
        ])

    def test_level_3_case_08_randomized_sequence_48(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('select', (0, 6), ''),
            ('copy', (), ''),
            ('move_cursor', (6,), ''),
            ('insert', ('',), ''),
            ('insert', ('a',), 'a'),
            ('get_cursor', (), 1),
            ('move_cursor', (10,), 'a'),
            ('get_cursor', (), 1),
            ('undo', (), ''),
            ('insert', ('bc',), 'bc'),
            ('insert', ('',), 'bc'),
            ('insert', ('',), 'bc'),
            ('copy', (), ''),
            ('redo', (), 'bc'),
            ('insert', ('Q',), 'bcQ'),
            ('move_cursor', (3,), 'bcQ'),
            ('copy', (), ''),
            ('insert', ('bc',), 'bcQbc'),
            ('move_cursor', (8,), 'bcQbc'),
            ('insert', ('Q',), 'bcQbcQ'),
            ('undo', (), 'bcQbc'),
            ('select', (3, 8), 'bc'),
            ('backspace', (), 'bcQ'),
            ('insert', ('Q',), 'bcQQ'),
            ('move_cursor', (3,), 'bcQQ'),
            ('insert', ('Q',), 'bcQQQ'),
            ('move_cursor', (5,), 'bcQQQ'),
            ('copy', (), ''),
            ('paste', (), 'bcQQQ'),
            ('move_cursor', (3,), 'bcQQQ'),
            ('backspace', (), 'bcQQ'),
            ('copy', (), ''),
            ('paste', (), 'bcQQ'),
            ('insert', ('a',), 'bcaQQ'),
            ('paste', (), 'bcaQQ'),
            ('backspace', (), 'bcQQ'),
            ('undo', (), 'bcaQQ'),
            ('insert', ('Q',), 'bcaQQQ'),
            ('undo', (), 'bcaQQ'),
            ('select', (5, 4), 'Q'),
            ('select', (0, 10), 'bcaQQ'),
            ('delete_forward', (), ''),
            ('backspace', (), ''),
            ('redo', (), ''),
            ('move_cursor', (8,), ''),
            ('redo', (), ''),
            ('insert', ('bc',), 'bc'),
            ('insert', ('Q',), 'bcQ'),
            ('undo', (), 'bc'),
            ('copy', (), ''),
            ('select', (6, 12), ''),
            ('delete_forward', (), 'bc'),
            ('backspace', (), 'b'),
            ('copy', (), ''),
            ('undo', (), 'bc'),
            ('undo', (), ''),
            ('select', (-2, 8), ''),
            ('insert', ('a',), 'a'),
            ('paste', (), 'a'),
            ('copy', (), ''),
            ('delete_forward', (), 'a'),
            ('undo', (), ''),
            ('copy', (), ''),
            ('undo', (), 'bcaQQ'),
            ('backspace', (), 'bcaQ'),
            ('undo', (), 'bcaQQ'),
            ('backspace', (), 'bcaQ'),
            ('redo', (), 'bcaQ'),
            ('undo', (), 'bcaQQ'),
            ('insert', ('bc',), 'bcaQQbc'),
        ])


if __name__ == "__main__":
    unittest.main()
