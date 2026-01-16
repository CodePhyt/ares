"""
Custom middleware for ARES API.
"""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from loguru import logger
import time
from typing import Callable

from src.api.metrics import metrics_collector


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add unique request ID to each request."""
    
    async def dispatch(self, request: Request, call_next):
        import uuid
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all API requests with timing information."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and log timing."""
        start_time = time.time()
        
        # Log request
        logger.info(
            "{} {} - Client: {}",
            request.method,
            request.url.path,
            request.client.host if request.client else "unknown",
        )
        
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log response
            logger.info(
                "{} {} - Status: {} - Duration: {:.3f}s",
                request.method,
                request.url.path,
                response.status_code,
                duration,
            )
            
            # Record metrics
            endpoint = f"{request.method} {request.url.path}"
            metrics_collector.record_request(endpoint, duration, response.status_code)
            
            # Add timing header
            response.headers["X-Process-Time"] = str(duration)
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                "{} {} - Error: {} - Duration: {:.3f}s",
                request.method,
                request.url.path,
                str(e),
                duration,
            )
            raise


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers."""
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response
