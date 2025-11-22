"""
Error Wrapper for Service Methods

Provides decorators for consistent error handling across services.
"""

import logging
from functools import wraps
from typing import Callable, Any


logger = logging.getLogger(__name__)


def handle_service_errors(
    service_name: str,
    error_message: str = "Service operation failed"
) -> Callable:
    """
    Decorator to handle errors in service methods.
    
    Args:
        service_name: Name of the service
        error_message: Custom error message
        
    Returns:
        Decorated function with error handling
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(
                    f"{service_name}.{func.__name__} failed: {error_message} - {e}"
                )
                raise
        return wrapper
    return decorator
