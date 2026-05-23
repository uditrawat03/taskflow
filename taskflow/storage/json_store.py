import json
import shutil
import datetime
import time
from pathlib import Path

from ..config import DATA_FILE, DATE_FMT
from ..errors import StorageError
from ..core.task_factory import task_from_dict
from ..core.task         import Task

import logging
logger = logging.getLogger(__name__)

# Save tasks
def save_tasks(tasks, filepath=DATA_FILE):
    """Save tasks to JSON — atomic write."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    tmp = filepath.with_suffix(".tmp")
    start = time.perf_counter()
    try:
        data = [t.to_dict() if isinstance(t, Task) else t for t in tasks]
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        tmp.rename(filepath)
        elapsed_ms = round((time.perf_counter() - start) * 1000, 1)
        logger.info(
            "Tasks saved",
            extra={"task_count": len(tasks), "duration_ms": elapsed_ms}
        )
    except (OSError, TypeError) as e:
        if tmp.exists():
            tmp.unlink()
        logger.error("Save failed: %s", e, exc_info=True)
        raise StorageError(f"Could not save tasks: {e}") from e


# load tasks
def load_tasks(filepath=DATA_FILE):
    """Load tasks from JSON."""
    if not filepath.exists():
        logger.debug("Storage file not found — returning empty list: %s", filepath)
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        tasks = [task_from_dict(d) for d in data]
        logger.info("Tasks loaded", extra={"task_count": len(tasks)})
        return tasks
    except json.JSONDecodeError as e:
        logger.error("Storage file corrupted: %s", e)
        raise StorageError("Storage file contains invalid JSON") from e
    except OSError as e:
        logger.error("Could not read storage file: %s", e)
        raise StorageError(f"Could not read storage file: {e}") from e


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


# ─ Helpers 

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


# ─ Backup ─

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


# ─ Storage metadata ─

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