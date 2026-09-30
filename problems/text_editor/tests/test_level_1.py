"""
Level 1 tests for Text Editor.

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


class TestLevel1(unittest.TestCase):
    def setUp(self):
        self.impl = TextEditorImpl()

    def test_level_1_case_01_example_from_spec(self):
        """The Level 1 example table."""
        run_steps(self, self.impl, [
            ('insert', ('Hello',), 'Hello'),
            ('insert', (' world',), 'Hello world'),
            ('move_cursor', (5,), 'Hello world'),
            ('insert', (',',), 'Hello, world'),
            ('get_cursor', (), 6),
            ('delete_forward', (), 'Hello,world'),
            ('backspace', (), 'Helloworld'),
            ('move_cursor', (100,), 'Helloworld'),
            ('delete_forward', (), 'Helloworld'),
            ('move_cursor', (-3,), 'Helloworld'),
            ('backspace', (), 'Helloworld'),
            ('get_cursor', (), 0),
        ])

    def test_level_1_case_02_empty_document(self):
        run_steps(self, self.impl, [
            ('get_cursor', (), 0),
            ('backspace', (), ''),
            ('delete_forward', (), ''),
            ('move_cursor', (3,), ''),
            ('get_cursor', (), 0),
            ('insert', ('',), ''),
            ('get_cursor', (), 0),
        ])

    def test_level_1_case_03_insert_in_the_middle(self):
        run_steps(self, self.impl, [
            ('insert', ('ace',), 'ace'),
            ('move_cursor', (1,), 'ace'),
            ('insert', ('b',), 'abce'),
            ('move_cursor', (3,), 'abce'),
            ('insert', ('d',), 'abcde'),
            ('get_cursor', (), 4),
        ])

    def test_level_1_case_04_delete_forward_keeps_cursor(self):
        run_steps(self, self.impl, [
            ('insert', ('12345',), '12345'),
            ('move_cursor', (1,), '12345'),
            ('delete_forward', (), '1345'),
            ('delete_forward', (), '145'),
            ('get_cursor', (), 1),
            ('backspace', (), '45'),
            ('get_cursor', (), 0),
        ])

    def test_level_1_case_05_backspace_everything(self):
        run_steps(self, self.impl, [
            ('insert', ('abc',), 'abc'),
            ('backspace', (), 'ab'),
            ('backspace', (), 'a'),
            ('backspace', (), ''),
            ('backspace', (), ''),
            ('insert', ('z',), 'z'),
        ])

    def test_level_1_case_06_randomized_sequence_19(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('delete_forward', (), ''),
            ('backspace', (), ''),
            ('move_cursor', (6,), ''),
            ('insert', ('xyz',), 'xyz'),
            ('get_cursor', (), 3),
            ('insert', ('bc',), 'xyzbc'),
            ('move_cursor', (-1,), 'xyzbc'),
            ('insert', ('xyz',), 'xyzxyzbc'),
            ('get_cursor', (), 3),
            ('backspace', (), 'xyxyzbc'),
            ('backspace', (), 'xxyzbc'),
            ('backspace', (), 'xyzbc'),
            ('insert', ('Q',), 'Qxyzbc'),
            ('insert', ('a',), 'Qaxyzbc'),
            ('backspace', (), 'Qxyzbc'),
            ('insert', ('',), 'Qxyzbc'),
            ('move_cursor', (9,), 'Qxyzbc'),
            ('insert', ('a',), 'Qxyzbca'),
            ('move_cursor', (-1,), 'Qxyzbca'),
            ('move_cursor', (4,), 'Qxyzbca'),
            ('delete_forward', (), 'Qxyzca'),
            ('move_cursor', (8,), 'Qxyzca'),
            ('get_cursor', (), 6),
            ('move_cursor', (6,), 'Qxyzca'),
            ('backspace', (), 'Qxyzc'),
            ('backspace', (), 'Qxyz'),
            ('get_cursor', (), 4),
            ('insert', ('Q',), 'QxyzQ'),
            ('move_cursor', (-1,), 'QxyzQ'),
            ('backspace', (), 'QxyzQ'),
            ('move_cursor', (0,), 'QxyzQ'),
            ('insert', ('',), 'QxyzQ'),
            ('insert', ('',), 'QxyzQ'),
            ('insert', ('',), 'QxyzQ'),
            ('backspace', (), 'QxyzQ'),
            ('move_cursor', (6,), 'QxyzQ'),
            ('move_cursor', (6,), 'QxyzQ'),
            ('move_cursor', (4,), 'QxyzQ'),
            ('backspace', (), 'QxyQ'),
            ('backspace', (), 'QxQ'),
        ])


if __name__ == "__main__":
    unittest.main()
