# Configuration Service Quick Reference

## Quick Start

```python
from backend.services.configuration_service import ConfigurationService
from backend.models.configuration_schemas import *

# Initialize
service = ConfigurationService(db_session)

# Create
config = service.create_configuration(
    ConfigurationCreate(
        key="app.setting",
        value="value",
        value_type=ValueType.STRING,
        category=ConfigCategory.USER,
        namespace="app"
    ),
    user="admin"
)

# Read
value = service.get_configuration_value("app.setting", "app")

# Update
service.update_configuration(
    config.id,
    ConfigurationUpdate(value="new_value"),
    user="admin"
)

# Delete
service.delete_configuration(config.id, user="admin")
```

## Common Operations

### CRUD

```python
# Create with validation
config = service.create_configuration(
    ConfigurationCreate(
        key="solar.efficiency",
        value="0.85",
        value_type=ValueType.NUMBER,
        category=ConfigCategory.MODULE,
        namespace="solar",
        validation_schema={"type": "number", "minimum": 0, "maximum": 1}
    )
)

# Get by key
config = service.get_configuration_by_key("solar.efficiency", "solar")

# Get value with type conversion
efficiency = service.get_configuration_value("solar.efficiency", "solar", default=0.8)

# Update
service.update_configuration(
    config.id,
    ConfigurationUpdate(value="0.90")
)

# Search
results, total = service.search_configurations(
    ConfigurationSearch(namespace="solar", limit=50)
)
```

### Versioning

```python
# Get versions
versions = service.get_configuration_versions(config.id)

# Rollback
service.rollback_configuration(config.id, version_number=3, user="admin")
```

### Backup/Restore

```python
# Create backup
backup = service.create_backup(
    ConfigurationBackupCreate(
        backup_name="daily_backup",
        backup_type=BackupType.AUTOMATIC,
        namespace_filter=["solar"]
    )
)

# Restore backup
stats = service.restore_backup(
    ConfigurationRestoreRequest(
        backup_id=backup.id,
        restore_mode="merge"
    )
)
```

### Export/Import

```python
# Export to JSON
json_data = service.export_configurations(
    ConfigurationExport(
        namespace_filter=["solar"],
        format="json"
    )
)

# Import from JSON
stats = service.import_configurations(
    ConfigurationImport(
        data=json_data,
        format="json",
        merge_mode="merge"
    )
)
```

### Migration

```python
# Migrate namespace
stats = service.migrate_configuration(
    from_namespace="old_solar",
    to_namespace="solar",
    key_mapping={"old.key": "new.key"}
)
```

## Value Types

```python
ValueType.STRING   # "text"
ValueType.NUMBER   # 42.5
ValueType.BOOLEAN  # true/false
ValueType.JSON     # {"key": "value"}
ValueType.ARRAY    # ["item1", "item2"]
```

## Categories

```python
ConfigCategory.SYSTEM   # System configurations
ConfigCategory.USER     # User configurations
ConfigCategory.MODULE   # Module configurations
ConfigCategory.FEATURE  # Feature configurations
```

## Validation Schema Examples

### Number Range

```python
{
    "type": "number",
    "minimum": 0,
    "maximum": 100
}
```

### String Pattern

```python
{
    "type": "string",
    "pattern": "^[A-Z]{2,3}$"
}
```

### Enum

```python
{
    "type": "string",
    "enum": ["option1", "option2", "option3"]
}
```

### Object

```python
{
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "number", "minimum": 0}
    },
    "required": ["name"]
}
```

## Cache Operations

```python
# Use cache (default)
config = service.get_configuration_by_key("key", "namespace", use_cache=True)

# Bypass cache
config = service.get_configuration_by_key("key", "namespace", use_cache=False)

# Clear namespace cache
service.cache.clear_namespace("solar")

# Clear all cache
service.cache.clear()
```

## Search Filters

```python
ConfigurationSearch(
    query="search_term",           # Search in key, value, description
    namespace="solar",              # Filter by namespace
    category=ConfigCategory.MODULE, # Filter by category
    is_active=True,                 # Filter by active status
    is_system=False,                # Filter by system flag
    parent_id=None,                 # Filter by parent
    created_after=datetime(...),    # Filter by creation date
    created_before=datetime(...),
    updated_after=datetime(...),    # Filter by update date
    updated_before=datetime(...),
    limit=50,                       # Pagination
    offset=0,
    sort_by="key",                  # Sort column
    sort_order="asc"                # Sort direction
)
```

## Export Formats

### JSON

```python
ConfigurationExport(
    namespace_filter=["solar"],
    include_versions=False,
    format="json"
)
```

### YAML

```python
ConfigurationExport(
    namespace_filter=["solar"],
    format="yaml"
)
```

### CSV

```python
ConfigurationExport(
    namespace_filter=["solar"],
    format="csv"
)
```

## Import Modes

```python
# Merge: Create new, update changed
ConfigurationImport(data=data, format="json", merge_mode="merge")

# Replace: Always update existing
ConfigurationImport(data=data, format="json", merge_mode="replace")

# Skip: Create new only
ConfigurationImport(data=data, format="json", merge_mode="skip")
```

## Restore Modes

