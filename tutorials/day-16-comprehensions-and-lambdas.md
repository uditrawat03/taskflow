# Day 16 — List Comprehensions & Lambdas

> **Series:** Python & AI Engineering — Zero to Production
> **Phase:** 2 — Real Engineering
> **Python Version:** 3.14
> **Project:** TaskFlow AI — Writing more Pythonic, expressive code

---

## Learning Objective

By the end of today, you will write code that is shorter, faster, and more expressive using list comprehensions, dictionary comprehensions, set comprehensions, generator expressions, and lambda functions. You will refactor TaskFlow AI's filtering and transformation logic from verbose loops into clean, idiomatic Python — and understand precisely when to use each tool and when not to.

---

## What We Build Today

A `filters.py` module that replaces scattered filtering logic with a composable, comprehension-driven pipeline. The `stats.py` module gets refactored to use generators for memory efficiency.

```python
# Before — verbose loop
high_priority = []
for task in tasks:
    if task.priority == "high" and not task.done:
        high_priority.append(task)

# After — list comprehension
high_priority = [t for t in tasks if t.priority == "high" and not t.done]

# Pipeline — compose filters
from taskflow.filters import TaskFilter
results = (TaskFilter(tasks)
           .by_priority("high")
           .pending()
           .due_within(days=7)
           .sort_by("priority")
           .limit(5)
           .get())
```

---

## Concepts Covered

- List comprehensions — `[expr for item in iterable if condition]`
- Dictionary comprehensions — `{k: v for ...}`
- Set comprehensions — `{expr for ...}`
- Nested comprehensions
- Generator expressions — `(expr for item in iterable)`
- `lambda` — anonymous single-expression functions
- `sorted()` with `key=lambda`
- `filter()`, `map()` — built-in higher-order functions
- When to use comprehensions vs loops
- When to use `lambda` vs named functions
- Generator memory efficiency
- The `TaskFilter` fluent interface

---

## Full Tutorial

### List Comprehensions

A list comprehension creates a new list by applying an expression to each item in an iterable, optionally filtering items with a condition:

```python
# Syntax: [expression for item in iterable if condition]

numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# All numbers doubled
doubled = [n * 2 for n in numbers]
print(doubled)   # [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]

# Only even numbers
evens = [n for n in numbers if n % 2 == 0]
print(evens)     # [2, 4, 6, 8, 10]

# Even numbers doubled
even_doubled = [n * 2 for n in numbers if n % 2 == 0]
print(even_doubled)  # [4, 8, 12, 16, 20]
```

With tasks:

```python
from taskflow.core.task import Task

# All task titles
titles = [t.title for t in tasks]

# Titles of pending tasks
pending_titles = [t.title for t in tasks if t.is_pending()]

# Priority labels in uppercase
priorities = [t.priority.upper() for t in tasks]

# Tasks created this week
import datetime
today = datetime.date.today()
this_week = [t for t in tasks
             if t.age_days() <= 7]

# Task IDs mapped to titles
id_title_pairs = [(t.id, t.title) for t in tasks]
```

---

### When NOT to Use a Comprehension

Comprehensions are for **transformation** and **filtering**. Not for side effects:

```python
# ❌ Using comprehension for side effects — confusing and wrong
[print(t.title) for t in tasks]   # works but terrible style

# ✅ Use a regular for loop for side effects
for t in tasks:
    print(t.title)

# ❌ Comprehension too complex — use a loop
results = [
    complicated_function(t)
    for t in tasks
    if some_long_condition(t) and another_condition(t)
    if yet_another_condition(t)
]

# ✅ Loop is clearer for complex logic
results = []
for t in tasks:
    if some_long_condition(t) and another_condition(t):
        if yet_another_condition(t):
            results.append(complicated_function(t))
```

**Rule:** if a comprehension does not fit comfortably on one line, or if you need to do multiple things per iteration, use a regular loop.

---

### Dictionary Comprehensions

