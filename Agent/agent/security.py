"""
Security Module for KAI Agent
==============================

Provides input validation, path sanitization, and security checks
to prevent common vulnerabilities like path traversal, command injection,
and unauthorized file access.
"""

import logging
import os
import re
from pathlib import Path

logger = logging.getLogger(__name__)


class SecurityError(Exception):
    """Base exception for security violations."""


class PathTraversalError(SecurityError):
    """Raised when path traversal attempt is detected."""


class CommandInjectionError(SecurityError):
    """Raised when command injection attempt is detected."""


class InputValidationError(SecurityError):
    """Raised when input validation fails."""


# Dangerous command patterns that could be used for injection
DANGEROUS_COMMAND_PATTERNS = [
    r'\brm\s+-rf',  # rm -rf command (anywhere)
    r';\s*rm\s+',  # rm after semicolon
    r'\|\s*rm\s+',  # rm after pipe
    r'&&\s*rm\s+',  # rm after &&
    r'`.*`',  # Command substitution with backticks
    r'\$\(.*\)',  # Command substitution with $()
    r'>\s*/dev/',  # Writing to device files
    r'<\s*/dev/',  # Reading from device files
    r'/etc/passwd',  # Accessing password file
    r'/etc/shadow',  # Accessing shadow file
    r'\bsudo\s+',  # Sudo commands
    r'\bsu\s+',  # Switch user
    r'chmod\s+777',  # Dangerous permissions
    r'curl.*\|\s*bash',  # Piping curl to bash
    r'wget.*\|\s*bash',  # Piping wget to bash
]

# Compile patterns for efficiency
DANGEROUS_PATTERNS_COMPILED = [
    re.compile(
        pattern,
        re.IGNORECASE) for pattern in DANGEROUS_COMMAND_PATTERNS]


def validate_path(path: str, base_dir: str) -> tuple[bool, str, str | None]:
    """
    Validate that a path is safe and within the allowed base directory.

    Prevents:
    - Path traversal attacks (../)
    - Absolute paths outside base directory
    - Symbolic link attacks
    - Access to system directories

    Args:
        path: The path to validate
        base_dir: The base directory that path must be within

    Returns:
        Tuple of (is_valid: bool, resolved_path: str, error_message: Optional[str])

    Example:
        >>> validate_path("../etc/passwd", "/app/workspace")
        (False, "", "Path traversal detected")

        >>> validate_path("myfile.txt", "/app/workspace")
        (True, "/app/workspace/myfile.txt", None)
    """
    try:
        # Normalize the base directory
        base_path = Path(base_dir).resolve()

        # Join and resolve the full path
        full_path = (base_path / path).resolve()

        # Check if the resolved path is within the base directory
        try:
            full_path.relative_to(base_path)
        except ValueError:
            error_msg = f"Path traversal detected: '{path}' attempts to access outside workspace"
            logger.warning(f"Security violation: {error_msg}")
            return False, "", error_msg

        # Additional checks for dangerous paths
        path_str = str(full_path).lower()
        dangerous_dirs = [
            '/etc/',
            '/sys/',
            '/proc/',
            '/dev/',
            '/root/',
            '/boot/']

        for dangerous_dir in dangerous_dirs:
            if dangerous_dir in path_str:
                error_msg = f"Access to system directory denied: {dangerous_dir}"
                logger.warning(f"Security violation: {error_msg}")
                return False, "", error_msg

        return True, str(full_path), None

    except Exception as e:
        error_msg = f"Path validation error: {str(e)}"
        logger.error(error_msg)
        return False, "", error_msg


def sanitize_file_path(path: str, base_dir: str) -> str:
    """
    Sanitize and validate a file path, raising exception if invalid.

    Args:
        path: The path to sanitize
        base_dir: The base directory that path must be within

    Returns:
        The validated absolute path

    Raises:
        PathTraversalError: If path validation fails
    """
    is_valid, resolved_path, error_msg = validate_path(path, base_dir)

    if not is_valid:
        raise PathTraversalError(error_msg or "Invalid path")

    return resolved_path


