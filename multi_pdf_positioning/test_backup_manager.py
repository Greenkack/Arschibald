"""
Tests for Backup Manager

Tests backup creation, restoration, listing, and validation functionality.
"""
import os
import shutil
import tempfile
from pathlib import Path
import pytest
import yaml

from multi_pdf_positioning.backup_manager import BackupManager, create_backup, restore_backup, list_backups, validate_backup


@pytest.fixture
def temp_dirs():
    """Create temporary directories for testing"""
    temp_dir = Path(tempfile.mkdtemp())
    yml_dir = temp_dir / "coords_multi"
    backup_dir = temp_dir / "coords_multi_backup"
    
    yml_dir.mkdir(parents=True, exist_ok=True)
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    yield yml_dir, backup_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_yml_files(temp_dirs):
    """Create sample YML files for testing"""
    yml_dir, _ = temp_dirs
    
    files = []
    for i in range(1, 4):
        yml_file = yml_dir / f"seite{i}_f1.yml"
        content = {
            "text": f"Test Text {i}",
            "position": [100.0, 200.0, 300.0, 400.0],
            "font": "Helvetica",
            "font_size": 12.0,
            "color": 0
        }
        with open(yml_file, 'w', encoding='utf-8') as f:
            yaml.dump(content, f)
        files.append(yml_file)
    
    return files


def test_backup_manager_initialization(temp_dirs):
    """Test BackupManager initialization"""
    yml_dir, backup_dir = temp_dirs
    
    manager = BackupManager(yml_dir, backup_dir)
    
    assert manager.yml_dir == yml_dir
    assert manager.backup_dir == backup_dir
    assert backup_dir.exists()


def test_create_backup_all_files(temp_dirs, sample_yml_files):
    """Test creating backup of all YML files"""
    yml_dir, backup_dir = temp_dirs
    
    manager = BackupManager(yml_dir, backup_dir)
    backup_id = manager.create_backup()
    
    # Check backup was created
    assert backup_id.startswith("backup_")
    backup_path = backup_dir / backup_id
    assert backup_path.exists()
    
    # Check manifest exists
    manifest_path = backup_path / "backup_manifest.yml"
    assert manifest_path.exists()
    
    # Check manifest content
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = yaml.safe_load(f)
    
    assert manifest["backup_id"] == backup_id
    assert manifest["files_count"] == 3
    assert len(manifest["files"]) == 3
    
    # Check files were copied
    for yml_file in sample_yml_files:
        backup_file = backup_path / yml_file.name
        assert backup_file.exists()


def test_create_backup_specific_files(temp_dirs, sample_yml_files):
    """Test creating backup of specific YML files"""
    yml_dir, backup_dir = temp_dirs
    
    manager = BackupManager(yml_dir, backup_dir)
    
    # Backup only first two files
    files_to_backup = sample_yml_files[:2]
    backup_id = manager.create_backup(files_to_backup)
    
    backup_path = backup_dir / backup_id
    
    # Check only specified files were backed up
    backed_up_files = list(backup_path.glob("*.yml"))
    backed_up_files = [f for f in backed_up_files if f.name != "backup_manifest.yml"]
    
    assert len(backed_up_files) == 2


def test_list_backups_empty(temp_dirs):
    """Test listing backups when none exist"""
    yml_dir, backup_dir = temp_dirs
    
    manager = BackupManager(yml_dir, backup_dir)
    backups = manager.list_backups()
    
    assert backups == []


def test_list_backups_multiple(temp_dirs, sample_yml_files):
    """Test listing multiple backups"""
    yml_dir, backup_dir = temp_dirs
    
    manager = BackupManager(yml_dir, backup_dir)
    
    # Create multiple backups
    backup_id1 = manager.create_backup()
    backup_id2 = manager.create_backup()
    
    backups = manager.list_backups()
    
    assert len(backups) == 2
    assert backups[0]["backup_id"] == backup_id2  # Most recent first
    assert backups[1]["backup_id"] == backup_id1


def test_validate_backup_valid(temp_dirs, sample_yml_files):
    """Test validating a valid backup"""
    yml_dir, backup_dir = temp_dirs
    
    manager = BackupManager(yml_dir, backup_dir)
    backup_id = manager.create_backup()
    
    validation = manager.validate_backup(backup_id)
    
    assert validation["valid"] is True
    assert validation["exists"] is True
    assert validation["manifest_valid"] is True
    assert validation["files_valid"] is True
    assert len(validation["errors"]) == 0


