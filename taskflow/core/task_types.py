import datetime
from .task import Task
from ..config import DATE_FMT
from ..errors import ValidationError

__all__ = ["UrgentTask", "RecurringTask", "DeadlineTask"]


class UrgentTask(Task):
    """
    A task that is always high priority and surfaces escalation guidance.

    Priority is forced to 'high' and cannot be lowered via the setter.
    Displays a 🚨 prefix in __str__ output.
    """

    ESCALATION_THRESHOLD_HOURS = 2

    def __init__(self, title: str, category: str = "work"):
        """
        Create an urgent task. Priority is always 'high'.

        Args:
            title    (str): Task title.
            category (str): Task category. Defaults to 'work'.
        """
        super().__init__(title, priority="high", category=category)

    # Force priority to always be 'high'
    @property
    def priority(self) -> str:
        return "high"

    @priority.setter
    def priority(self, value: str) -> None:
        if value != "high":
            raise ValidationError(
                "UrgentTask priority is always 'high' and cannot be changed.",
                field="priority",
                value=value,
            )
        self._priority = "high"

    @property
    def escalation_note(self) -> str:
        """Return an escalation message appropriate for the task's age."""
        age_hours = self.age_days() * 24
        if self.is_pending() and age_hours >= self.ESCALATION_THRESHOLD_HOURS:
            return f"⚠  URGENT — pending for ~{self.age_days()}d. Escalate immediately."
        return "⚠  URGENT — handle as soon as possible."

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["type"] = "urgent"
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "UrgentTask":
        task = cls.__new__(cls)
        task.id = data["id"]
        task.title = data["title"]
        task._priority = "high"
        task._category = data.get("category", "work")
        task.status = data.get("status", "pending")
        task.done = data.get("done", False)
        task.created_at = data.get("created_at", "")
        Task._id_counter = max(Task._id_counter, task.id)
        return task

    def __str__(self) -> str:
        return f"🚨 {super().__str__()}"

    def __repr__(self) -> str:
        return f"UrgentTask(id={self.id!r}, title={self.title!r}, done={self.done!r})"


# ─ RecurringTask


class RecurringTask(Task):
    """
    A task that automatically resets to pending after being marked done.

    Useful for daily standups, weekly reviews, recurring chores.

    Attributes:
        recurrence       (str): 'daily', 'weekly', or 'monthly'.
        completion_count (int): How many times the task has been completed.
    """

    VALID_RECURRENCES: set[str] = {"daily", "weekly", "monthly"}

    def __init__(
        self,
        title: str,
        priority: str = "medium",
        category: str = "work",
        recurrence: str = "daily",
    ):
        """
        Create a recurring task.

        Args:
            title      (str): Task title.
            priority   (str): Task priority. Defaults to 'medium'.
            category   (str): Task category. Defaults to 'work'.
            recurrence (str): How often it recurs. Defaults to 'daily'.

        Raises:
            ValidationError: If recurrence is not a valid value.
        """
        if recurrence not in self.VALID_RECURRENCES:
            raise ValidationError(
                f"Invalid recurrence '{recurrence}'. "
                f"Choose from: {', '.join(sorted(self.VALID_RECURRENCES))}",
                field="recurrence",
                value=recurrence,
            )
        super().__init__(title, priority=priority, category=category)
        self.recurrence = recurrence
        self.completion_count = 0

    def mark_done(self) -> "RecurringTask":
        """
        Record a completion and immediately reset to pending.

        The task is never permanently 'done' — it resets for the next cycle.

        Returns:
            RecurringTask: self — enables method chaining.
        """
        self.completion_count += 1
        self.done = False
        self.status = "pending"
        return self

    @property
    def recurrence_label(self) -> str:
        """Short display label for the recurrence type."""
        return f"↺ {self.recurrence.title()}"

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["type"] = "recurring"
        d["recurrence"] = self.recurrence
        d["completion_count"] = self.completion_count
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "RecurringTask":
        task = cls.__new__(cls)
        task.id = data["id"]
        task.title = data["title"]
        task._priority = data.get("priority", "medium")
        task._category = data.get("category", "work")
        task.status = data.get("status", "pending")
        task.done = data.get("done", False)
        task.created_at = data.get("created_at", "")
        task.recurrence = data.get("recurrence", "daily")
        task.completion_count = data.get("completion_count", 0)
        Task._id_counter = max(Task._id_counter, task.id)
        return task

    def __str__(self) -> str:
        base = super().__str__()
        return f"{base} {self.recurrence_label} (done {self.completion_count}×)"

    def __repr__(self) -> str:
        return (
            f"RecurringTask(id={self.id!r}, title={self.title!r}, "
            f"recurrence={self.recurrence!r}, "
            f"completion_count={self.completion_count!r})"
        )


