# taskflow/core/task_factory.py
"""
TaskFactory — creates the right Task subclass from a dict.
Used during deserialization to restore the original task type.
"""

from .task import Task
from .task_types import UrgentTask, RecurringTask, DeadlineTask


TASK_TYPE_MAP = {
    "urgent": UrgentTask,
    "recurring": RecurringTask,
    "deadline": DeadlineTask,
}


def task_from_dict(data: dict) -> Task:
    """
    Create the appropriate Task subclass from a dictionary.

    Args:
        data (dict): Task data dict, optionally containing a 'type' field.

    Returns:
        Task: An instance of the correct Task subclass.
    """
    task_type = data.get("type", "standard")
    cls = TASK_TYPE_MAP.get(task_type, Task)
    return cls.from_dict(data)
