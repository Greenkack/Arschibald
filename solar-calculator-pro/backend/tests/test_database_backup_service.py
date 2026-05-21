"""
Tests for Database Backup and Restore Service
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from ..services.database_backup_service import DatabaseBackupService, BackupMetadata

Base = declarative_base()


class TestModel(Base):
    """Test database model"""
    __tablename__ = 'test_table'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    value = Column(Integer)


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def test_database(temp_dir):
    """Create test database"""
    db_path = temp_dir / "test.db"
    database_url = f"sqlite:///{db_path}"
    
    # Create database and tables
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    
    # Add test data
    Session = sessionmaker(bind=engine)
    session = Session()
    
    session.add(TestModel(id=1, name="Test 1", value=100))
    session.add(TestModel(id=2, name="Test 2", value=200))
    session.add(TestModel(id=3, name="Test 3", value=300))
    
    session.commit()
    session.close()
    
    yield database_url
    
    engine.dispose()


@pytest.fixture
def backup_service(test_database, temp_dir):
    """Create backup service instance"""
    backup_dir = temp_dir / "backups"
    service = DatabaseBackupService(
        database_url=test_database,
        backup_dir=str(backup_dir),
        compression_enabled=True
    )
    return service


class TestDatabaseBackupService:
    """Test suite for DatabaseBackupService"""
    
    def test_create_full_backup(self, backup_service):
        """Test creating a full backup"""
        metadata = backup_service.create_full_backup(
            encrypt=True,
            compress=True
        )
        
        assert metadata is not None
        assert metadata.backup_type == 'full'
        assert metadata.compressed is True
        assert metadata.encrypted is True
        assert metadata.size_bytes > 0
        assert len(metadata.tables) > 0
        assert metadata.checksum is not None
    
    def test_create_full_backup_uncompressed(self, backup_service):
        """Test creating an uncompressed backup"""
        metadata = backup_service.create_full_backup(
            encrypt=False,
            compress=False
        )
        
        assert metadata is not None
        assert metadata.compressed is False
        assert metadata.encrypted is False
    
    def test_create_incremental_backup(self, backup_service):
        """Test creating an incremental backup"""
        # Create full backup first
        full_metadata = backup_service.create_full_backup()
        
        # Create incremental backup
        incremental_metadata = backup_service.create_incremental_backup(
            parent_backup_id=full_metadata.backup_id,
            encrypt=True,
            compress=True
        )
        
        assert incremental_metadata is not None
        assert incremental_metadata.backup_type == 'incremental'
        assert incremental_metadata.parent_backup_id == full_metadata.backup_id
    
    def test_validate_backup(self, backup_service):
        """Test backup validation"""
        metadata = backup_service.create_full_backup()
        
        is_valid = backup_service.validate_backup(metadata.backup_id)
        
        assert is_valid is True
    
    def test_validate_nonexistent_backup(self, backup_service):
        """Test validation of nonexistent backup"""
        is_valid = backup_service.validate_backup("nonexistent_backup")
        
        assert is_valid is False
    
    def test_restore_backup(self, backup_service, test_database, temp_dir):
        """Test restoring from backup"""
        # Create backup
        metadata = backup_service.create_full_backup()
        
        # Modify database
        engine = create_engine(test_database)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        session.query(TestModel).delete()
        session.commit()
        session.close()
        
        # Verify data is deleted
        session = Session()
        count = session.query(TestModel).count()
        assert count == 0
        session.close()
        
        # Restore backup
        success = backup_service.restore_backup(
            backup_id=metadata.backup_id,
            validate=True
        )
        
        assert success is True
        
        # Verify data is restored
        session = Session()
        count = session.query(TestModel).count()
        assert count == 3
        session.close()
        
        engine.dispose()
    
    def test_list_backups(self, backup_service):
        """Test listing backups"""
        # Create multiple backups
        backup1 = backup_service.create_full_backup()
        backup2 = backup_service.create_full_backup()
        
        # List all backups
        backups = backup_service.list_backups()
        
        assert len(backups) >= 2
        assert any(b.backup_id == backup1.backup_id for b in backups)
        assert any(b.backup_id == backup2.backup_id for b in backups)
    
    def test_list_backups_filtered(self, backup_service):
        """Test listing backups with filters"""
        # Create full and incremental backups
        full_backup = backup_service.create_full_backup()
        incremental_backup = backup_service.create_incremental_backup(
            parent_backup_id=full_backup.backup_id
        )
        
        # Filter by type
        full_backups = backup_service.list_backups(backup_type='full')
        incremental_backups = backup_service.list_backups(backup_type='incremental')
        
        assert len(full_backups) >= 1
        assert len(incremental_backups) >= 1
        assert all(b.backup_type == 'full' for b in full_backups)
        assert all(b.backup_type == 'incremental' for b in incremental_backups)
    
    def test_get_backup_info(self, backup_service):
        """Test getting backup information"""
        metadata = backup_service.create_full_backup()
        
        info = backup_service.get_backup_info(metadata.backup_id)
        
        assert info is not None
        assert info['backup_id'] == metadata.backup_id
        assert info['file_exists'] is True
        assert info['is_valid'] is True
    
    def test_delete_backup(self, backup_service):
        """Test deleting a backup"""
        metadata = backup_service.create_full_backup()
        
        # Verify backup exists
        info = backup_service.get_backup_info(metadata.backup_id)
        assert info is not None
        
        # Delete backup
        backup_service._delete_backup(metadata.backup_id)
        
        # Verify backup is deleted
        info = backup_service.get_backup_info(metadata.backup_id)
        assert info is None
    
    def test_retention_policy(self, backup_service):
        """Test backup retention policy"""
        # Create multiple backups with different timestamps
        backups = []
        for i in range(10):
            metadata = backup_service.create_full_backup()
            # Manually adjust timestamp for testing
            metadata.timestamp = datetime.now() - timedelta(days=i)
            backups.append(metadata)
        
        # Update metadata
        backup_service.metadata = backups
        backup_service._save_metadata()
        
        # Apply retention policy (keep only 5 daily backups)
        backup_service.apply_retention_policy(
            keep_daily=5,
            keep_weekly=0,
            keep_monthly=0,
            keep_yearly=0
        )
        
        # Verify only 5 backups remain
        remaining_backups = backup_service.list_backups()
        assert len(remaining_backups) <= 5
    
    def test_checksum_validation(self, backup_service):
        """Test checksum validation"""
        metadata = backup_service.create_full_backup()
        
        # Get backup file
        backup_file = backup_service._get_backup_file_path(metadata)
        
        # Corrupt the file
        with open(backup_file, 'ab') as f:
            f.write(b'corrupted data')
        
        # Validation should fail
        is_valid = backup_service.validate_backup(metadata.backup_id)
        assert is_valid is False
    
    def test_encryption_decryption(self, backup_service, temp_dir):
        """Test file encryption and decryption"""
        # Create test file
        test_file = temp_dir / "test.txt"
        test_data = b"Test data for encryption"
        with open(test_file, 'wb') as f:
            f.write(test_data)
        
        # Encrypt file
        encrypted_file = temp_dir / "test.enc"
        backup_service._encrypt_file(test_file, encrypted_file)
        
        # Verify encrypted file is different
        with open(encrypted_file, 'rb') as f:
            encrypted_data = f.read()
        assert encrypted_data != test_data
        
        # Decrypt file
        decrypted_file = temp_dir / "test.dec"
        backup_service._decrypt_file(encrypted_file, decrypted_file)
        
        # Verify decrypted data matches original
        with open(decrypted_file, 'rb') as f:
            decrypted_data = f.read()
        assert decrypted_data == test_data
    
    def test_compression_decompression(self, backup_service, temp_dir):
        """Test file compression and decompression"""
        # Create test file
        test_file = temp_dir / "test.txt"
        test_data = b"Test data for compression" * 100
        with open(test_file, 'wb') as f:
            f.write(test_data)
        
        # Compress file
        compressed_file = temp_dir / "test.gz"
        backup_service._compress_file(test_file, compressed_file)
        
        # Verify compressed file is smaller
        original_size = test_file.stat().st_size
        compressed_size = compressed_file.stat().st_size
        assert compressed_size < original_size
        
        # Decompress file
        decompressed_file = temp_dir / "test.dec"
        backup_service._decompress_file(compressed_file, decompressed_file)
        
        # Verify decompressed data matches original
        with open(decompressed_file, 'rb') as f:
            decompressed_data = f.read()
        assert decompressed_data == test_data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
