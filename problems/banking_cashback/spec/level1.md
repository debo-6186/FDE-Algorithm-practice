## Level 1

Initially the banking system has no accounts. Implement operations to create accounts, deposit money, and transfer money between two different accounts.

*   `create_account(self, timestamp: int, account_id: str) -> bool` — should create a new account with the given identifier if it doesn't already exist. Returns `True` if the account was created, or `False` if an account with `account_id` already exists.

*   `deposit(self, timestamp: int, account_id: str, amount: int) -> int | None` — should deposit `amount` into the account `account_id`. Returns the balance of the account after the operation. Returns `None` if the account doesn't exist.

*   `transfer(self, timestamp: int, source_account_id: str, target_account_id: str, amount: int) -> int | None` — should transfer `amount` from `source_account_id` to `target_account_id`. Returns the balance of `source_account_id` after a successful transfer, or `None` otherwise:
    *   `None` if `source_account_id` or `target_account_id` doesn't exist;
    *   `None` if `source_account_id` and `target_account_id` are the same;
    *   `None` if `source_account_id` has insufficient funds. A failed transfer changes nothing.

### Examples

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
| --- | --- |
| `create_account(1, "alice")` | returns True |
| `create_account(2, "alice")` | returns False; account already exists |
| `create_account(3, "bob")` | returns True |
| `deposit(4, "carol", 500)` | returns None; no such account |
| `deposit(5, "alice", 1000)` | returns 1000 |
| `transfer(6, "alice", "bob", 1001)` | returns None; insufficient funds |
| `transfer(7, "alice", "alice", 10)` | returns None; same account |
| `transfer(8, "alice", "bob", 300)` | returns 700; alice's balance after the transfer |
| `deposit(9, "bob", 50)` | returns 350 |

### Input/Output

*   **[execution time limit]** 3 seconds
*   **[memory limit]** 1 GB
