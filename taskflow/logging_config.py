from __future__ import annotations
import json, logging, logging.config, logging.handlers
from datetime import datetime, timezone
from pathlib import Path

__all__ = ["setup_logging", "JsonFormatter"]


class JsonFormatter(logging.Formatter):
    _SKIP = frozenset({"args","created","exc_info","exc_text","filename",
                        "funcName","levelno","lineno","module","msecs","msg",
                        "name","pathname","process","processName",
                        "relativeCreated","stack_info","thread","threadName"})

    def format(self, record: logging.LogRecord) -> str:
        data: dict = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "level":   record.levelname,
            "logger":  record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            data["exception"] = self.formatException(record.exc_info)
        for k, v in record.__dict__.items():
            if k not in self._SKIP and not k.startswith("_"):
                try:
                    json.dumps(v)
                    data[k] = v
                except (TypeError, ValueError):
                    data[k] = str(v)
        return json.dumps(data, ensure_ascii=False)


def setup_logging(level: str = "INFO", log_dir: Path | None = None,
                  json_file: bool = True, console: bool = True) -> None:
    from .config import BASE_DIR
    handlers: dict = {}
    handler_names: list[str] = []

    if console:
        handlers["console"] = {
            "class": "logging.StreamHandler", "level": level,
            "formatter": "console", "stream": "ext://sys.stderr",
        }
        handler_names.append("console")

    if json_file:
        resolved_dir = log_dir or (BASE_DIR / "logs")
        resolved_dir.mkdir(parents=True, exist_ok=True)
        handlers["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG", "formatter": "json",
            "filename": str(resolved_dir / "taskflow.log"),
            "maxBytes": 5 * 1024 * 1024, "backupCount": 3,
            "encoding": "utf-8",
        }
        handler_names.append("file")

    config = {
        "version": 1, "disable_existing_loggers": False,
        "formatters": {
            "console": {"format": "%(asctime)s %(levelname)-8s %(name)-35s %(message)s",
                        "datefmt": "%Y-%m-%d %H:%M:%S"},
            "json":    {"()": "taskflow.logging_config.JsonFormatter"},
        },
        "handlers": handlers,
        "loggers": {"taskflow": {"level": level, "handlers": handler_names, "propagate": False}},
        "root": {"level": "WARNING", "handlers": []},
    }
    logging.config.dictConfig(config)