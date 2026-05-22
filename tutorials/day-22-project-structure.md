# Day 22 — Project Structure Deep Dive

> **Series:** Python & AI Engineering — Zero to Production
> **Phase:** 2 — Real Engineering
> **Python Version:** 3.14
> **Project:** TaskFlow AI — Finalising package layout, resolving TD-002

---

## Learning Objective

By the end of today, every module in TaskFlow AI has a single clear responsibility, the Task object / dict inconsistency (TD-002) is resolved, all `__init__.py` files accurately reflect their package's public API, and the project layout matches what a professional Python open-source project looks like. No new features — pure structural clarity.

---

## What We Build Today

A finalised, consistent package structure with TD-002 resolved, a new `taskflow/services.py` fully wired into `commands.py`, `taskflow/utils.py` integrated everywhere it is needed, and a complete `docs/` directory with architecture artefacts.

```
taskflow-project/
├── taskflow/               ← application package
│   ├── __init__.py         ← public API
│   ├── config.py           ← all constants
│   ├── errors.py           ← exception hierarchy
│   ├── services.py         ← pure business logic (new Day 21)
│   ├── utils.py            ← shared helpers (new Day 21)
│   ├── parser.py           ← input parser
│   ├── filters.py          ← TaskFilter pipeline
│   ├── decorators.py       ← @timer, @retry, etc.
│   ├── context.py          ← context managers
│   ├── shell.py            ← interactive loop
│   ├── cli.py              ← argparse one-shot
│   ├── main.py             ← entry point
│   ├── core/
│   │   ├── __init__.py
│   │   ├── task.py
│   │   ├── task_types.py
│   │   ├── task_factory.py
│   │   └── stats.py
│   ├── storage/
│   │   ├── __init__.py
│   │   └── json_store.py
│   ├── integrations/
│   │   ├── __init__.py
│   │   └── weather.py
│   └── display/
│       ├── __init__.py
│       ├── renderer.py     ← only module that calls print()
│       └── commands.py     ← thin command handlers
├── tests/
│   ├── __init__.py
│   ├── conftest.py         ← shared fixtures (today)
│   └── test_services.py    ← first real tests (today)
├── docs/
│   ├── architecture.md     ← system diagram description
│   ├── technical-debt.md   ← updated
│   └── adr/
│       ├── ADR-001.md
│       └── ADR-002.md
├── scripts/
│   └── setup.sh
├── data/                   ← git-ignored runtime data
├── run.py
├── pyproject.toml
├── requirements.in
├── requirements-dev.in
├── .gitignore
├── .env.example
├── .pre-commit-config.yaml
├── README.md
└── CHANGELOG.md
```

---

## Concepts Covered

- Module responsibility mapping — what belongs where
- Resolving TD-002: standardising on Task objects everywhere
- The `__init__.py` as a public contract — what to export and what to hide
- `conftest.py` — shared test fixtures
- `tests/` directory structure
- `src/` layout vs flat layout — when to use each
- Import discipline — relative vs absolute within a package
- Verifying no circular imports with `pydeps`
- The principle of least privilege for modules

---

## Full Tutorial

### Module Responsibility Map

Before making any changes, write down what each module is supposed to do. If you cannot describe a module in one sentence, it has too many responsibilities.

```
config.py       — Store all constants. Never import from other taskflow modules.
errors.py       — Define exception types. Never import from other taskflow modules.
utils.py        — Shared pure helpers (task_attr, pluralise). No business logic.
services.py     — Pure business logic. No print(), no input(). Testable in isolation.
parser.py       — Convert raw strings to ParseResult and Task objects.
filters.py      — Composable TaskFilter pipeline. Pure queries.
decorators.py   — Cross-cutting function wrappers. No business logic.
context.py      — Context managers for safe operations.
core/task.py    — Task domain model and behaviour.
core/task_types.py — Task subclasses.
core/task_factory.py — Polymorphic deserialisation.
core/stats.py   — Pure statistics calculations.
storage/json_store.py — Read and write tasks to disk. Atomic. No business logic.
integrations/weather.py — Fetch and parse weather data.
display/renderer.py — ALL terminal output. The only module that calls print().
display/commands.py — Thin command handlers. Collect input, call services, show output.
shell.py        — Interactive command loop dispatcher.
cli.py          — argparse one-shot command dispatcher.
main.py         — Application orchestration entry point.
```

Print this map. Put it on your wall. If you ever catch yourself violating one of these single sentences, stop and restructure.

---

### Resolving TD-002 — Standardising on Task Objects

