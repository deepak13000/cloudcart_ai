import json
import logging
from datetime import datetime
from typing import Any

from app.config.settings import settings


class JsonFormatter(logging.Formatter):
    """Format log records as single-line JSON objects."""

    def formatTime(self, record: logging.LogRecord, datefmt: str | None = None) -> str:
        timestamp = datetime.fromtimestamp(record.created)
        return timestamp.isoformat(timespec="seconds")

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": "cloudcart_ai",
        }

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        payload.update(self._extract_extra(record))
        return json.dumps(payload, default=str, ensure_ascii=False)

    def _extract_extra(self, record: logging.LogRecord) -> dict[str, Any]:
        standard_attributes = {
            "name",
            "msg",
            "args",
            "levelname",
            "levelno",
            "pathname",
            "filename",
            "module",
            "exc_info",
            "exc_text",
            "stack_info",
            "lineno",
            "funcName",
            "created",
            "msecs",
            "relativeCreated",
            "thread",
            "threadName",
            "processName",
            "process",
            "message",
        }
        return {
            key: value
            for key, value in record.__dict__.items()
            if key not in standard_attributes
        }


def configure_structured_logging() -> logging.Logger:
    """Configure the root logger to emit structured JSON logs."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    formatter = JsonFormatter()
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(log_level)
    root_logger.propagate = False

    return get_logger()


def get_logger(name: str = "cloudcart_ai") -> logging.Logger:
    """Return a structured logger instance for the given module name."""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
    logger.propagate = False

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)

    return logger


def log_event(level: str, message: str, **extra: Any) -> None:
    """Emit a one-shot structured event with optional fields."""
    logger = get_logger()
    level_name = level.upper()
    log_level = getattr(logging, level_name, logging.INFO)
    logger.log(log_level, message, extra=extra)
