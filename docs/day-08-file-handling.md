# Day 08 — File Handling

> **Series:** Python & AI Engineering — Zero to Production
> **Phase:** 1 — Foundations
> **Python Version:** 3.14
> **Project:** TaskFlow AI — Making tasks persist between sessions

---

## Learning Objective

By the end of today, TaskFlow AI will remember your tasks after you quit and restart it. You will learn how to read and write files in Python — text files, file paths, the `with` statement, and safe file operations. This is the moment the app crosses from a demo into a tool you can actually use daily.

---

## What We Build Today

A `storage.py` module that handles all file reading and writing for TaskFlow AI. Tasks saved to a `.txt` file survive app restarts.

```
$ python tasks.py
Loading tasks from taskflow_tasks.txt... 3 tasks loaded.

========================================
   TaskFlow AI — Task Manager v0.5
========================================

> view

  ─────────────────────────────────────────────────────
  #   Title                     Priority   Category   Status
  ─────────────────────────────────────────────────────
  1   Review pull request       HIGH       work       ✓ done
  2   Buy groceries             LOW        personal   pending
  3   Write Day 08 tutorial     HIGH       learning   pending
  ─────────────────────────────────────────────────────
  3 tasks · 2 pending · 1 done · 33.3% complete

> add
  Title    : Push code to GitHub
  Priority : high
  Category : work
  ✓ Task added! (4 tasks total)

> quit
  Saving tasks to taskflow_tasks.txt... done.
  Goodbye, Udit! 3/4 tasks completed. Keep going!

$ python tasks.py
Loading tasks from taskflow_tasks.txt... 4 tasks loaded.
```

---

## Concepts Covered

- Opening files — `open()`, modes (`r`, `w`, `a`, `x`)
- Reading files — `.read()`, `.readline()`, `.readlines()`
- Writing files — `.write()`, `.writelines()`
- The `with` statement — context managers for files
- File paths — absolute vs relative, `os.path`
- Checking if a file exists — `os.path.exists()`
- `pathlib.Path` — the modern way to handle paths
- Encoding — always use `utf-8`
- Appending vs overwriting
- Safe file operations — handling missing files gracefully
- Separating storage logic from app logic

---

## Full Tutorial

### Why Persistence Matters

Every time you run `tasks.py` right now, it starts with an empty list. Add ten tasks, quit, restart — gone. This is the most glaring limitation of the current app. Files are the simplest solution: write tasks to disk when the app closes, read them back when it opens.

This is not just a feature — it is an architectural decision. Where does data live? How does it flow in and out of the app? These questions will scale from files (today) to JSON (Day 09) to databases (Day 34). The pattern you learn today is the same one used at every level.

---

### Opening Files — `open()`

The built-in `open()` function opens a file and returns a **file object** you can read from or write to:

```python
file = open("tasks.txt", "r")   # open for reading
content = file.read()
file.close()                    # MUST close when done
```

The second argument is the **mode**:

| Mode | Meaning | File must exist? |
|------|---------|-----------------|
| `"r"` | Read (default) | Yes — `FileNotFoundError` if missing |
| `"w"` | Write (overwrites) | No — creates if missing |
| `"a"` | Append (adds to end) | No — creates if missing |
| `"x"` | Create (exclusive) | No — `FileExistsError` if already exists |
| `"r+"` | Read + write | Yes |

Always pass `encoding="utf-8"` explicitly — it prevents encoding errors on different operating systems:

```python
file = open("tasks.txt", "r", encoding="utf-8")
```

---

### The `with` Statement — Always Use It

Manually calling `file.close()` is error-prone. If an exception occurs between `open()` and `close()`, the file stays open — which can corrupt data or lock the file on Windows.

The `with` statement solves this. It guarantees the file is closed when the block exits, even if an exception occurs:

