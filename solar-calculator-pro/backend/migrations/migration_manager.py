"""
Migration Manager for Streamlit to Electron Migration
Handles database, settings, project data, and user data migration
Requirements: 5.1, 5.2, 5.3, 5.4
"""

import sqlite3
import json
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)


class MigrationManager:
    """Main migration manager coordinating all migration tasks"""
    
    def __init__(self, source_path: Path, target_path: Path):
        """
        Initialize migration manager
        
        Args:
            source_path: Path to Streamlit application data
            target_path: Path to new Electron application data
        """
        self.source_path = Path(source_path)
        self.target_path = Path(target_path)
        self.backup_path = self.target_path / "backups" / datetime.now().strftime("%Y%m%d_%H%M%S")
        self.migration_log: List[Dict[str, Any]] = []
        
        # Ensure paths exist
        self.target_path.mkdir(parents=True, exist_ok=True)
        self.backup_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Migration Manager initialized: {self.source_path} -> {self.target_path}")
    
    def run_full_migration(self) -> Dict[str, Any]:
        """
        Run complete migration process
        
        Returns:
            Migration report with success/failure status
        """
        logger.info("Starting full migration process")
        
        report = {
            "started_at": datetime.now().isoformat(),
            "source_path": str(self.source_path),
            "target_path": str(self.target_path),
            "backup_path": str(self.backup_path),
            "steps": [],
            "success": False,
            "errors": []
        }
        
        try:
            # Step 1: Create backup
            backup_result = self._create_backup()
            report["steps"].append(backup_result)
            if not backup_result["success"]:
                raise Exception("Backup creation failed")
            
            # Step 2: Migrate database
            db_result = self._migrate_database()
            report["steps"].append(db_result)
            if not db_result["success"]:
                raise Exception("Database migration failed")
            
            # Step 3: Migrate settings
            settings_result = self._migrate_settings()
            report["steps"].append(settings_result)
            if not settings_result["success"]:
                raise Exception("Settings migration failed")
            
            # Step 4: Migrate project data
            project_result = self._migrate_project_data()
            report["steps"].append(project_result)
            if not project_result["success"]:
                raise Exception("Project data migration failed")
            
            # Step 5: Migrate user data
            user_result = self._migrate_user_data()
            report["steps"].append(user_result)
            if not user_result["success"]:
                raise Exception("User data migration failed")
            
            # Step 6: Validate migration
            validation_result = self._validate_migration()
            report["steps"].append(validation_result)
            if not validation_result["success"]:
                raise Exception("Migration validation failed")
            
            report["success"] = True
            logger.info("Full migration completed successfully")
            
        except Exception as e:
            logger.error(f"Migration failed: {str(e)}", exc_info=True)
            report["errors"].append(str(e))
            report["success"] = False
            
            # Attempt rollback
            rollback_result = self._rollback_migration()
            report["rollback"] = rollback_result
        
        finally:
            report["completed_at"] = datetime.now().isoformat()
            self._save_migration_report(report)
        
        return report
    
    def _create_backup(self) -> Dict[str, Any]:
        """Create backup of source data before migration"""
        logger.info("Creating backup of source data")
        
        result = {
            "step": "backup",
            "success": False,
            "message": "",
            "files_backed_up": 0
        }
        
        try:
            # Backup all source files
            if self.source_path.exists():
                shutil.copytree(
                    self.source_path,
                    self.backup_path / "source",
                    dirs_exist_ok=True
                )
                
                # Count backed up files
                result["files_backed_up"] = sum(1 for _ in self.backup_path.rglob("*") if _.is_file())
                result["success"] = True
                result["message"] = f"Backup created successfully: {result['files_backed_up']} files"
                logger.info(result["message"])
            else:
                result["message"] = f"Source path does not exist: {self.source_path}"
                logger.warning(result["message"])
                result["success"] = False
                
        except Exception as e:
            result["message"] = f"Backup failed: {str(e)}"
            logger.error(result["message"], exc_info=True)
        
        return result
    
    def _migrate_database(self) -> Dict[str, Any]:
        """Migrate SQLite databases"""
        logger.info("Migrating databases")
        
        result = {
            "step": "database_migration",
            "success": False,
            "message": "",
            "databases_migrated": 0,
            "tables_migrated": 0,
            "records_migrated": 0
        }
        
        try:
            # Find all SQLite databases in source
            db_files = list(self.source_path.glob("**/*.db"))
            
            for db_file in db_files:
                db_result = self._migrate_single_database(db_file)
                result["databases_migrated"] += 1
                result["tables_migrated"] += db_result["tables"]
                result["records_migrated"] += db_result["records"]
            
            result["success"] = True
            result["message"] = f"Migrated {result['databases_migrated']} databases, {result['tables_migrated']} tables, {result['records_migrated']} records"
            logger.info(result["message"])
            
        except Exception as e:
            result["message"] = f"Database migration failed: {str(e)}"
            logger.error(result["message"], exc_info=True)
        
        return result
    
    def _migrate_single_database(self, source_db: Path) -> Dict[str, int]:
        """Migrate a single SQLite database"""
        logger.info(f"Migrating database: {source_db.name}")
        
        # Determine target database path
        relative_path = source_db.relative_to(self.source_path)
        target_db = self.target_path / relative_path
        target_db.parent.mkdir(parents=True, exist_ok=True)
        
        # Connect to source and target databases
        source_conn = sqlite3.connect(source_db)
        target_conn = sqlite3.connect(target_db)
        
        tables_migrated = 0
        records_migrated = 0
        
        try:
            # Get all tables
            cursor = source_conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            for table in tables:
                # Get table schema
                cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'")
                create_sql = cursor.fetchone()[0]
                
                # Create table in target
                target_conn.execute(create_sql)
                
                # Copy data
                cursor.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
                
                if rows:
                    placeholders = ','.join(['?' for _ in range(len(rows[0]))])
                    target_conn.executemany(
                        f"INSERT INTO {table} VALUES ({placeholders})",
                        rows
                    )
                    records_migrated += len(rows)
                
                tables_migrated += 1
                logger.debug(f"Migrated table {table}: {len(rows)} records")
            
            target_conn.commit()
            
        finally:
            source_conn.close()
            target_conn.close()
        
        return {"tables": tables_migrated, "records": records_migrated}
    
    def _migrate_settings(self) -> Dict[str, Any]:
        """Migrate application settings"""
        logger.info("Migrating settings")
        
        result = {
            "step": "settings_migration",
            "success": False,
            "message": "",
            "settings_migrated": 0
        }
        
        try:
            # Look for settings files (JSON, YAML, INI, etc.)
            settings_files = []
            settings_files.extend(self.source_path.glob("**/*.json"))
            settings_files.extend(self.source_path.glob("**/*.yaml"))
            settings_files.extend(self.source_path.glob("**/*.yml"))
            settings_files.extend(self.source_path.glob("**/*.ini"))
            settings_files.extend(self.source_path.glob("**/*.conf"))
            
            for settings_file in settings_files:
                # Skip database files
                if settings_file.suffix == '.db':
                    continue
                
                # Copy settings file
                relative_path = settings_file.relative_to(self.source_path)
                target_file = self.target_path / relative_path
                target_file.parent.mkdir(parents=True, exist_ok=True)
                
                shutil.copy2(settings_file, target_file)
                result["settings_migrated"] += 1
                logger.debug(f"Migrated settings file: {settings_file.name}")
            
            result["success"] = True
            result["message"] = f"Migrated {result['settings_migrated']} settings files"
            logger.info(result["message"])
            
        except Exception as e:
            result["message"] = f"Settings migration failed: {str(e)}"
            logger.error(result["message"], exc_info=True)
        
        return result
    
    def _migrate_project_data(self) -> Dict[str, Any]:
        """Migrate project-specific data"""
        logger.info("Migrating project data")
        
        result = {
            "step": "project_data_migration",
            "success": False,
            "message": "",
            "projects_migrated": 0
        }
        
        try:
            # Look for project data directories
            project_dirs = [
                self.source_path / "projects",
                self.source_path / "data",
                self.source_path / "uploads"
            ]
            
            for project_dir in project_dirs:
                if project_dir.exists():
                    target_dir = self.target_path / project_dir.name
                    shutil.copytree(project_dir, target_dir, dirs_exist_ok=True)
                    
                    # Count projects
                    project_count = sum(1 for _ in target_dir.iterdir() if _.is_dir())
                    result["projects_migrated"] += project_count
                    logger.debug(f"Migrated {project_count} projects from {project_dir.name}")
            
            result["success"] = True
            result["message"] = f"Migrated {result['projects_migrated']} projects"
            logger.info(result["message"])
            
        except Exception as e:
            result["message"] = f"Project data migration failed: {str(e)}"
            logger.error(result["message"], exc_info=True)
        
        return result
    
    def _migrate_user_data(self) -> Dict[str, Any]:
        """Migrate user-specific data"""
        logger.info("Migrating user data")
        
        result = {
            "step": "user_data_migration",
            "success": False,
            "message": "",
            "users_migrated": 0
        }
        
        try:
            # Look for user data
            user_dirs = [
                self.source_path / "users",
                self.source_path / "profiles"
            ]
            
            for user_dir in user_dirs:
                if user_dir.exists():
                    target_dir = self.target_path / user_dir.name
                    shutil.copytree(user_dir, target_dir, dirs_exist_ok=True)
                    
                    # Count users
                    user_count = sum(1 for _ in target_dir.iterdir() if _.is_dir())
                    result["users_migrated"] += user_count
                    logger.debug(f"Migrated {user_count} users from {user_dir.name}")
            
            result["success"] = True
            result["message"] = f"Migrated {result['users_migrated']} users"
            logger.info(result["message"])
            
        except Exception as e:
            result["message"] = f"User data migration failed: {str(e)}"
            logger.error(result["message"], exc_info=True)
        
        return result
    
    def _validate_migration(self) -> Dict[str, Any]:
        """Validate migrated data"""
        logger.info("Validating migration")
        
        result = {
            "step": "validation",
            "success": False,
            "message": "",
            "checks": []
        }
        
        try:
            # Check 1: Database integrity
            db_check = self._validate_databases()
            result["checks"].append(db_check)
            
            # Check 2: File count comparison
            file_check = self._validate_file_counts()
            result["checks"].append(file_check)
            
            # Check 3: Data integrity
            data_check = self._validate_data_integrity()
            result["checks"].append(data_check)
            
            # All checks must pass
            all_passed = all(check["passed"] for check in result["checks"])
            
            if all_passed:
                result["success"] = True
                result["message"] = "All validation checks passed"
                logger.info(result["message"])
            else:
                failed_checks = [c["name"] for c in result["checks"] if not c["passed"]]
                result["message"] = f"Validation failed: {', '.join(failed_checks)}"
                logger.error(result["message"])
            
        except Exception as e:
            result["message"] = f"Validation failed: {str(e)}"
            logger.error(result["message"], exc_info=True)
        
        return result
    
    def _validate_databases(self) -> Dict[str, Any]:
        """Validate database migration"""
        check = {
            "name": "database_integrity",
            "passed": False,
            "details": {}
        }
        
        try:
            source_dbs = list(self.source_path.glob("**/*.db"))
            target_dbs = list(self.target_path.glob("**/*.db"))
            
            check["details"]["source_count"] = len(source_dbs)
            check["details"]["target_count"] = len(target_dbs)
            
            # Compare record counts
            for source_db in source_dbs:
                relative_path = source_db.relative_to(self.source_path)
                target_db = self.target_path / relative_path
                
                if target_db.exists():
                    source_count = self._count_db_records(source_db)
                    target_count = self._count_db_records(target_db)
                    
                    check["details"][source_db.name] = {
                        "source_records": source_count,
                        "target_records": target_count,
                        "match": source_count == target_count
                    }
            
            # Check if all databases match
            check["passed"] = all(
                db_info.get("match", False) 
                for db_info in check["details"].values() 
                if isinstance(db_info, dict)
            )
            
        except Exception as e:
            check["details"]["error"] = str(e)
            logger.error(f"Database validation error: {str(e)}")
        
        return check
    
    def _count_db_records(self, db_path: Path) -> int:
        """Count total records in a database"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        total = 0
        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                total += cursor.fetchone()[0]
        finally:
            conn.close()
        
        return total
    
    def _validate_file_counts(self) -> Dict[str, Any]:
        """Validate file counts match"""
        check = {
            "name": "file_count",
            "passed": False,
            "details": {}
        }
        
        try:
            source_files = list(self.source_path.rglob("*"))
            target_files = list(self.target_path.rglob("*"))
            
            source_count = sum(1 for f in source_files if f.is_file())
            target_count = sum(1 for f in target_files if f.is_file())
            
            check["details"]["source_files"] = source_count
            check["details"]["target_files"] = target_count
            check["details"]["difference"] = abs(source_count - target_count)
            
            # Allow small difference for generated files
            check["passed"] = check["details"]["difference"] <= 5
            
        except Exception as e:
            check["details"]["error"] = str(e)
            logger.error(f"File count validation error: {str(e)}")
        
        return check
    
    def _validate_data_integrity(self) -> Dict[str, Any]:
        """Validate data integrity using checksums"""
        check = {
            "name": "data_integrity",
            "passed": False,
            "details": {}
        }
        
        try:
            # Compare checksums of critical files
            critical_files = [
                "product_database.db",
                "crm_database.db",
                "settings.json"
            ]
            
            matches = 0
            total = 0
            
            for filename in critical_files:
                source_file = self.source_path / filename
                target_file = self.target_path / filename
                
                if source_file.exists() and target_file.exists():
                    source_hash = self._calculate_file_hash(source_file)
                    target_hash = self._calculate_file_hash(target_file)
                    
                    match = source_hash == target_hash
                    check["details"][filename] = {
                        "source_hash": source_hash[:16],
                        "target_hash": target_hash[:16],
                        "match": match
                    }
                    
                    if match:
                        matches += 1
                    total += 1
            
            check["details"]["matches"] = matches
            check["details"]["total"] = total
            check["passed"] = matches == total if total > 0 else True
            
        except Exception as e:
            check["details"]["error"] = str(e)
            logger.error(f"Data integrity validation error: {str(e)}")
        
        return check
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file"""
        sha256 = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        
        return sha256.hexdigest()
    
    def _rollback_migration(self) -> Dict[str, Any]:
        """Rollback migration in case of failure"""
        logger.warning("Attempting migration rollback")
        
        result = {
            "rollback_attempted": True,
            "success": False,
            "message": ""
        }
        
        try:
            # Remove target directory
            if self.target_path.exists():
                shutil.rmtree(self.target_path)
            
            # Restore from backup
            backup_source = self.backup_path / "source"
            if backup_source.exists():
                shutil.copytree(backup_source, self.target_path)
                result["success"] = True
                result["message"] = "Rollback successful: restored from backup"
                logger.info(result["message"])
            else:
                result["message"] = "Rollback failed: backup not found"
                logger.error(result["message"])
                
        except Exception as e:
            result["message"] = f"Rollback failed: {str(e)}"
            logger.error(result["message"], exc_info=True)
        
        return result
    
    def _save_migration_report(self, report: Dict[str, Any]):
        """Save migration report to file"""
        report_file = self.target_path / "migration_report.json"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Migration report saved: {report_file}")
        except Exception as e:
            logger.error(f"Failed to save migration report: {str(e)}")
