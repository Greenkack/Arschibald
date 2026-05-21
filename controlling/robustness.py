"""
Controlling System Robustness Module

Provides comprehensive error handling, validation, retry logic, and
stability features for the Employee Controlling System.

This module ensures the controlling system is extremely robust and stable.
"""

import logging
import functools
import time
from typing import Any, Callable, Optional, TypeVar, cast
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ControllingError(Exception):
    """Base exception for controlling system errors."""
    pass


class ValidationError(ControllingError):
    """Raised when validation fails."""
    pass


class DatabaseError(ControllingError):
    """Raised when database operations fail."""
    pass


class ExportError(ControllingError):
    """Raised when export operations fail."""
    pass


def retry_on_db_error(
    max_retries: int = 3,
    delay: float = 0.5,
    backoff: float = 2.0
):
    """
    Decorator to retry database operations on transient errors.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each retry
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except OperationalError as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            f"Database operation failed (attempt {attempt + 1}/"
                            f"{max_retries + 1}): {e}. Retrying in "
                            f"{current_delay}s..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"Database operation failed after {max_retries + 1} "
                            f"attempts: {e}"
                        )
                except Exception as e:
                    # Don't retry on non-transient errors
                    logger.error(f"Non-retryable error in {func.__name__}: {e}")
                    raise
            
            # If we get here, all retries failed
            raise DatabaseError(
                f"Database operation failed after {max_retries + 1} attempts"
            ) from last_exception
        
        return wrapper
    return decorator


def safe_db_operation(
    func: Callable[..., T],
    db: Session,
    rollback_on_error: bool = True
) -> Callable[..., Optional[T]]:
    """
    Wrapper for safe database operations with automatic rollback.
    
    Args:
        func: Function to wrap
        db: Database session
        rollback_on_error: Whether to rollback on error
    
    Returns:
        Wrapped function that handles errors gracefully
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Optional[T]:
        try:
            result = func(*args, **kwargs)
            db.commit()
            return result
        except IntegrityError as e:
            if rollback_on_error:
                db.rollback()
            logger.error(f"Integrity error in {func.__name__}: {e}")
            raise ValidationError(
                f"Data integrity violation: {str(e)}"
            ) from e
        except SQLAlchemyError as e:
            if rollback_on_error:
                db.rollback()
            logger.error(f"Database error in {func.__name__}: {e}")
            raise DatabaseError(
                f"Database operation failed: {str(e)}"
            ) from e
        except Exception as e:
            if rollback_on_error:
                db.rollback()
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            raise ControllingError(
                f"Operation failed: {str(e)}"
            ) from e
    
    return wrapper


def validate_not_none(value: Any, field_name: str) -> None:
    """
    Validate that a value is not None.
    
    Args:
        value: Value to validate
        field_name: Name of the field for error messages
    
    Raises:
        ValidationError: If value is None
    """
    if value is None:
        raise ValidationError(f"{field_name} cannot be None")


def validate_not_empty(value: str, field_name: str) -> None:
    """
    Validate that a string is not empty.
    
    Args:
        value: String to validate
        field_name: Name of the field for error messages
    
    Raises:
        ValidationError: If string is empty or whitespace
    """
    if not value or not value.strip():
        raise ValidationError(f"{field_name} cannot be empty")


def validate_positive(value: float, field_name: str) -> None:
    """
    Validate that a number is positive.
    
    Args:
        value: Number to validate
        field_name: Name of the field for error messages
    
    Raises:
        ValidationError: If number is not positive
    """
    if value < 0:
        raise ValidationError(f"{field_name} must be positive")


def validate_percentage(value: float, field_name: str) -> None:
    """
    Validate that a number is a valid percentage (0-100).
    
    Args:
        value: Number to validate
        field_name: Name of the field for error messages
    
    Raises:
        ValidationError: If number is not between 0 and 100
    """
    if not 0 <= value <= 100:
        raise ValidationError(f"{field_name} must be between 0 and 100")


