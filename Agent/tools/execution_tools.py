"""
Docker Sandbox Execution Tools

This module provides secure code execution tools using Docker containers.
All code runs in isolated, unprivileged containers with network isolation
and automatic cleanup.
"""

from agent.security import (
    sanitize_command,
    sanitize_user_input,
    CommandInjectionError,
    InputValidationError
)
from agent.logging_config import get_logger, log_docker_operation
import docker
import logging
import time
from langchain.tools import tool

# Import logging utilities
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logger = get_logger(__name__)

# Docker configuration
DOCKER_IMAGE = "kai_agent_sandbox"
PYTHON_TIMEOUT = 30  # seconds
TERMINAL_TIMEOUT = 120  # seconds

# Resource limits
MEMORY_LIMIT = "512m"  # 512 MB
CPU_QUOTA = 50000  # 50% of one core (100000 = 100%)
PIDS_LIMIT = 100  # Maximum number of processes


def _ensure_docker_image_exists() -> tuple[bool, str]:
    """
    Check if Docker image exists, provide build instructions if not.

    Returns:
        tuple: (exists: bool, message: str)
    """
    try:
        client = docker.from_env()
        try:
            client.images.get(DOCKER_IMAGE)
            return True, "Docker image found"
        except docker.errors.ImageNotFound:
            build_instructions = f"""
Docker image '{DOCKER_IMAGE}' not found.

To build the image, run:
cd Agent/sandbox
docker build -t {DOCKER_IMAGE} .

Or from the project root:
docker build -t {DOCKER_IMAGE} -f Agent/sandbox/Dockerfile Agent/sandbox
"""
            return False, build_instructions
    except docker.errors.DockerException as e:
        return False, f"Docker error: {str(e)}. Is Docker running?"


