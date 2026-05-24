# Pluggable sort and filter strategies. Day 29.
from __future__ import annotations
from abc import ABC, abstractmethod
from .core.task import Task

__all__ = ["SortStrategy","SortByPriority","SortByTitle","SortByCategory",
           "SortByAge","SortByDueDate","CompositeSort"]


class SortStrategy(ABC):
    @abstractmethod
    def sort(self, tasks: list[Task]) -> list[Task]: ...
    def __call__(self, tasks: list[Task]) -> list[Task]:
        return self.sort(tasks)


class SortByPriority(SortStrategy):
    def __init__(self, reverse: bool = False) -> None:
        self._reverse = reverse
    def sort(self, tasks: list[Task]) -> list[Task]:
        return sorted(tasks, key=lambda t: (-t.priority_score, t.id), reverse=self._reverse)


class SortByTitle(SortStrategy):
    def __init__(self, reverse: bool = False) -> None:
        self._reverse = reverse
    def sort(self, tasks: list[Task]) -> list[Task]:
        return sorted(tasks, key=lambda t: t.title.lower(), reverse=self._reverse)


class SortByCategory(SortStrategy):
    def sort(self, tasks: list[Task]) -> list[Task]:
        return sorted(tasks, key=lambda t: (t.category, -t.priority_score))


class SortByAge(SortStrategy):
    def __init__(self, newest_first: bool = False) -> None:
        self._reverse = newest_first
    def sort(self, tasks: list[Task]) -> list[Task]:
        return sorted(tasks, key=lambda t: t.created_at, reverse=self._reverse)


class SortByDueDate(SortStrategy):
    def sort(self, tasks: list[Task]) -> list[Task]:
        from .core.task_types import DeadlineTask
        deadline = sorted([t for t in tasks if isinstance(t, DeadlineTask)],
                          key=lambda t: t.due_date)
        other    = [t for t in tasks if not isinstance(t, DeadlineTask)]
        return deadline + other


class CompositeSort(SortStrategy):
    def __init__(self, strategies: list[SortStrategy]) -> None:
        self._strategies = strategies
    def sort(self, tasks: list[Task]) -> list[Task]:
        result = list(tasks)
        for strategy in reversed(self._strategies):
            result = strategy.sort(result)
        return result
