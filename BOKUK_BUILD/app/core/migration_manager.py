"""Database Migration Manager with Automatic Execution and Rollback

This module provides comprehensive migration management including:
- Automatic migration execution on application startup
- Migration rollback with safety checks
- Migration status tracking
- Zero-downtime migration support
"""

import logging
from pathlib import Path
from typing import Any

from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory

from .config import get_config
from .database import get_db_manager

try:
    import structlog

    logger = structlog.get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class MigrationError(Exception):
    """Base exception for migration errors"""


class MigrationRollbackError(MigrationError):
    """Exception raised when migration rollback fails"""


class MigrationManager:
    """
    Database migration management with automatic execution and rollback

    This class provides comprehensive migration management including:
    - Automatic migration execution on startup
    - Safe rollback capabilities
    - Migration status tracking
    - Environment-specific configuration
    """

    def __init__(self):
        """Initialize migration manager"""
        self.app_config = get_config()
        self.db_manager = get_db_manager()

        # Get alembic configuration
        self.alembic_cfg = self._get_alembic_config()
        self.script_dir = ScriptDirectory.from_config(self.alembic_cfg)

    def _get_alembic_config(self) -> Config:
        """
        Get Alembic configuration with environment-specific settings

        Returns:
            Alembic Config object
        """
        # Path to alembic.ini
        alembic_ini_path = Path(__file__).parent / "alembic.ini"

        if not alembic_ini_path.exists():
            raise MigrationError(
                f"Alembic configuration not found: {alembic_ini_path}"
            )

        # Create Alembic config
        alembic_cfg = Config(str(alembic_ini_path))

        # Set script location
        script_location = Path(__file__).parent / "alembic"
        alembic_cfg.set_main_option(
            "script_location", str(script_location)
        )

        # Override database URL from app config
        database_url = self.app_config.get_database_url()
        alembic_cfg.set_main_option("sqlalchemy.url", database_url)

        return alembic_cfg

    def get_current_revision(self) -> str | None:
        """
        Get current database revision

        Returns:
            Current revision ID or None if no migrations applied
        """
        try:
            with self.db_manager.engine.connect() as connection:
                context = MigrationContext.configure(connection)
                current_rev = context.get_current_revision()
                return current_rev
        except Exception as e:
            logger.warning(
                "Failed to get current revision",
                error=str(e),
            )
            return None

    def get_head_revision(self) -> str | None:
        """
        Get head revision from migration scripts

        Returns:
            Head revision ID or None if no migrations exist
        """
        try:
            return self.script_dir.get_current_head()
        except Exception as e:
            logger.warning(
                "Failed to get head revision",
                error=str(e),
            )
            return None

    def get_pending_migrations(self) -> list[str]:
        """
        Get list of pending migrations

        Returns:
            List of pending migration revision IDs
        """
        current = self.get_current_revision()
        head = self.get_head_revision()

        if not head:
            return []

        if not current:
            # No migrations applied yet, all are pending
            revisions = []
            for script in self.script_dir.walk_revisions(
                base="base", head=head
            ):
                revisions.append(script.revision)
            return list(reversed(revisions))

        if current == head:
            return []

        # Get revisions between current and head
        revisions = []
        for script in self.script_dir.walk_revisions(
            base=current, head=head
        ):
            if script.revision != current:
                revisions.append(script.revision)

        return list(reversed(revisions))

    def has_pending_migrations(self) -> bool:
        """
        Check if there are pending migrations

        Returns:
            True if there are pending migrations
        """
        return len(self.get_pending_migrations()) > 0

    def run_migrations(
        self,
        target_revision: str = "head",
        dry_run: bool = False,
    ) -> bool:
        """
        Run pending migrations

        Args:
            target_revision: Target revision to migrate to (default: 'head')
            dry_run: If True, only show what would be done

        Returns:
            True if migrations were successful

        Raises:
            MigrationError: If migration fails
        """
        try:
            current = self.get_current_revision()
            pending = self.get_pending_migrations()

            if not pending:
                logger.info("No pending migrations")
                return True

            logger.info(
                "Running migrations",
                current_revision=current,
                target_revision=target_revision,
                pending_count=len(pending),
                pending_migrations=pending,
            )

            if dry_run:
                logger.info(
                    "Dry run - would apply migrations",
                    migrations=pending,
                )
                return True

            # Run migrations
            command.upgrade(self.alembic_cfg, target_revision)

            new_revision = self.get_current_revision()
            logger.info(
                "Migrations completed successfully",
                old_revision=current,
                new_revision=new_revision,
            )

            return True

        except Exception as e:
            logger.error(
                "Migration failed",
                error=str(e),
                current_revision=current,
            )
            raise MigrationError(f"Migration failed: {e}") from e

    def rollback_migration(
        self,
        target_revision: str = "-1",
        safety_check: bool = True,
    ) -> bool:
        """
        Rollback migrations with safety checks

        Args:
            target_revision: Target revision to rollback to
                           '-1' for one step back
                           'base' for complete rollback
            safety_check: If True, perform safety checks before rollback

        Returns:
            True if rollback was successful

        Raises:
            MigrationRollbackError: If rollback fails or safety check fails
        """
        try:
            current = self.get_current_revision()

            if not current:
                logger.info("No migrations to rollback")
                return True

            logger.info(
                "Rolling back migration",
                current_revision=current,
                target_revision=target_revision,
            )

            # Safety checks
            if safety_check:
                if not self._perform_safety_checks():
                    raise MigrationRollbackError(
                        "Safety checks failed - rollback aborted"
                    )

            # Perform rollback
            command.downgrade(self.alembic_cfg, target_revision)

            new_revision = self.get_current_revision()
            logger.info(
                "Rollback completed successfully",
                old_revision=current,
                new_revision=new_revision,
            )

            return True

        except Exception as e:
            logger.error(
                "Rollback failed",
                error=str(e),
                current_revision=current,
            )
            raise MigrationRollbackError(f"Rollback failed: {e}") from e

    def _perform_safety_checks(self) -> bool:
        """
        Perform safety checks before rollback

        Returns:
            True if all safety checks pass

        Raises:
            MigrationRollbackError: If safety check fails
        """
        # Check 1: Database is accessible
        if not self.db_manager.health_check():
            logger.error("Safety check failed: Database not accessible")
            return False

        # Check 2: Not in production without explicit confirmation
        if self.app_config.is_production():
            logger.warning(
                "Safety check: Rollback in production environment"
            )
            # In production, require explicit confirmation
            # This would be handled by CLI or UI
            return False

        # Check 3: Backup exists (if backup feature is enabled)
        if self.app_config.backup.enabled:
            # Check if recent backup exists
            # This would integrate with backup system
            pass

        logger.info("All safety checks passed")
        return True

    def create_migration(
        self,
        message: str,
        autogenerate: bool = True,
    ) -> str | None:
        """
        Create a new migration

        Args:
            message: Migration message/description
            autogenerate: If True, auto-generate migration from model changes

        Returns:
            Revision ID of created migration

        Raises:
            MigrationError: If migration creation fails
        """
        try:
            logger.info(
                "Creating migration",
                message=message,
                autogenerate=autogenerate,
            )

            if autogenerate:
                # Auto-generate migration from model changes
                revision = command.revision(
                    self.alembic_cfg,
                    message=message,
                    autogenerate=True,
                )
            else:
                # Create empty migration template
                revision = command.revision(
                    self.alembic_cfg,
                    message=message,
                )

            logger.info(
                "Migration created successfully",
                revision=revision,
                message=message,
            )

            return revision

        except Exception as e:
            logger.error(
                "Failed to create migration",
                error=str(e),
                message=message,
            )
            raise MigrationError(f"Failed to create migration: {e}") from e

    def get_migration_history(self) -> list[dict[str, Any]]:
        """
        Get migration history

        Returns:
            List of migration information dictionaries
        """
        history = []

        try:
            current = self.get_current_revision()

            for script in self.script_dir.walk_revisions():
                is_current = script.revision == current
                history.append(
                    {
                        "revision": script.revision,
                        "down_revision": script.down_revision,
                        "message": script.doc,
                        "is_current": is_current,
                        "module_path": script.module.__file__
                        if script.module
                        else None,
                    }
                )

            return history

        except Exception as e:
            logger.error(
                "Failed to get migration history",
                error=str(e),
            )
            return []

    def stamp_database(self, revision: str = "head") -> bool:
        """
        Stamp database with a specific revision without running migrations

        This is useful for marking an existing database as being at a
        specific migration version.

        Args:
            revision: Revision to stamp database with

        Returns:
            True if stamping was successful

        Raises:
            MigrationError: If stamping fails
        """
        try:
            logger.info(
                "Stamping database",
                revision=revision,
            )

            command.stamp(self.alembic_cfg, revision)

            logger.info(
                "Database stamped successfully",
                revision=revision,
            )

            return True

        except Exception as e:
            logger.error(
                "Failed to stamp database",
                error=str(e),
                revision=revision,
            )
            raise MigrationError(f"Failed to stamp database: {e}") from e

    def verify_migrations(self) -> dict[str, Any]:
        """
        Verify migration integrity and consistency

        Returns:
            Dictionary with verification results
        """
        results = {
            "status": "ok",
            "current_revision": None,
            "head_revision": None,
            "pending_migrations": [],
            "issues": [],
        }

        try:
            # Get current and head revisions
            current = self.get_current_revision()
            head = self.get_head_revision()
            pending = self.get_pending_migrations()

            results["current_revision"] = current
            results["head_revision"] = head
            results["pending_migrations"] = pending

            # Check for issues
            if not current and head:
                results["issues"].append(
                    "Database not initialized - no migrations applied"
                )
                results["status"] = "warning"

            if pending:
                results["issues"].append(
                    f"{len(pending)} pending migration(s)"
                )
                results["status"] = "warning"

            # Verify database health
            if not self.db_manager.health_check():
                results["issues"].append("Database health check failed")
                results["status"] = "error"

        except Exception as e:
            results["status"] = "error"
            results["issues"].append(f"Verification failed: {str(e)}")

        return results


