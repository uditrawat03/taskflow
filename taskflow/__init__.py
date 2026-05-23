from .config import VERSION
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
