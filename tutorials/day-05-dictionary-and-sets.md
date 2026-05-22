# Day 05 — Dictionaries & Sets

> **Series:** Python & AI Engineering — Zero to Production
> **Phase:** 1 — Foundations
> **Python Version:** 3.14
> **Project:** TaskFlow AI — Upgrading tasks from strings to rich objects

---

## Learning Objective

By the end of today, you will understand Python's two most powerful data structures for structured and unique data — dictionaries and sets. You will upgrade TaskFlow AI so every task is no longer a plain string but a rich dictionary with a title, priority, status, category, and creation date. This is the first major architectural upgrade of the project.

---

## What We Build Today

An upgraded `tasks.py` where each task is a full dictionary object. The app now supports priorities, statuses, and categories — and the display is a properly formatted table.

```
========================================
   TaskFlow AI — Task Manager v0.2
========================================

Commands: add | view | remove | done | quit

> add
Title    : Review pull request
Priority : high
Category : work

✓ Task added! (1 task total)

> add
Title    : Buy groceries
Priority : low
Category : personal

✓ Task added! (2 tasks total)

> view

Your Tasks:
------------------------------------------------------------
  #   Title                    Priority   Category   Status
------------------------------------------------------------
  1   Review pull request      HIGH       work       pending
  2   Buy groceries            LOW        personal   pending
------------------------------------------------------------

> done
Mark task number as done: 1
✓ "Review pull request" marked as done!

> view

Your Tasks:
------------------------------------------------------------
  #   Title                    Priority   Category   Status
------------------------------------------------------------
  1   Review pull request      HIGH       work       ✓ done
  2   Buy groceries            LOW        personal   pending
------------------------------------------------------------
```

---

## Concepts Covered

- Dictionaries — creating, accessing, updating, deleting
- Dictionary methods — `.keys()`, `.values()`, `.items()`, `.get()`, `.update()`
- Nested dictionaries — dicts inside dicts
- Looping over dictionaries
- Sets — unique unordered collections
- Set operations — union, intersection, difference
- `in` with dicts and sets
- List of dicts — the most common real-world data pattern
- `datetime` for timestamps
- Upgrading a project's data model without breaking existing logic

---

## Full Tutorial

### The Problem with Plain Strings

Yesterday's task list stored tasks as plain strings:

```python
tasks = ["Buy groceries", "Review PR", "Write tests"]
```

This works for a demo but fails for a real app. How do you store the priority of a task? Its due date? Whether it is done or still pending? Its category?

You could hack it — `"[HIGH] Buy groceries"` — but that is fragile and impossible to query cleanly. The right solution is a **dictionary**.

---

### What Is a Dictionary?

A dictionary stores data as **key-value pairs**. Instead of accessing data by position (index), you access it by name (key). Think of it like a real dictionary: you look up a word (key) to get its definition (value).

```python
task = {
    "title":    "Review pull request",
    "priority": "high",
    "status":   "pending",
    "category": "work"
}
```

Keys are almost always strings. Values can be anything — strings, numbers, booleans, lists, even other dictionaries.

---

### Creating & Accessing Dictionaries

```python
task = {
    "title":    "Review pull request",
    "priority": "high",
    "status":   "pending",
    "done":     False
}

# Access a value by key
print(task["title"])      # "Review pull request"
print(task["priority"])   # "high"

# Safe access with .get() — returns None (or a default) if key doesn't exist
print(task.get("due_date"))           # None — no crash
print(task.get("due_date", "N/A"))    # "N/A" — custom default
```

**`dict["key"]` vs `dict.get("key")`:**

- `dict["key"]` raises a `KeyError` if the key does not exist.
- `dict.get("key")` returns `None` (or your default) — safe for optional fields.

