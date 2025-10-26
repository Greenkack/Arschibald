"""
Error Classes and Exception Handling for KAI Agent
===================================================

Defines custom exception hierarchy and error handling utilities
for the KAI Agent system.

Requirements: 11.1, 11.2, 11.3, 11.4, 11.5
"""

from datetime import datetime
from typing import Any


class AgentError(Exception):
    """
    Base exception for all agent-related errors.

    All custom exceptions in the KAI Agent system inherit from this class.
    This allows for catching all agent-specific errors with a single except clause.

    Attributes:
        message: Human-readable error message
        details: Additional error details (optional)
        timestamp: When the error occurred
        solution: Suggested solution or troubleshooting steps (optional)
    """

    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
        solution: str | None = None
    ):
        """
        Initialize agent error.

        Args:
            message: Human-readable error message
            details: Additional error details (optional)
            solution: Suggested solution or troubleshooting steps (optional)
        """
        self.message = message
        self.details = details or {}
        self.solution = solution
        self.timestamp = datetime.now()

        # Build full error message
        full_message = f"{message}"
        if details:
            full_message += f"\nDetails: {details}"
        if solution:
            full_message += f"\nSolution: {solution}"

        super().__init__(full_message)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert error to dictionary format.

        Returns:
            Dictionary representation of the error
        """
        return {
            'error_type': self.__class__.__name__,
            'message': self.message,
            'details': self.details,
            'solution': self.solution,
            'timestamp': self.timestamp.isoformat()
        }

    def __str__(self) -> str:
        """String representation of the error."""
        return self.message


class ConfigurationError(AgentError):
    """
    Configuration or setup error.

    Raised when:
    - Required API keys are missing
    - Environment variables are not set
    - Configuration files are invalid
    - System prerequisites are not met

    Examples:
        - Missing OPENAI_API_KEY
        - Invalid .env file format
        - Docker not installed
        - Knowledge base directory not found
    """

    def __init__(
        self,
        message: str,
        missing_keys: list | None = None,
        details: dict[str, Any] | None = None,
        solution: str | None = None
    ):
        """
        Initialize configuration error.

        Args:
            message: Human-readable error message
            missing_keys: List of missing configuration keys (optional)
            details: Additional error details (optional)
            solution: Suggested solution (optional)
        """
        if missing_keys:
            if details is None:
                details = {}
            details['missing_keys'] = missing_keys

        if solution is None and missing_keys:
            solution = (
                "Check your .env file and ensure all required keys are set. "
                f"Missing: {', '.join(missing_keys)}"
            )

        super().__init__(message, details, solution)


class ExecutionError(AgentError):
    """
    Code execution error.

    Raised when:
    - Python code execution fails in sandbox
    - Terminal commands fail
    - Docker container errors occur
    - Timeout errors happen
    - Resource limits are exceeded

    Examples:
        - Syntax error in generated code
        - Docker container failed to start
        - Execution timeout (30s for Python, 120s for terminal)
        - Out of memory in container
    """

    def __init__(
        self,
        message: str,
        code: str | None = None,
        exit_code: int | None = None,
        stdout: str | None = None,
        stderr: str | None = None,
        details: dict[str, Any] | None = None,
        solution: str | None = None
    ):
        """
        Initialize execution error.

        Args:
            message: Human-readable error message
            code: Code that failed to execute (optional)
            exit_code: Process exit code (optional)
            stdout: Standard output (optional)
            stderr: Standard error (optional)
            details: Additional error details (optional)
            solution: Suggested solution (optional)
        """
        if details is None:
            details = {}

        if code:
            details['code'] = code
        if exit_code is not None:
            details['exit_code'] = exit_code
        if stdout:
            details['stdout'] = stdout
        if stderr:
            details['stderr'] = stderr

        if solution is None:
            if stderr and 'SyntaxError' in stderr:
                solution = "Check code for syntax errors. Review Python syntax rules."
            elif stderr and 'ModuleNotFoundError' in stderr:
                solution = "Install required module in sandbox using run_terminal_command_in_sandbox."
            elif exit_code == 124:
                solution = "Execution timed out. Optimize code or increase timeout limit."
            else:
                solution = "Review error output and fix code issues. Check Docker logs if needed."

        super().__init__(message, details, solution)


class APIError(AgentError):
    """
    External API error.

    Raised when:
    - OpenAI API calls fail
    - Tavily search API fails
    - Twilio telephony API fails
    - ElevenLabs voice synthesis fails
    - Rate limits are exceeded
    - Authentication fails
    - Network errors occur

    Examples:
        - OpenAI rate limit exceeded
        - Invalid API key
        - Network timeout
        - API service unavailable
    """

    def __init__(
        self,
        message: str,
        api_name: str | None = None,
        status_code: int | None = None,
        response: str | None = None,
        details: dict[str, Any] | None = None,
        solution: str | None = None
    ):
        """
        Initialize API error.

        Args:
            message: Human-readable error message
            api_name: Name of the API that failed (optional)
            status_code: HTTP status code (optional)
            response: API response (optional)
            details: Additional error details (optional)
            solution: Suggested solution (optional)
        """
        if details is None:
            details = {}

        if api_name:
            details['api_name'] = api_name
        if status_code:
            details['status_code'] = status_code
        if response:
            details['response'] = response

        if solution is None:
            if status_code == 401:
                solution = f"Check {api_name} API key in .env file. Ensure it's valid and not expired."
            elif status_code == 429:
                solution = f"{api_name} rate limit exceeded. Wait and retry, or upgrade API plan."
            elif status_code == 503:
                solution = f"{api_name} service temporarily unavailable. Retry in a few minutes."
            elif status_code and status_code >= 500:
                solution = f"{api_name} server error. Check API status page and retry later."
            else:
                solution = f"Check {api_name} API credentials and network connection."

        super().__init__(message, details, solution)


class DockerError(ExecutionError):
    """
    Docker-specific execution error.

    Raised when:
    - Docker daemon is not running
    - Docker image not found
    - Container creation fails
    - Container execution fails
    - Network isolation issues

    Examples:
        - Docker daemon not running
        - Image 'kai_agent_sandbox' not found
        - Container failed to start
        - Permission denied for Docker socket
    """

    def __init__(
        self,
        message: str,
        image_name: str | None = None,
        container_id: str | None = None,
        details: dict[str, Any] | None = None,
        solution: str | None = None
    ):
        """
        Initialize Docker error.

        Args:
            message: Human-readable error message
            image_name: Docker image name (optional)
            container_id: Container ID (optional)
            details: Additional error details (optional)
            solution: Suggested solution (optional)
        """
        if details is None:
            details = {}

        if image_name:
            details['image_name'] = image_name
        if container_id:
            details['container_id'] = container_id

        if solution is None:
            if 'not found' in message.lower() and image_name:
                solution = (
                    f"Docker image '{image_name}' not found. Build it with:\n"
                    f"cd Agent/sandbox && docker build -t {image_name} ."
                )
            elif 'daemon' in message.lower() or 'connection' in message.lower():
                solution = (
                    "Docker daemon is not running. Start Docker Desktop or Docker service:\n"
                    "- Windows/Mac: Start Docker Desktop\n"
                    "- Linux: sudo systemctl start docker")
            elif 'permission' in message.lower():
                solution = (
                    "Permission denied for Docker. Add user to docker group:\n"
                    "sudo usermod -aG docker $USER\n"
                    "Then log out and back in."
                )
            else:
                solution = "Check Docker installation and ensure Docker daemon is running."

        super().__init__(message, details=details, solution=solution)


class KnowledgeBaseError(AgentError):
    """
    Knowledge base error.

    Raised when:
    - Knowledge base initialization fails
    - FAISS index loading fails
    - PDF loading fails
    - Embedding creation fails
    - Search query fails

    Examples:
        - No PDF files found in knowledge_base/
        - FAISS index corrupted
        - OpenAI embeddings API failed
        - Invalid PDF format
    """

    def __init__(
        self,
        message: str,
        path: str | None = None,
        details: dict[str, Any] | None = None,
        solution: str | None = None
    ):
        """
        Initialize knowledge base error.

        Args:
            message: Human-readable error message
            path: Path to knowledge base or file (optional)
            details: Additional error details (optional)
            solution: Suggested solution (optional)
        """
        if details is None:
            details = {}

        if path:
            details['path'] = path

        if solution is None:
            if 'no pdf' in message.lower():
                solution = (
                    "Add PDF documents to the knowledge_base/ directory. "
                    "The agent will automatically index them on next startup."
                )
            elif 'faiss' in message.lower():
                solution = (
                    "Delete the faiss_index directory and restart to rebuild the index. "
                    "Ensure all PDF files are valid.")
            else:
                solution = "Check knowledge_base/ directory and ensure PDF files are valid."

        super().__init__(message, details, solution)


class ToolError(AgentError):
    """
    Tool execution error.

    Raised when:
    - Tool function fails
    - Invalid tool input
    - Tool not available
    - Tool timeout

    Examples:
        - Invalid file path in write_file
        - Tool not registered
        - Tool execution timeout
    """

    def __init__(
        self,
        message: str,
        tool_name: str | None = None,
        tool_input: dict[str, Any] | None = None,
        details: dict[str, Any] | None = None,
        solution: str | None = None
    ):
        """
        Initialize tool error.

        Args:
            message: Human-readable error message
            tool_name: Name of the tool that failed (optional)
            tool_input: Input provided to the tool (optional)
            details: Additional error details (optional)
            solution: Suggested solution (optional)
        """
        if details is None:
            details = {}

        if tool_name:
            details['tool_name'] = tool_name
        if tool_input:
            details['tool_input'] = tool_input

        if solution is None:
            solution = f"Check {tool_name} tool input and try again. Review tool documentation."

        super().__init__(message, details, solution)


# Error handling utilities

def format_error_message(error: Exception) -> str:
    """
    Format error message for user display.

    Args:
        error: Exception instance

    Returns:
        Formatted error message with solution if available
    """
    if isinstance(error, AgentError):
        msg = f"❌ {error.__class__.__name__}: {error.message}"
        if error.solution:
            msg += f"\n\n💡 Solution:\n{error.solution}"
        return msg
    return f"❌ Unexpected Error: {str(error)}"


def get_error_details(error: Exception) -> dict[str, Any]:
    """
    Extract error details for logging.

    Args:
        error: Exception instance

    Returns:
        Dictionary with error details
    """
    if isinstance(error, AgentError):
        return error.to_dict()
    return {
        'error_type': error.__class__.__name__,
        'message': str(error),
        'timestamp': datetime.now().isoformat()
    }


def should_retry(error: Exception) -> bool:
    """
    Determine if an operation should be retried based on error type.

    Args:
        error: Exception instance

    Returns:
        True if operation should be retried, False otherwise
    """
    # Retry on transient errors
    if isinstance(error, APIError):
        # Retry on rate limits and server errors
        if hasattr(error, 'details'):
            status_code = error.details.get('status_code')
            if status_code in [429, 500, 502, 503, 504]:
                return True

    # Don't retry on configuration or validation errors
    if isinstance(error, (ConfigurationError, ToolError)):
        return False

    # Retry on execution errors (might be transient)
    if isinstance(error, ExecutionError):
        return True

    return False


def get_retry_delay(attempt: int, max_delay: int = 60) -> int:
    """
    Calculate exponential backoff delay for retries.

    Args:
        attempt: Retry attempt number (0-indexed)
        max_delay: Maximum delay in seconds

    Returns:
        Delay in seconds
    """
    delay = min(2 ** attempt, max_delay)
    return delay
