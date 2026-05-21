"""
Data Backup Service for Solar Calculator Pro
Provides comprehensive backup, restore, and management functionality
Requirements: 5.5
"""

import sqlite3
import json
import shutil
import zipfile
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib
import os

logger = logging.getLogger(__name__)


class BackupService:
    """Service for managing data backups"""
    
    def __init__(self, data_path: Path, backup_root: Path):
        """
        Initialize backup service
        
        Args:
            data_path: Path to application data directory
            backup_root: Root directory for storing backups
        """
        self.data_path = Path(data_path)
        self.backup_root = Path(backup_root)
        self.backup_root.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Backup Service initialized: data={self.data_path}, backups={self.backup_root}")
    
    def create_backup(
        self,
        backup_name: Optional[str] = None,
        description: str = "",
        include_databases: bool = True,
        include_settings: bool = True,
        include_user_data: bool = True,
        include_projects: bool = True,
        compress: bool = True
    ) -> Dict[str, Any]:
        """
        Create a new backup
        
        Args:
            backup_name: Optional custom backup name (auto-generated if None)
            description: Optional description for the backup
            include_databases: Include database files
            include_settings: Include settings files
            include_user_data: Include user data
            include_projects: Include project data
            compress: Compress backup into ZIP file
        
        Returns:
            Backup result with metadata
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = backup_name or f"backup_{timestamp}"
        backup_dir = self.backup_root / backup_name
        
        logger.info(f"Creating backup: {backup_name}")
        
        result = {
            "backup_name": backup_name,
            "timestamp": timestamp,
            "description": description,
            "success": False,
            "backup_path": str(backup_dir),
            "files_backed_up": 0,
            "total_size_bytes": 0,
            "components": {},
            "errors": []
        }
        
        try:
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Backup databases
            if include_databases:
                db_result = self._backup_databases(backup_dir)
                result["components"]["databases"] = db_result
                result["files_backed_up"] += db_result["files_count"]
                result["total_size_bytes"] += db_result["size_bytes"]
            
            # Backup settings
            if include_settings:
                settings_result = self._backup_settings(backup_dir)
                result["components"]["settings"] = settings_result
                result["files_backed_up"] += settings_result["files_count"]
                result["total_size_bytes"] += settings_result["size_bytes"]
            
            # Backup user data
            if include_user_data:
                user_result = self._backup_user_data(backup_dir)
                result["components"]["user_data"] = user_result
                result["files_backed_up"] += user_result["files_count"]
                result["total_size_bytes"] += user_result["size_bytes"]
            
            # Backup projects
            if include_projects:
                project_result = self._backup_projects(backup_dir)
                result["components"]["projects"] = project_result
                result["files_backed_up"] += project_result["files_count"]
                result["total_size_bytes"] += project_result["size_bytes"]
            
            # Create backup metadata
            metadata = {
                "backup_name": backup_name,
                "timestamp": timestamp,
                "description": description,
                "created_at": datetime.now().isoformat(),
                "source_path": str(self.data_path),
                "components": result["components"],
                "files_count": result["files_backed_up"],
                "total_size_bytes": result["total_size_bytes"]
            }
            
            metadata_file = backup_dir / "backup_metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            # Compress if requested
            if compress:
                zip_result = self._compress_backup(backup_dir)
                result["compressed"] = True
                result["compressed_path"] = zip_result["zip_path"]
                result["compressed_size_bytes"] = zip_result["size_bytes"]
                result["compression_ratio"] = zip_result["compression_ratio"]
            
            result["success"] = True
            result["message"] = f"Backup created successfully: {result['files_backed_up']} files, {self._format_size(result['total_size_bytes'])}"
            logger.info(result["message"])
            
        except Exception as e:
            result["errors"].append(str(e))
            result["message"] = f"Backup failed: {str(e)}"
            logger.error(result["message"], exc_info=True)
        
        return result
    
    def _backup_databases(self, backup_dir: Path) -> Dict[str, Any]:
        """Backup all database files"""
        logger.debug("Backing up databases")
        
        result = {
            "files_count": 0,
            "size_bytes": 0,
            "databases": []
        }
        
        db_backup_dir = backup_dir / "databases"
        db_backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Find all database files
        db_files = list(self.data_path.glob("**/*.db"))
        
        for db_file in db_files:
            try:
                # Calculate relative path
                relative_path = db_file.relative_to(self.data_path)
                target_file = db_backup_dir / relative_path
                target_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy database file
                shutil.copy2(db_file, target_file)
                
                file_size = target_file.stat().st_size
                result["files_count"] += 1
                result["size_bytes"] += file_size
                
                result["databases"].append({
                    "name": db_file.name,
                    "path": str(relative_path),
                    "size_bytes": file_size
                })
                
                logger.debug(f"Backed up database: {db_file.name}")
                
            except Exception as e:
                logger.error(f"Failed to backup database {db_file.name}: {str(e)}")
        
        return result
    
    def _backup_settings(self, backup_dir: Path) -> Dict[str, Any]:
        """Backup settings files"""
        logger.debug("Backing up settings")
        
        result = {
            "files_count": 0,
            "size_bytes": 0,
            "settings": []
        }
        
        settings_backup_dir = backup_dir / "settings"
        settings_backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Find settings files
        settings_patterns = ["**/*.json", "**/*.yaml", "**/*.yml", "**/*.ini", "**/*.conf", "**/.env"]
        settings_files = []
        
        for pattern in settings_patterns:
            settings_files.extend(self.data_path.glob(pattern))
        
        # Remove duplicates and database files
        settings_files = [f for f in set(settings_files) if f.suffix != '.db']
        
        for settings_file in settings_files:
            try:
                relative_path = settings_file.relative_to(self.data_path)
                target_file = settings_backup_dir / relative_path
                target_file.parent.mkdir(parents=True, exist_ok=True)
                
                shutil.copy2(settings_file, target_file)
                
                file_size = target_file.stat().st_size
                result["files_count"] += 1
                result["size_bytes"] += file_size
                
                result["settings"].append({
                    "name": settings_file.name,
                    "path": str(relative_path),
                    "size_bytes": file_size
                })
                
                logger.debug(f"Backed up settings: {settings_file.name}")
                
            except Exception as e:
                logger.error(f"Failed to backup settings {settings_file.name}: {str(e)}")
        
        return result
    
    def _backup_user_data(self, backup_dir: Path) -> Dict[str, Any]:
        """Backup user data"""
        logger.debug("Backing up user data")
        
        result = {
            "files_count": 0,
            "size_bytes": 0,
            "users": []
        }
        
        user_backup_dir = backup_dir / "user_data"
        user_backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Find user data directories
        user_dirs = [
            self.data_path / "users",
            self.data_path / "profiles",
            self.data_path / "uploads"
        ]
        
        for user_dir in user_dirs:
            if user_dir.exists():
                try:
                    target_dir = user_backup_dir / user_dir.name
                    shutil.copytree(user_dir, target_dir, dirs_exist_ok=True)
                    
                    # Count files and size
                    for file_path in target_dir.rglob("*"):
                        if file_path.is_file():
                            result["files_count"] += 1
                            result["size_bytes"] += file_path.stat().st_size
                    
                    logger.debug(f"Backed up user directory: {user_dir.name}")
                    
                except Exception as e:
                    logger.error(f"Failed to backup user directory {user_dir.name}: {str(e)}")
        
        return result
    
    def _backup_projects(self, backup_dir: Path) -> Dict[str, Any]:
        """Backup project data"""
        logger.debug("Backing up projects")
        
        result = {
            "files_count": 0,
            "size_bytes": 0,
            "projects": []
        }
        
        project_backup_dir = backup_dir / "projects"
        project_backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Find project directories
        project_dirs = [
            self.data_path / "projects",
            self.data_path / "data"
        ]
        
        for project_dir in project_dirs:
            if project_dir.exists():
                try:
                    target_dir = project_backup_dir / project_dir.name
                    shutil.copytree(project_dir, target_dir, dirs_exist_ok=True)
                    
                    # Count files and size
                    for file_path in target_dir.rglob("*"):
                        if file_path.is_file():
                            result["files_count"] += 1
                            result["size_bytes"] += file_path.stat().st_size
                    
                    logger.debug(f"Backed up project directory: {project_dir.name}")
                    
                except Exception as e:
                    logger.error(f"Failed to backup project directory {project_dir.name}: {str(e)}")
        
        return result
    
    def _compress_backup(self, backup_dir: Path) -> Dict[str, Any]:
        """Compress backup directory into ZIP file"""
        logger.debug(f"Compressing backup: {backup_dir.name}")
        
        zip_path = backup_dir.parent / f"{backup_dir.name}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in backup_dir.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(backup_dir.parent)
                    zipf.write(file_path, arcname)
        
        # Calculate compression ratio
        original_size = sum(f.stat().st_size for f in backup_dir.rglob("*") if f.is_file())
        compressed_size = zip_path.stat().st_size
        compression_ratio = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
        
        # Don't remove uncompressed directory in case it's needed
        # shutil.rmtree(backup_dir)
        
        logger.info(f"Backup compressed: {self._format_size(compressed_size)} ({compression_ratio:.1f}% reduction)")
        
        return {
            "zip_path": str(zip_path),
            "size_bytes": compressed_size,
            "compression_ratio": compression_ratio
        }
    
    def restore_backup(
        self,
        backup_name: str,
        target_path: Optional[Path] = None,
        verify_before_restore: bool = True
    ) -> Dict[str, Any]:
        """
        Restore data from a backup
        
        Args:
            backup_name: Name of backup to restore
            target_path: Target path for restoration (defaults to original data path)
            verify_before_restore: Verify backup integrity before restoring
        
        Returns:
            Restoration result
        """
        logger.info(f"Restoring backup: {backup_name}")
        
        target_path = target_path or self.data_path
        
        result = {
            "backup_name": backup_name,
            "success": False,
            "files_restored": 0,
            "errors": []
        }
        
        try:
            # Find backup
            backup_path = self._find_backup(backup_name)
            if not backup_path:
                raise FileNotFoundError(f"Backup not found: {backup_name}")
            
            # Extract if compressed
            if backup_path.suffix == '.zip':
                backup_dir = self._extract_backup(backup_path)
            else:
                backup_dir = backup_path
            
            # Verify backup if requested
            if verify_before_restore:
                verification = self.verify_backup(backup_name)
                if not verification["valid"]:
                    raise ValueError(f"Backup verification failed: {verification['message']}")
            
            # Create backup of current data before restoring
            pre_restore_backup = self.create_backup(
                backup_name=f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                description=f"Automatic backup before restoring {backup_name}",
                compress=True
            )
            
            if not pre_restore_backup["success"]:
                logger.warning("Failed to create pre-restore backup")
            
            # Restore data
            for component_dir in backup_dir.iterdir():
                if component_dir.is_dir() and component_dir.name not in ["backup_metadata.json", backup_dir.name]:
                    # Map backup component names to target paths
                    component_name = component_dir.name
                    
                    # Handle nested structure from backup
                    if component_name in ["databases", "settings", "user_data", "projects"]:
                        # Copy contents of component directory to target
                        for item in component_dir.iterdir():
                            if item.is_dir():
                                target_item = target_path / item.name
                                # Remove existing data
                                if target_item.exists():
                                    shutil.rmtree(target_item)
                                # Copy backup data
                                shutil.copytree(item, target_item)
                                # Count restored files
                                files_count = sum(1 for _ in target_item.rglob("*") if _.is_file())
                                result["files_restored"] += files_count
                                logger.debug(f"Restored {item.name}: {files_count} files")
                            elif item.is_file():
                                target_item = target_path / item.name
                                shutil.copy2(item, target_item)
                                result["files_restored"] += 1
                                logger.debug(f"Restored file: {item.name}")
            
            result["success"] = True
            result["message"] = f"Backup restored successfully: {result['files_restored']} files"
            result["pre_restore_backup"] = pre_restore_backup["backup_name"]
            logger.info(result["message"])
            
        except Exception as e:
            result["errors"].append(str(e))
            result["message"] = f"Restore failed: {str(e)}"
            logger.error(result["message"], exc_info=True)
        
        return result
    
    def verify_backup(self, backup_name: str) -> Dict[str, Any]:
        """
        Verify backup integrity
        
        Args:
            backup_name: Name of backup to verify
        
        Returns:
            Verification result
        """
        logger.info(f"Verifying backup: {backup_name}")
        
        result = {
            "backup_name": backup_name,
            "valid": False,
            "checks": [],
            "message": ""
        }
        
        try:
            # Find backup
            backup_path = self._find_backup(backup_name)
            if not backup_path:
                raise FileNotFoundError(f"Backup not found: {backup_name}")
            
            # Extract if compressed
            if backup_path.suffix == '.zip':
                backup_dir = self._extract_backup(backup_path, temp=True)
            else:
                backup_dir = backup_path
            
            # Check 1: Metadata exists
            metadata_check = self._verify_metadata(backup_dir)
            result["checks"].append(metadata_check)
            
            # Check 2: File integrity
            integrity_check = self._verify_file_integrity(backup_dir)
            result["checks"].append(integrity_check)
            
            # Check 3: Database integrity
            db_check = self._verify_database_integrity(backup_dir)
            result["checks"].append(db_check)
            
            # All checks must pass
            all_passed = all(check["passed"] for check in result["checks"])
            
            if all_passed:
                result["valid"] = True
                result["message"] = "Backup verification passed"
                logger.info(result["message"])
            else:
                failed_checks = [c["name"] for c in result["checks"] if not c["passed"]]
                result["message"] = f"Backup verification failed: {', '.join(failed_checks)}"
                logger.warning(result["message"])
            
        except Exception as e:
            result["message"] = f"Verification error: {str(e)}"
            logger.error(result["message"], exc_info=True)
        
        return result
    
    def _verify_metadata(self, backup_dir: Path) -> Dict[str, Any]:
        """Verify backup metadata"""
        check = {
            "name": "metadata",
            "passed": False,
            "details": {}
        }
        
        try:
            metadata_file = backup_dir / "backup_metadata.json"
            
            if not metadata_file.exists():
                check["details"]["error"] = "Metadata file not found"
                return check
            
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Check required fields
            required_fields = ["backup_name", "timestamp", "created_at", "components"]
            missing_fields = [f for f in required_fields if f not in metadata]
            
            if missing_fields:
                check["details"]["missing_fields"] = missing_fields
                return check
            
            check["passed"] = True
            check["details"]["metadata"] = metadata
            
        except Exception as e:
            check["details"]["error"] = str(e)
        
        return check
    
    def _verify_file_integrity(self, backup_dir: Path) -> Dict[str, Any]:
        """Verify file integrity"""
        check = {
            "name": "file_integrity",
            "passed": False,
            "details": {}
        }
        
        try:
            # Count files in backup
            file_count = sum(1 for _ in backup_dir.rglob("*") if _.is_file())
            
            check["details"]["file_count"] = file_count
            check["passed"] = file_count > 0
            
        except Exception as e:
            check["details"]["error"] = str(e)
        
        return check
    
    def _verify_database_integrity(self, backup_dir: Path) -> Dict[str, Any]:
        """Verify database integrity"""
        check = {
            "name": "database_integrity",
            "passed": False,
            "details": {}
        }
        
        try:
            db_dir = backup_dir / "databases"
            
            if not db_dir.exists():
                check["details"]["warning"] = "No databases in backup"
                check["passed"] = True  # Not an error if no databases
                return check
            
            db_files = list(db_dir.glob("**/*.db"))
            check["details"]["database_count"] = len(db_files)
            
            # Test each database
            valid_dbs = 0
            for db_file in db_files:
                try:
                    conn = sqlite3.connect(db_file)
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = cursor.fetchall()
                    conn.close()
                    
                    if tables:
                        valid_dbs += 1
                except Exception as e:
                    check["details"][f"error_{db_file.name}"] = str(e)
            
            check["details"]["valid_databases"] = valid_dbs
            check["passed"] = valid_dbs == len(db_files)
            
        except Exception as e:
            check["details"]["error"] = str(e)
        
        return check
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        List all available backups
        
        Returns:
            List of backup information
        """
        logger.debug("Listing backups")
        
        backups = []
        
        try:
            for item in self.backup_root.iterdir():
                if item.is_dir() or item.suffix == '.zip':
                    backup_info = self._get_backup_info(item)
                    if backup_info:
                        backups.append(backup_info)
            
            # Sort by creation time (newest first)
            backups.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to list backups: {str(e)}")
        
        return backups
    
    def _get_backup_info(self, backup_path: Path) -> Optional[Dict[str, Any]]:
        """Get information about a backup"""
        try:
            # Extract if compressed
            if backup_path.suffix == '.zip':
                backup_dir = self._extract_backup(backup_path, temp=True)
                is_compressed = True
            else:
                backup_dir = backup_path
                is_compressed = False
            
            # Read metadata
            metadata_file = backup_dir / "backup_metadata.json"
            
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                # Add file system info
                if is_compressed:
                    size_bytes = backup_path.stat().st_size
                else:
                    size_bytes = sum(f.stat().st_size for f in backup_dir.rglob("*") if f.is_file())
                
                metadata["size_bytes"] = size_bytes
                metadata["size_formatted"] = self._format_size(size_bytes)
                metadata["is_compressed"] = is_compressed
                metadata["backup_path"] = str(backup_path)
                
                return metadata
            
        except Exception as e:
            logger.error(f"Failed to get backup info for {backup_path.name}: {str(e)}")
        
        return None
    
    def delete_backup(self, backup_name: str) -> Dict[str, Any]:
        """
        Delete a backup
        
        Args:
            backup_name: Name of backup to delete
        
        Returns:
            Deletion result
        """
        logger.info(f"Deleting backup: {backup_name}")
        
        result = {
            "backup_name": backup_name,
            "success": False,
            "message": ""
        }
        
        try:
            backup_path = self._find_backup(backup_name)
            
            if not backup_path:
                raise FileNotFoundError(f"Backup not found: {backup_name}")
            
            # Delete backup
            if backup_path.is_dir():
                shutil.rmtree(backup_path)
            else:
                backup_path.unlink()
            
            result["success"] = True
            result["message"] = f"Backup deleted: {backup_name}"
            logger.info(result["message"])
            
        except Exception as e:
            result["message"] = f"Delete failed: {str(e)}"
            logger.error(result["message"], exc_info=True)
        
        return result
    
    def _find_backup(self, backup_name: str) -> Optional[Path]:
        """Find backup by name"""
        # Check for directory
        backup_dir = self.backup_root / backup_name
        if backup_dir.exists():
            return backup_dir
        
        # Check for ZIP file
        backup_zip = self.backup_root / f"{backup_name}.zip"
        if backup_zip.exists():
            return backup_zip
        
        return None
    
    def _extract_backup(self, zip_path: Path, temp: bool = False) -> Path:
        """Extract compressed backup"""
        if temp:
            extract_dir = self.backup_root / f"temp_{zip_path.stem}"
        else:
            extract_dir = self.backup_root / zip_path.stem
        
        # Remove existing directory
        if extract_dir.exists():
            shutil.rmtree(extract_dir)
        
        extract_dir.mkdir(parents=True, exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zipf.extractall(extract_dir)
        
        return extract_dir
    
    def _format_size(self, size_bytes: int) -> str:
        """Format size in bytes to human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
