from __future__ import annotations

import time
from collections import defaultdict, deque

from aiohttp import web


class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        if max_requests <= 0:
            raise ValueError("max_requests должен быть больше 0")
        if window_seconds <= 0:
            raise ValueError("window_seconds должен быть больше 0")

        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests = defaultdict(deque)

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        bucket = self._requests[key]
        cutoff = now - self.window_seconds

        while bucket and bucket[0] <= cutoff:
            bucket.popleft()

        if len(bucket) >= self.max_requests:
            return False

        bucket.append(now)
        return True


def build_rate_limit_middleware(rate_limiter: RateLimiter):
    @web.middleware
    async def rate_limit_middleware(request: web.Request, handler):
        if request.method == "POST" and request.path.startswith("/api/v1/"):
            if not rate_limiter.allow(_build_key(request)):
                return web.json_response(
                    {
                        "error": {
                            "code": "rate_limited",
                            "message": "Слишком много запросов",
                        }
                    },
                    status=429,
                    headers={"Retry-After": str(rate_limiter.window_seconds)},
                )

        return await handler(request)

    return rate_limit_middleware


def _build_key(request: web.Request) -> str:
    auth_header = request.headers.get("Authorization", "")
    if auth_header:
        return auth_header

    peername = request.transport.get_extra_info("peername") if request.transport else None
    if peername:
        return str(peername[0])

    return "anonymous"
