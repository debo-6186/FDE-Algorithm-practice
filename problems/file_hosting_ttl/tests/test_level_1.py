"""
Level 1 tests for File Hosting (TTL + rollback).

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


class TestLevel1(unittest.TestCase):
    def setUp(self):
        self.impl = FileHostingImpl()

    def test_level_1_case_01_example_from_spec(self):
        """The Level 1 example table."""
        run_steps(self, self.impl, [
            ('file_upload', ('/docs/cv.pdf', 300), ANY),
            ('file_upload', ('/docs/cv.pdf', 100), Raises(RuntimeError)),
            ('file_get', ('/docs/cv.pdf',), 300),
            ('file_get', ('/nope',), None),
            ('file_copy', ('/docs/cv.pdf', '/backup/cv.pdf'), ANY),
            ('file_get', ('/backup/cv.pdf',), 300),
            ('file_upload', ('/tmp.txt', 5), ANY),
            ('file_copy', ('/tmp.txt', '/backup/cv.pdf'), ANY),
            ('file_get', ('/backup/cv.pdf',), 5),
            ('file_copy', ('/nope', '/x'), Raises(RuntimeError)),
        ])

    def test_level_1_case_02_failed_upload_keeps_original(self):
        run_steps(self, self.impl, [
            ('file_upload', ('/f', 1), ANY),
            ('file_upload', ('/f', 2), Raises(RuntimeError)),
            ('file_get', ('/f',), 1),
        ])

    def test_level_1_case_03_copy_to_new_name_then_reupload_fails(self):
        run_steps(self, self.impl, [
            ('file_upload', ('/a', 7), ANY),
            ('file_copy', ('/a', '/b'), ANY),
            ('file_upload', ('/b', 1), Raises(RuntimeError)),
            ('file_get', ('/b',), 7),
            ('file_get', ('/a',), 7),
        ])

    def test_level_1_case_04_copy_onto_itself_is_allowed(self):
        run_steps(self, self.impl, [
            ('file_upload', ('/a', 7), ANY),
            ('file_copy', ('/a', '/a'), ANY),
            ('file_get', ('/a',), 7),
        ])

    def test_level_1_case_05_failed_copy_creates_nothing(self):
        run_steps(self, self.impl, [
            ('file_copy', ('/missing', '/dest'), Raises(RuntimeError)),
            ('file_get', ('/dest',), None),
            ('file_upload', ('/dest', 3), ANY),
        ])

    def test_level_1_case_06_randomized_sequence_15(self):
        """Longer mixed sequence (like CodeSignal's hidden stress tests)."""
        run_steps(self, self.impl, [
            ('file_copy', ('/n0', '/b'), Raises(RuntimeError)),
            ('file_copy', ('/n5', '/n7'), Raises(RuntimeError)),
            ('file_upload', ('/n4', 3), ANY),
            ('file_upload', ('/n10', 5), ANY),
            ('file_copy', ('/n8', '/n12'), Raises(RuntimeError)),
            ('file_upload', ('/n7', 2), ANY),
            ('file_copy', ('/n10', '/n7'), ANY),
            ('file_upload', ('/b', 5), ANY),
            ('file_upload', ('/a', 5), ANY),
            ('file_upload', ('/a', 8), Raises(RuntimeError)),
            ('file_copy', ('/a', '/c'), ANY),
            ('file_upload', ('/e', 5), ANY),
            ('file_upload', ('/n2', 5), ANY),
            ('file_copy', ('/n0', '/n6'), Raises(RuntimeError)),
            ('file_upload', ('/n5', 8), ANY),
            ('file_copy', ('/n0', '/n9'), Raises(RuntimeError)),
            ('file_get', ('/n4',), 3),
            ('file_copy', ('/n3', '/n3'), Raises(RuntimeError)),
            ('file_upload', ('/n2', 5), Raises(RuntimeError)),
            ('file_copy', ('/b/c', '/n9'), Raises(RuntimeError)),
            ('file_upload', ('/b', 2), Raises(RuntimeError)),
            ('file_upload', ('/b', 3), Raises(RuntimeError)),
            ('file_upload', ('/n9', 3), ANY),
            ('file_upload', ('/e', 3), Raises(RuntimeError)),
            ('file_upload', ('/ab', 3), ANY),
            ('file_copy', ('/n2', '/n8'), ANY),
            ('file_upload', ('/n3', 5), ANY),
            ('file_upload', ('/n0', 3), ANY),
            ('file_copy', ('/n2', '/n9'), ANY),
            ('file_upload', ('/a', 1), Raises(RuntimeError)),
            ('file_copy', ('/n5', '/ab'), ANY),
            ('file_get', ('/ab',), 8),
            ('file_upload', ('/n1', 5), ANY),
            ('file_copy', ('/c', '/a'), ANY),
            ('file_upload', ('/c', 5), Raises(RuntimeError)),
            ('file_get', ('/n8',), 5),
            ('file_get', ('/d.txt',), None),
            ('file_upload', ('/n10', 5), Raises(RuntimeError)),
            ('file_upload', ('/n1', 8), Raises(RuntimeError)),
            ('file_copy', ('/n9', '/d.txt'), ANY),
        ])


if __name__ == "__main__":
    unittest.main()
