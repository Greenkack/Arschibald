"""
Example usage of the Enhanced Configuration System (Task 1.1)

This demonstrates the key features:
1. Environment-specific loading (dev/stage/prod)
2. Mode configuration (offline/online)
3. Theme configuration (auto/light/dark)
4. Compute mode (fast/accurate)
5. Configuration validation with Pydantic
6. Hot-reloading capability for development
"""

import os

from core.config import (
    get_config,
    load_config,
    reload_config,
)


def example_basic_usage():
    """Example 1: Basic configuration loading"""
    print("=" * 60)
    print("Example 1: Basic Configuration Loading")
    print("=" * 60)

    # Load configuration (reads from environment variables)
    config = load_config()

    print(f"Environment: {config.env}")
    print(f"Debug Mode: {config.debug}")
    print(f"App Mode: {config.mode}")
    print(f"Theme: {config.theme}")
    print(f"Compute Mode: {config.compute}")
    print(f"App Name: {config.app_name}")
    print(f"App Version: {config.app_version}")
    print()


def example_environment_specific():
    """Example 2: Environment-specific configuration"""
    print("=" * 60)
    print("Example 2: Environment-Specific Configuration")
    print("=" * 60)

    # Load development configuration
    os.environ["ENV"] = "dev"
    dev_config = load_config()
    print(f"Development: {dev_config.env}")
    print(f"  - Is Development: {dev_config.is_development()}")
    print(f"  - Database URL: {dev_config.database.url}")

    # Load production configuration
    os.environ["ENV"] = "prod"
    prod_config = load_config()
    print(f"\nProduction: {prod_config.env}")
    print(f"  - Is Production: {prod_config.is_production()}")
    print(f"  - Database URL: {prod_config.get_database_url()}")
    print()


def example_mode_configuration():
    """Example 3: Mode configuration (offline/online)"""
    print("=" * 60)
    print("Example 3: Mode Configuration")
    print("=" * 60)

    # Online mode
    os.environ["APP_MODE"] = "online"
    config = load_config()
    print(f"Mode: {config.mode}")
    print(f"  - Is Online: {config.is_online_mode()}")
    print(f"  - Is Offline: {config.is_offline_mode()}")

    # Offline mode
    os.environ["APP_MODE"] = "offline"
    config = load_config()
    print(f"\nMode: {config.mode}")
    print(f"  - Is Online: {config.is_online_mode()}")
    print(f"  - Is Offline: {config.is_offline_mode()}")
    print()


def example_theme_configuration():
    """Example 4: Theme configuration (auto/light/dark)"""
    print("=" * 60)
    print("Example 4: Theme Configuration")
    print("=" * 60)

    themes = ["auto", "light", "dark"]
    for theme in themes:
        os.environ["APP_THEME"] = theme
        config = load_config()
        print(f"Theme: {config.theme}")
    print()


def example_compute_configuration():
    """Example 5: Compute mode configuration (fast/accurate)"""
    print("=" * 60)
    print("Example 5: Compute Mode Configuration")
    print("=" * 60)

    # Fast compute mode
    os.environ["APP_COMPUTE"] = "fast"
    config = load_config()
    print(f"Compute Mode: {config.compute}")
    print(f"  - Is Fast: {config.is_fast_compute()}")
    print(f"  - Is Accurate: {config.is_accurate_compute()}")

    # Accurate compute mode
    os.environ["APP_COMPUTE"] = "accurate"
    config = load_config()
    print(f"\nCompute Mode: {config.compute}")
    print(f"  - Is Fast: {config.is_fast_compute()}")
    print(f"  - Is Accurate: {config.is_accurate_compute()}")
    print()


