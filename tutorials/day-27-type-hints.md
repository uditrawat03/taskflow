# Day 27 — Type Hints & Mypy

> **Series:** Python & AI Engineering — Zero to Production
> **Phase:** 2 — Real Engineering
> **Python Version:** 3.14
> **Project:** TaskFlow AI — Full type annotation and static analysis

---

## Learning Objective

By the end of today, every public function in TaskFlow AI has type hints, `mypy --strict` passes on `core/`, `services.py`, and `storage/`, and you understand the full Python typing system — `Optional`, `Union`, generics, `Protocol`, `TypeVar`, `overload`, and Python 3.14's new type features. Type hints are machine-checked documentation that catches bugs before runtime.

---

## What We Build Today

Complete type annotation across all modules, a `mypy` configuration that runs in strict mode for core modules and lenient mode for display/integration code, and a `TypedDict` definition for the weather data structure.

```bash
$ mypy taskflow/core/ taskflow/services.py taskflow/storage/ --strict

Success: no issues found in 8 source files

$ mypy taskflow/ --ignore-missing-imports

taskflow/display/commands.py:142: error: Incompatible return value type
  (got "None", expected "Task")
Found 1 error in 1 file
```

---

## Concepts Covered

- Basic type annotations — `str`, `int`, `bool`, `float`, `None`
- Container types — `list[Task]`, `dict[str, int]`, `set[str]`
- `Optional[X]` and `X | None` — nullable types
- `Union[X, Y]` and `X | Y` — multiple possible types
- Return type `None` vs no annotation
- `TypeVar` — generic functions
- `Generic[T]` — generic classes
- `Protocol` — structural subtyping
- `TypedDict` — typed dictionaries
- `@overload` — multiple function signatures
- `cast()` — explicit type assertions
- `TYPE_CHECKING` — avoiding circular imports from type annotations
- Python 3.14 type system improvements
- `mypy` configuration in `pyproject.toml`
- Running mypy in CI

---

## Full Tutorial

### Why Type Hints?

Python is dynamically typed — you never have to declare types. But you can annotate them, and doing so gives you:

1. **IDE intelligence** — autocomplete knows `task.title` is a `str`, not any object
2. **Static analysis** — mypy finds type errors before you run the code
3. **Documentation** — function signatures explain what goes in and what comes out
4. **Refactoring safety** — change a type and mypy shows every call site that breaks

Type hints do not affect runtime behaviour. They are checked by tools like `mypy` and ignored by the Python interpreter.

---

### Basic Annotations

```python
# Variable annotations
name:     str   = "Udit"
age:      int   = 24
is_admin: bool  = False
rate:     float = 0.75

# Function annotations
def greet(name: str, times: int = 1) -> str:
    return f"Hello, {name}! " * times

# No return value
def log_error(message: str) -> None:
    print(f"ERROR: {message}")
```

**Python 3.14:** Since Python 3.10, you can use `X | Y` instead of `Union[X, Y]` and `X | None` instead of `Optional[X]`. Python 3.14 extends this with **deferred annotation evaluation** — annotations are not evaluated at import time, eliminating most forward reference issues.

```python
# Python 3.10+ style (preferred in this series)
def find_task(tasks: list[Task], task_id: int) -> Task | None:
    ...

# Pre-3.10 style (still valid but verbose)
from typing import List, Optional
def find_task(tasks: List[Task], task_id: int) -> Optional[Task]:
    ...
```

---

### Container Types

```python
from pathlib import Path

# Lists
tasks:      list[Task]       = []
titles:     list[str]        = ["Review PR", "Buy groceries"]
scores:     list[int]        = [3, 2, 1]

# Dicts
settings:   dict[str, str]   = {"theme": "dark"}
counts:     dict[str, int]   = {"high": 3, "medium": 2}
id_map:     dict[int, Task]  = {}

# Sets
priorities: set[str]         = {"high", "medium", "low"}

# Tuples
point:      tuple[float, float]      = (28.6, 77.2)
rgb:        tuple[int, int, int]     = (255, 128, 0)
any_ints:   tuple[int, ...]          = (1, 2, 3, 4, 5)   # variable length

# Nested
task_groups: dict[str, list[Task]]   = {}
matrix:      list[list[int]]         = [[1, 2], [3, 4]]
```

---

### `TypedDict` — Typing Dictionary Structures

For dictionaries with a fixed schema (like the weather dict), `TypedDict` gives you full type-checking:

