# Enhanced Configuration System Guide

## Overview

The enhanced configuration system provides a robust, type-safe, and flexible way to manage application configuration across different environments (dev/stage/prod) with support for hot-reloading, validation, and multiple configuration sources.

## Features

### 1. Environment-Specific Loading
- **Development (dev)**: Debug enabled, DuckDB, fast cache TTL
- **Staging (stage)**: Debug disabled, PostgreSQL, moderate cache TTL
- **Production (prod)**: Debug disabled, PostgreSQL, long cache TTL

### 2. Configuration Options

#### Mode
- `offline`: Application runs without external dependencies
- `online`: Application connects to external services

#### Theme
- `auto`: Automatically detect system theme
- `light`: Force light theme
- `dark`: Force dark theme

#### Compute
- `fast`: Optimized for speed, may sacrifice accuracy
- `accurate`: Optimized for accuracy, may be slower

### 3. Pydantic Validation
All configuration values are validated using Pydantic models with:
- Type checking
- Range validation (e.g., pool_size: 1-100)
- Custom validators
- Automatic error messages

### 4. Hot-Reload Capability
In development mode, configuration can be reloaded without restarting:
```python
config = get_config(reload=True)
```

### 5. Multiple Configuration Sources
- Environment variables
- JSON configuration files
- Environment-specific config files (config.dev.json, config.stage.json, config.prod.json)

## Usage Examples

### Basic Usage

```python
from core.config import load_config, get_config

# Load configuration
config = load_config()

# Access configuration values
print(f"Environment: {config.env.value}")
print(f"Mode: {config.mode.value}")
print(f"Theme: {config.theme.value}")
print(f"Compute: {config.compute.value}")
print(f"Database URL: {config.database.url}")
```

### Environment-Specific Loading

```python
from core.config import load_config_for_environment, Environment

# Load development configuration
dev_config = load_config_for_environment(Environment.DEV)

# Load production configuration
prod_config = load_config_for_environment(Environment.PROD)
```

### Configuration from File

```python
from pathlib import Path
from core.config import load_config

# Load from specific file
config = load_config(config_file=Path("config.prod.json"))

# Or use environment-specific file (automatically detected)
# Place config.dev.json, config.stage.json, or config.prod.json in root
config = load_config()
```

### Configuration Validation

```python
from core.config import load_config, validate_config

config = load_config()
is_valid, errors = validate_config(config)

if not is_valid:
    for error in errors:
        print(f"Validation error: {error}")
```

### Global Configuration Instance

```python
from core.config import get_config

# Get global instance (singleton)
config = get_config()

# Hot-reload in development
config = get_config(reload=True)
```

### Configuration Serialization

```python
from pathlib import Path
from core.config import load_config

config = load_config()

# Convert to dictionary
config_dict = config.to_dict()

# Save to file
config.save_to_file(Path("my_config.json"))
```

## Environment Variables

### Core Settings
- `ENV`: Environment (dev/stage/prod)
- `DEBUG`: Debug mode (true/false)
- `MODE`: Application mode (offline/online)
- `THEME`: UI theme (auto/light/dark)
- `COMPUTE`: Compute mode (fast/accurate)

### Application Settings
- `APP_NAME`: Application name
- `APP_VERSION`: Application version
- `HOST`: Server host
- `PORT`: Server port

### Database Settings
- `DATABASE_URL`: Database connection URL
- `DB_POOL_SIZE`: Connection pool size (1-100)
- `DB_MAX_OVERFLOW`: Max overflow connections (0-50)
- `DB_ECHO`: Echo SQL statements (true/false)

### Cache Settings
- `REDIS_URL`: Redis connection URL
- `CACHE_TTL`: Default cache TTL in seconds
- `CACHE_MAX_ENTRIES`: Maximum cache entries

### Job Settings
- `JOB_BACKEND`: Job backend (memory/redis)
- `JOB_MAX_WORKERS`: Maximum worker threads (1-32)
- `JOB_TIMEOUT`: Job timeout in seconds

### Security Settings
- `SECRET_KEY`: Secret key for encryption (min 16 chars)
- `SESSION_TIMEOUT`: Session timeout in seconds
- `BCRYPT_ROUNDS`: BCrypt hashing rounds (4-31)

### Backup Settings
- `BACKUP_ENABLED`: Enable backup system (true/false)
- `BACKUP_PATH`: Backup storage path
- `BACKUP_RETENTION`: Backup retention in days
- `BACKUP_SCHEDULE_FULL`: Full backup cron schedule
- `BACKUP_SCHEDULE_INC`: Incremental backup cron schedule

### Performance Settings
- `RESPONSE_TIME_TARGET_MS`: Target response time in milliseconds
- `MAX_CACHE_MEMORY_MB`: Maximum cache memory in MB
- `ENABLE_PROFILING`: Enable performance profiling (true/false)
- `LAZY_LOADING`: Enable lazy loading (true/false)

### Feature Flags
- `FEATURE_AUTH`: Enable authentication
- `FEATURE_JOBS`: Enable job system
- `FEATURE_BACKUP`: Enable backup system
- `FEATURE_METRICS`: Enable metrics collection

## Configuration File Format

### JSON Configuration File

