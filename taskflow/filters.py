# TaskFilter fluent pipeline. Day 16.
from __future__ import annotations
import re as re_module, datetime
from typing import Callable
from .core.task import Task
from .config    import DATE_FMT

__all__ = ["TaskFilter"]


def _attr(task, key: str, default=""):
    return getattr(task, key, default) if isinstance(task, Task) else task.get(key, default)

def _is_done(task) -> bool:
    return task.done if isinstance(task, Task) else task.get("done", False)

def _is_overdue(task, threshold_days: int = 7) -> bool:
    if isinstance(task, Task):
        return task.is_overdue(threshold_days)
    created = task.get("created_at", "")
    if not created or _is_done(task):
        return False
    try:
        age = (datetime.datetime.now() - datetime.datetime.strptime(created, DATE_FMT)).days
        return age >= threshold_days
    except ValueError:
        return False

def _priority_score(task) -> int:
    if isinstance(task, Task):
        return task.priority_score
    return {"high": 3, "medium": 2, "low": 1}.get(task.get("priority","medium"), 0)

def _age_days(task) -> int:
    if isinstance(task, Task):
        return task.age_days()
    created = task.get("created_at", "")
    if not created:
        return 0
    try:
        return (datetime.datetime.now() - datetime.datetime.strptime(created, DATE_FMT)).days
    except ValueError:
        return 0


class TaskFilter:
    """Chainable task filter and sort pipeline."""

    def __init__(self, tasks: list) -> None:
        self._tasks: list = list(tasks)

    # ── Status ──
    def pending(self) -> "TaskFilter":
        self._tasks = [t for t in self._tasks if not _is_done(t)]; return self
    def done(self) -> "TaskFilter":
        self._tasks = [t for t in self._tasks if _is_done(t)]; return self
    def overdue(self, threshold_days: int = 7) -> "TaskFilter":
        self._tasks = [t for t in self._tasks if not _is_done(t) and _is_overdue(t, threshold_days)]; return self

    # ── Attribute ──
    def by_priority(self, priority: str) -> "TaskFilter":
        p = priority.strip().lower()
        self._tasks = [t for t in self._tasks if _attr(t, "priority") == p]; return self
    def by_category(self, category: str) -> "TaskFilter":
        c = category.strip().lower()
        self._tasks = [t for t in self._tasks if _attr(t, "category") == c]; return self
    def by_type(self, task_type: type) -> "TaskFilter":
        self._tasks = [t for t in self._tasks if isinstance(t, task_type)]; return self

    # ── Text ──
    def search(self, keyword: str) -> "TaskFilter":
        kw = keyword.strip().lower()
        self._tasks = [t for t in self._tasks if kw in _attr(t,"title","").lower()]; return self
    def search_regex(self, pattern: str, flags: int = re_module.IGNORECASE) -> "TaskFilter":
        try:
            compiled = re_module.compile(pattern, flags)
        except re_module.error as e:
            raise ValueError(f"Invalid regex '{pattern}': {e}")
        self._tasks = [t for t in self._tasks if compiled.search(_attr(t,"title",""))]; return self

    # ── Date ──
    def due_within(self, days: int) -> "TaskFilter":
        from .core.task_types import DeadlineTask
        self._tasks = [t for t in self._tasks
                       if isinstance(t, DeadlineTask) and 0 <= t.days_until_due <= days]; return self
    def created_within(self, days: int) -> "TaskFilter":
        self._tasks = [t for t in self._tasks if _age_days(t) <= days]; return self

    # ── Custom ──
    def where(self, predicate: Callable) -> "TaskFilter":
        self._tasks = [t for t in self._tasks if predicate(t)]; return self

    # ── Sort ──
    def sort_by(self, key: str, reverse: bool = False) -> "TaskFilter":
        sort_keys: dict[str, Callable] = {
            "priority":       lambda t: -(_priority_score(t)),
            "priority_score": lambda t: _priority_score(t),
            "title":          lambda t: _attr(t,"title","").lower(),
            "category":       lambda t: _attr(t,"category",""),
            "id":             lambda t: _attr(t,"id",0),
            "created_at":     lambda t: _attr(t,"created_at",""),
        }
        if key not in sort_keys:
            raise ValueError(f"Unknown sort key '{key}'. Choose from: {', '.join(sort_keys)}")
        self._tasks = sorted(self._tasks, key=sort_keys[key], reverse=reverse); return self

    def sort_with(self, strategy: "SortStrategy") -> "TaskFilter":
        self._tasks = strategy.sort(self._tasks); return self

    # ── Paging ──
    def limit(self, n: int) -> "TaskFilter":
        self._tasks = self._tasks[:n]; return self
    def offset(self, n: int) -> "TaskFilter":
        self._tasks = self._tasks[n:]; return self

    # ── Terminal ──
    def get(self) -> list:       return list(self._tasks)
    def first(self):             return self._tasks[0] if self._tasks else None
    def count(self) -> int:      return len(self._tasks)
    def titles(self) -> list[str]: return [_attr(t,"title","") for t in self._tasks]
    def ids(self) -> list[int]:  return [_attr(t,"id",0) for t in self._tasks]
    def id_map(self) -> dict:    return {_attr(t,"id",0): t for t in self._tasks}
    def any_overdue(self) -> bool: return any(_is_overdue(t) for t in self._tasks)
    def all_done(self) -> bool:  return all(_is_done(t) for t in self._tasks)
    def priority_summary(self) -> dict[str, int]:
        return {p: sum(1 for t in self._tasks if _attr(t,"priority") == p) for p in ["high","medium","low"]}
    def __len__(self) -> int:    return len(self._tasks)
    def __bool__(self) -> bool:  return bool(self._tasks)
    def __repr__(self) -> str:   return f"TaskFilter({len(self._tasks)} tasks)"