def validate_command(command: str) -> tuple[bool, str | None]:
    """
    Validate that a command doesn't contain dangerous patterns.

    Checks for:
    - Command injection attempts
    - Dangerous system commands
    - Privilege escalation attempts
    - File system manipulation

    Args:
        command: The command string to validate

    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])

    Example:
        >>> validate_command("echo hello")
        (True, None)

        >>> validate_command("rm -rf / && echo done")
        (False, "Dangerous command pattern detected")
    """
    if not command or not command.strip():
        return False, "Empty command not allowed"

    # Check against dangerous patterns
    for pattern in DANGEROUS_PATTERNS_COMPILED:
        if pattern.search(command):
            error_msg = f"Dangerous command pattern detected: {
                pattern.pattern}"
            logger.warning(
                f"Security violation: {error_msg} in command: {command[:100]}")
            return False, error_msg

    # Check for null bytes (command injection technique)
    if '\x00' in command:
        error_msg = "Null byte detected in command"
        logger.warning(f"Security violation: {error_msg}")
        return False, error_msg

    return True, None


def sanitize_command(command: str) -> str:
    """
    Sanitize and validate a command, raising exception if invalid.

    Args:
        command: The command to sanitize

    Returns:
        The validated command string

    Raises:
        CommandInjectionError: If command validation fails
    """
    is_valid, error_msg = validate_command(command)

    if not is_valid:
        raise CommandInjectionError(error_msg or "Invalid command")

    return command.strip()


def validate_user_input(
        user_input: str, max_length: int = 10000) -> tuple[bool, str | None]:
    """
    Validate user input for basic safety checks.

    Args:
        user_input: The user input to validate
        max_length: Maximum allowed length

    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])
    """
    if not user_input:
        return False, "Empty input not allowed"

    if len(user_input) > max_length:
        return False, f"Input too long (max {max_length} characters)"

    # Check for null bytes
    if '\x00' in user_input:
        return False, "Null byte detected in input"

    return True, None


def sanitize_user_input(user_input: str, max_length: int = 10000) -> str:
    """
    Sanitize and validate user input, raising exception if invalid.

    Args:
        user_input: The input to sanitize
        max_length: Maximum allowed length

    Returns:
        The validated input string

    Raises:
        InputValidationError: If input validation fails
    """
    is_valid, error_msg = validate_user_input(user_input, max_length)

    if not is_valid:
        raise InputValidationError(error_msg or "Invalid input")

    return user_input.strip()


def validate_filename(filename: str) -> tuple[bool, str | None]:
    """
    Validate that a filename is safe.

    Args:
        filename: The filename to validate

    Returns:
        Tuple of (is_valid: bool, error_message: Optional[str])
    """
    if not filename:
        return False, "Empty filename not allowed"

    # Check for path separators (should be just a filename)
    if '/' in filename or '\\' in filename:
        return False, "Path separators not allowed in filename"

    # Check for hidden files (starting with .)
    if filename.startswith('.'):
        return False, "Hidden files not allowed"

    # Check for dangerous characters
    dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\x00']
    for char in dangerous_chars:
        if char in filename:
            return False, f"Dangerous character '{char}' not allowed in filename"

    # Check length
    if len(filename) > 255:
        return False, "Filename too long (max 255 characters)"

    return True, None


def sanitize_filename(filename: str) -> str:
    """
    Sanitize and validate a filename, raising exception if invalid.

    Args:
        filename: The filename to sanitize

    Returns:
        The validated filename

    Raises:
        InputValidationError: If filename validation fails
    """
    is_valid, error_msg = validate_filename(filename)

    if not is_valid:
        raise InputValidationError(error_msg or "Invalid filename")

    return filename


