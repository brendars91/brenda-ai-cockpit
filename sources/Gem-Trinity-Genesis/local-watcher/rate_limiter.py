"""
Rate Limiting Middleware for FastAPI
Implements sliding window rate limiting per IP address.
"""
import time
from collections import defaultdict
from typing import Dict, Tuple
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Sliding window rate limiter.
    Tracks requests per IP within a time window.
    """
    
    def __init__(self, requests_per_minute: int = 60, burst_limit: int = 10):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_minute: Max requests allowed per minute
            burst_limit: Max requests in a 1-second burst
        """
        self.requests_per_minute = requests_per_minute
        self.burst_limit = burst_limit
        self.request_counts: Dict[str, list] = defaultdict(list)
    
    def _clean_old_requests(self, ip: str, current_time: float):
        """Remove requests older than 1 minute."""
        cutoff = current_time - 60
        self.request_counts[ip] = [
            t for t in self.request_counts[ip] if t > cutoff
        ]
    
    def is_allowed(self, ip: str) -> Tuple[bool, Dict]:
        """
        Check if request is allowed.
        
        Returns:
            Tuple of (is_allowed, rate_limit_info)
        """
        current_time = time.time()
        self._clean_old_requests(ip, current_time)
        
        # Check minute limit
        minute_count = len(self.request_counts[ip])
        if minute_count >= self.requests_per_minute:
            return False, {
                "error": "rate_limit_exceeded",
                "limit": self.requests_per_minute,
                "window": "60s",
                "retry_after": 60
            }
        
        # Check burst limit (last second)
        one_second_ago = current_time - 1
        burst_count = sum(1 for t in self.request_counts[ip] if t > one_second_ago)
        if burst_count >= self.burst_limit:
            return False, {
                "error": "burst_limit_exceeded",
                "limit": self.burst_limit,
                "window": "1s",
                "retry_after": 1
            }
        
        # Record request
        self.request_counts[ip].append(current_time)
        
        return True, {
            "remaining": self.requests_per_minute - minute_count - 1,
            "limit": self.requests_per_minute,
            "reset": 60
        }


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for rate limiting.
    """
    
    def __init__(self, app, requests_per_minute: int = 60, burst_limit: int = 10):
        super().__init__(app)
        self.limiter = RateLimiter(requests_per_minute, burst_limit)
        # Paths to exclude from rate limiting (health checks, etc.)
        self.excluded_paths = {"/", "/api/status", "/api/health"}
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for excluded paths
        if request.url.path in self.excluded_paths:
            return await call_next(request)
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            client_ip = forwarded.split(",")[0].strip()
        
        # Check rate limit
        allowed, info = self.limiter.is_allowed(client_ip)
        
        if not allowed:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Too Many Requests",
                    **info
                },
                headers={
                    "Retry-After": str(info.get("retry_after", 60)),
                    "X-RateLimit-Limit": str(info.get("limit", 60)),
                    "X-RateLimit-Remaining": "0"
                }
            )
        
        # Process request
        response = await call_next(request)

        # Add rate limit headers to all responses
        response.headers["X-RateLimit-Limit"] = str(info.get("limit", 60))
        response.headers["X-RateLimit-Remaining"] = str(info.get("remaining", 0))
        response.headers["X-RateLimit-Reset"] = str(info.get("reset", 60))
        response.headers["X-RateLimit-Window"] = "60s"

        return response


def get_rate_limit_stats() -> dict:
    """Get current rate limiting statistics for monitoring."""
    # This function can be called to get stats about the rate limiter
    return {
        "status": "active",
        "type": "sliding_window",
        "window": "60 seconds",
        "description": "Rate limiting is enforced per IP address"
    }
