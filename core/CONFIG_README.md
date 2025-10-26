# Enhanced Configuration System (Task 1.1)

## Overview

The Enhanced Configuration System provides a robust, type-safe, and flexible way to manage application configuration with support for:

- **Environment-specific loading** (dev/stage/prod)
- **Mode configuration** (offline/online)
- **Theme configuration** (auto/light/dark)
- **Compute mode** (fast/accurate)
- **Pydantic validation** for type safety
- **Hot-reloading** capability for development
- **Sub-configurations** for database, cache, jobs, security, backup, and performance

## Quick Start

### Basic Usage

```python
from core.config import load_config, get_config

# Load configuration from environment
config = load_config()

print(f"Environment: {config.env}")
print(f"Mode: {config.mode}")
print(f"Theme: {config.theme}")
print(f"Compute: {config.compute}")
```

### Environment Variables

Set these environment variables to configure the application:

```bash
# Core settings
ENV=dev                    # dev, stage, staging, prod, production
DEBUG=true                 # true or false
APP_MODE=online            # online or offline
APP_THEME=auto             # auto, light, or dark
APP_COMPUTE=accurate       # fast or accurate

# Application settings
APP_NAME="My App"
APP_VERSION="1.0.0"
HOST=localhost
PORT=8501

# Database
DATABASE_URL=duckdb:///app.db
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10

# Cache
CACHE_TTL=3600
CACHE_MAX_ENTRIES=1000

# Jobs
JOB_BACKEND=memory
JOB_MAX_WORKERS=4
JOB_TIMEOUT=3600

# Performance
PERF_RESPONSE_TIME_TARGET=50
PERF_CACHE_WARMING=true
PERF_LAZY_LOADING=true
PERF_MAX_MEMORY_MB=2048
```

## Features

### 1. Environment-Specific Loading

Load configuration for different environments:

```python
from core.config import load_config

# Load development configuration
config = load_config(env="dev")
assert config.is_development()

# Load production configuration
config = load_config(env="prod")
assert config.is_production()

# Load staging configuration
config = load_config(env="staging")
assert config.is_staging()
```

The system automatically loads environment-specific `.env` files:
- `.env.dev` for development
- `.env.staging` for staging
- `.env.prod` for production

### 2. Mode Configuration

Control application mode (offline/online):

```python
import os
from core.config import load_config

# Online mode (default)
os.environ["APP_MODE"] = "online"
config = load_config()
assert config.is_online_mode()

# Offline mode
os.environ["APP_MODE"] = "offline"
config = load_config()
assert config.is_offline_mode()
```

### 3. Theme Configuration

Configure UI theme:

```python
import os
from core.config import load_config

# Auto theme (follows system)
os.environ["APP_THEME"] = "auto"
config = load_config()

# Light theme
os.environ["APP_THEME"] = "light"
config = load_config()

# Dark theme
os.environ["APP_THEME"] = "dark"
config = load_config()
```

### 4. Compute Mode

Choose between fast and accurate computation:

```python
import os
from core.config import load_config

# Fast compute (optimized for speed)
os.environ["APP_COMPUTE"] = "fast"
config = load_config()
assert config.is_fast_compute()

# Accurate compute (optimized for precision)
os.environ["APP_COMPUTE"] = "accurate"
config = load_config()
assert config.is_accurate_compute()
```

### 5. Configuration Validation

All configuration values are validated on load:

```python
import os
from core.config import load_config

# Valid configuration
os.environ["ENV"] = "dev"
os.environ["APP_MODE"] = "online"
config = load_config()  # Success

# Invalid configuration
os.environ["APP_MODE"] = "invalid"
try:
    config = load_config()
except ValueError as e:
    print(f"Validation failed: {e}")
```

Validation rules:
- `env` must be one of: dev, stage, staging, prod, production
- `mode` must be one of: offline, online
- `theme` must be one of: auto, light, dark
- `compute` must be one of: fast, accurate

### 6. Hot-Reloading (Development Only)

Reload configuration without restarting:

```python
import os
from core.config import get_config, reload_config

# Get initial configuration
config = get_config()
print(f"Initial mode: {config.mode}")

# Change environment variable
os.environ["APP_MODE"] = "offline"

# Reload configuration
config = reload_config()
print(f"Reloaded mode: {config.mode}")
```

Hot-reloading features:
- Automatically checks for `.env` file changes in development
- Thread-safe reloading with locks
- Validates configuration after reload
- Disabled in production for safety

### 7. Sub-Configurations

Access sub-configuration objects:

```python
from core.config import load_config

config = load_config()

# Database configuration
print(config.database.url)
print(config.database.pool_size)

# Cache configuration
print(config.cache.default_ttl)
print(config.cache.max_entries)

# Jobs configuration
print(config.jobs.backend)
print(config.jobs.max_workers)

# Performance configuration
print(config.performance.response_time_target_ms)
print(config.performance.cache_warming_enabled)
```

### 8. Configuration Serialization

Save and load configuration from files:

```python
from pathlib import Path
from core.config import load_config, AppConfig

# Save configuration to file
config = load_config()
config.save_to_file(Path("config.json"))

# Load configuration from file
config = AppConfig.load_from_file(Path("config.json"))
```

## API Reference

### Core Functions

