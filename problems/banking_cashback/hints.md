# Hints: Banking System (cashback)

## Level 1
- Keep `self.accounts: dict[str, Account]` where `Account` is a tiny class (balance, outgoing, ...). A class is easier to extend at Level 3/4 than a dict of ints.
- Validate everything first, then mutate: a failed transfer must not change either balance.
- Same-account transfer returns `None` even when funds are sufficient.

## Level 2
- Track `outgoing` as a running total on each account; don't recompute from a log.
- `sorted(accounts, key=lambda a: (-a.outgoing, a.id))[:n]` handles descending amount + ascending id and "fewer than n".
- Format exactly `f"{a.id}({a.outgoing})"` with no spaces.

## Level 3
- Put `self._process(timestamp)` as the FIRST line of EVERY public method. It applies every cashback with `due <= timestamp` before the operation runs.
- Store pending cashbacks in a heap `(due_time, seq, payment_id)`, or a list you scan. Timestamps are unique, so the sequence number only breaks ties.
- Cashback = `amount * 2 // 100` (integer math, rounds down). Only successful payments get an id and increment the counter.
- Status is per payment and must be checked against the owning account.

## Level 4
- Merge: move balance and outgoing, point every payment of account 2 at account 1 (so pending cashback and status checks follow), then delete account 2.
- `get_balance` needs history: append `(timestamp, balance)` to a per-id list whenever a balance changes, including cashback (use the cashback's DUE time), then binary-search with `bisect_right`.
- Mark the merged-away id with `(merge_timestamp, None)` so queries at or after the merge return `None`, while earlier times still return its old balance.
- `get_balance` is also an operation: it must process due cashbacks first.
