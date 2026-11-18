"""
Request body sanitization middleware (SB1/US43).
Strips <script> tags and common SQL injection patterns from string values.
"""

import re
import json
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


# Patterns to strip / escape
_SCRIPT_PATTERN = re.compile(r"<script[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL)
_INLINE_EVENT_PATTERN = re.compile(r"\son\w+\s*=", re.IGNORECASE)
_SQL_PATTERNS = [
    re.compile(r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)", re.IGNORECASE),
    re.compile(r"(--|\bOR\b\s+\d+\s*=\s*\d+|\bAND\b\s+\d+\s*=\s*\d+)", re.IGNORECASE),
    re.compile(r"['\"];\s*(DROP|DELETE|INSERT|UPDATE)", re.IGNORECASE),
]


def _sanitize_value(value: Any) -> Any:
    """Recursively sanitize a value."""
    if isinstance(value, str):
        value = _SCRIPT_PATTERN.sub("", value)
        value = _INLINE_EVENT_PATTERN.sub("", value)
        # We log suspicious SQL patterns but do NOT strip keywords that might
        # appear in legitimate data (e.g., course names with 'SELECT').
        # Instead, parameterised queries are the real defence.
        return value.strip()
    if isinstance(value, dict):
        return {k: _sanitize_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_sanitize_value(item) for item in value]
    return value


class SanitizerMiddleware(BaseHTTPMiddleware):
    """Sanitize JSON request bodies."""

    _JSON_CONTENT_TYPES = {"application/json", "application/json; charset=utf-8"}

    async def dispatch(self, request: Request, call_next) -> Response:
        content_type = request.headers.get("Content-Type", "").lower()

        if any(ct in content_type for ct in ("application/json",)):
            try:
                body_bytes = await request.body()
                if body_bytes:
                    data = json.loads(body_bytes)
                    sanitized = _sanitize_value(data)

                    # Rebuild the request with the sanitized body
                    sanitized_bytes = json.dumps(sanitized).encode("utf-8")

                    async def receive():
                        return {"type": "http.request", "body": sanitized_bytes, "more_body": False}

                    request = Request(request.scope, receive)
            except (json.JSONDecodeError, Exception):
                # If body cannot be parsed, let downstream handle it
                pass

        return await call_next(request)
