import datetime
from .config import DATE_FMT
from .core.task import Task

__all__ = [
    "task_attr",
    "task_is_done",
    "task_age_days",
    "pluralise",
    "truncate",
]


def task_attr(task, key: str, default=""):
    """
    Get an attribute from either a Task object or a plain dict.

    Centralises the isinstance(task, Task) pattern used throughout
    the display and service layers.

    Args:
        task    : Task object or dict.
        key     (str): Attribute / key name.
        default     : Value to return if not found.
    """
    if isinstance(task, Task):
        return getattr(task, key, default)
    return task.get(key, default)


def task_is_done(task) -> bool:
    """Return done status from either a Task object or a dict."""
    if isinstance(task, Task):
        return task.done
    return task.get("done", False)


def task_age_days(task) -> int:
    """Return how many days ago the task was created."""
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


def pluralise(count: int, singular: str, plural: str | None = None) -> str:
    """
    Return the correct singular or plural form based on count.

    Args:
        count    (int)     : The quantity.
        singular (str)     : Singular form, e.g. "task".
        plural   (str|None): Plural form. Defaults to singular + "s".

    Returns:
        str: e.g. "1 task" or "3 tasks"

    Example:
        pluralise(1, "task")   → "1 task"
        pluralise(3, "task")   → "3 tasks"
        pluralise(1, "fish", "fish") → "1 fish"
    """
    word = singular if count == 1 else (plural or singular + "s")
    return f"{count} {word}"


def truncate(text: str, max_length: int, suffix: str = "..") -> str:
    """
    Truncate text to max_length, appending suffix if truncated.

    Args:
        text       (str): Text to truncate.
        max_length (int): Maximum character length including suffix.
        suffix     (str): Characters appended when truncation occurs.

    Returns:
        str: Truncated or original text.

    Example:
        truncate("Review pull request", 15) → "Review pull ..."
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix
