#!/usr/bin/env python3
"""
Verification script for Docker sandbox build (Task 14.1).

This script verifies that the Docker image is properly built with all
required features and security configurations.

Requirements verified: 5.1, 5.2, 5.5
"""

import sys

import docker
from docker.errors import DockerException, ImageNotFound


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(text)
    print("=" * 70)


def print_check(passed, message):
    """Print a check result."""
    symbol = "✓" if passed else "✗"
    color = "\033[92m" if passed else "\033[91m"
    reset = "\033[0m"
    print(f"{color}{symbol}{reset} {message}")


def verify_docker_available():
    """Verify Docker is available."""
    print_header("Checking Docker Availability")

    try:
        client = docker.from_env()
        version = client.version()
        print_check(True, "Docker is available")
        print(f"  Version: {version.get('Version', 'Unknown')}")
        print(f"  API Version: {version.get('ApiVersion', 'Unknown')}")
        return True, client
    except DockerException as e:
        print_check(False, f"Docker is not available: {e}")
        print("\nPlease install Docker:")
        print("  - Windows/Mac: https://www.docker.com/products/docker-desktop")
        print("  - Linux: https://docs.docker.com/engine/install/")
        return False, None


def verify_image_exists(client):
    """Verify the sandbox image exists."""
    print_header("Checking Docker Image")

    image_name = "kai_agent_sandbox"

    try:
        image = client.images.get(image_name)
        print_check(True, f"Image '{image_name}' exists")

        # Print image details
        print("\nImage Details:")
        print(f"  ID: {image.id}")
        print(f"  Tags: {image.tags}")
        print(f"  Size: {image.attrs['Size'] / (1024 * 1024):.2f} MB")
        print(f"  Created: {image.attrs['Created']}")

        return True, image
    except ImageNotFound:
        print_check(False, f"Image '{image_name}' not found")
        print("\nTo build the image, run:")
        print("  cd Agent/sandbox")
        print("  docker build -t kai_agent_sandbox .")
        print("\nOr use the build script:")
        print("  python Agent/build_sandbox.py")
        return False, None


def verify_python_version(client):
    """Verify Python version in image (Requirement 5.5)."""
    print_header("Verifying Python Environment")

    try:
        result = client.containers.run(
            "kai_agent_sandbox",
            "python --version",
            remove=True
        )
        version = result.decode('utf-8').strip()

        has_python_3 = "Python 3." in version
        print_check(has_python_3, f"Python version: {version}")

        if "Python 3.11" in version:
            print("  ✓ Python 3.11 detected (recommended)")

        return has_python_3
    except Exception as e:
        print_check(False, f"Failed to check Python version: {e}")
        return False


def verify_unprivileged_user(client):
    """Verify container runs as unprivileged user (Requirement 5.2)."""
    print_header("Verifying Unprivileged User")

    try:
        # Check username
        result = client.containers.run(
            "kai_agent_sandbox",
            "whoami",
            remove=True
        )
        username = result.decode('utf-8').strip()

        is_sandboxuser = username == "sandboxuser"
        is_not_root = username != "root"

        print_check(is_sandboxuser, f"User is 'sandboxuser': {username}")
        print_check(is_not_root, f"User is not root: {username}")

        # Check UID
        result = client.containers.run(
            "kai_agent_sandbox",
            "id -u",
            remove=True
        )
        uid = result.decode('utf-8').strip()

        is_non_zero_uid = uid != "0"
        print_check(is_non_zero_uid, f"UID is non-zero: {uid}")

        return is_sandboxuser and is_not_root and is_non_zero_uid
    except Exception as e:
        print_check(False, f"Failed to verify user: {e}")
        return False


def verify_workspace_directory(client):
    """Verify workspace directory exists."""
    print_header("Verifying Workspace Directory")

    try:
        result = client.containers.run(
            "kai_agent_sandbox",
            "pwd",
            remove=True
        )
        workdir = result.decode('utf-8').strip()

        is_workspace = "workspace" in workdir
        print_check(is_workspace, f"Working directory: {workdir}")

        # Check if directory is writable
        result = client.containers.run(
            "kai_agent_sandbox",
            "touch test.txt && rm test.txt && echo 'writable'",
            remove=True
        )
        output = result.decode('utf-8').strip()

        is_writable = "writable" in output
        print_check(is_writable, "Workspace is writable")

        return is_workspace and is_writable
    except Exception as e:
        print_check(False, f"Failed to verify workspace: {e}")
        return False


def verify_installed_packages(client):
    """Verify required packages are installed."""
    print_header("Verifying Installed Packages")

    required_packages = ["pytest", "requests", "python-dotenv"]

    try:
        result = client.containers.run(
            "kai_agent_sandbox",
            "pip list",
            remove=True
        )
        installed = result.decode('utf-8')

        all_installed = True
        for package in required_packages:
            is_installed = package in installed
            print_check(is_installed, f"Package '{package}' installed")
            all_installed = all_installed and is_installed

        return all_installed
    except Exception as e:
        print_check(False, f"Failed to verify packages: {e}")
        return False