```python
# {key_expr: value_expr for item in iterable if condition}

tasks = [Task("Review PR", "high", "work"),
         Task("Buy groceries", "low", "personal"),
         Task("Write tests", "high", "work")]

# Map task ID → task title
id_to_title = {t.id: t.title for t in tasks}
print(id_to_title)   # {1: "Review PR", 2: "Buy groceries", 3: "Write tests"}

# Map task ID → task object (fast lookup by ID)
id_to_task = {t.id: t for t in tasks}
task = id_to_task.get(2)   # O(1) lookup

# Map priority → count
from collections import Counter
priority_counts = {p: sum(1 for t in tasks if t.priority == p)
                   for p in ["high", "medium", "low"]}
print(priority_counts)   # {"high": 2, "medium": 0, "low": 1}

# Invert a dictionary
original  = {"work": 1, "personal": 2, "health": 3}
inverted  = {v: k for k, v in original.items()}
print(inverted)   # {1: "work", 2: "personal", 3: "health"}
```

---

### Set Comprehensions

```python
# {expr for item in iterable if condition}

# All unique categories in use
used_categories = {t.category for t in tasks}
print(used_categories)   # {"work", "personal"}

# Titles of overdue tasks as a set
overdue_titles = {t.title for t in tasks if t.is_overdue()}

# Unique priorities — verify only valid ones are present
task_priorities = {t.priority for t in tasks}
assert task_priorities <= {"high", "medium", "low"}, \
    f"Unexpected priorities: {task_priorities - {'high', 'medium', 'low'}}"
```

---

### Nested Comprehensions

Use sparingly — they can become unreadable quickly:

```python
# Flatten a list of lists
task_groups = [["Review PR", "Write tests"], ["Buy groceries"], ["Workout"]]
all_titles  = [title for group in task_groups for title in group]
print(all_titles)   # ["Review PR", "Write tests", "Buy groceries", "Workout"]

# Read as: for each group in task_groups, for each title in group

# 2D grid — matrix transposition
matrix    = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
transposed = [[row[i] for row in matrix] for i in range(3)]
# [[1, 4, 7], [2, 5, 8], [3, 6, 9]]
```

For anything more than two levels deep, use explicit loops.

---

### Generator Expressions

A generator expression has the same syntax as a list comprehension but uses `()` instead of `[]`. The key difference: **generators are lazy** — they compute values one at a time on demand, without building the entire list in memory:

```python
# List comprehension — builds entire list in memory immediately
all_titles_list = [t.title for t in tasks]   # allocates memory for all titles

# Generator expression — computes lazily, one at a time
all_titles_gen = (t.title for t in tasks)    # no memory allocated yet
for title in all_titles_gen:
    print(title)   # computed one at a time

# Generators work perfectly with built-in functions that consume iterables
total_chars = sum(len(t.title) for t in tasks)   # no intermediate list!
any_overdue = any(t.is_overdue() for t in tasks)  # short-circuits on first True
all_valid   = all(t.priority in {"high","medium","low"} for t in tasks)
max_title   = max((len(t.title) for t in tasks), default=0)
done_count  = sum(1 for t in tasks if t.done)    # you have used this already!
```

**When to use generators vs list comprehensions:**
- Use a **list** when you need to iterate multiple times, index into it, or know the length
- Use a **generator** when you only iterate once, and especially with `sum()`, `any()`, `all()`, `max()`, `min()`

---

### `lambda` — Anonymous Functions

A `lambda` is a single-expression anonymous function. It takes arguments and returns the result of one expression:

```python
# Syntax: lambda args: expression

# Equivalent named function
def double(x):
    return x * 2

# Lambda equivalent
double = lambda x: x * 2
print(double(5))   # 10

# Multiple arguments
add = lambda x, y: x + y
print(add(3, 4))   # 7
```

**The primary use case: `key=` argument in `sorted()`:**

```python
tasks = [Task("Review PR", "high", "work"),
         Task("Buy groceries", "low", "personal"),
         Task("Write tests", "medium", "work")]

# Sort by title alphabetically
by_title = sorted(tasks, key=lambda t: t.title)

# Sort by priority score (high first)
by_priority = sorted(tasks, key=lambda t: t.priority_score, reverse=True)

# Sort by category, then by title within category
by_cat_title = sorted(tasks, key=lambda t: (t.category, t.title))

# Sort pending first, then by priority
by_status_priority = sorted(tasks,
    key=lambda t: (t.done, -t.priority_score))
```

