"""
FastAPI Middleware for Request Tracking and Logging.

Provides middleware for:
- Request ID generation
- Request timing
- Structured logging
- Rate limiting
"""

import logging
import time
import uuid
from collections import defaultdict
from collections.abc import Callable

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests with timing and request IDs.
    
    Features:
    - Generates unique request IDs
    - Logs request method, path, and timing
    - Adds request ID to response headers
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        """Process request and log details."""
        # Generate request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # Store request ID in state for access in handlers
        request.state.request_id = request_id

        # Record start time
        start_time = time.time()

        # Log incoming request
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query": str(request.query_params),
                "client_ip": self._get_client_ip(request),
            },
        )

        # Process request
        try:
            response = await call_next(request)

            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Log completed request
            logger.info(
                f"Request completed: {request.method} {request.url.path} "
                f"- {response.status_code} ({duration_ms:.2f}ms)",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": round(duration_ms, 2),
                },
            )

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as exc:
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Log failed request
            logger.error(
                f"Request failed: {request.method} {request.url.path} "
                f"- {type(exc).__name__}: {exc} ({duration_ms:.2f}ms)",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                    "duration_ms": round(duration_ms, 2),
                },
                exc_info=True,
            )
            raise

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request.

        Uses the LAST value of X-Forwarded-For (set by the trusted proxy)
        rather than the first, which a client can forge.
        """
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[-1].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        if request.client:
            return request.client.host

        return "unknown"


class SlowRequestMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging slow requests.
    
    Logs a warning when requests exceed a configured threshold.
    """

    def __init__(self, app, threshold_ms: float = 1000.0):
        """
        Initialize slow request middleware.
        
        Args:
            app: FastAPI application
            threshold_ms: Threshold in milliseconds for slow requests
        """
        super().__init__(app)
        self.threshold_ms = threshold_ms

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        """Process request and warn if slow."""
        start_time = time.time()

        response = await call_next(request)

        duration_ms = (time.time() - start_time) * 1000

        if duration_ms > self.threshold_ms:
            logger.warning(
                f"Slow request: {request.method} {request.url.path} "
                f"took {duration_ms:.2f}ms (threshold: {self.threshold_ms}ms)",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": round(duration_ms, 2),
                    "threshold_ms": self.threshold_ms,
                },
            )

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Redis-backed rate limiting middleware with in-memory fallback.

    Uses INCR + EXPIRE per key so state survives across workers and restarts.
    Falls back to an in-memory sliding-window if Redis is unavailable.
    """

    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour

        # In-memory fallback (used only when Redis is unreachable)
        self._fallback: dict[str, dict[str, list[float]]] = defaultdict(
            lambda: {"minute": [], "hour": []}
        )

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP using the LAST X-Forwarded-For value (proxy-set)."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[-1].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        if request.client:
            return request.client.host

        return "unknown"

    async def _check_rate_limit_redis(self, ip: str) -> tuple[bool, str]:
        """Check rate limit via Redis INCR+EXPIRE. Returns (allowed, reason)."""
        from redis.exceptions import RedisError

        from app.redis_client import get_redis_client

        try:
            client = await get_redis_client()

            minute_key = f"ratelimit:{ip}:minute"
            hour_key = f"ratelimit:{ip}:hour"

            # Atomic increment; set TTL only on first increment
            minute_count = await client.incr(minute_key)
            if minute_count == 1:
                await client.expire(minute_key, 60)

            hour_count = await client.incr(hour_key)
            if hour_count == 1:
                await client.expire(hour_key, 3600)

            if minute_count > self.requests_per_minute:
                return False, f"Rate limit exceeded: {self.requests_per_minute} requests per minute"
            if hour_count > self.requests_per_hour:
                return False, f"Rate limit exceeded: {self.requests_per_hour} requests per hour"

            return True, ""

        except RedisError as exc:
            logger.warning(f"Redis unavailable for rate limiting, using fallback: {exc}")
            return self._check_rate_limit_fallback(ip)

    def _check_rate_limit_fallback(self, ip: str) -> tuple[bool, str]:
        """Sliding-window in-memory fallback used when Redis is unreachable."""
        current_time = time.time()
        self._fallback[ip]["minute"] = [
            ts for ts in self._fallback[ip]["minute"] if current_time - ts < 60
        ]
        self._fallback[ip]["hour"] = [
            ts for ts in self._fallback[ip]["hour"] if current_time - ts < 3600
        ]

        if len(self._fallback[ip]["minute"]) >= self.requests_per_minute:
            return False, f"Rate limit exceeded: {self.requests_per_minute} requests per minute"
        if len(self._fallback[ip]["hour"]) >= self.requests_per_hour:
            return False, f"Rate limit exceeded: {self.requests_per_hour} requests per hour"

        self._fallback[ip]["minute"].append(current_time)
        self._fallback[ip]["hour"].append(current_time)
        return True, ""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        """Process request with rate limiting."""
        if request.url.path in ["/health", "/ready"] or request.method == "OPTIONS":
            return await call_next(request)

        client_ip = self._get_client_ip(request)
        is_allowed, reason = await self._check_rate_limit_redis(client_ip)

        if not is_allowed:
            logger.warning(
                f"Rate limit exceeded for IP {client_ip}: {reason}",
                extra={
                    "client_ip": client_ip,
                    "reason": reason,
                    "path": request.url.path,
                },
            )
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": {
                        "code": 429,
                        "message": "Too Many Requests",
                        "details": {"reason": reason},
                    }
                },
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                },
            )

        return await call_next(request)
