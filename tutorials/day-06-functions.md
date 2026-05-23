# Day 06 — Functions

> **Series:** Python & AI Engineering — Zero to Production
> **Phase:** 1 — Foundations
> **Python Version:** 3.14
> **Project:** TaskFlow AI — Refactoring into clean, reusable functions

---

## Learning Objective

By the end of today, you will understand functions deeply — not just how to write them, but how to design them well. You will refactor TaskFlow AI so every logical action is encapsulated in a well-named, single-purpose function with proper parameters, return values, and docstrings. The codebase will become dramatically cleaner overnight.

---

## What We Build Today

A refactored `tasks.py` where all logic lives in purpose-built functions. No repeated code. No mystery blocks. Every action has a name, a clear input, and a clear output.

```
# Before (Day 04 style — logic scattered everywhere):
command = input("> ").strip().lower()
if command == "add":
    if len(tasks) >= MAX_TASKS:
        print("Limit reached...")
        return
    task = input("Enter task: ").strip()
    if not task:
        print("Empty...")
        return
    tasks.append(task)
    ...

# After (Day 06 style — clean, named, testable):
command = input("> ").strip().lower()
if command == "add":
    add_task(tasks, user)
```

---

## Concepts Covered

- `def` — defining functions
- Parameters and arguments
- Default parameter values
- Return values — `return`
- Multiple return values
- Keyword arguments
- Docstrings — documenting functions
- Scope — local vs global vs enclosing
- The `global` keyword and why to avoid it
- Pure functions vs functions with side effects
- Single Responsibility Principle — one function, one job
- Type hints on functions (preview of Day 27)

---

## Full Tutorial

### What Is a Function?

A function is a named, reusable block of code that does one specific thing. You define it once. You call it anywhere.

Without functions, code is a wall of instructions. With functions, code reads like a story — `greet_user()`, `add_task()`, `display_tasks()`. You know what each chapter does before reading a single line inside it.

```python
# Define a function
def greet(name):
    print(f"Hello, {name}!")

# Call it — as many times as you want
greet("Udit")
greet("Priya")
greet("Rohan")
```

The `def` keyword starts the definition. The function name follows. Parameters (inputs) go in parentheses. The body is indented. The function does nothing until it is called.

---

### Parameters & Arguments

**Parameter** — the variable name in the function definition.
**Argument** — the actual value passed when calling the function.

```python
def add_task(task_list, title, priority):   # parameters
    task_list.append({"title": title, "priority": priority})

tasks = []
add_task(tasks, "Review PR", "high")        # arguments
```

**Default parameters** — give a parameter a fallback value. If the caller does not supply it, the default is used:

```python
def create_task(title, priority="medium", category="general", status="pending"):
    return {
        "title":    title,
        "priority": priority,
        "category": category,
        "status":   status,
    }

# All defaults
t1 = create_task("Buy groceries")

# Override some
t2 = create_task("Review PR", priority="high", category="work")

# Override all
t3 = create_task("Deploy app", "urgent", "engineering", "in-progress")
```

**Rule:** parameters with defaults must come after parameters without defaults.

```python
def bad(priority="medium", title):   # ❌ SyntaxError
def good(title, priority="medium"):  # ✅ correct
```

---

### Keyword Arguments

When calling a function, you can name the arguments explicitly. This makes calls self-documenting and allows any order:

```python
def create_task(title, priority="medium", category="general"):
    ...

# Positional — order matters
create_task("Review PR", "high", "work")

# Keyword — order doesn't matter, intent is clear
create_task(title="Review PR", category="work", priority="high")

# Mix — positional first, then keyword
create_task("Review PR", category="work", priority="high")
```

Use keyword arguments for functions with more than 2–3 parameters. Your future self will thank you.

---

### Return Values

Functions can send a value back to the caller with `return`:

```python
def calculate_completion_rate(tasks):
    if not tasks:
        return 0.0
    done  = sum(1 for t in tasks if t["done"])
    total = len(tasks)
    return round(done / total * 100, 1)

rate = calculate_completion_rate(tasks)
print(f"Completion rate: {rate}%")
```

**`return` exits the function immediately.** Any code after `return` in the same block is unreachable:

```python
def get_priority_score(priority):
    if priority == "high":
        return 3       # exits here for "high"
    elif priority == "medium":
        return 2       # exits here for "medium"
    return 1           # default for "low" or anything else
```

**Functions without `return` return `None`:**

