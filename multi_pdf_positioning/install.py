"""
Installation Script for Multi-PDF Positioning System

This script automates the installation and setup process.
"""

import sys
import subprocess
import platform
from pathlib import Path
from typing import List, Tuple, Optional


class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(message: str):
    """Print a header message."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 70}{Colors.ENDC}\n")


def print_success(message: str):
    """Print a success message."""
    print(f"{Colors.OKGREEN}{message}{Colors.ENDC}")


def print_error(message: str):
    """Print an error message."""
    print(f"{Colors.FAIL}{message}{Colors.ENDC}")


def print_warning(message: str):
    """Print a warning message."""
    print(f"{Colors.WARNING} {message}{Colors.ENDC}")


def print_info(message: str):
    """Print an info message."""
    print(f"{Colors.OKBLUE}ℹ {message}{Colors.ENDC}")


def check_python_version() -> Tuple[bool, str]:
    """
    Check if Python version meets requirements.
    
    Returns:
        Tuple of (success, message)
    """
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        return False, f"Python 3.8+ required, found {version_str}"
    
    return True, f"Python {version_str}"


def check_pip() -> Tuple[bool, str]:
    """
    Check if pip is available.
    
    Returns:
        Tuple of (success, message)
    """
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout.strip()
    except subprocess.CalledProcessError:
        return False, "pip not found"


def install_dependencies() -> Tuple[bool, str]:
    """
    Install required dependencies.
    
    Returns:
        Tuple of (success, message)
    """
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        return False, f"requirements.txt not found at {requirements_file}"
    
    try:
        print_info("Installing dependencies...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
            capture_output=True,
            text=True,
            check=True
        )
        return True, "Dependencies installed successfully"
    except subprocess.CalledProcessError as e:
        return False, f"Failed to install dependencies: {e.stderr}"


def verify_dependencies() -> List[Tuple[str, bool, str]]:
    """
    Verify that all dependencies are installed.
    
    Returns:
        List of (package_name, success, version/error)
    """
    dependencies = [
        ("yaml", "PyYAML"),
        ("PyPDF2", "PyPDF2"),
        ("pdfplumber", "pdfplumber"),
        ("PIL", "Pillow")
    ]
    
    results = []
    
    for import_name, package_name in dependencies:
        try:
            module = __import__(import_name)
            version = getattr(module, "__version__", "unknown")
            results.append((package_name, True, version))
        except ImportError:
            results.append((package_name, False, "not installed"))
    
    return results


def create_directories() -> Tuple[bool, str]:
    """
    Create required directories.
    
    Returns:
        Tuple of (success, message)
    """
    directories = [
        "output",
        "coords_multi_backup",
        "logs",
        "analysis"
    ]
    
    created = []
    
    for dir_name in directories:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                created.append(dir_name)
            except Exception as e:
                return False, f"Failed to create {dir_name}: {e}"
    
    if created:
        return True, f"Created directories: {', '.join(created)}"
    else:
        return True, "All directories already exist"


def verify_input_files() -> Tuple[bool, str]:
    """
    Verify that input files exist.
    
    Returns:
        Tuple of (success, message)
    """
    # Check YML directory
    yml_dir = Path("coords_multi")
    if not yml_dir.exists():
        return False, f"YML directory not found: {yml_dir}"
    
    yml_files = list(yml_dir.glob("*.yml"))
    if len(yml_files) == 0:
        return False, f"No YML files found in {yml_dir}"
    
    # Check PDF directory (from config)
    try:
        from multi_pdf_positioning.config import PDF_DIR
        if not PDF_DIR.exists():
            return False, f"PDF directory not found: {PDF_DIR}"
        
        pdf_files = list(PDF_DIR.glob("*.pdf"))
        if len(pdf_files) == 0:
            return False, f"No PDF files found in {PDF_DIR}"
        
        return True, f"Found {len(yml_files)} YML files and {len(pdf_files)} PDF files"
    
    except ImportError:
        return False, "Failed to import config module"


def install_package() -> Tuple[bool, str]:
    """
    Install the package in development mode.
    
    Returns:
        Tuple of (success, message)
    """
    try:
        print_info("Installing package...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", "."],
            capture_output=True,
            text=True,
            check=True
        )
        return True, "Package installed successfully"
    except subprocess.CalledProcessError as e:
        return False, f"Failed to install package: {e.stderr}"


def run_tests() -> Tuple[bool, str]:
    """
    Run basic tests to verify installation.
    
    Returns:
        Tuple of (success, message)
    """
    try:
        # Test imports
        from multi_pdf_positioning.yml_parser import YMLParser
        from multi_pdf_positioning.pdf_analyzer import PDFAnalyzer
        from multi_pdf_positioning.position_calculator import PositionCalculator
        from multi_pdf_positioning.yml_generator import YMLGenerator
        from multi_pdf_positioning.validation_system import ValidationSystem
        
        return True, "All modules imported successfully"
    except ImportError as e:
        return False, f"Failed to import modules: {e}"


def display_system_info():
    """Display system information."""
    print_info("System Information:")
    print(f"  OS: {platform.system()} {platform.release()}")
    print(f"  Architecture: {platform.machine()}")
    print(f"  Python: {sys.version.split()[0]}")
    print(f"  Python Path: {sys.executable}")


def main():
    """Main installation function."""
    print_header("Multi-PDF Positioning System - Installation")
    
    # Display system info
    display_system_info()
    
    # Step 1: Check Python version
    print_header("Step 1: Checking Python Version")
    success, message = check_python_version()
    if success:
        print_success(message)
    else:
        print_error(message)
        print_error("Installation aborted. Please upgrade Python to 3.8 or higher.")
        return 1
    
    # Step 2: Check pip
    print_header("Step 2: Checking pip")
    success, message = check_pip()
    if success:
        print_success(message)
    else:
        print_error(message)
        print_error("Installation aborted. Please install pip.")
        return 1
    
    # Step 3: Install dependencies
    print_header("Step 3: Installing Dependencies")
    success, message = install_dependencies()
    if success:
        print_success(message)
    else:
        print_error(message)
        print_error("Installation aborted.")
        return 1
    
    # Step 4: Verify dependencies
    print_header("Step 4: Verifying Dependencies")
    results = verify_dependencies()
    all_installed = True
    for package, success, version in results:
        if success:
            print_success(f"{package}: {version}")
        else:
            print_error(f"{package}: {version}")
            all_installed = False
    
    if not all_installed:
        print_warning("Some dependencies are missing. Installation may not work correctly.")
    
    # Step 5: Create directories
    print_header("Step 5: Creating Directories")
    success, message = create_directories()
    if success:
        print_success(message)
    else:
        print_error(message)
        print_warning("Continuing anyway...")
    
    # Step 6: Install package
    print_header("Step 6: Installing Package")
    success, message = install_package()
    if success:
        print_success(message)
    else:
        print_error(message)
        print_warning("Package installation failed. You can still use the system by adding it to PYTHONPATH.")
    
    # Step 7: Run tests
    print_header("Step 7: Running Tests")
    success, message = run_tests()
    if success:
        print_success(message)
    else:
        print_error(message)
        print_warning("Some tests failed. System may not work correctly.")
    
    # Step 8: Verify input files
    print_header("Step 8: Verifying Input Files")
    success, message = verify_input_files()
    if success:
        print_success(message)
    else:
        print_warning(message)
        print_warning("Input files not found. You'll need to configure paths in config.py")
    
    # Final summary
    print_header("Installation Complete")
    print_success("Multi-PDF Positioning System has been installed successfully!")
    
    print("\nNext Steps:")
    print("  1. Review and update configuration in multi_pdf_positioning/config.py")
    print("  2. Verify input files (PDF templates and YML coordinates)")
    print("  3. Run a test: multi-pdf-positioning run --firmen 1 --seiten 1")
    print("  4. Review documentation: multi_pdf_positioning/DEPLOYMENT_GUIDE.md")
    
    print("\nUsage:")
    print("  multi-pdf-positioning --help")
    print("  multi-pdf-positioning run")
    print("  multi-pdf-positioning analyze")
    print("  multi-pdf-positioning validate")
    
    print(f"\n{Colors.OKGREEN}Installation successful!{Colors.ENDC}\n")
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Installation interrupted by user{Colors.ENDC}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.FAIL}Unexpected error: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
