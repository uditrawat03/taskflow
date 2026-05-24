# Day 28 — Design Patterns I: Repository & Singleton

> **Series:** Python & AI Engineering — Zero to Production
> **Phase:** 2 — Real Engineering
> **Python Version:** 3.14
> **Project:** TaskFlow AI — Abstracting storage with the Repository pattern

---

## Learning Objective

By the end of today, you will understand two foundational design patterns — Repository and Singleton — and have applied them to TaskFlow AI. The Repository pattern will give the app a clean storage abstraction that makes swapping JSON for SQLite (Day 34) or PostgreSQL (Day 55) a matter of changing one line. The Singleton will centralise app configuration safely.

---

## What We Build Today

A `taskflow/repositories/` subpackage with an abstract `TaskRepository` base and a concrete `JsonTaskRepository` implementation. The rest of the app talks to the abstraction — never directly to `json_store.py`.

```python
# Before — commands.py coupled directly to json_store:
from taskflow.storage.json_store import save_tasks, load_tasks
tasks = load_tasks(DATA_FILE)
save_tasks(tasks, DATA_FILE)

# After — commands.py talks to the repository abstraction:
from taskflow.repositories import get_repository
repo  = get_repository()
tasks = repo.find_all()
repo.save_all(tasks)

# Swapping storage later — ONE line change in config:
REPOSITORY_BACKEND = "sqlite"   # was "json" — nothing else changes
```

---

## Concepts Covered

- Design patterns — what they are and when to use them
- Repository pattern — abstracting data access
- Abstract Base Classes with `ABC` and `@abstractmethod`
- Concrete implementations behind an interface
- Factory function — `get_repository()`
- Singleton pattern — ensuring one instance
- `__new__` — controlling object creation
- Module-level singleton — Python's simplest singleton
- Singleton via `functools.lru_cache`
- When to use patterns and when they add unnecessary complexity

---

## Full Tutorial

### What Are Design Patterns?

Design patterns are reusable solutions to commonly occurring problems in software design. They are not library functions you import — they are templates for structuring code. The classic reference is the "Gang of Four" book (1994), which catalogued 23 patterns. Today we cover two.

**When to use a pattern:**
- The problem it solves is clearly present in your code
- The pattern makes the code simpler or more maintainable
- The team is familiar with the pattern

**When not to use a pattern:**
- Your code does not have the problem the pattern solves
- The pattern adds more complexity than it removes
- You are using it because it sounds impressive

Patterns are solutions — not goals.

---

### The Repository Pattern

**Problem:** Your business logic (`services.py`, `commands.py`) knows how data is stored — it calls `json.load()`, constructs file paths, handles `JSONDecodeError`. When you want to change from JSON to SQLite, you must change every caller.

**Solution:** Introduce a **Repository** — an object that encapsulates all data access logic behind a clean interface. Business logic talks to the repository; the repository talks to the database (or file, or API).

```
Business Logic          Repository Interface        Concrete Implementations
─────────────           ────────────────────        ─────────────────────────
services.py    ───►    TaskRepository (ABC)  ◄───   JsonTaskRepository
commands.py            find_all()                    SqliteTaskRepository  (Day 34)
                       find_by_id()                  PostgresTaskRepository (Day 55)
                       save_all()
                       delete()
```

The business logic never changes. Only the concrete repository class changes.

---

### Building `taskflow/repositories/`

Create the directory structure:

```
taskflow/repositories/
├── __init__.py
├── base.py          ← Abstract base class (the interface)
└── json_repo.py     ← JSON file implementation
```

**`taskflow/repositories/base.py`:**

