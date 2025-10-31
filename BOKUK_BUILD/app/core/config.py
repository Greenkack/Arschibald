"""App Configuration Management"""

import json
import os
import threading
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # dotenv not available, use environment variables directly
    pass

try:
    from pydantic import (
        BaseModel,
        ValidationError,
        validator,
    )
    from pydantic import (
        Field as PydanticField,
    )

    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    BaseModel = object

    def PydanticField(*args, **kwargs):
        return None

    def validator(*args, **kwargs):
        def decorator(f):
            return f

        return decorator

    ValidationError = Exception


# Enums for configuration options
class AppMode(str, Enum):
    """Application mode"""

    OFFLINE = "offline"
    ONLINE = "online"


class AppTheme(str, Enum):
    """Application theme"""

    AUTO = "auto"
    LIGHT = "light"
    DARK = "dark"


class ComputeMode(str, Enum):
    """Computation mode"""

    FAST = "fast"
    ACCURATE = "accurate"


class Environment(str, Enum):
    """Environment type"""

    DEV = "dev"
    STAGING = "staging"
    STAGE = "stage"
    PROD = "prod"
    PRODUCTION = "production"


def _get_database_url():
    return os.getenv("DATABASE_URL", "duckdb:///app.db")


def _get_db_pool_size():
    return int(os.getenv("DB_POOL_SIZE", "5"))


def _get_db_max_overflow():
    return int(os.getenv("DB_MAX_OVERFLOW", "10"))


def _get_db_echo():
    return os.getenv("DB_ECHO", "false").lower() == "true"


@dataclass
class DatabaseConfig:
    """Database configuration"""

    url: str = field(default_factory=_get_database_url)
    pool_size: int = field(default_factory=_get_db_pool_size)
    max_overflow: int = field(default_factory=_get_db_max_overflow)
    echo: bool = field(default_factory=_get_db_echo)

    def validate(self) -> None:
        """Validate database configuration"""
        if self.pool_size < 1:
            raise ValueError("DB_POOL_SIZE must be at least 1")
        if self.max_overflow < 0:
            raise ValueError("DB_MAX_OVERFLOW must be non-negative")
        if not self.url:
            raise ValueError("DATABASE_URL is required")


def _get_redis_url():
    return os.getenv("REDIS_URL")


def _get_cache_ttl():
    return int(os.getenv("CACHE_TTL", "3600"))


def _get_cache_max_entries():
    return int(os.getenv("CACHE_MAX_ENTRIES", "1000"))


@dataclass
class CacheConfig:
    """Cache configuration"""

    redis_url: str | None = field(default_factory=_get_redis_url)
    default_ttl: int = field(default_factory=_get_cache_ttl)
    max_entries: int = field(default_factory=_get_cache_max_entries)

    def validate(self) -> None:
        """Validate cache configuration"""
        if self.default_ttl < 0:
            raise ValueError("CACHE_TTL must be non-negative")
        if self.max_entries < 1:
            raise ValueError("CACHE_MAX_ENTRIES must be at least 1")


def _get_job_backend():
    return os.getenv("JOB_BACKEND", "memory")


def _get_job_max_workers():
    return int(os.getenv("JOB_MAX_WORKERS", "4"))


def _get_job_timeout():
    return int(os.getenv("JOB_TIMEOUT", "3600"))


@dataclass
class JobConfig:
    """Job system configuration"""

    backend: str = field(default_factory=_get_job_backend)
    redis_url: str | None = field(default_factory=_get_redis_url)
    max_workers: int = field(default_factory=_get_job_max_workers)
    job_timeout: int = field(default_factory=_get_job_timeout)

    def validate(self) -> None:
        """Validate job configuration"""
        if self.max_workers < 1:
            raise ValueError("JOB_MAX_WORKERS must be at least 1")
        if self.job_timeout < 1:
            raise ValueError("JOB_TIMEOUT must be at least 1")
        if self.backend not in ["memory", "redis", "rq"]:
            raise ValueError(f"Invalid JOB_BACKEND: {self.backend}")


def _get_secret_key():
    return os.getenv("SECRET_KEY", "dev-secret-key")


def _get_session_timeout():
    return int(os.getenv("SESSION_TIMEOUT", "86400"))


def _get_bcrypt_rounds():
    return int(os.getenv("BCRYPT_ROUNDS", "12"))


@dataclass
class SecurityConfig:
    """Security configuration"""

    secret_key: str = field(default_factory=_get_secret_key)
    session_timeout: int = field(default_factory=_get_session_timeout)
    bcrypt_rounds: int = field(default_factory=_get_bcrypt_rounds)

    def __post_init__(self):
        if self.secret_key == "dev-secret-key" and os.getenv("ENV") == "prod":
            raise ValueError("SECRET_KEY must be set in production")