```python
# Old way — risky
file = open("tasks.txt", "r", encoding="utf-8")
content = file.read()
file.close()   # might never reach here if read() raises an exception

# Correct way — always use with
with open("tasks.txt", "r", encoding="utf-8") as file:
    content = file.read()
# file is automatically closed here, no matter what
```

From today onwards: **always use `with` to open files**. No exceptions.

---

### Reading Files

```python
# Read the entire file as one string
with open("tasks.txt", "r", encoding="utf-8") as f:
    content = f.read()
print(content)

# Read line by line into a list (each line includes the '\n' newline character)
with open("tasks.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()
print(lines)   # ["Buy groceries\n", "Review PR\n", "Write tests\n"]

# Read one line at a time (memory-efficient for large files)
with open("tasks.txt", "r", encoding="utf-8") as f:
    first_line = f.readline()

# Best approach: iterate directly (no \n stripping needed with strip())
with open("tasks.txt", "r", encoding="utf-8") as f:
    for line in f:
        print(line.strip())   # strip() removes the trailing \n
```

---

### Writing Files

```python
# Write (overwrites the entire file each time)
with open("tasks.txt", "w", encoding="utf-8") as f:
    f.write("Buy groceries\n")
    f.write("Review PR\n")
    f.write("Write tests\n")

# Write multiple lines at once
lines = ["Buy groceries\n", "Review PR\n", "Write tests\n"]
with open("tasks.txt", "w", encoding="utf-8") as f:
    f.writelines(lines)

# Append — add to the end without overwriting
with open("tasks.txt", "a", encoding="utf-8") as f:
    f.write("Deploy app\n")
```

---

### File Paths — `os.path` and `pathlib`

A file path tells Python where to find a file. Two styles:

**Relative path** — relative to where the script is run from:

```python
open("tasks.txt")            # same folder as the script
open("data/tasks.txt")       # inside a 'data' subfolder
open("../tasks.txt")         # one folder up
```

**Absolute path** — full path from the root of the filesystem:

```python
open("/home/udit/taskflow/tasks.txt")    # Linux/macOS
open("C:\\Users\\Udit\\taskflow\\tasks.txt")  # Windows
```

**`pathlib.Path` — the modern, cross-platform way:**

```python
from pathlib import Path

# Get the directory where this script lives
BASE_DIR = Path(__file__).parent

# Build paths safely (works on Windows, macOS, Linux)
DATA_FILE = BASE_DIR / "taskflow_tasks.txt"

print(DATA_FILE)          # /home/udit/taskflow/taskflow_tasks.txt
print(DATA_FILE.exists()) # True or False
print(DATA_FILE.name)     # "taskflow_tasks.txt"
print(DATA_FILE.suffix)   # ".txt"
print(DATA_FILE.stem)     # "taskflow_tasks"
```

`pathlib` is cleaner than `os.path` for everything path-related. Use it from now on.

---

### Checking if a File Exists

```python
from pathlib import Path

data_file = Path("taskflow_tasks.txt")

if data_file.exists():
    # safe to read
    with open(data_file, "r", encoding="utf-8") as f:
        content = f.read()
else:
    # file doesn't exist yet — first run
    content = ""
    print("No saved tasks found. Starting fresh.")
```

Never assume a file exists before trying to read it. Always check first.

---

### Building `storage.py`

Create a new file `storage.py` inside your `taskflow` folder. This module handles all file I/O — nothing else. This is the **separation of concerns** principle in action: storage logic lives in `storage.py`, display logic in `tasks.py`, and never the two shall mix.

