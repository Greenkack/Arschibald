#!/usr/bin/env python3
"""
Backend Build Script

This script automates the process of building the backend into a standalone executable.
It handles dependency installation, PyInstaller execution, and post-build optimization.

Usage:
    python build_backend.py [--clean] [--optimize] [--test]

Options:
    --clean     Clean build directories before building
    --optimize  Apply additional optimizations to reduce bundle size
    --test      Test the built executable after building
"""

import os
import sys
import shutil
import subprocess
import argparse
from pathlib import Path
import platform

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(message):
    """Print a formatted header message"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(message):
    """Print a success message"""
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")

def print_error(message):
    """Print an error message"""
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")

def print_info(message):
    """Print an info message"""
    print(f"{Colors.OKBLUE}ℹ {message}{Colors.ENDC}")

def print_warning(message):
    """Print a warning message"""
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")

def get_backend_dir():
    """Get the backend directory path"""
    return Path(__file__).parent.absolute()

def clean_build_dirs():
    """Clean build and dist directories"""
    print_header("Cleaning Build Directories")
    
    backend_dir = get_backend_dir()
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        dir_path = backend_dir / dir_name
        if dir_path.exists():
            print_info(f"Removing {dir_name}/")
            shutil.rmtree(dir_path)
            print_success(f"Removed {dir_name}/")
    
    # Remove .spec file if it exists (will be regenerated)
    spec_file = backend_dir / 'backend.spec'
    if spec_file.exists() and not args.keep_spec:
        print_info("Removing old spec file")
        spec_file.unlink()
        print_success("Removed backend.spec")

def install_pyinstaller():
    """Install PyInstaller if not already installed"""
    print_header("Checking PyInstaller Installation")
    
    try:
        import PyInstaller
        print_success(f"PyInstaller {PyInstaller.__version__} is already installed")
        return True
    except ImportError:
        print_warning("PyInstaller not found. Installing...")
        try:
            subprocess.run(
                [sys.executable, '-m', 'pip', 'install', 'pyinstaller'],
                check=True,
                capture_output=True
            )
            print_success("PyInstaller installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print_error(f"Failed to install PyInstaller: {e}")
            return False

def check_dependencies():
    """Check if all required dependencies are installed"""
    print_header("Checking Dependencies")
    
    backend_dir = get_backend_dir()
    requirements_file = backend_dir / 'requirements.txt'
    
    if not requirements_file.exists():
        print_error("requirements.txt not found")
        return False
    
    print_info("Verifying all dependencies are installed...")
    try:
        subprocess.run(
            [sys.executable, '-m', 'pip', 'check'],
            check=True,
            capture_output=True
        )
        print_success("All dependencies are properly installed")
        return True
    except subprocess.CalledProcessError:
        print_warning("Some dependencies may be missing or incompatible")
        print_info("Installing/updating dependencies from requirements.txt...")
        try:
            subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)],
                check=True
            )
            print_success("Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print_error(f"Failed to install dependencies: {e}")
            return False

def create_runtime_hook():
    """Create a runtime hook for PyInstaller"""
    print_header("Creating Runtime Hook")
    
    backend_dir = get_backend_dir()
    hook_file = backend_dir / 'runtime_hook.py'
    
    hook_content = '''"""
Runtime hook for PyInstaller

