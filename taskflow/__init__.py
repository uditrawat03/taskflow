# taskflow/__init__.py
"""
TaskFlow AI — Intelligent task management.

Public API — everything a caller needs is available from here.
"""

from .config import APP_NAME, VERSION, USER_NAME
from .errors import TaskFlowError, StorageError, ValidationError, TaskNotFoundError
from .core.tasks import (
    add_task,
    remove_task,
    mark_task_done,
    get_pending_tasks,
    search_tasks,
)
from .core.stats import calculate_stats
from .storage.json_store import load_tasks, save_tasks

__version__ = VERSION
__all__ = [
    "APP_NAME",
    "VERSION",
    "USER_NAME",
    "TaskFlowError",
    "StorageError",
    "ValidationError",
    "TaskNotFoundError",
    "add_task",
    "remove_task",
    "mark_task_done",
    "get_pending_tasks",
    "search_tasks",
    "calculate_stats",
    "load_tasks",
    "save_tasks",
]