---

### `filter()` and `map()` — Built-in Higher-Order Functions

Python has built-in `filter()` and `map()` functions. They return iterators (lazy, like generators):

```python
# filter(function, iterable) — keep items where function returns True
pending = list(filter(lambda t: t.is_pending(), tasks))
high    = list(filter(lambda t: t.priority == "high", tasks))

# map(function, iterable) — transform each item
titles  = list(map(lambda t: t.title, tasks))
scores  = list(map(lambda t: t.priority_score, tasks))
dicts   = list(map(lambda t: t.to_dict(), tasks))
```

In modern Python, comprehensions and generators are almost always preferred over `filter()` and `map()` — they are more readable. But you will encounter `filter()` and `map()` in other codebases, so know them.

```python
# Prefer comprehension over filter/map:
pending_titles = [t.title for t in tasks if t.is_pending()]
# over:
pending_titles = list(map(lambda t: t.title, filter(lambda t: t.is_pending(), tasks)))
```

---

### `sorted()` — The Right Way

```python
from operator import attrgetter

tasks = [...]

# By single attribute
sorted(tasks, key=attrgetter("priority"))   # cleaner than lambda for simple cases

# By priority score descending
sorted(tasks, key=lambda t: t.priority_score, reverse=True)

# Multi-key sort: pending first, then high priority, then alphabetical
sorted(tasks, key=lambda t: (t.done, -t.priority_score, t.title))

# Stable sort — equal elements preserve original order
# Python's sort is always stable — use this property deliberately
```

---

### Building `taskflow/filters.py`

A fluent filter pipeline using method chaining and comprehensions:

