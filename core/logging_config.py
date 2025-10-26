"""
Logging Configuration Integration
==================================

Integrates structured logging with AppConfig for environment-specific
log level configuration and runtime adjustment.

Requirements: 7.6, 9.5, 12.5
"""

import os

from core.config import AppConfig
from core.logging_system import (
    get_log_level,
    get_logger,
    set_log_level,
    setup_structured_logging,
)

# Environment-specific log level defaults
ENV_LOG_LEVELS = {
    "dev": "DEBUG",
    "stage": "INFO",
    "staging": "INFO",
    "prod": "WARNING",
    "production": "WARNING",
}


def get_log_level_for_env(env: str) -> str:
    """
    Get appropriate log level for environment

    Args:
        env: Environment name (dev/stage/prod)

    Returns:
        Log level string (DEBUG/INFO/WARNING/ERROR/CRITICAL)
    """
    # Check for explicit override
    override = os.getenv("LOG_LEVEL")
    if override:
        return override.upper()

    # Use environment-specific default
    return ENV_LOG_LEVELS.get(env.lower(), "INFO")


def should_use_json_format(env: str) -> bool:
    """
    Determine if JSON format should be used

    Args:
        env: Environment name

    Returns:
        True if JSON format should be used
    """
    # Always use JSON in production/staging for log aggregation
    if env.lower() in {"prod", "production", "stage", "staging"}:
        return True

    # Check for explicit override
    json_override = os.getenv("LOG_JSON", "").lower()
    if json_override in {"true", "1", "yes"}:
        return True
    if json_override in {"false", "0", "no"}:
        return False

    # Default to human-readable in dev
    return False


def init_logging_from_config(config: AppConfig) -> None:
    """
    Initialize logging system from AppConfig

    Args:
        config: Application configuration
    """
    log_level = get_log_level_for_env(config.env)
    json_format = should_use_json_format(config.env)

    setup_structured_logging(
        env=config.env,
        log_level=log_level,
        log_dir=config.log_dir,
        enable_console=True,
        enable_file=not config.is_development() or config.debug,
        json_format=json_format,
    )

    logger = get_logger(__name__)
    logger.info(
        "logging_initialized",
        environment=config.env,
        log_level=log_level,
        json_format=json_format,
        log_dir=str(config.log_dir),
        debug_mode=config.debug,
    )


def adjust_log_level_runtime(new_level: str) -> None:
    """
    Adjust log level at runtime

    Args:
        new_level: New log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)
    """
    old_level = get_log_level()
    set_log_level(new_level)

    logger = get_logger(__name__)
    logger.info(
        "log_level_changed",
        old_level=old_level,
        new_level=new_level,
    )


def get_current_log_level() -> str:
    """
    Get current log level

    Returns:
        Current log level name
    """
    return get_log_level()


class LoggingConfigManager:
    """Manager for logging configuration with runtime adjustment"""

    def __init__(self, config: AppConfig):
        """
        Initialize logging config manager

        Args:
            config: Application configuration
        """
        self.config = config
        self.logger = None

    def initialize(self) -> None:
        """Initialize logging system"""
        init_logging_from_config(self.config)
        self.logger = get_logger(__name__)

    def set_level(self, level: str) -> None:
        """
        Set log level

        Args:
            level: Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)
        """
        adjust_log_level_runtime(level)

    def get_level(self) -> str:
        """
        Get current log level

        Returns:
            Current log level name
        """
        return get_current_log_level()

    def reload_from_config(self) -> None:
        """Reload logging configuration from AppConfig"""
        if self.config.should_reload():
            self.config.reload()

        # Adjust log level if environment changed
        new_level = get_log_level_for_env(self.config.env)
        current_level = self.get_level()

        if new_level != current_level:
            self.set_level(new_level)
            if self.logger:
                self.logger.info(
                    "logging_config_reloaded",
                    new_level=new_level,
                    environment=self.config.env,
                )


# Global logging config manager instance
_logging_manager: LoggingConfigManager | None = None


def get_logging_manager(
        config: AppConfig | None = None) -> LoggingConfigManager:
    """
    Get global logging config manager

    Args:
        config: Optional AppConfig (required on first call)

    Returns:
        LoggingConfigManager instance
    """
    global _logging_manager

    if _logging_manager is None:
        if config is None:
            from core.config import get_config
            config = get_config()

        _logging_manager = LoggingConfigManager(config)
        _logging_manager.initialize()

    return _logging_manager


def reset_logging_manager() -> None:
    """Reset global logging manager (useful for testing)"""
    global _logging_manager
    _logging_manager = None
