"""
Tests for Logging Configuration Integration
============================================

Tests for integration between structured logging and AppConfig.

Requirements: 7.6, 9.5, 12.5
"""

import os
import tempfile
from pathlib import Path

import pytest

from core.config import AppConfig
from core.logging_config import (
    LoggingConfigManager,
    adjust_log_level_runtime,
    get_current_log_level,
    get_log_level_for_env,
    get_logging_manager,
    init_logging_from_config,
    reset_logging_manager,
    should_use_json_format,
)
from core.logging_system import get_logger


@pytest.fixture
def temp_dirs():
    """Create temporary directories for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        data_dir = Path(tmpdir) / "data"
        log_dir = Path(tmpdir) / "logs"
        data_dir.mkdir()
        log_dir.mkdir()
        yield {"data": data_dir, "log": log_dir}


@pytest.fixture
def test_config(temp_dirs):
    """Create test configuration"""
    os.environ["ENV"] = "dev"
    os.environ["DATA_DIR"] = str(temp_dirs["data"])
    os.environ["LOG_DIR"] = str(temp_dirs["log"])

    config = AppConfig.load()
    yield config

    # Cleanup
    if "LOG_LEVEL" in os.environ:
        del os.environ["LOG_LEVEL"]
    if "LOG_JSON" in os.environ:
        del os.environ["LOG_JSON"]


@pytest.fixture(autouse=True)
def reset_logging():
    """Reset logging manager before each test"""
    reset_logging_manager()
    yield
    reset_logging_manager()


class TestEnvironmentLogLevels:
    """Test environment-specific log levels"""

    def test_dev_log_level(self):
        """Test development environment log level"""
        level = get_log_level_for_env("dev")
        assert level == "DEBUG"

    def test_staging_log_level(self):
        """Test staging environment log level"""
        level = get_log_level_for_env("staging")
        assert level == "INFO"

        level = get_log_level_for_env("stage")
        assert level == "INFO"

    def test_prod_log_level(self):
        """Test production environment log level"""
        level = get_log_level_for_env("prod")
        assert level == "WARNING"

        level = get_log_level_for_env("production")
        assert level == "WARNING"

    def test_log_level_override(self):
        """Test log level override via environment variable"""
        os.environ["LOG_LEVEL"] = "ERROR"

        level = get_log_level_for_env("dev")
        assert level == "ERROR"

        del os.environ["LOG_LEVEL"]

    def test_unknown_environment_default(self):
        """Test unknown environment uses INFO default"""
        level = get_log_level_for_env("unknown")
        assert level == "INFO"


class TestJSONFormatConfiguration:
    """Test JSON format configuration"""

    def test_json_format_in_production(self):
        """Test JSON format is enabled in production"""
        assert should_use_json_format("prod") is True
        assert should_use_json_format("production") is True

    def test_json_format_in_staging(self):
        """Test JSON format is enabled in staging"""
        assert should_use_json_format("staging") is True
        assert should_use_json_format("stage") is True

    def test_json_format_in_dev(self):
        """Test JSON format is disabled in dev by default"""
        assert should_use_json_format("dev") is False

    def test_json_format_override_true(self):
        """Test JSON format override to true"""
        os.environ["LOG_JSON"] = "true"
        assert should_use_json_format("dev") is True
        del os.environ["LOG_JSON"]

    def test_json_format_override_false(self):
        """Test JSON format override to false"""
        os.environ["LOG_JSON"] = "false"
        assert should_use_json_format("prod") is False
        del os.environ["LOG_JSON"]


class TestLoggingInitialization:
    """Test logging initialization from config"""

    def test_init_logging_from_config(self, test_config):
        """Test logging initialization from AppConfig"""
        init_logging_from_config(test_config)

        logger = get_logger("test")
        logger.info("test_message")

        # Verify log file was created
        log_files = list(test_config.log_dir.glob("app_*.log"))
        assert len(log_files) > 0

    def test_init_logging_dev_environment(self, test_config):
        """Test logging initialization in dev environment"""
        test_config.env = "dev"
        init_logging_from_config(test_config)

        # Should use DEBUG level in dev
        current_level = get_current_log_level()
        assert current_level == "DEBUG"

    def test_init_logging_prod_environment(self, temp_dirs):
        """Test logging initialization in prod environment"""
        os.environ["ENV"] = "prod"
        config = AppConfig.load()
        config.log_dir = temp_dirs["log"]

        init_logging_from_config(config)

        # Should use WARNING level in prod
        current_level = get_current_log_level()
        assert current_level == "WARNING"


class TestRuntimeLogLevelAdjustment:
    """Test runtime log level adjustment"""

    def test_adjust_log_level(self, test_config):
        """Test adjusting log level at runtime"""
        init_logging_from_config(test_config)

        # Change to INFO
        adjust_log_level_runtime("INFO")
        assert get_current_log_level() == "INFO"

        # Change to WARNING
        adjust_log_level_runtime("WARNING")
        assert get_current_log_level() == "WARNING"

        # Change to ERROR
        adjust_log_level_runtime("ERROR")
        assert get_current_log_level() == "ERROR"

    def test_adjust_log_level_case_insensitive(self, test_config):
        """Test log level adjustment is case-insensitive"""
        init_logging_from_config(test_config)

        adjust_log_level_runtime("info")
        assert get_current_log_level() == "INFO"


class TestLoggingConfigManager:
    """Test LoggingConfigManager"""

    def test_manager_initialization(self, test_config):
        """Test manager initialization"""
        manager = LoggingConfigManager(test_config)
        manager.initialize()

        assert manager.logger is not None

    def test_manager_set_level(self, test_config):
        """Test setting log level via manager"""
        manager = LoggingConfigManager(test_config)
        manager.initialize()

        manager.set_level("WARNING")
        assert manager.get_level() == "WARNING"

    def test_manager_get_level(self, test_config):
        """Test getting log level via manager"""
        manager = LoggingConfigManager(test_config)
        manager.initialize()

        level = manager.get_level()
        assert level in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}

    def test_manager_reload_from_config(self, test_config):
        """Test reloading configuration"""
        manager = LoggingConfigManager(test_config)
        manager.initialize()

        # Change environment
        test_config.env = "prod"
        manager.reload_from_config()

        # Should adjust to prod log level
        assert manager.get_level() == "WARNING"


class TestGlobalLoggingManager:
    """Test global logging manager"""

    def test_get_logging_manager(self, test_config):
        """Test getting global logging manager"""
        manager = get_logging_manager(test_config)
        assert manager is not None
        assert isinstance(manager, LoggingConfigManager)

    def test_get_logging_manager_singleton(self, test_config):
        """Test logging manager is singleton"""
        manager1 = get_logging_manager(test_config)
        manager2 = get_logging_manager()

        assert manager1 is manager2

    def test_reset_logging_manager(self, test_config):
        """Test resetting logging manager"""
        manager1 = get_logging_manager(test_config)
        reset_logging_manager()
        manager2 = get_logging_manager(test_config)

        assert manager1 is not manager2


class TestLoggingWithConfig:
    """Test logging with configuration"""

    def test_logging_respects_config_level(self, test_config):
        """Test logging respects configured level"""
        test_config.env = "prod"
        init_logging_from_config(test_config)

        logger = get_logger("test")

        # INFO should not be logged in prod (WARNING level)
        logger.info("should_not_appear")

        # WARNING should be logged
        logger.warning("should_appear")

    def test_logging_uses_config_log_dir(self, test_config):
        """Test logging uses configured log directory"""
        init_logging_from_config(test_config)

        logger = get_logger("test")
        logger.info("test_message")

        # Verify log file is in configured directory
        log_files = list(test_config.log_dir.glob("app_*.log"))
        assert len(log_files) > 0
        assert log_files[0].parent == test_config.log_dir

    def test_logging_debug_mode(self, test_config):
        """Test logging in debug mode"""
        test_config.debug = True
        init_logging_from_config(test_config)

        logger = get_logger("test")
        logger.debug("debug_message")

        # Debug messages should be logged
        log_files = list(test_config.log_dir.glob("app_*.log"))
        assert len(log_files) > 0


class TestEnvironmentSpecificBehavior:
    """Test environment-specific logging behavior"""

    def test_dev_environment_behavior(self, temp_dirs):
        """Test development environment logging behavior"""
        os.environ["ENV"] = "dev"
        config = AppConfig.load()
        config.log_dir = temp_dirs["log"]

        init_logging_from_config(config)

        # Dev should use DEBUG level
        assert get_current_log_level() == "DEBUG"

        # Dev should not use JSON format by default
        assert should_use_json_format("dev") is False

    def test_staging_environment_behavior(self, temp_dirs):
        """Test staging environment logging behavior"""
        os.environ["ENV"] = "staging"
        config = AppConfig.load()
        config.log_dir = temp_dirs["log"]

        init_logging_from_config(config)

        # Staging should use INFO level
        assert get_current_log_level() == "INFO"

        # Staging should use JSON format
        assert should_use_json_format("staging") is True

    def test_prod_environment_behavior(self, temp_dirs):
        """Test production environment logging behavior"""
        os.environ["ENV"] = "prod"
        config = AppConfig.load()
        config.log_dir = temp_dirs["log"]

        init_logging_from_config(config)

        # Prod should use WARNING level
        assert get_current_log_level() == "WARNING"

        # Prod should use JSON format
        assert should_use_json_format("prod") is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
