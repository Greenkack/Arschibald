"""
Logging Decorator for Services

This module provides logging decorators for automatic method logging
with timing, arguments, and result tracking.
"""

from typing import Any, Callable, Optional, TypeVar
from functools import wraps
import logging
import time
from datetime import datetime
import json


logger = logging.getLogger(__name__)


T = TypeVar('T')


def log_service_call(
    log_level: int = logging.INFO,
    log_args: bool = True,
    log_result: bool = False,
    log_timing: bool = True,
    service_name: str = ""
):
    """
    Decorator for logging service method calls.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_args: Whether to log method arguments
        log_result: Whether to log method result
        log_timing: Whether to log execution time
        service_name: Name of the service (for context)
        
    Example:
        @log_service_call(service_name="SolarService", log_result=True)
        def calculate(self, params):
            # Implementation
            pass
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            # Get method name and service context
            method_name = func.__name__
            service_context = service_name or (args[0].__class__.__name__ if args else "")
            full_name = f"{service_context}.{method_name}" if service_context else method_name
            
            # Log method entry
            log_message = f"Calling {full_name}"
            
            if log_args and (args or kwargs):
                # Format arguments (skip 'self' if present)
                args_to_log = args[1:] if args and hasattr(args[0], method_name) else args
                args_str = _format_args(args_to_log, kwargs)
                log_message += f" with args: {args_str}"
            
            logger.log(log_level, log_message)
            
            # Execute method with timing
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Log successful completion
                success_message = f"Completed {full_name}"
                
                if log_timing:
                    success_message += f" in {execution_time:.3f}s"
                
                if log_result:
                    result_str = _format_result(result)
                    success_message += f" with result: {result_str}"
                
                logger.log(log_level, success_message)
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                error_message = f"Failed {full_name} after {execution_time:.3f}s: {str(e)}"
                logger.error(error_message, exc_info=True)
                raise
        
        return wrapper
    return decorator


def log_performance(
    threshold_seconds: float = 1.0,
    log_level: int = logging.WARNING,
    service_name: str = ""
):
    """
    Decorator for logging slow method executions.
    
    Only logs if execution time exceeds threshold.
    
    Args:
        threshold_seconds: Time threshold in seconds
        log_level: Logging level for slow executions
        service_name: Name of the service
        
    Example:
        @log_performance(threshold_seconds=0.5, service_name="DatabaseService")
        def query_data(self, query):
            # Implementation
            pass
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            if execution_time > threshold_seconds:
                method_name = func.__name__
                service_context = service_name or (args[0].__class__.__name__ if args else "")
                full_name = f"{service_context}.{method_name}" if service_context else method_name
                
                logger.log(
                    log_level,
                    f"Slow execution: {full_name} took {execution_time:.3f}s (threshold: {threshold_seconds}s)"
                )
            
            return result
        
        return wrapper
    return decorator


def log_exceptions(
    log_level: int = logging.ERROR,
    reraise: bool = True,
    service_name: str = ""
):
    """
    Decorator for logging exceptions with full context.
    
    Args:
        log_level: Logging level for exceptions
        reraise: Whether to reraise the exception after logging
        service_name: Name of the service
        
    Example:
        @log_exceptions(service_name="PDFService")
        def generate_pdf(self, data):
            # Implementation
            pass
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                method_name = func.__name__
                service_context = service_name or (args[0].__class__.__name__ if args else "")
                full_name = f"{service_context}.{method_name}" if service_context else method_name
                
                logger.log(
                    log_level,
                    f"Exception in {full_name}: {type(e).__name__}: {str(e)}",
                    exc_info=True
                )
                
                if reraise:
                    raise
                return None
        
        return wrapper
    return decorator


def log_entry_exit(
    service_name: str = "",
    log_level: int = logging.DEBUG
):
    """
    Decorator for logging method entry and exit.
    
    Useful for debugging and tracing execution flow.
    
    Args:
        service_name: Name of the service
        log_level: Logging level
        
    Example:
        @log_entry_exit(service_name="CalculationService")
        def complex_calculation(self, params):
            # Implementation
            pass
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            method_name = func.__name__
            service_context = service_name or (args[0].__class__.__name__ if args else "")
            full_name = f"{service_context}.{method_name}" if service_context else method_name
            
            logger.log(log_level, f"→ Entering {full_name}")
            
            try:
                result = func(*args, **kwargs)
                logger.log(log_level, f"← Exiting {full_name}")
                return result
            except Exception as e:
                logger.log(log_level, f" Exiting {full_name} with exception: {type(e).__name__}")
                raise
        
        return wrapper
    return decorator