```python
def print_header():
    print("=" * 40)

result = print_header()
print(result)   # None
```

This is fine — functions that exist purely for their side effects (printing, writing to files, updating state) don't need to return anything.

---

### Multiple Return Values

Python functions can return multiple values as a tuple:

```python
def get_task_stats(tasks):
    total   = len(tasks)
    done    = sum(1 for t in tasks if t["done"])
    pending = total - done
    return total, done, pending    # returns a tuple

# Unpack into separate variables
total, done, pending = get_task_stats(tasks)
print(f"Total: {total}, Done: {done}, Pending: {pending}")
```

This is cleaner than returning a dictionary for simple multi-value returns, and cleaner than using global variables.

---

### Docstrings — Documenting Functions

A docstring is a string literal immediately after the `def` line. It describes what the function does, its parameters, and what it returns. Every function you write from here should have one:

```python
def create_task(title, priority="medium", category="general"):
    """
    Create a new task dictionary with the given attributes.

    Args:
        title    (str): The task title. Must not be empty.
        priority (str): Task priority — "high", "medium", or "low".
                        Defaults to "medium".
        category (str): Task category. Defaults to "general".

    Returns:
        dict: A task dictionary with title, priority, category,
              status, done, and created_at fields.
    """
    import datetime
    return {
        "title":      title,
        "priority":   priority,
        "category":   category,
        "status":     "pending",
        "done":       False,
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
```

Access the docstring programmatically:

```python
print(create_task.__doc__)
help(create_task)
```

VS Code and most editors display docstrings as tooltips when you hover over a function call. Write them for your tools and your teammates — and your future self at 2am debugging production.

---

### Scope — Where Variables Live

**Local scope** — a variable created inside a function only exists inside that function:

```python
def greet(name):
    message = f"Hello, {name}!"   # local variable
    print(message)

greet("Udit")
print(message)   # ❌ NameError — 'message' doesn't exist outside the function
```

**Global scope** — a variable created at the top level of a file exists everywhere in that file:

```python
APP_NAME = "TaskFlow AI"   # global

def show_app():
    print(APP_NAME)        # ✅ can read globals

show_app()
```

**The `global` keyword** — needed only when you want to *modify* a global variable inside a function:

```python
task_id = 1

def make_task(title):
    global task_id         # tell Python: use the global, not a new local
    task = {"id": task_id, "title": title}
    task_id += 1
    return task
```

**Avoid `global` wherever possible.** It creates invisible dependencies between functions and makes code hard to test and reason about. The Day 12 solution — wrapping state in a class — eliminates all `global` usage cleanly.

---

### Pure Functions vs Side Effects

A **pure function** takes inputs, computes a result, and returns it — no external state touched:

```python
def calculate_completion_rate(tasks):
    """Pure — same inputs always produce same output. Easy to test."""
    if not tasks:
        return 0.0
    return round(sum(1 for t in tasks if t["done"]) / len(tasks) * 100, 1)
```

A function with **side effects** modifies something outside itself — prints to terminal, appends to a list, writes to a file:

```python
def add_task(tasks, title, priority):
    """Side effect — modifies the tasks list."""
    tasks.append({"title": title, "priority": priority, "done": False})
```

Both are valid. The key is knowing which you are writing, and not mixing them accidentally. Pure functions are easier to test (Day 25), easier to reason about, and easier to reuse.

---

### Single Responsibility Principle

Each function should do **one thing** and do it well. If you find yourself writing a function called `add_task_and_display_and_check_limit`, stop. Split it into three functions.

```python
# ❌ One function doing too much
def add_task_and_display(tasks, title, priority, limit):
    if len(tasks) >= limit:
        print("Limit reached")
        return
    tasks.append({"title": title, "priority": priority})
    print(f"Added: {title}")
    for i, t in enumerate(tasks, 1):
        print(f"{i}. {t['title']}")

# ✅ Three focused functions
def is_at_limit(tasks, limit):
    return len(tasks) >= limit

def add_task(tasks, title, priority):
    tasks.append({"title": title, "priority": priority, "done": False})

def display_tasks(tasks):
    for i, t in enumerate(tasks, 1):
        print(f"{i}. {t['title']}")
```

Now each piece is testable, reusable, and readable on its own.

---

### Type Hints on Functions (Preview)

Python 3.14 supports type hints — annotations that tell readers (and tools) what types a function expects and returns. We cover them fully on Day 27, but you will start seeing them from today:

