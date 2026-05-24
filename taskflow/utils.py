# taskflow/utils.py — Shared utility helpers. Day 21.
from __future__ import annotations
import datetime
from .config  import DATE_FMT
from .core.task import Task

__all__ = ["task_attr","task_is_done","task_age_days","pluralise","truncate"]


def task_attr(task, key: str, default=""):
    """Get an attribute from a Task object or a dict."""
    return getattr(task, key, default) if isinstance(task, Task) else task.get(key, default)


def task_is_done(task) -> bool:
    """Return done status from a Task object or a dict."""
    return task.done if isinstance(task, Task) else task.get("done", False)


def task_age_days(task) -> int:
    """Return how many days ago the task was created."""
    if isinstance(task, Task):
        return task.age_days()
    created = task.get("created_at", "")
    if not created:
        return 0
    try:
        return (datetime.datetime.now() - datetime.datetime.strptime(created, DATE_FMT)).days
    except ValueError:
        return 0


def pluralise(count: int, singular: str, plural: str | None = None) -> str:
    """Return '1 task' or '3 tasks' based on count."""
    word = singular if count == 1 else (plural or singular + "s")
    return f"{count} {word}"


def truncate(text: str, max_length: int, suffix: str = "..") -> str:
    """Truncate text to max_length characters, appending suffix if needed."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix
