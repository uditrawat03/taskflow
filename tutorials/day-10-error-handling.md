# Day 10 — Error Handling

> **Series:** Python & AI Engineering — Zero to Production
> **Phase:** 1 — Foundations
> **Python Version:** 3.14
> **Project:** TaskFlow AI — Making the app genuinely crash-proof

---

## Learning Objective

By the end of today, TaskFlow AI will handle every foreseeable failure gracefully — bad input, missing files, network errors, corrupted data — without a single unhandled crash. You will understand Python's full exception system: `try/except/else/finally`, `raise`, custom exceptions, and exception chaining. This is the difference between demo code and production code.

---

## What We Build Today

A hardened `errors.py` module with custom exceptions, plus a complete error-handling pass across every risky operation in the app. Every function that can fail will now fail gracefully, with a clear message and a safe recovery path.

```
# Before — crashes on bad input
> add
  Title    : Buy groceries
  Priority : super-urgent
  ✗ Invalid priority. Choose from: high, medium, low
  [works fine]

# But what about this?
$ python tasks.py
  ✗ Storage file is corrupted — creating backup and starting fresh.
  ✓ Backup saved: taskflow_backup_20250519_143201.json
  ✓ Starting with empty task list.

# Or this?
> weather
  ✗ Weather service unavailable (Connection timeout).
  ℹ  Showing last cached weather from 14:20.
  38°C ☀ Clear sky

# Or this in a future import:
try:
    tasks = load_tasks()
except StorageError as e:
    print(f"Storage failed: {e}")
    tasks = []
```

---

## Concepts Covered

- `try / except / else / finally` — the full exception block
- Catching specific exception types
- Catching multiple exceptions
- The exception hierarchy
- `raise` — raising exceptions intentionally
- `raise ... from ...` — exception chaining
- Custom exception classes
- `else` in try blocks — runs only when no exception occurs
- `finally` — always runs, even on exception
- Re-raising exceptions
- Logging errors vs printing them
- When NOT to catch exceptions
- Python 3.14: exception notes (`add_note()`)

---

## Full Tutorial

### Why `if` Checks Are Not Enough

You have been defending against errors with `if` checks:

```python
raw = input("Age: ").strip()
if raw.isdigit():
    age = int(raw)
else:
    print("Invalid age")
    age = 0
```

This works for anticipated problems. But what about unanticipated ones?

- The JSON file exists but was written by a different version of the app and has unexpected fields
- The network request succeeds but the API changed its response format
- The disk is full and `write()` fails halfway through
- A library you are calling raises an exception you did not expect

`if` checks require you to predict every possible failure in advance. Exceptions let you write the happy path clearly, then handle failures in one place.

---

### The `try / except` Block

```python
# Without exception handling
age = int(input("Age: "))   # crashes if user types "abc"

# With exception handling
try:
    age = int(input("Age: "))
except ValueError:
    print("Please enter a whole number.")
    age = 0
```

**How it works:**
1. Python executes the `try` block
2. If no exception occurs, the `except` block is skipped entirely
3. If an exception occurs, Python checks if it matches the `except` type
4. If it matches, the `except` block runs
5. Execution continues after the entire `try/except` structure

---

### Catching Specific Exceptions

Always catch the most specific exception you can. Catching `Exception` (the base class) is a code smell — it hides bugs:

```python
# ❌ Too broad — catches everything, hides real bugs
try:
    data = json.load(f)
except Exception:
    data = []

# ✅ Specific — only catches what we expect
try:
    data = json.load(f)
except json.JSONDecodeError:
    print("Storage file is corrupted.")
    data = []
```

---

### Catching Multiple Exceptions

```python
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
except requests.exceptions.ConnectionError:
    print("No internet connection.")
    data = None
except requests.exceptions.Timeout:
    print("Request timed out.")
    data = None
except requests.exceptions.HTTPError as e:
    print(f"Server error: {e.response.status_code}")
    data = None
except json.JSONDecodeError:
    print("Could not parse API response.")
    data = None
```

Each `except` clause handles a different failure mode. Order matters — Python checks them top to bottom and runs the first match.

**Catching multiple types in one clause:**