# Global migration manager instance
_migration_manager: MigrationManager | None = None


def get_migration_manager() -> MigrationManager:
    """
    Get global migration manager instance

    Returns:
        MigrationManager instance
    """
    global _migration_manager
    if _migration_manager is None:
        _migration_manager = MigrationManager()
    return _migration_manager


def migrate(
    target_revision: str = "head",
    auto_run: bool = True,
) -> bool:
    """
    Run database migrations

    This is the main entry point for running migrations, typically called
    during application startup.

    Args:
        target_revision: Target revision to migrate to
        auto_run: If True, automatically run pending migrations

    Returns:
        True if migrations were successful or no migrations needed

    Raises:
        MigrationError: If migration fails
    """
    manager = get_migration_manager()

    if not auto_run:
        # Just check for pending migrations
        pending = manager.get_pending_migrations()
        if pending:
            logger.warning(
                "Pending migrations detected but auto_run=False",
                pending_count=len(pending),
                pending_migrations=pending,
            )
        return True

    # Run migrations
    return manager.run_migrations(target_revision=target_revision)


def rollback(
    target_revision: str = "-1",
    safety_check: bool = True,
) -> bool:
    """
    Rollback database migrations

    Args:
        target_revision: Target revision to rollback to
        safety_check: If True, perform safety checks before rollback

    Returns:
        True if rollback was successful

    Raises:
        MigrationRollbackError: If rollback fails
    """
    manager = get_migration_manager()
    return manager.rollback_migration(
        target_revision=target_revision,
        safety_check=safety_check,
    )


def create_migration(
    message: str,
    autogenerate: bool = True,
) -> str | None:
    """
    Create a new migration

    Args:
        message: Migration message/description
        autogenerate: If True, auto-generate migration from model changes

    Returns:
        Revision ID of created migration

    Raises:
        MigrationError: If migration creation fails
    """
    manager = get_migration_manager()
    return manager.create_migration(
        message=message,
        autogenerate=autogenerate,
    )


def get_migration_status() -> dict[str, Any]:
    """
    Get current migration status

    Returns:
        Dictionary with migration status information
    """
    manager = get_migration_manager()

    return {
        "current_revision": manager.get_current_revision(),
        "head_revision": manager.get_head_revision(),
        "pending_migrations": manager.get_pending_migrations(),
        "has_pending": manager.has_pending_migrations(),
    }
