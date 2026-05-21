# taskflow/__init__.py
# TaskFlow AI — Package entry point and public API.
#
# Import from here for the cleanest interface:
#   from taskflow import Task, add_task, load_tasks
#
# Version history:
#   Day 11 — package structure created
#   Day 12 — Task class added
#   Day 13 — Task subclasses added
#   Day 15 — version bumped to 1.0.0
#   Day 18 — version bumped to 1.1.0

from .config import APP_NAME, VERSION, USER_NAME
from .errors import (
    TaskFlowError,
    StorageError,
    ValidationError,
    TaskNotFoundError,
    WeatherError,
)
from .core.task import Task
from .core.task_types import UrgentTask, RecurringTask, DeadlineTask
from .core.task_factory import task_from_dict
from .core.stats import calculate_stats
from .storage.json_store import load_tasks, save_tasks
from .display.commands import (
    cmd_add,
    cmd_view,
    cmd_done,
    cmd_remove,
    cmd_filter,
    cmd_search,
    cmd_stats,
    cmd_quit,
)

__version__ = VERSION
__author__ = "Udit Rawat"

__all__ = [
    # Meta
    "__version__",
    "__author__",
    "APP_NAME",
    "VERSION",
    "USER_NAME",
    # Errors
    "TaskFlowError",
    "StorageError",
    "ValidationError",
    "TaskNotFoundError",
    "WeatherError",
    # Models
    "Task",
    "UrgentTask",
    "RecurringTask",
    "DeadlineTask",
    "task_from_dict",
    # Business logic
    "calculate_stats",
    # Storage
    "load_tasks",
    "save_tasks",
    # Commands
    "cmd_add",
    "cmd_view",
    "cmd_done",
    "cmd_remove",
    "cmd_filter",
    "cmd_search",
    "cmd_stats",
    "cmd_quit",
]
