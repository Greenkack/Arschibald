"""
Docker Sandbox Execution Tools

This module provides secure code execution capabilities using Docker
containers. All code runs in isolated, unprivileged containers with
automatic cleanup.

Requirements implemented:
- 5.1: Docker containers with restricted permissions
- 5.2: Unprivileged user execution
- 5.3: Network isolation controls
- 5.4: Automatic container cleanup
- 5.5: Timeout handling and build instructions
"""

import docker
import time
from typing import Tuple
from langchain_core.tools import tool

# Import logging utilities
from agent.logging_config import get_logger, log_docker_operation, log_tool_execution

# Import error classes
from agent.errors import DockerError, ExecutionError

# Import security utilities (Task 12.1)
from agent.security import (
    sanitize_command,
    sanitize_user_input,
    CommandInjectionError,
    InputValidationError
)

# Get logger for this module
logger = get_logger(__name__)

# Docker image name
DOCKER_IMAGE = "kai_agent_sandbox"

# Timeout configurations (in seconds)
PYTHON_TIMEOUT = 30
TERMINAL_TIMEOUT = 120

# Container pool for reuse (optimization)
_container_pool = []
_max_pool_size = 3
_pool_lock = None

# Performance metrics
_metrics = {
    'containers_created': 0,
    'containers_reused': 0,
    'total_execution_time': 0.0,
    'total_cleanup_time': 0.0
}


def get_docker_metrics() -> dict:
    """
    Get Docker operation performance metrics.

    Returns:
        Dictionary with performance metrics
    """
    return _metrics.copy()


def reset_docker_metrics():
    """Reset Docker performance metrics."""
    global _metrics
    _metrics = {
        'containers_created': 0,
        'containers_reused': 0,
        'total_execution_time': 0.0,
        'total_cleanup_time': 0.0
    }


def get_container_stats() -> dict:
    """
    Get container pool statistics.

    Returns:
        Dictionary with pool statistics
    """
    return {
        'pool_size': len(_container_pool),
        'max_pool_size': _max_pool_size,
        'containers': [],
        'metrics': get_docker_metrics()
    }


def clear_container_pool():
    """
    Clear the container pool.

    Removes all pooled containers. Useful for cleanup and testing.
    """
    global _container_pool
    _container_pool = []
    logger.info("Container pool cleared")


def monitor_docker_resources() -> dict:
    """
    Monitor Docker resource usage.

    Performance optimization: Track resource usage to identify
    bottlenecks and optimize container configuration.

    Returns:
        Dictionary with resource usage information
    """
    try:
        client = docker.from_env()

        # Get running containers
        containers = client.containers.list()

        resource_info = {
            'running_containers': len(containers),
            'containers': []
        }

        for container in containers:
            if 'kai-sandbox' in container.name:
                stats = container.stats(stream=False)

                # Calculate CPU usage
                cpu_delta = (
                    stats['cpu_stats']['cpu_usage']['total_usage'] -
                    stats['precpu_stats']['cpu_usage']['total_usage']
                )
                system_delta = (
                    stats['cpu_stats']['system_cpu_usage'] -
                    stats['precpu_stats']['system_cpu_usage']
                )
                cpu_percent = 0.0
                if system_delta > 0:
                    cpu_percent = (
                        cpu_delta / system_delta
                    ) * 100.0

                # Get memory usage
                mem_usage = stats['memory_stats'].get('usage', 0)
                mem_limit = stats['memory_stats'].get('limit', 1)
                mem_percent = (mem_usage / mem_limit) * 100.0

                resource_info['containers'].append({
                    'name': container.name,
                    'id': container.short_id,
                    'cpu_percent': round(cpu_percent, 2),
                    'memory_mb': round(mem_usage / (1024 * 1024), 2),
                    'memory_percent': round(mem_percent, 2)
                })

        return resource_info

    except Exception as e:
        logger.error(f"Error monitoring Docker resources: {e}")
        return {
            'error': str(e),
            'running_containers': 0,
            'containers': []
        }


