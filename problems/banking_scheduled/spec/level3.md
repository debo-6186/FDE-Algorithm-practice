## Level 3

The banking system should allow scheduling payments and canceling them.

*   `schedule_payment(self, timestamp: int, account_id: str, amount: int, delay: int) -> str | None` — should schedule a payment (a withdrawal of `amount` from `account_id`) that will be performed at `timestamp + delay` (`delay >= 1`). Returns a unique identifier `"payment<k>"`, where `k` is the ordinal number of **scheduled** payments across all accounts (`"payment1"`, `"payment2"`, ...). Returns `None` if `account_id` doesn't exist. Funds are **not** checked when scheduling.
    *   When a payment is performed, if the account has sufficient funds the amount is withdrawn; otherwise the payment is **skipped** (and never retried).
    *   Performed payments count as outgoing transactions in `top_spenders`.
    *   Scheduled payments must be processed **before any other operation** at the given timestamp. If no operation happens exactly at that time, they must still be reflected by any later operation.
    *   If several payments are due at the same time, process them in order of creation (`"payment1"` before `"payment2"`).

*   `cancel_payment(self, timestamp: int, account_id: str, payment_id: str) -> bool` — should cancel the scheduled payment `payment_id`. Returns `True` if it was canceled. Returns `False` if the payment doesn't exist, was already performed, skipped or canceled, or if `account_id` is not the account the payment was scheduled for. Payments due at `timestamp` are processed before the cancel attempt.

### Examples

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
| --- | --- |
| `create_account(1, "alice")` | returns True |
| `create_account(2, "bob")` | returns True |
| `deposit(3, "alice", 1000)` | returns 1000 |
| `schedule_payment(4, "alice", 300, 10)` | returns "payment1"; due at 14 |
| `schedule_payment(5, "carol", 100, 5)` | returns None; no such account |
| `schedule_payment(6, "bob", 50, 8)` | returns "payment2"; due at 14; bob has no money |
| `schedule_payment(7, "alice", 200, 20)` | returns "payment3"; due at 27 |
| `cancel_payment(8, "bob", "payment1")` | returns False; payment1 belongs to alice |
| `cancel_payment(9, "alice", "payment9")` | returns False; no such payment |
| `deposit(13, "alice", 10)` | returns 1010; nothing performed yet |
| `deposit(14, "bob", 100)` | returns 100; first payment1 (alice: 710), then payment2 is skipped (bob had 0), then the deposit |
| `cancel_payment(15, "bob", "payment2")` | returns False; already skipped |
| `cancel_payment(16, "alice", "payment3")` | returns True |
| `cancel_payment(17, "alice", "payment3")` | returns False; already canceled |
| `top_spenders(30, 2)` | returns ["alice(300)", "bob(0)"]; skipped and canceled payments don't count |
| `deposit(31, "alice", 1)` | returns 711 |

### Input/Output

*   **[execution time limit]** 3 seconds
*   **[memory limit]** 1 GB
