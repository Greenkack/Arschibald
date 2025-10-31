"""
Tests for Structured Logging System
====================================

Tests for structured logging with correlation IDs, JSON output,
and environment-specific configuration.

Requirements: 7.6, 9.5, 12.5
"""

import json
import logging
import tempfile
import uuid
from pathlib import Path

import pytest

from core.logging_system import (
    CorrelationContext,
    LogContext,
    clear_correlation_id,
    get_correlation_id,
    get_log_level,
    get_logger,
    log_cache_operation,
    log_database_query,
    log_error,
    log_job_event,
    log_performance_metric,
    log_request,
    log_response,
    log_security_event,
    set_correlation_id,
    set_log_level,
    setup_structured_logging,
)


@pytest.fixture
def temp_log_dir():
    """Create temporary log directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)
        # Close all handlers to release file locks
        import logging
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            handler.close()
            root_logger.removeHandler(handler)


@pytest.fixture
def logger(temp_log_dir):
    """Set up logger for testing"""
    setup_structured_logging(
        env="test",
        log_level="DEBUG",
        log_dir=temp_log_dir,
        enable_console=False,
        enable_file=True,
        json_format=True,
    )
    logger = get_logger("test")
    yield logger
    # Close all handlers after test
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        handler.close()
        root_logger.removeHandler(handler)


class TestCorrelationID:
    """Test correlation ID functionality"""

    def test_set_and_get_correlation_id(self):
        """Test setting and getting correlation ID"""
        test_id = str(uuid.uuid4())
        result = set_correlation_id(test_id)

        assert result == test_id
        assert get_correlation_id() == test_id

    def test_auto_generate_correlation_id(self):
        """Test auto-generation of correlation ID"""
        result = set_correlation_id()

        assert result is not None
        assert get_correlation_id() == result
        # Verify it's a valid UUID
        uuid.UUID(result)

    def test_clear_correlation_id(self):
        """Test clearing correlation ID"""
        set_correlation_id("test-id")
        clear_correlation_id()

        assert get_correlation_id() is None

    def test_correlation_context_manager(self):
        """Test correlation context manager"""
        test_id = "context-test-id"

        with CorrelationContext(test_id) as ctx_id:
            assert ctx_id == test_id
            assert get_correlation_id() == test_id

        # Should be cleared after context
        assert get_correlation_id() is None

    def test_correlation_context_auto_generate(self):
        """Test correlation context with auto-generation"""
        with CorrelationContext() as ctx_id:
            assert ctx_id is not None
            assert get_correlation_id() == ctx_id

        assert get_correlation_id() is None

    def test_correlation_context_nesting(self):
        """Test nested correlation contexts"""
        outer_id = "outer-id"
        inner_id = "inner-id"

        with CorrelationContext(outer_id):
            assert get_correlation_id() == outer_id

            with CorrelationContext(inner_id):
                assert get_correlation_id() == inner_id

            # Should restore outer ID
            assert get_correlation_id() == outer_id

        assert get_correlation_id() is None


class TestLogContext:
    """Test log context functionality"""

    def test_log_context_binding(self, logger):
        """Test context variable binding"""
        with LogContext(user_id="user123", request_id="req456"):
            logger.info("test_message")
            # Context should be bound during this block

    def test_log_context_unbinding(self, logger):
        """Test context variable unbinding"""
        with LogContext(user_id="user123"):
            pass

        # Context should be unbound after block
        logger.info("test_message_after")


class TestLogLevelManagement:
    """Test log level management"""

    def test_set_log_level(self):
        """Test setting log level"""
        set_log_level("DEBUG")
        assert get_log_level() == "DEBUG"

        set_log_level("INFO")
        assert get_log_level() == "INFO"

        set_log_level("WARNING")
        assert get_log_level() == "WARNING"

    def test_set_log_level_case_insensitive(self):
        """Test log level setting is case-insensitive"""
        set_log_level("debug")
        assert get_log_level() == "DEBUG"

        set_log_level("info")
        assert get_log_level() == "INFO"


class TestStructuredLogging:
    """Test structured logging functionality"""

    def test_basic_logging(self, logger, temp_log_dir):
        """Test basic structured logging"""
        logger.info("test_event", key1="value1", key2=42)

        # Verify log file was created
        log_files = list(temp_log_dir.glob("app_*.log"))
        assert len(log_files) > 0

    def test_json_output(self, logger, temp_log_dir):
        """Test JSON output format"""
        test_message = "json_test_event"
        logger.info(test_message, test_key="test_value")

        # Flush handlers
        for handler in logging.getLogger().handlers:
            handler.flush()

        # Read log file
        log_files = list(temp_log_dir.glob("app_*.log"))
        assert len(log_files) > 0

        with open(log_files[0]) as f:
            lines = f.readlines()
            assert len(lines) > 0

            # Parse JSON - the line itself is the JSON
            log_entry = json.loads(lines[-1].strip())
            assert log_entry["event"] == test_message
            assert log_entry["test_key"] == "test_value"
            assert "timestamp" in log_entry
            assert "environment" in log_entry

    def test_correlation_id_in_logs(self, logger, temp_log_dir):
        """Test correlation ID appears in logs"""
        test_id = "test-correlation-id"
        set_correlation_id(test_id)

        logger.info("correlation_test")

        # Flush handlers
        for handler in logging.getLogger().handlers:
            handler.flush()

        # Read log file
        log_files = list(temp_log_dir.glob("app_*.log"))
        with open(log_files[0]) as f:
            lines = f.readlines()
            log_entry = json.loads(lines[-1].strip())
            assert log_entry["correlation_id"] == test_id

        clear_correlation_id()

    def test_sensitive_data_censoring(self, logger, temp_log_dir):
        """Test sensitive data is censored"""
        logger.info(
            "sensitive_test",
            password="secret123",
            api_key="sk-1234567890",
            normal_field="visible",
        )

        # Flush handlers
        for handler in logging.getLogger().handlers:
            handler.flush()

        # Read log file
        log_files = list(temp_log_dir.glob("app_*.log"))
        with open(log_files[0]) as f:
            lines = f.readlines()
            log_entry = json.loads(lines[-1].strip())

            assert log_entry["password"] == "[REDACTED]"
            assert log_entry["api_key"] == "[REDACTED]"
            assert log_entry["normal_field"] == "visible"

    def test_error_logging_with_exception(self, logger, temp_log_dir):
        """Test error logging with exception info"""
        try:
            raise ValueError("Test error")
        except ValueError as e:
            log_error(logger, e, context={"operation": "test"})

        # Flush handlers
        for handler in logging.getLogger().handlers:
            handler.flush()

        # Read error log file
        error_files = list(temp_log_dir.glob("errors_*.log"))
        assert len(error_files) > 0

        with open(error_files[0]) as f:
            lines = f.readlines()
            log_entry = json.loads(lines[-1].strip())

            assert log_entry["event"] == "error_occurred"
            assert log_entry["error_type"] == "ValueError"
            assert "Test error" in log_entry["error_message"]
            assert log_entry["context"]["operation"] == "test"


class TestConvenienceFunctions:
    """Test convenience logging functions"""

    def test_log_request(self, logger):
        """Test HTTP request logging"""
        log_request(logger, "GET", "/api/users", user_id="user123")

    def test_log_response(self, logger):
        """Test HTTP response logging"""
        log_response(logger, "GET", "/api/users", 200, 45.5)

    def test_log_database_query(self, logger):
        """Test database query logging"""
        log_database_query(
            logger,
            "SELECT",
            "users",
            12.3,
            rows_affected=5,
        )

    def test_log_cache_operation(self, logger):
        """Test cache operation logging"""
        log_cache_operation(logger, "get", "user:123", hit=True)
        log_cache_operation(logger, "set", "user:456", hit=False)

    def test_log_job_event(self, logger):
        """Test job event logging"""
        log_job_event(
            logger,
            event_type="started",
            job_id="job-123",
            job_type="calculation",
            priority=1,
        )

    def test_log_security_event(self, logger):
        """Test security event logging"""
        log_security_event(
            logger,
            "login_attempt",
            user_id="user123",
            ip_address="192.168.1.1",
            success=True,
        )

    def test_log_performance_metric(self, logger):
        """Test performance metric logging"""
        log_performance_metric(
            logger,
            "response_time",
            45.5,
            unit="ms",
            endpoint="/api/users",
        )


class TestEnvironmentConfiguration:
    """Test environment-specific configuration"""

    def test_dev_environment_setup(self, temp_log_dir):
        """Test development environment setup"""
        setup_structured_logging(
            env="dev",
            log_level="DEBUG",
            log_dir=temp_log_dir,
            json_format=False,
        )

        logger = get_logger("test")
        logger.debug("dev_test")

    def test_prod_environment_setup(self, temp_log_dir):
        """Test production environment setup"""
        setup_structured_logging(
            env="prod",
            log_level="WARNING",
            log_dir=temp_log_dir,
            json_format=True,
        )

        logger = get_logger("test")
        logger.warning("prod_test")

    def test_staging_environment_setup(self, temp_log_dir):
        """Test staging environment setup"""
        setup_structured_logging(
            env="staging",
            log_level="INFO",
            log_dir=temp_log_dir,
            json_format=True,
        )

        logger = get_logger("test")
        logger.info("staging_test")


class TestLogAggregationPreparation:
    """Test log aggregation preparation"""

    def test_json_format_for_aggregation(self, temp_log_dir):
        """Test JSON format suitable for log aggregation"""
        setup_structured_logging(
            env="prod",
            log_level="INFO",
            log_dir=temp_log_dir,
            json_format=True,
        )

        logger = get_logger("test")
        logger.info(
            "aggregation_test",
            service="api",
            endpoint="/users",
            method="GET",
            status=200,
            duration_ms=45.5,
        )

        # Flush handlers
        for handler in logging.getLogger().handlers:
            handler.flush()

        # Verify JSON structure
        log_files = list(temp_log_dir.glob("app_*.log"))
        with open(log_files[0]) as f:
            lines = f.readlines()
            log_entry = json.loads(lines[-1].strip())

            # Verify required fields for aggregation
            assert "timestamp" in log_entry
            assert "environment" in log_entry
            assert "app" in log_entry
            assert "version" in log_entry
            assert "level" in log_entry
            assert "event" in log_entry

    def test_structured_fields(self, temp_log_dir):
        """Test structured fields are preserved"""
        setup_structured_logging(
            env="prod",
            log_level="INFO",
            log_dir=temp_log_dir,
            json_format=True,
        )

        logger = get_logger("test")

        # Log with nested structure
        logger.info(
            "structured_test",
            user={"id": "123", "name": "Test User"},
            metrics={"count": 42, "rate": 0.95},
        )

        # Flush handlers
        for handler in logging.getLogger().handlers:
            handler.flush()

        # Verify structure is preserved
        log_files = list(temp_log_dir.glob("app_*.log"))
        with open(log_files[0]) as f:
            lines = f.readlines()
            log_entry = json.loads(lines[-1].strip())

            assert log_entry["user"]["id"] == "123"
            assert log_entry["metrics"]["count"] == 42


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
