# Configuration Database Schema - Quick Reference

## Tables Overview

| Table | Purpose | Key Features |
|-------|---------|--------------|
| `configurations` | Main config storage | Versioning, inheritance, validation |
| `configuration_versions` | Version history | Complete change tracking |
| `configuration_audit_logs` | Audit trail | All access/modifications logged |
| `configuration_backups` | Backup snapshots | Point-in-time recovery |
| `configuration_validation_rules` | Validation rules | Schema-based validation |
| `configuration_templates` | Reusable templates | Quick setup |

## Quick Commands

### Create Configuration

```python
config = Configuration(
    key="app.max_users",
    value="100",
    value_type="number",
    category="system",
    namespace="global",
    description="Maximum concurrent users"
)
db.add(config)
db.commit()
```

### Query Configuration

```python
# By key and namespace
config = db.query(Configuration).filter(
    Configuration.key == "app.max_users",
    Configuration.namespace == "global",
    Configuration.is_active == True
).first()

# All in namespace
configs = db.query(Configuration).filter(
    Configuration.namespace == "solar",
    Configuration.is_active == True
).all()
```

### Update Configuration (with versioning)

```python
old_value = config.value
config.value = "200"
config.version += 1
config.updated_by = "admin"

# Create version record
version = ConfigurationVersion(
    configuration_id=config.id,
    version_number=config.version,
    value=config.value,
    value_type=config.value_type,
    change_type="updated",
    previous_value=old_value,
    created_by="admin"
)
db.add(version)
db.commit()
```

### Create Backup

```python
configs = db.query(Configuration).filter(
    Configuration.is_active == True
).all()

backup = ConfigurationBackup(
    backup_name=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
    backup_type="manual",
    configuration_data={
        "configs": [c.to_dict() for c in configs]
    },
    configuration_count=len(configs),
    status="completed",
    created_by="admin"
)
db.add(backup)
db.commit()
```

### Apply Template

```python
template = db.query(ConfigurationTemplate).filter(
    ConfigurationTemplate.template_name == "solar_defaults"
).first()

for key, value in template.configuration_data.items():
    config = Configuration(
        key=key,
        value=str(value),
        namespace="project_123",
        category="module"
    )
    db.add(config)

template.usage_count += 1
template.last_used_at = datetime.now()
db.commit()
```

## Value Types

| Type | Description | Example |
|------|-------------|---------|
| `string` | Text value | `"Hello World"` |
| `number` | Numeric value | `"42"` or `"3.14"` |
| `boolean` | True/False | `"true"` or `"false"` |
| `json` | JSON object | `'{"key": "value"}'` |
| `array` | JSON array | `'["item1", "item2"]'` |

## Categories

| Category | Use Case |
|----------|----------|
| `system` | System-wide settings |
| `user` | User-specific settings |
| `module` | Module/feature settings |
| `feature` | Feature flags |

## Common Namespaces

| Namespace | Purpose |
|-----------|---------|
| `global` | Application-wide |
| `solar` | Solar calculator |
| `heatpump` | Heat pump calculator |
| `pdf` | PDF generation |
| `crm` | CRM system |
| `pricing` | Price matrix |

## Validation Schema Examples

### Number Range

```json
{
  "type": "number",
  "minimum": 0,
  "maximum": 100
}
```

### String Pattern

```json
{
  "type": "string",
  "pattern": "^[A-Z]{2}[0-9]{4}$"
}
```

### Enum

```json
{
  "type": "string",
  "enum": ["small", "medium", "large"]
}
```

### Object

```json
{
  "type": "object",
  "properties": {
    "host": {"type": "string"},
    "port": {"type": "number"}
  },
  "required": ["host", "port"]
}
```

## Indexes

### configurations

- `idx_config_key`: Fast key lookup
- `idx_config_key_namespace`: Unique key per namespace
- `idx_config_category_active`: Filter by category
- `idx_config_namespace_active`: Filter by namespace

### configuration_versions

- `idx_version_config_version`: Version history lookup
- `idx_version_created_at`: Time-based queries

### configuration_audit_logs