```python
def calculate_completion_rate(tasks: list) -> float:
    """Calculate the percentage of completed tasks."""
    if not tasks:
        return 0.0
    return round(sum(1 for t in tasks if t["done"]) / len(tasks) * 100, 1)

def create_task(title: str, priority: str = "medium") -> dict:
    """Create and return a new task dictionary."""
    ...
```

`parameter: type` annotates inputs. `-> type` annotates the return value. They are optional and do not affect runtime behaviour — but they make your intentions unmistakably clear.

---

### Building the Refactored `tasks.py`

Create `tasks.py` — now fully function-driven. Notice how the main command loop shrinks to almost nothing because all logic is properly encapsulated:

```python
# tasks.py
# TaskFlow AI — Day 06
# Fully refactored: every action is a clean, documented, single-purpose function.

import datetime

# ─ Constants ─
APP_NAME         = "TaskFlow AI"
VERSION          = "0.3"
USER_NAME        = "Udit"
USER_PLAN        = "free"
MAX_TASKS        = 10
VALID_PRIORITIES = {"high", "medium", "low"}
VALID_CATEGORIES = {"work", "personal", "health", "learning", "other"}


# ─ Pure Helper Functions 

def make_task(task_id: int, title: str, priority: str, category: str) -> dict:
    """
    Create and return a new task dictionary.

    Args:
        task_id  (int): Unique identifier for the task.
        title    (str): Task title.
        priority (str): One of 'high', 'medium', 'low'.
        category (str): One of the valid categories.

    Returns:
        dict: A fully populated task dictionary.
    """
    return {
        "id":         task_id,
        "title":      title,
        "priority":   priority,
        "category":   category,
        "status":     "pending",
        "done":       False,
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    }


def calculate_stats(tasks: list) -> dict:
    """
    Calculate summary statistics for a list of tasks.

    Args:
        tasks (list): List of task dictionaries.

    Returns:
        dict: Stats including total, done, pending, and completion_rate.
    """
    total   = len(tasks)
    done    = sum(1 for t in tasks if t["done"])
    pending = total - done
    rate    = round(done / total * 100, 1) if total > 0 else 0.0
    return {"total": total, "done": done, "pending": pending, "rate": rate}


def get_tasks_by_priority(tasks: list, priority: str) -> list:
    """Return a filtered list of tasks matching the given priority."""
    return [t for t in tasks if t["priority"] == priority]


def get_pending_tasks(tasks: list) -> list:
    """Return only tasks that are not yet done."""
    return [t for t in tasks if not t["done"]]


def is_at_limit(tasks: list, limit: int) -> bool:
    """Return True if the task list has reached its limit."""
    return len(tasks) >= limit


def format_status(task: dict) -> str:
    """Return a formatted status string for display."""
    return "✓ done" if task["done"] else "pending"


# ─ Display Functions (side effects) 

def display_header() -> None:
    """Print the application header."""
    print("=" * 42)
    print(f"   {APP_NAME} — Task Manager v{VERSION}")
    print("=" * 42)
    print(f"   Hello, {USER_NAME}! Plan: {USER_PLAN.title()} ({MAX_TASKS} tasks max)")
    print()


def display_tasks(tasks: list) -> None:
    """
    Display all tasks in a formatted table.

    Args:
        tasks (list): List of task dictionaries to display.
    """
    if not tasks:
        print("\n  No tasks yet. Type 'add' to create your first task.\n")
        return

    col = {"num": 4, "title": 26, "priority": 10, "category": 12, "status": 10}
    width = sum(col.values()) + 4

    print()
    print("  " + "-" * width)
    print(
        f"  {'#':<{col['num']}}"
        f"{'Title':<{col['title']}}"
        f"{'Priority':<{col['priority']}}"
        f"{'Category':<{col['category']}}"
        f"Status"
    )
    print("  " + "-" * width)

    for i, task in enumerate(tasks, start=1):
        title = (task["title"][:col["title"] - 2] + "..") \
                if len(task["title"]) >= col["title"] else task["title"]
        print(
            f"  {i:<{col['num']}}"
            f"{title:<{col['title']}}"
            f"{task['priority'].upper():<{col['priority']}}"
            f"{task['category']:<{col['category']}}"
            f"{format_status(task)}"
        )

    print("  " + "-" * width)
    stats = calculate_stats(tasks)
    print(f"  {stats['total']} tasks · {stats['pending']} pending · "
          f"{stats['done']} done · {stats['rate']}% complete\n")


def display_stats(tasks: list) -> None:
    """Display a detailed statistics dashboard."""
    stats = calculate_stats(tasks)

    print("\n   Task Statistics ")
    print(f"  Total      : {stats['total']}")
    print(f"  Done       : {stats['done']}  ({stats['rate']}%)")
    print(f"  Pending    : {stats['pending']}")

    if tasks:
        print("\n  By Priority:")
        for p in ["high", "medium", "low"]:
            count = len(get_tasks_by_priority(tasks, p))
            bar   = "█" * count
            print(f"    {p.upper():<8}: {count:>2}  {bar}")

        print("\n  By Category:")
        categories = {t["category"] for t in tasks}
        for cat in sorted(categories):
            count = sum(1 for t in tasks if t["category"] == cat)
            print(f"    {cat:<12}: {count}")
    print()


# ─ Input Collection Functions ─

def prompt_valid(prompt: str, valid_options: set, label: str = "option") -> str:
    """
    Prompt the user until they enter a value from valid_options.

    Args:
        prompt        (str): The input prompt to display.
        valid_options (set): Set of accepted values.
        label         (str): Human-readable name used in error messages.

    Returns:
        str: The validated, lowercased user input.
    """
    while True:
        value = input(prompt).strip().lower()
        if value in valid_options:
            return value
        print(f"  ✗ Invalid {label}. Choose from: {', '.join(sorted(valid_options))}")


def prompt_task_number(tasks: list, action: str = "select") -> int | None:
    """
    Prompt the user for a task number and return a 0-based index.

    Args:
        tasks  (list): Current task list (used for range validation).
        action (str) : Verb to use in the prompt (e.g., 'remove', 'mark done').

    Returns:
        int | None: 0-based index if valid, None if invalid.
    """
    raw = input(f"  Task number to {action}: ").strip()
    if not raw.isdigit():
        print("  ✗ Please enter a number.\n")
        return None
    index = int(raw) - 1
    if not (0 <= index < len(tasks)):
        print(f"  ✗ Choose a number between 1 and {len(tasks)}.\n")
        return None
    return index


# ─ Command Functions 

def cmd_add(tasks: list, next_id: list) -> None:
    """
    Prompt for task details and add a new task to the list.

    Args:
        tasks   (list): The current task list (mutated in place).
        next_id (list): Single-element list holding the next task ID.
                        Using a list avoids the 'global' keyword.
    """
    if is_at_limit(tasks, MAX_TASKS):
        print(f"\n  ✗ Task limit reached ({MAX_TASKS} tasks on {USER_PLAN} plan). "
              f"Upgrade to premium.\n")
        return

    title = input("  Title    : ").strip()
    if not title:
        print("  ✗ Title cannot be empty.\n")
        return

    priority = prompt_valid("  Priority : ", VALID_PRIORITIES, "priority")
    category = prompt_valid("  Category : ", VALID_CATEGORIES, "category")

    task = make_task(next_id[0], title, priority, category)
    tasks.append(task)
    next_id[0] += 1

    count = len(tasks)
    print(f"\n  ✓ Task added! ({count} task{'s' if count != 1 else ''} total)\n")

    remaining = MAX_TASKS - count
    if remaining <= 2:
        print(f"  ⚠  Only {remaining} task slot{'s' if remaining != 1 else ''} remaining "
              f"on your {USER_PLAN} plan.\n")


def cmd_done(tasks: list) -> None:
    """Mark a selected task as done."""
    pending = get_pending_tasks(tasks)
    if not pending:
        print("\n  ✓ All tasks are already done! Great work.\n")
        return

    display_tasks(tasks)
    index = prompt_task_number(tasks, action="mark done")
    if index is None:
        return

    if tasks[index]["done"]:
        print("  ✗ Task is already marked as done.\n")
    else:
        tasks[index]["done"]   = True
        tasks[index]["status"] = "done"
        print(f"\n  ✓ \"{tasks[index]['title']}\" marked as done!\n")


def cmd_remove(tasks: list) -> None:
    """Remove a selected task from the list."""
    if not tasks:
        print("\n  ✗ No tasks to remove.\n")
        return

    display_tasks(tasks)
    index = prompt_task_number(tasks, action="remove")
    if index is None:
        return

    removed   = tasks.pop(index)
    remaining = len(tasks)
    print(f"\n  ✓ \"{removed['title']}\" removed. "
          f"({remaining} task{'s' if remaining != 1 else ''} remaining)\n")


def cmd_filter(tasks: list) -> None:
    """Display tasks filtered by priority."""
    priority = prompt_valid(
        "  Show priority (high/medium/low): ",
        VALID_PRIORITIES,
        "priority"
    )
    filtered = get_tasks_by_priority(tasks, priority)
    if not filtered:
        print(f"\n  No {priority}-priority tasks found.\n")
    else:
        print(f"\n  {priority.upper()} priority tasks ({len(filtered)}):")
        display_tasks(filtered)


def cmd_search(tasks: list) -> None:
    """Search tasks by keyword in title."""
    keyword = input("  Search keyword: ").strip().lower()
    if not keyword:
        print("  ✗ Please enter a search term.\n")
        return
    matches = [t for t in tasks if keyword in t["title"].lower()]
    if not matches:
        print(f"\n  No tasks matching '{keyword}'.\n")
    else:
        print(f"\n  Results for '{keyword}' ({len(matches)} found):")
        display_tasks(matches)


def cmd_quit(tasks: list) -> None:
    """Display a goodbye message and exit."""
    stats = calculate_stats(tasks)
    print(f"\n  Goodbye, {USER_NAME}!")
    if stats["total"] == 0:
        print("  No tasks — clean slate. See you tomorrow.")
    else:
        print(f"  {stats['done']}/{stats['total']} tasks completed "
              f"({stats['rate']}%). Keep going!")
    print()


# ─ Command Registry ─
# Maps command strings to functions — no giant if/elif chain needed.
# We will expand this pattern into a full CLI framework on Day 11.

COMMANDS = {
    "add":    "Add a new task",
    "view":   "View all tasks",
    "done":   "Mark a task as done",
    "remove": "Remove a task",
    "filter": "Filter by priority",
    "search": "Search tasks by keyword",
    "stats":  "View statistics dashboard",
    "quit":   "Exit TaskFlow AI",
}


def display_help() -> None:
    """Display available commands."""
    print("\n  Available commands:")
    for cmd, description in COMMANDS.items():
        print(f"    {cmd:<10} — {description}")
    print()


# ─ Main ─

def main() -> None:
    """Entry point — initialise state and run the command loop."""
    tasks   = []
    next_id = [1]    # list wrapper to avoid 'global' keyword

    display_header()
    display_help()

    while True:
        command = input("> ").strip().lower()

        if   command == "add":    cmd_add(tasks, next_id)
        elif command == "view":   display_tasks(tasks)
        elif command == "done":   cmd_done(tasks)
        elif command == "remove": cmd_remove(tasks)
        elif command == "filter": cmd_filter(tasks)
        elif command == "search": cmd_search(tasks)
        elif command == "stats":  display_stats(tasks)
        elif command == "help":   display_help()
        elif command == "quit":
            cmd_quit(tasks)
            break
        elif command == "":
            continue
        else:
            print(f"\n  ✗ Unknown command '{command}'. Type 'help' for options.\n")


if __name__ == "__main__":
    main()
```

