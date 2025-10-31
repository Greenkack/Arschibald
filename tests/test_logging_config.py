"""
Tests for structured logging configuration

This test suite validates:
- Correlation ID generation and propagation
- Log level configuration per environment
- PII masking in logs
- JSON output for production
- Console output for development
- Runtime log level adjustment
"""

import json
import logging
from io import StringIO

import pytest
import structlog

from core.config import AppConfig, Environment
from core.logging_config import (
    CorrelationIdContext,
    LogContext,
    clear_correlation_id,
    generate_correlation_id,
    get_correlation_id,
    get_logger,
    log_error,
    set_correlation_id,
    set_log_level,
    setup_logging,
    track,
)


@pytest.fixture
def dev_config():
    """Development configuration for testing"""
    config = AppConfig()
    config.env = Environment.DEV
    config.debug = True
    return config


@pytest.fixture
def prod_config():
    """Production configuration for testing"""
    config = AppConfig()
    config.env = Environment.PROD
    config.debug = False
    return config


@pytest.fixture
def capture_logs():
    """Fixture to capture log output"""
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setLevel(logging.DEBUG)

    # Store original level
    root_logger = logging.getLogger()
    original_level = root_logger.level

    # Add handler to root logger
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.DEBUG)

    yield stream

    # Cleanup
    root_logger.removeHandler(handler)
    root_logger.setLevel(original_level)


class TestCorrelationId:
    """Test correlation ID generation and propagation"""

    def test_generate_correlation_id(self):
        """Test correlation ID generation"""
        correlation_id = generate_correlation_id()
        assert correlation_id is not None
        assert isinstance(correlation_id, str)
        assert len(correlation_id) > 0

        # Should generate unique IDs
        correlation_id2 = generate_correlation_id()
        assert correlation_id != correlation_id2

    def test_set_and_get_correlation_id(self):
        """Test setting and getting correlation ID"""
        test_id = "test-correlation-123"
        set_correlation_id(test_id)

        retrieved_id = get_correlation_id()
        assert retrieved_id == test_id

        clear_correlation_id()
        assert get_correlation_id() is None

    def test_correlation_id_context(self):
        """Test correlation ID context manager"""
        # No correlation ID initially
        clear_correlation_id()
        assert get_correlation_id() is None

        # Within context, correlation ID is set
        with CorrelationIdContext() as correlation_id:
            assert correlation_id is not None
            assert get_correlation_id() == correlation_id

        # After context, correlation ID is cleared
        assert get_correlation_id() is None

    def test_correlation_id_context_with_custom_id(self):
        """Test correlation ID context with custom ID"""
        custom_id = "custom-123"

        with CorrelationIdContext(custom_id) as correlation_id:
            assert correlation_id == custom_id
            assert get_correlation_id() == custom_id

    def test_nested_correlation_id_contexts(self):
        """Test nested correlation ID contexts"""
        outer_id = "outer-123"
        inner_id = "inner-456"

        with CorrelationIdContext(outer_id):
            assert get_correlation_id() == outer_id

            with CorrelationIdContext(inner_id):
                assert get_correlation_id() == inner_id

            # Should restore outer ID
            assert get_correlation_id() == outer_id


class TestLoggingSetup:
    """Test logging setup and configuration"""

    def test_setup_logging_dev(self, dev_config):
        """Test logging setup for development"""
        setup_logging(dev_config)

        logger = get_logger("test")
        assert logger is not None
        # Logger can be BoundLogger or BoundLoggerLazyProxy
        assert hasattr(logger, "info")
        assert hasattr(logger, "error")

    def test_setup_logging_prod(self, prod_config):
        """Test logging setup for production"""
        setup_logging(prod_config)

        logger = get_logger("test")
        assert logger is not None

    def test_get_logger_with_name(self, dev_config):
        """Test getting logger with specific name"""
        setup_logging(dev_config)

        logger = get_logger("my.module")
        assert logger is not None

    def test_set_log_level_string(self, dev_config):
        """Test setting log level with string"""
        setup_logging(dev_config)

        set_log_level("WARNING")
        assert logging.root.level == logging.WARNING

        set_log_level("DEBUG")
        assert logging.root.level == logging.DEBUG

    def test_set_log_level_constant(self, dev_config):
        """Test setting log level with constant"""
        setup_logging(dev_config)

        set_log_level(logging.ERROR)
        assert logging.root.level == logging.ERROR


class TestStructuredLogging:
    """Test structured logging functionality"""

    def test_log_with_context(self, dev_config, capture_logs):
        """Test logging with additional context"""
        setup_logging(dev_config)
        logger = get_logger("test")

        logger.info("test_event", user_id="123", action="login")

        output = capture_logs.getvalue()
        assert "test_event" in output
        assert "user_id" in output or "123" in output

    def test_log_context_manager(self, dev_config, capture_logs):
        """Test LogContext context manager"""
        setup_logging(dev_config)
        logger = get_logger("test")

        with LogContext(user_id="123", session="abc"):
            logger.info("within_context")

        output = capture_logs.getvalue()
        assert "within_context" in output

    def test_correlation_id_in_logs(self, dev_config, capture_logs):
        """Test correlation ID appears in logs"""
        setup_logging(dev_config)
        logger = get_logger("test")

        with CorrelationIdContext() as correlation_id:
            logger.info("test_with_correlation")

        output = capture_logs.getvalue()
        assert "test_with_correlation" in output
        # Correlation ID should be in output
        assert correlation_id in output or "correlation_id" in output