- `idx_audit_action_timestamp`: Action history
- `idx_audit_user_timestamp`: User activity
- `idx_audit_config_timestamp`: Config history

## Best Practices

### ✅ DO

- Use dot notation for keys: `module.feature.setting`
- Set validation schemas for all configs
- Create backups before major changes
- Use namespaces for isolation
- Mark sensitive configs appropriately
- Document configuration purpose

### ❌ DON'T

- Store large binary data in value field
- Delete system configurations
- Skip version creation on updates
- Use special characters in keys
- Store passwords unencrypted
- Modify audit logs

## Common Queries

### Get All Active Configs in Namespace

```python
configs = db.query(Configuration).filter(
    Configuration.namespace == "solar",
    Configuration.is_active == True
).all()
```

### Get Config with Version History

```python
config = db.query(Configuration).filter(
    Configuration.id == config_id
).first()

versions = db.query(ConfigurationVersion).filter(
    ConfigurationVersion.configuration_id == config_id
).order_by(ConfigurationVersion.version_number.desc()).all()
```

### Get Recent Audit Logs

```python
from datetime import datetime, timedelta

recent_logs = db.query(ConfigurationAuditLog).filter(
    ConfigurationAuditLog.timestamp >= datetime.now() - timedelta(days=7)
).order_by(ConfigurationAuditLog.timestamp.desc()).limit(100).all()
```

### Find Configs by Pattern

```python
configs = db.query(Configuration).filter(
    Configuration.key.like("solar.%"),
    Configuration.is_active == True
).all()
```

### Get Expired Backups

```python
expired_backups = db.query(ConfigurationBackup).filter(
    ConfigurationBackup.expires_at < datetime.now(),
    ConfigurationBackup.status == "completed"
).all()
```

## Migration Commands

```bash
# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1

# Check current version
alembic current

# Show migration history
alembic history
```

## Troubleshooting

### Issue: Duplicate Key Error

```python
# Check if key exists
existing = db.query(Configuration).filter(
    Configuration.key == key,
    Configuration.namespace == namespace
).first()

if existing:
    # Update instead of create
    existing.value = new_value
else:
    # Create new
    config = Configuration(key=key, value=new_value)
    db.add(config)
```

### Issue: Invalid JSON Value

```python
import json

try:
    if config.value_type == "json":
        json.loads(config.value)
except json.JSONDecodeError as e:
    raise ValueError(f"Invalid JSON: {e}")
```

### Issue: Circular Parent Reference

```python
def check_circular_reference(config_id, parent_id, db):
    """Check if parent_id would create circular reference"""
    current_id = parent_id
    visited = set()
    
    while current_id:
        if current_id == config_id:
            return True  # Circular reference detected
        if current_id in visited:
            return True  # Loop detected
        visited.add(current_id)
        
        parent = db.query(Configuration).filter(
            Configuration.id == current_id
        ).first()
        current_id = parent.parent_id if parent else None
    
    return False  # No circular reference
```

## Performance Tips

1. **Use Indexes**: Query by indexed columns (key, namespace, category)
2. **Batch Operations**: Use bulk insert/update for multiple configs
3. **Cache Frequently Used**: Cache configs that don't change often
4. **Limit Version History**: Archive old versions periodically
5. **Compress Backups**: Enable compression for large backups
6. **Partition Audit Logs**: Archive old logs to separate table

## Security Checklist

- [ ] Encrypt sensitive configurations
- [ ] Mark sensitive configs with `is_sensitive=True`
- [ ] Audit all configuration access
- [ ] Restrict system config modifications
- [ ] Use validation schemas
- [ ] Regular backup testing
- [ ] Monitor audit logs for suspicious activity
- [ ] Implement role-based access control

## Related Documentation

- [Configuration Database Schema](./CONFIGURATION_DATABASE_SCHEMA.md) - Complete documentation
- [Configuration Service API](./CONFIGURATION_SERVICE_API.md) - API endpoints
- [Configuration Management Guide](./CONFIGURATION_MANAGEMENT_GUIDE.md) - Usage guide

## Support

For issues or questions:
- Check the complete documentation
- Review audit logs for errors
- Verify database constraints
- Test with dry-run mode first