# ─ DeadlineTask ─


class DeadlineTask(Task):
    """
    A task with an explicit due date and urgency tracking.

    Overrides is_overdue() to use the due date rather than task age.
    Provides an urgency_label property with colour-coded status.

    Attributes:
        due_date (str): Due date in 'YYYY-MM-DD' format.
    """

    DUE_DATE_FMT = "%Y-%m-%d"

    def __init__(
        self,
        title: str,
        category: str = "work",
        priority: str = "medium",
        due_date: str = "",
    ):
        """
        Create a task with a deadline.

        Args:
            title    (str): Task title.
            category (str): Task category. Defaults to 'work'.
            priority (str): Task priority. Defaults to 'medium'.
            due_date (str): Due date as 'YYYY-MM-DD'. Required.

        Raises:
            ValidationError: If due_date is missing or has wrong format.
        """
        if not due_date:
            raise ValidationError(
                "DeadlineTask requires a due_date in YYYY-MM-DD format.",
                field="due_date",
                value=due_date,
            )
        try:
            datetime.datetime.strptime(due_date, self.DUE_DATE_FMT)
        except ValueError:
            raise ValidationError(
                f"Invalid due_date '{due_date}'. Expected YYYY-MM-DD.",
                field="due_date",
                value=due_date,
            )

        super().__init__(title, priority=priority, category=category)
        self.due_date = due_date

    @property
    def days_until_due(self) -> int:
        """Days until due date. Negative if overdue."""
        due = datetime.datetime.strptime(self.due_date, self.DUE_DATE_FMT).date()
        today = datetime.date.today()
        return (due - today).days

    def is_overdue(self, threshold_days: int = 0) -> bool:
        """
        Return True if the task is pending and past its due date.

        Overrides the base class age-based implementation.
        threshold_days is accepted for LSP compatibility but unused.
        """
        return self.is_pending() and self.days_until_due < 0

    @property
    def urgency_label(self) -> str:
        """Colour-coded urgency label based on days until due."""
        if self.done:
            return "✓ Complete"
        days = self.days_until_due
        if days < 0:
            return f"🔴 OVERDUE by {abs(days)}d"
        if days == 0:
            return "🔴 DUE TODAY"
        if days <= 2:
            return f"🟠 DUE IN {days}d"
        if days <= 7:
            return f"🟡 DUE IN {days}d"
        return f"🟢 DUE IN {days}d"

    def to_dict(self) -> dict:
        d = super().to_dict()
        d["type"] = "deadline"
        d["due_date"] = self.due_date
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "DeadlineTask":
        task = cls.__new__(cls)
        task.id = data["id"]
        task.title = data["title"]
        task._priority = data.get("priority", "medium")
        task._category = data.get("category", "work")
        task.status = data.get("status", "pending")
        task.done = data.get("done", False)
        task.created_at = data.get("created_at", "")
        task.due_date = data.get("due_date", "")
        Task._id_counter = max(Task._id_counter, task.id)
        return task

    def __str__(self) -> str:
        base = super().__str__()
        return f"{base} [{self.urgency_label}]"

    def __repr__(self) -> str:
        return (
            f"DeadlineTask(id={self.id!r}, title={self.title!r}, "
            f"due_date={self.due_date!r}, done={self.done!r})"
        )
