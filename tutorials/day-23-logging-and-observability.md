# Day 23 — Logging & Observability

> **Series:** Python & AI Engineering — Zero to Production
> **Phase:** 2 — Real Engineering
> **Python Version:** 3.14
> **Project:** TaskFlow AI — Replacing print() with professional logging

---

## Learning Objective

By the end of today, TaskFlow AI will have a production-grade logging system. You will understand Python's logging hierarchy, log levels, handlers, formatters, and structured JSON logging. Every module that currently uses `print()` for diagnostics will be replaced with proper logging — leaving `print()` only in `display/renderer.py` where it belongs.

---

## What We Build Today

A `taskflow/logging_config.py` module that configures the entire logging stack, plus structured log output for every significant application event.

```bash
# Console output (human-readable during development):
2025-05-19 14:32:01 INFO     taskflow.main       Loading tasks from data/taskflow_tasks.json
2025-05-19 14:32:01 INFO     taskflow.main       4 tasks loaded in 0.003s
2025-05-19 14:32:01 DEBUG    taskflow.integrations.weather  Cache hit — returning cached weather
2025-05-19 14:32:05 INFO     taskflow.display.commands      Task added: "Review PR" [high/work]
2025-05-19 14:32:08 WARNING  taskflow.storage.json_store    Save retried after OSError
2025-05-19 14:32:08 INFO     taskflow.storage.json_store    Tasks saved (4 tasks, 0.002s)

# JSON log file (machine-readable for production):
{"timestamp": "2025-05-19T14:32:01", "level": "INFO", "logger": "taskflow.main",
 "message": "Tasks loaded", "task_count": 4, "duration_ms": 3.1}
```

---

## Concepts Covered

- Python's logging hierarchy — root logger, named loggers, propagation
- Log levels — DEBUG, INFO, WARNING, ERROR, CRITICAL
- Handlers — StreamHandler, FileHandler, RotatingFileHandler
- Formatters — text and JSON
- `logging.config.dictConfig` — configuring the whole stack declaratively
- Logger naming convention — `__name__` in every module
- Structured logging — adding context fields to log records
- `logging.getLogger(__name__)` — the correct pattern
- Log filtering — keeping noisy libraries quiet
- The `structlog` library — preview for Phase 3
- Replacing debug `print()` with `logger.debug()`

---

## Full Tutorial

### Why `print()` Is Not Enough

`print()` is fine for user-facing output. For diagnostic output it falls short:

- No timestamp — when did this happen?
- No severity — is this informational or a warning?
- No source — which module printed this?
- Cannot be silenced — must delete or comment out
- Cannot be redirected — goes to stdout, mixed with user output
- Cannot be filtered — see everything or nothing

The Python `logging` module solves all of these. It has been in the standard library since Python 2.3 and is universally used in production Python code.

---

### The Logging Hierarchy

Python logging is organised as a tree of **loggers**, each identified by a dotted name:

```
root
└ taskflow
    ├ taskflow.main
    ├ taskflow.storage
    │   └ taskflow.storage.json_store
    ├ taskflow.core
    │   └ taskflow.core.task
    ├ taskflow.display
    │   └ taskflow.display.commands
    └ taskflow.integrations
        └ taskflow.integrations.weather
```

By convention, every module gets its own logger named after the module:

```python
import logging
logger = logging.getLogger(__name__)
# In taskflow/storage/json_store.py, __name__ == "taskflow.storage.json_store"
```

Log records **propagate upward** by default — a record emitted by `taskflow.storage.json_store` travels to `taskflow.storage`, then to `taskflow`, then to the root logger. Handlers attached to any ancestor will receive it.

---

### Log Levels

```python
logger.debug("Variable value: %s", value)      # detailed dev info
logger.info("User added a task")               # normal operation
logger.warning("Retrying after network error") # something unexpected
logger.error("Could not save tasks: %s", e)    # something failed
logger.critical("Data file corrupted!")        # serious failure

# With extra context (structured logging)
logger.info("Task saved", extra={"task_id": 42, "duration_ms": 3.1})
```

