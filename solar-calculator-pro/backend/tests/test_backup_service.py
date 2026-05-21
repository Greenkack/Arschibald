"""
Tests for Backup Service
Requirements: 5.5
"""

import pytest
import tempfile
import shutil
import sqlite3
import json
from pathlib import Path
from backend.services.backup_service import BackupService


@pytest.fixture
def temp_dirs():
    """Create temporary directories for testing"""
    data_dir = Path(tempfile.mkdtemp())
    backup_dir = Path(tempfile.mkdtemp())
    
    # Create test data structure
    (data_dir / "databases").mkdir()
    (data_dir / "settings").mkdir()
    (data_dir / "users").mkdir()
    (data_dir / "projects").mkdir()
    
    # Create test database
    db_path = data_dir / "databases" / "test.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT)")
    cursor.execute("INSERT INTO test_table VALUES (1, 'test')")
    conn.commit()
    conn.close()
    
    # Create test settings file
    settings_path = data_dir / "settings" / "config.json"
    with open(settings_path, 'w') as f:
        json.dump({"test": "value"}, f)
    
    # Create test user file
    user_path = data_dir / "users" / "user1.json"
    with open(user_path, 'w') as f:
        json.dump({"username": "test_user"}, f)
    
    # Create test project file
    project_path = data_dir / "projects" / "project1.json"
    with open(project_path, 'w') as f:
        json.dump({"name": "test_project"}, f)
    
    yield data_dir, backup_dir
    
    # Cleanup
    shutil.rmtree(data_dir)
    shutil.rmtree(backup_dir)


@pytest.fixture
def backup_service(temp_dirs):
    """Create backup service instance"""
    data_dir, backup_dir = temp_dirs
    return BackupService(data_dir, backup_dir)


def test_create_backup_uncompressed(backup_service, temp_dirs):
    """Test creating an uncompressed backup"""
    data_dir, backup_dir = temp_dirs
    
    result = backup_service.create_backup(
        backup_name="test_backup",
        description="Test backup",
        compress=False
    )
    
    assert result["success"] is True
    assert result["backup_name"] == "test_backup"
    assert result["files_backed_up"] > 0
    assert result["total_size_bytes"] > 0
    
    # Verify backup directory exists
    backup_path = backup_dir / "test_backup"
    assert backup_path.exists()
    
    # Verify metadata file exists
    metadata_file = backup_path / "backup_metadata.json"
    assert metadata_file.exists()
    
    # Verify components exist
    assert (backup_path / "databases").exists()
    assert (backup_path / "settings").exists()
    assert (backup_path / "user_data").exists()
    assert (backup_path / "projects").exists()


def test_create_backup_compressed(backup_service, temp_dirs):
    """Test creating a compressed backup"""
    data_dir, backup_dir = temp_dirs
    
    result = backup_service.create_backup(
        backup_name="test_backup_compressed",
        description="Test compressed backup",
        compress=True
    )
    
    assert result["success"] is True
    assert result["compressed"] is True
    assert "compressed_path" in result
    assert "compression_ratio" in result
    
    # Verify ZIP file exists
    zip_path = Path(result["compressed_path"])
    assert zip_path.exists()
    assert zip_path.suffix == ".zip"


def test_create_backup_selective_components(backup_service, temp_dirs):
    """Test creating backup with selective components"""
    data_dir, backup_dir = temp_dirs
    
    result = backup_service.create_backup(
        backup_name="test_backup_selective",
        description="Test selective backup",
        include_databases=True,
        include_settings=False,
        include_user_data=False,
        include_projects=False,
        compress=False
    )
    
    assert result["success"] is True
    assert "databases" in result["components"]
    assert "settings" not in result["components"]
    
    # Verify only databases directory exists
    backup_path = backup_dir / "test_backup_selective"
    assert (backup_path / "databases").exists()
    assert not (backup_path / "settings").exists()


def test_list_backups(backup_service, temp_dirs):
    """Test listing backups"""
    # Create multiple backups
    backup_service.create_backup(backup_name="backup1", compress=False)
    backup_service.create_backup(backup_name="backup2", compress=True)
    
    backups = backup_service.list_backups()
    
    assert len(backups) >= 2
    assert any(b["backup_name"] == "backup1" for b in backups)
    assert any(b["backup_name"] == "backup2" for b in backups)
    
    # Verify backup info structure
    for backup in backups:
        assert "backup_name" in backup
        assert "created_at" in backup
        assert "size_bytes" in backup
        assert "size_formatted" in backup


