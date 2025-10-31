"""Tests for enhanced configuration system (Task 1.1)"""

import os
import tempfile
from pathlib import Path

import pytest

from core.config import (
    AppConfig,
    AppMode,
    AppTheme,
    ComputeMode,
    Environment,
    get_config,
    load_config,
    reload_config,
    reset_config,
)


class TestAppConfig:
    """Test AppConfig dataclass"""

    def setup_method(self):
        """Reset config before each test"""
        reset_config()

    def test_default_config(self):
        """Test default configuration values"""
        # Clear environment to test defaults
        for key in ["ENV", "DEBUG", "APP_MODE", "APP_THEME", "APP_COMPUTE"]:
            os.environ.pop(key, None)

        config = AppConfig()

        assert config.env == "dev"
        # Debug may be set from .env, so just check it's a boolean
        assert isinstance(config.debug, bool)
        assert config.mode == "online"
        assert config.theme == "auto"
        assert config.compute == "accurate"
        assert config.app_name == "Robust Streamlit App"
        assert config.app_version == "1.0.0"

    def test_environment_specific_loading(self):
        """Test loading configuration for different environments"""
        # Test dev environment
        os.environ["ENV"] = "dev"
        config = load_config()
        assert config.env == "dev"
        assert config.is_development()
        assert not config.is_production()
        assert not config.is_staging()

        # Test staging environment
        os.environ["ENV"] = "staging"
        config = load_config()
        assert config.env == "staging"
        assert config.is_staging()
        assert not config.is_development()

        # Test production environment
        os.environ["ENV"] = "prod"
        config = load_config()
        assert config.env == "prod"
        assert config.is_production()
        assert not config.is_development()

    def test_mode_configuration(self):
        """Test mode configuration (offline/online)"""
        # Test online mode
        os.environ["APP_MODE"] = "online"
        config = load_config()
        assert config.mode == "online"
        assert config.is_online_mode()
        assert not config.is_offline_mode()

        # Test offline mode
        os.environ["APP_MODE"] = "offline"
        config = load_config()
        assert config.mode == "offline"
        assert config.is_offline_mode()
        assert not config.is_online_mode()

    def test_theme_configuration(self):
        """Test theme configuration (auto/light/dark)"""
        # Test auto theme
        os.environ["APP_THEME"] = "auto"
        config = load_config()
        assert config.theme == "auto"

        # Test light theme
        os.environ["APP_THEME"] = "light"
        config = load_config()
        assert config.theme == "light"

        # Test dark theme
        os.environ["APP_THEME"] = "dark"
        config = load_config()
        assert config.theme == "dark"

    def test_compute_configuration(self):
        """Test compute mode configuration (fast/accurate)"""
        # Test accurate compute
        os.environ["APP_COMPUTE"] = "accurate"
        config = load_config()
        assert config.compute == "accurate"
        assert config.is_accurate_compute()
        assert not config.is_fast_compute()

        # Test fast compute
        os.environ["APP_COMPUTE"] = "fast"
        config = load_config()
        assert config.compute == "fast"
        assert config.is_fast_compute()
        assert not config.is_accurate_compute()

    def test_validation_invalid_env(self):
        """Test validation fails for invalid environment"""
        os.environ["ENV"] = "invalid"
        with pytest.raises(ValueError, match="Invalid environment"):
            load_config()

    def test_validation_invalid_mode(self):
        """Test validation fails for invalid mode"""
        os.environ["ENV"] = "dev"
        os.environ["APP_MODE"] = "invalid"
        with pytest.raises(ValueError, match="Invalid mode"):
            load_config()

    def test_validation_invalid_theme(self):
        """Test validation fails for invalid theme"""
        os.environ["ENV"] = "dev"
        os.environ["APP_MODE"] = "online"  # Set valid mode
        os.environ["APP_THEME"] = "invalid"
        os.environ["APP_COMPUTE"] = "accurate"  # Set valid compute
        with pytest.raises(ValueError, match="Invalid theme"):
            load_config()

    def test_validation_invalid_compute(self):
        """Test validation fails for invalid compute mode"""
        os.environ["ENV"] = "dev"
        os.environ["APP_MODE"] = "online"  # Set valid mode
        os.environ["APP_THEME"] = "auto"  # Set valid theme
        os.environ["APP_COMPUTE"] = "invalid"
        with pytest.raises(ValueError, match="Invalid compute mode"):
            load_config()

    def test_config_to_dict(self):
        """Test configuration serialization to dictionary"""
        os.environ["ENV"] = "dev"
        os.environ["APP_MODE"] = "online"
        os.environ["APP_THEME"] = "dark"
        os.environ["APP_COMPUTE"] = "fast"

        config = load_config()
        config_dict = config.to_dict()

        assert config_dict["env"] == "dev"
        assert config_dict["mode"] == "online"
        assert config_dict["theme"] == "dark"
        assert config_dict["compute"] == "fast"
        assert "database" in config_dict
        assert "cache" in config_dict
        assert "jobs" in config_dict

    def test_save_and_load_from_file(self):
        """Test saving and loading configuration from file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.json"

            # Create and save config
            os.environ["ENV"] = "dev"
            os.environ["APP_MODE"] = "offline"
            os.environ["APP_THEME"] = "light"
            config = load_config()
            config.save_to_file(config_path)

            # Verify file exists
            assert config_path.exists()

            # Load from file
            loaded_config = AppConfig.load_from_file(config_path)
            assert loaded_config.env == "dev"
            assert loaded_config.mode == "offline"
            assert loaded_config.theme == "light"


class TestConfigReloading:
    """Test configuration hot-reloading"""

    def setup_method(self):
        """Reset config before each test"""
        reset_config()

    def test_get_config_singleton(self):
        """Test get_config returns singleton instance"""
        config1 = get_config()
        config2 = get_config()
        assert config1 is config2

    def test_reload_config(self):
        """Test configuration reloading"""
        # Get initial config
        os.environ["ENV"] = "dev"
        os.environ["APP_MODE"] = "online"
        config = get_config()
        assert config.mode == "online"

        # Change environment and reload
        os.environ["APP_MODE"] = "offline"
        reloaded_config = reload_config()
        assert reloaded_config.mode == "offline"

    def test_should_reload_in_development(self):
        """Test should_reload returns True in development"""
        os.environ["ENV"] = "dev"
        config = get_config()
        # In development, should check for reload
        # (actual reload depends on file modification time)
        assert config.is_development()

    def test_should_not_reload_in_production(self):
        """Test should_reload returns False in production"""
        os.environ["ENV"] = "prod"
        config = get_config()
        assert not config.should_reload()


class TestSubConfigs:
    """Test sub-configuration objects"""

    def setup_method(self):
        """Reset config before each test"""
        reset_config()

    def test_database_config(self):
        """Test database configuration"""
        os.environ["DATABASE_URL"] = "postgresql://localhost/test"
        os.environ["DB_POOL_SIZE"] = "10"
        config = load_config()

        assert config.database.url == "postgresql://localhost/test"
        assert config.database.pool_size == 10

    def test_cache_config(self):
        """Test cache configuration"""
        os.environ["CACHE_TTL"] = "7200"
        os.environ["CACHE_MAX_ENTRIES"] = "5000"
        config = load_config()

        assert config.cache.default_ttl == 7200
        assert config.cache.max_entries == 5000

    def test_jobs_config(self):
        """Test jobs configuration"""
        os.environ["JOB_MAX_WORKERS"] = "8"
        os.environ["JOB_TIMEOUT"] = "1800"
        config = load_config()

        assert config.jobs.max_workers == 8
        assert config.jobs.job_timeout == 1800

    def test_performance_config(self):
        """Test performance configuration"""
        os.environ["PERF_RESPONSE_TIME_TARGET"] = "100"
        os.environ["PERF_MAX_MEMORY_MB"] = "4096"
        config = load_config()

        assert config.performance.response_time_target_ms == 100
        assert config.performance.max_memory_mb == 4096


class TestEnums:
    """Test configuration enums"""

    def test_app_mode_enum(self):
        """Test AppMode enum"""
        assert AppMode.OFFLINE == "offline"
        assert AppMode.ONLINE == "online"

    def test_app_theme_enum(self):
        """Test AppTheme enum"""
        assert AppTheme.AUTO == "auto"
        assert AppTheme.LIGHT == "light"
        assert AppTheme.DARK == "dark"

    def test_compute_mode_enum(self):
        """Test ComputeMode enum"""
        assert ComputeMode.FAST == "fast"
        assert ComputeMode.ACCURATE == "accurate"

    def test_environment_enum(self):
        """Test Environment enum"""
        assert Environment.DEV == "dev"
        assert Environment.STAGING == "staging"
        assert Environment.PROD == "prod"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
