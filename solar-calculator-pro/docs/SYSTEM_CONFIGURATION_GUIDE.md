# System Configuration Management Guide

## Overview

The System Configuration Management feature provides a comprehensive interface for managing all application settings, both global system-wide configurations and module-specific settings.

## Features

### 1. Global System Configuration
- Manage application-wide settings
- Categorized configuration (General, Security, Database, Email, etc.)
- Support for different value types (String, Number, Boolean, JSON)
- Sensitive data protection
- Read-only configuration protection
- Version history tracking

### 2. Module-Specific Configuration
- Configure individual modules (Solar, Heat Pump, PDF, CRM, Pricing)
- Enable/disable module features
- Validation rules for configuration values
- Default value management

### 3. Configuration Templates
- Predefined configuration sets
- Quick application of configuration profiles
- System templates (Development, Production, etc.)
- Custom template creation

### 4. Import/Export
- Export all configurations to JSON
- Import configurations from file
- Backup and restore capabilities
- Configuration migration between environments

### 5. Version Control
- Track all configuration changes
- View version history
- Rollback to previous versions
- Change reason tracking

### 6. Validation
- Type validation (string, number, boolean, JSON)
- Custom validation rules (regex, range, enum)
- Error messages for invalid values

## Configuration Categories

### General
- Application name and version
- Default language and timezone
- Regional settings

### Security
- Session timeout
- Maximum login attempts
- Password policies
- Authentication settings

### Database
- Backup settings
- Connection pooling
- Query optimization

### Email
- SMTP configuration
- Email templates
- Notification settings

### Backup
- Automatic backup schedule
- Backup retention policy
- Backup location

### Logging
- Log level (DEBUG, INFO, WARNING, ERROR)
- Log rotation
- Log storage

### Performance
- Caching settings
- Query optimization
- Resource limits

### UI
- Default theme
- Language preferences
- Display settings

### API
- Rate limiting
- API versioning
- Endpoint configuration

## Usage

### Creating a Configuration

1. Navigate to Admin Panel → System Configuration
2. Select the appropriate tab (System or Module)
3. Click "New" button
4. Fill in the configuration details:
   - Key: Unique identifier
   - Value: Configuration value
   - Type: Value type (string, number, boolean, json)
   - Category/Module: Classification
   - Description: Optional description
5. Set additional options (sensitive, readonly, enabled)
6. Click "Save"

### Editing a Configuration

1. Find the configuration in the table
2. Click the edit icon (pencil)
3. Modify the value or other fields
4. Optionally provide a change reason
5. Click "Save"

### Deleting a Configuration

1. Find the configuration in the table
2. Click the delete icon (trash)
3. Confirm the deletion
4. Note: Read-only configurations cannot be deleted

### Applying a Template

1. Go to the "Templates" tab
2. Find the desired template
3. Click "Apply"
4. Confirm the action
5. Review the results (applied, failed, skipped)

### Exporting Configuration

1. Click the "Export" button in the toolbar
2. Choose whether to include sensitive data
3. Save the JSON file to your computer

### Importing Configuration

1. Click the "Import" button in the toolbar
2. Select a JSON configuration file
3. Choose whether to overwrite existing configurations
4. Review the import results

### Viewing Version History

1. Select a system configuration
2. Click "View History"
3. See all previous versions with timestamps
4. Optionally rollback to a previous version

## API Endpoints

### System Configuration

```
POST   /api/v1/system-config/system              Create system configuration
GET    /api/v1/system-config/system              List system configurations
GET    /api/v1/system-config/system/{id}         Get system configuration
GET    /api/v1/system-config/system/key/{key}    Get by key
PUT    /api/v1/system-config/system/{id}         Update system configuration
DELETE /api/v1/system-config/system/{id}         Delete system configuration
```

### Module Configuration

```
POST   /api/v1/system-config/module              Create module configuration
GET    /api/v1/system-config/module              List module configurations
GET    /api/v1/system-config/module/{id}         Get module configuration
PUT    /api/v1/system-config/module/{id}         Update module configuration
DELETE /api/v1/system-config/module/{id}         Delete module configuration
```

### Templates

```
POST   /api/v1/system-config/template            Create template
GET    /api/v1/system-config/template            List templates
GET    /api/v1/system-config/template/{id}       Get template
POST   /api/v1/system-config/template/{id}/apply Apply template
```

### Import/Export

