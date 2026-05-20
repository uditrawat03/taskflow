# taskflow/storage/json_store.py — updated for Day 12
import json
import shutil
import datetime
from pathlib import Path
from ..core.task import Task
from ..config import DATA_FILE, DATE_FMT
from ..errors import StorageError


def save_tasks(tasks: list[Task], filepath: Path = DATA_FILE) -> None:
    """Save a list of Task objects to JSON."""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = filepath.with_suffix(".tmp")
    try:
        data = [t.to_dict() for t in tasks]
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        tmp.rename(filepath)
    except (OSError, TypeError) as e:
        if tmp.exists():
            tmp.unlink()
        raise StorageError(f"Could not save tasks: {e}") from e


def load_tasks(filepath: Path = DATA_FILE) -> list[Task]:
    """Load Task objects from JSON. Returns [] if file missing."""
    if not filepath.exists():
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise StorageError("Expected a list in storage file")
        return [Task.from_dict(d) for d in data]
    except json.JSONDecodeError as e:
        raise StorageError("Storage file contains invalid JSON") from e
    except OSError as e:
        raise StorageError(f"Could not read storage file: {e}") from e


def load_tasks_safe(filepath: Path = DATA_FILE) -> tuple[list, str | None]:
    """
    Load tasks without raising — returns (tasks, error_message).

    Use in main() where you want to handle errors inline rather than
    propagating them up the call stack.

    Returns:
        tuple: (task_list, None) on success, ([], error_message) on failure.
    """
    try:
        tasks = load_tasks(filepath)
        return tasks, None
    except StorageError as e:
        return [], str(e)


def get_next_id(tasks: list) -> int:
    """Return the next available task ID."""
    return max((t["id"] for t in tasks), default=0) + 1


def backup_tasks(filepath: Path = DATA_FILE) -> bool:
    """
    Create a timestamped backup of the JSON storage file.

    Args:
        filepath (Path): Path to the storage file to back up.

    Returns:
        bool: True if backup succeeded.
    """
    if not filepath.exists():
        print("  ✗ No storage file to back up.")
        return False

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = filepath.parent / f"taskflow_backup_{timestamp}.json"

    try:
        shutil.copy2(filepath, backup_path)
        print(f"  ✓ Backup saved: {backup_path.name}")
        return True
    except OSError as e:
        print(f"  ✗ Backup failed: {e}")
        return False


def get_storage_info(filepath: Path = DATA_FILE) -> dict:
    """Return metadata about the storage file."""
    if not filepath.exists():
        return {"exists": False}

    stat = filepath.stat()
    return {
        "exists": True,
        "filepath": str(filepath),
        "size_bytes": stat.st_size,
        "last_modified": datetime.datetime.fromtimestamp(stat.st_mtime).strftime(
            DATE_FMT
        ),
    }
