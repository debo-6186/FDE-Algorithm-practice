# Hints: Worker Hours & Payroll

## Level 1
- `Worker` class with `entered_at: int | None`. `None` means outside. `register` toggles it.
- Store finished sessions as a list of `(start, end)` (you'll want this later), not just a running total.
- Unknown worker returns the exact string `"invalid_request"`.

## Level 2
- Filter by position, sort by `(-time, worker_id)`, slice `[:n]`, format `f"{id}({time})"`.
- Workers with no finished sessions still appear with `(0)`.

## Level 3
- Promotion is PENDING until the first ENTRY at or after `start_timestamp`, so apply it inside `register` when the worker enters.
- Store position and compensation on each finished session so salary can use the right rate.
- Remember when the current position became active (`position_since`). `top_n_workers` sums only sessions that started at or after it.
- Salary per session = `overlap(session, window) * compensation`, where `overlap = max(0, min(e1, e2) - max(s1, s2))`.
- A second `promote` while one is pending returns `"invalid_request"`. After it becomes active, a new promote is allowed.

## Level 4
- Keep the raw list of double-paid periods and merge them (sort + sweep) when you calculate, so overlaps don't double-count.
- Pay = `rate * (clipped_length + overlap_with_double_periods)`: normal pay for every unit, plus one extra unit of pay for each double-paid unit.
- Double periods apply retroactively, since salary is computed on demand from stored sessions.