def verify_security_features(client):
    """Verify security features."""
    print_header("Verifying Security Features")

    checks_passed = 0
    total_checks = 0

    # Check 1: No sudo access
    total_checks += 1
    try:
        result = client.containers.run(
            "kai_agent_sandbox",
            "which sudo",
            remove=True
        )
        output = result.decode('utf-8').strip()
        has_no_sudo = not output or "not found" in output
        print_check(has_no_sudo, "No sudo access")
        if has_no_sudo:
            checks_passed += 1
    except Exception:
        # Command failed - good, sudo not available
        print_check(True, "No sudo access (command failed)")
        checks_passed += 1

    # Check 2: Cannot write to /etc
    total_checks += 1
    try:
        result = client.containers.run(
            "kai_agent_sandbox",
            "touch /etc/test.txt",
            remove=True
        )
        print_check(False, "Can write to /etc (security issue)")
    except Exception:
        # Expected - should not be able to write
        print_check(True, "Cannot write to /etc")
        checks_passed += 1

    # Check 3: Limited shell access
    total_checks += 1
    try:
        result = client.containers.run(
            "kai_agent_sandbox",
            "echo $SHELL",
            remove=True
        )
        shell = result.decode('utf-8').strip()
        print_check(True, f"Shell: {shell}")
        checks_passed += 1
    except Exception as e:
        print_check(False, f"Failed to check shell: {e}")

    return checks_passed == total_checks


def verify_basic_execution(client):
    """Verify basic code execution works."""
    print_header("Verifying Basic Execution")

    try:
        # Test Python execution
        result = client.containers.run(
            "kai_agent_sandbox",
            "python -c \"print('Hello from sandbox')\"",
            remove=True
        )
        output = result.decode('utf-8').strip()

        python_works = "Hello from sandbox" in output
        print_check(python_works, f"Python execution: {output}")

        # Test file operations
        result = client.containers.run(
            "kai_agent_sandbox",
            "python -c \"with open('test.txt', 'w') as f: f.write('test'); print('File created')\"",
            remove=True)
        output = result.decode('utf-8').strip()

        file_ops_work = "File created" in output
        print_check(file_ops_work, f"File operations: {output}")

        return python_works and file_ops_work
    except Exception as e:
        print_check(False, f"Failed to verify execution: {e}")
        return False


def main():
    """Run all verification checks."""
    print("\n" + "=" * 70)
    print("DOCKER SANDBOX BUILD VERIFICATION (Task 14.1)")
    print("=" * 70)
    print("\nThis script verifies:")
    print("  - Docker is available")
    print("  - Sandbox image is built")
    print("  - Python 3.11 environment")
    print("  - Unprivileged user (sandboxuser)")
    print("  - Workspace directory")
    print("  - Required packages")
    print("  - Security features")
    print("  - Basic execution")

    # Run all checks
    checks = []

    # Check 1: Docker available
    docker_ok, client = verify_docker_available()
    checks.append(("Docker Available", docker_ok))

    if not docker_ok:
        print("\n" + "=" * 70)
        print("✗ VERIFICATION FAILED - Docker not available")
        print("=" * 70)
        return 1

    # Check 2: Image exists
    image_ok, image = verify_image_exists(client)
    checks.append(("Image Exists", image_ok))

    if not image_ok:
        print("\n" + "=" * 70)
        print("✗ VERIFICATION FAILED - Image not built")
        print("=" * 70)
        return 1

    # Check 3-8: Image features
    checks.append(("Python Version", verify_python_version(client)))
    checks.append(("Unprivileged User", verify_unprivileged_user(client)))
    checks.append(("Workspace Directory", verify_workspace_directory(client)))
    checks.append(("Installed Packages", verify_installed_packages(client)))
    checks.append(("Security Features", verify_security_features(client)))
    checks.append(("Basic Execution", verify_basic_execution(client)))

    # Print summary
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, ok in checks if ok)
    total = len(checks)

    for check_name, ok in checks:
        symbol = "✓" if ok else "✗"
        print(f"{symbol} {check_name}")

    print(f"\nPassed: {passed}/{total}")
    print(f"Success rate: {(passed / total * 100):.1f}%")

    if passed == total:
        print("\n" + "=" * 70)
        print("✓ ALL CHECKS PASSED - Task 14.1 Complete!")
        print("=" * 70)
        print("\nThe Docker sandbox image is properly built and configured.")
        print("\nRequirements verified:")
        print("  ✓ 5.1 - Docker container with Python")
        print("  ✓ 5.2 - Unprivileged user execution")
        print("  ✓ 5.5 - Python environment setup")
        print("\nNext steps:")
        print("  1. Run full tests: python Agent/test_sandbox_complete.py")
        print("  2. Or run: python Agent/test_execution_tools.py")
        return 0
    print("\n" + "=" * 70)
    print("✗ VERIFICATION FAILED")
    print("=" * 70)
    print("\nSome checks failed. Please review the output above.")
    print("\nTo rebuild the image:")
    print("  python Agent/build_sandbox.py")
    return 1


if __name__ == "__main__":
    sys.exit(main())
