# Day 17 — Decorators & Context Managers

> **Series:** Python & AI Engineering — Zero to Production
> **Phase:** 2 — Real Engineering
> **Python Version:** 3.14
> **Project:** TaskFlow AI — Adding invisible superpowers to functions

---

## Learning Objective

By the end of today, you will understand how decorators work at a deep level — not just how to use them, but how to write your own. You will also build custom context managers using both the class-based and `contextlib` approaches. TaskFlow AI gains a timer decorator, a retry decorator, a validation decorator, and a snapshot context manager.

---

## What We Build Today

A `taskflow/decorators.py` module with production-quality decorators, and a `taskflow/context.py` module with reusable context managers.

```python
# Decorator usage — transparent enhancement
@timer(label="Task save")
@retry(times=3, exceptions=(StorageError,))
def save_tasks(tasks, filepath):
    ...

# Timer output:
# [timer] Task save: 0.023s

# Context manager — temporary state
with task_snapshot(tasks) as snapshot:
    tasks.clear()   # destructive operation
    risky_operation(tasks)
# If anything goes wrong, tasks is restored from snapshot automatically

# Validation decorator
@validate_non_empty
def cmd_done(tasks):
    ...
# Automatically checks len(tasks) > 0 before running
```

---

## Concepts Covered

- How decorators work — functions returning functions
- `functools.wraps` — preserving function metadata
- Decorators with arguments — factory pattern
- Class-based decorators
- Stacking decorators
- `@timer` — measuring execution time
- `@retry` — automatic retry on failure
- `@validate_*` — precondition decorators
- `@cache_result` — simple memoization
- Context managers — `__enter__` and `__exit__`
- `contextlib.contextmanager` — generator-based context managers
- `contextlib.suppress` — suppressing specific exceptions
- `contextlib.nullcontext` — conditional context managers
- Exception handling inside `__exit__`

---

## Full Tutorial

### How Decorators Work

A decorator is a function that takes a function and returns a new function. It wraps the original function with additional behaviour — before it runs, after it runs, or both.

```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print(f"Before {func.__name__}()")
        result = func(*args, **kwargs)   # call the original
        print(f"After {func.__name__}()")
        return result
    return wrapper

# Using the decorator manually
def greet(name):
    print(f"Hello, {name}!")

greet = my_decorator(greet)   # wrap it
greet("Udit")
# Before greet()
# Hello, Udit!
# After greet()
```

The `@` syntax is just syntactic sugar for this wrapping:

```python
@my_decorator
def greet(name):
    print(f"Hello, {name}!")

# Exactly equivalent to:
# greet = my_decorator(greet)
```

---

### `functools.wraps` — Preserving Metadata

Without `@wraps`, the decorated function loses its name, docstring, and other metadata:

```python
def my_decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def greet(name):
    """Greet someone by name."""
    print(f"Hello, {name}!")

print(greet.__name__)   # "wrapper" — wrong!
print(greet.__doc__)    # None — lost!
```

`@functools.wraps(func)` copies the original function's metadata to the wrapper:

```python
from functools import wraps

def my_decorator(func):
    @wraps(func)                      # ← preserves __name__, __doc__, etc.
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def greet(name):
    """Greet someone by name."""
    print(f"Hello, {name}!")

print(greet.__name__)   # "greet" ✓
print(greet.__doc__)    # "Greet someone by name." ✓
```

**Always use `@wraps(func)` in every decorator you write.**

---

### Decorators with Arguments — The Factory Pattern

To pass arguments to a decorator, you need an extra level of nesting — a factory function that creates the decorator:

```python
# Without arguments:
@my_decorator
def func(): ...
# = func = my_decorator(func)

# With arguments:
@my_decorator(arg1, arg2)
def func(): ...
# = func = my_decorator(arg1, arg2)(func)
# my_decorator(arg1, arg2) must return a decorator
```

Example — a decorator that repeats a function N times:

```python
from functools import wraps

def repeat(times):
    """Decorator factory — repeat the function N times."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = None
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(3)
def greet(name):
    print(f"Hello, {name}!")

greet("Udit")
# Hello, Udit!
# Hello, Udit!
# Hello, Udit!
```

---

### Stacking Decorators

Multiple decorators can be stacked — they apply bottom-up:

```python
@decorator_a
@decorator_b
@decorator_c
def func():
    ...

# Equivalent to:
# func = decorator_a(decorator_b(decorator_c(func)))
```

