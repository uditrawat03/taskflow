# taskflow/filters.py
# TaskFlow AI — Day 16
# Composable task filtering pipeline using comprehensions.
# Uses fluent interface (method chaining) for readable filter composition.

import datetime
import re as re_module
from typing import Callable
from .core.task import Task

__all__ = ["TaskFilter"]


class TaskFilter:
    """
    A chainable task filter pipeline.

    Each method returns self, enabling fluent chaining:

        results = (TaskFilter(tasks)
                   .pending()
                   .by_priority("high")
                   .due_within(days=7)
                   .sort_by("priority")
                   .limit(5)
                   .get())
    """

    def __init__(self, tasks: list[Task]):
        """
        Initialise the filter with a task list.

        Args:
            tasks (list[Task]): The task list to filter. Not modified in place.
        """
        self._tasks: list[Task] = list(tasks)   # work on a copy

    # ── Status filters ────────────────────────────────────

    def pending(self) -> "TaskFilter":
        """Keep only pending (not done) tasks."""
        self._tasks = [t for t in self._tasks if t.is_pending()]
        return self

    def done(self) -> "TaskFilter":
        """Keep only completed tasks."""
        self._tasks = [t for t in self._tasks if t.done]
        return self

    def overdue(self, threshold_days: int = 7) -> "TaskFilter":
        """Keep only overdue tasks."""
        self._tasks = [t for t in self._tasks if t.is_overdue(threshold_days)]
        return self

    # ── Attribute filters ─────────────────────────────────

    def by_priority(self, priority: str) -> "TaskFilter":
        """Keep tasks matching the given priority."""
        p = priority.strip().lower()
        self._tasks = [t for t in self._tasks if t.priority == p]
        return self

    def by_category(self, category: str) -> "TaskFilter":
        """Keep tasks matching the given category."""
        c = category.strip().lower()
        self._tasks = [t for t in self._tasks if t.category == c]
        return self

    def by_type(self, task_type: type) -> "TaskFilter":
        """Keep tasks that are instances of the given type."""
        self._tasks = [t for t in self._tasks if isinstance(t, task_type)]
        return self

    # ── Text filters ──────────────────────────────────────

    def search(self, keyword: str) -> "TaskFilter":
        """Keep tasks whose title contains the keyword (case-insensitive)."""
        kw = keyword.strip().lower()
        self._tasks = [t for t in self._tasks if kw in t.title.lower()]
        return self

    def search_regex(self, pattern: str,
                     flags: int = re_module.IGNORECASE) -> "TaskFilter":
        """
        Keep tasks whose title matches the given regex pattern.

        Args:
            pattern (str): Regex pattern string.
            flags   (int): re flags, default IGNORECASE.

        Raises:
            ValueError: If the pattern is invalid regex.
        """
        try:
            compiled = re_module.compile(pattern, flags)
        except re_module.error as e:
            raise ValueError(f"Invalid regex pattern '{pattern}': {e}")
        self._tasks = [t for t in self._tasks
                       if compiled.search(t.title)]
        return self

    # ── Date filters ──────────────────────────────────────

    def due_within(self, days: int) -> "TaskFilter":
        """Keep DeadlineTask instances due within the given number of days."""
        from .core.task_types import DeadlineTask
        self._tasks = [
            t for t in self._tasks
            if isinstance(t, DeadlineTask)
            and 0 <= t.days_until_due <= days
        ]
        return self

    def created_within(self, days: int) -> "TaskFilter":
        """Keep tasks created within the last N days."""
        self._tasks = [t for t in self._tasks if t.age_days() <= days]
        return self

    # ── Custom filter ─────────────────────────────────────

    def where(self, predicate: Callable[[Task], bool]) -> "TaskFilter":
        """
        Apply a custom filter function.

        Args:
            predicate: A callable that takes a Task and returns bool.

        Example:
            TaskFilter(tasks).where(lambda t: len(t.title) > 20)
        """
        self._tasks = [t for t in self._tasks if predicate(t)]
        return self

    # ── Sorting ───────────────────────────────────────────

    def sort_by(self, key: str, reverse: bool = False) -> "TaskFilter":
        """
        Sort tasks by a named attribute.

        Args:
            key     (str) : Attribute name — 'priority', 'title', 'category',
                            'id', 'created_at', or 'priority_score'.
            reverse (bool): Sort descending if True.
        """
        sort_keys = {
            "priority":       lambda t: -t.priority_score,
            "priority_score": lambda t: t.priority_score,
            "title":          lambda t: t.title.lower(),
            "category":       lambda t: t.category,
            "id":             lambda t: t.id,
            "created_at":     lambda t: t.created_at,
        }
        if key not in sort_keys:
            raise ValueError(f"Unknown sort key '{key}'. "
                             f"Choose from: {', '.join(sort_keys)}")
        self._tasks = sorted(self._tasks,
                             key=sort_keys[key], reverse=reverse)
        return self

    # ── Limiting ──────────────────────────────────────────

    def limit(self, n: int) -> "TaskFilter":
        """Keep only the first N tasks."""
        self._tasks = self._tasks[:n]
        return self

    def offset(self, n: int) -> "TaskFilter":
        """Skip the first N tasks."""
        self._tasks = self._tasks[n:]
        return self

    # ── Terminal operations ───────────────────────────────

    def get(self) -> list[Task]:
        """Return the filtered task list."""
        return list(self._tasks)

    def first(self) -> Task | None:
        """Return the first task, or None if empty."""
        return self._tasks[0] if self._tasks else None

    def count(self) -> int:
        """Return the number of tasks after filtering."""
        return len(self._tasks)

    def titles(self) -> list[str]:
        """Return a list of task titles."""
        return [t.title for t in self._tasks]

    def ids(self) -> list[int]:
        """Return a list of task IDs."""
        return [t.id for t in self._tasks]

    def id_map(self) -> dict[int, Task]:
        """Return a dict mapping task ID → Task for O(1) lookup."""
        return {t.id: t for t in self._tasks}

    def priority_summary(self) -> dict[str, int]:
        """Return a count of tasks per priority level."""
        return {p: sum(1 for t in self._tasks if t.priority == p)
                for p in ["high", "medium", "low"]}

    def any_overdue(self) -> bool:
        """Return True if any task in the current set is overdue."""
        return any(t.is_overdue() for t in self._tasks)

    def all_done(self) -> bool:
        """Return True if every task in the current set is done."""
        return all(t.done for t in self._tasks)

    def __len__(self) -> int:
        return len(self._tasks)

    def __bool__(self) -> bool:
        return bool(self._tasks)

    def __repr__(self) -> str:
        return f"TaskFilter({len(self._tasks)} tasks)"