# tests/test_stats.py — Tests for taskflow/core/stats.py
import pytest
from taskflow.core.task        import Task
from taskflow.core.task_types  import UrgentTask
from taskflow.core.stats       import (
    calculate_stats, priority_breakdown, category_breakdown,
    completion_rate, average_title_length, most_productive_category,
)


class TestCalculateStats:
    def test_empty_list(self, empty_tasks):
        stats = calculate_stats(empty_tasks)
        assert stats == {"total": 0, "done": 0, "pending": 0, "rate": 0.0}

    def test_all_pending(self, mixed_tasks):
        # Reset done state
        for t in mixed_tasks:
            t.done = False; t.status = "pending"
        stats = calculate_stats(mixed_tasks)
        assert stats["total"]   == len(mixed_tasks)
        assert stats["done"]    == 0
        assert stats["pending"] == len(mixed_tasks)
        assert stats["rate"]    == 0.0

    def test_all_done(self, mixed_tasks):
        for t in mixed_tasks:
            t.done = True; t.status = "done"
        stats = calculate_stats(mixed_tasks)
        assert stats["done"]    == len(mixed_tasks)
        assert stats["pending"] == 0
        assert stats["rate"]    == 100.0

    def test_mixed_states(self, mixed_tasks):
        # mixed_tasks fixture has 1 done, 4 pending
        stats = calculate_stats(mixed_tasks)
        assert stats["total"]   == len(mixed_tasks)
        assert stats["done"]    == 1
        assert stats["pending"] == len(mixed_tasks) - 1

    def test_rate_precision(self):
        tasks = [Task(f"T{i}", "low", "work") for i in range(3)]
        tasks[0].mark_done()
        stats = calculate_stats(tasks)
        assert stats["rate"] == round(1/3 * 100, 1)


class TestPriorityBreakdown:
    def test_all_priorities_present(self, mixed_tasks):
        result = priority_breakdown(mixed_tasks)
        assert set(result.keys()) == {"high", "medium", "low"}

    def test_counts_correct(self):
        tasks = [
            Task("A", "high",   "work"),
            Task("B", "high",   "work"),
            Task("C", "medium", "work"),
            Task("D", "low",    "work"),
        ]
        result = priority_breakdown(tasks)
        assert result["high"]   == 2
        assert result["medium"] == 1
        assert result["low"]    == 1

    def test_missing_priority_is_zero(self, empty_tasks):
        empty_tasks.append(Task("Only high", "high", "work"))
        result = priority_breakdown(empty_tasks)
        assert result["medium"] == 0
        assert result["low"]    == 0


class TestCategoryBreakdown:
    def test_returns_dict(self, mixed_tasks):
        result = category_breakdown(mixed_tasks)
        assert isinstance(result, dict)

    def test_counts_correct(self):
        tasks = [
            Task("A", "low", "work"),
            Task("B", "low", "work"),
            Task("C", "low", "personal"),
        ]
        result = category_breakdown(tasks)
        assert result["work"]     == 2
        assert result["personal"] == 1

    def test_sorted_most_common_first(self):
        tasks = [
            Task("A", "low", "personal"),
            Task("B", "low", "work"),
            Task("C", "low", "work"),
            Task("D", "low", "work"),
        ]
        result = category_breakdown(tasks)
        keys = list(result.keys())
        assert keys[0] == "work"   # most common first


class TestCompletionRate:
    def test_empty_returns_zero(self, empty_tasks):
        assert completion_rate(empty_tasks) == 0.0

    def test_none_done(self, one_task):
        assert completion_rate(one_task) == 0.0

    def test_all_done(self, one_task):
        one_task[0].mark_done()
        assert completion_rate(one_task) == 100.0

    def test_half_done(self):
        tasks = [Task(f"T{i}", "low", "work") for i in range(4)]
        tasks[0].mark_done()
        tasks[1].mark_done()
        assert completion_rate(tasks) == 50.0


class TestAverageTitleLength:
    def test_empty_returns_zero(self, empty_tasks):
        assert average_title_length(empty_tasks) == 0.0

    def test_single_task(self):
        tasks = [Task("Hello", "low", "work")]
        assert average_title_length(tasks) == 5.0

    def test_multiple_tasks(self):
        tasks = [
            Task("AB",   "low", "work"),   # 2 chars
            Task("ABCD", "low", "work"),   # 4 chars
        ]
        assert average_title_length(tasks) == 3.0


class TestMostProductiveCategory:
    def test_none_when_empty(self, empty_tasks):
        assert most_productive_category(empty_tasks) is None

    def test_none_when_none_done(self, one_task):
        assert most_productive_category(one_task) is None

    def test_returns_category_with_most_done(self):
        tasks = [
            Task("A", "low", "work"),
            Task("B", "low", "work"),
            Task("C", "low", "personal"),
        ]
        tasks[0].mark_done()
        tasks[1].mark_done()
        tasks[2].mark_done()
        result = most_productive_category(tasks)
        assert result == "work"

    def test_single_done_task(self, mixed_tasks):
        # mixed_tasks has 1 done task ("Write tests" in "work")
        result = most_productive_category(mixed_tasks)
        assert result == "work"