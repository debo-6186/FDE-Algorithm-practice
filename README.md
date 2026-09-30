# Meta FDE coding assessment: practice kit

This kit copies the format of Meta's 90-minute online assessment: CodeSignal's
**Industry Coding Assessment**, which CodeSignal calls the "Progressive Filesystem"
question type. You get one problem with four levels. Each level adds requirements,
and the next level unlocks only when **every** test of the current level passes.

Everything runs locally with plain Python 3.8+. No packages needed.

## Quick start

```bash
cd meta_fde_ica_kit
python3 practice.py list                       # problems + your progress
python3 practice.py start integer_container    # warm-up (same shape as CodeSignal's practice test)
#   edit workspace/integer_container/integer_container_impl.py
python3 practice.py test integer_container     # run the tests; passing unlocks the next level
```

Other commands:

| Command | What it does |
|---|---|
| `python3 practice.py spec <problem>` | re-print the requirements for the levels you've unlocked |
| `python3 practice.py hint <problem>` | hints for your current level (only if you're stuck) |
| `python3 practice.py status` | elapsed time and per-level split times |
| `python3 practice.py solution <problem>` | print the reference solution (after you finish!) |
| `python3 practice.py reset <problem> --yes` | wipe your attempt and start again |
| `python3 practice.py verify` | self-check: the reference solutions pass every test |

`<problem>` can be the id, a unique prefix (`task`, `worker`), or the number from `list`.

## What you'll see in `workspace/<problem>/`

This mirrors the real environment:

- `README.md`: problem intro and the one-line summary of all four levels.
- `LEVEL_1.md` ... : the requirements for each **unlocked** level, written the way CodeSignal
  presents a question: an intro line, the operation list with full signatures, an
  `Examples` table of `Queries | Explanations`, and the execution limits.
- `<name>.py`: the read-only **interface** (method signatures and docstrings). It gains new
  methods when a level unlocks.
- `<name>_impl.py`: **your code**. The class inherits the interface. Methods you haven't
  written yet fall back to the interface's placeholder return values, so tests fail
  instead of crashing.
- `tests/test_level_N.py`: the read-only unit tests. **Read them.** In the real test they
  settle every ambiguity in the text (return types, `None` vs `""`, sort order, format).

Test output tells you exactly which call failed:

```
  FAIL test_level_3_case_02_cashback_rounds_down
         step 6: deposit(86400003, 'a', 1) returned 805, expected 806
```

## The problems

| # | id | Level 1 | Level 2 | Level 3 | Level 4 |
|---|---|---|---|---|---|
| 0 | `integer_container` | add / delete | median | range count, k-th smallest | undo / redo |
| 1 | `banking_cashback` | create / deposit / transfer | top spenders | pay + 2% cashback after 24h, status | merge accounts, balance at a past time |
| 2 | `banking_scheduled` | create / deposit / transfer | top spenders | schedule / cancel delayed payments | merge accounts, balance at a past time |
| 3 | `cloud_storage` | add / get / delete file | n largest by prefix | users + capacity, merge users | backup / restore user |
| 4 | `cloud_storage_v2` | add / copy / get | find by prefix + suffix | users, update capacity with eviction | compress / decompress |
| 5 | `file_hosting_ttl` | upload / get / copy (exceptions) | top-10 search | timestamps + TTL | rollback to a past time |
| 6 | `in_memory_db` | set / get / delete | scan, scan by prefix | TTL versions of everything | backup / restore with TTL recalculation |
| 7 | `worker_hours` | add worker, register in/out, total | top workers by position | promotions, salary for a window | double-paid periods |
| 8 | `task_manager` | tasks with ids, JSON output | search + priority sort | users, quotas, timed assignments | complete + overdue |
| 9 | `text_editor` | cursor insert / delete | select, copy, paste | undo / redo | multiple documents |
| 10 | `job_scheduler` | priority queue of jobs | peek, list by status | dependencies + cycle check | cascading cancel |

Problems 1-8 are the families candidates report for this assessment format
(banking and cloud storage come up the most; `file_hosting_ttl` follows the shape
of a public CodeSignal-style mock). Problems 9-10 are extra practice with different
shapes: string/cursor state and graphs. `GUIDE.html` is the study guide (patterns,
mistakes, time plan) for offline reading.

Each level's tests include the example from the spec, targeted edge cases, and
longer randomized sequences (like CodeSignal's bigger hidden-style tests). Every
expected value was checked against two independent implementations.

## How to practice (so it transfers to the real thing)

1. **Don't open `problems/`.** It holds future levels, tests and solutions. Work only in `workspace/`.
2. **Always run the full 90 minutes with the clock.** Target splits: L1 ≤ 10 min, L2 ≤ 15, L3 ≤ 30, L4 whatever's left.
3. **Write in the same editor habits you'll use on CodeSignal:** no autocomplete-heavy IDE
   magic, and look up Python docs only. (Check the rules on your test's start screen.)
4. After each attempt: `practice.py status` for splits, then `practice.py solution <id>` and
   compare. Write down the one or two things that cost you the most time.
5. Re-do any problem where you went over 90 minutes, from scratch, a day later.

Suggested order: `integer_container` (learn the tool), `banking_cashback`, `cloud_storage`,
`in_memory_db`, `banking_scheduled`, `worker_hours`, `cloud_storage_v2`, `task_manager`,
`file_hosting_ttl`, then `text_editor` and `job_scheduler`.

Before the real test, also take CodeSignal's own practice test from your invitation
email so the real IDE (Run vs Submit, file tree, test panel) feels familiar.
