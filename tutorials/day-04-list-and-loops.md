# Day 04 — Lists & Loops

> **Series:** Python & AI Engineering — Zero to Production
> **Phase:** 1 — Foundations
> **Python Version:** 3.14
> **Project:** TaskFlow AI — Building the task list engine

---

## Learning Objective

By the end of today, you will work with Python's most essential data structure — the list — and master two types of loops: `for` and `while`. You will solve the unsolvable Exercise 6 from Day 03, and build the beating heart of TaskFlow AI: a live, interactive task manager that lets Udit add, view, and remove tasks from the terminal.

---

## What We Build Today

`tasks.py` — the task management engine of TaskFlow AI. A fully interactive terminal app that loops until the user decides to quit.

```
========================================
   TaskFlow AI — Task Manager v0.1
========================================

Commands: add | view | remove | quit

> add
Enter task: Buy groceries
✓ Task added! (1 task total)

> add
Enter task: Review pull request
✓ Task added! (2 tasks total)

> view

Your Tasks:
-----------
  1. Buy groceries
  2. Review pull request

> remove
Enter task number to remove: 1
✓ "Buy groceries" removed. (1 task remaining)

> view

Your Tasks:
-----------
  1. Review pull request

> quit
Goodbye, Udit. You have 1 task remaining. Don't forget!
```

---

## Concepts Covered

- Lists — creating, indexing, slicing
- List methods — `.append()`, `.remove()`, `.pop()`, `.insert()`, `.sort()`, `.reverse()`
- `len()` — getting the size of a list
- `for` loops — iterating over a list
- `range()` — generating number sequences
- `while` loops — looping until a condition changes
- `break` and `continue` — controlling loop flow
- `enumerate()` — looping with index and value
- Nested loops — loops inside loops
- Solving the Day 03 "keep asking" problem
- Building an interactive command loop

---

## Full Tutorial

### What Is a List?

A list is an ordered, changeable collection of items. You can put anything in a list — strings, numbers, booleans, even other lists. Lists are defined with square brackets `[]` and items are separated by commas.

```python
tasks = ["Buy groceries", "Review pull request", "Write tests"]
numbers = [1, 2, 3, 4, 5]
mixed = ["Udit", 24, True, None]    # valid, but unusual
empty = []                           # an empty list
```

Lists are **ordered** — items stay in the order you put them. They are **indexed** — each item has a position number starting from `0`.

---

### Indexing & Slicing

```python
tasks = ["Buy groceries", "Review PR", "Write tests", "Deploy app"]

# Indexing — access a single item
print(tasks[0])    # "Buy groceries"   — first item (index 0)
print(tasks[1])    # "Review PR"
print(tasks[-1])   # "Deploy app"      — last item (negative index)
print(tasks[-2])   # "Write tests"     — second to last

# Slicing — access a range of items [start:stop] (stop is exclusive)
print(tasks[0:2])  # ["Buy groceries", "Review PR"]
print(tasks[1:])   # ["Review PR", "Write tests", "Deploy app"]
print(tasks[:2])   # ["Buy groceries", "Review PR"]
print(tasks[:])    # full copy of the list
```

**Index starts at 0, not 1.** This trips up every beginner. A list with 4 items has indices `0`, `1`, `2`, `3`. Accessing index `4` raises an `IndexError`.

```python
print(tasks[4])   # ❌ IndexError: list index out of range
print(tasks[3])   # ✅ "Deploy app"
```

---

### List Methods

Lists come with built-in methods for adding, removing, and rearranging items:

```python
tasks = ["Buy groceries", "Review PR"]

# Adding items
tasks.append("Write tests")        # adds to the END
tasks.insert(0, "Urgent: Deploy")  # inserts at index 0

print(tasks)
# ["Urgent: Deploy", "Buy groceries", "Review PR", "Write tests"]

# Removing items
tasks.remove("Buy groceries")   # removes by VALUE (first match)
popped = tasks.pop()            # removes and returns the LAST item
popped_at = tasks.pop(0)        # removes and returns item at index 0

# Checking membership
print("Review PR" in tasks)    # True or False

# Useful info
print(len(tasks))              # number of items
print(tasks.count("Review PR")) # how many times an item appears
print(tasks.index("Review PR")) # index of first occurrence

# Reordering
tasks.sort()                   # sort alphabetically (in place)
tasks.reverse()                # reverse order (in place)
sorted_copy = sorted(tasks)    # returns new sorted list, original unchanged

# Clearing
tasks.clear()                  # removes all items → []
```

