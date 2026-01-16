"""
Retry utilities for resilient API calls.
"""

from functools import wraps
from typing import Callable, TypeVar, Any
import asyncio
from loguru import logger

T = TypeVar('T')


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
):
    """
    Retry decorator for functions.

    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch and retry

    Returns:
        Decorated function
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> T:
            current_delay = delay
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts:
                        logger.warning(
                            "Attempt {}/{} failed for {}: {}. Retrying in {:.2f}s...",
                            attempt,
                            max_attempts,
                            func.__name__,
                            str(e),
                            current_delay,
                        )
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            "All {} attempts failed for {}: {}",
                            max_attempts,
                            func.__name__,
                            str(e),
                        )
            
            raise last_exception
        
        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> T:
            current_delay = delay
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts:
                        logger.warning(
                            "Attempt {}/{} failed for {}: {}. Retrying in {:.2f}s...",
                            attempt,
                            max_attempts,
                            func.__name__,
                            str(e),
                            current_delay,
                        )
                        import time
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            "All {} attempts failed for {}: {}",
                            max_attempts,
                            func.__name__,
                            str(e),
                        )
            
            raise last_exception
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