**Level hierarchy** (ascending severity):
`DEBUG` < `INFO` < `WARNING` < `ERROR` < `CRITICAL`

Setting a logger's level to `INFO` means DEBUG messages are silently dropped. In development you typically want `DEBUG`. In production, `INFO` or `WARNING`.

---

### Handlers and Formatters

A **handler** decides where log records go — stdout, a file, a remote service.
A **formatter** decides how log records look.

```python
import logging

# Create a logger
logger = logging.getLogger("taskflow")
logger.setLevel(logging.DEBUG)

# Console handler — human-readable
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
console.setFormatter(logging.Formatter(
    "%(asctime)s %(levelname)-8s %(name)-30s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
))

# File handler — all logs persisted
file_handler = logging.FileHandler("logs/taskflow.log", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter(
    "%(asctime)s %(levelname)s %(name)s %(message)s"
))

logger.addHandler(console)
logger.addHandler(file_handler)
```

---

### `RotatingFileHandler` — Prevent Log Files Growing Forever

```python
from logging.handlers import RotatingFileHandler

rotating = RotatingFileHandler(
    "logs/taskflow.log",
    maxBytes=5 * 1024 * 1024,   # 5 MB per file
    backupCount=3,               # keep 3 backup files
    encoding="utf-8",
)
```

When `taskflow.log` reaches 5 MB, it is renamed to `taskflow.log.1`, the previous `.1` becomes `.2`, and so on. Only the 3 most recent files are kept. The app always writes to `taskflow.log`. No manual log rotation needed.

---

### `logging.config.dictConfig` — Declarative Configuration

For anything beyond the simplest setup, configure logging declaratively with a dictionary. This is the pattern used in every production Python application:

```python
import logging.config

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "console": {
            "format": "%(asctime)s %(levelname)-8s %(name)-30s %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "json": {
            "()": "taskflow.logging_config.JsonFormatter",
        },
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "console",
            "stream": "ext://sys.stderr",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "json",
            "filename": "logs/taskflow.log",
            "maxBytes": 5242880,   # 5 MB
            "backupCount": 3,
            "encoding": "utf-8",
        },
    },

    "loggers": {
        "taskflow": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": False,
        },
    },

    # Silence noisy third-party libraries
    "root": {
        "level": "WARNING",
    },
}
```

---

### Building `taskflow/logging_config.py`