The problem: `renderer.py`, `commands.py`, `shell.py`, and `services.py` all have `isinstance(task, Task)` checks because sometimes tasks are `Task` objects and sometimes they are plain dicts.

The fix: **standardise on `Task` objects everywhere in memory.** Dicts only appear at the serialisation boundary (JSON file in, JSON file out).

**The rule:**
- `json_store.load_tasks()` returns `list[Task]` — already done ✓
- `json_store.save_tasks()` accepts `list[Task]` and calls `.to_dict()` internally — already done ✓
- `display/renderer.py` accepts `list[Task]` only — needs updating
- `services.py` accepts `list[Task]` only — use type hints to enforce
- Remove all `isinstance(task, Task) / task.get(key)` dual-path code

**Update `renderer.py`** — remove dict fallbacks:

```python
# taskflow/display/renderer.py — updated for Day 22

def display_tasks(tasks: list[Task]) -> None:
    """
    Display a list of Task objects as a formatted table.

    Args:
        tasks (list[Task]): Task objects to display.
                            Plain dicts are no longer accepted.
    """
    if not tasks:
        print("\n  No tasks to display. Type 'add' to create one.\n")
        return

    col = {"num": 4, "title": 26, "priority": 10, "category": 13}
    width = sum(col.values()) + 10
    div   = "  " + "─" * width

    print()
    print(div)
    print(
        f"  {'#':<{col['num']}}"
        f"{'Title':<{col['title']}}"
        f"{'Priority':<{col['priority']}}"
        f"{'Category':<{col['category']}}"
        f"Status"
    )
    print(div)

    for i, task in enumerate(tasks, start=1):
        from ..utils import truncate
        from ..core.task_types import DeadlineTask, RecurringTask, UrgentTask

        title  = truncate(task.title, col["title"] - 1)
        status = "✓ done" if task.done else "pending"
        extra  = ""

        if isinstance(task, DeadlineTask):
            extra = f" {task.urgency_label}"
        elif isinstance(task, RecurringTask):
            extra = f" {task.recurrence_label}"
        elif isinstance(task, UrgentTask):
            extra = " 🚨"

        print(
            f"  {i:<{col['num']}}"
            f"{title:<{col['title']}}"
            f"{task.priority.upper():<{col['priority']}}"
            f"{task.category:<{col['category']}}"
            f"{status}{extra}"
        )

    print(div)

    total   = len(tasks)
    done    = sum(1 for t in tasks if t.done)
    pending = total - done
    rate    = round(done / total * 100, 1) if total > 0 else 0.0
    print(
        f"  {total} task{'s' if total != 1 else ''} · "
        f"{pending} pending · {done} done · {rate}% complete"
    )
    print()
```

Now `renderer.py` only works with `Task` objects. The `_attr()` / `_done()` helpers are deleted. The code is half as long and entirely unambiguous.

---

### `conftest.py` — Shared Test Fixtures

Create `tests/conftest.py` — pytest loads this automatically before every test:

```python
# tests/conftest.py
# TaskFlow AI — shared pytest fixtures.
#
# A fixture is a reusable piece of test setup. Instead of creating
# a Task or a task list in every test, we define it once here and
# let pytest inject it automatically.

import pytest
from taskflow.core.task       import Task
from taskflow.core.task_types import UrgentTask, RecurringTask, DeadlineTask


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
```

---

### First Real Tests — `tests/test_services.py`

