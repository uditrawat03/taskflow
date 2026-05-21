# taskflow/storage/json_store.py
# TaskFlow AI — JSON-based task persistence.
#
# Storage format: a JSON array of task dictionaries.
# Uses an atomic write pattern (write to .tmp, then rename)
# so the data file is never left in a partially-written state.
#
# Version history:
#   Day 08 — pipe-separated text storage
#   Day 09 — migrated to JSON
#   Day 10 — StorageError hierarchy, load_tasks_safe() added
#   Day 11 — moved into storage/ subpackage (Day 11 supplement)
#   Day 12 — save/load now handle Task objects via to_dict/from_dict

import json
import shutil
import datetime
from pathlib import Path

from ..config import DATA_FILE, DATE_FMT
from ..errors import StorageError
from ..core.task_factory import task_from_dict
from ..core.task         import Task

__all__ = [
    "save_tasks",
    "load_tasks",
    "load_tasks_safe",
    "backup_tasks",
    "get_next_id",
    "get_storage_info",
]


# ─── Save ─────────────────────────────────────────────────

def save_tasks(tasks: list, filepath: Path = DATA_FILE) -> None:
    """
    Persist a list of Task objects (or dicts) to a JSON file.

    Uses an atomic write: writes to a .tmp file first, then renames
    it over the target path — the data file is never half-written.

    Args:
        tasks    (list): Task objects or plain dicts to save.
        filepath (Path): Destination JSON file. Defaults to DATA_FILE.

    Raises:
        StorageError: If the file cannot be written.
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)
    tmp = filepath.with_suffix(".tmp")

    try:
        # Serialise — convert Task objects to dicts
        data = [
            t.to_dict() if isinstance(t, Task) else t
            for t in tasks
        ]
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        tmp.rename(filepath)   # atomic replace on most filesystems
    except (OSError, TypeError) as e:
        if tmp.exists():
            tmp.unlink()
        raise StorageError(
            f"Could not save tasks to '{filepath.name}': {e}"
        ) from e


# ─── Load ─────────────────────────────────────────────────

def load_tasks(filepath: Path = DATA_FILE) -> list[Task]:
    """
    Load Task objects from a JSON file.

    Returns an empty list if the file does not exist (first run).
    Uses task_from_dict to restore the correct subclass for each task.

    Args:
        filepath (Path): Source JSON file. Defaults to DATA_FILE.

    Returns:
        list[Task]: Loaded Task instances (correct subclass for each).

    Raises:
        StorageError: If the file exists but cannot be read or parsed.
    """
    if not filepath.exists():
        return []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise StorageError(
            f"Storage file '{filepath.name}' contains invalid JSON "
            f"(line {e.lineno}, col {e.colno})."
        ) from e
    except OSError as e:
        raise StorageError(
            f"Could not read storage file '{filepath.name}': {e}"
        ) from e

    if not isinstance(data, list):
        raise StorageError(
            f"Storage file has unexpected format: "
            f"expected a JSON array, got {type(data).__name__}."
        )

    return [task_from_dict(d) for d in data]


def load_tasks_safe(
    filepath: Path = DATA_FILE,
) -> tuple[list[Task], str | None]:
    """
    Load tasks without raising exceptions.

    Returns:
        tuple: (task_list, None) on success,
               ([], error_message) on failure.
    """
    try:
        tasks = load_tasks(filepath)
        return tasks, None
    except StorageError as e:
        return [], str(e)


# ─── Helpers ──────────────────────────────────────────────

def get_next_id(tasks: list) -> int:
    """
    Return the next available task ID.

    Args:
        tasks (list): Current list of Task objects or dicts.

    Returns:
        int: max(existing IDs) + 1, or 1 if list is empty.
    """
    ids = [
        (t.id if isinstance(t, Task) else t.get("id", 0))
        for t in tasks
    ]
    return max(ids, default=0) + 1


# ─── Backup ───────────────────────────────────────────────

def backup_tasks(filepath: Path = DATA_FILE) -> bool:
    """
    Create a timestamped backup of the storage file.

    The backup is saved in the same directory as the original.

    Args:
        filepath (Path): File to back up. Defaults to DATA_FILE.

    Returns:
        bool: True if backup succeeded, False if source does not exist.
    """
    if not filepath.exists():
        print("  ✗ No storage file to back up.")
        return False

    timestamp   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{filepath.stem}_backup_{timestamp}{filepath.suffix}"
    backup_path = filepath.parent / backup_name

    try:
        shutil.copy2(filepath, backup_path)
        print(f"  ✓ Backup saved: {backup_path.name}")
        return True
    except OSError as e:
        print(f"  ✗ Backup failed: {e}")
        return False


# ─── Storage metadata ─────────────────────────────────────

def get_storage_info(filepath: Path = DATA_FILE) -> dict:
    """
    Return metadata about the storage file.

    Args:
        filepath (Path): Storage file to inspect.

    Returns:
        dict: exists, filepath, size_bytes, last_modified.
    """
    if not filepath.exists():
        return {"exists": False}

    stat = filepath.stat()
    return {
        "exists":        True,
        "filepath":      str(filepath.resolve()),
        "size_bytes":    stat.st_size,
        "last_modified": datetime.datetime.fromtimestamp(
            stat.st_mtime
        ).strftime(DATE_FMT),
    }