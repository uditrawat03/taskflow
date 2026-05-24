# Abstract Task Repository. Day 28.
from __future__ import annotations
from abc import ABC, abstractmethod
from ..core.task import Task

__all__ = ["TaskRepository"]


class TaskRepository(ABC):
    """Abstract interface for all task storage backends."""

    @abstractmethod
    def find_all(self) -> list[Task]: ...

    @abstractmethod
    def find_by_id(self, task_id: int) -> Task | None: ...

    @abstractmethod
    def find_by_priority(self, priority: str) -> list[Task]: ...

    @abstractmethod
    def save_all(self, tasks: list[Task]) -> None: ...

    @abstractmethod
    def add(self, task: Task) -> Task: ...

    @abstractmethod
    def update(self, task: Task) -> Task: ...

    @abstractmethod
    def delete(self, task_id: int) -> Task: ...

    @abstractmethod
    def count(self) -> int: ...

    @abstractmethod
    def exists(self, task_id: int) -> bool: ...

    # Concrete helpers built on abstract methods
    def find_pending(self) -> list[Task]:
        return [t for t in self.find_all() if not t.done]

    def find_done(self) -> list[Task]:
        return [t for t in self.find_all() if t.done]

    def find_overdue(self, threshold_days: int = 7) -> list[Task]:
        return [t for t in self.find_all() if t.is_overdue(threshold_days)]
