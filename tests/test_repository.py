# tests/test_repository.py — Tests for taskflow/repositories/json_repo.py
import json
import pytest
from pathlib import Path
from taskflow.core.task        import Task
from taskflow.core.task_types  import UrgentTask, RecurringTask
from taskflow.repositories.json_repo import JsonTaskRepository
from taskflow.errors import TaskNotFoundError, StorageError


class TestJsonTaskRepository:

    def test_find_all_empty_initially(self, tmp_repo):
        assert tmp_repo.find_all() == []

    def test_add_and_find_all(self, tmp_repo, one_task):
        task = one_task[0]
        tmp_repo.add(task)
        all_tasks = tmp_repo.find_all()
        assert len(all_tasks) == 1
        assert all_tasks[0].title == task.title

    def test_find_by_id_found(self, tmp_repo, one_task):
        task = one_task[0]
        tmp_repo.add(task)
        found = tmp_repo.find_by_id(task.id)
        assert found is not None
        assert found.id == task.id

    def test_find_by_id_not_found(self, tmp_repo):
        assert tmp_repo.find_by_id(9999) is None

    def test_find_by_priority(self, tmp_repo, mixed_tasks):
        for t in mixed_tasks:
            tmp_repo.add(t)
        high = tmp_repo.find_by_priority("high")
        assert all(t.priority == "high" for t in high)
        assert len(high) > 0

    def test_delete(self, tmp_repo, one_task):
        task = one_task[0]
        tmp_repo.add(task)
        removed = tmp_repo.delete(task.id)
        assert removed.id == task.id
        assert tmp_repo.count() == 0

    def test_delete_raises_when_not_found(self, tmp_repo):
        with pytest.raises(TaskNotFoundError):
            tmp_repo.delete(9999)

    def test_update(self, tmp_repo, one_task):
        task = one_task[0]
        tmp_repo.add(task)
        task.rename("Updated title")
        tmp_repo.update(task)
        found = tmp_repo.find_by_id(task.id)
        assert found.title == "Updated title"

    def test_update_raises_when_not_found(self, tmp_repo):
        task = Task("Ghost task", "low", "work", task_id=999)
        with pytest.raises(TaskNotFoundError):
            tmp_repo.update(task)

    def test_count(self, tmp_repo, mixed_tasks):
        for t in mixed_tasks:
            tmp_repo.add(t)
        assert tmp_repo.count() == len(mixed_tasks)

    def test_exists_true(self, tmp_repo, one_task):
        task = one_task[0]
        tmp_repo.add(task)
        assert tmp_repo.exists(task.id) is True

    def test_exists_false(self, tmp_repo, one_task):
        assert tmp_repo.exists(one_task[0].id) is False

    def test_save_all(self, tmp_repo, mixed_tasks):
        tmp_repo.save_all(mixed_tasks)
        assert tmp_repo.count() == len(mixed_tasks)

    def test_persists_across_instances(self, tmp_path, one_task):
        """Data written by one repo instance survives to the next."""
        filepath = tmp_path / "tasks.json"
        repo1    = JsonTaskRepository(filepath)
        repo1.add(one_task[0])
        repo2    = JsonTaskRepository(filepath)
        assert repo2.count() == 1
        assert repo2.find_all()[0].title == one_task[0].title

    def test_find_pending(self, tmp_repo, mixed_tasks):
        for t in mixed_tasks:
            tmp_repo.add(t)
        pending = tmp_repo.find_pending()
        assert all(not t.done for t in pending)

    def test_find_done(self, tmp_repo, mixed_tasks):
        for t in mixed_tasks:
            tmp_repo.add(t)
        done = tmp_repo.find_done()
        assert all(t.done for t in done)
        assert len(done) == 1

    def test_find_overdue(self, tmp_repo, overdue_task):
        tmp_repo.add(overdue_task)
        tmp_repo.add(Task("Fresh task", "low", "work"))
        overdue = tmp_repo.find_overdue()
        assert len(overdue) == 1
        assert overdue[0].id == overdue_task.id

    def test_raises_on_corrupt_file(self, tmp_path):
        filepath = tmp_path / "corrupt.json"
        filepath.write_text("{not valid json}", encoding="utf-8")
        repo = JsonTaskRepository(filepath)
        with pytest.raises(StorageError):
            repo.find_all()

    def test_saves_urgent_task_type(self, tmp_path):
        filepath = tmp_path / "tasks.json"
        repo = JsonTaskRepository(filepath)
        urgent = UrgentTask("Server down", "work")
        repo.add(urgent)
        repo2   = JsonTaskRepository(filepath)
        loaded  = repo2.find_all()
        assert isinstance(loaded[0], UrgentTask)

    def test_saves_recurring_task_type(self, tmp_path):
        filepath = tmp_path / "tasks.json"
        repo = JsonTaskRepository(filepath)
        rec  = RecurringTask("Standup", "medium", "work", "daily")
        rec.mark_done()
        repo.add(rec)
        repo2  = JsonTaskRepository(filepath)
        loaded = repo2.find_all()
        assert isinstance(loaded[0], RecurringTask)
        assert loaded[0].completion_count == 1

    def test_repr_contains_filename(self, tmp_repo):
        assert "tasks.json" in repr(tmp_repo)


class TestGetRepository:
    def test_returns_singleton(self):
        from taskflow.repositories import get_repository
        r1 = get_repository()
        r2 = get_repository()
        assert r1 is r2

    def test_cache_clear_creates_new_instance(self):
        from taskflow.repositories import get_repository
        r1 = get_repository()
        get_repository.cache_clear()
        r2 = get_repository()
        assert r1 is not r2

    def test_unknown_backend_raises(self):
        from taskflow.repositories import get_repository
        get_repository.cache_clear()
        with pytest.raises(ValueError, match="Unknown repository backend"):
            get_repository(backend="nonexistent_backend")
        get_repository.cache_clear()