```python
# taskflow/filters.py
# TaskFlow AI — Day 16
# Composable task filtering pipeline using comprehensions.
# Uses fluent interface (method chaining) for readable filter composition.

import datetime
import re as re_module
from typing import Callable
from .core.task import Task

__all__ = ["TaskFilter"]


class TaskFilter:
    """
    A chainable task filter pipeline.

    Each method returns self, enabling fluent chaining:

        results = (TaskFilter(tasks)
                   .pending()
                   .by_priority("high")
                   .due_within(days=7)
                   .sort_by("priority")
                   .limit(5)
                   .get())
    """

    def __init__(self, tasks: list[Task]):
        """
        Initialise the filter with a task list.

        Args:
            tasks (list[Task]): The task list to filter. Not modified in place.
        """
        self._tasks: list[Task] = list(tasks)   # work on a copy

    #  Status filters 

    def pending(self) -> "TaskFilter":
        """Keep only pending (not done) tasks."""
        self._tasks = [t for t in self._tasks if t.is_pending()]
        return self

    def done(self) -> "TaskFilter":
        """Keep only completed tasks."""
        self._tasks = [t for t in self._tasks if t.done]
        return self

    def overdue(self, threshold_days: int = 7) -> "TaskFilter":
        """Keep only overdue tasks."""
        self._tasks = [t for t in self._tasks if t.is_overdue(threshold_days)]
        return self

    #  Attribute filters ─

    def by_priority(self, priority: str) -> "TaskFilter":
        """Keep tasks matching the given priority."""
        p = priority.strip().lower()
        self._tasks = [t for t in self._tasks if t.priority == p]
        return self

    def by_category(self, category: str) -> "TaskFilter":
        """Keep tasks matching the given category."""
        c = category.strip().lower()
        self._tasks = [t for t in self._tasks if t.category == c]
        return self

    def by_type(self, task_type: type) -> "TaskFilter":
        """Keep tasks that are instances of the given type."""
        self._tasks = [t for t in self._tasks if isinstance(t, task_type)]
        return self

    #  Text filters 

    def search(self, keyword: str) -> "TaskFilter":
        """Keep tasks whose title contains the keyword (case-insensitive)."""
        kw = keyword.strip().lower()
        self._tasks = [t for t in self._tasks if kw in t.title.lower()]
        return self

    def search_regex(self, pattern: str,
                     flags: int = re_module.IGNORECASE) -> "TaskFilter":
        """
        Keep tasks whose title matches the given regex pattern.

        Args:
            pattern (str): Regex pattern string.
            flags   (int): re flags, default IGNORECASE.

        Raises:
            ValueError: If the pattern is invalid regex.
        """
        try:
            compiled = re_module.compile(pattern, flags)
        except re_module.error as e:
            raise ValueError(f"Invalid regex pattern '{pattern}': {e}")
        self._tasks = [t for t in self._tasks
                       if compiled.search(t.title)]
        return self

    #  Date filters 

    def due_within(self, days: int) -> "TaskFilter":
        """Keep DeadlineTask instances due within the given number of days."""
        from .core.task_types import DeadlineTask
        self._tasks = [
            t for t in self._tasks
            if isinstance(t, DeadlineTask)
            and 0 <= t.days_until_due <= days
        ]
        return self

    def created_within(self, days: int) -> "TaskFilter":
        """Keep tasks created within the last N days."""
        self._tasks = [t for t in self._tasks if t.age_days() <= days]
        return self

    #  Custom filter ─

    def where(self, predicate: Callable[[Task], bool]) -> "TaskFilter":
        """
        Apply a custom filter function.

        Args:
            predicate: A callable that takes a Task and returns bool.

        Example:
            TaskFilter(tasks).where(lambda t: len(t.title) > 20)
        """
        self._tasks = [t for t in self._tasks if predicate(t)]
        return self

    #  Sorting ─

    def sort_by(self, key: str, reverse: bool = False) -> "TaskFilter":
        """
        Sort tasks by a named attribute.

        Args:
            key     (str) : Attribute name — 'priority', 'title', 'category',
                            'id', 'created_at', or 'priority_score'.
            reverse (bool): Sort descending if True.
        """
        sort_keys = {
            "priority":       lambda t: -t.priority_score,
            "priority_score": lambda t: t.priority_score,
            "title":          lambda t: t.title.lower(),
            "category":       lambda t: t.category,
            "id":             lambda t: t.id,
            "created_at":     lambda t: t.created_at,
        }
        if key not in sort_keys:
            raise ValueError(f"Unknown sort key '{key}'. "
                             f"Choose from: {', '.join(sort_keys)}")
        self._tasks = sorted(self._tasks,
                             key=sort_keys[key], reverse=reverse)
        return self

    #  Limiting 

    def limit(self, n: int) -> "TaskFilter":
        """Keep only the first N tasks."""
        self._tasks = self._tasks[:n]
        return self

    def offset(self, n: int) -> "TaskFilter":
        """Skip the first N tasks."""
        self._tasks = self._tasks[n:]
        return self

    #  Terminal operations ─

    def get(self) -> list[Task]:
        """Return the filtered task list."""
        return list(self._tasks)

    def first(self) -> Task | None:
        """Return the first task, or None if empty."""
        return self._tasks[0] if self._tasks else None

    def count(self) -> int:
        """Return the number of tasks after filtering."""
        return len(self._tasks)

    def titles(self) -> list[str]:
        """Return a list of task titles."""
        return [t.title for t in self._tasks]

    def ids(self) -> list[int]:
        """Return a list of task IDs."""
        return [t.id for t in self._tasks]

    def id_map(self) -> dict[int, Task]:
        """Return a dict mapping task ID → Task for O(1) lookup."""
        return {t.id: t for t in self._tasks}

    def priority_summary(self) -> dict[str, int]:
        """Return a count of tasks per priority level."""
        return {p: sum(1 for t in self._tasks if t.priority == p)
                for p in ["high", "medium", "low"]}

    def any_overdue(self) -> bool:
        """Return True if any task in the current set is overdue."""
        return any(t.is_overdue() for t in self._tasks)

    def all_done(self) -> bool:
        """Return True if every task in the current set is done."""
        return all(t.done for t in self._tasks)

    def __len__(self) -> int:
        return len(self._tasks)

    def __bool__(self) -> bool:
        return bool(self._tasks)

    def __repr__(self) -> str:
        return f"TaskFilter({len(self._tasks)} tasks)"
```

---

### Refactoring `stats.py` with Generators