```python
# taskflow/logging_config.py
# TaskFlow AI — Logging configuration.
#
# Call setup_logging() once in main.py before anything else runs.
# Every other module gets a logger with: logger = logging.getLogger(__name__)
#
# Version history:
#   Day 23 — initial implementation

import json
import logging
import logging.config
import logging.handlers
import sys
from datetime import datetime, timezone
from pathlib import Path

__all__ = ["setup_logging", "JsonFormatter"]


class JsonFormatter(logging.Formatter):
    """
    Format log records as JSON lines for machine-readable log files.

    Each log line is a self-contained JSON object with:
        timestamp, level, logger, message, and any extra fields.

    Example output:
        {"timestamp":"2025-05-19T14:32:01Z","level":"INFO",
         "logger":"taskflow.main","message":"Tasks loaded","task_count":4}
    """

    # Fields from LogRecord that are not useful in structured logs
    _SKIP_ATTRS = frozenset({
        "args", "created", "exc_info", "exc_text", "filename",
        "funcName", "levelno", "lineno", "module", "msecs",
        "msg", "name", "pathname", "process", "processName",
        "relativeCreated", "stack_info", "thread", "threadName",
    })

    def format(self, record: logging.LogRecord) -> str:
        data: dict = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "level":   record.levelname,
            "logger":  record.name,
            "message": record.getMessage(),
        }

        # Include exception info if present
        if record.exc_info:
            data["exception"] = self.formatException(record.exc_info)

        # Include any extra fields passed via extra={...}
        for key, value in record.__dict__.items():
            if key not in self._SKIP_ATTRS and not key.startswith("_"):
                try:
                    json.dumps(value)   # only include JSON-serialisable values
                    data[key] = value
                except (TypeError, ValueError):
                    data[key] = str(value)

        return json.dumps(data, ensure_ascii=False)


def setup_logging(
    level: str = "INFO",
    log_dir: Path | None = None,
    json_file: bool = True,
    console: bool = True,
) -> None:
    """
    Configure the taskflow logging stack.

    Should be called once at application startup, before any other
    taskflow code runs.

    Args:
        level    (str)       : Minimum log level for the taskflow logger.
                               "DEBUG" during development, "INFO" in production.
        log_dir  (Path|None) : Directory for log files. Defaults to BASE_DIR/logs.
                               Pass None to disable file logging.
        json_file (bool)     : Write JSON-formatted logs to a rotating file.
        console   (bool)     : Write human-readable logs to stderr.
    """
    from .config import BASE_DIR

    handlers: dict = {}
    handler_names: list[str] = []

    #  Console handler ─
    if console:
        handlers["console"] = {
            "class":     "logging.StreamHandler",
            "level":     level,
            "formatter": "console",
            "stream":    "ext://sys.stderr",
        }
        handler_names.append("console")

    #  Rotating JSON file handler 
    if json_file:
        resolved_dir = log_dir or (BASE_DIR / "logs")
        resolved_dir.mkdir(parents=True, exist_ok=True)
        log_path = resolved_dir / "taskflow.log"

        handlers["file"] = {
            "class":       "logging.handlers.RotatingFileHandler",
            "level":       "DEBUG",   # always capture DEBUG in file
            "formatter":   "json",
            "filename":    str(log_path),
            "maxBytes":    5 * 1024 * 1024,   # 5 MB
            "backupCount": 3,
            "encoding":    "utf-8",
        }
        handler_names.append("file")

    config = {
        "version":                1,
        "disable_existing_loggers": False,

        "formatters": {
            "console": {
                "format":  "%(asctime)s %(levelname)-8s %(name)-35s %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "()": "taskflow.logging_config.JsonFormatter",
            },
        },

        "handlers": handlers,

        "loggers": {
            "taskflow": {
                "level":     level,
                "handlers":  handler_names,
                "propagate": False,
            },
        },

        # Silence noisy third-party libraries
        "root": {
            "level":    "WARNING",
            "handlers": [],
        },
    }

    logging.config.dictConfig(config)

    logger = logging.getLogger("taskflow")
    logger.debug(
        "Logging configured",
        extra={
            "log_level":   level,
            "console":     console,
            "json_file":   json_file,
            "log_dir":     str(resolved_dir) if json_file else None,
        }
    )
```

---

### Adding Loggers to Every Module

Add these two lines at the top of every `taskflow` module (below imports):

```python
import logging
logger = logging.getLogger(__name__)
```

Then replace all diagnostic `print()` calls with the appropriate log level.

**`taskflow/storage/json_store.py` — updated with logging:**

```python
import logging
logger = logging.getLogger(__name__)

def save_tasks(tasks, filepath=DATA_FILE):
    """Save tasks to JSON — atomic write."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    tmp = filepath.with_suffix(".tmp")
    start = time.perf_counter()
    try:
        data = [t.to_dict() if isinstance(t, Task) else t for t in tasks]
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        tmp.rename(filepath)
        elapsed_ms = round((time.perf_counter() - start) * 1000, 1)
        logger.info(
            "Tasks saved",
            extra={"task_count": len(tasks), "duration_ms": elapsed_ms}
        )
    except (OSError, TypeError) as e:
        if tmp.exists():
            tmp.unlink()
        logger.error("Save failed: %s", e, exc_info=True)
        raise StorageError(f"Could not save tasks: {e}") from e


def load_tasks(filepath=DATA_FILE):
    """Load tasks from JSON."""
    if not filepath.exists():
        logger.debug("Storage file not found — returning empty list: %s", filepath)
        return []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        tasks = [task_from_dict(d) for d in data]
        logger.info("Tasks loaded", extra={"task_count": len(tasks)})
        return tasks
    except json.JSONDecodeError as e:
        logger.error("Storage file corrupted: %s", e)
        raise StorageError("Storage file contains invalid JSON") from e
    except OSError as e:
        logger.error("Could not read storage file: %s", e)
        raise StorageError(f"Could not read storage file: {e}") from e
```

