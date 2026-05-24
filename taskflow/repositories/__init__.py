from __future__ import annotations
import logging
from pathlib import Path
from functools import lru_cache

from .base      import TaskRepository
from .json_repo import JsonTaskRepository
from ..env_config import get_settings

logger = logging.getLogger(__name__)

__all__ = ["TaskRepository", "JsonTaskRepository", "get_repository"]

# Registry — maps backend name to class
_BACKENDS: dict[str, type[TaskRepository]] = {
    "json": JsonTaskRepository,
    # "sqlite":   SqliteTaskRepository,   # added Day 34
    # "postgres": PostgresTaskRepository, # added Day 55
}


@lru_cache(maxsize=1)
def get_repository(backend: str | None = None) -> TaskRepository:
    """
    Return the application's task repository (singleton via lru_cache).

    The first call constructs and caches the repository.
    Subsequent calls return the same instance.

    Args:
        backend (str | None): Backend name — 'json', 'sqlite', 'postgres'.
                              Reads TASKFLOW_REPOSITORY env var if None.
                              Defaults to 'json'.

    Returns:
        TaskRepository: The configured repository instance.

    Raises:
        ValueError: If the backend name is not recognised.
    """
    settings = get_settings()
    chosen   = backend or getattr(settings, "repository_backend", "json")

    if chosen not in _BACKENDS:
        raise ValueError(
            f"Unknown repository backend '{chosen}'. "
            f"Available: {', '.join(_BACKENDS)}"
        )

    repo_class = _BACKENDS[chosen]
    repo       = repo_class(settings.data_file)

    logger.info(
        "Repository initialised",
        extra={"backend": chosen, "filepath": str(settings.data_file)}
    )
    return repo