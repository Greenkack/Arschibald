"""
Verification script for Task 1.1: Enhanced Configuration System

This script verifies that all requirements for task 1.1 have been met.
"""

import os
import sys
from pathlib import Path


def verify_imports():
    """Verify all required imports work"""
    print("Verifying imports...")
    try:
        from core.config import (
            AppConfig,
            DatabaseConfig,
            CacheConfig,
            JobConfig,
            SecurityConfig,
            BackupConfig,
            PerformanceConfig,
            Environment,
            Mode,
            Theme,
            ComputeMode,
            load_config,
            load_config_for_environment,
            get_config,
            reset_config,
            validate_config,
        )
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def verify_appconfig_fields():
    """Verify AppConfig has all required fields"""
    print("\nVerifying AppConfig fields...")
    from core.config import load_config

    config = load_config()

    required_fields = [
        "env",
        "debug",
        "mode",
        "theme",
        "compute",
        "database",
        "cache",
        "jobs",
        "security",
        "backup",
        "performance",
        "features",
    ]

    missing_fields = []
    for field in required_fields:
        if not hasattr(config, field):
            missing_fields.append(field)

    if missing_fields:
        print(f"✗ Missing fields: {missing_fields}")
        return False

    print("✓ All required fields present")
    return True


def verify_enums():
    """Verify all enums are defined"""
    print("\nVerifying enums...")
    from core.config import Environment, Mode, Theme, ComputeMode

    checks = [
        (Environment, ["DEV", "STAGE", "PROD"]),
        (Mode, ["OFFLINE", "ONLINE"]),
        (Theme, ["AUTO", "LIGHT", "DARK"]),
        (ComputeMode, ["FAST", "ACCURATE"]),
    ]

    for enum_class, expected_values in checks:
        for value in expected_values:
            if not hasattr(enum_class, value):
                print(f"✗ {enum_class.__name__} missing {value}")
                return False

    print("✓ All enums defined correctly")
    return True


def verify_environment_loading():
    """Verify environment-specific loading works"""
    print("\nVerifying environment-specific loading...")
    from core.config import load_config_for_environment, Environment, reset_config

    try:
        for env in [Environment.DEV, Environment.STAGE, Environment.PROD]:
            reset_config()
            os.environ.pop("DEBUG", None)
            os.environ.pop("DATABASE_URL", None)
            config = load_config_for_environment(env)
            if config.env != env:
                print(f"✗ Environment loading failed for {env}")
                return False

        print("✓ Environment-specific loading works")
        return True
    except Exception as e:
        print(f"✗ Environment loading failed: {e}")
        return False


def verify_pydantic_validation():
    """Verify Pydantic validation is working"""
    print("\nVerifying Pydantic validation...")
    from core.config import DatabaseConfig, CacheConfig
    from pydantic import ValidationError

    # Test valid config
    try:
        db_config = DatabaseConfig(url="duckdb:///test.db", pool_size=5)
        print("✓ Valid configuration accepted")
    except ValidationError:
        print("✗ Valid configuration rejected")
        return False

    # Test invalid config (pool_size out of range)
    try:
        db_config = DatabaseConfig(url="duckdb:///test.db", pool_size=200)
        print("✗ Invalid configuration accepted (should have failed)")
        return False
    except ValidationError:
        print("✓ Invalid configuration rejected")

    return True


def verify_mode_theme_compute():
    """Verify mode, theme, and compute options work"""
    print("\nVerifying mode, theme, and compute options...")
    from core.config import load_config, Mode, Theme, ComputeMode, reset_config

    test_cases = [
        ("MODE", "offline", Mode.OFFLINE),
        ("MODE", "online", Mode.ONLINE),
        ("THEME", "auto", Theme.AUTO),
        ("THEME", "light", Theme.LIGHT),
        ("THEME", "dark", Theme.DARK),
        ("COMPUTE", "fast", ComputeMode.FAST),
        ("COMPUTE", "accurate", ComputeMode.ACCURATE),
    ]

    for env_var, value, expected in test_cases:
        reset_config()
        os.environ[env_var] = value
        config = load_config()
        actual = getattr(config, env_var.lower())
        if actual != expected:
            print(f"✗ {env_var}={value} failed: got {actual}, expected {expected}")
            return False

    print("✓ Mode, theme, and compute options work")
    return True


def verify_hot_reload():
    """Verify hot-reload capability exists"""
    print("\nVerifying hot-reload capability...")
    from core.config import load_config, reset_config

    reset_config()
    os.environ["ENV"] = "dev"
    config = load_config()

    if not hasattr(config, "reload"):
        print("✗ reload() method not found")
        return False

    # Test that reload method exists and is callable
    if not callable(config.reload):
        print("✗ reload() is not callable")
        return False

    print("✓ Hot-reload capability implemented")
    return True


def verify_validation_function():
    """Verify validate_config function works"""
    print("\nVerifying validate_config function...")
    from core.config import load_config, validate_config

    config = load_config()
    is_valid, errors = validate_config(config)

    if not isinstance(is_valid, bool):
        print("✗ validate_config should return bool")
        return False

    if not isinstance(errors, list):
        print("✗ validate_config should return list of errors")
        return False

    print("✓ validate_config function works")
    return True


def verify_file_operations():
    """Verify configuration file operations"""
    print("\nVerifying file operations...")
    from core.config import load_config

    config = load_config()

    # Test save_to_file
    if not hasattr(config, "save_to_file"):
        print("✗ save_to_file method not found")
        return False

    # Test to_dict
    if not hasattr(config, "to_dict"):
        print("✗ to_dict method not found")
        return False

    config_dict = config.to_dict()
    if not isinstance(config_dict, dict):
        print("✗ to_dict should return dictionary")
        return False

    print("✓ File operations implemented")
    return True


def verify_documentation():
    """Verify documentation files exist"""
    print("\nVerifying documentation...")

    docs = [
        "core/CONFIG_SYSTEM_GUIDE.md",
        "core/CONFIG_QUICK_REFERENCE.md",
        "TASK_1_1_IMPLEMENTATION_SUMMARY.md",
    ]

    missing_docs = []
    for doc in docs:
        if not Path(doc).exists():
            missing_docs.append(doc)

    if missing_docs:
        print(f"✗ Missing documentation: {missing_docs}")
        return False

    print("✓ All documentation files present")
    return True


def main():
    """Run all verification checks"""
    print("=" * 70)
    print(" " * 15 + "Task 1.1 Verification")
    print("=" * 70)

    checks = [
        verify_imports,
        verify_appconfig_fields,
        verify_enums,
        verify_environment_loading,
        verify_pydantic_validation,
        verify_mode_theme_compute,
        verify_hot_reload,
        verify_validation_function,
        verify_file_operations,
        verify_documentation,
    ]

    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"✗ Check failed with exception: {e}")
            import traceback

            traceback.print_exc()
            results.append(False)

    print("\n" + "=" * 70)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} checks passed")

    if passed == total:
        print("✓ Task 1.1 implementation verified successfully!")
        print("=" * 70)
        return 0
    else:
        print("✗ Some checks failed")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
