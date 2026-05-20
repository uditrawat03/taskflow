import json
import shutil
import datetime
from pathlib import Path

from ..config import DATA_FILE, DATE_FMT
from ..errors import StorageError



# ─── Core Operations ──────────────────────────────────────


def save_tasks(tasks: list, filepath: Path = DATA_FILE) -> None:
    """
    Save a list of task dictionaries to a JSON file.

    Uses an atomic write pattern — writes to a .tmp file first, then
    renames it over the target file so the data file is never left
    in a partially-written state.

    Args:
        tasks    (list): List of task dictionaries to persist.
        filepath (Path): Destination JSON file. Defaults to DATA_FILE.

    Raises:
        StorageError: If the file cannot be written.
    """
    # Ensure the data directory exists
    filepath.parent.mkdir(parents=True, exist_ok=True)

    tmp_path = filepath.with_suffix(".tmp")
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(tasks, f, indent=2, ensure_ascii=False)
        tmp_path.rename(filepath)  # atomic replace on most filesystems
    except (OSError, TypeError) as e:
        # Clean up temp file if it was created
        if tmp_path.exists():
            tmp_path.unlink()
        raise StorageError(f"Could not save tasks to '{filepath}': {e}") from e


def load_tasks(filepath: Path = DATA_FILE) -> list:
    """
    Load task dictionaries from a JSON file.

    Returns an empty list if the file does not exist yet (first run).

    Args:
        filepath (Path): Source JSON file. Defaults to DATA_FILE.

    Returns:
        list: List of task dictionaries loaded from the file.

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
            f"(line {e.lineno}, col {e.colno}): {e.msg}"
        ) from e
    except OSError as e:
        raise StorageError(f"Could not read storage file '{filepath}': {e}") from e

    if not isinstance(data, list):
        raise StorageError(
            f"Storage file has unexpected format: "
            f"expected a JSON array, got {type(data).__name__}."
        )

    return data


def load_tasks_safe(filepath: Path = DATA_FILE) -> tuple[list, str | None]:
    """
    Load tasks without raising — returns (tasks, error_message).

    Use in entry points where you want to handle errors inline rather
    than propagating exceptions up the call stack.

    Args:
        filepath (Path): Source JSON file. Defaults to DATA_FILE.

    Returns:
        tuple: (task_list, None) on success,
               ([], error_message_string) on failure.
    """
    try:
        tasks = load_tasks(filepath)
        return tasks, None
    except StorageError as e:
        return [], str(e)


def get_next_id(tasks: list) -> int:
    """
    Calculate the next available task ID from a loaded task list.

    Finds the maximum existing ID and adds 1. Returns 1 if the list
    is empty.

    Args:
        tasks (list): List of task dictionaries (must have 'id' key).

    Returns:
        int: The next available task ID.
    """
    return max((t.get("id", 0) for t in tasks), default=0) + 1


# ─── Backup ───────────────────────────────────────────────


def backup_tasks(filepath: Path = DATA_FILE) -> bool:
    """
    Create a timestamped backup copy of the storage file.

    The backup is saved in the same directory as the original,
    with a timestamp appended to the filename.

    Args:
        filepath (Path): Path to the file to back up.

    Returns:
        bool: True if the backup was created, False if the source
              file does not exist.
    """
    if not filepath.exists():
        print("  ✗ No storage file to back up.")
        return False

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{filepath.stem}_backup_{timestamp}{filepath.suffix}"
    backup_path = filepath.parent / backup_name

    try:
        shutil.copy2(filepath, backup_path)
        print(f"  ✓ Backup saved: {backup_path.name}")
        return True
    except OSError as e:
        print(f"  ✗ Backup failed: {e}")
        return False


# ─── Metadata ─────────────────────────────────────────────


def get_storage_info(filepath: Path = DATA_FILE) -> dict:
    """
    Return metadata about the storage file.

    Args:
        filepath (Path): Path to the storage file.

    Returns:
        dict: File metadata — exists, filepath, size_bytes, last_modified.
              If file does not exist, only 'exists': False is set.
    """
    if not filepath.exists():
        return {"exists": False}

    stat = filepath.stat()
    return {
        "exists": True,
        "filepath": str(filepath.resolve()),
        "size_bytes": stat.st_size,
        "last_modified": datetime.datetime.fromtimestamp(stat.st_mtime).strftime(
            DATE_FMT
        ),
    }
