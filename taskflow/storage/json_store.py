# JSON-based task persistence. Day 09/12.
from __future__ import annotations
import json, shutil, datetime
from pathlib import Path
from ..config import DATE_FMT
from ..errors import StorageError
from ..core.task_factory import task_from_dict
from ..core.task import Task

__all__ = ["save_tasks","load_tasks","load_tasks_safe",
           "backup_tasks","get_next_id","get_storage_info"]


def save_tasks(tasks: list, filepath: Path | None = None) -> None:
    from ..env_config import get_settings
    if filepath is None:
        filepath = get_settings().data_file
    filepath.parent.mkdir(parents=True, exist_ok=True)
    tmp = filepath.with_suffix(".tmp")
    try:
        data = [t.to_dict() if isinstance(t, Task) else t for t in tasks]
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        tmp.rename(filepath)
    except (OSError, TypeError) as e:
        if tmp.exists():
            tmp.unlink()
        raise StorageError(f"Could not save tasks: {e}") from e


def load_tasks(filepath: Path | None = None) -> list[Task]:
    from ..env_config import get_settings
    if filepath is None:
        filepath = get_settings().data_file
    if not filepath.exists():
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise StorageError(f"Storage file contains invalid JSON: {e}") from e
    except OSError as e:
        raise StorageError(f"Could not read storage file: {e}") from e
    if not isinstance(data, list):
        raise StorageError(f"Expected a JSON array, got {type(data).__name__}")
    return [task_from_dict(d) for d in data]


def load_tasks_safe(filepath: Path | None = None) -> tuple[list[Task], str | None]:
    try:
        return load_tasks(filepath), None
    except StorageError as e:
        return [], str(e)


def get_next_id(tasks: list) -> int:
    ids = [(t.id if isinstance(t, Task) else t.get("id", 0)) for t in tasks]
    return max(ids, default=0) + 1


def backup_tasks(filepath: Path | None = None) -> bool:
    from ..env_config import get_settings
    if filepath is None:
        filepath = get_settings().data_file
    if not filepath.exists():
        print("  ✗ No storage file to back up.")
        return False
    timestamp   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = filepath.parent / f"{filepath.stem}_backup_{timestamp}{filepath.suffix}"
    try:
        shutil.copy2(filepath, backup_path)
        print(f"  ✓ Backup saved: {backup_path.name}")
        return True
    except OSError as e:
        print(f"  ✗ Backup failed: {e}")
        return False


def get_storage_info(filepath: Path | None = None) -> dict:
    from ..env_config import get_settings
    if filepath is None:
        filepath = get_settings().data_file
    if not filepath.exists():
        return {"exists": False}
    stat = filepath.stat()
    return {
        "exists":        True,
        "filepath":      str(filepath.resolve()),
        "size_bytes":    stat.st_size,
        "last_modified": datetime.datetime.fromtimestamp(stat.st_mtime).strftime(DATE_FMT),
    }
