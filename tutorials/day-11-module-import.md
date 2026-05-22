# Day 11 — Modules & Imports

> **Series:** Python & AI Engineering — Zero to Production
> **Phase:** 1 — Foundations
> **Python Version:** 3.14
> **Project:** TaskFlow AI — Restructuring into a proper Python package

---

## Learning Objective

By the end of today, you will understand Python's module system deeply — how imports work under the hood, how to structure a multi-file project cleanly, how `__init__.py` turns a folder into a package, and how the standard library gives you hundreds of powerful tools for free. TaskFlow AI gets restructured from a flat collection of files into a proper Python package with a clean public API.

---

## What We Build Today

A restructured TaskFlow AI project with a proper package layout. Instead of five files in one folder, the app has a clean `taskflow/` package with logical submodules.

```
taskflow/                    ← Python package (folder with __init__.py)
│
├── __init__.py              ← Package entry point, public API
├── main.py                  ← App entry point and command loop
├── config.py                ← All constants and configuration
│
├── core/                    ← Core business logic
│   ├── __init__.py
│   ├── tasks.py             ← Task operations (add, remove, filter)
│   └── stats.py             ← Statistics calculations
│
├── storage/                 ← Data persistence
│   ├── __init__.py
│   └── json_store.py        ← JSON file storage
│
├── integrations/            ← External services
│   ├── __init__.py
│   └── weather.py           ← Weather API integration
│
├── display/                 ← Terminal UI
│   ├── __init__.py
│   └── renderer.py          ← All display/print functions
│
└── errors.py                ← Custom exception hierarchy

run.py                       ← Project root entry point
```

---

## Concepts Covered

- What a module is — any `.py` file
- `import module` — importing a whole module
- `from module import name` — importing specific names
- `from module import name as alias` — aliasing imports
- `import *` — why you should never use it
- How Python finds modules — `sys.path`
- `__init__.py` — making a folder a package
- Relative imports — `from .module import name`
- The standard library — `os`, `sys`, `datetime`, `pathlib`, `collections`, `itertools`, `functools`
- `__all__` — defining a module's public API
- Circular imports — what they are and how to avoid them
- `importlib` — dynamic imports (preview)
- Reloading modules in the REPL

---

## Full Tutorial

### What Is a Module?

Every `.py` file is a module. When you write `import storage`, Python finds `storage.py`, executes it top-to-bottom, and makes its names available under the `storage` namespace.

```python
# storage.py
DATA_FILE = "tasks.json"

def save_tasks(tasks):
    ...

def load_tasks():
    ...
```

```python
# main.py
import storage

print(storage.DATA_FILE)       # "tasks.json"
storage.save_tasks(my_tasks)   # calls the function
```

The module name is the filename without `.py`. The names inside it are accessed with dot notation.

---

### Three Ways to Import

**1. Import the whole module:**

```python
import json
import datetime
import storage

data = json.loads('{"key": "value"}')
now  = datetime.datetime.now()
tasks = storage.load_tasks()
```

Advantage: origin is always clear — `json.loads()` tells you exactly which module `loads` comes from.

**2. Import specific names:**

```python
from json import loads, dumps
from datetime import datetime, date
from storage import load_tasks, save_tasks

data  = loads('{"key": "value"}')   # no prefix needed
now   = datetime.now()
tasks = load_tasks()
```

Advantage: less typing. Disadvantage: origin is less obvious, especially in large files.

**3. Import with an alias:**

```python
import numpy as np               # industry convention
import pandas as pd              # industry convention
from storage import load_tasks as load
from errors import ValidationError as VError
```

Use aliases when a name is long, conflicts with another name, or follows a well-known convention (like `np` for numpy).

**Never use `import *`:**

```python
from storage import *   # ❌ imports everything — pollutes namespace, hides origins
```

`import *` makes it impossible to tell where a name came from. It breaks auto-complete, confuses linters, and causes subtle bugs when two modules define the same name. Never use it in production code.

---

### How Python Finds Modules — `sys.path`

When you write `import storage`, Python searches for `storage.py` in this order:

1. The directory containing the script that was run
2. Directories in the `PYTHONPATH` environment variable
3. The standard library directories
4. Directories from installed packages (`site-packages`)

