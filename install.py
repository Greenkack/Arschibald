#!/usr/bin/env python3
"""Installation script for Robust Streamlit App"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required, found {version.major}.{version.minor}")
        return False
    print(
        f"✅ Python {
            version.major}.{
            version.minor}.{
                version.micro} is compatible")
    return True


def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")

    # Core dependencies that are absolutely required
    core_deps = [
        "streamlit>=1.28.0",
        "pandas>=2.0.0",
        "sqlalchemy>=2.0.0",
        "duckdb>=0.9.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0"
    ]

    # Optional dependencies for full functionality
    optional_deps = [
        "structlog>=23.0.0",
        "apscheduler>=3.10.0",
        "redis>=4.5.0",
        "typer>=0.9.0",
        "rich>=13.5.0"
    ]

    # Try to install core dependencies first
    for dep in core_deps:
        if not run_command(
            f"pip install {dep}",
            f"Installing {
                dep.split('>=')[0]}"):
            print(f"⚠️  Failed to install {dep}, but continuing...")

    # Try to install optional dependencies
    print("\n📦 Installing optional dependencies...")
    for dep in optional_deps:
        if not run_command(
            f"pip install {dep}",
            f"Installing {
                dep.split('>=')[0]}"):
            print(f"⚠️  Optional dependency {dep} failed, skipping...")

    return True


def create_env_file():
    """Create .env file if it doesn't exist"""
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file already exists")
        return True

    print("📝 Creating .env file...")
    env_content = """# Environment Configuration
ENV=dev
DEBUG=true

# Database
DATABASE_URL=duckdb:///app.db

# Security
SECRET_KEY=dev-secret-key-change-in-production

# Cache
CACHE_TTL=3600
CACHE_MAX_ENTRIES=1000

# Jobs
JOB_BACKEND=memory
JOB_MAX_WORKERS=4

# Logging
LOG_LEVEL=INFO
"""

    try:
        env_file.write_text(env_content)
        print("✅ .env file created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False


def create_directories():
    """Create necessary directories"""
    directories = ["data", "logs", "backups", "tests"]

    for dir_name in directories:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"✅ Created directory: {dir_name}")
            except Exception as e:
                print(f"❌ Failed to create directory {dir_name}: {e}")
        else:
            print(f"✅ Directory {dir_name} already exists")


def test_installation():
    """Test if the installation works"""
    print("\n🧪 Testing installation...")

    # Test imports
    test_imports = [
        ("streamlit", "Streamlit"),
        ("sqlalchemy", "SQLAlchemy"),
        ("duckdb", "DuckDB"),
        ("pydantic", "Pydantic")
    ]

    for module, name in test_imports:
        try:
            __import__(module)
            print(f"✅ {name} import successful")
        except ImportError:
            print(f"❌ {name} import failed")

    # Test simple app
    print("\n🚀 Testing simple app...")
    if run_command(
        "python -c \"import simple_app; print('Simple app loads successfully')\"",
            "Loading simple app"):
        print("✅ Simple app test passed")
    else:
        print("❌ Simple app test failed")


def main():
    """Main installation process"""
    print("🚀 Robust Streamlit App Installation")
    print("=" * 40)

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Install dependencies
    install_dependencies()

    # Create configuration
    create_env_file()

    # Create directories
    create_directories()

    # Test installation
    test_installation()

    print("\n" + "=" * 40)
    print("🎉 Installation completed!")
    print("\n📋 Next steps:")
    print("1. Review and update .env file if needed")
    print("2. Run simple version: streamlit run simple_app.py")
    print("3. Or run full version: streamlit run app.py")
    print("4. Check README.md for more information")


if __name__ == "__main__":
    main()