Always use `.get()` when a key might not be present. Always use `dict["key"]` when the key must exist (so you catch bugs loudly if it doesn't).

---

### Adding, Updating & Deleting

```python
task = {"title": "Review PR", "priority": "high"}

# Add a new key-value pair
task["status"] = "pending"
task["category"] = "work"

# Update an existing value
task["priority"] = "urgent"

# Update multiple keys at once
task.update({"status": "done", "category": "engineering"})

# Delete a key
del task["category"]

# Remove and return a value
status = task.pop("status")    # removes "status" and returns its value

print(task)
# {"title": "Review PR", "priority": "urgent"}
```

---

### Dictionary Methods

```python
task = {
    "title":    "Review PR",
    "priority": "high",
    "status":   "pending",
    "category": "work"
}

# Get all keys
print(task.keys())     # dict_keys(["title", "priority", "status", "category"])

# Get all values
print(task.values())   # dict_values(["Review PR", "high", "pending", "work"])

# Get all key-value pairs as tuples
print(task.items())    # dict_items([("title", "Review PR"), ...])

# Check if a key exists
print("title" in task)      # True
print("due_date" in task)   # False

# Number of keys
print(len(task))    # 4
```

---

### Looping Over Dictionaries

```python
task = {"title": "Review PR", "priority": "high", "status": "pending"}

# Loop over keys (default)
for key in task:
    print(key)

# Loop over values
for value in task.values():
    print(value)

# Loop over key-value pairs — most common
for key, value in task.items():
    print(f"{key:<12}: {value}")

# Output:
# title       : Review PR
# priority    : high
# status      : pending
```

---

### Nested Dictionaries

Dictionaries can contain other dictionaries. This is how complex objects are modelled:

```python
user = {
    "name": "Udit Rawat",
    "plan": "premium",
    "settings": {
        "theme":         "dark",
        "notifications": True,
        "language":      "en"
    }
}

# Access nested values
print(user["settings"]["theme"])          # "dark"
print(user["settings"]["notifications"])  # True

# Safe nested access
print(user.get("settings", {}).get("language", "en"))   # "en"
```

Nested dicts are everywhere in real applications — API responses, database records, configuration files. Get comfortable reading and navigating them.

---

### List of Dictionaries — The Real-World Pattern

The most common data pattern you will encounter in production Python code: a **list of dictionaries**. Each dictionary is one record (one task, one user, one product). The list holds all of them.

```python
tasks = [
    {"id": 1, "title": "Review PR",      "priority": "high", "status": "pending"},
    {"id": 2, "title": "Buy groceries",  "priority": "low",  "status": "pending"},
    {"id": 3, "title": "Write tests",    "priority": "high", "status": "done"},
]

# Access the second task's title
print(tasks[1]["title"])   # "Buy groceries"

# Loop and display
for task in tasks:
    print(f"{task['id']}. [{task['priority'].upper()}] {task['title']} — {task['status']}")

# Filter — find all high-priority tasks
high_priority = [t for t in tasks if t["priority"] == "high"]

# Filter — find all pending tasks
pending = [t for t in tasks if t["status"] == "pending"]
```

This list-of-dicts pattern is how REST APIs return data, how databases return rows, and how almost every data-driven feature in this series works. Internalize it today.

---

### Sets — Unique Unordered Collections

A set is like a list but with two key differences: **no duplicates** and **no guaranteed order**.

```python
categories = {"work", "personal", "health", "work", "personal"}
print(categories)    # {"work", "personal", "health"} — duplicates removed

tags = set()                 # create an empty set (NOT {} — that creates a dict)
tags.add("python")
tags.add("ai")
tags.add("python")           # duplicate — silently ignored
print(tags)                  # {"python", "ai"}
```

**Set operations — the real power of sets:**

```python
my_skills   = {"python", "sql", "docker", "git"}
job_requires = {"python", "docker", "kubernetes", "terraform"}

# Union — all skills from both (no duplicates)
all_skills = my_skills | job_requires
print(all_skills)
# {"python", "sql", "docker", "git", "kubernetes", "terraform"}

# Intersection — skills I have that the job needs
matching = my_skills & job_requires
print(matching)    # {"python", "docker"}

# Difference — skills the job needs that I don't have (gaps)
gaps = job_requires - my_skills
print(gaps)        # {"kubernetes", "terraform"}

# Symmetric difference — skills unique to either side
unique_to_each = my_skills ^ job_requires
print(unique_to_each)   # {"sql", "git", "kubernetes", "terraform"}
```

In TaskFlow AI, we will use sets to manage unique task categories and tags — ensuring no category appears twice in the system.

---

### `datetime` — Timestamps for Tasks

Every real task needs a creation timestamp. Python's `datetime` module handles this:

```python
import datetime

now = datetime.datetime.now()
print(now)                              # 2025-05-19 14:32:05.123456
print(now.strftime("%Y-%m-%d %H:%M"))  # "2025-05-19 14:32"
print(now.strftime("%d %b %Y"))        # "19 May 2025"

# Store as a string for display, keep the object for math
today = datetime.date.today()
due = datetime.date(2025, 6, 1)
days_remaining = (due - today).days
print(f"Due in {days_remaining} days")
```

---

### Building the Upgraded `tasks.py`

Replace the contents of `tasks.py` with this upgraded version:

```python
# tasks.py
# TaskFlow AI — Day 05
# Tasks are now rich dictionary objects with title, priority, category, status, and timestamp.

import datetime

# --- Constants ---
APP_NAME    = "TaskFlow AI"
VERSION     = "0.2"
USER_NAME   = "Udit"
USER_PLAN   = "free"
MAX_TASKS   = 10

VALID_PRIORITIES = {"high", "medium", "low"}
VALID_CATEGORIES = {"work", "personal", "health", "learning", "other"}

# --- State ---
tasks      = []          # list of task dicts
task_id    = 1           # auto-incrementing ID counter
categories = set()       # track unique categories in use

# --- Helper: Create a task dict ---
def make_task(title, priority, category):
    global task_id
    task = {
        "id":         task_id,
        "title":      title,
        "priority":   priority.lower(),
        "category":   category.lower(),
        "status":     "pending",
        "done":       False,
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    task_id += 1
    return task

# --- Helper: Display tasks as a table ---
def display_tasks(task_list):
    if not task_list:
        print("\n  No tasks yet. Type 'add' to get started.\n")
        return

    col_title    = 24
    col_priority = 10
    col_category = 12
    col_status   = 10
    total_width  = 4 + col_title + col_priority + col_category + col_status + 6

    header = (
        f"  {'#':<4}"
        f"{'Title':<{col_title}}"
        f"{'Priority':<{col_priority}}"
        f"{'Category':<{col_category}}"
        f"{'Status':<{col_status}}"
    )

    print()
    print("-" * total_width)
    print(header)
    print("-" * total_width)

    for i, task in enumerate(task_list, start=1):
        status_display = "✓ done" if task["done"] else "pending"
        title_display  = task["title"][:col_title - 2] + ".." \
                         if len(task["title"]) > col_title - 1 \
                         else task["title"]
        print(
            f"  {i:<4}"
            f"{title_display:<{col_title}}"
            f"{task['priority'].upper():<{col_priority}}"
            f"{task['category']:<{col_category}}"
            f"{status_display:<{col_status}}"
        )

    print("-" * total_width)

    # Summary line
    done_count    = sum(1 for t in task_list if t["done"])
    pending_count = len(task_list) - done_count
    print(f"  {len(task_list)} total · {pending_count} pending · {done_count} done")

    # Active categories
    if categories:
        print(f"  Categories in use: {', '.join(sorted(categories))}")
    print()

# --- Command: Add task ---
def add_task():
    if len(tasks) >= MAX_TASKS:
        print(f"\n  ✗ Limit reached ({MAX_TASKS} tasks on {USER_PLAN} plan). "
              f"Upgrade to premium for more.\n")
        return

    title = input("  Title    : ").strip()
    if not title:
        print("  ✗ Title cannot be empty.\n")
        return

    # Validated priority input loop
    while True:
        priority = input("  Priority : ").strip().lower()
        if priority in VALID_PRIORITIES:
            break
        print(f"  ✗ Enter one of: {', '.join(sorted(VALID_PRIORITIES))}")

    # Validated category input loop
    while True:
        category = input("  Category : ").strip().lower()
        if category in VALID_CATEGORIES:
            break
        print(f"  ✗ Enter one of: {', '.join(sorted(VALID_CATEGORIES))}")

    task = make_task(title, priority, category)
    tasks.append(task)
    categories.add(category)

    count = len(tasks)
    print(f"\n  ✓ Task added! ({count} task{'s' if count != 1 else ''} total)\n")

    # Soft limit warnings
    if count == MAX_TASKS - 2:
        print(f"  ⚠ Warning: 2 tasks until your {USER_PLAN} plan limit.\n")
    elif count == MAX_TASKS:
        print(f"  ⚠ Task limit reached. Upgrade to premium for more.\n")

# --- Command: Mark task done ---
def mark_done():
    pending = [t for t in tasks if not t["done"]]
    if not pending:
        print("\n  ✓ All tasks are already done! Great work.\n")
        return

    display_tasks(tasks)
    raw = input("  Mark task number as done: ").strip()

    if not raw.isdigit():
        print("  ✗ Please enter a valid number.\n")
        return

    index = int(raw) - 1
    if 0 <= index < len(tasks):
        if tasks[index]["done"]:
            print(f"  ✗ Task already marked as done.\n")
        else:
            tasks[index]["done"]   = True
            tasks[index]["status"] = "done"
            print(f"\n  ✓ \"{tasks[index]['title']}\" marked as done!\n")
    else:
        print(f"  ✗ Invalid number. Choose between 1 and {len(tasks)}.\n")

# --- Command: Remove task ---
def remove_task():
    if not tasks:
        print("\n  ✗ No tasks to remove.\n")
        return

    display_tasks(tasks)
    raw = input("  Remove task number: ").strip()

    if not raw.isdigit():
        print("  ✗ Please enter a valid number.\n")
        return

    index = int(raw) - 1
    if 0 <= index < len(tasks):
        removed = tasks.pop(index)
        # Rebuild categories set from remaining tasks
        categories.clear()
        for t in tasks:
            categories.add(t["category"])
        remaining = len(tasks)
        print(f"\n  ✓ \"{removed['title']}\" removed. "
              f"({remaining} task{'s' if remaining != 1 else ''} remaining)\n")
    else:
        print(f"  ✗ Invalid number. Choose between 1 and {len(tasks)}.\n")

# --- Command: Filter by priority ---
def filter_by_priority():
    while True:
        priority = input("  Show priority (high/medium/low): ").strip().lower()
        if priority in VALID_PRIORITIES:
            break
        print(f"  ✗ Enter one of: high, medium, low")

    filtered = [t for t in tasks if t["priority"] == priority]
    if not filtered:
        print(f"\n  No {priority}-priority tasks found.\n")
    else:
        print(f"\n  {priority.upper()} priority tasks:")
        display_tasks(filtered)

# --- Main Command Loop ---
print("=" * 40)
print(f"   {APP_NAME} — Task Manager v{VERSION}")
print("=" * 40)
print(f"\n  Hello, {USER_NAME}! Plan: {USER_PLAN.title()} ({MAX_TASKS} tasks max)")
print("\n  Commands: add | view | done | remove | filter | quit\n")

while True:
    command = input("> ").strip().lower()

    if command == "add":
        add_task()
    elif command == "view":
        display_tasks(tasks)
    elif command == "done":
        mark_done()
    elif command == "remove":
        remove_task()
    elif command == "filter":
        filter_by_priority()
    elif command == "quit":
        count = len(tasks)
        done  = sum(1 for t in tasks if t["done"])
        print(f"\n  Goodbye, {USER_NAME}!")
        if count == 0:
            print("  No tasks — clean slate. See you tomorrow.")
        else:
            print(f"  {done}/{count} tasks completed. Keep going!")
        break
    elif command == "":
        continue
    else:
        print(f"\n  ✗ Unknown command '{command}'.")
        print("  Try: add | view | done | remove | filter | quit\n")
```

Run it:

```bash
python tasks.py
```

---

### Understanding Key Lines

**`global task_id`**

Inside `make_task()`, we need to modify `task_id` which lives outside the function. `global` tells Python "use the one from the outer scope, not a new local one." We will replace this pattern with a class on Day 12 — `global` is a stepping stone, not the destination.

**`categories = set()` rebuilt after remove:**

When a task is removed, we rebuild the `categories` set from scratch by looping the remaining tasks. This ensures the set always reflects reality — no ghost categories for tasks that no longer exist. Sets make this check trivial: `categories.add(t["category"])` silently ignores duplicates.

**`sum(1 for t in tasks if t["done"])`**

A generator expression inside `sum()`. It counts the number of tasks where `done` is `True`. We will cover generators fully in Phase 2 — for now, read it as "count tasks where done is True."

**Title truncation:**

```python
title_display = task["title"][:col_title - 2] + ".." \
                if len(task["title"]) > col_title - 1 \
                else task["title"]
```

Long titles would break the table layout. This trims them and adds `".."` — the standard truncation pattern you see in every professional terminal UI.

---

## Exercises

**Exercise 1 — Add a `search` command.**
Ask for a keyword. Search through all task titles (case-insensitive). Display matching tasks using `display_tasks()`. Show `"No tasks match."` if nothing found.

**Exercise 2 — Task detail view.**
Add a `"detail"` command. Ask for a task number. Display everything about that task — including its `created_at` timestamp and `id` — in a vertical key-value format:

```
Task Detail — #1
-----------------
ID         : 1
Title      : Review pull request
Priority   : HIGH
Category   : work
Status     : pending
Created    : 2025-05-19 14:32
```

**Exercise 3 — Nested dictionary: user settings.**
Create a `user` dictionary with nested `settings`:

```python
user = {
    "name": "Udit Rawat",
    "plan": "free",
    "settings": {
        "theme": "dark",
        "notifications": True,
        "show_timestamps": False,
    }
}
```

Add a `"settings"` command that displays the current settings and lets the user toggle `notifications` on or off.

**Exercise 4 — Set operations in practice.**
After a few tasks are added, display a summary of unique categories using set operations:

```python
work_tasks     = {t["title"] for t in tasks if t["category"] == "work"}
personal_tasks = {t["title"] for t in tasks if t["category"] == "personal"}
overlap        = work_tasks & personal_tasks   # shouldn't be any!
```

Print the count of tasks per category using the `categories` set.

**Exercise 5 — Sort by priority.**
Add a `"sort"` command that reorders the `tasks` list: high → medium → low. Use a dictionary to define priority order:

```python
priority_order = {"high": 0, "medium": 1, "low": 2}
tasks.sort(key=lambda t: priority_order[t["priority"]])
```

Don't worry about `lambda` fully yet — Day 16 covers it in depth. For now, just use this pattern and see it work.

**Exercise 6 (stretch) — Stats command.**
Add a `"stats"` command that displays a summary dashboard:

```
  Task Statistics
  ---------------
  Total tasks   : 5
  Done          : 2 (40.0%)
  Pending       : 3 (60.0%)

  By Priority:
    HIGH        : 2
    MEDIUM      : 2
    LOW         : 1

  By Category:
    work        : 3
    personal    : 2

  Categories used: 2 of 5 available
```

---

## Checkpoint

Before moving to Day 06:

- [ ] I can create, access, update, and delete dictionary keys
- [ ] I use `.get()` for optional keys and `dict["key"]` for required ones
- [ ] I can loop over `.keys()`, `.values()`, and `.items()`
- [ ] I understand nested dictionaries and how to access them
- [ ] I can store and query a list of dictionaries
- [ ] I know what a set is and why duplicates are impossible in one
- [ ] I can use `|`, `&`, `-` for set union, intersection, and difference
- [ ] I understand when to use a list vs a dict vs a set
- [ ] `tasks.py` v0.2 runs with rich task objects, table display, and category tracking

---

## Common Errors on Day 05

**`KeyError: 'due_date'`**

```python
task = {"title": "Review PR", "priority": "high"}
print(task["due_date"])          # ❌ KeyError — key doesn't exist
print(task.get("due_date"))      # ✅ returns None safely
print(task.get("due_date", "—")) # ✅ returns "—" as default
```

**`TypeError: unhashable type: 'list'`** when adding to a set:

```python
my_set = set()
my_set.add("python")    # ✅ strings are hashable
my_set.add([1, 2, 3])   # ❌ lists are not hashable — use a tuple instead
my_set.add((1, 2, 3))   # ✅ tuples are hashable
```

Sets and dictionary keys must be **hashable** — immutable types like strings, numbers, and tuples. Lists and dicts are mutable, so they cannot be set members or dict keys.

**`{}` creates a dict, not a set:**

```python
empty_dict = {}          # dict — NOT a set
empty_set  = set()       # correct empty set
one_item   = {"python"}  # set — only works with at least one item
```

Always use `set()` for an empty set. `{}` is reserved for empty dictionaries.

**Mutating a dict while iterating:**

```python
for key in task:
    del task[key]   # ❌ RuntimeError: dictionary changed size during iteration

# Fix: iterate over a copy of the keys
for key in list(task.keys()):
    del task[key]   # ✅ safe
```

---

## What's Coming

On **Day 06** we formalize what you have been writing informally for two days — functions. You have already seen `def` used in `tasks.py`. Tomorrow we go deep: parameters, default values, return values, scope, and docstrings. We will extract every repeated pattern from `tasks.py` into clean, well-named functions — and the codebase will become dramatically more readable and reusable overnight.
