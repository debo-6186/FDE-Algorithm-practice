import json
from interface import TaskManager

class Task:
    def __init__(self, task_id: str, name: str, priority: int, seq: int):
        self.task_id = task_id
        self.name = name
        self.priority = priority
        self.seq = seq

    def __lt__(self, other: "Task") -> bool:
        return (-self.priority, self.seq) < (-other.priority, other.seq)

    def to_json(self) -> str:
        return json.dumps({"name": self.name, "priority": self.priority})

class Assignment:
    def __init__(self, task_id: str, start: int, finish_time: int, seq: int):
        self.task_id = task_id
        self.start = start
        self.finish_time = finish_time
        self.seq = seq
        self.completed = False

    def is_active(self, timestamp: int) -> bool:
        return not self.completed and self.start <= timestamp < self.finish_time

class User:
    def __init__(self, user_id: str, quota: int):
        self.user_id = user_id
        self.quota = quota
        self.assignments: list[Assignment] = []

class TaskManagerImpl(TaskManager):

    def __init__(self):
        self.tasks: dict[str, Task] = {}
        self.seq = 0
        self.users: dict[str, User] = {}
        self.assignment_seq = 0

    def add_task(self, timestamp: int, name: str, priority: int) -> str:
        """
        Should add a task and return its id "task_id_<k>".
        """
        self.seq += 1
        task_id = f"task_id_{self.seq}"
        self.tasks[task_id] = Task(task_id, name, priority, self.seq)
        return task_id

    def update_task(self, timestamp: int, task_id: str, name: str, priority: int) -> bool:
        """
        Should replace the task's name and priority. `False` if it doesn't exist.
        """
        task = self.tasks.get(task_id)
        if task is None:
            return False
        task.name = name
        task.priority = priority
        return True

    def get_task(self, timestamp: int, task_id: str) -> str | None:
        """
        Should return '{"name": "<name>", "priority": <priority>}' or `None`.
        """
        task = self.tasks.get(task_id)
        if task is None:
            return None
        return task.to_json()

    # @@LEVEL 2@@
    def _sorted_tasks(self) -> list[Task]:
        return sorted(self.tasks.values())

    def search_tasks(self, timestamp: int, name_filter: str, max_results: int) -> list[str]:
        """
        Should return ids of tasks whose name contains `name_filter`, by
        priority descending then creation order, at most `max_results`.
        """
        if max_results <= 0:
            return []
        result = []
        for task in self._sorted_tasks():
            if name_filter in task.name:
                result.append(task.task_id)
                if len(result) == max_results:
                    break
        return result

    def list_tasks_sorted(self, timestamp: int, limit: int) -> list[str]:
        """
        Should return ids of all tasks by priority descending then creation
        order, at most `limit`.
        """
        if limit <= 0:
            return []
        return [task.task_id for task in self._sorted_tasks()[:limit]]

    # @@LEVEL 3@@
    def add_user(self, timestamp: int, user_id: str, quota: int) -> bool:
        """
        Should add a user who can hold at most `quota` active assignments.
        """
        if user_id in self.users:
            return False
        self.users[user_id] = User(user_id, quota)
        return True

    def assign_task(self, timestamp: int, task_id: str, user_id: str, finish_time: int) -> bool:
        """
        Should assign the task to the user for [timestamp, finish_time).
        """
        task = self.tasks.get(task_id)
        user = self.users.get(user_id)
        if task is None or user is None:
            return False
        active_count = sum(1 for a in user.assignments if a.is_active(timestamp))
        if active_count >= user.quota:
            return False
        self.assignment_seq += 1
        user.assignments.append(Assignment(task_id, timestamp, finish_time, self.assignment_seq))
        return True

    def get_user_tasks(self, timestamp: int, user_id: str) -> list[str]:
        """
        Should return task ids of the user's active assignments, by
        finish_time then assignment order.
        """
        user = self.users.get(user_id)
        if user is None:
            return []
        active = [a for a in user.assignments if a.is_active(timestamp)]
        active.sort(key=lambda a: (a.finish_time, a.seq))
        return [a.task_id for a in active]

    # @@LEVEL 4@@
    def complete_task(self, timestamp: int, task_id: str, user_id: str) -> bool:
        """
        Should complete the user's active assignment of `task_id`.
        """
        user = self.users.get(user_id)
        if user is None:
            return False
        candidates = [
            a for a in user.assignments if a.task_id == task_id and a.is_active(timestamp)
        ]
        if not candidates:
            return False
        best = min(candidates, key=lambda a: (a.finish_time, a.seq))
        best.completed = True
        return True

    def get_overdue_assignments(self, timestamp: int, user_id: str) -> list[str]:
        """
        Should return task ids of the user's expired, uncompleted assignments,
        by finish_time then assignment order.
        """
        user = self.users.get(user_id)
        if user is None:
            return []
        overdue = [
            a for a in user.assignments if not a.completed and a.finish_time <= timestamp
        ]
        overdue.sort(key=lambda a: (a.finish_time, a.seq))
        return [a.task_id for a in overdue]
    