def mask_sensitive_data(text: str, patterns: list | None = None) -> str:
    """
    Mask sensitive data in text (API keys, tokens, etc.).

    Args:
        text: The text to mask
        patterns: Optional list of regex patterns to mask

    Returns:
        Text with sensitive data masked
    """
    if not text:
        return text

    # Default patterns for common sensitive data
    default_patterns = [
        (r'sk-[a-zA-Z0-9]{48}', 'sk-***'),  # OpenAI API keys
        (r'tvly-[a-zA-Z0-9]+', 'tvly-***'),  # Tavily API keys
        (r'AC[a-z0-9]{32}', 'AC***'),  # Twilio Account SID
        (r'[a-z0-9]{32}', '***'),  # Generic tokens (32 chars)
        (r'Bearer\s+[a-zA-Z0-9\-._~+/]+=*', 'Bearer ***'),  # Bearer tokens
        (r'password["\']?\s*[:=]\s*["\']?[^"\'\s]+',
         'password=***'),  # Passwords
    ]

    masked_text = text

    for pattern, replacement in default_patterns:
        masked_text = re.sub(
            pattern,
            replacement,
            masked_text,
            flags=re.IGNORECASE)

    # Apply custom patterns if provided
    if patterns:
        for pattern in patterns:
            masked_text = re.sub(pattern, '***', masked_text)

    return masked_text


# Convenience functions for common operations

def safe_read_file(path: str, base_dir: str) -> str:
    """
    Safely read a file with path validation.

    Args:
        path: Path to file (relative to base_dir)
        base_dir: Base directory

    Returns:
        File contents

    Raises:
        PathTraversalError: If path is invalid
        FileNotFoundError: If file doesn't exist
    """
    validated_path = sanitize_file_path(path, base_dir)

    with open(validated_path, encoding='utf-8') as f:
        return f.read()


def safe_write_file(path: str, content: str, base_dir: str) -> None:
    """
    Safely write a file with path validation.

    Args:
        path: Path to file (relative to base_dir)
        content: Content to write
        base_dir: Base directory

    Raises:
        PathTraversalError: If path is invalid
    """
    validated_path = sanitize_file_path(path, base_dir)

    # Create parent directories if needed
    os.makedirs(os.path.dirname(validated_path), exist_ok=True)

    with open(validated_path, 'w', encoding='utf-8') as f:
        f.write(content)


def safe_list_directory(path: str, base_dir: str) -> list:
    """
    Safely list directory contents with path validation.

    Args:
        path: Path to directory (relative to base_dir)
        base_dir: Base directory

    Returns:
        List of filenames

    Raises:
        PathTraversalError: If path is invalid
        FileNotFoundError: If directory doesn't exist
    """
    validated_path = sanitize_file_path(path, base_dir)

    if not os.path.exists(validated_path):
        raise FileNotFoundError(f"Directory not found: {path}")

    return os.listdir(validated_path)


# Test functions
def test_security_functions():
    """Test security validation functions."""
    print("Testing security functions...\n")

    # Test path validation
    print("Test 1: Path validation")
    print(f"Valid path: {validate_path('myfile.txt', '/app/workspace')}")
    print(
        f"Path traversal: {
            validate_path(
                '../../../etc/passwd',
                '/app/workspace')}")
    print(f"Absolute path: {validate_path('/etc/passwd', '/app/workspace')}")
    print()

    # Test command validation
    print("Test 2: Command validation")
    print(f"Safe command: {validate_command('echo hello')}")
    print(f"Dangerous command: {validate_command('rm -rf / && echo done')}")
    print(f"Command injection: {validate_command('echo $(cat /etc/passwd)')}")
    print()

    # Test filename validation
    print("Test 3: Filename validation")
    print(f"Valid filename: {validate_filename('myfile.txt')}")
    print(f"Path in filename: {validate_filename('../myfile.txt')}")
    print(f"Hidden file: {validate_filename('.hidden')}")
    print()

    # Test sensitive data masking
    print("Test 4: Sensitive data masking")
    text = "API Key: sk-1234567890abcdefghijklmnopqrstuvwxyz1234567890 and password=secret123"
    print(f"Original: {text}")
    print(f"Masked: {mask_sensitive_data(text)}")
    print()

    print("Tests complete!")


if __name__ == "__main__":
    test_security_functions()