```python
# tests/test_services.py
# TaskFlow AI — unit tests for the services layer.
#
# These tests verify business logic in complete isolation —
# no display, no file I/O, no network.

import pytest
from taskflow.core.task       import Task
from taskflow.core.task_types import RecurringTask
from taskflow.errors          import ValidationError, TaskNotFoundError
from taskflow.services        import (
    add_task_to_list,
    remove_task_by_index,
    remove_task_by_id,
    mark_task_done,
    rename_task,
    find_task_by_id,
    find_task_index_by_id,
    is_at_limit,
    filter_tasks,
    search_tasks,
    get_summary_stats,
)


class TestAddTask:
    def test_adds_task_to_list(self, empty_tasks):
        task = Task("Review PR", "high", "work")
        result = add_task_to_list(empty_tasks, task, plan="premium")
        assert len(empty_tasks) == 1
        assert result is task

    def test_raises_at_free_plan_limit(self, ten_free_tasks):
        extra = Task("One too many", "low", "personal")
        with pytest.raises(ValidationError):
            add_task_to_list(ten_free_tasks, extra, plan="free")

    def test_allows_up_to_limit(self, empty_tasks):
        for i in range(10):
            add_task_to_list(
                empty_tasks, Task(f"Task {i}", "low", "personal"),
                plan="free"
            )
        assert len(empty_tasks) == 10


class TestRemoveTask:
    def test_remove_by_index(self, one_task):
        removed = remove_task_by_index(one_task, 0)
        assert removed.title == "Review PR"
        assert len(one_task) == 0

    def test_remove_by_index_out_of_range(self, one_task):
        with pytest.raises(IndexError):
            remove_task_by_index(one_task, 99)

    def test_remove_by_id(self, one_task):
        task_id = one_task[0].id
        removed = remove_task_by_id(one_task, task_id)
        assert removed.id == task_id
        assert len(one_task) == 0

    def test_remove_by_id_not_found(self, one_task):
        with pytest.raises(TaskNotFoundError):
            remove_task_by_id(one_task, 9999)


class TestMarkDone:
    def test_marks_standard_task_done(self, one_task):
        result = mark_task_done(one_task, 0)
        assert result.done is True
        assert result.status == "done"

    def test_raises_if_already_done(self, one_task):
        mark_task_done(one_task, 0)
        with pytest.raises(ValidationError):
            mark_task_done(one_task, 0)

    def test_recurring_task_resets(self, empty_tasks):
        task = RecurringTask("Daily standup", "medium", "work", "daily")
        empty_tasks.append(task)
        result = mark_task_done(empty_tasks, 0)
        assert result.done is False           # reset to pending
        assert result.completion_count == 1   # counter incremented

    def test_raises_if_index_out_of_range(self, one_task):
        with pytest.raises(IndexError):
            mark_task_done(one_task, 99)


class TestRenameTask:
    def test_renames_successfully(self, one_task):
        result = rename_task(one_task, 0, "Updated title")
        assert result.title == "Updated title"

    def test_raises_on_empty_title(self, one_task):
        with pytest.raises(ValidationError):
            rename_task(one_task, 0, "")

    def test_raises_on_title_too_long(self, one_task):
        with pytest.raises(ValidationError):
            rename_task(one_task, 0, "x" * 201)

    def test_strips_whitespace(self, one_task):
        rename_task(one_task, 0, "  Trimmed  ")
        assert one_task[0].title == "Trimmed"


class TestFindTask:
    def test_find_by_id(self, mixed_tasks):
        task = mixed_tasks[0]
        found = find_task_by_id(mixed_tasks, task.id)
        assert found is task

    def test_find_by_id_not_found(self, mixed_tasks):
        with pytest.raises(TaskNotFoundError):
            find_task_by_id(mixed_tasks, 9999)

    def test_find_index_by_id(self, mixed_tasks):
        task  = mixed_tasks[2]
        index = find_task_index_by_id(mixed_tasks, task.id)
        assert index == 2


class TestFilterTasks:
    def test_filter_by_priority(self, mixed_tasks):
        high = filter_tasks(mixed_tasks, priority="high")
        assert all(t.priority == "high" for t in high)

    def test_filter_pending_only(self, mixed_tasks):
        pending = filter_tasks(mixed_tasks, is_done=False)
        assert all(not t.done for t in pending)

    def test_filter_done_only(self, mixed_tasks):
        done = filter_tasks(mixed_tasks, is_done=True)
        assert all(t.done for t in done)

    def test_limit(self, mixed_tasks):
        limited = filter_tasks(mixed_tasks, limit=2)
        assert len(limited) == 2

    def test_no_filters_returns_all(self, mixed_tasks):
        all_tasks = filter_tasks(mixed_tasks)
        assert len(all_tasks) == len(mixed_tasks)


class TestSearchTasks:
    def test_finds_by_keyword(self, mixed_tasks):
        results = search_tasks(mixed_tasks, "review")
        assert any("Review" in t.title for t in results)

    def test_case_insensitive(self, mixed_tasks):
        results = search_tasks(mixed_tasks, "REVIEW")
        assert len(results) > 0

    def test_no_match_returns_empty(self, mixed_tasks):
        results = search_tasks(mixed_tasks, "xyzzy_no_match")
        assert results == []


class TestGetSummaryStats:
    def test_stats_on_mixed_tasks(self, mixed_tasks):
        stats = get_summary_stats(mixed_tasks)
        assert stats["total"] == len(mixed_tasks)
        assert stats["done"] == 1     # only "Write tests" is done
        assert stats["pending"] == len(mixed_tasks) - 1

    def test_stats_empty_list(self, empty_tasks):
        stats = get_summary_stats(empty_tasks)
        assert stats == {"total": 0, "done": 0, "pending": 0, "rate": 0.0}
```

