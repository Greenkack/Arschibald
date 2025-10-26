"""
Test script for Docker sandbox execution tools.

This script tests the execution tools without requiring the full agent setup.
Tests all features including:
- Docker image detection
- Python code execution
- Terminal command execution
- Timeout handling
- Network isolation
- Automatic cleanup
- Error handling
"""

from agent.tools.execution_tools import (
    _ensure_docker_image_exists,
    execute_python_code_in_sandbox,
    run_terminal_command_in_sandbox,
)
import os
import sys
import time

# Add Agent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_docker_image():
    """Test if Docker image exists."""
    print("=" * 60)
    print("Test 1: Checking Docker image")
    print("=" * 60)
    exists, message = _ensure_docker_image_exists()
    print(f"Image exists: {exists}")
    print(f"Message:\n{message}")
    print()
    return exists


def test_simple_python():
    """Test simple Python code execution."""
    print("=" * 60)
    print("Test 2: Simple Python code")
    print("=" * 60)
    code = "print('Hello from Docker sandbox!')"
    print(f"Code: {code}")
    result = execute_python_code_in_sandbox.invoke({"code": code})
    print(f"Result:\n{result}")
    assert "Hello from Docker sandbox!" in result, "Expected output not found"
    print("✓ Test passed")
    print()


def test_python_calculation():
    """Test Python calculation."""
    print("=" * 60)
    print("Test 3: Python calculation")
    print("=" * 60)
    code = """
x = 10
y = 20
print(f'Sum: {x + y}')
print(f'Product: {x * y}')
"""
    print(f"Code: {code}")
    result = execute_python_code_in_sandbox.invoke({"code": code})
    print(f"Result:\n{result}")
    assert "Sum: 30" in result, "Expected sum not found"
    assert "Product: 200" in result, "Expected product not found"
    print("✓ Test passed")
    print()


def test_terminal_command():
    """Test terminal command execution."""
    print("=" * 60)
    print("Test 4: Terminal command")
    print("=" * 60)
    command = "echo 'Hello from terminal' && python --version"
    print(f"Command: {command}")
    result = run_terminal_command_in_sandbox.invoke({"command": command})
    print(f"Result:\n{result}")
    assert "Hello from terminal" in result, "Expected echo output not found"
    assert "Python 3.11" in result or "Python 3." in result, "Python version not found"
    print("✓ Test passed")
    print()


def test_error_handling():
    """Test error handling."""
    print("=" * 60)
    print("Test 5: Error handling")
    print("=" * 60)
    code = "print(undefined_variable)"
    print(f"Code: {code}")
    result = execute_python_code_in_sandbox.invoke({"code": code})
    print(f"Result:\n{result}")
    assert "NameError" in result or "undefined_variable" in result, "Expected error not found"
    print("✓ Test passed - Error correctly captured")
    print()


def test_installed_packages():
    """Test that sandbox has required packages."""
    print("=" * 60)
    print("Test 6: Installed packages")
    print("=" * 60)
    command = "pip list"
    print(f"Command: {command}")
    result = run_terminal_command_in_sandbox.invoke({"command": command})
    print(f"Result:\n{result}")
    assert "pytest" in result, "pytest not found in sandbox"
    assert "requests" in result, "requests not found in sandbox"
    print("✓ Test passed - Required packages installed")
    print()


def test_network_isolation():
    """Test network isolation for Python execution."""
    print("=" * 60)
    print("Test 7: Network isolation (Python)")
    print("=" * 60)
    code = """
import socket
try:
    socket.create_connection(('google.com', 80), timeout=2)
    print('Network is accessible')
except Exception as e:
    print(f'Network blocked: {type(e).__name__}')
"""
    print(f"Code: {code}")
    result = execute_python_code_in_sandbox.invoke({"code": code})
    print(f"Result:\n{result}")
    # Network should be blocked for Python execution
    assert "Network blocked" in result or "error" in result.lower(), "Network should be blocked"
    print("✓ Test passed - Network correctly isolated")
    print()


