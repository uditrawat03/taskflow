# taskflow/core/task_types.py
# TaskFlow AI — Day 13
# Specialised Task subclasses for different task types.

import datetime
from .task import Task
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
                field="priority",
                value=value,
            )
        self._priority = "high"

    @property
    def escalation_note(self) -> str:
        """Return an escalation message if the task has been pending too long."""
        age_hours = self.age_days() * 24
        if self.is_pending() and age_hours >= self.ESCALATION_THRESHOLD_HOURS:
            return f"⚠  URGENT — pending for ~{self.age_days()}d. Escalate immediately."
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


class RecurringTask(Task):
    """
    A task that automatically resets to pending after being marked done.

    Useful for daily standups, weekly reviews, recurring chores.

    Attributes:
        recurrence        (str): How often the task recurs ('daily', 'weekly', 'monthly').
        completion_count  (int): How many times the task has been completed.
    """

    VALID_RECURRENCES = {"daily", "weekly", "monthly"}

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
            priority   (str): Task priority.
            category   (str): Task category.
            recurrence (str): How often it recurs — 'daily', 'weekly', 'monthly'.
        """
        if recurrence not in self.VALID_RECURRENCES:
            raise ValidationError(
                f"Invalid recurrence. Choose from: {self.VALID_RECURRENCES}",
                field="recurrence",
                value=recurrence,
            )
        super().__init__(title, priority=priority, category=category)
        self.recurrence = recurrence
        self.completion_count = 0

    def mark_done(self) -> "RecurringTask":
        """Mark done AND immediately reset to pending — it will recur."""
        self.completion_count += 1
        # Reset to pending after recording the completion
        self.done = False
        self.status = "pending"
        return self

    @property
    def recurrence_label(self) -> str:
        return f"↺ {self.recurrence.title()}"

    def __str__(self) -> str:
        base = super().__str__()
        return f"{base} {self.recurrence_label} (done {self.completion_count}×)"

    def __repr__(self) -> str:
        return (
            f"RecurringTask(id={self.id!r}, title={self.title!r}, "
            f"recurrence={self.recurrence!r}, "
            f"completion_count={self.completion_count!r})"
        )

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


class DeadlineTask(Task):
    """
    A task with an explicit due date and urgency tracking.

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
            category (str): Task category.
            priority (str): Task priority.
            due_date (str): Due date as 'YYYY-MM-DD'. Required.
        """
        if not due_date:
            raise ValidationError(
                "DeadlineTask requires a due_date (YYYY-MM-DD)",
                field="due_date",
                value=due_date,
            )
        try:
            datetime.datetime.strptime(due_date, self.DUE_DATE_FMT)
        except ValueError:
            raise ValidationError(
                f"Invalid due_date format. Expected YYYY-MM-DD.",
                field="due_date",
                value=due_date,
            )
        super().__init__(title, priority=priority, category=category)
        self.due_date = due_date

    @property
    def days_until_due(self) -> int:
        """Return days until due (negative if overdue)."""
        due = datetime.datetime.strptime(self.due_date, self.DUE_DATE_FMT).date()
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
        return (
            f"DeadlineTask(id={self.id!r}, title={self.title!r}, "
            f"due_date={self.due_date!r}, done={self.done!r})"
        )

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