def _get_backup_enabled():
    return os.getenv("BACKUP_ENABLED", "true").lower() == "true"


def _get_backup_path():
    return Path(os.getenv("BACKUP_PATH", "./backups"))


def _get_backup_retention():
    return int(os.getenv("BACKUP_RETENTION", "30"))


def _get_backup_schedule_full():
    return os.getenv("BACKUP_SCHEDULE_FULL", "0 2 * * *")


def _get_backup_schedule_inc():
    return os.getenv("BACKUP_SCHEDULE_INC", "0 */1 * * *")


@dataclass
class BackupConfig:
    """Backup configuration"""

    enabled: bool = field(default_factory=_get_backup_enabled)
    storage_path: Path = field(default_factory=_get_backup_path)
    retention_days: int = field(default_factory=_get_backup_retention)
    schedule_full: str = field(default_factory=_get_backup_schedule_full)
    schedule_incremental: str = field(default_factory=_get_backup_schedule_inc)


def _get_perf_response_time():
    return int(os.getenv("PERF_RESPONSE_TIME_TARGET", "50"))


def _get_perf_cache_warming():
    return os.getenv("PERF_CACHE_WARMING", "true").lower() == "true"


def _get_perf_lazy_loading():
    return os.getenv("PERF_LAZY_LOADING", "true").lower() == "true"


def _get_perf_max_memory():
    return int(os.getenv("PERF_MAX_MEMORY_MB", "2048"))


@dataclass
class PerformanceConfig:
    """Performance configuration"""

    response_time_target_ms: int = field(
        default_factory=_get_perf_response_time
    )
    cache_warming_enabled: bool = field(
        default_factory=_get_perf_cache_warming
    )
    lazy_loading_enabled: bool = field(default_factory=_get_perf_lazy_loading)
    max_memory_mb: int = field(default_factory=_get_perf_max_memory)

    def validate(self) -> None:
        """Validate performance configuration"""
        if self.response_time_target_ms < 1:
            raise ValueError("Response time target must be at least 1ms")
        if self.max_memory_mb < 128:
            raise ValueError("Max memory must be at least 128MB")


def _get_env():
    return os.getenv("ENV", "dev")


def _get_debug():
    return os.getenv("DEBUG", "false").lower() == "true"


def _get_app_mode():
    return os.getenv("APP_MODE", "online")


def _get_app_theme():
    return os.getenv("APP_THEME", "auto")


def _get_app_compute():
    return os.getenv("APP_COMPUTE", "accurate")


def _get_app_name():
    return os.getenv("APP_NAME", "Robust Streamlit App")


def _get_app_version():
    return os.getenv("APP_VERSION", "1.0.0")


def _get_host():
    return os.getenv("HOST", "localhost")


def _get_port():
    return int(os.getenv("PORT", "8501"))


def _get_data_dir():
    return Path(os.getenv("DATA_DIR", "./data"))


def _get_log_dir():
    return Path(os.getenv("LOG_DIR", "./logs"))


def _get_config_file_path():
    return Path(".env")


def _get_reload_lock():
    return threading.Lock()


