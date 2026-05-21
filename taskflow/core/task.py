# taskflow/core/task.py
# TaskFlow AI — Task base class.
# Replaces plain task dictionaries introduced on Day 05.
#
# Version history:
#   Day 05 — tasks stored as plain dicts
#   Day 12 — Task class introduced; replaces dicts throughout

import datetime
from ..config import VALID_PRIORITIES, VALID_CATEGORIES, DATE_FMT
from ..errors import ValidationError

__all__ = ["Task"]


class Task:
    """
    Represents a single task in TaskFlow AI.

    Attributes:
        id         (int)  : Unique identifier, auto-assigned via class counter.
        title      (str)  : Task description (1–200 characters).
        priority   (str)  : One of 'high', 'medium', 'low'. Validated via property.
        category   (str)  : One of VALID_CATEGORIES. Validated via property.
        status     (str)  : 'pending' or 'done'.
        done       (bool) : True when the task is completed.
        created_at (str)  : Timestamp string in DATE_FMT format.

    Class Attributes:
        _id_counter (int): Auto-incrementing ID shared across all instances.
    """

    _id_counter: int = 0

    # ── Constructor ───────────────────────────────────────

    def __init__(
        self,
        title: str,
        priority: str = "medium",
        category: str = "general",
        task_id: int | None = None,
    ):
        """
        Create a new Task.

        Args:
            title    (str)       : Task title. Must not be empty.
            priority (str)       : Task priority. Defaults to 'medium'.
            category (str)       : Task category. Defaults to 'general'.
            task_id  (int|None)  : Explicit ID (used when loading from storage).
                                   Auto-increments class counter if None.

        Raises:
            ValidationError: If title is empty/too long, priority or
                             category is invalid.
        """
        # Normalise
        title = title.strip()
        priority = priority.strip().lower()
        category = category.strip().lower()

        # Validate
        if not title:
            raise ValidationError("Title cannot be empty.", field="title", value=title)
        if len(title) > 200:
            raise ValidationError(
                "Title too long (max 200 chars).",
                field="title",
                value=len(title),
            )
        if priority not in VALID_PRIORITIES:
            raise ValidationError(
                f"Invalid priority '{priority}'. "
                f"Choose from: {', '.join(sorted(VALID_PRIORITIES))}",
                field="priority",
                value=priority,
            )
        if category not in VALID_CATEGORIES and category != "general":
            raise ValidationError(
                f"Invalid category '{category}'. "
                f"Choose from: {', '.join(sorted(VALID_CATEGORIES))}",
                field="category",
                value=category,
            )

        # Assign ID
        if task_id is not None:
            self.id = task_id
            Task._id_counter = max(Task._id_counter, task_id)
        else:
            Task._id_counter += 1
            self.id = Task._id_counter

        # Set attributes
        self.title = title
        self._priority = priority
        self._category = category
        self.status = "pending"
        self.done = False
        self.created_at = datetime.datetime.now().strftime(DATE_FMT)

    # ── Properties ────────────────────────────────────────

    @property
    def priority(self) -> str:
        """Current priority string."""
        return self._priority

    @priority.setter
    def priority(self, value: str) -> None:
        """Set priority with validation."""
        value = value.strip().lower()
        if value not in VALID_PRIORITIES:
            raise ValidationError(
                f"Invalid priority '{value}'.",
                field="priority",
                value=value,
            )
        self._priority = value

    @property
    def category(self) -> str:
        """Current category string."""
        return self._category

    @category.setter
    def category(self, value: str) -> None:
        """Set category with validation."""
        value = value.strip().lower()
        if value not in VALID_CATEGORIES:
            raise ValidationError(
                f"Invalid category '{value}'.",
                field="category",
                value=value,
            )
        self._category = value

    @property
    def priority_score(self) -> int:
        """Numeric score for sorting: high=3, medium=2, low=1."""
        return {"high": 3, "medium": 2, "low": 1}.get(self._priority, 0)

    # ── Instance Methods ──────────────────────────────────

    def mark_done(self) -> "Task":
        """
        Mark this task as completed.

        Returns:
            Task: self — enables method chaining.
        """
        self.done = True
        self.status = "done"
        return self

    def mark_pending(self) -> "Task":
        """Re-open a completed task back to pending."""
        self.done = False
        self.status = "pending"
        return self

    def rename(self, new_title: str) -> "Task":
        """
        Update the task title with validation.

        Args:
            new_title (str): The replacement title.

        Returns:
            Task: self — enables method chaining.

        Raises:
            ValidationError: If new_title is empty.
        """
        new_title = new_title.strip()
        if not new_title:
            raise ValidationError(
                "Title cannot be empty.", field="title", value=new_title
            )
        self.title = new_title
        return self

    def is_pending(self) -> bool:
        """Return True if the task has not been completed."""
        return not self.done

    def matches(self, keyword: str) -> bool:
        """Return True if keyword appears in the title (case-insensitive)."""
        return keyword.strip().lower() in self.title.lower()

    def age_days(self) -> int:
        """Return how many days ago this task was created."""
        try:
            created = datetime.datetime.strptime(self.created_at, DATE_FMT)
            return (datetime.datetime.now() - created).days
        except ValueError:
            return 0

    def is_overdue(self, threshold_days: int = 7) -> bool:
        """
        Return True if this task is pending and older than threshold_days.

        Args:
            threshold_days (int): Days after which a pending task is overdue.
        """
        return self.is_pending() and self.age_days() >= threshold_days

    # ── Serialisation ─────────────────────────────────────

    def to_dict(self) -> dict:
        """
        Serialise the Task to a plain dictionary for JSON storage.

        Returns:
            dict: All task fields as JSON-serialisable types.
        """
        return {
            "id": self.id,
            "title": self.title,
            "priority": self._priority,
            "category": self._category,
            "status": self.status,
            "done": self.done,
            "created_at": self.created_at,
            "type": "standard",
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """
        Create a Task from a stored dictionary.

        Bypasses __init__ validation so that previously stored data
        (which was already validated on creation) can be restored as-is.

        Args:
            data (dict): A task dictionary from JSON storage.

        Returns:
            Task: A fully populated Task instance.
        """
        task = cls.__new__(cls)
        task.id = data["id"]
        task.title = data["title"]
        task._priority = data.get("priority", "medium")
        task._category = data.get("category", "general")
        task.status = data.get("status", "pending")
        task.done = data.get("done", False)
        task.created_at = data.get("created_at", "")
        # Keep class counter ahead of any loaded IDs
        Task._id_counter = max(Task._id_counter, task.id)
        return task

    # ── Class / Static Methods ────────────────────────────

    @staticmethod
    def priority_to_score(priority: str) -> int:
        """Convert a priority string to a numeric sort score."""
        return {"high": 3, "medium": 2, "low": 1}.get(priority.lower(), 0)

    @classmethod
    def reset_counter(cls) -> None:
        """Reset the ID counter to 0. Use ONLY in tests."""
        cls._id_counter = 0

    # ── Dunder Methods ────────────────────────────────────

    def __str__(self) -> str:
        mark = "✓" if self.done else "○"
        return (
            f"{mark} Task #{self.id} "
            f"[{self._priority.upper()}] "
            f"{self.title} "
            f"({self._category})"
        )

    def __repr__(self) -> str:
        return (
            f"Task(id={self.id!r}, title={self.title!r}, "
            f"priority={self._priority!r}, "
            f"category={self._category!r}, "
            f"done={self.done!r})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Task):
            return NotImplemented
        return self.id == other.id

    def __lt__(self, other: "Task") -> bool:
        """Sort by priority score descending, then by ID ascending."""
        if not isinstance(other, Task):
            return NotImplemented
        if self.priority_score != other.priority_score:
            return self.priority_score > other.priority_score
        return self.id < other.id

    def __hash__(self) -> int:
        """Make Task hashable — enables use in sets and as dict keys."""
        return hash(self.id)
