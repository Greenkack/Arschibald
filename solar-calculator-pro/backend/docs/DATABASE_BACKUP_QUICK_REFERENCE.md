# Database Backup and Restore - Quick Reference

## Overview

Comprehensive database backup and restore system with automatic scheduling, incremental backups, compression, encryption, and retention policies.

## Key Features

- ✅ **Automatic Backup Scheduling** - Daily, weekly, and monthly backups
- ✅ **Incremental Backups** - Save space with incremental backup chains
- ✅ **Backup Compression** - Reduce backup file sizes with gzip
- ✅ **Backup Encryption** - Secure backups with Fernet encryption
- ✅ **Restore Validation** - Verify backup integrity before restore
- ✅ **Retention Policies** - Automatic cleanup of old backups
- ✅ **Checksum Verification** - SHA256 checksums for data integrity
- ✅ **Metadata Tracking** - Complete backup history and information

## Quick Start

### Create a Full Backup

```python
from services.database_backup_service import DatabaseBackupService

service = DatabaseBackupService(
    database_url="sqlite:///database.db",
    backup_dir="backups"
)

# Create encrypted and compressed backup
metadata = service.create_full_backup(
    encrypt=True,
    compress=True
)

print(f"Backup created: {metadata.backup_id}")
```

### Create an Incremental Backup

```python
# Create incremental backup based on most recent full backup
full_backups = service.list_backups(backup_type='full')
parent_id = full_backups[0].backup_id

metadata = service.create_incremental_backup(
    parent_backup_id=parent_id,
    encrypt=True,
    compress=True
)
```

### Restore from Backup

```python
# Restore with validation
success = service.restore_backup(
    backup_id="backup_20240101_120000",
    validate=True
)

if success:
    print("Database restored successfully")
```

### Setup Automatic Backups

```python
from services.backup_scheduler import BackupScheduler

scheduler = BackupScheduler(backup_service=service)

# Schedule daily incremental backups at 2 AM
scheduler.schedule_daily_backup(
    time="02:00",
    backup_type="incremental"
)

# Schedule weekly full backups on Sunday at 3 AM
scheduler.schedule_weekly_backup(
    day="sunday",
    time="03:00"
)

# Schedule monthly full backups on the 1st at 4 AM
scheduler.schedule_monthly_backup(
    day=1,
    time="04:00"
)

# Set retention policy
scheduler.set_retention_policy(
    keep_daily=7,
    keep_weekly=4,
    keep_monthly=12,
    keep_yearly=5
)

# Start scheduler
scheduler.start()
```

## API Endpoints

### Create Backup

```http
POST /api/v1/database/backup/create
Content-Type: application/json

{
  "backup_type": "full",
  "encrypt": true,
  "compress": true
}
```

### Restore Backup

```http
POST /api/v1/database/backup/restore
Content-Type: application/json

{
  "backup_id": "backup_20240101_120000",
  "validate": true
}
```

### List Backups

```http
GET /api/v1/database/backup/list?backup_type=full
```

### Get Backup Info

```http
GET /api/v1/database/backup/info/{backup_id}
```

### Validate Backup

```http
POST /api/v1/database/backup/validate/{backup_id}
```

### Delete Backup

```http
DELETE /api/v1/database/backup/delete/{backup_id}
```

### Configure Schedule

```http
POST /api/v1/database/backup/schedule/configure
Content-Type: application/json

{
  "daily_enabled": true,
  "daily_time": "02:00",
  "daily_type": "incremental",
  "weekly_enabled": true,
  "weekly_day": "sunday",
  "weekly_time": "03:00",
  "monthly_enabled": true,
  "monthly_day": 1,
  "monthly_time": "04:00",
  "retention_policy": {
    "keep_daily": 7,
    "keep_weekly": 4,
    "keep_monthly": 12,
    "keep_yearly": 5
  }
}
```

### Run Immediate Backup

```http
POST /api/v1/database/backup/schedule/immediate?backup_type=full&encrypt=true&compress=true
```

## Backup Types

### Full Backup
- Complete database snapshot
- Independent of other backups
- Larger file size
- Can be restored directly

### Incremental Backup
- Only changes since parent backup
- Requires parent backup chain
- Smaller file size
- Faster to create

## Retention Policy

The retention policy automatically manages backup lifecycle:

- **Daily Backups**: Keep last N days (default: 7)
- **Weekly Backups**: Keep last N weeks (default: 4)
- **Monthly Backups**: Keep last N months (default: 12)
- **Yearly Backups**: Keep last N years (default: 5)

Backups are automatically deleted when they exceed retention limits.

## Backup Metadata

Each backup includes comprehensive metadata:

```json
{
  "backup_id": "backup_20240101_120000",
  "timestamp": "2024-01-01T12:00:00",
  "backup_type": "full",
  "size_bytes": 1048576,
  "compressed": true,
  "encrypted": true,
  "checksum": "sha256_hash",
  "database_name": "database",
  "tables": ["users", "projects", "products"],
  "parent_backup_id": null
}
```

## Security Features

### Encryption
- Uses Fernet (symmetric encryption)
- Secure key management
- Encrypted at rest

### Checksums
- SHA256 hash verification
- Detects file corruption
- Validates backup integrity

### Access Control
- API authentication required
- Role-based permissions
- Audit logging

## Best Practices

1. **Regular Full Backups**: Create full backups weekly
2. **Incremental Backups**: Use for daily backups to save space
3. **Test Restores**: Regularly test backup restoration
4. **Off-site Storage**: Store backups in multiple locations
5. **Monitor Schedule**: Check scheduler status regularly
6. **Validate Backups**: Run validation after creation
7. **Secure Keys**: Protect encryption keys
8. **Document Procedures**: Maintain restore procedures

## Troubleshooting

### Backup Creation Fails
- Check disk space
- Verify database permissions
- Check backup directory permissions

### Restore Fails
- Validate backup first
- Check database is not in use
- Verify sufficient disk space

### Scheduler Not Running
- Check scheduler status
- Verify schedule configuration
- Check system time settings

### Validation Fails
- Backup file may be corrupted
- Checksum mismatch
- File may have been modified

## Performance Considerations

- **Compression**: Reduces file size by 60-80%
- **Encryption**: Adds ~10% overhead
- **Incremental**: 5-10x faster than full backup
- **Validation**: Minimal overhead (~1-2 seconds)

## File Naming Convention

```
backup_YYYYMMDD_HHMMSS.ext

Extensions:
- .tmp: Uncompressed, unencrypted
- .gz: Compressed, unencrypted
- .enc: Encrypted (may be compressed)
```

## Requirements

- Python 3.10+
- SQLAlchemy
- cryptography
- schedule
- FastAPI

## See Also

- [Complete Backup Guide](DATABASE_BACKUP_GUIDE.md)
- [API Documentation](API_DOCUMENTATION.md)
- [Security Guide](SECURITY_GUIDE.md)
