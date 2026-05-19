from pathlib import Path
import datetime

# ─── Configuration ────────────────────────────────────────
BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "taskflow_tasks.txt"
SEPARATOR = "|"
DATE_FMT = "%Y-%m-%d %H:%M"


# ─── Serialization ────────────────────────────────────────


def task_to_line(task: dict) -> str:
    """
    Convert a task dictionary to a single line string for file storage.

    Format: id|title|priority|category|status|done|created_at

    Args:
        task (dict): A task dictionary.

    Returns:
        str: A pipe-separated string representation of the task.
    """
    return SEPARATOR.join(
        [
            str(task["id"]),
            task["title"],
            task["priority"],
            task["category"],
            task["status"],
            str(task["done"]),
            task["created_at"],
        ]
    )


def line_to_task(line: str) -> dict | None:
    """
    Convert a stored line back into a task dictionary.

    Args:
        line (str): A pipe-separated line from the storage file.

    Returns:
        dict | None: A task dictionary, or None if the line is malformed.
    """
    line = line.strip()
    if not line:
        return None

    parts = line.split(SEPARATOR)
    if len(parts) != 7:
        print(f"  ⚠ Skipping malformed line: '{line}'")
        return None

    task_id, title, priority, category, status, done_str, created_at = parts

    return {
        "id": int(task_id),
        "title": title,
        "priority": priority,
        "category": category,
        "status": status,
        "done": done_str == "True",
        "created_at": created_at,
    }


# ─── File Operations ──────────────────────────────────────


def save_tasks(tasks: list, filepath: Path = DATA_FILE) -> bool:
    """
    Save all tasks to a text file.

    Each task is written as one pipe-separated line.
    Overwrites the file completely on each save.

    Args:
        tasks    (list): List of task dictionaries to save.
        filepath (Path): Path to the storage file.

    Returns:
        bool: True if save succeeded, False otherwise.
    """
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            for task in tasks:
                f.write(task_to_line(task) + "\n")
        return True
    except OSError as e:
        print(f"  ✗ Failed to save tasks: {e}")
        return False


def load_tasks(filepath: Path = DATA_FILE) -> list:
    """
    Load tasks from a text file.

    Returns an empty list if the file does not exist or cannot be read.

    Args:
        filepath (Path): Path to the storage file.

    Returns:
        list: List of task dictionaries loaded from file.
    """
    if not filepath.exists():
        return []

    tasks = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                task = line_to_task(line)
                if task is not None:
                    tasks.append(task)
    except OSError as e:
        print(f"  ✗ Failed to load tasks: {e}")
        return []

    return tasks


def get_next_id(tasks: list) -> int:
    """
    Calculate the next available task ID from the loaded task list.

    Args:
        tasks (list): List of task dictionaries.

    Returns:
        int: The next available ID (max existing ID + 1, or 1 if empty).
    """
    if not tasks:
        return 1
    return max(t["id"] for t in tasks) + 1


def backup_tasks(filepath: Path = DATA_FILE) -> bool:
    """
    Create a timestamped backup of the tasks file.

    Args:
        filepath (Path): Path to the storage file to back up.

    Returns:
        bool: True if backup succeeded, False otherwise.
    """
    if not filepath.exists():
        return False

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = filepath.parent / f"taskflow_tasks_backup_{timestamp}.txt"

    try:
        content = filepath.read_text(encoding="utf-8")
        backup_path.write_text(content, encoding="utf-8")
        print(f"  ✓ Backup saved: {backup_path.name}")
        return True
    except OSError as e:
        print(f"  ✗ Backup failed: {e}")
        return False


def get_storage_info(filepath: Path = DATA_FILE) -> dict:
    """
    Return metadata about the storage file.

    Args:
        filepath (Path): Path to the storage file.

    Returns:
        dict: File metadata — exists, size, last modified.
    """
    if not filepath.exists():
        return {"exists": False, "size_bytes": 0, "last_modified": None}

    stat = filepath.stat()
    return {
        "exists": True,
        "size_bytes": stat.st_size,
        "last_modified": datetime.datetime.fromtimestamp(stat.st_mtime).strftime(
            DATE_FMT
        ),
        "filepath": str(filepath),
    }
