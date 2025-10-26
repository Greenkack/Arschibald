"""
Structured Logging System with structlog
=========================================

Implements comprehensive structured logging with:
- JSON output for log aggregation
- Correlation ID generation and propagation
- Environment-specific log levels
- Runtime log level adjustment
- Centralized logging preparation

Requirements: 7.6, 9.5, 12.5
"""

import logging
import logging.handlers
import os
import sys
import uuid
from contextvars import ContextVar
from datetime import datetime
from pathlib import Path
from typing import Any

import structlog
from structlog.types import EventDict, Processor

# Context variable for correlation ID (thread-safe)
correlation_id_var: ContextVar[str | None] = ContextVar(
    "correlation_id", default=None
)


class CorrelationIDProcessor:
    """Processor to add correlation ID to log entries"""

    def __call__(self, logger: Any, method_name: str,
                 event_dict: EventDict) -> EventDict:
        """Add correlation ID to event dict"""
        correlation_id = correlation_id_var.get()
        if correlation_id:
            event_dict["correlation_id"] = correlation_id
        return event_dict


class TimestampProcessor:
    """Processor to add ISO 8601 timestamp"""

    def __call__(self, logger: Any, method_name: str,
                 event_dict: EventDict) -> EventDict:
        """Add timestamp to event dict"""
        event_dict["timestamp"] = datetime.now().astimezone().isoformat()
        return event_dict


class EnvironmentProcessor:
    """Processor to add environment information"""

    def __init__(self, env: str):
        self.env = env

    def __call__(self, logger: Any, method_name: str,
                 event_dict: EventDict) -> EventDict:
        """Add environment to event dict"""
        event_dict["environment"] = self.env
        return event_dict


def add_app_context(
        logger: Any,
        method_name: str,
        event_dict: EventDict) -> EventDict:
    """Add application context to log entries"""
    event_dict["app"] = "streamlit-robust"
    event_dict["version"] = os.getenv("APP_VERSION", "1.0.0")
    return event_dict


def censor_sensitive_data(
        logger: Any,
        method_name: str,
        event_dict: EventDict) -> EventDict:
    """Censor sensitive data from log entries"""
    sensitive_keys = {
        "password",
        "secret",
        "token",
        "api_key",
        "apikey",
        "auth",
        "authorization",
        "credential",
    }

    def _censor_dict(d: dict[str, Any]) -> dict[str, Any]:
        """Recursively censor sensitive keys in dictionary"""
        censored = {}
        for key, value in d.items():
            key_lower = key.lower()
            if any(sensitive in key_lower for sensitive in sensitive_keys):
                censored[key] = "[REDACTED]"
            elif isinstance(value, dict):
                censored[key] = _censor_dict(value)
            elif isinstance(value, list):
                censored[key] = [
                    _censor_dict(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                censored[key] = value
        return censored

    return _censor_dict(event_dict)


def setup_structured_logging(
    env: str = "dev",
    log_level: str = "INFO",
    log_dir: Path | None = None,
    enable_console: bool = True,
    enable_file: bool = True,
    json_format: bool = True,
) -> None:
    """
    Set up structured logging with structlog

    Args:
        env: Environment (dev/stage/prod)
        log_level: Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)
        log_dir: Directory for log files (default: ./logs)
        enable_console: Enable console logging
        enable_file: Enable file logging
        json_format: Use JSON format for logs (recommended for production)
    """
    # Create log directory
    if log_dir is None:
        log_dir = Path("./logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, log_level.upper()),
        handlers=[],
    )

    # Build processor chain
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        CorrelationIDProcessor(),
        TimestampProcessor(),
        EnvironmentProcessor(env),
        add_app_context,
        censor_sensitive_data,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    # Add appropriate renderer based on format
    if json_format:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Set up handlers for standard library logging
    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))

        # Use colored output for console in dev
        if env == "dev" and not json_format:
            console_formatter = structlog.stdlib.ProcessorFormatter(
                processor=structlog.dev.ConsoleRenderer(colors=True),
                foreign_pre_chain=processors[:-1],
            )
        else:
            console_formatter = structlog.stdlib.ProcessorFormatter(
                processor=structlog.processors.JSONRenderer(),
                foreign_pre_chain=processors[:-1],
            )

        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)

    # File handler (rotating)
    if enable_file:
        log_file = log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=50 * 1024 * 1024,  # 50MB
            backupCount=10,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)  # Log everything to file

        # Always use JSON for file output
        file_formatter = structlog.stdlib.ProcessorFormatter(
            processor=structlog.processors.JSONRenderer(),
            foreign_pre_chain=processors[:-1],
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

        # Separate error log file
        error_log_file = log_dir / \
            f"errors_{datetime.now().strftime('%Y%m%d')}.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=50 * 1024 * 1024,  # 50MB
            backupCount=10,
            encoding="utf-8",
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        root_logger.addHandler(error_handler)


def get_logger(name: str = None) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger instance

    Args:
        name: Logger name (typically __name__)

    Returns:
        Structured logger instance
    """
    if name:
        return structlog.get_logger(name)
    return structlog.get_logger()


def set_correlation_id(correlation_id: str | None = None) -> str:
    """
    Set correlation ID for current context

    Args:
        correlation_id: Correlation ID to set (generates new UUID if None)

    Returns:
        The correlation ID that was set
    """
    if correlation_id is None:
        correlation_id = str(uuid.uuid4())
    correlation_id_var.set(correlation_id)
    return correlation_id


def get_correlation_id() -> str | None:
    """
    Get current correlation ID

    Returns:
        Current correlation ID or None
    """
    return correlation_id_var.get()


def clear_correlation_id() -> None:
    """Clear correlation ID from current context"""
    correlation_id_var.set(None)


def set_log_level(level: str) -> None:
    """
    Set log level at runtime

    Args:
        level: Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)
    """
    log_level = getattr(logging, level.upper())
    logging.getLogger().setLevel(log_level)

    # Update all handlers
    for handler in logging.getLogger().handlers:
        if isinstance(
                handler,
                logging.StreamHandler) and handler.stream == sys.stdout:
            # Console handler - respect the level
            handler.setLevel(log_level)


def get_log_level() -> str:
    """
    Get current log level

    Returns:
        Current log level name
    """
    return logging.getLevelName(logging.getLogger().level)


class LogContext:
    """Context manager for adding context to logs"""

    def __init__(self, **kwargs):
        self.context = kwargs
        self.token = None

    def __enter__(self):
        """Enter context and bind variables"""
        structlog.contextvars.bind_contextvars(**self.context)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context and unbind variables"""
        structlog.contextvars.unbind_contextvars(*self.context.keys())