def validate_date_range(
    start_date: datetime,
    end_date: datetime,
    field_name: str = "Date range"
) -> None:
    """
    Validate that a date range is valid.
    
    Args:
        start_date: Start date
        end_date: End date
        field_name: Name of the field for error messages
    
    Raises:
        ValidationError: If date range is invalid
    """
    if start_date > end_date:
        raise ValidationError(
            f"{field_name}: start date must be before or equal to end date"
        )


def safe_division(
    numerator: float,
    denominator: float,
    default: float = 0.0
) -> float:
    """
    Safely divide two numbers, returning default if denominator is zero.
    
    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value to return if denominator is zero
    
    Returns:
        Result of division or default value
    """
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (TypeError, ValueError, ZeroDivisionError):
        logger.warning(
            f"Division error: {numerator} / {denominator}, "
            f"returning default {default}"
        )
        return default


def safe_percentage(
    numerator: float,
    denominator: float,
    default: float = 0.0
) -> float:
    """
    Safely calculate percentage, returning default if denominator is zero.
    
    Args:
        numerator: Numerator
        denominator: Denominator
        default: Default value to return if denominator is zero
    
    Returns:
        Percentage (0-100) or default value
    """
    result = safe_division(numerator, denominator, default)
    return result * 100.0


def log_operation(operation_name: str):
    """
    Decorator to log operation start, success, and failure.
    
    Args:
        operation_name: Name of the operation for logging
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            logger.info(f"Starting operation: {operation_name}")
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                logger.info(
                    f"Operation {operation_name} completed successfully "
                    f"in {elapsed:.2f}s"
                )
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(
                    f"Operation {operation_name} failed after {elapsed:.2f}s: {e}"
                )
                raise
        
        return wrapper
    return decorator


def ensure_session_state(key: str, default: Any = None):
    """
    Decorator to ensure session state key exists before function execution.
    
    Args:
        key: Session state key
        default: Default value if key doesn't exist
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            import streamlit as st
            
            if key not in st.session_state:
                st.session_state[key] = default
                logger.debug(f"Initialized session state key: {key}")
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def handle_streamlit_errors(
    error_message: str = "Ein Fehler ist aufgetreten",
    show_details: bool = True
):
    """
    Decorator to handle errors in Streamlit UI functions.
    
    Args:
        error_message: User-friendly error message
        show_details: Whether to show error details to user
    """
    def decorator(func: Callable[..., T]) -> Callable[..., Optional[T]]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Optional[T]:
            import streamlit as st
            
            try:
                return func(*args, **kwargs)
            except ValidationError as e:
                st.error(f" Validierungsfehler: {e}")
                logger.warning(f"Validation error in {func.__name__}: {e}")
                return None
            except DatabaseError as e:
                st.error(f" Datenbankfehler: {e}")
                logger.error(f"Database error in {func.__name__}: {e}")
                return None
            except ExportError as e:
                st.error(f" Exportfehler: {e}")
                logger.error(f"Export error in {func.__name__}: {e}")
                return None
            except Exception as e:
                st.error(f" {error_message}")
                if show_details:
                    st.error(f"Details: {str(e)}")
                logger.error(f"Unexpected error in {func.__name__}: {e}")
                return None
        
        return wrapper
    return decorator


class TransactionContext:
    """
    Context manager for database transactions with automatic rollback.
    
    Usage:
        with TransactionContext(db) as ctx:
            # Perform database operations
            ctx.add(obj)
            ctx.commit()
    """
    
    def __init__(self, db: Session, auto_commit: bool = False):
        """
        Initialize transaction context.
        
        Args:
            db: Database session
            auto_commit: Whether to auto-commit on exit
        """
        self.db = db
        self.auto_commit = auto_commit
        self._committed = False
    
    def __enter__(self):
        """Enter transaction context."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit transaction context with automatic rollback on error."""
        if exc_type is not None:
            # Error occurred, rollback
            logger.warning(f"Rolling back transaction due to error: {exc_val}")
            self.db.rollback()
            return False
        
        if self.auto_commit and not self._committed:
            # Auto-commit if enabled and not already committed
            try:
                self.db.commit()
                self._committed = True
                logger.debug("Transaction auto-committed")
            except Exception as e:
                logger.error(f"Auto-commit failed: {e}")
                self.db.rollback()
                raise
        
        return True
    
    def add(self, obj: Any) -> None:
        """Add object to session."""
        self.db.add(obj)
    
    def commit(self) -> None:
        """Commit transaction."""
        try:
            self.db.commit()
            self._committed = True
            logger.debug("Transaction committed")
        except Exception as e:
            logger.error(f"Commit failed: {e}")
            self.db.rollback()
            raise
    
    def rollback(self) -> None:
        """Rollback transaction."""
        self.db.rollback()
        logger.debug("Transaction rolled back")