```python
# taskflow/repositories/base.py
# TaskFlow AI — Abstract Task Repository.
#
# Defines the interface that all storage backends must implement.
# Business logic depends on this interface — never on concrete implementations.
#
# Version history:
#   Day 28 — introduced as part of Repository pattern

from __future__ import annotations
from abc import ABC, abstractmethod
from taskflow.core.task import Task

__all__ = ["TaskRepository"]


class TaskRepository(ABC):
    """
    Abstract base class defining the storage interface for tasks.

    All concrete implementations must provide these methods.
    Business logic (services.py, commands.py) should only interact
    with this interface — never with concrete implementations directly.
    """

    @abstractmethod
    def find_all(self) -> list[Task]:
        """
        Return all stored tasks.

        Returns:
            list[Task]: All tasks, in storage order. Empty list if none.
        """
        ...

    @abstractmethod
    def find_by_id(self, task_id: int) -> Task | None:
        """
        Return the task with the given ID, or None if not found.

        Args:
            task_id (int): The unique task identifier.

        Returns:
            Task | None: The matching task, or None.
        """
        ...

    @abstractmethod
    def find_by_priority(self, priority: str) -> list[Task]:
        """
        Return all tasks with the given priority.

        Args:
            priority (str): One of 'high', 'medium', 'low'.

        Returns:
            list[Task]: Matching tasks.
        """
        ...

    @abstractmethod
    def save_all(self, tasks: list[Task]) -> None:
        """
        Persist the complete task list.

        Replaces the entire stored collection with the provided list.

        Args:
            tasks (list[Task]): The complete current task list.

        Raises:
            StorageError: If persistence fails.
        """
        ...

    @abstractmethod
    def add(self, task: Task) -> Task:
        """
        Add a single new task and persist it.

        Args:
            task (Task): The task to add.

        Returns:
            Task: The added task (same object).

        Raises:
            StorageError: If persistence fails.
        """
        ...

    @abstractmethod
    def update(self, task: Task) -> Task:
        """
        Update an existing task and persist the change.

        Args:
            task (Task): The task with updated fields (matched by task.id).

        Returns:
            Task: The updated task.

        Raises:
            TaskNotFoundError: If no task with task.id exists.
            StorageError: If persistence fails.
        """
        ...

    @abstractmethod
    def delete(self, task_id: int) -> Task:
        """
        Remove the task with the given ID and persist the change.

        Args:
            task_id (int): The ID of the task to remove.

        Returns:
            Task: The removed task.

        Raises:
            TaskNotFoundError: If no task with that ID exists.
            StorageError: If persistence fails.
        """
        ...

    @abstractmethod
    def count(self) -> int:
        """
        Return the total number of stored tasks.

        Returns:
            int: Task count.
        """
        ...

    @abstractmethod
    def exists(self, task_id: int) -> bool:
        """
        Return True if a task with the given ID exists.

        Args:
            task_id (int): Task ID to check.

        Returns:
            bool: True if found.
        """
        ...

    # ── Concrete helpers built on abstract methods ────────
    # Subclasses inherit these — they do not need to override them.

    def find_pending(self) -> list[Task]:
        """Return all tasks that are not yet done."""
        return [t for t in self.find_all() if not t.done]

    def find_done(self) -> list[Task]:
        """Return all completed tasks."""
        return [t for t in self.find_all() if t.done]

    def find_overdue(self, threshold_days: int = 7) -> list[Task]:
        """Return all overdue pending tasks."""
        return [t for t in self.find_all() if t.is_overdue(threshold_days)]
```

**`taskflow/repositories/json_repo.py`:**

```python
# taskflow/repositories/json_repo.py
# TaskFlow AI — JSON file implementation of TaskRepository.
#
# Wraps the existing json_store.py functions behind the repository interface.
# All state is persisted on every mutating operation (add, update, delete).
#
# Version history:
#   Day 28 — initial implementation wrapping json_store.py

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
```

**`taskflow/repositories/__init__.py`:**

```python
# taskflow/repositories/__init__.py
# Factory function and public API for the repository layer.

from __future__ import annotations
import logging
from pathlib import Path
from functools import lru_cache

from .base      import TaskRepository
from .json_repo import JsonTaskRepository
from ..env_config import get_settings

logger = logging.getLogger(__name__)

__all__ = ["TaskRepository", "JsonTaskRepository", "get_repository"]

# Registry — maps backend name to class
_BACKENDS: dict[str, type[TaskRepository]] = {
    "json": JsonTaskRepository,
    # "sqlite":   SqliteTaskRepository,   # added Day 34
    # "postgres": PostgresTaskRepository, # added Day 55
}


@lru_cache(maxsize=1)
def get_repository(backend: str | None = None) -> TaskRepository:
    """
    Return the application's task repository (singleton via lru_cache).

    The first call constructs and caches the repository.
    Subsequent calls return the same instance.

    Args:
        backend (str | None): Backend name — 'json', 'sqlite', 'postgres'.
                              Reads TASKFLOW_REPOSITORY env var if None.
                              Defaults to 'json'.

    Returns:
        TaskRepository: The configured repository instance.

    Raises:
        ValueError: If the backend name is not recognised.
    """
    settings = get_settings()
    chosen   = backend or getattr(settings, "repository_backend", "json")

    if chosen not in _BACKENDS:
        raise ValueError(
            f"Unknown repository backend '{chosen}'. "
            f"Available: {', '.join(_BACKENDS)}"
        )

    repo_class = _BACKENDS[chosen]
    repo       = repo_class(settings.data_file)

    logger.info(
        "Repository initialised",
        extra={"backend": chosen, "filepath": str(settings.data_file)}
    )
    return repo
```

