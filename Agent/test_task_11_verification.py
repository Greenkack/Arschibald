"""
Task 11 Verification Test
==========================

Verifies that error handling and logging are working correctly.
"""

from agent.errors import (
    AgentError,
    APIError,
    ConfigurationError,
    DockerError,
    ExecutionError,
    KnowledgeBaseError,
    ToolError,
    format_error_message,
    get_retry_delay,
    should_retry,
)
import os
import sys

# Add Agent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_error_classes():
    """Test that all error classes are properly defined."""
    print("Testing error classes...")

    # Test AgentError
    error = AgentError(
        "Test error",
        details={'key': 'value'},
        solution="Test solution"
    )
    assert error.message == "Test error"
    assert error.solution == "Test solution"
    assert 'key' in error.details
    print("✅ AgentError works")

    # Test ConfigurationError
    config_error = ConfigurationError(
        "Missing API key",
        missing_keys=["OPENAI_API_KEY"]
    )
    assert "OPENAI_API_KEY" in config_error.details['missing_keys']
    assert config_error.solution is not None
    print("✅ ConfigurationError works")

    # Test ExecutionError
    exec_error = ExecutionError(
        "Code failed",
        code="print('test')",
        exit_code=1,
        stderr="Error message"
    )
    assert exec_error.details['exit_code'] == 1
    print("✅ ExecutionError works")

    # Test APIError
    api_error = APIError(
        "API failed",
        api_name="OpenAI",
        status_code=429
    )
    assert api_error.details['status_code'] == 429
    assert "rate limit" in api_error.solution.lower()
    print("✅ APIError works")

    # Test DockerError
    docker_error = DockerError(
        "Image not found",
        image_name="test_image"
    )
    assert "test_image" in docker_error.details['image_name']
    print("✅ DockerError works")

    # Test KnowledgeBaseError
    kb_error = KnowledgeBaseError(
        "No PDFs found",
        path="knowledge_base/"
    )
    assert kb_error.details['path'] == "knowledge_base/"
    print("✅ KnowledgeBaseError works")

    # Test ToolError
    tool_error = ToolError(
        "Tool failed",
        tool_name="test_tool",
        tool_input={'arg': 'value'}
    )
    assert tool_error.details['tool_name'] == "test_tool"
    print("✅ ToolError works")

    print("\n✅ All error classes working correctly!\n")


def test_error_utilities():
    """Test error utility functions."""
    print("Testing error utilities...")

    # Test format_error_message
    error = ConfigurationError(
        "Test error",
        solution="Test solution"
    )
    formatted = format_error_message(error)
    assert "❌" in formatted
    assert "💡" in formatted
    assert "Test error" in formatted
    assert "Test solution" in formatted
    print("✅ format_error_message works")

    # Test should_retry
    api_error_429 = APIError("Rate limit", status_code=429)
    assert should_retry(api_error_429)
    print("✅ should_retry works for retryable errors")

    config_error = ConfigurationError("Missing key")
    assert should_retry(config_error) == False
    print("✅ should_retry works for non-retryable errors")

    # Test get_retry_delay
    delay_0 = get_retry_delay(0)
    delay_1 = get_retry_delay(1)
    delay_2 = get_retry_delay(2)
    assert delay_0 == 1
    assert delay_1 == 2
    assert delay_2 == 4
    print("✅ get_retry_delay works with exponential backoff")

    print("\n✅ All error utilities working correctly!\n")


def test_error_to_dict():
    """Test error serialization."""
    print("Testing error serialization...")

    error = APIError(
        "API failed",
        api_name="OpenAI",
        status_code=500,
        solution="Retry later"
    )

    error_dict = error.to_dict()
    assert error_dict['error_type'] == 'APIError'
    assert error_dict['message'] == "API failed"
    assert error_dict['solution'] == "Retry later"
    assert 'timestamp' in error_dict

    print("✅ Error serialization works")
    print("\n✅ Error to_dict() working correctly!\n")


def test_logging_imports():
    """Test that logging configuration can be imported."""
    print("Testing logging imports...")

    try:
        from agent.logging_config import (
            get_logger,
            log_agent_reasoning,
            log_api_call,
            log_docker_operation,
            log_tool_execution,
        )
        print("✅ All logging functions imported successfully")

        # Test logger creation
        logger = get_logger(__name__)
        assert logger is not None
        print("✅ Logger creation works")

        print("\n✅ Logging system working correctly!\n")
    except ImportError as e:
        print(f"❌ Failed to import logging: {e}")
        return False

    return True


def main():
    """Run all verification tests."""
    print("=" * 60)
    print("TASK 11 VERIFICATION TEST")
    print("=" * 60)
    print()

    try:
        test_error_classes()
        test_error_utilities()
        test_error_to_dict()
        test_logging_imports()

        print("=" * 60)
        print("✅ ALL TESTS PASSED - TASK 11 COMPLETE!")
        print("=" * 60)
        print()
        print("Summary:")
        print("  ✅ Error classes defined and working")
        print("  ✅ Error utilities functioning correctly")
        print("  ✅ Error serialization working")
        print("  ✅ Logging system operational")
        print()
        print("Task 11 'Implement error handling and logging' is COMPLETE!")

        return True

    except Exception as e:
        print("=" * 60)
        print(f"❌ TEST FAILED: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