Run it:

```bash
python tasks.py
```

---

### Understanding Key Lines

**`if __name__ == "__main__": main()`**

This is one of the most important Python idioms. When Python runs a file directly, `__name__` equals `"__main__"`. When another file imports this file, `__name__` equals the module name — and `main()` does NOT run automatically. This means `tasks.py` can be safely imported by other files without launching the command loop. We use this pattern for every Python file from now on.

**`next_id = [1]` — avoiding `global`**

Instead of `global task_id`, we pass a single-element list. Lists are mutable — changes inside a function persist in the caller. `next_id[0] += 1` modifies the list's first element, which is visible everywhere. It is a clean workaround until Day 12 when we use a class with instance variables.

**`COMMANDS` dictionary as a registry**

The help display loops over `COMMANDS.items()` — no manual listing. When you add a new command later, add one line to the dict and help updates automatically. This is the seed of a pattern we grow into a full CLI framework on Day 11.

**`prompt_valid()` — DRY input validation**

On Day 05, the same "keep asking until valid" loop appeared twice (priority and category). Today it is extracted into `prompt_valid()`. One function, used everywhere input validation is needed. This is DRY (Don't Repeat Yourself) applied in practice.

---

## Exercises

**Exercise 1 — Add a `rename` command.**
Write a `cmd_rename(tasks)` function that asks for a task number and a new title, validates both, and updates `tasks[index]["title"]`. Add it to the command loop and the `COMMANDS` dict.

**Exercise 2 — Explore `__doc__`.**
After defining several functions, add these lines and run:

```python
print(make_task.__doc__)
print(calculate_stats.__doc__)
print(prompt_valid.__doc__)
```

Then try `help(calculate_stats)` in the Python REPL (`python` with no file). Notice how VS Code also shows docstrings as tooltips when you hover over a function call.

**Exercise 3 — Pure function practice.**
Write a `get_overdue_tasks(tasks, days_old)` function. A task is "overdue" if it was created more than `days_old` days ago and is still pending. It should be a pure function — no printing, just return the filtered list. Test it by manually setting a `created_at` timestamp to a past date on one task.

**Exercise 4 — Multiple return values.**
Rewrite `calculate_stats` to return multiple values directly instead of a dict:

```python
def calculate_stats(tasks):
    ...
    return total, done, pending, rate

total, done, pending, rate = calculate_stats(tasks)
```

Does the rest of the code still work? Why or why not? Which style do you prefer?

**Exercise 5 — Default parameter behaviour.**
Write a `format_task_line(task, show_id=False, show_date=False, uppercase_priority=True)` function. Call it four ways — different combinations of default and overridden arguments. Print the results and verify each combination works correctly.

**Exercise 6 (stretch) — Command aliases.**
Extend the command loop to support aliases: `"a"` for `"add"`, `"v"` for `"view"`, `"d"` for `"done"`, `"r"` for `"remove"`, `"q"` for `"quit"`. Use a dictionary to map aliases to canonical commands, then resolve before the main `if/elif` chain.

```python
ALIASES = {"a": "add", "v": "view", "d": "done", "r": "remove", "q": "quit"}
command = ALIASES.get(command, command)   # resolve alias or keep as-is
```

---

## Checkpoint

Before moving to Day 07:

- [ ] I can define functions with `def` and call them
- [ ] I understand parameters, default values, and keyword arguments
- [ ] I use `return` to send values back from functions
- [ ] I can return multiple values and unpack them
- [ ] Every function I write has a docstring
- [ ] I understand local vs global scope
- [ ] I avoid `global` by passing state as arguments or using list wrappers
- [ ] I understand the difference between pure functions and side-effect functions
- [ ] I apply the Single Responsibility Principle — one function, one job
- [ ] I understand `if __name__ == "__main__":` and use it in every file
- [ ] `tasks.py` v0.3 is fully function-driven and runs correctly

---

## Common Errors on Day 06

**Calling a function before defining it:**

```python
greet("Udit")       # ❌ NameError — greet not defined yet

def greet(name):
    print(f"Hello, {name}!")
```

Python executes files top-to-bottom. A function must be defined before it is called — unless both definition and call are inside another function (like `main()`), which runs after everything is defined.

**Mutable default arguments — a classic Python trap:**

```python
def add_task(title, task_list=[]):   # ❌ DANGEROUS
    task_list.append(title)
    return task_list

# The default list is created ONCE and reused across all calls
print(add_task("Task 1"))   # ["Task 1"]
print(add_task("Task 2"))   # ["Task 1", "Task 2"]  ← unexpected!
```

Fix: use `None` as the default and create the list inside:

```python
def add_task(title, task_list=None):   # ✅ safe
    if task_list is None:
        task_list = []
    task_list.append(title)
    return task_list
```

**Forgetting `return` — function returns `None` silently:**

```python
def get_done_count(tasks):
    count = sum(1 for t in tasks if t["done"])
    # forgot return!

result = get_done_count(tasks)
print(result + 1)   # ❌ TypeError: unsupported operand type(s) for +: 'NoneType' and 'int'
```

**`return` inside a loop exits the whole function, not just the loop:**

```python
def find_task(tasks, title):
    for task in tasks:
        if task["title"] == title:
            return task    # exits the function immediately with this task
    return None            # reached only if no match was found
```

This is correct behaviour — use it intentionally when searching.

---

## What's Coming

On **Day 07** we pause new features and do something equally important — review, debug, and improve everything built in Week 1. You will learn systematic debugging with `print()`, how to read tracebacks, and how to ask Python what is happening inside your code. The Day 07 session will also clean up `tasks.py` with comments, better error messages, and a code review checklist you will use for the rest of the series.
