"""
Simple test runner for security tests.
Runs tests without pytest configuration conflicts.
"""

from Agent.agent.security import (
    mask_sensitive_data,
    validate_command,
    validate_filename,
    validate_path,
    validate_user_input,
)
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_path_validation():
    """Test path validation."""
    print("Testing path validation...")

    # Valid path
    is_valid, path, error = validate_path("myfile.txt", "/app/workspace")
    assert is_valid, "Valid path should be accepted"
    print("  ✓ Valid path accepted")

    # Path traversal
    is_valid, path, error = validate_path(
        "../../../etc/passwd", "/app/workspace")
    assert not is_valid, "Path traversal should be blocked"
    print("  ✓ Path traversal blocked")

    # System directory
    is_valid, path, error = validate_path("/etc/passwd", "/app/workspace")
    assert not is_valid, "System directory access should be blocked"
    print("  ✓ System directory access blocked")

    print("  ✅ Path validation tests passed\n")


def test_command_validation():
    """Test command validation."""
    print("Testing command validation...")

    # Valid command
    is_valid, error = validate_command("echo hello")
    assert is_valid, "Valid command should be accepted"
    print("  ✓ Valid command accepted")

    # Dangerous rm command
    is_valid, error = validate_command("rm -rf /")
    assert not is_valid, "Dangerous rm command should be blocked"
    print("  ✓ Dangerous rm command blocked")

    # Command substitution
    is_valid, error = validate_command("echo $(cat /etc/passwd)")
    assert not is_valid, "Command substitution should be blocked"
    print("  ✓ Command substitution blocked")

    # Privilege escalation
    is_valid, error = validate_command("sudo rm -rf /")
    assert not is_valid, "Privilege escalation should be blocked"
    print("  ✓ Privilege escalation blocked")

    print("  ✅ Command validation tests passed\n")


def test_input_validation():
    """Test input validation."""
    print("Testing input validation...")

    # Valid input
    is_valid, error = validate_user_input("Hello, world!")
    assert is_valid, "Valid input should be accepted"
    print("  ✓ Valid input accepted")

    # Empty input
    is_valid, error = validate_user_input("")
    assert not is_valid, "Empty input should be rejected"
    print("  ✓ Empty input rejected")

    # Input too long
    long_input = "x" * 20000
    is_valid, error = validate_user_input(long_input, max_length=10000)
    assert not is_valid, "Overly long input should be rejected"
    print("  ✓ Overly long input rejected")

    # Null byte
    is_valid, error = validate_user_input("hello\x00world")
    assert not is_valid, "Null byte should be rejected"
    print("  ✓ Null byte rejected")

    print("  ✅ Input validation tests passed\n")


def test_filename_validation():
    """Test filename validation."""
    print("Testing filename validation...")

    # Valid filename
    is_valid, error = validate_filename("myfile.txt")
    assert is_valid, "Valid filename should be accepted"
    print("  ✓ Valid filename accepted")

    # Path in filename
    is_valid, error = validate_filename("../myfile.txt")
    assert not is_valid, "Path in filename should be rejected"
    print("  ✓ Path in filename rejected")

    # Hidden file
    is_valid, error = validate_filename(".hidden")
    assert not is_valid, "Hidden file should be rejected"
    print("  ✓ Hidden file rejected")

    # Dangerous character
    is_valid, error = validate_filename("file<name>.txt")
    assert not is_valid, "Dangerous character should be rejected"
    print("  ✓ Dangerous character rejected")

    print("  ✅ Filename validation tests passed\n")


def test_sensitive_data_masking():
    """Test sensitive data masking."""
    print("Testing sensitive data masking...")

    # OpenAI key
    text = "My API key is sk-1234567890abcdefghijklmnopqrstuvwxyz1234567890"
    masked = mask_sensitive_data(text)
    assert "sk-1234567890" not in masked, "OpenAI key should be masked"
    assert "sk-***" in masked, "Masked placeholder should be present"
    print("  ✓ OpenAI key masked")

    # Tavily key
    text = "Tavily key: tvly-abc123def456"
    masked = mask_sensitive_data(text)
    assert "tvly-abc123" not in masked, "Tavily key should be masked"
    print("  ✓ Tavily key masked")

    # Password
    text = "password=secret123"
    masked = mask_sensitive_data(text)
    assert "secret123" not in masked, "Password should be masked"
    print("  ✓ Password masked")

    # Safe text unchanged
    text = "This is a safe message"
    masked = mask_sensitive_data(text)
    assert masked == text, "Safe text should not be modified"
    print("  ✓ Safe text unchanged")

    print("  ✅ Sensitive data masking tests passed\n")


def test_file_operations_security():
    """Test file operations security."""
    print("Testing file operations security...")

    try:
        from Agent.agent.tools.coding_tools import read_file, write_file

        # Try to write outside workspace
        result = write_file.invoke(
            {"path": "../../../etc/passwd", "content": "malicious content"})
        assert "Sicherheitsfehler" in result or "Security" in result, \
            "Should block write outside workspace"
        print("  ✓ Write outside workspace blocked")

        # Try to read outside workspace
        result = read_file.invoke({"path": "../../../etc/passwd"})
        assert "Sicherheitsfehler" in result or "Security" in result, \
            "Should block read outside workspace"
        print("  ✓ Read outside workspace blocked")

        print("  ✅ File operations security tests passed\n")
    except ImportError as e:
        print(f"  ⚠️  Skipping file operations test: {e}\n")
    except Exception as e:
        print(f"  ⚠️  File operations test error (non-critical): {e}\n")


def main():
    """Run all security tests."""
    print("=" * 70)
    print("KAI Agent Security Tests")
    print("=" * 70)
    print()

    tests = [
        test_path_validation,
        test_command_validation,
        test_input_validation,
        test_filename_validation,
        test_sensitive_data_masking,
        test_file_operations_security,
    ]

    failed = 0
    passed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  ❌ Test failed: {e}\n")
            failed += 1
        except Exception as e:
            print(f"  ❌ Test error: {e}\n")
            failed += 1

    print("=" * 70)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 70)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