def create_safe_getter(
    db: Session,
    model_class: Any,
    error_message: str = "Object not found"
):
    """
    Create a safe getter function for database objects.
    
    Args:
        db: Database session
        model_class: SQLAlchemy model class
        error_message: Error message if object not found
    
    Returns:
        Safe getter function
    """
    @retry_on_db_error()
    def safe_get(object_id: int) -> Any:
        """
        Safely get object by ID.
        
        Args:
            object_id: ID of object to get
        
        Returns:
            Object instance
        
        Raises:
            ValidationError: If object not found
        """
        obj = db.query(model_class).filter(
            model_class.id == object_id
        ).first()
        
        if obj is None:
            raise ValidationError(
                f"{error_message}: ID {object_id}"
            )
        
        return obj
    
    return safe_get


def validate_export_format(format_name: str) -> None:
    """
    Validate export format.
    
    Args:
        format_name: Export format name
    
    Raises:
        ValidationError: If format is not supported
    """
    valid_formats = ["json", "excel", "pdf"]
    if format_name.lower() not in valid_formats:
        raise ValidationError(
            f"Unsupported export format: {format_name}. "
            f"Valid formats: {', '.join(valid_formats)}"
        )


def ensure_dependencies(dependencies: list[str]) -> None:
    """
    Ensure required dependencies are available.
    
    Args:
        dependencies: List of module names to check
    
    Raises:
        ImportError: If any dependency is missing
    """
    missing = []
    for dep in dependencies:
        try:
            __import__(dep)
        except ImportError:
            missing.append(dep)
    
    if missing:
        raise ImportError(
            f"Missing required dependencies: {', '.join(missing)}. "
            f"Install with: pip install {' '.join(missing)}"
        )


class PerformanceMonitor:
    """Monitor performance of operations."""
    
    def __init__(self, operation_name: str):
        """
        Initialize performance monitor.
        
        Args:
            operation_name: Name of operation to monitor
        """
        self.operation_name = operation_name
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        """Start monitoring."""
        self.start_time = time.time()
        logger.debug(f"Started monitoring: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop monitoring and log results."""
        self.end_time = time.time()
        elapsed = self.end_time - self.start_time
        
        if exc_type is None:
            logger.info(
                f"Operation {self.operation_name} completed in {elapsed:.2f}s"
            )
        else:
            logger.warning(
                f"Operation {self.operation_name} failed after {elapsed:.2f}s"
            )
        
        return False
    
    @property
    def elapsed(self) -> float:
        """Get elapsed time in seconds."""
        if self.start_time is None:
            return 0.0
        if self.end_time is None:
            return time.time() - self.start_time
        return self.end_time - self.start_time


# Export all public functions and classes
__all__ = [
    'ControllingError',
    'ValidationError',
    'DatabaseError',
    'ExportError',
    'retry_on_db_error',
    'safe_db_operation',
    'validate_not_none',
    'validate_not_empty',
    'validate_positive',
    'validate_percentage',
    'validate_date_range',
    'safe_division',
    'safe_percentage',
    'log_operation',
    'ensure_session_state',
    'handle_streamlit_errors',
    'TransactionContext',
    'create_safe_getter',
    'validate_export_format',
    'ensure_dependencies',
    'PerformanceMonitor'
]
