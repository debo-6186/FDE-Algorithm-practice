# Hints: Job Scheduler

## Level 1
- A `Job` class (id, priority, insertion number, state). With small inputs, picking the next job by sorting on `(-priority, seq)` is fast enough; a heap is optional.
- Only RUNNING jobs can be completed.

## Level 2
- Reuse the same ordering function for `next_job` and `peek_jobs` so they can never disagree.
- `jobs_with_status` sorts ids alphabetically; that is a different order from the queue order.

## Level 3
- Store both directions: `prereqs` (what I wait for) and `dependents` (who waits for me). Level 4 needs the second.
- Derive "queued" vs "blocked" when asked (not started AND all prereqs done means queued), rather than storing it. Then completing a prerequisite unblocks dependents automatically.
- Cycle check: adding "A waits for B" creates a cycle iff B already (transitively) waits for A. Run a DFS from B over prereqs.

## Level 4
- BFS or DFS over `dependents`, canceling every not-started job you reach. Use a visited check (state != PENDING) so shared descendants are handled once.
- Return the canceled ids sorted alphabetically.
