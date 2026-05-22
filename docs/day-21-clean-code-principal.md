# Day 21 — Clean Code Principles

> **Series:** Python & AI Engineering — Zero to Production
> **Phase:** 2 — Real Engineering
> **Python Version:** 3.14
> **Project:** TaskFlow AI — Refactoring for readability and maintainability

---

## Learning Objective

By the end of today, you will apply the most impactful clean code principles to TaskFlow AI — naming, function length, the Single Responsibility Principle, and comment quality. You will also resolve TD-001 (commands.py mixing concerns) by extracting a `services.py` module. The codebase will be more readable, more testable, and more maintainable without a single new feature added.

---

## What We Build Today

A `taskflow/services.py` module containing pure business logic functions extracted from `display/commands.py`, plus a clean pass over every module's naming and function lengths.

```python
# Before (Day 20) — business logic buried in a display module:
# display/commands.py line 87-134:
def cmd_add(tasks, raw_input=""):
    max_tasks = _max_tasks()
    if len(tasks) >= max_tasks:
        print(f"\n  ✗ Task limit reached...")
        return
    # ... 40 more lines mixing validation, parsing, mutation, printing

# After (Day 21) — cleanly separated:
# services.py:
def add_task_to_list(tasks, raw_input, max_tasks):
    """Pure: validate, parse, append. Returns the new Task. Never prints."""
    ...

# display/commands.py:
def cmd_add(tasks, raw_input=""):
    """Thin: collect input, call service, print result."""
    ...
```

---

## Concepts Covered

- Meaningful names — variables, functions, classes, modules
- Function length — the 20-line guideline
- Single Responsibility Principle — one function, one job
- Command-Query Separation — functions either do something OR return something
- DRY — Don't Repeat Yourself
- Comment quality — explaining WHY, not WHAT
- Magic numbers — why they are dangerous and how to eliminate them
- Extracting `services.py` — the integration layer for testable business logic
- Code review checklist applied live

---

## Full Tutorial

### Why Clean Code Matters

Code is read far more often than it is written. A function you write today will be read — by you, your teammates, your future self at 2am — hundreds of times before it is deleted. Clean code reduces the cognitive load of that reading. It makes bugs visible. It makes the next change obvious. It makes testing straightforward.

Clean code is not about style preferences. It is about communication.

---

### Principle 1 — Meaningful Names

Names should reveal intent. They should answer: what is this thing, what does it do, why does it exist?

```python
# ❌ Cryptic names
def fn(tl, ri, mt):
    if len(tl) >= mt:
        return None
    r = parse(ri)
    t = mk(r)
    tl.append(t)
    return t

# ✅ Intent-revealing names
def add_task_to_list(
    tasks: list,
    raw_input: str,
    max_tasks: int,
) -> Task | None:
    if len(tasks) >= max_tasks:
        return None
    result = parse_task_input(raw_input)
    task   = create_task_from_parse(result)
    tasks.append(task)
    return task
```

**Naming rules:**

| What | Convention | Examples |
|------|-----------|---------|
| Variables | `snake_case` noun | `task_count`, `raw_input`, `filtered_tasks` |
| Functions | `snake_case` verb phrase | `mark_task_done()`, `get_pending_tasks()` |
| Classes | `PascalCase` noun | `Task`, `UrgentTask`, `TaskFilter` |
| Constants | `ALL_CAPS` noun | `MAX_TASKS_FREE`, `DATE_FMT` |
| Modules | `snake_case` noun | `json_store.py`, `task_factory.py` |
| Private | `_leading_underscore` | `_next_id()`, `_CACHE_FILE` |
| Boolean variables | `is_`, `has_`, `can_` prefix | `is_done`, `has_due_date`, `can_edit` |

**Avoid abbreviations unless universally understood:**

```python
# ❌
def calc_cr(tl): ...   # completion rate? character return? who knows
def get_hp_tasks(): ... # high priority? hit points?

# ✅
def calculate_completion_rate(tasks): ...
def get_high_priority_tasks(tasks): ...
```

**Boolean variables should read like questions:**

```python
# ❌
done = task.get("done", False)

# ✅
is_done = task.get("done", False)
if is_done:
    ...
```

---

### Principle 2 — Function Length

A function should do one thing and do it well. If you need to scroll to read a function, it almost certainly does more than one thing.

**Guideline: aim for 20 lines or fewer.** This is not a hard rule — some functions are legitimately longer — but if you routinely write 50-line functions, something is wrong.

