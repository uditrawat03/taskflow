# taskflow/filters.py
# TaskFlow AI — Composable task filtering pipeline.
#
# Uses a fluent (method-chaining) interface so filters can be
# composed declaratively:
#
#   results = (TaskFilter(tasks)
#              .pending()
#              .by_priority("high")
#              .due_within(days=7)
#              .sort_by("priority")
#              .limit(5)
#              .get())
#
# Version history:
#   Day 16 — initial implementation

import re as re_module
import datetime
from typing import Callable

from .core.task import Task
from .config import DATE_FMT

__all__ = ["TaskFilter"]


class TaskFilter:
    """
    A chainable task filter and sort pipeline.

    Operates on a copy of the input list — the original is never mutated.
    Filters are applied eagerly at each step.

    Usage:
        results = TaskFilter(tasks).pending().by_priority("high").get()
    """

    def __init__(self, tasks: list):
        """
        Initialise with a task list.

        Args:
            tasks (list): Task objects or dicts. Copied on entry.
        """
        self._tasks: list = list(tasks)

    # ── Status ────────────────────────────────────────────

    def pending(self) -> "TaskFilter":
        """Keep only pending (not done) tasks."""
        self._tasks = [t for t in self._tasks if not _is_done(t)]
        return self

    def done(self) -> "TaskFilter":
        """Keep only completed tasks."""
        self._tasks = [t for t in self._tasks if _is_done(t)]
        return self

    def overdue(self, threshold_days: int = 7) -> "TaskFilter":
        """Keep only overdue tasks."""
        self._tasks = [
            t for t in self._tasks if not _is_done(t) and _is_overdue(t, threshold_days)
        ]
        return self

    # ── Attribute ─────────────────────────────────────────

    def by_priority(self, priority: str) -> "TaskFilter":
        """Keep tasks matching the given priority."""
        p = priority.strip().lower()
        self._tasks = [t for t in self._tasks if _get_attr(t, "priority") == p]
        return self

    def by_category(self, category: str) -> "TaskFilter":
        """Keep tasks matching the given category."""
        c = category.strip().lower()
        self._tasks = [t for t in self._tasks if _get_attr(t, "category") == c]
        return self

    def by_type(self, task_type: type) -> "TaskFilter":
        """Keep Task objects that are instances of task_type."""
        self._tasks = [t for t in self._tasks if isinstance(t, task_type)]
        return self

    # ── Text ──────────────────────────────────────────────

    def search(self, keyword: str) -> "TaskFilter":
        """Keep tasks whose title contains keyword (case-insensitive)."""
        kw = keyword.strip().lower()
        self._tasks = [
            t for t in self._tasks if kw in _get_attr(t, "title", "").lower()
        ]
        return self

    def search_regex(
        self, pattern: str, flags: int = re_module.IGNORECASE
    ) -> "TaskFilter":
        """
        Keep tasks whose title matches a regex pattern.

        Raises:
            ValueError: If pattern is invalid regex.
        """
        try:
            compiled = re_module.compile(pattern, flags)
        except re_module.error as e:
            raise ValueError(f"Invalid regex '{pattern}': {e}")
        self._tasks = [
            t for t in self._tasks if compiled.search(_get_attr(t, "title", ""))
        ]
        return self

    # ── Date ──────────────────────────────────────────────

    def due_within(self, days: int) -> "TaskFilter":
        """Keep DeadlineTask instances due within the given days."""
        from .core.task_types import DeadlineTask

        self._tasks = [
            t
            for t in self._tasks
            if isinstance(t, DeadlineTask) and 0 <= t.days_until_due <= days
        ]
        return self

    def created_within(self, days: int) -> "TaskFilter":
        """Keep tasks created within the last N days."""
        self._tasks = [t for t in self._tasks if _age_days(t) <= days]
        return self

    # ── Custom ────────────────────────────────────────────

    def where(self, predicate: Callable) -> "TaskFilter":
        """
        Apply a custom filter predicate.

        Args:
            predicate: Callable that takes a task and returns bool.

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
            key     (str) : One of: 'priority', 'title', 'category',
                            'id', 'created_at', 'priority_score'.
            reverse (bool): Descending order if True.

        Raises:
            ValueError: If key is not recognised.
        """
        sort_keys: dict[str, Callable] = {
            "priority": lambda t: -(_priority_score(t)),
            "priority_score": lambda t: _priority_score(t),
            "title": lambda t: _get_attr(t, "title", "").lower(),
            "category": lambda t: _get_attr(t, "category", ""),
            "id": lambda t: _get_attr(t, "id", 0),
            "created_at": lambda t: _get_attr(t, "created_at", ""),
        }
        if key not in sort_keys:
            raise ValueError(
                f"Unknown sort key '{key}'. Choose from: {', '.join(sort_keys)}"
            )
        self._tasks = sorted(self._tasks, key=sort_keys[key], reverse=reverse)
        return self

    # ── Paging ────────────────────────────────────────────

    def limit(self, n: int) -> "TaskFilter":
        """Keep only the first N tasks."""
        self._tasks = self._tasks[:n]
        return self

    def offset(self, n: int) -> "TaskFilter":
        """Skip the first N tasks."""
        self._tasks = self._tasks[n:]
        return self

    # ── Terminal operations ───────────────────────────────

    def get(self) -> list:
        """Return the filtered task list."""
        return list(self._tasks)

    def first(self):
        """Return the first task, or None."""
        return self._tasks[0] if self._tasks else None

    def count(self) -> int:
        """Return the number of tasks after filtering."""
        return len(self._tasks)

    def titles(self) -> list[str]:
        """Return task titles as a list."""
        return [_get_attr(t, "title", "") for t in self._tasks]

    def ids(self) -> list[int]:
        """Return task IDs as a list."""
        return [_get_attr(t, "id", 0) for t in self._tasks]

    def id_map(self) -> dict:
        """Return {task_id: task} dict for O(1) lookup."""
        return {_get_attr(t, "id", 0): t for t in self._tasks}

    def priority_summary(self) -> dict[str, int]:
        """Count tasks per priority level."""
        return {
            p: sum(1 for t in self._tasks if _get_attr(t, "priority") == p)
            for p in ["high", "medium", "low"]
        }

    def any_overdue(self) -> bool:
        """Return True if any task in the current set is overdue."""
        return any(_is_overdue(t) for t in self._tasks)

    def all_done(self) -> bool:
        """Return True if every task in the current set is done."""
        return all(_is_done(t) for t in self._tasks)

    def __len__(self) -> int:
        return len(self._tasks)

    def __bool__(self) -> bool:
        return bool(self._tasks)

    def __repr__(self) -> str:
        return f"TaskFilter({len(self._tasks)} tasks)"


# ─── Internal helpers — support Task objects and dicts ────


def _get_attr(task, key: str, default=""):
    if isinstance(task, Task):
        return getattr(task, key, default)
    return task.get(key, default)


def _is_done(task) -> bool:
    if isinstance(task, Task):
        return task.done
    return task.get("done", False)


def _is_overdue(task, threshold_days: int = 7) -> bool:
    if isinstance(task, Task):
        return task.is_overdue(threshold_days)
    # Dict fallback: age-based check
    created = task.get("created_at", "")
    if not created or _is_done(task):
        return False
    try:
        age = (
            datetime.datetime.now() - datetime.datetime.strptime(created, DATE_FMT)
        ).days
        return age >= threshold_days
    except ValueError:
        return False


def _age_days(task) -> int:
    if isinstance(task, Task):
        return task.age_days()
    created = task.get("created_at", "")
    if not created:
        return 0
    try:
        return (
            datetime.datetime.now() - datetime.datetime.strptime(created, DATE_FMT)
        ).days
    except ValueError:
        return 0


def _priority_score(task) -> int:
    if isinstance(task, Task):
        return task.priority_score
    return {"high": 3, "medium": 2, "low": 1}.get(task.get("priority", "medium"), 0)
