"""
Logging Decorator for Service Methods

Provides decorators for consistent logging across services.
"""

import logging
import time
from functools import wraps
from typing import Callable, Any


logger = logging.getLogger(__name__)


def log_service_call(
    service_name: str,
    log_timing: bool = False
) -> Callable:
    """
    Decorator to log service method calls.
    
    Args:
        service_name: Name of the service
        log_timing: Whether to log execution time
        
    Returns:
        Decorated function with logging
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time() if log_timing else None
            
            logger.debug(f"{service_name}.{func.__name__} called")
            
            try:
                result = func(*args, **kwargs)
                
                if log_timing and start_time:
                    elapsed = time.time() - start_time
                    logger.debug(
                        f"{service_name}.{func.__name__} completed in {elapsed:.3f}s"
                    )
                
                return result
            except Exception as e:
                logger.error(f"{service_name}.{func.__name__} failed: {e}")
                raise
        
        return wrapper
    return decorator