```python
@timer(label="save")
@retry(times=3)
def save_tasks(tasks, filepath):
    ...

# save_tasks = timer("save")(retry(3)(save_tasks))
# Outer decorator runs first: timer wraps retry which wraps save_tasks
```

---

### Context Managers — `__enter__` and `__exit__`

A context manager is any object that implements `__enter__` and `__exit__`. The `with` statement calls them automatically:

```python
class ManagedFile:
    def __init__(self, filepath, mode, encoding="utf-8"):
        self.filepath = filepath
        self.mode     = mode
        self.encoding = encoding
        self.file     = None

    def __enter__(self):
        """Called at the start of the with block. Return value bound to 'as' target."""
        self.file = open(self.filepath, self.mode, encoding=self.encoding)
        return self.file

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Called when the with block exits — whether normally or via exception.

        Args:
            exc_type: Exception type if an exception occurred, else None.
            exc_val:  Exception value if an exception occurred, else None.
            exc_tb:   Exception traceback if an exception occurred, else None.

        Returns:
            bool: True to suppress the exception, False (or None) to re-raise.
        """
        if self.file:
            self.file.close()
        return False   # do not suppress exceptions

with ManagedFile("tasks.json", "r") as f:
    data = f.read()
# file is always closed here
```

The `__exit__` method receives exception information if one occurred inside the `with` block. Return `True` to suppress the exception; return `False` (or nothing) to re-raise it.

---

### `contextlib.contextmanager` — Simpler Context Managers

The `@contextmanager` decorator turns a generator function into a context manager. The `yield` statement splits it into `__enter__` (before yield) and `__exit__` (after yield):

```python
from contextlib import contextmanager

@contextmanager
def managed_file(filepath, mode, encoding="utf-8"):
    """Context manager for file handling — using generator syntax."""
    file = open(filepath, mode, encoding=encoding)
    try:
        yield file   # everything before yield is __enter__
    finally:
        file.close() # everything after yield is __exit__ (always runs)

with managed_file("tasks.json", "r") as f:
    data = f.read()
```

The `try/finally` ensures cleanup even if an exception occurs inside the `with` block.

---

### Building `taskflow/decorators.py`

