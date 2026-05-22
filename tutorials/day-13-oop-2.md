# Day 13 — Object-Oriented Programming II: Inheritance & Polymorphism

> **Series:** Python & AI Engineering — Zero to Production
> **Phase:** 1 — Foundations
> **Python Version:** 3.14
> **Project:** TaskFlow AI — Building a family of specialised task types

---

## Learning Objective

By the end of today, you will understand inheritance — how classes extend other classes — and polymorphism — how different classes can be used interchangeably through a shared interface. You will build a family of specialised `Task` subclasses (`UrgentTask`, `RecurringTask`, `DeadlineTask`) and learn when inheritance helps and when it hurts.

---

## What We Build Today

Three `Task` subclasses in `taskflow/core/task_types.py`, each with unique behaviour while sharing the full `Task` base interface. The app learns to display and handle each type differently.

```python
# UrgentTask — auto-sets priority to high, adds escalation
urgent = UrgentTask("Server is down", category="work")
print(urgent.priority)        # "high" — always
print(urgent.escalation_note) # "⚠ URGENT — escalate immediately if pending > 2h"

# RecurringTask — resets itself after being marked done
daily = RecurringTask("Review metrics", category="work",
                      recurrence="daily")
daily.mark_done()
print(daily.done)             # False — auto-reset!
print(daily.completion_count) # 1

# DeadlineTask — tracks due date and urgency
report = DeadlineTask("Submit quarterly report", category="work",
                      due_date="2025-06-01")
print(report.days_until_due)  # 13
print(report.is_overdue())    # False (not past due date)
print(report.urgency_label)   # "⚡ DUE SOON" or "🔴 OVERDUE" etc.
```

---

## Concepts Covered

- Inheritance — `class Child(Parent):`
- `super()` — calling the parent class
- Method overriding — replacing parent behaviour
- `isinstance()` and `issubclass()` — type checking
- Polymorphism — one interface, many implementations
- Abstract Base Classes — `ABC` and `@abstractmethod`
- The Liskov Substitution Principle
- Multiple inheritance — Python's MRO
- Composition vs inheritance — when to use which
- `__init_subclass__` — hook for subclass creation

---

## Full Tutorial

### Inheritance — Extending a Class

Inheritance lets you create a new class that inherits all attributes and methods of an existing class, then add or override what you need:

```python
class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        return "..."

class Dog(Animal):
    def speak(self):          # overrides parent method
        return f"{self.name} says: Woof!"

class Cat(Animal):
    def speak(self):
        return f"{self.name} says: Meow!"

dog = Dog("Rex")
cat = Cat("Whiskers")

print(dog.name)    # "Rex"     — inherited from Animal
print(dog.speak()) # "Rex says: Woof!"
print(cat.speak()) # "Whiskers says: Meow!"
```

`Dog` inherits `__init__` and `name` from `Animal`. It overrides `speak()` with its own behaviour. `Cat` does the same, differently.

---

### `super()` — Calling the Parent

`super()` gives you access to the parent class. Use it to extend, not replace, the parent's `__init__`:

```python
class Task:
    def __init__(self, title, priority="medium", category="general"):
        self.title    = title
        self.priority = priority
        self.category = category
        self.done     = False

class UrgentTask(Task):
    def __init__(self, title, category="general"):
        super().__init__(title, priority="high", category=category)
        self.escalation_note = "⚠ URGENT — escalate immediately if pending > 2h"

urgent = UrgentTask("Server is down", category="work")
print(urgent.title)           # "Server is down"  — from Task.__init__ via super()
print(urgent.priority)        # "high"             — forced by UrgentTask
print(urgent.escalation_note) # "⚠ URGENT..."     — UrgentTask-specific
```

`super().__init__(...)` runs the parent's `__init__`. Always call it first in the child's `__init__` unless you have a specific reason not to.

---

### Method Overriding

A subclass can replace any parent method with its own version:

```python
class Task:
    def __str__(self):
        status = "✓" if self.done else "○"
        return f"{status} [{self.priority.upper()}] {self.title}"

class UrgentTask(Task):
    def __str__(self):
        base = super().__str__()    # get the parent's string
        return f"🚨 {base}"         # add urgent prefix

urgent = UrgentTask("Server down", "work")
print(urgent)   # 🚨 ○ [HIGH] Server down
```

Use `super().method()` to build on the parent's implementation rather than rewriting it from scratch.

---

### Polymorphism — One Interface, Many Behaviours

Polymorphism means you can write code that works on the parent type, and it will automatically use the correct behaviour for whatever subclass you give it:

