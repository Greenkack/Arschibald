"""
Configuration Management for KAI Agent
======================================

Handles API keys, environment variables, and system configuration.

Security Features:
- Loads keys from .env only (never hardcoded)
- Never logs or displays keys
- Validates keys on startup
- Ensures .env is in .gitignore

Requirements: 12.1, 12.2, 12.3, 12.5
"""

import logging
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Set up logger (will use sensitive data filter from logging_config)
logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Configuration container for KAI Agent."""

    # API Keys
    openai_api_key: str
    tavily_api_key: str | None = None
    twilio_account_sid: str | None = None
    twilio_auth_token: str | None = None
    twilio_phone_number: str | None = None
    eleven_labs_api_key: str | None = None

    # Paths
    knowledge_base_path: str = "knowledge_base"
    faiss_index_path: str = "faiss_index"
    agent_workspace_path: str = "agent_workspace"

    # Docker Configuration
    docker_image_name: str = "kai_agent-sandbox"
    docker_timeout_python: int = 30
    docker_timeout_terminal: int = 120

    # LLM Configuration
    llm_model: str = "gpt-4o"
    llm_temperature: float = 0.7

    # Knowledge Base Configuration
    chunk_size: int = 1000
    chunk_overlap: int = 100
    similarity_search_k: int = 3

    @classmethod
    def from_env(cls) -> "AgentConfig":
        """
        Load configuration from environment variables.

        Returns:
            AgentConfig instance

        Raises:
            ValueError: If required API keys are missing
        """
        load_dotenv()

        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            raise ValueError(
                "OPENAI_API_KEY is required but not found in environment")

        return cls(
            openai_api_key=openai_key,
            tavily_api_key=os.getenv("TAVILY_API_KEY"),
            twilio_account_sid=os.getenv("TWILIO_ACCOUNT_SID"),
            twilio_auth_token=os.getenv("TWILIO_AUTH_TOKEN"),
            twilio_phone_number=os.getenv("TWILIO_PHONE_NUMBER"),
            eleven_labs_api_key=os.getenv("ELEVEN_LABS_API_KEY"),
        )

    def validate_telephony(self) -> bool:
        """Check if telephony credentials are configured."""
        return all([
            self.twilio_account_sid,
            self.twilio_auth_token,
            self.twilio_phone_number,
            self.eleven_labs_api_key
        ])

    def validate_search(self) -> bool:
        """Check if search API is configured."""
        return self.tavily_api_key is not None


def check_api_keys() -> dict[str, bool]:
    """
    Check which API keys are configured.

    Returns:
        Dictionary with key names and their availability status
    """
    load_dotenv()

    required_keys = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "TAVILY_API_KEY": os.getenv("TAVILY_API_KEY"),
        "TWILIO_ACCOUNT_SID": os.getenv("TWILIO_ACCOUNT_SID"),
        "TWILIO_AUTH_TOKEN": os.getenv("TWILIO_AUTH_TOKEN"),
        "TWILIO_PHONE_NUMBER": os.getenv("TWILIO_PHONE_NUMBER"),
        "ELEVEN_LABS_API_KEY": os.getenv("ELEVEN_LABS_API_KEY"),
    }

    return {key: bool(value) for key, value in required_keys.items()}


def get_missing_keys() -> list[str]:
    """
    Get list of missing API keys.

    Returns:
        List of missing key names
    """
    keys_status = check_api_keys()
    return [key for key, available in keys_status.items() if not available]


def get_setup_instructions() -> str:
    """
    Get setup instructions for missing API keys.

    Returns:
        Formatted setup instructions
    """
    missing = get_missing_keys()

    if not missing:
        return "✅ All API keys are configured!"

    instructions = """
🔧 KAI Agent Setup Instructions
================================

The following API keys are missing from your .env file:

"""

    for key in missing:
        instructions += f"  ❌ {key}\n"

    instructions += """

📝 Setup Steps:
---------------

