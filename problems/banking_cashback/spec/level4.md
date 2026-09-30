## Level 4

The banking system should support merging two accounts while retaining both accounts' balances and transaction histories.

*   `merge_accounts(self, timestamp: int, account_id_1: str, account_id_2: str) -> bool` — should merge `account_id_2` into `account_id_1`. Returns `True` if the accounts were merged, or `False` otherwise:
    *   `False` if `account_id_1` equals `account_id_2`;
    *   `False` if `account_id_1` or `account_id_2` doesn't exist.
    *   On success:
        *   the balance of `account_id_2` is added to the balance of `account_id_1`;
        *   pending cashback refunds of `account_id_2` are still processed on time, but refunded to `account_id_1`;
        *   payments made by `account_id_2` can now be checked with `get_payment_status` using `account_id_1`;
        *   `top_spenders` treats the merged account's outgoing total as the sum of both accounts' outgoing totals;
        *   `account_id_2` is removed from the system (a later `create_account` with that id creates a brand-new account).

*   `get_balance(self, timestamp: int, account_id: str, time_at: int) -> int | None` — should return the balance of `account_id` at time `time_at` (`time_at <= timestamp`).
    *   If operations were processed at `time_at`, return the balance **after** they were processed.
    *   Returns `None` if the account did not exist at `time_at` (not created yet, or already merged into another account at or before `time_at`).
    *   Before a merge, each account's history is its own. From the merge timestamp on, `account_id_1`'s balance includes the money from `account_id_2`. The history of `account_id_2` before the merge can still be queried with `account_id_2`.
    *   Cashback counts from the moment it is due (`payment time + 86400000`).

### Examples

`DAY = 86400000`

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
| --- | --- |
| `create_account(1, "alice")` | returns True |
| `create_account(2, "bob")` | returns True |
| `deposit(3, "alice", 2000)` | returns 2000 |
| `deposit(4, "bob", 2000)` | returns 2000 |
| `pay(5, "alice", 500)` | returns "payment1"; cashback of 10 due at `5 + DAY` |
| `transfer(6, "alice", "bob", 500)` | returns 1000; bob now has 2500 |
| `merge_accounts(7, "alice", "carol")` | returns False; carol doesn't exist |
| `merge_accounts(8, "alice", "alice")` | returns False; cannot merge into itself |
| `merge_accounts(9, "alice", "bob")` | returns True; alice: 1000 + 2500 = 3500 |
| `get_balance(10, "alice", 9)` | returns 3500 |
| `get_balance(11, "bob", 8)` | returns 2500; bob still existed at time 8 |
| `get_balance(12, "bob", 9)` | returns None; bob was merged at time 9 |
| `get_balance(13, "bob", 1)` | returns None; bob was not created yet |
| `get_payment_status(14, "alice", "payment1")` | returns "IN_PROGRESS" |
| `get_payment_status(15, "bob", "payment1")` | returns None; bob doesn't exist anymore |
| `top_spenders(16, 3)` | returns ["alice(1000)"]; 500 paid + 500 transferred |
| `get_balance(17, "alice", 6)` | returns 1000; alice's own balance before the merge |
| `deposit(5 + DAY, "alice", 100)` | returns 3610; 3500 + 10 cashback + 100 |
| `get_balance(6 + DAY, "alice", 4 + DAY)` | returns 3500; cashback not due yet at that time |
| `get_balance(7 + DAY, "alice", 5 + DAY)` | returns 3610 |

### Input/Output

*   **[execution time limit]** 3 seconds
*   **[memory limit]** 1 GB
