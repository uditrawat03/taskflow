# tests/test_repository.py

import pytest
from pathlib import Path
from taskflow.core.task import Task
from taskflow.core.task_types import UrgentTask
from taskflow.repositories.json_repo import JsonTaskRepository
from taskflow.repositories.base import TaskRepository
from taskflow.errors import TaskNotFoundError, StorageError


class TestJsonTaskRepository:
    @pytest.fixture
    def repo(self, tmp_path) -> JsonTaskRepository:
        filepath = tmp_path / "tasks.json"
        return JsonTaskRepository(filepath)

    def test_find_all_returns_empty_initially(self, repo):
        assert repo.find_all() == []

    def test_add_and_find_all(self, repo, one_task):
        task = one_task[0]
        repo.add(task)
        all_tasks = repo.find_all()
        assert len(all_tasks) == 1
        assert all_tasks[0].title == task.title

    def test_find_by_id(self, repo, one_task):
        task = one_task[0]
        repo.add(task)
        found = repo.find_by_id(task.id)
        assert found is not None
        assert found.id == task.id

    def test_find_by_id_returns_none_when_missing(self, repo):
        assert repo.find_by_id(9999) is None

    def test_delete(self, repo, one_task):
        task = one_task[0]
        repo.add(task)
        removed = repo.delete(task.id)
        assert removed.id == task.id
        assert repo.count() == 0

    def test_delete_raises_when_not_found(self, repo):
        with pytest.raises(TaskNotFoundError):
            repo.delete(9999)

    def test_update(self, repo, one_task):
        task = one_task[0]
        repo.add(task)
        task.rename("Updated title")
        repo.update(task)
        found = repo.find_by_id(task.id)
        assert found.title == "Updated title"

    def test_persists_across_instances(self, tmp_path, one_task):
        """Data written by one repo instance survives to the next."""
        filepath = tmp_path / "tasks.json"
        repo1 = JsonTaskRepository(filepath)
        repo1.add(one_task[0])

        repo2 = JsonTaskRepository(filepath)
        assert repo2.count() == 1
        assert repo2.find_all()[0].title == one_task[0].title

    def test_find_pending(self, repo, mixed_tasks):
        for t in mixed_tasks:
            repo.add(t)
        pending = repo.find_pending()
        assert all(not t.done for t in pending)

    def test_count(self, repo, mixed_tasks):
        for t in mixed_tasks:
            repo.add(t)
        assert repo.count() == len(mixed_tasks)

    def test_exists(self, repo, one_task):
        task = one_task[0]
        assert repo.exists(task.id) is False
        repo.add(task)
        assert repo.exists(task.id) is True

    def test_raises_on_corrupt_file(self, tmp_path):
        filepath = tmp_path / "corrupt.json"
        filepath.write_text("{not valid json}", encoding="utf-8")
        repo = JsonTaskRepository(filepath)
        with pytest.raises(StorageError):
            repo.find_all()

    def test_saves_urgent_task_correctly(self, repo):
        urgent = UrgentTask("Server down", "work")
        repo.add(urgent)
        filepath = repo._filepath
        repo2 = JsonTaskRepository(filepath)
        loaded = repo2.find_all()
        assert isinstance(loaded[0], UrgentTask)
