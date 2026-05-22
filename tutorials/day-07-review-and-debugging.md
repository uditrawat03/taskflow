# Day 07 — Week 1 Review & Debugging

> **Series:** Python & AI Engineering — Zero to Production
> **Phase:** 1 — Foundations
> **Python Version:** 3.14
> **Project:** TaskFlow AI — Code review, debugging, and Week 1 consolidation

---

## Learning Objective

By the end of today, you will know how to read Python tracebacks, debug code systematically using `print()` and the VS Code debugger, perform a code review against a professional checklist, and produce a clean, documented, fully working `tasks.py` that serves as the stable foundation for Week 2. Debugging is not a remedial skill — it is the skill that separates programmers who ship from those who struggle.

---

## What We Build Today

Not new features — something more valuable. A **debugged, reviewed, and hardened** version of `tasks.py` that passes a professional code review checklist. You will also build a small `debug_practice.py` full of intentional bugs to practise finding and fixing them.

```
Code Review Checklist — tasks.py v0.3
======================================
[✓] Functions are single-purpose
[✓] Every function has a docstring
[✓] No magic numbers — constants used
[✓] Input always validated before use
[✓] No silent failures — errors reported
[✓] if __name__ == "__main__" present
[✓] No unused variables
[✓] Consistent naming (snake_case)
[✓] No deeply nested code (max 2 levels)
[✓] Edge cases handled (empty list, etc.)
======================================
Score: 10/10 — Ready for Week 2
```

---

## Concepts Covered

- Reading Python tracebacks — anatomy of an error message
- The five most common exception types
- Debugging with `print()` — strategic placement
- Using VS Code's built-in debugger — breakpoints, step over, watch
- `assert` statements — lightweight correctness checks
- Code review — what to look for
- Naming conventions revisited
- Removing dead code and unused variables
- Edge case thinking — "what if the user does the unexpected?"
- The debugging mindset — hypothesis, test, confirm

---

## Full Tutorial

### The Debugging Mindset

Every programmer spends more time debugging than writing new code. This is not a sign of failure — it is the nature of programming. The difference between a junior and a senior developer is not that the senior writes bug-free code. It is that the senior finds and fixes bugs faster.

Debugging is a scientific method:

1. **Observe** — what is the actual behaviour?
2. **Hypothesise** — what do you think is causing it?
3. **Test** — add a print or a breakpoint to verify
4. **Fix** — change one thing at a time
5. **Confirm** — run again and verify the fix works
6. **Understand** — make sure you know *why* it was broken

Never guess randomly and change multiple things at once. That is how you introduce new bugs while fixing old ones.

---

### Reading Python Tracebacks

When Python encounters an error it cannot handle, it prints a **traceback** — a full report of what went wrong and where. Most beginners see a traceback and panic. Experienced developers read it like a map.

```
Traceback (most recent call last):
  File "tasks.py", line 142, in main        ← outermost call
    cmd_add(tasks, next_id)
  File "tasks.py", line 87, in cmd_add      ← next call in the chain
    task = make_task(next_id[0], title, priority, category)
  File "tasks.py", line 34, in make_task    ← where it actually broke
    "created_at": datetime.datetime.now().strftime(format_string),
NameError: name 'format_string' is not defined   ← the actual error
```

**How to read a traceback:**

1. **Start at the bottom** — the last line is the actual error type and message.
2. **Read the error message** — it usually tells you exactly what went wrong.
3. **Look at the line just above it** — that is where the error occurred.
4. **Read upward** — the chain of calls that led there.
5. **Find the line in your code** — VS Code will take you there instantly.

The bottom line is always the most important. Read it first.

---

### The Five Most Common Exceptions

You will see these every day. Know them by sight:

**`NameError` — using a variable that does not exist:**

```python
print(message)   # ❌ NameError: name 'message' is not defined
message = "hello"
```

Cause: typo in a variable name, or using it before assignment.

**`TypeError` — wrong type for an operation:**

```python
age = "24"
print(age + 1)   # ❌ TypeError: can only concatenate str (not "int") to str
```

Cause: forgot to convert input, mixed types in an operation.

**`IndexError` — accessing a list position that does not exist:**

```python
tasks = ["Task A", "Task B"]
print(tasks[5])   # ❌ IndexError: list index out of range
```

