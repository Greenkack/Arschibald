"""Alembic Environment Configuration with Environment-Specific Settings"""

import sys
from logging.config import fileConfig
from pathlib import Path

# Add parent directory to path to import core modules
# This must be done before importing core modules (standard Alembic pattern)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from alembic import context  # noqa: E402
from sqlalchemy import engine_from_config, pool  # noqa: E402

from core.config import get_config  # noqa: E402
from core.database import Base  # noqa: E402

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add your model's MetaData object here for 'autogenerate' support
target_metadata = Base.metadata

# Load application configuration
app_config = get_config()


def get_url():
    """Get database URL from application configuration"""
    return app_config.get_database_url()


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine,
    though an Engine is acceptable here as well. By skipping the Engine
    creation we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the script output.
    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    In this scenario we need to create an Engine and associate a connection
    with the context.
    """
    # Override the sqlalchemy.url in the alembic config
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()

    # Configure connection pooling based on database type
    database_url = get_url()
    if "duckdb" in database_url or "sqlite" in database_url:
        # Use StaticPool for SQLite/DuckDB
        configuration["sqlalchemy.poolclass"] = pool.StaticPool
        connectable = engine_from_config(
            configuration,
            prefix="sqlalchemy.",
            poolclass=pool.StaticPool,
            connect_args={"check_same_thread": False},
        )
    else:
        # Use default pooling for PostgreSQL
        connectable = engine_from_config(
            configuration,
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,  # Use NullPool for migrations
        )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            # Enable transaction per migration for safety
            transaction_per_migration=True,
            # Include schemas if needed
            # include_schemas=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
