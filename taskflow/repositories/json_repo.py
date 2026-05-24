# JSON file implementation. Day 28.
from __future__ import annotations
import logging
from pathlib import Path
from .base import TaskRepository
from ..core.task import Task
from ..errors import TaskNotFoundError, StorageError
from ..storage.json_store import save_tasks, load_tasks

logger = logging.getLogger(__name__)
__all__ = ["JsonTaskRepository"]


class JsonTaskRepository(TaskRepository):
    """Repository backed by a JSON file. Loads lazily, saves on every mutation."""

    def __init__(self, filepath: Path) -> None:
        self._filepath: Path = filepath
        self._cache: list[Task] | None = None

    def _load(self) -> list[Task]:
        if self._cache is None:
            self._cache = load_tasks(self._filepath)
            logger.debug("Loaded %d tasks from %s", len(self._cache), self._filepath.name)
        return self._cache

    def _save(self) -> None:
        tasks = self._cache or []
        save_tasks(tasks, filepath=self._filepath)
        logger.debug("Saved %d tasks to %s", len(tasks), self._filepath.name)

    def find_all(self) -> list[Task]:
        return list(self._load())

    def find_by_id(self, task_id: int) -> Task | None:
        for t in self._load():
            if t.id == task_id: return t
        return None

    def find_by_priority(self, priority: str) -> list[Task]:
        p = priority.strip().lower()
        return [t for t in self._load() if t.priority == p]

    def save_all(self, tasks: list[Task]) -> None:
        self._cache = list(tasks)
        self._save()

    def add(self, task: Task) -> Task:
        self._load().append(task)
        self._save()
        logger.info("Task added", extra={"task_id": task.id, "title": task.title})
        return task

    def update(self, task: Task) -> Task:
        tasks = self._load()
        for i, t in enumerate(tasks):
            if t.id == task.id:
                tasks[i] = task
                self._save()
                logger.info("Task updated", extra={"task_id": task.id})
                return task
        raise TaskNotFoundError(task.id)

    def delete(self, task_id: int) -> Task:
        tasks = self._load()
        for i, t in enumerate(tasks):
            if t.id == task_id:
                removed = tasks.pop(i)
                self._save()
                logger.info("Task deleted", extra={"task_id": task_id})
                return removed
        raise TaskNotFoundError(task_id)

    def count(self) -> int:
        return len(self._load())

    def exists(self, task_id: int) -> bool:
        return any(t.id == task_id for t in self._load())

    def __repr__(self) -> str:
        count = len(self._cache) if self._cache is not None else "?"
        return f"JsonTaskRepository(filepath={self._filepath.name!r}, cached={count})"
    