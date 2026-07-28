import hashlib
import json
import logging
import time
import uuid
from collections import defaultdict, deque
from collections.abc import Awaitable, Callable

from fastapi import Request
from fastapi.responses import JSONResponse, Response
from redis.asyncio import Redis
from redis.exceptions import RedisError
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings

logger = logging.getLogger("nexus.requests")
_redis: Redis | None = None
_fallback_windows: dict[str, deque[float]] = defaultdict(deque)
_request_count: dict[tuple[str, str, int], int] = defaultdict(int)
_latency_seconds: dict[tuple[str, str], float] = defaultdict(float)


def _client_key(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if settings.trust_proxy_headers and forwarded:
        client = forwarded.split(",", 1)[0].strip()
    else:
        client = request.client.host if request.client else "unknown"
    return hashlib.sha256(client.encode()).hexdigest()[:24]


async def _allowed(key: str, limit: int) -> tuple[bool, int]:
    global _redis
    minute = int(time.time() // 60)
    redis_key = f"nexus:rate:{minute}:{key}"
    try:
        if _redis is None:
            _redis = Redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=0.2,
                socket_timeout=0.2,
            )
        count = int(await _redis.incr(redis_key))
        if count == 1:
            await _redis.expire(redis_key, 70)
        return count <= limit, max(0, limit - count)
    except RedisError:
        now = time.monotonic()
        window = _fallback_windows[key]
        while window and window[0] <= now - 60:
            window.popleft()
        if len(window) >= limit:
            return False, 0
        window.append(now)
        return True, limit - len(window)


class OperationsMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        started = time.perf_counter()
        path = request.url.path
        if settings.rate_limit_enabled and path.startswith("/api/"):
            auth_sensitive = path in {
                "/api/v1/auth/login",
                "/api/v1/auth/register",
                "/api/v1/auth/password-reset/request",
                "/api/v1/auth/password-reset/confirm",
            }
            limit = (
                settings.auth_rate_limit_requests_per_minute
                if auth_sensitive
                else settings.rate_limit_requests_per_minute
            )
            allowed, remaining = await _allowed(
                f"{_client_key(request)}:{'auth' if auth_sensitive else 'api'}",
                limit,
            )
            if not allowed:
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": {
                            "code": "rate_limit_exceeded",
                            "message": "Muitas solicitações. Tente novamente em instantes.",
                            "details": {},
                        }
                    },
                    headers={
                        "Retry-After": "60",
                        "X-RateLimit-Limit": str(limit),
                        "X-RateLimit-Remaining": "0",
                        "X-Request-ID": request_id,
                    },
                )
        else:
            limit, remaining = 0, 0

        response = await call_next(request)
        elapsed = time.perf_counter() - started
        route = request.scope.get("route")
        route_path = getattr(route, "path", path)
        metric_key = (request.method, route_path)
        _request_count[(request.method, route_path, response.status_code)] += 1
        _latency_seconds[metric_key] += elapsed
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        if path in {"/docs", "/docs/oauth2-redirect", "/redoc"}:
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "img-src 'self' data: https://fastapi.tiangolo.com; "
                "frame-ancestors 'none'; object-src 'none'"
            )
        else:
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; frame-ancestors 'none'; object-src 'none'"
            )
        if settings.secure_cookies:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )
        if limit:
            response.headers["X-RateLimit-Limit"] = str(limit)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
        logger.info(
            json.dumps(
                {
                    "event": "http_request",
                    "request_id": request_id,
                    "method": request.method,
                    "route": route_path,
                    "status": response.status_code,
                    "duration_ms": round(elapsed * 1000, 2),
                },
                separators=(",", ":"),
            )
        )
        return response


def prometheus_metrics() -> str:
    lines = [
        "# HELP nexus_http_requests_total Total de solicitações HTTP.",
        "# TYPE nexus_http_requests_total counter",
    ]
    for (method, route, status), count in sorted(_request_count.items()):
        labels = f'method="{method}",route="{route}",status="{status}"'
        lines.append(f"nexus_http_requests_total{{{labels}}} {count}")
    lines.extend(
        [
            "# HELP nexus_http_request_duration_seconds_sum Latência HTTP acumulada.",
            "# TYPE nexus_http_request_duration_seconds_sum counter",
        ]
    )
    for (method, route), seconds in sorted(_latency_seconds.items()):
        labels = f'method="{method}",route="{route}"'
        lines.append(f"nexus_http_request_duration_seconds_sum{{{labels}}} {seconds:.6f}")
    return "\n".join(lines) + "\n"
