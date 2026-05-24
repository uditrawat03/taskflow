import datetime
from .config import DATE_FMT
from .config import PLAN_LIMITS, OVERDUE_THRESHOLD_DAYS
from .errors import ValidationError, TaskNotFoundError
from .core.task import Task
from .core.task_types import RecurringTask
from .core.stats import calculate_stats
from typing import TYPE_CHECKING

from __future__ import annotations
from typing import TYPE_CHECKING

from .errors import ValidationError, TaskNotFoundError
from .core.task       import Task
from .core.task_types import RecurringTask

if TYPE_CHECKING:
    from .repositories.base import TaskRepository


from .env_config import get_settings

settings = get_settings()

if TYPE_CHECKING:
    pass  # no circular-import-only types needed currently


__all__ = [
    "add_task_to_list",
    "remove_task_by_index",
    "remove_task_by_id",
    "mark_task_done",
    "rename_task",
    "find_task_by_id",
    "find_task_index_by_id",
    "get_task_limit",
    "is_at_limit",
    "filter_tasks",
    "search_tasks",
    "get_overdue_tasks",
    "get_summary_stats",
]


# ─ Limit checks ─


def get_task_limit(plan: str | None = None) -> int:
    """Return the task limit for the given plan name."""
    p: str = plan or settings.user_plan
    return PLAN_LIMITS.get(p, PLAN_LIMITS["free"])


def is_at_limit(tasks: list[Task], plan: str | None = None) -> bool:
    """Return True if the task list has reached its plan limit."""
    return len(tasks) >= get_task_limit(plan)

def add_task(
    task: Task,
    repo: "TaskRepository",
    plan: str | None = None,
) -> Task:
    """
    Validate the plan limit and add a task through the repository.

    Args:
        task (Task)          : The task to add.
        repo (TaskRepository): The storage repository.
        plan (str | None)    : Plan name for limit checking.

    Returns:
        Task: The added task.

    Raises:
        ValidationError: If the task limit is reached.
    """
    limit = PLAN_LIMITS.get(plan or settings.user_plan, PLAN_LIMITS["free"])
    if repo.count() >= limit:
        raise ValidationError(
            f"Task limit reached ({limit} tasks on {plan or settings.user_plan} plan).",
            field="tasks", value=repo.count(),
        )
    return repo.add(task)


def add_task_to_list(
    tasks: list[Task],
    task: Task,
    plan: str | None = None,
) -> Task:
    """Append a Task to the list after checking the plan limit."""
    limit: int = get_task_limit(plan)
    if len(tasks) >= limit:
        raise ValidationError(
            f"Task limit reached ({limit} tasks on {plan or settings.user_plan} plan).",
            field="tasks",
            value=len(tasks),
        )
    tasks.append(task)
    return task


def remove_task_by_index(tasks: list[Task], index: int) -> Task:
    """Remove a task at the given 0-based index."""
    if not (0 <= index < len(tasks)):
        raise IndexError(f"Index {index} out of range for {len(tasks)} tasks.")
    return tasks.pop(index)


def remove_task_by_id(tasks: list[Task], task_id: int) -> Task:
    """Remove a task by its ID."""
    index: int = find_task_index_by_id(tasks, task_id)
    return tasks.pop(index)


def mark_task_done(tasks: list[Task], index: int) -> Task:
    """Mark a task as done. Handles RecurringTask reset behaviour."""
    if not (0 <= index < len(tasks)):
        raise IndexError(f"Index {index} out of range.")
    task: Task = tasks[index]
    if isinstance(task, Task) and task.done and not isinstance(task, RecurringTask):
        raise ValidationError(
            f"Task '{task.title}' is already done.", field="done", value=True
        )
    task.mark_done()
    return task


def rename_task(task_id: int, new_title: str, repo: TaskRepository) -> Task:
    """Rename a task and persist through the repository."""
    task = repo.find_by_id(task_id)
    if task is None:
        raise TaskNotFoundError(task_id)
    task.rename(new_title)
    return repo.update(task)


def find_task_by_id(tasks: list[Task], task_id: int) -> Task:
    """Find and return a task by its ID."""
    for task in tasks:
        if task.id == task_id:
            return task
    raise TaskNotFoundError(task_id)


def find_task_index_by_id(tasks: list[Task], task_id: int) -> int:
    """Return the 0-based index of a task by its ID."""
    for i, task in enumerate(tasks):
        if task.id == task_id:
            return i
    raise TaskNotFoundError(task_id)


def filter_tasks(
    tasks: list[Task],
    priority: str | None = None,
    category: str | None = None,
    is_done: bool | None = None,
    overdue_only: bool = False,
    limit: int | None = None,
) -> list[Task]:
    """Apply filters to a task list and return a new filtered list."""
    result: list[Task] = list(tasks)

    if priority is not None:
        result = [t for t in result if t.priority == priority.lower()]
    if category is not None:
        result = [t for t in result if t.category == category.lower()]
    if is_done is True:
        result = [t for t in result if t.done]
    elif is_done is False:
        result = [t for t in result if not t.done]
    if overdue_only:
        result = [t for t in result if t.is_overdue()]
    if limit is not None:
        result = result[:limit]

    return result


def search_tasks(tasks: list[Task], keyword: str) -> list[Task]:
    """Return tasks whose titles contain keyword (case-insensitive)."""
    kw: str = keyword.strip().lower()
    return [t for t in tasks if kw in t.title.lower()]


def get_overdue_tasks(tasks: list[Task]) -> list[Task]:
    """Return all overdue tasks."""
    return [t for t in tasks if t.is_overdue()]


def get_summary_stats(tasks: list[Task]) -> dict[str, int | float]:
    """Return summary statistics for the task list."""
    return calculate_stats(tasks)


# ─ Private helpers


def _attr(task, key: str, default=""):
    if isinstance(task, Task):
        return getattr(task, key, default)
    return task.get(key, default)


def _is_done(task) -> bool:
    if isinstance(task, Task):
        return task.done
    return task.get("done", False)


def _is_overdue(task) -> bool:
    if isinstance(task, Task):
        return task.is_overdue()
    created = task.get("created_at", "")
    if not created or _is_done(task):
        return False
    try:
        age = (
            datetime.datetime.now() - datetime.datetime.strptime(created, DATE_FMT)
        ).days
        return age >= OVERDUE_THRESHOLD_DAYS
    except ValueError:
        return False

def remove_task(task_id: int, repo: TaskRepository) -> Task:
    """Remove a task by ID through the repository."""
    return repo.delete(task_id)


def mark_done(task_id: int, repo: TaskRepository) -> Task:
    """Mark a task as done and persist through the repository."""
    task = repo.find_by_id(task_id)
    if task is None:
        raise TaskNotFoundError(task_id)
    if isinstance(task, Task) and task.done and not isinstance(task, RecurringTask):
        raise ValidationError(f"Task {task_id} is already done.", field="done")
    task.mark_done()
    return repo.update(task)



