from __future__ import annotations

import json

from task_manager import TaskManager


class Task:
    def __init__(self, task_id: str, seq: int, name: str, priority: int):
        self.id = task_id
        self.seq = seq                  # creation order; never sort by the id string ("task_id_10" < "task_id_2")
        self.name = name
        self.priority = priority


class Assignment:
    def __init__(self, task_id: str, start: int, finish: int, seq: int):
        self.task_id = task_id
        self.start = start
        self.finish = finish
        self.seq = seq                  # assignment order
        self.completed_at: int | None = None

    def active(self, t: int) -> bool:
        return self.completed_at is None and self.start <= t < self.finish

    def overdue(self, t: int) -> bool:
        return self.completed_at is None and self.finish <= t


class User:
    def __init__(self, user_id: str, quota: int):
        self.id = user_id
        self.quota = quota
        self.assignments: list[Assignment] = []


class TaskManagerImpl(TaskManager):

    def __init__(self):
        self.tasks: dict[str, Task] = {}
        self.users: dict[str, User] = {}
        self.task_count = 0
        self.assign_count = 0

    def _ordered(self, tasks) -> list[str]:
        return [t.id for t in sorted(tasks, key=lambda t: (-t.priority, t.seq))]

    # ---- Level 1 ---------------------------------------------------------------
    def add_task(self, timestamp: int, name: str, priority: int) -> str:
        self.task_count += 1
        task_id = f"task_id_{self.task_count}"
        self.tasks[task_id] = Task(task_id, self.task_count, name, priority)
        return task_id

    def update_task(self, timestamp: int, task_id: str, name: str, priority: int) -> bool:
        task = self.tasks.get(task_id)
        if task is None:
            return False
        task.name, task.priority = name, priority
        return True

    def get_task(self, timestamp: int, task_id: str) -> str | None:
        task = self.tasks.get(task_id)
        if task is None:
            return None
        return json.dumps({"name": task.name, "priority": task.priority})

    # ---- Level 2 ---------------------------------------------------------------
    def search_tasks(self, timestamp: int, name_filter: str, max_results: int) -> list[str]:
        if max_results <= 0:
            return []
        return self._ordered(t for t in self.tasks.values() if name_filter in t.name)[:max_results]

    def list_tasks_sorted(self, timestamp: int, limit: int) -> list[str]:
        return self._ordered(self.tasks.values())[:max(limit, 0)]

    # ---- Level 3 ---------------------------------------------------------------
    def add_user(self, timestamp: int, user_id: str, quota: int) -> bool:
        if user_id in self.users:
            return False
        self.users[user_id] = User(user_id, quota)
        return True

    def assign_task(self, timestamp: int, task_id: str, user_id: str, finish_time: int) -> bool:
        user = self.users.get(user_id)
        if user is None or task_id not in self.tasks:
            return False
        if sum(a.active(timestamp) for a in user.assignments) >= user.quota:
            return False
        self.assign_count += 1
        user.assignments.append(Assignment(task_id, timestamp, finish_time, self.assign_count))
        return True

    def get_user_tasks(self, timestamp: int, user_id: str) -> list[str]:
        user = self.users.get(user_id)
        if user is None:
            return []
        active = sorted((a for a in user.assignments if a.active(timestamp)), key=lambda a: (a.finish, a.seq))
        return [a.task_id for a in active]

    # ---- Level 4 ---------------------------------------------------------------
    def complete_task(self, timestamp: int, task_id: str, user_id: str) -> bool:
        user = self.users.get(user_id)
        if user is None:
            return False
        candidates = [a for a in user.assignments if a.task_id == task_id and a.active(timestamp)]
        if not candidates:
            return False
        min(candidates, key=lambda a: (a.finish, a.seq)).completed_at = timestamp
        return True

    def get_overdue_assignments(self, timestamp: int, user_id: str) -> list[str]:
        user = self.users.get(user_id)
        if user is None:
            return []
        overdue = sorted((a for a in user.assignments if a.overdue(timestamp)), key=lambda a: (a.finish, a.seq))
        return [a.task_id for a in overdue]
