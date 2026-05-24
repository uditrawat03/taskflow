# Context managers for safe operations.
from __future__ import annotations
import copy, time, shutil, logging
from contextlib import contextmanager
from pathlib import Path
from typing import Generator
from .errors import StorageError

__all__ = ["task_snapshot","timed_operation","temporary_data_file","suppress_storage_errors"]
logger = logging.getLogger(__name__)


@contextmanager
def task_snapshot(tasks: list) -> Generator[list, None, None]:
    """Snapshot task list on entry; restore on exception."""
    snapshot = copy.deepcopy(tasks)
    try:
        yield snapshot
    except Exception as e:
        tasks.clear()
        tasks.extend(snapshot)
        print(f"\n  ⚠  Operation failed: {e}")
        print("  ✓ Task list restored from snapshot.\n")
        raise


@contextmanager
def timed_operation(label: str, warn_threshold: float = 1.0) -> Generator[None, None, None]:
    """Time a block; warn if it exceeds threshold."""
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        if elapsed >= warn_threshold:
            print(f"  ⚠  [{label}] took {elapsed:.3f}s (threshold: {warn_threshold}s)")
        else:
            print(f"  ⏱  [{label}] completed in {elapsed:.3f}s")


@contextmanager
def temporary_data_file(filepath: Path) -> Generator[Path, None, None]:
    """Backup data file; restore on failure."""
    backup_path = filepath.with_suffix(".backup")
    restored = False
    if filepath.exists():
        shutil.copy2(filepath, backup_path)
    try:
        yield filepath
    except Exception as e:
        if backup_path.exists():
            shutil.copy2(backup_path, filepath)
            restored = True
            print(f"\n  ✓ Data file restored from backup after error: {e}\n")
        raise
    finally:
        if backup_path.exists() and not restored:
            backup_path.unlink()


@contextmanager
def suppress_storage_errors(log: bool = True) -> Generator[None, None, None]:
    """Suppress StorageError; optionally log it."""
    try:
        yield
    except StorageError as e:
        if log:
            logger.warning("[suppress] StorageError suppressed: %s", e)