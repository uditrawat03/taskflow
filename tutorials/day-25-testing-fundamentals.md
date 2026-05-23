# Day 25 — Testing Fundamentals

> **Series:** Python & AI Engineering — Zero to Production
> **Phase:** 2 — Real Engineering
> **Python Version:** 3.14
> **Project:** TaskFlow AI — Building a real test suite from scratch

---

## Learning Objective

By the end of today, TaskFlow AI will have a meaningful test suite covering all business logic in `core/` and `services/`. You will understand pytest fundamentals, test organisation, fixtures, parametrize, and how to write tests that actually catch bugs rather than just passing.

---

## What We Build Today

A complete test suite in `tests/` covering `core/task.py`, `core/task_types.py`, `core/stats.py`, `services.py`, `parser.py`, and `storage/json_store.py`.

```bash
$ pytest tests/ -v

tests/test_task.py::TestTaskCreation::test_valid_task PASSED
tests/test_task.py::TestTaskCreation::test_empty_title_raises PASSED
tests/test_task.py::TestTaskCreation::test_invalid_priority_raises PASSED
tests/test_task.py::TestTaskCreation::test_auto_id_increments PASSED
tests/test_task.py::TestTaskMethods::test_mark_done PASSED
tests/test_task.py::TestTaskMethods::test_mark_pending PASSED
tests/test_task.py::TestTaskMethods::test_rename PASSED
tests/test_task.py::TestTaskSerialization::test_to_dict PASSED
tests/test_task.py::TestTaskSerialization::test_from_dict_roundtrip PASSED
...

tests/test_services.py::TestAddTask::test_adds_task PASSED
...

====== 47 passed in 0.31s ======

Coverage report:
  taskflow/core/task.py         95%
  taskflow/core/task_types.py   88%
  taskflow/core/stats.py        100%
  taskflow/services.py          92%
  taskflow/parser.py            84%
  taskflow/storage/json_store.py 79%
  ─────────────────────────────────
  TOTAL                         89%
```

---

## Concepts Covered

- pytest — test discovery, running, output
- Test file and function naming conventions
- `assert` in pytest — readable failure messages
- Test classes — grouping related tests
- Fixtures — `@pytest.fixture`, scope, yield
- `conftest.py` — sharing fixtures across files
- `@pytest.mark.parametrize` — data-driven tests
- `pytest.raises` — testing exceptions
- `tmp_path` — built-in temporary directory fixture
- `caplog` — capturing log output in tests
- `monkeypatch` — overriding behaviour in tests
- Test independence — every test starts clean
- What to test and what not to test
- Coverage targets and `--cov`

---

## Full Tutorial

### What Makes a Good Test?

A good test:
- Tests one thing — one behaviour, one code path
- Has a clear name that describes the scenario and expected outcome
- Is independent — does not depend on other tests or global state
- Is deterministic — always passes or always fails, never flaky
- Is fast — runs in milliseconds
- Fails clearly — when it fails, you know exactly what broke

A bad test:
- Tests multiple things at once
- Has a vague name like `test_task()` or `test_everything()`
- Depends on execution order
- Makes network calls or writes to production files
- Takes seconds to run

---

### pytest Basics

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run a specific file
pytest tests/test_task.py

# Run a specific test class
pytest tests/test_task.py::TestTaskCreation

# Run a specific test
pytest tests/test_task.py::TestTaskCreation::test_empty_title_raises

# Run tests matching a keyword
pytest -k "mark_done"

# Stop on first failure
pytest -x

# Show print output (disabled by default)
pytest -s

# Run with coverage
pytest --cov=taskflow --cov-report=term-missing
```

---

### Test Naming Conventions

```
tests/
├── conftest.py              ← shared fixtures
├── test_task.py             ← tests for core/task.py
├── test_task_types.py       ← tests for core/task_types.py
├── test_stats.py            ← tests for core/stats.py
├── test_services.py         ← tests for services.py
├── test_parser.py           ← tests for parser.py
├── test_storage.py          ← tests for storage/json_store.py
└── test_filters.py          ← tests for filters.py
```

- Files: `test_<module>.py`
- Classes: `Test<Feature>` (grouping related tests)
- Functions: `test_<scenario>_<expected_outcome>`

Examples:
```
test_empty_title_raises_validation_error
test_mark_done_sets_status_to_done
test_from_dict_roundtrip_preserves_all_fields
test_recurring_task_resets_after_mark_done
```

---

### `assert` in pytest

pytest rewrites `assert` statements to give detailed failure messages:

```python
def test_task_title():
    task = Task("Review PR", "high", "work")
    assert task.title == "Review PR"
    # If this fails:
    # AssertionError: assert 'Review PR ' == 'Review PR'
    #   (notice the trailing space — pytest shows the difference)

