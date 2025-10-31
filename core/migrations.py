"""Database Migration System with Alembic"""

import os
from pathlib import Path
from typing import Any

from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect

from .config import get_config

try:
    import structlog
    logger = structlog.get_logger(__name__)
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class MigrationManager:
    """Database migration management with Alembic"""

    def __init__(self):
        self.config = get_config()
        self.alembic_config = self._setup_alembic()
        self.engine = create_engine(self.config.get_database_url())

    def _setup_alembic(self) -> Config:
        """Setup Alembic configuration"""
        # Get the migrations directory path
        migrations_dir = Path(__file__).parent / "alembic"
        migrations_dir.mkdir(exist_ok=True)

        # Create alembic.ini if it doesn't exist
        alembic_ini = Path(__file__).parent / "alembic.ini"
        if not alembic_ini.exists():
            self._create_alembic_ini(alembic_ini, migrations_dir)

        # Load Alembic config
        alembic_config = Config(str(alembic_ini))
        alembic_config.set_main_option("script_location", str(migrations_dir))
        alembic_config.set_main_option("sqlalchemy.url", self.config.get_database_url())

        # Set environment-specific options
        if self.config.is_development():
            alembic_config.set_main_option("file_template", "%%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d%%(minute).2d_%%(slug)s")
        else:
            alembic_config.set_main_option("file_template", "%%(rev)s_%%(slug)s")

        return alembic_config

    def _create_alembic_ini(self, ini_path: Path, migrations_dir: Path):
        """Create alembic.ini configuration file"""
        ini_content = f"""# Alembic Configuration File

[alembic]
# Path to migration scripts
script_location = {migrations_dir}

# Template used to generate migration file names
file_template = %%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d%%(minute).2d_%%(slug)s

# Timezone for migration timestamps
timezone = UTC

# Max length of characters to apply to the "slug" field
truncate_slug_length = 40

# Set to 'true' to run the environment during the 'revision' command
revision_environment = false

# Set to 'true' to allow .pyc and .pyo files without a source .py file
sourceless = false

# Version location specification
version_locations = %(here)s/alembic/versions

# Output encoding used when revision files are written
output_encoding = utf-8

[post_write_hooks]
# Format code with black after generation
hooks = black
black.type = console_scripts
black.entrypoint = black
black.options = -l 100

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
"""
        ini_path.write_text(ini_content)
        logger.info("Created alembic.ini", path=str(ini_path))

    def initialize_alembic(self):
        """Initialize Alembic migration environment"""
        migrations_dir = Path(__file__).parent / "alembic"

        # Create directory structure
        migrations_dir.mkdir(exist_ok=True)
        versions_dir = migrations_dir / "versions"
        versions_dir.mkdir(exist_ok=True)

        # Create env.py
        env_py = migrations_dir / "env.py"
        if not env_py.exists():
            self._create_env_py(env_py)

        # Create script.py.mako template
        script_mako = migrations_dir / "script.py.mako"
        if not script_mako.exists():
            self._create_script_template(script_mako)

        logger.info("Alembic environment initialized", directory=str(migrations_dir))

    def _create_env_py(self, env_path: Path):
        """Create Alembic env.py file"""
        env_content = '''"""Alembic Environment Configuration"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Import your models here
from core.database import Base

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add your model's MetaData object here for 'autogenerate' support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
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
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
            # Enable transaction per migration for safety
            transaction_per_migration=True,
            # Include schemas
            include_schemas=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
'''
        env_path.write_text(env_content)
        logger.info("Created env.py", path=str(env_path))

    def _create_script_template(self, template_path: Path):
        """Create migration script template"""
        template_content = '''"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    """Upgrade database schema"""
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    """Downgrade database schema"""
    ${downgrades if downgrades else "pass"}
'''
        template_path.write_text(template_content)
        logger.info("Created script.py.mako", path=str(template_path))

    def run_migrations(self, target_revision: str = "head") -> None:
        """
        Run pending migrations.

        Args:
            target_revision: Target revision to migrate to (default: "head")
        """
        try:
            logger.info("Running database migrations", target=target_revision)
            command.upgrade(self.alembic_config, target_revision)
            logger.info("Migrations completed successfully")
        except Exception as e:
            logger.error("Migration failed", error=str(e))
            raise

    def create_migration(
        self,
        message: str,
        autogenerate: bool = True,
        sql: bool = False
    ) -> str:
        """
        Create new migration.

        Args:
            message: Migration description
            autogenerate: Auto-generate migration from model changes
            sql: Generate SQL script instead of Python

        Returns:
            Path to created migration file
        """
        try:
            logger.info("Creating migration", message=message, autogenerate=autogenerate)

            if sql:
                command.revision(
                    self.alembic_config,
                    message=message,
                    autogenerate=autogenerate,
                    sql=True
                )
            else:
                revision = command.revision(
                    self.alembic_config,
                    message=message,
                    autogenerate=autogenerate
                )
                logger.info("Migration created", revision=revision)
                return revision

        except Exception as e:
            logger.error("Failed to create migration", error=str(e))
            raise

    def rollback_migration(self, target_revision: str = "-1") -> None:
        """
        Rollback to specific revision.

        Args:
            target_revision: Target revision (default: "-1" for previous)
        """
        try:
            # Safety check: confirm rollback in production
            if self.config.is_production():
                logger.warning("Attempting rollback in production", target=target_revision)

            logger.info("Rolling back migration", target=target_revision)
            command.downgrade(self.alembic_config, target_revision)
            logger.info("Rollback completed successfully")

        except Exception as e:
            logger.error("Rollback failed", error=str(e))
            raise

    def get_current_revision(self) -> str | None:
        """Get current database revision"""
        try:
            with self.engine.connect() as connection:
                context = MigrationContext.configure(connection)
                current_rev = context.get_current_revision()
                return current_rev
        except Exception as e:
            logger.error("Failed to get current revision", error=str(e))
            return None

    def get_pending_migrations(self) -> list[str]:
        """Get list of pending migrations"""
        try:
            script = ScriptDirectory.from_config(self.alembic_config)
            current_rev = self.get_current_revision()

            if current_rev is None:
                # No migrations applied yet
                return [rev.revision for rev in script.walk_revisions()]

            pending = []
            for rev in script.iterate_revisions(current_rev, "head"):
                if rev.revision != current_rev:
                    pending.append(rev.revision)

            return pending

        except Exception as e:
            logger.error("Failed to get pending migrations", error=str(e))
            return []

    def get_migration_history(self) -> list[dict[str, Any]]:
        """Get migration history"""
        try:
            script = ScriptDirectory.from_config(self.alembic_config)
            current_rev = self.get_current_revision()

            history = []
            for rev in script.walk_revisions():
                history.append({
                    "revision": rev.revision,
                    "down_revision": rev.down_revision,
                    "message": rev.doc,
                    "is_current": rev.revision == current_rev,
                })

            return history

        except Exception as e:
            logger.error("Failed to get migration history", error=str(e))
            return []

    def validate_migrations(self) -> dict[str, Any]:
        """
        Validate migration state.

        Returns:
            Dictionary with validation results
        """
        results = {
            "status": "success",
            "current_revision": None,
            "pending_migrations": [],
            "errors": [],
            "warnings": []
        }

        try:
            # Get current revision
            current_rev = self.get_current_revision()
            results["current_revision"] = current_rev

            # Get pending migrations
            pending = self.get_pending_migrations()
            results["pending_migrations"] = pending

            if pending:
                results["warnings"].append(
                    f"{len(pending)} pending migration(s) found"
                )

            # Check if database schema matches models
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()

            if not tables:
                results["warnings"].append("No tables found in database")

        except Exception as e:
            results["status"] = "error"
            results["errors"].append(str(e))

        return results

    def create_migration_template(self, template_name: str) -> Path:
        """
        Create migration template for common operations.

        Args:
            template_name: Template name (add_column, add_index, etc.)

        Returns:
            Path to template file
        """
        templates_dir = Path(__file__).parent / "alembic" / "templates"
        templates_dir.mkdir(exist_ok=True)

        templates = {
            "add_column": '''"""Add column template

Revision ID: ${revision}
"""
from alembic import op
import sqlalchemy as sa

def upgrade() -> None:
    op.add_column('table_name', sa.Column('column_name', sa.String(255), nullable=True))

def downgrade() -> None:
    op.drop_column('table_name', 'column_name')
''',
            "add_index": '''"""Add index template

Revision ID: ${revision}
"""
from alembic import op

def upgrade() -> None:
    op.create_index('idx_table_column', 'table_name', ['column_name'])

def downgrade() -> None:
    op.drop_index('idx_table_column', 'table_name')
''',
            "add_table": '''"""Add table template

Revision ID: ${revision}
"""
from alembic import op
import sqlalchemy as sa

def upgrade() -> None:
    op.create_table(
        'table_name',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now()),
    )

def downgrade() -> None:
    op.drop_table('table_name')
''',
            "add_foreign_key": '''"""Add foreign key template

Revision ID: ${revision}
"""
from alembic import op

def upgrade() -> None:
    op.create_foreign_key(
        'fk_table_ref_id',
        'table_name', 'ref_table',
        ['ref_id'], ['id']
    )

def downgrade() -> None:
    op.drop_constraint('fk_table_ref_id', 'table_name', type_='foreignkey')
''',
        }

        if template_name not in templates:
            raise ValueError(f"Unknown template: {template_name}")

        template_path = templates_dir / f"{template_name}.py.template"
        template_path.write_text(templates[template_name])

        logger.info("Created migration template", template=template_name, path=str(template_path))
        return template_path


# Global migration manager
_migration_manager: MigrationManager | None = None


def get_migration_manager() -> MigrationManager:
    """Get global migration manager"""
    global _migration_manager
    if _migration_manager is None:
        _migration_manager = MigrationManager()
    return _migration_manager


def migrate(target_revision: str = "head") -> None:
    """
    Run database migrations.

    Args:
        target_revision: Target revision to migrate to (default: "head")
    """
    manager = get_migration_manager()
    manager.run_migrations(target_revision)


def rollback(target_revision: str = "-1") -> None:
    """
    Rollback database migration.

    Args:
        target_revision: Target revision (default: "-1" for previous)
    """
    manager = get_migration_manager()
    manager.rollback_migration(target_revision)


def create_migration(message: str, autogenerate: bool = True) -> str:
    """
    Create new migration.

    Args:
        message: Migration description
        autogenerate: Auto-generate from model changes

    Returns:
        Revision ID
    """
    manager = get_migration_manager()
    return manager.create_migration(message, autogenerate)
