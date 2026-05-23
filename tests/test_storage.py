# tests/test_storage.py
import json
import pytest
from pathlib import Path
from taskflow.core.task import Task
from taskflow.core.task_types import UrgentTask, RecurringTask
from taskflow.storage.json_store import (
    save_tasks,
    load_tasks,
    load_tasks_safe,
    get_next_id,
    backup_tasks,
)
from taskflow.errors import StorageError


class TestSaveTasks:
    def test_creates_file(self, tmp_path, one_task):
        filepath = tmp_path / "tasks.json"
        save_tasks(one_task, filepath=filepath)
        assert filepath.exists()

    def test_creates_parent_directory(self, tmp_path, one_task):
        filepath = tmp_path / "subdir" / "tasks.json"
        save_tasks(one_task, filepath=filepath)
        assert filepath.exists()

    def test_file_is_valid_json(self, tmp_path, one_task):
        filepath = tmp_path / "tasks.json"
        save_tasks(one_task, filepath=filepath)
        content = json.loads(filepath.read_text())
        assert isinstance(content, list)
        assert len(content) == 1

    def test_save_empty_list(self, tmp_path):
        filepath = tmp_path / "tasks.json"
        save_tasks([], filepath=filepath)
        content = json.loads(filepath.read_text())
        assert content == []


class TestLoadTasks:
    def test_returns_empty_list_when_file_missing(self, tmp_path):
        filepath = tmp_path / "nonexistent.json"
        tasks = load_tasks(filepath=filepath)
        assert tasks == []

    def test_roundtrip(self, tmp_path, mixed_tasks):
        filepath = tmp_path / "tasks.json"
        save_tasks(mixed_tasks, filepath=filepath)
        loaded = load_tasks(filepath=filepath)
        assert len(loaded) == len(mixed_tasks)
        assert loaded[0].title == mixed_tasks[0].title
        assert loaded[0].priority == mixed_tasks[0].priority

    def test_raises_on_invalid_json(self, tmp_path):
        filepath = tmp_path / "tasks.json"
        filepath.write_text("{not valid json}", encoding="utf-8")
        with pytest.raises(StorageError):
            load_tasks(filepath=filepath)

    def test_raises_on_non_list_json(self, tmp_path):
        filepath = tmp_path / "tasks.json"
        filepath.write_text('{"key": "value"}', encoding="utf-8")
        with pytest.raises(StorageError):
            load_tasks(filepath=filepath)

    def test_restores_urgent_task_type(self, tmp_path):
        tasks = [UrgentTask("Server down", "work")]
        filepath = tmp_path / "tasks.json"
        save_tasks(tasks, filepath=filepath)
        loaded = load_tasks(filepath=filepath)
        assert isinstance(loaded[0], UrgentTask)

    def test_restores_done_state(self, tmp_path, one_task):
        one_task[0].mark_done()
        filepath = tmp_path / "tasks.json"
        save_tasks(one_task, filepath=filepath)
        loaded = load_tasks(filepath=filepath)
        assert loaded[0].done is True


class TestLoadTasksSafe:
    def test_returns_empty_list_on_error(self, tmp_path):
        filepath = tmp_path / "corrupt.json"
        filepath.write_text("not json", encoding="utf-8")
        tasks, error = load_tasks_safe(filepath=filepath)
        assert tasks == []
        assert error is not None
        assert isinstance(error, str)

    def test_returns_tasks_and_none_on_success(self, tmp_path, one_task):
        filepath = tmp_path / "tasks.json"
        save_tasks(one_task, filepath=filepath)
        tasks, error = load_tasks_safe(filepath=filepath)
        assert len(tasks) == 1
        assert error is None


class TestGetNextId:
    def test_returns_one_for_empty_list(self):
        assert get_next_id([]) == 1

    def test_returns_max_plus_one(self):
        tasks = [
            Task("A", "low", "work", task_id=5),
            Task("B", "low", "work", task_id=3),
            Task("C", "low", "work", task_id=9),
        ]
        assert get_next_id(tasks) == 10


class TestBackupTasks:
    def test_creates_backup_file(self, tmp_path, one_task):
        filepath = tmp_path / "tasks.json"
        save_tasks(one_task, filepath=filepath)
        result = backup_tasks(filepath=filepath)
        assert result is True
        backup_files = list(tmp_path.glob("*backup*.json"))
        assert len(backup_files) == 1

    def test_returns_false_when_no_source(self, tmp_path):
        filepath = tmp_path / "nonexistent.json"
        result = backup_tasks(filepath=filepath)
        assert result is False