**`taskflow/integrations/weather.py` — updated with logging:**

```python
import logging
logger = logging.getLogger(__name__)

def fetch_weather(latitude, longitude, location_name="", use_cache=True):
    if use_cache:
        cached = _load_cache()
        if cached:
            logger.debug("Weather cache hit — returning cached data")
            return cached

    logger.info("Fetching weather", extra={"location": location_name})
    weather = _do_fetch_weather(latitude, longitude, location_name)
    if weather:
        _save_cache(weather)
        logger.debug("Weather cached successfully")
    else:
        logger.warning("Weather fetch returned None")
    return weather
```

**`taskflow/display/commands.py` — updated with logging:**

```python
import logging
logger = logging.getLogger(__name__)

def cmd_add(tasks, raw_input=""):
    # ... input collection ...
    try:
        task = _parse_to_task(raw)
    except ValidationError as e:
        logger.warning("Task add failed validation: %s", e)
        print(f"\n  ✗ {e}\n")
        return

    try:
        add_task_to_list(tasks, task)
        logger.info(
            "Task added",
            extra={
                "task_id":   task.id,
                "task_type": type(task).__name__,
                "priority":  task.priority,
                "category":  task.category,
            }
        )
    except ValidationError as e:
        logger.warning("Task add rejected (limit): %s", e)
        print(f"\n  ✗ {e}\n")
        return

    _print_add_success(task, len(tasks))
```

---

### Updating `main.py` to Call `setup_logging()`

```python
# taskflow/main.py — updated for Day 23

def main() -> None:
    """Application entry point."""
    import sys
    from .logging_config import setup_logging

    args       = sys.argv[1:]
    no_weather = "--no-weather" in args
    debug_mode = "--debug" in args

    # Configure logging FIRST — before anything else runs
    setup_logging(
        level   = "DEBUG" if debug_mode else "INFO",
        console = True,
        json_file = True,
    )

    import logging
    logger = logging.getLogger(__name__)
    logger.info("TaskFlow AI starting", extra={"version": VERSION})

    # ... rest of main() unchanged ...
```

Now run with `--debug` to see all debug-level output:

```bash
python run.py --debug
```

---

### Silencing Noisy Libraries

Third-party libraries like `requests` and `urllib3` emit verbose debug logs that clutter your output. The `dictConfig` already sets `root` to `WARNING`. To silence specific libraries:

```python
# In setup_logging(), add to the "loggers" section of dictConfig:
"loggers": {
    "taskflow": {"level": level, "handlers": handler_names, "propagate": False},
    "urllib3":  {"level": "WARNING", "propagate": True},
    "requests": {"level": "WARNING", "propagate": True},
},
```

---

## Exercises

**Exercise 1 — Add `logger = logging.getLogger(__name__)` to every module.**
Open every `.py` file in `taskflow/`. Add the two logger lines at the top. Replace every `print()` that is diagnostic (not user output) with the correct log level call.

**Exercise 2 — Structured log audit.**
After running the app and performing add/view/done/remove operations, open `logs/taskflow.log`. Read each JSON line. Are all the important events logged? Are there events that should be logged but are not? Add missing log calls.

**Exercise 3 — Custom log filter.**
Write a `SensitiveDataFilter` that scrubs any log record containing the key `"api_key"` or `"password"`:

```python
class SensitiveDataFilter(logging.Filter):
    _SENSITIVE = {"api_key", "password", "token", "secret"}

    def filter(self, record):
        for key in self._SENSITIVE:
            if hasattr(record, key):
                setattr(record, key, "***REDACTED***")
        return True   # always let the record through
```