```python
# storage.py
# TaskFlow AI — Day 08
# Handles all file reading and writing for task persistence.
# Storage format: one task per line, fields separated by pipe '|' character.
# Format: id|title|priority|category|status|done|created_at

from pathlib import Path
import datetime

# ─── Configuration ────────────────────────────────────────
BASE_DIR   = Path(__file__).parent
DATA_FILE  = BASE_DIR / "taskflow_tasks.txt"
SEPARATOR  = "|"
DATE_FMT   = "%Y-%m-%d %H:%M"


# ─── Serialization ────────────────────────────────────────

def task_to_line(task: dict) -> str:
    """
    Convert a task dictionary to a single line string for file storage.

    Format: id|title|priority|category|status|done|created_at

    Args:
        task (dict): A task dictionary.

    Returns:
        str: A pipe-separated string representation of the task.
    """
    return SEPARATOR.join([
        str(task["id"]),
        task["title"],
        task["priority"],
        task["category"],
        task["status"],
        str(task["done"]),
        task["created_at"],
    ])


def line_to_task(line: str) -> dict | None:
    """
    Convert a stored line back into a task dictionary.

    Args:
        line (str): A pipe-separated line from the storage file.

    Returns:
        dict | None: A task dictionary, or None if the line is malformed.
    """
    line = line.strip()
    if not line:
        return None

    parts = line.split(SEPARATOR)
    if len(parts) != 7:
        print(f"  ⚠ Skipping malformed line: '{line}'")
        return None

    task_id, title, priority, category, status, done_str, created_at = parts

    return {
        "id":         int(task_id),
        "title":      title,
        "priority":   priority,
        "category":   category,
        "status":     status,
        "done":       done_str == "True",
        "created_at": created_at,
    }


# ─── File Operations ──────────────────────────────────────

def save_tasks(tasks: list, filepath: Path = DATA_FILE) -> bool:
    """
    Save all tasks to a text file.

    Each task is written as one pipe-separated line.
    Overwrites the file completely on each save.

    Args:
        tasks    (list): List of task dictionaries to save.
        filepath (Path): Path to the storage file.

    Returns:
        bool: True if save succeeded, False otherwise.
    """
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            for task in tasks:
                f.write(task_to_line(task) + "\n")
        return True
    except OSError as e:
        print(f"  ✗ Failed to save tasks: {e}")
        return False


def load_tasks(filepath: Path = DATA_FILE) -> list:
    """
    Load tasks from a text file.

    Returns an empty list if the file does not exist or cannot be read.

    Args:
        filepath (Path): Path to the storage file.

    Returns:
        list: List of task dictionaries loaded from file.
    """
    if not filepath.exists():
        return []

    tasks = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                task = line_to_task(line)
                if task is not None:
                    tasks.append(task)
    except OSError as e:
        print(f"  ✗ Failed to load tasks: {e}")
        return []

    return tasks


def get_next_id(tasks: list) -> int:
    """
    Calculate the next available task ID from the loaded task list.

    Args:
        tasks (list): List of task dictionaries.

    Returns:
        int: The next available ID (max existing ID + 1, or 1 if empty).
    """
    if not tasks:
        return 1
    return max(t["id"] for t in tasks) + 1


def backup_tasks(filepath: Path = DATA_FILE) -> bool:
    """
    Create a timestamped backup of the tasks file.

    Args:
        filepath (Path): Path to the storage file to back up.

    Returns:
        bool: True if backup succeeded, False otherwise.
    """
    if not filepath.exists():
        return False

    timestamp   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = filepath.parent / f"taskflow_tasks_backup_{timestamp}.txt"

    try:
        content = filepath.read_text(encoding="utf-8")
        backup_path.write_text(content, encoding="utf-8")
        print(f"  ✓ Backup saved: {backup_path.name}")
        return True
    except OSError as e:
        print(f"  ✗ Backup failed: {e}")
        return False


def get_storage_info(filepath: Path = DATA_FILE) -> dict:
    """
    Return metadata about the storage file.

    Args:
        filepath (Path): Path to the storage file.

    Returns:
        dict: File metadata — exists, size, last modified.
    """
    if not filepath.exists():
        return {"exists": False, "size_bytes": 0, "last_modified": None}

    stat = filepath.stat()
    return {
        "exists":        True,
        "size_bytes":    stat.st_size,
        "last_modified": datetime.datetime.fromtimestamp(stat.st_mtime)
                                         .strftime(DATE_FMT),
        "filepath":      str(filepath),
    }
```

