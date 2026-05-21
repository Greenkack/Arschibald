# Data Backup System Guide

## Overview

The Data Backup System provides comprehensive backup, restore, and management functionality for Solar Calculator Pro. It ensures data safety during migrations and allows manual backups at any time.

**Requirements:** 5.5

## Features

### 1. Automatic Backup Before Migration
- Automatically creates a backup before any migration operation
- Ensures data safety in case migration fails
- Includes all application data by default

### 2. Manual Backup Creation
- Create backups on-demand at any time
- Customize what to include in the backup
- Add descriptions for easy identification
- Optional compression to save storage space

### 3. Backup Restoration
- Restore data from any previous backup
- Automatic verification before restoration
- Creates a backup of current data before restoring
- Rollback capability if restoration fails

### 4. Backup Verification
- Verify backup integrity before restoration
- Check metadata completeness
- Validate file integrity
- Test database connectivity

### 5. Backup Management Interface
- List all available backups
- View backup details and metadata
- Delete old or unnecessary backups
- Monitor backup storage usage

## Architecture

### Backend Components

#### BackupService (`backend/services/backup_service.py`)
Core service handling all backup operations:
- `create_backup()` - Create new backups
- `restore_backup()` - Restore from backups
- `verify_backup()` - Verify backup integrity
- `list_backups()` - List all backups
- `delete_backup()` - Delete backups

#### Backup API (`backend/api/v1/backup.py`)
REST API endpoints:
- `POST /backup/create` - Create backup
- `POST /backup/restore` - Restore backup
- `GET /backup/list` - List backups
- `GET /backup/verify/{name}` - Verify backup
- `DELETE /backup/delete/{name}` - Delete backup
- `GET /backup/info/{name}` - Get backup details

### Frontend Components

#### BackupManagement Component
React component providing UI for:
- Creating backups with custom options
- Viewing backup list with details
- Restoring backups with confirmation
- Verifying backup integrity
- Deleting backups

## Usage

### Creating a Backup

#### Via API

```python
import requests

# Create a full backup
response = requests.post('http://localhost:8000/api/v1/backup/create', json={
    "backup_name": "my_backup",
    "description": "Manual backup before update",
    "include_databases": True,
    "include_settings": True,
    "include_user_data": True,
    "include_projects": True,
    "compress": True
})

print(response.json())
```

#### Via Python Service

```python
from pathlib import Path
from backend.services.backup_service import BackupService

# Initialize service
backup_service = BackupService(
    data_path=Path("./data"),
    backup_root=Path("./backups")
)

# Create backup
result = backup_service.create_backup(
    backup_name="my_backup",
    description="Manual backup",
    compress=True
)

print(f"Backup created: {result['backup_name']}")
print(f"Files backed up: {result['files_backed_up']}")
print(f"Size: {result['total_size_bytes']} bytes")
```

#### Via UI

1. Navigate to Admin Panel → Backup Management
2. Click "Create Backup" button
3. Fill in backup details:
   - Backup Name (optional, auto-generated if empty)
   - Description
   - Select components to include
   - Enable/disable compression
4. Click "Create" button
5. Wait for backup completion

### Restoring a Backup

#### Via API

```python
import requests

# Restore a backup
response = requests.post('http://localhost:8000/api/v1/backup/restore', json={
    "backup_name": "backup_20240115_143022",
    "verify_before_restore": True
})

print(response.json())
```

#### Via Python Service

```python
# Restore backup
result = backup_service.restore_backup(
    backup_name="backup_20240115_143022",
    verify_before_restore=True
)

print(f"Restore status: {result['success']}")
print(f"Files restored: {result['files_restored']}")
```

#### Via UI

1. Navigate to Admin Panel → Backup Management
2. Find the backup you want to restore
3. Click the restore button (green refresh icon)
4. Confirm the restoration
5. Wait for restoration completion

**Note:** A backup of current data is automatically created before restoration.

### Verifying a Backup

#### Via API

```python
import requests

# Verify backup
response = requests.get('http://localhost:8000/api/v1/backup/verify/backup_20240115_143022')

result = response.json()
print(f"Valid: {result['valid']}")
print(f"Message: {result['message']}")

for check in result['checks']:
    print(f"- {check['name']}: {'✓' if check['passed'] else '✗'}")
```

#### Via Python Service

```python
# Verify backup
result = backup_service.verify_backup("backup_20240115_143022")

print(f"Valid: {result['valid']}")
for check in result['checks']:
    print(f"{check['name']}: {check['passed']}")
```

#### Via UI

1. Navigate to Admin Panel → Backup Management
2. Find the backup you want to verify
3. Click the verify button (blue check icon)
4. View verification results in dialog

### Listing Backups

#### Via API

```python
import requests

# List all backups
response = requests.get('http://localhost:8000/api/v1/backup/list')

backups = response.json()['backups']
for backup in backups:
    print(f"{backup['backup_name']}: {backup['size_formatted']}")
```

#### Via Python Service

```python
# List backups
backups = backup_service.list_backups()

for backup in backups:
    print(f"Name: {backup['backup_name']}")
    print(f"Created: {backup['created_at']}")
    print(f"Size: {backup['size_formatted']}")
    print(f"Files: {backup['files_count']}")
    print("---")
```

### Deleting a Backup

#### Via API

```python
import requests

# Delete backup
response = requests.delete('http://localhost:8000/api/v1/backup/delete/backup_20240115_143022')

print(response.json())
```

#### Via Python Service

