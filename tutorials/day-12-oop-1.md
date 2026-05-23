# Day 12 — Object-Oriented Programming I

> **Series:** Python & AI Engineering — Zero to Production
> **Phase:** 1 — Foundations
> **Python Version:** 3.14
> **Project:** TaskFlow AI — Replacing task dicts with a proper Task class

---

## Learning Objective

By the end of today, you will understand the fundamentals of Object-Oriented Programming — classes, instances, `__init__`, instance attributes, methods, and `self`. You will replace TaskFlow AI's plain task dictionaries with a proper `Task` class that carries its own behaviour, eliminates the `[1]` list hack for ID generation, and makes the codebase dramatically more expressive and self-documenting.

---

## What We Build Today

A `Task` class in `taskflow/core/task.py` that replaces the raw task dictionaries used since Day 05. The class handles its own validation, ID generation, serialization, and display.

```python
# Before (Day 05-style dict):
task = {
    "id":         1,
    "title":      "Review pull request",
    "priority":   "high",
    "category":   "work",
    "status":     "pending",
    "done":       False,
    "created_at": "2025-05-19 14:32",
}
print(task["title"])          # "Review pull request"
task["done"] = True           # mutate directly — no validation

# After (Day 12-style class):
task = Task(title="Review pull request", priority="high", category="work")
print(task.title)             # "Review pull request"
task.mark_done()              # validated, updates status too
print(task.is_overdue())      # False
print(task.to_dict())         # serializes back to dict for JSON storage
print(task)                   # "Task #1 [HIGH] Review pull request (pending)"
```

---

## Concepts Covered

- Classes and instances — blueprints and objects
- `__init__` — the constructor
- Instance attributes — data that belongs to each object
- Class attributes — data shared across all instances
- `self` — the reference to the current instance
- Instance methods — functions that belong to objects
- `__str__` and `__repr__` — string representation
- `__eq__` — equality comparison
- Properties — `@property` and `@setter`
- Class methods — `@classmethod`
- Static methods — `@staticmethod`
- `dataclasses` — a modern alternative to manual `__init__`
- Converting between objects and dicts — `.to_dict()` / `.from_dict()`

---

## Full Tutorial

### Classes Are Blueprints

A class is a blueprint. An instance is a thing built from that blueprint.

```python
class Task:
    pass   # empty class — valid Python

# Creating instances
t1 = Task()
t2 = Task()

print(type(t1))    # <class '__main__.Task'>
print(t1 is t2)   # False — two separate objects
```

Every time you call `Task()`, Python creates a new, independent object in memory. The class defines the structure; instances are the actual data.

---

### `__init__` — The Constructor

`__init__` is called automatically when a new instance is created. It sets up the initial state of the object:

```python
class Task:
    def __init__(self, title, priority, category):
        self.title    = title
        self.priority = priority
        self.category = category

task = Task("Review PR", "high", "work")
print(task.title)      # "Review PR"
print(task.priority)   # "high"
```

`self` is the first parameter of every instance method. It refers to the specific instance being operated on. Python passes it automatically — you never supply it when calling the method.

---

### Instance Attributes vs Class Attributes

**Instance attributes** — unique to each object, set in `__init__`:

```python
task1 = Task("Review PR",      "high", "work")
task2 = Task("Buy groceries",  "low",  "personal")

print(task1.title)   # "Review PR"
print(task2.title)   # "Buy groceries"   — completely independent
```

**Class attributes** — shared across all instances, defined at class level:

```python
class Task:
    VALID_PRIORITIES = {"high", "medium", "low"}   # class attribute
    _id_counter      = 0                           # class attribute (private)

    def __init__(self, title, priority):
        Task._id_counter += 1          # modifies the CLASS attribute
        self.id       = Task._id_counter   # instance attribute
        self.title    = title
        self.priority = priority

t1 = Task("Task A", "high")
t2 = Task("Task B", "low")

print(t1.id)              # 1
print(t2.id)              # 2
print(Task._id_counter)   # 2 — shared counter
```

`Task._id_counter` is the clean replacement for the `next_id = [1]` list hack from Days 06-11. The class owns its own counter.

---

### Instance Methods

Methods are functions defined inside a class. They always receive `self` as the first argument:

```python
class Task:
    def __init__(self, title, priority="medium"):
        self.title    = title
        self.priority = priority
        self.done     = False
        self.status   = "pending"

    def mark_done(self):
        """Mark this task as completed."""
        self.done   = True
        self.status = "done"

    def is_pending(self):
        """Return True if the task is not yet done."""
        return not self.done

    def matches(self, keyword):
        """Return True if the keyword appears in the title."""
        return keyword.lower() in self.title.lower()

task = Task("Review PR", "high")
print(task.is_pending())     # True
task.mark_done()
print(task.is_pending())     # False
print(task.matches("review"))  # True
```

---

### `__str__` and `__repr__`

**`__str__`** — called by `print()` and `str()`. Human-readable:

```python
def __str__(self):
    status = "✓" if self.done else "○"
    return f"{status} Task #{self.id} [{self.priority.upper()}] {self.title}"
```

**`__repr__`** — called in the REPL and for debugging. Should be unambiguous enough to reconstruct the object:

```python
def __repr__(self):
    return (f"Task(id={self.id!r}, title={self.title!r}, "
            f"priority={self.priority!r}, done={self.done!r})")
```

```python
task = Task("Review PR", "high")
print(task)      # ○ Task #1 [HIGH] Review PR     (uses __str__)
repr(task)       # Task(id=1, title='Review PR', priority='high', done=False)  (__repr__)
```

**Rule:** always define both. `__repr__` for developers, `__str__` for users.

---

### `__eq__` — Equality

Without `__eq__`, two Task objects with identical data are not equal:

```python
t1 = Task("Review PR", "high")
t2 = Task("Review PR", "high")
print(t1 == t2)   # False — comparing memory addresses by default
```

Define `__eq__` to compare by value:

```python
def __eq__(self, other):
    if not isinstance(other, Task):
        return NotImplemented
    return self.id == other.id
```

---

### `@property` — Controlled Attribute Access

Properties let you access a method like an attribute — no parentheses — while keeping validation and logic hidden:

```python
class Task:
    VALID_PRIORITIES = {"high", "medium", "low"}

    def __init__(self, title, priority="medium"):
        self.title     = title
        self._priority = priority   # private — store with underscore

    @property
    def priority(self):
        """Get the task priority."""
        return self._priority

    @priority.setter
    def priority(self, value):
        """Set priority with validation."""
        value = value.strip().lower()
        if value not in self.VALID_PRIORITIES:
            raise ValueError(f"Invalid priority: {value!r}. "
                             f"Choose from {self.VALID_PRIORITIES}")
        self._priority = value

task = Task("Review PR")
print(task.priority)        # "medium"   — calls getter
task.priority = "high"      # calls setter — validated
task.priority = "urgent"    # ❌ raises ValueError — caught before stored
```

---

### `@classmethod` and `@staticmethod`

**`@classmethod`** — receives the class itself (`cls`) instead of an instance. Used for alternative constructors:

```python
@classmethod
def from_dict(cls, data: dict) -> "Task":
    """
    Create a Task instance from a dictionary (e.g., loaded from JSON).
    This is an alternative constructor.
    """
    task          = cls.__new__(cls)        # create without calling __init__
    task.id       = data["id"]
    task.title    = data["title"]
    task._priority = data["priority"]
    task._category = data["category"]
    task.status   = data["status"]
    task.done     = data["done"]
    task.created_at = data["created_at"]
    return task
```

**`@staticmethod`** — no `self` or `cls`. A regular function that logically belongs to the class:

```python
@staticmethod
def priority_to_score(priority: str) -> int:
    """Convert priority string to a numeric score for sorting."""
    return {"high": 3, "medium": 2, "low": 1}.get(priority, 0)
```

---

### Building the `Task` Class

Create `taskflow/core/task.py`:

```python
# taskflow/core/task.py
# TaskFlow AI — Day 12
# The Task class — replaces plain task dictionaries.

import datetime
from ..config import VALID_PRIORITIES, VALID_CATEGORIES, DATE_FMT
from ..errors import ValidationError


class Task:
    """
    Represents a single task in TaskFlow AI.

    Attributes:
        id         (int)  : Unique identifier, auto-assigned.
        title      (str)  : Task description.
        priority   (str)  : One of 'high', 'medium', 'low'.
        category   (str)  : One of the valid categories.
        status     (str)  : 'pending' or 'done'.
        done       (bool) : True if the task is completed.
        created_at (str)  : ISO-style timestamp string.

    Class Attributes:
        _id_counter (int) : Auto-incrementing ID counter (shared across all instances).
    """

    _id_counter: int = 0

    def __init__(self, title: str, priority: str = "medium",
                 category: str = "general", task_id: int | None = None):
        """
        Create a new Task instance.

        Args:
            title    (str)       : Task title. Must not be empty.
            priority (str)       : Task priority. Defaults to 'medium'.
            category (str)       : Task category. Defaults to 'general'.
            task_id  (int | None): Explicit ID (used when loading from storage).
                                   If None, auto-increments the class counter.
        """
        #  Validate 
        title    = title.strip()
        priority = priority.strip().lower()
        category = category.strip().lower()

        if not title:
            raise ValidationError("Title cannot be empty",
                                   field="title", value=title)
        if len(title) > 200:
            raise ValidationError("Title too long (max 200 chars)",
                                   field="title", value=len(title))
        if priority not in VALID_PRIORITIES:
            raise ValidationError(f"Invalid priority",
                                   field="priority", value=priority)
        if category not in VALID_CATEGORIES:
            raise ValidationError(f"Invalid category",
                                   field="category", value=category)

        #  Assign ID ─
        if task_id is not None:
            self.id = task_id
            # Keep counter ahead of any explicitly assigned ID
            Task._id_counter = max(Task._id_counter, task_id)
        else:
            Task._id_counter += 1
            self.id = Task._id_counter

        #  Set Attributes 
        self.title      = title
        self._priority  = priority
        self._category  = category
        self.status     = "pending"
        self.done       = False
        self.created_at = datetime.datetime.now().strftime(DATE_FMT)

    #  Properties 

    @property
    def priority(self) -> str:
        return self._priority

    @priority.setter
    def priority(self, value: str) -> None:
        value = value.strip().lower()
        if value not in VALID_PRIORITIES:
            raise ValidationError("Invalid priority",
                                   field="priority", value=value)
        self._priority = value

    @property
    def category(self) -> str:
        return self._category

    @category.setter
    def category(self, value: str) -> None:
        value = value.strip().lower()
        if value not in VALID_CATEGORIES:
            raise ValidationError("Invalid category",
                                   field="category", value=value)
        self._category = value

    @property
    def priority_score(self) -> int:
        """Numeric priority for sorting. High=3, Medium=2, Low=1."""
        return {"high": 3, "medium": 2, "low": 1}.get(self._priority, 0)

    #  Instance Methods 

    def mark_done(self) -> "Task":
        """
        Mark the task as completed.

        Returns:
            Task: self — allows method chaining.
        """
        self.done   = True
        self.status = "done"
        return self

    def mark_pending(self) -> "Task":
        """Re-open a completed task."""
        self.done   = False
        self.status = "pending"
        return self

    def is_pending(self) -> bool:
        """Return True if the task is not yet done."""
        return not self.done

    def matches(self, keyword: str) -> bool:
        """Return True if keyword appears in the title (case-insensitive)."""
        return keyword.strip().lower() in self.title.lower()

    def age_days(self) -> int:
        """Return how many days ago this task was created."""
        try:
            created = datetime.datetime.strptime(self.created_at, DATE_FMT)
            delta   = datetime.datetime.now() - created
            return delta.days
        except ValueError:
            return 0

    def is_overdue(self, threshold_days: int = 7) -> bool:
        """
        Return True if the task is older than threshold_days and still pending.

        Args:
            threshold_days (int): Number of days before a task is considered overdue.
        """
        return self.is_pending() and self.age_days() >= threshold_days

    def rename(self, new_title: str) -> "Task":
        """Update the task title with validation."""
        new_title = new_title.strip()
        if not new_title:
            raise ValidationError("Title cannot be empty",
                                   field="title", value=new_title)
        self.title = new_title
        return self

    #  Serialization ─

    def to_dict(self) -> dict:
        """
        Convert the Task to a dictionary for JSON serialization.

        Returns:
            dict: All task fields as a plain dictionary.
        """
        return {
            "id":         self.id,
            "title":      self.title,
            "priority":   self._priority,
            "category":   self._category,
            "status":     self.status,
            "done":       self.done,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """
        Create a Task instance from a dictionary (e.g., loaded from JSON).

        Args:
            data (dict): A task dictionary, typically from JSON storage.

        Returns:
            Task: A fully populated Task instance.
        """
        task            = cls.__new__(cls)
        task.id         = data["id"]
        task.title      = data["title"]
        task._priority  = data.get("priority", "medium")
        task._category  = data.get("category", "general")
        task.status     = data.get("status", "pending")
        task.done       = data.get("done", False)
        task.created_at = data.get("created_at", "")
        # Keep class counter ahead of loaded IDs
        Task._id_counter = max(Task._id_counter, task.id)
        return task

    @staticmethod
    def priority_to_score(priority: str) -> int:
        """Convert a priority string to a numeric score for sorting."""
        return {"high": 3, "medium": 2, "low": 1}.get(priority.lower(), 0)

    @classmethod
    def reset_counter(cls) -> None:
        """Reset the ID counter. Use only in tests."""
        cls._id_counter = 0

    #  Dunder Methods 

    def __str__(self) -> str:
        status = "✓" if self.done else "○"
        return (f"{status} Task #{self.id} "
                f"[{self._priority.upper()}] "
                f"{self.title} "
                f"({self._category})")

    def __repr__(self) -> str:
        return (f"Task(id={self.id!r}, title={self.title!r}, "
                f"priority={self._priority!r}, "
                f"category={self._category!r}, "
                f"done={self.done!r})")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Task):
            return NotImplemented
        return self.id == other.id

    def __lt__(self, other: "Task") -> bool:
        """Enable sorting by priority score (high first), then by ID."""
        if not isinstance(other, Task):
            return NotImplemented
        if self.priority_score != other.priority_score:
            return self.priority_score > other.priority_score   # higher score = comes first
        return self.id < other.id

    def __hash__(self) -> int:
        """Make Task hashable so it can be used in sets and as dict keys."""
        return hash(self.id)
```