```python
# ❌ 60-line function doing 5 different things
def cmd_add(tasks, raw_input=""):
    # collect input (10 lines)
    # validate plan limit (5 lines)
    # run parser (8 lines)
    # handle parser errors (5 lines)
    # append to list (2 lines)
    # print confirmation (15 lines)
    # print type-specific extras (15 lines)

# ✅ Decomposed into focused functions
def cmd_add(tasks, raw_input=""):
    """Collect input, delegate to service, print confirmation."""
    if _is_at_limit(tasks):
        _print_limit_warning()
        return
    raw = _collect_input(raw_input)
    if raw is None:
        return
    task = _parse_and_create(raw)
    if task is None:
        return
    tasks.append(task)
    _print_add_confirmation(task, len(tasks))
    _print_type_extras(task)
```

Each extracted function is independently testable and independently readable.

---

### Principle 3 — Single Responsibility Principle

Every module, class, and function should have one reason to change.

The violation in TaskFlow AI is `display/commands.py` — it has three reasons to change:
1. The user interface changes (how input is collected)
2. The business rules change (what makes a task valid)
3. The display format changes (how confirmation is shown)

The fix is to extract business logic into `services.py`:

```
display/commands.py         ← reason to change: UI
    calls ↓
taskflow/services.py        ← reason to change: business rules
    calls ↓
core/task*.py               ← reason to change: domain model
```

---

### Principle 4 — Command-Query Separation

A function should either **command** (do something, return nothing) or **query** (return something, change nothing) — never both.

```python
# ❌ Violates CQS — returns the task AND appends to list AND prints
def add_and_show(tasks, title, priority):
    task = Task(title, priority)
    tasks.append(task)
    print(f"Added: {task}")
    return task

# ✅ Command (mutates, returns None)
def add_task_to_list(tasks, task):
    tasks.append(task)

# ✅ Query (returns value, no mutation)
def get_pending_tasks(tasks):
    return [t for t in tasks if not t.done]
```

Services functions should follow CQS strictly — they either mutate state and return `None`, or they compute and return a value. Display functions (`print`) are always commands.

---

### Principle 5 — DRY — Don't Repeat Yourself

Every piece of knowledge should have a single, authoritative representation.

**Find the repetition in TaskFlow AI:**

```python
# In commands.py, renderer.py, and shell.py:
if isinstance(task, Task):
    return getattr(task, key, default)
return task.get(key, default)

# This pattern appears 6 times across 3 files
# Extract once:

def task_attr(task, key: str, default=""):
    """Get an attribute from either a Task object or a plain dict."""
    if isinstance(task, Task):
        return getattr(task, key, default)
    return task.get(key, default)
```

After Day 21, `task_attr()` lives in `taskflow/utils.py` and is imported everywhere.

---

### Principle 6 — Comment Quality

Comments should explain **why**, not **what**. If the code is clear enough to explain what it does, the comment is noise.

```python
# ❌ Comments that state the obvious
task_count = len(tasks)   # count the tasks
tasks.append(task)        # append task to tasks list

# ❌ Outdated comments — worse than no comment
# Parse the CSV file
data = json.load(f)       # we changed from CSV to JSON but forgot the comment

# ✅ Comments that explain why
# Use Path.rename() for atomicity — on POSIX systems, rename()
# within the same filesystem is guaranteed atomic.
tmp_path.rename(filepath)

# ✅ Comments that explain non-obvious decisions
# next_id uses a list [n] rather than a plain int so it can be
# mutated by nested functions without the 'global' keyword.
# Day 12's Task class replaces this pattern entirely.
next_id = [1]
```

**Rule:** if you feel the urge to write a comment explaining what code does, rewrite the code to be self-explanatory instead. Comments are for context that cannot be expressed in code.

---

### Principle 7 — No Magic Numbers

A magic number is a literal value with no explanation of what it represents.

```python
# ❌ Magic numbers
if len(tasks) >= 10:
    print("Limit reached")

time.sleep(2)

if age_days() >= 7:
    return True

# ✅ Named constants in config.py
from .config import MAX_TASKS_FREE, WEATHER_CACHE_TTL, OVERDUE_THRESHOLD_DAYS

if len(tasks) >= MAX_TASKS_FREE:
    print("Limit reached")

time.sleep(WEATHER_CACHE_TTL / 300)

if age_days() >= OVERDUE_THRESHOLD_DAYS:
    return True
```

Every magic number in TaskFlow AI should be a named constant in `config.py`. Do a search for bare integer and float literals right now.

---

### Building `taskflow/services.py`