Cause: off-by-one error, empty list not checked, user entered a number out of range.

**`KeyError` — accessing a dict key that does not exist:**

```python
task = {"title": "Review PR"}
print(task["priority"])   # ❌ KeyError: 'priority'
```

Cause: key missing from dict, typo in key name. Fix: use `.get()` for optional keys.

**`ValueError` — right type, wrong value:**

```python
age = int("twenty-four")   # ❌ ValueError: invalid literal for int() with base 10
```

Cause: converting a string that is not actually a number.

---

### Debugging with `print()` — Strategic Placement

`print()` debugging is fast, universal, and underrated. The key is *strategic* placement — not random printing everywhere:

```python
def cmd_add(tasks, next_id):
    print(f"DEBUG: cmd_add called. tasks={len(tasks)}, next_id={next_id[0]}")  # entry

    if is_at_limit(tasks, MAX_TASKS):
        print("DEBUG: at limit — returning early")  # branch taken
        return

    title = input("  Title    : ").strip()
    print(f"DEBUG: title received = '{title}'")  # value check

    priority = prompt_valid("  Priority : ", VALID_PRIORITIES, "priority")
    print(f"DEBUG: priority = '{priority}'")  # value check

    task = make_task(next_id[0], title, priority, "work")
    print(f"DEBUG: task created = {task}")  # result check

    tasks.append(task)
    print(f"DEBUG: tasks now has {len(tasks)} items")  # state after
```

**Debug print conventions:**

- Prefix with `DEBUG:` so they are easy to find and remove later
- Print at function entry (show inputs), at key branches (show which path was taken), and after state changes (show what changed)
- Remove all debug prints before committing code — or use the `logging` module (Day 23) which lets you toggle them with a flag

---

### Using the VS Code Debugger

The VS Code debugger is more powerful than print-debugging for complex issues. Here is how to use it:

**Set a breakpoint:**
Click the red dot in the gutter to the left of a line number. The program will pause there when it reaches that line.

**Start debugging:**
Press `F5` or go to Run → Start Debugging. Select "Python File."

**While paused, you can:**
- **Step Over (`F10`)** — run the current line and pause at the next
- **Step Into (`F11`)** — jump inside a function call
- **Step Out (`Shift+F11`)** — finish the current function and pause in the caller
- **Continue (`F5`)** — run until the next breakpoint or end

**The Variables panel** shows every variable in scope and its current value — far more powerful than print statements for complex nested data.

**The Watch panel** — add any expression (e.g. `len(tasks)`, `tasks[0]["priority"]`) and VS Code evaluates it live as you step through code.

**The Debug Console** — type any Python expression and evaluate it in the current scope. `tasks[0]` will print the first task. `calculate_stats(tasks)` will run the function with live data.

---

### `assert` — Lightweight Correctness Checks

An `assert` statement verifies that a condition is `True`. If it is `False`, Python raises an `AssertionError`. Use them to catch impossible states early:

```python
def make_task(task_id, title, priority, category):
    assert isinstance(task_id, int),  f"task_id must be int, got {type(task_id)}"
    assert title.strip(),             "title must not be empty"
    assert priority in VALID_PRIORITIES, f"invalid priority: {priority}"
    assert category in VALID_CATEGORIES, f"invalid category: {category}"

    return {
        "id":       task_id,
        "title":    title,
        "priority": priority,
        "category": category,
        "status":   "pending",
        "done":     False,
    }
```

`assert` is documentation that executes. It says: "at this point in the code, this must be true — if it isn't, something has gone seriously wrong." We will replace `assert` with proper exception handling on Day 10, but assertions are a useful stepping stone.

---

### `debug_practice.py` — Intentional Bugs to Fix

Create this file, run it, and fix every bug. Read the traceback before looking at the hints:

```python
# debug_practice.py
# TaskFlow AI — Day 07
# This file contains 8 intentional bugs.
# Find them, read the traceback, and fix each one.

import datetime

# Bug 1
def greet_user(name):
    message = f"Hello {Name}! Welcome to TaskFlow AI."
    print(message)

greet_user("Udit")


# Bug 2
def calculate_completion(done_count, total_count):
    return done_count / total_count * 100

tasks_done  = 3
tasks_total = 0
rate = calculate_completion(tasks_done, tasks_total)
print(f"Completion rate: {rate}%")


# Bug 3
task_titles = ["Review PR", "Buy groceries", "Write tests"]
print(f"First task: {task_titles[0]}")
print(f"Last task: {task_titles[3]}")


# Bug 4
user_age = input("Enter your age: ")
years_to_retirement = 60 - user_age
print(f"Years until retirement: {years_to_retirement}")


# Bug 5
def get_high_priority(task_list):
    high = []
    for task in task_list:
        if task["priority"] = "high":
            high.append(task)
    return high

sample_tasks = [
    {"title": "Deploy app",   "priority": "high"},
    {"title": "Buy groceries","priority": "low"},
]
print(get_high_priority(sample_tasks))


# Bug 6
def show_task_count(tasks):
    count = len(tasks)
    if count = 0:
        print("No tasks")
    else:
        print(f"{count} tasks")

show_task_count(sample_tasks)


# Bug 7
config = {
    "theme": "dark",
    "notifications": True,
}
print(f"Language setting: {config['language']}")


# Bug 8
def format_date(dt):
    return dt.strftime("%d %B %Y")

today = datetime.date.today()
result = format_date("2025-05-19")   # passing string instead of date object
print(result)
```

**Hints (read only after attempting each fix):**

1. Variable name typo — Python is case-sensitive
2. Division by zero — check before dividing
3. List index out of range — lists are 0-based
4. `input()` returns str — convert before arithmetic
5. `=` vs `==` in a condition — assignment vs comparison
6. Same `=` vs `==` trap in an `if` block
7. Key does not exist — use `.get()` with a default
8. Wrong type passed to a function — `str` instead of `datetime.date`

---

### The Code Review Checklist

Use this checklist on every file you write from now on. Run through it on `tasks.py` today:

```
Code Review Checklist
=====================

Naming:
[ ] Variables and functions use snake_case
[ ] Classes use PascalCase (Day 12)
[ ] Constants use ALL_CAPS
[ ] Names are descriptive — no single letters except loop counters
[ ] No abbreviations that are not universally understood

Functions:
[ ] Every function has a docstring
[ ] Every function does ONE thing
[ ] Functions are short (aim for under 20 lines)
[ ] No function takes more than 4-5 parameters
[ ] Return values are consistent — always a dict, or always None, not sometimes one sometimes the other

Input Handling:
[ ] All user input is stripped and lowercased before use
[ ] All numeric input is validated with .isdigit() before int()
[ ] Empty input is handled gracefully — no crashes

Edge Cases:
[ ] Empty list handled before indexing
[ ] Division only happens when denominator is not zero
[ ] Index bounds checked before list access

Code Quality:
[ ] No magic numbers — use named constants
[ ] No dead code (unreachable lines, unused variables)
[ ] No deeply nested code (more than 2 indentation levels is a warning sign)
[ ] No repeated code blocks — extract into a function

Structure:
[ ] if __name__ == "__main__": present in every runnable file
[ ] Imports at the top
[ ] Constants below imports
[ ] Functions in logical order (helpers before callers)
[ ] Main logic at the bottom
```

Run this checklist on `tasks.py`. Fix everything that fails. This is your first formal code review.

---

### Cleaning Up `tasks.py`

After the review, make these specific improvements:

**1. Add a version history comment block at the top:**

```python
# tasks.py
# TaskFlow AI — Task Manager
#
# Version History:
#   v0.1 (Day 04) — Basic string-based task list, command loop
#   v0.2 (Day 05) — Tasks upgraded to dict objects, categories, priorities
#   v0.3 (Day 06) — Full function refactor, docstrings, command registry
#   v0.4 (Day 07) — Code review pass, edge cases hardened, debug practice
```

**2. Add edge case protection to `display_tasks`:**

```python
def display_tasks(tasks: list) -> None:
    """Display tasks. Handles empty list gracefully."""
    if not isinstance(tasks, list):
        print("  ✗ Internal error: tasks must be a list.")
        return
    if not tasks:
        print("\n  No tasks yet. Type 'add' to create your first task.\n")
        return
    # ... rest of display logic
```

**3. Add zero-division protection to `calculate_stats`:**