```python
from typing import TypedDict

class WeatherData(TypedDict):
    location:    str
    temperature: float
    feels_like:  float
    humidity:    int
    wind_speed:  float
    condition:   str
    emoji:       str
    fetched_at:  str


class ForecastDay(TypedDict):
    date:      str
    max_temp:  float | None
    min_temp:  float | None
    condition: str
    emoji:     str
    rain_prob: int | None
```

Now `fetch_weather()` returns `WeatherData | None` and mypy knows exactly which keys it has:

```python
def fetch_weather(
    latitude:      float,
    longitude:     float,
    location_name: str = "Your Location",
    use_cache:     bool = True,
) -> WeatherData | None:
    ...
```

---

### `TypeVar` — Generic Functions

```python
from typing import TypeVar

T = TypeVar("T")

def first_or_none(items: list[T]) -> T | None:
    """Return the first item or None if list is empty."""
    return items[0] if items else None

# mypy knows the return type matches the input type
task:   Task | None = first_or_none([Task("A", "low", "work")])
number: int  | None = first_or_none([1, 2, 3])
```

---

### `Protocol` — Structural Subtyping

`Protocol` defines an interface by structure (duck typing) rather than inheritance. Any class that has the required methods satisfies the protocol — no explicit `class MyClass(Protocol)` inheritance needed:

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Serialisable(Protocol):
    """Any object that can be converted to a dict for JSON storage."""
    def to_dict(self) -> dict: ...

@runtime_checkable
class Markable(Protocol):
    """Any object that can be marked done."""
    done: bool
    def mark_done(self) -> "Markable": ...
    def mark_pending(self) -> "Markable": ...


def save_any(items: list[Serialisable], filepath: Path) -> None:
    """Save any list of serialisable objects to JSON."""
    import json
    with open(filepath, "w") as f:
        json.dump([item.to_dict() for item in items], f)


# Task satisfies Serialisable without inheriting from it
task = Task("Review PR", "high", "work")
assert isinstance(task, Serialisable)   # True — runtime_checkable
```

---

### `@overload` — Multiple Signatures

When a function can return different types depending on its arguments, `@overload` lets you declare each signature separately:

```python
from typing import overload

@overload
def get_tasks(tasks: list[Task], *, done: bool) -> list[Task]: ...
@overload
def get_tasks(tasks: list[Task]) -> list[Task]: ...

def get_tasks(tasks: list[Task], *, done: bool | None = None) -> list[Task]:
    """Return tasks, optionally filtered by done status."""
    if done is None:
        return list(tasks)
    return [t for t in tasks if t.done == done]
```

The `@overload` decorators are only for type checkers — the actual implementation is the final undecorated function.

---

### `TYPE_CHECKING` — Avoiding Circular Import Errors

Sometimes you need to import a type for annotation purposes, but the import would create a circular dependency at runtime:

```python
from __future__ import annotations   # Python 3.14 makes this the default via lazy annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from taskflow.core.task import Task   # only imported during type checking
    from taskflow.storage.json_store import StorageBackend

def process(task: "Task") -> None:   # without __future__.annotations, need string literal
    ...
```

In Python 3.14, annotation evaluation is deferred by default (PEP 649), which largely eliminates this problem. But `TYPE_CHECKING` is still useful for avoiding heavy imports.

---

### Fully Annotated `taskflow/services.py`

```python
# taskflow/services.py — fully annotated version

from __future__ import annotations
from typing import TYPE_CHECKING

from .config import PLAN_LIMITS, USER_PLAN, OVERDUE_THRESHOLD_DAYS
from .errors import ValidationError, TaskNotFoundError
from .core.task       import Task
from .core.task_types import RecurringTask
from .core.stats      import calculate_stats

if TYPE_CHECKING:
    pass   # no circular-import-only types needed currently


def get_task_limit(plan: str | None = None) -> int:
    """Return the task limit for the given plan name."""
    p: str = plan or USER_PLAN
    return PLAN_LIMITS.get(p, PLAN_LIMITS["free"])


def is_at_limit(tasks: list[Task], plan: str | None = None) -> bool:
    """Return True if the task list has reached its plan limit."""
    return len(tasks) >= get_task_limit(plan)


def add_task_to_list(
    tasks: list[Task],
    task:  Task,
    plan:  str | None = None,
) -> Task:
    """Append a Task to the list after checking the plan limit."""
    limit: int = get_task_limit(plan)
    if len(tasks) >= limit:
        raise ValidationError(
            f"Task limit reached ({limit} tasks on {plan or USER_PLAN} plan).",
            field="tasks",
            value=len(tasks),
        )
    tasks.append(task)
    return task


