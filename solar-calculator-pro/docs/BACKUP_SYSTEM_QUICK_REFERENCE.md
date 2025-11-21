# Backup System Quick Reference

## Quick Commands

### Create Backup
```python
from backend.services.backup_service import BackupService
from pathlib import Path

backup_service = BackupService(Path("./data"), Path("./backups"))
result = backup_service.create_backup(
    backup_name="my_backup",
    description="Quick backup",
    compress=True
)
```

### Restore Backup
```python
result = backup_service.restore_backup(
    backup_name="backup_20240115_143022",
    verify_before_restore=True
)
```

### List Backups
```python
backups = backup_service.list_backups()
for backup in backups:
    print(f"{backup['backup_name']}: {backup['size_formatted']}")
```

### Verify Backup
```python
result = backup_service.verify_backup("backup_20240115_143022")
print(f"Valid: {result['valid']}")
```

### Delete Backup
```python
result = backup_service.delete_backup("backup_20240115_143022")
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/backup/create` | Create new backup |
| POST | `/backup/restore` | Restore from backup |
| GET | `/backup/list` | List all backups |
| GET | `/backup/verify/{name}` | Verify backup |
| DELETE | `/backup/delete/{name}` | Delete backup |
| GET | `/backup/info/{name}` | Get backup details |

## Backup Components

- **Databases** - All `.db` files
- **Settings** - Configuration files (`.json`, `.yaml`, `.ini`, `.env`)
- **User Data** - User profiles and uploads
- **Projects** - Project data and files

## Common Options

### Create Backup Options
```json
{
  "backup_name": "optional_name",
  "description": "Backup description",
  "include_databases": true,
  "include_settings": true,
  "include_user_data": true,
  "include_projects": true,
  "compress": true
}
```

### Restore Options
```json
{
  "backup_name": "backup_20240115_143022",
  "verify_before_restore": true
}
```

## Verification Checks

1. **Metadata** - Backup metadata file exists and is valid
2. **File Integrity** - All files are present and readable
3. **Database Integrity** - Databases can be opened and queried

## Best Practices

✅ **DO:**
- Create backups before major operations
- Use descriptive names and descriptions
- Verify backups after creation
- Enable compression for storage efficiency
- Keep multiple backup versions

❌ **DON'T:**
- Delete backups without verification
- Restore without creating pre-restore backup
- Skip verification before restoration
- Store backups in same location as data

## Troubleshooting

### Backup Creation Fails
```bash
# Check permissions
chmod 755 backups/

# Check disk space
df -h
```

### Restoration Fails
```python
# Verify backup first
result = backup_service.verify_backup("backup_name")
if not result['valid']:
    print(result['message'])
```

### Backup Not Found
```python
# List all backups
backups = backup_service.list_backups()
print([b['backup_name'] for b in backups])
```

## File Locations

- **Data Directory:** `./data`
- **Backup Directory:** `./backups`
- **Backup Metadata:** `backup_metadata.json`
- **Compressed Backups:** `.zip` files

## Size Estimates

| Component | Typical Size |
|-----------|--------------|
| Databases | 1-10 MB |
| Settings | < 1 MB |
| User Data | 5-50 MB |
| Projects | 10-100 MB |
| **Total** | **16-161 MB** |

Compression typically reduces size by 40-60%.

## Integration Example

```python
# Automatic backup before migration
from backend.migrations.migration_manager import MigrationManager

migration_manager = MigrationManager(source_path, target_path)
result = migration_manager.run_full_migration()

# Backup is created automatically
backup_info = result['steps'][0]
print(f"Backup created: {backup_info['message']}")
```

## UI Access

1. Navigate to **Admin Panel**
2. Click **Backup Management**
3. Use buttons to:
   - Create Backup
   - Restore Backup
   - Verify Backup
   - Delete Backup

## Support

- 📖 Full Guide: `docs/BACKUP_SYSTEM_GUIDE.md`
- 🐛 Issues: Submit bug report
- 💬 Questions: Contact development team