@dataclass
class AppConfig:
    """Main application configuration with enhanced features"""

    # Environment
    env: str = field(default_factory=_get_env)
    debug: bool = field(default_factory=_get_debug)

    # Enhanced configuration fields (Task 1.1)
    mode: str = field(default_factory=_get_app_mode)
    theme: str = field(default_factory=_get_app_theme)
    compute: str = field(default_factory=_get_app_compute)

    # App Settings
    app_name: str = field(default_factory=_get_app_name)
    app_version: str = field(default_factory=_get_app_version)

    # Server
    host: str = field(default_factory=_get_host)
    port: int = field(default_factory=_get_port)

    # Paths
    data_dir: Path = field(default_factory=_get_data_dir)
    log_dir: Path = field(default_factory=_get_log_dir)

    # Sub-configs
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    jobs: JobConfig = field(default_factory=JobConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    backup: BackupConfig = field(default_factory=BackupConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)

    # Features
    features: dict[str, bool] = field(default_factory=dict)

    # Hot-reload tracking
    _config_file_path: Path = field(
        default_factory=_get_config_file_path, init=False, repr=False
    )
    _last_reload: datetime = field(
        default_factory=datetime.now, init=False, repr=False
    )
    _reload_lock: threading.Lock = field(
        default_factory=_get_reload_lock, init=False, repr=False
    )

    def __post_init__(self):
        """Initialize configuration and validate settings"""
        # Set default features if not provided
        if not self.features:
            self.features = {
                "auth": os.getenv("FEATURE_AUTH", "true").lower() == "true",
                "jobs": os.getenv("FEATURE_JOBS", "true").lower() == "true",
                "backup": os.getenv("FEATURE_BACKUP", "true").lower()
                == "true",
                "metrics": os.getenv("FEATURE_METRICS", "true").lower()
                == "true",
            }

        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        if self.backup.enabled:
            self.backup.storage_path.mkdir(parents=True, exist_ok=True)

        # Validate configuration
        self.validate()

    def validate(self) -> None:
        """Validate all configuration settings"""
        # Validate environment
        valid_envs = {"dev", "stage", "staging", "prod", "production"}
        if self.env not in valid_envs:
            raise ValueError(
                f"Invalid environment: {self.env}. "
                f"Must be one of {valid_envs}"
            )

        # Validate mode
        valid_modes = {"offline", "online"}
        if self.mode not in valid_modes:
            raise ValueError(
                f"Invalid mode: {self.mode}. " f"Must be one of {valid_modes}"
            )

        # Validate theme
        valid_themes = {"auto", "light", "dark"}
        if self.theme not in valid_themes:
            raise ValueError(
                f"Invalid theme: {self.theme}. "
                f"Must be one of {valid_themes}"
            )

        # Validate compute mode
        valid_compute = {"fast", "accurate"}
        if self.compute not in valid_compute:
            raise ValueError(
                f"Invalid compute mode: {self.compute}. "
                f"Must be one of {valid_compute}"
            )

        # Validate sub-configs
        self.database.validate()
        self.cache.validate()
        self.jobs.validate()
        self.performance.validate()

    @classmethod
    def load(cls, env: str = None) -> "AppConfig":
        """
        Load configuration from environment with environment-specific loading

        Args:
            env: Optional environment override (dev/stage/prod)

        Returns:
            AppConfig instance
        """
        # Override environment if specified
        if env:
            os.environ["ENV"] = env

        # Load environment-specific .env file if it exists
        current_env = os.getenv("ENV", "dev")
        env_file = Path(f".env.{current_env}")
        if env_file.exists():
            try:
                from dotenv import load_dotenv

                load_dotenv(env_file, override=True)
            except ImportError:
                pass

        return cls()

    @classmethod
    def load_from_file(cls, config_path: Path) -> "AppConfig":
        """
        Load configuration from a JSON file

        Args:
            config_path: Path to configuration JSON file

        Returns:
            AppConfig instance
        """
        if not config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {config_path}"
            )

        with open(config_path) as f:
            config_data = json.load(f)

        # Set environment variables from config file
        for key, value in config_data.items():
            if isinstance(value, dict):
                # Handle nested configs
                for nested_key, nested_value in value.items():
                    env_key = f"{key.upper()}_{nested_key.upper()}"
                    os.environ[env_key] = str(nested_value)
            else:
                os.environ[key.upper()] = str(value)

        return cls()

    def reload(self) -> None:
        """
        Hot-reload configuration from environment

        This method reloads configuration values from environment variables
        without restarting the application. Useful for development.
        """
        with self._reload_lock:
            # Reload .env file
            try:
                from dotenv import load_dotenv

                load_dotenv(override=True)

                # Load environment-specific file
                env_file = Path(f".env.{self.env}")
                if env_file.exists():
                    load_dotenv(env_file, override=True)
            except ImportError:
                pass

            # Reload configuration values
            self.env = os.getenv("ENV", self.env)
            self.debug = os.getenv("DEBUG", str(self.debug)).lower() == "true"
            self.mode = os.getenv("APP_MODE", self.mode)
            self.theme = os.getenv("APP_THEME", self.theme)
            self.compute = os.getenv("APP_COMPUTE", self.compute)

            # Reload sub-configs
            self.database = DatabaseConfig()
            self.cache = CacheConfig()
            self.jobs = JobConfig()
            self.security = SecurityConfig()
            self.backup = BackupConfig()
            self.performance = PerformanceConfig()

            # Update last reload timestamp
            self._last_reload = datetime.now()

            # Validate reloaded configuration
            self.validate()

    def should_reload(self, check_interval_seconds: int = 5) -> bool:
        """
        Check if configuration should be reloaded

        Args:
            check_interval_seconds: Minimum seconds between reload checks

        Returns:
            True if configuration should be reloaded
        """
        if not self.is_development():
            return False

        time_since_reload = (
            datetime.now() - self._last_reload
        ).total_seconds()
        if time_since_reload < check_interval_seconds:
            return False

        # Check if .env file has been modified
        if self._config_file_path.exists():
            file_mtime = datetime.fromtimestamp(
                self._config_file_path.stat().st_mtime
            )
            return file_mtime > self._last_reload

        return False

    def is_production(self) -> bool:
        """Check if running in production"""
        return self.env in {"prod", "production"}

    def is_staging(self) -> bool:
        """Check if running in staging"""
        return self.env in {"stage", "staging"}

    def is_development(self) -> bool:
        """Check if running in development"""
        return self.env == "dev"

    def is_offline_mode(self) -> bool:
        """Check if running in offline mode"""
        return self.mode == "offline"

    def is_online_mode(self) -> bool:
        """Check if running in online mode"""
        return self.mode == "online"

    def is_fast_compute(self) -> bool:
        """Check if using fast compute mode"""
        return self.compute == "fast"

    def is_accurate_compute(self) -> bool:
        """Check if using accurate compute mode"""
        return self.compute == "accurate"

    def get_database_url(self) -> str:
        """Get database URL with environment-specific defaults"""
        if self.is_production() and "duckdb" in self.database.url:
            # In production, prefer PostgreSQL
            default_url = "postgresql://user:pass@localhost/app"
            return os.getenv("DATABASE_URL", default_url)
        return self.database.url

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "env": self.env,
            "debug": self.debug,
            "mode": self.mode,
            "theme": self.theme,
            "compute": self.compute,
            "app_name": self.app_name,
            "app_version": self.app_version,
            "features": self.features,
            "database": {
                "url": self.database.url,
                "pool_size": self.database.pool_size,
            },
            "cache": {
                "default_ttl": self.cache.default_ttl,
                "max_entries": self.cache.max_entries,
            },
            "jobs": {
                "backend": self.jobs.backend,
                "max_workers": self.jobs.max_workers,
            },
            "performance": {
                "response_time_target_ms": (
                    self.performance.response_time_target_ms
                ),
                "cache_warming_enabled": (
                    self.performance.cache_warming_enabled
                ),
            },
        }

    def save_to_file(self, config_path: Path) -> None:
        """
        Save configuration to a JSON file

        Args:
            config_path: Path to save configuration
        """
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)


