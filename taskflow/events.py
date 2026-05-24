# taskflow/events.py — Event bus (Observer pattern). Day 29.
from __future__ import annotations
import logging
from collections import defaultdict
from typing import Callable, Any

logger = logging.getLogger(__name__)
__all__ = ["EventBus","Events","event_bus"]


class EventBus:
    """Simple synchronous event bus."""

    def __init__(self) -> None:
        self._handlers: dict[str, list[Callable[..., Any]]] = defaultdict(list)

    def on(self, event_name: str) -> Callable:
        def decorator(handler: Callable) -> Callable:
            self._handlers[event_name].append(handler)
            logger.debug("Registered handler '%s' for event '%s'", handler.__name__, event_name)
            return handler
        return decorator

    def subscribe(self, event_name: str, handler: Callable) -> None:
        self._handlers[event_name].append(handler)

    def unsubscribe(self, event_name: str, handler: Callable) -> None:
        try:
            self._handlers[event_name].remove(handler)
        except ValueError:
            logger.warning("Handler '%s' not found for event '%s'",
                           getattr(handler,"__name__",repr(handler)), event_name)

    def emit(self, event_name: str, *args: Any, **kwargs: Any) -> None:
        handlers = self._handlers.get(event_name, [])
        logger.debug("Emitting '%s' to %d handler(s)", event_name, len(handlers))
        for handler in handlers:
            try:
                handler(*args, **kwargs)
            except Exception as e:
                logger.error("Handler '%s' raised for event '%s': %s",
                             getattr(handler,"__name__",repr(handler)), event_name, e, exc_info=True)

    def handlers_for(self, event_name: str) -> list[Callable]:
        return list(self._handlers.get(event_name, []))

    def clear(self, event_name: str | None = None) -> None:
        if event_name:
            self._handlers.pop(event_name, None)
        else:
            self._handlers.clear()

    def __repr__(self) -> str:
        total = sum(len(h) for h in self._handlers.values())
        return f"EventBus({len(self._handlers)} events, {total} handlers)"


class Events:
    """Canonical event name constants."""
    TASK_ADDED    = "task.added"
    TASK_DONE     = "task.done"
    TASK_REMOVED  = "task.removed"
    TASK_RENAMED  = "task.renamed"
    LIMIT_REACHED = "task.limit_reached"
    STORAGE_SAVED = "storage.saved"
    STORAGE_ERROR = "storage.error"


event_bus = EventBus()