```python
except (ConnectionError, Timeout) as e:
    print(f"Network problem: {e}")
```

---

### The `as` Keyword — Accessing the Exception

```python
try:
    age = int("twenty-four")
except ValueError as e:
    print(f"Conversion failed: {e}")
    # Output: Conversion failed: invalid literal for int() with base 10: 'twenty-four'
```

The `as e` captures the exception object. Its string representation is the error message. Its type is the exception class. Both are useful for logging.

---

### `else` — Runs Only When No Exception Occurred

```python
try:
    with open("taskflow_tasks.json", "r", encoding="utf-8") as f:
        tasks = json.load(f)
except (OSError, json.JSONDecodeError) as e:
    print(f"Failed to load tasks: {e}")
    tasks = []
else:
    # Only runs if try succeeded — no exception was raised
    print(f"✓ {len(tasks)} tasks loaded successfully.")
```

`else` keeps the "success path" visually separate from the "failure path." Use it when you have code that should only run on success but does not belong inside the `try` block itself.

---

### `finally` — Always Runs

```python
file = None
try:
    file = open("tasks.json", "r", encoding="utf-8")
    data = json.load(file)
except OSError as e:
    print(f"File error: {e}")
    data = []
finally:
    if file:
        file.close()   # runs even if an exception occurred
```

`finally` is used for cleanup — closing files, releasing locks, closing database connections. In practice, the `with` statement handles this automatically (which is why `with` is preferred). But `finally` matters for resources that do not support `with`.

---

### `raise` — Raising Exceptions Intentionally

Sometimes you detect a problem and need to signal it to the caller:

```python
def load_tasks(filepath):
    if not filepath.exists():
        raise FileNotFoundError(f"Storage file not found: {filepath}")

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Storage file is corrupted: {e}") from e
```

`raise ValueError("message")` creates and raises an exception immediately.
`raise ValueError("message") from e` — **exception chaining** — attaches the original exception as context, which helps during debugging.

---

### `raise ... from ...` — Exception Chaining

```python
try:
    data = json.load(f)
except json.JSONDecodeError as e:
    raise ValueError("Storage file is corrupted") from e
```

When Python prints the traceback, it shows both exceptions:

```
json.decoder.JSONDecodeError: Expecting value: line 3 column 1

The above exception was the direct cause of the following exception:

ValueError: Storage file is corrupted
```

This tells you both *what went wrong* (JSONDecodeError) and *what it means* for the application (storage is corrupted). Always chain when converting low-level exceptions to higher-level ones.

---

### Custom Exception Classes

Custom exceptions make your code self-documenting. Callers can catch `StorageError` specifically — not just any `Exception`:

```python
class TaskFlowError(Exception):
    """Base exception for all TaskFlow AI errors."""
    pass

class StorageError(TaskFlowError):
    """Raised when task storage operations fail."""
    pass

class WeatherError(TaskFlowError):
    """Raised when weather API operations fail."""
    pass

class ValidationError(TaskFlowError):
    """Raised when input data fails validation."""
    pass
```

Usage:

```python
def load_tasks(filepath):
    if not filepath.exists():
        raise StorageError(f"Storage file not found: {filepath}")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise StorageError("Storage file contains invalid JSON") from e

# Caller:
try:
    tasks = load_tasks(DATA_FILE)
except StorageError as e:
    print(f"  ✗ {e}")
    tasks = []
```

---

### Python 3.14: Exception Notes — `add_note()`

Python 3.11+ added `add_note()` to exception objects. Python 3.14 makes this even more useful in tracebacks. Notes let you add context to an exception without creating a new one:

```python
try:
    tasks = load_tasks(DATA_FILE)
except StorageError as e:
    e.add_note(f"Filepath: {DATA_FILE}")
    e.add_note("Tip: Run 'python tasks.py --repair' to attempt recovery.")
    raise
```

The traceback will show:

```
StorageError: Storage file contains invalid JSON
  Filepath: /home/udit/taskflow/taskflow_tasks.json
  Tip: Run 'python tasks.py --repair' to attempt recovery.
```

This is invaluable in production where you cannot interactively debug. Use `add_note()` to add runtime context — file paths, user IDs, request parameters — to exceptions before they bubble up to a log.