---

### `for` Loops — Iterating Over a List

A `for` loop runs a block of code once for each item in a collection:

```python
tasks = ["Buy groceries", "Review PR", "Write tests"]

for task in tasks:
    print(task)

# Output:
# Buy groceries
# Review PR
# Write tests
```

Read it aloud: "For each task in tasks, print the task." Python is almost English here.

---

### `range()` — Generating Number Sequences

`range()` generates a sequence of numbers — useful when you need to loop a specific number of times:

```python
for i in range(5):
    print(i)       # prints 0, 1, 2, 3, 4

for i in range(1, 6):
    print(i)       # prints 1, 2, 3, 4, 5

for i in range(0, 10, 2):
    print(i)       # prints 0, 2, 4, 6, 8 (step of 2)
```

`range(start, stop, step)` — `stop` is always exclusive.

---

### `enumerate()` — Index + Value Together

When you need both the position and the value while looping, use `enumerate()`. This is how you build numbered task lists:

```python
tasks = ["Buy groceries", "Review PR", "Write tests"]

for index, task in enumerate(tasks):
    print(f"{index + 1}. {task}")

# Output:
# 1. Buy groceries
# 2. Review PR
# 3. Write tests
```

`enumerate()` returns pairs of `(index, value)`. The `index + 1` shifts from 0-based to 1-based display — users expect numbering to start at 1, not 0.

---

### `while` Loops — Loop Until a Condition Changes

A `while` loop repeats as long as its condition is `True`. Unlike `for` (which loops over a fixed collection), `while` loops an unknown number of times — until something changes.

```python
count = 0

while count < 3:
    print(f"Count is {count}")
    count += 1

# Output:
# Count is 0
# Count is 1
# Count is 2
```

**Warning: infinite loops.** If the condition never becomes `False`, the loop runs forever and freezes your program. Always make sure something inside the loop changes the condition:

```python
# ❌ INFINITE LOOP — never do this accidentally
while True:
    print("This runs forever")

# ✅ Intentional infinite loop — broken out with 'break'
while True:
    command = input("> ")
    if command == "quit":
        break    # exits the loop immediately
    print(f"You typed: {command}")
```

The pattern `while True: ... if condition: break` is the standard way to build an interactive command loop — exactly what TaskFlow AI needs.

---

### Solving Day 03's Exercise 6 — Input Validation Loop

Remember the "keep asking until valid" problem? Here it is solved cleanly with a `while` loop:

```python
VALID_PLANS = ["free", "premium"]

while True:
    plan = input("Choose your plan (free/premium): ").strip().lower()
    if plan in VALID_PLANS:
        break   # valid input — exit the loop
    print(f"  ✗ Invalid plan '{plan}'. Please enter 'free' or 'premium'.")

print(f"Plan confirmed: {plan}")
```

No matter how many times the user types garbage, the loop keeps asking. The moment they enter a valid plan, `break` exits. This pattern — **validate, loop until valid** — is one of the most used patterns in real-world CLI tools.

---

### `break` and `continue`

**`break`** exits the loop entirely:

```python
tasks = ["Buy groceries", "Review PR", "URGENT: Server down", "Write tests"]

for task in tasks:
    if "URGENT" in task:
        print(f"Stopping — handle this first: {task}")
        break       # exits the for loop immediately
    print(f"Task: {task}")
```

**`continue`** skips the rest of the current iteration and jumps to the next:

```python
tasks = ["Buy groceries", "", "Review PR", "", "Write tests"]

for task in tasks:
    if not task:       # skip empty strings
        continue
    print(f"Task: {task}")

# Output:
# Task: Buy groceries
# Task: Review PR
# Task: Write tests
```

---

### Nested Loops

A loop inside a loop. The inner loop completes fully for every single iteration of the outer loop:

