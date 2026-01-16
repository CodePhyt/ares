"""
Rate limiting middleware for ARES API.
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Tuple
import time
from loguru import logger


class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self, requests_per_minute: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_minute: Maximum requests allowed per minute per client
        """
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = defaultdict(list)
        self.window_seconds = 60
    
    def is_allowed(self, client_id: str) -> Tuple[bool, int]:
        """
        Check if request is allowed.
        
        Args:
            client_id: Unique identifier for the client (IP address, API key, etc.)
            
        Returns:
            Tuple of (is_allowed, remaining_requests)
        """
        now = time.time()
        
        # Clean old requests outside the window
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if now - req_time < self.window_seconds
        ]
        
        # Check if limit exceeded
        if len(self.requests[client_id]) >= self.requests_per_minute:
            remaining = 0
            return False, remaining
        
        # Add current request
        self.requests[client_id].append(now)
        remaining = self.requests_per_minute - len(self.requests[client_id])
        
        return True, remaining
    
    def get_retry_after(self, client_id: str) -> int:
        """
        Get seconds until next request is allowed.
        
        Args:
            client_id: Client identifier
            
        Returns:
            Seconds until retry is allowed
        """
        if not self.requests[client_id]:
            return 0
        
        oldest_request = min(self.requests[client_id])
        elapsed = time.time() - oldest_request
        retry_after = int(self.window_seconds - elapsed) + 1
        
        return max(0, retry_after)


# Global rate limiter instance
rate_limiter = RateLimiter(requests_per_minute=60)


async def rate_limit_middleware(request: Request, call_next):
    """
    Rate limiting middleware.
    
    Checks if the request should be rate limited based on client IP.
    """
    # Skip rate limiting for health checks and docs
    if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
        return await call_next(request)
    
    # Get client identifier (IP address)
    client_id = request.client.host if request.client else "unknown"
    
    # Check rate limit
    is_allowed, remaining = rate_limiter.is_allowed(client_id)
    
    if not is_allowed:
        retry_after = rate_limiter.get_retry_after(client_id)
        logger.warning(
            "Rate limit exceeded for client {}: {} requests/min",
            client_id,
            rate_limiter.requests_per_minute,
        )
        
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "Rate limit exceeded",
                "message": f"Too many requests. Maximum {rate_limiter.requests_per_minute} requests per minute.",
                "retry_after": retry_after,
            },
            headers={
                "X-RateLimit-Limit": str(rate_limiter.requests_per_minute),
                "X-RateLimit-Remaining": "0",
                "Retry-After": str(retry_after),
            },
        )
    
    # Add rate limit headers to response
    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(rate_limiter.requests_per_minute)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    
    return response