def test_task_count():
    tasks = [Task("A", "low", "work"), Task("B", "low", "work")]
    assert len(tasks) == 3
    # AssertionError: assert 2 == 3
    # (pytest shows the actual value)
```

No custom message needed — pytest introspects the expression and shows you exactly what was expected and what was received.

---

### `pytest.raises` — Testing Exceptions

```python
import pytest
from taskflow.errors import ValidationError
from taskflow.core.task import Task

def test_empty_title_raises():
    with pytest.raises(ValidationError):
        Task("", "high", "work")

def test_invalid_priority_raises():
    with pytest.raises(ValidationError) as exc_info:
        Task("Review PR", "urgent", "work")   # "urgent" is not valid
    assert "priority" in str(exc_info.value).lower()

def test_title_too_long_raises():
    with pytest.raises(ValidationError) as exc_info:
        Task("x" * 201, "high", "work")
    assert exc_info.value.field == "title"
```

`exc_info.value` gives you the exception object — you can inspect its attributes, message, and type.

---

### `@pytest.mark.parametrize` — Data-Driven Tests

Instead of writing the same test 5 times with different inputs, parametrize:

```python
import pytest
from taskflow.core.task import Task
from taskflow.errors import ValidationError

@pytest.mark.parametrize("priority", ["high", "medium", "low"])
def test_valid_priorities(priority):
    task = Task("Test task", priority, "work")
    assert task.priority == priority


@pytest.mark.parametrize("invalid_priority", [
    "urgent", "critical", "HIGH", "", "  ", "1", "none"
])
def test_invalid_priorities_raise(invalid_priority):
    with pytest.raises(ValidationError):
        Task("Test task", invalid_priority, "work")


@pytest.mark.parametrize("title,priority,category,expected_score", [
    ("Task A", "high",   "work",     3),
    ("Task B", "medium", "personal", 2),
    ("Task C", "low",    "health",   1),
])
def test_priority_score(title, priority, category, expected_score):
    task = Task(title, priority, category)
    assert task.priority_score == expected_score
```

---

### `tmp_path` — Testing File Operations

`tmp_path` is a built-in pytest fixture that provides a temporary directory unique to each test. Files written there are cleaned up automatically:

```python
from pathlib import Path
from taskflow.core.task import Task
from taskflow.storage.json_store import save_tasks, load_tasks

def test_save_and_load_roundtrip(tmp_path):
    filepath = tmp_path / "test_tasks.json"
    tasks = [
        Task("Review PR",    "high", "work"),
        Task("Buy groceries", "low", "personal"),
    ]

    save_tasks(tasks, filepath=filepath)

    assert filepath.exists()

    loaded = load_tasks(filepath=filepath)

    assert len(loaded) == 2
    assert loaded[0].title    == "Review PR"
    assert loaded[0].priority == "high"
    assert loaded[1].title    == "Buy groceries"
    assert loaded[1].done     is False
```

---

### `monkeypatch` — Overriding Behaviour

`monkeypatch` lets you temporarily override environment variables, module attributes, and functions during a test:

```python
def test_weather_disabled(monkeypatch):
    """Verify the app skips weather when TASKFLOW_WEATHER=false."""
    monkeypatch.setenv("TASKFLOW_WEATHER", "false")
    from taskflow.env_config import get_settings
    settings = get_settings(reload=True)
    assert settings.weather_enabled is False


def test_fetch_weather_network_error(monkeypatch):
    """Verify fetch_weather() returns None on connection error."""
    import requests
    def mock_get(*args, **kwargs):
        raise requests.exceptions.ConnectionError("No network")
    monkeypatch.setattr(requests, "get", mock_get)

    from taskflow.integrations.weather import fetch_weather
    result = fetch_weather(0, 0, "Test", use_cache=False)
    assert result is None
```

---

### Building the Full Test Suite

**`tests/test_task.py`:**

```python
# tests/test_task.py
import pytest
import datetime
from taskflow.core.task import Task
from taskflow.errors import ValidationError


