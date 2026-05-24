# Day 29 — Design Patterns II: Factory, Observer, Strategy

> **Series:** Python & AI Engineering — Zero to Production
> **Phase:** 2 — Real Engineering
> **Python Version:** 3.14
> **Project:** TaskFlow AI — Events, flexible creation, pluggable algorithms

---

## Learning Objective

By the end of today, you will have applied three more design patterns to TaskFlow AI: Factory (already seen in `task_factory.py` — now formalised), Observer (emit events when tasks change), and Strategy (pluggable sorting and filtering algorithms). These patterns are the backbone of the FastAPI event system (Phase 3) and the AI workflow orchestration (Phase 4).

---

## What We Build Today

A `taskflow/events.py` module implementing the Observer pattern, a formalised `TaskFactory` class, and a `SortStrategy` hierarchy with pluggable sorting algorithms.

```python
# Observer — emit and respond to task lifecycle events
from taskflow.events import event_bus

@event_bus.on("task.added")
def on_task_added(task: Task) -> None:
    logger.info("New task: %s", task.title)
    if len(task.title) > 50:
        print("  ℹ  Long title — consider breaking this task into subtasks.")

@event_bus.on("task.done")
def on_task_completed(task: Task) -> None:
    print(f"\n  🎉 Well done! '{task.title}' is complete.")

# Emit events from services
event_bus.emit("task.added", task)
event_bus.emit("task.done", task)

# Strategy — swap sorting algorithm without changing callers
from taskflow.strategies import SortByPriority, SortByTitle, SortByAge

sorter = SortByPriority()
sorted_tasks = sorter.sort(tasks)

sorter = SortByAge()   # ONE LINE CHANGE — everything else unchanged
sorted_tasks = sorter.sort(tasks)
```

---

## Concepts Covered

- Factory pattern — centralised object creation
- Factory Method vs Abstract Factory
- Observer / Event Bus pattern
- Weak references in observers — preventing memory leaks
- Strategy pattern — interchangeable algorithms
- `ABC` and `@abstractmethod` for strategy interfaces
- Callable strategies — functions as strategies
- `functools.partial` for parameterised strategies
- When patterns overlap — Factory + Strategy, Observer + Strategy

---

## Full Tutorial

### The Factory Pattern

**Problem:** You need to create one of several related objects, but the caller should not need to know which specific class to use.

**Solution:** A **Factory** centralises the creation logic. Callers pass data to the factory and receive the correct object back without knowing which class was used.

You already have this in `task_factory.py` — `task_from_dict()` is a factory function. Today we formalise it into a class-based `TaskFactory` with registration support:

```python
# taskflow/core/task_factory.py — upgraded for Day 29

from __future__ import annotations
import logging
from typing import ClassVar
from .task        import Task
from .task_types  import UrgentTask, RecurringTask, DeadlineTask

logger = logging.getLogger(__name__)

__all__ = ["TaskFactory", "task_from_dict"]


class TaskFactory:
    """
    Centralised factory for creating Task objects from stored dictionaries.

    Supports registration of custom task types at runtime — useful for
    plugins and Phase 4's AI task types.

    Class Attributes:
        _registry (dict): Maps type name strings to Task subclasses.
    """

    _registry: ClassVar[dict[str, type[Task]]] = {
        "standard":  Task,
        "urgent":    UrgentTask,
        "recurring": RecurringTask,
        "deadline":  DeadlineTask,
    }

    @classmethod
    def register(cls, type_name: str, task_class: type[Task]) -> None:
        """
        Register a new task type with the factory.

        Args:
            type_name  (str)        : The string identifier stored in JSON.
            task_class (type[Task]) : The Task subclass to instantiate.
        """
        if type_name in cls._registry:
            logger.warning(
                "Overwriting existing factory registration for '%s'", type_name
            )
        cls._registry[type_name] = task_class
        logger.debug("Registered task type: %s → %s", type_name, task_class.__name__)

    @classmethod
    def create_from_dict(cls, data: dict) -> Task:
        """
        Create the appropriate Task subclass from a stored dictionary.

        Args:
            data (dict): Task data with an optional 'type' field.

        Returns:
            Task: An instance of the correct subclass.
        """
        type_name  = data.get("type", "standard")
        task_class = cls._registry.get(type_name, Task)

        if type_name not in cls._registry:
            logger.warning(
                "Unknown task type '%s' — falling back to Task", type_name
            )

        return task_class.from_dict(data)

    @classmethod
    def registered_types(cls) -> list[str]:
        """Return all registered type name strings."""
        return list(cls._registry.keys())


# Module-level convenience function — preserves backward compatibility
def task_from_dict(data: dict) -> Task:
    """Create a Task from a dict using the default TaskFactory."""
    return TaskFactory.create_from_dict(data)
```