Extract pure business logic from `display/commands.py`:

```python
# taskflow/services.py
# TaskFlow AI — Pure business logic services.
#
# These functions are the testable core of the application.
# They NEVER print, NEVER read from stdin, and NEVER depend on
# the display layer.
#
# Rules:
#   - Every function is either a pure query (returns value, no side effects)
#     or a clear command (mutates one thing, returns None or the result).
#   - No print() calls anywhere in this module.
#   - All validation raises ValidationError — never silent failure.
#
# Version history:
#   Day 21 — extracted from display/commands.py (TD-001 resolution)

from .config import PLAN_LIMITS, USER_PLAN, OVERDUE_THRESHOLD_DAYS
from .errors import ValidationError, TaskNotFoundError
from .core.task       import Task
from .core.task_types import RecurringTask
from .core.stats      import calculate_stats

__all__ = [
    "add_task_to_list",
    "remove_task_by_index",
    "remove_task_by_id",
    "mark_task_done",
    "rename_task",
    "find_task_by_id",
    "find_task_index_by_id",
    "get_task_limit",
    "is_at_limit",
    "filter_tasks",
    "search_tasks",
    "get_overdue_tasks",
    "get_summary_stats",
]


# ─── Limit checks ─────────────────────────────────────────

def get_task_limit(plan: str | None = None) -> int:
    """
    Return the task limit for the given plan.

    Args:
        plan (str | None): Plan name. Defaults to USER_PLAN from config.

    Returns:
        int: Maximum number of tasks allowed.
    """
    p = plan or USER_PLAN
    return PLAN_LIMITS.get(p, PLAN_LIMITS["free"])


def is_at_limit(tasks: list, plan: str | None = None) -> bool:
    """Return True if the task list has reached its plan limit."""
    return len(tasks) >= get_task_limit(plan)


# ─── Add ──────────────────────────────────────────────────

def add_task_to_list(
    tasks: list,
    task: Task,
    plan: str | None = None,
) -> Task:
    """
    Append a Task to the task list after checking the plan limit.

    Args:
        tasks (list)     : Current task list — modified in place.
        task  (Task)     : The Task to add.
        plan  (str|None) : Plan name for limit check.

    Returns:
        Task: The added task (same object that was passed in).

    Raises:
        ValidationError: If the task list is already at its limit.
    """
    limit = get_task_limit(plan)
    if len(tasks) >= limit:
        raise ValidationError(
            f"Task limit reached ({limit} tasks on "
            f"{plan or USER_PLAN} plan). Upgrade to premium.",
            field="tasks",
            value=len(tasks),
        )
    tasks.append(task)
    return task


# ─── Remove ───────────────────────────────────────────────

def remove_task_by_index(tasks: list, index: int) -> Task:
    """
    Remove a task at the given 0-based index.

    Args:
        tasks (list): Current task list — modified in place.
        index (int) : 0-based index.

    Returns:
        Task: The removed task.

    Raises:
        IndexError: If index is out of range.
    """
    if not (0 <= index < len(tasks)):
        raise IndexError(
            f"Index {index} is out of range for a list of "
            f"{len(tasks)} task{'s' if len(tasks) != 1 else ''}."
        )
    return tasks.pop(index)


def remove_task_by_id(tasks: list, task_id: int) -> Task:
    """
    Remove a task by its ID.

    Args:
        tasks   (list): Current task list — modified in place.
        task_id (int) : Task ID to remove.

    Returns:
        Task: The removed task.

    Raises:
        TaskNotFoundError: If no task with that ID exists.
    """
    index = find_task_index_by_id(tasks, task_id)
    return tasks.pop(index)


# ─── Done ─────────────────────────────────────────────────

def mark_task_done(tasks: list, index: int) -> Task:
    """
    Mark a task as done, handling RecurringTask reset behaviour.

    Args:
        tasks (list): Task list.
        index (int) : 0-based index of the task to mark done.

    Returns:
        Task: The updated task.

    Raises:
        IndexError:      If index is out of range.
        ValidationError: If the task is already done (non-recurring).
    """
    if not (0 <= index < len(tasks)):
        raise IndexError(f"Index {index} out of range.")

    task = tasks[index]

    if isinstance(task, Task) and task.done and not isinstance(task, RecurringTask):
        raise ValidationError(
            f"Task '{task.title}' is already marked as done.",
            field="done",
            value=True,
        )

    task.mark_done()
    return task


# ─── Rename ───────────────────────────────────────────────

def rename_task(tasks: list, index: int, new_title: str) -> Task:
    """
    Rename a task with full validation.

    Args:
        tasks     (list): Task list.
        index     (int) : 0-based index.
        new_title (str) : Replacement title.

    Returns:
        Task: The updated task.

    Raises:
        IndexError:      If index is out of range.
        ValidationError: If new_title is empty or too long.
    """
    if not (0 <= index < len(tasks)):
        raise IndexError(f"Index {index} out of range.")
    new_title = new_title.strip()
    if not new_title:
        raise ValidationError(
            "New title cannot be empty.", field="title", value=new_title
        )
    if len(new_title) > 200:
        raise ValidationError(
            "New title too long (max 200 characters).",
            field="title", value=len(new_title),
        )
    task = tasks[index]
    if isinstance(task, Task):
        task.rename(new_title)
    else:
        task["title"] = new_title
    return task


# ─── Lookup ───────────────────────────────────────────────

def find_task_by_id(tasks: list, task_id: int) -> Task:
    """
    Find a task by its ID.

    Args:
        tasks   (list): Task list to search.
        task_id (int) : Task ID to find.

    Returns:
        Task: The matching task.

    Raises:
        TaskNotFoundError: If no task with that ID exists.
    """
    for task in tasks:
        tid = task.id if isinstance(task, Task) else task.get("id")
        if tid == task_id:
            return task
    raise TaskNotFoundError(task_id)


def find_task_index_by_id(tasks: list, task_id: int) -> int:
    """
    Find the 0-based index of a task by ID.

    Raises:
        TaskNotFoundError: If no task with that ID exists.
    """
    for i, task in enumerate(tasks):
        tid = task.id if isinstance(task, Task) else task.get("id")
        if tid == task_id:
            return i
    raise TaskNotFoundError(task_id)


# ─── Filtering ────────────────────────────────────────────

def filter_tasks(
    tasks: list,
    priority: str | None = None,
    category: str | None = None,
    is_done: bool | None = None,
    overdue_only: bool = False,
    limit: int | None = None,
) -> list:
    """
    Apply one or more filters to a task list and return a new list.

    All arguments are optional — omitting one means "no filter on that field."

    Args:
        tasks       (list)     : Task list to filter.
        priority    (str|None) : Keep only tasks with this priority.
        category    (str|None) : Keep only tasks with this category.
        is_done     (bool|None): True → done only, False → pending only.
        overdue_only(bool)     : Keep only overdue tasks.
        limit       (int|None) : Return at most N tasks.

    Returns:
        list: Filtered task list (new list, original unmodified).
    """
    result = list(tasks)

    if priority is not None:
        p = priority.lower()
        result = [t for t in result if _attr(t, "priority") == p]

    if category is not None:
        c = category.lower()
        result = [t for t in result if _attr(t, "category") == c]

    if is_done is True:
        result = [t for t in result if _is_done(t)]
    elif is_done is False:
        result = [t for t in result if not _is_done(t)]

    if overdue_only:
        result = [t for t in result if _is_overdue(t)]

    if limit is not None:
        result = result[:limit]

    return result


def search_tasks(tasks: list, keyword: str) -> list:
    """
    Return tasks whose titles contain keyword (case-insensitive).

    Args:
        tasks   (list): Task list to search.
        keyword (str) : Search keyword.

    Returns:
        list: Matching tasks.
    """
    kw = keyword.strip().lower()
    return [t for t in tasks if kw in _attr(t, "title", "").lower()]


def get_overdue_tasks(tasks: list) -> list:
    """Return tasks that are overdue according to their type's definition."""
    return [t for t in tasks if _is_overdue(t)]


# ─── Stats ────────────────────────────────────────────────

def get_summary_stats(tasks: list) -> dict:
    """
    Return a summary statistics dict for the task list.

    Wraps calculate_stats() for import convenience.

    Returns:
        dict: total, done, pending, rate.
    """
    return calculate_stats(tasks)


# ─── Private helpers ──────────────────────────────────────

def _attr(task, key: str, default=""):
    if isinstance(task, Task):
        return getattr(task, key, default)
    return task.get(key, default)


def _is_done(task) -> bool:
    if isinstance(task, Task):
        return task.done
    return task.get("done", False)


def _is_overdue(task) -> bool:
    if isinstance(task, Task):
        return task.is_overdue()
    import datetime
    from .config import DATE_FMT
    created = task.get("created_at", "")
    if not created or _is_done(task):
        return False
    try:
        age = (datetime.datetime.now()
               - datetime.datetime.strptime(created, DATE_FMT)).days
        return age >= OVERDUE_THRESHOLD_DAYS
    except ValueError:
        return False
```