class TestTaskCreation:

    def test_valid_task(self):
        task = Task("Review PR", "high", "work")
        assert task.title    == "Review PR"
        assert task.priority == "high"
        assert task.category == "work"
        assert task.done     is False
        assert task.status   == "pending"

    def test_empty_title_raises(self):
        with pytest.raises(ValidationError) as exc:
            Task("", "high", "work")
        assert exc.value.field == "title"

    def test_whitespace_only_title_raises(self):
        with pytest.raises(ValidationError):
            Task("   ", "high", "work")

    def test_title_stripped_of_whitespace(self):
        task = Task("  Review PR  ", "high", "work")
        assert task.title == "Review PR"

    def test_title_too_long_raises(self):
        with pytest.raises(ValidationError) as exc:
            Task("x" * 201, "high", "work")
        assert exc.value.field == "title"

    @pytest.mark.parametrize("priority", ["high", "medium", "low"])
    def test_valid_priorities(self, priority):
        task = Task("Test", priority, "work")
        assert task.priority == priority

    @pytest.mark.parametrize("bad_priority", ["urgent", "CRITICAL", "", "3"])
    def test_invalid_priority_raises(self, bad_priority):
        with pytest.raises(ValidationError):
            Task("Test", bad_priority, "work")

    @pytest.mark.parametrize("category", [
        "work", "personal", "health", "learning", "other"
    ])
    def test_valid_categories(self, category):
        task = Task("Test", "medium", category)
        assert task.category == category

    def test_auto_id_increments(self):
        t1 = Task("Task 1", "low", "work")
        t2 = Task("Task 2", "low", "work")
        assert t2.id == t1.id + 1

    def test_explicit_id(self):
        task = Task("Task", "low", "work", task_id=99)
        assert task.id == 99

    def test_created_at_format(self):
        task = Task("Test", "low", "work")
        # Should parse without error
        datetime.datetime.strptime(task.created_at, "%Y-%m-%d %H:%M")


class TestTaskMethods:

    def test_mark_done(self, one_task):
        task = one_task[0]
        result = task.mark_done()
        assert task.done   is True
        assert task.status == "done"
        assert result is task   # method chaining

    def test_mark_pending(self, one_task):
        task = one_task[0]
        task.mark_done()
        task.mark_pending()
        assert task.done   is False
        assert task.status == "pending"

    def test_rename(self, one_task):
        task = one_task[0]
        task.rename("New title")
        assert task.title == "New title"

    def test_rename_empty_raises(self, one_task):
        with pytest.raises(ValidationError):
            one_task[0].rename("")

    def test_is_pending_true_when_not_done(self, one_task):
        assert one_task[0].is_pending() is True

    def test_is_pending_false_when_done(self, one_task):
        one_task[0].mark_done()
        assert one_task[0].is_pending() is False

    def test_matches_keyword(self, one_task):
        assert one_task[0].matches("review") is True
        assert one_task[0].matches("REVIEW") is True
        assert one_task[0].matches("grocery") is False

    def test_priority_property_setter_validates(self, one_task):
        with pytest.raises(ValidationError):
            one_task[0].priority = "urgent"

    def test_priority_property_setter_accepts_valid(self, one_task):
        one_task[0].priority = "low"
        assert one_task[0].priority == "low"

    @pytest.mark.parametrize("priority,score", [
        ("high", 3), ("medium", 2), ("low", 1)
    ])
    def test_priority_score(self, priority, score):
        task = Task("Test", priority, "work")
        assert task.priority_score == score


class TestTaskSerialization:

    def test_to_dict_has_required_keys(self, one_task):
        d = one_task[0].to_dict()
        required = {"id", "title", "priority", "category",
                    "status", "done", "created_at", "type"}
        assert required.issubset(d.keys())

    def test_to_dict_done_is_bool(self, one_task):
        d = one_task[0].to_dict()
        assert isinstance(d["done"], bool)

    def test_from_dict_roundtrip(self, one_task):
        original = one_task[0]
        d        = original.to_dict()
        restored = Task.from_dict(d)
        assert restored.id       == original.id
        assert restored.title    == original.title
        assert restored.priority == original.priority
        assert restored.category == original.category
        assert restored.done     == original.done

    def test_from_dict_restores_done_state(self):
        d = {
            "id": 1, "title": "Done task", "priority": "high",
            "category": "work", "status": "done", "done": True,
            "created_at": "2025-05-19 14:00", "type": "standard",
        }
        task = Task.from_dict(d)
        assert task.done   is True
        assert task.status == "done"