---

### When NOT to Catch Exceptions

Not every exception should be caught. Some exceptions indicate programming bugs — catch them and you hide the bug:

```python
# ❌ Hiding a bug — your code has a logic error if index is out of range
try:
    task = tasks[index]
except IndexError:
    task = None

# ✅ Fix the bug — validate the index before accessing
if 0 <= index < len(tasks):
    task = tasks[index]
```

**Rules for when to catch:**
- Catch exceptions from **external systems** — files, networks, databases, user input
- Catch exceptions where you have a **meaningful recovery path**
- Never catch `Exception` or `BaseException` broadly — it masks bugs
- Never catch and silently ignore exceptions — at minimum, log them

---

### Building `errors.py`

```python
# errors.py
# TaskFlow AI — Day 10
# Custom exception hierarchy for the entire application.

class TaskFlowError(Exception):
    """
    Base exception for all TaskFlow AI errors.

    Catch this in the main loop to handle any app-level failure.
    Catch subclasses for specific, recoverable failures.
    """
    pass


class StorageError(TaskFlowError):
    """
    Raised when task persistence operations fail.

    Examples:
        - JSON file is corrupted
        - File cannot be read or written
        - Storage file has unexpected structure
    """
    pass


class WeatherError(TaskFlowError):
    """
    Raised when weather API operations fail.

    Examples:
        - No internet connection
        - API returned unexpected response
        - Request timed out
    """
    pass


class ValidationError(TaskFlowError):
    """
    Raised when input data fails business rule validation.

    Examples:
        - Task title is empty
        - Priority is not one of the valid options
        - Task ID is not a positive integer

    Attributes:
        field   (str): The name of the field that failed validation.
        value   (any): The invalid value that was provided.
    """
    def __init__(self, message: str, field: str = "", value=None):
        super().__init__(message)
        self.field = field
        self.value = value

    def __str__(self):
        base = super().__str__()
        if self.field:
            return f"{base} (field: '{self.field}', got: {self.value!r})"
        return base


class TaskNotFoundError(TaskFlowError):
    """
    Raised when a task with the requested ID does not exist.

    Attributes:
        task_id (int): The ID that was not found.
    """
    def __init__(self, task_id: int):
        super().__init__(f"No task found with ID {task_id}")
        self.task_id = task_id
```

---

### Updating `storage.py` with Proper Error Handling

```python
# storage.py — updated for Day 10
import json
import shutil
import datetime
from pathlib import Path
from errors import StorageError

BASE_DIR  = Path(__file__).parent
DATA_FILE = BASE_DIR / "taskflow_tasks.json"
DATE_FMT  = "%Y-%m-%d %H:%M"


def save_tasks(tasks: list, filepath: Path = DATA_FILE) -> None:
    """
    Save tasks to JSON using an atomic write pattern.

    Raises:
        StorageError: If the file cannot be written.
    """
    tmp_path = filepath.with_suffix(".tmp")
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(tasks, f, indent=2, ensure_ascii=False)
        tmp_path.rename(filepath)
    except (OSError, TypeError) as e:
        if tmp_path.exists():
            tmp_path.unlink()
        raise StorageError(f"Could not save tasks: {e}") from e


def load_tasks(filepath: Path = DATA_FILE) -> list:
    """
    Load tasks from JSON.

    Returns an empty list if file does not exist.

    Raises:
        StorageError: If the file exists but cannot be read or parsed.
    """
    if not filepath.exists():
        return []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise StorageError("Storage file contains invalid JSON") from e
    except OSError as e:
        raise StorageError(f"Could not read storage file: {e}") from e

    if not isinstance(data, list):
        raise StorageError(
            f"Storage file has unexpected format: expected list, "
            f"got {type(data).__name__}"
        )

    return data


def load_tasks_safe(filepath: Path = DATA_FILE) -> tuple[list, str | None]:
    """
    Load tasks without raising — returns (tasks, error_message).

    Use in main() where you want to handle errors inline rather than
    propagating them up the call stack.

    Returns:
        tuple: (task_list, None) on success, ([], error_message) on failure.
    """
    try:
        tasks = load_tasks(filepath)
        return tasks, None
    except StorageError as e:
        return [], str(e)
```

