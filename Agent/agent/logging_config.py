"""
Logging Configuration for KAI Agent
====================================

Centralized logging configuration with multiple handlers and formatters.
Implements secure logging practices (no sensitive data exposure).

Requirements: 11.5
"""

import logging
import logging.handlers
import re
import sys
from datetime import datetime
from pathlib import Path

# Create logs directory if it doesn't exist
LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)


class SensitiveDataFilter(logging.Filter):
    """
    Filter to redact sensitive data from log messages.

    Redacts:
    - API keys
    - Tokens
    - Passwords
    - Phone numbers
    - Email addresses (partially)
    """

    # Patterns for sensitive data
    PATTERNS = [
        # API keys (various formats)
        (re.compile(
            r'(api[_-]?key["\s:=]+)([a-zA-Z0-9_\-]{20,})', re.IGNORECASE), r'\1[REDACTED]'),
        (re.compile(r'(sk-[a-zA-Z0-9]{20,})'), r'[REDACTED_API_KEY]'),
        (re.compile(r'(tvly-[a-zA-Z0-9]{20,})'), r'[REDACTED_API_KEY]'),

        # Tokens
        (re.compile(
            r'(token["\s:=]+)([a-zA-Z0-9_\-]{20,})', re.IGNORECASE), r'\1[REDACTED]'),
        (re.compile(
            r'(bearer\s+)([a-zA-Z0-9_\-\.]{20,})', re.IGNORECASE), r'\1[REDACTED]'),

        # Passwords
        (re.compile(r'(password["\s:=]+)([^\s"]+)',
         re.IGNORECASE), r'\1[REDACTED]'),
        (re.compile(r'(pwd["\s:=]+)([^\s"]+)',
         re.IGNORECASE), r'\1[REDACTED]'),

        # Phone numbers (international format)
        (re.compile(
            r'\+\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}'), r'[REDACTED_PHONE]'),

        # Email addresses (partial redaction)
        (re.compile(
            r'([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'), r'[REDACTED]@\2'),

        # Account SIDs (Twilio)
        (re.compile(r'(AC[a-z0-9]{32})'), r'[REDACTED_SID]'),

        # Auth tokens (Twilio)
        (re.compile(
            r'(auth[_-]?token["\s:=]+)([a-z0-9]{32})', re.IGNORECASE), r'\1[REDACTED]'),
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter log record to redact sensitive data.

        Args:
            record: Log record to filter

        Returns:
            True (always allow record, just modify it)
        """
        # Redact message
        if record.msg:
            message = str(record.msg)
            for pattern, replacement in self.PATTERNS:
                message = pattern.sub(replacement, message)
            record.msg = message

        # Redact args if present
        if record.args:
            try:
                args = list(record.args)
                for i, arg in enumerate(args):
                    if isinstance(arg, str):
                        for pattern, replacement in self.PATTERNS:
                            args[i] = pattern.sub(replacement, arg)
                record.args = tuple(args)
            except (TypeError, AttributeError):
                pass

        return True


class AgentLogFormatter(logging.Formatter):
    """
    Custom formatter for agent logs with color support (for console).
    """

    # Color codes for different log levels
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'

    def __init__(self, use_colors: bool = True, *args, **kwargs):
        """
        Initialize formatter.

        Args:
            use_colors: Whether to use color codes (for console output)
        """
        super().__init__(*args, **kwargs)
        self.use_colors = use_colors

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record with optional colors.

        Args:
            record: Log record to format

        Returns:
            Formatted log string
        """
        # Add color to level name if enabled
        if self.use_colors and record.levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[record.levelname]}{record.levelname}{self.RESET}"
            )

        # Format the record
        return super().format(record)


