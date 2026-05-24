# tests/test_task_types.py — Tests for UrgentTask, RecurringTask, DeadlineTask
import pytest
from taskflow.core.task_types import UrgentTask, RecurringTask, DeadlineTask
from taskflow.errors import ValidationError


class TestUrgentTask:
    def test_priority_always_high(self):
        assert UrgentTask("Server down", "work").priority == "high"

    def test_cannot_change_priority(self):
        task = UrgentTask("Server down", "work")
        with pytest.raises(ValidationError):
            task.priority = "low"

    def test_str_has_emoji(self):
        assert "🚨" in str(UrgentTask("Server down", "work"))

    def test_to_dict_type(self):
        assert UrgentTask("Server down", "work").to_dict()["type"] == "urgent"

    def test_from_dict_roundtrip(self):
        task = UrgentTask("Server down", "work")
        restored = UrgentTask.from_dict(task.to_dict())
        assert restored.title    == "Server down"
        assert restored.priority == "high"

    def test_escalation_note_present(self):
        task = UrgentTask("Server down", "work")
        assert len(task.escalation_note) > 0


class TestRecurringTask:
    @pytest.mark.parametrize("recurrence", ["daily", "weekly", "monthly"])
    def test_valid_recurrences(self, recurrence):
        task = RecurringTask("Standup", "medium", "work", recurrence)
        assert task.recurrence == recurrence

    def test_invalid_recurrence_raises(self):
        with pytest.raises(ValidationError):
            RecurringTask("Standup", "medium", "work", "hourly")

    def test_mark_done_resets_to_pending(self):
        task = RecurringTask("Standup", "medium", "work", "daily")
        task.mark_done()
        assert task.done             is False
        assert task.status           == "pending"
        assert task.completion_count == 1

    def test_completion_count_increments(self):
        task = RecurringTask("Standup", "medium", "work", "daily")
        task.mark_done()
        task.mark_done()
        task.mark_done()
        assert task.completion_count == 3

    def test_to_dict_includes_recurrence(self):
        d = RecurringTask("Standup", "medium", "work", "weekly").to_dict()
        assert d["type"]       == "recurring"
        assert d["recurrence"] == "weekly"

    def test_from_dict_roundtrip(self):
        task = RecurringTask("Standup", "medium", "work", "monthly")
        task.mark_done()
        restored = RecurringTask.from_dict(task.to_dict())
        assert restored.recurrence       == "monthly"
        assert restored.completion_count == 1

    def test_recurrence_label(self):
        task = RecurringTask("Standup", "medium", "work", "daily")
        assert "Daily" in task.recurrence_label


class TestDeadlineTask:
    def test_valid_due_date(self):
        task = DeadlineTask("Report", "work", due_date="2099-12-31")
        assert task.due_date == "2099-12-31"

    def test_missing_due_date_raises(self):
        with pytest.raises(ValidationError):
            DeadlineTask("Report", "work", due_date="")

    def test_invalid_date_format_raises(self):
        with pytest.raises(ValidationError):
            DeadlineTask("Report", "work", due_date="31-12-2099")

    def test_days_until_due_future(self):
        task = DeadlineTask("Report", "work", due_date="2099-12-31")
        assert task.days_until_due > 0

    def test_days_until_due_past_negative(self):
        task = DeadlineTask("Report", "work", due_date="2020-01-01")
        assert task.days_until_due < 0

    def test_is_overdue_past(self):
        task = DeadlineTask("Report", "work", due_date="2020-01-01")
        assert task.is_overdue() is True

    def test_is_overdue_future(self):
        task = DeadlineTask("Report", "work", due_date="2099-12-31")
        assert task.is_overdue() is False

    def test_is_overdue_false_when_done(self):
        task = DeadlineTask("Report", "work", due_date="2020-01-01")
        task.mark_done()
        assert task.is_overdue() is False

    def test_urgency_label_overdue(self):
        task = DeadlineTask("Report", "work", due_date="2020-01-01")
        assert "OVERDUE" in task.urgency_label

    def test_urgency_label_future(self):
        task = DeadlineTask("Report", "work", due_date="2099-12-31")
        assert "🟢" in task.urgency_label

    def test_to_dict_includes_due_date(self):
        d = DeadlineTask("Report", "work", due_date="2099-12-31").to_dict()
        assert d["type"]     == "deadline"
        assert d["due_date"] == "2099-12-31"

    def test_from_dict_roundtrip(self):
        task = DeadlineTask("Report", "work", due_date="2099-06-15")
        restored = DeadlineTask.from_dict(task.to_dict())
        assert restored.due_date == "2099-06-15"
