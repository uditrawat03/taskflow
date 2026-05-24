# taskflow/core/task_factory.py — Polymorphic task deserialisation. Day 13/29.
from __future__ import annotations
import logging
from typing import ClassVar
from .task        import Task
from .task_types  import UrgentTask, RecurringTask, DeadlineTask

logger = logging.getLogger(__name__)
__all__ = ["TaskFactory", "task_from_dict"]


class TaskFactory:
    """Factory for creating the correct Task subclass from a stored dict."""

    _registry: ClassVar[dict[str, type[Task]]] = {
        "standard":  Task,
        "urgent":    UrgentTask,
        "recurring": RecurringTask,
        "deadline":  DeadlineTask,
    }

    @classmethod
    def register(cls, type_name: str, task_class: type[Task]) -> None:
        if type_name in cls._registry:
            logger.warning("Overwriting factory registration for '%s'", type_name)
        cls._registry[type_name] = task_class

    @classmethod
    def create_from_dict(cls, data: dict) -> Task:
        type_name  = data.get("type", "standard")
        task_class = cls._registry.get(type_name, Task)
        if type_name not in cls._registry:
            logger.warning("Unknown task type '%s' — using Task", type_name)
        return task_class.from_dict(data)

    @classmethod
    def registered_types(cls) -> list[str]:
        return list(cls._registry.keys())


def task_from_dict(data: dict) -> Task:
    return TaskFactory.create_from_dict(data)