class MethodLogger:
    """
    Context manager for logging method execution with detailed tracking.
    
    Example:
        with MethodLogger("MyService", "calculate", log_args=True):
            result = perform_calculation()
    """
    
    def __init__(
        self,
        service_name: str,
        method_name: str,
        log_level: int = logging.INFO,
        log_args: bool = False,
        args: tuple = (),
        kwargs: dict = None
    ):
        """
        Initialize method logger.
        
        Args:
            service_name: Name of the service
            method_name: Name of the method
            log_level: Logging level
            log_args: Whether to log arguments
            args: Method arguments
            kwargs: Method keyword arguments
        """
        self.service_name = service_name
        self.method_name = method_name
        self.log_level = log_level
        self.log_args = log_args
        self.args = args
        self.kwargs = kwargs or {}
        self.start_time = None
        self.full_name = f"{service_name}.{method_name}"
    
    def __enter__(self):
        self.start_time = time.time()
        
        log_message = f"Starting {self.full_name}"
        if self.log_args and (self.args or self.kwargs):
            args_str = _format_args(self.args, self.kwargs)
            log_message += f" with args: {args_str}"
        
        logger.log(self.log_level, log_message)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        execution_time = time.time() - self.start_time
        
        if exc_type is None:
            logger.log(
                self.log_level,
                f"Completed {self.full_name} in {execution_time:.3f}s"
            )
        else:
            logger.error(
                f"Failed {self.full_name} after {execution_time:.3f}s: {exc_val}",
                exc_info=True
            )
        
        return False  # Don't suppress exceptions


def _format_args(args: tuple, kwargs: dict) -> str:
    """Format arguments for logging"""
    parts = []
    
    if args:
        args_str = ", ".join(_safe_repr(arg) for arg in args)
        parts.append(args_str)
    
    if kwargs:
        kwargs_str = ", ".join(f"{k}={_safe_repr(v)}" for k, v in kwargs.items())
        parts.append(kwargs_str)
    
    return ", ".join(parts)


def _format_result(result: Any) -> str:
    """Format result for logging"""
    return _safe_repr(result)


def _safe_repr(obj: Any, max_length: int = 200) -> str:
    """
    Safe representation of object for logging.
    
    Handles large objects, sensitive data, and complex types.
    """
    try:
        # Handle None
        if obj is None:
            return "None"
        
        # Handle basic types
        if isinstance(obj, (str, int, float, bool)):
            repr_str = repr(obj)
            if len(repr_str) > max_length:
                return repr_str[:max_length] + "..."
            return repr_str
        
        # Handle collections
        if isinstance(obj, (list, tuple)):
            if len(obj) == 0:
                return "[]" if isinstance(obj, list) else "()"
            return f"[{len(obj)} items]"
        
        if isinstance(obj, dict):
            if len(obj) == 0:
                return "{}"
            return f"{{{len(obj)} keys}}"
        
        # Handle objects with __dict__
        if hasattr(obj, '__dict__'):
            return f"<{type(obj).__name__} object>"
        
        # Fallback
        repr_str = repr(obj)
        if len(repr_str) > max_length:
            return repr_str[:max_length] + "..."
        return repr_str
        
    except Exception:
        return f"<{type(obj).__name__} (repr failed)>"