class TestTaskComparison:

    def test_equal_by_id(self):
        t1 = Task("Task A", "high", "work", task_id=42)
        t2 = Task("Task B", "low",  "personal", task_id=42)
        assert t1 == t2

    def test_not_equal_different_id(self):
        t1 = Task("Same title", "high", "work")
        t2 = Task("Same title", "high", "work")
        assert t1 != t2   # different auto-assigned IDs

    def test_hashable_in_set(self):
        t1 = Task("Task", "high", "work")
        s  = {t1}
        assert t1 in s

    def test_sorted_by_priority_score(self):
        low  = Task("Low task",  "low",  "work")
        high = Task("High task", "high", "work")
        med  = Task("Med task",  "medium", "work")
        tasks = sorted([low, high, med])
        assert tasks[0].priority == "high"
        assert tasks[1].priority == "medium"
        assert tasks[2].priority == "low"
```

**`tests/test_task_types.py`:**

```python
# tests/test_task_types.py
import pytest
from taskflow.core.task_types import UrgentTask, RecurringTask, DeadlineTask
from taskflow.errors import ValidationError


class TestUrgentTask:

    def test_priority_always_high(self):
        task = UrgentTask("Server down", "work")
        assert task.priority == "high"

    def test_cannot_change_priority(self):
        task = UrgentTask("Server down", "work")
        with pytest.raises(ValidationError):
            task.priority = "low"

    def test_str_has_emoji(self):
        task = UrgentTask("Server down", "work")
        assert "🚨" in str(task)

    def test_to_dict_type_is_urgent(self):
        task = UrgentTask("Server down", "work")
        assert task.to_dict()["type"] == "urgent"

    def test_from_dict_roundtrip(self):
        task = UrgentTask("Server down", "work")
        d    = task.to_dict()
        restored = UrgentTask.from_dict(d)
        assert restored.title    == "Server down"
        assert restored.priority == "high"


class TestRecurringTask:

    @pytest.mark.parametrize("recurrence", ["daily", "weekly", "monthly"])
    def test_valid_recurrences(self, recurrence):
        task = RecurringTask("Standup", "medium", "work", recurrence)
        assert task.recurrence == recurrence

    def test_invalid_recurrence_raises(self):
        with pytest.raises(ValidationError):
            RecurringTask("Standup", "medium", "work", "hourly")

    def test_mark_done_resets_to_pending(self):
        task = RecurringTask("Standup", "medium", "work", "daily")
        task.mark_done()
        assert task.done             is False
        assert task.status           == "pending"
        assert task.completion_count == 1

    def test_completion_count_increments(self):
        task = RecurringTask("Standup", "medium", "work", "daily")
        task.mark_done()
        task.mark_done()
        task.mark_done()
        assert task.completion_count == 3

    def test_to_dict_includes_recurrence(self):
        task = RecurringTask("Standup", "medium", "work", "weekly")
        d    = task.to_dict()
        assert d["type"]       == "recurring"
        assert d["recurrence"] == "weekly"


class TestDeadlineTask:

    def test_valid_due_date(self):
        task = DeadlineTask("Report", "work", due_date="2099-12-31")
        assert task.due_date == "2099-12-31"

    def test_missing_due_date_raises(self):
        with pytest.raises(ValidationError):
            DeadlineTask("Report", "work", due_date="")

    def test_invalid_date_format_raises(self):
        with pytest.raises(ValidationError):
            DeadlineTask("Report", "work", due_date="31-12-2099")

    def test_days_until_due_future(self):
        task = DeadlineTask("Report", "work", due_date="2099-12-31")
        assert task.days_until_due > 0

    def test_days_until_due_past_is_negative(self):
        task = DeadlineTask("Report", "work", due_date="2020-01-01")
        assert task.days_until_due < 0

    def test_is_overdue_past_due(self):
        task = DeadlineTask("Report", "work", due_date="2020-01-01")
        assert task.is_overdue() is True

    def test_is_overdue_future_due(self):
        task = DeadlineTask("Report", "work", due_date="2099-12-31")
        assert task.is_overdue() is False

    def test_is_overdue_false_when_done(self):
        task = DeadlineTask("Report", "work", due_date="2020-01-01")
        task.mark_done()
        assert task.is_overdue() is False

    def test_to_dict_includes_due_date(self):
        task = DeadlineTask("Report", "work", due_date="2099-12-31")
        d    = task.to_dict()
        assert d["type"]     == "deadline"
        assert d["due_date"] == "2099-12-31"
