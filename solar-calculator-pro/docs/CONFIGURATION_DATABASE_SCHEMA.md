# Configuration Database Schema Documentation

## Overview

The Configuration Database Schema provides a comprehensive, enterprise-grade system for managing dynamic application configuration. It supports versioning, inheritance, validation, backup/restore, and complete audit trails.

## Table of Contents

1. [Architecture](#architecture)
2. [Tables](#tables)
3. [Features](#features)
4. [Usage Examples](#usage-examples)
5. [Best Practices](#best-practices)
6. [Migration Guide](#migration-guide)

## Architecture

### Design Principles

- **Hierarchical Configuration**: Support parent-child relationships for configuration inheritance
- **Version Control**: Track all configuration changes with complete history
- **Audit Trail**: Log all access and modifications for compliance
- **Backup & Restore**: Point-in-time recovery capabilities
- **Validation**: Schema-based validation with custom rules
- **Templates**: Reusable configuration templates
- **Namespacing**: Isolate configurations by module/feature
- **Security**: Encryption support for sensitive values

### Entity Relationship Diagram

```
┌─────────────────────┐
│  configurations     │
│  (Main Config)      │
├─────────────────────┤
│ id (PK)             │
│ key                 │
│ value               │
│ namespace           │
│ parent_id (FK)      │◄──┐
│ version             │   │
│ ...                 │   │
└─────────────────────┘   │
         │                │
         │ 1:N            │ Self-Reference
         ▼                │
┌─────────────────────┐   │
│ configuration_      │   │
│ versions            │   │
├─────────────────────┤   │
│ id (PK)             │   │
│ configuration_id(FK)│───┘
│ version_number      │
│ value               │
│ change_type         │
│ ...                 │
└─────────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────────┐
│ configuration_      │
│ audit_logs          │
├─────────────────────┤
│ id (PK)             │
│ configuration_id(FK)│
│ action              │
│ user_id             │
│ timestamp           │
│ ...                 │
└─────────────────────┘

┌─────────────────────┐
│ configuration_      │
│ backups             │
├─────────────────────┤
│ id (PK)             │
│ backup_name         │
│ configuration_data  │
│ created_at          │
│ ...                 │
└─────────────────────┘

┌─────────────────────┐
│ configuration_      │
│ validation_rules    │
├─────────────────────┤
│ id (PK)             │
│ rule_name           │
│ rule_definition     │
│ applies_to_*        │
│ ...                 │
└─────────────────────┘

┌─────────────────────┐
│ configuration_      │
│ templates           │
├─────────────────────┤
│ id (PK)             │
│ template_name       │
│ configuration_data  │
│ ...                 │
└─────────────────────┘
```

## Tables

### 1. configurations

**Purpose**: Main configuration storage with hierarchical support

**Columns**:

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| key | VARCHAR(255) | Configuration key (indexed) |
| value | TEXT | Configuration value (can be JSON) |
| value_type | VARCHAR(50) | Data type: string, number, boolean, json, array |
| description | TEXT | Human-readable description |
| category | VARCHAR(100) | Category: system, user, module, feature |
| namespace | VARCHAR(100) | Namespace for isolation (default: 'global') |
| parent_id | INTEGER | Foreign key to parent configuration |
| version | INTEGER | Current version number |
| is_active | BOOLEAN | Whether configuration is active |
| validation_schema | JSON | JSON schema for validation |
| is_required | BOOLEAN | Whether configuration is required |
| default_value | TEXT | Default value if not set |
| is_system | BOOLEAN | System configs cannot be deleted |
| is_encrypted | BOOLEAN | Whether value is encrypted |
| is_sensitive | BOOLEAN | Hide in UI |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |
| created_by | VARCHAR(100) | Creator username |
| updated_by | VARCHAR(100) | Last updater username |

**Indexes**:
- `idx_config_key`: On `key`
- `idx_config_category`: On `category`
- `idx_config_namespace`: On `namespace`
- `idx_config_key_namespace`: Composite on `key, namespace`
- `idx_config_category_active`: Composite on `category, is_active`
- `idx_config_namespace_active`: Composite on `namespace, is_active`

**Example**:
```sql
INSERT INTO configurations (key, value, value_type, category, namespace, description)
VALUES ('max_upload_size', '10485760', 'number', 'system', 'global', 'Maximum file upload size in bytes');
```

### 2. configuration_versions

**Purpose**: Track all historical versions of configuration changes

**Columns**:

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| configuration_id | INTEGER | Foreign key to configurations |
| version_number | INTEGER | Version number |
| value | TEXT | Value at this version |
| value_type | VARCHAR(50) | Data type |
| change_type | VARCHAR(50) | created, updated, deleted, restored |
| change_description | TEXT | Description of change |
| previous_value | TEXT | Previous value before change |
| created_at | TIMESTAMP | Version creation time |
| created_by | VARCHAR(100) | Who made the change |

**Indexes**:
- `idx_version_config_id`: On `configuration_id`
- `idx_version_config_version`: Composite on `configuration_id, version_number`
- `idx_version_created_at`: On `created_at`

**Example**:
```sql
INSERT INTO configuration_versions (configuration_id, version_number, value, value_type, change_type, previous_value)
VALUES (1, 2, '20971520', 'number', 'updated', '10485760');
```

### 3. configuration_audit_logs

**Purpose**: Complete audit trail of all configuration access and modifications

**Columns**:

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| configuration_id | INTEGER | Foreign key to configurations (nullable) |
| action | VARCHAR(50) | read, create, update, delete, export, import |
| action_details | JSON | Additional context |
| user_id | INTEGER | User ID who performed action |
| username | VARCHAR(100) | Username |
| ip_address | VARCHAR(45) | IP address (IPv6 support) |
| user_agent | VARCHAR(255) | Browser/client user agent |
| old_value | TEXT | Value before change |
| new_value | TEXT | Value after change |
| status | VARCHAR(50) | success, failed, partial |
| error_message | TEXT | Error details if failed |
| timestamp | TIMESTAMP | When action occurred |

**Indexes**:
- `idx_audit_config_id`: On `configuration_id`
- `idx_audit_action`: On `action`
- `idx_audit_user_id`: On `user_id`
- `idx_audit_timestamp`: On `timestamp`
- `idx_audit_action_timestamp`: Composite on `action, timestamp`
- `idx_audit_user_timestamp`: Composite on `user_id, timestamp`
- `idx_audit_config_timestamp`: Composite on `configuration_id, timestamp`

**Example**:
```sql
INSERT INTO configuration_audit_logs (configuration_id, action, user_id, username, ip_address, old_value, new_value, status)
VALUES (1, 'update', 5, 'admin', '192.168.1.100', '10485760', '20971520', 'success');
```

### 4. configuration_backups

**Purpose**: Store complete configuration snapshots for disaster recovery

**Columns**:

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| backup_name | VARCHAR(255) | Backup name |
| backup_type | VARCHAR(50) | manual, automatic, scheduled |
| description | TEXT | Backup description |
| configuration_data | JSON | Complete configuration snapshot |
| configuration_count | INTEGER | Number of configurations in backup |
| is_compressed | BOOLEAN | Whether data is compressed |
| is_encrypted | BOOLEAN | Whether data is encrypted |
| compression_algorithm | VARCHAR(50) | gzip, bzip2, lzma |
| file_path | VARCHAR(500) | Path to backup file |
| file_size_bytes | INTEGER | Backup file size |
| checksum | VARCHAR(64) | SHA-256 checksum |
| status | VARCHAR(50) | pending, in_progress, completed, failed |
| error_message | TEXT | Error details if failed |
| retention_days | INTEGER | How long to keep backup |
| expires_at | TIMESTAMP | When backup expires |
| created_at | TIMESTAMP | Backup creation time |
| created_by | VARCHAR(100) | Who created backup |
| restored_at | TIMESTAMP | When backup was restored |
| restored_by | VARCHAR(100) | Who restored backup |
| restore_count | INTEGER | Number of times restored |

**Indexes**:
- `idx_backup_created_at`: On `created_at`
- `idx_backup_type_created`: Composite on `backup_type, created_at`
- `idx_backup_status`: On `status`
- `idx_backup_expires`: On `expires_at`

**Example**:
```sql
INSERT INTO configuration_backups (backup_name, backup_type, configuration_data, configuration_count, status)
VALUES ('daily_backup_2024_01_15', 'automatic', '{"configs": [...]}', 150, 'completed');
```

### 5. configuration_validation_rules

**Purpose**: Define validation schemas and rules for configuration values

**Columns**:

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| rule_name | VARCHAR(255) | Unique rule name |
| rule_type | VARCHAR(50) | schema, regex, range, enum, custom |
| description | TEXT | Rule description |
| rule_definition | JSON | Rule parameters/schema |
| error_message | TEXT | Custom error message |
| applies_to_namespace | VARCHAR(100) | Target namespace |
| applies_to_category | VARCHAR(100) | Target category |
| applies_to_key_pattern | VARCHAR(255) | Regex pattern for keys |
| is_active | BOOLEAN | Whether rule is active |
| severity | VARCHAR(50) | error, warning, info |
| created_at | TIMESTAMP | Rule creation time |
| updated_at | TIMESTAMP | Last update time |
| created_by | VARCHAR(100) | Creator username |

**Indexes**:
- `idx_validation_rule_name`: On `rule_name`
- `idx_validation_namespace`: On `applies_to_namespace`
- `idx_validation_active`: On `is_active`

**Example**:
```sql
INSERT INTO configuration_validation_rules (rule_name, rule_type, rule_definition, applies_to_namespace, severity)
VALUES ('positive_number', 'range', '{"min": 0, "type": "number"}', 'global', 'error');
```

### 6. configuration_templates

**Purpose**: Store reusable configuration templates for quick setup

**Columns**:

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| template_name | VARCHAR(255) | Unique template name |
| template_type | VARCHAR(50) | system, module, feature, custom |
| description | TEXT | Template description |
| configuration_data | JSON | Template configuration values |
| category | VARCHAR(100) | Template category |
| tags | JSON | Array of tags for searching |
| usage_count | INTEGER | Number of times used |
| last_used_at | TIMESTAMP | Last usage time |
| is_active | BOOLEAN | Whether template is active |
| is_system | BOOLEAN | System templates cannot be deleted |
| created_at | TIMESTAMP | Template creation time |
| updated_at | TIMESTAMP | Last update time |
| created_by | VARCHAR(100) | Creator username |

**Indexes**:
- `idx_template_name`: On `template_name`
- `idx_template_type_active`: Composite on `template_type, is_active`
- `idx_template_category`: On `category`

**Example**:
```sql
INSERT INTO configuration_templates (template_name, template_type, configuration_data, category)
VALUES ('solar_calculator_defaults', 'module', '{"efficiency": 0.85, "degradation": 0.005}', 'solar');
```

## Features

### 1. Configuration Versioning

Every configuration change creates a new version entry:

```python
# When updating a configuration
config.value = "new_value"
config.version += 1

# Create version record
version = ConfigurationVersion(
    configuration_id=config.id,
    version_number=config.version,
    value=config.value,
    change_type="updated",
    previous_value=old_value
)
```

### 2. Configuration Inheritance

Child configurations inherit from parent:

```python
# Parent configuration
parent = Configuration(
    key="theme.colors",
    value='{"primary": "#007bff"}',
    namespace="global"
)

# Child configuration (overrides parent)
child = Configuration(
    key="theme.colors.primary",
    value="#ff0000",
    parent_id=parent.id,
    namespace="solar"
)
```

### 3. Validation Schema

JSON Schema validation for configuration values:

```python
validation_schema = {
    "type": "number",
    "minimum": 0,
    "maximum": 100,
    "multipleOf": 0.01
}

config = Configuration(
    key="efficiency_percentage",
    value="85.5",
    value_type="number",
    validation_schema=validation_schema
)
```

### 4. Backup and Restore

Create backups with filtering:

```python
# Create backup
backup = ConfigurationBackup(
    backup_name="pre_migration_backup",
    backup_type="manual",
    configuration_data={
        "configs": [config.to_dict() for config in configs],
        "metadata": {"total": len(configs)}
    },
    configuration_count=len(configs)
)

# Restore from backup
restore_configurations(backup.configuration_data)
```

### 5. Audit Logging

All actions are logged:

```python
audit_log = ConfigurationAuditLog(
    configuration_id=config.id,
    action="update",
    user_id=current_user.id,
    username=current_user.username,
    ip_address=request.client.host,
    old_value=old_value,
    new_value=new_value,
    status="success"
)
```

## Usage Examples

### Example 1: Create Configuration with Validation

```python
from backend.models.configuration_models import Configuration
from backend.models.configuration_schemas import ConfigurationCreate

# Define configuration
config_data = ConfigurationCreate(
    key="solar.max_system_size",
    value="100",
    value_type="number",
    description="Maximum solar system size in kWp",
    category="module",
    namespace="solar",
    validation_schema={
        "type": "number",
        "minimum": 1,
        "maximum": 1000
    },
    is_required=True,
    default_value="50"
)

# Create in database
config = Configuration(**config_data.dict())
db.add(config)
db.commit()
```

### Example 2: Query Configurations by Namespace

```python
# Get all solar configurations
solar_configs = db.query(Configuration).filter(
    Configuration.namespace == "solar",
    Configuration.is_active == True
).all()

# Get configuration with children
config_with_children = db.query(Configuration).filter(
    Configuration.key == "theme.colors"
).first()

children = config_with_children.children
```

### Example 3: Create Backup

```python
from backend.models.configuration_models import ConfigurationBackup
import json

# Get all active configurations
configs = db.query(Configuration).filter(
    Configuration.is_active == True
).all()

# Create backup
backup = ConfigurationBackup(
    backup_name=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
    backup_type="automatic",
    configuration_data={
        "configs": [
            {
                "key": c.key,
                "value": c.value,
                "namespace": c.namespace,
                "category": c.category
            }
            for c in configs
        ]
    },
    configuration_count=len(configs),
    status="completed"
)

db.add(backup)
db.commit()
```

### Example 4: Apply Template

```python
from backend.models.configuration_models import ConfigurationTemplate

# Get template
template = db.query(ConfigurationTemplate).filter(
    ConfigurationTemplate.template_name == "solar_calculator_defaults"
).first()

# Apply template to namespace
for key, value in template.configuration_data.items():
    config = Configuration(
        key=key,
        value=str(value),
        namespace="solar_project_123",
        category="module",
        created_by="system"
    )
    db.add(config)

# Update usage tracking
template.usage_count += 1
template.last_used_at = datetime.now()
db.commit()
```

## Best Practices

### 1. Naming Conventions

- Use dot notation for hierarchical keys: `module.feature.setting`
- Use lowercase with underscores: `max_upload_size`
- Be descriptive: `solar_panel_efficiency` not `eff`

### 2. Namespacing

- Use namespaces to isolate configurations
- Global namespace for system-wide settings
- Module namespaces for feature-specific settings
- Project/user namespaces for instance-specific settings

### 3. Versioning

- Always increment version on updates
- Store meaningful change descriptions
- Keep version history for audit compliance

### 4. Validation

- Define validation schemas for all configurations
- Use appropriate value types
- Set reasonable defaults

### 5. Backup Strategy

- Schedule automatic daily backups
- Create manual backups before major changes
- Set retention policies (e.g., keep 30 days)
- Test restore procedures regularly

### 6. Security

- Mark sensitive configurations with `is_sensitive=True`
- Encrypt sensitive values with `is_encrypted=True`
- Audit all configuration access
- Restrict system configuration modifications

### 7. Performance

- Use indexes for frequent queries
- Cache frequently accessed configurations
- Use bulk operations for multiple updates
- Archive old audit logs periodically

## Migration Guide

### Running the Migration

```bash
# Using Alembic
cd solar-calculator-pro/backend
alembic upgrade head

# Or run migration script directly
python migrations/add_configuration_tables.py
```

### Rollback

```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific version
alembic downgrade <revision_id>
```

### Verification

```python
# Verify tables exist
from sqlalchemy import inspect
from backend.core.database import engine

inspector = inspect(engine)
tables = inspector.get_table_names()

required_tables = [
    'configurations',
    'configuration_versions',
    'configuration_audit_logs',
    'configuration_backups',
    'configuration_validation_rules',
    'configuration_templates'
]

for table in required_tables:
    assert table in tables, f"Table {table} not found!"

print("✅ All configuration tables exist!")
```

## Troubleshooting

### Issue: Foreign Key Constraint Errors

**Solution**: Ensure parent configurations exist before creating children

```python
# Check if parent exists
parent = db.query(Configuration).filter(Configuration.id == parent_id).first()
if not parent:
    raise ValueError(f"Parent configuration {parent_id} not found")
```

### Issue: JSON Validation Errors

**Solution**: Validate JSON before storing

```python
import json

try:
    json.loads(config.value)
except json.JSONDecodeError:
    raise ValueError("Invalid JSON value")
```

### Issue: Backup File Too Large

**Solution**: Enable compression

```python
import gzip
import json

data = json.dumps(configuration_data)
compressed = gzip.compress(data.encode())

backup.is_compressed = True
backup.compression_algorithm = "gzip"
backup.configuration_data = compressed
```

## API Integration

The configuration database schema integrates with the Configuration Service API:

- `GET /api/v1/configuration` - List configurations
- `POST /api/v1/configuration` - Create configuration
- `PUT /api/v1/configuration/{id}` - Update configuration
- `DELETE /api/v1/configuration/{id}` - Delete configuration
- `GET /api/v1/configuration/versions/{id}` - Get version history
- `POST /api/v1/configuration/backup` - Create backup
- `POST /api/v1/configuration/restore` - Restore from backup

See the Configuration Service documentation for complete API details.

## Summary

The Configuration Database Schema provides:

✅ **Hierarchical configuration** with parent-child relationships  
✅ **Complete version history** for all changes  
✅ **Comprehensive audit trail** for compliance  
✅ **Backup and restore** capabilities  
✅ **Validation rules** with JSON Schema support  
✅ **Reusable templates** for quick setup  
✅ **Namespace isolation** for multi-tenant support  
✅ **Security features** including encryption  
✅ **Performance optimized** with strategic indexes  
✅ **Production-ready** with proper constraints and relationships  

This schema forms the foundation for a robust, enterprise-grade configuration management system.
