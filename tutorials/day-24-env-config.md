# Day 24 — Environment Configuration & Secrets

> **Series:** Python & AI Engineering — Zero to Production
> **Phase:** 2 — Real Engineering
> **Python Version:** 3.14
> **Project:** TaskFlow AI — 12-factor config, .env files, secrets management

---

## Learning Objective

By the end of today, TaskFlow AI will read all environment-specific values — user name, data directory, API keys, log level — from environment variables and `.env` files rather than hardcoded constants. You will understand the 12-factor app methodology, implement a layered config system, and resolve TD-005. The app will be fully configurable for any environment without changing source code.

---

## What We Build Today

A `taskflow/env_config.py` module that loads configuration from environment variables with sensible defaults, replacing hardcoded values in `config.py`.

```bash
# .env file — different per environment
TASKFLOW_USER_NAME=Udit
TASKFLOW_USER_PLAN=premium
TASKFLOW_DATA_DIR=./data
TASKFLOW_LOG_LEVEL=DEBUG
TASKFLOW_LATITUDE=28.6139
TASKFLOW_LONGITUDE=77.2090
TASKFLOW_LOCATION=Delhi, IN

# Secrets (never committed)
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# Running the app picks up .env automatically
python run.py

# Running in production with env vars set directly
TASKFLOW_USER_NAME=Priya TASKFLOW_LOG_LEVEL=WARNING python run.py
```

---

## Concepts Covered

- The 12-factor app methodology — specifically Factor III (Config)
- `os.environ` — reading environment variables
- `python-dotenv` — loading `.env` files automatically
- Layered configuration — env vars override `.env`, which overrides defaults
- Type-safe config loading — converting string env vars to the right type
- `.env.example` — documenting required variables without exposing secrets
- `pydantic-settings` — modern type-safe settings management
- Secret management patterns — never log secrets, never commit secrets
- Multi-environment setup — dev, staging, production
- Updating `config.py` to use `env_config.py`

---

## Full Tutorial

### The Problem with Hardcoded Config

The current `config.py` has values like:

```python
USER_NAME  = "Udit"
USER_PLAN  = "free"
DATA_FILE  = BASE_DIR / "data" / "taskflow_tasks.json"
```

These are fine for a single developer. In the real world:
- Different users need different `USER_NAME`
- Different environments (dev/staging/prod) need different `DATA_FILE`
- API keys must never be in source code
- Docker containers need config injected at runtime

The solution: **environment variables** — the universal, secure, runtime-configurable mechanism supported by every language, OS, and deployment platform.

---

### Factor III — Config

The **12-factor app** is a methodology for building modern, deployable software. Factor III states:

> "Store config in the environment. An app's config is everything that is likely to vary between deploys (staging, production, developer environments). Config should be strictly separated from code."

**Signs that config is NOT properly separated from code:**
- Constants that differ between environments are in source files
- Credentials are checked into the repository
- You need to edit files to deploy to a different environment

**The correct pattern:**
- Defaults in code for everything that is safe to have a default
- Environment variables override defaults for anything environment-specific
- Secrets live only in environment variables — never in code or `.env` committed to git

---

### `os.environ` — Reading Environment Variables

```python
import os

# Read a variable — returns None if not set
name = os.environ.get("TASKFLOW_USER_NAME")

# Read with a default
name = os.environ.get("TASKFLOW_USER_NAME", "User")

# Read and convert to int
limit = int(os.environ.get("MAX_TASKS", "10"))

# Read and convert to bool
debug = os.environ.get("DEBUG", "false").lower() == "true"

# Read required variable — raise if missing
api_key = os.environ["ANTHROPIC_API_KEY"]   # KeyError if not set
```

---

### `python-dotenv` — Loading `.env` Files

`python-dotenv` reads a `.env` file and loads its contents into `os.environ`. This lets you store local dev config in a `.env` file without setting environment variables manually in every shell session.

```bash
pip install python-dotenv
```

```python
from dotenv import load_dotenv

# Load .env from the current directory (or a specified path)
load_dotenv()   # call this BEFORE reading os.environ

# Now os.environ contains everything from .env
import os
name = os.environ.get("TASKFLOW_USER_NAME", "User")
```

**`load_dotenv()` does NOT override existing environment variables by default.** This means real environment variables (set in the shell or by Docker) always take precedence over `.env`. This is the correct priority order.

