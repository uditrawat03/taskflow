# Cross-cutting decorators
from __future__ import annotations
import time, logging, functools, warnings
from typing import Callable

logger = logging.getLogger(__name__)
__all__ = ["timer","retry","validate_non_empty","validate_tasks_arg","log_call","deprecated"]


def timer(label: str = "", log: bool = False) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            name    = label or func.__name__
            start   = time.perf_counter()
            result  = func(*args, **kwargs)
            elapsed = time.perf_counter() - start
            msg     = f"[timer] {name}: {elapsed:.4f}s"
            if log: logger.debug(msg)
            else:   print(f"  ⏱  {msg}")
            return result
        return wrapper
    return decorator


def retry(times: int = 3, delay: float = 1.0, backoff: float = 2.0,
          exceptions: tuple = (Exception,)) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay; last_exc = None
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exc = e
                    if attempt < times:
                        logger.warning("[retry] %s failed (%d/%d): %s. Retrying in %.1fs...",
                                       func.__name__, attempt, times, e, current_delay)
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error("[retry] %s failed after %d attempts.", func.__name__, times)
            raise last_exc
        return wrapper
    return decorator


def validate_non_empty(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(tasks, *args, **kwargs):
        if not tasks:
            print(f"\n  ✗ No tasks available for '{func.__name__}'. Add a task first.\n")
            return None
        return func(tasks, *args, **kwargs)
    return wrapper


def validate_tasks_arg(func: Callable) -> Callable:
    from .core.task import Task
    @functools.wraps(func)
    def wrapper(tasks, *args, **kwargs):
        if not isinstance(tasks, list):
            raise TypeError(f"{func.__name__} expects a list, got {type(tasks).__name__}")
        non_tasks = [t for t in tasks if not isinstance(t, Task)]
        if non_tasks:
            raise TypeError(f"{func.__name__} requires Task objects. Found: {[type(t).__name__ for t in non_tasks]}")
        return func(tasks, *args, **kwargs)
    return wrapper


def log_call(level: str = "debug") -> Callable:
    _map = {"debug": logger.debug, "info": logger.info, "warning": logger.warning}
    log_fn = _map.get(level, logger.debug)
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            parts = []
            if args:   parts.append(f"args={args!r}")
            if kwargs: parts.append(f"kwargs={kwargs!r}")
            log_fn(f"[call] {func.__name__}({', '.join(parts)})")
            result = func(*args, **kwargs)
            log_fn(f"[return] {func.__name__} → {result!r}")
            return result
        return wrapper
    return decorator


def deprecated(message: str = "") -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warn_msg = f"{func.__name__} is deprecated."
            if message: warn_msg += f" {message}"
            warnings.warn(warn_msg, DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)
        return wrapper
    return decorator