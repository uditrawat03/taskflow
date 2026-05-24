from __future__ import annotations
from abc import ABC, abstractmethod
from taskflow.core.task import Task

__all__ = ["TaskRepository"]


class TaskRepository(ABC):
    """
    Abstract base class defining the storage interface for tasks.

    All concrete implementations must provide these methods.
    Business logic (services.py, commands.py) should only interact
    with this interface — never with concrete implementations directly.
    """

    @abstractmethod
    def find_all(self) -> list[Task]:
        """
        Return all stored tasks.

        Returns:
            list[Task]: All tasks, in storage order. Empty list if none.
        """
        ...

    @abstractmethod
    def find_by_id(self, task_id: int) -> Task | None:
        """
        Return the task with the given ID, or None if not found.

        Args:
            task_id (int): The unique task identifier.

        Returns:
            Task | None: The matching task, or None.
        """
        ...

    @abstractmethod
    def find_by_priority(self, priority: str) -> list[Task]:
        """
        Return all tasks with the given priority.

        Args:
            priority (str): One of 'high', 'medium', 'low'.

        Returns:
            list[Task]: Matching tasks.
        """
        ...

    @abstractmethod
    def save_all(self, tasks: list[Task]) -> None:
        """
        Persist the complete task list.

        Replaces the entire stored collection with the provided list.

        Args:
            tasks (list[Task]): The complete current task list.

        Raises:
            StorageError: If persistence fails.
        """
        ...

    @abstractmethod
    def add(self, task: Task) -> Task:
        """
        Add a single new task and persist it.

        Args:
            task (Task): The task to add.

        Returns:
            Task: The added task (same object).

        Raises:
            StorageError: If persistence fails.
        """
        ...

    @abstractmethod
    def update(self, task: Task) -> Task:
        """
        Update an existing task and persist the change.

        Args:
            task (Task): The task with updated fields (matched by task.id).

        Returns:
            Task: The updated task.

        Raises:
            TaskNotFoundError: If no task with task.id exists.
            StorageError: If persistence fails.
        """
        ...

    @abstractmethod
    def delete(self, task_id: int) -> Task:
        """
        Remove the task with the given ID and persist the change.

        Args:
            task_id (int): The ID of the task to remove.

        Returns:
            Task: The removed task.

        Raises:
            TaskNotFoundError: If no task with that ID exists.
            StorageError: If persistence fails.
        """
        ...

    @abstractmethod
    def count(self) -> int:
        """
        Return the total number of stored tasks.

        Returns:
            int: Task count.
        """
        ...

    @abstractmethod
    def exists(self, task_id: int) -> bool:
        """
        Return True if a task with the given ID exists.

        Args:
            task_id (int): Task ID to check.

        Returns:
            bool: True if found.
        """
        ...

    # ── Concrete helpers built on abstract methods ────────
    # Subclasses inherit these — they do not need to override them.

    def find_pending(self) -> list[Task]:
        """Return all tasks that are not yet done."""
        return [t for t in self.find_all() if not t.done]

    def find_done(self) -> list[Task]:
        """Return all completed tasks."""
        return [t for t in self.find_all() if t.done]

    def find_overdue(self, threshold_days: int = 7) -> list[Task]:
        """Return all overdue pending tasks."""
        return [t for t in self.find_all() if t.is_overdue(threshold_days)]