---

### Integrating `storage.py` into `tasks.py`

Update the top of `tasks.py` to import and use the storage module:

```python
# tasks.py — updated for Day 08
# Add these imports at the top
from storage import load_tasks, save_tasks, get_next_id, get_storage_info

# Update the main() function:
def main() -> None:
    """Entry point — load persisted tasks, run command loop, save on exit."""

    # Load tasks from file
    print(f"\n  Loading tasks from storage...")
    tasks   = load_tasks()
    next_id = [get_next_id(tasks)]

    if tasks:
        print(f"  ✓ {len(tasks)} task{'s' if len(tasks) != 1 else ''} loaded.\n")
    else:
        print("  No saved tasks found. Starting fresh.\n")

    display_header()
    display_help()

    while True:
        command = input("> ").strip().lower()

        if   command == "add":     cmd_add(tasks, next_id)
        elif command == "view":    display_tasks(tasks)
        elif command == "done":    cmd_done(tasks)
        elif command == "remove":  cmd_remove(tasks)
        elif command == "filter":  cmd_filter(tasks)
        elif command == "search":  cmd_search(tasks)
        elif command == "stats":   display_stats(tasks)
        elif command == "backup":  backup_tasks()
        elif command == "storage": show_storage_info()
        elif command == "help":    display_help()
        elif command == "quit":
            # Save before quitting
            print(f"\n  Saving tasks...")
            if save_tasks(tasks):
                print(f"  ✓ {len(tasks)} task{'s' if len(tasks) != 1 else ''} saved.")
            cmd_quit(tasks)
            break
        elif command == "":
            continue
        else:
            print(f"\n  ✗ Unknown command '{command}'. Type 'help' for options.\n")


def show_storage_info() -> None:
    """Display file storage metadata."""
    from storage import get_storage_info, DATA_FILE
    info = get_storage_info(DATA_FILE)
    print("\n  ── Storage Info ──────────────────────")
    if info["exists"]:
        print(f"  File      : {info['filepath']}")
        print(f"  Size      : {info['size_bytes']} bytes")
        print(f"  Modified  : {info['last_modified']}")
    else:
        print("  No storage file found yet.")
    print()


if __name__ == "__main__":
    main()
```

Run it, add tasks, quit, run again. Your tasks are there waiting for you.

---

### Understanding the Storage Format

The storage format is a pipe-separated plain text file:

```
1|Review pull request|high|work|done|True|2025-05-19 14:32
2|Buy groceries|low|personal|pending|False|2025-05-19 14:33
3|Write Day 08 tutorial|high|learning|pending|False|2025-05-19 14:35
```

Why pipe `|` instead of comma `,`? Task titles might contain commas — "Buy milk, eggs, bread" would break comma-separated parsing. Pipes are rare in natural text, making them a safer separator. (On Day 09 we switch to JSON which eliminates this problem entirely.)

Why `str(task["done"])` for booleans? Files store text only. `True` becomes the string `"True"`, and `done_str == "True"` converts it back. Always think about the round-trip: write → read → identical data.

---

## Exercises

**Exercise 1 — Verify round-trip integrity.**
Add a `"verify"` command that loads tasks from disk and compares them to the in-memory list. Print `"✓ Storage consistent"` if they match, or list any discrepancies. This is the simplest form of a data integrity check.

**Exercise 2 — Line count without loading.**
Write a `count_saved_tasks(filepath)` function that opens the file and counts non-empty lines **without** loading the full task list into memory. Use a `for line in f:` loop with a counter. Compare the result to `len(load_tasks())`.

**Exercise 3 — Export to plain text.**
Add an `"export"` command that writes a human-readable plain-text report to `taskflow_report.txt`:

