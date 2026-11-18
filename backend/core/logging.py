"""
Structured JSON logging for Career Pathway Navigator.
Provides logger and audit_logger with file rotation.
"""

import logging
import logging.handlers
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any


class JSONFormatter(logging.Formatter):
    """Format log records as JSON."""

    def format(self, record: logging.LogRecord) -> str:
        log_data: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Merge any extra fields
        for key, value in record.__dict__.items():
            if key not in (
                "name", "msg", "args", "levelname", "levelno", "pathname",
                "filename", "module", "exc_info", "exc_text", "stack_info",
                "lineno", "funcName", "created", "msecs", "relativeCreated",
                "thread", "threadName", "processName", "process", "message",
                "taskName",
            ):
                log_data[key] = value

        return json.dumps(log_data, default=str)


def _build_logger(name: str, log_file: str, level: int = logging.INFO) -> logging.Logger:
    """Build a configured logger with console and rotating file handlers."""
    log = logging.getLogger(name)
    log.setLevel(level)

    if log.handlers:
        return log  # already configured

    formatter = JSONFormatter()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    log.addHandler(console_handler)

    # Rotating file handler
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
    os.makedirs(log_dir, exist_ok=True)
    file_path = os.path.join(log_dir, log_file)

    file_handler = logging.handlers.RotatingFileHandler(
        file_path,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)
    log.addHandler(file_handler)

    log.propagate = False
    return log


# Application logger
logger: logging.Logger = _build_logger(
    name="career_navigator",
    log_file="app.log",
    level=logging.INFO,
)

# Audit logger — only WARNING+ to keep audit trail tidy
audit_logger: logging.Logger = _build_logger(
    name="career_navigator.audit",
    log_file="audit.log",
    level=logging.INFO,
)


def log_audit_event(
    action: str,
    resource: str,
    user_id: str | None = None,
    ip_address: str | None = None,
    details: dict | None = None,
) -> None:
    """Convenience helper to log a structured audit event."""
    audit_logger.info(
        "audit_event",
        extra={
            "audit": True,
            "action": action,
            "resource": resource,
            "user_id": user_id,
            "ip_address": ip_address,
            "details": details or {},
        },
    )