```python
def display_task(task: Task) -> None:
    """Works with Task, UrgentTask, RecurringTask, DeadlineTask — any Task subclass."""
    print(task)                    # calls the right __str__ for each type
    if task.is_pending():
        print("  Status: pending")
    else:
        print("  Status: done")

tasks = [
    Task("Buy groceries", "low", "personal"),
    UrgentTask("Server down", "work"),
    DeadlineTask("Submit report", "work", due_date="2025-06-01"),
]

for task in tasks:
    display_task(task)   # each prints differently — same function, different results
```

This is the power of polymorphism: `display_task` does not need to know what kind of task it receives. It just calls the methods defined on `Task`, and the subclass provides the right implementation.

---

### `isinstance()` and `issubclass()`

```python
t  = Task("Review PR", "high", "work")
ut = UrgentTask("Server down", "work")

print(isinstance(ut, UrgentTask))  # True  — it IS an UrgentTask
print(isinstance(ut, Task))        # True  — it IS ALSO a Task (inheritance)
print(isinstance(t,  UrgentTask))  # False — plain Task is NOT an UrgentTask

print(issubclass(UrgentTask, Task))   # True
print(issubclass(Task, UrgentTask))   # False
```

Use `isinstance()` when you need to handle subclasses differently — but prefer designing with polymorphism so type checks are rarely needed.

---

### Abstract Base Classes

An **abstract base class (ABC)** defines a contract — methods that every subclass MUST implement. You cannot instantiate an ABC directly:

```python
from abc import ABC, abstractmethod

class BaseTask(ABC):
    """Abstract base — all task types must implement these methods."""

    @abstractmethod
    def mark_done(self) -> "BaseTask":
        """Mark the task as done. Must be implemented by subclasses."""
        ...

    @abstractmethod
    def is_pending(self) -> bool:
        """Return True if the task needs to be done."""
        ...

    @abstractmethod
    def to_dict(self) -> dict:
        """Serialize the task to a dictionary."""
        ...


# You cannot instantiate ABC directly:
bt = BaseTask()   # ❌ TypeError: Can't instantiate abstract class
```

ABCs enforce the interface contract at instantiation time — you will know immediately if a subclass forgot to implement a required method.

---

### The Liskov Substitution Principle

The **Liskov Substitution Principle (LSP)** states: anywhere you use a `Task`, you should be able to use any `Task` subclass without breaking the code.

In practice this means:
- Subclasses must accept at least the same arguments as the parent
- Subclasses must return the same types from overridden methods
- Subclasses must not raise new exceptions that callers don't expect
- Subclasses must honour the parent's contracts (a `mark_done()` method on any task subclass must actually mark it done)

Violating LSP breaks polymorphism — your subclass cannot safely replace the parent in existing code.

---

### Multiple Inheritance and MRO

Python supports multiple inheritance — a class can inherit from more than one parent:

```python
class Timestamped:
    def __init__(self):
        import datetime
        self.created_at = datetime.datetime.now().isoformat()

class Taggable:
    def __init__(self):
        self.tags = set()

    def add_tag(self, tag):
        self.tags.add(tag)

class TaggedTask(Task, Timestamped, Taggable):
    def __init__(self, title, priority, category):
        Task.__init__(self, title, priority, category)
        Timestamped.__init__(self)
        Taggable.__init__(self)
```

Python resolves method lookup using the **Method Resolution Order (MRO)** — a linearized chain of parent classes:

```python
print(TaggedTask.__mro__)
# (<class 'TaggedTask'>, <class 'Task'>, <class 'Timestamped'>, <class 'Taggable'>, ...)
```

Multiple inheritance is powerful but complex. Use it sparingly — prefer **composition** (see below) for most cases.

---

### Composition vs Inheritance

**Inheritance** ("is-a"): `UrgentTask` IS a `Task`.
**Composition** ("has-a"): `Task` HAS a `Reminder`. `Task` HAS a `Tag`.

```python
# Inheritance — good for "is-a" relationships
class UrgentTask(Task): ...

# Composition — better for "has-a" relationships
class Reminder:
    def __init__(self, message, remind_at):
        self.message   = message
        self.remind_at = remind_at

class Task:
    def __init__(self, title, priority, category):
        ...
        self.reminder = None    # composition — Task HAS a Reminder (optional)

    def set_reminder(self, message, remind_at):
        self.reminder = Reminder(message, remind_at)
```

**Rule of thumb:** if you find yourself overriding many parent methods, or the relationship is "has-a" not "is-a", use composition. Inheritance hierarchies deeper than 2-3 levels are almost always a design smell.

