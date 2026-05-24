# tests/test_task.py — Unit tests for taskflow/core/task.py
import pytest
import datetime
from taskflow.core.task import Task
from taskflow.errors    import ValidationError


class TestTaskCreation:
    def test_valid_task(self):
        task = Task("Review PR", "high", "work")
        assert task.title    == "Review PR"
        assert task.priority == "high"
        assert task.category == "work"
        assert task.done     is False
        assert task.status   == "pending"

    def test_empty_title_raises(self):
        with pytest.raises(ValidationError) as exc:
            Task("", "high", "work")
        assert exc.value.field == "title"

    def test_whitespace_title_raises(self):
        with pytest.raises(ValidationError):
            Task("   ", "high", "work")

    def test_title_stripped(self):
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

    @pytest.mark.parametrize("bad", ["urgent", "CRITICAL", "", "3", "  "])
    def test_invalid_priority_raises(self, bad):
        with pytest.raises(ValidationError):
            Task("Test", bad, "work")

    @pytest.mark.parametrize("category", ["work","personal","health","learning","other"])
    def test_valid_categories(self, category):
        task = Task("Test", "medium", category)
        assert task.category == category

    def test_auto_id_increments(self):
        t1 = Task("A", "low", "work")
        t2 = Task("B", "low", "work")
        assert t2.id == t1.id + 1

    def test_explicit_id(self):
        task = Task("Test", "low", "work", task_id=99)
        assert task.id == 99

    def test_created_at_format(self):
        task = Task("Test", "low", "work")
        datetime.datetime.strptime(task.created_at, "%Y-%m-%d %H:%M")


class TestTaskMethods:
    def test_mark_done(self, one_task):
        task = one_task[0]
        result = task.mark_done()
        assert task.done   is True
        assert task.status == "done"
        assert result is task

    def test_mark_pending(self, one_task):
        task = one_task[0]
        task.mark_done().mark_pending()
        assert task.done   is False
        assert task.status == "pending"

    def test_rename(self, one_task):
        one_task[0].rename("New title")
        assert one_task[0].title == "New title"

    def test_rename_empty_raises(self, one_task):
        with pytest.raises(ValidationError):
            one_task[0].rename("")

    def test_is_pending_true(self, one_task):
        assert one_task[0].is_pending() is True

    def test_is_pending_false_when_done(self, one_task):
        one_task[0].mark_done()
        assert one_task[0].is_pending() is False

    def test_matches_keyword(self, one_task):
        assert one_task[0].matches("review")  is True
        assert one_task[0].matches("REVIEW")  is True
        assert one_task[0].matches("grocery") is False

    def test_priority_setter_validates(self, one_task):
        with pytest.raises(ValidationError):
            one_task[0].priority = "urgent"

    def test_priority_setter_valid(self, one_task):
        one_task[0].priority = "low"
        assert one_task[0].priority == "low"

    @pytest.mark.parametrize("priority,score", [("high",3),("medium",2),("low",1)])
    def test_priority_score(self, priority, score):
        assert Task("T", priority, "work").priority_score == score

    def test_is_overdue_old_task(self, overdue_task):
        assert overdue_task.is_overdue(threshold_days=7)  is True
        assert overdue_task.is_overdue(threshold_days=40) is False

    def test_is_overdue_done_task_never_overdue(self, overdue_task):
        overdue_task.mark_done()
        assert overdue_task.is_overdue() is False


class TestTaskSerialization:
    def test_to_dict_keys(self, one_task):
        d = one_task[0].to_dict()
        assert {"id","title","priority","category","status","done","created_at","type"}.issubset(d)

    def test_to_dict_done_is_bool(self, one_task):
        assert isinstance(one_task[0].to_dict()["done"], bool)

    def test_from_dict_roundtrip(self, one_task):
        original = one_task[0]
        restored = Task.from_dict(original.to_dict())
        assert restored.id       == original.id
        assert restored.title    == original.title
        assert restored.priority == original.priority
        assert restored.done     == original.done

    def test_from_dict_restores_done_state(self):
        d = {"id":1,"title":"Done","priority":"high","category":"work",
             "status":"done","done":True,"created_at":"2025-05-19 14:00","type":"standard"}
        task = Task.from_dict(d)
        assert task.done is True


class TestTaskComparison:
    def test_equal_by_id(self):
        t1 = Task("A","high","work", task_id=42)
        t2 = Task("B","low","personal", task_id=42)
        assert t1 == t2

    def test_not_equal_different_id(self):
        t1 = Task("Same","high","work")
        t2 = Task("Same","high","work")
        assert t1 != t2

    def test_hashable(self):
        t = Task("Task","high","work")
        assert t in {t}

    def test_sorted_by_priority(self):
        low  = Task("L","low","work")
        high = Task("H","high","work")
        med  = Task("M","medium","work")
        result = sorted([low, high, med])
        assert result[0].priority == "high"
        assert result[-1].priority == "low"