This hook is executed before the main application starts.
It sets up the environment and handles any runtime configuration.
"""

import sys
import os

# Set up environment variables
if getattr(sys, 'frozen', False):
    # Running in PyInstaller bundle
    bundle_dir = sys._MEIPASS
    
    # Add bundle directory to path
    sys.path.insert(0, bundle_dir)
    
    # Set environment variable for bundle directory
    os.environ['BUNDLE_DIR'] = bundle_dir
    
    # Disable bytecode writing
    sys.dont_write_bytecode = True
'''
    
    with open(hook_file, 'w') as f:
        f.write(hook_content)
    
    print_success("Runtime hook created")
    return hook_file

def build_executable():
    """Build the executable using PyInstaller"""
    print_header("Building Executable")
    
    backend_dir = get_backend_dir()
    spec_file = backend_dir / 'backend.spec'
    
    if not spec_file.exists():
        print_error("backend.spec not found")
        return False
    
    print_info("Running PyInstaller...")
    print_info(f"Platform: {platform.system()} {platform.machine()}")
    print_info(f"Python: {sys.version}")
    
    try:
        # Run PyInstaller
        result = subprocess.run(
            ['pyinstaller', '--clean', str(spec_file)],
            cwd=backend_dir,
            check=True,
            capture_output=False
        )
        
        print_success("Executable built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"PyInstaller failed: {e}")
        return False
    except FileNotFoundError:
        print_error("PyInstaller command not found. Is it installed?")
        return False

def optimize_bundle():
    """Apply optimizations to reduce bundle size"""
    print_header("Optimizing Bundle")
    
    backend_dir = get_backend_dir()
    dist_dir = backend_dir / 'dist' / 'backend'
    
    if not dist_dir.exists():
        print_error("Distribution directory not found")
        return False
    
    # Remove unnecessary files
    patterns_to_remove = [
        '*.pyc',
        '*.pyo',
        '__pycache__',
        '*.dist-info',
        'tests',
        'test',
        'examples',
        'docs',
        'LICENSE*',
        'README*',
        '*.md',
    ]
    
    removed_count = 0
    for pattern in patterns_to_remove:
        for item in dist_dir.rglob(pattern):
            try:
                if item.is_file():
                    item.unlink()
                    removed_count += 1
                elif item.is_dir():
                    shutil.rmtree(item)
                    removed_count += 1
            except Exception as e:
                print_warning(f"Could not remove {item}: {e}")
    
    print_success(f"Removed {removed_count} unnecessary files/directories")
    
    # Calculate bundle size
    total_size = sum(f.stat().st_size for f in dist_dir.rglob('*') if f.is_file())
    size_mb = total_size / (1024 * 1024)
    print_info(f"Final bundle size: {size_mb:.2f} MB")
    
    return True

def test_executable():
    """Test the built executable"""
    print_header("Testing Executable")
    
    backend_dir = get_backend_dir()
    
    # Determine executable name based on platform
    if platform.system() == 'Windows':
        exe_name = 'backend.exe'
    else:
        exe_name = 'backend'
    
    exe_path = backend_dir / 'dist' / 'backend' / exe_name
    
    if not exe_path.exists():
        print_error(f"Executable not found at {exe_path}")
        return False
    
    print_info(f"Testing {exe_path}")
    
    # Test 1: Check if executable runs
    print_info("Test 1: Checking if executable runs...")
    try:
        result = subprocess.run(
            [str(exe_path), '--help'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0 or 'uvicorn' in result.stdout.lower():
            print_success("Executable runs successfully")
        else:
            print_warning("Executable runs but may have issues")
            print_info(f"Output: {result.stdout}")
    except subprocess.TimeoutExpired:
        print_warning("Executable test timed out (this may be normal)")
    except Exception as e:
        print_error(f"Failed to run executable: {e}")
        return False
    
    # Test 2: Check file size
    print_info("Test 2: Checking file size...")
    exe_size = exe_path.stat().st_size / (1024 * 1024)
    print_info(f"Executable size: {exe_size:.2f} MB")
    
    if exe_size > 500:
        print_warning("Executable is quite large (>500 MB)")
    else:
        print_success("Executable size is reasonable")
    
    return True

def create_distribution_package():
    """Create a distribution package with all necessary files"""
    print_header("Creating Distribution Package")
    
    backend_dir = get_backend_dir()
    dist_dir = backend_dir / 'dist' / 'backend'
    package_dir = backend_dir / 'dist' / 'backend-package'
    
    if package_dir.exists():
        shutil.rmtree(package_dir)
    
    package_dir.mkdir(parents=True)
    
    # Copy executable and dependencies
    print_info("Copying files to package directory...")
    shutil.copytree(dist_dir, package_dir / 'backend')
    
    # Copy additional files
    files_to_copy = [
        '.env.example',
        'README.md',
    ]
    
    for file_name in files_to_copy:
        src = backend_dir / file_name
        if src.exists():
            shutil.copy2(src, package_dir / file_name)
            print_success(f"Copied {file_name}")
    
    # Create a startup script
    if platform.system() == 'Windows':
        startup_script = package_dir / 'start-backend.bat'
        script_content = '@echo off\ncd backend\nbackend.exe\n'
    else:
        startup_script = package_dir / 'start-backend.sh'
        script_content = '#!/bin/bash\ncd backend\n./backend\n'
    
    with open(startup_script, 'w') as f:
        f.write(script_content)
    
    if platform.system() != 'Windows':
        startup_script.chmod(0o755)
    
    print_success(f"Created startup script: {startup_script.name}")
    
    # Create README
    readme_content = f"""# Solar Calculator Pro - Backend