```python
def calculate_stats(tasks: list) -> dict:
    total   = len(tasks)
    done    = sum(1 for t in tasks if t.get("done", False))
    pending = total - done
    rate    = round(done / total * 100, 1) if total > 0 else 0.0
    return {"total": total, "done": done, "pending": pending, "rate": rate}
```

**4. Use `.get()` everywhere task fields are accessed:**

```python
# Defensive — works even if a task dict is missing a field
priority = task.get("priority", "medium")
category = task.get("category", "general")
is_done  = task.get("done", False)
```

---

## Exercises

**Exercise 1 — Fix `debug_practice.py`.**
Fix all 8 bugs. Run the file after each fix to verify the error is gone before moving to the next. Keep track of what each bug was and what the fix was — write it as a comment above each function.

**Exercise 2 — Run the code review checklist on `tasks.py`.**
Print the checklist, go line by line, and mark each item. If anything fails, fix it. Document what you changed and why in the version history comment.

**Exercise 3 — Create your own bug file.**
Write `buggy_tasks.py` — a stripped-down version of `tasks.py` with 5 intentional bugs. Give it to a friend, classmate, or post it in your community. This forces you to think like a code reviewer, not just a writer.

**Exercise 4 — Traceback reading practice.**
Intentionally cause each of the five exception types in the Python REPL. Run `python` with no file, and type:

```python
>>> print(undefined_variable)      # NameError
>>> "hello" + 5                    # TypeError
>>> [][0]                          # IndexError
>>> {}["missing"]                  # KeyError
>>> int("not a number")            # ValueError
```

Read each traceback carefully. Notice how Python 3.14's error messages give you extra context compared to older versions.

**Exercise 5 — VS Code debugger walkthrough.**
Set a breakpoint at the start of `cmd_add()`. Start debugging. Step through the function line by line. In the Watch panel, add `tasks`, `next_id[0]`, and `is_at_limit(tasks, MAX_TASKS)`. Step through an entire add-task flow and watch each variable change in real time.

**Exercise 6 (stretch) — Add `assert` guards.**
Add `assert` statements to `make_task()`, `cmd_done()`, and `calculate_stats()`. Each should assert at least two preconditions. Run the app and deliberately trigger an assertion failure by calling a function with bad arguments from the Python REPL.

---

## Checkpoint

Before moving to Day 08:

- [ ] I can read a Python traceback — starting from the bottom
- [ ] I recognise `NameError`, `TypeError`, `IndexError`, `KeyError`, `ValueError` on sight
- [ ] I use strategic `print()` debugging — entry points, branches, state changes
- [ ] I have used the VS Code debugger with breakpoints and step-over
- [ ] I understand `assert` and when to use it
- [ ] I have run the code review checklist on `tasks.py` and fixed all issues
- [ ] All 8 bugs in `debug_practice.py` are fixed
- [ ] `tasks.py` is at v0.4 — clean, reviewed, and hardened

---

## Common Errors on Day 07

**"My print debug statements are showing in production."**

Always remove `DEBUG:` prints before considering code "done." Better long-term: use the `logging` module (Day 23) with a `DEBUG` log level — you can suppress all debug output with one config change instead of hunting through files.

**"I set a breakpoint but the debugger never stops there."**

Make sure you are running in Debug mode (`F5`), not Run mode (`Ctrl+F5`). Also confirm the breakpoint is on an executable line — not a comment, blank line, or function definition line.

**"The error message says line 87 but there's nothing wrong there."**

The error location in a traceback is where Python *noticed* the problem, not necessarily where you *caused* it. A `KeyError` on line 87 might be caused by a typo on line 34 that stored the wrong key. Read the full traceback chain.

**`AssertionError` with no message:**

```python
assert len(tasks) > 0   # ❌ no message — hard to diagnose
assert len(tasks) > 0, f"tasks must not be empty, got {len(tasks)}"  # ✅ clear
```

Always include an f-string message in your asserts.

---

## What's Coming

On **Day 08** the project gets a critical upgrade: persistence. Right now, every time you quit and restart `tasks.py`, all your tasks vanish. Tomorrow you will learn file handling — reading and writing to disk — and TaskFlow AI will remember your tasks between sessions for the first time. This is the moment the app crosses from toy to tool.