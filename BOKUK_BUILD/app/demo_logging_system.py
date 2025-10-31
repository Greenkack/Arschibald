"""
Demo: Structured Logging System

This script demonstrates the structured logging capabilities:
- Correlation ID generation and propagation
- Context management
- PII masking
- Error logging
- Event tracking
- Different output formats for dev/prod
"""

import time
from datetime import datetime

from core.config import AppConfig, Environment
from core.logging_config import (
    CorrelationIdContext,
    LogContext,
    get_logger,
    log_error,
    set_log_level,
    setup_logging,
    track,
)


def demo_basic_logging():
    """Demo basic structured logging"""
    print("\n" + "=" * 60)
    print("DEMO 1: Basic Structured Logging")
    print("=" * 60)

    logger = get_logger(__name__)

    # Simple log messages with structured data
    logger.info("application_started", version="1.0.0", env="development")

    logger.info(
        "user_login",
        user_id="user_123",
        username="john_doe",
        ip_address="192.168.1.100",
        login_method="oauth",
    )

    logger.warning(
        "cache_miss",
        cache_key="user_profile_123",
        cache_type="redis",
        ttl_seconds=3600,
    )

    logger.error(
        "database_error",
        error_type="ConnectionTimeout",
        database="postgresql",
        retry_count=3,
    )


def demo_correlation_id():
    """Demo correlation ID for request tracing"""
    print("\n" + "=" * 60)
    print("DEMO 2: Correlation ID for Request Tracing")
    print("=" * 60)

    logger = get_logger(__name__)

    # Simulate multiple requests with correlation IDs
    print("\n--- Request 1 ---")
    with CorrelationIdContext() as correlation_id:
        logger.info("request_started", method="GET", path="/api/users")
        time.sleep(0.1)
        logger.info("database_query", query="SELECT * FROM users", rows=10)
        time.sleep(0.1)
        logger.info("request_completed", status=200, duration_ms=250)
        print(f"Correlation ID: {correlation_id}")

    print("\n--- Request 2 ---")
    with CorrelationIdContext() as correlation_id:
        logger.info("request_started", method="POST", path="/api/orders")
        time.sleep(0.1)
        logger.info("validation_passed", fields=5)
        time.sleep(0.1)
        logger.info("request_completed", status=201, duration_ms=180)
        print(f"Correlation ID: {correlation_id}")


def demo_log_context():
    """Demo log context for adding scope-wide context"""
    print("\n" + "=" * 60)
    print("DEMO 3: Log Context for Scope-Wide Context")
    print("=" * 60)

    logger = get_logger(__name__)

    # All logs within this context include user_id and session
    with LogContext(user_id="user_456", session="session_abc"):
        logger.info("user_action", action="view_profile")
        logger.info("user_action", action="edit_profile")
        logger.info("user_action", action="save_profile")

    # Nested contexts
    print("\n--- Nested Contexts ---")
    with LogContext(request_id="req_123"):
        logger.info("processing_request")

        with LogContext(user_id="user_789"):
            logger.info("user_authenticated")
            logger.info("loading_user_data")

        logger.info("request_completed")


def demo_pii_masking():
    """Demo PII masking in logs"""
    print("\n" + "=" * 60)
    print("DEMO 4: PII Masking for Security")
    print("=" * 60)

    logger = get_logger(__name__)

    # Sensitive data is automatically masked
    logger.info(
        "user_registration",
        username="john_doe",
        email="john@example.com",
        password="SuperSecret123!",  # Will be masked
        api_key="sk-1234567890abcdef",  # Will be masked
    )

    logger.info(
        "payment_processed",
        user_id="user_123",
        amount=99.99,
        credit_card="4111-1111-1111-1111",  # Will be masked
        token="tok_abc123xyz",  # Will be masked
    )

    # Nested sensitive data
    logger.info(
        "user_data",
        user={
            "name": "John Doe",
            "email": "john@example.com",
            "password": "secret",  # Will be masked
            "preferences": {"theme": "dark", "api_key": "key123"},  # Masked
        },
    )


def demo_error_logging():
    """Demo error logging with context"""
    print("\n" + "=" * 60)
    print("DEMO 5: Error Logging with Full Context")
    print("=" * 60)

    logger = get_logger(__name__)

    # Simple error
    try:
        result = 10 / 0
    except ZeroDivisionError as e:
        log_error(e, {"operation": "division", "numerator": 10, "denominator": 0})

    # Error with nested calls (shows traceback)
    def inner_function():
        raise ValueError("Invalid configuration")

    def outer_function():
        inner_function()

    try:
        outer_function()
    except ValueError as e:
        log_error(
            e,
            {
                "user_id": "user_123",
                "operation": "load_config",
                "config_file": "app.json",
            },
        )


