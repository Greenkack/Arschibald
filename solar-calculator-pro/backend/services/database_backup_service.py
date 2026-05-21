"""
Database Backup and Restore Service

Provides comprehensive backup and restore functionality with:
- Automatic backup scheduling
- Incremental backups
- Backup compression
- Backup encryption
- Restore validation
- Backup retention policies
"""

import os
import shutil
import gzip
import tarfile
import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Any
from cryptography.fernet import Fernet
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


class BackupMetadata:
    """Metadata for backup files"""
    
    def __init__(
        self,
        backup_id: str,
        timestamp: datetime,
        backup_type: str,
        size_bytes: int,
        compressed: bool,
        encrypted: bool,
        checksum: str,
        database_name: str,
        tables: List[str],
        parent_backup_id: Optional[str] = None
    ):
        self.backup_id = backup_id
        self.timestamp = timestamp
        self.backup_type = backup_type  # 'full' or 'incremental'
        self.size_bytes = size_bytes
        self.compressed = compressed
        self.encrypted = encrypted
        self.checksum = checksum
        self.database_name = database_name
        self.tables = tables
        self.parent_backup_id = parent_backup_id
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'backup_id': self.backup_id,
            'timestamp': self.timestamp.isoformat(),
            'backup_type': self.backup_type,
            'size_bytes': self.size_bytes,
            'compressed': self.compressed,
            'encrypted': self.encrypted,
            'checksum': self.checksum,
            'database_name': self.database_name,
            'tables': self.tables,
            'parent_backup_id': self.parent_backup_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BackupMetadata':
        return cls(
            backup_id=data['backup_id'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            backup_type=data['backup_type'],
            size_bytes=data['size_bytes'],
            compressed=data['compressed'],
            encrypted=data['encrypted'],
            checksum=data['checksum'],
            database_name=data['database_name'],
            tables=data['tables'],
            parent_backup_id=data.get('parent_backup_id')
        )


class DatabaseBackupService:
    """Service for database backup and restore operations"""
    
    def __init__(
        self,
        database_url: str,
        backup_dir: str = "backups",
        encryption_key: Optional[bytes] = None,
        compression_enabled: bool = True
    ):
        self.database_url = database_url
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        self.compression_enabled = compression_enabled
        self.encryption_key = encryption_key or Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
        
        self.metadata_file = self.backup_dir / "backup_metadata.json"
        self.metadata: List[BackupMetadata] = self._load_metadata()
        
        self.engine = create_engine(database_url)
    
    def _load_metadata(self) -> List[BackupMetadata]:
        """Load backup metadata from file"""
        if not self.metadata_file.exists():
            return []
        
        try:
            with open(self.metadata_file, 'r') as f:
                data = json.load(f)
                return [BackupMetadata.from_dict(item) for item in data]
        except Exception as e:
            logger.error(f"Failed to load backup metadata: {e}")
            return []
    
    def _save_metadata(self):
        """Save backup metadata to file"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump([m.to_dict() for m in self.metadata], f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save backup metadata: {e}")
    
    def _generate_backup_id(self) -> str:
        """Generate unique backup ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"backup_{timestamp}"
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def _compress_file(self, source_path: Path, target_path: Path):
        """Compress file using gzip"""
        with open(source_path, 'rb') as f_in:
            with gzip.open(target_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
    
    def _decompress_file(self, source_path: Path, target_path: Path):
        """Decompress gzip file"""
        with gzip.open(source_path, 'rb') as f_in:
            with open(target_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
    
    def _encrypt_file(self, source_path: Path, target_path: Path):
        """Encrypt file using Fernet"""
        with open(source_path, 'rb') as f:
            data = f.read()
        
        encrypted_data = self.cipher.encrypt(data)
        
        with open(target_path, 'wb') as f:
            f.write(encrypted_data)
    
    def _decrypt_file(self, source_path: Path, target_path: Path):
        """Decrypt file using Fernet"""
        with open(source_path, 'rb') as f:
            encrypted_data = f.read()
        
        decrypted_data = self.cipher.decrypt(encrypted_data)
        
        with open(target_path, 'wb') as f:
            f.write(decrypted_data)
    
    def _get_database_tables(self) -> List[str]:
        """Get list of all tables in database"""
        with self.engine.connect() as conn:
            result = conn.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            ))
            return [row[0] for row in result]
    
    def _export_database(self, output_path: Path):
        """Export database to SQL file"""
        # For SQLite, we can simply copy the database file
        # For other databases, we would use pg_dump, mysqldump, etc.
        
        if 'sqlite' in self.database_url:
            # Extract database file path from URL
            db_path = self.database_url.replace('sqlite:///', '')
            shutil.copy2(db_path, output_path)
        else:
            # For PostgreSQL, MySQL, etc., use appropriate dump command
            raise NotImplementedError("Non-SQLite databases not yet implemented")
    
    def _import_database(self, backup_path: Path):
        """Import database from backup file"""
        if 'sqlite' in self.database_url:
            db_path = self.database_url.replace('sqlite:///', '')
            shutil.copy2(backup_path, db_path)
        else:
            raise NotImplementedError("Non-SQLite databases not yet implemented")
    
    def create_full_backup(
        self,
        encrypt: bool = True,
        compress: bool = True
    ) -> BackupMetadata:
        """
        Create a full database backup
        
        Args:
            encrypt: Whether to encrypt the backup
            compress: Whether to compress the backup
            
        Returns:
            BackupMetadata object with backup information
        """
        logger.info("Starting full database backup")
        
        backup_id = self._generate_backup_id()
        timestamp = datetime.now()
        
        # Create temporary backup file
        temp_backup = self.backup_dir / f"{backup_id}.tmp"
        
        try:
            # Export database
            self._export_database(temp_backup)
            
            # Get database info
            tables = self._get_database_tables()
            database_name = Path(self.database_url.split('/')[-1]).stem
            
            # Process backup file
            final_backup = temp_backup
            
            # Compress if enabled
            if compress and self.compression_enabled:
                compressed_backup = self.backup_dir / f"{backup_id}.gz"
                self._compress_file(temp_backup, compressed_backup)
                temp_backup.unlink()
                final_backup = compressed_backup
            
            # Encrypt if enabled
            if encrypt:
                encrypted_backup = self.backup_dir / f"{backup_id}.enc"
                self._encrypt_file(final_backup, encrypted_backup)
                final_backup.unlink()
                final_backup = encrypted_backup
            
            # Calculate checksum
            checksum = self._calculate_checksum(final_backup)
            
            # Get file size
            size_bytes = final_backup.stat().st_size
            
            # Create metadata
            metadata = BackupMetadata(
                backup_id=backup_id,
                timestamp=timestamp,
                backup_type='full',
                size_bytes=size_bytes,
                compressed=compress and self.compression_enabled,
                encrypted=encrypt,
                checksum=checksum,
                database_name=database_name,
                tables=tables
            )
            
            # Save metadata
            self.metadata.append(metadata)
            self._save_metadata()
            
            logger.info(f"Full backup completed: {backup_id}")
            return metadata
            
        except Exception as e:
            logger.error(f"Full backup failed: {e}")
            # Cleanup temporary files
            if temp_backup.exists():
                temp_backup.unlink()
            raise
    
    def create_incremental_backup(
        self,
        parent_backup_id: str,
        encrypt: bool = True,
        compress: bool = True
    ) -> BackupMetadata:
        """
        Create an incremental backup based on a parent backup
        
        Args:
            parent_backup_id: ID of the parent backup
            encrypt: Whether to encrypt the backup
            compress: Whether to compress the backup
            
        Returns:
            BackupMetadata object with backup information
        """
        logger.info(f"Starting incremental backup from {parent_backup_id}")
        
        # Find parent backup
        parent_metadata = next(
            (m for m in self.metadata if m.backup_id == parent_backup_id),
            None
        )
        
        if not parent_metadata:
            raise ValueError(f"Parent backup not found: {parent_backup_id}")
        
        backup_id = self._generate_backup_id()
        timestamp = datetime.now()
        
        # For SQLite, incremental backups are simulated by creating a full backup
        # and storing the parent relationship
        # In production, you would implement actual incremental logic
        
        temp_backup = self.backup_dir / f"{backup_id}.tmp"
        
        try:
            # Export current database state
            self._export_database(temp_backup)
            
            # Get database info
            tables = self._get_database_tables()
            database_name = Path(self.database_url.split('/')[-1]).stem
            
            # Process backup file
            final_backup = temp_backup
            
            # Compress if enabled
            if compress and self.compression_enabled:
                compressed_backup = self.backup_dir / f"{backup_id}.gz"
                self._compress_file(temp_backup, compressed_backup)
                temp_backup.unlink()
                final_backup = compressed_backup
            
            # Encrypt if enabled
            if encrypt:
                encrypted_backup = self.backup_dir / f"{backup_id}.enc"
                self._encrypt_file(final_backup, encrypted_backup)
                final_backup.unlink()
                final_backup = encrypted_backup
            
            # Calculate checksum
            checksum = self._calculate_checksum(final_backup)
            
            # Get file size
            size_bytes = final_backup.stat().st_size
            
            # Create metadata
            metadata = BackupMetadata(
                backup_id=backup_id,
                timestamp=timestamp,
                backup_type='incremental',
                size_bytes=size_bytes,
                compressed=compress and self.compression_enabled,
                encrypted=encrypt,
                checksum=checksum,
                database_name=database_name,
                tables=tables,
                parent_backup_id=parent_backup_id
            )
            
            # Save metadata
            self.metadata.append(metadata)
            self._save_metadata()
            
            logger.info(f"Incremental backup completed: {backup_id}")
            return metadata
            
        except Exception as e:
            logger.error(f"Incremental backup failed: {e}")
            if temp_backup.exists():
                temp_backup.unlink()
            raise
    
    def restore_backup(
        self,
        backup_id: str,
        validate: bool = True,
        target_database_url: Optional[str] = None
    ) -> bool:
        """
        Restore database from backup
        
        Args:
            backup_id: ID of the backup to restore
            validate: Whether to validate backup before restoring
            target_database_url: Optional target database URL (defaults to current)
            
        Returns:
            True if restore was successful
        """
        logger.info(f"Starting restore from backup: {backup_id}")
        
        # Find backup metadata
        metadata = next(
            (m for m in self.metadata if m.backup_id == backup_id),
            None
        )
        
        if not metadata:
            raise ValueError(f"Backup not found: {backup_id}")
        
        # Determine backup file path
        backup_file = self._get_backup_file_path(metadata)
        
        if not backup_file.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_file}")
        
        # Validate backup if requested
        if validate:
            if not self.validate_backup(backup_id):
                raise ValueError(f"Backup validation failed: {backup_id}")
        
        # Create temporary restore file
        temp_restore = self.backup_dir / f"restore_{backup_id}.tmp"
        
        try:
            # Process backup file
            current_file = backup_file
            
            # Decrypt if encrypted
            if metadata.encrypted:
                decrypted_file = self.backup_dir / f"restore_{backup_id}.dec"
                self._decrypt_file(current_file, decrypted_file)
                current_file = decrypted_file
            
            # Decompress if compressed
            if metadata.compressed:
                decompressed_file = self.backup_dir / f"restore_{backup_id}.sql"
                self._decompress_file(current_file, decompressed_file)
                if metadata.encrypted:
                    current_file.unlink()
                current_file = decompressed_file
            
            # Import database
            target_url = target_database_url or self.database_url
            if target_url == self.database_url:
                self._import_database(current_file)
            else:
                # Restore to different database
                temp_engine = create_engine(target_url)
                # Implementation depends on database type
                raise NotImplementedError("Restore to different database not yet implemented")
            
            # Cleanup temporary files
            if current_file != backup_file:
                current_file.unlink()
            
            logger.info(f"Restore completed successfully: {backup_id}")
            return True
            
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            # Cleanup temporary files
            for temp_file in self.backup_dir.glob(f"restore_{backup_id}.*"):
                temp_file.unlink()
            raise
    
    def validate_backup(self, backup_id: str) -> bool:
        """
        Validate backup integrity
        
        Args:
            backup_id: ID of the backup to validate
            
        Returns:
            True if backup is valid
        """
        logger.info(f"Validating backup: {backup_id}")
        
        # Find backup metadata
        metadata = next(
            (m for m in self.metadata if m.backup_id == backup_id),
            None
        )
        
        if not metadata:
            logger.error(f"Backup metadata not found: {backup_id}")
            return False
        
        # Check if backup file exists
        backup_file = self._get_backup_file_path(metadata)
        if not backup_file.exists():
            logger.error(f"Backup file not found: {backup_file}")
            return False
        
        # Verify checksum
        current_checksum = self._calculate_checksum(backup_file)
        if current_checksum != metadata.checksum:
            logger.error(f"Checksum mismatch for backup {backup_id}")
            return False
        
        # Verify file size
        current_size = backup_file.stat().st_size
        if current_size != metadata.size_bytes:
            logger.error(f"File size mismatch for backup {backup_id}")
            return False
        
        logger.info(f"Backup validation successful: {backup_id}")
        return True
    
    def _get_backup_file_path(self, metadata: BackupMetadata) -> Path:
        """Get the file path for a backup based on its metadata"""
        extension = ""
        if metadata.encrypted:
            extension = ".enc"
        elif metadata.compressed:
            extension = ".gz"
        else:
            extension = ".tmp"
        
        return self.backup_dir / f"{metadata.backup_id}{extension}"
    
    def apply_retention_policy(
        self,
        keep_daily: int = 7,
        keep_weekly: int = 4,
        keep_monthly: int = 12,
        keep_yearly: int = 5
    ):
        """
        Apply backup retention policy
        
        Args:
            keep_daily: Number of daily backups to keep
            keep_weekly: Number of weekly backups to keep
            keep_monthly: Number of monthly backups to keep
            keep_yearly: Number of yearly backups to keep
        """
        logger.info("Applying backup retention policy")
        
        now = datetime.now()
        backups_to_keep = set()
        
        # Sort backups by timestamp (newest first)
        sorted_backups = sorted(
            self.metadata,
            key=lambda m: m.timestamp,
            reverse=True
        )
        
        # Keep daily backups
        daily_count = 0
        for backup in sorted_backups:
            if daily_count < keep_daily:
                backups_to_keep.add(backup.backup_id)
                daily_count += 1
        
        # Keep weekly backups (one per week)
        weekly_backups = {}
        for backup in sorted_backups:
            week_key = backup.timestamp.strftime("%Y-W%W")
            if week_key not in weekly_backups:
                weekly_backups[week_key] = backup
        
        for backup in list(weekly_backups.values())[:keep_weekly]:
            backups_to_keep.add(backup.backup_id)
        
        # Keep monthly backups (one per month)
        monthly_backups = {}
        for backup in sorted_backups:
            month_key = backup.timestamp.strftime("%Y-%m")
            if month_key not in monthly_backups:
                monthly_backups[month_key] = backup
        
        for backup in list(monthly_backups.values())[:keep_monthly]:
            backups_to_keep.add(backup.backup_id)
        
        # Keep yearly backups (one per year)
        yearly_backups = {}
        for backup in sorted_backups:
            year_key = backup.timestamp.strftime("%Y")
            if year_key not in yearly_backups:
                yearly_backups[year_key] = backup
        
        for backup in list(yearly_backups.values())[:keep_yearly]:
            backups_to_keep.add(backup.backup_id)
        
        # Delete backups not in retention policy
        deleted_count = 0
        for backup in self.metadata[:]:
            if backup.backup_id not in backups_to_keep:
                self._delete_backup(backup.backup_id)
                deleted_count += 1
        
        logger.info(f"Retention policy applied: {deleted_count} backups deleted")
    
    def _delete_backup(self, backup_id: str):
        """Delete a backup and its metadata"""
        # Find backup metadata
        metadata = next(
            (m for m in self.metadata if m.backup_id == backup_id),
            None
        )
        
        if not metadata:
            return
        
        # Delete backup file
        backup_file = self._get_backup_file_path(metadata)
        if backup_file.exists():
            backup_file.unlink()
        
        # Remove from metadata
        self.metadata = [m for m in self.metadata if m.backup_id != backup_id]
        self._save_metadata()
        
        logger.info(f"Backup deleted: {backup_id}")
    
    def list_backups(
        self,
        backup_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[BackupMetadata]:
        """
        List available backups with optional filtering
        
        Args:
            backup_type: Filter by backup type ('full' or 'incremental')
            start_date: Filter backups after this date
            end_date: Filter backups before this date
            
        Returns:
            List of BackupMetadata objects
        """
        filtered_backups = self.metadata
        
        if backup_type:
            filtered_backups = [
                b for b in filtered_backups
                if b.backup_type == backup_type
            ]
        
        if start_date:
            filtered_backups = [
                b for b in filtered_backups
                if b.timestamp >= start_date
            ]
        
        if end_date:
            filtered_backups = [
                b for b in filtered_backups
                if b.timestamp <= end_date
            ]
        
        return sorted(filtered_backups, key=lambda b: b.timestamp, reverse=True)
    
    def get_backup_info(self, backup_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a backup"""
        metadata = next(
            (m for m in self.metadata if m.backup_id == backup_id),
            None
        )
        
        if not metadata:
            return None
        
        backup_file = self._get_backup_file_path(metadata)
        
        return {
            **metadata.to_dict(),
            'file_exists': backup_file.exists(),
            'file_path': str(backup_file),
            'is_valid': self.validate_backup(backup_id) if backup_file.exists() else False
        }