```python
# taskflow/decorators.py
# TaskFlow AI — Day 17
# Production-quality decorators for cross-cutting concerns.

import time
import functools
import logging
from typing import Callable, Type

from .errors import TaskFlowError

logger = logging.getLogger(__name__)

__all__ = [
    "timer",
    "retry",
    "validate_non_empty",
    "validate_tasks_arg",
    "log_call",
    "deprecated",
]


def timer(label: str = "", log: bool = False):
    """
    Measure and print/log the execution time of a function.

    Args:
        label (str) : Label shown in the output. Defaults to function name.
        log   (bool): If True, use logger.debug instead of print.

    Example:
        @timer(label="Task save")
        def save_tasks(tasks): ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            name    = label or func.__name__
            start   = time.perf_counter()
            result  = func(*args, **kwargs)
            elapsed = time.perf_counter() - start
            message = f"[timer] {name}: {elapsed:.4f}s"
            if log:
                logger.debug(message)
            else:
                print(f"  ⏱  {message}")
            return result
        return wrapper
    return decorator


def retry(times: int = 3, delay: float = 1.0,
          backoff: float = 2.0,
          exceptions: tuple = (Exception,)):
    """
    Retry a function on failure with exponential backoff.

    Args:
        times      (int)  : Maximum number of attempts.
        delay      (float): Initial wait in seconds before first retry.
        backoff    (float): Multiplier applied to delay after each failure.
        exceptions (tuple): Exception types that trigger a retry.

    Example:
        @retry(times=3, delay=1.0, exceptions=(StorageError, OSError))
        def save_tasks(tasks): ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None

            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < times:
                        logger.warning(
                            f"[retry] {func.__name__} failed "
                            f"(attempt {attempt}/{times}): {e}. "
                            f"Retrying in {current_delay:.1f}s..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"[retry] {func.__name__} failed "
                            f"after {times} attempts: {e}"
                        )
            raise last_exception

        return wrapper
    return decorator


def validate_non_empty(func: Callable) -> Callable:
    """
    Validate that the first argument (tasks list) is non-empty.

    Prints an error message and returns early if the list is empty.
    Use on command functions that require at least one task.

    Example:
        @validate_non_empty
        def cmd_done(tasks: list) -> None: ...
    """
    @functools.wraps(func)
    def wrapper(tasks, *args, **kwargs):
        if not tasks:
            print(f"\n  ✗ No tasks available for '{func.__name__}'. "
                  f"Add a task first.\n")
            return None
        return func(tasks, *args, **kwargs)
    return wrapper


def validate_tasks_arg(func: Callable) -> Callable:
    """
    Validate that the first argument is a list and all items are Task instances.

    Raises:
        TypeError: If tasks is not a list or contains non-Task items.
    """
    from .core.task import Task

    @functools.wraps(func)
    def wrapper(tasks, *args, **kwargs):
        if not isinstance(tasks, list):
            raise TypeError(f"{func.__name__} expects a list, "
                            f"got {type(tasks).__name__}")
        non_tasks = [t for t in tasks if not isinstance(t, Task)]
        if non_tasks:
            raise TypeError(f"{func.__name__} requires a list of Task objects. "
                            f"Found: {[type(t).__name__ for t in non_tasks]}")
        return func(tasks, *args, **kwargs)
    return wrapper


def log_call(level: str = "debug"):
    """
    Log every call to the decorated function — arguments and return value.

    Args:
        level (str): Logging level — 'debug', 'info', 'warning'.

    Example:
        @log_call(level="info")
        def load_tasks(filepath): ...
    """
    log_fn_map = {
        "debug":   logger.debug,
        "info":    logger.info,
        "warning": logger.warning,
    }
    log_fn = log_fn_map.get(level, logger.debug)

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            arg_summary = f"args={args!r}" if args else ""
            kw_summary  = f"kwargs={kwargs!r}" if kwargs else ""
            params      = ", ".join(filter(None, [arg_summary, kw_summary]))
            log_fn(f"[call] {func.__name__}({params})")
            result = func(*args, **kwargs)
            log_fn(f"[return] {func.__name__} → {result!r}")
            return result
        return wrapper
    return decorator


def deprecated(message: str = ""):
    """
    Mark a function as deprecated — logs a warning on every call.

    Args:
        message (str): Additional guidance, e.g. what to use instead.

    Example:
        @deprecated("Use save_tasks() instead.")
        def old_save(tasks): ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import warnings
            warn_msg = f"{func.__name__} is deprecated."
            if message:
                warn_msg += f" {message}"
            warnings.warn(warn_msg, DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

---

### Building `taskflow/context.py`

```python
# taskflow/context.py
# TaskFlow AI — Day 17
# Custom context managers for safe, reversible operations.

import copy
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from .core.task import Task
from .errors    import StorageError

__all__ = [
    "task_snapshot",
    "timed_operation",
    "temporary_data_file",
    "suppress_storage_errors",
]


@contextmanager
def task_snapshot(tasks: list[Task]) -> Generator[list[Task], None, None]:
    """
    Context manager that takes a snapshot of the task list on entry
    and restores it if an exception occurs.

    This allows safe "destructive" operations — if anything goes wrong,
    the original state is automatically restored.

    Args:
        tasks (list[Task]): The task list to snapshot. Modified in place on restore.

    Example:
        with task_snapshot(tasks) as snapshot:
            tasks.clear()
            risky_bulk_operation(tasks)
        # If risky_bulk_operation raises, tasks is restored from snapshot.
    """
    snapshot = copy.deepcopy(tasks)   # deep copy — independent of originals
    try:
        yield snapshot
    except Exception as e:
        # Restore original state
        tasks.clear()
        tasks.extend(snapshot)
        print(f"\n  ⚠  Operation failed: {e}")
        print("  ✓ Task list restored from snapshot.\n")
        raise


@contextmanager
def timed_operation(label: str,
                    warn_threshold: float = 1.0) -> Generator[None, None, None]:
    """
    Context manager that times a block of code and warns if it is slow.

    Args:
        label          (str)  : Human-readable label for the operation.
        warn_threshold (float): Log a warning if operation exceeds this many seconds.

    Example:
        with timed_operation("Load tasks", warn_threshold=0.5):
            tasks = load_tasks()
    """
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        if elapsed >= warn_threshold:
            print(f"  ⚠  [{label}] took {elapsed:.3f}s "
                  f"(threshold: {warn_threshold}s)")
        else:
            print(f"  ⏱  [{label}] completed in {elapsed:.3f}s")