```python
# Delete backup
result = backup_service.delete_backup("backup_20240115_143022")

print(f"Deleted: {result['success']}")
```

#### Via UI

1. Navigate to Admin Panel → Backup Management
2. Find the backup you want to delete
3. Click the delete button (red trash icon)
4. Confirm the deletion

## Backup Structure

### Backup Directory Layout

```
backups/
├── backup_20240115_143022/
│   ├── backup_metadata.json
│   ├── databases/
│   │   ├── product_database.db
│   │   └── crm_database.db
│   ├── settings/
│   │   ├── config.json
│   │   └── .env
│   ├── user_data/
│   │   ├── users/
│   │   └── profiles/
│   └── projects/
│       └── data/
└── backup_20240115_143022.zip  # Compressed version
```

### Backup Metadata

```json
{
  "backup_name": "backup_20240115_143022",
  "timestamp": "20240115_143022",
  "description": "Manual backup before update",
  "created_at": "2024-01-15T14:30:22.123456",
  "source_path": "/path/to/data",
  "components": {
    "databases": {
      "files_count": 2,
      "size_bytes": 1048576
    },
    "settings": {
      "files_count": 5,
      "size_bytes": 4096
    },
    "user_data": {
      "files_count": 150,
      "size_bytes": 5242880
    },
    "projects": {
      "files_count": 300,
      "size_bytes": 10485760
    }
  },
  "files_count": 457,
  "total_size_bytes": 16781312
}
```

## Best Practices

### 1. Regular Backups
- Create backups before major operations
- Schedule regular automatic backups
- Keep multiple backup versions

### 2. Backup Naming
- Use descriptive names for manual backups
- Include date/time in backup names
- Add descriptions for context

### 3. Storage Management
- Monitor backup storage usage
- Delete old backups when no longer needed
- Use compression for long-term storage

### 4. Verification
- Verify backups after creation
- Test restoration periodically
- Keep verification logs

### 5. Security
- Store backups in secure location
- Encrypt sensitive backups
- Limit access to backup management

## Troubleshooting

### Backup Creation Fails

**Problem:** Backup creation fails with permission error

**Solution:**
```bash
# Check directory permissions
ls -la backups/

# Fix permissions
chmod 755 backups/
```

### Restoration Fails

**Problem:** Backup restoration fails with verification error

**Solution:**
1. Verify backup integrity first
2. Check verification results
3. Try restoring to different location
4. Contact support if issue persists

### Backup Too Large

**Problem:** Backup size is too large

**Solution:**
1. Enable compression
2. Exclude unnecessary components
3. Clean up old data before backup
4. Use incremental backups

### Cannot Find Backup

**Problem:** Backup not found in list

**Solution:**
1. Check backup directory
2. Verify backup name
3. Check if backup was deleted
4. Look for compressed (.zip) version

## API Reference

### Create Backup

```
POST /api/v1/backup/create
```

**Request Body:**
```json
{
  "backup_name": "string (optional)",
  "description": "string",
  "include_databases": true,
  "include_settings": true,
  "include_user_data": true,
  "include_projects": true,
  "compress": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Backup created successfully: 457 files, 16.00 MB",
  "backup_name": "backup_20240115_143022",
  "files_count": 457,
  "size_bytes": 16781312
}
```

### Restore Backup

```
POST /api/v1/backup/restore
```

**Request Body:**
```json
{
  "backup_name": "backup_20240115_143022",
  "verify_before_restore": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Backup restored successfully: 457 files",
  "backup_name": "backup_20240115_143022",
  "files_count": 457
}
```

### List Backups

```
GET /api/v1/backup/list
```

**Response:**
```json
{
  "success": true,
  "count": 5,
  "backups": [
    {
      "backup_name": "backup_20240115_143022",
      "timestamp": "20240115_143022",
      "created_at": "2024-01-15T14:30:22.123456",
      "description": "Manual backup",
      "files_count": 457,
      "total_size_bytes": 16781312,
      "size_formatted": "16.00 MB",
      "is_compressed": true
    }
  ]
}
```

### Verify Backup

```
GET /api/v1/backup/verify/{backup_name}
```

**Response:**
```json
{
  "success": true,
  "valid": true,
  "message": "Backup verification passed",
  "checks": [
    {
      "name": "metadata",
      "passed": true,
      "details": {}
    },
    {
      "name": "file_integrity",
      "passed": true,
      "details": {
        "file_count": 457
      }
    },
    {
      "name": "database_integrity",
      "passed": true,
      "details": {
        "database_count": 2,
        "valid_databases": 2
      }
    }
  ]
}
```

### Delete Backup

```
DELETE /api/v1/backup/delete/{backup_name}
```

**Response:**
```json
{
  "success": true,
  "message": "Backup deleted: backup_20240115_143022",
  "backup_name": "backup_20240115_143022"
}
```

## Integration with Migration System

The backup system is integrated with the migration system to ensure data safety:

```python
from backend.migrations.migration_manager import MigrationManager
from backend.services.backup_service import BackupService

# Migration automatically creates backup
migration_manager = MigrationManager(source_path, target_path)
result = migration_manager.run_full_migration()

# Backup is created in first step
print(result['steps'][0])  # Backup step
```

## Support

For issues or questions:
- Check troubleshooting section
- Review API documentation
- Contact development team
- Submit bug report

## Version History

- **v1.0.0** - Initial release
  - Automatic backup before migration
  - Manual backup creation
  - Backup restoration
  - Backup verification
  - Backup management interface