---

### The Observer / Event Bus Pattern

**Problem:** When a task is added, completed, or deleted, multiple parts of the system might want to react — logging, sending notifications, updating statistics, triggering AI analysis. But those parts should not be coupled to each other.

**Solution:** An **Event Bus** — components emit named events; other components subscribe to events and react independently.

```python
# taskflow/events.py
# TaskFlow AI — Event bus (Observer pattern).
#
# The event bus decouples event producers (services) from event consumers
# (logging, notifications, AI triggers).
#
# Usage:
#   # Subscribe
#   @event_bus.on("task.added")
#   def handler(task: Task) -> None: ...
#
#   # Emit
#   event_bus.emit("task.added", task)
#
# Version history:
#   Day 29 — initial implementation

from __future__ import annotations
import logging
from collections import defaultdict
from typing import Callable, Any

logger = logging.getLogger(__name__)

__all__ = ["EventBus", "event_bus"]


class EventBus:
    """
    Simple synchronous event bus.

    Subscribers register handlers for named events.
    When an event is emitted, all registered handlers are called in
    registration order.

    Handlers are called synchronously — no threading or async.
    Phase 3 will introduce async event handling via Celery.
    """

    def __init__(self) -> None:
        # event_name → list of handler callables
        self._handlers: dict[str, list[Callable[..., Any]]] = defaultdict(list)

    def on(self, event_name: str) -> Callable:
        """
        Decorator — register a function as a handler for an event.

        Args:
            event_name (str): The event to subscribe to.

        Returns:
            Callable: The original function (unchanged).

        Example:
            @event_bus.on("task.added")
            def handle_add(task: Task) -> None:
                print(f"Task added: {task.title}")
        """
        def decorator(handler: Callable) -> Callable:
            self._handlers[event_name].append(handler)
            logger.debug(
                "Registered handler '%s' for event '%s'",
                handler.__name__, event_name,
            )
            return handler
        return decorator

    def subscribe(self, event_name: str, handler: Callable) -> None:
        """
        Register a handler programmatically (without decorator).

        Args:
            event_name (str)    : The event to subscribe to.
            handler    (Callable): The handler function.
        """
        self._handlers[event_name].append(handler)

    def unsubscribe(self, event_name: str, handler: Callable) -> None:
        """
        Remove a previously registered handler.

        Args:
            event_name (str)    : The event name.
            handler    (Callable): The handler to remove.
        """
        try:
            self._handlers[event_name].remove(handler)
        except ValueError:
            logger.warning(
                "Handler '%s' not found for event '%s'",
                getattr(handler, "__name__", repr(handler)), event_name,
            )

    def emit(self, event_name: str, *args: Any, **kwargs: Any) -> None:
        """
        Emit an event — call all registered handlers with the given arguments.

        Failures in individual handlers are logged and do not prevent
        other handlers from running.

        Args:
            event_name (str): The event to emit.
            *args, **kwargs : Arguments passed to every handler.
        """
        handlers = self._handlers.get(event_name, [])
        if not handlers:
            logger.debug("Event '%s' emitted with no subscribers", event_name)
            return

        logger.debug(
            "Emitting '%s' to %d handler(s)", event_name, len(handlers)
        )
        for handler in handlers:
            try:
                handler(*args, **kwargs)
            except Exception as e:
                logger.error(
                    "Handler '%s' raised an error for event '%s': %s",
                    getattr(handler, "__name__", repr(handler)),
                    event_name, e,
                    exc_info=True,
                )

    def handlers_for(self, event_name: str) -> list[Callable]:
        """Return a copy of the handler list for an event."""
        return list(self._handlers.get(event_name, []))

    def clear(self, event_name: str | None = None) -> None:
        """
        Remove all handlers.

        Args:
            event_name (str | None): Clear handlers for one event.
                                     If None, clear all handlers.
        """
        if event_name:
            self._handlers.pop(event_name, None)
        else:
            self._handlers.clear()

    def __repr__(self) -> str:
        total = sum(len(h) for h in self._handlers.values())
        return f"EventBus({len(self._handlers)} events, {total} handlers)"


# Application-level singleton event bus
event_bus = EventBus()


# ── Built-in event names ──────────────────────────────────
# Use these constants to avoid typos in event name strings.

class Events:
    """Canonical event name constants."""
    TASK_ADDED    = "task.added"
    TASK_DONE     = "task.done"
    TASK_REMOVED  = "task.removed"
    TASK_RENAMED  = "task.renamed"
    LIMIT_REACHED = "task.limit_reached"
    STORAGE_SAVED = "storage.saved"
    STORAGE_ERROR = "storage.error"
```

