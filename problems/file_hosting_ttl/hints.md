# Hints: File Hosting (TTL + rollback)

## Level 1
- Raise with `raise RuntimeError("...")`. The tests check the exception type, not the message.
- Copy overwrites the destination. Only a missing source raises.

## Level 2
- Sort by `(-size, name)` and slice `[:10]`. Return names only.

## Level 3
- Store `name -> (size, expires_at)` with `expires_at = None` for no TTL. One helper, `_alive(name, t)`, answers "does it exist at t?" and every `_at` method uses it.
- Alive means `expires_at is None or t < expires_at` (the window is half-open: `[t0, t0 + ttl)`).
- Upload fails only if a LIVE file has the name, so expired names can be reused.
- A copy keeps the source's absolute `expires_at`, not a fresh TTL.
- Keep the Level 1-2 methods working: they can use the same dict and treat everything as alive.

## Level 4
- To go back to any past time you need history. Simplest: after every change, append `(timestamp, dict(self.files))` to a list. Then `bisect_right(times, time_to) - 1` finds the snapshot.
- When restoring, drop files already expired at `time_to` and shift the others: `new_expiry = timestamp + (old_expiry - time_to)`.
- Record a snapshot for the rollback too, so later rollbacks can target times after it.
- Snapshots must be copies. `dict(self.files)` is enough only because the values are immutable tuples.
