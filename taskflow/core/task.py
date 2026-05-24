# Task base class. Introduced Day 12.
from __future__ import annotations
import datetime
from ..config import VALID_PRIORITIES, VALID_CATEGORIES, DATE_FMT
from ..errors import ValidationError

__all__ = ["Task"]


class Task:
    """Represents a single task in TaskFlow AI."""

    _id_counter: int = 0

    def __init__(self, title: str, priority: str = "medium",
                 category: str = "general", task_id: int | None = None) -> None:
        title    = title.strip()
        priority = priority.strip().lower()
        category = category.strip().lower()

        if not title:
            raise ValidationError("Title cannot be empty.", field="title", value=title)
        if len(title) > 200:
            raise ValidationError("Title too long (max 200 chars).", field="title", value=len(title))
        if priority not in VALID_PRIORITIES:
            raise ValidationError(f"Invalid priority '{priority}'.", field="priority", value=priority)
        if category not in VALID_CATEGORIES and category != "general":
            raise ValidationError(f"Invalid category '{category}'.", field="category", value=category)

        if task_id is not None:
            self.id = task_id
            Task._id_counter = max(Task._id_counter, task_id)
        else:
            Task._id_counter += 1
            self.id = Task._id_counter

        self.title      = title
        self._priority  = priority
        self._category  = category
        self.status     = "pending"
        self.done       = False
        self.created_at = datetime.datetime.now().strftime(DATE_FMT)

    @property
    def priority(self) -> str:
        return self._priority

    @priority.setter
    def priority(self, value: str) -> None:
        value = value.strip().lower()
        if value not in VALID_PRIORITIES:
            raise ValidationError(f"Invalid priority '{value}'.", field="priority", value=value)
        self._priority = value

    @property
    def category(self) -> str:
        return self._category

    @category.setter
    def category(self, value: str) -> None:
        value = value.strip().lower()
        if value not in VALID_CATEGORIES:
            raise ValidationError(f"Invalid category '{value}'.", field="category", value=value)
        self._category = value

    @property
    def priority_score(self) -> int:
        return {"high": 3, "medium": 2, "low": 1}.get(self._priority, 0)

    def mark_done(self) -> "Task":
        self.done   = True
        self.status = "done"
        return self

    def mark_pending(self) -> "Task":
        self.done   = False
        self.status = "pending"
        return self

    def rename(self, new_title: str) -> "Task":
        new_title = new_title.strip()
        if not new_title:
            raise ValidationError("Title cannot be empty.", field="title", value=new_title)
        self.title = new_title
        return self

    def is_pending(self) -> bool:
        return not self.done

    def matches(self, keyword: str) -> bool:
        return keyword.strip().lower() in self.title.lower()

    def age_days(self) -> int:
        try:
            created = datetime.datetime.strptime(self.created_at, DATE_FMT)
            return (datetime.datetime.now() - created).days
        except ValueError:
            return 0

    def is_overdue(self, threshold_days: int = 7) -> bool:
        return self.is_pending() and self.age_days() >= threshold_days

    def to_dict(self) -> dict:
        return {
            "id": self.id, "title": self.title,
            "priority": self._priority, "category": self._category,
            "status": self.status, "done": self.done,
            "created_at": self.created_at, "type": "standard",
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        task            = cls.__new__(cls)
        task.id         = data["id"]
        task.title      = data["title"]
        task._priority  = data.get("priority", "medium")
        task._category  = data.get("category", "general")
        task.status     = data.get("status", "pending")
        task.done       = data.get("done", False)
        task.created_at = data.get("created_at", "")
        Task._id_counter = max(Task._id_counter, task.id)
        return task

    @staticmethod
    def priority_to_score(priority: str) -> int:
        return {"high": 3, "medium": 2, "low": 1}.get(priority.lower(), 0)

    @classmethod
    def reset_counter(cls) -> None:
        cls._id_counter = 0

    def __str__(self) -> str:
        mark = "✓" if self.done else "○"
        return f"{mark} Task #{self.id} [{self._priority.upper()}] {self.title} ({self._category})"

    def __repr__(self) -> str:
        return f"Task(id={self.id!r}, title={self.title!r}, priority={self._priority!r}, done={self.done!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Task):
            return NotImplemented
        return self.id == other.id

    def __lt__(self, other: "Task") -> bool:
        if not isinstance(other, Task):
            return NotImplemented
        if self.priority_score != other.priority_score:
            return self.priority_score > other.priority_score
        return self.id < other.id

    def __hash__(self) -> int:
        return hash(self.id)
