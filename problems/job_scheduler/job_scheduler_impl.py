from enum import Enum
import heapq
from interface import JobScheduler

class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    DONE = "done"
    # Level 3
    BLOCKED = "blocked"
    # Level 4
    CANCELED = "canceled"

class Job:
    def __init__(self, job_id: str, priority: int, seq: int):
        self.job_id = job_id
        self.priority = priority
        self.seq = seq
        self.status = JobStatus.QUEUED
        self.prereqs: set[str] = set()
        self.dependents: set[str] = set()

    def __lt__(self, other: "Job") -> bool:
        return (-self.priority, self.seq) < (-other.priority, other.seq)

class JobSchedulerImpl(JobScheduler):

    def __init__(self):
        self.jobs: dict(str, Job) = {}
        self.queue: list[Job] = []
        self.seq = 0

    def add_job(self, job_id: str, priority: int) -> bool:
        """
        Should add a queued job. `False` if the id already exists.
        """
        if job_id in self.jobs:
            return False
        job = Job(job_id, priority, self.seq)
        self.seq += 1
        self.jobs[job_id] = job
        heapq.heappush(self.queue, job)
        return True

    def next_job(self) -> str | None:
        skipped, result = [], None
        while self.queue:
            job = heapq.heappop(self.queue)
            if job.status == JobStatus.QUEUED:
                job.status = JobStatus.RUNNING
                result = job.job_id
                break
            skipped.append(job)
        for job in skipped:
            heapq.heappush(self.queue, job)
        return result

    def complete_job(self, job_id: str) -> bool:
        job = self.jobs.get(job_id)
        if job is None or job.status != JobStatus.RUNNING:
            return False
        job.status = JobStatus.DONE
        for dep_id in job.dependents:
            dep = self.jobs[dep_id]
            if dep.status == JobStatus.BLOCKED and all(
                self.jobs[p].status == JobStatus.DONE for p in dep.prereqs
            ):
                dep.status = JobStatus.QUEUED
        return True

    def get_status(self, job_id: str) -> str | None:
        """
        Should return the job's status or `None`.
        """
        job = self.jobs.get(job_id, None)
        if job is None:
            return None
        return job.status

    # @@LEVEL 2@@
    def peek_jobs(self, n: int) -> list[str]:
        found, popped = [], []
        while self.queue and len(found) < n:
            job = heapq.heappop(self.queue)
            popped.append(job)
            if job.status == JobStatus.QUEUED:
                found.append(job.job_id)
        for job in popped:
            heapq.heappush(self.queue, job)
        return found

    def jobs_with_status(self, status: str) -> list[str]:
        """
        Should return ids of jobs with `status`, sorted alphabetically.
        """
        return sorted(job.job_id for job in self.jobs.values() if job.status == status)

    def _depends_on(self, start: str, target: str):
        stack, seen = list(self.jobs[start].prereqs), set()
        while stack:
            cur = stack.pop()
            if cur == target:
                return True
            if cur not in seen:
                seen.add(cur)
                stack.extend(self.jobs[cur].prereqs)
        return False

    def add_dependency(self, job_id: str, prerequisite_id: str) -> bool:
        """
        Should make `job_id` wait for `prerequisite_id`. `False` on invalid
        input, started job, duplicate, or cycle.
        """
        if job_id == prerequisite_id:
            return False
        job, pre = self.jobs.get(job_id), self.jobs.get(prerequisite_id)
        if job is None or pre is None:
            return False
        if job.status not in (JobStatus.QUEUED, JobStatus.BLOCKED):
            return False
        if prerequisite_id in job.prereqs:
            return False
        if self._depends_on(prerequisite_id, job_id):
            return False
        # Level 4
        if pre.status in (JobStatus.CANCELED,):
            return False
        job.prereqs.add(prerequisite_id)
        pre.dependents.add(job_id)
        if pre.status != JobStatus.DONE:
            job.status = JobStatus.BLOCKED
        return True

    # @@LEVEL 4@@
    def cancel_job(self, job_id: str) -> list[str]:
        job = self.jobs.get(job_id)
        if job is None or job.status not in (JobStatus.QUEUED, JobStatus.BLOCKED):
            return []
        canceled = []
        stack = [job_id]
        while stack:
            cur = self.jobs[stack.pop()]
            if cur.status not in (JobStatus.QUEUED, JobStatus.BLOCKED):
                continue  # already started, done, or already canceled — stop here
            cur.status = JobStatus.CANCELED
            canceled.append(cur.job_id)
            stack.extend(cur.dependents)
        return sorted(canceled)

