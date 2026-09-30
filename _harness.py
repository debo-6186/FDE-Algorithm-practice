"""
Test harness used by practice.py (you never need to run this directly).

It imports your implementation from --impl-dir, runs the given level test
files one test at a time (with a per-test time limit, like CodeSignal),
and writes a JSON summary that practice.py prints.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import signal
import sys
import time
import traceback
import unittest
from pathlib import Path

PER_TEST_SECONDS = 6  # CodeSignal kills slow tests too; keep solutions reasonable


class _TestTimeout(Exception):
    pass


def _alarm_handler(signum, frame):  # pragma: no cover - only on timeout
    raise _TestTimeout(f"test exceeded {PER_TEST_SECONDS}s time limit (infinite loop?)")


def _iter_tests(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from _iter_tests(item)
        else:
            yield item


def _short_error(err_text: str, test_file: str) -> str:
    """Keep the useful part of a traceback.

    * Assertion failures: just the message ("step 3: add(5) returned 0, expected 1").
    * Exceptions: the deepest frame in YOUR code (or the test file) + the exception line.
    """
    lines = err_text.rstrip().splitlines()
    if not lines:
        return ""
    # final exception text = everything after the last code line of the last frame
    last_frame = max((i for i, l in enumerate(lines) if l.startswith("  File ")), default=-1)
    exc_start = last_frame + 2 if last_frame >= 0 else 0
    while exc_start < len(lines) and lines[exc_start].startswith("    "):
        exc_start += 1  # skip code / caret lines
    exc_lines = lines[exc_start:] or lines[-1:]
    if exc_lines[0].startswith("AssertionError"):
        return "\n".join(exc_lines).replace("AssertionError: ", "", 1)
    frames = []
    for i, l in enumerate(lines):
        if l.startswith("  File "):
            code = lines[i + 1].strip() if i + 1 < len(lines) and lines[i + 1].startswith("    ") else ""
            frames.append((l.strip(), code))
    tests_dir = str(Path(test_file).resolve().parent)
    user = [f for f in frames if "unittest" not in f[0] and "_harness.py" not in f[0] and tests_dir not in f[0]]
    chosen = user[-1] if user else (frames[-1] if frames else None)
    out = []
    if chosen:
        out.append(chosen[0])
        if chosen[1]:
            out.append("    " + chosen[1])
    return "\n".join(out + exc_lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--impl-dir", required=True)
    parser.add_argument("--json-out", required=True)
    parser.add_argument("tests", nargs="+")
    args = parser.parse_args()

    impl_dir = str(Path(args.impl_dir).resolve())
    sys.path.insert(0, impl_dir)

    use_alarm = hasattr(signal, "SIGALRM")
    if use_alarm:
        signal.signal(signal.SIGALRM, _alarm_handler)

    results = []
    for test_path in args.tests:
        m = re.search(r"test_level_(\d+)\.py$", test_path)
        level = int(m.group(1)) if m else 0
        mod_name = f"_ica_test_level_{level}"
        try:
            spec = importlib.util.spec_from_file_location(mod_name, test_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[mod_name] = module
            spec.loader.exec_module(module)
        except Exception:  # import error in user code or syntax error
            results.append({
                "level": level,
                "name": f"(could not import tests for level {level})",
                "passed": False,
                "seconds": 0.0,
                "error": _short_error(traceback.format_exc(), test_path),
            })
            continue

        suite = unittest.defaultTestLoader.loadTestsFromModule(module)
        tests = sorted(_iter_tests(suite), key=lambda t: t.id())
        for test in tests:
            result = unittest.TestResult()
            start = time.perf_counter()
            if use_alarm:
                signal.alarm(PER_TEST_SECONDS)
            try:
                test.run(result)
            except _TestTimeout as exc:  # raised outside the test body (rare)
                result.errors.append((test, f"_TestTimeout: {exc}"))
            finally:
                if use_alarm:
                    signal.alarm(0)
            elapsed = time.perf_counter() - start
            problems = result.failures + result.errors
            error = _short_error(problems[0][1], test_path) if problems else ""
            results.append({
                "level": level,
                "name": test.id().split(".")[-1],
                "passed": result.wasSuccessful() and not problems,
                "seconds": round(elapsed, 4),
                "error": error,
            })

    with open(args.json_out, "w", encoding="utf-8") as fh:
        json.dump(results, fh)
    return 0


if __name__ == "__main__":
    sys.exit(main())
