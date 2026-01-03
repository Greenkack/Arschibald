"""
Error Handling Wrapper

This module provides error handling utilities for wrapping legacy code
with consistent error handling and reporting.
"""

from typing import Any, Callable, Optional, Type, TypeVar, Union
from functools import wraps
import logging
import traceback
from datetime import datetime


logger = logging.getLogger(__name__)


T = TypeVar('T')


class ServiceError(Exception):
    """Base exception for service errors"""
    
    def __init__(
        self,
        message: str,
        service_name: str = "",
        original_error: Optional[Exception] = None,
        error_code: Optional[str] = None,
        details: Optional[dict] = None
    ):
        """
        Initialize service error.
        
        Args:
            message: Error message
            service_name: Name of the service where error occurred
            original_error: Original exception that was caught
            error_code: Error code for categorization
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.service_name = service_name
        self.original_error = original_error
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.details = details or {}
        self.timestamp = datetime.now()
    
    def to_dict(self) -> dict:
        """Convert error to dictionary representation"""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "service_name": self.service_name,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
            "original_error": str(self.original_error) if self.original_error else None,
            "original_error_type": type(self.original_error).__name__ if self.original_error else None
        }


class InitializationError(ServiceError):
    """Error during service initialization"""
    
    def __init__(self, message: str, service_name: str = "", original_error: Optional[Exception] = None):
        super().__init__(
            message=message,
            service_name=service_name,
            original_error=original_error,
            error_code="INITIALIZATION_ERROR"
        )


class DependencyError(ServiceError):
    """Error related to service dependencies"""
    
    def __init__(self, message: str, service_name: str = "", dependency_name: str = "", original_error: Optional[Exception] = None):
        super().__init__(
            message=message,
            service_name=service_name,
            original_error=original_error,
            error_code="DEPENDENCY_ERROR",
            details={"dependency_name": dependency_name}
        )


class ValidationError(ServiceError):
    """Error during input validation"""
    
    def __init__(self, message: str, service_name: str = "", field_name: str = "", original_error: Optional[Exception] = None):
        super().__init__(
            message=message,
            service_name=service_name,
            original_error=original_error,
            error_code="VALIDATION_ERROR",
            details={"field_name": field_name}
        )


class ExecutionError(ServiceError):
    """Error during service execution"""
    
    def __init__(self, message: str, service_name: str = "", operation: str = "", original_error: Optional[Exception] = None):
        super().__init__(
            message=message,
            service_name=service_name,
            original_error=original_error,
            error_code="EXECUTION_ERROR",
            details={"operation": operation}
        )


def handle_service_errors(
    service_name: str = "",
    error_message: str = "Service operation failed",
    reraise: bool = True,
    default_return: Any = None
):
    """
    Decorator for handling service errors with consistent logging and wrapping.
    
    Args:
        service_name: Name of the service
        error_message: Custom error message
        reraise: Whether to reraise the exception after handling
        default_return: Default value to return if error occurs and reraise=False
        
    Example:
        @handle_service_errors(service_name="SolarService", error_message="Calculation failed")
        def calculate(self, params):
            # Implementation
            pass
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Union[T, Any]:
            try:
                return func(*args, **kwargs)
            except ServiceError:
                # Already a ServiceError, just log and reraise
                logger.error(f"Service error in {service_name}.{func.__name__}: {error_message}")
                if reraise:
                    raise
                return default_return
            except Exception as e:
                # Wrap in ServiceError
                logger.error(
                    f"Error in {service_name}.{func.__name__}: {str(e)}",
                    exc_info=True
                )
                
                wrapped_error = ExecutionError(
                    message=f"{error_message}: {str(e)}",
                    service_name=service_name,
                    operation=func.__name__,
                    original_error=e
                )
                
                if reraise:
                    raise wrapped_error from e
                return default_return
        
        return wrapper
    return decorator


def safe_execute(
    func: Callable[..., T],
    *args,
    service_name: str = "",
    operation: str = "",
    default_return: Optional[T] = None,
    log_errors: bool = True,
    **kwargs
) -> Union[T, None]:
    """
    Safely execute a function with error handling.
    
    Args:
        func: Function to execute
        *args: Positional arguments for func
        service_name: Name of the service
        operation: Operation description
        default_return: Value to return on error
        log_errors: Whether to log errors
        **kwargs: Keyword arguments for func
        
    Returns:
        Function result or default_return on error
        
    Example:
        result = safe_execute(
            legacy_function,
            param1, param2,
            service_name="MyService",
            operation="legacy_operation",
            default_return={}
        )
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if log_errors:
            logger.error(
                f"Error in {service_name}.{operation}: {str(e)}",
                exc_info=True
            )
        return default_return


class ErrorContext:
    """
    Context manager for error handling with automatic logging and wrapping.
    
    Example:
        with ErrorContext(service_name="MyService", operation="calculate"):
            # Code that might raise errors
            result = perform_calculation()
    """
    
    def __init__(
        self,
        service_name: str = "",
        operation: str = "",
        error_message: str = "",
        reraise: bool = True,
        log_errors: bool = True
    ):
        """
        Initialize error context.
        
        Args:
            service_name: Name of the service
            operation: Operation description
            error_message: Custom error message
            reraise: Whether to reraise exceptions
            log_errors: Whether to log errors
        """
        self.service_name = service_name
        self.operation = operation
        self.error_message = error_message or f"Error in {operation}"
        self.reraise = reraise
        self.log_errors = log_errors
        self.error: Optional[Exception] = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            return True
        
        self.error = exc_val
        
        if self.log_errors:
            logger.error(
                f"Error in {self.service_name}.{self.operation}: {str(exc_val)}",
                exc_info=True
            )
        
        if self.reraise:
            if isinstance(exc_val, ServiceError):
                return False  # Reraise as-is
            
            # Wrap in ServiceError
            wrapped_error = ExecutionError(
                message=f"{self.error_message}: {str(exc_val)}",
                service_name=self.service_name,
                operation=self.operation,
                original_error=exc_val
            )
            raise wrapped_error from exc_val
        
        return True  # Suppress exception


def validate_input(
    condition: bool,
    error_message: str,
    service_name: str = "",
    field_name: str = ""
) -> None:
    """
    Validate input condition and raise ValidationError if false.
    
    Args:
        condition: Condition to validate
        error_message: Error message if validation fails
        service_name: Name of the service
        field_name: Name of the field being validated
        
    Raises:
        ValidationError: If condition is False
        
    Example:
        validate_input(
            value > 0,
            "Value must be positive",
            service_name="MyService",
            field_name="value"
        )
    """
    if not condition:
        raise ValidationError(
            message=error_message,
            service_name=service_name,
            field_name=field_name
        )


def get_error_details(error: Exception) -> dict:
    """
    Extract detailed information from an exception.
    
    Args:
        error: Exception to analyze
        
    Returns:
        Dictionary with error details
    """
    return {
        "type": type(error).__name__,
        "message": str(error),
        "traceback": traceback.format_exc(),
        "timestamp": datetime.now().isoformat()
    }
