import os
import logging
from pathlib import Path
from dataclasses import dataclass, field

__all__ = ["Settings", "get_settings"]

logger = logging.getLogger(__name__)

#  Project root 
# __file__ is taskflow/env_config.py → .parent is taskflow/ → .parent is root
_PROJECT_ROOT = Path(__file__).parent.parent


def _load_dotenv() -> None:
    """Load .env file into os.environ if python-dotenv is installed."""
    try:
        from dotenv import load_dotenv

        env_path = _PROJECT_ROOT / ".env"
        if env_path.exists():
            load_dotenv(env_path, override=False)
            logger.debug(".env loaded from %s", env_path)
        else:
            logger.debug("No .env file found at %s", env_path)
    except ImportError:
        logger.debug(
            "python-dotenv not installed — skipping .env load. "
            "Install with: pip install python-dotenv"
        )


def _get(key: str, default: str = "") -> str:
    """Read an env var, returning default if not set or empty."""
    return os.environ.get(key, default).strip() or default


def _get_int(key: str, default: int) -> int:
    """Read an env var as int, returning default on parse error."""
    raw = os.environ.get(key, "")
    try:
        return int(raw)
    except ValueError, TypeError:
        if raw:
            logger.warning(
                "Invalid int for %s=%r — using default %d", key, raw, default
            )
        return default


def _get_float(key: str, default: float) -> float:
    """Read an env var as float, returning default on parse error."""
    raw = os.environ.get(key, "")
    try:
        return float(raw)
    except ValueError, TypeError:
        if raw:
            logger.warning(
                "Invalid float for %s=%r — using default %f", key, raw, default
            )
        return default


def _get_bool(key: str, default: bool) -> bool:
    """
    Read an env var as bool.

    Truthy strings: "1", "true", "yes", "on"  (case-insensitive)
    Everything else is falsy.
    """
    raw = os.environ.get(key, "").strip().lower()
    if not raw:
        return default
    return raw in {"1", "true", "yes", "on"}


def _get_path(key: str, default: Path) -> Path:
    """Read an env var as a Path, resolved relative to project root."""
    raw = os.environ.get(key, "")
    if not raw:
        return default
    p = Path(raw)
    return p if p.is_absolute() else (_PROJECT_ROOT / p).resolve()


@dataclass(frozen=True)
class Settings:
    """
    Immutable settings object populated from environment variables.

    Using a frozen dataclass means the settings cannot be accidentally
    mutated after initialisation.

    Attributes mirror the environment variable names without the
    TASKFLOW_ prefix, lowercased.
    """

    #  User ─
    user_name: str = "User"
    user_plan: str = "free"
    user_latitude: float = 28.6139
    user_longitude: float = 77.2090
    user_location: str = "Delhi, IN"

    #  Storage ─
    data_dir: Path = field(default_factory=lambda: _PROJECT_ROOT / "data")
    data_file: Path = field(
        default_factory=lambda: _PROJECT_ROOT / "data" / "taskflow_tasks.json"
    )

    #  Logging ─
    log_level: str = "INFO"
    log_dir: Path = field(default_factory=lambda: _PROJECT_ROOT / "logs")
    log_to_file: bool = True
    log_to_console: bool = True

    #  Features 
    weather_enabled: bool = True
    debug_mode: bool = False

    #  AI (Phase 4) 
    anthropic_api_key: str = ""
    openai_api_key: str = ""

    def is_debug(self) -> bool:
        """Return True if debug mode is active."""
        return self.debug_mode or self.log_level.upper() == "DEBUG"

    def has_ai_key(self) -> bool:
        """Return True if at least one AI API key is configured."""
        return bool(self.anthropic_api_key or self.openai_api_key)

    def __repr__(self) -> str:
        """Safe repr — never show secrets."""
        return (
            f"Settings(user={self.user_name!r}, plan={self.user_plan!r}, "
            f"log_level={self.log_level!r}, "
            f"has_ai_key={self.has_ai_key()})"
        )


# Module-level singleton — loaded once at import time
_settings: Settings | None = None


def get_settings(reload: bool = False) -> Settings:
    """
    Return the application settings singleton.

    Loads .env on first call. Subsequent calls return the cached instance
    unless reload=True is passed.

    Args:
        reload (bool): Force a fresh load from the environment.

    Returns:
        Settings: Immutable settings object.
    """
    global _settings

    if _settings is not None and not reload:
        return _settings

    _load_dotenv()

    data_dir = _get_path("TASKFLOW_DATA_DIR", _PROJECT_ROOT / "data")

    _settings = Settings(
        user_name=_get("TASKFLOW_USER_NAME", "User"),
        user_plan=_get("TASKFLOW_USER_PLAN", "free").lower(),
        user_latitude=_get_float("TASKFLOW_LATITUDE", 28.6139),
        user_longitude=_get_float("TASKFLOW_LONGITUDE", 77.2090),
        user_location=_get("TASKFLOW_LOCATION", "Delhi, IN"),
        data_dir=data_dir,
        data_file=data_dir / _get("TASKFLOW_DATA_FILENAME", "taskflow_tasks.json"),
        log_level=_get("TASKFLOW_LOG_LEVEL", "INFO").upper(),
        log_dir=_get_path("TASKFLOW_LOG_DIR", _PROJECT_ROOT / "logs"),
        log_to_file=_get_bool("TASKFLOW_LOG_FILE", True),
        log_to_console=_get_bool("TASKFLOW_LOG_CONSOLE", True),
        weather_enabled=_get_bool("TASKFLOW_WEATHER", True),
        debug_mode=_get_bool("TASKFLOW_DEBUG", False),
        # Secrets — read from env only, no defaults
        anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
        openai_api_key=os.environ.get("OPENAI_API_KEY", ""),
    )

    logger.debug("Settings loaded: %s", _settings)
    return _settings