---

### Updating `main()` with Full Error Handling

```python
# In tasks.py — updated main() for Day 10

def main() -> None:
    """Entry point with full exception handling."""

    #  Load tasks 
    print("\n  Loading tasks...", end=" ", flush=True)
    tasks, load_error = load_tasks_safe()

    if load_error:
        print(f"\n  ✗ {load_error}")
        print("  ℹ  Creating a backup and starting with an empty task list.")
        try:
            backup_tasks()
        except Exception:
            pass   # backup failure is not critical — continue regardless
        tasks = []
    else:
        count = len(tasks)
        print(f"✓ {count} task{'s' if count != 1 else ''} loaded.")

    next_id = [get_next_id(tasks)]

    #  Fetch weather ─
    try:
        weather = fetch_weather(USER_LATITUDE, USER_LONGITUDE, USER_LOCATION)
    except Exception:
        weather = None   # weather is non-critical — never crash for it

    display_header(weather)
    display_help()

    #  Command loop 
    while True:
        try:
            command = input("> ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            # Handle Ctrl+C and Ctrl+D gracefully
            print("\n\n  Interrupted. Saving tasks before exit...")
            command = "quit"

        try:
            if   command == "add":     cmd_add(tasks, next_id)
            elif command == "view":    display_tasks(tasks)
            elif command == "done":    cmd_done(tasks)
            elif command == "remove":  cmd_remove(tasks)
            elif command == "filter":  cmd_filter(tasks)
            elif command == "search":  cmd_search(tasks)
            elif command == "stats":   display_stats(tasks)
            elif command == "weather":
                weather = fetch_weather(USER_LATITUDE, USER_LONGITUDE, USER_LOCATION)
                display_weather(weather)
            elif command == "backup":  backup_tasks()
            elif command == "help":    display_help()
            elif command == "quit":
                try:
                    save_tasks(tasks)
                    print(f"  ✓ {len(tasks)} tasks saved.")
                except StorageError as e:
                    print(f"  ✗ Could not save tasks: {e}")
                    print("  ⚠  Your tasks may not have been saved.")
                cmd_quit(tasks)
                break
            elif command == "":
                continue
            else:
                print(f"\n  ✗ Unknown command '{command}'. Type 'help'.\n")

        except ValidationError as e:
            print(f"\n  ✗ Validation error: {e}\n")
        except TaskFlowError as e:
            print(f"\n  ✗ Error: {e}\n")
        except Exception as e:
            # Catch-all for truly unexpected errors — log and continue
            print(f"\n  ✗ Unexpected error: {type(e).__name__}: {e}")
            print("  ℹ  The app will continue. Please report this bug.\n")
```

---

## Exercises

**Exercise 1 — Custom exception in `cmd_add()`.**
Update `cmd_add()` to raise `ValidationError` instead of printing and returning:

```python
def validate_task_title(title: str) -> str:
    if not title:
        raise ValidationError("Title cannot be empty", field="title", value=title)
    if len(title) > 200:
        raise ValidationError("Title too long (max 200 chars)", field="title", value=len(title))
    return title.strip()
```

Catch `ValidationError` in the command loop (already done in the updated `main()` above).

**Exercise 2 — Test all exception types.**
Write a `test_exceptions.py` file that deliberately triggers each custom exception and verifies the error message is correct:

```python
from errors import StorageError, ValidationError, TaskNotFoundError

try:
    raise ValidationError("Title too long", field="title", value=250)
except ValidationError as e:
    print(f"Caught: {e}")
    print(f"Field: {e.field}, Value: {e.value}")

try:
    raise TaskNotFoundError(999)
except TaskNotFoundError as e:
    print(f"Caught: {e}")
    print(f"Missing ID: {e.task_id}")
```

**Exercise 3 — `finally` for timing.**
Wrap the weather fetch in a `try/finally` block that measures and prints how long the request took:

```python
import time

start = time.time()
try:
    weather = fetch_weather(...)
finally:
    elapsed = time.time() - start
    print(f"  Weather fetch took {elapsed:.2f}s")
```

