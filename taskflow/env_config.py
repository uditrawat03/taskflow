from __future__ import annotations
import os, logging
from pathlib import Path
from dataclasses import dataclass, field

__all__ = ["Settings", "get_settings"]
logger = logging.getLogger(__name__)
_PROJECT_ROOT = Path(__file__).parent.parent


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv
        env_path = _PROJECT_ROOT / ".env"
        if env_path.exists():
            load_dotenv(env_path, override=False)
    except ImportError:
        pass


def _get(key: str, default: str = "") -> str:
    return os.environ.get(key, default).strip() or default

def _get_int(key: str, default: int) -> int:
    try:
        return int(os.environ.get(key, ""))
    except (ValueError, TypeError):
        return default

def _get_float(key: str, default: float) -> float:
    try:
        return float(os.environ.get(key, ""))
    except (ValueError, TypeError):
        return default

def _get_bool(key: str, default: bool) -> bool:
    raw = os.environ.get(key, "").strip().lower()
    if not raw:
        return default
    return raw in {"1", "true", "yes", "on"}

def _get_path(key: str, default: Path) -> Path:
    raw = os.environ.get(key, "")
    if not raw:
        return default
    p = Path(raw)
    return p if p.is_absolute() else (_PROJECT_ROOT / p).resolve()


@dataclass(frozen=True)
class Settings:
    user_name:       str   = "Udit"
    user_plan:       str   = "free"
    user_latitude:   float = 28.6139
    user_longitude:  float = 77.2090
    user_location:   str   = "Delhi, IN"
    data_dir:        Path  = field(default_factory=lambda: _PROJECT_ROOT / "data")
    data_file:       Path  = field(default_factory=lambda: _PROJECT_ROOT / "data" / "taskflow_tasks.json")
    log_level:       str   = "INFO"
    log_dir:         Path  = field(default_factory=lambda: _PROJECT_ROOT / "logs")
    log_to_file:     bool  = True
    log_to_console:  bool  = True
    weather_enabled: bool  = True
    debug_mode:      bool  = False
    anthropic_api_key: str = ""
    openai_api_key:    str = ""
    repository_backend: str = "json"

    def is_debug(self) -> bool:
        return self.debug_mode or self.log_level.upper() == "DEBUG"

    def has_ai_key(self) -> bool:
        return bool(self.anthropic_api_key or self.openai_api_key)

    def __repr__(self) -> str:
        return (f"Settings(user={self.user_name!r}, plan={self.user_plan!r}, "
                f"log_level={self.log_level!r}, has_ai_key={self.has_ai_key()})")


_settings: Settings | None = None


def get_settings(reload: bool = False) -> Settings:
    global _settings
    if _settings is not None and not reload:
        return _settings
    _load_dotenv()
    data_dir = _get_path("TASKFLOW_DATA_DIR", _PROJECT_ROOT / "data")
    _settings = Settings(
        user_name        = _get("TASKFLOW_USER_NAME",  "Udit"),
        user_plan        = _get("TASKFLOW_USER_PLAN",  "free").lower(),
        user_latitude    = _get_float("TASKFLOW_LATITUDE",  28.6139),
        user_longitude   = _get_float("TASKFLOW_LONGITUDE", 77.2090),
        user_location    = _get("TASKFLOW_LOCATION",   "Delhi, IN"),
        data_dir         = data_dir,
        data_file        = data_dir / _get("TASKFLOW_DATA_FILENAME", "taskflow_tasks.json"),
        log_level        = _get("TASKFLOW_LOG_LEVEL",  "INFO").upper(),
        log_dir          = _get_path("TASKFLOW_LOG_DIR", _PROJECT_ROOT / "logs"),
        log_to_file      = _get_bool("TASKFLOW_LOG_FILE",    True),
        log_to_console   = _get_bool("TASKFLOW_LOG_CONSOLE", True),
        weather_enabled  = _get_bool("TASKFLOW_WEATHER", True),
        debug_mode       = _get_bool("TASKFLOW_DEBUG",   False),
        anthropic_api_key  = os.environ.get("ANTHROPIC_API_KEY",  ""),
        openai_api_key     = os.environ.get("OPENAI_API_KEY",     ""),
        repository_backend = _get("TASKFLOW_REPOSITORY", "json"),
    )
    return _settings
