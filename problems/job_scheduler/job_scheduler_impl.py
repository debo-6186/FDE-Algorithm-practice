from interface import JobScheduler

class JobSchedulerImpl(JobScheduler):

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