```
GET    /api/v1/system-config/export              Export configuration
POST   /api/v1/system-config/import              Import configuration
```

### Search

```
POST   /api/v1/system-config/search              Search configurations
```

### Version Control

```
GET    /api/v1/system-config/system/{id}/versions           Get version history
POST   /api/v1/system-config/system/{id}/rollback/{version} Rollback to version
```

## Default Configurations

### System Configurations

| Key | Value | Type | Category | Description |
|-----|-------|------|----------|-------------|
| app.name | Solar Calculator Pro | string | general | Application name |
| app.version | 1.0.0 | string | general | Application version |
| app.language | de-DE | string | general | Default language |
| app.timezone | Europe/Berlin | string | general | Default timezone |
| security.session_timeout | 3600 | number | security | Session timeout (seconds) |
| security.max_login_attempts | 5 | number | security | Max login attempts |
| database.backup_enabled | true | boolean | database | Enable auto backup |
| database.backup_interval | 86400 | number | database | Backup interval (seconds) |
| email.smtp_enabled | false | boolean | email | Enable SMTP |
| logging.level | INFO | string | logging | Log level |
| performance.cache_enabled | true | boolean | performance | Enable caching |
| ui.theme | light | string | ui | Default theme |

### Module Configurations

| Module | Key | Value | Type | Description |
|--------|-----|-------|------|-------------|
| solar | default_module_efficiency | 0.20 | number | Default module efficiency |
| solar | default_system_loss | 0.14 | number | Default system loss |
| heatpump | default_cop | 4.0 | number | Default COP |
| pdf | default_template | standard | string | Default PDF template |
| pdf | compression_enabled | true | boolean | Enable PDF compression |
| crm | lead_scoring_enabled | true | boolean | Enable lead scoring |
| pricing | currency | EUR | string | Default currency |
| pricing | tax_rate | 0.19 | number | Default tax rate (VAT) |

## Best Practices

1. **Use Descriptive Keys**: Use dot notation for hierarchical keys (e.g., `module.feature.setting`)
2. **Document Changes**: Always provide a change reason when updating configurations
3. **Test Before Production**: Test configuration changes in development environment first
4. **Backup Regularly**: Export configurations before making major changes
5. **Use Templates**: Create templates for different environments (dev, staging, production)
6. **Validate Values**: Ensure values match the expected type and format
7. **Protect Sensitive Data**: Mark sensitive configurations appropriately
8. **Version Control**: Review version history before rolling back
9. **Module Organization**: Group related settings under the same module
10. **Read-Only Protection**: Use read-only flag for critical system settings

## Troubleshooting

### Configuration Not Saving
- Check if configuration is marked as read-only
- Verify value matches the specified type
- Check validation rules
- Review error messages in the UI

### Import Failing
- Verify JSON file format
- Check for duplicate keys
- Ensure value types are correct
- Review import results for specific errors

### Template Not Applying
- Verify template is active
- Check for conflicting configurations
- Review apply results for failures
- Ensure proper permissions

### Version Rollback Issues
- Verify version exists
- Check if configuration is read-only
- Ensure proper permissions
- Review version history

## Security Considerations

1. **Sensitive Data**: Mark passwords, API keys, and secrets as sensitive
2. **Access Control**: Restrict configuration management to admin users only
3. **Audit Trail**: All changes are logged with user and timestamp
4. **Read-Only Protection**: Critical system settings should be read-only
5. **Export Security**: Be cautious when exporting configurations with sensitive data
6. **Validation**: Always validate configuration values before applying
7. **Backup**: Keep secure backups of configuration data

## Integration

### Accessing Configuration in Code

**Backend (Python):**
```python
from backend.services.system_config_service import SystemConfigService

# Get configuration value
service = SystemConfigService(db)
config = service.get_system_config_by_key('app.language')
language = config.value

# Get module configuration
configs = service.get_module_configs(module_name='solar')
```

**Frontend (TypeScript):**
```typescript
import api from './services/api';

// Get configuration
const response = await api.get('/api/v1/system-config/system/key/app.language');
const language = response.data.value;

// Get module configurations
const moduleConfigs = await api.get('/api/v1/system-config/module?module_name=solar');
```

## Support

For additional help or questions about System Configuration Management:
- Check the API documentation at `/docs`
- Review the inline help in the UI
- Contact system administrator
- Refer to the developer guide