Run the tests:

```bash
pytest tests/test_services.py -v
```

All tests should pass. This is the first real automated test suite for TaskFlow AI.

---

### Verifying Import Cleanliness

```bash
# Check for circular imports
python -c "import taskflow; print('No circular imports ✓')"

# Check mypy on the full package
mypy taskflow/ --ignore-missing-imports

# Run ruff linter
ruff check taskflow/

# Check import structure
python -c "
from taskflow.services  import add_task_to_list
from taskflow.utils     import task_attr, pluralise, truncate
from taskflow           import Task, load_tasks, save_tasks
print('All top-level imports OK ✓')
"
```

---

## Exercises

**Exercise 1 — `__init__.py` audit.**
Open every `__init__.py` file. For each name in `__all__`, confirm it is actually useful to import from the package level. Remove anything that is an internal implementation detail. Add anything that a caller would reasonably need but cannot currently import cleanly.

**Exercise 2 — Remove all dict fallbacks.**
Search for `isinstance(task, Task)` in `renderer.py`, `commands.py`, and `services.py`. Every remaining dual-path code block is a TD-002 remnant. Remove it — Task objects only.

**Exercise 3 — `conftest.py` fixtures.**
Add three more fixtures to `tests/conftest.py`:
- `premium_tasks` — 50 tasks, testing premium limit
- `overdue_task` — a Task with `created_at` set to 30 days ago
- `all_task_types` — one of each: Task, UrgentTask, RecurringTask, DeadlineTask

**Exercise 4 — Test `core/task.py`.**
Write `tests/test_task.py` with at least 10 tests covering: `Task.__init__()` validation, `mark_done()`, `mark_pending()`, `rename()`, `is_overdue()`, `to_dict()` / `from_dict()` round-trip, `__eq__()`, `__lt__()`, `__hash__()`.

**Exercise 5 — `src/` layout exploration.**
Read about the `src/` layout (`src/taskflow/` instead of `taskflow/`). Update `pyproject.toml` to use `src/` layout. Move the `taskflow/` directory into `src/`. Verify `python run.py` still works. Move it back. Understand the trade-offs and document your decision in a new ADR.

**Exercise 6 (stretch) — Coverage report.**
Run the full test suite with coverage:

```bash
pytest --cov=taskflow --cov-report=html tests/
```

Open `htmlcov/index.html` in your browser. Which modules have 0% coverage? Which have 100%? Set a coverage target in `pyproject.toml`:

```toml
[tool.coverage.report]
fail_under = 30   # we will raise this day by day
```

---

## Checkpoint

Before moving to Day 23:

- [ ] Every module's responsibility can be described in one sentence
- [ ] TD-002 is resolved — `renderer.py` accepts only Task objects
- [ ] `taskflow/services.py` contains all business logic, no print()
- [ ] `taskflow/utils.py` is imported by all modules that previously duplicated helpers
- [ ] `tests/conftest.py` exists with at least 4 fixtures
- [ ] `tests/test_services.py` has all tests passing
- [ ] No circular imports — `python -c "import taskflow"` runs cleanly
- [ ] `mypy taskflow/` reports zero errors on `services.py` and `utils.py`
- [ ] TD-002 marked as resolved in `docs/technical-debt.md`

---

## Common Errors on Day 22

**Circular import introduced by services.py:**

```
taskflow/services.py imports from taskflow/core/task.py ✓
taskflow/core/task.py must NOT import from taskflow/services.py ✗
```

If `core/task.py` needs something from `services.py`, that is a sign the dependency direction is wrong. Move the shared logic to `utils.py` or `config.py` instead.

**`isinstance` check left in renderer.py:**

After the TD-002 fix, `renderer.py` should not contain a single `isinstance(task, Task)` check. If it does, you have a dict leaking through from somewhere — trace it back to `commands.py` or `services.py` and fix it there.

**Fixture not resetting Task counter:**

If tests pass in isolation but fail when run together, the Task counter is not being reset. Verify `conftest.py` has the `autouse=True` fixture and it calls `Task.reset_counter()` both before and after each test.

---

## What's Coming

On **Day 23** we add professional logging to replace every remaining `print()` call outside `renderer.py`, add log levels, rotating file handlers, and structured JSON logging. TaskFlow AI gains the observability needed to run as a long-running process — which prepares us for the FastAPI server in Phase 3.