---

### Wiring Events into Services

```python
# In taskflow/services.py — add event emissions

from .events import event_bus, Events

def add_task(task: Task, repo: TaskRepository, plan: str | None = None) -> Task:
    """Add task and emit TASK_ADDED event."""
    from .config import PLAN_LIMITS, USER_PLAN
    limit = PLAN_LIMITS.get(plan or USER_PLAN, PLAN_LIMITS["free"])
    if repo.count() >= limit:
        event_bus.emit(Events.LIMIT_REACHED, repo.count(), limit)
        raise ValidationError(...)
    result = repo.add(task)
    event_bus.emit(Events.TASK_ADDED, result)
    return result


def mark_done(task_id: int, repo: TaskRepository) -> Task:
    """Mark task done and emit TASK_DONE event."""
    # ... mark done logic ...
    event_bus.emit(Events.TASK_DONE, task)
    return task
```

Register default handlers in `main.py`:

```python
# taskflow/main.py — register event handlers on startup

from .events import event_bus, Events
from .core.task import Task

def _register_event_handlers() -> None:
    """Register built-in application event handlers."""
    import logging
    logger = logging.getLogger("taskflow.events")

    @event_bus.on(Events.TASK_ADDED)
    def log_task_added(task: Task) -> None:
        logger.info("Task added: '%s' [%s]", task.title, task.priority)

    @event_bus.on(Events.TASK_DONE)
    def log_task_done(task: Task) -> None:
        logger.info("Task completed: '%s'", task.title)

    @event_bus.on(Events.LIMIT_REACHED)
    def warn_limit(current: int, limit: int) -> None:
        logger.warning("Task limit reached: %d/%d", current, limit)

    @event_bus.on(Events.STORAGE_ERROR)
    def alert_storage_error(error: Exception) -> None:
        logger.critical("STORAGE ERROR: %s", error)
```

---

### The Strategy Pattern

**Problem:** The app sorts tasks — but the best sort order depends on context. Sorting by priority makes sense for the task view; sorting by due date makes sense for the daily agenda; sorting by creation date makes sense for chronological review. Hardcoding one sort order forces code changes for each new requirement.

**Solution:** A **Strategy** — encapsulate each sorting algorithm in its own class behind a common interface. Swap strategies without changing the code that uses them.

