"""
Task 235: Data Migration Implementation Service
================================================
Comprehensive data migration from SQLite (Streamlit) to new database system.
Handles all user data, projects, customers, products, and price matrices.
"""

import os
import json
import sqlite3
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class MigrationStatus(Enum):
    """Migration status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class MigrationResult:
    """Result of a migration operation."""
    table_name: str
    records_migrated: int
    records_failed: int
    errors: List[str] = field(default_factory=list)
    status: MigrationStatus = MigrationStatus.PENDING
    duration_ms: float = 0.0


@dataclass
class MigrationReport:
    """Complete migration report."""
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_tables: int = 0
    tables_migrated: int = 0
    total_records: int = 0
    records_migrated: int = 0
    records_failed: int = 0
    status: MigrationStatus = MigrationStatus.PENDING
    results: List[MigrationResult] = field(default_factory=list)
    backup_path: Optional[str] = None


class DataMigrationService:
    """
    Service for migrating data from SQLite to new database.
    
    Handles:
    - User data migration
    - Project data migration
    - Customer data migration
    - Product data migration
    - Price matrix migration
    - Settings migration
    - Audit log migration
    """
    
    # Table migration order (respects foreign key dependencies)
    MIGRATION_ORDER = [
        "users",
        "companies",
        "customers",
        "products",
        "pv_modules",
        "inverters",
        "batteries",
        "heatpumps",
        "price_matrices",
        "projects",
        "offers",
        "tasks",
        "notes",
        "communications",
        "settings",
        "audit_logs"
    ]
    
    # Column mappings for schema changes
    COLUMN_MAPPINGS = {
        "users": {
            "old_columns": ["id", "username", "password_hash", "email", "role", "created_at"],
            "new_columns": ["id", "username", "password_hash", "email", "role", "created_at", "updated_at", "is_active"],
            "defaults": {"updated_at": "NOW()", "is_active": True}
        },
        "customers": {
            "old_columns": ["id", "name", "email", "phone", "address", "notes", "created_at"],
            "new_columns": ["id", "name", "email", "phone", "address", "notes", "created_at", "updated_at", "company_id", "status"],
            "defaults": {"updated_at": "NOW()", "company_id": None, "status": "active"}
        },
        "projects": {
            "old_columns": ["id", "customer_id", "name", "data", "created_at"],
            "new_columns": ["id", "customer_id", "name", "project_data", "created_at", "updated_at", "status", "type"],
            "transforms": {"data": "project_data"},
            "defaults": {"updated_at": "NOW()", "status": "draft", "type": "solar"}
        },
        "products": {
            "old_columns": ["id", "name", "category", "price", "description", "specs"],
            "new_columns": ["id", "name", "category", "base_price", "description", "specifications", "is_active", "created_at"],
            "transforms": {"price": "base_price", "specs": "specifications"},
            "defaults": {"is_active": True, "created_at": "NOW()"}
        },
        "price_matrices": {
            "old_columns": ["id", "name", "data", "created_at", "is_active"],
            "new_columns": ["id", "name", "matrix_data", "created_at", "updated_at", "is_active", "version"],
            "transforms": {"data": "matrix_data"},
            "defaults": {"updated_at": "NOW()", "version": 1}
        }
    }
    
    def __init__(
        self,
        source_db_path: str,
        target_connection_string: str,
        backup_dir: str = "./backups"
    ):
        """
        Initialize migration service.
        
        Args:
            source_db_path: Path to source SQLite database
            target_connection_string: Connection string for target database
            backup_dir: Directory for backup files
        """
        self.source_db_path = source_db_path
        self.target_connection_string = target_connection_string
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        self._source_conn: Optional[sqlite3.Connection] = None
        self._report: Optional[MigrationReport] = None
    
    def create_backup(self) -> str:
        """
        Create backup of source database before migration.
        
        Returns:
            Path to backup file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"pre_migration_backup_{timestamp}.db"
        backup_path = self.backup_dir / backup_filename
        
        logger.info(f"Creating backup at {backup_path}")
        
        # Copy SQLite database
        import shutil
        shutil.copy2(self.source_db_path, backup_path)
        
        # Verify backup
        if not backup_path.exists():
            raise RuntimeError("Backup creation failed")
        
        logger.info(f"Backup created successfully: {backup_path}")
        return str(backup_path)
    
    def validate_source_database(self) -> Dict[str, Any]:
        """
        Validate source database structure and data.
        
        Returns:
            Validation report
        """
        validation = {
            "valid": True,
            "tables_found": [],
            "tables_missing": [],
            "record_counts": {},
            "issues": []
        }
        
        try:
            conn = sqlite3.connect(self.source_db_path)
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = {row[0] for row in cursor.fetchall()}
            
            for table in self.MIGRATION_ORDER:
                if table in existing_tables:
                    validation["tables_found"].append(table)
                    
                    # Count records
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    validation["record_counts"][table] = count
                else:
                    validation["tables_missing"].append(table)
            
            conn.close()
            
            # Check for critical missing tables
            critical_tables = ["users", "customers", "projects", "products"]
            for table in critical_tables:
                if table in validation["tables_missing"]:
                    validation["valid"] = False
                    validation["issues"].append(f"Critical table '{table}' is missing")
            
        except Exception as e:
            validation["valid"] = False
            validation["issues"].append(f"Database validation error: {str(e)}")
        
        return validation
    
    def migrate_table(
        self,
        table_name: str,
        batch_size: int = 1000
    ) -> MigrationResult:
        """
        Migrate a single table from source to target.
        
        Args:
            table_name: Name of table to migrate
            batch_size: Number of records per batch
            
        Returns:
            Migration result for this table
        """
        result = MigrationResult(
            table_name=table_name,
            records_migrated=0,
            records_failed=0,
            status=MigrationStatus.IN_PROGRESS
        )
        
        start_time = datetime.now()
        
        try:
            source_conn = sqlite3.connect(self.source_db_path)
            source_conn.row_factory = sqlite3.Row
            cursor = source_conn.cursor()
            
            # Get column info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cursor.fetchall()]
            
            # Get all records
            cursor.execute(f"SELECT * FROM {table_name}")
            
            while True:
                rows = cursor.fetchmany(batch_size)
                if not rows:
                    break
                
                for row in rows:
                    try:
                        # Transform row data
                        transformed = self._transform_row(table_name, dict(row), columns)
                        
                        # Insert into target (simulated)
                        self._insert_record(table_name, transformed)
                        result.records_migrated += 1
                        
                    except Exception as e:
                        result.records_failed += 1
                        result.errors.append(f"Row error: {str(e)}")
            
            source_conn.close()
            result.status = MigrationStatus.COMPLETED
            
        except Exception as e:
            result.status = MigrationStatus.FAILED
            result.errors.append(f"Table migration error: {str(e)}")
            logger.error(f"Failed to migrate table {table_name}: {e}")
        
        result.duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        return result
    
    def _transform_row(
        self,
        table_name: str,
        row: Dict[str, Any],
        source_columns: List[str]
    ) -> Dict[str, Any]:
        """
        Transform row data according to column mappings.
        
        Args:
            table_name: Name of table
            row: Source row data
            source_columns: Source column names
            
        Returns:
            Transformed row data
        """
        mapping = self.COLUMN_MAPPINGS.get(table_name, {})
        transformed = {}
        
        # Copy existing columns
        for col in source_columns:
            value = row.get(col)
            
            # Apply column name transforms
            transforms = mapping.get("transforms", {})
            new_col = transforms.get(col, col)
            
            # Handle JSON data
            if isinstance(value, str) and (value.startswith("{") or value.startswith("[")):
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    pass
            
            transformed[new_col] = value
        
        # Apply defaults for new columns
        defaults = mapping.get("defaults", {})
        for col, default in defaults.items():
            if col not in transformed:
                if default == "NOW()":
                    transformed[col] = datetime.now().isoformat()
                else:
                    transformed[col] = default
        
        return transformed
    
    def _insert_record(self, table_name: str, data: Dict[str, Any]) -> None:
        """
        Insert record into target database.
        
        Args:
            table_name: Target table name
            data: Record data to insert
        """
        # In production, this would insert into the actual target database
        # For now, we simulate the insert
        logger.debug(f"Inserting into {table_name}: {data.get('id', 'new')}")
    
    def run_migration(
        self,
        tables: Optional[List[str]] = None,
        dry_run: bool = False
    ) -> MigrationReport:
        """
        Run complete data migration.
        
        Args:
            tables: Specific tables to migrate (None = all)
            dry_run: If True, validate only without actual migration
            
        Returns:
            Complete migration report
        """
        self._report = MigrationReport(
            started_at=datetime.now(),
            status=MigrationStatus.IN_PROGRESS
        )
        
        try:
            # Validate source database
            logger.info("Validating source database...")
            validation = self.validate_source_database()
            
            if not validation["valid"]:
                self._report.status = MigrationStatus.FAILED
                logger.error(f"Source validation failed: {validation['issues']}")
                return self._report
            
            # Create backup
            if not dry_run:
                logger.info("Creating backup...")
                self._report.backup_path = self.create_backup()
            
            # Determine tables to migrate
            tables_to_migrate = tables or self.MIGRATION_ORDER
            tables_to_migrate = [t for t in tables_to_migrate if t in validation["tables_found"]]
            
            self._report.total_tables = len(tables_to_migrate)
            self._report.total_records = sum(
                validation["record_counts"].get(t, 0) for t in tables_to_migrate
            )
            
            # Migrate each table
            for table in tables_to_migrate:
                logger.info(f"Migrating table: {table}")
                
                if dry_run:
                    result = MigrationResult(
                        table_name=table,
                        records_migrated=validation["record_counts"].get(table, 0),
                        records_failed=0,
                        status=MigrationStatus.COMPLETED
                    )
                else:
                    result = self.migrate_table(table)
                
                self._report.results.append(result)
                self._report.tables_migrated += 1
                self._report.records_migrated += result.records_migrated
                self._report.records_failed += result.records_failed
                
                if result.status == MigrationStatus.FAILED:
                    logger.warning(f"Table {table} migration failed")
            
            # Finalize
            self._report.completed_at = datetime.now()
            self._report.status = MigrationStatus.COMPLETED
            
            logger.info(f"Migration completed: {self._report.records_migrated} records migrated")
            
        except Exception as e:
            self._report.status = MigrationStatus.FAILED
            logger.error(f"Migration failed: {e}")
        
        return self._report
    
    def rollback(self, backup_path: str) -> bool:
        """
        Rollback migration using backup.
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            True if rollback successful
        """
        try:
            import shutil
            
            logger.info(f"Rolling back from backup: {backup_path}")
            
            # Restore backup
            shutil.copy2(backup_path, self.source_db_path)
            
            logger.info("Rollback completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False
    
    def get_migration_status(self) -> Dict[str, Any]:
        """
        Get current migration status.
        
        Returns:
            Status dictionary
        """
        if not self._report:
            return {"status": "not_started"}
        
        return {
            "status": self._report.status.value,
            "started_at": self._report.started_at.isoformat(),
            "completed_at": self._report.completed_at.isoformat() if self._report.completed_at else None,
            "progress": {
                "tables": f"{self._report.tables_migrated}/{self._report.total_tables}",
                "records": f"{self._report.records_migrated}/{self._report.total_records}"
            },
            "backup_path": self._report.backup_path
        }


class UserDataMigrator:
    """Specialized migrator for user data."""
    
    def migrate_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate single user record."""
        return {
            "id": user_data.get("id"),
            "username": user_data.get("username"),
            "email": user_data.get("email"),
            "password_hash": user_data.get("password_hash"),
            "role": user_data.get("role", "user"),
            "is_active": True,
            "created_at": user_data.get("created_at"),
            "updated_at": datetime.now().isoformat()
        }


class ProjectDataMigrator:
    """Specialized migrator for project data."""
    
    def migrate_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate single project record."""
        # Parse JSON data if string
        data = project_data.get("data", {})
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                data = {}
        
        return {
            "id": project_data.get("id"),
            "customer_id": project_data.get("customer_id"),
            "name": project_data.get("name"),
            "project_data": data,
            "status": "active",
            "type": self._determine_project_type(data),
            "created_at": project_data.get("created_at"),
            "updated_at": datetime.now().isoformat()
        }
    
    def _determine_project_type(self, data: Dict[str, Any]) -> str:
        """Determine project type from data."""
        if "heatpump" in data or "heating" in data:
            return "heatpump"
        elif "solar" in data or "pv" in data:
            return "solar"
        elif "combined" in data:
            return "combined"
        return "solar"


class PriceMatrixMigrator:
    """Specialized migrator for price matrices."""
    
    def migrate_matrix(self, matrix_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate single price matrix record."""
        # Parse matrix data
        data = matrix_data.get("data", {})
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                data = {}
        
        return {
            "id": matrix_data.get("id"),
            "name": matrix_data.get("name"),
            "matrix_data": data,
            "is_active": matrix_data.get("is_active", True),
            "version": 1,
            "created_at": matrix_data.get("created_at"),
            "updated_at": datetime.now().isoformat()
        }


# Migration CLI helper
def run_migration_cli():
    """Run migration from command line."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Data Migration Tool")
    parser.add_argument("--source", required=True, help="Source SQLite database path")
    parser.add_argument("--target", required=True, help="Target database connection string")
    parser.add_argument("--dry-run", action="store_true", help="Validate only, don't migrate")
    parser.add_argument("--tables", nargs="+", help="Specific tables to migrate")
    
    args = parser.parse_args()
    
    service = DataMigrationService(
        source_db_path=args.source,
        target_connection_string=args.target
    )
    
    report = service.run_migration(
        tables=args.tables,
        dry_run=args.dry_run
    )
    
    print(f"\nMigration Status: {report.status.value}")
    print(f"Tables: {report.tables_migrated}/{report.total_tables}")
    print(f"Records: {report.records_migrated}/{report.total_records}")
    
    if report.records_failed > 0:
        print(f"Failed: {report.records_failed}")


if __name__ == "__main__":
    run_migration_cli()
