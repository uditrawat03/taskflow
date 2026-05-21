# taskflow/context.py
# TaskFlow AI — Custom context managers for safe, reversible operations.
#
# Context managers:
#   task_snapshot        — snapshot and restore task list on failure
#   timed_operation      — time a block and warn if slow
#   temporary_data_file  — backup file before risky operations
#   suppress_storage_errors — suppress StorageError with optional logging
#
# Version history:
#   Day 17 — initial implementation

import copy
import time
import shutil
import logging
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from .errors import StorageError

__all__ = [
    "task_snapshot",
    "timed_operation",
    "temporary_data_file",
    "suppress_storage_errors",
]

logger = logging.getLogger(__name__)


@contextmanager
def task_snapshot(tasks: list) -> Generator[list, None, None]:
    """
    Snapshot the task list on entry and restore it on exception.

    Allows safe "destructive" operations — if anything goes wrong inside
    the with block, the task list is automatically restored to its
    pre-operation state.

    Args:
        tasks (list): The task list to protect. Modified in place on restore.

    Yields:
        list: A deep copy of the task list (the snapshot itself).

    Example:
        with task_snapshot(tasks) as snapshot:
            tasks.clear()
            risky_bulk_operation(tasks)
        # If risky_bulk_operation raises, tasks is restored from snapshot.
    """
    snapshot = copy.deepcopy(tasks)
    try:
        yield snapshot
    except Exception as e:
        # Restore original state
        tasks.clear()
        tasks.extend(snapshot)
        print(f"\n  ⚠  Operation failed: {e}")
        print("  ✓ Task list restored from snapshot.\n")
        raise


@contextmanager
def timed_operation(
    label: str, warn_threshold: float = 1.0
) -> Generator[None, None, None]:
    """
    Time a block of code and print the elapsed time.

    If the block takes longer than warn_threshold seconds,
    a warning line is printed instead of the normal timing line.

    Args:
        label          (str)  : Human-readable label for the operation.
        warn_threshold (float): Seconds above which a warning is shown.

    Example:
        with timed_operation("Load tasks", warn_threshold=0.5):
            tasks = load_tasks()
    """
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
    """
    Back up a data file before a risky operation and restore on failure.

    Creates a `.backup` copy of filepath before yielding.
    On success, the backup is removed.
    On failure, the original file is restored from the backup.

    Args:
        filepath (Path): The data file to protect.

    Yields:
        Path: The original filepath (unchanged).

    Example:
        with temporary_data_file(DATA_FILE):
            dangerous_migration(DATA_FILE)
        # If migration fails, DATA_FILE is restored to its pre-migration state.
    """
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
        # Remove backup on success; leave it if we restored (for debugging)
        if backup_path.exists() and not restored:
            backup_path.unlink()


@contextmanager
def suppress_storage_errors(
    log: bool = True,
) -> Generator[None, None, None]:
    """
    Suppress StorageError exceptions, optionally logging them.

    Use when storage failure is non-critical and the app should continue.

    Args:
        log (bool): Log the suppressed error as a warning if True.

    Example:
        with suppress_storage_errors():
            save_tasks(tasks)   # if this fails, execution continues
    """
    try:
        yield
    except StorageError as e:
        if log:
            logger.warning(f"[suppress] StorageError suppressed: {e}")
