from __future__ import annotations
import datetime, logging
from typing import TYPE_CHECKING

from taskflow.env_config import get_settings
from .config import PLAN_LIMITS, OVERDUE_THRESHOLD_DAYS, DATE_FMT
from .errors import ValidationError, TaskNotFoundError
from .core.task       import Task
from .core.task_types import RecurringTask
from .core.stats      import calculate_stats

if TYPE_CHECKING:
    from .repositories.base import TaskRepository

logger = logging.getLogger(__name__)
__all__ = [
    "get_task_limit","is_at_limit",
    "add_task_to_list","remove_task_by_index","remove_task_by_id",
    "mark_task_done","rename_task",
    "find_task_by_id","find_task_index_by_id",
    "filter_tasks","search_tasks","get_overdue_tasks","get_summary_stats",
    "add_task","remove_task","mark_done","rename_task_by_id",
]

settings = get_settings()


#  Limit helpers 

def get_task_limit(plan: str | None = None) -> int:
    return PLAN_LIMITS.get(plan or settings.user_plan, PLAN_LIMITS["free"])

def is_at_limit(tasks: list, plan: str | None = None) -> bool:
    return len(tasks) >= get_task_limit(plan)


#  List-based operations (used before repo pattern) ─

def add_task_to_list(tasks: list[Task], task: Task, plan: str | None = None) -> Task:
    limit = get_task_limit(plan)
    if len(tasks) >= limit:
        raise ValidationError(f"Task limit reached ({limit} tasks on {plan or settings.user_plan} plan).",
                               field="tasks", value=len(tasks))
    tasks.append(task)
    return task

def remove_task_by_index(tasks: list[Task], index: int) -> Task:
    if not (0 <= index < len(tasks)):
        raise IndexError(f"Index {index} out of range for {len(tasks)} tasks.")
    return tasks.pop(index)

def remove_task_by_id(tasks: list[Task], task_id: int) -> Task:
    return tasks.pop(find_task_index_by_id(tasks, task_id))

def mark_task_done(tasks: list[Task], index: int) -> Task:
    if not (0 <= index < len(tasks)):
        raise IndexError(f"Index {index} out of range.")
    task = tasks[index]
    if isinstance(task, Task) and task.done and not isinstance(task, RecurringTask):
        raise ValidationError(f"Task '{task.title}' is already done.", field="done", value=True)
    task.mark_done()
    return task

def rename_task(tasks: list[Task], index: int, new_title: str) -> Task:
    if not (0 <= index < len(tasks)):
        raise IndexError(f"Index {index} out of range.")
    new_title = new_title.strip()
    if not new_title:
        raise ValidationError("Title cannot be empty.", field="title", value=new_title)
    if len(new_title) > 200:
        raise ValidationError("Title too long.", field="title", value=len(new_title))
    task = tasks[index]
    if isinstance(task, Task): task.rename(new_title)
    else:                      task["title"] = new_title
    return task

def find_task_by_id(tasks: list[Task], task_id: int) -> Task:
    for t in tasks:
        tid = t.id if isinstance(t, Task) else t.get("id")
        if tid == task_id: return t
    raise TaskNotFoundError(task_id)

def find_task_index_by_id(tasks: list[Task], task_id: int) -> int:
    for i, t in enumerate(tasks):
        tid = t.id if isinstance(t, Task) else t.get("id")
        if tid == task_id: return i
    raise TaskNotFoundError(task_id)

def filter_tasks(tasks: list[Task], priority: str | None = None, category: str | None = None,
                 is_done: bool | None = None, overdue_only: bool = False,
                 limit: int | None = None) -> list[Task]:
    result = list(tasks)
    if priority is not None:  result = [t for t in result if _attr(t,"priority") == priority.lower()]
    if category is not None:  result = [t for t in result if _attr(t,"category") == category.lower()]
    if is_done is True:       result = [t for t in result if _done(t)]
    elif is_done is False:    result = [t for t in result if not _done(t)]
    if overdue_only:          result = [t for t in result if _overdue(t)]
    if limit is not None:     result = result[:limit]
    return result

def search_tasks(tasks: list[Task], keyword: str) -> list[Task]:
    kw = keyword.strip().lower()
    return [t for t in tasks if kw in _attr(t,"title","").lower()]

def get_overdue_tasks(tasks: list[Task]) -> list[Task]:
    return [t for t in tasks if _overdue(t)]

def get_summary_stats(tasks: list[Task]) -> dict:
    return calculate_stats(tasks)


#  Repository-based operations (Day 28+) ─

def add_task(task: Task, repo: "TaskRepository", plan: str | None = None) -> Task:
    limit = PLAN_LIMITS.get(plan or settings.user_plan, PLAN_LIMITS["free"])
    if repo.count() >= limit:
        raise ValidationError(f"Task limit reached ({limit}).", field="tasks", value=repo.count())
    return repo.add(task)

def remove_task(task_id: int, repo: "TaskRepository") -> Task:
    return repo.delete(task_id)

def mark_done(task_id: int, repo: "TaskRepository") -> Task:
    task = repo.find_by_id(task_id)
    if task is None: raise TaskNotFoundError(task_id)
    if isinstance(task, Task) and task.done and not isinstance(task, RecurringTask):
        raise ValidationError(f"Task {task_id} is already done.", field="done")
    task.mark_done()
    return repo.update(task)

def rename_task_by_id(task_id: int, new_title: str, repo: "TaskRepository") -> Task:
    task = repo.find_by_id(task_id)
    if task is None: raise TaskNotFoundError(task_id)
    task.rename(new_title)
    return repo.update(task)


#  Private helpers 

def _attr(task, key: str, default=""):
    return getattr(task, key, default) if isinstance(task, Task) else task.get(key, default)

def _done(task) -> bool:
    return task.done if isinstance(task, Task) else task.get("done", False)

def _overdue(task) -> bool:
    if isinstance(task, Task): return task.is_overdue()
    created = task.get("created_at", "")
    if not created or _done(task): return False
    try:
        age = (datetime.datetime.now() - datetime.datetime.strptime(created, DATE_FMT)).days
        return age >= OVERDUE_THRESHOLD_DAYS
    except ValueError:
        return False