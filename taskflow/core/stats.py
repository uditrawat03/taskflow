"""
Task statistics calculations.
All functions are pure — no side effects, no printing.
"""

from collections import Counter
from ..config import VALID_PRIORITIES, VALID_CATEGORIES

__all__ = ["calculate_stats", "priority_breakdown", "category_breakdown"]


def calculate_stats(tasks: list) -> dict:
    """Return a summary statistics dictionary for the task list."""
    total = len(tasks)
    done = sum(1 for t in tasks if t["done"])
    pending = total - done
    rate = round(done / total * 100, 1) if total > 0 else 0.0
    return {
        "total": total,
        "done": done,
        "pending": pending,
        "rate": rate,
    }


def priority_breakdown(tasks: list) -> dict:
    """Return count of tasks per priority level."""
    counts = Counter(t["priority"] for t in tasks)
    return {p: counts.get(p, 0) for p in ["high", "medium", "low"]}


def category_breakdown(tasks: list) -> dict:
    """Return count of tasks per category."""
    counts = Counter(t["category"] for t in tasks)
    return dict(counts.most_common())