This package contains the standalone backend executable for Solar Calculator Pro.

## Contents

- `backend/` - Backend executable and dependencies
- `start-backend.{('bat' if platform.system() == 'Windows' else 'sh')}` - Startup script
- `.env.example` - Example environment configuration

## Running the Backend

### Option 1: Using the startup script
{('Double-click `start-backend.bat`' if platform.system() == 'Windows' else 'Run `./start-backend.sh`')}

### Option 2: Direct execution
```bash
cd backend
{('./backend.exe' if platform.system() == 'Windows' else './backend')}
```

## Configuration

1. Copy `.env.example` to `.env`
2. Edit `.env` with your configuration
3. Restart the backend

## Default Settings

- Port: 8000
- Host: localhost
- API Documentation: http://localhost:8000/docs

## System Requirements

- {platform.system()} {platform.machine()}
- No Python installation required (standalone executable)

## Support

For issues and support, please refer to the main documentation.

Built on: {platform.system()} {platform.release()}
Python version: {sys.version.split()[0]}
"""
    
    with open(package_dir / 'README.md', 'w') as f:
        f.write(readme_content)
    
    print_success("Created distribution package")
    print_info(f"Package location: {package_dir}")
    
    return True

def main():
    """Main build process"""
    global args
    
    parser = argparse.ArgumentParser(description='Build Solar Calculator Pro Backend')
    parser.add_argument('--clean', action='store_true', help='Clean build directories before building')
    parser.add_argument('--optimize', action='store_true', help='Apply optimizations to reduce bundle size')
    parser.add_argument('--test', action='store_true', help='Test the built executable')
    parser.add_argument('--keep-spec', action='store_true', help='Keep existing spec file')
    parser.add_argument('--package', action='store_true', help='Create distribution package')
    args = parser.parse_args()
    
    print_header("Solar Calculator Pro - Backend Build")
    print_info(f"Platform: {platform.system()} {platform.machine()}")
    print_info(f"Python: {sys.version}")
    
    # Step 1: Clean if requested
    if args.clean:
        clean_build_dirs()
    
    # Step 2: Install PyInstaller
    if not install_pyinstaller():
        print_error("Build failed: Could not install PyInstaller")
        return 1
    
    # Step 3: Check dependencies
    if not check_dependencies():
        print_error("Build failed: Dependency check failed")
        return 1
    
    # Step 4: Create runtime hook
    create_runtime_hook()
    
    # Step 5: Build executable
    if not build_executable():
        print_error("Build failed: PyInstaller execution failed")
        return 1
    
    # Step 6: Optimize if requested
    if args.optimize:
        if not optimize_bundle():
            print_warning("Optimization failed, but build is complete")
    
    # Step 7: Test if requested
    if args.test:
        if not test_executable():
            print_warning("Tests failed, but build is complete")
    
    # Step 8: Create package if requested
    if args.package:
        if not create_distribution_package():
            print_warning("Package creation failed, but build is complete")
    
    print_header("Build Complete!")
    print_success("Backend executable has been built successfully")
    print_info("Location: dist/backend/")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
