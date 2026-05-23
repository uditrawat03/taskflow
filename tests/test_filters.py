# tests/test_filters.py
import pytest
from taskflow.filters import TaskFilter
from taskflow.core.task import Task
from taskflow.core.task_types import DeadlineTask, UrgentTask


class TestTaskFilterBasic:
    def test_get_returns_all_tasks(self, mixed_tasks):
        result = TaskFilter(mixed_tasks).get()
        assert len(result) == len(mixed_tasks)

    def test_does_not_mutate_original(self, mixed_tasks):
        original_len = len(mixed_tasks)
        TaskFilter(mixed_tasks).pending().limit(1).get()
        assert len(mixed_tasks) == original_len

    def test_empty_filter_returns_empty(self, empty_tasks):
        result = TaskFilter(empty_tasks).get()
        assert result == []


class TestStatusFilters:
    def test_pending(self, mixed_tasks):
        result = TaskFilter(mixed_tasks).pending().get()
        assert all(not t.done for t in result)

    def test_done(self, mixed_tasks):
        result = TaskFilter(mixed_tasks).done().get()
        assert all(t.done for t in result)

    def test_pending_and_done_are_complementary(self, mixed_tasks):
        pending = TaskFilter(mixed_tasks).pending().count()
        done = TaskFilter(mixed_tasks).done().count()
        assert pending + done == len(mixed_tasks)


class TestAttributeFilters:
    def test_by_priority_high(self, mixed_tasks):
        result = TaskFilter(mixed_tasks).by_priority("high").get()
        assert all(t.priority == "high" for t in result)

    def test_by_category_work(self, mixed_tasks):
        result = TaskFilter(mixed_tasks).by_category("work").get()
        assert all(t.category == "work" for t in result)

    def test_by_type_urgent(self, mixed_tasks):
        result = TaskFilter(mixed_tasks).by_type(UrgentTask).get()
        assert all(isinstance(t, UrgentTask) for t in result)


class TestTextFilters:
    def test_search_case_insensitive(self, mixed_tasks):
        result = TaskFilter(mixed_tasks).search("REVIEW").get()
        assert len(result) > 0
        assert all("review" in t.title.lower() for t in result)

    def test_search_no_match(self, mixed_tasks):
        result = TaskFilter(mixed_tasks).search("xyzzy_no_match").get()
        assert result == []

    def test_search_regex(self, mixed_tasks):
        result = TaskFilter(mixed_tasks).search_regex(r"^Review").get()
        assert all(t.title.startswith("Review") for t in result)

    def test_search_regex_invalid_raises(self, mixed_tasks):
        with pytest.raises(ValueError):
            TaskFilter(mixed_tasks).search_regex("[unclosed")


class TestSortingAndPaging:
    def test_sort_by_priority(self, mixed_tasks):
        result = TaskFilter(mixed_tasks).sort_by("priority").get()
        scores = [t.priority_score for t in result]
        assert scores == sorted(scores, reverse=True)

    def test_sort_by_title(self, mixed_tasks):
        result = TaskFilter(mixed_tasks).sort_by("title").get()
        titles = [t.title.lower() for t in result]
        assert titles == sorted(titles)

    def test_sort_unknown_key_raises(self, mixed_tasks):
        with pytest.raises(ValueError):
            TaskFilter(mixed_tasks).sort_by("nonexistent_key")

    def test_limit(self, mixed_tasks):
        result = TaskFilter(mixed_tasks).limit(2).get()
        assert len(result) == 2

    def test_offset(self, mixed_tasks):
        all_tasks = TaskFilter(mixed_tasks).get()
        after_offset = TaskFilter(mixed_tasks).offset(2).get()
        assert after_offset == all_tasks[2:]


class TestTerminalOperations:
    def test_count(self, mixed_tasks):
        assert TaskFilter(mixed_tasks).count() == len(mixed_tasks)

    def test_first(self, mixed_tasks):
        first = TaskFilter(mixed_tasks).first()
        assert first is mixed_tasks[0]

    def test_first_on_empty(self, empty_tasks):
        assert TaskFilter(empty_tasks).first() is None

    def test_titles(self, mixed_tasks):
        titles = TaskFilter(mixed_tasks).titles()
        assert len(titles) == len(mixed_tasks)
        assert all(isinstance(t, str) for t in titles)

    def test_ids(self, mixed_tasks):
        ids = TaskFilter(mixed_tasks).ids()
        assert all(isinstance(i, int) for i in ids)

    def test_id_map(self, mixed_tasks):
        id_map = TaskFilter(mixed_tasks).id_map()
        for task in mixed_tasks:
            assert task.id in id_map
            assert id_map[task.id] is task

    def test_bool_true_when_has_tasks(self, mixed_tasks):
        assert bool(TaskFilter(mixed_tasks)) is True

    def test_bool_false_when_empty(self, empty_tasks):
        assert bool(TaskFilter(empty_tasks)) is False

    def test_all_done_false_for_mixed(self, mixed_tasks):
        assert TaskFilter(mixed_tasks).all_done() is False

    def test_all_done_true_when_all_complete(self):
        tasks = [Task("A", "low", "work"), Task("B", "low", "work")]
        for t in tasks:
            t.mark_done()
        assert TaskFilter(tasks).all_done() is True


class TestChaining:
    def test_multiple_filters_chained(self, mixed_tasks):
        result = (
            TaskFilter(mixed_tasks)
            .pending()
            .by_priority("high")
            .sort_by("title")
            .limit(3)
            .get()
        )
        assert all(not t.done for t in result)
        assert all(t.priority == "high" for t in result)
        assert len(result) <= 3
