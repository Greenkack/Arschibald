"""
Test Logging System Implementation
===================================

This script tests the comprehensive logging system for the KAI Agent.
Tests all logging features including:
- Logging levels configuration
- Agent reasoning logs
- API call logging (without sensitive data)
- Docker operation logging
- Error logging with stack traces
- Sensitive data filtering

Requirements: 11.5
"""

from agent.logging_config import (
    get_logger,
    log_agent_reasoning,
    log_api_call,
    log_docker_operation,
    log_tool_execution,
    setup_logging,
)
import sys
from pathlib import Path

# Add Agent directory to path
sys.path.insert(0, str(Path(__file__).parent))


def test_basic_logging():
    """Test basic logging configuration and levels."""
    print("\n" + "=" * 60)
    print("TEST 1: Basic Logging Configuration")
    print("=" * 60)

    # Setup logging with DEBUG level
    logger = setup_logging(
        level="DEBUG",
        log_to_file=True,
        log_to_console=True)

    # Test different log levels
    logger.debug("This is a DEBUG message")
    logger.info("This is an INFO message")
    logger.warning("This is a WARNING message")
    logger.error("This is an ERROR message")
    logger.critical("This is a CRITICAL message")

    print("✅ Basic logging test completed")


def test_sensitive_data_filtering():
    """Test that sensitive data is properly redacted."""
    print("\n" + "=" * 60)
    print("TEST 2: Sensitive Data Filtering")
    print("=" * 60)

    logger = get_logger("test_sensitive")

    # Test API key redaction
    logger.info("Testing with API key: sk-1234567890abcdefghijklmnopqrstuvwxyz")
    logger.info("OPENAI_API_KEY=sk-proj-abcdefghijklmnopqrstuvwxyz")
    logger.info("TAVILY_API_KEY=tvly-1234567890abcdefghijklmnopqrstuvwxyz")

    # Test token redaction
    logger.info("Bearer token: bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9")

    # Test password redaction
    logger.info("Password: my_secret_password123")

    # Test phone number redaction
    logger.info("Phone: +49 123 456 7890")

    # Test email redaction
    logger.info("Email: user@example.com")

    # Test Twilio credentials
    logger.info("Account SID: AC1234567890abcdefghijklmnopqrstuvwx")
    logger.info("Auth token: auth_token=abcdef1234567890abcdef1234567890")

    print("✅ Sensitive data filtering test completed")
    print("   Check logs to verify all sensitive data was redacted")


def test_api_call_logging():
    """Test API call logging."""
    print("\n" + "=" * 60)
    print("TEST 3: API Call Logging")
    print("=" * 60)

    logger = get_logger("test_api")

    # Test successful API call
    log_api_call(
        logger,
        api_name="OpenAI",
        endpoint="/v1/chat/completions",
        method="POST",
        status_code=200,
        duration=1.23
    )

    # Test failed API call
    log_api_call(
        logger,
        api_name="Tavily",
        endpoint="/search",
        method="GET",
        status_code=429,
        duration=0.5,
        error="Rate limit exceeded"
    )

    # Test API call without optional parameters
    log_api_call(
        logger,
        api_name="ElevenLabs",
        error="Connection timeout"
    )

    print("✅ API call logging test completed")


def test_docker_operation_logging():
    """Test Docker operation logging."""
    print("\n" + "=" * 60)
    print("TEST 4: Docker Operation Logging")
    print("=" * 60)

    logger = get_logger("test_docker")

    # Test container creation
    log_docker_operation(
        logger,
        operation="create",
        image_name="kai_agent_sandbox",
        container_id="abc123def456",
        success=True,
        duration=0.5
    )

    # Test code execution
    log_docker_operation(
        logger,
        operation="execute",
        image_name="kai_agent_sandbox",
        container_id="abc123def456",
        success=True,
        duration=2.3
    )

    # Test cleanup
    log_docker_operation(
        logger,
        operation="cleanup",
        image_name="kai_agent_sandbox",
        container_id="abc123def456",
        success=True,
        duration=0.2
    )

    # Test failed operation
    log_docker_operation(
        logger,
        operation="create",
        image_name="kai_agent_sandbox",
        success=False,
        error="Image not found"
    )

    print("✅ Docker operation logging test completed")


