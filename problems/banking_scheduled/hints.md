# Hints: Banking System (scheduled payments)

## Level 1
- Keep `self.accounts: dict[str, Account]` where `Account` is a tiny class (balance, outgoing, ...). A class is easier to extend at Level 3/4 than a dict of ints.
- Validate everything first, then mutate: a failed transfer must not change either balance.
- Same-account transfer returns `None` even when funds are sufficient.

## Level 2
- Track `outgoing` as a running total on each account; don't recompute from a log.
- `sorted(accounts, key=lambda a: (-a.outgoing, a.id))[:n]` handles descending amount + ascending id and "fewer than n".

## Level 3
- Put `self._process(timestamp)` as the FIRST line of EVERY public method (including `cancel_payment` and `top_spenders`).
- Heap of `(due, creation_number, payment_id)` gives the right processing order for free. Or keep a list and scan it sorted by `(due, number)`.
- The counter increments on every successful `schedule_payment`, whether or not the payment is later performed.
- Keep a status per payment: PENDING / DONE / SKIPPED / CANCELED. Cancel only succeeds for PENDING and the right owner.
- A canceled payment can stay in the heap. Check its status when you pop it.

## Level 4
- On merge, re-point pending payments whose owner is account 2 to account 1.
- `get_balance` needs a per-id history of `(timestamp, balance)`. Log a performed payment at its DUE time, even though you apply it lazily.
- Record `(merge_timestamp, None)` for the merged-away id so later times return `None` but earlier times still work.
