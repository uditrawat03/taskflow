import json
import shutil
import datetime
from pathlib import Path
from errors import StorageError

BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "taskflow_tasks.json"
DATE_FMT = "%Y-%m-%d %H:%M"


def save_tasks(tasks: list, filepath: Path = DATA_FILE) -> None:
    """
    Save tasks to JSON using an atomic write pattern.

    Raises:
        StorageError: If the file cannot be written.
    """
    tmp_path = filepath.with_suffix(".tmp")
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(tasks, f, indent=2, ensure_ascii=False)
        tmp_path.rename(filepath)
    except (OSError, TypeError) as e:
        if tmp_path.exists():
            tmp_path.unlink()
        raise StorageError(f"Could not save tasks: {e}") from e


def load_tasks(filepath: Path = DATA_FILE) -> list:
    """
    Load tasks from JSON.

    Returns an empty list if file does not exist.

    Raises:
        StorageError: If the file exists but cannot be read or parsed.
    """
    if not filepath.exists():
        return []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise StorageError("Storage file contains invalid JSON") from e
    except OSError as e:
        raise StorageError(f"Could not read storage file: {e}") from e

    if not isinstance(data, list):
        raise StorageError(
            f"Storage file has unexpected format: expected list, "
            f"got {type(data).__name__}"
        )

    return data


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