---

### Building `taskflow/env_config.py`

```python
# taskflow/env_config.py
# TaskFlow AI — Environment-based configuration loader.
#
# Loads values from (in priority order, highest first):
#   1. Real environment variables (set in shell / Docker / CI)
#   2. .env file in the project root
#   3. Hardcoded defaults in this module
#
# Call get_settings() to obtain a Settings object with all values.
# Every other module should import from here rather than os.environ directly.
#
# Version history:
#   Day 24 — initial implementation; resolves TD-005

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
    except (ValueError, TypeError):
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
    except (ValueError, TypeError):
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
    user_name:      str   = "User"
    user_plan:      str   = "free"
    user_latitude:  float = 28.6139
    user_longitude: float = 77.2090
    user_location:  str   = "Delhi, IN"

    #  Storage ─
    data_dir:  Path = field(default_factory=lambda: _PROJECT_ROOT / "data")
    data_file: Path = field(default_factory=lambda: _PROJECT_ROOT / "data" / "taskflow_tasks.json")

    #  Logging ─
    log_level:    str  = "INFO"
    log_dir:      Path = field(default_factory=lambda: _PROJECT_ROOT / "logs")
    log_to_file:  bool = True
    log_to_console: bool = True

    #  Features 
    weather_enabled: bool = True
    debug_mode:      bool = False

    #  AI (Phase 4) 
    anthropic_api_key: str = ""
    openai_api_key:    str = ""

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
        user_name      = _get("TASKFLOW_USER_NAME",  "User"),
        user_plan      = _get("TASKFLOW_USER_PLAN",  "free").lower(),
        user_latitude  = _get_float("TASKFLOW_LATITUDE",  28.6139),
        user_longitude = _get_float("TASKFLOW_LONGITUDE", 77.2090),
        user_location  = _get("TASKFLOW_LOCATION",   "Delhi, IN"),

        data_dir  = data_dir,
        data_file = data_dir / _get("TASKFLOW_DATA_FILENAME", "taskflow_tasks.json"),

        log_level      = _get("TASKFLOW_LOG_LEVEL",   "INFO").upper(),
        log_dir        = _get_path("TASKFLOW_LOG_DIR", _PROJECT_ROOT / "logs"),
        log_to_file    = _get_bool("TASKFLOW_LOG_FILE",    True),
        log_to_console = _get_bool("TASKFLOW_LOG_CONSOLE", True),

        weather_enabled = _get_bool("TASKFLOW_WEATHER", True),
        debug_mode      = _get_bool("TASKFLOW_DEBUG",   False),

        # Secrets — read from env only, no defaults
        anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY",  ""),
        openai_api_key    = os.environ.get("OPENAI_API_KEY",     ""),
    )

    logger.debug("Settings loaded: %s", _settings)
    return _settings
```

---

### Updating `config.py` to Use `env_config.py`

`config.py` keeps all compile-time constants (validation sets, format strings, API URLs). Dynamic, environment-specific values now come from `env_config.py`:

```python
# taskflow/config.py — updated for Day 24
# Static constants only. Runtime values in env_config.py.

from pathlib import Path

APP_NAME = "TaskFlow AI"
VERSION  = "1.1.0"

# Validation sets — never vary by environment
VALID_PRIORITIES: set[str] = {"high", "medium", "low"}
VALID_CATEGORIES: set[str] = {"work", "personal", "health", "learning", "other"}
VALID_PLANS:      set[str] = {"free", "premium", "enterprise"}

PLAN_LIMITS: dict[str, int] = {
    "free":       10,
    "premium":    100,
    "enterprise": 10_000,
}

# Format strings — never vary by environment
DATE_FMT     = "%Y-%m-%d %H:%M"
LOG_DATE_FMT = "%Y-%m-%dT%H:%M:%SZ"

# API constants — not secrets, but unlikely to change
WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"
WEATHER_TIMEOUT = 10    # seconds

# Behaviour constants
OVERDUE_THRESHOLD_DAYS = 7
MAX_TITLE_LENGTH       = 200
WEATHER_CACHE_TTL      = 600   # seconds

# Project root — needed by env_config and storage
BASE_DIR = Path(__file__).parent.parent
```

---

### Updating `main.py` to Use Settings

