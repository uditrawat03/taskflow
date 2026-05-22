# tests/test_services.py
# TaskFlow AI — unit tests for the services layer.
#
# These tests verify business logic in complete isolation —
# no display, no file I/O, no network.

import pytest
from taskflow.core.task import Task
from taskflow.core.task_types import RecurringTask
from taskflow.errors import ValidationError, TaskNotFoundError
from taskflow.services import (
    add_task_to_list,
    remove_task_by_index,
    remove_task_by_id,
    mark_task_done,
    rename_task,
    find_task_by_id,
    find_task_index_by_id,
    is_at_limit,
    filter_tasks,
    search_tasks,
    get_summary_stats,
)


class TestAddTask:
    def test_adds_task_to_list(self, empty_tasks):
        task = Task("Review PR", "high", "work")
        result = add_task_to_list(empty_tasks, task, plan="premium")
        assert len(empty_tasks) == 1
        assert result is task

    def test_raises_at_free_plan_limit(self, ten_free_tasks):
        extra = Task("One too many", "low", "personal")
        with pytest.raises(ValidationError):
            add_task_to_list(ten_free_tasks, extra, plan="free")

    def test_allows_up_to_limit(self, empty_tasks):
        for i in range(10):
            add_task_to_list(
                empty_tasks, Task(f"Task {i}", "low", "personal"), plan="free"
            )
        assert len(empty_tasks) == 10


class TestRemoveTask:
    def test_remove_by_index(self, one_task):
        removed = remove_task_by_index(one_task, 0)
        assert removed.title == "Review PR"
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
    def test_marks_standard_task_done(self, one_task):
        result = mark_task_done(one_task, 0)
        assert result.done is True
        assert result.status == "done"

    def test_raises_if_already_done(self, one_task):
        mark_task_done(one_task, 0)
        with pytest.raises(ValidationError):
            mark_task_done(one_task, 0)

    def test_recurring_task_resets(self, empty_tasks):
        task = RecurringTask("Daily standup", "medium", "work", "daily")
        empty_tasks.append(task)
        result = mark_task_done(empty_tasks, 0)
        assert result.done is False  # reset to pending
        assert result.completion_count == 1  # counter incremented

    def test_raises_if_index_out_of_range(self, one_task):
        with pytest.raises(IndexError):
            mark_task_done(one_task, 99)


class TestRenameTask:
    def test_renames_successfully(self, one_task):
        result = rename_task(one_task, 0, "Updated title")
        assert result.title == "Updated title"

    def test_raises_on_empty_title(self, one_task):
        with pytest.raises(ValidationError):
            rename_task(one_task, 0, "")

    def test_raises_on_title_too_long(self, one_task):
        with pytest.raises(ValidationError):
            rename_task(one_task, 0, "x" * 201)

    def test_strips_whitespace(self, one_task):
        rename_task(one_task, 0, "  Trimmed  ")
        assert one_task[0].title == "Trimmed"


class TestFindTask:
    def test_find_by_id(self, mixed_tasks):
        task = mixed_tasks[0]
        found = find_task_by_id(mixed_tasks, task.id)
        assert found is task

    def test_find_by_id_not_found(self, mixed_tasks):
        with pytest.raises(TaskNotFoundError):
            find_task_by_id(mixed_tasks, 9999)

    def test_find_index_by_id(self, mixed_tasks):
        task = mixed_tasks[2]
        index = find_task_index_by_id(mixed_tasks, task.id)
        assert index == 2


class TestFilterTasks:
    def test_filter_by_priority(self, mixed_tasks):
        high = filter_tasks(mixed_tasks, priority="high")
        assert all(t.priority == "high" for t in high)

    def test_filter_pending_only(self, mixed_tasks):
        pending = filter_tasks(mixed_tasks, is_done=False)
        assert all(not t.done for t in pending)

    def test_filter_done_only(self, mixed_tasks):
        done = filter_tasks(mixed_tasks, is_done=True)
        assert all(t.done for t in done)

    def test_limit(self, mixed_tasks):
        limited = filter_tasks(mixed_tasks, limit=2)
        assert len(limited) == 2

    def test_no_filters_returns_all(self, mixed_tasks):
        all_tasks = filter_tasks(mixed_tasks)
        assert len(all_tasks) == len(mixed_tasks)


class TestSearchTasks:
    def test_finds_by_keyword(self, mixed_tasks):
        results = search_tasks(mixed_tasks, "review")
        assert any("Review" in t.title for t in results)

    def test_case_insensitive(self, mixed_tasks):
        results = search_tasks(mixed_tasks, "REVIEW")
        assert len(results) > 0

    def test_no_match_returns_empty(self, mixed_tasks):
        results = search_tasks(mixed_tasks, "xyzzy_no_match")
        assert results == []


class TestGetSummaryStats:
    def test_stats_on_mixed_tasks(self, mixed_tasks):
        stats = get_summary_stats(mixed_tasks)
        assert stats["total"] == len(mixed_tasks)
        assert stats["done"] == 1  # only "Write tests" is done
        assert stats["pending"] == len(mixed_tasks) - 1

    def test_stats_empty_list(self, empty_tasks):
        stats = get_summary_stats(empty_tasks)
        assert stats == {"total": 0, "done": 0, "pending": 0, "rate": 0.0}
