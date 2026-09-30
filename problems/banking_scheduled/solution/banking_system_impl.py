from __future__ import annotations

import bisect
import heapq

from banking_system import BankingSystem


class History:
    """Timeline of (timestamp, value) for one account id. value None = account doesn't exist."""

    def __init__(self):
        self.times: list[int] = []
        self.values: list[int | None] = []

    def record(self, timestamp: int, value: int | None) -> None:
        self.times.append(timestamp)
        self.values.append(value)

    def at(self, timestamp: int) -> int | None:
        i = bisect.bisect_right(self.times, timestamp)
        return self.values[i - 1] if i else None


class Account:
    def __init__(self, account_id: str):
        self.id = account_id
        self.balance = 0
        self.outgoing = 0


class ScheduledPayment:
    def __init__(self, payment_id: str, owner: str, amount: int, due: int):
        self.id = payment_id
        self.owner = owner
        self.amount = amount
        self.due = due
        self.status = "PENDING"   # PENDING -> DONE | SKIPPED | CANCELED


class BankingSystemImpl(BankingSystem):

    def __init__(self):
        self.accounts: dict[str, Account] = {}
        self.history: dict[str, History] = {}
        self.payments: dict[str, ScheduledPayment] = {}
        self.payment_count = 0
        self.queue: list[tuple[int, int, str]] = []   # min-heap of (due, creation_seq, payment_id)

    # ---- shared helpers ----------------------------------------------------
    def _process(self, timestamp: int) -> None:
        """Perform every scheduled payment due at or before `timestamp`, in (due, creation) order."""
        while self.queue and self.queue[0][0] <= timestamp:
            due, _, pid = heapq.heappop(self.queue)
            p = self.payments[pid]
            if p.status != "PENDING":            # canceled while waiting in the heap
                continue
            account = self.accounts[p.owner]
            if account.balance >= p.amount:
                account.balance -= p.amount
                account.outgoing += p.amount
                p.status = "DONE"
                self._log(account.id, due, account.balance)
            else:
                p.status = "SKIPPED"

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
    def schedule_payment(self, timestamp: int, account_id: str, amount: int, delay: int) -> str | None:
        self._process(timestamp)
        if account_id not in self.accounts:
            return None
        self.payment_count += 1
        pid = f"payment{self.payment_count}"
        due = timestamp + delay
        self.payments[pid] = ScheduledPayment(pid, account_id, amount, due)
        heapq.heappush(self.queue, (due, self.payment_count, pid))
        return pid

    def cancel_payment(self, timestamp: int, account_id: str, payment_id: str) -> bool:
        self._process(timestamp)                 # payments due now run before the cancel
        p = self.payments.get(payment_id)
        if p is None or p.owner != account_id or p.status != "PENDING":
            return False
        p.status = "CANCELED"                    # lazily dropped when popped from the heap
        return True

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
        for p in self.payments.values():         # pending payments now charge account 1
            if p.owner == account_id_2:
                p.owner = account_id_1
        self._log(account_id_1, timestamp, a1.balance)
        self._log(account_id_2, timestamp, None)
        return True

    def get_balance(self, timestamp: int, account_id: str, time_at: int) -> int | None:
        self._process(timestamp)
        history = self.history.get(account_id)
        return history.at(time_at) if history else None