```python
users = ["Udit", "Priya", "Rohan"]
tasks = ["Design", "Build", "Test"]

for user in users:
    for task in tasks:
        print(f"{user} → {task}")

# Udit → Design
# Udit → Build
# Udit → Test
# Priya → Design
# ... and so on
```

We will use nested loops when building multi-user task boards in later phases. For now, know they exist and understand how they flow.

---

### Building `tasks.py`

Create `tasks.py` inside your `taskflow` folder:

```python
# tasks.py
# TaskFlow AI — Day 04
# Interactive task manager with a live command loop.

# --- Constants ---
APP_NAME = "TaskFlow AI"
VERSION = "0.1"
MAX_TASKS_FREE = 10
USER_NAME = "Udit"
USER_PLAN = "free"

# --- Setup ---
tasks = []    # our task list starts empty
max_tasks = MAX_TASKS_FREE

# --- Helper Functions (preview — we formalise these on Day 06) ---

def display_header():
    print("=" * 40)
    print(f"   {APP_NAME} — Task Manager v{VERSION}")
    print("=" * 40)
    print()

def display_tasks(task_list):
    if not task_list:
        print("  No tasks yet. Type 'add' to create one.")
        return
    print("\nYour Tasks:")
    print("-" * 20)
    for i, task in enumerate(task_list, start=1):
        print(f"  {i}. {task}")
    print()

def add_task(task_list, limit):
    if len(task_list) >= limit:
        print(f"  ✗ Task limit reached ({limit} tasks on {USER_PLAN} plan).")
        return
    task = input("Enter task: ").strip()
    if not task:
        print("  ✗ Task cannot be empty.")
        return
    task_list.append(task)
    print(f"  ✓ Task added! ({len(task_list)} task{'s' if len(task_list) != 1 else ''} total)")

def remove_task(task_list):
    if not task_list:
        print("  ✗ No tasks to remove.")
        return
    display_tasks(task_list)
    raw = input("Enter task number to remove: ").strip()
    if not raw.isdigit():
        print("  ✗ Please enter a valid number.")
        return
    index = int(raw) - 1    # convert 1-based user input to 0-based index
    if 0 <= index < len(task_list):
        removed = task_list.pop(index)
        remaining = len(task_list)
        print(f"  ✓ \"{removed}\" removed. ({remaining} task{'s' if remaining != 1 else ''} remaining)")
    else:
        print(f"  ✗ Invalid number. Choose between 1 and {len(task_list)}.")

# --- Main Command Loop ---
display_header()
print(f"Commands: add | view | remove | quit")
print()

while True:
    command = input("> ").strip().lower()

    if command == "add":
        add_task(tasks, max_tasks)

    elif command == "view":
        display_tasks(tasks)

    elif command == "remove":
        remove_task(tasks)

    elif command == "quit":
        count = len(tasks)
        if count == 0:
            print(f"Goodbye, {USER_NAME}. No tasks remaining — clean slate!")
        elif count == 1:
            print(f"Goodbye, {USER_NAME}. You have 1 task remaining. Don't forget!")
        else:
            print(f"Goodbye, {USER_NAME}. You have {count} tasks remaining. Stay productive!")
        break

    elif command == "":
        continue    # user just pressed Enter — ignore and re-prompt

    else:
        print(f"  ✗ Unknown command '{command}'. Try: add | view | remove | quit")
```

Run it:

```bash
python tasks.py
```

---

### Understanding Key Lines

**`for i, task in enumerate(task_list, start=1)`**

`enumerate()` accepts an optional `start` argument. `start=1` means the index begins at `1` instead of `0` — so we display `1.` not `0.` without needing `index + 1` in the loop body.

**`task{'s' if len(task_list) != 1 else ''}`**

This is pluralization logic inside an f-string. When there is exactly 1 task, it says `"1 task"`. For any other count it says `"2 tasks"`. Small detail — enormous difference in perceived quality.

**`index = int(raw) - 1`**

Users count from 1. Lists index from 0. Always subtract 1 when converting user-facing numbers to list indices. Always add 1 when displaying list indices to users.

**`0 <= index < len(task_list)`**

A Python range check in one expression. It reads exactly like math: "index is between 0 (inclusive) and the list length (exclusive)." This prevents `IndexError` if the user enters a number outside the valid range.

**`while True: ... break`**

