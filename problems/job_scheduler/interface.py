from __future__ import annotations

from abc import ABC


class JobScheduler(ABC):
    """
    `JobScheduler` interface.
    Default implementations return placeholder values; override every method
    in `JobSchedulerImpl` (job_scheduler_impl.py).
    """

# @@LEVEL 1@@
    def add_job(self, job_id: str, priority: int) -> bool:
        """
        Should add a queued job. `False` if the id already exists.
        """
        # default implementation
        return False

    def next_job(self) -> str | None:
        """
        Should start the highest-priority queued job (ties: added first) and
        return its id, or `None`.
        """
        # default implementation
        return None

    def complete_job(self, job_id: str) -> bool:
        """
        Should mark a running job as done. `False` otherwise.
        """
        # default implementation
        return False

    def get_status(self, job_id: str) -> str | None:
        """
        Should return the job's status or `None`.
        """
        # default implementation
        return None

# @@LEVEL 2@@
    def peek_jobs(self, n: int) -> list[str]:
        """
        Should return the next `n` jobs `next_job` would start, without starting them.
        """
        # default implementation
        return []

    def jobs_with_status(self, status: str) -> list[str]:
        """
        Should return ids of jobs with `status`, sorted alphabetically.
        """
        # default implementation
        return []

# @@LEVEL 3@@
    def add_dependency(self, job_id: str, prerequisite_id: str) -> bool:
        """
        Should make `job_id` wait for `prerequisite_id`. `False` on invalid
        input, started job, duplicate, or cycle.
        """
        # default implementation
        return False

# @@LEVEL 4@@
    def cancel_job(self, job_id: str) -> list[str]:
        """
        Should cancel a not-started job and all not-started jobs depending on
        it. Returns canceled ids sorted alphabetically.
        """
        # default implementation
        return []