```python
# taskflow/strategies.py
# TaskFlow AI — Pluggable sort and filter strategies.
#
# Version history:
#   Day 29 — initial implementation

from __future__ import annotations
from abc import ABC, abstractmethod
from .core.task import Task

__all__ = [
    "SortStrategy",
    "SortByPriority",
    "SortByTitle",
    "SortByCategory",
    "SortByAge",
    "SortByDueDate",
    "CompositeSort",
]


class SortStrategy(ABC):
    """Abstract base for all sort strategies."""

    @abstractmethod
    def sort(self, tasks: list[Task]) -> list[Task]:
        """
        Return a new sorted list without modifying the original.

        Args:
            tasks (list[Task]): Tasks to sort.

        Returns:
            list[Task]: Sorted copy.
        """
        ...

    def __call__(self, tasks: list[Task]) -> list[Task]:
        """Allow strategies to be called as functions."""
        return self.sort(tasks)


class SortByPriority(SortStrategy):
    """Sort by priority score descending (high first), then by ID."""

    def __init__(self, reverse: bool = False) -> None:
        self._reverse = reverse

    def sort(self, tasks: list[Task]) -> list[Task]:
        return sorted(
            tasks,
            key=lambda t: (-t.priority_score, t.id),
            reverse=self._reverse,
        )


class SortByTitle(SortStrategy):
    """Sort alphabetically by title."""

    def __init__(self, reverse: bool = False) -> None:
        self._reverse = reverse

    def sort(self, tasks: list[Task]) -> list[Task]:
        return sorted(
            tasks,
            key=lambda t: t.title.lower(),
            reverse=self._reverse,
        )


class SortByCategory(SortStrategy):
    """Sort alphabetically by category, then by priority within each category."""

    def sort(self, tasks: list[Task]) -> list[Task]:
        return sorted(
            tasks,
            key=lambda t: (t.category, -t.priority_score),
        )


class SortByAge(SortStrategy):
    """Sort by creation date — oldest first by default."""

    def __init__(self, newest_first: bool = False) -> None:
        self._reverse = newest_first

    def sort(self, tasks: list[Task]) -> list[Task]:
        return sorted(
            tasks,
            key=lambda t: t.created_at,
            reverse=self._reverse,
        )


class SortByDueDate(SortStrategy):
    """
    Sort DeadlineTasks by due date (soonest first).

    Non-DeadlineTasks are placed after all DeadlineTasks.
    """

    def sort(self, tasks: list[Task]) -> list[Task]:
        from .core.task_types import DeadlineTask

        deadline_tasks = [t for t in tasks if isinstance(t, DeadlineTask)]
        other_tasks    = [t for t in tasks if not isinstance(t, DeadlineTask)]

        sorted_deadlines = sorted(deadline_tasks, key=lambda t: t.due_date)
        return sorted_deadlines + other_tasks


class CompositeSort(SortStrategy):
    """
    Apply multiple sort strategies in sequence (primary, secondary, etc.).

    The last strategy in the list is the primary sort.
    Python's sort is stable — earlier strategies act as tiebreakers.

    Example:
        CompositeSort([SortByTitle(), SortByPriority()])
        # Sorts by priority first; within same priority, by title.
    """

    def __init__(self, strategies: list[SortStrategy]) -> None:
        self._strategies = strategies

    def sort(self, tasks: list[Task]) -> list[Task]:
        result = list(tasks)
        # Apply in reverse — last strategy is the primary sort
        for strategy in reversed(self._strategies):
            result = strategy.sort(result)
        return result
```

---

### Using Strategies in the Filter Pipeline

Update `TaskFilter.sort_by()` to accept a `SortStrategy` directly:

```python
# In taskflow/filters.py — add strategy support

def sort_with(self, strategy: "SortStrategy") -> "TaskFilter":
    """
    Sort using a Strategy object.

    Args:
        strategy (SortStrategy): Any SortStrategy implementation.

    Returns:
        TaskFilter: self for chaining.
    """
    from .strategies import SortStrategy
    self._tasks = strategy.sort(self._tasks)
    return self

# Usage:
from taskflow.strategies import SortByPriority, SortByDueDate, CompositeSort

results = (
    TaskFilter(tasks)
    .pending()
    .sort_with(CompositeSort([SortByPriority(), SortByDueDate()]))
    .limit(5)
    .get()
)
```

---

### Testing Observer and Strategy