```

**`tests/test_parser.py`:**

```python
# tests/test_parser.py
import pytest
from taskflow.parser import parse_task_input, parse_and_create, ParseResult
from taskflow.core.task_types import UrgentTask, RecurringTask, DeadlineTask
from taskflow.core.task import Task
from taskflow.errors import ValidationError


class TestParseTaskInput:

    def test_simple_title(self):
        result = parse_task_input("Review PR")
        assert result.title     == "Review PR"
        assert result.task_type == "standard"

    def test_priority_token(self):
        result = parse_task_input("Review PR #high")
        assert result.priority == "high"
        assert result.title    == "Review PR"

    def test_category_token(self):
        result = parse_task_input("Review PR @work")
        assert result.category == "work"
        assert result.title    == "Review PR"

    def test_due_date_token(self):
        result = parse_task_input("Submit report !2099-12-31")
        assert result.due_date   == "2099-12-31"
        assert result.task_type  == "deadline"

    def test_urgent_prefix(self):
        result = parse_task_input("!! Server down")
        assert result.is_urgent  is True
        assert result.priority   == "high"
        assert result.task_type  == "urgent"
        assert result.title      == "Server down"

    def test_recurring_prefix(self):
        result = parse_task_input("~daily Standup @work")
        assert result.recurrence == "daily"
        assert result.task_type  == "recurring"
        assert result.title      == "Standup"

    def test_multiple_tokens(self):
        result = parse_task_input("Submit report #high @work !2099-12-31")
        assert result.title     == "Submit report"
        assert result.priority  == "high"
        assert result.category  == "work"
        assert result.due_date  == "2099-12-31"
        assert result.task_type == "deadline"

    def test_empty_input_raises(self):
        with pytest.raises(ValidationError):
            parse_task_input("")

    def test_whitespace_only_raises(self):
        with pytest.raises(ValidationError):
            parse_task_input("   ")

    def test_invalid_category_raises(self):
        with pytest.raises(ValidationError):
            parse_task_input("Task @invalid_category")

    def test_invalid_date_raises(self):
        with pytest.raises(ValidationError):
            parse_task_input("Task !31-12-2099")

    @pytest.mark.parametrize("recurrence", ["daily", "weekly", "monthly"])
    def test_all_recurrences(self, recurrence):
        result = parse_task_input(f"~{recurrence} Standup")
        assert result.recurrence == recurrence


class TestParseAndCreate:

    def test_creates_urgent_task(self):
        task = parse_and_create("!! Server down @work")
        assert isinstance(task, UrgentTask)

    def test_creates_recurring_task(self):
        task = parse_and_create("~daily Standup @work")
        assert isinstance(task, RecurringTask)

    def test_creates_deadline_task(self):
        task = parse_and_create("Submit report !2099-12-31")
        assert isinstance(task, DeadlineTask)

    def test_creates_standard_task(self):
        task = parse_and_create("Review PR #high @work")
        assert isinstance(task, Task)
        assert not isinstance(task, (UrgentTask, RecurringTask, DeadlineTask))
```

**`tests/test_storage.py`:**

```python
# tests/test_storage.py
import json
import pytest
from pathlib import Path
from taskflow.core.task import Task
from taskflow.core.task_types import UrgentTask, RecurringTask
from taskflow.storage.json_store import (
    save_tasks, load_tasks, load_tasks_safe,
    get_next_id, backup_tasks,
)
from taskflow.errors import StorageError


class TestSaveTasks:

    def test_creates_file(self, tmp_path, one_task):
        filepath = tmp_path / "tasks.json"
        save_tasks(one_task, filepath=filepath)
        assert filepath.exists()

    def test_creates_parent_directory(self, tmp_path, one_task):
        filepath = tmp_path / "subdir" / "tasks.json"
        save_tasks(one_task, filepath=filepath)
        assert filepath.exists()

    def test_file_is_valid_json(self, tmp_path, one_task):
        filepath = tmp_path / "tasks.json"
        save_tasks(one_task, filepath=filepath)
        content = json.loads(filepath.read_text())
        assert isinstance(content, list)
        assert len(content) == 1

    def test_save_empty_list(self, tmp_path):
        filepath = tmp_path / "tasks.json"
        save_tasks([], filepath=filepath)
        content = json.loads(filepath.read_text())
        assert content == []


