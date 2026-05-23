# tests/test_task.py
import pytest
import datetime
from taskflow.core.task import Task
from taskflow.errors import ValidationError


class TestTaskCreation:
    def test_valid_task(self):
        task = Task("Review PR", "high", "work")
        assert task.title == "Review PR"
        assert task.priority == "high"
        assert task.category == "work"
        assert task.done is False
        assert task.status == "pending"

    def test_empty_title_raises(self):
        with pytest.raises(ValidationError) as exc:
            Task("", "high", "work")
        assert exc.value.field == "title"

    def test_whitespace_only_title_raises(self):
        with pytest.raises(ValidationError):
            Task("   ", "high", "work")

    def test_title_stripped_of_whitespace(self):
        task = Task("  Review PR  ", "high", "work")
        assert task.title == "Review PR"

    def test_title_too_long_raises(self):
        with pytest.raises(ValidationError) as exc:
            Task("x" * 201, "high", "work")
        assert exc.value.field == "title"

    @pytest.mark.parametrize("priority", ["high", "medium", "low"])
    def test_valid_priorities(self, priority):
        task = Task("Test", priority, "work")
        assert task.priority == priority

    @pytest.mark.parametrize("bad_priority", ["urgent", "CRITICAL", "", "3"])
    def test_invalid_priority_raises(self, bad_priority):
        with pytest.raises(ValidationError):
            Task("Test", bad_priority, "work")

    @pytest.mark.parametrize(
        "category", ["work", "personal", "health", "learning", "other"]
    )
    def test_valid_categories(self, category):
        task = Task("Test", "medium", category)
        assert task.category == category

    def test_auto_id_increments(self):
        t1 = Task("Task 1", "low", "work")
        t2 = Task("Task 2", "low", "work")
        assert t2.id == t1.id + 1

    def test_explicit_id(self):
        task = Task("Task", "low", "work", task_id=99)
        assert task.id == 99

    def test_created_at_format(self):
        task = Task("Test", "low", "work")
        # Should parse without error
        datetime.datetime.strptime(task.created_at, "%Y-%m-%d %H:%M")


class TestTaskMethods:
    def test_mark_done(self, one_task):
        task = one_task[0]
        result = task.mark_done()
        assert task.done is True
        assert task.status == "done"
        assert result is task  # method chaining

    def test_mark_pending(self, one_task):
        task = one_task[0]
        task.mark_done()
        task.mark_pending()
        assert task.done is False
        assert task.status == "pending"

    def test_rename(self, one_task):
        task = one_task[0]
        task.rename("New title")
        assert task.title == "New title"

    def test_rename_empty_raises(self, one_task):
        with pytest.raises(ValidationError):
            one_task[0].rename("")

    def test_is_pending_true_when_not_done(self, one_task):
        assert one_task[0].is_pending() is True

    def test_is_pending_false_when_done(self, one_task):
        one_task[0].mark_done()
        assert one_task[0].is_pending() is False

    def test_matches_keyword(self, one_task):
        assert one_task[0].matches("review") is True
        assert one_task[0].matches("REVIEW") is True
        assert one_task[0].matches("grocery") is False

    def test_priority_property_setter_validates(self, one_task):
        with pytest.raises(ValidationError):
            one_task[0].priority = "urgent"

    def test_priority_property_setter_accepts_valid(self, one_task):
        one_task[0].priority = "low"
        assert one_task[0].priority == "low"

    @pytest.mark.parametrize("priority,score", [("high", 3), ("medium", 2), ("low", 1)])
    def test_priority_score(self, priority, score):
        task = Task("Test", priority, "work")
        assert task.priority_score == score


class TestTaskSerialization:
    def test_to_dict_has_required_keys(self, one_task):
        d = one_task[0].to_dict()
        required = {
            "id",
            "title",
            "priority",
            "category",
            "status",
            "done",
            "created_at",
            "type",
        }
        assert required.issubset(d.keys())

    def test_to_dict_done_is_bool(self, one_task):
        d = one_task[0].to_dict()
        assert isinstance(d["done"], bool)

    def test_from_dict_roundtrip(self, one_task):
        original = one_task[0]
        d = original.to_dict()
        restored = Task.from_dict(d)
        assert restored.id == original.id
        assert restored.title == original.title
        assert restored.priority == original.priority
        assert restored.category == original.category
        assert restored.done == original.done

    def test_from_dict_restores_done_state(self):
        d = {
            "id": 1,
            "title": "Done task",
            "priority": "high",
            "category": "work",
            "status": "done",
            "done": True,
            "created_at": "2025-05-19 14:00",
            "type": "standard",
        }
        task = Task.from_dict(d)
        assert task.done is True
        assert task.status == "done"


class TestTaskComparison:
    def test_equal_by_id(self):
        t1 = Task("Task A", "high", "work", task_id=42)
        t2 = Task("Task B", "low", "personal", task_id=42)
        assert t1 == t2

    def test_not_equal_different_id(self):
        t1 = Task("Same title", "high", "work")
        t2 = Task("Same title", "high", "work")
        assert t1 != t2  # different auto-assigned IDs

    def test_hashable_in_set(self):
        t1 = Task("Task", "high", "work")
        s = {t1}
        assert t1 in s

    def test_sorted_by_priority_score(self):
        low = Task("Low task", "low", "work")
        high = Task("High task", "high", "work")
        med = Task("Med task", "medium", "work")
        tasks = sorted([low, high, med])
        assert tasks[0].priority == "high"
        assert tasks[1].priority == "medium"
        assert tasks[2].priority == "low"