```python
# taskflow/main.py — updated for Day 24

def main() -> None:
    """Application entry point."""
    import sys
    from .env_config      import get_settings
    from .logging_config  import setup_logging

    args     = sys.argv[1:]
    settings = get_settings()

    # Configure logging from settings
    setup_logging(
        level      = "DEBUG" if "--debug" in args else settings.log_level,
        log_dir    = settings.log_dir if settings.log_to_file else None,
        json_file  = settings.log_to_file,
        console    = settings.log_to_console,
    )

    import logging
    logger = logging.getLogger(__name__)
    logger.info(
        "TaskFlow AI starting",
        extra={"version": VERSION, "user": settings.user_name}
    )

    # Load tasks using path from settings
    from .storage.json_store import load_tasks_safe, backup_tasks
    print()
    print("  Loading tasks...", end=" ", flush=True)
    tasks, load_error = load_tasks_safe(settings.data_file)

    if load_error:
        print(f"\n  ⚠  {load_error}")
        logger.error("Task load failed: %s", load_error)
        print("  Creating backup and starting fresh.\n")
        try:
            backup_tasks(settings.data_file)
        except Exception:
            pass
        tasks = []
    else:
        count = len(tasks)
        print(f"✓ {count} task{'s' if count != 1 else ''} loaded.")
        logger.info("Tasks loaded", extra={"count": count})

    # Weather
    weather = None
    if settings.weather_enabled and "--no-weather" not in args:
        try:
            from .integrations.weather import fetch_weather
            weather = fetch_weather(
                settings.user_latitude,
                settings.user_longitude,
                settings.user_location,
            )
        except Exception as e:
            logger.warning("Weather fetch failed: %s", e)

    from .display.renderer import display_header
    display_header(weather)

    from .shell import run_interactive_shell
    run_interactive_shell(tasks)
```

---

### The `.env.example` File

Document every variable without committing real values:

```bash
# .env.example
# Copy to .env and fill in your values.
# NEVER commit .env to git.

#  User settings ─
TASKFLOW_USER_NAME=YourName
TASKFLOW_USER_PLAN=free

#  Location for weather 
TASKFLOW_LATITUDE=28.6139
TASKFLOW_LONGITUDE=77.2090
TASKFLOW_LOCATION=Delhi, IN

#  Storage ─
TASKFLOW_DATA_DIR=./data
TASKFLOW_DATA_FILENAME=taskflow_tasks.json

#  Logging ─
TASKFLOW_LOG_LEVEL=INFO
TASKFLOW_LOG_DIR=./logs
TASKFLOW_LOG_FILE=true
TASKFLOW_LOG_CONSOLE=true

#  Features 
TASKFLOW_WEATHER=true
TASKFLOW_DEBUG=false

#  AI API keys (Phase 4) — NEVER share these ─
# ANTHROPIC_API_KEY=sk-ant-...
# OPENAI_API_KEY=sk-...
```

---

### Multi-Environment Pattern

For professional projects, maintain multiple env files:

```
.env              ← personal local dev (git-ignored)
.env.example      ← template (committed)
.env.test         ← test environment overrides (committed — no secrets)
.env.production   ← production template (committed — no values)
```

`.env.test` example:

```bash
# .env.test — used by pytest
TASKFLOW_USER_NAME=TestUser
TASKFLOW_DATA_DIR=./tests/data
TASKFLOW_LOG_LEVEL=WARNING
TASKFLOW_LOG_FILE=false
TASKFLOW_WEATHER=false
```

Load it in `conftest.py`:

```python
# tests/conftest.py — updated for Day 24
import pytest
from dotenv import load_dotenv
from pathlib import Path

# Load test environment before any taskflow imports
load_dotenv(Path(__file__).parent.parent / ".env.test", override=True)
```

---

## Exercises

**Exercise 1 — Create your `.env` file.**
Copy `.env.example` to `.env`. Fill in your actual name, location coordinates, and preferred log level. Run `python run.py` and verify the greeting shows your name. Run `TASKFLOW_USER_NAME=TestOverride python run.py` and verify the shell variable overrides the `.env` value.

**Exercise 2 — Validate settings on startup.**
Add a `validate()` method to `Settings` that checks: `user_plan` is one of the valid plans, `log_level` is a valid logging level, `data_dir` parent exists or can be created, `user_latitude` is between -90 and 90, `user_longitude` is between -180 and 180. Call it in `main()` and raise a clear error if validation fails.

