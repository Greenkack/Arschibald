"""
Example Usage of Structured Logging System
===========================================

Demonstrates various features of the structured logging system.
"""

import time

from core.config import load_config
from core.logging_config import (
    adjust_log_level_runtime,
    get_current_log_level,
    init_logging_from_config,
)
from core.logging_system import (
    CorrelationContext,
    LogContext,
    get_logger,
    log_cache_operation,
    log_database_query,
    log_error,
    log_job_event,
    log_performance_metric,
    log_request,
    log_response,
    log_security_event,
)


def example_basic_logging():
    """Example: Basic structured logging"""
    print("\n=== Example 1: Basic Logging ===")

    logger = get_logger(__name__)

    # Simple log messages with structured fields
    logger.info("application_started", version="1.0.0", environment="dev")
    logger.debug(
        "debug_information",
        module="example",
        function="basic_logging")
    logger.warning("warning_message", reason="demonstration", severity="low")
    logger.error("error_message", error_type="Example", recoverable=True)


def example_correlation_ids():
    """Example: Using correlation IDs"""
    print("\n=== Example 2: Correlation IDs ===")

    logger = get_logger(__name__)

    # Automatic correlation ID generation
    with CorrelationContext() as correlation_id:
        logger.info("request_started", endpoint="/api/users")
        time.sleep(0.1)  # Simulate processing
        logger.info("processing_data", records=100)
        time.sleep(0.1)
        logger.info("request_completed", duration_ms=200)
        print(f"Correlation ID: {correlation_id}")

    # Manual correlation ID
    with CorrelationContext("custom-request-123"):
        logger.info("custom_request_started")
        logger.info("custom_request_completed")


def example_log_context():
    """Example: Adding context to logs"""
    print("\n=== Example 3: Log Context ===")

    logger = get_logger(__name__)

    # Add context variables that appear in all logs within the block
    with LogContext(user_id="user123", session_id="sess456", tenant="acme"):
        logger.info("user_login", method="password")
        logger.info("user_action", action="view_dashboard")
        logger.info("user_logout", duration_seconds=300)


def example_convenience_functions():
    """Example: Using convenience logging functions"""
    print("\n=== Example 4: Convenience Functions ===")

    logger = get_logger(__name__)

    # HTTP request/response logging
    log_request(logger, "GET", "/api/users", user_id="user123")
    log_response(logger, "GET", "/api/users", 200, 45.5)

    # Database query logging
    log_database_query(logger, "SELECT", "users", 12.3, rows_affected=5)
    log_database_query(logger, "INSERT", "orders", 8.7, rows_affected=1)

    # Cache operation logging
    log_cache_operation(logger, "get", "user:123", hit=True)
    log_cache_operation(logger, "set", "user:456", hit=False)

    # Job event logging
    log_job_event(
        logger,
        event_type="started",
        job_id="job-123",
        job_type="calculation",
        priority=1)
    log_job_event(
        logger,
        event_type="completed",
        job_id="job-123",
        job_type="calculation",
        duration_ms=5000)

    # Security event logging
    log_security_event(
        logger,
        "login_attempt",
        user_id="user123",
        ip_address="192.168.1.1",
        success=True,
    )

    # Performance metric logging
    log_performance_metric(
        logger,
        "response_time",
        45.5,
        unit="ms",
        endpoint="/api/users")
    log_performance_metric(logger, "memory_usage", 512, unit="MB")


def example_error_logging():
    """Example: Error logging with context"""
    print("\n=== Example 5: Error Logging ===")

    logger = get_logger(__name__)

    try:
        # Simulate an error
        result = 10 / 0
    except ZeroDivisionError as e:
        log_error(
            logger,
            e,
            context={
                "operation": "division",
                "numerator": 10,
                "denominator": 0,
            },
        )


