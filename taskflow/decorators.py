# taskflow/decorators.py
# TaskFlow AI — Cross-cutting decorator library.
#
# Decorators:
#   @timer           — measure execution time
#   @retry           — retry on failure with backoff
#   @validate_non_empty — guard commands against empty task lists
#   @validate_tasks_arg — type-check the tasks argument
#   @log_call        — log function entry and return value
#   @deprecated      — emit DeprecationWarning on every call
#
# Version history:
#   Day 17 — initial implementation

import time
import logging
import functools
import warnings
from typing import Callable

logger = logging.getLogger(__name__)

__all__ = [
    "timer",
    "retry",
    "validate_non_empty",
    "validate_tasks_arg",
    "log_call",
    "deprecated",
]


def timer(label: str = "", log: bool = False) -> Callable:
    """
    Measure and report the execution time of a function.

    Args:
        label (str) : Label for the output line. Defaults to function name.
        log   (bool): If True, use logger.debug instead of print.

    Example:
        @timer(label="Load tasks", log=True)
        def load_tasks(filepath): ...
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            name = label or func.__name__
            start = time.perf_counter()
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start
            msg = f"[timer] {name}: {elapsed:.4f}s"
            if log:
                logger.debug(msg)
            else:
                print(f"  ⏱  {msg}")
            return result

        return wrapper

    return decorator


def retry(
    times: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
) -> Callable:
    """
    Retry a function on failure with exponential backoff.

    Args:
        times      (int)  : Maximum number of attempts (default 3).
        delay      (float): Initial wait in seconds before first retry.
        backoff    (float): Multiplier applied to delay after each failure.
        exceptions (tuple): Exception types that trigger a retry.

    Example:
        @retry(times=3, delay=1.0, exceptions=(StorageError, OSError))
        def save_tasks(tasks): ...
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None

            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < times:
                        logger.warning(
                            f"[retry] {func.__name__} failed "
                            f"(attempt {attempt}/{times}): {e}. "
                            f"Retrying in {current_delay:.1f}s..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"[retry] {func.__name__} failed after {times} attempts."
                        )
            raise last_exception

        return wrapper

    return decorator


def validate_non_empty(func: Callable) -> Callable:
    """
    Guard a command function against an empty task list.

    Prints an error and returns early if the first argument (tasks) is empty.
    Use on command functions that require at least one task.

    Example:
        @validate_non_empty
        def cmd_done(tasks: list) -> None: ...
    """

    @functools.wraps(func)
    def wrapper(tasks, *args, **kwargs):
        if not tasks:
            print(
                f"\n  ✗ No tasks available for '{func.__name__}'. Add a task first.\n"
            )
            return None
        return func(tasks, *args, **kwargs)

    return wrapper


def validate_tasks_arg(func: Callable) -> Callable:
    """
    Validate that the first argument is a list of Task objects.

    Raises:
        TypeError: If tasks is not a list, or contains non-Task items.

    Example:
        @validate_tasks_arg
        def calculate_stats(tasks: list) -> dict: ...
    """
    from .core.task import Task

    @functools.wraps(func)
    def wrapper(tasks, *args, **kwargs):
        if not isinstance(tasks, list):
            raise TypeError(
                f"{func.__name__} expects a list, got {type(tasks).__name__}"
            )
        non_tasks = [t for t in tasks if not isinstance(t, Task)]
        if non_tasks:
            raise TypeError(
                f"{func.__name__} requires a list of Task objects. "
                f"Found: {[type(t).__name__ for t in non_tasks]}"
            )
        return func(tasks, *args, **kwargs)

    return wrapper


def log_call(level: str = "debug") -> Callable:
    """
    Log every call to a function — arguments and return value.

    Args:
        level (str): Logging level — 'debug', 'info', or 'warning'.

    Example:
        @log_call(level="info")
        def load_tasks(filepath): ...
    """
    _level_map = {
        "debug": logger.debug,
        "info": logger.info,
        "warning": logger.warning,
    }
    log_fn = _level_map.get(level, logger.debug)

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            parts = []
            if args:
                parts.append(f"args={args!r}")
            if kwargs:
                parts.append(f"kwargs={kwargs!r}")
            log_fn(f"[call] {func.__name__}({', '.join(parts)})")
            result = func(*args, **kwargs)
            log_fn(f"[return] {func.__name__} → {result!r}")
            return result

        return wrapper

    return decorator


def deprecated(message: str = "") -> Callable:
    """
    Mark a function as deprecated — emits DeprecationWarning on each call.

    Args:
        message (str): Additional guidance, e.g. what to use instead.

    Example:
        @deprecated("Use save_tasks() instead.")
        def old_save(tasks): ...
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warn_msg = f"{func.__name__} is deprecated."
            if message:
                warn_msg += f" {message}"
            warnings.warn(warn_msg, DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)

        return wrapper

    return decorator