The interactive loop runs forever until the user types `quit`. Every command is handled inside the loop. `break` is the clean exit. This is the standard architecture for any CLI tool.

---

## Exercises

**Exercise 1 — Add a `clear` command.**
Add a `"clear"` command that removes all tasks after asking for confirmation:

```
> clear
Are you sure you want to clear all tasks? (yes/no): yes
✓ All 3 tasks cleared.
```

If the user types `"no"`, do nothing.

**Exercise 2 — Count completed tasks.**
Add a `"done"` command. When called, it works like `remove` but moves the task to a `completed` list instead of deleting it. Add a `"completed"` command that displays all completed tasks with a checkmark:

```
Completed Tasks:
----------------
  ✓ Buy groceries
  ✓ Review pull request
```

**Exercise 3 — Slicing practice.**
After displaying tasks, show two bonus lines using slicing:
- "First task: ..." (index 0)
- "Last task: ..." (index -1)

Handle the case where the list is empty.

**Exercise 4 — Sort command.**
Add a `"sort"` command that sorts the task list alphabetically and confirms: `"✓ Tasks sorted A→Z."`. Run it, then view the list to verify the order changed.

**Exercise 5 — Task search.**
Add a `"search"` command. Ask for a keyword. Loop through all tasks and print any that contain the keyword (case-insensitive). Show `"No tasks match your search."` if nothing is found.

```python
keyword = input("Search for: ").strip().lower()
matches = []
for task in tasks:
    if keyword in task.lower():
        matches.append(task)
```

**Exercise 6 (stretch) — Limit warning.**
On the `free` plan, the limit is 10 tasks. When the user adds their 8th task, print a soft warning: `"⚠ You are 2 tasks away from your free plan limit."`. When they add their 10th, print: `"⚠ Task limit reached. Upgrade to premium for unlimited tasks."`.

---

## Checkpoint

Before moving to Day 05:

- [ ] I can create, index, and slice a list
- [ ] I can add, remove, and check items using list methods
- [ ] I can loop over a list with `for task in tasks:`
- [ ] I can use `range()` to loop a set number of times
- [ ] I use `enumerate()` when I need both index and value
- [ ] I can write a `while` loop that runs until a condition is met
- [ ] I understand `break` (exit loop) and `continue` (skip iteration)
- [ ] I solved the Day 03 "keep asking" problem with a `while True: ... break` pattern
- [ ] `tasks.py` runs interactively and handles all valid and invalid inputs cleanly

---

## Common Errors on Day 04

**`IndexError: list index out of range`**

```python
tasks = ["Buy groceries", "Review PR"]
print(tasks[2])    # ❌ only indices 0 and 1 exist

# Fix: always validate the index before using it
if 0 <= index < len(tasks):
    print(tasks[index])
```

**`ValueError: list.remove(x): x not in list`**

```python
tasks.remove("nonexistent task")   # ❌ ValueError if item doesn't exist

# Fix: check before removing
if "nonexistent task" in tasks:
    tasks.remove("nonexistent task")
```

**Modifying a list while looping over it:**

```python
tasks = ["a", "b", "c", "d"]

# ❌ Dangerous — skips items unexpectedly
for task in tasks:
    if "b" in task:
        tasks.remove(task)

# ✅ Loop over a copy instead
for task in tasks[:]:
    if "b" in task:
        tasks.remove(task)
```

Never modify a list while iterating over it directly. Loop over a copy (`tasks[:]`) or build a new list.

**Off-by-one error on user-facing numbers:**

```python
index = int(input("Task number: ")) - 1   # always subtract 1 for 0-based indexing
```

Forgetting this subtraction is the #1 bug when building task lists. If users see task `1` but the list index is `0`, always convert.

**`while True` without `break` — infinite loop:**

Press `Ctrl+C` to stop an infinite loop in the terminal. It raises a `KeyboardInterrupt`. If your terminal freezes, that is almost always an unintended infinite loop.

---

## What's Coming

On **Day 05** we introduce dictionaries and sets. Right now, each task is just a string — a title. But real tasks have more: a priority, a due date, a status, a category. Dictionaries let us store all of that together. We will upgrade the task list so each item is a rich dictionary object, moving TaskFlow AI significantly closer to what a real app looks like.