---

### Building `task_types.py`

```python
# taskflow/core/task_types.py
# TaskFlow AI — Day 13
# Specialised Task subclasses for different task types.

import datetime
from .task   import Task
from ..config import DATE_FMT
from ..errors import ValidationError


class UrgentTask(Task):
    """
    A task that is always high priority and surfaces escalation guidance.

    Priority is forced to 'high' and cannot be changed to lower values.
    """

    ESCALATION_THRESHOLD_HOURS = 2

    def __init__(self, title: str, category: str = "work"):
        """
        Create an urgent task. Priority is always 'high'.

        Args:
            title    (str): Task title.
            category (str): Task category.
        """
        super().__init__(title, priority="high", category=category)

    @property
    def priority(self) -> str:
        return "high"

    @priority.setter
    def priority(self, value: str) -> None:
        """Urgent tasks are always high priority — silently enforce it."""
        if value != "high":
            raise ValidationError(
                "UrgentTask priority is always 'high' and cannot be changed.",
                field="priority", value=value
            )
        self._priority = "high"

    @property
    def escalation_note(self) -> str:
        """Return an escalation message if the task has been pending too long."""
        age_hours = self.age_days() * 24
        if self.is_pending() and age_hours >= self.ESCALATION_THRESHOLD_HOURS:
            return (f"⚠  URGENT — pending for ~{self.age_days()}d. "
                    f"Escalate immediately.")
        return "⚠  URGENT — handle as soon as possible."

    def __str__(self) -> str:
        base = super().__str__()
        return f"🚨 {base}"

    def __repr__(self) -> str:
        return f"UrgentTask(id={self.id!r}, title={self.title!r}, done={self.done!r})"

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["type"] = "urgent"
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "UrgentTask":
        task          = cls.__new__(cls)
        task.id       = data["id"]
        task.title    = data["title"]
        task._priority = "high"
        task._category = data.get("category", "work")
        task.status   = data.get("status", "pending")
        task.done     = data.get("done", False)
        task.created_at = data.get("created_at", "")
        Task._id_counter = max(Task._id_counter, task.id)
        return task


class RecurringTask(Task):
    """
    A task that automatically resets to pending after being marked done.

    Useful for daily standups, weekly reviews, recurring chores.

    Attributes:
        recurrence        (str): How often the task recurs ('daily', 'weekly', 'monthly').
        completion_count  (int): How many times the task has been completed.
    """

    VALID_RECURRENCES = {"daily", "weekly", "monthly"}

    def __init__(self, title: str, priority: str = "medium",
                 category: str = "work", recurrence: str = "daily"):
        """
        Create a recurring task.

        Args:
            title      (str): Task title.
            priority   (str): Task priority.
            category   (str): Task category.
            recurrence (str): How often it recurs — 'daily', 'weekly', 'monthly'.
        """
        if recurrence not in self.VALID_RECURRENCES:
            raise ValidationError(
                f"Invalid recurrence. Choose from: {self.VALID_RECURRENCES}",
                field="recurrence", value=recurrence
            )
        super().__init__(title, priority=priority, category=category)
        self.recurrence       = recurrence
        self.completion_count = 0

    def mark_done(self) -> "RecurringTask":
        """Mark done AND immediately reset to pending — it will recur."""
        self.completion_count += 1
        # Reset to pending after recording the completion
        self.done   = False
        self.status = "pending"
        return self

    @property
    def recurrence_label(self) -> str:
        return f"↺ {self.recurrence.title()}"

    def __str__(self) -> str:
        base = super().__str__()
        return f"{base} {self.recurrence_label} (done {self.completion_count}×)"

    def __repr__(self) -> str:
        return (f"RecurringTask(id={self.id!r}, title={self.title!r}, "
                f"recurrence={self.recurrence!r}, "
                f"completion_count={self.completion_count!r})")

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["type"]             = "recurring"
        d["recurrence"]       = self.recurrence
        d["completion_count"] = self.completion_count
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "RecurringTask":
        task                 = cls.__new__(cls)
        task.id              = data["id"]
        task.title           = data["title"]
        task._priority       = data.get("priority", "medium")
        task._category       = data.get("category", "work")
        task.status          = data.get("status", "pending")
        task.done            = data.get("done", False)
        task.created_at      = data.get("created_at", "")
        task.recurrence      = data.get("recurrence", "daily")
        task.completion_count = data.get("completion_count", 0)
        Task._id_counter     = max(Task._id_counter, task.id)
        return task


class DeadlineTask(Task):
    """
    A task with an explicit due date and urgency tracking.

    Attributes:
        due_date (str): Due date in 'YYYY-MM-DD' format.
    """

    DUE_DATE_FMT = "%Y-%m-%d"

    def __init__(self, title: str, category: str = "work",
                 priority: str = "medium", due_date: str = ""):
        """
        Create a task with a deadline.

        Args:
            title    (str): Task title.
            category (str): Task category.
            priority (str): Task priority.
            due_date (str): Due date as 'YYYY-MM-DD'. Required.
        """
        if not due_date:
            raise ValidationError("DeadlineTask requires a due_date (YYYY-MM-DD)",
                                   field="due_date", value=due_date)
        try:
            datetime.datetime.strptime(due_date, self.DUE_DATE_FMT)
        except ValueError:
            raise ValidationError(
                f"Invalid due_date format. Expected YYYY-MM-DD.",
                field="due_date", value=due_date
            )
        super().__init__(title, priority=priority, category=category)
        self.due_date = due_date

    @property
    def days_until_due(self) -> int:
        """Return days until due (negative if overdue)."""
        due   = datetime.datetime.strptime(self.due_date, self.DUE_DATE_FMT).date()
        today = datetime.date.today()
        return (due - today).days

    def is_overdue(self, threshold_days: int = 0) -> bool:
        """
        Override base class: DeadlineTask is overdue if past its due date.

        Args:
            threshold_days: Unused — kept for LSP compatibility with base class.
        """
        return self.is_pending() and self.days_until_due < 0

    @property
    def urgency_label(self) -> str:
        """Return a coloured urgency label based on days until due."""
        days = self.days_until_due
        if self.done:
            return "✓ Complete"
        if days < 0:
            return f"🔴 OVERDUE by {abs(days)}d"
        if days == 0:
            return "🔴 DUE TODAY"
        if days <= 2:
            return f"🟠 DUE IN {days}d"
        if days <= 7:
            return f"🟡 DUE IN {days}d"
        return f"🟢 DUE IN {days}d"

    def __str__(self) -> str:
        base = super().__str__()
        return f"{base} [{self.urgency_label}]"

    def __repr__(self) -> str:
        return (f"DeadlineTask(id={self.id!r}, title={self.title!r}, "
                f"due_date={self.due_date!r}, done={self.done!r})")

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["type"]     = "deadline"
        d["due_date"] = self.due_date
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "DeadlineTask":
        task            = cls.__new__(cls)
        task.id         = data["id"]
        task.title      = data["title"]
        task._priority  = data.get("priority", "medium")
        task._category  = data.get("category", "work")
        task.status     = data.get("status", "pending")
        task.done       = data.get("done", False)
        task.created_at = data.get("created_at", "")
        task.due_date   = data.get("due_date", "")
        Task._id_counter = max(Task._id_counter, task.id)
        return task
```