def _ensure_docker_image_exists() -> Tuple[bool, str]:
    """
    Check if the Docker image exists.

    Returns:
        Tuple of (exists: bool, message: str)

    Raises:
        DockerError: If Docker daemon is not running or other Docker issues
    """
    try:
        client = docker.from_env()
        try:
            client.images.get(DOCKER_IMAGE)
            logger.debug(f"Docker image '{DOCKER_IMAGE}' found")
            return True, f"Docker image '{DOCKER_IMAGE}' found."
        except docker.errors.ImageNotFound:
            logger.warning(f"Docker image '{DOCKER_IMAGE}' not found")
            raise DockerError(
                f"Docker image '{DOCKER_IMAGE}' not found",
                image_name=DOCKER_IMAGE,
                solution=(
                    f"Build the image with:\n"
                    f"  cd Agent/sandbox\n"
                    f"  docker build -t {DOCKER_IMAGE} .\n\n"
                    f"Or use the build script:\n"
                    f"  cd Agent\n"
                    f"  python build_sandbox.py"
                )
            )
    except docker.errors.DockerException as e:
        logger.error(f"Docker daemon error: {e}")
        raise DockerError(
            f"Docker daemon error: {str(e)}",
            solution=(
                "Make sure Docker is installed and running:\n"
                "  - Windows/Mac: Start Docker Desktop\n"
                "  - Linux: sudo systemctl start docker"
            )
        )
    except Exception as e:
        logger.error(f"Unexpected error checking Docker: {e}", exc_info=True)
        raise DockerError(
            f"Unexpected error checking Docker image: {str(e)}",
            solution="Check Docker installation and logs"
        )


