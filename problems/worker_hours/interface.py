from __future__ import annotations

from abc import ABC


class WorkerRegistry(ABC):
    """
    `WorkerRegistry` interface.
    Default implementations return placeholder values; override every method
    in `WorkerRegistryImpl` (worker_registry_impl.py).
    """

# @@LEVEL 1@@
    def add_worker(self, worker_id: str, position: str, compensation: int) -> bool:
        """
        Should add the worker. Returns `False` if `worker_id` already exists.
        """
        # default implementation
        return False

    def register(self, worker_id: str, timestamp: int) -> str:
        """
        Should register an entry (if the worker is outside) or an exit (if
        inside). Returns "registered" or "invalid_request".
        """
        # default implementation
        return ""

    def get(self, worker_id: str) -> int | None:
        """
        Should return the total time of finished sessions, or `None`.
        """
        # default implementation
        return None

# @@LEVEL 2@@
    def top_n_workers(self, n: int, position: str) -> list[str]:
        """
        Should return ["<worker_id>(<time>)", ...] for the top `n` workers with
        the given current position, by time descending, ties by id ascending.
        """
        # default implementation
        return []

# @@LEVEL 3@@
    def promote(self, worker_id: str, new_position: str, new_compensation: int, start_timestamp: int) -> str:
        """
        Should schedule a promotion that becomes active at the worker's first
        entry at or after `start_timestamp`. Returns "success" or
        "invalid_request".
        """
        # default implementation
        return ""

    def calc_salary(self, worker_id: str, start_timestamp: int, end_timestamp: int) -> int | None:
        """
        Should return the salary for finished sessions overlapping
        [start_timestamp, end_timestamp], or `None` if the worker doesn't exist.
        """
        # default implementation
        return None

# @@LEVEL 4@@
    def set_double_paid(self, start_timestamp: int, end_timestamp: int) -> None:
        """
        Should mark [start_timestamp, end_timestamp] as double-paid for all
        workers (overlapping periods don't stack).
        """
        # default implementation
        return None
