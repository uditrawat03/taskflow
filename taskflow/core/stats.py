# taskflow/core/stats.py — Pure statistics calculations. Day 11/16.
from __future__ import annotations
from collections import Counter
from .task import Task

__all__ = ["calculate_stats","priority_breakdown","category_breakdown",
           "completion_rate","average_title_length","most_productive_category"]


def _is_done(t) -> bool:
    return t.done if isinstance(t, Task) else t.get("done", False)

def _get_priority(t) -> str:
    return t.priority if isinstance(t, Task) else t.get("priority","medium")

def _get_category(t) -> str:
    return t.category if isinstance(t, Task) else t.get("category","other")

def _get_title(t) -> str:
    return t.title if isinstance(t, Task) else t.get("title","")


def calculate_stats(tasks: list) -> dict:
    total   = len(tasks)
    done    = sum(1 for t in tasks if _is_done(t))
    pending = total - done
    rate    = round(done / total * 100, 1) if total > 0 else 0.0
    return {"total": total, "done": done, "pending": pending, "rate": rate}

def priority_breakdown(tasks: list) -> dict[str, int]:
    counts = Counter(_get_priority(t) for t in tasks)
    return {p: counts.get(p, 0) for p in ["high","medium","low"]}

def category_breakdown(tasks: list) -> dict[str, int]:
    return dict(Counter(_get_category(t) for t in tasks).most_common())

def completion_rate(tasks: list) -> float:
    if not tasks:
        return 0.0
    return round(sum(1 for t in tasks if _is_done(t)) / len(tasks) * 100, 1)

def average_title_length(tasks: list) -> float:
    if not tasks:
        return 0.0
    return round(sum(len(_get_title(t)) for t in tasks) / len(tasks), 1)

def most_productive_category(tasks: list) -> str | None:
    done = [t for t in tasks if _is_done(t)]
    if not done:
        return None
    return Counter(_get_category(t) for t in done).most_common(1)[0][0]