def test_validate_backup_not_exists(temp_dirs):
    """Test validating a non-existent backup"""
    yml_dir, backup_dir = temp_dirs
    
    manager = BackupManager(yml_dir, backup_dir)
    validation = manager.validate_backup("backup_nonexistent")
    
    assert validation["valid"] is False
    assert validation["exists"] is False
    assert len(validation["errors"]) > 0


def test_validate_backup_no_manifest(temp_dirs, sample_yml_files):
    """Test validating backup without manifest"""
    yml_dir, backup_dir = temp_dirs
    
    manager = BackupManager(yml_dir, backup_dir)
    backup_id = manager.create_backup()
    
    # Remove manifest
    backup_path = backup_dir / backup_id
    manifest_path = backup_path / "backup_manifest.yml"
    manifest_path.unlink()
    
    validation = manager.validate_backup(backup_id)
    
    assert validation["exists"] is True
    assert validation["manifest_valid"] is False
    assert len(validation["warnings"]) > 0


def test_restore_backup_dry_run(temp_dirs, sample_yml_files):
    """Test restore backup in dry-run mode"""
    yml_dir, backup_dir = temp_dirs
    
    manager = BackupManager(yml_dir, backup_dir)
    backup_id = manager.create_backup()
    
    # Modify original files
    for yml_file in sample_yml_files:
        with open(yml_file, 'w', encoding='utf-8') as f:
            yaml.dump({"modified": True}, f)
    
    # Dry run should not restore
    result = manager.restore_backup(backup_id, confirm=False)
    
    assert result is False
    
    # Files should still be modified
    with open(sample_yml_files[0], 'r', encoding='utf-8') as f:
        content = yaml.safe_load(f)
    assert content.get("modified") is True


def test_restore_backup_confirmed(temp_dirs, sample_yml_files):
    """Test restore backup with confirmation"""
    yml_dir, backup_dir = temp_dirs
    
    manager = BackupManager(yml_dir, backup_dir)
    
    # Get original content
    with open(sample_yml_files[0], 'r', encoding='utf-8') as f:
        original_content = yaml.safe_load(f)
    
    backup_id = manager.create_backup()
    
    # Modify original files
    for yml_file in sample_yml_files:
        with open(yml_file, 'w', encoding='utf-8') as f:
            yaml.dump({"modified": True}, f)
    
    # Restore with confirmation
    result = manager.restore_backup(backup_id, confirm=True)
    
    assert result is True
    
    # Files should be restored
    with open(sample_yml_files[0], 'r', encoding='utf-8') as f:
        restored_content = yaml.safe_load(f)
    
    assert restored_content == original_content
    assert restored_content.get("modified") is None


def test_restore_backup_creates_backup(temp_dirs, sample_yml_files):
    """Test that restore creates backup of current state"""
    yml_dir, backup_dir = temp_dirs
    
    manager = BackupManager(yml_dir, backup_dir)
    
    # Create initial backup
    backup_id1 = manager.create_backup()
    
    # Modify files
    for yml_file in sample_yml_files:
        with open(yml_file, 'w', encoding='utf-8') as f:
            yaml.dump({"modified": True}, f)
    
    # Count backups before restore
    backups_before = len(manager.list_backups())
    
    # Restore (creates backup of current state)
    manager.restore_backup(backup_id1, confirm=True)
    
    # Should have one more backup
    backups_after = len(manager.list_backups())
    assert backups_after == backups_before + 1


def test_convenience_functions(temp_dirs, sample_yml_files):
    """Test convenience functions"""
    yml_dir, backup_dir = temp_dirs
    
    # Test create_backup
    backup_id = create_backup(yml_dir=yml_dir, backup_dir=backup_dir)
    assert backup_id.startswith("backup_")
    
    # Test list_backups
    backups = list_backups(backup_dir=backup_dir)
    assert len(backups) == 1
    
    # Test validate_backup
    validation = validate_backup(backup_id, backup_dir=backup_dir)
    assert validation["valid"] is True
    
    # Test restore_backup (dry run)
    result = restore_backup(backup_id, confirm=False, yml_dir=yml_dir, backup_dir=backup_dir)
    assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