**Exercise 3 — Test environment isolation.**
Create `.env.test` with `TASKFLOW_DATA_DIR=./tests/data`. Update `conftest.py` to load it. Write a test that verifies `get_settings().data_dir` points to `tests/data` when running under pytest. Verify the test environment does not interfere with the dev `.env`.

**Exercise 4 — Secret safety check.**
Write a function `check_no_secrets_in_logs()` that opens `logs/taskflow.log`, parses each JSON line, and raises `AssertionError` if any line contains a string matching `sk-ant-` or `sk-` (OpenAI key patterns). Add it as a post-test check in `conftest.py`. Then deliberately log a fake key and watch the check catch it.

**Exercise 5 — `pydantic-settings` rewrite.**
Install `pydantic-settings` (`pip install pydantic-settings`). Rewrite `env_config.py` using Pydantic's `BaseSettings`:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    taskflow_user_name: str     = "User"
    taskflow_user_plan: str     = "free"
    taskflow_log_level: str     = "INFO"
    anthropic_api_key:  str     = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

settings = Settings()
```

Compare: what does Pydantic give you for free that the manual implementation requires you to write? Type coercion, validation, nested models, aliases?

**Exercise 6 (stretch) — Docker environment variables.**
Create a minimal `Dockerfile` for TaskFlow AI. Pass configuration as `--env` flags to `docker run`. Verify the app picks up the Docker environment variables correctly:

```dockerfile
FROM python:3.14-slim
WORKDIR /app
COPY . .
RUN pip install -e .
CMD ["python", "run.py", "--no-weather"]
```

```bash
docker build -t taskflow .
docker run --env TASKFLOW_USER_NAME=DockerUser \
           --env TASKFLOW_LOG_LEVEL=DEBUG \
           --env TASKFLOW_WEATHER=false \
           taskflow
```

This previews Day 53's containerisation work.

---

## Checkpoint

Before moving to Day 25:

- [ ] `taskflow/env_config.py` exists with `Settings` dataclass and `get_settings()`
- [ ] `.env` file created locally (git-ignored)
- [ ] `.env.example` committed with all variables documented
- [ ] `.env.test` created for test environment
- [ ] `config.py` contains only static constants — no user-specific values
- [ ] `main.py` reads all dynamic config from `get_settings()`
- [ ] `USER_NAME` now reads from `TASKFLOW_USER_NAME` env var — TD-005 resolved
- [ ] `conftest.py` loads `.env.test` before taskflow imports
- [ ] No secrets appear in any committed file
- [ ] No secrets appear in log files (verified manually)

---

## Common Errors on Day 24

**Committing `.env` to git:**

```bash
git add .env    # ❌ exposes all secrets to anyone with repo access
```

Your `.gitignore` must contain `.env`. Verify: `git check-ignore -v .env` should output a match. If you have already committed `.env`, remove it with `git rm --cached .env` and rotate any exposed keys immediately.

**`os.environ.get()` returns `None` vs empty string:**

```python
os.environ.get("MISSING_KEY")          # returns None
os.environ.get("MISSING_KEY", "")      # returns ""
os.environ.get("MISSING_KEY", "default")  # returns "default"
```

Always provide a default to `.get()`. Never use the return value without checking for `None` first.

**`load_dotenv()` called after `os.environ` already read:**

```python
import os
name = os.environ.get("TASKFLOW_USER_NAME")   # ❌ read before .env loaded
from dotenv import load_dotenv
load_dotenv()
```

`load_dotenv()` must be called before any `os.environ` reads. Put it at the very top of `env_config.py` and call `get_settings()` before anything else in `main.py`.

**Settings singleton not reloaded in tests:**

```python
# ❌ Test uses cached settings from previous test
settings = get_settings()

# ✅ Force reload in tests
settings = get_settings(reload=True)
```

In `conftest.py`, call `get_settings(reload=True)` after loading `.env.test` to ensure the test settings are fresh.

---

## What's Coming

On **Day 25** we write a real test suite — the most important engineering practice in Phase 2. `pytest` fundamentals, test structure, fixtures, parametrize, and building toward 60% coverage on `core/` and `storage/`. After today's solid foundation of clean code, logging, and config, tests will feel natural rather than bolted on.