```python
# Merge: Update only if value changed
ConfigurationRestoreRequest(backup_id=1, restore_mode="merge")

# Replace: Always update
ConfigurationRestoreRequest(backup_id=1, restore_mode="replace")

# Selective: Restore specific namespaces
ConfigurationRestoreRequest(
    backup_id=1,
    restore_mode="merge",
    namespace_filter=["solar"]
)
```

## Dry Run

```python
# Preview import without applying
import_params = ConfigurationImport(
    data=data,
    format="json",
    dry_run=True
)
stats = service.import_configurations(import_params)
# Review stats['created'], stats['updated'], stats['errors']

# Preview restore without applying
restore_request = ConfigurationRestoreRequest(
    backup_id=1,
    dry_run=True
)
stats = service.restore_backup(restore_request)
```

## Error Handling

```python
from fastapi import HTTPException

try:
    config = service.create_configuration(config_data)
except HTTPException as e:
    if e.status_code == 409:
        print("Configuration already exists")
    elif e.status_code == 422:
        print(f"Validation failed: {e.detail}")
    elif e.status_code == 404:
        print("Not found")
    elif e.status_code == 403:
        print("Forbidden")
```

## Audit Trail

```python
# All operations are automatically logged
# Query audit logs from database:
from backend.models.configuration_models import ConfigurationAuditLog

audit_logs = db.query(ConfigurationAuditLog).filter(
    ConfigurationAuditLog.configuration_id == config.id
).order_by(ConfigurationAuditLog.timestamp.desc()).all()

for log in audit_logs:
    print(f"{log.timestamp}: {log.action} by {log.username}")
    print(f"  Old: {log.old_value}")
    print(f"  New: {log.new_value}")
```

## Best Practices

### Naming Conventions

```python
# Use dot notation for hierarchical keys
"solar.module.efficiency"
"solar.inverter.max_power"
"heatpump.cop.winter"

# Use descriptive namespaces
namespace="solar"
namespace="heatpump"
namespace="pdf"
namespace="crm"
```

### Type Safety

```python
# Always specify value_type
value_type=ValueType.NUMBER  # For numbers
value_type=ValueType.BOOLEAN # For booleans
value_type=ValueType.JSON    # For objects
```

### Validation

```python
# Add validation for critical configurations
validation_schema={
    "type": "number",
    "minimum": 0,
    "maximum": 100,
    "description": "Must be between 0 and 100"
}
```

### Security

```python
# Mark sensitive configurations
is_sensitive=True  # Hide in UI
is_encrypted=True  # Encrypt value

# Protect system configurations
is_system=True  # Prevent deletion
```

## Performance Tips

1. **Use Caching**: Enable for read-heavy operations
2. **Batch Operations**: Use import for multiple configs
3. **Filter Early**: Use namespace and category filters
4. **Limit Results**: Use pagination for large datasets
5. **Clear Cache**: After bulk operations

## Common Patterns

### Configuration with Default

```python
def get_setting(key: str, namespace: str = "app", default: Any = None):
    return service.get_configuration_value(key, namespace, default)

max_size = get_setting("solar.max_system_size", "solar", default=100)
```

### Hierarchical Configuration

```python
# Parent configuration
parent = service.create_configuration(
    ConfigurationCreate(
        key="theme",
        value="default",
        category=ConfigCategory.SYSTEM,
        namespace="ui"
    )
)

# Child configuration
child = service.create_configuration(
    ConfigurationCreate(
        key="theme.primary_color",
        value="#007bff",
        category=ConfigCategory.SYSTEM,
        namespace="ui",
        parent_id=parent.id
    )
)
```

### Scheduled Backups

```python
from datetime import datetime

def create_daily_backup():
    backup_name = f"daily_{datetime.now().strftime('%Y%m%d')}"
    
    backup = service.create_backup(
        ConfigurationBackupCreate(
            backup_name=backup_name,
            backup_type=BackupType.AUTOMATIC,
            retention_days=30,
            is_compressed=True
        ),
        user="system"
    )
    
    return backup
```

## Troubleshooting

### Configuration Not Found

```python
config = service.get_configuration_by_key("key", "namespace")
if config is None:
    # Use default or create
    config = service.create_configuration(...)
```

### Cache Stale Data

```python
# Force refresh
config = service.get_configuration_by_key("key", "namespace", use_cache=False)

# Or clear cache
service.cache.clear_namespace("namespace")
```

### Import Errors

```python
# Use dry run first
import_params.dry_run = True
stats = service.import_configurations(import_params)

# Check errors
for error in stats['errors']:
    print(f"Error: {error}")

# Then import for real
import_params.dry_run = False
stats = service.import_configurations(import_params)
```

## Quick Commands

```bash
# Run tests
pytest backend/tests/test_configuration_service.py -v

# Check coverage
pytest backend/tests/test_configuration_service.py --cov=backend.services.configuration_service

# Run specific test
pytest backend/tests/test_configuration_service.py::TestConfigurationCRUD::test_create_configuration -v
```

## Resources

- [Configuration Service Guide](CONFIGURATION_SERVICE_GUIDE.md)
- [Configuration Database Schema](CONFIGURATION_DATABASE_SCHEMA.md)
- [API Documentation](API_DOCUMENTATION.md)