```python
# taskflow/core/stats.py — refactored for Day 16
"""
Task statistics — refactored to use generator expressions for memory efficiency.
All functions remain pure (no side effects).
"""

from collections import Counter
from .task import Task

__all__ = [
    "calculate_stats",
    "priority_breakdown",
    "category_breakdown",
    "completion_rate",
    "average_title_length",
    "most_productive_category",
]


def calculate_stats(tasks: list[Task]) -> dict:
    """Return a summary statistics dictionary."""
    total   = len(tasks)
    done    = sum(1 for t in tasks if t.done)       # generator
    pending = total - done
    rate    = round(done / total * 100, 1) if total > 0 else 0.0
    return {"total": total, "done": done, "pending": pending, "rate": rate}


def priority_breakdown(tasks: list[Task]) -> dict[str, int]:
    """Count tasks per priority level using Counter."""
    counts = Counter(t.priority for t in tasks)     # generator in Counter
    return {p: counts.get(p, 0) for p in ["high", "medium", "low"]}


def category_breakdown(tasks: list[Task]) -> dict[str, int]:
    """Count tasks per category, sorted by count descending."""
    counts = Counter(t.category for t in tasks)
    return dict(counts.most_common())


def completion_rate(tasks: list[Task]) -> float:
    """Return completion percentage as a float 0.0–100.0."""
    if not tasks:
        return 0.0
    return round(sum(1 for t in tasks if t.done) / len(tasks) * 100, 1)


def average_title_length(tasks: list[Task]) -> float:
    """Return the average character length of task titles."""
    if not tasks:
        return 0.0
    return round(sum(len(t.title) for t in tasks) / len(tasks), 1)


def most_productive_category(tasks: list[Task]) -> str | None:
    """Return the category with the most completed tasks."""
    done_tasks = [t for t in tasks if t.done]
    if not done_tasks:
        return None
    counts = Counter(t.category for t in done_tasks)
    return counts.most_common(1)[0][0]
```

---

### Using `TaskFilter` in Commands

Update `cli.py` to use the new filter pipeline:

```python
from taskflow.filters import TaskFilter

# In the 'view' command handler:
results = TaskFilter(tasks)

if args.priority:
    results = results.by_priority(args.priority)
if args.category:
    results = results.by_category(args.category)
if args.done:
    results = results.done()
if args.pending:
    results = results.pending()
if args.overdue:
    results = results.overdue()
if hasattr(args, "limit") and args.limit:
    results = results.limit(args.limit)

display_tasks(results.get())
```

Clean, composable, readable. Adding a new filter flag requires one `if` block — no rewriting the filtering logic.

---

## Exercises

**Exercise 1 — Comprehension conversion.**
Find every `for` loop in `taskflow/` that appends to a list and convert it to a list comprehension. Count how many lines you save. Keep a note of any loops that should NOT be converted (side effects, complex logic) and explain why.

**Exercise 2 — Generator benchmarking.**
Create a list of 10,000 fake tasks. Benchmark three approaches for counting done tasks using `time.time()`:

```python
# Approach 1: list comprehension + len
count = len([t for t in tasks if t.done])

# Approach 2: generator + sum
count = sum(1 for t in tasks if t.done)

# Approach 3: explicit loop
count = 0
for t in tasks:
    if t.done:
        count += 1
```

Measure each 1000 times. Print average time. Which is fastest? Which uses least memory (hint: use `sys.getsizeof()` on the intermediate result)?

**Exercise 3 — `TaskFilter` in action.**
Using `TaskFilter`, write one-liner queries for each of the following. No explicit loops:

```python
# a) The 3 most recently created pending tasks
# b) All high-priority work tasks sorted alphabetically by title
# c) Any task whose title contains a number
# d) All categories that have at least one overdue task
# e) The total character count of all pending task titles
```

**Exercise 4 — Lambda sorting.**
Sort a list of 20 mixed tasks using each of these keys separately, and print the first 3 results each time:

```python
# By title length (shortest first)
# By category + priority (alphabetical category, then priority score)
# By done status (pending first) then by age (oldest first)
# By number of vowels in the title (most vowels last)
```

**Exercise 5 — Custom `where` predicate.**
Use `TaskFilter.where()` with a lambda to find:
- Tasks whose title starts with a capital letter AND is longer than 15 characters
- Tasks that are `DeadlineTask` instances AND due within 3 days
- Tasks where `priority_score * age_days()` exceeds 21 (a "compound urgency" score)

