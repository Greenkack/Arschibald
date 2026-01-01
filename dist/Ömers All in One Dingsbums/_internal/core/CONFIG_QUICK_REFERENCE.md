# Configuration System Quick Reference

## Quick Start

```python
from core.config import load_config, get_config

# Load configuration
config = load_config()

# Or use global instance
config = get_config()
```

## Environment Variables

### Essential
```bash
ENV=dev|stage|prod          # Environment
DEBUG=true|false            # Debug mode
MODE=offline|online         # Application mode
THEME=auto|light|dark       # UI theme
COMPUTE=fast|accurate       # Compute mode
```

### Database
```bash
DATABASE_URL=duckdb:///app.db
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10
```

### Cache
```bash
REDIS_URL=redis://localhost:6379
CACHE_TTL=3600
CACHE_MAX_ENTRIES=1000
```

### Jobs
```bash
JOB_BACKEND=memory|redis
JOB_MAX_WORKERS=4
JOB_TIMEOUT=3600
```

### Security
```bash
SECRET_KEY=your-secret-key
SESSION_TIMEOUT=86400
BCRYPT_ROUNDS=12
```

## Common Patterns

### Load for Specific Environment
```python
from core.config import load_config_for_environment, Environment

config = load_config_for_environment(Environment.PROD)
```

### Load from File
```python
from pathlib import Path
from core.config import load_config

config = load_config(config_file=Path("config.prod.json"))
```

### Validate Configuration
```python
from core.config import validate_config

is_valid, errors = validate_config(config)
```

### Hot-Reload (Dev Only)
```python
from core.config import get_config

config = get_config(reload=True)
```

### Save Configuration
```python
config.save_to_file(Path("my_config.json"))
```

## Configuration Access

```python
# Environment
config.env.value              # "dev", "stage", "prod"
config.debug                  # True/False
config.mode.value             # "offline", "online"
config.theme.value            # "auto", "light", "dark"
config.compute.value          # "fast", "accurate"

# Database
config.database.url
config.database.pool_size
config.database.max_overflow

# Cache
config.cache.redis_url
config.cache.default_ttl
config.cache.max_entries

# Jobs
config.jobs.backend
config.jobs.max_workers
config.jobs.job_timeout

# Security
config.security.secret_key
config.security.session_timeout
config.security.bcrypt_rounds

# Performance
config.performance.response_time_target_ms
config.performance.max_cache_memory_mb
config.performance.enable_profiling

# Features
config.features["auth"]
config.features["jobs"]
config.features["backup"]
```

## Helper Methods

```python
config.is_development()       # True if ENV=dev
config.is_staging()           # True if ENV=stage
config.is_production()        # True if ENV=prod
config.get_database_url()     # Get environment-specific DB URL
config.to_dict()              # Convert to dictionary
```

## Validation Ranges

- `DB_POOL_SIZE`: 1-100
- `DB_MAX_OVERFLOW`: 0-50
- `JOB_MAX_WORKERS`: 1-32
- `BCRYPT_ROUNDS`: 4-31
- `CACHE_TTL`: ≥0
- `SESSION_TIMEOUT`: ≥60
- `SECRET_KEY`: ≥16 characters

## Production Checklist

- [ ] Set `ENV=prod`
- [ ] Set `DEBUG=false`
- [ ] Set unique `SECRET_KEY` (not "dev-secret-key")
- [ ] Use PostgreSQL for `DATABASE_URL`
- [ ] Configure Redis for caching and jobs
- [ ] Set appropriate worker counts
- [ ] Enable backup system
- [ ] Configure monitoring

## Troubleshooting

### Configuration not loading
- Check environment variables are set
- Verify .env file exists and is loaded
- Check file permissions for config files

### Validation errors
- Verify values are within valid ranges
- Check secret key is set in production
- Ensure database URL format is correct

### Hot-reload not working
- Confirm `ENV=dev`
- Set `CONFIG_FILE` environment variable
- Ensure config file exists and is writable