def remove_task_by_index(tasks: list[Task], index: int) -> Task:
    """Remove a task at the given 0-based index."""
    if not (0 <= index < len(tasks)):
        raise IndexError(f"Index {index} out of range for {len(tasks)} tasks.")
    return tasks.pop(index)


def remove_task_by_id(tasks: list[Task], task_id: int) -> Task:
    """Remove a task by its ID."""
    index: int = find_task_index_by_id(tasks, task_id)
    return tasks.pop(index)


def mark_task_done(tasks: list[Task], index: int) -> Task:
    """Mark a task as done. Handles RecurringTask reset behaviour."""
    if not (0 <= index < len(tasks)):
        raise IndexError(f"Index {index} out of range.")
    task: Task = tasks[index]
    if isinstance(task, Task) and task.done and not isinstance(task, RecurringTask):
        raise ValidationError(
            f"Task '{task.title}' is already done.", field="done", value=True
        )
    task.mark_done()
    return task


def rename_task(tasks: list[Task], index: int, new_title: str) -> Task:
    """Rename a task at the given index with validation."""
    if not (0 <= index < len(tasks)):
        raise IndexError(f"Index {index} out of range.")
    new_title = new_title.strip()
    if not new_title:
        raise ValidationError("Title cannot be empty.", field="title", value=new_title)
    if len(new_title) > 200:
        raise ValidationError("Title too long.", field="title", value=len(new_title))
    task: Task = tasks[index]
    task.rename(new_title)
    return task


def find_task_by_id(tasks: list[Task], task_id: int) -> Task:
    """Find and return a task by its ID."""
    for task in tasks:
        if task.id == task_id:
            return task
    raise TaskNotFoundError(task_id)


def find_task_index_by_id(tasks: list[Task], task_id: int) -> int:
    """Return the 0-based index of a task by its ID."""
    for i, task in enumerate(tasks):
        if task.id == task_id:
            return i
    raise TaskNotFoundError(task_id)


def filter_tasks(
    tasks:        list[Task],
    priority:     str | None   = None,
    category:     str | None   = None,
    is_done:      bool | None  = None,
    overdue_only: bool         = False,
    limit:        int | None   = None,
) -> list[Task]:
    """Apply filters to a task list and return a new filtered list."""
    result: list[Task] = list(tasks)

    if priority is not None:
        result = [t for t in result if t.priority == priority.lower()]
    if category is not None:
        result = [t for t in result if t.category == category.lower()]
    if is_done is True:
        result = [t for t in result if t.done]
    elif is_done is False:
        result = [t for t in result if not t.done]
    if overdue_only:
        result = [t for t in result if t.is_overdue()]
    if limit is not None:
        result = result[:limit]

    return result


def search_tasks(tasks: list[Task], keyword: str) -> list[Task]:
    """Return tasks whose titles contain keyword (case-insensitive)."""
    kw: str = keyword.strip().lower()
    return [t for t in tasks if kw in t.title.lower()]


def get_overdue_tasks(tasks: list[Task]) -> list[Task]:
    """Return all overdue tasks."""
    return [t for t in tasks if t.is_overdue()]


def get_summary_stats(tasks: list[Task]) -> dict[str, int | float]:
    """Return summary statistics for the task list."""
    return calculate_stats(tasks)
```

---

### `mypy` Configuration in `pyproject.toml`

```toml
[tool.mypy]
python_version          = "3.14"
warn_return_any         = true
warn_unused_configs     = true
warn_redundant_casts    = true
warn_unused_ignores     = true
no_implicit_optional    = true
strict_equality         = true
ignore_missing_imports  = true

# Strict mode for core business logic
[[tool.mypy.overrides]]
module               = ["taskflow.core.*", "taskflow.services", "taskflow.storage.*"]
strict               = true
disallow_untyped_defs = true
disallow_any_generics = true

# Lenient mode for display and integration code (has more any-typed dependencies)
[[tool.mypy.overrides]]
module                        = ["taskflow.display.*", "taskflow.integrations.*"]
disallow_untyped_defs         = false
warn_return_any               = false
```

Run mypy:

```bash
# Check core modules strictly
mypy taskflow/core/ taskflow/services.py taskflow/storage/ --strict

# Check everything with lenient settings
mypy taskflow/ --ignore-missing-imports