```json
{
  "env": "prod",
  "debug": false,
  "mode": "online",
  "theme": "auto",
  "compute": "accurate",
  "app_name": "My Application",
  "app_version": "1.0.0",
  "database": {
    "url": "postgresql://user:pass@localhost/app",
    "pool_size": 10,
    "max_overflow": 20,
    "echo": false
  },
  "cache": {
    "redis_url": "redis://localhost:6379",
    "default_ttl": 3600,
    "max_entries": 10000
  },
  "jobs": {
    "backend": "redis",
    "redis_url": "redis://localhost:6379",
    "max_workers": 8,
    "job_timeout": 3600
  },
  "security": {
    "secret_key": "your-secret-key-here",
    "session_timeout": 86400,
    "bcrypt_rounds": 12
  },
  "performance": {
    "response_time_target_ms": 50,
    "max_cache_memory_mb": 1024,
    "enable_profiling": false,
    "lazy_loading": true
  },
  "features": {
    "auth": true,
    "jobs": true,
    "backup": true,
    "metrics": true
  }
}
```

## Validation Rules

### Database Configuration
- URL must start with: sqlite://, duckdb://, postgresql://, or mysql://
- Pool size: 1-100
- Max overflow: 0-50

### Cache Configuration
- Default TTL: ≥0 seconds
- Max entries: ≥1

### Job Configuration
- Max workers: 1-32
- Job timeout: ≥1 second

### Security Configuration
- Secret key: minimum 16 characters
- Session timeout: ≥60 seconds
- BCrypt rounds: 4-31

### Performance Configuration
- Response time target: ≥1 millisecond
- Max cache memory: ≥1 MB

## Production Validation

When running in production (`ENV=prod`), additional validation is enforced:
- Debug mode must be disabled
- Secret key must not be the default "dev-secret-key"
- Database should use PostgreSQL, not DuckDB

## Hot-Reload

Hot-reload is only available in development mode and requires:
1. `ENV=dev`
2. Configuration file specified via `CONFIG_FILE` environment variable
3. File modification time changes

```python
# Enable hot-reload
os.environ["ENV"] = "dev"
os.environ["CONFIG_FILE"] = "config.dev.json"

config = get_config()

# Later, after modifying config.dev.json
config = get_config(reload=True)
```

## Best Practices

1. **Use Environment Variables for Secrets**: Never commit secrets to configuration files
2. **Validate Configuration on Startup**: Always validate configuration before starting the application
3. **Use Environment-Specific Files**: Create separate config files for each environment
4. **Enable Hot-Reload in Development**: Speed up development by reloading configuration without restart
5. **Set Appropriate Defaults**: Provide sensible defaults for all configuration values
6. **Document Configuration Changes**: Keep this guide updated when adding new configuration options

## Troubleshooting

### Configuration Validation Fails
- Check that all required environment variables are set
- Verify that values are within valid ranges
- Ensure secret key is set in production

### Hot-Reload Not Working
- Verify you're in development mode (`ENV=dev`)
- Check that `CONFIG_FILE` environment variable is set
- Ensure the configuration file exists and is writable

### Database Connection Fails
- Verify `DATABASE_URL` is correctly formatted
- Check that database server is running
- Ensure connection pool settings are appropriate

## API Reference

### Functions

#### `load_config(env: str | None = None, config_file: Path | None = None) -> AppConfig`
Load application configuration with optional environment and file specification.

#### `load_config_for_environment(environment: Environment) -> AppConfig`
Load configuration for specific environment with defaults.

#### `get_config(reload: bool = False) -> AppConfig`
Get global configuration instance with optional hot-reload.

#### `reset_config() -> None`
Reset global configuration instance (useful for testing).

#### `validate_config(config: AppConfig) -> tuple[bool, list[str]]`
Validate configuration and return validation results.

### Classes

#### `AppConfig`
Main application configuration dataclass with all settings.

#### `DatabaseConfig`
Database configuration with Pydantic validation.

#### `CacheConfig`
Cache configuration with Pydantic validation.

#### `JobConfig`
Job system configuration with Pydantic validation.

#### `SecurityConfig`
Security configuration with Pydantic validation.

#### `BackupConfig`
Backup configuration with Pydantic validation.

#### `PerformanceConfig`
Performance configuration with Pydantic validation.

### Enums

#### `Environment`
- `DEV`: Development environment
- `STAGE`: Staging environment
- `PROD`: Production environment

#### `Mode`
- `OFFLINE`: Offline mode
- `ONLINE`: Online mode

#### `Theme`
- `AUTO`: Auto-detect theme
- `LIGHT`: Light theme
- `DARK`: Dark theme

#### `ComputeMode`
- `FAST`: Fast computation mode
- `ACCURATE`: Accurate computation mode

## Requirements Satisfied

This implementation satisfies the following requirements from task 1.1:

✓ Create AppConfig @dataclass with env, debug, mode, theme, compute fields
✓ Implement load_config() function with environment-specific loading (dev/stage/prod)
✓ Add configuration validation with Pydantic models for type safety
✓ Support mode=offline/online, theme=auto/light/dark, compute=fast/accurate options
✓ Create configuration hot-reloading capability for development

Requirements: 1.6, 5.4, 9.1, 13.1
