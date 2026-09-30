from __future__ import annotations

from abc import ABC


class BankingSystem(ABC):
    """
    `BankingSystem` interface.
    Default implementations return placeholder values; override every method
    in `BankingSystemImpl` (banking_system_impl.py).
    """

# @@LEVEL 1@@
    def create_account(self, timestamp: int, account_id: str) -> bool:
        """
        Should create a new account with the given identifier if it doesn't
        already exist. Returns `True` if the account was successfully created
        or `False` if an account with `account_id` already exists.
        """
        # default implementation
        return False

    def deposit(self, timestamp: int, account_id: str, amount: int) -> int | None:
        """
        Should deposit the given `amount` of money to the specified account
        `account_id`. Returns the balance of the account after the operation
        has been processed. If the specified account doesn't exist, should
        return `None`.
        """
        # default implementation
        return None

    def transfer(self, timestamp: int, source_account_id: str, target_account_id: str, amount: int) -> int | None:
        """
        Should transfer the given amount of money from account
        `source_account_id` to account `target_account_id`. Returns the
        balance of `source_account_id` if the transfer was successful or
        `None` otherwise (missing account, same account, insufficient funds).
        """
        # default implementation
        return None

# @@LEVEL 2@@
    def top_spenders(self, timestamp: int, n: int) -> list[str]:
        """
        Should return the identifiers of the top `n` accounts with the highest
        outgoing transactions, sorted in descending order, ties broken by
        `account_id` ascending. Format: ["<account_id>(<total_outgoing>)", ...].
        """
        # default implementation
        return []

# @@LEVEL 3@@
    def pay(self, timestamp: int, account_id: str, amount: int) -> str | None:
        """
        Should withdraw the given amount of money from the specified account.
        2% cashback (rounded down) is refunded 24 hours (86400000 ms) later.
        Returns "payment<k>" (k = ordinal number of successful payments across
        all accounts) or `None` if the account doesn't exist or has
        insufficient funds.
        """
        # default implementation
        return None

    def get_payment_status(self, timestamp: int, account_id: str, payment: str) -> str | None:
        """
        Should return "IN_PROGRESS" or "CASHBACK_RECEIVED" for the given
        payment, or `None` if the account doesn't exist, the payment doesn't
        exist, or the payment belongs to a different account.
        """
        # default implementation
        return None

# @@LEVEL 4@@
    def merge_accounts(self, timestamp: int, account_id_1: str, account_id_2: str) -> bool:
        """
        Should merge `account_id_2` into `account_id_1`. Returns `True` if the
        accounts were merged, `False` otherwise (same id or missing account).
        """
        # default implementation
        return False

    def get_balance(self, timestamp: int, account_id: str, time_at: int) -> int | None:
        """
        Should return the balance of `account_id` at time `time_at` (after all
        operations at `time_at` were processed), or `None` if the account did
        not exist at `time_at`.
        """
        # default implementation
        return None
