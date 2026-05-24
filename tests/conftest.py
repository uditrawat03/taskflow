# tests/conftest.py — Shared pytest fixtures for TaskFlow AI.
# Loaded automatically by pytest before every test file.
import pytest
from pathlib import Path
from dotenv import load_dotenv

# Load test environment before any taskflow imports
load_dotenv(Path(__file__).parent.parent / ".env.test", override=True)

from taskflow.core.task        import Task
from taskflow.core.task_types  import UrgentTask, RecurringTask, DeadlineTask


# ── ID counter reset ─────────────────────────────────────

@pytest.fixture(autouse=True)
def reset_task_counter():
    """Reset Task._id_counter before and after every test."""
    Task.reset_counter()
    yield
    Task.reset_counter()


# ── Repository cache reset ────────────────────────────────

@pytest.fixture(autouse=True)
def clear_repository_cache():
    """Clear the get_repository lru_cache between tests."""
    try:
        from taskflow.repositories import get_repository
        get_repository.cache_clear()
    except Exception:
        pass
    yield
    try:
        from taskflow.repositories import get_repository
        get_repository.cache_clear()
    except Exception:
        pass


# ── Event bus reset ───────────────────────────────────────

@pytest.fixture(autouse=True)
def clear_event_bus():
    """Clear event bus handlers between tests."""
    try:
        from taskflow.events import event_bus
        event_bus.clear()
    except Exception:
        pass
    yield
    try:
        from taskflow.events import event_bus
        event_bus.clear()
    except Exception:
        pass


# ── Settings reset ────────────────────────────────────────

@pytest.fixture(autouse=True)
def reset_settings():
    """Force settings reload for each test (picks up .env.test)."""
    from taskflow.env_config import get_settings
    get_settings(reload=True)
    yield
    get_settings(reload=True)


# ── Task list fixtures ────────────────────────────────────

@pytest.fixture
def empty_tasks() -> list:
    """An empty task list."""
    return []


@pytest.fixture
def one_task() -> list:
    """A list with one standard pending task."""
    return [Task("Review pull request", "high", "work")]


@pytest.fixture
def mixed_tasks() -> list:
    """A list of 5 tasks with mixed types, priorities, and states."""
    tasks = [
        Task("Review pull request",    "high",   "work"),
        Task("Buy groceries",          "low",    "personal"),
        Task("Write tests",            "medium", "work"),
        UrgentTask("Server is down",   "work"),
        DeadlineTask("Submit report",  "work",   priority="high",
                     due_date="2099-12-31"),
    ]
    tasks[2].mark_done()   # "Write tests" is done
    return tasks


@pytest.fixture
def ten_free_tasks() -> list:
    """Exactly 10 tasks — the free plan limit."""
    return [Task(f"Task {i}", "low", "personal") for i in range(1, 11)]


@pytest.fixture
def overdue_task() -> Task:
    """A task with created_at set 30 days in the past."""
    import datetime
    task = Task("Old pending task", "high", "work")
    past = datetime.datetime.now() - datetime.timedelta(days=30)
    task.created_at = past.strftime("%Y-%m-%d %H:%M")
    return task


@pytest.fixture
def all_task_types() -> list:
    """One of each task type."""
    return [
        Task("Standard task",           "medium", "work"),
        UrgentTask("Urgent task",       "work"),
        RecurringTask("Recurring task", "medium", "work", "daily"),
        DeadlineTask("Deadline task",   "work",   due_date="2099-12-31"),
    ]


@pytest.fixture
def tmp_data_dir(tmp_path: Path) -> Path:
    """A temporary directory for test data files."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir


@pytest.fixture
def tmp_repo(tmp_path: Path):
    """A JsonTaskRepository backed by a temporary file."""
    from taskflow.repositories.json_repo import JsonTaskRepository
    filepath = tmp_path / "test_tasks.json"
    return JsonTaskRepository(filepath)