---

### The Singleton Pattern

**Problem:** A class should have only one instance (e.g., configuration, database connection pool, logger).

**Solution:** Control instantiation so a second `__init__` call returns the already-existing instance.

**Method 1 — Module-level singleton (simplest, most Pythonic):**

```python
# taskflow/app_config.py
# The module itself is the singleton — Python imports each module once.

from taskflow.env_config import get_settings

_settings = get_settings()   # created once at import time

def get_app_settings():
    return _settings
```

**Method 2 — `lru_cache` singleton (used in `get_repository()` above):**

```python
from functools import lru_cache

@lru_cache(maxsize=1)
def get_repository():
    """Called many times — returns the same instance every time."""
    return JsonTaskRepository(DATA_FILE)
```

`@lru_cache(maxsize=1)` caches the result of the first call. Every subsequent call with the same arguments returns the cached result. With `maxsize=1` and a function that takes no arguments, it is a perfect singleton.

**Method 3 — `__new__` class-based singleton:**

```python
class AppConfig:
    _instance: "AppConfig | None" = None

    def __new__(cls) -> "AppConfig":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialised = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialised:
            return   # already initialised — do not re-run
        self.settings  = get_settings()
        self.repo      = get_repository()
        self._initialised = True


# Usage
config1 = AppConfig()
config2 = AppConfig()
assert config1 is config2   # True — same instance
```

**Which to use?**
- Module-level variable → simplest, use for truly global constants
- `@lru_cache` → best for factory functions that are called in multiple places
- `__new__` → use only when you need a class with methods and need to prevent multiple instances explicitly

In Python, the module-level and `@lru_cache` approaches are almost always sufficient. Reach for `__new__` only when the other two do not fit.

---

### Updating `services.py` to Use the Repository

```python
# taskflow/services.py — updated to use repository (Day 28)
# The repo parameter allows dependency injection in tests.

from __future__ import annotations
from typing import TYPE_CHECKING

from .errors import ValidationError, TaskNotFoundError
from .core.task       import Task
from .core.task_types import RecurringTask

if TYPE_CHECKING:
    from .repositories.base import TaskRepository


def add_task(
    task: Task,
    repo: "TaskRepository",
    plan: str | None = None,
) -> Task:
    """
    Validate the plan limit and add a task through the repository.

    Args:
        task (Task)          : The task to add.
        repo (TaskRepository): The storage repository.
        plan (str | None)    : Plan name for limit checking.

    Returns:
        Task: The added task.

    Raises:
        ValidationError: If the task limit is reached.
    """
    from .config import PLAN_LIMITS, USER_PLAN
    limit = PLAN_LIMITS.get(plan or USER_PLAN, PLAN_LIMITS["free"])
    if repo.count() >= limit:
        raise ValidationError(
            f"Task limit reached ({limit} tasks on {plan or USER_PLAN} plan).",
            field="tasks", value=repo.count(),
        )
    return repo.add(task)


def remove_task(task_id: int, repo: "TaskRepository") -> Task:
    """Remove a task by ID through the repository."""
    return repo.delete(task_id)


def mark_done(task_id: int, repo: "TaskRepository") -> Task:
    """Mark a task as done and persist through the repository."""
    task = repo.find_by_id(task_id)
    if task is None:
        raise TaskNotFoundError(task_id)
    if isinstance(task, Task) and task.done and not isinstance(task, RecurringTask):
        raise ValidationError(f"Task {task_id} is already done.", field="done")
    task.mark_done()
    return repo.update(task)


def rename_task(task_id: int, new_title: str, repo: "TaskRepository") -> Task:
    """Rename a task and persist through the repository."""
    task = repo.find_by_id(task_id)
    if task is None:
        raise TaskNotFoundError(task_id)
    task.rename(new_title)
    return repo.update(task)
```