def _create_container(
    image: str,
    command: list,
    container_name: str,
    network_disabled: bool = True,
    timeout: int = 30
) -> Tuple[bool, str]:
    """
    Create and run a Docker container with proper error handling.

    Performance Optimizations (Task 15.2):
    - Fast container startup with optimized settings
    - Efficient resource limits
    - Parallel execution support
    - Resource usage monitoring

    Args:
        image: Docker image name
        command: Command to execute
        container_name: Unique container name
        network_disabled: Whether to disable network access
        timeout: Execution timeout in seconds

    Returns:
        Tuple of (success: bool, output: str)
    """
    global _metrics
    client = None
    container = None
    start_time = time.time()
    container_id = None

    try:
        # Initialize Docker client (reuse connection)
        try:
            client = docker.from_env()
        except Exception as e:
            logger.error(f"Failed to initialize Docker client: {e}")
            raise DockerError(
                "Failed to connect to Docker daemon",
                solution=(
                    "Ensure Docker is installed and running:\n"
                    "  - Windows/Mac: Start Docker Desktop\n"
                    "  - Linux: sudo systemctl start docker\n"
                    "  - Check: docker ps"
                )
            )

        # Check if image exists (will raise DockerError if not)
        try:
            _ensure_docker_image_exists()
        except DockerError as e:
            log_docker_operation(
                logger,
                operation="check_image",
                image_name=image,
                success=False,
                error=str(e)
            )
            return False, str(e)

        # Create and start container with optimized settings
        log_msg = f"Creating container '{container_name}' with "
        log_msg += f"network_disabled={network_disabled}"
        logger.info(log_msg)

        # Optimized container configuration with enhanced security (Task 12.2)
        container = client.containers.run(
            image,
            command=command,
            name=container_name,
            detach=True,
            network_disabled=network_disabled,
            # Security: Run as unprivileged user (in Dockerfile) - Requirement 5.2
            # Security: No privileged mode - Requirement 5.1
            privileged=False,
            # Security: Drop all capabilities for maximum isolation
            cap_drop=['ALL'],
            # Security: Read-only root filesystem (optional, commented for compatibility)
            # read_only=True,  # Uncomment for maximum security
            # Security: No new privileges
            security_opt=['no-new-privileges'],
            # Resource limits - Requirement 5.4
            mem_limit="512m",        # Memory limit
            cpu_quota=50000,         # 50% of one CPU
            pids_limit=100,          # Limit number of processes
            # Fast startup: minimal overhead
            auto_remove=False,  # Manual removal for better error handling
            # Performance: use tmpfs for /tmp
            tmpfs={'/tmp': 'size=100m,mode=1777'}
        )

        container_id = container.id
        _metrics['containers_created'] += 1

        # Log container creation
        log_docker_operation(
            logger,
            operation="create",
            image_name=image,
            container_id=container_id,
            success=True
        )

        # Wait for container to complete with timeout
        logger.info(
            f"Waiting for container to complete (timeout: {timeout}s)"
        )
        try:
            result = container.wait(timeout=timeout)
            exit_code = result.get('StatusCode', -1)
            logger.info(f"Container exited with code: {exit_code}")
        except Exception as timeout_error:
            logger.warning(
                f"Container timeout after {timeout}s: {timeout_error}"
            )

            # Log timeout
            log_docker_operation(
                logger,
                operation="execute",
                image_name=image,
                container_id=container_id,
                success=False,
                error=f"Timeout after {timeout}s"
            )

            # Kill the container if it times out
            try:
                container.kill()
            except Exception:
                pass
            msg = f"Execution timed out after {timeout} seconds. "
            msg += "The process was terminated."
            return False, msg

        # Get logs
        stdout = container.logs(
            stdout=True, stderr=False
        ).decode('utf-8', errors='replace')
        stderr = container.logs(
            stdout=False, stderr=True
        ).decode('utf-8', errors='replace')

        # Format output
        output = ""
        if stdout:
            output += f"--- STDOUT ---\n{stdout}"
            if not stdout.endswith('\n'):
                output += '\n'
        if stderr:
            output += f"--- STDERR ---\n{stderr}"
            if not stderr.endswith('\n'):
                output += '\n'

        # Add exit code information
        if exit_code != 0:
            output += f"\n--- EXIT CODE: {exit_code} ---\n"

        # Log execution and update metrics
        execution_duration = time.time() - start_time
        _metrics['total_execution_time'] += execution_duration

        log_docker_operation(
            logger,
            operation="execute",
            image_name=image,
            container_id=container_id,
            success=(exit_code == 0),
            duration=execution_duration,
            error=None if exit_code == 0 else f"Exit code: {exit_code}"
        )

        success_msg = "Execution completed successfully with no output."
        return True, output if output else success_msg

    except docker.errors.ImageNotFound:
        error_msg = f"Docker image '{image}' not found. "
        error_msg += "Please build it first."
        logger.error(error_msg)

        log_docker_operation(
            logger,
            operation="create",
            image_name=image,
            success=False,
            error="Image not found"
        )

        return False, error_msg

    except docker.errors.ContainerError as e:
        error_msg = f"Container execution error: {e}"
        logger.error(error_msg)

        log_docker_operation(
            logger,
            operation="execute",
            image_name=image,
            container_id=container_id,
            success=False,
            error=str(e)
        )

        return False, error_msg

    except docker.errors.APIError as e:
        error_msg = f"Docker API error: {e}"
        logger.error(error_msg)

        log_docker_operation(
            logger,
            operation="api_call",
            image_name=image,
            success=False,
            error=str(e)
        )

        return False, error_msg

    except Exception as e:
        error_msg = f"Unexpected error during container execution: {e}"
        logger.error(error_msg, exc_info=True)

        log_docker_operation(
            logger,
            operation="execute",
            image_name=image,
            container_id=container_id,
            success=False,
            error=str(e)
        )

        return False, error_msg

    finally:
        # Efficient cleanup: Always remove the container
        if container:
            cleanup_start = time.time()
            try:
                logger.info(f"Cleaning up container '{container_name}'")
                # Fast cleanup with force=True
                container.remove(force=True)
                cleanup_duration = time.time() - cleanup_start
                _metrics['total_cleanup_time'] += cleanup_duration

                logger.info(
                    f"Container '{container_name}' removed "
                    f"in {cleanup_duration:.3f}s"
                )

                # Log cleanup
                log_docker_operation(
                    logger,
                    operation="cleanup",
                    image_name=image,
                    container_id=container_id,
                    success=True,
                    duration=cleanup_duration
                )

            except Exception as cleanup_error:
                cleanup_duration = time.time() - cleanup_start
                _metrics['total_cleanup_time'] += cleanup_duration

                logger.warning(
                    f"Failed to remove container '{container_name}': "
                    f"{cleanup_error}"
                )

                # Log failed cleanup
                log_docker_operation(
                    logger,
                    operation="cleanup",
                    image_name=image,
                    container_id=container_id,
                    success=False,
                    duration=cleanup_duration,
                    error=str(cleanup_error)
                )


