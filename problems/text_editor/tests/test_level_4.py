"""
Level 4 tests for Text Editor.

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


class TestLevel4(unittest.TestCase):
    def setUp(self):
        self.impl = TextEditorImpl()

    def test_level_4_case_01_example_from_spec(self):
        """The Level 4 example table."""
        run_steps(self, self.impl, [
            ('insert', ('draft',), 'draft'),
            ('create_document', ('notes',), True),
            ('create_document', ('notes',), False),
            ('switch_document', ('notes',), ''),
            ('insert', ('todo',), 'todo'),
            ('switch_document', ('untitled',), 'draft'),
            ('select', (0, 5), 'draft'),
            ('copy', (), 'draft'),
            ('switch_document', ('notes',), 'todo'),
            ('paste', (), 'tododraft'),
            ('undo', (), 'todo'),
            ('switch_document', ('untitled',), 'draft'),
            ('undo', (), ''),
            ('switch_document', ('missing',), None),
            ('get_cursor', (), 0),
        ])

    def test_level_4_case_02_untitled_already_exists(self):
        run_steps(self, self.impl, [
            ('create_document', ('untitled',), False),
            ('switch_document', ('untitled',), ''),
        ])

    def test_level_4_case_03_cursor_and_selection_are_per_document(self):
        run_steps(self, self.impl, [
            ('insert', ('abcd',), 'abcd'),
            ('select', (1, 3), 'bc'),
            ('create_document', ('b',), True),
            ('switch_document', ('b',), ''),
            ('insert', ('xy',), 'xy'),
            ('switch_document', ('untitled',), 'abcd'),
            ('get_cursor', (), 3),
            ('backspace', (), 'ad'),
        ])

    def test_level_4_case_04_redo_history_is_per_document(self):
        run_steps(self, self.impl, [
            ('insert', ('1',), '1'),
            ('undo', (), ''),
            ('create_document', ('d2',), True),
            ('switch_document', ('d2',), ''),
            ('insert', ('2',), '2'),
            ('switch_document', ('untitled',), ''),
            ('redo', (), '1'),
        ])

    def test_level_4_case_05_undo_history_not_shared(self):
        """Undoing in one document must not consume another document's history."""
        run_steps(self, self.impl, [
            ('insert', ('x',), 'x'),
            ('create_document', ('b',), True),
            ('switch_document', ('b',), ''),
            ('insert', ('yy',), 'yy'),
            ('switch_document', ('untitled',), 'x'),
            ('undo', (), ''),
            ('undo', (), ''),
            ('switch_document', ('b',), 'yy'),
            ('undo', (), ''),
            ('redo', (), 'yy'),
        ])

    def test_level_4_case_06_new_document_is_not_current(self):
        run_steps(self, self.impl, [
            ('create_document', ('other',), True),
            ('insert', ('x',), 'x'),
            ('switch_document', ('other',), ''),
            ('get_cursor', (), 0),
        ])

    def test_level_4_case_07_randomized_sequence_65(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('backspace', (), ''),
            ('delete_forward', (), ''),
            ('redo', (), ''),
            ('get_cursor', (), 0),
            ('select', (6, 12), ''),
            ('delete_forward', (), ''),
            ('copy', (), ''),
            ('create_document', ('untitled',), False),
            ('redo', (), ''),
            ('select', (1, 8), ''),
            ('select', (9, -2), ''),
            ('move_cursor', (0,), ''),
            ('select', (11, 0), ''),
            ('undo', (), ''),
            ('redo', (), ''),
            ('insert', ('xyz',), 'xyz'),
            ('backspace', (), 'xy'),
            ('paste', (), 'xy'),
            ('copy', (), ''),
            ('switch_document', ('d2',), None),
            ('move_cursor', (5,), 'xy'),
            ('select', (9, 0), 'xy'),
            ('undo', (), 'xyz'),
            ('undo', (), ''),
            ('delete_forward', (), ''),
            ('switch_document', ('d1',), None),
            ('insert', ('',), ''),
            ('insert', ('Q',), 'Q'),
            ('insert', ('bc',), 'Qbc'),
            ('copy', (), ''),
            ('select', (4, 0), 'Qbc'),
            ('select', (10, 4), ''),
            ('undo', (), 'Q'),
            ('undo', (), ''),
            ('move_cursor', (2,), ''),
            ('select', (1, 3), ''),
            ('copy', (), ''),
            ('paste', (), ''),
            ('copy', (), ''),
            ('insert', ('a',), 'a'),
            ('move_cursor', (5,), 'a'),
            ('undo', (), ''),
            ('insert', ('bc',), 'bc'),
            ('insert', ('xyz',), 'bcxyz'),
            ('undo', (), 'bc'),
            ('get_cursor', (), 2),
            ('paste', (), 'bc'),
            ('paste', (), 'bc'),
            ('switch_document', ('untitled',), 'bc'),
            ('switch_document', ('d2',), None),
            ('select', (4, 0), 'bc'),
            ('insert', ('',), ''),
            ('redo', (), ''),
            ('copy', (), ''),
            ('select', (11, 6), ''),
            ('redo', (), ''),
            ('redo', (), ''),
            ('create_document', ('d2',), True),
            ('select', (9, 6), ''),
            ('insert', ('a',), 'a'),
            ('move_cursor', (10,), 'a'),
            ('delete_forward', (), 'a'),
            ('paste', (), 'a'),
            ('switch_document', ('d1',), None),
            ('undo', (), ''),
            ('undo', (), 'bc'),
            ('insert', ('xyz',), 'bcxyz'),
            ('move_cursor', (11,), 'bcxyz'),
            ('backspace', (), 'bcxy'),
            ('backspace', (), 'bcx'),
            ('copy', (), ''),
            ('redo', (), 'bcx'),
            ('paste', (), 'bcx'),
            ('switch_document', ('d1',), None),
            ('paste', (), 'bcx'),
            ('select', (7, 9), ''),
            ('create_document', ('d1',), True),
            ('switch_document', ('untitled',), 'bcx'),
            ('move_cursor', (6,), 'bcx'),
            ('copy', (), ''),
            ('redo', (), 'bcx'),
            ('undo', (), 'bcxy'),
            ('move_cursor', (1,), 'bcxy'),
            ('undo', (), 'bcxyz'),
            ('insert', ('xyz',), 'bcxyzxyz'),
            ('move_cursor', (4,), 'bcxyzxyz'),
            ('undo', (), 'bcxyz'),
            ('undo', (), 'bc'),
            ('paste', (), 'bc'),
            ('insert', ('xyz',), 'bcxyz'),
        ])

    def test_level_4_case_08_randomized_sequence_66(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('insert', ('',), ''),
            ('create_document', ('d1',), True),
            ('delete_forward', (), ''),
            ('switch_document', ('d2',), None),
            ('insert', ('',), ''),
            ('move_cursor', (6,), ''),
            ('insert', ('a',), 'a'),
            ('undo', (), ''),
            ('undo', (), ''),
            ('backspace', (), ''),
            ('paste', (), ''),
            ('copy', (), ''),
            ('insert', ('a',), 'a'),
            ('redo', (), 'a'),
            ('switch_document', ('d1',), ''),
            ('insert', ('a',), 'a'),
            ('paste', (), 'a'),
            ('paste', (), 'a'),
            ('switch_document', ('untitled',), 'a'),
            ('paste', (), 'a'),
            ('copy', (), ''),
            ('switch_document', ('untitled',), 'a'),
            ('delete_forward', (), 'a'),
            ('move_cursor', (12,), 'a'),
            ('delete_forward', (), 'a'),
            ('paste', (), 'a'),
            ('delete_forward', (), 'a'),
            ('switch_document', ('untitled',), 'a'),
            ('delete_forward', (), 'a'),
            ('backspace', (), ''),
            ('insert', ('a',), 'a'),
            ('delete_forward', (), 'a'),
            ('copy', (), ''),
            ('insert', ('',), 'a'),
            ('select', (-1, 9), 'a'),
            ('redo', (), 'a'),
            ('backspace', (), ''),
            ('select', (3, 10), ''),
            ('backspace', (), ''),
            ('create_document', ('untitled',), False),
            ('move_cursor', (12,), ''),
            ('delete_forward', (), ''),
            ('delete_forward', (), ''),
            ('insert', ('',), ''),
            ('create_document', ('d2',), True),
            ('undo', (), 'a'),
            ('delete_forward', (), 'a'),
            ('copy', (), ''),
            ('copy', (), ''),
            ('undo', (), ''),
            ('delete_forward', (), ''),
            ('insert', ('a',), 'a'),
            ('undo', (), ''),
            ('backspace', (), ''),
            ('insert', ('',), ''),
            ('insert', ('bc',), 'bc'),
            ('select', (8, 9), ''),
            ('switch_document', ('d2',), ''),
            ('insert', ('',), ''),
            ('insert', ('a',), 'a'),
            ('delete_forward', (), 'a'),
            ('backspace', (), ''),
            ('select', (12, 7), ''),
            ('move_cursor', (9,), ''),
            ('undo', (), 'a'),
            ('select', (8, -1), 'a'),
            ('insert', ('Q',), 'Q'),
            ('select', (1, 7), ''),
            ('insert', ('xyz',), 'Qxyz'),
            ('get_cursor', (), 4),
            ('move_cursor', (4,), 'Qxyz'),
            ('insert', ('bc',), 'Qxyzbc'),
            ('backspace', (), 'Qxyzb'),
            ('paste', (), 'Qxyzb'),
            ('undo', (), 'Qxyzbc'),
            ('select', (-1, 10), 'Qxyzbc'),
            ('insert', ('a',), 'a'),
            ('copy', (), ''),
            ('undo', (), 'Qxyzbc'),
            ('redo', (), 'a'),
            ('insert', ('Q',), 'aQ'),
            ('insert', ('xyz',), 'aQxyz'),
            ('undo', (), 'aQ'),
            ('undo', (), 'a'),
            ('backspace', (), ''),
            ('undo', (), 'a'),
            ('paste', (), 'a'),
            ('undo', (), 'Qxyzbc'),
            ('delete_forward', (), 'Qxyzbc'),
            ('delete_forward', (), 'Qxyzbc'),
        ])

    def test_level_4_case_09_randomized_sequence_67(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('insert', ('',), ''),
            ('switch_document', ('d1',), None),
            ('move_cursor', (7,), ''),
            ('get_cursor', (), 0),
            ('copy', (), ''),
            ('create_document', ('untitled',), False),
            ('paste', (), ''),
            ('paste', (), ''),
            ('delete_forward', (), ''),
            ('insert', ('bc',), 'bc'),
            ('insert', ('a',), 'bca'),
            ('select', (1, 4), 'ca'),
            ('undo', (), 'bc'),
            ('copy', (), ''),
            ('backspace', (), 'b'),
            ('select', (12, 9), ''),
            ('paste', (), 'b'),
            ('switch_document', ('d1',), None),
            ('select', (9, 5), ''),
            ('undo', (), 'bc'),
            ('undo', (), ''),
            ('paste', (), ''),
            ('switch_document', ('d1',), None),
            ('undo', (), ''),
            ('redo', (), 'bc'),
            ('insert', ('Q',), 'bcQ'),
            ('undo', (), 'bc'),
            ('insert', ('',), 'bc'),
            ('delete_forward', (), 'bc'),
            ('insert', ('Q',), 'bcQ'),
            ('insert', ('bc',), 'bcQbc'),
            ('copy', (), ''),
            ('undo', (), 'bcQ'),
            ('get_cursor', (), 3),
            ('backspace', (), 'bc'),
            ('insert', ('Q',), 'bcQ'),
            ('select', (9, 1), 'cQ'),
            ('select', (-2, 9), 'bcQ'),
            ('copy', (), 'bcQ'),
            ('paste', (), 'bcQ'),
            ('delete_forward', (), 'bcQ'),
            ('insert', ('',), 'bcQ'),
            ('insert', ('',), 'bcQ'),
            ('backspace', (), 'bc'),
            ('switch_document', ('untitled',), 'bc'),
            ('redo', (), 'bc'),
            ('insert', ('',), 'bc'),
            ('redo', (), 'bc'),
            ('move_cursor', (-1,), 'bc'),
            ('select', (2, 2), ''),
            ('copy', (), 'bcQ'),
            ('undo', (), 'bcQ'),
            ('paste', (), 'bcQbcQ'),
            ('undo', (), 'bcQ'),
            ('undo', (), 'bc'),
            ('backspace', (), 'b'),
            ('paste', (), 'bbcQ'),
            ('undo', (), 'b'),
            ('insert', ('bc',), 'bbc'),
            ('get_cursor', (), 3),
            ('insert', ('xyz',), 'bbcxyz'),
            ('redo', (), 'bbcxyz'),
            ('move_cursor', (1,), 'bbcxyz'),
            ('select', (12, 5), 'z'),
            ('copy', (), 'z'),
            ('insert', ('xyz',), 'bbcxyxyz'),
            ('select', (10, 12), ''),
            ('copy', (), 'z'),
            ('undo', (), 'bbcxyz'),
            ('insert', ('bc',), 'bbcxyzbc'),
            ('insert', ('',), 'bbcxyzbc'),
            ('undo', (), 'bbcxyz'),
            ('undo', (), 'bbc'),
            ('switch_document', ('d1',), None),
            ('insert', ('a',), 'bbca'),
            ('paste', (), 'bbcaz'),
            ('paste', (), 'bbcazz'),
            ('redo', (), 'bbcazz'),
            ('redo', (), 'bbcazz'),
            ('insert', ('Q',), 'bbcazzQ'),
            ('backspace', (), 'bbcazz'),
            ('paste', (), 'bbcazzz'),
            ('insert', ('Q',), 'bbcazzzQ'),
            ('switch_document', ('untitled',), 'bbcazzzQ'),
            ('redo', (), 'bbcazzzQ'),
            ('insert', ('',), 'bbcazzzQ'),
            ('insert', ('a',), 'bbcazzzQa'),
            ('switch_document', ('d2',), None),
            ('insert', ('xyz',), 'bbcazzzQaxyz'),
            ('backspace', (), 'bbcazzzQaxy'),
        ])


if __name__ == "__main__":
    unittest.main()
