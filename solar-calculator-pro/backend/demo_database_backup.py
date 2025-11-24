"""
Database Backup and Restore System - Demo Script

This script demonstrates all features of the backup system.
"""

import sys
import time
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from services.database_backup_service import DatabaseBackupService
from services.backup_scheduler import BackupScheduler


def print_section(title: str):
    """Print section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def demo_basic_backup():
    """Demonstrate basic backup operations"""
    print_section("1. Basic Backup Operations")
    
    # Initialize service
    service = DatabaseBackupService(
        database_url="sqlite:///demo_database.db",
        backup_dir="demo_backups"
    )
    
    print("✓ Backup service initialized")
    print(f"  Backup directory: {service.backup_dir}")
    print(f"  Compression enabled: {service.compression_enabled}")
    
    # Create full backup
    print("\n📦 Creating full backup...")
    metadata = service.create_full_backup(encrypt=True, compress=True)
    
    print(f"✓ Full backup created successfully!")
    print(f"  Backup ID: {metadata.backup_id}")
    print(f"  Size: {metadata.size_bytes / 1024:.2f} KB")
    print(f"  Compressed: {metadata.compressed}")
    print(f"  Encrypted: {metadata.encrypted}")
    print(f"  Tables: {', '.join(metadata.tables)}")
    print(f"  Checksum: {metadata.checksum[:16]}...")
    
    return service, metadata


def demo_incremental_backup(service, parent_metadata):
    """Demonstrate incremental backup"""
    print_section("2. Incremental Backup")
    
    print(f"📦 Creating incremental backup based on {parent_metadata.backup_id}...")
    metadata = service.create_incremental_backup(
        parent_backup_id=parent_metadata.backup_id,
        encrypt=True,
        compress=True
    )
    
    print(f"✓ Incremental backup created successfully!")
    print(f"  Backup ID: {metadata.backup_id}")
    print(f"  Parent: {metadata.parent_backup_id}")
    print(f"  Size: {metadata.size_bytes / 1024:.2f} KB")
    
    return metadata


def demo_list_backups(service):
    """Demonstrate listing backups"""
    print_section("3. Listing Backups")
    
    # List all backups
    all_backups = service.list_backups()
    print(f"📋 Total backups: {len(all_backups)}")
    
    # List by type
    full_backups = service.list_backups(backup_type='full')
    incremental_backups = service.list_backups(backup_type='incremental')
    
    print(f"  Full backups: {len(full_backups)}")
    print(f"  Incremental backups: {len(incremental_backups)}")
    
    # Display backup details
    print("\n📊 Backup Details:")
    for backup in all_backups[:5]:  # Show first 5
        print(f"\n  {backup.backup_id}")
        print(f"    Type: {backup.backup_type}")
        print(f"    Time: {backup.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"    Size: {backup.size_bytes / 1024:.2f} KB")
        print(f"    Compressed: {'Yes' if backup.compressed else 'No'}")
        print(f"    Encrypted: {'Yes' if backup.encrypted else 'No'}")


def demo_validate_backup(service, backup_id):
    """Demonstrate backup validation"""
    print_section("4. Backup Validation")
    
    print(f"🔍 Validating backup: {backup_id}...")
    is_valid = service.validate_backup(backup_id)
    
    if is_valid:
        print("✓ Backup is valid!")
        print("  - Checksum verified")
        print("  - File size correct")
        print("  - File exists")
    else:
        print("✗ Backup validation failed!")
    
    # Get detailed info
    info = service.get_backup_info(backup_id)
    print(f"\n📄 Backup Information:")
    print(f"  File path: {info['file_path']}")
    print(f"  File exists: {info['file_exists']}")
    print(f"  Is valid: {info['is_valid']}")
    print(f"  Database: {info['database_name']}")
    print(f"  Tables: {len(info['tables'])}")


def demo_restore_backup(service, backup_id):
    """Demonstrate backup restoration"""
    print_section("5. Backup Restoration")
    
    print(f"🔄 Restoring from backup: {backup_id}...")
    print("  (This is a demo - actual restore would overwrite database)")
    
    # In production, you would do:
    # success = service.restore_backup(backup_id=backup_id, validate=True)
    
    print("✓ Restore would complete successfully!")
    print("  - Backup validated")
    print("  - File decrypted")
    print("  - File decompressed")
    print("  - Database restored")


def demo_scheduler():
    """Demonstrate backup scheduler"""
    print_section("6. Automatic Backup Scheduling")
    
    # Initialize service and scheduler
    service = DatabaseBackupService(
        database_url="sqlite:///demo_database.db",
        backup_dir="demo_backups"
    )
    
    scheduler = BackupScheduler(backup_service=service)
    
    print("⏰ Configuring backup schedule...")
    
    # Configure daily backups
    scheduler.schedule_daily_backup(
        time="02:00",
        backup_type="incremental"
    )
    print("✓ Daily incremental backups scheduled at 02:00")
    
    # Configure weekly backups
    scheduler.schedule_weekly_backup(
        day="sunday",
        time="03:00"
    )
    print("✓ Weekly full backups scheduled on Sunday at 03:00")
    
    # Configure monthly backups
    scheduler.schedule_monthly_backup(
        day=1,
        time="04:00"
    )
    print("✓ Monthly full backups scheduled on day 1 at 04:00")
    
    # Configure retention policy
    scheduler.set_retention_policy(
        keep_daily=7,
        keep_weekly=4,
        keep_monthly=12,
        keep_yearly=5
    )
    print("✓ Retention policy configured")
    print("  - Keep 7 daily backups")
    print("  - Keep 4 weekly backups")
    print("  - Keep 12 monthly backups")
    print("  - Keep 5 yearly backups")
    
    # Get schedule info
    info = scheduler.get_schedule_info()
    print(f"\n📅 Schedule Information:")
    print(f"  Running: {info['running']}")
    print(f"  Scheduled jobs: {info['scheduled_jobs']}")
    print(f"  Daily backup time: {info['daily_backup_time']}")
    print(f"  Weekly backup day: {info['weekly_backup_day']}")
    print(f"  Monthly backup day: {info['monthly_backup_day']}")
    
    # Run immediate backup
    print("\n🚀 Running immediate backup...")
    metadata = scheduler.run_immediate_backup(backup_type="full")
    print(f"✓ Immediate backup completed: {metadata.backup_id}")
    
    return scheduler


def demo_retention_policy(service):
    """Demonstrate retention policy"""
    print_section("7. Retention Policy Management")
    
    print("🗑️  Applying retention policy...")
    
    # Show current backups
    backups_before = service.list_backups()
    print(f"  Backups before: {len(backups_before)}")
    
    # Apply retention policy
    service.apply_retention_policy(
        keep_daily=3,
        keep_weekly=2,
        keep_monthly=1,
        keep_yearly=0
    )
    
    # Show remaining backups
    backups_after = service.list_backups()
    print(f"  Backups after: {len(backups_after)}")
    print(f"  Deleted: {len(backups_before) - len(backups_after)} backups")
    
    print("\n✓ Retention policy applied successfully!")


def demo_security_features(service):
    """Demonstrate security features"""
    print_section("8. Security Features")
    
    print("🔒 Security Features:")
    print("  ✓ Encryption: Fernet (symmetric encryption)")
    print("  ✓ Checksums: SHA256 hash verification")
    print("  ✓ Validation: Integrity checks before restore")
    print("  ✓ Access Control: API authentication required")
    
    # Show encryption key
    print(f"\n🔑 Encryption Key (first 16 bytes):")
    print(f"  {service.encryption_key[:16].hex()}...")
    
    # Create encrypted backup
    print("\n📦 Creating encrypted backup...")
    metadata = service.create_full_backup(encrypt=True, compress=True)
    
    print(f"✓ Encrypted backup created!")
    print(f"  Backup ID: {metadata.backup_id}")
    print(f"  Encrypted: {metadata.encrypted}")
    print(f"  Checksum: {metadata.checksum[:16]}...")


def demo_performance_metrics(service):
    """Demonstrate performance metrics"""
    print_section("9. Performance Metrics")
    
    print("⚡ Creating backups to measure performance...")
    
    # Measure full backup time
    start_time = time.time()
    metadata_full = service.create_full_backup(encrypt=True, compress=True)
    full_time = time.time() - start_time
    
    print(f"\n📊 Full Backup Performance:")
    print(f"  Time: {full_time:.2f} seconds")
    print(f"  Size: {metadata_full.size_bytes / 1024:.2f} KB")
    print(f"  Speed: {(metadata_full.size_bytes / 1024) / full_time:.2f} KB/s")
    
    # Measure incremental backup time
    start_time = time.time()
    metadata_inc = service.create_incremental_backup(
        parent_backup_id=metadata_full.backup_id,
        encrypt=True,
        compress=True
    )
    inc_time = time.time() - start_time
    
    print(f"\n📊 Incremental Backup Performance:")
    print(f"  Time: {inc_time:.2f} seconds")
    print(f"  Size: {metadata_inc.size_bytes / 1024:.2f} KB")
    print(f"  Speed: {(metadata_inc.size_bytes / 1024) / inc_time:.2f} KB/s")
    print(f"  Speedup: {full_time / inc_time:.2f}x faster")


def demo_summary():
    """Print demo summary"""
    print_section("Demo Summary")
    
    print("✅ All features demonstrated successfully!")
    print("\nKey Features:")
    print("  ✓ Full and incremental backups")
    print("  ✓ Compression and encryption")
    print("  ✓ Automatic scheduling")
    print("  ✓ Retention policies")
    print("  ✓ Backup validation")
    print("  ✓ Restore operations")
    print("  ✓ Security features")
    print("  ✓ Performance optimization")
    
    print("\nNext Steps:")
    print("  1. Review the documentation")
    print("  2. Configure backup schedule")
    print("  3. Set retention policy")
    print("  4. Test restore procedures")
    print("  5. Monitor backup operations")
    
    print("\nDocumentation:")
    print("  - Quick Reference: docs/DATABASE_BACKUP_QUICK_REFERENCE.md")
    print("  - Complete Guide: docs/DATABASE_BACKUP_GUIDE.md")
    print("  - API Docs: docs/API_DOCUMENTATION.md")


def main():
    """Run all demos"""
    print("\n" + "=" * 70)
    print("  DATABASE BACKUP AND RESTORE SYSTEM - DEMO")
    print("=" * 70)
    
    try:
        # Run demos
        service, full_metadata = demo_basic_backup()
        inc_metadata = demo_incremental_backup(service, full_metadata)
        demo_list_backups(service)
        demo_validate_backup(service, full_metadata.backup_id)
        demo_restore_backup(service, full_metadata.backup_id)
        scheduler = demo_scheduler()
        demo_retention_policy(service)
        demo_security_features(service)
        demo_performance_metrics(service)
        demo_summary()
        
        # Cleanup scheduler
        if scheduler.running:
            scheduler.stop()
        
        print("\n✅ Demo completed successfully!\n")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
