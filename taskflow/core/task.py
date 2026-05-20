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

    def __init__(
        self,
        title: str,
        priority: str = "medium",
        category: str = "general",
        task_id: int | None = None,
    ):
        """
        Create a new Task instance.

        Args:
            title    (str)       : Task title. Must not be empty.
            priority (str)       : Task priority. Defaults to 'medium'.
            category (str)       : Task category. Defaults to 'general'.
            task_id  (int | None): Explicit ID (used when loading from storage).
                                   If None, auto-increments the class counter.
        """
        # ── Validate ──────────────────────────────────────
        title = title.strip()
        priority = priority.strip().lower()
        category = category.strip().lower()

        if not title:
            raise ValidationError("Title cannot be empty", field="title", value=title)
        if len(title) > 200:
            raise ValidationError(
                "Title too long (max 200 chars)", field="title", value=len(title)
            )
        if priority not in VALID_PRIORITIES:
            raise ValidationError(f"Invalid priority", field="priority", value=priority)
        if category not in VALID_CATEGORIES:
            raise ValidationError(f"Invalid category", field="category", value=category)

        # ── Assign ID ─────────────────────────────────────
        if task_id is not None:
            self.id = task_id
            # Keep counter ahead of any explicitly assigned ID
            Task._id_counter = max(Task._id_counter, task_id)
        else:
            Task._id_counter += 1
            self.id = Task._id_counter

        # ── Set Attributes ────────────────────────────────
        self.title = title
        self._priority = priority
        self._category = category
        self.status = "pending"
        self.done = False
        self.created_at = datetime.datetime.now().strftime(DATE_FMT)

    # ── Properties ────────────────────────────────────────

    @property
    def priority(self) -> str:
        return self._priority

    @priority.setter
    def priority(self, value: str) -> None:
        value = value.strip().lower()
        if value not in VALID_PRIORITIES:
            raise ValidationError("Invalid priority", field="priority", value=value)
        self._priority = value

    @property
    def category(self) -> str:
        return self._category

    @category.setter
    def category(self, value: str) -> None:
        value = value.strip().lower()
        if value not in VALID_CATEGORIES:
            raise ValidationError("Invalid category", field="category", value=value)
        self._category = value

    @property
    def priority_score(self) -> int:
        """Numeric priority for sorting. High=3, Medium=2, Low=1."""
        return {"high": 3, "medium": 2, "low": 1}.get(self._priority, 0)

    # ── Instance Methods ──────────────────────────────────

    def mark_done(self) -> "Task":
        """
        Mark the task as completed.

        Returns:
            Task: self — allows method chaining.
        """
        self.done = True
        self.status = "done"
        return self

    def mark_pending(self) -> "Task":
        """Re-open a completed task."""
        self.done = False
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
            delta = datetime.datetime.now() - created
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
            raise ValidationError(
                "Title cannot be empty", field="title", value=new_title
            )
        self.title = new_title
        return self

    # ── Serialization ─────────────────────────────────────

    def to_dict(self) -> dict:
        """
        Convert the Task to a dictionary for JSON serialization.

        Returns:
            dict: All task fields as a plain dictionary.
        """
        return {
            "id": self.id,
            "title": self.title,
            "priority": self._priority,
            "category": self._category,
            "status": self.status,
            "done": self.done,
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
        task = cls.__new__(cls)
        task.id = data["id"]
        task.title = data["title"]
        task._priority = data.get("priority", "medium")
        task._category = data.get("category", "general")
        task.status = data.get("status", "pending")
        task.done = data.get("done", False)
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

    # ── Dunder Methods ────────────────────────────────────

    def __str__(self) -> str:
        status = "✓" if self.done else "○"
        return (
            f"{status} Task #{self.id} "
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
        """Enable sorting by priority score (high first), then by ID."""
        if not isinstance(other, Task):
            return NotImplemented
        if self.priority_score != other.priority_score:
            return (
                self.priority_score > other.priority_score
            )  # higher score = comes first
        return self.id < other.id

    def __hash__(self) -> int:
        """Make Task hashable so it can be used in sets and as dict keys."""
        return hash(self.id)