---

### Creating `taskflow/utils.py`

Collect the shared helper functions that currently appear multiple times:

```python
# taskflow/utils.py
# TaskFlow AI — Shared utility functions.
#
# Functions here are framework-agnostic helpers used across multiple modules.
# They have no dependencies on display, storage, or business logic.
#
# Version history:
#   Day 21 — created to DRY up repeated patterns

import datetime
from .config import DATE_FMT
from .core.task import Task

__all__ = [
    "task_attr",
    "task_is_done",
    "task_age_days",
    "pluralise",
    "truncate",
]


def task_attr(task, key: str, default=""):
    """
    Get an attribute from either a Task object or a plain dict.

    Centralises the isinstance(task, Task) pattern used throughout
    the display and service layers.

    Args:
        task    : Task object or dict.
        key     (str): Attribute / key name.
        default     : Value to return if not found.
    """
    if isinstance(task, Task):
        return getattr(task, key, default)
    return task.get(key, default)


def task_is_done(task) -> bool:
    """Return done status from either a Task object or a dict."""
    if isinstance(task, Task):
        return task.done
    return task.get("done", False)


def task_age_days(task) -> int:
    """Return how many days ago the task was created."""
    if isinstance(task, Task):
        return task.age_days()
    created = task.get("created_at", "")
    if not created:
        return 0
    try:
        return (
            datetime.datetime.now()
            - datetime.datetime.strptime(created, DATE_FMT)
        ).days
    except ValueError:
        return 0


def pluralise(count: int, singular: str, plural: str | None = None) -> str:
    """
    Return the correct singular or plural form based on count.

    Args:
        count    (int)     : The quantity.
        singular (str)     : Singular form, e.g. "task".
        plural   (str|None): Plural form. Defaults to singular + "s".

    Returns:
        str: e.g. "1 task" or "3 tasks"

    Example:
        pluralise(1, "task")   → "1 task"
        pluralise(3, "task")   → "3 tasks"
        pluralise(1, "fish", "fish") → "1 fish"
    """
    word = singular if count == 1 else (plural or singular + "s")
    return f"{count} {word}"


def truncate(text: str, max_length: int, suffix: str = "..") -> str:
    """
    Truncate text to max_length, appending suffix if truncated.

    Args:
        text       (str): Text to truncate.
        max_length (int): Maximum character length including suffix.
        suffix     (str): Characters appended when truncation occurs.

    Returns:
        str: Truncated or original text.

    Example:
        truncate("Review pull request", 15) → "Review pull ..."
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix
```