```
TaskFlow AI — Task Report
Generated: 2025-05-19 14:45
==============================

PENDING TASKS (2):
  1. Buy groceries [low] [personal]
  2. Write Day 08 tutorial [high] [learning]

COMPLETED TASKS (1):
  ✓ Review pull request [high] [work]

==============================
Total: 3 tasks | 1 done | 2 pending
```

**Exercise 4 — Read a file line by line.**
Create a `search_in_file(filepath, keyword)` function that searches the raw storage file for lines containing the keyword — without calling `load_tasks()`. Open the file, iterate line by line, and print matching raw lines. Compare this to searching the in-memory list. When would raw file search be preferable?

**Exercise 5 — Auto-save on every change.**
Modify `cmd_add()`, `cmd_done()`, and `cmd_remove()` so they call `save_tasks()` automatically after every successful change. Remove the save from `main()` on quit. What are the trade-offs of saving after every operation vs saving only on exit?

**Exercise 6 (stretch) — Atomic writes.**
The current `save_tasks()` function overwrites the file directly. If Python crashes mid-write, the file could be corrupted and all tasks lost. Implement an **atomic write** pattern:

1. Write to a temporary file: `taskflow_tasks.tmp`
2. If write succeeds, rename the temp file to replace the real file
3. Use `Path.rename()` for the atomic rename

```python
tmp_path = filepath.with_suffix(".tmp")
# write to tmp_path
# then:
tmp_path.rename(filepath)   # atomic on most OS filesystems
```

This guarantees the data file is either fully written or fully intact — never half-written.

---

## Checkpoint

Before moving to Day 09:

- [ ] I always use `with open(...) as f:` — never manual `open()`/`close()`
- [ ] I always pass `encoding="utf-8"` to `open()`
- [ ] I know the four file modes: `r`, `w`, `a`, `x`
- [ ] I use `pathlib.Path` for all file path handling
- [ ] I check `filepath.exists()` before reading
- [ ] I understand serialization — converting Python objects to storable text
- [ ] I understand deserialization — converting stored text back to Python objects
- [ ] `storage.py` is a separate module — storage logic is fully separated from app logic
- [ ] Tasks persist across app restarts — quit, reopen, tasks are there

---

## Common Errors on Day 08

**`FileNotFoundError` when reading:**

```python
with open("tasks.txt", "r") as f:   # ❌ crashes if file doesn't exist
    ...

# Fix: check first
from pathlib import Path
if Path("tasks.txt").exists():
    with open("tasks.txt", "r", encoding="utf-8") as f:
        ...
```

**Data corruption from missing `encoding`:**

```python
with open("tasks.txt", "w") as f:              # ❌ uses system default encoding
with open("tasks.txt", "w", encoding="utf-8") as f:   # ✅ always explicit
```

On Windows the default is often `cp1252`. On Linux it is `utf-8`. Omitting encoding causes files written on one OS to fail on another — a bug that is very hard to diagnose later.

**Forgetting the newline in `write()`:**

```python
f.write("Buy groceries")    # ❌ no newline — next write appends to same line
f.write("Buy groceries\n")  # ✅ newline separates lines
```

**Splitting on the wrong separator:**

```python
line = "1|Review PR|high|work|pending|False|2025-05-19"
parts = line.split(",")   # ❌ wrong separator — produces one giant string
parts = line.split("|")   # ✅ correct
```

**`bool("False") == True`:**

```python
done = bool("False")   # ❌ "False" is a non-empty string — evaluates to True!
done = "False" == "True"  # ❌ also wrong
done = done_str == "True"  # ✅ only True when the string is exactly "True"
```

This is a very common bug when serializing booleans to text. Always compare the string explicitly.

---

## What's Coming

On **Day 09** we replace the pipe-separated text format with JSON — the universal data interchange format and the language of every API you will ever consume. JSON stores task dictionaries directly with no custom serialization code, handles nested data naturally, and opens the door to reading data from real web APIs. The storage module gets a major upgrade, and the `.txt` file becomes a `.json` file.