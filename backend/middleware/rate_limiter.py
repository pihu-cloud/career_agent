"""
In-memory rate limiter middleware (SB1/US44, US46).
Limits each IP to 60 requests per minute.
"""

import time
from collections import defaultdict, deque
from typing import Deque

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


RATE_LIMIT = 60       # requests
WINDOW_SECONDS = 60   # per minute


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Sliding-window in-memory rate limiter."""

    def __init__(self, app, rate_limit: int = RATE_LIMIT, window: int = WINDOW_SECONDS):
        super().__init__(app)
        self.rate_limit = rate_limit
        self.window = window
        # ip -> deque of request timestamps
        self._requests: dict[str, Deque[float]] = defaultdict(deque)

    def _get_client_ip(self, request: Request) -> str:
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        if request.client:
            return request.client.host
        return "unknown"

    async def dispatch(self, request: Request, call_next):
        ip = self._get_client_ip(request)
        now = time.time()
        window_start = now - self.window

        timestamps: Deque[float] = self._requests[ip]

        # Purge expired entries
        while timestamps and timestamps[0] < window_start:
            timestamps.popleft()

        remaining = self.rate_limit - len(timestamps)
        reset_at = int(timestamps[0] + self.window) if timestamps else int(now + self.window)

        if remaining <= 0:
            return JSONResponse(
                status_code=429,
                content={"error": "Too many requests. Please try again later."},
                headers={
                    "X-RateLimit-Limit": str(self.rate_limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_at),
                    "Retry-After": str(reset_at - int(now)),
                },
            )

        timestamps.append(now)

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.rate_limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining - 1)
        response.headers["X-RateLimit-Reset"] = str(reset_at)
        return response