@contextmanager
def temporary_data_file(filepath: Path) -> Generator[Path, None, None]:
    """
    Context manager that backs up a data file before a risky operation
    and restores it if the operation fails.

    Args:
        filepath (Path): Path to the data file to protect.

    Example:
        with temporary_data_file(DATA_FILE):
            dangerous_migration(DATA_FILE)
        # If migration fails, original file is restored.
    """
    backup_path = filepath.with_suffix(".backup")
    restored    = False

    if filepath.exists():
        import shutil
        shutil.copy2(filepath, backup_path)

    try:
        yield filepath
    except Exception as e:
        if backup_path.exists():
            import shutil
            shutil.copy2(backup_path, filepath)
            restored = True
            print(f"\n  ✓ Data file restored from backup after error: {e}\n")
        raise
    finally:
        if backup_path.exists() and not restored:
            backup_path.unlink()   # clean up backup on success


@contextmanager
def suppress_storage_errors(
    default=None,
    log: bool = True
) -> Generator[None, None, None]:
    """
    Context manager that suppresses StorageError and returns a default value.

    Use when storage failure is non-critical — the app should continue.

    Args:
        default: Value to use if a StorageError occurs.
        log     (bool): Log the suppressed error if True.

    Example:
        with suppress_storage_errors(default=[]):
            tasks = load_tasks()
    """
    import logging
    try:
        yield
    except StorageError as e:
        if log:
            logging.getLogger(__name__).warning(
                f"[suppress] StorageError suppressed: {e}"
            )
```

---

### Applying Decorators to TaskFlow AI

```python
# In taskflow/storage/json_store.py — apply decorators

from ..decorators import timer, retry, log_call
from ..errors import StorageError

@log_call(level="debug")
@retry(times=3, delay=0.5, exceptions=(OSError,))
def save_tasks(tasks, filepath=DATA_FILE):
    """Save tasks to JSON with retry on OS errors."""
    ...

@timer(label="Load tasks", log=True)
def load_tasks(filepath=DATA_FILE):
    """Load tasks from JSON, timed."""
    ...


# In taskflow/integrations/weather.py — apply retry to network calls

from ..decorators import retry
import requests

@retry(times=3, delay=2.0, backoff=2.0,
       exceptions=(requests.exceptions.RequestException,))
def fetch_weather(latitude, longitude, location_name=""):
    """Fetch weather with automatic retry on network failure."""
    ...


# In taskflow/display/commands.py — apply validation decorator

from ..decorators import validate_non_empty

@validate_non_empty
def cmd_done(tasks):
    """Mark a task done — requires non-empty task list."""
    ...

@validate_non_empty
def cmd_remove(tasks):
    """Remove a task — requires non-empty task list."""
    ...
```

---

### `contextlib` Utilities

```python
from contextlib import suppress, nullcontext, ExitStack

# suppress — silently ignore specific exceptions
from contextlib import suppress

with suppress(FileNotFoundError):
    Path("optional_file.json").unlink()   # no crash if file doesn't exist

# nullcontext — conditional context manager
def get_context(use_snapshot: bool, tasks: list):
    if use_snapshot:
        return task_snapshot(tasks)
    return nullcontext()   # does nothing — allows consistent with usage

with get_context(safe_mode, tasks):
    do_operation()

# ExitStack — dynamic number of context managers
from contextlib import ExitStack

files_to_process = [Path("a.json"), Path("b.json"), Path("c.json")]

with ExitStack() as stack:
    file_objects = [
        stack.enter_context(open(f, "r", encoding="utf-8"))
        for f in files_to_process
    ]
    # All files open here, all closed automatically when with block exits
    for f in file_objects:
        print(f.read())
```

---

## Exercises

**Exercise 1 — `@cache_result` decorator.**
Write a `@cache_result(ttl_seconds=60)` decorator that caches function return values. If called again within `ttl_seconds`, return the cached result without re-executing. Use a dict `{(args, kwargs_tuple): (result, timestamp)}` as the cache:

```python
@cache_result(ttl_seconds=300)
def fetch_weather(lat, lon, location):
    ...   # expensive network call — only runs once per 5 minutes
```

**Exercise 2 — Decorator introspection.**
After applying multiple decorators, write a function `inspect_decorator_chain(func)` that prints the decorator stack by following `__wrapped__` attributes (set by `@wraps`):

```python
inspect_decorator_chain(save_tasks)
# save_tasks
#   → log_call wrapper
#     → retry wrapper
#       → original save_tasks
```

**Exercise 3 — Class-based decorator.**
Rewrite the `@timer` decorator as a class-based decorator:

```python
class timer:
    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func = func

    def __call__(self, *args, **kwargs):
        start  = time.perf_counter()
        result = self.func(*args, **kwargs)
        print(f"  ⏱  {self.func.__name__}: {time.perf_counter() - start:.4f}s")
        return result
