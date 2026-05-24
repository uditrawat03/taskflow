# tests/test_strategies.py — Tests for taskflow/strategies.py
import pytest
from taskflow.core.task       import Task
from taskflow.core.task_types import DeadlineTask
from taskflow.strategies import (
    SortByPriority, SortByTitle, SortByCategory,
    SortByAge, SortByDueDate, CompositeSort,
)


@pytest.fixture
def sample_tasks():
    return [
        Task("Zebra task", "low",    "personal"),
        Task("Apple task", "high",   "work"),
        Task("Mango task", "medium", "work"),
    ]


class TestSortByPriority:
    def test_high_first(self, sample_tasks):
        result = SortByPriority().sort(sample_tasks)
        assert result[0].priority == "high"
        assert result[-1].priority == "low"

    def test_does_not_mutate_original(self, sample_tasks):
        original = [t.title for t in sample_tasks]
        SortByPriority().sort(sample_tasks)
        assert [t.title for t in sample_tasks] == original

    def test_callable_interface(self, sample_tasks):
        sorter = SortByPriority()
        result = sorter(sample_tasks)
        assert result[0].priority == "high"

    def test_reverse(self, sample_tasks):
        result = SortByPriority(reverse=True).sort(sample_tasks)
        assert result[0].priority == "low"


class TestSortByTitle:
    def test_alphabetical(self, sample_tasks):
        result = SortByTitle().sort(sample_tasks)
        titles = [t.title.lower() for t in result]
        assert titles == sorted(titles)

    def test_reverse(self, sample_tasks):
        result = SortByTitle(reverse=True).sort(sample_tasks)
        titles = [t.title.lower() for t in result]
        assert titles == sorted(titles, reverse=True)

    def test_case_insensitive(self):
        tasks = [Task("banana","low","work"), Task("Apple","low","work"), Task("cherry","low","work")]
        result = SortByTitle().sort(tasks)
        assert result[0].title == "Apple"


class TestSortByCategory:
    def test_sorts_by_category(self, sample_tasks):
        result = SortByCategory().sort(sample_tasks)
        categories = [t.category for t in result]
        assert categories == sorted(categories)

    def test_secondary_sort_by_priority(self):
        tasks = [
            Task("B work high",   "high",   "work"),
            Task("A work medium", "medium", "work"),
            Task("C personal",    "low",    "personal"),
        ]
        result = SortByCategory().sort(tasks)
        work_tasks = [t for t in result if t.category == "work"]
        assert work_tasks[0].priority == "high"


class TestSortByAge:
    def test_oldest_first_by_default(self):
        import datetime
        t1 = Task("Newest", "low", "work")
        t2 = Task("Oldest", "low", "work")
        t2.created_at = "2020-01-01 00:00"
        result = SortByAge().sort([t1, t2])
        assert result[0] is t2

    def test_newest_first(self):
        import datetime
        t1 = Task("Newest", "low", "work")
        t2 = Task("Oldest", "low", "work")
        t2.created_at = "2020-01-01 00:00"
        result = SortByAge(newest_first=True).sort([t1, t2])
        assert result[0] is t1


class TestSortByDueDate:
    def test_deadline_tasks_before_standard(self):
        standard = Task("Standard", "low", "work")
        deadline = DeadlineTask("Due soon", "work", due_date="2099-06-01")
        result   = SortByDueDate().sort([standard, deadline])
        assert isinstance(result[0], DeadlineTask)

    def test_earliest_due_date_first(self):
        d1 = DeadlineTask("Later",  "work", due_date="2099-12-31")
        d2 = DeadlineTask("Sooner", "work", due_date="2099-06-01")
        result = SortByDueDate().sort([d1, d2])
        assert result[0].due_date == "2099-06-01"

    def test_no_deadline_tasks_unchanged(self, sample_tasks):
        result = SortByDueDate().sort(sample_tasks)
        assert len(result) == len(sample_tasks)


class TestCompositeSort:
    def test_two_strategies_applied(self):
        tasks = [
            Task("Zebra high",  "high",   "work"),
            Task("Apple high",  "high",   "work"),
            Task("Only medium", "medium", "work"),
        ]
        result = CompositeSort([SortByTitle(), SortByPriority()]).sort(tasks)
        # All high-priority first
        assert result[0].priority == "high"
        assert result[1].priority == "high"
        # Within high-priority: alphabetical
        assert result[0].title < result[1].title

    def test_does_not_mutate_original(self, sample_tasks):
        original = [t.title for t in sample_tasks]
        CompositeSort([SortByTitle(), SortByPriority()]).sort(sample_tasks)
        assert [t.title for t in sample_tasks] == original

    def test_empty_strategies_returns_copy(self, sample_tasks):
        result = CompositeSort([]).sort(sample_tasks)
        assert len(result) == len(sample_tasks)

    def test_single_strategy(self, sample_tasks):
        result = CompositeSort([SortByPriority()]).sort(sample_tasks)
        assert result[0].priority == "high"


class TestSortStrategyInTaskFilter:
    def test_sort_with_strategy(self, mixed_tasks):
        from taskflow.filters import TaskFilter
        result = (
            TaskFilter(mixed_tasks)
            .sort_with(SortByPriority())
            .get()
        )
        scores = [t.priority_score for t in result]
        assert scores == sorted(scores, reverse=True)

    def test_sort_with_composite(self, mixed_tasks):
        from taskflow.filters import TaskFilter
        result = (
            TaskFilter(mixed_tasks)
            .sort_with(CompositeSort([SortByTitle(), SortByPriority()]))
            .get()
        )
        assert len(result) == len(mixed_tasks)