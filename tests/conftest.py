import pytest

from taskflow.core.task import Task
from taskflow.core.task_types import (
    UrgentTask,
    RecurringTask,
    DeadlineTask,
)


@pytest.fixture(autouse=True)
def reset_task_counter():
    """
    Reset the Task ID counter before every test.

    Without this, tests that create tasks would produce ever-increasing IDs
    depending on what ran before, making assertions fragile.
    """
    Task.reset_counter()
    yield
    Task.reset_counter()


@pytest.fixture
def empty_tasks():
    """An empty task list."""
    return []


@pytest.fixture
def one_task():
    """A list with a single standard task."""
    return [Task("Review PR", "high", "work")]


@pytest.fixture
def mixed_tasks():
    """A list with five tasks of mixed types and states."""
    tasks = [
        Task("Review PR",       "high",   "work"),
        Task("Buy groceries",   "low",    "personal"),
        Task("Write tests",     "medium", "work"),
        UrgentTask("Server down", "work"),
        DeadlineTask("Submit report", "work", priority="high",
                     due_date="2099-12-31"),
    ]
    tasks[2].mark_done()   # "Write tests" is done
    return tasks


@pytest.fixture
def ten_free_tasks():
    """Exactly 10 tasks — the free plan limit."""
    return [Task(f"Task {i}", "low", "personal") for i in range(1, 11)]