"""
Configuration Validation Script
================================

Validates API keys and configuration on startup.
Ensures secure configuration and provides helpful error messages.
"""

from Agent.config import (
    check_api_keys,
    get_missing_keys,
    validate_env_file_security,
    validate_startup_security,
)
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def validate_env_file() -> tuple[bool, str]:
    """
    Validate that .env file exists and is properly configured.

    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    # Use the new security validation function
    is_secure, warnings = validate_env_file_security()

    if not is_secure:
        message = "\n❌ .env file security issues detected:\n\n"
        for warning in warnings:
            message += f"{warning}\n"

        env_example_path = Path(".env.example")
        if not Path(".env").exists() and env_example_path.exists():
            message += """
To set up your configuration:
1. Copy the example file: cp .env.example .env
2. Edit .env and add your API keys
3. Run this script again to validate
"""

        return False, message

    return True, "✅ .env file found and properly configured"


def validate_api_keys() -> tuple[bool, str]:
    """
    Validate API keys are present and have correct format.

    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    load_dotenv()

    # Use the new comprehensive validation function
    is_valid, issues = validate_startup_security()

    if not is_valid:
        message = "\n❌ API key validation failed:\n\n"
        for issue in issues:
            message += f"{issue}\n"

        message += """
Get your API keys from:
- OpenAI: https://platform.openai.com/api-keys (REQUIRED)
- Tavily: https://tavily.com/ (optional, for web search)
- Twilio: https://www.twilio.com/console (optional, for telephony)
- ElevenLabs: https://elevenlabs.io/ (optional, for voice synthesis)

Add them to your .env file and run this script again.
"""
        return False, message

    # Check which keys are configured
    keys_status = check_api_keys()
    missing_keys = get_missing_keys()

    # Check optional keys
    optional_missing = [k for k in missing_keys if k != "OPENAI_API_KEY"]

    if optional_missing:
        message = "✅ Required API keys configured\n\n"
        message += "ℹ️  Optional keys not configured:\n"
        for key in optional_missing:
            message += f"   - {key}\n"
        message += "\nThese keys enable additional features but are not required.\n"
        return True, message

    return True, "✅ All API keys configured and validated!"


def validate_docker() -> tuple[bool, str]:
    """
    Validate Docker is installed and running.

    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    try:
        import docker
        client = docker.from_env()
        client.ping()
        return True, "✅ Docker is installed and running"
    except ImportError:
        return False, """
❌ Docker Python library not installed!

Install it with:
pip install docker

"""
    except Exception as e:
        return False, f"""
❌ Docker is not running or not accessible!

Error: {str(e)}

Please ensure Docker is installed and running:
- Windows/Mac: Start Docker Desktop
- Linux: sudo systemctl start docker

"""


def validate_docker_image() -> tuple[bool, str]:
    """
    Validate Docker sandbox image exists.

    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    try:
        import docker
        client = docker.from_env()

        try:
            client.images.get("kai_agent_sandbox")
            return True, "✅ Docker sandbox image found"
        except docker.errors.ImageNotFound:
            return False, """
⚠️  Docker sandbox image not found!

Build the image with:
cd Agent/sandbox
docker build -t kai_agent_sandbox .

Or from project root:
docker build -t kai_agent_sandbox -f Agent/sandbox/Dockerfile Agent/sandbox

"""
    except Exception as e:
        return False, f"⚠️  Could not check Docker image: {str(e)}"


def validate_permissions() -> tuple[bool, str]:
    """
    Validate file permissions are secure.

    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    import platform

    env_path = Path(".env")

    if not env_path.exists():
        return True, "ℹ️  No .env file to check permissions"

    # Only check permissions on Unix-like systems
    if platform.system() == 'Windows':
        return True, "✅ .env file exists (Windows - permissions not checked)"

    # Check if file is readable by others (security risk)
    try:
        import stat
        stat_info = env_path.stat()
        mode = stat_info.st_mode

        # Check if file is world-readable (on Unix systems)
        if mode & stat.S_IROTH:
            return False, """
⚠️  WARNING: .env file is readable by others!

Secure your .env file:
chmod 600 .env

This prevents other users from reading your API keys.
"""

        return True, "✅ .env file permissions are secure"
    except Exception as e:
        return True, f"ℹ️  Could not check permissions: {str(e)}"


def run_validation(verbose: bool = True) -> bool:
    """
    Run all validation checks.

    Args:
        verbose: Whether to print detailed output

    Returns:
        True if all critical checks pass, False otherwise
    """
    if verbose:
        print("=" * 70)
        print("KAI Agent Configuration Validation")
        print("=" * 70)
        print()

    all_passed = True
    critical_failed = False

    # Run all checks
    checks = [
        ("Environment File", validate_env_file, True),
        ("API Keys", validate_api_keys, True),
        ("Docker Installation", validate_docker, True),
        ("Docker Image", validate_docker_image, False),
        ("File Permissions", validate_permissions, False),
    ]

    for check_name, check_func, is_critical in checks:
        if verbose:
            print(f"Checking {check_name}...")

        try:
            passed, message = check_func()

            if verbose:
                print(message)
                print()

            if not passed:
                all_passed = False
                if is_critical:
                    critical_failed = True
        except Exception as e:
            if verbose:
                print(f"❌ Error during {check_name} check: {str(e)}")
                print()
            all_passed = False
            if is_critical:
                critical_failed = True

    # Summary
    if verbose:
        print("=" * 70)
        if critical_failed:
            print("❌ VALIDATION FAILED - Critical issues found")
            print("Please fix the issues above before running the agent.")
        elif not all_passed:
            print("⚠️  VALIDATION PASSED WITH WARNINGS")
            print("Agent can run, but some features may be limited.")
        else:
            print("✅ VALIDATION PASSED - All checks successful!")
            print("Agent is ready to run.")
        print("=" * 70)

    return not critical_failed


def main():
    """Main entry point for validation script."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate KAI Agent configuration and security"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only show errors, no verbose output"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Attempt to fix common issues automatically"
    )

    args = parser.parse_args()

    # Run validation
    passed = run_validation(verbose=not args.quiet)

    # Exit with appropriate code
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
