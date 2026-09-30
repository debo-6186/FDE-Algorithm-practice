## Level 2

The bank wants to identify people who are not keeping money in their accounts. Implement an operation to rank accounts by outgoing transactions.

*   `top_spenders(self, timestamp: int, n: int) -> list[str]` — should return the identifiers of the top `n` accounts with the highest **outgoing transactions**: the total amount of money transferred out of the account (and, from Level 3 on, paid out of it with `pay`). Sort by total outgoing in **descending** order; in case of a tie, sort by `account_id` in **ascending** (alphabetical) order.
    *   Format: `["<account_id_1>(<total_outgoing_1>)", "<account_id_2>(<total_outgoing_2>)", ...]`.
    *   If fewer than `n` accounts exist, return all of them.
    *   Accounts with no outgoing transactions are included with `0`.
    *   Incoming money (deposits, transfers in, and Level 3 cashback) does not count.

### Examples

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
| --- | --- |
| `create_account(1, "acc3")` | returns True |
| `create_account(2, "acc2")` | returns True |
| `create_account(3, "acc1")` | returns True |
| `deposit(4, "acc3", 2000)` | returns 2000 |
| `deposit(5, "acc2", 3000)` | returns 3000 |
| `deposit(6, "acc3", 4000)` | returns 6000 |
| `top_spenders(7, 3)` | returns ["acc1(0)", "acc2(0)", "acc3(0)"]; all tied at 0, so alphabetical |
| `transfer(8, "acc3", "acc2", 500)` | returns 5500 |
| `transfer(9, "acc3", "acc1", 1000)` | returns 4500 |
| `transfer(10, "acc1", "acc2", 700)` | returns 300 |
| `top_spenders(11, 3)` | returns ["acc3(1500)", "acc1(700)", "acc2(0)"] |
| `top_spenders(12, 1)` | returns ["acc3(1500)"] |
| `top_spenders(13, 5)` | returns ["acc3(1500)", "acc1(700)", "acc2(0)"]; only 3 accounts exist |

### Input/Output

*   **[execution time limit]** 3 seconds
*   **[memory limit]** 1 GB
