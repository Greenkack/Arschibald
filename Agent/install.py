#!/usr/bin/env python3
"""
KAI Agent Installation Script

This script automates the installation and setup of the KAI Agent system.

Usage:
    python Agent/install.py
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print a formatted header."""
    print()
    print("=" * 70)
    print(f"{Colors.CYAN}{Colors.BOLD}{text}{Colors.RESET}")
    print("=" * 70)
    print()


def print_success(text):
    """Print a success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")


def print_error(text):
    """Print an error message."""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")


def print_warning(text):
    """Print a warning message."""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")


def print_info(text):
    """Print an info message."""
    print(f"{Colors.CYAN}ℹ {text}{Colors.RESET}")


def check_python_version():
    """Check if Python version is 3.11 or higher."""
    print_header("Checking Python Version")

    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")

    if version.major >= 3 and version.minor >= 11:
        print_success("Python version is compatible")
        return True
    print_error("Python 3.11 or higher is required")
    print_info("Download from: https://www.python.org/downloads/")
    return False


def check_docker():
    """Check if Docker is installed and running."""
    print_header("Checking Docker")

    # Check if Docker is installed
    if not shutil.which("docker"):
        print_error("Docker is not installed")
        print_info("Install Docker Desktop:")
        print_info(
            "  Windows/Mac: https://www.docker.com/products/docker-desktop")
        print_info("  Linux: https://docs.docker.com/engine/install/")
        return False

    print_success("Docker is installed")

    # Check if Docker is running
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print_success("Docker is running")
            return True
        print_error("Docker is not running")
        print_info("Please start Docker Desktop and try again")
        return False
    except subprocess.TimeoutExpired:
        print_error("Docker command timed out")
        return False
    except Exception as e:
        print_error(f"Error checking Docker: {e}")
        return False


def install_dependencies():
    """Install Python dependencies."""
    print_header("Installing Python Dependencies")

    requirements_file = Path("Agent/requirements.txt")

    if not requirements_file.exists():
        print_error(f"Requirements file not found: {requirements_file}")
        return False

    print_info(f"Installing from: {requirements_file}")
    print()

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
            check=True
        )
        print()
        print_success("Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print()
        print_error("Failed to install dependencies")
        print_info("Try running manually: pip install -r Agent/requirements.txt")
        return False


def setup_env_file():
    """Set up the .env file."""
    print_header("Setting Up Environment File")

    env_file = Path(".env")
    env_example = Path(".env.example")

    if env_file.exists():
        print_warning(".env file already exists")
        response = input(
            "Do you want to overwrite it? (y/N): ").strip().lower()
        if response != 'y':
            print_info("Keeping existing .env file")
            return True

    if not env_example.exists():
        print_error(".env.example file not found")
        return False

    # Copy example file
    shutil.copy(env_example, env_file)
    print_success("Created .env file from template")

    # Prompt for API keys
    print()
    print_info("Please configure your API keys in the .env file")
    print_info("At minimum, you need: OPENAI_API_KEY")
    print()

    # Ask if user wants to edit now
    response = input(
        "Do you want to edit the .env file now? (Y/n): ").strip().lower()
    if response != 'n':
        # Try to open in default editor
        if sys.platform == 'win32':
            os.system(f'notepad {env_file}')
        elif sys.platform == 'darwin':
            os.system(f'open -e {env_file}')
        else:
            os.system(f'nano {env_file}')

    return True


def build_docker_image():
    """Build the Docker sandbox image."""
    print_header("Building Docker Sandbox Image")

    sandbox_dir = Path("Agent/sandbox")

    if not sandbox_dir.exists():
        print_error(f"Sandbox directory not found: {sandbox_dir}")
        return False

    print_info("Building image 'kai_agent_sandbox'...")
    print_info("This may take a few minutes on first build...")
    print()

    try:
        result = subprocess.run(
            ["docker", "build", "-t", "kai_agent_sandbox", "-f",
             str(sandbox_dir / "Dockerfile"), str(sandbox_dir)],
            check=True
        )
        print()
        print_success("Docker image built successfully")
        return True
    except subprocess.CalledProcessError:
        print()
        print_error("Failed to build Docker image")
        print_info("Try running manually:")
        print_info(
            "  docker build -t kai_agent_sandbox -f Agent/sandbox/Dockerfile Agent/sandbox/")
        return False


def setup_knowledge_base():
    """Set up the knowledge base directory."""
    print_header("Setting Up Knowledge Base")

    kb_dir = Path("Agent/knowledge_base")

    if not kb_dir.exists():
        kb_dir.mkdir(parents=True, exist_ok=True)
        print_success(f"Created knowledge base directory: {kb_dir}")
    else:
        print_success(f"Knowledge base directory exists: {kb_dir}")

    # Check if there are any PDFs
    pdf_files = list(kb_dir.glob("*.pdf"))

    if pdf_files:
        print_success(f"Found {len(pdf_files)} PDF document(s)")
    else:
        print_warning("No PDF documents found in knowledge base")
        print_info("Add PDF files to Agent/knowledge_base/ for domain knowledge")

    return True


def setup_workspace():
    """Set up the agent workspace directory."""
    print_header("Setting Up Agent Workspace")

    workspace_dir = Path("Agent/agent_workspace")

    if not workspace_dir.exists():
        workspace_dir.mkdir(parents=True, exist_ok=True)
        print_success(f"Created workspace directory: {workspace_dir}")
    else:
        print_success(f"Workspace directory exists: {workspace_dir}")

    return True


def setup_logs():
    """Set up the logs directory."""
    print_header("Setting Up Logs Directory")

    logs_dir = Path("Agent/logs")

    if not logs_dir.exists():
        logs_dir.mkdir(parents=True, exist_ok=True)
        print_success(f"Created logs directory: {logs_dir}")
    else:
        print_success(f"Logs directory exists: {logs_dir}")

    return True


def run_validation():
    """Run the validation script."""
    print_header("Running Validation")

    validation_script = Path("Agent/validate_config.py")

    if not validation_script.exists():
        print_warning("Validation script not found")
        return True

    try:
        result = subprocess.run(
            [sys.executable, str(validation_script)],
            check=True
        )
        print()
        print_success("Validation passed")
        return True
    except subprocess.CalledProcessError:
        print()
        print_warning("Validation found some issues")
        print_info("Please review the output above and fix any problems")
        return True  # Don't fail installation


def print_next_steps():
    """Print next steps for the user."""
    print_header("Installation Complete!")

    print("Next steps:")
    print()
    print("1. Configure API Keys:")
    print("   - Edit the .env file")
    print("   - Add your OPENAI_API_KEY (required)")
    print("   - Add optional keys for additional features")
    print()
    print("2. Add Knowledge Base (Optional):")
    print("   - Place PDF documents in Agent/knowledge_base/")
    print("   - Agent will automatically index them")
    print()
    print("3. Start the Application:")
    print("   - Run your main application")
    print("   - Navigate to the A.G.E.N.T. menu")
    print()
    print("4. Test the Agent:")
    print("   - Try a simple task like:")
    print("     'Schreibe eine Funktion, die 1+1 berechnet'")
    print()
    print("For help and documentation:")
    print("  - Agent/README.md")
    print("  - Agent/AGENT_CORE_QUICK_START.md")
    print("  - Agent/API_KEY_SECURITY_GUIDE.md")
    print()


def main():
    """Main installation flow."""
    print()
    print(f"{Colors.BOLD}{Colors.CYAN}")
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║                                                                   ║")
    print("║              KAI Agent Installation Script                        ║")
    print("║                                                                   ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}")

    # Track success of each step
    steps = [
        ("Check Python Version", check_python_version),
        ("Check Docker", check_docker),
        ("Install Dependencies", install_dependencies),
        ("Setup Environment File", setup_env_file),
        ("Build Docker Image", build_docker_image),
        ("Setup Knowledge Base", setup_knowledge_base),
        ("Setup Workspace", setup_workspace),
        ("Setup Logs", setup_logs),
        ("Run Validation", run_validation),
    ]

    failed_steps = []

    for step_name, step_func in steps:
        try:
            if not step_func():
                failed_steps.append(step_name)
        except KeyboardInterrupt:
            print()
            print()
            print_warning("Installation cancelled by user")
            sys.exit(1)
        except Exception as e:
            print_error(f"Unexpected error in {step_name}: {e}")
            failed_steps.append(step_name)

    # Print summary
    print()
    print("=" * 70)
    print(f"{Colors.BOLD}Installation Summary{Colors.RESET}")
    print("=" * 70)
    print()

    if failed_steps:
        print_error(
            f"Installation completed with {
                len(failed_steps)} issue(s):")
        for step in failed_steps:
            print(f"  - {step}")
        print()
        print_info("Please fix the issues above and run the installation again")
        sys.exit(1)
    else:
        print_success("All installation steps completed successfully!")
        print_next_steps()
        sys.exit(0)


if __name__ == "__main__":
    main()