def example_sensitive_data_censoring():
    """Example: Sensitive data censoring"""
    print("\n=== Example 6: Sensitive Data Censoring ===")

    logger = get_logger(__name__)

    # These sensitive fields will be automatically censored
    logger.info(
        "api_call",
        api_key="sk-1234567890abcdef",  # Will be [REDACTED]
        password="secret123",            # Will be [REDACTED]
        token="bearer xyz123",           # Will be [REDACTED]
        username="john_doe",             # Will be visible
        endpoint="/api/data",            # Will be visible
    )


def example_runtime_log_level():
    """Example: Runtime log level adjustment"""
    print("\n=== Example 7: Runtime Log Level Adjustment ===")

    logger = get_logger(__name__)

    # Show current log level
    current_level = get_current_log_level()
    print(f"Current log level: {current_level}")

    # Set to DEBUG
    adjust_log_level_runtime("DEBUG")
    logger.debug("This debug message will appear")
    print(f"Log level changed to: {get_current_log_level()}")

    # Set to WARNING
    adjust_log_level_runtime("WARNING")
    logger.info("This info message will NOT appear")
    logger.warning("This warning message will appear")
    print(f"Log level changed to: {get_current_log_level()}")

    # Reset to INFO
    adjust_log_level_runtime("INFO")


def example_nested_correlation():
    """Example: Nested correlation contexts"""
    print("\n=== Example 8: Nested Correlation Contexts ===")

    logger = get_logger(__name__)

    with CorrelationContext("parent-request-123") as parent_id:
        logger.info("parent_request_started")

        # Nested context with different correlation ID
        with CorrelationContext("child-request-456") as child_id:
            logger.info("child_request_started")
            logger.info("child_request_completed")

        # Back to parent correlation ID
        logger.info("parent_request_completed")
        print(f"Parent ID: {parent_id}, Child ID: {child_id}")


def example_structured_data():
    """Example: Logging structured data"""
    print("\n=== Example 9: Structured Data ===")

    logger = get_logger(__name__)

    # Log with nested structures
    logger.info(
        "user_profile_updated",
        user={
            "id": "user123",
            "name": "John Doe",
            "email": "john@example.com",
        },
        changes={
            "name": {"old": "John", "new": "John Doe"},
            "email": {"old": "j@example.com", "new": "john@example.com"},
        },
        metadata={
            "updated_by": "admin",
            "timestamp": "2025-01-19T10:30:45Z",
        },
    )


def example_performance_tracking():
    """Example: Performance tracking with logging"""
    print("\n=== Example 10: Performance Tracking ===")

    logger = get_logger(__name__)

    with CorrelationContext() as correlation_id:
        start_time = time.time()

        logger.info("operation_started", operation="data_processing")

        # Simulate work
        time.sleep(0.1)
        checkpoint1 = time.time()
        log_performance_metric(
            logger,
            "checkpoint_1",
            (checkpoint1 - start_time) * 1000,
            unit="ms",
        )

        time.sleep(0.1)
        checkpoint2 = time.time()
        log_performance_metric(
            logger,
            "checkpoint_2",
            (checkpoint2 - checkpoint1) * 1000,
            unit="ms",
        )

        total_duration = (time.time() - start_time) * 1000
        logger.info(
            "operation_completed",
            operation="data_processing",
            duration_ms=total_duration,
        )


def main():
    """Run all examples"""
    print("=" * 60)
    print("Structured Logging System Examples")
    print("=" * 60)

    # Initialize logging
    config = load_config()
    init_logging_from_config(config)

    # Run examples
    example_basic_logging()
    example_correlation_ids()
    example_log_context()
    example_convenience_functions()
    example_error_logging()
    example_sensitive_data_censoring()
    example_runtime_log_level()
    example_nested_correlation()
    example_structured_data()
    example_performance_tracking()

    print("\n" + "=" * 60)
    print("Examples completed! Check logs/ directory for output.")
    print("=" * 60)


if __name__ == "__main__":
    main()
