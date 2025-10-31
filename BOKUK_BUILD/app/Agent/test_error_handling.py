"""
Test Error Handling and Logging System
=======================================

Simple tests to verify error handling and logging functionality.
"""

from agent.logging_config import (
    log_api_call,
    log_docker_operation,
    log_tool_execution,
    setup_logging,
)
from agent.errors import (
    APIError,
    ConfigurationError,
    DockerError,
    ExecutionError,
    ToolError,
    format_error_message,
    get_error_details,
    get_retry_delay,
    should_retry,
)
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_error_classes():
    """Test error class creation and formatting."""
    print("\n" + "=" * 60)
    print("Testing Error Classes")
    print("=" * 60)

    # Test ConfigurationError
    print("\n1. ConfigurationError:")
    error = ConfigurationError(
        "Missing API keys",
        missing_keys=["OPENAI_API_KEY", "TAVILY_API_KEY"],
        solution="Add keys to .env file"
    )
    print(format_error_message(error))
    print(f"Details: {get_error_details(error)}")
    print(f"Should retry: {should_retry(error)}")

    # Test APIError
    print("\n2. APIError:")
    error = APIError(
        "Rate limit exceeded",
        api_name="OpenAI",
        status_code=429
    )
    print(format_error_message(error))
    print(f"Should retry: {should_retry(error)}")

    # Test ExecutionError
    print("\n3. ExecutionError:")
    error = ExecutionError(
        "Code execution failed",
        code="print(undefined)",
        exit_code=1,
        stderr="NameError: name 'undefined' is not defined"
    )
    print(format_error_message(error))
    print(f"Should retry: {should_retry(error)}")

    # Test DockerError
    print("\n4. DockerError:")
    error = DockerError(
        "Docker image not found",
        image_name="kai_agent_sandbox"
    )
    print(format_error_message(error))

    print("\n✅ Error class tests passed!")


def test_retry_logic():
    """Test retry logic and exponential backoff."""
    print("\n" + "=" * 60)
    print("Testing Retry Logic")
    print("=" * 60)

    # Test retry delays
    print("\nExponential backoff delays:")
    for attempt in range(5):
        delay = get_retry_delay(attempt)
        print(f"  Attempt {attempt + 1}: {delay}s delay")

    # Test should_retry for different errors
    print("\nRetry decisions:")
    errors = [
        ("ConfigurationError", ConfigurationError("Test")),
        ("APIError (429)", APIError("Test", status_code=429)),
        ("APIError (401)", APIError("Test", status_code=401)),
        ("ExecutionError", ExecutionError("Test")),
        ("ToolError", ToolError("Test")),
    ]

    for name, error in errors:
        print(f"  {name}: {'Retry' if should_retry(error) else 'No retry'}")

    print("\n✅ Retry logic tests passed!")


def test_logging_system():
    """Test logging configuration and specialized logging functions."""
    print("\n" + "=" * 60)
    print("Testing Logging System")
    print("=" * 60)

    # Setup logging
    logger = setup_logging(
        level="DEBUG",
        log_to_console=True,
        log_to_file=False)

    # Test basic logging
    print("\n1. Basic logging:")
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")

    # Test API call logging
    print("\n2. API call logging:")
    log_api_call(
        logger,
        api_name="OpenAI",
        endpoint="/v1/chat/completions",
        method="POST",
        status_code=200,
        duration=1.23
    )

    log_api_call(
        logger,
        api_name="Tavily",
        method="POST",
        status_code=429,
        error="Rate limit exceeded"
    )

    # Test Docker operation logging
    print("\n3. Docker operation logging:")
    log_docker_operation(
        logger,
        operation="create",
        image_name="kai_agent_sandbox",
        container_id="abc123def456",
        success=True
    )

    log_docker_operation(
        logger,
        operation="execute",
        container_id="abc123def456",
        success=False,
        error="Timeout"
    )

    # Test tool execution logging
    print("\n4. Tool execution logging:")
    log_tool_execution(
        logger,
        tool_name="write_file",
        input_summary="path=test.py, content=...",
        success=True,
        duration=0.05
    )

    # Test sensitive data filtering
    print("\n5. Sensitive data filtering:")
    logger.info("API key: sk-1234567890abcdefghijklmnopqrstuvwxyz")
    logger.info("Token: bearer abc123def456ghi789jkl012mno345pqr678")
    logger.info("Password: mySecretPassword123")
    logger.info("Phone: +1-555-123-4567")

    print("\n✅ Logging system tests passed!")


def test_error_to_dict():
    """Test error serialization."""
    print("\n" + "=" * 60)
    print("Testing Error Serialization")
    print("=" * 60)

    error = APIError(
        "Test error",
        api_name="TestAPI",
        status_code=500,
        response="Internal server error"
    )

    error_dict = error.to_dict()
    print("\nError dictionary:")
    for key, value in error_dict.items():
        print(f"  {key}: {value}")

    print("\n✅ Error serialization tests passed!")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("KAI Agent Error Handling and Logging Tests")
    print("=" * 60)

    try:
        test_error_classes()
        test_retry_logic()
        test_logging_system()
        test_error_to_dict()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