```python
# tests/test_events.py
import pytest
from taskflow.events import EventBus, Events
from taskflow.core.task import Task


@pytest.fixture
def bus() -> EventBus:
    """Fresh EventBus for each test."""
    b = EventBus()
    yield b
    b.clear()


class TestEventBus:

    def test_emit_calls_handler(self, bus):
        received = []
        bus.subscribe("test.event", lambda x: received.append(x))
        bus.emit("test.event", "payload")
        assert received == ["payload"]

    def test_multiple_handlers_all_called(self, bus):
        called = []
        bus.subscribe("test.event", lambda: called.append("a"))
        bus.subscribe("test.event", lambda: called.append("b"))
        bus.emit("test.event")
        assert called == ["a", "b"]

    def test_emit_no_subscribers_does_not_raise(self, bus):
        bus.emit("no.subscribers.event")   # should not raise

    def test_handler_error_does_not_stop_others(self, bus):
        called = []

        def bad_handler():
            raise RuntimeError("Broken handler")

        def good_handler():
            called.append("good")

        bus.subscribe("test.event", bad_handler)
        bus.subscribe("test.event", good_handler)
        bus.emit("test.event")
        assert "good" in called   # good handler still ran

    def test_decorator_registration(self, bus):
        @bus.on("task.added")
        def handler(task):
            pass
        assert handler in bus.handlers_for("task.added")

    def test_unsubscribe(self, bus):
        received = []
        handler = lambda x: received.append(x)
        bus.subscribe("test.event", handler)
        bus.unsubscribe("test.event", handler)
        bus.emit("test.event", "payload")
        assert received == []

    def test_clear_specific_event(self, bus):
        bus.subscribe("event.a", lambda: None)
        bus.subscribe("event.b", lambda: None)
        bus.clear("event.a")
        assert bus.handlers_for("event.a") == []
        assert len(bus.handlers_for("event.b")) == 1

    def test_clear_all(self, bus):
        bus.subscribe("event.a", lambda: None)
        bus.subscribe("event.b", lambda: None)
        bus.clear()
        assert bus.handlers_for("event.a") == []
        assert bus.handlers_for("event.b") == []


# tests/test_strategies.py
import pytest
from taskflow.core.task import Task
from taskflow.core.task_types import DeadlineTask
from taskflow.strategies import (
    SortByPriority, SortByTitle, SortByAge,
    SortByDueDate, CompositeSort,
)


@pytest.fixture
def sample_tasks():
    return [
        Task("Zebra task", "low",  "personal"),
        Task("Apple task", "high", "work"),
        Task("Mango task", "medium", "work"),
    ]


class TestSortByPriority:

    def test_high_comes_first(self, sample_tasks):
        sorter = SortByPriority()
        result = sorter.sort(sample_tasks)
        assert result[0].priority == "high"
        assert result[-1].priority == "low"

    def test_does_not_mutate_original(self, sample_tasks):
        original_order = [t.title for t in sample_tasks]
        SortByPriority().sort(sample_tasks)
        assert [t.title for t in sample_tasks] == original_order

    def test_callable_interface(self, sample_tasks):
        sorter = SortByPriority()
        result = sorter(sample_tasks)   # __call__
        assert result[0].priority == "high"


class TestSortByTitle:

    def test_alphabetical_order(self, sample_tasks):
        sorter = SortByTitle()
        result = sorter.sort(sample_tasks)
        titles = [t.title for t in result]
        assert titles == sorted(titles, key=str.lower)

    def test_reverse(self, sample_tasks):
        sorter = SortByTitle(reverse=True)
        result = sorter.sort(sample_tasks)
        titles = [t.title for t in result]
        assert titles == sorted(titles, key=str.lower, reverse=True)


class TestSortByDueDate:

    def test_deadline_tasks_before_standard(self):
        standard = Task("Standard", "low", "work")
        deadline = DeadlineTask("Due soon", "work", due_date="2099-06-01")
        tasks    = [standard, deadline]
        sorter   = SortByDueDate()
        result   = sorter.sort(tasks)
        assert isinstance(result[0], DeadlineTask)

    def test_earliest_due_date_first(self):
        d1 = DeadlineTask("Later",  "work", due_date="2099-12-31")
        d2 = DeadlineTask("Sooner", "work", due_date="2099-06-01")
        result = SortByDueDate().sort([d1, d2])
        assert result[0].due_date == "2099-06-01"


class TestCompositeSort:

    def test_priority_then_title(self, sample_tasks):
        # Add two high-priority tasks to test secondary sort
        from taskflow.core.task import Task
        Task.reset_counter()
        tasks = [
            Task("Zebra high",  "high",   "work"),
            Task("Apple high",  "high",   "work"),
            Task("Only medium", "medium", "work"),
        ]
        sorter = CompositeSort([SortByTitle(), SortByPriority()])
        result = sorter.sort(tasks)

        # All high-priority first
        assert result[0].priority == "high"
        assert result[1].priority == "high"
        # Within high-priority, alphabetical
        assert result[0].title < result[1].title
```

---

## Exercises

**Exercise 1 — `task.overdue` event.**
Add `Events.TASK_OVERDUE = "task.overdue"` to the `Events` class. In `main.py`, register a startup check that emits this event for every overdue task at app launch. Write a handler that prints a warning for each overdue task.