---

### A `TaskFactory` for Polymorphic Loading

Update storage to detect task type and instantiate the right class:

```python
# taskflow/core/task_factory.py
"""
TaskFactory — creates the right Task subclass from a dict.
Used during deserialization to restore the original task type.
"""

from .task        import Task
from .task_types  import UrgentTask, RecurringTask, DeadlineTask


TASK_TYPE_MAP = {
    "urgent":    UrgentTask,
    "recurring": RecurringTask,
    "deadline":  DeadlineTask,
}


def task_from_dict(data: dict) -> Task:
    """
    Create the appropriate Task subclass from a dictionary.

    Args:
        data (dict): Task data dict, optionally containing a 'type' field.

    Returns:
        Task: An instance of the correct Task subclass.
    """
    task_type = data.get("type", "standard")
    cls       = TASK_TYPE_MAP.get(task_type, Task)
    return cls.from_dict(data)
```

Update `json_store.py` to use `task_from_dict`:

```python
from ..core.task_factory import task_from_dict

def load_tasks(filepath: Path = DATA_FILE) -> list[Task]:
    ...
    return [task_from_dict(d) for d in data]
```

---

## Exercises

**Exercise 1 — Polymorphism in action.**
Create a list containing one of each task type. Write a `display_all(tasks)` function that loops and prints each. Confirm each type uses its own `__str__`. Then call `t.is_overdue()` on each — verify that `DeadlineTask` uses the due-date logic, while plain `Task` uses the age-based logic.

**Exercise 2 — Add a `ChecklistTask` subclass.**
Create `ChecklistTask(Task)` — a task with a list of sub-items. The task is done only when all sub-items are checked off:

