## Level 4

The banking system should support merging two accounts while retaining both accounts' balances and transaction histories.

*   `merge_accounts(self, timestamp: int, account_id_1: str, account_id_2: str) -> bool` — should merge `account_id_2` into `account_id_1`. Returns `True` if the accounts were merged, or `False` otherwise:
    *   `False` if `account_id_1` equals `account_id_2`;
    *   `False` if `account_id_1` or `account_id_2` doesn't exist.
    *   On success:
        *   the balance of `account_id_2` is added to the balance of `account_id_1`;
        *   pending scheduled payments of `account_id_2` now belong to `account_id_1`: they will be withdrawn from `account_id_1`, and can only be canceled with `account_id_1`;
        *   `top_spenders` treats the merged account's outgoing total as the sum of both accounts' outgoing totals;
        *   `account_id_2` is removed from the system (a later `create_account` with that id creates a brand-new account).

*   `get_balance(self, timestamp: int, account_id: str, time_at: int) -> int | None` — should return the balance of `account_id` at time `time_at` (`time_at <= timestamp`).
    *   If operations were processed at `time_at`, return the balance **after** they were processed.
    *   Returns `None` if the account did not exist at `time_at` (not created yet, or already merged into another account at or before `time_at`).
    *   Before a merge, each account's history is its own. From the merge timestamp on, `account_id_1`'s balance includes the money from `account_id_2`. The history of `account_id_2` before the merge can still be queried with `account_id_2`.
    *   A scheduled payment changes the balance at the moment it is due (`timestamp + delay`).

### Examples

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
| --- | --- |
| `create_account(1, "alice")` | returns True |
| `create_account(2, "bob")` | returns True |
| `deposit(3, "alice", 500)` | returns 500 |
| `deposit(4, "bob", 800)` | returns 800 |
| `schedule_payment(5, "bob", 300, 10)` | returns "payment1"; due at 15 |
| `transfer(6, "bob", "alice", 100)` | returns 700; alice: 600 |
| `merge_accounts(7, "alice", "bob")` | returns True; alice: 600 + 700 = 1300 |
| `cancel_payment(8, "bob", "payment1")` | returns False; bob doesn't exist anymore |
| `get_balance(9, "bob", 6)` | returns 700; bob's own history before the merge |
| `get_balance(10, "alice", 6)` | returns 600 |
| `get_balance(11, "alice", 7)` | returns 1300 |
| `deposit(15, "alice", 1)` | returns 1001; payment1 is withdrawn from alice first: 1000, then + 1 |
| `top_spenders(16, 2)` | returns ["alice(400)"]; bob's 100 transfer + 300 payment |
| `get_balance(17, "alice", 15)` | returns 1001 |
| `get_balance(18, "alice", 14)` | returns 1300 |

### Input/Output

*   **[execution time limit]** 3 seconds
*   **[memory limit]** 1 GB
