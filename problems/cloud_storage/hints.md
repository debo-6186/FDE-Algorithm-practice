# Hints: Cloud Storage

## Level 1
- `self.files: dict[str, File]` with a small `File` class (name, size, and later owner).
- `delete_file` returns the size of what it deleted, so pop first and then read the size.

## Level 2
- Filter with `name.startswith(prefix)`, then sort with `key=lambda f: (-f.size, f.name)`, then slice `[:n]`.
- Output strings have no spaces: `f"{name}({size})"`. No matches returns `[]`.

## Level 3
- Refactor so every add goes through one `_add(owner, name, size)` helper. `add_file` becomes `_add("admin", ...)`.
- Model admin as a real user with `capacity=None` (unlimited). Then ownership code has no special cases.
- Track `used` per user and update it on add and delete. Deleting a user's file must free their capacity.
- The file namespace is global: a name owned by any user or admin blocks `add_file_by`.
- Merge: move file ownership, add used and capacity, delete user 2. The answer is `capacity - used`.

## Level 4
- Backup = snapshot dict `{name: size}` of the user's files. Build a NEW dict; don't keep a reference to live objects.
- Restore: delete every file the user owns now, then re-add backup files whose names are free. No backup restores 0 files.
- Iterate over a copy (`list(user.files)`) when deleting inside a loop.
- The backup lives on the user object, so deleting user 2 in a merge drops its backup automatically.
