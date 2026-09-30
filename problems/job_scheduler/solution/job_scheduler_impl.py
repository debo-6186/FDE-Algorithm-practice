from __future__ import annotations

from collections import deque

from job_scheduler import JobScheduler

PENDING, RUNNING, DONE, CANCELED = "pending", "running", "done", "canceled"


class Job:
    def __init__(self, job_id: str, priority: int, seq: int):
        self.id = job_id
        self.priority = priority
        self.seq = seq                         # insertion order for tie-breaks
        self.state = PENDING                   # pending = not started, not canceled
        self.prereqs: set[str] = set()         # jobs this one waits for
        self.dependents: set[str] = set()      # jobs waiting for this one


class JobSchedulerImpl(JobScheduler):

    def __init__(self):
        self.jobs: dict[str, Job] = {}
        self.count = 0

    # ---- helpers ---------------------------------------------------------------
    def _ready(self, job: Job) -> bool:
        return job.state == PENDING and all(self.jobs[p].state == DONE for p in job.prereqs)

    def _status(self, job: Job) -> str:
        if job.state == PENDING:
            return "queued" if self._ready(job) else "blocked"
        return job.state

    def _ready_in_order(self) -> list[Job]:
        return sorted((j for j in self.jobs.values() if self._ready(j)), key=lambda j: (-j.priority, j.seq))

    def _depends_on(self, start: str, target: str) -> bool:
        """True if `start` (transitively) waits for `target`."""
        stack, seen = [start], set()
        while stack:
            cur = stack.pop()
            if cur == target:
                return True
            if cur in seen:
                continue
            seen.add(cur)
            stack.extend(self.jobs[cur].prereqs)
        return False

    # ---- Level 1 ---------------------------------------------------------------
    def add_job(self, job_id: str, priority: int) -> bool:
        if job_id in self.jobs:
            return False
        self.count += 1
        self.jobs[job_id] = Job(job_id, priority, self.count)
        return True

    def next_job(self) -> str | None:
        ready = self._ready_in_order()
        if not ready:
            return None
        ready[0].state = RUNNING
        return ready[0].id

    def complete_job(self, job_id: str) -> bool:
        job = self.jobs.get(job_id)
        if job is None or job.state != RUNNING:
            return False
        job.state = DONE
        return True

    def get_status(self, job_id: str) -> str | None:
        job = self.jobs.get(job_id)
        return self._status(job) if job else None

    # ---- Level 2 ---------------------------------------------------------------
    def peek_jobs(self, n: int) -> list[str]:
        return [j.id for j in self._ready_in_order()[:max(n, 0)]]

    def jobs_with_status(self, status: str) -> list[str]:
        return sorted(j.id for j in self.jobs.values() if self._status(j) == status)

    # ---- Level 3 ---------------------------------------------------------------
    def add_dependency(self, job_id: str, prerequisite_id: str) -> bool:
        job, pre = self.jobs.get(job_id), self.jobs.get(prerequisite_id)
        if job is None or pre is None or job is pre:
            return False
        if job.state != PENDING or pre.state == CANCELED or prerequisite_id in job.prereqs:
            return False
        if self._depends_on(prerequisite_id, job_id):   # edge would close a cycle
            return False
        job.prereqs.add(prerequisite_id)
        pre.dependents.add(job_id)
        return True

    # ---- Level 4 ---------------------------------------------------------------
    def cancel_job(self, job_id: str) -> list[str]:
        job = self.jobs.get(job_id)
        if job is None or job.state != PENDING:
            return []
        canceled, queue = [], deque([job_id])
        while queue:                                    # BFS over dependents
            cur = self.jobs[queue.popleft()]
            if cur.state != PENDING:
                continue
            cur.state = CANCELED
            canceled.append(cur.id)
            queue.extend(cur.dependents)
        return sorted(canceled)
