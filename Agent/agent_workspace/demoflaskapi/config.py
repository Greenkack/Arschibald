"""
Configuration management
"""
import os

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Base configuration class."""

    # Environment
    ENV: str = os.getenv("ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

    # Add your configuration variables here

    @classmethod
    def get(
        cls,
        key: str,
        default: str | None = None
    ) -> str | None:
        """Get configuration value."""
        return os.getenv(key, default)


# Create config instance
config = Config()