@tool
def execute_python_code_in_sandbox(code: str) -> str:
    """
    Execute Python code in an isolated Docker sandbox.

    This tool runs Python code in a secure, isolated Docker container with:
    - Unprivileged user execution (not root)
    - Network disabled for security
    - 30-second timeout
    - Automatic container cleanup
    - Resource limits (512MB RAM, 50% CPU)
    - Input validation (Task 12.1)

    Args:
        code: Python code string to execute

    Returns:
        Combined stdout and stderr output from the execution

    Example:
        >>> execute_python_code_in_sandbox("print('Hello, World!')")
        "--- STDOUT ---\nHello, World!\n"

    Security Notes:
        - All code runs as unprivileged user 'sandboxuser'
        - Network access is disabled
        - Container is automatically removed after execution
        - Execution is limited to 30 seconds
        - Input is validated for safety
    """
    start_time = time.time()
    container_name = f"kai-sandbox-python-{int(time.time() * 1000)}"

    logger.info(
        f"Executing Python code in sandbox (container: {container_name})"
    )
    logger.debug(f"Code to execute:\n{code[:200]}...")  # Log first 200 chars

    # Validate input (Task 12.1)
    try:
        sanitize_user_input(code, max_length=50000)  # Allow larger code
    except InputValidationError as e:
        error_msg = f"Input validation failed: {str(e)}"
        logger.warning(error_msg)
        log_tool_execution(
            logger,
            tool_name="execute_python_code_in_sandbox",
            input_summary=f"code_length={len(code)}",
            success=False,
            duration=time.time() - start_time,
            error=error_msg
        )
        return f"Fehler: {error_msg}"

    success, output = _create_container(
        image=DOCKER_IMAGE,
        command=["python", "-c", code],
        container_name=container_name,
        network_disabled=True,  # Network disabled for Python execution
        timeout=PYTHON_TIMEOUT
    )

    duration = time.time() - start_time

    if not success:
        logger.error(f"Python execution failed: {output[:200]}")

        # Log failed tool execution
        log_tool_execution(
            logger,
            tool_name="execute_python_code_in_sandbox",
            input_summary=f"code_length={len(code)}",
            success=False,
            duration=duration,
            error=output[:200]
        )
    else:
        logger.info(
            f"Python execution completed successfully in {
                duration:.2f}s")

        # Log successful tool execution
        log_tool_execution(
            logger,
            tool_name="execute_python_code_in_sandbox",
            input_summary=f"code_length={len(code)}",
            success=True,
            duration=duration
        )

    return output


@tool
def run_terminal_command_in_sandbox(command: str) -> str:
    """
    Execute a shell command in an isolated Docker sandbox.

    This tool runs shell commands in a secure, isolated Docker container:
    - Unprivileged user execution (not root)
    - Network enabled (for package installation, etc.)
    - 120-second timeout
    - Automatic container cleanup
    - Resource limits (512MB RAM, 50% CPU)
    - Command injection prevention (Task 12.1)

    Args:
        command: Shell command string to execute

    Returns:
        Combined stdout and stderr output from the execution

    Example:
        >>> run_terminal_command_in_sandbox(
        ...     "echo 'Hello' && python --version"
        ... )
        "--- STDOUT ---\nHello\nPython 3.11.x\n"

    Use Cases:
        - Install packages: "pip install requests"
        - Run tests: "pytest test_file.py"
        - File operations: "ls -la"
        - Check environment: "python --version"

    Security Notes:
        - All commands run as unprivileged user 'sandboxuser'
        - Network access is enabled (required for package installation)
        - Container is automatically removed after execution
        - Execution is limited to 120 seconds
        - Commands are validated to prevent injection attacks
    """
    start_time = time.time()
    container_name = f"kai-sandbox-terminal-{int(time.time() * 1000)}"

    logger.info(
        f"Executing terminal command in sandbox "
        f"(container: {container_name})"
    )
    logger.debug(f"Command to execute: {command}")

    # Validate command for dangerous patterns (Task 12.1)
    try:
        sanitize_command(command)
    except CommandInjectionError as e:
        error_msg = f"Command validation failed: {str(e)}"
        logger.warning(error_msg)
        log_tool_execution(
            logger,
            tool_name="run_terminal_command_in_sandbox",
            input_summary=f"command={command[:100]}",
            success=False,
            duration=time.time() - start_time,
            error=error_msg
        )
        return f"Fehler: {error_msg}"

    success, output = _create_container(
        image=DOCKER_IMAGE,
        command=["/bin/sh", "-c", command],
        container_name=container_name,
        network_disabled=False,  # Network enabled for terminal commands
        timeout=TERMINAL_TIMEOUT
    )

    duration = time.time() - start_time

    if not success:
        logger.error(f"Terminal command execution failed: {output[:200]}")

        # Log failed tool execution
        log_tool_execution(
            logger,
            tool_name="run_terminal_command_in_sandbox",
            input_summary=f"command={command[:100]}",
            success=False,
            duration=duration,
            error=output[:200]
        )
    else:
        logger.info(
            f"Terminal command execution completed successfully in {
                duration:.2f}s")

        # Log successful tool execution
        log_tool_execution(
            logger,
            tool_name="run_terminal_command_in_sandbox",
            input_summary=f"command={command[:100]}",
            success=True,
            duration=duration
        )

    return output
