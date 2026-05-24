# taskflow/repositories/__init__.py — Factory and public API.
from __future__ import annotations
import logging
from functools import lru_cache
from .base      import TaskRepository
from .json_repo import JsonTaskRepository

logger = logging.getLogger(__name__)
__all__ = ["TaskRepository","JsonTaskRepository","get_repository"]

_BACKENDS: dict[str, type[TaskRepository]] = {
    "json": JsonTaskRepository,
}


@lru_cache(maxsize=1)
def get_repository(backend: str | None = None) -> TaskRepository:
    """Return the singleton repository instance (cached after first call)."""
    from ..env_config import get_settings
    settings = get_settings()
    chosen   = backend or getattr(settings, "repository_backend", "json")
    if chosen not in _BACKENDS:
        raise ValueError(f"Unknown repository backend '{chosen}'. Available: {', '.join(_BACKENDS)}")
    repo = _BACKENDS[chosen](settings.data_file)
    logger.info("Repository initialised", extra={"backend": chosen})
    return repo