class CorrelationContext:
    """Context manager for correlation ID"""

    def __init__(self, correlation_id: str | None = None):
        self.correlation_id = correlation_id
        self.previous_id = None

    def __enter__(self):
        """Enter context and set correlation ID"""
        self.previous_id = get_correlation_id()
        set_correlation_id(self.correlation_id)
        return self.correlation_id or get_correlation_id()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context and restore previous correlation ID"""
        if self.previous_id:
            set_correlation_id(self.previous_id)
        else:
            clear_correlation_id()


def log_function_call(logger: structlog.stdlib.BoundLogger):
    """
    Decorator to log function calls with timing

    Args:
        logger: Logger instance to use

    Example:
        @log_function_call(logger)
        def my_function(arg1, arg2):
            pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            import time
            start_time = time.time()

            logger.debug(
                "function_call_start",
                function=func.__name__,
                module=func.__module__,
            )

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                logger.debug(
                    "function_call_end",
                    function=func.__name__,
                    module=func.__module__,
                    duration_ms=round(duration * 1000, 2),
                    success=True,
                )

                return result
            except Exception as e:
                duration = time.time() - start_time

                logger.error(
                    "function_call_error",
                    function=func.__name__,
                    module=func.__module__,
                    duration_ms=round(duration * 1000, 2),
                    error=str(e),
                    error_type=type(e).__name__,
                )
                raise

        return wrapper
    return decorator


# Convenience functions for common log patterns
def log_request(
    logger: structlog.stdlib.BoundLogger,
    method: str,
    path: str,
    user_id: str | None = None,
    **kwargs
) -> None:
    """Log HTTP request"""
    logger.info(
        "http_request",
        method=method,
        path=path,
        user_id=user_id,
        **kwargs
    )


def log_response(
    logger: structlog.stdlib.BoundLogger,
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    **kwargs
) -> None:
    """Log HTTP response"""
    logger.info(
        "http_response",
        method=method,
        path=path,
        status_code=status_code,
        duration_ms=duration_ms,
        **kwargs
    )


def log_database_query(
    logger: structlog.stdlib.BoundLogger,
    query_type: str,
    table: str,
    duration_ms: float,
    rows_affected: int | None = None,
    **kwargs
) -> None:
    """Log database query"""
    logger.debug(
        "database_query",
        query_type=query_type,
        table=table,
        duration_ms=duration_ms,
        rows_affected=rows_affected,
        **kwargs
    )


def log_cache_operation(
    logger: structlog.stdlib.BoundLogger,
    operation: str,
    key: str,
    hit: bool | None = None,
    **kwargs
) -> None:
    """Log cache operation"""
    logger.debug(
        "cache_operation",
        operation=operation,
        key=key,
        hit=hit,
        **kwargs
    )


def log_job_event(
    logger: structlog.stdlib.BoundLogger,
    event_type: str,
    job_id: str,
    job_type: str,
    **kwargs
) -> None:
    """Log job event"""
    logger.info(
        "job_event",
        event_type=event_type,
        job_id=job_id,
        job_type=job_type,
        **kwargs
    )


def log_error(
    logger: structlog.stdlib.BoundLogger,
    error: Exception,
    context: dict[str, Any] | None = None,
    **kwargs
) -> None:
    """
    Log error with full context

    Args:
        logger: Logger instance
        error: Exception that occurred
        context: Additional context dictionary
        **kwargs: Additional key-value pairs to log
    """
    error_data = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        **kwargs
    }

    if context:
        error_data["context"] = context

    logger.error("error_occurred", **error_data, exc_info=True)


def log_security_event(
    logger: structlog.stdlib.BoundLogger,
    event_type: str,
    user_id: str | None = None,
    ip_address: str | None = None,
    success: bool = True,
    **kwargs
) -> None:
    """Log security event"""
    logger.warning(
        "security_event",
        event_type=event_type,
        user_id=user_id,
        ip_address=ip_address,
        success=success,
        **kwargs
    )


def log_performance_metric(
    logger: structlog.stdlib.BoundLogger,
    metric_name: str,
    value: float,
    unit: str = "ms",
    **kwargs
) -> None:
    """Log performance metric"""
    logger.info(
        "performance_metric",
        metric_name=metric_name,
        value=value,
        unit=unit,
        **kwargs
    )