class TestLoadTasks:

    def test_returns_empty_list_when_file_missing(self, tmp_path):
        filepath = tmp_path / "nonexistent.json"
        tasks = load_tasks(filepath=filepath)
        assert tasks == []

    def test_roundtrip(self, tmp_path, mixed_tasks):
        filepath = tmp_path / "tasks.json"
        save_tasks(mixed_tasks, filepath=filepath)
        loaded = load_tasks(filepath=filepath)
        assert len(loaded) == len(mixed_tasks)
        assert loaded[0].title    == mixed_tasks[0].title
        assert loaded[0].priority == mixed_tasks[0].priority

    def test_raises_on_invalid_json(self, tmp_path):
        filepath = tmp_path / "tasks.json"
        filepath.write_text("{not valid json}", encoding="utf-8")
        with pytest.raises(StorageError):
            load_tasks(filepath=filepath)

    def test_raises_on_non_list_json(self, tmp_path):
        filepath = tmp_path / "tasks.json"
        filepath.write_text('{"key": "value"}', encoding="utf-8")
        with pytest.raises(StorageError):
            load_tasks(filepath=filepath)

    def test_restores_urgent_task_type(self, tmp_path):
        tasks    = [UrgentTask("Server down", "work")]
        filepath = tmp_path / "tasks.json"
        save_tasks(tasks, filepath=filepath)
        loaded = load_tasks(filepath=filepath)
        assert isinstance(loaded[0], UrgentTask)

    def test_restores_done_state(self, tmp_path, one_task):
        one_task[0].mark_done()
        filepath = tmp_path / "tasks.json"
        save_tasks(one_task, filepath=filepath)
        loaded = load_tasks(filepath=filepath)
        assert loaded[0].done is True


class TestLoadTasksSafe:

    def test_returns_empty_list_on_error(self, tmp_path):
        filepath = tmp_path / "corrupt.json"
        filepath.write_text("not json", encoding="utf-8")
        tasks, error = load_tasks_safe(filepath=filepath)
        assert tasks == []
        assert error is not None
        assert isinstance(error, str)

    def test_returns_tasks_and_none_on_success(self, tmp_path, one_task):
        filepath = tmp_path / "tasks.json"
        save_tasks(one_task, filepath=filepath)
        tasks, error = load_tasks_safe(filepath=filepath)
        assert len(tasks) == 1
        assert error is None


class TestGetNextId:

    def test_returns_one_for_empty_list(self):
        assert get_next_id([]) == 1

    def test_returns_max_plus_one(self):
        tasks = [
            Task("A", "low", "work", task_id=5),
            Task("B", "low", "work", task_id=3),
            Task("C", "low", "work", task_id=9),
        ]
        assert get_next_id(tasks) == 10


class TestBackupTasks:

    def test_creates_backup_file(self, tmp_path, one_task):
        filepath = tmp_path / "tasks.json"
        save_tasks(one_task, filepath=filepath)
        result = backup_tasks(filepath=filepath)
        assert result is True
        backup_files = list(tmp_path.glob("*backup*.json"))
        assert len(backup_files) == 1

    def test_returns_false_when_no_source(self, tmp_path):
        filepath = tmp_path / "nonexistent.json"
        result = backup_tasks(filepath=filepath)
        assert result is False
```

---

### Running the Full Suite with Coverage

```bash
# Install coverage
pip install pytest-cov

# Run with coverage report
pytest tests/ -v --cov=taskflow --cov-report=term-missing

# Generate HTML report
pytest tests/ --cov=taskflow --cov-report=html
open htmlcov/index.html
```

Set a coverage gate in `pyproject.toml`:

```toml
[tool.coverage.report]
fail_under = 75   # fail the test run if coverage drops below 75%
```

---

## Checkpoint

Before moving to Day 26:

- [ ] `tests/test_task.py` — all tests pass, >90% coverage on `core/task.py`
- [ ] `tests/test_task_types.py` — all tests pass
- [ ] `tests/test_parser.py` — all tests pass
- [ ] `tests/test_storage.py` — all tests pass
- [ ] `tests/test_services.py` — all tests from Day 22 still pass
- [ ] `conftest.py` has all shared fixtures
- [ ] `pytest --cov=taskflow` shows overall coverage >70%
- [ ] CI-safe: no network calls, no `print()` in tests, no file system side effects outside `tmp_path`

---

## What's Coming

On **Day 26** we cover test coverage, mocking, and fixtures in depth — `unittest.mock`, `monkeypatch`, `pytest-mock`, patching network calls, and building a test suite that covers the weather integration and CLI commands without actually hitting the internet or the real filesystem.