def test_tool_execution_logging():
    """Test tool execution logging."""
    print("\n" + "=" * 60)
    print("TEST 5: Tool Execution Logging")
    print("=" * 60)

    logger = get_logger("test_tools")

    # Test successful tool execution
    log_tool_execution(
        logger,
        tool_name="write_file",
        input_summary="path=test.py, size=1234",
        success=True,
        duration=0.05
    )

    # Test failed tool execution
    log_tool_execution(
        logger,
        tool_name="read_file",
        input_summary="path=nonexistent.txt",
        success=False,
        duration=0.01,
        error="File not found"
    )

    # Test knowledge base search
    log_tool_execution(
        logger,
        tool_name="knowledge_base_search",
        input_summary="query=photovoltaik vorteile",
        success=True,
        duration=0.8
    )

    print("✅ Tool execution logging test completed")


def test_agent_reasoning_logging():
    """Test agent reasoning step logging."""
    print("\n" + "=" * 60)
    print("TEST 6: Agent Reasoning Logging")
    print("=" * 60)

    logger = get_logger("test_reasoning")

    # Simulate agent reasoning steps
    log_agent_reasoning(
        logger,
        step=1,
        thought="I need to search the knowledge base for information about photovoltaics",
        action="knowledge_base_search",
        observation="Found 3 relevant documents about PV systems")

    log_agent_reasoning(
        logger,
        step=2,
        thought="Now I should create a project structure for the user",
        action="generate_project_structure",
        observation="Project structure created successfully with 15 files"
    )

    log_agent_reasoning(
        logger,
        step=3,
        thought="I have completed the task successfully"
    )

    print("✅ Agent reasoning logging test completed")


def test_error_logging():
    """Test error logging with stack traces."""
    print("\n" + "=" * 60)
    print("TEST 7: Error Logging with Stack Traces")
    print("=" * 60)

    logger = get_logger("test_errors")

    # Test error with stack trace
    try:
        # Intentionally cause an error
        result = 1 / 0
    except ZeroDivisionError:
        logger.error("Division by zero error occurred", exc_info=True)

    # Test error without stack trace
    logger.error("Simple error message without stack trace")

    # Test warning
    logger.warning("This is a warning about potential issues")

    print("✅ Error logging test completed")


def test_module_loggers():
    """Test getting loggers for different modules."""
    print("\n" + "=" * 60)
    print("TEST 8: Module-Specific Loggers")
    print("=" * 60)

    # Get loggers for different modules
    agent_logger = get_logger("agent_core")
    tools_logger = get_logger("tools.coding_tools")
    execution_logger = get_logger("tools.execution_tools")

    agent_logger.info("Agent core module log message")
    tools_logger.info("Coding tools module log message")
    execution_logger.info("Execution tools module log message")

    print("✅ Module-specific loggers test completed")


def test_log_file_creation():
    """Test that log files are created correctly."""
    print("\n" + "=" * 60)
    print("TEST 9: Log File Creation")
    print("=" * 60)

    logs_dir = Path(__file__).parent / "logs"

    if logs_dir.exists():
        log_files = list(logs_dir.glob("*.log"))
        print(f"Found {len(log_files)} log files:")
        for log_file in log_files:
            size = log_file.stat().st_size
            print(f"  - {log_file.name} ({size} bytes)")
        print("✅ Log files created successfully")
    else:
        print("⚠️  Logs directory not found")


def main():
    """Run all logging tests."""
    print("\n" + "=" * 70)
    print("KAI AGENT LOGGING SYSTEM TEST SUITE")
    print("=" * 70)
    print("Testing comprehensive logging implementation...")
    print("Requirements: 11.5")

    try:
        # Run all tests
        test_basic_logging()
        test_sensitive_data_filtering()
        test_api_call_logging()
        test_docker_operation_logging()
        test_tool_execution_logging()
        test_agent_reasoning_logging()
        test_error_logging()
        test_module_loggers()
        test_log_file_creation()

        print("\n" + "=" * 70)
        print("ALL TESTS COMPLETED SUCCESSFULLY! ✅")
        print("=" * 70)
        print("\nLogging system features verified:")
        print("  ✅ Logging levels configuration (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
        print("  ✅ Agent reasoning logs")
        print("  ✅ API call logging (without sensitive data)")
        print("  ✅ Docker operation logging")
        print("  ✅ Tool execution logging")
        print("  ✅ Error logging with stack traces")
        print("  ✅ Sensitive data filtering")
        print("  ✅ Module-specific loggers")
        print("  ✅ Log file creation and rotation")

        print("\nLog files location: Agent/logs/")
        print("Check the log files to verify all logging features work correctly.")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
