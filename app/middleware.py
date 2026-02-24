"""
FastAPI Middleware for Request Tracking and Logging.

Provides middleware for:
- Request ID generation
- Request timing
- Structured logging
"""

import logging
import time
import uuid
from typing import Callable

from fastapi import Request, Response
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
