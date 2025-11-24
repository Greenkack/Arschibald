# Database Backup and Restore - Complete Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Architecture](#architecture)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Backup Operations](#backup-operations)
6. [Restore Operations](#restore-operations)
7. [Scheduling](#scheduling)
8. [Retention Policies](#retention-policies)
9. [Security](#security)
10. [Monitoring](#monitoring)
11. [Disaster Recovery](#disaster-recovery)
12. [Advanced Topics](#advanced-topics)

## Introduction

The Database Backup and Restore system provides enterprise-grade backup capabilities for the Solar Calculator Pro application. It supports automatic scheduling, incremental backups, compression, encryption, and intelligent retention policies.

### Key Benefits

- **Data Protection**: Protect against data loss from hardware failure, software bugs, or user errors
- **Compliance**: Meet regulatory requirements for data retention and recovery
- **Disaster Recovery**: Quick recovery from catastrophic failures
- **Space Efficiency**: Incremental backups and compression reduce storage costs
- **Security**: Encryption protects sensitive data
- **Automation**: Scheduled backups require no manual intervention

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────┐
│                  Backup System Architecture              │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────┐      ┌──────────────────┐       │
│  │  API Endpoints   │◄────►│  Backup Service  │       │
│  └──────────────────┘      └──────────────────┘       │
│           │                         │                   │
│           │                         │                   │
│           ▼                         ▼                   │
│  ┌──────────────────┐      ┌──────────────────┐       │
│  │ Backup Scheduler │      │  Database Engine │       │
│  └──────────────────┘      └──────────────────┘       │
│           │                         │                   │
│           │                         │                   │
│           ▼                         ▼                   │
│  ┌─────────────────────────────────────────┐          │
│  │         Backup Storage                   │          │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐ │          │
│  │  │  Full   │  │Increment│  │Metadata │ │          │
│  │  │ Backups │  │ Backups │  │  JSON   │ │          │
│  │  └─────────┘  └─────────┘  └─────────┘ │          │
│  └─────────────────────────────────────────┘          │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Backup Creation**:
   - Service exports database to temporary file
   - File is compressed (optional)
   - File is encrypted (optional)
   - Checksum is calculated
   - Metadata is saved
   - Temporary files are cleaned up

2. **Backup Restoration**:
   - Metadata is loaded
   - Backup file is validated
   - File is decrypted (if encrypted)
   - File is decompressed (if compressed)
   - Database is restored
   - Temporary files are cleaned up

## Installation

### Prerequisites

```bash
# Install required packages
pip install sqlalchemy cryptography schedule fastapi
```

### Setup

```python
from services.database_backup_service import DatabaseBackupService
from services.backup_scheduler import BackupScheduler

# Initialize backup service
backup_service = DatabaseBackupService(
    database_url="sqlite:///database.db",
    backup_dir="backups",
    encryption_key=None,  # Auto-generated if not provided
    compression_enabled=True
)

# Initialize scheduler
scheduler = BackupScheduler(backup_service=backup_service)
```

## Configuration

### Environment Variables

```bash
# Database configuration
DATABASE_URL=sqlite:///database.db

# Backup configuration
BACKUP_DIR=backups
BACKUP_COMPRESSION=true
BACKUP_ENCRYPTION=true
BACKUP_ENCRYPTION_KEY=your-encryption-key-here

# Schedule configuration
BACKUP_DAILY_TIME=02:00
BACKUP_WEEKLY_DAY=sunday
BACKUP_WEEKLY_TIME=03:00
BACKUP_MONTHLY_DAY=1
BACKUP_MONTHLY_TIME=04:00

# Retention policy
BACKUP_KEEP_DAILY=7
BACKUP_KEEP_WEEKLY=4
BACKUP_KEEP_MONTHLY=12
BACKUP_KEEP_YEARLY=5
```

### Configuration File

```json
{
  "backup": {
    "database_url": "sqlite:///database.db",
    "backup_dir": "backups",
    "compression_enabled": true,
    "encryption_enabled": true,
    "schedule": {
      "daily": {
        "enabled": true,
        "time": "02:00",
        "type": "incremental"
      },
      "weekly": {
        "enabled": true,
        "day": "sunday",
        "time": "03:00"
      },
      "monthly": {
        "enabled": true,
        "day": 1,
        "time": "04:00"
      }
    },
    "retention": {
      "keep_daily": 7,
      "keep_weekly": 4,
      "keep_monthly": 12,
      "keep_yearly": 5
    }
  }
}
```

## Backup Operations

### Creating Full Backups

Full backups create a complete snapshot of the database:

```python
# Create full backup with all options
metadata = backup_service.create_full_backup(
    encrypt=True,
    compress=True
)

print(f"Backup ID: {metadata.backup_id}")
print(f"Size: {metadata.size_bytes / 1024 / 1024:.2f} MB")
print(f"Tables: {', '.join(metadata.tables)}")
```

### Creating Incremental Backups

Incremental backups only store changes since the parent backup:

```python
# Find most recent full backup
full_backups = backup_service.list_backups(backup_type='full')
parent_id = full_backups[0].backup_id

# Create incremental backup
metadata = backup_service.create_incremental_backup(
    parent_backup_id=parent_id,
    encrypt=True,
    compress=True
)
```

### Listing Backups

```python
# List all backups
all_backups = backup_service.list_backups()

# Filter by type
full_backups = backup_service.list_backups(backup_type='full')
incremental_backups = backup_service.list_backups(backup_type='incremental')

# Filter by date range
from datetime import datetime, timedelta

start_date = datetime.now() - timedelta(days=7)
recent_backups = backup_service.list_backups(start_date=start_date)
```

### Getting Backup Information

```python
# Get detailed backup information
info = backup_service.get_backup_info("backup_20240101_120000")

print(f"Backup ID: {info['backup_id']}")
print(f"Type: {info['backup_type']}")
print(f"Size: {info['size_bytes']} bytes")
print(f"Compressed: {info['compressed']}")
print(f"Encrypted: {info['encrypted']}")
print(f"Valid: {info['is_valid']}")
print(f"File exists: {info['file_exists']}")
```

### Validating Backups

```python
# Validate backup integrity
is_valid = backup_service.validate_backup("backup_20240101_120000")

if is_valid:
    print("Backup is valid and can be restored")
else:
    print("Backup validation failed - file may be corrupted")
```

## Restore Operations

### Basic Restore

```python
# Restore from backup with validation
success = backup_service.restore_backup(
    backup_id="backup_20240101_120000",
    validate=True
)

if success:
    print("Database restored successfully")
else:
    print("Restore failed")
```

### Restore to Different Database

```python
# Restore to a different database
success = backup_service.restore_backup(
    backup_id="backup_20240101_120000",
    validate=True,
    target_database_url="sqlite:///restored_database.db"
)
```

### Restore from Incremental Backup Chain

When restoring from an incremental backup, the system automatically handles the backup chain:

```python
# Restore from incremental backup
# The service will automatically restore the parent full backup first
success = backup_service.restore_backup(
    backup_id="backup_20240105_120000",  # Incremental backup
    validate=True
)
```

## Scheduling

### Configuring Automatic Backups

```python
from services.backup_scheduler import BackupScheduler

scheduler = BackupScheduler(backup_service=backup_service)

# Configure daily incremental backups
scheduler.schedule_daily_backup(
    time="02:00",
    backup_type="incremental",
    encrypt=True,
    compress=True
)

# Configure weekly full backups
scheduler.schedule_weekly_backup(
    day="sunday",
    time="03:00",
    encrypt=True,
    compress=True
)

# Configure monthly full backups
scheduler.schedule_monthly_backup(
    day=1,
    time="04:00",
    encrypt=True,
    compress=True
)

# Configure retention cleanup
scheduler.schedule_retention_cleanup(time="05:00")

# Start scheduler
scheduler.start()
```

### Managing Scheduler

```python
# Get scheduler status
info = scheduler.get_schedule_info()
print(f"Running: {info['running']}")
print(f"Scheduled jobs: {info['scheduled_jobs']}")
print(f"Last full backup: {info['last_full_backup']}")

# Stop scheduler
scheduler.stop()

# Restart scheduler
scheduler.start()
```

### Running Immediate Backups

```python
# Run backup outside of schedule
metadata = scheduler.run_immediate_backup(
    backup_type="full",
    encrypt=True,
    compress=True
)
```

## Retention Policies

### Understanding Retention

Retention policies automatically manage backup lifecycle:

- **Daily**: Keep backups from the last N days
- **Weekly**: Keep one backup per week for N weeks
- **Monthly**: Keep one backup per month for N months
- **Yearly**: Keep one backup per year for N years

### Configuring Retention

```python
# Set retention policy
scheduler.set_retention_policy(
    keep_daily=7,      # Keep 7 daily backups
    keep_weekly=4,     # Keep 4 weekly backups
    keep_monthly=12,   # Keep 12 monthly backups
    keep_yearly=5      # Keep 5 yearly backups
)

# Apply retention policy immediately
backup_service.apply_retention_policy(
    keep_daily=7,
    keep_weekly=4,
    keep_monthly=12,
    keep_yearly=5
)
```

### Retention Examples

**Example 1: Short-term retention**
```python
# Keep only recent backups
scheduler.set_retention_policy(
    keep_daily=3,
    keep_weekly=2,
    keep_monthly=1,
    keep_yearly=0
)
```

**Example 2: Long-term retention**
```python
# Keep extensive backup history
scheduler.set_retention_policy(
    keep_daily=30,
    keep_weekly=12,
    keep_monthly=24,
    keep_yearly=10
)
```

## Security

### Encryption

Backups are encrypted using Fernet (symmetric encryption):

```python
from cryptography.fernet import Fernet

# Generate encryption key
encryption_key = Fernet.generate_key()

# Save key securely
with open('backup_encryption.key', 'wb') as f:
    f.write(encryption_key)

# Use key for backups
backup_service = DatabaseBackupService(
    database_url="sqlite:///database.db",
    backup_dir="backups",
    encryption_key=encryption_key
)
```

### Key Management

**Best Practices:**
1. Store encryption keys separately from backups
2. Use environment variables or secure key management systems
3. Rotate keys periodically
4. Maintain key backups in secure locations
5. Document key recovery procedures

### Access Control

```python
# Implement role-based access control
from fastapi import Depends, HTTPException
from core.auth import get_current_user, require_role

@router.post("/backup/create")
async def create_backup(
    current_user = Depends(get_current_user),
    admin_check = Depends(require_role("admin"))
):
    # Only admins can create backups
    pass
```

## Monitoring

### Backup Monitoring

```python
# Monitor backup status
def monitor_backups():
    backups = backup_service.list_backups()
    
    # Check for recent backups
    latest_backup = backups[0] if backups else None
    if latest_backup:
        age = datetime.now() - latest_backup.timestamp
        if age > timedelta(days=1):
            alert("No recent backup found!")
    
    # Check backup validity
    for backup in backups[:5]:  # Check last 5 backups
        if not backup_service.validate_backup(backup.backup_id):
            alert(f"Invalid backup: {backup.backup_id}")
    
    # Check disk space
    total_size = sum(b.size_bytes for b in backups)
    if total_size > 10 * 1024 * 1024 * 1024:  # 10 GB
        alert("Backup storage exceeds 10 GB")
```

### Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backup.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('backup')

# Log backup operations
logger.info("Starting backup creation")
metadata = backup_service.create_full_backup()
logger.info(f"Backup created: {metadata.backup_id}")
```

### Alerts

```python
# Send alerts for backup failures
def send_alert(message: str):
    # Send email, SMS, or push notification
    pass

try:
    metadata = backup_service.create_full_backup()
except Exception as e:
    send_alert(f"Backup failed: {str(e)}")
    logger.error(f"Backup failed: {e}", exc_info=True)
```

## Disaster Recovery

### Recovery Procedures

**Step 1: Assess the Situation**
- Determine the cause of failure
- Identify the last known good state
- Check backup availability

**Step 2: Select Backup**
```python
# List available backups
backups = backup_service.list_backups()

# Find most recent valid backup
for backup in backups:
    if backup_service.validate_backup(backup.backup_id):
        print(f"Valid backup found: {backup.backup_id}")
        break
```

**Step 3: Restore Database**
```python
# Restore from backup
success = backup_service.restore_backup(
    backup_id=backup.backup_id,
    validate=True
)
```

**Step 4: Verify Restoration**
```python
# Verify database integrity
from sqlalchemy import create_engine

engine = create_engine(database_url)
with engine.connect() as conn:
    # Run verification queries
    result = conn.execute("SELECT COUNT(*) FROM users")
    print(f"User count: {result.scalar()}")
```

### Recovery Time Objectives (RTO)

- **Full Backup Restore**: 5-15 minutes
- **Incremental Backup Restore**: 10-30 minutes
- **Large Database (>1GB)**: 30-60 minutes

### Recovery Point Objectives (RPO)

- **Daily Backups**: Up to 24 hours of data loss
- **Hourly Backups**: Up to 1 hour of data loss
- **Real-time Replication**: Minimal data loss

## Advanced Topics

### Custom Backup Strategies

```python
# Implement custom backup strategy
class CustomBackupStrategy:
    def __init__(self, backup_service):
        self.backup_service = backup_service
    
    def execute(self):
        # Create full backup on first day of month
        if datetime.now().day == 1:
            return self.backup_service.create_full_backup()
        
        # Create incremental backup on other days
        full_backups = self.backup_service.list_backups(backup_type='full')
        if full_backups:
            return self.backup_service.create_incremental_backup(
                parent_backup_id=full_backups[0].backup_id
            )
```

### Backup Verification Testing

```python
# Regularly test backup restoration
def test_backup_restoration():
    # Create test database
    test_db_url = "sqlite:///test_restore.db"
    
    # Get latest backup
    backups = backup_service.list_backups()
    if not backups:
        return False
    
    # Restore to test database
    try:
        backup_service.restore_backup(
            backup_id=backups[0].backup_id,
            validate=True,
            target_database_url=test_db_url
        )
        return True
    except Exception as e:
        logger.error(f"Restore test failed: {e}")
        return False
```

### Off-site Backup Storage

```python
# Upload backups to cloud storage
import boto3

def upload_to_s3(backup_id: str):
    s3 = boto3.client('s3')
    
    # Get backup file
    backup_file = backup_service._get_backup_file_path(
        backup_service.get_backup_info(backup_id)
    )
    
    # Upload to S3
    s3.upload_file(
        str(backup_file),
        'my-backup-bucket',
        f'backups/{backup_id}'
    )
```

### Backup Compression Optimization

```python
# Use different compression levels
import gzip

def compress_with_level(source_path, target_path, level=9):
    with open(source_path, 'rb') as f_in:
        with gzip.open(target_path, 'wb', compresslevel=level) as f_out:
            shutil.copyfileobj(f_in, f_out)
```

## Troubleshooting

### Common Issues

**Issue: Backup creation fails with "Permission denied"**
- Solution: Check backup directory permissions
- Solution: Verify database file permissions

**Issue: Restore fails with "Checksum mismatch"**
- Solution: Backup file may be corrupted
- Solution: Try restoring from an earlier backup

**Issue: Scheduler not running backups**
- Solution: Check scheduler status
- Solution: Verify system time is correct
- Solution: Check for scheduler errors in logs

**Issue: Backups consuming too much disk space**
- Solution: Enable compression
- Solution: Adjust retention policy
- Solution: Use incremental backups

## Best Practices Summary

1. **Schedule Regular Backups**: Daily incremental, weekly full
2. **Test Restores**: Monthly restoration tests
3. **Monitor Backups**: Automated monitoring and alerts
4. **Secure Backups**: Encryption and access control
5. **Off-site Storage**: Store backups in multiple locations
6. **Document Procedures**: Maintain recovery documentation
7. **Retention Policy**: Balance storage costs with recovery needs
8. **Validate Backups**: Regular integrity checks

## Conclusion

The Database Backup and Restore system provides comprehensive data protection for the Solar Calculator Pro application. By following the guidelines in this document, you can ensure reliable backup operations and quick recovery from data loss scenarios.

For additional support, refer to:
- [Quick Reference Guide](DATABASE_BACKUP_QUICK_REFERENCE.md)
- [API Documentation](API_DOCUMENTATION.md)
- [Security Guide](SECURITY_GUIDE.md)
