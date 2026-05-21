"""
Demo: Backup Manager Usage

This script demonstrates how to use the Backup Manager to:
1. Create backups of YML files
2. List available backups
3. Validate backup integrity
4. Restore backups

Requirements: 8.1, 8.2, 8.3, 8.4, 8.5
"""
from pathlib import Path
from backup_manager import BackupManager, create_backup, restore_backup, list_backups, validate_backup
from config import YML_DIR, BACKUP_DIR


def demo_create_backup():
    """Demonstrate creating a backup"""
    print("=" * 60)
    print("DEMO 1: Creating Backup")
    print("=" * 60)
    
    manager = BackupManager(YML_DIR, BACKUP_DIR)
    
    # Create backup of all YML files
    print("\n1. Creating backup of all YML files...")
    backup_id = manager.create_backup()
    
    print(f"\nBackup created successfully!")
    print(f"  Backup ID: {backup_id}")
    
    return backup_id


def demo_list_backups():
    """Demonstrate listing backups"""
    print("\n" + "=" * 60)
    print("DEMO 2: Listing Backups")
    print("=" * 60)
    
    manager = BackupManager(YML_DIR, BACKUP_DIR)
    
    backups = manager.list_backups()
    
    if not backups:
        print("\nNo backups found.")
        return
    
    print(f"\nFound {len(backups)} backup(s):\n")
    
    for i, backup in enumerate(backups, 1):
        print(f"{i}. Backup ID: {backup['backup_id']}")
        print(f"   Timestamp: {backup.get('timestamp', 'unknown')}")
        print(f"   Files: {backup.get('files_count', 0)}")
        if 'error' in backup:
            print(f"   Error: {backup['error']}")
        print()


def demo_validate_backup(backup_id: str):
    """Demonstrate validating a backup"""
    print("\n" + "=" * 60)
    print("DEMO 3: Validating Backup")
    print("=" * 60)
    
    manager = BackupManager(YML_DIR, BACKUP_DIR)
    
    print(f"\nValidating backup: {backup_id}")
    validation = manager.validate_backup(backup_id)
    
    print(f"\nValidation Results:")
    print(f"  Valid: {validation['valid']}")
    print(f"  Exists: {validation['exists']}")
    print(f"  Manifest Valid: {validation['manifest_valid']}")
    print(f"  Files Valid: {validation['files_valid']}")
    
    if validation['errors']:
        print(f"\n  Errors:")
        for error in validation['errors']:
            print(f"    - {error}")
    
    if validation['warnings']:
        print(f"\n  Warnings:")
        for warning in validation['warnings']:
            print(f"    - {warning}")
    
    if validation['valid']:
        print("\nBackup is valid and can be restored")
    else:
        print("\nBackup validation failed")


def demo_restore_backup_dry_run(backup_id: str):
    """Demonstrate restoring a backup (dry run)"""
    print("\n" + "=" * 60)
    print("DEMO 4: Restore Backup (Dry Run)")
    print("=" * 60)
    
    manager = BackupManager(YML_DIR, BACKUP_DIR)
    
    print(f"\nDry run: Restoring backup {backup_id}")
    print("(No actual changes will be made)\n")
    
    result = manager.restore_backup(backup_id, confirm=False)
    
    if result:
        print("\nDry run successful")
    else:
        print("\nDry run complete (see above for what would be restored)")


def demo_convenience_functions():
    """Demonstrate convenience functions"""
    print("\n" + "=" * 60)
    print("DEMO 5: Convenience Functions")
    print("=" * 60)
    
    print("\n1. Using create_backup() convenience function...")
    backup_id = create_backup()
    print(f"   Created: {backup_id}")
    
    print("\n2. Using list_backups() convenience function...")
    backups = list_backups()
    print(f"   Found {len(backups)} backup(s)")
    
    print("\n3. Using validate_backup() convenience function...")
    validation = validate_backup(backup_id)
    print(f"   Valid: {validation['valid']}")
    
    print("\n4. Using restore_backup() convenience function (dry run)...")
    result = restore_backup(backup_id, confirm=False)
    print(f"   Dry run result: {result}")


def demo_backup_specific_files():
    """Demonstrate backing up specific files"""
    print("\n" + "=" * 60)
    print("DEMO 6: Backup Specific Files")
    print("=" * 60)
    
    manager = BackupManager(YML_DIR, BACKUP_DIR)
    
    # Get first 3 YML files
    yml_files = list(YML_DIR.glob("*.yml"))[:3]
    
    if not yml_files:
        print("\nNo YML files found to backup")
        return
    
    print(f"\nBacking up {len(yml_files)} specific files:")
    for yml_file in yml_files:
        print(f"  - {yml_file.name}")
    
    backup_id = manager.create_backup(yml_files)
    print(f"\nBackup created: {backup_id}")


def main():
    """Run all demos"""
    print("\n" + "=" * 60)
    print("BACKUP MANAGER DEMONSTRATION")
    print("=" * 60)
    
    print(f"\nYML Directory: {YML_DIR}")
    print(f"Backup Directory: {BACKUP_DIR}")
    
    # Check if YML directory exists and has files
    if not YML_DIR.exists():
        print(f"\nYML directory not found: {YML_DIR}")
        print("Please ensure the YML directory exists with YML files.")
        return
    
    yml_files = list(YML_DIR.glob("*.yml"))
    if not yml_files:
        print(f"\nNo YML files found in: {YML_DIR}")
        print("Please ensure there are YML files to backup.")
        return
    
    print(f"Found {len(yml_files)} YML file(s) to backup")
    
    # Run demos
    try:
        # Demo 1: Create backup
        backup_id = demo_create_backup()
        
        # Demo 2: List backups
        demo_list_backups()
        
        # Demo 3: Validate backup
        demo_validate_backup(backup_id)
        
        # Demo 4: Restore backup (dry run)
        demo_restore_backup_dry_run(backup_id)
        
        # Demo 5: Convenience functions
        demo_convenience_functions()
        
        # Demo 6: Backup specific files
        demo_backup_specific_files()
        
        print("\n" + "=" * 60)
        print("ALL DEMOS COMPLETED SUCCESSFULLY")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nError during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
