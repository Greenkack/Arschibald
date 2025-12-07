#!/usr/bin/env python3
"""
Packaging Setup Verification Script

This script verifies that all packaging files are in place and the system
is ready to build the backend executable.

Usage:
    python verify_packaging_setup.py
"""

import os
import sys
from pathlib import Path

class Colors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_success(message):
    print(f"{Colors.OKGREEN} {message}{Colors.ENDC}")

def print_error(message):
    print(f"{Colors.FAIL} {message}{Colors.ENDC}")

def print_warning(message):
    print(f"{Colors.WARNING} {message}{Colors.ENDC}")

def print_header(message):
    print(f"\n{Colors.BOLD}{message}{Colors.ENDC}")

def check_file_exists(file_path, description):
    """Check if a file exists"""
    if file_path.exists():
        print_success(f"{description}: {file_path.name}")
        return True
    else:
        print_error(f"{description} not found: {file_path}")
        return False

def check_python_version():
    """Check Python version"""
    print_header("Checking Python Version")
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        print_success(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_error(f"Python 3.10+ required, found {version.major}.{version.minor}.{version.micro}")
        return False

def check_dependencies():
    """Check if required dependencies are installed"""
    print_header("Checking Dependencies")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'pydantic',
        'PyInstaller',
    ]
    
    all_installed = True
    for package in required_packages:
        try:
            # Special handling for PyInstaller
            if package == 'PyInstaller':
                __import__('PyInstaller')
            else:
                __import__(package.lower().replace('-', '_'))
            print_success(f"{package} installed")
        except ImportError:
            print_error(f"{package} not installed")
            all_installed = False
    
    return all_installed

def check_packaging_files():
    """Check if all packaging files exist"""
    print_header("Checking Packaging Files")
    
    backend_dir = Path(__file__).parent
    
    files_to_check = [
        (backend_dir / 'backend.spec', 'PyInstaller spec file'),
        (backend_dir / 'build_backend.py', 'Build script'),
        (backend_dir / 'test_packaging.py', 'Test suite'),
        (backend_dir / 'requirements.txt', 'Requirements file'),
        (backend_dir / 'main.py', 'Main application file'),
    ]
    
    all_exist = True
    for file_path, description in files_to_check:
        if not check_file_exists(file_path, description):
            all_exist = False
    
    return all_exist

def check_documentation():
    """Check if documentation files exist"""
    print_header("Checking Documentation")
    
    backend_dir = Path(__file__).parent
    docs_dir = backend_dir / 'docs'
    
    docs_to_check = [
        (docs_dir / 'BACKEND_PACKAGING_GUIDE.md', 'Complete guide'),
        (docs_dir / 'BACKEND_PACKAGING_QUICK_REFERENCE.md', 'Quick reference'),
        (backend_dir / 'PACKAGING_README.md', 'README'),
        (backend_dir / 'QUICK_START_PACKAGING.md', 'Quick start guide'),
    ]
    
    all_exist = True
    for file_path, description in docs_to_check:
        if not check_file_exists(file_path, description):
            all_exist = False
    
    return all_exist

def check_directory_structure():
    """Check if required directories exist"""
    print_header("Checking Directory Structure")
    
    backend_dir = Path(__file__).parent
    
    dirs_to_check = [
        (backend_dir / 'api', 'API directory'),
        (backend_dir / 'core', 'Core directory'),
        (backend_dir / 'models', 'Models directory'),
        (backend_dir / 'services', 'Services directory'),
        (backend_dir / 'docs', 'Documentation directory'),
    ]
    
    all_exist = True
    for dir_path, description in dirs_to_check:
        if dir_path.exists():
            print_success(f"{description}: {dir_path.name}/")
        else:
            print_warning(f"{description} not found: {dir_path}")
            all_exist = False
    
    return all_exist

def check_pyinstaller():
    """Check if PyInstaller is properly installed"""
    print_header("Checking PyInstaller")
    
    try:
        import PyInstaller
        print_success(f"PyInstaller {PyInstaller.__version__} installed")
        
        # Check if pyinstaller command is available
        import subprocess
        result = subprocess.run(
            ['pyinstaller', '--version'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print_success("PyInstaller command available")
            return True
        else:
            print_warning("PyInstaller installed but command not available")
            return True
    except ImportError:
        print_error("PyInstaller not installed")
        print_warning("Install with: pip install pyinstaller")
        return False
    except FileNotFoundError:
        print_warning("PyInstaller command not found in PATH")
        return True

def print_summary(results):
    """Print summary of checks"""
    print_header("Summary")
    
    total = len(results)
    passed = sum(results.values())
    
    print(f"\nChecks passed: {passed}/{total}")
    
    if passed == total:
        print_success("\n All checks passed! Ready to build.")
        print("\nNext steps:")
        print("  1. Run: python build_backend.py")
        print("  2. Or: python build_backend.py --clean --optimize --test --package")
        return 0
    else:
        print_error("\n Some checks failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  - Install dependencies: pip install -r requirements.txt")
        print("  - Install PyInstaller: pip install pyinstaller")
        print("  - Check Python version: python --version")
        return 1

def main():
    """Main verification function"""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{'Backend Packaging Setup Verification'.center(60)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")
    
    results = {
        'Python Version': check_python_version(),
        'Dependencies': check_dependencies(),
        'Packaging Files': check_packaging_files(),
        'Documentation': check_documentation(),
        'Directory Structure': check_directory_structure(),
        'PyInstaller': check_pyinstaller(),
    }
    
    return print_summary(results)

if __name__ == '__main__':
    sys.exit(main())