---

### Updating Storage to Use Task Objects

Update `taskflow/storage/json_store.py` to serialize/deserialize `Task` objects:

```python
# taskflow/storage/json_store.py — updated for Day 12
import json
import shutil
import datetime
from pathlib import Path
from ..core.task import Task
from ..config import DATA_FILE, DATE_FMT
from ..errors import StorageError


def save_tasks(tasks: list[Task], filepath: Path = DATA_FILE) -> None:
    """Save a list of Task objects to JSON."""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = filepath.with_suffix(".tmp")
    try:
        data = [t.to_dict() for t in tasks]
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        tmp.rename(filepath)
    except (OSError, TypeError) as e:
        if tmp.exists():
            tmp.unlink()
        raise StorageError(f"Could not save tasks: {e}") from e


def load_tasks(filepath: Path = DATA_FILE) -> list[Task]:
    """Load Task objects from JSON. Returns [] if file missing."""
    if not filepath.exists():
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise StorageError("Expected a list in storage file")
        return [Task.from_dict(d) for d in data]
    except json.JSONDecodeError as e:
        raise StorageError("Storage file contains invalid JSON") from e
    except OSError as e:
        raise StorageError(f"Could not read storage file: {e}") from e
```

---

### Using the Task Class in Practice

```python
# In the Python REPL — try this yourself
from taskflow.core.task import Task

# Create tasks
t1 = Task("Review pull request", priority="high",   category="work")
t2 = Task("Buy groceries",       priority="low",    category="personal")
t3 = Task("Write Day 12 notes",  priority="medium", category="learning")

# Use methods
print(t1)                # ○ Task #1 [HIGH] Review pull request (work)
t1.mark_done()
print(t1)                # ✓ Task #1 [HIGH] Review pull request (work)
print(t1.is_pending())   # False

# Change priority through the property (validated)
t2.priority = "high"
t2.priority = "urgent"   # ❌ raises ValidationError

# Sort tasks — uses __lt__
tasks = [t2, t3, t1]
sorted_tasks = sorted(tasks)
for t in sorted_tasks:
    print(t)

# Use in a set — uses __hash__ and __eq__
task_set = {t1, t2, t3}
print(t1 in task_set)    # True

# Serialize to dict (for JSON)
print(t1.to_dict())

# Deserialize from dict (from JSON)
data = {"id": 99, "title": "Loaded task", "priority": "low",
        "category": "work", "status": "pending",
        "done": False, "created_at": "2025-05-19 10:00"}
t_loaded = Task.from_dict(data)
print(t_loaded)
```

---

## Exercises

**Exercise 1 — Method chaining.**
`mark_done()` and `rename()` return `self`. Use method chaining to do both in one line:

```python
task = Task("old title", "low", "personal")
task.rename("new title").mark_done()
print(task)   # ✓ Task #N [LOW] new title (personal)
```

**Exercise 2 — Sorting and `__lt__`.**
Create 10 tasks with mixed priorities. Sort them with `sorted()` and with `tasks.sort()`. Verify high-priority tasks come first. Then sort by `age_days()` instead — write a one-liner using `key=`.