```

Compare to the function-based version. When is the class-based approach preferable?

**Exercise 4 — `task_snapshot` in practice.**
Write a `bulk_update(tasks, update_fn)` function that applies `update_fn` to every task. Wrap the operation in `task_snapshot` so if `update_fn` raises on any task, all changes are rolled back:

```python
def mark_all_high_urgent(tasks):
    def update(task):
        task.priority = "high"
        if some_condition(task):
            raise ValueError("Cannot update this task")
    with task_snapshot(tasks):
        for task in tasks:
            update(task)
```

**Exercise 5 — `@validate_tasks_arg` in action.**
Apply `@validate_tasks_arg` to `calculate_stats()`, `display_tasks()`, and `save_tasks()`. Then deliberately call each with wrong argument types (a string, a number, a list containing dicts). Verify the `TypeError` is raised with a clear message each time.

**Exercise 6 (stretch) — Parametric `@validate` decorator.**
Write a general-purpose `@validate` decorator factory that accepts a list of validator functions — any callable that takes `(func, args, kwargs)` and either passes silently or raises `ValidationError`:

```python
def non_empty_tasks(func, args, kwargs):
    tasks = args[0] if args else kwargs.get("tasks", [])
    if not tasks:
        raise ValidationError(f"{func.__name__} requires non-empty task list")

def within_limit(limit):
    def validator(func, args, kwargs):
        tasks = args[0] if args else kwargs.get("tasks", [])
        if len(tasks) > limit:
            raise ValidationError(f"Too many tasks: {len(tasks)} > {limit}")
    return validator

@validate([non_empty_tasks, within_limit(100)])
def cmd_done(tasks):
    ...
```

---

## Checkpoint

Before moving to Day 18:

- [ ] I understand decorators as functions-returning-functions
- [ ] I always use `@functools.wraps(func)` inside every decorator
- [ ] I can write decorators with arguments using the factory pattern
- [ ] I can stack multiple decorators and explain the application order
- [ ] `@timer`, `@retry`, `@validate_non_empty`, `@log_call`, `@deprecated` are implemented
- [ ] I understand `__enter__` / `__exit__` for class-based context managers
- [ ] I can write generator-based context managers with `@contextmanager`
- [ ] `task_snapshot`, `timed_operation`, `temporary_data_file` are implemented
- [ ] I know `contextlib.suppress`, `nullcontext`, and `ExitStack`
- [ ] Decorators are applied to `save_tasks`, `load_tasks`, `fetch_weather`, and command functions

---

## Common Errors on Day 17

**Forgetting `@wraps` — metadata lost:**

```python
def decorator(func):
    def wrapper(*args, **kwargs):   # ← __name__ is "wrapper", not func's name
        return func(*args, **kwargs)
    return wrapper
# Fix: add @functools.wraps(func) above wrapper
```

**Decorator with arguments — wrong nesting level:**

```python
# ❌ Wrong — trying to use arguments without factory
def retry(func, times=3):   # times is mixed with func
    @wraps(func)
    def wrapper(*args, **kwargs): ...
    return wrapper

# ✅ Correct — factory returns decorator
def retry(times=3):         # factory takes arguments
    def decorator(func):    # decorator takes function
        @wraps(func)
        def wrapper(*args, **kwargs): ...
        return wrapper
    return decorator
```

**`__exit__` return value — accidentally suppressing exceptions:**

```python
def __exit__(self, exc_type, exc_val, exc_tb):
    self.cleanup()
    return True   # ❌ suppresses ALL exceptions — silent failures

def __exit__(self, exc_type, exc_val, exc_tb):
    self.cleanup()
    return False  # ✅ re-raises exception (or return None — same effect)
```

**Generator context manager — yielding more than once:**

```python
@contextmanager
def bad_context():
    yield "first"
    yield "second"   # ❌ RuntimeError: generator didn't stop after yield
```

A `@contextmanager` generator must yield exactly once.

---

## What's Coming

On **Day 18** we tackle virtual environments and dependency management — the professional Python developer's workflow. You will learn `venv`, `pip`, `requirements.txt`, `pip-tools`, and get a first look at `uv` — the blazing-fast package manager taking the Python world by storm in 2025. TaskFlow AI gets a locked, reproducible dependency setup and a proper development vs production dependency separation.