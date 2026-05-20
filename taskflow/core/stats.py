# taskflow/core/stats.py — refactored for Day 16
"""
Task statistics — refactored to use generator expressions for memory efficiency.
All functions remain pure (no side effects).
"""

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


def calculate_stats(tasks: list[Task]) -> dict:
    """Return a summary statistics dictionary."""
    total   = len(tasks)
    done    = sum(1 for t in tasks if t.done)       # generator
    pending = total - done
    rate    = round(done / total * 100, 1) if total > 0 else 0.0
    return {"total": total, "done": done, "pending": pending, "rate": rate}


def priority_breakdown(tasks: list[Task]) -> dict[str, int]:
    """Count tasks per priority level using Counter."""
    counts = Counter(t.priority for t in tasks)     # generator in Counter
    return {p: counts.get(p, 0) for p in ["high", "medium", "low"]}


def category_breakdown(tasks: list[Task]) -> dict[str, int]:
    """Count tasks per category, sorted by count descending."""
    counts = Counter(t.category for t in tasks)
    return dict(counts.most_common())


def completion_rate(tasks: list[Task]) -> float:
    """Return completion percentage as a float 0.0–100.0."""
    if not tasks:
        return 0.0
    return round(sum(1 for t in tasks if t.done) / len(tasks) * 100, 1)


def average_title_length(tasks: list[Task]) -> float:
    """Return the average character length of task titles."""
    if not tasks:
        return 0.0
    return round(sum(len(t.title) for t in tasks) / len(tasks), 1)


def most_productive_category(tasks: list[Task]) -> str | None:
    """Return the category with the most completed tasks."""
    done_tasks = [t for t in tasks if t.done]
    if not done_tasks:
        return None
    counts = Counter(t.category for t in done_tasks)
    return counts.most_common(1)[0][0]