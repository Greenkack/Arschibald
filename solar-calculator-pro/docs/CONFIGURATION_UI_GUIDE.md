# Configuration UI Guide

## Overview

The Configuration UI provides a comprehensive interface for managing application configurations. It includes features for creating, editing, searching, comparing, and importing/exporting configurations.

## Features

### 1. Configuration Management Interface

The main configuration manager provides:

- **Search and Filtering**: Search configurations by key, value, or description
- **Namespace Filtering**: Filter by namespace (global, solar, heatpump, pdf, crm, pricing)
- **Category Filtering**: Filter by category (system, user, module, feature)
- **Status Filtering**: Filter by active/inactive status
- **Bulk Operations**: Select multiple configurations for comparison or bulk actions

### 2. Configuration Editor

Create and edit configurations with:

- **Basic Information Tab**:
  - Key (unique identifier)
  - Namespace (organizational grouping)
  - Category (configuration type)
  - Description (human-readable explanation)

- **Value Configuration Tab**:
  - Value Type (string, number, boolean, json, array)
  - Value (the actual configuration value)
  - Default Value (fallback value)
  - Validation Schema (JSON Schema for validation)
  - Real-time validation

- **Advanced Options Tab**:
  - Required flag
  - Encryption flag
  - Sensitive flag (hide in UI)
  - Parent configuration (for inheritance)

### 3. Configuration Comparison

Compare multiple configurations side-by-side:

- Visual highlighting of differences
- Similarity percentage calculation
- Export comparison results
- Field-by-field comparison

### 4. Configuration Templates

Pre-defined configuration sets:

- Browse available templates
- Preview template contents
- Apply templates to namespaces
- Merge or replace existing configurations

### 5. Import/Export

Import and export configurations in multiple formats:

**Export Features**:
- Format options: JSON, YAML, CSV
- Filter by namespace and category
- Include version history
- Include audit logs

**Import Features**:
- Format options: JSON, YAML, CSV
- Merge modes: merge, replace, skip
- Validation before import
- Dry run mode (preview changes)
- File upload or paste data
- Import results summary

## Usage Examples

### Creating a New Configuration

1. Click "New" button in the toolbar
2. Fill in the basic information:
   - Key: `app.feature.solar_calculator.enabled`
   - Namespace: `solar`
   - Category: `feature`
   - Description: `Enable/disable solar calculator feature`
3. Configure the value:
   - Value Type: `boolean`
   - Value: `true`
4. Set advanced options if needed
5. Click "Create"

### Comparing Configurations

1. Select 2 or more configurations using checkboxes
2. Click "Compare" button in the toolbar
3. Review the side-by-side comparison
4. Export comparison if needed

### Applying a Template

1. Click "Templates" button in the toolbar
2. Browse available templates
3. Click "Preview" to see template contents
4. Click "Apply" and select target namespace
5. Choose merge mode (replace or merge)
6. Confirm application

### Exporting Configurations

1. Click "Import/Export" button in the toolbar
2. Go to "Export" tab
3. Select export format (JSON, YAML, or CSV)
4. Optionally filter by namespace and category
5. Choose whether to include versions and audit logs
6. Click "Export Configurations"
7. File will be downloaded automatically

### Importing Configurations

1. Click "Import/Export" button in the toolbar
2. Go to "Import" tab
3. Select import format
4. Choose merge mode
5. Either upload a file or paste data directly
6. Enable "Dry run" to preview changes
7. Click "Import Configurations"
8. Review import results

## Configuration Value Types

### String
Simple text values:
```
"Hello World"
```

### Number
Numeric values:
```
42
3.14
```

### Boolean
True/false values:
```
true
false
```

### JSON
Complex objects:
```json
{
  "key1": "value1",
  "key2": 123,
  "nested": {
    "key3": true
  }
}
```

### Array
Lists of values:
```json
["item1", "item2", "item3"]
```

## Validation Schema

Use JSON Schema to validate configuration values:

### String with minimum length:
```json
{
  "type": "string",
  "minLength": 1,
  "maxLength": 100
}
```

### Number with range:
```json
{
  "type": "number",
  "minimum": 0,
  "maximum": 100
}
```

### Enum (specific values):
```json
{
  "type": "string",
  "enum": ["option1", "option2", "option3"]
}
```

### Object with required properties:
```json
{
  "type": "object",
  "properties": {
    "name": {"type": "string"},
    "age": {"type": "number"}
  },
  "required": ["name"]
}
```

## Best Practices

### Naming Conventions

Use dot notation for hierarchical keys:
```
app.module.feature.setting
```

Examples:
- `solar.calculator.default_module_count`
- `pdf.generation.default_template`
- `crm.email.smtp_server`

### Namespaces

Organize configurations by functional area:
- `global`: Application-wide settings
- `solar`: Solar calculator specific
- `heatpump`: Heat pump calculator specific
- `pdf`: PDF generation settings
- `crm`: CRM system settings
- `pricing`: Pricing engine settings

### Categories

Use appropriate categories:
- `system`: Core system configurations (cannot be deleted)
- `user`: User-customizable settings
- `module`: Module-specific settings
- `feature`: Feature flags and toggles

### Security

- Mark sensitive configurations with `is_sensitive` flag
- Enable encryption for passwords and API keys
- Use validation schemas to prevent invalid values
- Regularly backup configurations

### Version Control

- Configuration changes are automatically versioned
- View version history for any configuration
- Rollback to previous versions if needed
- Track who made changes and when

## API Integration

The Configuration UI integrates with the following backend endpoints:

- `GET /api/v1/configurations/search` - Search configurations
- `POST /api/v1/configurations` - Create configuration
- `GET /api/v1/configurations/{id}` - Get configuration
- `PUT /api/v1/configurations/{id}` - Update configuration
- `DELETE /api/v1/configurations/{id}` - Delete configuration
- `GET /api/v1/configurations/{id}/versions` - Get version history
- `POST /api/v1/configurations/{id}/rollback` - Rollback to version
- `POST /api/v1/configurations/export` - Export configurations
- `POST /api/v1/configurations/import` - Import configurations
- `GET /api/v1/configuration-templates` - List templates
- `POST /api/v1/configuration-templates/apply` - Apply template

## Troubleshooting

### Import Fails

- Check format matches selected format (JSON, YAML, CSV)
- Validate JSON/YAML syntax
- Ensure required fields are present (key, namespace)
- Check for duplicate keys in same namespace

### Validation Errors

- Review validation schema syntax
- Ensure value matches schema requirements
- Check value type matches declared type

### Cannot Delete Configuration

- System configurations cannot be deleted
- Use force flag for system configurations (admin only)
- Deactivate instead of deleting

### Template Application Fails

- Check target namespace exists
- Verify merge mode is appropriate
- Review template contents for errors
- Check for conflicting configurations

## Support

For additional help:
- Review API documentation: `/api/v1/docs`
- Check backend logs for errors
- Contact system administrator
- Refer to Configuration Service Guide

## Related Documentation

- [Configuration Service Guide](./CONFIGURATION_SERVICE_GUIDE.md)
- [Configuration Database Schema](./CONFIGURATION_DATABASE_SCHEMA.md)
- [API Documentation](./API_DOCUMENTATION.md)
- [Developer Guide](./DEVELOPER_GUIDE.md)