def load_config(env: str = None) -> AppConfig:
    """
    Load application configuration with environment-specific loading

    Args:
        env: Optional environment override (dev/stage/prod)

    Returns:
        AppConfig instance with validated settings
    """
    return AppConfig.load(env=env)


# Global config instance
_config: AppConfig | None = None
_config_lock = threading.Lock()


def get_config(reload_if_needed: bool = True) -> AppConfig:
    """
    Get global configuration instance with optional hot-reload

    Args:
        reload_if_needed: If True, check and reload config if changed

    Returns:
        Global AppConfig instance
    """
    global _config

    with _config_lock:
        if _config is None:
            _config = load_config()
        elif reload_if_needed and _config.should_reload():
            _config.reload()

    return _config


def reload_config() -> AppConfig:
    """
    Force reload of global configuration

    Returns:
        Reloaded AppConfig instance
    """
    global _config

    with _config_lock:
        if _config is not None:
            _config.reload()
        else:
            _config = load_config()

    return _config


def reset_config() -> None:
    """Reset global configuration instance (useful for testing)"""
    global _config
    with _config_lock:
        _config = None


# Pydantic validation models (if Pydantic is available)
if PYDANTIC_AVAILABLE:

    class AppConfigValidator(BaseModel):
        """Pydantic model for AppConfig validation"""

        env: str = PydanticField(
            ..., pattern="^(dev|stage|staging|prod|production)$"
        )
        debug: bool = PydanticField(default=False)
        mode: str = PydanticField(..., pattern="^(offline|online)$")
        theme: str = PydanticField(..., pattern="^(auto|light|dark)$")
        compute: str = PydanticField(..., pattern="^(fast|accurate)$")
        app_name: str = PydanticField(..., min_length=1)
        app_version: str = PydanticField(..., pattern=r"^\d+\.\d+\.\d+$")

        class Config:
            extra = "allow"

        @validator("env")
        def validate_env(cls, v):
            """Validate environment value"""
            valid = {"dev", "stage", "staging", "prod", "production"}
            if v not in valid:
                msg = f"env must be one of {valid}"
                raise ValueError(msg)
            return v

        @validator("mode")
        def validate_mode(cls, v):
            """Validate mode value"""
            valid = {"offline", "online"}
            if v not in valid:
                msg = f"mode must be one of {valid}"
                raise ValueError(msg)
            return v

        @validator("theme")
        def validate_theme(cls, v):
            """Validate theme value"""
            valid = {"auto", "light", "dark"}
            if v not in valid:
                msg = f"theme must be one of {valid}"
                raise ValueError(msg)
            return v

        @validator("compute")
        def validate_compute(cls, v):
            """Validate compute value"""
            valid = {"fast", "accurate"}
            if v not in valid:
                msg = f"compute must be one of {valid}"
                raise ValueError(msg)
            return v

    def validate_config_with_pydantic(config: AppConfig) -> None:
        """
        Validate AppConfig using Pydantic models

        Args:
            config: AppConfig instance to validate

        Raises:
            ValidationError: If configuration is invalid
        """
        config_dict = config.to_dict()
        AppConfigValidator(**config_dict)

else:

    def validate_config_with_pydantic(config: AppConfig) -> None:
        """Pydantic not available, skip validation"""
