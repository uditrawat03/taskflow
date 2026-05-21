# taskflow/core/__init__.py
# Public API for the core subpackage.

from .task import Task
from .task_types import UrgentTask, RecurringTask, DeadlineTask
from .task_factory import task_from_dict
from .stats import (
    calculate_stats,
    priority_breakdown,
    category_breakdown,
    completion_rate,
    average_title_length,
    most_productive_category,
)

__all__ = [
    "Task",
    "UrgentTask",
    "RecurringTask",
    "DeadlineTask",
    "task_from_dict",
    "calculate_stats",
    "priority_breakdown",
    "category_breakdown",
    "completion_rate",
    "average_title_length",
    "most_productive_category",
]
