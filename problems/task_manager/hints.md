# Hints: Task Manager

## Level 1
- Keep a counter and build ids with `f"task_id_{n}"`. Also store `n` itself on the task; you need it for sorting.
- Build the JSON output with `json.dumps({"name": ..., "priority": ...})`. Hand-built f-strings get quotes and spacing wrong.

## Level 2
- Sort key `(-priority, creation_number)`. NEVER sort by the id string: `"task_id_10" < "task_id_2"`.
- Substring test: `name_filter in task.name` (case-sensitive).
- Guard `max_results <= 0`.

## Level 3
- An assignment is a small object: task_id, start, finish, sequence number, (later) completed flag.
- Active at t means `start <= t < finish`. The quota check counts active assignments AT the assignment timestamp.
- Sort a user's active assignments by `(finish, sequence)`.

## Level 4
- Completing sets `completed_at`. The active and overdue checks must both look at it.
- Overdue = `finish <= t` and never completed. Completing after expiry is impossible (it is no longer active).
- When several assignments match, complete the one with the smallest `(finish, sequence)`.
