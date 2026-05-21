# taskflow/core/task_factory.py
# TaskFlow AI — Polymorphic task deserialisation.
# Creates the correct Task subclass from a stored dictionary.
#
# Version history:
#   Day 13 — introduced alongside task_types.py

from .task import Task
from .task_types import UrgentTask, RecurringTask, DeadlineTask

__all__ = ["task_from_dict"]

# Maps the 'type' field stored in JSON → the correct class
_TASK_TYPE_MAP: dict[str, type] = {
    "standard": Task,
    "urgent": UrgentTask,
    "recurring": RecurringTask,
    "deadline": DeadlineTask,
}


def task_from_dict(data: dict) -> Task:
    """
    Create the appropriate Task subclass from a stored dictionary.

    Reads the optional 'type' field to determine the correct class.
    Falls back to plain Task if 'type' is missing or unrecognised.

    Args:
        data (dict): A task dictionary loaded from JSON storage.

    Returns:
        Task: An instance of the correct Task subclass.
    """
    task_type = data.get("type", "standard")
    cls = _TASK_TYPE_MAP.get(task_type, Task)
    return cls.from_dict(data)
