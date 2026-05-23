from collections import Counter
from .task import Task

__all__ = [
    "calculate_stats",
    "priority_breakdown",
    "category_breakdown",
    "completion_rate",
    "average_title_length",
    "most_productive_category",
]


def calculate_stats(tasks: list) -> dict:
    """
    Return a summary statistics dictionary for a task list.

    Args:
        tasks (list): List of Task objects or task dicts.

    Returns:
        dict: Keys — total, done, pending, rate (float 0.0–100.0).
    """
    total = len(tasks)
    done = sum(1 for t in tasks if _is_done(t))
    pending = total - done
    rate = round(done / total * 100, 1) if total > 0 else 0.0
    return {"total": total, "done": done, "pending": pending, "rate": rate}


def priority_breakdown(tasks: list) -> dict[str, int]:
    """
    Count tasks per priority level.

    Returns all three levels even when count is 0.

    Returns:
        dict: {"high": N, "medium": N, "low": N}
    """
    counts = Counter(_get_priority(t) for t in tasks)
    return {p: counts.get(p, 0) for p in ["high", "medium", "low"]}


def category_breakdown(tasks: list) -> dict[str, int]:
    """
    Count tasks per category, sorted by count descending.

    Returns:
        dict: {category: count, ...} ordered most-to-least common.
    """
    counts = Counter(_get_category(t) for t in tasks)
    return dict(counts.most_common())


def completion_rate(tasks: list) -> float:
    """
    Return the percentage of tasks that are done (0.0–100.0).

    Returns:
        float: Completion percentage, 1 decimal place.
    """
    if not tasks:
        return 0.0
    return round(sum(1 for t in tasks if _is_done(t)) / len(tasks) * 100, 1)


def average_title_length(tasks: list) -> float:
    """
    Return the average character length of all task titles.

    Returns:
        float: Average length, 1 decimal place. 0.0 if no tasks.
    """
    if not tasks:
        return 0.0
    return round(sum(len(_get_title(t)) for t in tasks) / len(tasks), 1)


def most_productive_category(tasks: list) -> str | None:
    """
    Return the category with the most completed tasks.

    Returns:
        str | None: Category name, or None if no tasks are done.
    """
    done_tasks = [t for t in tasks if _is_done(t)]
    if not done_tasks:
        return None
    counts = Counter(_get_category(t) for t in done_tasks)
    return counts.most_common(1)[0][0]


# ─ Internal helpers — support both Task objects and dicts ─


def _is_done(task) -> bool:
    if isinstance(task, Task):
        return task.done
    return task.get("done", False)


def _get_priority(task) -> str:
    if isinstance(task, Task):
        return task.priority
    return task.get("priority", "medium")


def _get_category(task) -> str:
    if isinstance(task, Task):
        return task.category
    return task.get("category", "other")


def _get_title(task) -> str:
    if isinstance(task, Task):
        return task.title
    return task.get("title", "")