---

### Updating `display/commands.py` to Use Services

Slim down `cmd_add` as an example of the pattern shift:

```python
# display/commands.py — updated cmd_add after TD-001 resolution

from ..services import add_task_to_list, is_at_limit, get_task_limit
from ..utils    import pluralise

def cmd_add(tasks: list, raw_input: str = "") -> None:
    """Collect task input and delegate creation to the service layer."""

    if is_at_limit(tasks):
        limit = get_task_limit()
        print(f"\n  ✗ {pluralise(limit, 'task')} limit reached "
              f"on {USER_PLAN} plan. Upgrade to premium.\n")
        return

    raw = _collect_raw_input(raw_input)
    if raw is None:
        return

    try:
        task = _parse_to_task(raw)
    except ValidationError as e:
        print(f"\n  ✗ {e}\n")
        return

    try:
        add_task_to_list(tasks, task)
    except ValidationError as e:
        print(f"\n  ✗ {e}\n")
        return

    _print_add_success(task, len(tasks))


def _collect_raw_input(raw_input: str) -> str | None:
    """Prompt for input if not pre-supplied. Returns None on empty input."""
    if not raw_input:
        print()
        print("  Shorthand: !!  ~daily/weekly/monthly  "
              "#priority  @category  !YYYY-MM-DD")
        print()
        raw_input = input("  Input: ").strip()
    if not raw_input:
        print("  ✗ Input cannot be empty.\n")
        return None
    return raw_input


def _parse_to_task(raw: str) -> Task:
    """Parse raw input into a Task. Raises ValidationError on failure."""
    from ..parser import parse_task_input, create_task_from_parse
    result = parse_task_input(raw)
    return create_task_from_parse(result)


def _print_add_success(task: Task, total: int) -> None:
    """Print the post-add confirmation message."""
    typename = type(task).__name__
    print(f"\n  ✓ {typename} added: \"{task.title}\"")
    print(f"  Total: {pluralise(total, 'task')}")
    limit = get_task_limit()
    remaining = limit - total
    if 0 < remaining <= 2:
        print(f"  ⚠  {pluralise(remaining, 'slot')} remaining on "
              f"{USER_PLAN} plan.")
    print()
```