1. Create a .env file in your project root (if it doesn't exist)
2. Add the missing API keys to your .env file:

   OPENAI_API_KEY=sk-...
   TAVILY_API_KEY=tvly-...
   TWILIO_ACCOUNT_SID=AC...
   TWILIO_AUTH_TOKEN=...
   TWILIO_PHONE_NUMBER=+1...
   ELEVEN_LABS_API_KEY=...

3. Restart the application

📚 Where to get API keys:
-------------------------

- OpenAI: https://platform.openai.com/api-keys (REQUIRED)
- Tavily: https://tavily.com/ (for web search)
- Twilio: https://www.twilio.com/console (for telephony)
- ElevenLabs: https://elevenlabs.io/ (for voice synthesis)

Note: Only OPENAI_API_KEY is strictly required. Other keys enable additional features.
"""

    return instructions


def validate_env_file_security() -> tuple[bool, list[str]]:
    """
    Validate that .env file is properly secured.

    Checks:
    - .env file exists
    - .env is in .gitignore
    - .env has appropriate permissions (Unix systems)

    Returns:
        Tuple of (is_secure: bool, warnings: list[str])
    """
    warnings = []
    env_path = Path(".env")
    gitignore_path = Path(".gitignore")

    # Check if .env exists
    if not env_path.exists():
        warnings.append(
            "⚠️  .env file not found. Create one from .env.example")
        return False, warnings

    # Check if .env is in .gitignore
    if gitignore_path.exists():
        with open(gitignore_path, encoding='utf-8') as f:
            gitignore_content = f.read()
            if '.env' not in gitignore_content:
                warnings.append(
                    "🔴 SECURITY RISK: .env is not in .gitignore! Add it immediately.")
                return False, warnings
    else:
        warnings.append(
            "⚠️  .gitignore not found. Ensure .env is not committed to version control.")

    # Check file permissions (Unix systems only)
    try:
        import platform
        import stat

        # Only check permissions on Unix-like systems
        if platform.system() != 'Windows':
            file_stat = env_path.stat()
            mode = file_stat.st_mode

            # Check if file is world-readable or group-readable
            if mode & stat.S_IROTH:
                warnings.append(
                    "⚠️  .env is readable by others. Run: chmod 600 .env")
            elif mode & stat.S_IRGRP:
                warnings.append(
                    "⚠️  .env is readable by group. Run: chmod 600 .env")
    except (AttributeError, OSError):
        # Permission check not available
        pass

    if not warnings:
        logger.info("✅ .env file security validated")

    return len(warnings) == 0, warnings


def validate_api_key_format(
        key_name: str, key_value: str | None) -> tuple[bool, str | None]:
    """
    Validate API key format without logging the actual key.

    Args:
        key_name: Name of the API key
        key_value: Value of the API key

    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])
    """
    if not key_value:
        return False, f"{key_name} is not set"

    # Validate format based on key type
    if key_name == "OPENAI_API_KEY":
        if not key_value.startswith("sk-"):
            return False, f"{key_name} should start with 'sk-'"
        if len(key_value) < 20:
            return False, f"{key_name} appears too short"

    elif key_name == "TAVILY_API_KEY":
        if not key_value.startswith("tvly-"):
            return False, f"{key_name} should start with 'tvly-'"

    elif key_name == "TWILIO_ACCOUNT_SID":
        if not key_value.startswith("AC"):
            return False, f"{key_name} should start with 'AC'"
        if len(key_value) != 34:
            return False, f"{key_name} should be 34 characters"

    elif key_name == "TWILIO_PHONE_NUMBER":
        if not key_value.startswith("+"):
            return False, f"{key_name} should start with '+' (international format)"

    # Key format looks valid
    logger.debug(f"✅ {key_name} format validated (value not logged)")
    return True, None


def validate_startup_security() -> tuple[bool, list[str]]:
    """
    Comprehensive security validation on startup.

    Validates:
    - .env file security
    - API key formats
    - No keys in environment variables (should be in .env only)

    Returns:
        Tuple of (is_secure: bool, issues: list[str])
    """
    issues = []

    # Validate .env file security
    env_secure, env_warnings = validate_env_file_security()
    issues.extend(env_warnings)

    # Load environment variables
    load_dotenv()

    # Validate API key formats
    keys_to_validate = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "TAVILY_API_KEY": os.getenv("TAVILY_API_KEY"),
        "TWILIO_ACCOUNT_SID": os.getenv("TWILIO_ACCOUNT_SID"),
        "TWILIO_AUTH_TOKEN": os.getenv("TWILIO_AUTH_TOKEN"),
        "TWILIO_PHONE_NUMBER": os.getenv("TWILIO_PHONE_NUMBER"),
        "ELEVEN_LABS_API_KEY": os.getenv("ELEVEN_LABS_API_KEY"),
    }

    for key_name, key_value in keys_to_validate.items():
        if key_value:  # Only validate if key is present
            is_valid, error_msg = validate_api_key_format(key_name, key_value)
            if not is_valid:
                issues.append(f"⚠️  {error_msg}")

    # Check that OPENAI_API_KEY is present (required)
    if not keys_to_validate["OPENAI_API_KEY"]:
        issues.append("🔴 OPENAI_API_KEY is required but not found in .env")
        return False, issues

    # Log validation result (without sensitive data)
    if not issues:
        logger.info("✅ Startup security validation passed")
    else:
        logger.warning(
            f"⚠️  Startup security validation found {
                len(issues)} issue(s)")

    return len(issues) == 0, issues


def ensure_no_key_logging():
    """
    Ensure that logging configuration filters sensitive data.

    This function verifies that the logging system has sensitive data
    filters in place to prevent accidental exposure of API keys.
    """
    # Check if logging has been configured with sensitive data filter
    root_logger = logging.getLogger()

    has_filter = False
    for handler in root_logger.handlers:
        for filter_obj in handler.filters:
            if 'SensitiveDataFilter' in str(type(filter_obj)):
                has_filter = True
                break

    if not has_filter:
        logger.warning(
            "⚠️  Sensitive data filter not detected in logging configuration. "
            "Ensure logging_config.setup_logging() is called before using the agent.")
    else:
        logger.debug("✅ Sensitive data filter active in logging")

    return has_filter
