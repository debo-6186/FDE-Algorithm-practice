from __future__ import annotations

import bisect
import heapq

from banking_system import BankingSystem

DAY_MS = 24 * 60 * 60 * 1000
CASHBACK_PERCENT = 2


class History:
    """Timeline of (timestamp, value) for one account id. value None = account doesn't exist."""

    def __init__(self):
        self.times: list[int] = []
        self.values: list[int | None] = []

    def record(self, timestamp: int, value: int | None) -> None:
        self.times.append(timestamp)
        self.values.append(value)

    def at(self, timestamp: int) -> int | None:
        i = bisect.bisect_right(self.times, timestamp)   # last entry with time <= timestamp
        return self.values[i - 1] if i else None


class Account:
    def __init__(self, account_id: str):
        self.id = account_id
        self.balance = 0
        self.outgoing = 0
        self.payment_ids: list[str] = []


class Payment:
    def __init__(self, payment_id: str, owner: str, cashback: int, due: int):
        self.id = payment_id
        self.owner = owner
        self.cashback = cashback
        self.due = due
        self.status = "IN_PROGRESS"


class BankingSystemImpl(BankingSystem):

    def __init__(self):
        self.accounts: dict[str, Account] = {}
        self.history: dict[str, History] = {}
        self.payments: dict[str, Payment] = {}
        self.payment_count = 0
        self.pending: list[tuple[int, int, str]] = []   # min-heap of (due, seq, payment_id)

    # ---- shared helpers ----------------------------------------------------
    def _process(self, timestamp: int) -> None:
        """Apply every cashback due at or before `timestamp` (called first by every operation)."""
        while self.pending and self.pending[0][0] <= timestamp:
            due, _, pid = heapq.heappop(self.pending)
            payment = self.payments[pid]
            account = self.accounts[payment.owner]      # owner is updated on merge
            account.balance += payment.cashback
            payment.status = "CASHBACK_RECEIVED"
            self._log(account.id, due, account.balance)  # history uses the due time

    def _log(self, account_id: str, timestamp: int, value: int | None) -> None:
        self.history.setdefault(account_id, History()).record(timestamp, value)

    # ---- Level 1 -------------------------------------------------------------
    def create_account(self, timestamp: int, account_id: str) -> bool:
        self._process(timestamp)
        if account_id in self.accounts:
            return False
        self.accounts[account_id] = Account(account_id)
        self._log(account_id, timestamp, 0)
        return True

    def deposit(self, timestamp: int, account_id: str, amount: int) -> int | None:
        self._process(timestamp)
        account = self.accounts.get(account_id)
        if account is None:
            return None
        account.balance += amount
        self._log(account_id, timestamp, account.balance)
        return account.balance

    def transfer(self, timestamp: int, source_account_id: str, target_account_id: str, amount: int) -> int | None:
        self._process(timestamp)
        source = self.accounts.get(source_account_id)
        target = self.accounts.get(target_account_id)
        if source is None or target is None or source is target or source.balance < amount:
            return None
        source.balance -= amount
        source.outgoing += amount
        target.balance += amount
        self._log(source.id, timestamp, source.balance)
        self._log(target.id, timestamp, target.balance)
        return source.balance

    # ---- Level 2 -------------------------------------------------------------
    def top_spenders(self, timestamp: int, n: int) -> list[str]:
        self._process(timestamp)
        ranked = sorted(self.accounts.values(), key=lambda a: (-a.outgoing, a.id))
        return [f"{a.id}({a.outgoing})" for a in ranked[:n]]

    # ---- Level 3 -------------------------------------------------------------
    def pay(self, timestamp: int, account_id: str, amount: int) -> str | None:
        self._process(timestamp)
        account = self.accounts.get(account_id)
        if account is None or account.balance < amount:
            return None
        account.balance -= amount
        account.outgoing += amount
        self.payment_count += 1
        pid = f"payment{self.payment_count}"
        due = timestamp + DAY_MS
        self.payments[pid] = Payment(pid, account_id, amount * CASHBACK_PERCENT // 100, due)
        account.payment_ids.append(pid)
        heapq.heappush(self.pending, (due, self.payment_count, pid))
        self._log(account_id, timestamp, account.balance)
        return pid

    def get_payment_status(self, timestamp: int, account_id: str, payment: str) -> str | None:
        self._process(timestamp)
        if account_id not in self.accounts:
            return None
        p = self.payments.get(payment)
        if p is None or p.owner != account_id:
            return None
        return p.status

    # ---- Level 4 -------------------------------------------------------------
    def merge_accounts(self, timestamp: int, account_id_1: str, account_id_2: str) -> bool:
        self._process(timestamp)
        if account_id_1 == account_id_2:
            return False
        if account_id_1 not in self.accounts or account_id_2 not in self.accounts:
            return False
        a1 = self.accounts[account_id_1]
        a2 = self.accounts.pop(account_id_2)
        a1.balance += a2.balance
        a1.outgoing += a2.outgoing
        for pid in a2.payment_ids:            # pending cashbacks + status lookups follow the money
            self.payments[pid].owner = account_id_1
            a1.payment_ids.append(pid)
        self._log(account_id_1, timestamp, a1.balance)
        self._log(account_id_2, timestamp, None)   # account_id_2 stops existing now
        return True

    def get_balance(self, timestamp: int, account_id: str, time_at: int) -> int | None:
        self._process(timestamp)
        history = self.history.get(account_id)
        return history.at(time_at) if history else None