def setup_logging(
    level: str = "INFO",
    log_to_file: bool = True,
    log_to_console: bool = True,
    log_file_name: str | None = None
) -> logging.Logger:
    """
    Set up comprehensive logging configuration for the agent.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to log to file
        log_to_console: Whether to log to console
        log_file_name: Custom log file name (default: agent_YYYYMMDD.log)

    Returns:
        Configured logger instance
    """
    # Get root logger for agent
    logger = logging.getLogger('agent')
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Add sensitive data filter
    sensitive_filter = SensitiveDataFilter()

    # Console handler (with colors)
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = AgentLogFormatter(
            use_colors=True,
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        console_handler.addFilter(sensitive_filter)
        logger.addHandler(console_handler)

    # File handler (rotating, no colors)
    if log_to_file:
        if log_file_name is None:
            log_file_name = f"agent_{datetime.now().strftime('%Y%m%d')}.log"

        log_file_path = LOGS_DIR / log_file_name

        # Use rotating file handler (max 10MB, keep 5 backups)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file_path,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)  # Log everything to file
        file_formatter = AgentLogFormatter(
            use_colors=False,
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(file_formatter)
        file_handler.addFilter(sensitive_filter)
        logger.addHandler(file_handler)

    # Error file handler (separate file for errors only)
    if log_to_file:
        error_log_path = LOGS_DIR / \
            f"agent_errors_{datetime.now().strftime('%Y%m%d')}.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_path,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_formatter = AgentLogFormatter(
            use_colors=False,
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s\n%(exc_info)s',
            datefmt='%Y-%m-%d %H:%M:%S')
        error_handler.setFormatter(error_formatter)
        error_handler.addFilter(sensitive_filter)
        logger.addHandler(error_handler)

    logger.info(
        f"Logging configured: level={level}, file={log_to_file}, console={log_to_console}")

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(f'agent.{name}')


def log_api_call(
    logger: logging.Logger,
    api_name: str,
    endpoint: str | None = None,
    method: str = "POST",
    status_code: int | None = None,
    duration: float | None = None,
    error: str | None = None
):
    """
    Log API call with standardized format (without sensitive data).

    Args:
        logger: Logger instance
        api_name: Name of the API (e.g., "OpenAI", "Tavily")
        endpoint: API endpoint (optional)
        method: HTTP method
        status_code: Response status code (optional)
        duration: Request duration in seconds (optional)
        error: Error message if failed (optional)
    """
    log_data = {
        'api': api_name,
        'method': method,
    }

    if endpoint:
        log_data['endpoint'] = endpoint
    if status_code:
        log_data['status'] = status_code
    if duration:
        log_data['duration'] = f"{duration:.2f}s"

    if error:
        logger.error(f"API call failed: {log_data} - Error: {error}")
    elif status_code and status_code >= 400:
        logger.warning(f"API call returned error: {log_data}")
    else:
        logger.info(f"API call: {log_data}")


def log_docker_operation(
    logger: logging.Logger,
    operation: str,
    image_name: str | None = None,
    container_id: str | None = None,
    success: bool = True,
    duration: float | None = None,
    error: str | None = None
):
    """
    Log Docker operation with standardized format.

    Args:
        logger: Logger instance
        operation: Operation type (e.g., "create", "execute", "cleanup")
        image_name: Docker image name (optional)
        container_id: Container ID (optional)
        success: Whether operation succeeded
        duration: Operation duration in seconds (optional)
        error: Error message if failed (optional)
    """
    log_data = {
        'operation': operation,
    }

    if image_name:
        log_data['image'] = image_name
    if container_id:
        # Only log first 12 chars of container ID
        log_data['container'] = container_id[:12] if len(
            container_id) > 12 else container_id
    if duration:
        log_data['duration'] = f"{duration:.2f}s"

    if not success:
        logger.error(f"Docker operation failed: {log_data} - Error: {error}")
    else:
        logger.info(f"Docker operation: {log_data}")


def log_tool_execution(
    logger: logging.Logger,
    tool_name: str,
    input_summary: str,
    success: bool = True,
    duration: float | None = None,
    error: str | None = None
):
    """
    Log tool execution with standardized format.

    Args:
        logger: Logger instance
        tool_name: Name of the tool
        input_summary: Brief summary of input (no sensitive data)
        success: Whether execution succeeded
        duration: Execution duration in seconds (optional)
        error: Error message if failed (optional)
    """
    log_data = {
        'tool': tool_name,
        'input': input_summary[:100],  # Limit length
    }

    if duration:
        log_data['duration'] = f"{duration:.2f}s"

    if not success:
        logger.error(f"Tool execution failed: {log_data} - Error: {error}")
    else:
        logger.debug(f"Tool execution: {log_data}")


def log_agent_reasoning(
    logger: logging.Logger,
    step: int,
    thought: str,
    action: str | None = None,
    observation: str | None = None
):
    """
    Log agent reasoning step (ReAct pattern).

    Args:
        logger: Logger instance
        step: Step number
        thought: Agent's thought/reasoning
        action: Action taken (optional)
        observation: Observation from action (optional)
    """
    logger.debug(f"[Step {step}] Thought: {thought[:200]}")
    if action:
        logger.debug(f"[Step {step}] Action: {action[:200]}")
    if observation:
        logger.debug(f"[Step {step}] Observation: {observation[:200]}")


# Initialize default logger
default_logger = setup_logging()
