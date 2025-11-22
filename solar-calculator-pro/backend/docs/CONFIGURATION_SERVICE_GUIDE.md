# Configuration Service Guide

## Overview

The Configuration Service provides comprehensive configuration management for the Solar Calculator Pro application. It offers CRUD operations, caching, validation, versioning, backup/restore, export/import, and migration capabilities.

## Table of Contents

1. [Features](#features)
2. [Architecture](#architecture)
3. [Usage Examples](#usage-examples)
4. [API Reference](#api-reference)
5. [Caching Strategy](#caching-strategy)
6. [Validation](#validation)
7. [Versioning and Rollback](#versioning-and-rollback)
8. [Backup and Restore](#backup-and-restore)
9. [Export and Import](#export-and-import)
10. [Migration](#migration)
11. [Best Practices](#best-practices)
12. [Troubleshooting](#troubleshooting)

## Features

### Core Features

- **CRUD Operations**: Create, read, update, and delete configurations
- **Hierarchical Configuration**: Parent-child relationships for configuration inheritance
- **Namespacing**: Isolate configurations by module, feature, or tenant
- **Type Safety**: Support for string, number, boolean, JSON, and array types
- **Validation**: JSON Schema validation for configuration values
- **Versioning**: Complete version history with rollback capability
- **Caching**: In-memory caching with TTL and namespace-based invalidation
- **Audit Trail**: Complete logging of all configuration operations
- **Backup/Restore**: Point-in-time recovery with compression and encryption
- **Export/Import**: JSON, YAML, and CSV format support
- **Migration**: Move configurations between namespaces with key mapping

### Security Features

- **Encryption Support**: Mark sensitive configurations for encryption
- **System Protection**: Prevent deletion of system configurations
- **Audit Logging**: Track all access and modifications
- **User Attribution**: Record who made each change

### Performance Features

- **Caching**: Reduce database queries with intelligent caching
- **Batch Operations**: Import/export multiple configurations efficiently
- **Lazy Loading**: Load configurations on demand
- **Index Optimization**: Strategic database indexes for fast queries

## Architecture

### Service Layer

```
ConfigurationService
├── CRUD Operations
│   ├── create_configuration()
│   ├── get_configuration()
│   ├── get_configuration_by_key()
│   ├── get_configuration_value()
│   ├── update_configuration()
│   ├── delete_configuration()
│   └── search_configurations()
├── Caching
│   ├── ConfigurationCache
│   └── Cache invalidation
├── Validation
│   └── JSON Schema validation
├── Versioning
│   ├── get_configuration_versions()
│   └── rollback_configuration()
├── Backup/Restore
│   ├── create_backup()
│   └── restore_backup()
├── Export/Import
│   ├── export_configurations()
│   └── import_configurations()
└── Migration
    └── migrate_configuration()
```

### Database Models

- **Configuration**: Main configuration storage
- **ConfigurationVersion**: Version history
- **ConfigurationAuditLog**: Audit trail
- **ConfigurationBackup**: Backup snapshots
- **ConfigurationValidationRule**: Validation rules
- **ConfigurationTemplate**: Reusable templates

## Usage Examples

### Basic CRUD Operations

#### Create Configuration

```python
from backend.services.configuration_service import ConfigurationService
from backend.models.configuration_schemas import ConfigurationCreate, ValueType, ConfigCategory

# Initialize service
service = ConfigurationService(db_session)

# Create configuration
config_data = ConfigurationCreate(
    key="solar.max_system_size",
    value="100",
    value_type=ValueType.NUMBER,
    description="Maximum solar system size in kWp",
    category=ConfigCategory.MODULE,
    namespace="solar",
    validation_schema={
        "type": "number",
        "minimum": 1,
        "maximum": 1000
    }
)

config = service.create_configuration(config_data, user="admin")
print(f"Created configuration: {config.key} with ID {config.id}")
```

#### Get Configuration

```python
# Get by ID
config = service.get_configuration(config_id=1)

# Get by key and namespace
config = service.get_configuration_by_key("solar.max_system_size", "solar")

# Get value with type conversion
max_size = service.get_configuration_value("solar.max_system_size", "solar", default=50)
print(f"Max system size: {max_size} kWp")  # Returns float
```

#### Update Configuration

```python
from backend.models.configuration_schemas import ConfigurationUpdate

update_data = ConfigurationUpdate(
    value="150",
    description="Updated maximum system size"
)

updated_config = service.update_configuration(
    config_id=1,
    update_data=update_data,
    user="admin"
)

print(f"Updated to version {updated_config.version}")
```

#### Delete Configuration

```python
# Soft delete (default)
result = service.delete_configuration(config_id=1, user="admin")

# Force delete system configuration
result = service.delete_configuration(config_id=1, user="admin", force=True)
```

#### Search Configurations

```python
from backend.models.configuration_schemas import ConfigurationSearch

search_params = ConfigurationSearch(
    query="solar",  # Search in key, value, description
    namespace="solar",
    category=ConfigCategory.MODULE,
    is_active=True,
    limit=50,
    offset=0,
    sort_by="key",
    sort_order="asc"
)

results, total_count = service.search_configurations(search_params)

print(f"Found {total_count} configurations")
for config in results:
    print(f"  - {config.key}: {config.value}")
```

### Caching

#### Using Cache

```python
# Get with cache (default)
config = service.get_configuration_by_key("solar.max_system_size", "solar", use_cache=True)

# Bypass cache
config = service.get_configuration_by_key("solar.max_system_size", "solar", use_cache=False)

# Clear cache for namespace
service.cache.clear_namespace("solar")

# Clear all cache
service.cache.clear()
```

### Validation

#### Create with Validation

```python
config_data = ConfigurationCreate(
    key="solar.efficiency",
    value="0.85",
    value_type=ValueType.NUMBER,
    category=ConfigCategory.MODULE,
    namespace="solar",
    validation_schema={
        "type": "number",
        "minimum": 0,
        "maximum": 1,
        "description": "Efficiency must be between 0 and 1"
    }
)

try:
    config = service.create_configuration(config_data, user="admin")
except HTTPException as e:
    print(f"Validation failed: {e.detail}")
```

### Versioning and Rollback

#### Get Version History

```python
versions = service.get_configuration_versions(config_id=1, limit=10)

for version in versions:
    print(f"Version {version.version_number}: {version.value}")
    print(f"  Changed: {version.change_type}")
    print(f"  By: {version.created_by}")
    print(f"  At: {version.created_at}")
```

#### Rollback to Previous Version

```python
# Rollback to version 3
rolled_back = service.rollback_configuration(
    config_id=1,
    version_number=3,
    user="admin"
)

print(f"Rolled back to version 3, new version is {rolled_back.version}")
```

### Backup and Restore

#### Create Backup

```python
from backend.models.configuration_schemas import ConfigurationBackupCreate, BackupType

backup_data = ConfigurationBackupCreate(
    backup_name=f"daily_backup_{datetime.now().strftime('%Y%m%d')}",
    backup_type=BackupType.AUTOMATIC,
    description="Daily automatic backup",
    is_compressed=True,
    is_encrypted=False,
    retention_days=30,
    namespace_filter=["solar", "heatpump"],  # Optional: backup specific namespaces
    category_filter=["module", "system"]     # Optional: backup specific categories
)

backup = service.create_backup(backup_data, user="system")
print(f"Created backup with {backup.configuration_count} configurations")
```

#### Restore Backup

```python
from backend.models.configuration_schemas import ConfigurationRestoreRequest

restore_request = ConfigurationRestoreRequest(
    backup_id=1,
    restore_mode="merge",  # merge, replace, or selective
    namespace_filter=["solar"],  # Optional: restore specific namespaces
    dry_run=False  # Set to True to preview changes
)

stats = service.restore_backup(restore_request, user="admin")

print(f"Restore complete:")
print(f"  Created: {stats['created']}")
print(f"  Updated: {stats['updated']}")
print(f"  Skipped: {stats['skipped']}")
print(f"  Errors: {len(stats['errors'])}")
```

### Export and Import

#### Export Configurations

```python
from backend.models.configuration_schemas import ConfigurationExport

# Export to JSON
export_params = ConfigurationExport(
    namespace_filter=["solar"],
    category_filter=["module"],
    include_versions=False,
    format="json"
)

json_data = service.export_configurations(export_params, user="admin")

# Save to file
with open("solar_config.json", "w") as f:
    f.write(json_data)

# Export to YAML
export_params.format = "yaml"
yaml_data = service.export_configurations(export_params, user="admin")

# Export to CSV
export_params.format = "csv"
csv_data = service.export_configurations(export_params, user="admin")
```

#### Import Configurations

```python
from backend.models.configuration_schemas import ConfigurationImport

# Read from file
with open("solar_config.json", "r") as f:
    import_data = f.read()

import_params = ConfigurationImport(
    data=import_data,
    format="json",
    merge_mode="merge",  # merge, replace, or skip
    validate_before_import=True,
    dry_run=False  # Set to True to preview changes
)

stats = service.import_configurations(import_params, user="admin")

print(f"Import complete:")
print(f"  Created: {stats['created']}")
print(f"  Updated: {stats['updated']}")
print(f"  Skipped: {stats['skipped']}")
print(f"  Errors: {len(stats['errors'])}")
```

### Migration

#### Migrate Between Namespaces

```python
# Simple migration
stats = service.migrate_configuration(
    from_namespace="old_solar",
    to_namespace="solar",
    user="admin"
)

# Migration with key renaming
key_mapping = {
    "old.key.name": "new.key.name",
    "deprecated.setting": "current.setting"
}

stats = service.migrate_configuration(
    from_namespace="legacy",
    to_namespace="current",
    key_mapping=key_mapping,
    user="admin"
)

print(f"Migration complete:")
print(f"  Migrated: {stats['migrated']}")
print(f"  Skipped: {stats['skipped']}")
print(f"  Errors: {len(stats['errors'])}")
```

## API Reference

### ConfigurationService

#### `__init__(db: Session)`

Initialize the configuration service.

**Parameters:**
- `db`: SQLAlchemy database session

#### `create_configuration(config_data: ConfigurationCreate, user: Optional[str] = None) -> Configuration`

Create a new configuration.

**Parameters:**
- `config_data`: Configuration creation data
- `user`: Username for audit trail

**Returns:** Created configuration

**Raises:** HTTPException if validation fails or key already exists

#### `get_configuration(config_id: int, use_cache: bool = True) -> Optional[Configuration]`

Get configuration by ID.

**Parameters:**
- `config_id`: Configuration ID
- `use_cache`: Whether to use cache

**Returns:** Configuration or None if not found

#### `get_configuration_by_key(key: str, namespace: str = "global", use_cache: bool = True) -> Optional[Configuration]`

Get configuration by key and namespace.

**Parameters:**
- `key`: Configuration key
- `namespace`: Configuration namespace
- `use_cache`: Whether to use cache

**Returns:** Configuration or None if not found

#### `get_configuration_value(key: str, namespace: str = "global", default: Any = None, use_cache: bool = True) -> Any`

Get configuration value with type conversion.

**Parameters:**
- `key`: Configuration key
- `namespace`: Configuration namespace
- `default`: Default value if not found
- `use_cache`: Whether to use cache

**Returns:** Configuration value or default

#### `update_configuration(config_id: int, update_data: ConfigurationUpdate, user: Optional[str] = None) -> Configuration`

Update configuration.

**Parameters:**
- `config_id`: Configuration ID
- `update_data`: Update data
- `user`: Username for audit trail

**Returns:** Updated configuration

**Raises:** HTTPException if not found or validation fails

#### `delete_configuration(config_id: int, user: Optional[str] = None, force: bool = False) -> bool`

Delete configuration (soft delete by default).

**Parameters:**
- `config_id`: Configuration ID
- `user`: Username for audit trail
- `force`: Force delete system configurations

**Returns:** True if deleted

**Raises:** HTTPException if not found or cannot delete

#### `search_configurations(search_params: ConfigurationSearch) -> Tuple[List[Configuration], int]`

Search configurations with filters.

**Parameters:**
- `search_params`: Search parameters

**Returns:** Tuple of (configurations, total_count)

#### `get_configuration_versions(config_id: int, limit: int = 50) -> List[ConfigurationVersion]`

Get version history for configuration.

**Parameters:**
- `config_id`: Configuration ID
- `limit`: Maximum number of versions to return

**Returns:** List of versions

#### `rollback_configuration(config_id: int, version_number: int, user: Optional[str] = None) -> Configuration`

Rollback configuration to a previous version.

**Parameters:**
- `config_id`: Configuration ID
- `version_number`: Version number to rollback to
- `user`: Username for audit trail

**Returns:** Updated configuration

**Raises:** HTTPException if not found or invalid version

#### `create_backup(backup_data: ConfigurationBackupCreate, user: Optional[str] = None) -> ConfigurationBackup`

Create configuration backup.

**Parameters:**
- `backup_data`: Backup creation data
- `user`: Username for audit trail

**Returns:** Created backup

#### `restore_backup(restore_request: ConfigurationRestoreRequest, user: Optional[str] = None) -> Dict[str, Any]`

Restore configuration from backup.

**Parameters:**
- `restore_request`: Restore request data
- `user`: Username for audit trail

**Returns:** Restore result with statistics

**Raises:** HTTPException if backup not found

#### `export_configurations(export_params: ConfigurationExport, user: Optional[str] = None) -> str`

Export configurations to JSON, YAML, or CSV.

**Parameters:**
- `export_params`: Export parameters
- `user`: Username for audit trail

**Returns:** Exported data as string

#### `import_configurations(import_params: ConfigurationImport, user: Optional[str] = None) -> Dict[str, Any]`

Import configurations from JSON, YAML, or CSV.

**Parameters:**
- `import_params`: Import parameters
- `user`: Username for audit trail

**Returns:** Import result with statistics

#### `migrate_configuration(from_namespace: str, to_namespace: str, key_mapping: Optional[Dict[str, str]] = None, user: Optional[str] = None) -> Dict[str, Any]`

Migrate configurations from one namespace to another.

**Parameters:**
- `from_namespace`: Source namespace
- `to_namespace`: Target namespace
- `key_mapping`: Optional key renaming map
- `user`: Username for audit trail

**Returns:** Migration result with statistics

## Caching Strategy

### Cache Behavior

- **TTL**: Default 5 minutes (300 seconds)
- **Invalidation**: Automatic on create, update, delete
- **Namespace Clearing**: Clear all cache entries for a namespace
- **Manual Control**: Bypass cache with `use_cache=False`

### Cache Keys

- By ID: `config:id:{config_id}`
- By key: `config:{namespace}:{key}`
- Namespace prefix: `{namespace}:`

### Best Practices

1. Use cache for read-heavy operations
2. Bypass cache when you need the latest data
3. Clear namespace cache after bulk operations
4. Monitor cache hit rates

## Validation

### JSON Schema Validation

Configurations can be validated against JSON Schema:

```python
validation_schema = {
    "type": "object",
    "properties": {
        "min": {"type": "number", "minimum": 0},
        "max": {"type": "number", "maximum": 100}
    },
    "required": ["min", "max"]
}
```

### Validation Rules

- Applied on create and update
- Validation errors prevent save
- Custom error messages supported
- Severity levels: error, warning, info

## Versioning and Rollback

### Version Tracking

- Every change creates a new version
- Version number increments automatically
- Previous values stored for comparison
- Change type tracked (created, updated, deleted, restored)

### Rollback Process

1. Get target version
2. Restore value from version
3. Create new version for rollback
4. Increment version number
5. Log audit entry

## Backup and Restore

### Backup Features

- **Compression**: gzip, bzip2, lzma support
- **Encryption**: Optional encryption for sensitive data
- **Filtering**: Backup specific namespaces/categories
- **Retention**: Automatic expiration based on retention days
- **Checksum**: SHA-256 verification

### Restore Modes

- **Merge**: Update only if value changed
- **Replace**: Always update existing configurations
- **Selective**: Restore specific namespaces/categories

### Dry Run

Preview changes before applying:

```python
restore_request.dry_run = True
stats = service.restore_backup(restore_request)
# Review stats without making changes
```

## Export and Import

### Supported Formats

- **JSON**: Full fidelity, includes all fields
- **YAML**: Human-readable, good for version control
- **CSV**: Simple format, limited to basic fields

### Import Modes

- **Merge**: Create new, update changed
- **Replace**: Always update existing
- **Skip**: Create new only, skip existing

### Validation

- Validate before import (optional)
- Dry run to preview changes
- Error reporting for failed imports

## Migration

### Use Cases

- Rename namespaces
- Consolidate configurations
- Split configurations
- Rename keys

### Key Mapping

```python
key_mapping = {
    "old.key": "new.key",
    "deprecated": "current"
}
```

### Migration Process

1. Query source configurations
2. Apply key mapping
3. Check for conflicts in target
4. Create in target namespace
5. Report statistics

## Best Practices

### Configuration Design

1. **Use Namespaces**: Isolate by module/feature
2. **Hierarchical Keys**: Use dot notation (e.g., `solar.module.efficiency`)
3. **Type Safety**: Always specify value_type
4. **Validation**: Add schemas for critical configurations
5. **Documentation**: Provide clear descriptions

### Performance

1. **Use Caching**: Enable for read-heavy operations
2. **Batch Operations**: Use import for multiple configurations
3. **Index Usage**: Filter by namespace and category
4. **Limit Results**: Use pagination for large result sets

### Security

1. **Mark Sensitive**: Use `is_sensitive` for passwords/keys
2. **Encrypt Values**: Enable encryption for sensitive data
3. **System Protection**: Mark critical configs as `is_system`
4. **Audit Trail**: Review audit logs regularly

### Maintenance

1. **Regular Backups**: Schedule automatic backups
2. **Retention Policies**: Set appropriate retention days
3. **Version Cleanup**: Archive old versions periodically
4. **Monitor Usage**: Track configuration access patterns

## Troubleshooting

### Common Issues

#### Configuration Not Found

```python
config = service.get_configuration_by_key("missing.key", "namespace")
if config is None:
    # Handle missing configuration
    print("Configuration not found, using default")
```

#### Validation Errors

```python
try:
    config = service.create_configuration(config_data)
except HTTPException as e:
    if e.status_code == 422:
        print(f"Validation failed: {e.detail}")
```

#### Cache Inconsistency

```python
# Force refresh from database
config = service.get_configuration_by_key("key", "namespace", use_cache=False)

# Or clear cache
service.cache.clear_namespace("namespace")
```

#### Import Failures

```python
import_params.dry_run = True
stats = service.import_configurations(import_params)

# Review errors
for error in stats['errors']:
    print(f"Error: {error['key']} - {error['error']}")
```

### Debug Mode

Enable detailed logging:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("backend.services.configuration_service")
logger.setLevel(logging.DEBUG)
```

### Performance Issues

1. **Check Cache Hit Rate**: Monitor cache effectiveness
2. **Review Queries**: Use database query logging
3. **Optimize Filters**: Use indexed columns
4. **Batch Operations**: Reduce individual queries

## Conclusion

The Configuration Service provides a robust, enterprise-grade solution for managing application configurations. With features like versioning, backup/restore, and comprehensive validation, it ensures configuration integrity and reliability.

For additional support, refer to:
- [Configuration Database Schema](CONFIGURATION_DATABASE_SCHEMA.md)
- [Configuration Schema Quick Reference](CONFIGURATION_SCHEMA_QUICK_REFERENCE.md)
- [API Documentation](API_DOCUMENTATION.md)