**Exercise 3 — `is_overdue()` in practice.**
Manually override `created_at` on a task to simulate an old date:

```python
import datetime
task = Task("Old task", "high", "work")
task.created_at = (datetime.datetime.now() -
                   datetime.timedelta(days=10)).strftime("%Y-%m-%d %H:%M")
print(task.is_overdue(threshold_days=7))    # True
print(task.is_overdue(threshold_days=14))   # False
```

Add an `"overdue"` command to the app that shows all overdue tasks.

**Exercise 4 — `__eq__` and sets.**
Create two Task objects with the same ID but different titles. Verify they are considered equal (`==` returns `True`). Add both to a set — how many items does the set contain? Why? What does this tell you about the equality contract?

**Exercise 5 — `@property` for computed values.**
Add a `summary` property to `Task` that returns a one-line string without calling it as a method:

```python
@property
def summary(self) -> str:
    age  = f"{self.age_days()}d old"
    flag = "⚠ OVERDUE" if self.is_overdue() else ""
    return f"#{self.id} {self.title} [{self._priority}] {age} {flag}".strip()

print(task.summary)   # "#1 Review PR [high] 2d old"
```

**Exercise 6 (stretch) — `dataclasses` comparison.**
Rewrite `Task` using `@dataclass` from Python's `dataclasses` module. Use `field()` for defaults and `__post_init__` for validation. Compare the two implementations:

```python
from dataclasses import dataclass, field
import datetime

@dataclass
class TaskDataclass:
    title:      str
    priority:   str = "medium"
    category:   str = "general"
    id:         int = field(default_factory=lambda: 0, init=False)
    done:       bool = field(default=False, init=False)
    status:     str  = field(default="pending", init=False)
    created_at: str  = field(default_factory=lambda:
                             datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                             init=False)

    def __post_init__(self):
        if not self.title.strip():
            raise ValueError("Title cannot be empty")
```

What does `@dataclass` give you for free? What does it not give you?

---

## Checkpoint

Before moving to Day 13:

- [ ] I understand the difference between a class and an instance
- [ ] I can write `__init__` with instance and class attributes
- [ ] I understand what `self` is and why it exists
- [ ] I can define instance methods that read and modify `self`
- [ ] I have defined `__str__`, `__repr__`, `__eq__`, `__lt__`, `__hash__`
- [ ] I use `@property` and `@setter` for validated attribute access
- [ ] I use `@classmethod` for alternative constructors (`from_dict`)
- [ ] I use `@staticmethod` for utility functions that belong to the class
- [ ] The `Task` class replaces plain dicts throughout the app
- [ ] `Task.from_dict()` and `Task.to_dict()` enable clean JSON round-trips
- [ ] `Task._id_counter` replaces the `next_id = [1]` list hack
- [ ] Tasks can be sorted with `sorted()` thanks to `__lt__`
- [ ] Tasks can live in sets thanks to `__hash__`

---

## Common Errors on Day 12

**Forgetting `self` in method definition:**

```python
class Task:
    def mark_done():       # ❌ missing self
        self.done = True   # NameError: name 'self' is not defined
    
    def mark_done(self):   # ✅
        self.done = True
```

**Calling a method without parentheses:**

```python
task.mark_done    # ❌ returns the method object — does nothing
task.mark_done()  # ✅ calls the method
```

**`@property` getter and setter must have the same name:**

```python
@property
def priority(self):       # getter named 'priority'
    return self._priority

@priority.setter          # must use the SAME name
def priority(self, value):
    self._priority = value
```

**Modifying a class attribute through an instance creates an instance attribute instead:**

```python
class Task:
    _id_counter = 0

t = Task(...)
t._id_counter += 1     # ❌ creates an instance attribute on t, not modifying the class attr
Task._id_counter += 1  # ✅ modifies the shared class attribute
```

**`__hash__` must be defined if `__eq__` is defined:**

Python automatically sets `__hash__ = None` when you define `__eq__` without `__hash__` — making instances unhashable (cannot be put in sets or used as dict keys). Always define both together.

---

## What's Coming

On **Day 13** we go deeper into OOP — inheritance and polymorphism. Right now every task is the same type: `Task`. Tomorrow we introduce subclasses: `UrgentTask`, `RecurringTask`, `DeadlineTask` — each extending the base `Task` with its own behaviour. We also explore `super()`, `isinstance()`, abstract base classes, and the Liskov Substitution Principle. The TaskFlow data model gets genuinely rich.
