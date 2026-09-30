"""
Level 2 tests for Text Editor.

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


class TestLevel2(unittest.TestCase):
    def setUp(self):
        self.impl = TextEditorImpl()

    def test_level_2_case_01_example_from_spec(self):
        """The Level 2 example table."""
        run_steps(self, self.impl, [
            ('insert', ('abcdef',), 'abcdef'),
            ('select', (1, 4), 'bcd'),
            ('copy', (), 'bcd'),
            ('insert', ('X',), 'aXef'),
            ('paste', (), 'aXbcdef'),
            ('select', (6, 2), 'bcde'),
            ('backspace', (), 'aXf'),
            ('get_cursor', (), 2),
            ('select', (-5, 1), 'a'),
            ('move_cursor', (3,), 'aXf'),
            ('paste', (), 'aXfbcd'),
            ('select', (2, 2), ''),
            ('copy', (), 'bcd'),
        ])

    def test_level_2_case_02_paste_with_empty_clipboard(self):
        run_steps(self, self.impl, [
            ('insert', ('abc',), 'abc'),
            ('paste', (), 'abc'),
            ('select', (0, 1), 'a'),
            ('paste', (), 'bc'),
            ('get_cursor', (), 0),
        ])

    def test_level_2_case_03_delete_forward_removes_selection(self):
        run_steps(self, self.impl, [
            ('insert', ('hello world',), 'hello world'),
            ('select', (5, 11), ' world'),
            ('delete_forward', (), 'hello'),
            ('get_cursor', (), 5),
            ('delete_forward', (), 'hello'),
        ])

    def test_level_2_case_04_select_moves_cursor_to_right_end(self):
        run_steps(self, self.impl, [
            ('insert', ('abcdef',), 'abcdef'),
            ('select', (4, 1), 'bcd'),
            ('get_cursor', (), 4),
            ('move_cursor', (0,), 'abcdef'),
            ('insert', ('>',), '>abcdef'),
        ])

    def test_level_2_case_05_selection_cleared_after_edit(self):
        run_steps(self, self.impl, [
            ('insert', ('abc',), 'abc'),
            ('select', (0, 3), 'abc'),
            ('insert', ('x',), 'x'),
            ('insert', ('y',), 'xy'),
            ('copy', (), ''),
        ])

    def test_level_2_case_06_copy_paste_multiple_times(self):
        run_steps(self, self.impl, [
            ('insert', ('ab',), 'ab'),
            ('select', (0, 2), 'ab'),
            ('copy', (), 'ab'),
            ('move_cursor', (2,), 'ab'),
            ('paste', (), 'abab'),
            ('paste', (), 'ababab'),
            ('get_cursor', (), 6),
        ])

    def test_level_2_case_07_randomized_sequence_37(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('select', (-1, 12), ''),
            ('get_cursor', (), 0),
            ('copy', (), ''),
            ('copy', (), ''),
            ('backspace', (), ''),
            ('get_cursor', (), 0),
            ('move_cursor', (6,), ''),
            ('select', (8, 5), ''),
            ('get_cursor', (), 0),
            ('move_cursor', (4,), ''),
            ('paste', (), ''),
            ('delete_forward', (), ''),
            ('insert', ('a',), 'a'),
            ('insert', ('a',), 'aa'),
            ('backspace', (), 'a'),
            ('paste', (), 'a'),
            ('get_cursor', (), 1),
            ('delete_forward', (), 'a'),
            ('backspace', (), ''),
            ('move_cursor', (9,), ''),
            ('backspace', (), ''),
            ('insert', ('Q',), 'Q'),
            ('get_cursor', (), 1),
            ('backspace', (), ''),
            ('insert', ('a',), 'a'),
            ('select', (12, 3), ''),
            ('insert', ('Q',), 'aQ'),
            ('insert', ('xyz',), 'aQxyz'),
            ('move_cursor', (0,), 'aQxyz'),
            ('copy', (), ''),
            ('insert', ('a',), 'aaQxyz'),
            ('copy', (), ''),
            ('insert', ('xyz',), 'axyzaQxyz'),
            ('select', (6, 8), 'xy'),
            ('paste', (), 'axyzaQz'),
            ('get_cursor', (), 6),
            ('move_cursor', (9,), 'axyzaQz'),
            ('insert', ('bc',), 'axyzaQzbc'),
            ('insert', ('Q',), 'axyzaQzbcQ'),
            ('get_cursor', (), 10),
            ('delete_forward', (), 'axyzaQzbcQ'),
            ('insert', ('a',), 'axyzaQzbcQa'),
            ('move_cursor', (1,), 'axyzaQzbcQa'),
            ('insert', ('bc',), 'abcxyzaQzbcQa'),
            ('move_cursor', (-2,), 'abcxyzaQzbcQa'),
            ('insert', ('bc',), 'bcabcxyzaQzbcQa'),
            ('insert', ('bc',), 'bcbcabcxyzaQzbcQa'),
            ('get_cursor', (), 4),
            ('select', (11, 6), 'cxyza'),
            ('move_cursor', (-2,), 'bcbcabcxyzaQzbcQa'),
        ])

    def test_level_2_case_08_randomized_sequence_38(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('get_cursor', (), 0),
            ('delete_forward', (), ''),
            ('select', (-1, 3), ''),
            ('select', (3, -2), ''),
            ('get_cursor', (), 0),
            ('insert', ('xyz',), 'xyz'),
            ('move_cursor', (9,), 'xyz'),
            ('move_cursor', (9,), 'xyz'),
            ('move_cursor', (10,), 'xyz'),
            ('backspace', (), 'xy'),
            ('insert', ('Q',), 'xyQ'),
            ('insert', ('',), 'xyQ'),
            ('insert', ('Q',), 'xyQQ'),
            ('insert', ('',), 'xyQQ'),
            ('move_cursor', (6,), 'xyQQ'),
            ('paste', (), 'xyQQ'),
            ('copy', (), ''),
            ('paste', (), 'xyQQ'),
            ('backspace', (), 'xyQ'),
            ('insert', ('a',), 'xyQa'),
            ('move_cursor', (9,), 'xyQa'),
            ('insert', ('',), 'xyQa'),
            ('insert', ('',), 'xyQa'),
            ('move_cursor', (0,), 'xyQa'),
            ('move_cursor', (12,), 'xyQa'),
            ('delete_forward', (), 'xyQa'),
            ('move_cursor', (2,), 'xyQa'),
            ('insert', ('xyz',), 'xyxyzQa'),
            ('select', (0, 9), 'xyxyzQa'),
            ('move_cursor', (1,), 'xyxyzQa'),
            ('backspace', (), 'yxyzQa'),
            ('backspace', (), 'yxyzQa'),
            ('move_cursor', (-2,), 'yxyzQa'),
            ('insert', ('',), 'yxyzQa'),
            ('paste', (), 'yxyzQa'),
            ('insert', ('xyz',), 'xyzyxyzQa'),
            ('copy', (), ''),
            ('insert', ('Q',), 'xyzQyxyzQa'),
            ('copy', (), ''),
            ('select', (12, 3), 'QyxyzQa'),
            ('copy', (), 'QyxyzQa'),
            ('backspace', (), 'xyz'),
            ('insert', ('',), 'xyz'),
            ('insert', ('',), 'xyz'),
            ('paste', (), 'xyzQyxyzQa'),
            ('insert', ('Q',), 'xyzQyxyzQaQ'),
            ('backspace', (), 'xyzQyxyzQa'),
            ('backspace', (), 'xyzQyxyzQ'),
            ('select', (0, 4), 'xyzQ'),
            ('insert', ('Q',), 'QyxyzQ'),
        ])


if __name__ == "__main__":
    unittest.main()