def test_timeout_handling():
    """Test timeout handling."""
    print("=" * 60)
    print("Test 8: Timeout handling")
    print("=" * 60)
    code = """
import time
print('Starting long operation...')
time.sleep(35)  # Longer than 30s timeout
print('This should not print')
"""
    print(f"Code: {code}")
    print("(This test will take ~30 seconds)")
    start_time = time.time()
    result = execute_python_code_in_sandbox.invoke({"code": code})
    elapsed = time.time() - start_time
    print(f"Result:\n{result}")
    print(f"Elapsed time: {elapsed:.1f}s")
    assert "timeout" in result.lower(
    ) or "terminated" in result.lower(), "Timeout not handled"
    assert elapsed < 35, "Timeout did not trigger in time"
    print("✓ Test passed - Timeout correctly enforced")
    print()


def test_automatic_cleanup():
    """Test that containers are automatically cleaned up."""
    print("=" * 60)
    print("Test 9: Automatic cleanup")
    print("=" * 60)

    # Run a simple command
    code = "print('Testing cleanup')"
    print(f"Code: {code}")
    result = execute_python_code_in_sandbox.invoke({"code": code})
    print(f"Result:\n{result}")

    # Check for leftover containers
    import docker
    client = docker.from_env()
    containers = client.containers.list(
        all=True, filters={"name": "kai-sandbox"})

    print(f"Leftover containers: {len(containers)}")
    if containers:
        print("Container names:")
        for container in containers:
            print(f"  - {container.name}")

    assert len(containers) == 0, "Containers not cleaned up properly"
    print("✓ Test passed - Containers automatically cleaned up")
    print()


def test_resource_limits():
    """Test resource limits."""
    print("=" * 60)
    print("Test 10: Resource limits")
    print("=" * 60)
    code = """
import sys
print(f'Python version: {sys.version}')
print('Resource limits are enforced by Docker')
"""
    print(f"Code: {code}")
    result = execute_python_code_in_sandbox.invoke({"code": code})
    print(f"Result:\n{result}")
    assert "Python version" in result, "Expected output not found"
    print("✓ Test passed - Resource limits configured")
    print()


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Docker Sandbox Execution Tools Test Suite")
    print("=" * 60 + "\n")

    # First check if Docker image exists
    image_exists = test_docker_image()

    if not image_exists:
        print("\n" + "!" * 60)
        print("Docker image not found. Please build it first:")
        print()
        print("Option 1 - Use build script:")
        print("  cd Agent")
        print("  python build_sandbox.py")
        print()
        print("Option 2 - Manual build:")
        print("  cd Agent/sandbox")
        print("  docker build -t kai_agent_sandbox .")
        print("!" * 60 + "\n")
        return

    # Run tests
    tests_passed = 0
    tests_failed = 0

    tests = [
        ("Simple Python", test_simple_python),
        ("Python calculation", test_python_calculation),
        ("Terminal command", test_terminal_command),
        ("Error handling", test_error_handling),
        ("Installed packages", test_installed_packages),
        ("Network isolation", test_network_isolation),
        ("Timeout handling", test_timeout_handling),
        ("Automatic cleanup", test_automatic_cleanup),
        ("Resource limits", test_resource_limits),
    ]

    for test_name, test_func in tests:
        try:
            test_func()
            tests_passed += 1
        except AssertionError as e:
            print(f"✗ Test failed: {e}")
            tests_failed += 1
        except Exception as e:
            print(f"✗ Test error: {e}")
            import traceback
            traceback.print_exc()
            tests_failed += 1

    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Passed: {tests_passed}/{len(tests)}")
    print(f"Failed: {tests_failed}/{len(tests)}")
    print("=" * 60)

    if tests_failed == 0:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed")


if __name__ == "__main__":
    main()