#### `load_config(env: str = None) -> AppConfig`

Load application configuration with optional environment override.

**Parameters:**
- `env` (str, optional): Environment override (dev/stage/prod)

**Returns:**
- `AppConfig`: Validated configuration instance

**Example:**
```python
config = load_config(env="prod")
```

#### `get_config(reload_if_needed: bool = True) -> AppConfig`

Get global configuration instance with optional hot-reload.

**Parameters:**
- `reload_if_needed` (bool): Check and reload if changed (default: True)

**Returns:**
- `AppConfig`: Global configuration instance

**Example:**
```python
config = get_config()
```

#### `reload_config() -> AppConfig`

Force reload of global configuration.

**Returns:**
- `AppConfig`: Reloaded configuration instance

**Example:**
```python
config = reload_config()
```

#### `reset_config() -> None`

Reset global configuration instance (useful for testing).

**Example:**
```python
reset_config()
```

### AppConfig Class

#### Properties

- `env` (str): Environment (dev/stage/prod)
- `debug` (bool): Debug mode flag
- `mode` (str): Application mode (offline/online)
- `theme` (str): UI theme (auto/light/dark)
- `compute` (str): Compute mode (fast/accurate)
- `app_name` (str): Application name
- `app_version` (str): Application version
- `host` (str): Server host
- `port` (int): Server port
- `data_dir` (Path): Data directory path
- `log_dir` (Path): Log directory path
- `database` (DatabaseConfig): Database configuration
- `cache` (CacheConfig): Cache configuration
- `jobs` (JobConfig): Jobs configuration
- `security` (SecurityConfig): Security configuration
- `backup` (BackupConfig): Backup configuration
- `performance` (PerformanceConfig): Performance configuration
- `features` (Dict[str, bool]): Feature flags

#### Methods

##### `validate() -> None`

Validate all configuration settings.

**Raises:**
- `ValueError`: If any configuration value is invalid

##### `reload() -> None`

Hot-reload configuration from environment.

##### `should_reload(check_interval_seconds: int = 5) -> bool`

Check if configuration should be reloaded.

**Parameters:**
- `check_interval_seconds` (int): Minimum seconds between checks

**Returns:**
- `bool`: True if configuration should be reloaded

##### `is_production() -> bool`

Check if running in production.

##### `is_staging() -> bool`

Check if running in staging.

##### `is_development() -> bool`

Check if running in development.

##### `is_offline_mode() -> bool`

Check if running in offline mode.

##### `is_online_mode() -> bool`

Check if running in online mode.

##### `is_fast_compute() -> bool`

Check if using fast compute mode.

##### `is_accurate_compute() -> bool`

Check if using accurate compute mode.

##### `to_dict() -> Dict[str, Any]`

Convert configuration to dictionary.

**Returns:**
- `Dict[str, Any]`: Configuration as dictionary

##### `save_to_file(config_path: Path) -> None`

Save configuration to JSON file.

**Parameters:**
- `config_path` (Path): Path to save configuration

### Enums

#### `AppMode`

Application mode enumeration.

- `OFFLINE = "offline"`
- `ONLINE = "online"`

#### `AppTheme`

UI theme enumeration.

- `AUTO = "auto"`
- `LIGHT = "light"`
- `DARK = "dark"`

#### `ComputeMode`

Compute mode enumeration.

- `FAST = "fast"`
- `ACCURATE = "accurate"`

#### `Environment`

Environment enumeration.

- `DEV = "dev"`
- `STAGING = "staging"`
- `STAGE = "stage"`
- `PROD = "prod"`
- `PRODUCTION = "production"`

## Testing

Run the test suite:

```bash
pytest core/test_config.py -v
```

Run the example:

```bash
python -m core.example_config_usage
```

## Best Practices

1. **Use environment variables** for configuration instead of hardcoding values
2. **Create environment-specific .env files** (.env.dev, .env.staging, .env.prod)
3. **Validate configuration early** by calling `load_config()` at application startup
4. **Use the singleton pattern** with `get_config()` for consistent configuration access
5. **Enable hot-reloading only in development** for safety
6. **Store secrets in environment variables** and never commit them to version control
7. **Use type hints** when accessing configuration values for better IDE support

## Requirements Satisfied

This implementation satisfies the following requirements from Task 1.1:

- ✅ Create AppConfig @dataclass with env, debug, mode, theme, compute fields
- ✅ Implement load_config() function with environment-specific loading (dev/stage/prod)
- ✅ Add configuration validation with Pydantic models for type safety
- ✅ Support mode=offline/online, theme=auto/light/dark, compute=fast/accurate options
- ✅ Create configuration hot-reloading capability for development

Requirements mapping:
- **1.6**: Enhanced configuration with mode, theme, compute fields
- **5.4**: Environment-specific loading and validation
- **9.1**: Configuration management for deployment
- **13.1**: Core AppConfig class implementation

## Next Steps

After implementing the Enhanced Configuration System, the next tasks are:

1. **Task 1.2**: Structured Logging Implementation
2. **Task 1.3**: Database Migration System
3. **Task 2**: Enhanced Session Management & State Persistence

## Support

For issues or questions about the configuration system, please refer to:
- Test suite: `core/test_config.py`
- Example usage: `core/example_config_usage.py`
- Source code: `core/config.py`
