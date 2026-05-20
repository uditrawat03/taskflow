"""
Core task operations — add, remove, update, filter, search.
All functions are pure (return values) or clearly side-effecting (mutate list).
"""

import datetime
from ..config import VALID_PRIORITIES, VALID_CATEGORIES, DATE_FMT
from ..errors import ValidationError, TaskNotFoundError

__all__ = [
    "make_task",
    "add_task",
    "remove_task",
    "mark_task_done",
    "find_task_by_id",
    "get_all_tasks",
    "get_pending_tasks",
    "get_done_tasks",
    "get_tasks_by_priority",
    "get_tasks_by_category",
    "search_tasks",
    "get_next_id",
]


def make_task(task_id: int, title: str, priority: str, category: str) -> dict:
    """Create and return a validated task dictionary."""
    title = title.strip()
    priority = priority.strip().lower()
    category = category.strip().lower()

    if not title:
        raise ValidationError("Title cannot be empty", field="title", value=title)
    if len(title) > 200:
        raise ValidationError(
            "Title too long (max 200 chars)", field="title", value=len(title)
        )
    if priority not in VALID_PRIORITIES:
        raise ValidationError(f"Invalid priority", field="priority", value=priority)
    if category not in VALID_CATEGORIES:
        raise ValidationError(f"Invalid category", field="category", value=category)

    return {
        "id": task_id,
        "title": title,
        "priority": priority,
        "category": category,
        "status": "pending",
        "done": False,
        "created_at": datetime.datetime.now().strftime(DATE_FMT),
    }


def get_next_id(tasks: list) -> int:
    """Return the next available task ID."""
    return max((t["id"] for t in tasks), default=0) + 1


def find_task_by_id(tasks: list, task_id: int) -> dict:
    """
    Find a task by its ID.

    Raises:
        TaskNotFoundError: If no task with the given ID exists.
    """
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise TaskNotFoundError(task_id)


def add_task(tasks: list, title: str, priority: str, category: str) -> dict:
    """
    Create a new task and append it to the task list.

    Returns:
        dict: The newly created task.
    """
    task_id = get_next_id(tasks)
    task = make_task(task_id, title, priority, category)
    tasks.append(task)
    return task


def remove_task(tasks: list, index: int) -> dict:
    """
    Remove a task at the given 0-based index.

    Returns:
        dict: The removed task.
    """
    if not (0 <= index < len(tasks)):
        raise IndexError(f"Index {index} out of range for {len(tasks)} tasks")
    return tasks.pop(index)


def mark_task_done(tasks: list, index: int) -> dict:
    """
    Mark the task at the given index as done.

    Returns:
        dict: The updated task.
    """
    if not (0 <= index < len(tasks)):
        raise IndexError(f"Index {index} out of range")
    tasks[index]["done"] = True
    tasks[index]["status"] = "done"
    return tasks[index]


def get_all_tasks(tasks: list) -> list:
    """Return a copy of all tasks."""
    return list(tasks)


def get_pending_tasks(tasks: list) -> list:
    """Return tasks that are not yet done."""
    return [t for t in tasks if not t["done"]]


def get_done_tasks(tasks: list) -> list:
    """Return completed tasks."""
    return [t for t in tasks if t["done"]]


def get_tasks_by_priority(tasks: list, priority: str) -> list:
    """Return tasks matching the given priority."""
    return [t for t in tasks if t["priority"] == priority.lower()]


def get_tasks_by_category(tasks: list, category: str) -> list:
    """Return tasks matching the given category."""
    return [t for t in tasks if t["category"] == category.lower()]


def search_tasks(tasks: list, keyword: str) -> list:
    """Return tasks whose titles contain the keyword (case-insensitive)."""
    kw = keyword.strip().lower()
    return [t for t in tasks if kw in t["title"].lower()]
