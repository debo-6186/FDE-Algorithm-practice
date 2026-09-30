#!/usr/bin/env python3
"""
Progressive coding assessment simulator (CodeSignal ICA / "Progressive Filesystem" format).

Each problem has 4 levels. You see one level at a time. A level's tests must ALL
pass before the next level unlocks, and earlier levels' tests keep running (the
real test re-checks them too). A 90-minute clock starts when you start a problem.

Usage:
  python3 practice.py list                  show problems and your progress
  python3 practice.py start <problem>       start (or resume) a timed attempt
  python3 practice.py test <problem>        run the tests; unlocks the next level when the current one passes
  python3 practice.py spec <problem>        re-print the requirements for the levels you have unlocked
  python3 practice.py hint <problem>        hints for your current level (only if you are stuck)
  python3 practice.py status [<problem>]    elapsed time and level splits
  python3 practice.py solution <problem>    print the reference solution (spoiler)
  python3 practice.py reset <problem>       delete your workspace for a problem and start over
  python3 practice.py verify [<problem>]    self-check: reference solutions must pass every level

<problem> can be the problem id, a unique prefix of it, or its number from `list`.
Your code lives in workspace/<problem>/ . Edit the *_impl.py file there.
"""
from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROBLEMS = ROOT / "problems"
WORKSPACE = ROOT / "workspace"
HARNESS = ROOT / "_harness.py"
TIME_LIMIT_SECONDS = 90 * 60
MARKER = "# @@LEVEL "


# --------------------------------------------------------------------------- helpers

def fmt_clock(seconds: float) -> str:
    seconds = int(max(0, seconds))
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


def all_problem_ids() -> list[str]:
    ids = [p.name for p in PROBLEMS.iterdir() if (p / "meta.json").exists()]
    return sorted(ids, key=lambda pid: (load_meta(pid).get("order", 99), pid))


def load_meta(pid: str) -> dict:
    with open(PROBLEMS / pid / "meta.json", encoding="utf-8") as fh:
        return json.load(fh)


def resolve(name: str) -> str:
    ids = all_problem_ids()
    if name.isdigit():
        n = int(name)
        for pid in ids:
            if load_meta(pid).get("order") == n:
                return pid
    if name in ids:
        return name
    matches = [pid for pid in ids if pid.startswith(name)]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        sys.exit(f"Unknown problem '{name}'. Run: python3 practice.py list")
    sys.exit(f"'{name}' is ambiguous: {', '.join(matches)}")


def ws_dir(pid: str) -> Path:
    return WORKSPACE / pid


def state_file(pid: str) -> Path:
    return ws_dir(pid) / ".state.json"


