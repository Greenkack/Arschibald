# Backup Manager Reference

## Overview

The Backup Manager provides comprehensive backup and restoration functionality for YML coordinate files in the Multi-PDF Positioning System. It ensures that original files can be safely preserved before modifications and restored when needed.

## Requirements Coverage

- **Requirement 8.1**: Create backups with timestamps before modifying files
- **Requirement 8.2**: Store backups in separate directory with metadata
- **Requirement 8.3**: Provide restoration functionality with validation
- **Requirement 8.4**: Validate backup integrity
- **Requirement 8.5**: List and manage multiple backups

## Core Components

### BackupManager Class

The main class that handles all backup operations.

```python
from backup_manager import BackupManager
from config import YML_DIR, BACKUP_DIR

manager = BackupManager(YML_DIR, BACKUP_DIR)
```

### Key Methods

#### 1. create_backup()

Creates a timestamped backup of YML files.

```python
# Backup all YML files
backup_id = manager.create_backup()

# Backup specific files
yml_files = [Path("seite1_f1.yml"), Path("seite2_f1.yml")]
backup_id = manager.create_backup(yml_files)
```

**Returns**: Unique backup ID (e.g., `backup_2025-01-10_14-30-00`)

**Features**:
- Automatic timestamp generation
- Creates backup manifest with metadata
- Preserves file attributes (timestamps, permissions)
- Reports number of files backed up

#### 2. list_backups()

Lists all available backups in reverse chronological order.

```python
backups = manager.list_backups()

for backup in backups:
    print(f"ID: {backup['backup_id']}")
    print(f"Timestamp: {backup['timestamp']}")
    print(f"Files: {backup['files_count']}")
```

**Returns**: List of dictionaries with backup information

**Backup Information**:
- `backup_id`: Unique identifier
- `timestamp`: Creation time
- `yml_dir`: Original YML directory
- `files_count`: Number of files in backup
- `files`: List of backed up filenames

#### 3. validate_backup()

Validates backup integrity and completeness.

```python
validation = manager.validate_backup(backup_id)

if validation['valid']:
    print("Backup is valid and can be restored")
else:
    print("Backup validation failed:")
    for error in validation['errors']:
        print(f"  - {error}")
```

**Returns**: Dictionary with validation results

**Validation Checks**:
- Backup directory exists
- Manifest file is present and valid
- All YML files are readable and valid YAML
- File count matches manifest
- No corrupted files

**Validation Result Structure**:
```python
{
    "backup_id": "backup_2025-01-10_14-30-00",
    "valid": True,
    "exists": True,
    "manifest_valid": True,
    "files_valid": True,
    "errors": [],
    "warnings": []
}
```

#### 4. restore_backup()

Restores YML files from a backup.

```python
# Dry run (preview what would be restored)
manager.restore_backup(backup_id, confirm=False)

# Actual restoration
manager.restore_backup(backup_id, confirm=True)
```

**Parameters**:
- `backup_id`: Backup to restore
- `confirm`: If False, performs dry run only

**Safety Features**:
- Validates backup before restoration
- Creates backup of current state before restoring
- Reports which files will be overwritten
- Dry-run mode for preview

## Convenience Functions

For quick operations without creating a BackupManager instance:

```python
from backup_manager import create_backup, restore_backup, list_backups, validate_backup

# Create backup
backup_id = create_backup()

# List backups
backups = list_backups()

# Validate backup
validation = validate_backup(backup_id)

# Restore backup
restore_backup(backup_id, confirm=True)
```

## Backup Structure

### Directory Layout

```
coords_multi_backup/
├── backup_2025-01-10_14-30-00/
│   ├── backup_manifest.yml
│   ├── seite1_f1.yml
│   ├── seite1_f2.yml
│   └── ...
├── backup_2025-01-10_15-45-00/
│   ├── backup_manifest.yml
│   └── ...
└── backup_2025-01-11_09-15-00/
    └── ...
```

### Manifest File Format

Each backup includes a `backup_manifest.yml` file:

```yaml
backup_id: backup_2025-01-10_14-30-00
timestamp: '2025-01-10_14-30-00'
yml_dir: C:\Users\win10\Desktop\Bokuk2 - Kopie\coords_multi
files_count: 48
files:
  - seite1_f1.yml
  - seite1_f2.yml
  - seite2_f1.yml
  # ... all backed up files
```

## Usage Examples

### Example 1: Basic Backup Workflow

```python
from backup_manager import BackupManager
from config import YML_DIR, BACKUP_DIR

# Initialize manager
manager = BackupManager(YML_DIR, BACKUP_DIR)

# Create backup before making changes
print("Creating backup before modifications...")
backup_id = manager.create_backup()
print(f"Backup created: {backup_id}")

# Make your modifications to YML files here
# ...

# If something goes wrong, restore the backup
print("Restoring backup...")
manager.restore_backup(backup_id, confirm=True)
```