```python
import sys
print(sys.path)   # list of directories Python searches
```

This is why `import storage` works when `storage.py` is in the same folder as `main.py` — the script's directory is always first in `sys.path`.

---

### `__init__.py` — Making a Folder a Package

A folder becomes a Python **package** when it contains an `__init__.py` file. This file is executed when the package is first imported and controls what is exposed to the outside world.

```
taskflow/
├── __init__.py      ← this makes 'taskflow' a package
├── config.py
└── core/
    ├── __init__.py  ← this makes 'taskflow.core' a sub-package
    └── tasks.py
```

```python
# taskflow/__init__.py
"""
TaskFlow AI — Task management with AI integration.
"""

__version__ = "1.0.0"
__author__  = "Udit Rawat"

# Re-export the most commonly used names for convenience
from taskflow.core.tasks  import add_task, remove_task, get_all_tasks
from taskflow.storage.json_store import load_tasks, save_tasks
from taskflow.errors import TaskFlowError, StorageError, ValidationError
```

Now users can do:

```python
import taskflow

tasks = taskflow.load_tasks()     # instead of taskflow.storage.json_store.load_tasks()
taskflow.add_task(tasks, "Review PR", "high", "work")
```

The `__init__.py` defines the **public API** of your package — what callers should use. Internal implementation details stay inside submodules.

---

### Relative Imports

Inside a package, use **relative imports** to import from sibling modules. They are more reliable than absolute imports for internal package structure:

```python
# taskflow/core/tasks.py

# Absolute import (works but fragile if package is renamed)
from taskflow.errors import ValidationError
from taskflow.config import VALID_PRIORITIES

# Relative import (preferred inside a package)
from ..errors import ValidationError    # go up one level, import from errors
from ..config import VALID_PRIORITIES   # go up one level, import from config
```

`.` means current package. `..` means parent package. `...` means grandparent.

---

### `__all__` — Defining a Module's Public API

`__all__` is a list of names that should be exported when someone does `from module import *`. More importantly, it signals to readers (and tools) what is the intended public interface of the module:

```python
# taskflow/core/tasks.py

__all__ = [
    "add_task",
    "remove_task",
    "mark_done",
    "get_all_tasks",
    "get_pending_tasks",
    "get_tasks_by_priority",
]

# Private helper — not in __all__, not part of the public API
def _validate_task_dict(task: dict) -> bool:
    """Internal helper — prefix with _ to signal it's private."""
    return all(k in task for k in ("id", "title", "priority", "status", "done"))
```

Convention: names prefixed with `_` are private — they work normally but signal "don't use this from outside the module."

---

### The Standard Library — Your Free Toolkit

Python ships with over 200 modules. You do not need to install anything — they are available everywhere Python runs. Here are the ones you will use constantly:

**`os` — operating system interface:**

```python
import os

print(os.getcwd())              # current working directory
print(os.listdir("."))          # list files in current dir
os.makedirs("data", exist_ok=True)   # create directory (no error if exists)
print(os.environ.get("HOME"))   # read environment variable
```

**`sys` — system-specific parameters:**

```python
import sys

print(sys.version)    # Python version string
print(sys.platform)  # 'linux', 'darwin', 'win32'
sys.exit(0)          # exit the program with a status code
print(sys.argv)      # command-line arguments
```

**`collections` — specialised container types:**

```python
from collections import Counter, defaultdict, OrderedDict, namedtuple

# Counter — count occurrences
priorities = ["high", "low", "high", "medium", "high"]
counts = Counter(priorities)
print(counts)              # Counter({'high': 3, 'low': 1, 'medium': 1})
print(counts.most_common(2))  # [('high', 3), ('low', 1)]

# defaultdict — dict with default values
task_groups = defaultdict(list)
for task in tasks:
    task_groups[task["priority"]].append(task["title"])
# No KeyError if 'high' doesn't exist yet — creates empty list automatically

# namedtuple — lightweight, readable data containers
TaskSummary = namedtuple("TaskSummary", ["id", "title", "priority"])
summary = TaskSummary(id=1, title="Review PR", priority="high")
print(summary.title)   # "Review PR"
```

