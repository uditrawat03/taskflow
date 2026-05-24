# tests/test_parser.py — Tests for taskflow/parser.py
import pytest
from taskflow.parser import parse_task_input, parse_and_create, ParseResult
from taskflow.core.task        import Task
from taskflow.core.task_types  import UrgentTask, RecurringTask, DeadlineTask
from taskflow.errors           import ValidationError


class TestParseTaskInput:
    def test_simple_title(self):
        r = parse_task_input("Review PR")
        assert r.title     == "Review PR"
        assert r.task_type == "standard"
        assert r.priority  == "medium"

    def test_priority_token(self):
        r = parse_task_input("Review PR #high")
        assert r.priority == "high"
        assert r.title    == "Review PR"

    def test_category_token(self):
        r = parse_task_input("Review PR @work")
        assert r.category == "work"
        assert r.title    == "Review PR"

    def test_due_date_token(self):
        r = parse_task_input("Submit report !2099-12-31")
        assert r.due_date  == "2099-12-31"
        assert r.task_type == "deadline"

    def test_urgent_prefix(self):
        r = parse_task_input("!! Server down")
        assert r.is_urgent  is True
        assert r.priority   == "high"
        assert r.task_type  == "urgent"
        assert r.title      == "Server down"

    def test_recurring_prefix_daily(self):
        r = parse_task_input("~daily Standup @work")
        assert r.recurrence == "daily"
        assert r.task_type  == "recurring"
        assert r.title      == "Standup"

    @pytest.mark.parametrize("recurrence", ["daily", "weekly", "monthly"])
    def test_all_recurrences(self, recurrence):
        r = parse_task_input(f"~{recurrence} Standup")
        assert r.recurrence == recurrence

    def test_multiple_tokens(self):
        r = parse_task_input("Submit report #high @work !2099-12-31")
        assert r.title     == "Submit report"
        assert r.priority  == "high"
        assert r.category  == "work"
        assert r.due_date  == "2099-12-31"
        assert r.task_type == "deadline"

    def test_empty_input_raises(self):
        with pytest.raises(ValidationError):
            parse_task_input("")

    def test_whitespace_only_raises(self):
        with pytest.raises(ValidationError):
            parse_task_input("   ")

    def test_invalid_category_raises(self):
        with pytest.raises(ValidationError):
            parse_task_input("Task @nonexistent_category")

    def test_invalid_date_raises(self):
        with pytest.raises(ValidationError):
            parse_task_input("Task !31-12-2099")

    def test_tokens_only_no_title_raises(self):
        with pytest.raises(ValidationError):
            parse_task_input("#high @work")

    def test_priority_case_insensitive(self):
        r = parse_task_input("Task #HIGH")
        assert r.priority == "high"

    def test_repr(self):
        r = parse_task_input("Test task #high @work")
        assert "ParseResult" in repr(r)
        assert "Test task" in repr(r)


class TestParseAndCreate:
    def test_creates_urgent_task(self):
        task = parse_and_create("!! Server down @work")
        assert isinstance(task, UrgentTask)
        assert task.title    == "Server down"
        assert task.category == "work"

    def test_creates_recurring_task(self):
        task = parse_and_create("~daily Standup @work")
        assert isinstance(task, RecurringTask)
        assert task.recurrence == "daily"

    def test_creates_deadline_task(self):
        task = parse_and_create("Submit report !2099-12-31")
        assert isinstance(task, DeadlineTask)
        assert task.due_date == "2099-12-31"

    def test_creates_standard_task(self):
        task = parse_and_create("Review PR #high @work")
        assert isinstance(task, Task)
        assert not isinstance(task, (UrgentTask, RecurringTask, DeadlineTask))
        assert task.priority == "high"

    def test_full_shorthand_roundtrip(self):
        task = parse_and_create("Deploy app #high @work !2099-06-01")
        assert task.title    == "Deploy app"
        assert task.priority == "high"
        assert task.category == "work"
        assert isinstance(task, DeadlineTask)
        assert task.due_date == "2099-06-01"

    def test_urgent_forces_high_priority(self):
        task = parse_and_create("!! Critical bug @work")
        assert task.priority == "high"
