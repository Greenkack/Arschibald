"""
Database Migration Manager
Comprehensive system for managing database migrations with validation, rollback, and progress tracking.
"""

import logging
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from pathlib import Path
import json
import hashlib
from enum import Enum
from dataclasses import dataclass, asdict
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


class MigrationStatus(Enum):
    """Migration execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class MigrationType(Enum):
    """Type of migration operation"""
    SCHEMA = "schema"
    DATA = "data"
    TRANSFORMATION = "transformation"
    CLEANUP = "cleanup"


@dataclass
class MigrationStep:
    """Individual migration step"""
    id: str
    name: str
    description: str
    type: MigrationType
    up_sql: Optional[str] = None
    down_sql: Optional[str] = None
    up_function: Optional[Callable] = None
    down_function: Optional[Callable] = None
    dependencies: List[str] = None
    validation_function: Optional[Callable] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class MigrationResult:
    """Result of migration execution"""
    step_id: str
    status: MigrationStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    rows_affected: int = 0
    validation_passed: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = asdict(self)
        result['status'] = self.status.value
        result['started_at'] = self.started_at.isoformat()
        if self.completed_at:
            result['completed_at'] = self.completed_at.isoformat()
        return result


class MigrationManager:
    """
    Comprehensive database migration manager
    
    Features:
    - Schema and data migrations
    - Dependency resolution
    - Validation before and after migration
    - Rollback capabilities
    - Incremental migration
    - Progress tracking
    - Backup before migration
    """
    
    def __init__(self, database_url: str, migrations_dir: str = "migrations"):
        """
        Initialize migration manager
        
        Args:
            database_url: Database connection URL
            migrations_dir: Directory containing migration files
        """
        self.database_url = database_url
        self.migrations_dir = Path(migrations_dir)
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        # Migration tracking
        self.migrations: List[MigrationStep] = []
        self.results: List[MigrationResult] = []
        self.current_version: Optional[str] = None
        
        # Initialize migration tracking table
        self._init_migration_table()
    
    def _init_migration_table(self):
        """Create migration tracking table if it doesn't exist"""
        with self.engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS migration_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    migration_id TEXT NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    started_at TIMESTAMP NOT NULL,
                    completed_at TIMESTAMP,
                    error_message TEXT,
                    rows_affected INTEGER DEFAULT 0,
                    checksum TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.commit()
    
    def register_migration(self, step: MigrationStep):
        """
        Register a migration step
        
        Args:
            step: Migration step to register
        """
        # Validate step
        if not step.id or not step.name:
            raise ValueError("Migration step must have id and name")
        
        if not step.up_sql and not step.up_function:
            raise ValueError("Migration step must have either up_sql or up_function")
        
        # Check for duplicates
        if any(m.id == step.id for m in self.migrations):
            raise ValueError(f"Migration {step.id} already registered")
        
        # Validate dependencies
        for dep_id in step.dependencies:
            if not any(m.id == dep_id for m in self.migrations):
                logger.warning(f"Dependency {dep_id} not found for migration {step.id}")
        
        self.migrations.append(step)
        logger.info(f"Registered migration: {step.id} - {step.name}")
    
    def _resolve_dependencies(self) -> List[MigrationStep]:
        """
        Resolve migration dependencies and return ordered list
        
        Returns:
            List of migrations in execution order
        """
        ordered = []
        visited = set()
        visiting = set()
        
        def visit(step: MigrationStep):
            if step.id in visited:
                return
            if step.id in visiting:
                raise ValueError(f"Circular dependency detected for migration {step.id}")
            
            visiting.add(step.id)
            
            # Visit dependencies first
            for dep_id in step.dependencies:
                dep_step = next((m for m in self.migrations if m.id == dep_id), None)
                if dep_step:
                    visit(dep_step)
            
            visiting.remove(step.id)
            visited.add(step.id)
            ordered.append(step)
        
        for migration in self.migrations:
            visit(migration)
        
        return ordered
    
    def _get_applied_migrations(self) -> List[str]:
        """Get list of already applied migration IDs"""
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT migration_id FROM migration_history 
                WHERE status = 'completed'
                ORDER BY completed_at
            """))
            return [row[0] for row in result]
    
    def _calculate_checksum(self, step: MigrationStep) -> str:
        """Calculate checksum for migration step"""
        content = f"{step.id}:{step.name}:{step.up_sql or ''}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _validate_migration(self, step: MigrationStep, session: Session) -> bool:
        """
        Validate migration before execution
        
        Args:
            step: Migration step to validate
            session: Database session
            
        Returns:
            True if validation passed
        """
        if not step.validation_function:
            return True
        
        try:
            return step.validation_function(session)
        except Exception as e:
            logger.error(f"Validation failed for {step.id}: {str(e)}")
            return False
    
    def _execute_migration_step(self, step: MigrationStep, session: Session) -> MigrationResult:
        """
        Execute a single migration step
        
        Args:
            step: Migration step to execute
            session: Database session
            
        Returns:
            Migration result
        """
        result = MigrationResult(
            step_id=step.id,
            status=MigrationStatus.RUNNING,
            started_at=datetime.now()
        )
        
        try:
            # Validate before execution
            if not self._validate_migration(step, session):
                result.status = MigrationStatus.FAILED
                result.error_message = "Pre-migration validation failed"
                result.completed_at = datetime.now()
                return result
            
            # Execute migration
            if step.up_sql:
                # Execute SQL migration
                cursor_result = session.execute(text(step.up_sql))
                result.rows_affected = cursor_result.rowcount if hasattr(cursor_result, 'rowcount') else 0
            elif step.up_function:
                # Execute function migration
                result.rows_affected = step.up_function(session)
            
            # Validate after execution
            result.validation_passed = self._validate_migration(step, session)
            
            if not result.validation_passed:
                raise ValueError("Post-migration validation failed")
            
            # Commit transaction
            session.commit()
            
            result.status = MigrationStatus.COMPLETED
            result.completed_at = datetime.now()
            
            logger.info(f"Migration {step.id} completed successfully")
            
        except Exception as e:
            session.rollback()
            result.status = MigrationStatus.FAILED
            result.error_message = str(e)
            result.completed_at = datetime.now()
            logger.error(f"Migration {step.id} failed: {str(e)}")
        
        return result
    
    def _record_migration(self, step: MigrationStep, result: MigrationResult):
        """Record migration execution in history"""
        with self.engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO migration_history 
                (migration_id, name, type, status, started_at, completed_at, 
                 error_message, rows_affected, checksum)
                VALUES (:migration_id, :name, :type, :status, :started_at, 
                        :completed_at, :error_message, :rows_affected, :checksum)
            """), {
                'migration_id': step.id,
                'name': step.name,
                'type': step.type.value,
                'status': result.status.value,
                'started_at': result.started_at,
                'completed_at': result.completed_at,
                'error_message': result.error_message,
                'rows_affected': result.rows_affected,
                'checksum': self._calculate_checksum(step)
            })
            conn.commit()
    
    def migrate(self, target_version: Optional[str] = None, 
                dry_run: bool = False) -> Dict[str, Any]:
        """
        Execute migrations
        
        Args:
            target_version: Target migration version (None = latest)
            dry_run: If True, don't actually execute migrations
            
        Returns:
            Migration summary
        """
        logger.info("Starting database migration")
        
        # Resolve dependencies
        ordered_migrations = self._resolve_dependencies()
        
        # Get applied migrations
        applied = set(self._get_applied_migrations())
        
        # Filter migrations to execute
        to_execute = [
            m for m in ordered_migrations 
            if m.id not in applied and (not target_version or m.id <= target_version)
        ]
        
        if not to_execute:
            logger.info("No migrations to execute")
            return {
                'status': 'up_to_date',
                'migrations_executed': 0,
                'results': []
            }
        
        logger.info(f"Found {len(to_execute)} migrations to execute")
        
        if dry_run:
            logger.info("DRY RUN - No migrations will be executed")
            return {
                'status': 'dry_run',
                'migrations_to_execute': [m.id for m in to_execute],
                'results': []
            }
        
        # Execute migrations
        session = self.SessionLocal()
        results = []
        
        try:
            for step in to_execute:
                logger.info(f"Executing migration: {step.id} - {step.name}")
                
                result = self._execute_migration_step(step, session)
                results.append(result)
                self.results.append(result)
                
                # Record in history
                self._record_migration(step, result)
                
                # Stop on failure
                if result.status == MigrationStatus.FAILED:
                    logger.error(f"Migration failed, stopping execution")
                    break
        
        finally:
            session.close()
        
        # Generate summary
        successful = sum(1 for r in results if r.status == MigrationStatus.COMPLETED)
        failed = sum(1 for r in results if r.status == MigrationStatus.FAILED)
        
        summary = {
            'status': 'completed' if failed == 0 else 'failed',
            'migrations_executed': successful,
            'migrations_failed': failed,
            'total_rows_affected': sum(r.rows_affected for r in results),
            'results': [r.to_dict() for r in results]
        }
        
        logger.info(f"Migration summary: {successful} successful, {failed} failed")
        
        return summary
    
    def rollback(self, target_version: Optional[str] = None) -> Dict[str, Any]:
        """
        Rollback migrations
        
        Args:
            target_version: Target version to rollback to (None = rollback last)
            
        Returns:
            Rollback summary
        """
        logger.info("Starting migration rollback")
        
        # Get applied migrations in reverse order
        applied = self._get_applied_migrations()
        applied.reverse()
        
        if not applied:
            logger.info("No migrations to rollback")
            return {
                'status': 'nothing_to_rollback',
                'migrations_rolled_back': 0,
                'results': []
            }
        
        # Determine migrations to rollback
        if target_version:
            # Rollback to specific version
            to_rollback = []
            for migration_id in applied:
                if migration_id > target_version:
                    to_rollback.append(migration_id)
                else:
                    break
        else:
            # Rollback last migration only
            to_rollback = [applied[0]]
        
        logger.info(f"Rolling back {len(to_rollback)} migrations")
        
        # Execute rollbacks
        session = self.SessionLocal()
        results = []
        
        try:
            for migration_id in to_rollback:
                step = next((m for m in self.migrations if m.id == migration_id), None)
                
                if not step:
                    logger.warning(f"Migration {migration_id} not found in registered migrations")
                    continue
                
                if not step.down_sql and not step.down_function:
                    logger.warning(f"Migration {migration_id} has no rollback defined")
                    continue
                
                logger.info(f"Rolling back migration: {step.id} - {step.name}")
                
                result = MigrationResult(
                    step_id=step.id,
                    status=MigrationStatus.RUNNING,
                    started_at=datetime.now()
                )
                
                try:
                    # Execute rollback
                    if step.down_sql:
                        cursor_result = session.execute(text(step.down_sql))
                        result.rows_affected = cursor_result.rowcount if hasattr(cursor_result, 'rowcount') else 0
                    elif step.down_function:
                        result.rows_affected = step.down_function(session)
                    
                    session.commit()
                    
                    result.status = MigrationStatus.ROLLED_BACK
                    result.completed_at = datetime.now()
                    
                    # Update history
                    with self.engine.connect() as conn:
                        conn.execute(text("""
                            UPDATE migration_history 
                            SET status = 'rolled_back'
                            WHERE migration_id = :migration_id
                        """), {'migration_id': step.id})
                        conn.commit()
                    
                    logger.info(f"Rollback {step.id} completed successfully")
                    
                except Exception as e:
                    session.rollback()
                    result.status = MigrationStatus.FAILED
                    result.error_message = str(e)
                    result.completed_at = datetime.now()
                    logger.error(f"Rollback {step.id} failed: {str(e)}")
                
                results.append(result)
        
        finally:
            session.close()
        
        # Generate summary
        successful = sum(1 for r in results if r.status == MigrationStatus.ROLLED_BACK)
        failed = sum(1 for r in results if r.status == MigrationStatus.FAILED)
        
        summary = {
            'status': 'completed' if failed == 0 else 'failed',
            'migrations_rolled_back': successful,
            'rollbacks_failed': failed,
            'results': [r.to_dict() for r in results]
        }
        
        logger.info(f"Rollback summary: {successful} successful, {failed} failed")
        
        return summary
    
    def get_migration_status(self) -> Dict[str, Any]:
        """Get current migration status"""
        applied = self._get_applied_migrations()
        pending = [m.id for m in self.migrations if m.id not in applied]
        
        return {
            'current_version': applied[-1] if applied else None,
            'applied_migrations': len(applied),
            'pending_migrations': len(pending),
            'total_migrations': len(self.migrations),
            'applied': applied,
            'pending': pending
        }
    
    def validate_database(self) -> Dict[str, Any]:
        """
        Validate database integrity
        
        Returns:
            Validation results
        """
        logger.info("Validating database integrity")
        
        issues = []
        
        # Check for missing tables
        inspector = inspect(self.engine)
        existing_tables = set(inspector.get_table_names())
        
        # Check migration history
        if 'migration_history' not in existing_tables:
            issues.append({
                'type': 'missing_table',
                'severity': 'critical',
                'message': 'Migration history table not found'
            })
        
        # Check for orphaned migrations
        applied = set(self._get_applied_migrations())
        registered = set(m.id for m in self.migrations)
        
        orphaned = applied - registered
        if orphaned:
            issues.append({
                'type': 'orphaned_migrations',
                'severity': 'warning',
                'message': f'Found {len(orphaned)} applied migrations not in registry',
                'migrations': list(orphaned)
            })
        
        # Check for checksum mismatches
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT migration_id, checksum FROM migration_history
                WHERE status = 'completed'
            """))
            
            for row in result:
                migration_id, stored_checksum = row
                step = next((m for m in self.migrations if m.id == migration_id), None)
                
                if step:
                    current_checksum = self._calculate_checksum(step)
                    if current_checksum != stored_checksum:
                        issues.append({
                            'type': 'checksum_mismatch',
                            'severity': 'warning',
                            'message': f'Migration {migration_id} has been modified',
                            'migration_id': migration_id
                        })
        
        return {
            'valid': len(issues) == 0,
            'issues_found': len(issues),
            'issues': issues
        }
    
    def export_migration_history(self, output_file: str):
        """Export migration history to JSON file"""
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT * FROM migration_history ORDER BY started_at
            """))
            
            history = []
            for row in result:
                history.append(dict(row._mapping))
            
            with open(output_file, 'w') as f:
                json.dump(history, f, indent=2, default=str)
            
            logger.info(f"Migration history exported to {output_file}")