def _run_in_container(
    command: list[str],
    timeout: int,
    network_disabled: bool = True,
    working_dir: str = "/app/workspace"
) -> str:
    """
    Execute command in Docker container with security controls.

    Args:
        command: Command to execute as list
        timeout: Timeout in seconds
        network_disabled: Whether to disable network access
        working_dir: Working directory in container

    Returns:
        Combined stdout and stderr output

    Raises:
        docker.errors.DockerException: If Docker operation fails
    """
    start_time = time.time()
    container_id = None

    # Check if image exists
    exists, message = _ensure_docker_image_exists()
    if not exists:
        logger.error(f"Docker image not found: {DOCKER_IMAGE}")
        log_docker_operation(
            logger,
            operation="check_image",
            image_name=DOCKER_IMAGE,
            success=False,
            error="Image not found"
        )
        return message

    logger.debug(f"Starting container execution: {' '.join(command[:3])}...")

    client = docker.from_env()

    try:
        # Run container with comprehensive security settings
        logger.debug(f"Creating container with image: {DOCKER_IMAGE}")

        # Security configuration
        security_opts = [
            "no-new-privileges",  # Prevent privilege escalation
            "seccomp=unconfined",
            # Allow Python to work (can be restricted further)
        ]

        # Create container with all security features
        container = client.containers.run(
            image=DOCKER_IMAGE,
            command=command,
            detach=True,
            remove=False,  # We'll remove manually after getting logs
            network_disabled=network_disabled,
            working_dir=working_dir,

            # Resource limits
            mem_limit=MEMORY_LIMIT,
            memswap_limit=MEMORY_LIMIT,  # Disable swap
            cpu_quota=CPU_QUOTA,
            pids_limit=PIDS_LIMIT,

            # Security options
            security_opt=security_opts,
            cap_drop=["ALL"],  # Drop all capabilities
            read_only=False,  # Allow writes to workspace

            # User (already set in Dockerfile, but explicit here)
            user="sandboxuser",

            # Prevent container from gaining additional privileges
            privileged=False,
        )

        container_id = container.id
        logger.debug(f"Container created: {container_id[:12]}")

        log_docker_operation(
            logger,
            operation="create",
            image_name=DOCKER_IMAGE,
            container_id=container_id,
            success=True
        )

        # Wait for completion with timeout
        try:
            logger.debug(
                f"Waiting for container execution (timeout: {timeout}s)")
            result = container.wait(timeout=timeout)
            logs = container.logs(stdout=True, stderr=True).decode('utf-8')

            # Check exit code
            exit_code = result.get('StatusCode', -1)
            execution_time = time.time() - start_time

            if exit_code != 0:
                logs += f"\n\n[Exit code: {exit_code}]"
                logger.warning(f"Container exited with code {exit_code}")
                log_docker_operation(
                    logger,
                    operation="execute",
                    image_name=DOCKER_IMAGE,
                    container_id=container_id,
                    success=False,
                    duration=execution_time,
                    error=f"Exit code: {exit_code}"
                )
            else:
                logger.debug(f"Container execution completed successfully")
                log_docker_operation(
                    logger,
                    operation="execute",
                    image_name=DOCKER_IMAGE,
                    container_id=container_id,
                    success=True,
                    duration=execution_time
                )

            return logs

        except Exception as e:
            # Timeout or other error
            execution_time = time.time() - start_time
            logger.error(f"Container execution failed: {e}")
            log_docker_operation(
                logger,
                operation="execute",
                image_name=DOCKER_IMAGE,
                container_id=container_id,
                success=False,
                duration=execution_time,
                error=str(e)
            )

            try:
                logger.debug("Killing container due to error")
                container.kill()
            except Exception as kill_error:
                logger.error(f"Failed to kill container: {kill_error}")

            return f"Execution error: {str(e)}"

        finally:
            # Always cleanup container
            try:
                logger.debug(
                    f"Removing container: {container_id[:12] if container_id else 'unknown'}")
                container.remove(force=True)
                log_docker_operation(
                    logger,
                    operation="cleanup",
                    container_id=container_id,
                    success=True
                )
            except Exception as cleanup_error:
                logger.error(f"Failed to cleanup container: {cleanup_error}")
                log_docker_operation(
                    logger,
                    operation="cleanup",
                    container_id=container_id,
                    success=False,
                    error=str(cleanup_error)
                )

    except docker.errors.DockerException as e:
        execution_time = time.time() - start_time
        logger.error(f"Docker error: {e}", exc_info=True)
        log_docker_operation(
            logger,
            operation="create",
            image_name=DOCKER_IMAGE,
            success=False,
            duration=execution_time,
            error=str(e)
        )
        return f"Docker error: {str(e)}"
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Unexpected error: {e}", exc_info=True)
        log_docker_operation(
            logger,
            operation="execute",
            image_name=DOCKER_IMAGE,
            container_id=container_id,
            success=False,
            duration=execution_time,
            error=str(e)
        )
        return f"Unexpected error: {str(e)}"


@tool
def execute_python_code_in_sandbox(code: str) -> str:
    """
    Execute Python code in an isolated Docker sandbox.

    This tool runs Python code in a secure, isolated Docker container with:
    - Unprivileged user (not root)
    - Network disabled by default
    - 30-second timeout
    - Automatic cleanup after execution
    - Memory and CPU limits
    - Input validation

    Args:
        code: Python code to execute as a string

    Returns:
        Combined stdout and stderr from the execution

    Example:
        code = "print('Hello from sandbox!')"
        result = execute_python_code_in_sandbox(code)

    Security:
        - Runs as unprivileged 'sandboxuser'
        - No network access
        - Resource limits enforced
        - Container automatically removed
        - Input validation for dangerous patterns
    """
    if not code or not code.strip():
        return "Error: No code provided"

    # Validate input length
    try:
        sanitize_user_input(code, max_length=50000)
    except InputValidationError as e:
        logger.warning(f"Code validation failed: {e}")
        return f"Security error: {str(e)}"

    # Check for null bytes
    if '\x00' in code:
        logger.warning("Null byte detected in Python code")
        return "Security error: Null byte detected in code"

    # Create command to execute Python code
    # Use python -c to execute code directly
    command = ["python", "-c", code]

    # Execute in container
    result = _run_in_container(
        command=command,
        timeout=PYTHON_TIMEOUT,
        network_disabled=True
    )

    return result


