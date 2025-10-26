"""App Configuration Management"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not available, use environment variables directly
    pass


@dataclass
class DatabaseConfig:
    """Database configuration"""
    url: str = field(
        default_factory=lambda: os.getenv(
            "DATABASE_URL",
            "duckdb:///app.db"))
    pool_size: int = field(
        default_factory=lambda: int(
            os.getenv(
                "DB_POOL_SIZE",
                "5")))
    max_overflow: int = field(
        default_factory=lambda: int(
            os.getenv(
                "DB_MAX_OVERFLOW",
                "10")))
    echo: bool = field(
        default_factory=lambda: os.getenv(
            "DB_ECHO",
            "false").lower() == "true")


@dataclass
class CacheConfig:
    """Cache configuration"""
    redis_url: str | None = field(
        default_factory=lambda: os.getenv("REDIS_URL"))
    default_ttl: int = field(
        default_factory=lambda: int(
            os.getenv(
                "CACHE_TTL",
                "3600")))
    max_entries: int = field(
        default_factory=lambda: int(
            os.getenv(
                "CACHE_MAX_ENTRIES",
                "1000")))


@dataclass
class JobConfig:
    """Job system configuration"""
    backend: str = field(
        default_factory=lambda: os.getenv(
            "JOB_BACKEND", "memory"))
    redis_url: str | None = field(
        default_factory=lambda: os.getenv("REDIS_URL"))
    max_workers: int = field(
        default_factory=lambda: int(
            os.getenv(
                "JOB_MAX_WORKERS",
                "4")))
    job_timeout: int = field(
        default_factory=lambda: int(
            os.getenv(
                "JOB_TIMEOUT",
                "3600")))


@dataclass
class SecurityConfig:
    """Security configuration"""
    secret_key: str = field(
        default_factory=lambda: os.getenv(
            "SECRET_KEY", "dev-secret-key"))
    session_timeout: int = field(
        default_factory=lambda: int(
            os.getenv(
                "SESSION_TIMEOUT",
                "86400")))
    bcrypt_rounds: int = field(
        default_factory=lambda: int(
            os.getenv(
                "BCRYPT_ROUNDS",
                "12")))

    def __post_init__(self):
        if self.secret_key == "dev-secret-key" and os.getenv("ENV") == "prod":
            raise ValueError("SECRET_KEY must be set in production")


@dataclass
class BackupConfig:
    """Backup configuration"""
    enabled: bool = field(
        default_factory=lambda: os.getenv(
            "BACKUP_ENABLED",
            "true").lower() == "true")
    storage_path: Path = field(
        default_factory=lambda: Path(
            os.getenv(
                "BACKUP_PATH",
                "./backups")))
    retention_days: int = field(
        default_factory=lambda: int(
            os.getenv(
                "BACKUP_RETENTION",
                "30")))
    schedule_full: str = field(
        default_factory=lambda: os.getenv(
            "BACKUP_SCHEDULE_FULL", "0 2 * * *"))
    schedule_incremental: str = field(
        default_factory=lambda: os.getenv(
            "BACKUP_SCHEDULE_INC", "0 */1 * * *"))


@dataclass
class AppConfig:
    """Main application configuration"""

    # Environment
    env: str = field(default_factory=lambda: os.getenv("ENV", "dev"))
    debug: bool = field(
        default_factory=lambda: os.getenv(
            "DEBUG", "false").lower() == "true")

    # App Settings
    app_name: str = field(
        default_factory=lambda: os.getenv(
            "APP_NAME", "Robust Streamlit App"))
    app_version: str = field(
        default_factory=lambda: os.getenv(
            "APP_VERSION", "1.0.0"))

    # Server
    host: str = field(default_factory=lambda: os.getenv("HOST", "localhost"))
    port: int = field(default_factory=lambda: int(os.getenv("PORT", "8501")))

    # Paths
    data_dir: Path = field(
        default_factory=lambda: Path(
            os.getenv(
                "DATA_DIR",
                "./data")))
    log_dir: Path = field(
        default_factory=lambda: Path(
            os.getenv(
                "LOG_DIR",
                "./logs")))

    # Sub-configs
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    jobs: JobConfig = field(default_factory=JobConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    backup: BackupConfig = field(default_factory=BackupConfig)

    # Features
    features: dict[str, bool] = field(default_factory=lambda: {
        "auth": os.getenv("FEATURE_AUTH", "true").lower() == "true",
        "jobs": os.getenv("FEATURE_JOBS", "true").lower() == "true",
        "backup": os.getenv("FEATURE_BACKUP", "true").lower() == "true",
        "metrics": os.getenv("FEATURE_METRICS", "true").lower() == "true",
    })

    def __post_init__(self):
        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        if self.backup.enabled:
            self.backup.storage_path.mkdir(parents=True, exist_ok=True)

    @classmethod
    def load(cls) -> "AppConfig":
        """Load configuration from environment"""
        return cls()

    def is_production(self) -> bool:
        """Check if running in production"""
        return self.env == "prod"

    def is_development(self) -> bool:
        """Check if running in development"""
        return self.env == "dev"

    def get_database_url(self) -> str:
        """Get database URL with environment-specific defaults"""
        if self.is_production() and "duckdb" in self.database.url:
            # In production, prefer PostgreSQL
            return os.getenv("DATABASE_URL",
                             "postgresql://user:pass@localhost/app")
        return self.database.url

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "env": self.env,
            "debug": self.debug,
            "app_name": self.app_name,
            "app_version": self.app_version,
            "features": self.features,
        }


def load_config() -> AppConfig:
    """Load application configuration"""
    return AppConfig.load()


# Global config instance
_config: AppConfig | None = None


def get_config() -> AppConfig:
    """Get global configuration instance"""
    global _config
    if _config is None:
        _config = load_config()
    return _config
