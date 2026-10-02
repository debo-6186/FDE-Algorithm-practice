from dataclasses import dataclass, field
from interface import WorkerRegistry

@dataclass
class Worker:
    worker_id: str
    position: str
    compensation: str
    position_hours: int = 0

@dataclass
class WorkerRegistry:
    timestamp: int = 0
    current_state: str = ""
    total_working_hours: int = 0
    sessions: list[tuple[int, int, int]] = field(default_factory=list)  # (entry_ts, exit_ts, compensation)

@dataclass
class WorkerPromotion:
    worker_id: str
    promotion_status: str
    new_position: str
    new_salary: int
    start_timestamp: int

class WorkerRegistryImpl(WorkerRegistry):

    def __init__(self):
        self.workers: dict[str, Worker] = {}
        self.registry: dict[str, WorkerRegistry] = {}
        self.promotions: dict[str, WorkerPromotion] = {}

    # @@LEVEL 1@@
    def add_worker(self, worker_id: str, position: str, compensation: int) -> bool:
        """
        Should add the worker. Returns `False` if `worker_id` already exists.
        """
        worker = self.workers.get(worker_id, None)
        if worker is not None:
            return False
        self.workers[worker_id] = Worker(worker_id, position, compensation)
        self.registry[worker_id] = None
        return True

    def register(self, worker_id: str, timestamp: int) -> str:
        """
        Should register an entry (if the worker is outside) or an exit (if
        inside). Returns "registered" or "invalid_request".
        """
        worker = self.workers.get(worker_id, None)
        if worker is None:
            return "invalid_request"
        worker_registry = self.registry.get(worker_id, None)
        if worker_registry is None:
            self.registry[worker_id] = WorkerRegistry(timestamp, "entry", 0)
            self._maybe_apply_promotion(worker, timestamp)
        elif worker_registry.current_state == "entry":
            duration = timestamp - worker_registry.timestamp
            worker_registry.sessions.append((worker_registry.timestamp, timestamp, worker.compensation))
            worker_registry.total_working_hours += duration
            worker.position_hours += duration
            worker_registry.current_state = "exit"
            worker_registry.timestamp = timestamp
        else:
            worker_registry.current_state = "entry"
            worker_registry.timestamp = timestamp
            self._maybe_apply_promotion(worker, timestamp)
        return "registered"

    def _maybe_apply_promotion(self, worker: Worker, timestamp: int) -> None:
        promotion = self.promotions.get(worker.worker_id, None)
        if promotion is None or promotion.promotion_status != "pending":
            return
        if timestamp >= promotion.start_timestamp:
            worker.position = promotion.new_position
            worker.compensation = promotion.new_salary
            worker.position_hours = 0
            promotion.promotion_status = "active"

    def get(self, worker_id: str) -> int | None:
        """
        Should return the total time of finished sessions, or `None`.
        """
        worker = self.workers.get(worker_id, None)
        if worker is None:
            return None
        worker_registry = self.registry.get(worker_id, None)
        if worker_registry is None:
            return 0
        return worker_registry.total_working_hours

    # @@LEVEL 2@@
    def top_n_workers(self, n: int, position: str) -> list[str]:
        """
        Should return ["<worker_id>(<time>)", ...] for the top `n` workers with
        the given current position, by time descending, ties by id ascending.
        """
        worker_registry_set = []
        for worker_id, worker in self.workers.items():
            if worker.position == position:
                worker_registry_set.append(worker_id)
        worker_registry_set = sorted(
            worker_registry_set,
            key=lambda w: (-self.workers[w].position_hours, w),
        )
        return [f"{w}({self.workers[w].position_hours})" for w in worker_registry_set[:n]]

    # @@LEVEL 3@@
    def promote(self, worker_id: str, new_position: str, new_compensation: int, start_timestamp: int) -> str:
        """
        Should schedule a promotion that becomes active at the worker's first
        entry at or after `start_timestamp`. Returns "success" or
        "invalid_request".
        """
        worker = self.workers.get(worker_id)
        if worker is None:
            return "invalid_request"
        promotion = self.promotions.get(worker_id, None)
        if promotion is not None and promotion.promotion_status == "pending":
            return "invalid_request"
        self.promotions[worker_id] = WorkerPromotion(worker_id, "pending", new_position, new_compensation, start_timestamp)
        return "success"

    def calc_salary(self, worker_id: str, start_timestamp: int, end_timestamp: int) -> int | None:
        worker = self.workers.get(worker_id, None)
        if worker is None:
            return None
        worker_registry = self.registry.get(worker_id, None)
        if worker_registry is None:
            return 0
        salary = 0
        for entry_ts, exit_ts, compensation in worker_registry.sessions:
            overlap = min(exit_ts, end_timestamp) - max(entry_ts, start_timestamp)
            if overlap > 0:
                salary += overlap * compensation
        return salary
