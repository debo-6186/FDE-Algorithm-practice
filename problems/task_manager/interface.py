from __future__ import annotations

from abc import ABC


class TaskManager(ABC):
    """
    `TaskManager` interface.
    Default implementations return placeholder values; override every method
    in `TaskManagerImpl` (task_manager_impl.py).
    """

# @@LEVEL 1@@
    def add_task(self, timestamp: int, name: str, priority: int) -> str:
        """
        Should add a task and return its id "task_id_<k>".
        """
        # default implementation
        return ""

    def update_task(self, timestamp: int, task_id: str, name: str, priority: int) -> bool:
        """
        Should replace the task's name and priority. `False` if it doesn't exist.
        """
        # default implementation
        return False

    def get_task(self, timestamp: int, task_id: str) -> str | None:
        """
        Should return '{"name": "<name>", "priority": <priority>}' or `None`.
        """
        # default implementation
        return None

# @@LEVEL 2@@
    def search_tasks(self, timestamp: int, name_filter: str, max_results: int) -> list[str]:
        """
        Should return ids of tasks whose name contains `name_filter`, by
        priority descending then creation order, at most `max_results`.
        """
        # default implementation
        return []

    def list_tasks_sorted(self, timestamp: int, limit: int) -> list[str]:
        """
        Should return ids of all tasks by priority descending then creation
        order, at most `limit`.
        """
        # default implementation
        return []

# @@LEVEL 3@@
    def add_user(self, timestamp: int, user_id: str, quota: int) -> bool:
        """
        Should add a user who can hold at most `quota` active assignments.
        """
        # default implementation
        return False

    def assign_task(self, timestamp: int, task_id: str, user_id: str, finish_time: int) -> bool:
        """
        Should assign the task to the user for [timestamp, finish_time).
        """
        # default implementation
        return False

    def get_user_tasks(self, timestamp: int, user_id: str) -> list[str]:
        """
        Should return task ids of the user's active assignments, by
        finish_time then assignment order.
        """
        # default implementation
        return []

# @@LEVEL 4@@
    def complete_task(self, timestamp: int, task_id: str, user_id: str) -> bool:
        """
        Should complete the user's active assignment of `task_id`.
        """
        # default implementation
        return False

    def get_overdue_assignments(self, timestamp: int, user_id: str) -> list[str]:
        """
        Should return task ids of the user's expired, uncompleted assignments,
        by finish_time then assignment order.
        """
        # default implementation
        return []
