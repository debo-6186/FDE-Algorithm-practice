## Level 3

The banking system should allow making payments that earn cashback, and checking the status of those payments.

*   `pay(self, timestamp: int, account_id: str, amount: int) -> str | None` — should withdraw `amount` from the account. Every successful payment earns a **2% cashback**: 2% of the amount, **rounded down** to an integer, is refunded to the account **24 hours** after the payment. If the payment succeeds, returns a unique identifier `"payment<k>"`, where `k` is the ordinal number of successful payments across **all** accounts (`"payment1"`, `"payment2"`, ...).
    *   Returns `None` if `account_id` doesn't exist.
    *   Returns `None` if the account has insufficient funds (nothing changes).
    *   `top_spenders` must now also include money paid with `pay`.
    *   24 hours = `24 * 60 * 60 * 1000 = 86400000` milliseconds, so cashback for a payment made at `timestamp` is refunded at `timestamp + 86400000`.
    *   When it is time to refund a cashback, the refund must happen **before any other operation** at that timestamp. If no operation happens exactly at that time, the refund must still be reflected by any later operation.

*   `get_payment_status(self, timestamp: int, account_id: str, payment: str) -> str | None` — should return the status of the payment `payment`:
    *   `None` if `account_id` doesn't exist;
    *   `None` if the payment doesn't exist;
    *   `None` if the payment was made from a different account than `account_id`;
    *   otherwise `"IN_PROGRESS"` (cashback not refunded yet) or `"CASHBACK_RECEIVED"`.

### Examples

`DAY = 86400000`

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
| --- | --- |
| `create_account(1, "alice")` | returns True |
| `create_account(2, "bob")` | returns True |
| `deposit(3, "alice", 2000)` | returns 2000 |
| `pay(4, "alice", 1000)` | returns "payment1"; cashback of 20 due at `4 + DAY` |
| `pay(5, "bob", 10)` | returns None; insufficient funds |
| `pay(6, "carol", 10)` | returns None; no such account |
| `pay(100, "alice", 500)` | returns "payment2"; cashback of 10 due at `100 + DAY` |
| `get_payment_status(101, "carol", "payment1")` | returns None; no such account |
| `get_payment_status(102, "bob", "payment1")` | returns None; payment belongs to alice |
| `get_payment_status(103, "alice", "payment3")` | returns None; no such payment |
| `get_payment_status(104, "alice", "payment1")` | returns "IN_PROGRESS" |
| `top_spenders(105, 2)` | returns ["alice(1500)", "bob(0)"] |
| `deposit(3 + DAY, "alice", 100)` | returns 600; cashback for payment1 not due yet |
| `get_payment_status(4 + DAY, "alice", "payment1")` | returns "CASHBACK_RECEIVED"; refund happens first |
| `deposit(5 + DAY, "alice", 100)` | returns 720; 600 + 20 cashback + 100 |
| `deposit(99 + DAY, "alice", 100)` | returns 820 |
| `deposit(100 + DAY, "alice", 100)` | returns 930; 820 + 10 cashback + 100 |
| `top_spenders(101 + DAY, 1)` | returns ["alice(1500)"]; cashback does not reduce outgoing |

### Input/Output

*   **[execution time limit]** 3 seconds
*   **[memory limit]** 1 GB
