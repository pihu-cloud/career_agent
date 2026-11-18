"""
Audit log middleware (SB1/US24).
Logs every HTTP request with method, path, user, IP, status code, and latency.
Uses Python logger (not DB) to avoid circular dependencies.
"""

import time
from typing import Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from backend.core.logging import audit_logger


def _extract_user_from_header(request: Request) -> Optional[str]:
    """Attempt to decode user_id from Authorization header without full DB lookup."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth[7:]
    try:
        import os
        from jose import jwt

        secret = os.getenv("SECRET_KEY", "CHANGE_ME_IN_PRODUCTION_supersecretkey_32chars!")
        algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        payload = jwt.decode(token, secret, algorithms=[algorithm])
        return payload.get("sub")
    except Exception:
        return None


class AuditLogMiddleware(BaseHTTPMiddleware):
    """Log every request to the audit logger."""

    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.time()

        # Try to get user early (best effort — might fail for invalid tokens)
        user_id = _extract_user_from_header(request)

        # Get client IP
        forwarded_for = request.headers.get("X-Forwarded-For")
        ip_address = (
            forwarded_for.split(",")[0].strip()
            if forwarded_for
            else (request.client.host if request.client else "unknown")
        )

        response = await call_next(request)

        latency_ms = round((time.time() - start) * 1000, 2)

        audit_logger.info(
            "http_request",
            extra={
                "audit": True,
                "method": request.method,
                "path": request.url.path,
                "query": str(request.url.query),
                "user_id": user_id,
                "ip_address": ip_address,
                "user_agent": request.headers.get("User-Agent", ""),
                "status_code": response.status_code,
                "latency_ms": latency_ms,
            },
        )

        return response