**Exercise 4 — Exception notes in practice.**
In `load_tasks()`, before re-raising `StorageError`, add notes with `add_note()`:

```python
except json.JSONDecodeError as e:
    err = StorageError("Storage file contains invalid JSON")
    err.add_note(f"File: {filepath}")
    err.add_note(f"JSON error at line {e.lineno}, column {e.colno}")
    raise err from e
```

Trigger a JSON error by corrupting `taskflow_tasks.json`. Observe the full traceback with notes in Python 3.14.

**Exercise 5 — Retry decorator.**
Write a `retry(times=3, delay=1.0)` decorator that catches exceptions and retries the function up to `times` times with a `delay` second pause between attempts. Apply it to `fetch_weather()`:

```python
import time
from functools import wraps

def retry(times=3, delay=1.0, exceptions=(Exception,)):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == times:
                        raise
                    print(f"  ⚠ Attempt {attempt} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
        return wrapper
    return decorator

@retry(times=3, delay=2.0, exceptions=(WeatherError,))
def fetch_weather_with_retry(lat, lon, location):
    ...
```

**Exercise 6 (stretch) — Exception hierarchy diagram.**
Draw (on paper or in ASCII art in a `.md` file) the full exception hierarchy for TaskFlow AI. Show how `TaskFlowError` → `StorageError`, `WeatherError`, `ValidationError`, `TaskNotFoundError` relates to Python's built-in `BaseException` → `Exception` chain. Add where `OSError`, `ValueError`, `json.JSONDecodeError`, and `requests.exceptions.RequestException` fit. This diagram will be your reference for the rest of Phase 1.

---

## Checkpoint

Before moving to Day 11:

- [ ] I understand `try / except / else / finally` fully
- [ ] I always catch specific exception types — never bare `except:`
- [ ] I use `as e` to access the exception object and its message
- [ ] I understand `raise`, `raise from`, and re-raising
- [ ] I have built a custom exception hierarchy in `errors.py`
- [ ] I use `ValidationError`, `StorageError`, `WeatherError`, `TaskNotFoundError`
- [ ] I understand `add_note()` for Python 3.14 exception notes
- [ ] I know when NOT to catch — hiding bugs with broad `except` is an anti-pattern
- [ ] `main()` handles `KeyboardInterrupt` and `EOFError` gracefully (Ctrl+C, Ctrl+D)
- [ ] Every risky operation in the app is wrapped in appropriate `try/except`

---

## Common Errors on Day 10

**Bare `except:` — catches everything including `SystemExit` and `KeyboardInterrupt`:**

```python
try:
    ...
except:           # ❌ catches EVERYTHING — even Ctrl+C
    pass

try:
    ...
except Exception: # ✅ catches all normal exceptions, not SystemExit/KeyboardInterrupt
    pass
```

**Swallowing exceptions silently:**

```python
try:
    tasks = load_tasks()
except StorageError:
    pass   # ❌ user has no idea something went wrong
```

At minimum, log or print the error. Silent failures are worse than crashes — they corrupt data quietly.

**Wrong exception order — unreachable except clause:**

```python
try:
    ...
except Exception as e:    # ❌ catches everything — the specific clause below never runs
    print(f"Error: {e}")
except StorageError as e:
    print(f"Storage error: {e}")
```

Always put specific exceptions before general ones.

**`raise` without argument re-raises the current exception:**

```python
try:
    load_tasks()
except StorageError as e:
    print(f"Logging: {e}")
    raise   # ✅ re-raises the same StorageError — does not create a new one
```

This is the correct way to log-and-reraise. Do not `raise e` (that loses the original traceback in Python 2 style) — just `raise`.

---

## What's Coming

On **Day 11** we introduce modules and imports in depth. TaskFlow AI now has five files — `tasks.py`, `storage.py`, `weather.py`, `errors.py`, and soon more. Tomorrow we learn how Python's module system works, how to structure a multi-file project cleanly, how to use `__init__.py`, and how the standard library gives you hundreds of powerful tools for free. We will also refactor the import structure of TaskFlow AI and prepare for the week's big milestone — the full v1.0 release on Day 15.