# In CI — fail on any error
mypy taskflow/ --ignore-missing-imports --no-error-summary
```

---

## Exercises

**Exercise 1 — Annotate `taskflow/utils.py`.**
Add complete type hints to every function in `utils.py`. Include return types, parameter types, and any complex generic types. Run `mypy taskflow/utils.py --strict` — fix every error.

**Exercise 2 — `TypedDict` for Settings.**
Convert the `Settings` dataclass in `env_config.py` to use `TypedDict` for its nested dict structures. Or alternatively, keep the dataclass but add explicit `TypedDict` for the return type of `to_dict()` (if you add one). Verify mypy is happy.

**Exercise 3 — `Protocol` for storage.**
Define a `StorageBackend` Protocol in `taskflow/protocols.py`:

```python
from typing import Protocol
from pathlib import Path
from taskflow.core.task import Task

class StorageBackend(Protocol):
    def save_tasks(self, tasks: list[Task], filepath: Path) -> None: ...
    def load_tasks(self, filepath: Path) -> list[Task]: ...
    def backup_tasks(self, filepath: Path) -> bool: ...
```

Verify that `json_store` module satisfies this protocol. This prepares for Day 28's Repository pattern.

**Exercise 4 — Generic `TaskFilter`.**
Rewrite `TaskFilter` to be generic over the task type:

```python
from typing import TypeVar, Generic

TaskType = TypeVar("TaskType", bound=Task)

class TaskFilter(Generic[TaskType]):
    def __init__(self, tasks: list[TaskType]) -> None: ...
    def get(self) -> list[TaskType]: ...
```

Verify that `TaskFilter([UrgentTask(...)])` is typed as `TaskFilter[UrgentTask]` and `.get()` returns `list[UrgentTask]`.

**Exercise 5 — `@overload` for `load_tasks`.**
Add overloads to `load_tasks_safe()` so mypy can narrow the return type:

```python
@overload
def load_tasks_safe(filepath: Path, strict: bool = True) -> tuple[list[Task], None]: ...
@overload
def load_tasks_safe(filepath: Path, strict: bool = False) -> tuple[list[Task], str | None]: ...
```

**Exercise 6 (stretch) — Full strict pass.**
Run `mypy taskflow/ --strict --ignore-missing-imports`. Fix every error that is not in `display/` or `integrations/`. Document each suppressed error with an inline `# type: ignore[specific-error]` comment explaining why it is acceptable.

---

## Checkpoint

Before moving to Day 28:

- [ ] Every public function in `core/`, `services.py`, `storage/`, `utils.py` has type hints
- [ ] `mypy taskflow/core/ taskflow/services.py taskflow/storage/ --strict` passes with 0 errors
- [ ] `WeatherData` and `ForecastDay` TypedDict defined in `integrations/weather.py`
- [ ] `Serialisable` and `Markable` Protocol defined in `taskflow/protocols.py`
- [ ] `mypy` configured in `pyproject.toml` with per-module overrides
- [ ] `pre-commit` hook runs `mypy` on every commit

---

## Common Errors on Day 27

**`error: Missing return statement`:**

```python
def find_task(tasks: list[Task], task_id: int) -> Task:
    for task in tasks:
        if task.id == task_id:
            return task
    # ❌ mypy: Missing return statement — what if loop finds nothing?

def find_task(tasks: list[Task], task_id: int) -> Task:
    for task in tasks:
        if task.id == task_id:
            return task
    raise TaskNotFoundError(task_id)   # ✅ explicit — mypy is happy
```

**`error: Incompatible types in assignment`:**

```python
tasks: list[Task] = []
tasks = [{"id": 1, "title": "..."}]   # ❌ list[dict], not list[Task]
tasks = [Task("...", "low", "work")]   # ✅ correct
```

**Forgetting `from __future__ import annotations` for forward references:**

```python
# Without __future__.annotations:
class Task:
    def rename(self, title: str) -> Task:   # ❌ Task not yet defined
        ...

# Fix: either use string literal
    def rename(self, title: str) -> "Task":   # ✅

# Or add the future import at the top
from __future__ import annotations   # ✅ deferred evaluation everywhere
```

**`error: Argument 1 to "sorted" has incompatible type`:**

```python
tasks: list[Task | None] = [task1, None, task2]
sorted(tasks)   # ❌ None is not comparable with Task

# Fix: filter None values first
valid: list[Task] = [t for t in tasks if t is not None]
sorted(valid)   # ✅
```

---

## What's Coming

On **Day 28** we introduce Design Patterns — specifically the Repository pattern and Singleton. The Repository pattern will give TaskFlow AI a clean abstraction over storage, making it trivial to swap `json_store.py` for SQLite (Day 34) or PostgreSQL (Day 55) without changing any business logic. The foundation of the `StorageBackend` Protocol from today's Exercise 3 sets this up perfectly.
