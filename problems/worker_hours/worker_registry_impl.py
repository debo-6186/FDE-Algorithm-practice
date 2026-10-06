from dataclasses import dataclass, field
from interface import WorkerRegistry

@dataclass
class Worker:
    worker_id: str
    position: str
    compensation: int
    registry: list["RegistryEntry"] = field(default_factory=list)
    promotions: list["Promotion"] = field(default_factory=list)
    total_time: int = 0
    position_time: int = 0

@dataclass
class RegistryEntry:
    worker_id: str
    timestamp: int
    type: str
    compensation: int
    shift_time: int

@dataclass
class Promotion:
    worker_id: str
    start_timestamp: int
    new_position: str
    new_compensation: int
    status: str

class WorkerRegistryImpl(WorkerRegistry):

    def __init__(self):
        self.workers: dict[str, Worker] = {}

    # @@LEVEL 1@@
    def add_worker(self, worker_id: str, position: str, compensation: int) -> bool:
        """
        Should add the worker. Returns `False` if `worker_id` already exists.
        """
        worker = self.workers.get(worker_id, None)
        if worker is not None:
            return False
        self.workers[worker_id] = Worker(worker_id, position, compensation)
        return True
        

    def register(self, worker_id: str, timestamp: int) -> str:
        """
        Should register an entry (if the worker is outside) or an exit (if
        inside). Returns "registered" or "invalid_request".
        """
        worker = self.workers.get(worker_id, None)
        if worker is None:
            return "invalid_request"
        worker_registries = worker.registry
        if len(worker_registries) > 0:
            last_entry = worker_registries[len(worker_registries) - 1]
            if last_entry.type == "entry":
                worker_registries.append(RegistryEntry(worker_id, timestamp, "exit", worker.compensation, (timestamp-last_entry.timestamp)))
                worker.total_time += (timestamp - last_entry.timestamp)
                worker.position_time += (timestamp - last_entry.timestamp)
            else:
                if len(worker.promotions) > 0:
                    last_promotion = worker.promotions[-1]
                    if last_promotion.status == "pending" and timestamp >= last_promotion.start_timestamp:
                        last_promotion.status = "active"
                        worker.position = last_promotion.new_position
                        worker.compensation = last_promotion.new_compensation
                        worker.position_time = 0
                worker_registries.append(RegistryEntry(worker_id, timestamp, "entry", worker.compensation, 0))
        else:
            if len(worker.promotions) > 0:
                last_promotion = worker.promotions[-1]
                if last_promotion.status == "pending" and timestamp >= last_promotion.start_timestamp:
                    last_promotion.status = "active"
                    worker.position = last_promotion.new_position
                    worker.compensation = last_promotion.new_compensation
                    worker.position_time = 0
            worker_registries.append(RegistryEntry(worker_id, timestamp, "entry", worker.compensation, 0))
        return "registered"

    def get(self, worker_id: str) -> int | None:
        """
        Should return the total time of finished sessions, or `None`.
        """
        worker = self.workers.get(worker_id, None)
        if worker is None:
            return None
        return worker.total_time

    # @@LEVEL 2@@
    def top_n_workers(self, n: int, position: str) -> list[str]:
        """
        Should return ["<worker_id>(<time>)", ...] for the top `n` workers with
        the given current position, by time descending, ties by id ascending.
        """
        workers = []
        for worker_id, worker in self.workers.items():
            if worker.position == position:
                workers.append(worker_id)

        workers.sort(key=lambda w: (-self.workers[w].position_time, w))
        return [f"{w}({self.workers[w].position_time})" for w in workers[:n]]

    # @@LEVEL 3@@
    def promote(self, worker_id: str, new_position: str, new_compensation: int, start_timestamp: int) -> str:
        """
        Should schedule a promotion that becomes active at the worker's first
        entry at or after `start_timestamp`. Returns "success" or
        "invalid_request".
        """
        worker = self.workers.get(worker_id, None)
        if worker is None or (len(worker.promotions) > 0 and worker.promotions[-1].status == "pending"):
            return "invalid_request"
        worker.promotions.append(Promotion(worker_id, start_timestamp, new_position, new_compensation, "pending"))
        return "success"

    def calc_salary(self, worker_id: str, start_timestamp: int, end_timestamp: int) -> int | None:
        """
        Should return the salary for finished sessions overlapping
        [start_timestamp, end_timestamp], or `None` if the worker doesn't exist.
        """
        worker = self.workers.get(worker_id, None)
        if worker is None:
            return None
        total_salary = 0
        for idx, each_registry in enumerate(worker.registry):
            if each_registry.type == "exit":
                entry_timestamp = worker.registry[idx - 1].timestamp
                overlap_start = max(entry_timestamp, start_timestamp)
                overlap_end = min(each_registry.timestamp, end_timestamp)
                if overlap_start < overlap_end:
                    total_salary += (overlap_end - overlap_start) * each_registry.compensation
        return total_salary