**`itertools` — efficient iterators:**

```python
from itertools import groupby, islice, chain

# groupby — group tasks by a key
sorted_tasks = sorted(tasks, key=lambda t: t["priority"])
for priority, group in groupby(sorted_tasks, key=lambda t: t["priority"]):
    group_list = list(group)
    print(f"{priority}: {len(group_list)} tasks")

# islice — take the first N items from any iterable
top_3 = list(islice(tasks, 3))

# chain — combine multiple iterables
all_items = list(chain(pending_tasks, done_tasks))
```

**`functools` — higher-order functions:**

```python
from functools import lru_cache, partial, reduce

# lru_cache — memoize expensive function results
@lru_cache(maxsize=128)
def expensive_calculation(n):
    return sum(range(n))   # cached after first call

# partial — fix some arguments of a function
from taskflow.core.tasks import get_tasks_by_priority
get_high = partial(get_tasks_by_priority, priority="high")
high_tasks = get_high(tasks)   # only need to pass tasks

# reduce — accumulate values
from functools import reduce
total_chars = reduce(lambda acc, t: acc + len(t["title"]), tasks, 0)
```

**`datetime` — dates and times (you've used this already):**

```python
from datetime import datetime, date, timedelta

now       = datetime.now()
today     = date.today()
yesterday = today - timedelta(days=1)
next_week = today + timedelta(weeks=1)

# Parse a string into a datetime
dt = datetime.strptime("2025-05-19 14:32", "%Y-%m-%d %H:%M")
```

**`pathlib` — file paths (you've used this already):**

```python
from pathlib import Path

p = Path("taskflow") / "data" / "tasks.json"
p.mkdir(parents=True, exist_ok=True)   # create all parent dirs
p.write_text("[]", encoding="utf-8")
content = p.read_text(encoding="utf-8")
files   = list(Path(".").glob("*.json"))   # find all JSON files
```

---

### Circular Imports — The Classic Trap

A circular import occurs when module A imports module B, and module B imports module A:

```python
# tasks.py
from errors import ValidationError   # imports errors.py

# errors.py
from tasks import Task               # imports tasks.py — CIRCULAR!
```

Python detects this and raises an `ImportError`. The fix is almost always to restructure — move the shared code to a third module that both can import:

```python
# Bad: tasks.py ↔ errors.py (circular)

# Good:
# errors.py     — no imports from taskflow
# tasks.py      — imports from errors.py
# display.py    — imports from tasks.py and errors.py
```

**Rule: dependency direction should be one-way.** Low-level modules (`errors.py`, `config.py`) should not import from high-level modules (`tasks.py`, `main.py`). Data flows up; errors and config live at the bottom.

---

### Restructuring TaskFlow AI

Create the new directory structure:

```bash
mkdir -p taskflow/core taskflow/storage taskflow/integrations taskflow/display
touch taskflow/__init__.py
touch taskflow/core/__init__.py
touch taskflow/storage/__init__.py
touch taskflow/integrations/__init__.py
touch taskflow/display/__init__.py
```

**`taskflow/config.py`** — all constants in one place:

```python
# taskflow/config.py
"""
TaskFlow AI — Central configuration.
All constants live here. Import from this module, never hardcode.
"""

from pathlib import Path

# ── App ───────────────────────────────────────────────────
APP_NAME = "TaskFlow AI"
VERSION  = "1.0.0"

# ── User ──────────────────────────────────────────────────
USER_NAME      = "Udit"
USER_PLAN      = "free"
USER_LATITUDE  = 28.6139
USER_LONGITUDE = 77.2090
USER_LOCATION  = "Delhi, IN"

# ── Limits ────────────────────────────────────────────────
MAX_TASKS_FREE    = 10
MAX_TASKS_PREMIUM = 100

PLAN_LIMITS = {
    "free":      MAX_TASKS_FREE,
    "premium":   MAX_TASKS_PREMIUM,
    "enterprise": 10_000,
}

# ── Validation ────────────────────────────────────────────
VALID_PRIORITIES = {"high", "medium", "low"}
VALID_CATEGORIES = {"work", "personal", "health", "learning", "other"}
VALID_PLANS      = set(PLAN_LIMITS.keys())

# ── Storage ───────────────────────────────────────────────
BASE_DIR  = Path(__file__).parent.parent   # project root
DATA_DIR  = BASE_DIR / "data"
DATA_FILE = DATA_DIR / "taskflow_tasks.json"
DATE_FMT  = "%Y-%m-%d %H:%M"

# ── Weather ───────────────────────────────────────────────
WEATHER_API_URL   = "https://api.open-meteo.com/v1/forecast"
WEATHER_TIMEOUT   = 10
WEATHER_CACHE_TTL = 600   # seconds
```

**`taskflow/errors.py`** — unchanged from Day 10, moved to new location.

**`taskflow/core/tasks.py`** — pure task business logic:

```python
# taskflow/core/tasks.py
"""
Core task operations — add, remove, update, filter, search.
All functions are pure (return values) or clearly side-effecting (mutate list).
"""

import datetime
from ..config import VALID_PRIORITIES, VALID_CATEGORIES, DATE_FMT
from ..errors import ValidationError, TaskNotFoundError

__all__ = [
    "make_task",
    "add_task",
    "remove_task",
    "mark_task_done",
    "find_task_by_id",
    "get_all_tasks",
    "get_pending_tasks",
    "get_done_tasks",
    "get_tasks_by_priority",
    "get_tasks_by_category",
    "search_tasks",
    "get_next_id",
]


def make_task(task_id: int, title: str,
              priority: str, category: str) -> dict:
    """Create and return a validated task dictionary."""
    title    = title.strip()
    priority = priority.strip().lower()
    category = category.strip().lower()

    if not title:
        raise ValidationError("Title cannot be empty", field="title", value=title)
    if len(title) > 200:
        raise ValidationError("Title too long (max 200 chars)",
                              field="title", value=len(title))
    if priority not in VALID_PRIORITIES:
        raise ValidationError(f"Invalid priority",
                              field="priority", value=priority)
    if category not in VALID_CATEGORIES:
        raise ValidationError(f"Invalid category",
                              field="category", value=category)

    return {
        "id":         task_id,
        "title":      title,
        "priority":   priority,
        "category":   category,
        "status":     "pending",
        "done":       False,
        "created_at": datetime.datetime.now().strftime(DATE_FMT),
    }


def get_next_id(tasks: list) -> int:
    """Return the next available task ID."""
    return max((t["id"] for t in tasks), default=0) + 1


def find_task_by_id(tasks: list, task_id: int) -> dict:
    """
    Find a task by its ID.

    Raises:
        TaskNotFoundError: If no task with the given ID exists.
    """
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise TaskNotFoundError(task_id)


def add_task(tasks: list, title: str,
             priority: str, category: str) -> dict:
    """
    Create a new task and append it to the task list.

    Returns:
        dict: The newly created task.
    """
    task_id = get_next_id(tasks)
    task    = make_task(task_id, title, priority, category)
    tasks.append(task)
    return task


def remove_task(tasks: list, index: int) -> dict:
    """
    Remove a task at the given 0-based index.

    Returns:
        dict: The removed task.
    """
    if not (0 <= index < len(tasks)):
        raise IndexError(f"Index {index} out of range for {len(tasks)} tasks")
    return tasks.pop(index)


def mark_task_done(tasks: list, index: int) -> dict:
    """
    Mark the task at the given index as done.

    Returns:
        dict: The updated task.
    """
    if not (0 <= index < len(tasks)):
        raise IndexError(f"Index {index} out of range")
    tasks[index]["done"]   = True
    tasks[index]["status"] = "done"
    return tasks[index]


def get_all_tasks(tasks: list) -> list:
    """Return a copy of all tasks."""
    return list(tasks)


def get_pending_tasks(tasks: list) -> list:
    """Return tasks that are not yet done."""
    return [t for t in tasks if not t["done"]]


def get_done_tasks(tasks: list) -> list:
    """Return completed tasks."""
    return [t for t in tasks if t["done"]]


def get_tasks_by_priority(tasks: list, priority: str) -> list:
    """Return tasks matching the given priority."""
    return [t for t in tasks if t["priority"] == priority.lower()]


def get_tasks_by_category(tasks: list, category: str) -> list:
    """Return tasks matching the given category."""
    return [t for t in tasks if t["category"] == category.lower()]


def search_tasks(tasks: list, keyword: str) -> list:
    """Return tasks whose titles contain the keyword (case-insensitive)."""
    kw = keyword.strip().lower()
    return [t for t in tasks if kw in t["title"].lower()]
```

**`taskflow/core/stats.py`** — statistics extracted to their own module:

```python
# taskflow/core/stats.py
"""
Task statistics calculations.
All functions are pure — no side effects, no printing.
"""

from collections import Counter
from ..config import VALID_PRIORITIES, VALID_CATEGORIES

__all__ = ["calculate_stats", "priority_breakdown", "category_breakdown"]


def calculate_stats(tasks: list) -> dict:
    """Return a summary statistics dictionary for the task list."""
    total   = len(tasks)
    done    = sum(1 for t in tasks if t["done"])
    pending = total - done
    rate    = round(done / total * 100, 1) if total > 0 else 0.0
    return {
        "total":   total,
        "done":    done,
        "pending": pending,
        "rate":    rate,
    }


def priority_breakdown(tasks: list) -> dict:
    """Return count of tasks per priority level."""
    counts = Counter(t["priority"] for t in tasks)
    return {p: counts.get(p, 0) for p in ["high", "medium", "low"]}


def category_breakdown(tasks: list) -> dict:
    """Return count of tasks per category."""
    counts = Counter(t["category"] for t in tasks)
    return dict(counts.most_common())
```

**`taskflow/__init__.py`** — the package's public API:

```python
# taskflow/__init__.py
"""
TaskFlow AI — Intelligent task management.

Public API — everything a caller needs is available from here.
"""

from .config  import APP_NAME, VERSION, USER_NAME
from .errors  import TaskFlowError, StorageError, ValidationError, TaskNotFoundError
from .core.tasks  import (add_task, remove_task, mark_task_done,
                           get_pending_tasks, search_tasks)
from .core.stats  import calculate_stats
from .storage.json_store import load_tasks, save_tasks

__version__ = VERSION
__all__ = [
    "APP_NAME", "VERSION", "USER_NAME",
    "TaskFlowError", "StorageError", "ValidationError", "TaskNotFoundError",
    "add_task", "remove_task", "mark_task_done",
    "get_pending_tasks", "search_tasks",
    "calculate_stats",
    "load_tasks", "save_tasks",
]
```

**`run.py`** — the project root entry point:

```python
# run.py
# Project root entry point.
# Run this file to start TaskFlow AI: python run.py

from taskflow.main import main

if __name__ == "__main__":
    main()
```

---

### Useful Standard Library Modules to Explore

Beyond what is used in the project, these will appear throughout the series:

| Module | What it does | First used |
|--------|-------------|------------|
| `os` | OS operations, env vars | Day 24 |
| `sys` | Interpreter, argv | Day 11 |
| `argparse` | CLI argument parsing | Day 15 |
| `logging` | Professional logging | Day 23 |
| `collections` | Counter, defaultdict | Day 11 |
| `itertools` | Efficient iteration | Day 11 |
| `functools` | Decorators, caching | Day 17 |
| `dataclasses` | Data classes | Day 13 |
| `abc` | Abstract base classes | Day 28 |
| `typing` | Type hints | Day 27 |
| `unittest` | Testing | Day 25 |
| `asyncio` | Async programming | Day 30 |
| `hashlib` | Hashing | Day 36 |
| `re` | Regular expressions | Day 14 |
| `time` | Timing and delays | Day 10 |
| `copy` | Shallow/deep copy | Day 12 |
| `contextlib` | Context managers | Day 17 |

---

## Exercises

**Exercise 1 — Verify the package structure.**
After restructuring, run these imports in the Python REPL and verify they all work:

```python
import taskflow
print(taskflow.__version__)

from taskflow import add_task, load_tasks
from taskflow.core.tasks import search_tasks
from taskflow.core.stats import priority_breakdown
from taskflow.config import VALID_PRIORITIES
```

**Exercise 2 — Explore `sys.path`.**
Add a `"debug-path"` command (for development only) that prints `sys.path` formatted one entry per line. Run it. Identify where `taskflow` was found. Then temporarily move `taskflow/` to a different location and show what breaks.

**Exercise 3 — `collections.Counter` in action.**
In `taskflow/core/stats.py`, add a `tag_breakdown(tasks)` function that uses `Counter` to count how many tasks mention each priority keyword in their title (e.g. "urgent", "important", "quick"). Display results sorted by frequency.

**Exercise 4 — `collections.defaultdict` grouping.**
Write a `group_by_category(tasks)` function using `defaultdict(list)` that groups tasks into a dict of `{category: [task, task, ...]}`. Add a `"group"` command to the app that displays tasks organized by category rather than flat.

**Exercise 5 — `functools.lru_cache`.**
Apply `@lru_cache` to `calculate_stats()`. Since tasks is a list (unhashable), you will need to convert it first. Write a wrapper:

```python
from functools import lru_cache

@lru_cache(maxsize=32)
def _cached_stats(tasks_tuple: tuple) -> dict:
    tasks = [dict(t) for t in tasks_tuple]
    return calculate_stats(tasks)

def get_cached_stats(tasks: list) -> dict:
    return _cached_stats(tuple(frozenset(t.items()) for t in tasks))
```

Benchmark with `time.time()` before and after caching on a list of 1000 tasks.

**Exercise 6 (stretch) — `__all__` enforcement.**
Write a test that imports every name in `taskflow.__all__` and verifies each one is callable or a non-None value. Then deliberately add a typo to `__all__` (e.g. `"add_taks"`) and watch the import fail. This is how you catch `__all__` mismatches before users do.

```python
import taskflow

for name in taskflow.__all__:
    obj = getattr(taskflow, name, None)
    assert obj is not None, f"'{name}' in __all__ but not defined in taskflow"
    print(f"  ✓ {name}")
```

---

## Checkpoint

Before moving to Day 12:

- [ ] I understand the difference between a module and a package
- [ ] I know three ways to import and when to use each
- [ ] I never use `import *`
- [ ] I understand how Python finds modules via `sys.path`
- [ ] I can create a package with `__init__.py`
- [ ] I use relative imports inside a package
- [ ] I define `__all__` in every module to signal the public API
- [ ] I prefix private names with `_`
- [ ] I understand circular imports and how to avoid them
- [ ] I have used `Counter`, `defaultdict`, `lru_cache`, and `partial` from the standard library
- [ ] TaskFlow AI is restructured into the `taskflow/` package layout
- [ ] `run.py` starts the app cleanly

---

## Common Errors on Day 11

**`ModuleNotFoundError: No module named 'taskflow'`**

Run from the project root (where `run.py` lives), not from inside the `taskflow/` folder:

```bash
# ❌ wrong — inside the package
cd taskflow && python main.py

# ✅ correct — from project root
python run.py
```

**`ImportError: attempted relative import with no known parent package`**

Relative imports (`from ..config import ...`) only work inside a package. If you run `python taskflow/core/tasks.py` directly, Python treats it as a script, not a package member. Always run from the project root via `run.py`.

**`ImportError: cannot import name 'X' from 'taskflow'`**

The name `X` is not in `taskflow/__init__.py`. Either add it to `__init__.py` or import from the submodule directly:

```python
from taskflow import X                     # ❌ if X not in __init__.py
from taskflow.core.tasks import X          # ✅ direct submodule import
```

**Circular import symptom — `ImportError: cannot import name 'Y' from partially initialized module`:**

Module A is being imported, starts importing module B, which tries to import A before A is finished loading. Fix: restructure so dependencies only flow downward. Move shared types/constants to a module neither A nor B imports from.

---

## What's Coming

On **Day 12** we introduce Object-Oriented Programming — classes, `__init__`, instance attributes, and methods. Right now a "task" is just a plain dictionary. Tomorrow we give it a class — `Task` — with its own attributes, methods, and behaviour. The entire data model upgrades from passive dicts to active objects, and `next_id` stops being a `[1]` list hack and becomes a proper class attribute. This is the most significant design upgrade of Phase 1.
