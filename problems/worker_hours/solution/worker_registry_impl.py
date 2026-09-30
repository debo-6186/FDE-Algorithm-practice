from __future__ import annotations

from worker_registry import WorkerRegistry


class Session:
    def __init__(self, start: int, end: int, position: str, compensation: int):
        self.start = start
        self.end = end
        self.position = position
        self.compensation = compensation


class Worker:
    def __init__(self, worker_id: str, position: str, compensation: int):
        self.id = worker_id
        self.position = position
        self.compensation = compensation
        self.position_since = 0                       # when the current position became active
        self.sessions: list[Session] = []             # finished sessions only
        self.entered_at: int | None = None            # set while the worker is in the office
        self.pending: tuple[str, int, int] | None = None   # (position, compensation, start_timestamp)

    def total_time(self) -> int:
        return sum(s.end - s.start for s in self.sessions)

    def time_in_current_position(self) -> int:
        return sum(s.end - s.start for s in self.sessions if s.start >= self.position_since)


def _overlap(a1: int, a2: int, b1: int, b2: int) -> int:
    return max(0, min(a2, b2) - max(a1, b1))


class WorkerRegistryImpl(WorkerRegistry):

    def __init__(self):
        self.workers: dict[str, Worker] = {}
        self.double_periods: list[tuple[int, int]] = []

    # ---- Level 1 ---------------------------------------------------------------
    def add_worker(self, worker_id: str, position: str, compensation: int) -> bool:
        if worker_id in self.workers:
            return False
        self.workers[worker_id] = Worker(worker_id, position, compensation)
        return True

    def register(self, worker_id: str, timestamp: int) -> str:
        w = self.workers.get(worker_id)
        if w is None:
            return "invalid_request"
        if w.entered_at is None:                                  # entering
            if w.pending is not None and timestamp >= w.pending[2]:
                w.position, w.compensation, _ = w.pending         # promotion becomes active now
                w.position_since = timestamp
                w.pending = None
            w.entered_at = timestamp
        else:                                                     # leaving
            w.sessions.append(Session(w.entered_at, timestamp, w.position, w.compensation))
            w.entered_at = None
        return "registered"

    def get(self, worker_id: str) -> int | None:
        w = self.workers.get(worker_id)
        return w.total_time() if w else None

    # ---- Level 2 ---------------------------------------------------------------
    def top_n_workers(self, n: int, position: str) -> list[str]:
        ranked = sorted(
            ((w.time_in_current_position(), w.id) for w in self.workers.values() if w.position == position),
            key=lambda tw: (-tw[0], tw[1]),
        )
        return [f"{wid}({t})" for t, wid in ranked[:n]]

    # ---- Level 3 ---------------------------------------------------------------
    def promote(self, worker_id: str, new_position: str, new_compensation: int, start_timestamp: int) -> str:
        w = self.workers.get(worker_id)
        if w is None or w.pending is not None:
            return "invalid_request"
        w.pending = (new_position, new_compensation, start_timestamp)
        return "success"

    def calc_salary(self, worker_id: str, start_timestamp: int, end_timestamp: int) -> int | None:
        w = self.workers.get(worker_id)
        if w is None:
            return None
        doubles = self._merged_double_periods()
        total = 0
        for s in w.sessions:
            a, b = max(s.start, start_timestamp), min(s.end, end_timestamp)
            if a >= b:
                continue
            extra = sum(_overlap(a, b, x, y) for x, y in doubles)   # double time is paid once more
            total += s.compensation * ((b - a) + extra)
        return total

    # ---- Level 4 ---------------------------------------------------------------
    def set_double_paid(self, start_timestamp: int, end_timestamp: int) -> None:
        self.double_periods.append((start_timestamp, end_timestamp))

    def _merged_double_periods(self) -> list[tuple[int, int]]:
        merged: list[list[int]] = []
        for x, y in sorted(self.double_periods):
            if merged and x <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], y)
            else:
                merged.append([x, y])
        return [(x, y) for x, y in merged]