### Example 2: Validate Before Restore

```python
# List available backups
backups = manager.list_backups()
print(f"Found {len(backups)} backups")

# Select a backup to restore
backup_id = backups[0]['backup_id']

# Validate before restoring
validation = manager.validate_backup(backup_id)

if validation['valid']:
    # Preview what will be restored
    manager.restore_backup(backup_id, confirm=False)
    
    # Confirm and restore
    user_input = input("Proceed with restoration? (yes/no): ")
    if user_input.lower() == 'yes':
        manager.restore_backup(backup_id, confirm=True)
else:
    print("Backup validation failed:")
    for error in validation['errors']:
        print(f"  - {error}")
```

### Example 3: Backup Specific Files

```python
from pathlib import Path

# Backup only files for Firma 1
yml_files = list(YML_DIR.glob("*_f1.yml"))
backup_id = manager.create_backup(yml_files)
print(f"Backed up {len(yml_files)} files for Firma 1")
```

### Example 4: Automated Backup Management

```python
# Keep only last 5 backups
backups = manager.list_backups()

if len(backups) > 5:
    old_backups = backups[5:]  # Get backups beyond the 5 most recent
    
    for backup in old_backups:
        backup_path = BACKUP_DIR / backup['backup_id']
        shutil.rmtree(backup_path)
        print(f"Removed old backup: {backup['backup_id']}")
```

## Integration with Main Workflow

The Backup Manager integrates seamlessly with the positioning workflow:

```python
from backup_manager import create_backup
from yml_generator import generate_yml
from position_calculator import calculate_positions

# Create backup before generating new positions
backup_id = create_backup()
print(f"Created backup: {backup_id}")

try:
    # Generate new positions
    for firma in range(1, 7):
        for seite in range(1, 9):
            # Calculate and generate new positions
            new_positions = calculate_positions(firma, seite)
            generate_yml(firma, seite, new_positions)
    
    print("All positions updated successfully")
    
except Exception as e:
    print(f"Error occurred: {e}")
    print("Restoring from backup...")
    restore_backup(backup_id, confirm=True)
```

## Best Practices

1. **Always Create Backups**: Create a backup before any batch modifications
2. **Validate Backups**: Validate backups periodically to ensure integrity
3. **Use Dry Runs**: Preview restorations with `confirm=False` before committing
4. **Manage Backup Storage**: Periodically clean up old backups to save space
5. **Document Backups**: Use the manifest to track what each backup contains
6. **Test Restoration**: Periodically test restoration to ensure backups work

## Error Handling

The Backup Manager handles various error scenarios:

```python
try:
    backup_id = manager.create_backup()
except PermissionError:
    print("Error: No write permission for backup directory")
except Exception as e:
    print(f"Backup failed: {e}")

try:
    manager.restore_backup(backup_id, confirm=True)
except FileNotFoundError:
    print("Error: Backup not found")
except Exception as e:
    print(f"Restoration failed: {e}")
```

## Command-Line Usage

The Backup Manager can be used from command line:

```bash
# Create backup
python -c "from backup_manager import create_backup; print(create_backup())"

# List backups
python -c "from backup_manager import list_backups; [print(b['backup_id']) for b in list_backups()]"

# Validate backup
python -c "from backup_manager import validate_backup; print(validate_backup('backup_2025-01-10_14-30-00'))"

# Restore backup (dry run)
python -c "from backup_manager import restore_backup; restore_backup('backup_2025-01-10_14-30-00', confirm=False)"
```

## Performance Considerations

- **Backup Speed**: ~0.1-0.2 seconds per file
- **Storage**: Each backup requires ~50-100 KB for 48 YML files
- **Validation**: ~0.05 seconds per file
- **Restoration**: ~0.1-0.2 seconds per file

For 48 YML files:
- Backup creation: ~5-10 seconds
- Validation: ~2-3 seconds
- Restoration: ~5-10 seconds

## Troubleshooting

### Backup Creation Fails

**Problem**: Cannot create backup
**Solutions**:
- Check write permissions for backup directory
- Ensure sufficient disk space
- Verify YML directory exists and contains files

### Validation Fails

**Problem**: Backup validation reports errors
**Solutions**:
- Check if backup directory was modified manually
- Verify all YML files are valid YAML format
- Ensure manifest file is intact

### Restoration Fails

**Problem**: Cannot restore backup
**Solutions**:
- Validate backup first with `validate_backup()`
- Check write permissions for YML directory
- Ensure backup directory hasn't been moved or deleted

## See Also

- [YML Parser Reference](YML_PARSER_REFERENCE.md)
- [YML Generator Reference](YML_GENERATOR_REFERENCE.md)
- [Position Calculator Reference](POSITION_CALCULATOR_REFERENCE.md)
