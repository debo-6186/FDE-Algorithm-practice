# Hints: Cloud Storage v2

## Level 1
- `copy_file` fails if the source is missing OR the destination exists. Check both before changing anything.

## Level 2
- `name.startswith(prefix) and name.endswith(suffix)`, then sort with `key=(-size, name)`.
- Don't try `name[len(prefix):]` tricks: prefix and suffix may overlap.

## Level 3
- Give every file an `owner`; make admin a user with unlimited capacity (`None`) so `add_file` and `add_file_by` share one code path.
- Keep `used` per user, updated by one `_put` / `_remove` pair. Every size change goes through them.
- `update_capacity`: sort the user's files by `(-size, name)`, delete from the front while `used > capacity`. Return the COUNT of deleted files, not the remaining capacity.
- `copy_file` now has to charge the source owner's capacity.

## Level 4
- Store the original size on the compressed file so decompress can restore it exactly (odd sizes!).
- Compress: check ownership, check the name doesn't already end with `.COMPRESSED`, check the target name is free.
- Decompress: capacity check uses the DIFFERENCE (`original - compressed`), because the compressed file is removed first.
- Return `capacity - used` after the change.
