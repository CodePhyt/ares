"""
Simple in-memory cache for frequently accessed data.
"""

from typing import Optional, Dict, Any, Callable
from datetime import datetime, timedelta
from functools import wraps
import hashlib
import json


class SimpleCache:
    """Simple in-memory cache with TTL support."""

    def __init__(self, default_ttl: int = 3600):
        """
        Initialize cache.

        Args:
            default_ttl: Default time-to-live in seconds
        """
        self.default_ttl = default_ttl
        self._cache: Dict[str, Dict[str, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key not in self._cache:
            return None

        entry = self._cache[key]
        if datetime.now() > entry["expires_at"]:
            del self._cache[key]
            return None

        return entry["value"]

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache."""
        ttl = ttl or self.default_ttl
        expires_at = datetime.now() + timedelta(seconds=ttl)
        self._cache[key] = {
            "value": value,
            "expires_at": expires_at,
        }

    def delete(self, key: str) -> None:
        """Delete key from cache."""
        if key in self._cache:
            del self._cache[key]

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()

    def cleanup_expired(self) -> int:
        """Remove expired entries. Returns number of entries removed."""
        now = datetime.now()
        expired_keys = [
            key for key, entry in self._cache.items()
            if now > entry["expires_at"]
        ]
        for key in expired_keys:
            del self._cache[key]
        return len(expired_keys)

    def size(self) -> int:
        """Get number of entries in cache."""
        return len(self._cache)


def cache_key(*args, **kwargs) -> str:
    """Generate cache key from function arguments."""
    key_data = {
        "args": args,
        "kwargs": sorted(kwargs.items()),
    }
    key_str = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.md5(key_str.encode()).hexdigest()


def cached(ttl: int = 3600, key_func: Optional[Callable] = None):
    """
    Decorator for caching function results.

    Args:
        ttl: Time-to-live in seconds
        key_func: Optional function to generate cache key
    """
    cache = SimpleCache(default_ttl=ttl)

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key_str = key_func(*args, **kwargs)
            else:
                cache_key_str = cache_key(*args, **kwargs)

            # Check cache
            cached_value = cache.get(cache_key_str)
            if cached_value is not None:
                return cached_value

            # Execute function
            result = func(*args, **kwargs)

            # Store in cache
            cache.set(cache_key_str, result, ttl=ttl)

            return result

        wrapper.cache = cache  # Expose cache for manual control
        return wrapper

    return decorator
