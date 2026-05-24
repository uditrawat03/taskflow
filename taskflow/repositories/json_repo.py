from __future__ import annotations
import logging
from pathlib import Path

from .base import TaskRepository
from ..core.task       import Task
from ..errors          import TaskNotFoundError, StorageError
from ..storage.json_store import save_tasks, load_tasks

logger = logging.getLogger(__name__)

__all__ = ["JsonTaskRepository"]


class JsonTaskRepository(TaskRepository):
    """
    Repository implementation backed by a JSON file.

    Loads all tasks into memory on first access (lazy loading).
    Writes the entire list to disk on every mutation.

    This is appropriate for small task lists (< 10,000 items).
    For larger datasets, use SqliteTaskRepository (Day 34).

    Args:
        filepath (Path): Path to the JSON storage file.
    """

    def __init__(self, filepath: Path) -> None:
        self._filepath: Path          = filepath
        self._cache:    list[Task] | None = None   # lazy-loaded

    # ── Internal cache management ─────────────────────────

    def _load(self) -> list[Task]:
        """Load from disk if not cached. Return the in-memory list."""
        if self._cache is None:
            self._cache = load_tasks(self._filepath)
            logger.debug("Loaded %d tasks from %s",
                         len(self._cache), self._filepath.name)
        return self._cache

    def _save(self) -> None:
        """Persist the current in-memory list to disk."""
        tasks = self._cache or []
        save_tasks(tasks, filepath=self._filepath)
        logger.debug("Saved %d tasks to %s",
                     len(tasks), self._filepath.name)

    def _invalidate(self) -> None:
        """Force a reload from disk on next access."""
        self._cache = None

    # ── TaskRepository implementation ─────────────────────

    def find_all(self) -> list[Task]:
        return list(self._load())   # return a copy

    def find_by_id(self, task_id: int) -> Task | None:
        for task in self._load():
            if task.id == task_id:
                return task
        return None

    def find_by_priority(self, priority: str) -> list[Task]:
        p = priority.strip().lower()
        return [t for t in self._load() if t.priority == p]

    def save_all(self, tasks: list[Task]) -> None:
        self._cache = list(tasks)
        self._save()

    def add(self, task: Task) -> Task:
        tasks = self._load()
        tasks.append(task)
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
        tasks  = self._load()
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