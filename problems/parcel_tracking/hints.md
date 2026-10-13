# Hints: Parcel Tracking System

## Level 1
- `self.parcels: dict[str, dict[str, str]]`; `self.parcels.setdefault(parcel_id, {})[tag] = value`.
- When the last tag of a parcel is removed, delete the parcel too (it matters for the Level 4 count).

## Level 2
- `sorted(tags)` sorts by tag name (uppercase before lowercase). Sort the NAMES, then format `f"{tag}({value})"`.
- `list_tags` is `list_tags_by_prefix` with `""`. A missing parcel returns `[]`.

## Level 3
- Refactor NOW: store `(value, expires_at)` per tag and route every public method through private helpers that take an optional timestamp (`None` = ignore expiry). The Level 1-2 methods call the same helpers with `None`.
- Valid at `t` means `expires_at is None or t < expires_at` (a tag expiring AT `t` is already gone).
- `ttl == 0` means "never expires", not "expires immediately". `set_tag_at` makes the tag permanent again if it overwrites a hold.
- `remove_tag_at` on an expired tag returns `False`.
- Timestamps never decrease, so you only ever need the current state, not a history of values.

## Level 4
- A checkpoint saves ONLY the valid tags and ONLY the parcels that still have one; `checkpoint` returns that count.
- Store absolute expirations in the snapshot. On restore: `new_expiration = old_expiration + (timestamp - checkpoint_timestamp)`. Use the checkpoint's own timestamp, not `timestamp_to_restore`. Tags with no TTL stay `None`.
- Pick the checkpoint with `bisect_right(times, timestamp_to_restore) - 1`; a negative index means no checkpoint, so do nothing. If two checkpoints share a timestamp, the later one wins (that is what `bisect_right` gives you).
- Rebuild `self.parcels` as NEW dicts on restore. Checkpoints stay available after a restore, so restoring the same one twice must work.