---

### Writing Repository Tests

The Repository pattern makes tests dramatically simpler — use an in-memory fake repository:

```python
# tests/test_repository.py

import pytest
from pathlib import Path
from taskflow.core.task import Task
from taskflow.core.task_types import UrgentTask
from taskflow.repositories.json_repo import JsonTaskRepository
from taskflow.repositories.base import TaskRepository
from taskflow.errors import TaskNotFoundError, StorageError


class TestJsonTaskRepository:

    @pytest.fixture
    def repo(self, tmp_path) -> JsonTaskRepository:
        filepath = tmp_path / "tasks.json"
        return JsonTaskRepository(filepath)

    def test_find_all_returns_empty_initially(self, repo):
        assert repo.find_all() == []

    def test_add_and_find_all(self, repo, one_task):
        task = one_task[0]
        repo.add(task)
        all_tasks = repo.find_all()
        assert len(all_tasks) == 1
        assert all_tasks[0].title == task.title

    def test_find_by_id(self, repo, one_task):
        task = one_task[0]
        repo.add(task)
        found = repo.find_by_id(task.id)
        assert found is not None
        assert found.id == task.id

    def test_find_by_id_returns_none_when_missing(self, repo):
        assert repo.find_by_id(9999) is None

    def test_delete(self, repo, one_task):
        task = one_task[0]
        repo.add(task)
        removed = repo.delete(task.id)
        assert removed.id == task.id
        assert repo.count() == 0

    def test_delete_raises_when_not_found(self, repo):
        with pytest.raises(TaskNotFoundError):
            repo.delete(9999)

    def test_update(self, repo, one_task):
        task = one_task[0]
        repo.add(task)
        task.rename("Updated title")
        repo.update(task)
        found = repo.find_by_id(task.id)
        assert found.title == "Updated title"

    def test_persists_across_instances(self, tmp_path, one_task):
        """Data written by one repo instance survives to the next."""
        filepath = tmp_path / "tasks.json"
        repo1 = JsonTaskRepository(filepath)
        repo1.add(one_task[0])

        repo2 = JsonTaskRepository(filepath)
        assert repo2.count() == 1
        assert repo2.find_all()[0].title == one_task[0].title

    def test_find_pending(self, repo, mixed_tasks):
        for t in mixed_tasks:
            repo.add(t)
        pending = repo.find_pending()
        assert all(not t.done for t in pending)

    def test_count(self, repo, mixed_tasks):
        for t in mixed_tasks:
            repo.add(t)
        assert repo.count() == len(mixed_tasks)

    def test_exists(self, repo, one_task):
        task = one_task[0]
        assert repo.exists(task.id) is False
        repo.add(task)
        assert repo.exists(task.id) is True

    def test_raises_on_corrupt_file(self, tmp_path):
        filepath = tmp_path / "corrupt.json"
        filepath.write_text("{not valid json}", encoding="utf-8")
        repo = JsonTaskRepository(filepath)
        with pytest.raises(StorageError):
            repo.find_all()

    def test_saves_urgent_task_correctly(self, repo):
        urgent = UrgentTask("Server down", "work")
        repo.add(urgent)
        filepath = repo._filepath
        repo2    = JsonTaskRepository(filepath)
        loaded   = repo2.find_all()
        assert isinstance(loaded[0], UrgentTask)
```

---

## Exercises

**Exercise 1 — In-memory repository for tests.**
Create `taskflow/repositories/memory_repo.py` — an `InMemoryTaskRepository` that stores tasks in a plain Python list, never touches the filesystem. Use it as the default repository in all tests:

```python
class InMemoryTaskRepository(TaskRepository):
    def __init__(self) -> None:
        self._tasks: list[Task] = []

    def find_all(self) -> list[Task]:
        return list(self._tasks)
    # ... implement all abstract methods
```