def example_validation():
    """Example 6: Configuration validation"""
    print("=" * 60)
    print("Example 6: Configuration Validation")
    print("=" * 60)

    # Valid configuration
    os.environ["ENV"] = "dev"
    os.environ["APP_MODE"] = "online"
    os.environ["APP_THEME"] = "dark"
    os.environ["APP_COMPUTE"] = "fast"

    try:
        config = load_config()
        print("✓ Valid configuration loaded successfully")
        print(f"  - Environment: {config.env}")
        print(f"  - Mode: {config.mode}")
        print(f"  - Theme: {config.theme}")
        print(f"  - Compute: {config.compute}")
    except ValueError as e:
        print(f"✗ Validation failed: {e}")

    # Invalid configuration
    print("\nTrying invalid configuration...")
    os.environ["APP_MODE"] = "invalid_mode"

    try:
        config = load_config()
        print("✗ Should have failed validation")
    except ValueError as e:
        print(f"✓ Validation correctly failed: {e}")
    print()


def example_hot_reload():
    """Example 7: Hot-reloading configuration"""
    print("=" * 60)
    print("Example 7: Hot-Reloading Configuration")
    print("=" * 60)

    # Get initial configuration
    os.environ["ENV"] = "dev"
    os.environ["APP_MODE"] = "online"
    config = get_config()
    print(f"Initial Mode: {config.mode}")

    # Change environment variable
    os.environ["APP_MODE"] = "offline"

    # Reload configuration
    reloaded_config = reload_config()
    print(f"Reloaded Mode: {reloaded_config.mode}")
    print("✓ Configuration hot-reloaded successfully")
    print()


def example_serialization():
    """Example 8: Configuration serialization"""
    print("=" * 60)
    print("Example 8: Configuration Serialization")
    print("=" * 60)

    config = load_config()

    # Convert to dictionary
    config_dict = config.to_dict()
    print("Configuration as dictionary:")
    for key, value in config_dict.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for sub_key, sub_value in value.items():
                print(f"    {sub_key}: {sub_value}")
        else:
            print(f"  {key}: {value}")
    print()


def example_sub_configs():
    """Example 9: Sub-configuration objects"""
    print("=" * 60)
    print("Example 9: Sub-Configuration Objects")
    print("=" * 60)

    config = load_config()

    print("Database Configuration:")
    print(f"  - URL: {config.database.url}")
    print(f"  - Pool Size: {config.database.pool_size}")
    print(f"  - Max Overflow: {config.database.max_overflow}")

    print("\nCache Configuration:")
    print(f"  - Default TTL: {config.cache.default_ttl}s")
    print(f"  - Max Entries: {config.cache.max_entries}")

    print("\nJobs Configuration:")
    print(f"  - Backend: {config.jobs.backend}")
    print(f"  - Max Workers: {config.jobs.max_workers}")
    print(f"  - Timeout: {config.jobs.job_timeout}s")

    print("\nPerformance Configuration:")
    print(
        f"  - Response Time Target: "
        f"{config.performance.response_time_target_ms}ms"
    )
    print(
        f"  - Cache Warming: {config.performance.cache_warming_enabled}"
    )
    print(
        f"  - Lazy Loading: {config.performance.lazy_loading_enabled}"
    )
    print(f"  - Max Memory: {config.performance.max_memory_mb}MB")
    print()


def main():
    """Run all examples"""
    print("\n")
    print("*" * 60)
    print("Enhanced Configuration System Examples (Task 1.1)")
    print("*" * 60)
    print()

    # Set default environment for examples
    os.environ["ENV"] = "dev"
    os.environ["APP_MODE"] = "online"
    os.environ["APP_THEME"] = "auto"
    os.environ["APP_COMPUTE"] = "accurate"

    example_basic_usage()
    example_environment_specific()
    example_mode_configuration()
    example_theme_configuration()
    example_compute_configuration()
    example_validation()
    example_hot_reload()
    example_serialization()
    example_sub_configs()

    print("*" * 60)
    print("All examples completed successfully!")
    print("*" * 60)
    print()


if __name__ == "__main__":
    main()