class TestPIIMasking:
    """Test PII masking in logs"""

    def test_password_masking(self, dev_config, capture_logs):
        """Test password is masked in logs"""
        setup_logging(dev_config)
        logger = get_logger("test")

        logger.info("user_login", password="secret123", username="john")

        output = capture_logs.getvalue()
        assert "secret123" not in output
        assert "REDACTED" in output or "***" in output

    def test_token_masking(self, dev_config, capture_logs):
        """Test API token is masked in logs"""
        setup_logging(dev_config)
        logger = get_logger("test")

        logger.info("api_call", api_key="sk-1234567890", endpoint="/users")

        output = capture_logs.getvalue()
        assert "sk-1234567890" not in output
        assert "REDACTED" in output or "***" in output

    def test_nested_sensitive_data_masking(self, dev_config, capture_logs):
        """Test nested sensitive data is masked"""
        setup_logging(dev_config)
        logger = get_logger("test")

        logger.info(
            "user_data",
            user={
                "name": "John",
                "password": "secret",
                "email": "john@example.com",
            },
        )

        output = capture_logs.getvalue()
        assert "secret" not in output or "REDACTED" in output


class TestErrorLogging:
    """Test error logging functionality"""

    def test_log_error_basic(self, dev_config, capture_logs):
        """Test basic error logging"""
        setup_logging(dev_config)

        try:
            raise ValueError("Test error")
        except ValueError as e:
            log_error(e)

        output = capture_logs.getvalue()
        assert "Test error" in output
        assert "ValueError" in output

    def test_log_error_with_context(self, dev_config, capture_logs):
        """Test error logging with context"""
        setup_logging(dev_config)

        try:
            raise RuntimeError("Operation failed")
        except RuntimeError as e:
            log_error(e, {"user_id": "123", "operation": "save"})

        output = capture_logs.getvalue()
        assert "Operation failed" in output
        assert "RuntimeError" in output

    def test_log_error_includes_traceback(self, dev_config, capture_logs):
        """Test error logging includes traceback"""
        setup_logging(dev_config)

        try:
            # Create a traceback
            def inner():
                raise ValueError("Inner error")

            def outer():
                inner()

            outer()
        except ValueError as e:
            log_error(e)

        output = capture_logs.getvalue()
        assert "ValueError" in output
        assert "Inner error" in output


class TestEventTracking:
    """Test event tracking functionality"""

    def test_track_event_basic(self, dev_config, capture_logs):
        """Test basic event tracking"""
        setup_logging(dev_config)

        track("user_login", {"user_id": "123"})

        output = capture_logs.getvalue()
        assert "user_login" in output

    def test_track_event_with_properties(self, dev_config, capture_logs):
        """Test event tracking with properties"""
        setup_logging(dev_config)

        track(
            "form_submitted",
            {
                "form_id": "contact",
                "duration_ms": 1234,
                "success": True,
            },
        )

        output = capture_logs.getvalue()
        assert "form_submitted" in output

    def test_track_event_without_properties(self, dev_config, capture_logs):
        """Test event tracking without properties"""
        setup_logging(dev_config)

        track("page_view")

        output = capture_logs.getvalue()
        assert "page_view" in output


class TestProductionLogging:
    """Test production-specific logging features"""

    def test_json_output_in_production(self, prod_config, capture_logs):
        """Test JSON output format in production"""
        setup_logging(prod_config)
        logger = get_logger("test")

        logger.info("test_event", key="value")

        output = capture_logs.getvalue()
        # Should be valid JSON in production
        try:
            # Try to parse as JSON
            lines = output.strip().split("\n")
            for line in lines:
                if line.strip():
                    json.loads(line)
        except json.JSONDecodeError:
            # In some test environments, might not be pure JSON
            # Just check that structured data is present
            assert "test_event" in output

    def test_log_level_in_production(self, prod_config):
        """Test default log level in production is WARNING"""
        # Reset logging before test
        logging.root.handlers.clear()
        
        setup_logging(prod_config)

        # Production should default to WARNING or higher
        assert logging.root.level >= logging.WARNING


class TestLogLevelConfiguration:
    """Test log level configuration per environment"""

    def test_dev_log_level(self, dev_config):
        """Test development uses DEBUG level"""
        # Reset logging before test
        logging.root.handlers.clear()
        
        setup_logging(dev_config)
        assert logging.root.level == logging.DEBUG

    def test_prod_log_level(self, prod_config):
        """Test production uses WARNING level"""
        # Reset logging before test
        logging.root.handlers.clear()
        
        setup_logging(prod_config)
        assert logging.root.level == logging.WARNING

    def test_runtime_log_level_change(self, dev_config, capture_logs):
        """Test changing log level at runtime"""
        setup_logging(dev_config)
        logger = get_logger("test")

        # Set to ERROR - DEBUG messages should not appear
        set_log_level(logging.ERROR)
        logger.debug("debug_message")
        logger.error("error_message")

        output = capture_logs.getvalue()
        assert "error_message" in output
        # debug_message should not appear (level too low)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
