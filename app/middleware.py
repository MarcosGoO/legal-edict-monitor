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
        """Extract client IP from request."""
        # Check for forwarded headers (behind proxy)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        # Check for real IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fall back to direct client
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
    Simple in-memory rate limiting middleware.
    
    Features:
    - Limits requests per IP address
    - Configurable requests per window
    - Returns 429 when limit exceeded
    
    Note: For production, consider using Redis-based rate limiting
    for distributed systems.
    """

    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
    ):
        """
        Initialize rate limit middleware.
        
        Args:
            app: FastAPI application
            requests_per_minute: Max requests per minute per IP
            requests_per_hour: Max requests per hour per IP
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour

        # In-memory storage for rate limits
        # Structure: {ip: {"minute": [(timestamp, count)], "hour": [(timestamp, count)]}}
        self._requests: dict[str, dict[str, list[float]]] = defaultdict(
            lambda: {"minute": [], "hour": []}
        )

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        if request.client:
            return request.client.host

        return "unknown"

    def _clean_old_requests(self, timestamps: list[float], window_seconds: float) -> list[float]:
        """Remove timestamps older than the window."""
        current_time = time.time()
        return [ts for ts in timestamps if current_time - ts < window_seconds]

    def _check_rate_limit(self, ip: str) -> tuple[bool, str]:
        """
        Check if IP is within rate limits.
        
        Returns:
            Tuple of (is_allowed, reason)
        """
        current_time = time.time()

        # Clean old requests
        self._requests[ip]["minute"] = self._clean_old_requests(
            self._requests[ip]["minute"], 60
        )
        self._requests[ip]["hour"] = self._clean_old_requests(
            self._requests[ip]["hour"], 3600
        )

        # Check minute limit
        if len(self._requests[ip]["minute"]) >= self.requests_per_minute:
            return False, f"Rate limit exceeded: {self.requests_per_minute} requests per minute"

        # Check hour limit
        if len(self._requests[ip]["hour"]) >= self.requests_per_hour:
            return False, f"Rate limit exceeded: {self.requests_per_hour} requests per hour"

        # Record this request
        self._requests[ip]["minute"].append(current_time)
        self._requests[ip]["hour"].append(current_time)

        return True, ""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        """Process request with rate limiting."""
        # Skip rate limiting for health checks and CORS preflight (OPTIONS)
        if request.url.path in ["/health", "/ready"] or request.method == "OPTIONS":
            return await call_next(request)

        client_ip = self._get_client_ip(request)

        is_allowed, reason = self._check_rate_limit(client_ip)

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