def demo_event_tracking():
    """Demo event tracking for analytics"""
    print("\n" + "=" * 60)
    print("DEMO 6: Event Tracking for Analytics")
    print("=" * 60)

    # Track various user events
    track(
        "user_login",
        {"user_id": "user_123", "method": "oauth", "provider": "google"},
    )

    track(
        "form_submitted",
        {
            "form_id": "contact_form",
            "duration_ms": 1234,
            "fields_filled": 5,
            "success": True,
        },
    )

    track(
        "feature_used",
        {"feature": "export_pdf", "user_tier": "premium", "file_size_mb": 2.5},
    )

    track(
        "checkout_completed",
        {
            "order_id": "order_789",
            "total_amount": 149.99,
            "items_count": 3,
            "payment_method": "credit_card",
        },
    )


def demo_log_levels():
    """Demo different log levels"""
    print("\n" + "=" * 60)
    print("DEMO 7: Log Levels and Runtime Adjustment")
    print("=" * 60)

    logger = get_logger(__name__)

    print("\n--- All Levels (DEBUG) ---")
    set_log_level("DEBUG")
    logger.debug("debug_message", detail="This is a debug message")
    logger.info("info_message", detail="This is an info message")
    logger.warning("warning_message", detail="This is a warning")
    logger.error("error_message", detail="This is an error")

    print("\n--- Only Warnings and Above (WARNING) ---")
    set_log_level("WARNING")
    logger.debug("debug_message", detail="This won't appear")
    logger.info("info_message", detail="This won't appear either")
    logger.warning("warning_message", detail="This will appear")
    logger.error("error_message", detail="This will also appear")


def demo_production_vs_development():
    """Demo different output formats for prod vs dev"""
    print("\n" + "=" * 60)
    print("DEMO 8: Production vs Development Output")
    print("=" * 60)

    print("\n--- Development Mode (Human-Readable) ---")
    dev_config = AppConfig()
    dev_config.env = Environment.DEV
    dev_config.debug = True
    setup_logging(dev_config)

    logger = get_logger(__name__)
    logger.info("user_action", user_id="123", action="login", timestamp=datetime.now())

    print("\n--- Production Mode (JSON) ---")
    prod_config = AppConfig()
    prod_config.env = Environment.PROD
    prod_config.debug = False
    setup_logging(prod_config)

    logger = get_logger(__name__)
    logger.info("user_action", user_id="123", action="login", timestamp=datetime.now())


def demo_complete_request_flow():
    """Demo complete request handling with all features"""
    print("\n" + "=" * 60)
    print("DEMO 9: Complete Request Flow")
    print("=" * 60)

    logger = get_logger(__name__)

    # Simulate a complete request with correlation ID and context
    with CorrelationIdContext() as correlation_id:
        logger.info(
            "request_received",
            method="POST",
            path="/api/orders",
            content_type="application/json",
        )

        with LogContext(user_id="user_123", session="session_abc"):
            # Authentication
            logger.info("authenticating_user")
            time.sleep(0.05)
            logger.info("user_authenticated", roles=["user", "premium"])

            # Validation
            logger.info("validating_request", fields=["items", "shipping", "payment"])
            time.sleep(0.05)
            logger.info("validation_passed")

            # Business logic
            logger.info("processing_order", items_count=3, total_amount=149.99)
            time.sleep(0.1)

            # Database operations
            logger.info("database_write", table="orders", operation="INSERT")
            time.sleep(0.05)
            logger.info("database_write", table="order_items", operation="BULK_INSERT")

            # Track event
            track(
                "order_created",
                {
                    "order_id": "order_789",
                    "user_id": "user_123",
                    "total": 149.99,
                    "items": 3,
                },
            )

            logger.info(
                "request_completed",
                status=201,
                duration_ms=250,
                correlation_id=correlation_id,
            )


def main():
    """Run all demos"""
    print("\n" + "=" * 60)
    print("STRUCTURED LOGGING SYSTEM DEMO")
    print("=" * 60)

    # Setup logging for development
    config = AppConfig()
    config.env = Environment.DEV
    config.debug = True
    setup_logging(config)

    # Run demos
    demo_basic_logging()
    demo_correlation_id()
    demo_log_context()
    demo_pii_masking()
    demo_error_logging()
    demo_event_tracking()
    demo_log_levels()
    demo_production_vs_development()
    demo_complete_request_flow()

    print("\n" + "=" * 60)
    print("DEMO COMPLETED")
    print("=" * 60)
    print("\nKey Features Demonstrated:")
    print("✅ Structured logging with key-value pairs")
    print("✅ Correlation ID generation and propagation")
    print("✅ Context management for scope-wide data")
    print("✅ Automatic PII masking")
    print("✅ Error logging with full context")
    print("✅ Event tracking for analytics")
    print("✅ Runtime log level adjustment")
    print("✅ Environment-specific output formats")
    print("\nSee core/LOGGING_QUICK_REFERENCE.md for more details")


if __name__ == "__main__":
    main()
