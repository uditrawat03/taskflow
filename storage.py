import json
import datetime
import shutil
from pathlib import Path

# ─── Configuration ────────────────────────────────────────
BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "taskflow_tasks.json"
DATE_FMT = "%Y-%m-%d %H:%M"


def save_tasks(tasks: list, filepath: Path = DATA_FILE) -> bool:
    """
    Save all tasks to a JSON file.

    Uses an atomic write pattern — writes to a temp file first,
    then renames, so the data file is never left half-written.

    Args:
        tasks    (list): List of task dictionaries.
        filepath (Path): Destination JSON file path.

    Returns:
        bool: True if save succeeded, False otherwise.
    """
    tmp_path = filepath.with_suffix(".tmp")
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(tasks, f, indent=2, ensure_ascii=False)
        tmp_path.rename(filepath)  # atomic replace
        return True
    except (OSError, TypeError) as e:
        print(f"  ✗ Save failed: {e}")
        if tmp_path.exists():
            tmp_path.unlink()  # clean up temp file on failure
        return False


def load_tasks(filepath: Path = DATA_FILE) -> list:
    """
    Load tasks from a JSON file.

    Returns an empty list if the file does not exist or is corrupted.

    Args:
        filepath (Path): Source JSON file path.

    Returns:
        list: List of task dictionaries, or [] on failure.
    """
    if not filepath.exists():
        return []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            print("  ✗ Storage file is corrupted — expected a list.")
            return []
        return data
    except json.JSONDecodeError as e:
        print(f"  ✗ Storage file is invalid JSON: {e}")
        return []
    except OSError as e:
        print(f"  ✗ Could not read storage file: {e}")
        return []


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
