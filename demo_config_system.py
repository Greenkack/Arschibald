"""
Demo script for Enhanced Configuration System

This script demonstrates all features of the enhanced configuration system:
- Environment-specific loading (dev/stage/prod)
- Mode, theme, and compute options
- Pydantic validation
- Configuration file loading
- Hot-reload capability
- Configuration serialization
"""

import os
from pathlib import Path
from core.config import (
    AppConfig,
    load_config,
    load_config_for_environment,
    get_config,
    validate_config,
    Environment,
    Mode,
    Theme,
    ComputeMode,
)


def demo_basic_usage():
    """Demonstrate basic configuration usage"""
    print("\n" + "=" * 60)
    print("1. Basic Configuration Usage")
    print("=" * 60)

    # Load configuration from environment
    config = load_config()

    print(f"Environment: {config.env.value}")
    print(f"Debug Mode: {config.debug}")
    print(f"Application Mode: {config.mode.value}")
    print(f"Theme: {config.theme.value}")
    print(f"Compute Mode: {config.compute.value}")
    print(f"Database URL: {config.database.url}")
    print(f"Cache TTL: {config.cache.default_ttl}s")
    print(f"Job Workers: {config.jobs.max_workers}")


def demo_environment_specific():
    """Demonstrate environment-specific configuration"""
    print("\n" + "=" * 60)
    print("2. Environment-Specific Configuration")
    print("=" * 60)

    for env in [Environment.DEV, Environment.STAGE, Environment.PROD]:
        print(f"\n{env.value.upper()} Environment:")
        config = load_config_for_environment(env)
        print(f"  Debug: {config.debug}")
        print(f"  Database: {config.database.url}")
        print(f"  Cache TTL: {config.cache.default_ttl}s")
        print(f"  Workers: {config.jobs.max_workers}")


def demo_mode_options():
    """Demonstrate mode, theme, and compute options"""
    print("\n" + "=" * 60)
    print("3. Mode, Theme, and Compute Options")
    print("=" * 60)

    # Mode options
    print("\nMode Options:")
    for mode in [Mode.OFFLINE, Mode.ONLINE]:
        os.environ["MODE"] = mode.value
        config = load_config()
        print(f"  {mode.value}: {config.mode}")

    # Theme options
    print("\nTheme Options:")
    for theme in [Theme.AUTO, Theme.LIGHT, Theme.DARK]:
        os.environ["THEME"] = theme.value
        config = load_config()
        print(f"  {theme.value}: {config.theme}")

    # Compute options
    print("\nCompute Options:")
    for compute in [ComputeMode.FAST, ComputeMode.ACCURATE]:
        os.environ["COMPUTE"] = compute.value
        config = load_config()
        print(f"  {compute.value}: {config.compute}")


def demo_validation():
    """Demonstrate Pydantic validation"""
    print("\n" + "=" * 60)
    print("4. Configuration Validation")
    print("=" * 60)

    config = load_config()
    is_valid, errors = validate_config(config)

    print(f"Configuration Valid: {is_valid}")
    if errors:
        print("Validation Errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("No validation errors!")

    # Demonstrate validation constraints
    print("\nValidation Constraints:")
    print(f"  DB Pool Size: {config.database.pool_size} (1-100)")
    print(f"  Cache TTL: {config.cache.default_ttl}s (≥0)")
    print(f"  Job Workers: {config.jobs.max_workers} (1-32)")
    print(f"  BCrypt Rounds: {config.security.bcrypt_rounds} (4-31)")


def demo_file_operations():
    """Demonstrate configuration file operations"""
    print("\n" + "=" * 60)
    print("5. Configuration File Operations")
    print("=" * 60)

    config = load_config()

    # Save to file
    config_file = Path("demo_config.json")
    config.save_to_file(config_file)
    print(f"✓ Configuration saved to {config_file}")

    # Load from file
    loaded_config = load_config(config_file=config_file)
    print(f"✓ Configuration loaded from {config_file}")
    print(f"  App Name: {loaded_config.app_name}")
    print(f"  Environment: {loaded_config.env.value}")

    # Cleanup
    if config_file.exists():
        config_file.unlink()
        print(f"✓ Cleaned up {config_file}")


def demo_serialization():
    """Demonstrate configuration serialization"""
    print("\n" + "=" * 60)
    print("6. Configuration Serialization")
    print("=" * 60)

    config = load_config()
    config_dict = config.to_dict()

    print("Configuration as Dictionary:")
    for key, value in config_dict.items():
        if isinstance(value, dict):
            print(f"  {key}:")
            for sub_key, sub_value in value.items():
                print(f"    {sub_key}: {sub_value}")
        else:
            print(f"  {key}: {value}")


def demo_global_instance():
    """Demonstrate global configuration instance"""
    print("\n" + "=" * 60)
    print("7. Global Configuration Instance")
    print("=" * 60)

    # Get global instance
    config1 = get_config()
    config2 = get_config()

    print(f"Same instance: {config1 is config2}")
    print(f"App Name: {config1.app_name}")
    print(f"Environment: {config1.env.value}")

    # Hot-reload (only in development)
    if config1.is_development():
        reloaded = get_config(reload=True)
        print(f"Hot-reload attempted: {reloaded is not None}")


def demo_helper_methods():
    """Demonstrate helper methods"""
    print("\n" + "=" * 60)
    print("8. Helper Methods")
    print("=" * 60)

    config = load_config()

    print(f"Is Development: {config.is_development()}")
    print(f"Is Staging: {config.is_staging()}")
    print(f"Is Production: {config.is_production()}")
    print(f"Database URL: {config.get_database_url()}")


def main():
    """Run all demos"""
    print("\n" + "=" * 70)
    print(" " * 15 + "Enhanced Configuration System Demo")
    print("=" * 70)

    try:
        demo_basic_usage()
        demo_environment_specific()
        demo_mode_options()
        demo_validation()
        demo_file_operations()
        demo_serialization()
        demo_global_instance()
        demo_helper_methods()

        print("\n" + "=" * 70)
        print(" " * 20 + "Demo completed successfully!")
        print("=" * 70 + "\n")

    except Exception as e:
        print(f"\n✗ Demo failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