**Exercise 6 (stretch) — Lazy evaluation chain.**
Rewrite `TaskFilter` to use a list of stored predicate functions instead of eagerly filtering at each step. Apply all predicates in one final pass when `.get()` is called:

```python
class LazyTaskFilter:
    def __init__(self, tasks):
        self._tasks     = tasks
        self._predicates = []    # list of callables

    def pending(self):
        self._predicates.append(lambda t: t.is_pending())
        return self

    def by_priority(self, p):
        self._predicates.append(lambda t: t.priority == p)
        return self

    def get(self):
        return [t for t in self._tasks
                if all(pred(t) for pred in self._predicates)]
```

Benchmark `LazyTaskFilter` vs the eager `TaskFilter` on 10,000 tasks with 3 chained filters. Which is faster? Why?

---

## Checkpoint

Before moving to Day 17:

- [ ] I can write list, dict, and set comprehensions fluently
- [ ] I know when NOT to use a comprehension (side effects, complex logic)
- [ ] I use generator expressions with `sum()`, `any()`, `all()`, `max()`, `min()`
- [ ] I understand the memory difference between `[]` and `()`
- [ ] I use `lambda` with `sorted(key=...)` for flexible sorting
- [ ] I know `filter()` and `map()` but prefer comprehensions in new code
- [ ] `TaskFilter` is working with fluent chaining
- [ ] `stats.py` uses generators throughout — no intermediate lists
- [ ] I can chain multiple `TaskFilter` methods in one expression

---

## Common Errors on Day 16

**Comprehension with side effect — confusing and order-dependent:**

```python
results = [tasks.append(make_task(...)) for _ in range(5)]   # ❌ terrible
for _ in range(5):
    tasks.append(make_task(...))                              # ✅ clear
```

**Generator exhausted after one pass:**

```python
gen = (t.title for t in tasks)
list1 = list(gen)   # consumes the generator
list2 = list(gen)   # ❌ empty — generator already exhausted!

# Fix: use a list if you need multiple passes
titles = [t.title for t in tasks]   # list — reusable
```

**`lambda` with mutable default — closure trap:**

```python
filters = [lambda t: t.priority == p for p in ["high", "medium", "low"]]
# ❌ All lambdas capture 'p' by reference — all see the final value "low"

filters = [lambda t, p=p: t.priority == p for p in ["high", "medium", "low"]]
# ✅ Capture by value using default argument
```

**Nested comprehension read order — outer loop first:**

```python
# Read left to right, outer first:
result = [x for row in matrix for x in row]
# Equivalent to:
result = []
for row in matrix:
    for x in row:
        result.append(x)
```

---

## What's Coming

On **Day 17** we go deep on two of Python's most powerful features: decorators and context managers. You will write a `@timer` decorator that logs how long any function takes, a `@validate_tasks` decorator that checks task list integrity before operations, and a custom context manager for temporary task snapshots. These are the tools that make Python code feel like it has invisible superpowers.

---

## Vlog Content Angle

**"I deleted 40 lines of loops and replaced them with 8 lines of comprehensions. Here's every one."**

Open with a split-screen: the old verbose filtering code from Day 04 on the left, the new `TaskFilter` chain on the right. Same result, one fifth the lines. Let the audience compare for 10 seconds without commentary.

Then build the `TaskFilter` live, method by method. After each method is added, run a query against a real task list and show the results. The fluent chaining — `.pending().by_priority("high").sort_by("priority").limit(3).get()` — looks like a SQL query. That analogy resonates strongly with developers from other backgrounds.

The generator benchmarking exercise is great video content — run the three approaches side by side, time them, show the results. Real numbers. "Generator expressions: same result, no intermediate list, almost identical speed. This is why Pythonistas reach for generators."

End with a challenge: "Take any loop in your own projects and convert it to a comprehension. If you cannot, explain why in the comments. Learning to identify when a loop cannot be a comprehension is as important as knowing when it can."

---

*Day 16 of 90 · Phase 2: Real Engineering · Python 3.14 · Project: TaskFlow AI*