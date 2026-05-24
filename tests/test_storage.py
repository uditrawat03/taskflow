# tests/test_storage.py — Tests for taskflow/storage/json_store.py
import json
import pytest
from pathlib import Path
from taskflow.core.task        import Task
from taskflow.core.task_types  import UrgentTask, RecurringTask, DeadlineTask
from taskflow.storage.json_store import (
    save_tasks, load_tasks, load_tasks_safe,
    backup_tasks, get_next_id,
)
from taskflow.errors import StorageError


class TestSaveTasks:
    def test_creates_file(self, tmp_path, one_task):
        fp = tmp_path / "tasks.json"
        save_tasks(one_task, filepath=fp)
        assert fp.exists()

    def test_creates_parent_dirs(self, tmp_path, one_task):
        fp = tmp_path / "sub" / "tasks.json"
        save_tasks(one_task, filepath=fp)
        assert fp.exists()

    def test_file_is_valid_json(self, tmp_path, one_task):
        fp = tmp_path / "tasks.json"
        save_tasks(one_task, filepath=fp)
        data = json.loads(fp.read_text())
        assert isinstance(data, list)
        assert len(data) == 1

    def test_save_empty_list(self, tmp_path):
        fp = tmp_path / "tasks.json"
        save_tasks([], filepath=fp)
        assert json.loads(fp.read_text()) == []

    def test_overwrite_existing(self, tmp_path, one_task):
        fp = tmp_path / "tasks.json"
        save_tasks(one_task, filepath=fp)
        save_tasks([], filepath=fp)
        assert json.loads(fp.read_text()) == []


class TestLoadTasks:
    def test_empty_when_file_missing(self, tmp_path):
        fp = tmp_path / "nonexistent.json"
        assert load_tasks(filepath=fp) == []

    def test_roundtrip(self, tmp_path, mixed_tasks):
        fp = tmp_path / "tasks.json"
        save_tasks(mixed_tasks, filepath=fp)
        loaded = load_tasks(filepath=fp)
        assert len(loaded) == len(mixed_tasks)
        assert loaded[0].title    == mixed_tasks[0].title
        assert loaded[0].priority == mixed_tasks[0].priority

    def test_raises_on_invalid_json(self, tmp_path):
        fp = tmp_path / "tasks.json"
        fp.write_text("{not valid}", encoding="utf-8")
        with pytest.raises(StorageError):
            load_tasks(filepath=fp)

    def test_raises_on_non_list_json(self, tmp_path):
        fp = tmp_path / "tasks.json"
        fp.write_text('{"key": "value"}', encoding="utf-8")
        with pytest.raises(StorageError):
            load_tasks(filepath=fp)

    def test_restores_urgent_type(self, tmp_path):
        tasks = [UrgentTask("Server down", "work")]
        fp    = tmp_path / "tasks.json"
        save_tasks(tasks, filepath=fp)
        loaded = load_tasks(filepath=fp)
        assert isinstance(loaded[0], UrgentTask)

    def test_restores_recurring_type(self, tmp_path):
        tasks = [RecurringTask("Standup", "medium", "work", "daily")]
        fp    = tmp_path / "tasks.json"
        save_tasks(tasks, filepath=fp)
        loaded = load_tasks(filepath=fp)
        assert isinstance(loaded[0], RecurringTask)
        assert loaded[0].recurrence == "daily"

    def test_restores_deadline_type(self, tmp_path):
        tasks = [DeadlineTask("Report", "work", due_date="2099-12-31")]
        fp    = tmp_path / "tasks.json"
        save_tasks(tasks, filepath=fp)
        loaded = load_tasks(filepath=fp)
        assert isinstance(loaded[0], DeadlineTask)
        assert loaded[0].due_date == "2099-12-31"

    def test_restores_done_state(self, tmp_path, one_task):
        one_task[0].mark_done()
        fp = tmp_path / "tasks.json"
        save_tasks(one_task, filepath=fp)
        loaded = load_tasks(filepath=fp)
        assert loaded[0].done   is True
        assert loaded[0].status == "done"


class TestLoadTasksSafe:
    def test_success(self, tmp_path, one_task):
        fp = tmp_path / "tasks.json"
        save_tasks(one_task, filepath=fp)
        tasks, error = load_tasks_safe(filepath=fp)
        assert len(tasks) == 1
        assert error is None

    def test_error_on_corrupt(self, tmp_path):
        fp = tmp_path / "tasks.json"
        fp.write_text("not json", encoding="utf-8")
        tasks, error = load_tasks_safe(filepath=fp)
        assert tasks == []
        assert isinstance(error, str)
        assert len(error) > 0

    def test_empty_list_when_missing(self, tmp_path):
        fp = tmp_path / "nonexistent.json"
        tasks, error = load_tasks_safe(filepath=fp)
        assert tasks == []
        assert error is None


class TestGetNextId:
    def test_returns_one_for_empty(self):
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
        fp = tmp_path / "tasks.json"
        save_tasks(one_task, filepath=fp)
        result = backup_tasks(filepath=fp)
        assert result is True
        backup_files = list(tmp_path.glob("*backup*.json"))
        assert len(backup_files) == 1

    def test_returns_false_no_source(self, tmp_path):
        fp = tmp_path / "nonexistent.json"
        result = backup_tasks(filepath=fp)
        assert result is False

    def test_backup_content_matches(self, tmp_path, one_task):
        fp = tmp_path / "tasks.json"
        save_tasks(one_task, filepath=fp)
        backup_tasks(filepath=fp)
        backup_files = list(tmp_path.glob("*backup*.json"))
        original = json.loads(fp.read_text())
        backup   = json.loads(backup_files[0].read_text())
        assert original == backup