# tests/test_services.py — Unit tests for taskflow/services.py
import pytest
from taskflow.core.task        import Task
from taskflow.core.task_types  import RecurringTask
from taskflow.errors           import ValidationError, TaskNotFoundError
from taskflow.services         import (
    add_task_to_list, remove_task_by_index, remove_task_by_id,
    mark_task_done, rename_task, find_task_by_id, find_task_index_by_id,
    is_at_limit, get_task_limit, filter_tasks, search_tasks,
    get_overdue_tasks, get_summary_stats,
)


class TestAddTask:
    def test_adds_task(self, empty_tasks):
        task   = Task("Review PR", "high", "work")
        result = add_task_to_list(empty_tasks, task, plan="premium")
        assert len(empty_tasks) == 1
        assert result is task

    def test_raises_at_free_limit(self, ten_free_tasks):
        extra = Task("One too many", "low", "personal")
        with pytest.raises(ValidationError):
            add_task_to_list(ten_free_tasks, extra, plan="free")

    def test_allows_up_to_free_limit(self, empty_tasks):
        for i in range(10):
            add_task_to_list(empty_tasks, Task(f"Task {i}", "low", "personal"), plan="free")
        assert len(empty_tasks) == 10

    def test_premium_allows_more(self, empty_tasks):
        for i in range(50):
            add_task_to_list(empty_tasks, Task(f"Task {i}", "low", "personal"), plan="premium")
        assert len(empty_tasks) == 50


class TestRemoveTask:
    def test_remove_by_index(self, one_task):
        removed = remove_task_by_index(one_task, 0)
        assert removed.title == "Review pull request"
        assert len(one_task) == 0

    def test_remove_by_index_out_of_range(self, one_task):
        with pytest.raises(IndexError):
            remove_task_by_index(one_task, 99)

    def test_remove_by_id(self, one_task):
        task_id = one_task[0].id
        removed = remove_task_by_id(one_task, task_id)
        assert removed.id == task_id
        assert len(one_task) == 0

    def test_remove_by_id_not_found(self, one_task):
        with pytest.raises(TaskNotFoundError):
            remove_task_by_id(one_task, 9999)


class TestMarkDone:
    def test_marks_done(self, one_task):
        result = mark_task_done(one_task, 0)
        assert result.done   is True
        assert result.status == "done"

    def test_raises_if_already_done(self, one_task):
        mark_task_done(one_task, 0)
        with pytest.raises(ValidationError):
            mark_task_done(one_task, 0)

    def test_recurring_task_resets(self, empty_tasks):
        task = RecurringTask("Standup", "medium", "work", "daily")
        empty_tasks.append(task)
        result = mark_task_done(empty_tasks, 0)
        assert result.done             is False
        assert result.completion_count == 1

    def test_raises_out_of_range(self, one_task):
        with pytest.raises(IndexError):
            mark_task_done(one_task, 99)


class TestRenameTask:
    def test_renames(self, one_task):
        rename_task(one_task, 0, "Updated title")
        assert one_task[0].title == "Updated title"

    def test_raises_empty_title(self, one_task):
        with pytest.raises(ValidationError):
            rename_task(one_task, 0, "")

    def test_raises_title_too_long(self, one_task):
        with pytest.raises(ValidationError):
            rename_task(one_task, 0, "x" * 201)

    def test_strips_whitespace(self, one_task):
        rename_task(one_task, 0, "  Trimmed  ")
        assert one_task[0].title == "Trimmed"

    def test_raises_out_of_range(self, one_task):
        with pytest.raises(IndexError):
            rename_task(one_task, 99, "New title")


class TestFindTask:
    def test_find_by_id(self, mixed_tasks):
        task  = mixed_tasks[0]
        found = find_task_by_id(mixed_tasks, task.id)
        assert found is task

    def test_find_by_id_not_found(self, mixed_tasks):
        with pytest.raises(TaskNotFoundError):
            find_task_by_id(mixed_tasks, 9999)

    def test_find_index_by_id(self, mixed_tasks):
        task  = mixed_tasks[2]
        index = find_task_index_by_id(mixed_tasks, task.id)
        assert index == 2

    def test_find_index_not_found(self, mixed_tasks):
        with pytest.raises(TaskNotFoundError):
            find_task_index_by_id(mixed_tasks, 9999)


class TestIsAtLimit:
    def test_not_at_limit(self, empty_tasks):
        assert is_at_limit(empty_tasks, plan="free") is False

    def test_at_limit(self, ten_free_tasks):
        assert is_at_limit(ten_free_tasks, plan="free") is True

    def test_premium_limit_higher(self, ten_free_tasks):
        assert is_at_limit(ten_free_tasks, plan="premium") is False


class TestFilterTasks:
    def test_filter_by_priority(self, mixed_tasks):
        result = filter_tasks(mixed_tasks, priority="high")
        assert all(t.priority == "high" for t in result)
        assert len(result) > 0

    def test_filter_pending(self, mixed_tasks):
        result = filter_tasks(mixed_tasks, is_done=False)
        assert all(not t.done for t in result)

    def test_filter_done(self, mixed_tasks):
        result = filter_tasks(mixed_tasks, is_done=True)
        assert all(t.done for t in result)
        assert len(result) == 1  # only "Write tests" is done

    def test_limit(self, mixed_tasks):
        result = filter_tasks(mixed_tasks, limit=2)
        assert len(result) == 2

    def test_no_filter_returns_all(self, mixed_tasks):
        result = filter_tasks(mixed_tasks)
        assert len(result) == len(mixed_tasks)

    def test_filter_by_category(self, mixed_tasks):
        result = filter_tasks(mixed_tasks, category="work")
        assert all(t.category == "work" for t in result)


class TestSearchTasks:
    def test_finds_by_keyword(self, mixed_tasks):
        result = search_tasks(mixed_tasks, "review")
        assert len(result) > 0
        assert all("review" in t.title.lower() for t in result)

    def test_case_insensitive(self, mixed_tasks):
        result = search_tasks(mixed_tasks, "REVIEW")
        assert len(result) > 0

    def test_no_match_empty(self, mixed_tasks):
        assert search_tasks(mixed_tasks, "xyzzy_nomatch") == []


class TestGetOverdueTasks:
    def test_returns_overdue(self, overdue_task, empty_tasks):
        empty_tasks.append(overdue_task)
        result = get_overdue_tasks(empty_tasks)
        assert len(result) == 1
        assert result[0] is overdue_task

    def test_done_task_not_overdue(self, overdue_task, empty_tasks):
        overdue_task.mark_done()
        empty_tasks.append(overdue_task)
        assert get_overdue_tasks(empty_tasks) == []


class TestGetSummaryStats:
    def test_mixed_tasks(self, mixed_tasks):
        stats = get_summary_stats(mixed_tasks)
        assert stats["total"]   == len(mixed_tasks)
        assert stats["done"]    == 1
        assert stats["pending"] == len(mixed_tasks) - 1

    def test_empty_tasks(self, empty_tasks):
        stats = get_summary_stats(empty_tasks)
        assert stats == {"total": 0, "done": 0, "pending": 0, "rate": 0.0}