@tool
def run_terminal_command_in_sandbox(command: str) -> str:
    """
    Execute a terminal command in an isolated Docker sandbox.

    This tool runs shell commands in a secure, isolated Docker container with:
    - Unprivileged user (not root)
    - Network disabled by default
    - 120-second timeout
    - Automatic cleanup after execution
    - Memory and CPU limits
    - Command validation for dangerous patterns

    Args:
        command: Shell command to execute as a string

    Returns:
        Combined stdout and stderr from the execution

    Example:
        command = "pip install requests && python -c 'import requests; print(requests.__version__)'"
        result = run_terminal_command_in_sandbox(command)

    Common use cases:
        - Install packages: "pip install numpy"
        - Run tests: "pytest -v"
        - File operations: "ls -la"
        - Check environment: "python --version"

    Security:
        - Runs as unprivileged 'sandboxuser'
        - No network access by default
        - Resource limits enforced
        - Container automatically removed
        - Command validation for injection attempts
    """
    if not command or not command.strip():
        return "Error: No command provided"

    # Validate command for dangerous patterns
    try:
        sanitized_command = sanitize_command(command)
    except CommandInjectionError as e:
        logger.warning(f"Command validation failed: {e}")
        return f"Security error: {str(e)}"

    # Additional validation
    try:
        sanitize_user_input(command, max_length=10000)
    except InputValidationError as e:
        logger.warning(f"Command input validation failed: {e}")
        return f"Security error: {str(e)}"

    # Use bash -c to execute the command
    cmd_list = ["bash", "-c", sanitized_command]

    # Execute in container
    result = _run_in_container(
        command=cmd_list,
        timeout=TERMINAL_TIMEOUT,
        network_disabled=True
    )

    return result


@tool
def execute_python_code_with_network(code: str) -> str:
    """
    Execute Python code in sandbox WITH network access enabled.

    Use this when the code needs to make HTTP requests or access external resources.
    Same security features as execute_python_code_in_sandbox but with network enabled.

    Args:
        code: Python code to execute as a string

    Returns:
        Combined stdout and stderr from the execution

    Warning:
        Only use this when network access is explicitly required.

    Security:
        - Input validation
        - Resource limits
        - Unprivileged user
        - Automatic cleanup
    """
    if not code or not code.strip():
        return "Error: No code provided"

    # Validate input
    try:
        sanitize_user_input(code, max_length=50000)
    except InputValidationError as e:
        logger.warning(f"Code validation failed: {e}")
        return f"Security error: {str(e)}"

    # Check for null bytes
    if '\x00' in code:
        logger.warning("Null byte detected in Python code")
        return "Security error: Null byte detected in code"

    command = ["python", "-c", code]

    result = _run_in_container(
        command=command,
        timeout=PYTHON_TIMEOUT,
        network_disabled=False  # Network enabled
    )

    return result


def get_execution_tools() -> list:
    """
    Get all execution tools for the agent.

    Returns:
        List of LangChain tools for code execution
    """
    return [
        execute_python_code_in_sandbox,
        run_terminal_command_in_sandbox,
        execute_python_code_with_network,
    ]


# Test function for manual verification
def test_sandbox():
    """Test the sandbox execution tools."""
    print("Testing Docker sandbox execution tools...\n")

    # Test 1: Simple Python code
    print("Test 1: Simple Python code")
    result = execute_python_code_in_sandbox("print('Hello from sandbox!')")
    print(f"Result: {result}\n")

    # Test 2: Python with calculation
    print("Test 2: Python calculation")
    code = """
x = 10
y = 20
print(f"Sum: {x + y}")
print(f"Product: {x * y}")
"""
    result = execute_python_code_in_sandbox(code)
    print(f"Result: {result}\n")

    # Test 3: Terminal command
    print("Test 3: Terminal command")
    result = run_terminal_command_in_sandbox(
        "echo 'Hello from terminal' && python --version")
    print(f"Result: {result}\n")

    # Test 4: Error handling
    print("Test 4: Error handling")
    result = execute_python_code_in_sandbox("print(undefined_variable)")
    print(f"Result: {result}\n")

    print("Tests complete!")


if __name__ == "__main__":
    test_sandbox()
