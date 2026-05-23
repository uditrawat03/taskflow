# tests/test_parser.py
import pytest
from taskflow.parser import parse_task_input, parse_and_create, ParseResult
from taskflow.core.task_types import UrgentTask, RecurringTask, DeadlineTask
from taskflow.core.task import Task
from taskflow.errors import ValidationError


class TestParseTaskInput:
    def test_simple_title(self):
        result = parse_task_input("Review PR")
        assert result.title == "Review PR"
        assert result.task_type == "standard"

    def test_priority_token(self):
        result = parse_task_input("Review PR #high")
        assert result.priority == "high"
        assert result.title == "Review PR"

    def test_category_token(self):
        result = parse_task_input("Review PR @work")
        assert result.category == "work"
        assert result.title == "Review PR"

    def test_due_date_token(self):
        result = parse_task_input("Submit report !2099-12-31")
        assert result.due_date == "2099-12-31"
        assert result.task_type == "deadline"

    def test_urgent_prefix(self):
        result = parse_task_input("!! Server down")
        assert result.is_urgent is True
        assert result.priority == "high"
        assert result.task_type == "urgent"
        assert result.title == "Server down"

    def test_recurring_prefix(self):
        result = parse_task_input("~daily Standup @work")
        assert result.recurrence == "daily"
        assert result.task_type == "recurring"
        assert result.title == "Standup"

    def test_multiple_tokens(self):
        result = parse_task_input("Submit report #high @work !2099-12-31")
        assert result.title == "Submit report"
        assert result.priority == "high"
        assert result.category == "work"
        assert result.due_date == "2099-12-31"
        assert result.task_type == "deadline"

    def test_empty_input_raises(self):
        with pytest.raises(ValidationError):
            parse_task_input("")

    def test_whitespace_only_raises(self):
        with pytest.raises(ValidationError):
            parse_task_input("   ")

    def test_invalid_category_raises(self):
        with pytest.raises(ValidationError):
            parse_task_input("Task @invalid_category")

    def test_invalid_date_raises(self):
        with pytest.raises(ValidationError):
            parse_task_input("Task !31-12-2099")

    @pytest.mark.parametrize("recurrence", ["daily", "weekly", "monthly"])
    def test_all_recurrences(self, recurrence):
        result = parse_task_input(f"~{recurrence} Standup")
        assert result.recurrence == recurrence


class TestParseAndCreate:
    def test_creates_urgent_task(self):
        task = parse_and_create("!! Server down @work")
        assert isinstance(task, UrgentTask)

    def test_creates_recurring_task(self):
        task = parse_and_create("~daily Standup @work")
        assert isinstance(task, RecurringTask)

    def test_creates_deadline_task(self):
        task = parse_and_create("Submit report !2099-12-31")
        assert isinstance(task, DeadlineTask)

    def test_creates_standard_task(self):
        task = parse_and_create("Review PR #high @work")
        assert isinstance(task, Task)
        assert not isinstance(task, (UrgentTask, RecurringTask, DeadlineTask))