def load_state(pid: str) -> dict | None:
    path = state_file(pid)
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def save_state(pid: str, state: dict) -> None:
    with open(state_file(pid), "w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=2)


def read(path: Path) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def write(path: Path, text: str, readonly: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        os.chmod(path, stat.S_IWRITE | stat.S_IREAD)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    if readonly:
        os.chmod(path, stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)


def interface_for_level(pid: str, level: int) -> str:
    """Interface file containing only the methods of levels <= level."""
    out, current = [], 0
    for line in read(PROBLEMS / pid / "interface.py").splitlines(keepends=True):
        stripped = line.strip()
        if stripped.startswith(MARKER):
            current = int(stripped[len(MARKER):].strip("@ \n"))
            continue
        if current <= level:
            out.append(line)
    return "".join(out).rstrip() + "\n"


def spec_text(pid: str, upto: int) -> str:
    parts = [read(PROBLEMS / pid / "spec" / "intro.md").rstrip()]
    for lvl in range(1, upto + 1):
        parts.append(read(PROBLEMS / pid / "spec" / f"level{lvl}.md").rstrip())
    return "\n\n".join(parts) + "\n"


def hint_text(pid: str, level: int) -> str:
    text = read(PROBLEMS / pid / "hints.md")
    sections, key = {}, None
    for line in text.splitlines():
        if line.startswith("## Level "):
            key = int(line.split()[2])
            sections[key] = []
        elif key is not None:
            sections[key].append(line)
    return "\n".join(sections.get(level, ["(no hints for this level)"])).strip()


def sync_visible_files(pid: str, unlocked: int) -> None:
    """(Re)write the read-only files the candidate is allowed to see."""
    meta = load_meta(pid)
    ws = ws_dir(pid)
    write(ws / f"{meta['interface_module']}.py", interface_for_level(pid, unlocked), readonly=True)
    for lvl in range(1, unlocked + 1):
        write(ws / f"LEVEL_{lvl}.md", read(PROBLEMS / pid / "spec" / f"level{lvl}.md"), readonly=True)
        src = PROBLEMS / pid / "tests" / f"test_level_{lvl}.py"
        write(ws / "tests" / f"test_level_{lvl}.py", read(src), readonly=True)
    write(ws / "README.md", read(PROBLEMS / pid / "spec" / "intro.md"), readonly=True)


def run_tests(impl_dir: Path, test_files: list[Path]) -> list[dict]:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "results.json"
        cmd = [sys.executable, str(HARNESS), "--impl-dir", str(impl_dir), "--json-out", str(out)]
        cmd += [str(p) for p in test_files]
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300, env=env, cwd=str(impl_dir))
        except subprocess.TimeoutExpired:
            return [{"level": 0, "name": "(test run timed out after 300s)", "passed": False, "seconds": 300, "error": ""}]
        if not out.exists():
            return [{"level": 0, "name": "(test harness crashed)", "passed": False, "seconds": 0,
                     "error": (proc.stdout + proc.stderr)[-3000:]}]
        with open(out, encoding="utf-8") as fh:
            results = json.load(fh)
        if proc.stdout.strip():
            print("---- your print() output ----")
            print(proc.stdout.rstrip()[-4000:])
            print("-----------------------------")
        return results


def summarize(results: list[dict], levels: list[int], verbose: bool = True) -> dict[int, tuple[int, int]]:
    per_level: dict[int, tuple[int, int]] = {}
    for lvl in levels:
        rows = [r for r in results if r["level"] == lvl]
        passed = sum(r["passed"] for r in rows)
        per_level[lvl] = (passed, len(rows))
        if not verbose:
            continue
        mark = "PASS" if rows and passed == len(rows) else "FAIL"
        print(f"\nLevel {lvl}: {passed}/{len(rows)} tests passed [{mark}]")
        for r in rows:
            tag = "  ok  " if r["passed"] else "  FAIL"
            print(f"{tag} {r['name']}  ({r['seconds']:.3f}s)")
            if not r["passed"] and r["error"]:
                for line in r["error"].splitlines():
                    print(f"         {line}")
    stray = [r for r in results if r["level"] not in levels]
    for r in stray:
        print(f"  FAIL {r['name']}\n{r['error']}")
    return per_level


# --------------------------------------------------------------------------- commands

def cmd_list() -> None:
    print(f"{'#':>2}  {'problem':<22} {'seen in real tests':<20} progress")
    print("-" * 78)
    for pid in all_problem_ids():
        meta = load_meta(pid)
        st = load_state(pid)
        if st is None:
            progress = "not started"
        elif st.get("completed_at"):
            progress = f"all 4 levels done in {fmt_clock(st['completed_at'] - st['started_at'])}"
        else:
            progress = f"on level {st['unlocked']}, {fmt_clock(time.time() - st['started_at'])} elapsed"
        print(f"{meta.get('order', ''):>2}  {pid:<22} {meta.get('frequency', ''):<20} {progress}")
        print(f"    {meta['title']}: {meta.get('summary', '')}")
    print("\nStart one with: python3 practice.py start <problem>")


def cmd_start(pid: str) -> None:
    meta = load_meta(pid)
    ws = ws_dir(pid)
    st = load_state(pid)
    if st is not None:
        print(f"Resuming '{pid}' (level {st['unlocked']} unlocked, {fmt_clock(time.time() - st['started_at'])} elapsed).")
        print(f"Your code: {ws / (meta['impl_module'] + '.py')}")
        sync_visible_files(pid, st["unlocked"])
        return
    ws.mkdir(parents=True, exist_ok=True)
    impl = ws / f"{meta['impl_module']}.py"
    if not impl.exists():
        write(impl, read(PROBLEMS / pid / "starter.py"))
    now = time.time()
    st = {"started_at": now, "unlocked": 1, "unlocked_at": {"1": now}, "completed_at": None, "runs": 0}
    save_state(pid, st)
    sync_visible_files(pid, 1)
    print(spec_text(pid, 1))
    print("=" * 78)
    print(f"Clock started: you have {TIME_LIMIT_SECONDS // 60} minutes.")
    print(f"Edit:      {impl}")
    print(f"Interface: {ws / (meta['interface_module'] + '.py')}  (read-only, like the real test)")
    print(f"Tests:     {ws / 'tests'}  (read them! they are the real spec)")
    print(f"Run tests: python3 practice.py test {pid}")


def cmd_test(pid: str) -> None:
    meta = load_meta(pid)
    st = load_state(pid)
    if st is None:
        sys.exit(f"Not started yet. Run: python3 practice.py start {pid}")
    unlocked = st["unlocked"]
    sync_visible_files(pid, unlocked)
    tests = [PROBLEMS / pid / "tests" / f"test_level_{lvl}.py" for lvl in range(1, unlocked + 1)]
    results = run_tests(ws_dir(pid), tests)
    per_level = summarize(results, list(range(1, unlocked + 1)))
    st["runs"] = st.get("runs", 0) + 1
    now = time.time()
    elapsed = now - st["started_at"]

    cur_passed, cur_total = per_level.get(unlocked, (0, 0))
    regressions = [lvl for lvl in range(1, unlocked) if per_level[lvl][0] < per_level[lvl][1]]
    print()
    if regressions:
        print(f"Warning: earlier level(s) {regressions} now fail. The real test re-runs them too; fix before moving on.")
    if cur_total and cur_passed == cur_total and not st.get("completed_at"):
        if unlocked < meta.get("levels", 4):
            nxt = unlocked + 1
            st["unlocked"] = nxt
            st.setdefault("unlocked_at", {})[str(nxt)] = now
            save_state(pid, st)
            sync_visible_files(pid, nxt)
            print("=" * 78)
            print(f"Level {unlocked} complete at {fmt_clock(elapsed)}.  Level {nxt} unlocked:\n")
            print(read(PROBLEMS / pid / "spec" / f"level{nxt}.md"))
            print("=" * 78)
            print(f"New files: LEVEL_{nxt}.md, tests/test_level_{nxt}.py, updated {meta['interface_module']}.py")
        else:
            st["completed_at"] = now
            save_state(pid, st)
            print("=" * 78)
            print(f"All levels passed in {fmt_clock(elapsed)} (limit 90:00). Splits:")
            print_splits(st)
            print("Next: compare with the reference (python3 practice.py solution " + pid + ") and note what slowed you down.")
    else:
        save_state(pid, st)
        print(f"Level {unlocked}: {cur_passed}/{cur_total} passing. Elapsed {fmt_clock(elapsed)} of 90:00.")
    if elapsed > TIME_LIMIT_SECONDS and not st.get("completed_at"):
        print(f"Note: you are {fmt_clock(elapsed - TIME_LIMIT_SECONDS)} past 90:00. The real test would have ended; keep going for practice.")


def print_splits(st: dict) -> None:
    marks = sorted((int(k), v) for k, v in st.get("unlocked_at", {}).items())
    end = st.get("completed_at") or time.time()
    for i, (lvl, t0) in enumerate(marks):
        t1 = marks[i + 1][1] if i + 1 < len(marks) else end
        done = i + 1 < len(marks) or st.get("completed_at")
        label = "done" if done else "in progress"
        print(f"  Level {lvl}: {fmt_clock(t1 - t0)} ({label})")


def cmd_spec(pid: str) -> None:
    st = load_state(pid)
    if st is None:
        sys.exit(f"Not started yet. Run: python3 practice.py start {pid}")
    print(spec_text(pid, st["unlocked"]))


def cmd_hint(pid: str) -> None:
    st = load_state(pid)
    level = st["unlocked"] if st else 1
    print(f"Hints for {pid}, level {level}:\n")
    print(hint_text(pid, level))


def cmd_status(pid: str | None) -> None:
    pids = [pid] if pid else [p for p in all_problem_ids() if load_state(p)]
    if not pids:
        print("No attempts yet.")
    for p in pids:
        st = load_state(p)
        if not st:
            print(f"{p}: not started")
            continue
        end = st.get("completed_at") or time.time()
        print(f"{p}: level {st['unlocked']} unlocked, {fmt_clock(end - st['started_at'])} elapsed, {st.get('runs', 0)} test runs")
        print_splits(st)


def cmd_solution(pid: str, yes: bool) -> None:
    meta = load_meta(pid)
    if not yes:
        ans = input("This prints the full reference solution. Continue? [y/N] ").strip().lower()
        if ans != "y":
            return
    path = PROBLEMS / pid / "solution" / f"{meta['impl_module']}.py"
    print(f"# {path}\n")
    print(read(path))


def cmd_reset(pid: str, yes: bool) -> None:
    if not yes:
        ans = input(f"Delete workspace/{pid} (your code for this problem)? [y/N] ").strip().lower()
        if ans != "y":
            return
    ws = ws_dir(pid)
    if ws.exists():
        for path in ws.rglob("*"):
            try:
                os.chmod(path, stat.S_IWRITE | stat.S_IREAD | stat.S_IEXEC)
            except OSError:
                pass
        shutil.rmtree(ws)
    print(f"Reset {pid}.")


def cmd_verify(pid: str | None) -> int:
    pids = [pid] if pid else all_problem_ids()
    failures = 0
    for p in pids:
        meta = load_meta(p)
        levels = meta.get("levels", 4)
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            write(tmpdir / f"{meta['interface_module']}.py", interface_for_level(p, levels))
            shutil.copy(PROBLEMS / p / "solution" / f"{meta['impl_module']}.py", tmpdir)
            tests = [PROBLEMS / p / "tests" / f"test_level_{lvl}.py" for lvl in range(1, levels + 1)]
            results = run_tests(tmpdir, tests)
        per_level = summarize(results, list(range(1, levels + 1)), verbose=False)
        bad = [r for r in results if not r["passed"]]
        failures += len(bad)
        summary = "  ".join(f"L{l}: {p_}/{t}" for l, (p_, t) in per_level.items())
        print(f"{'OK  ' if not bad else 'FAIL'} {p:<22} {summary}")
        for r in bad:
            print(f"      {r['name']}\n{r['error']}")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[1] in {"-h", "--help", "help"}:
        print(__doc__)
        return 0
    cmd, rest = argv[1], [a for a in argv[2:] if not a.startswith("--")]
    yes = "--yes" in argv or "-y" in argv
    if cmd == "list":
        cmd_list()
    elif cmd == "verify":
        return cmd_verify(resolve(rest[0]) if rest else None)
    elif cmd == "status":
        cmd_status(resolve(rest[0]) if rest else None)
    elif cmd in {"start", "test", "spec", "hint", "solution", "reset"}:
        if not rest:
            sys.exit(f"Usage: python3 practice.py {cmd} <problem>")
        pid = resolve(rest[0])
        if cmd == "start":
            cmd_start(pid)
        elif cmd == "test":
            cmd_test(pid)
        elif cmd == "spec":
            cmd_spec(pid)
        elif cmd == "hint":
            cmd_hint(pid)
        elif cmd == "solution":
            cmd_solution(pid, yes)
        else:
            cmd_reset(pid, yes)
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