Add a `conftest.py` fixture that provides an `InMemoryTaskRepository` for every test that needs it.

**Exercise 2 — Add `find_by_category()` to the base.**
Extend `TaskRepository` with:
```python
@abstractmethod
def find_by_category(self, category: str) -> list[Task]: ...
```
Implement it in `JsonTaskRepository`. Write tests. What happens to `InMemoryTaskRepository` from Exercise 1?

**Exercise 3 — Repository in `commands.py`.**
Update `cmd_add()`, `cmd_done()`, and `cmd_remove()` to call `services.py` functions that accept a `repo` argument instead of a raw `tasks` list. The `get_repository()` call moves to `main.py` and `shell.py`. Verify all tests still pass.

**Exercise 4 — Singleton verification.**
Write a test that calls `get_repository()` 100 times and asserts every call returns the exact same object:

```python
def test_get_repository_returns_singleton():
    from taskflow.repositories import get_repository
    instances = [get_repository() for _ in range(100)]
    assert all(r is instances[0] for r in instances)
```

Then call `get_repository.cache_clear()` and call again — verify a new instance is created.

**Exercise 5 — Repository factory test.**
Write a test that verifies the factory function raises `ValueError` for unknown backends:

```python
def test_unknown_backend_raises():
    from taskflow.repositories import get_repository
    with pytest.raises(ValueError, match="Unknown repository backend"):
        get_repository.cache_clear()
        get_repository(backend="oracle")
```

**Exercise 6 (stretch) — Unit of Work pattern.**
The Repository pattern handles individual entities. The **Unit of Work** pattern groups multiple repository operations into a single atomic transaction. Implement a simple `UnitOfWork` context manager:

```python
class UnitOfWork:
    def __init__(self, repo: TaskRepository) -> None:
        self._repo = repo
        self._pending: list[Task] = []

    def __enter__(self) -> "UnitOfWork":
        self._pending = list(self._repo.find_all())
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if exc_type is None:
            self._repo.save_all(self._pending)
        # On exception, changes are discarded — no save
        return False

# Usage:
with UnitOfWork(repo) as uow:
    task1 = Task("Task A", "high", "work")
    task2 = Task("Task B", "low", "personal")
    uow._pending.append(task1)
    uow._pending.append(task2)
    # Both saved atomically on exit
```

---

## Checkpoint

Before moving to Day 29:

- [ ] `taskflow/repositories/base.py` defines `TaskRepository` ABC with 8 abstract methods
- [ ] `taskflow/repositories/json_repo.py` implements all 8 methods correctly
- [ ] `taskflow/repositories/__init__.py` has `get_repository()` factory with `@lru_cache`
- [ ] `tests/test_repository.py` has all tests passing
- [ ] I understand the difference between module singleton, `lru_cache` singleton, and `__new__` singleton
- [ ] `services.py` functions accept a `repo` parameter instead of a raw `tasks` list
- [ ] `get_repository()` is called in `main.py` and passed down the call chain
- [ ] Swapping to a different backend requires changing one setting only

---

## Common Errors on Day 28

**Instantiating the ABC directly:**

```python
repo = TaskRepository()   # ❌ TypeError: Can't instantiate abstract class
repo = JsonTaskRepository(filepath)   # ✅ concrete class
```

**Mutating the returned list from `find_all()`:**

```python
tasks = repo.find_all()
tasks.append(new_task)   # ❌ only mutates local copy — not persisted
repo.add(new_task)       # ✅ goes through the repo and persists
```

Always mutate through the repository — never through the list it returns.

**`lru_cache` singleton not clearing between tests:**

```python
# In conftest.py:
@pytest.fixture(autouse=True)
def clear_repository_cache():
    from taskflow.repositories import get_repository
    get_repository.cache_clear()
    yield
    get_repository.cache_clear()
```

The `@lru_cache` persists across tests unless explicitly cleared. Add this fixture to `conftest.py`.

---

## What's Coming

On **Day 29** we cover three more patterns: Factory (to create the right Task subclass from data), Observer (to emit events when tasks change — e.g., "task completed", "limit reached"), and Strategy (to swap the sorting algorithm). These three patterns appear throughout Phase 3's FastAPI server and Phase 4's AI pipelines.