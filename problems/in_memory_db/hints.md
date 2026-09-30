# Hints: In-Memory Database

## Level 1
- `self.data: dict[str, dict[str, ...]]`. `self.data.setdefault(key, {})[field] = value`.
- When the last field of a record is deleted, delete the record too (it matters for counts later).

## Level 2
- `sorted(fields)` gives lexicographic order (uppercase sorts before lowercase: "B" < "a").
- One private `_scan(key, prefix)`; `scan` is `_scan(key, "")`.
- Unknown record returns `[]`.

## Level 3
- Refactor NOW: store `(value, expires_at)` per field and route every public method through private helpers that take an optional timestamp (`None` = ignore expiry). The Level 1-2 methods then call the same helpers with `None`.
- Alive check: `expires_at is None or timestamp < expires_at` (window `[t, t + ttl)`).
- Note the parameter order: `set_at(key, field, value, timestamp)`, `timestamp` is not first.
- `set_at` on an existing TTL field makes it permanent (the new write replaces the expiry).

## Level 4
- A backup stores REMAINING ttl (`expires_at - backup_ts`), not the absolute expiry. Skip expired fields and empty records, and return the number of records saved.
- Keep backups in a list in time order and use `bisect_right(times, timestamp_to_restore) - 1` to pick the latest one at or before the target.
- Restore rebuilds `self.data` as NEW dicts: `expires_at = restore_timestamp + remaining`. Never hand out references to the stored backup, because later writes would corrupt it.