Apply the same decomposition to every other command function.

---

## Exercises

**Exercise 1 — Name audit.**
Search the entire `taskflow/` package for any variable name shorter than 3 characters (excluding loop counters `i`, `j`, `k`). For each one, decide: is it acceptable (e.g., `db`, `id`, `kw`) or does it need to be renamed? Rename every genuinely unclear short name.

**Exercise 2 — Function length audit.**
Run this command and inspect every function over 25 lines:

```bash
python -c "
import ast, sys
from pathlib import Path

for path in Path('taskflow').rglob('*.py'):
    tree = ast.parse(path.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            lines = node.end_lineno - node.lineno
            if lines > 25:
                print(f'{path}:{node.lineno} {node.name}() — {lines} lines')
"
```

For each function over 25 lines, extract at least one sub-function.

**Exercise 3 — Magic number hunt.**
Search for bare integer literals in the codebase:

```bash
grep -rn "[^a-zA-Z_][0-9]\{2,\}[^0-9]" taskflow/ | grep -v "test_\|#\|__version__"
```

For each one that is not already a named constant in `config.py`, add it there and replace the literal.

**Exercise 4 — Comment quality pass.**
Read every comment in the codebase. Delete any comment that just restates what the code does. For any comment that explains something non-obvious — add "WHY:" at the start. After the pass, the ratio of explanatory comments to restatement comments should be 100:0.

**Exercise 5 — Update `display/commands.py`.**
Apply the TD-001 fix to every command function, not just `cmd_add`. Each command function should:
- Be under 20 lines
- Call `services.py` for business logic
- Call `renderer.py` for display
- Contain no logic of its own beyond input collection and output formatting

**Exercise 6 (stretch) — Verify with coverage.**
Install `pytest-cov` and write a single test that imports from `services.py` directly (no display dependency):

```python
# tests/test_services.py
from taskflow.core.task import Task
from taskflow.services  import add_task_to_list, is_at_limit

def test_add_task_to_list():
    tasks = []
    task  = Task("Review PR", "high", "work")
    result = add_task_to_list(tasks, task, plan="premium")
    assert len(tasks) == 1
    assert result is task

def test_is_at_limit_free_plan():
    tasks = [Task(f"Task {i}", "low", "work") for i in range(10)]
    assert is_at_limit(tasks, plan="free") is True
```

Run `pytest --cov=taskflow.services` and see coverage for the new module. This previews Day 25.

---

## Checkpoint

Before moving to Day 22:

- [ ] Every variable name reveals its intent — no single-letter names outside loops
- [ ] Every function is under 25 lines or has a clear reason to be longer
- [ ] `taskflow/services.py` exists with pure, printless business logic
- [ ] `taskflow/utils.py` exists with `task_attr()`, `pluralise()`, `truncate()`
- [ ] `display/commands.py` delegates to `services.py` for all mutations
- [ ] No magic numbers remain in business logic code
- [ ] Every comment explains WHY, not WHAT
- [ ] TD-001 is resolved and marked as such in `docs/technical-debt.md`

---

## Common Errors on Day 21

**Extracting too aggressively — one-line "functions":**

```python
# ❌ Over-extracted — adds complexity with no benefit
def _is_empty(tasks):
    return len(tasks) == 0

# ✅ Inline — obvious enough without extraction
if not tasks:
    ...
```

Extract functions when extraction adds clarity. Do not extract for its own sake.

**Services that print:**

```python
# ❌ Service with a print — breaks the contract
def add_task_to_list(tasks, task):
    tasks.append(task)
    print(f"Added: {task.title}")   # NO — services never print

# ✅ Return the result; let the command function print
def add_task_to_list(tasks, task):
    tasks.append(task)
    return task
```

**Renaming too broadly at once:**

When renaming a variable or function, use VS Code's "Rename Symbol" (`F2`) rather than global find-and-replace. It handles all references across files including imports.

---

## What's Coming

On **Day 22** we do a deep dive on project structure — finalising the package layout, resolving TD-002 (Task objects vs dicts), and ensuring every module has a single clear responsibility. We will also add `taskflow/utils.py` to every `__init__.py` that needs it, and run a full import graph verification.
