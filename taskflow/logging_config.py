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
    _SKIP_ATTRS = frozenset(
        {
            "args",
            "created",
            "exc_info",
            "exc_text",
            "filename",
            "funcName",
            "levelno",
            "lineno",
            "module",
            "msecs",
            "msg",
            "name",
            "pathname",
            "process",
            "processName",
            "relativeCreated",
            "stack_info",
            "thread",
            "threadName",
        }
    )

    def format(self, record: logging.LogRecord) -> str:
        data: dict = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Include exception info if present
        if record.exc_info:
            data["exception"] = self.formatException(record.exc_info)

        # Include any extra fields passed via extra={...}
        for key, value in record.__dict__.items():
            if key not in self._SKIP_ATTRS and not key.startswith("_"):
                try:
                    json.dumps(value)  # only include JSON-serialisable values
                    data[key] = value
                except TypeError, ValueError:
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

    # ── Console handler ───────────────────────────────────
    if console:
        handlers["console"] = {
            "class": "logging.StreamHandler",
            "level": level,
            "formatter": "console",
            "stream": "ext://sys.stderr",
        }
        handler_names.append("console")

    # ── Rotating JSON file handler ────────────────────────
    if json_file:
        resolved_dir = log_dir or (BASE_DIR / "logs")
        resolved_dir.mkdir(parents=True, exist_ok=True)
        log_path = resolved_dir / "taskflow.log"

        handlers["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",  # always capture DEBUG in file
            "formatter": "json",
            "filename": str(log_path),
            "maxBytes": 5 * 1024 * 1024,  # 5 MB
            "backupCount": 3,
            "encoding": "utf-8",
        }
        handler_names.append("file")

    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "console": {
                "format": "%(asctime)s %(levelname)-8s %(name)-35s %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "()": "taskflow.logging_config.JsonFormatter",
            },
        },
        "handlers": handlers,
        "loggers": {
            "taskflow": {
                "level": level,
                "handlers": handler_names,
                "propagate": False,
            },
        },
        # Silence noisy third-party libraries
        "root": {
            "level": "WARNING",
            "handlers": [],
        },
    }

    logging.config.dictConfig(config)

    logger = logging.getLogger("taskflow")
    logger.debug(
        "Logging configured",
        extra={
            "log_level": level,
            "console": console,
            "json_file": json_file,
            "log_dir": str(resolved_dir) if json_file else None,
        },
    )