def test_verify_backup(backup_service, temp_dirs):
    """Test backup verification"""
    # Create a backup
    result = backup_service.create_backup(
        backup_name="test_verify",
        compress=False
    )
    
    assert result["success"] is True
    
    # Verify the backup
    verification = backup_service.verify_backup("test_verify")
    
    assert verification["valid"] is True
    assert len(verification["checks"]) > 0
    
    # Check that all checks passed
    for check in verification["checks"]:
        assert check["passed"] is True


def test_restore_backup(backup_service, temp_dirs):
    """Test backup restoration"""
    data_dir, backup_dir = temp_dirs
    
    # Create a backup
    create_result = backup_service.create_backup(
        backup_name="test_restore",
        compress=False
    )
    
    assert create_result["success"] is True
    
    # Modify original data
    test_file = data_dir / "settings" / "config.json"
    with open(test_file, 'w') as f:
        json.dump({"test": "modified"}, f)
    
    # Restore the backup
    restore_result = backup_service.restore_backup(
        backup_name="test_restore",
        target_path=data_dir,
        verify_before_restore=True
    )
    
    assert restore_result["success"] is True
    assert restore_result["files_restored"] > 0
    
    # Verify data was restored
    with open(test_file, 'r') as f:
        data = json.load(f)
        assert data["test"] == "value"  # Original value


def test_delete_backup(backup_service, temp_dirs):
    """Test backup deletion"""
    data_dir, backup_dir = temp_dirs
    
    # Create a backup
    result = backup_service.create_backup(
        backup_name="test_delete",
        compress=False
    )
    
    assert result["success"] is True
    
    # Verify backup exists
    backup_path = backup_dir / "test_delete"
    assert backup_path.exists()
    
    # Delete the backup
    delete_result = backup_service.delete_backup("test_delete")
    
    assert delete_result["success"] is True
    assert not backup_path.exists()


def test_backup_with_auto_generated_name(backup_service, temp_dirs):
    """Test backup with auto-generated name"""
    result = backup_service.create_backup(
        backup_name=None,  # Auto-generate name
        compress=False
    )
    
    assert result["success"] is True
    assert result["backup_name"].startswith("backup_")
    assert len(result["backup_name"]) > 7  # backup_ + timestamp


def test_verify_nonexistent_backup(backup_service, temp_dirs):
    """Test verifying a non-existent backup"""
    verification = backup_service.verify_backup("nonexistent_backup")
    
    assert verification["valid"] is False
    assert "not found" in verification["message"].lower()


def test_restore_nonexistent_backup(backup_service, temp_dirs):
    """Test restoring a non-existent backup"""
    result = backup_service.restore_backup("nonexistent_backup")
    
    assert result["success"] is False
    assert len(result["errors"]) > 0


def test_delete_nonexistent_backup(backup_service, temp_dirs):
    """Test deleting a non-existent backup"""
    result = backup_service.delete_backup("nonexistent_backup")
    
    assert result["success"] is False
    assert "not found" in result["message"].lower()


def test_backup_metadata_structure(backup_service, temp_dirs):
    """Test backup metadata structure"""
    data_dir, backup_dir = temp_dirs
    
    result = backup_service.create_backup(
        backup_name="test_metadata",
        description="Test metadata",
        compress=False
    )
    
    assert result["success"] is True
    
    # Read metadata file
    metadata_file = backup_dir / "test_metadata" / "backup_metadata.json"
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)
    
    # Verify required fields
    assert "backup_name" in metadata
    assert "timestamp" in metadata
    assert "description" in metadata
    assert "created_at" in metadata
    assert "source_path" in metadata
    assert "components" in metadata
    assert "files_count" in metadata
    assert "total_size_bytes" in metadata


def test_database_integrity_check(backup_service, temp_dirs):
    """Test database integrity verification"""
    # Create a backup
    result = backup_service.create_backup(
        backup_name="test_db_integrity",
        compress=False
    )
    
    assert result["success"] is True
    
    # Verify backup
    verification = backup_service.verify_backup("test_db_integrity")
    
    # Find database integrity check
    db_check = next(
        (c for c in verification["checks"] if c["name"] == "database_integrity"),
        None
    )
    
    assert db_check is not None
    assert db_check["passed"] is True
    assert db_check["details"]["database_count"] > 0


def test_compression_ratio(backup_service, temp_dirs):
    """Test that compression reduces backup size"""
    # Create uncompressed backup
    uncompressed = backup_service.create_backup(
        backup_name="test_uncompressed",
        compress=False
    )
    
    # Create compressed backup
    compressed = backup_service.create_backup(
        backup_name="test_compressed",
        compress=True
    )
    
    assert uncompressed["success"] is True
    assert compressed["success"] is True
    
    # Compressed should be smaller
    assert compressed["compressed_size_bytes"] < uncompressed["total_size_bytes"]
    assert compressed["compression_ratio"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