**Exercise 2 — Strategy for filtering.**
Create a `FilterStrategy` ABC and two implementations: `PendingFilter` and `OverdueFilter`. Add `filter_with(strategy)` to `TaskFilter` alongside `sort_with()`. Test both.

**Exercise 3 — Factory registration test.**
Write a test that registers a custom task type with `TaskFactory`:

```python
class AITask(Task):
    def to_dict(self):
        d = super().to_dict()
        d["type"] = "ai"
        return d

TaskFactory.register("ai", AITask)
data = {"id": 1, "title": "AI Task", "priority": "high",
        "category": "work", "status": "pending", "done": False,
        "created_at": "2025-05-19 14:00", "type": "ai"}
task = TaskFactory.create_from_dict(data)
assert isinstance(task, AITask)
```

**Exercise 4 — Observer for limit warning.**
Subscribe to `Events.LIMIT_REACHED`. When emitted, the handler should check what percentage of the limit is used and print a progressively stronger warning:
- 80%: "⚠ Getting close to your task limit"
- 90%: "🟠 Almost at your task limit"
- 100%: "🔴 Task limit reached — upgrade to premium"

**Exercise 5 — Callable strategy with `functools.partial`.**
Create a `sort_by_field(field_name, reverse=False)` function that returns a `SortStrategy`-compatible callable using `functools.partial`. Use it in `TaskFilter.sort_by()` as an alternative to the string-keyed sort.

**Exercise 6 (stretch) — Chain of Responsibility.**
Implement the Chain of Responsibility pattern for input validation. Each validator in the chain either passes the task data along or raises `ValidationError`:

```python
class Validator(ABC):
    def __init__(self) -> None:
        self._next: Validator | None = None

    def set_next(self, validator: "Validator") -> "Validator":
        self._next = validator
        return validator

    @abstractmethod
    def validate(self, data: dict) -> dict: ...

class TitleValidator(Validator):
    def validate(self, data):
        if not data.get("title", "").strip():
            raise ValidationError("Title empty", field="title")
        return self._next.validate(data) if self._next else data

class PriorityValidator(Validator):
    def validate(self, data):
        if data.get("priority") not in VALID_PRIORITIES:
            raise ValidationError("Bad priority", field="priority")
        return self._next.validate(data) if self._next else data

# Usage
chain = TitleValidator()
chain.set_next(PriorityValidator())
chain.validate({"title": "Test", "priority": "high"})
```

---

## Checkpoint

Before moving to Day 30:

- [ ] `TaskFactory` class with `register()` and `create_from_dict()` is in `task_factory.py`
- [ ] `taskflow/events.py` has `EventBus` and the `Events` constants class
- [ ] `event_bus` singleton is created at module level
- [ ] `services.py` emits `TASK_ADDED` and `TASK_DONE` events
- [ ] `main.py` registers built-in event handlers at startup
- [ ] `taskflow/strategies.py` has 6 strategy classes + `CompositeSort`
- [ ] `TaskFilter.sort_with()` accepts strategy objects
- [ ] `tests/test_events.py` and `tests/test_strategies.py` all pass

---

## Common Errors on Day 29

**Global `event_bus` state leaking between tests:**

```python
# In conftest.py — clear the event bus between tests
@pytest.fixture(autouse=True)
def clear_event_bus():
    from taskflow.events import event_bus
    event_bus.clear()
    yield
    event_bus.clear()
```

**Strategy mutating the input list:**

```python
# ❌ Sorts in place — mutates the original
class BadSort(SortStrategy):
    def sort(self, tasks):
        tasks.sort(key=lambda t: t.title)  # mutates!
        return tasks

# ✅ Returns a new sorted list
class GoodSort(SortStrategy):
    def sort(self, tasks):
        return sorted(tasks, key=lambda t: t.title)
```

**Observer tight coupling — importing from `events.py` in `core/`:**

`core/task.py` should never import from `events.py`. Keep the event bus in `services.py` and `commands.py` only. The domain model should be pure — no dependencies on the event infrastructure.

---

## What's Coming

On **Day 30** we introduce async programming — `asyncio`, `async/await`, coroutines, and `asyncio.gather()`. This allows TaskFlow AI to fetch weather data and check for overdue tasks concurrently on startup, cutting cold start time in half. It also prepares the architecture for the async FastAPI server in Phase 3.