Add it to the file handler in `setup_logging()`.

**Exercise 4 — Log the full application lifecycle.**
Add log calls to cover the entire app lifecycle:
- `INFO` on startup with version
- `INFO` on task load with count and duration
- `INFO` on each command executed
- `INFO` on shutdown with task count and session duration
- `WARNING` on any retry
- `ERROR` on any exception that is caught and recovered

**Exercise 5 — `structlog` preview.**
Install `structlog` (`pip install structlog`) and write a 20-line demo that configures it with JSON output and adds context fields that persist across calls:

```python
import structlog

log = structlog.get_logger()
log = log.bind(app="TaskFlow AI", version="1.1.0")
log.info("app_started")
log.info("task_added", task_id=42, priority="high")
```

Compare the output format to the standard library approach. Structlog will replace `logging_config.py` in Phase 3 when we add the FastAPI server.

**Exercise 6 (stretch) — Log-based test assertion.**
Write a pytest test that verifies a log message is emitted when `save_tasks()` is called successfully:

```python
import logging
import pytest

def test_save_tasks_logs_success(tmp_path, one_task, caplog):
    from taskflow.storage.json_store import save_tasks
    filepath = tmp_path / "test_tasks.json"

    with caplog.at_level(logging.INFO, logger="taskflow.storage.json_store"):
        save_tasks(one_task, filepath=filepath)

    assert any("Tasks saved" in r.message for r in caplog.records)
    assert any(
        getattr(r, "task_count", None) == 1
        for r in caplog.records
    )
```

---

## Checkpoint

Before moving to Day 24:

- [ ] `taskflow/logging_config.py` exists with `setup_logging()` and `JsonFormatter`
- [ ] `main.py` calls `setup_logging()` as its first action
- [ ] `logs/taskflow.log` is created and populated when the app runs
- [ ] Every module has `logger = logging.getLogger(__name__)`
- [ ] No diagnostic `print()` calls remain outside `display/renderer.py`
- [ ] `logs/` is in `.gitignore`
- [ ] `urllib3` and `requests` are silenced at WARNING level
- [ ] Running with `--debug` shows DEBUG-level messages in the console

---

## Common Errors on Day 23

**Calling `setup_logging()` too late:**

```python
import logging
logger = logging.getLogger(__name__)

# ❌ setup_logging() called AFTER logger is created and used
logger.info("This won't appear correctly")
setup_logging()
```

Always call `setup_logging()` before any other application code runs. In `main.py`, it must be the very first call after argument parsing.

**Using `print()` in the logging formatter:**

```python
class BadFormatter(logging.Formatter):
    def format(self, record):
        print("Formatting...")   # ❌ recursive logging or lost output
        return super().format(record)
```

Never call `print()` inside a logging component. It creates confusion and can cause infinite recursion.

**The `%s` vs f-string performance trap:**

```python
# ❌ f-string — always evaluates, even if log level is below threshold
logger.debug(f"Processing {len(tasks)} tasks with {complex_function()}")

# ✅ % formatting — lazy evaluation — args only computed if record passes
logger.debug("Processing %d tasks", len(tasks))
```

The `%s` / `%d` formatting in logger calls is intentional — the arguments are only evaluated if the log record actually passes the level filter. This makes high-volume debug logging cheap in production.

**Not adding `logs/` to `.gitignore`:**

```gitignore
# .gitignore — add these
logs/
*.log
```

Log files should never be committed. They grow without bound and contain runtime data that has no place in version control.

---

## What's Coming

On **Day 24** we handle environment configuration and secrets properly — `python-dotenv`, the 12-factor app methodology, and reading `USER_NAME`, API keys, and `DATA_DIR` from `.env` files rather than hardcoding them in `config.py`. This also resolves TD-005 from the technical debt register and prepares TaskFlow AI for containerised deployment in Phase 3.
