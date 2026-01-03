"""
Data Migration Service for Streamlit to Electron Migration
Task 235: Data Migration Implementation

This service handles:
- SQLite to new database migration
- Data validation during migration
- Migration progress tracking
- Rollback functionality
- Backup before migration
- Migration of all data types (users, projects, customers, products, price matrices)
"""

import os
import json
import shutil
import sqlite3
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class MigrationStatus(str, Enum):
    """Migration status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class DataType(str, Enum):
    """Data types for migration"""
    USER_SETTINGS = "user_settings"
    PROJECTS = "projects"
    CUSTOMERS = "customers"
    PRODUCTS = "products"
    PRICE_MATRICES = "price_matrices"
    CRM_DATA = "crm_data"
    PDF_TEMPLATES = "pdf_templates"
    SYSTEM_CONFIG = "system_config"


@dataclass
class MigrationProgress:
    """Track migration progress for each data type"""
    data_type: str
    total_records: int = 0
    migrated_records: int = 0
    failed_records: int = 0
    status: MigrationStatus = MigrationStatus.PENDING
    errors: List[str] = field(default_factory=list)
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    
    @property
    def progress_percent(self) -> float:
        if self.total_records == 0:
            return 0.0
        return (self.migrated_records / self.total_records) * 100


@dataclass
class MigrationReport:
    """Complete migration report"""
    migration_id: str
    source_db: str
    target_db: str
    started_at: str
    completed_at: Optional[str] = None
    overall_status: MigrationStatus = MigrationStatus.PENDING
    backup_path: Optional[str] = None
    progress: Dict[str, MigrationProgress] = field(default_factory=dict)
    total_records: int = 0
    migrated_records: int = 0
    failed_records: int = 0
    validation_errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "migration_id": self.migration_id,
            "source_db": self.source_db,
            "target_db": self.target_db,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "overall_status": self.overall_status.value,
            "backup_path": self.backup_path,
            "progress": {k: asdict(v) for k, v in self.progress.items()},
            "total_records": self.total_records,
            "migrated_records": self.migrated_records,
            "failed_records": self.failed_records,
            "validation_errors": self.validation_errors
        }


class DataValidator:
    """Validates data during migration"""
    
    @staticmethod
    def validate_user_settings(data: Dict[str, Any]) -> List[str]:
        """Validate user settings data"""
        errors = []
        if not data.get("user_id"):
            errors.append("Missing user_id")
        return errors
    
    @staticmethod
    def validate_project(data: Dict[str, Any]) -> List[str]:
        """Validate project data"""
        errors = []
        required_fields = ["project_id", "name"]
        for field in required_fields:
            if not data.get(field):
                errors.append(f"Missing required field: {field}")
        return errors
    
    @staticmethod
    def validate_customer(data: Dict[str, Any]) -> List[str]:
        """Validate customer data"""
        errors = []
        if not data.get("customer_id") and not data.get("id"):
            errors.append("Missing customer identifier")
        return errors
    
    @staticmethod
    def validate_product(data: Dict[str, Any]) -> List[str]:
        """Validate product data"""
        errors = []
        if not data.get("product_id") and not data.get("id"):
            errors.append("Missing product identifier")
        return errors
    
    @staticmethod
    def validate_price_matrix(data: Dict[str, Any]) -> List[str]:
        """Validate price matrix data"""
        errors = []
        if not data.get("matrix_id") and not data.get("id"):
            errors.append("Missing matrix identifier")
        return errors


class MigrationService:
    """
    Main migration service for handling data migration from Streamlit SQLite
    to the new Electron application database.
    """
    
    def __init__(
        self,
        source_db_path: str,
        target_db_path: str,
        backup_dir: str = "backups/migrations"
    ):
        self.source_db_path = source_db_path
        self.target_db_path = target_db_path
        self.backup_dir = backup_dir
        self.validator = DataValidator()
        self.report: Optional[MigrationReport] = None
        self._progress_callbacks: List[Callable[[MigrationProgress], None]] = []
        
        # Ensure backup directory exists
        Path(backup_dir).mkdir(parents=True, exist_ok=True)
    
    def add_progress_callback(self, callback: Callable[[MigrationProgress], None]):
        """Add a callback for progress updates"""
        self._progress_callbacks.append(callback)
    
    def _notify_progress(self, progress: MigrationProgress):
        """Notify all callbacks of progress update"""
        for callback in self._progress_callbacks:
            try:
                callback(progress)
            except Exception as e:
                logger.error(f"Progress callback error: {e}")
    
    def generate_migration_id(self) -> str:
        """Generate unique migration ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        hash_input = f"{self.source_db_path}_{timestamp}"
        short_hash = hashlib.md5(hash_input.encode()).hexdigest()[:8]
        return f"migration_{timestamp}_{short_hash}"
    
    def create_backup(self) -> str:
        """Create backup of source database before migration"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"backup_{timestamp}.db"
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        if os.path.exists(self.source_db_path):
            shutil.copy2(self.source_db_path, backup_path)
            logger.info(f"Backup created: {backup_path}")
            return backup_path
        else:
            logger.warning(f"Source database not found: {self.source_db_path}")
            return ""
    
    def rollback(self, backup_path: str) -> bool:
        """Rollback migration using backup"""
        try:
            if os.path.exists(backup_path):
                shutil.copy2(backup_path, self.source_db_path)
                logger.info(f"Rollback completed from: {backup_path}")
                if self.report:
                    self.report.overall_status = MigrationStatus.ROLLED_BACK
                return True
            else:
                logger.error(f"Backup not found: {backup_path}")
                return False
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False
    
    def _get_source_connection(self) -> sqlite3.Connection:
        """Get connection to source database"""
        conn = sqlite3.connect(self.source_db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _get_target_connection(self) -> sqlite3.Connection:
        """Get connection to target database"""
        conn = sqlite3.connect(self.target_db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _count_records(self, conn: sqlite3.Connection, table: str) -> int:
        """Count records in a table"""
        try:
            cursor = conn.execute(f"SELECT COUNT(*) FROM {table}")
            return cursor.fetchone()[0]
        except sqlite3.OperationalError:
            return 0
    
    def _table_exists(self, conn: sqlite3.Connection, table: str) -> bool:
        """Check if table exists"""
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table)
        )
        return cursor.fetchone() is not None
    
    def migrate_user_settings(self) -> MigrationProgress:
        """Migrate user settings and preferences"""
        progress = MigrationProgress(data_type=DataType.USER_SETTINGS.value)
        progress.status = MigrationStatus.IN_PROGRESS
        progress.started_at = datetime.now().isoformat()
        
        try:
            source_conn = self._get_source_connection()
            target_conn = self._get_target_connection()
            
            # Check for user settings tables
            settings_tables = ["user_settings", "user_preferences", "app_settings"]
            
            for table in settings_tables:
                if self._table_exists(source_conn, table):
                    count = self._count_records(source_conn, table)
                    progress.total_records += count
                    
                    cursor = source_conn.execute(f"SELECT * FROM {table}")
                    rows = cursor.fetchall()
                    
                    for row in rows:
                        data = dict(row)
                        errors = self.validator.validate_user_settings(data)
                        
                        if errors:
                            progress.failed_records += 1
                            progress.errors.extend(errors)
                        else:
                            # Insert into target database
                            self._insert_record(target_conn, table, data)
                            progress.migrated_records += 1
                        
                        self._notify_progress(progress)
            
            target_conn.commit()
            progress.status = MigrationStatus.COMPLETED
            progress.completed_at = datetime.now().isoformat()
            
            source_conn.close()
            target_conn.close()
            
        except Exception as e:
            progress.status = MigrationStatus.FAILED
            progress.errors.append(str(e))
            logger.error(f"User settings migration failed: {e}")
        
        return progress
    
    def migrate_projects(self) -> MigrationProgress:
        """Migrate all project data"""
        progress = MigrationProgress(data_type=DataType.PROJECTS.value)
        progress.status = MigrationStatus.IN_PROGRESS
        progress.started_at = datetime.now().isoformat()
        
        try:
            source_conn = self._get_source_connection()
            target_conn = self._get_target_connection()
            
            project_tables = ["projects", "solar_projects", "heatpump_projects"]
            
            for table in project_tables:
                if self._table_exists(source_conn, table):
                    count = self._count_records(source_conn, table)
                    progress.total_records += count
                    
                    cursor = source_conn.execute(f"SELECT * FROM {table}")
                    rows = cursor.fetchall()
                    
                    for row in rows:
                        data = dict(row)
                        # Add project_id if missing
                        if "project_id" not in data and "id" in data:
                            data["project_id"] = data["id"]
                        if "name" not in data:
                            data["name"] = f"Project_{data.get('id', 'unknown')}"
                        
                        errors = self.validator.validate_project(data)
                        
                        if errors:
                            progress.failed_records += 1
                            progress.errors.extend(errors)
                        else:
                            self._insert_record(target_conn, table, data)
                            progress.migrated_records += 1
                        
                        self._notify_progress(progress)
            
            target_conn.commit()
            progress.status = MigrationStatus.COMPLETED
            progress.completed_at = datetime.now().isoformat()
            
            source_conn.close()
            target_conn.close()
            
        except Exception as e:
            progress.status = MigrationStatus.FAILED
            progress.errors.append(str(e))
            logger.error(f"Projects migration failed: {e}")
        
        return progress
    
    def migrate_customers(self) -> MigrationProgress:
        """Migrate all customer data from CRM"""
        progress = MigrationProgress(data_type=DataType.CUSTOMERS.value)
        progress.status = MigrationStatus.IN_PROGRESS
        progress.started_at = datetime.now().isoformat()
        
        try:
            source_conn = self._get_source_connection()
            target_conn = self._get_target_connection()
            
            customer_tables = ["customers", "crm_customers", "contacts"]
            
            for table in customer_tables:
                if self._table_exists(source_conn, table):
                    count = self._count_records(source_conn, table)
                    progress.total_records += count
                    
                    cursor = source_conn.execute(f"SELECT * FROM {table}")
                    rows = cursor.fetchall()
                    
                    for row in rows:
                        data = dict(row)
                        errors = self.validator.validate_customer(data)
                        
                        if errors:
                            progress.failed_records += 1
                            progress.errors.extend(errors)
                        else:
                            self._insert_record(target_conn, table, data)
                            progress.migrated_records += 1
                        
                        self._notify_progress(progress)
            
            target_conn.commit()
            progress.status = MigrationStatus.COMPLETED
            progress.completed_at = datetime.now().isoformat()
            
            source_conn.close()
            target_conn.close()
            
        except Exception as e:
            progress.status = MigrationStatus.FAILED
            progress.errors.append(str(e))
            logger.error(f"Customers migration failed: {e}")
        
        return progress
    
    def migrate_products(self) -> MigrationProgress:
        """Migrate all product data"""
        progress = MigrationProgress(data_type=DataType.PRODUCTS.value)
        progress.status = MigrationStatus.IN_PROGRESS
        progress.started_at = datetime.now().isoformat()
        
        try:
            source_conn = self._get_source_connection()
            target_conn = self._get_target_connection()
            
            product_tables = [
                "products", "pv_modules", "inverters", "batteries",
                "heatpumps", "wallboxes", "accessories"
            ]
            
            for table in product_tables:
                if self._table_exists(source_conn, table):
                    count = self._count_records(source_conn, table)
                    progress.total_records += count
                    
                    cursor = source_conn.execute(f"SELECT * FROM {table}")
                    rows = cursor.fetchall()
                    
                    for row in rows:
                        data = dict(row)
                        errors = self.validator.validate_product(data)
                        
                        if errors:
                            progress.failed_records += 1
                            progress.errors.extend(errors)
                        else:
                            self._insert_record(target_conn, table, data)
                            progress.migrated_records += 1
                        
                        self._notify_progress(progress)
            
            target_conn.commit()
            progress.status = MigrationStatus.COMPLETED
            progress.completed_at = datetime.now().isoformat()
            
            source_conn.close()
            target_conn.close()
            
        except Exception as e:
            progress.status = MigrationStatus.FAILED
            progress.errors.append(str(e))
            logger.error(f"Products migration failed: {e}")
        
        return progress
    
    def migrate_price_matrices(self) -> MigrationProgress:
        """Migrate all price matrices"""
        progress = MigrationProgress(data_type=DataType.PRICE_MATRICES.value)
        progress.status = MigrationStatus.IN_PROGRESS
        progress.started_at = datetime.now().isoformat()
        
        try:
            source_conn = self._get_source_connection()
            target_conn = self._get_target_connection()
            
            matrix_tables = ["price_matrices", "price_matrix_data", "pricing_rules"]
            
            for table in matrix_tables:
                if self._table_exists(source_conn, table):
                    count = self._count_records(source_conn, table)
                    progress.total_records += count
                    
                    cursor = source_conn.execute(f"SELECT * FROM {table}")
                    rows = cursor.fetchall()
                    
                    for row in rows:
                        data = dict(row)
                        errors = self.validator.validate_price_matrix(data)
                        
                        if errors:
                            progress.failed_records += 1
                            progress.errors.extend(errors)
                        else:
                            self._insert_record(target_conn, table, data)
                            progress.migrated_records += 1
                        
                        self._notify_progress(progress)
            
            target_conn.commit()
            progress.status = MigrationStatus.COMPLETED
            progress.completed_at = datetime.now().isoformat()
            
            source_conn.close()
            target_conn.close()
            
        except Exception as e:
            progress.status = MigrationStatus.FAILED
            progress.errors.append(str(e))
            logger.error(f"Price matrices migration failed: {e}")
        
        return progress
    
    def _insert_record(
        self,
        conn: sqlite3.Connection,
        table: str,
        data: Dict[str, Any]
    ):
        """Insert a record into target database"""
        # Ensure table exists in target
        self._ensure_table_exists(conn, table, data)
        
        columns = list(data.keys())
        placeholders = ", ".join(["?" for _ in columns])
        column_names = ", ".join(columns)
        
        values = [
            json.dumps(v) if isinstance(v, (dict, list)) else v
            for v in data.values()
        ]
        
        try:
            conn.execute(
                f"INSERT OR REPLACE INTO {table} ({column_names}) VALUES ({placeholders})",
                values
            )
        except sqlite3.Error as e:
            logger.error(f"Insert error for {table}: {e}")
            raise
    
    def _ensure_table_exists(
        self,
        conn: sqlite3.Connection,
        table: str,
        sample_data: Dict[str, Any]
    ):
        """Ensure table exists in target database"""
        if not self._table_exists(conn, table):
            # Create table based on sample data
            columns = []
            primary_key_set = False
            
            # Priority order for primary key
            pk_candidates = ["id", "user_id", "project_id", "customer_id", "product_id", "matrix_id"]
            
            for key, value in sample_data.items():
                if isinstance(value, int):
                    col_type = "INTEGER"
                elif isinstance(value, float):
                    col_type = "REAL"
                elif isinstance(value, bool):
                    col_type = "INTEGER"
                else:
                    col_type = "TEXT"
                
                # Only set one primary key
                if not primary_key_set and key in pk_candidates:
                    columns.append(f"{key} {col_type} PRIMARY KEY")
                    primary_key_set = True
                else:
                    columns.append(f"{key} {col_type}")
            
            create_sql = f"CREATE TABLE IF NOT EXISTS {table} ({', '.join(columns)})"
            conn.execute(create_sql)
    
    def run_full_migration(self) -> MigrationReport:
        """Run complete migration of all data types"""
        migration_id = self.generate_migration_id()
        
        self.report = MigrationReport(
            migration_id=migration_id,
            source_db=self.source_db_path,
            target_db=self.target_db_path,
            started_at=datetime.now().isoformat()
        )
        
        # Create backup first
        backup_path = self.create_backup()
        self.report.backup_path = backup_path
        self.report.overall_status = MigrationStatus.IN_PROGRESS
        
        try:
            # Run all migrations
            migrations = [
                (DataType.USER_SETTINGS, self.migrate_user_settings),
                (DataType.PROJECTS, self.migrate_projects),
                (DataType.CUSTOMERS, self.migrate_customers),
                (DataType.PRODUCTS, self.migrate_products),
                (DataType.PRICE_MATRICES, self.migrate_price_matrices),
            ]
            
            for data_type, migrate_func in migrations:
                logger.info(f"Starting migration: {data_type.value}")
                progress = migrate_func()
                self.report.progress[data_type.value] = progress
                self.report.total_records += progress.total_records
                self.report.migrated_records += progress.migrated_records
                self.report.failed_records += progress.failed_records
                
                if progress.status == MigrationStatus.FAILED:
                    self.report.validation_errors.extend(progress.errors)
            
            # Determine overall status
            if self.report.failed_records == 0:
                self.report.overall_status = MigrationStatus.COMPLETED
            elif self.report.migrated_records > 0:
                self.report.overall_status = MigrationStatus.COMPLETED  # Partial success
            else:
                self.report.overall_status = MigrationStatus.FAILED
            
            self.report.completed_at = datetime.now().isoformat()
            
        except Exception as e:
            self.report.overall_status = MigrationStatus.FAILED
            self.report.validation_errors.append(str(e))
            logger.error(f"Full migration failed: {e}")
        
        return self.report
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate migration report as dictionary"""
        if self.report:
            return self.report.to_dict()
        return {"error": "No migration has been run"}
    
    def save_report(self, output_path: str):
        """Save migration report to file"""
        report_data = self.generate_report()
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Migration report saved: {output_path}")