```python
checklist = ChecklistTask("Deploy v1.0", "work", items=[
    "Write tests", "Update README", "Tag release", "Push to Docker Hub"
])
checklist.check("Write tests")
checklist.check("Update README")
print(checklist.progress)   # "2/4 items complete"
print(checklist.done)       # False — not all items done yet
checklist.check("Tag release")
checklist.check("Push to Docker Hub")
print(checklist.done)       # True — all items checked
```

**Exercise 3 — `isinstance()` type routing.**
In `display.py`, update `display_tasks()` to show extra info for each type:
- `UrgentTask`: show `escalation_note`
- `RecurringTask`: show `completion_count` and `recurrence_label`
- `DeadlineTask`: show `urgency_label` and `days_until_due`
- Plain `Task`: no extra info

Use `isinstance()` for the type checks.

**Exercise 4 — LSP violation detection.**
Write a `RecurringTask` that overrides `mark_done()` such that it raises an exception instead of resetting (breaking LSP). Add it to a list of tasks and call a generic `complete_all(tasks)` function. Show how it breaks. Then fix it to honour the LSP.

**Exercise 5 — `__init_subclass__` registry.**
Use `__init_subclass__` to automatically register every Task subclass:

```python
class Task:
    _registry: dict[str, type] = {}

    def __init_subclass__(cls, task_type: str = "", **kwargs):
        super().__init_subclass__(**kwargs)
        if task_type:
            Task._registry[task_type] = cls
            print(f"Registered task type: '{task_type}' → {cls.__name__}")

class UrgentTask(Task, task_type="urgent"): ...
class RecurringTask(Task, task_type="recurring"): ...

print(Task._registry)
# {'urgent': UrgentTask, 'recurring': RecurringTask}
```

Replace `TASK_TYPE_MAP` in `task_factory.py` with `Task._registry`.

**Exercise 6 (stretch) — Abstract `BaseTask`.**
Refactor: create an abstract `BaseTask(ABC)` with `@abstractmethod` for `mark_done`, `is_pending`, `to_dict`, and `from_dict`. Make `Task` inherit from `BaseTask`. Verify that creating an incomplete subclass (missing a required method) raises `TypeError` immediately at instantiation.

---

## Checkpoint

Before moving to Day 14:

- [ ] I can define a subclass with `class Child(Parent):`
- [ ] I always call `super().__init__(...)` first in a subclass `__init__`
- [ ] I understand method overriding — child replaces parent behaviour
- [ ] I use `super().method()` to extend (not replace) parent behaviour
- [ ] I understand polymorphism — code written for `Task` works for all subclasses
- [ ] I use `isinstance(obj, Class)` for type-aware behaviour
- [ ] I understand abstract base classes and `@abstractmethod`
- [ ] I know the Liskov Substitution Principle and can identify violations
- [ ] I understand composition vs inheritance and when to use each
- [ ] `UrgentTask`, `RecurringTask`, `DeadlineTask` are implemented and tested
- [ ] `TaskFactory` restores the correct subclass on deserialization

---

## Common Errors on Day 13

**Not calling `super().__init__()`:**

```python
class UrgentTask(Task):
    def __init__(self, title, category):
        self.category = category   # ❌ forgot super() — title, done, etc. never set
        
    def __init__(self, title, category):
        super().__init__(title, priority="high", category=category)  # ✅
```

**Violating LSP — returning a different type from an overridden method:**

```python
class RecurringTask(Task):
    def mark_done(self):
        return "done"   # ❌ base Task.mark_done() returns Task — LSP violated
    
    def mark_done(self) -> "RecurringTask":
        ...
        return self     # ✅ returns self, compatible with base contract
```

**`isinstance()` vs `type()`:**

```python
task = UrgentTask("Server down", "work")

print(type(task) == Task)          # False — it's an UrgentTask
print(isinstance(task, Task))      # True  — it IS a Task (via inheritance)
print(isinstance(task, UrgentTask)) # True
```

Always use `isinstance()` — `type()` equality ignores inheritance.

**Forgetting to update `to_dict()` and `from_dict()` in subclasses:**

Every subclass that adds attributes must override `to_dict()` to include them and `from_dict()` to restore them. If you forget, those attributes are lost on save/load.

---

## What's Coming

On **Day 14** we introduce the final two concepts of Week 2 before the first milestone: `working with APIs` more deeply and `regular expressions`. We will add a smarter task input parser that understands natural language shorthand — `"#high @work Review PR !2025-06-01"` — using `re` to extract priority, category, and deadline from a single input string. The parser will automatically create the right Task subclass based on what it finds.
