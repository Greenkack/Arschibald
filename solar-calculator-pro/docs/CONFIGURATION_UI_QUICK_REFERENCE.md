# Configuration UI Quick Reference

## Quick Actions

| Action | Steps |
|--------|-------|
| **Create Configuration** | Click "New" → Fill form → Click "Create" |
| **Edit Configuration** | Click pencil icon → Modify → Click "Update" |
| **Delete Configuration** | Click trash icon → Confirm |
| **Search** | Type in search box → Results filter automatically |
| **Compare** | Select 2+ configs → Click "Compare" |
| **Export** | Click "Import/Export" → Export tab → Select options → Click "Export" |
| **Import** | Click "Import/Export" → Import tab → Upload/paste data → Click "Import" |
| **Apply Template** | Click "Templates" → Select template → Click "Apply" |

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl/Cmd + N` | New configuration |
| `Ctrl/Cmd + S` | Save configuration |
| `Ctrl/Cmd + F` | Focus search |
| `Esc` | Close dialog |
| `Enter` | Submit form |

## Configuration Fields

### Required Fields
- **Key**: Unique identifier (alphanumeric, dots, underscores, hyphens)
- **Namespace**: Organizational grouping
- **Category**: Configuration type

### Optional Fields
- **Value**: Configuration value
- **Description**: Human-readable explanation
- **Value Type**: string, number, boolean, json, array
- **Default Value**: Fallback value
- **Validation Schema**: JSON Schema for validation
- **Parent ID**: For configuration inheritance

### Flags
- **Required**: Configuration must have a value
- **Encrypted**: Value is encrypted in database
- **Sensitive**: Hide value in UI
- **System**: Cannot be deleted (admin only)

## Value Types

| Type | Example | Use Case |
|------|---------|----------|
| `string` | `"Hello"` | Text values |
| `number` | `42` | Numeric values |
| `boolean` | `true` | On/off flags |
| `json` | `{"key": "value"}` | Complex objects |
| `array` | `["a", "b"]` | Lists |

## Namespaces

| Namespace | Purpose |
|-----------|---------|
| `global` | Application-wide settings |
| `solar` | Solar calculator |
| `heatpump` | Heat pump calculator |
| `pdf` | PDF generation |
| `crm` | CRM system |
| `pricing` | Pricing engine |
| `visualization` | 3D visualization |

## Categories

| Category | Description |
|----------|-------------|
| `system` | Core system configs (protected) |
| `user` | User-customizable settings |
| `module` | Module-specific settings |
| `feature` | Feature flags |

## Export Formats

| Format | Extension | Use Case |
|--------|-----------|----------|
| JSON | `.json` | Most common, preserves structure |
| YAML | `.yaml` | Human-readable, version control |
| CSV | `.csv` | Spreadsheet import, simple data |

## Import Merge Modes

| Mode | Behavior |
|------|----------|
| `merge` | Keep existing values, add new |
| `replace` | Overwrite existing values |
| `skip` | Ignore duplicates, add new only |

## Common Validation Schemas

### String with length constraint:
```json
{"type": "string", "minLength": 1, "maxLength": 100}
```

### Number with range:
```json
{"type": "number", "minimum": 0, "maximum": 100}
```

### Enum (specific values):
```json
{"type": "string", "enum": ["value1", "value2"]}
```

### Email format:
```json
{"type": "string", "format": "email"}
```

### URL format:
```json
{"type": "string", "format": "uri"}
```

## Status Indicators

| Icon/Color | Meaning |
|------------|---------|
| 🟢 Green "Active" | Configuration is active |
| 🔴 Red "Inactive" | Configuration is disabled |
| 🔴 Red "System" | System configuration (protected) |
| ⚠️ Orange triangle | Values differ (in comparison) |
| 🔒 Lock icon | Encrypted value |
| 👁️ Eye slash | Sensitive (hidden) |

## Tips & Tricks

### Bulk Operations
1. Use checkboxes to select multiple configurations
2. Compare up to 10 configurations at once
3. Export filtered results only

### Search Tips
- Search searches key, value, and description
- Use filters to narrow results
- Combine search with filters for precision

### Template Usage
- Preview templates before applying
- Use dry run for imports to preview changes
- Templates can be applied to any namespace

### Version Control
- All changes are automatically versioned
- View version history via history icon
- Rollback to any previous version

### Performance
- Use pagination for large datasets
- Filter by namespace for faster searches
- Cache is automatically managed

## Error Messages

| Error | Solution |
|-------|----------|
| "Key already exists" | Use different key or edit existing |
| "Validation failed" | Check value matches schema |
| "Cannot delete system config" | Use force flag (admin only) |
| "Invalid JSON" | Validate JSON syntax |
| "Import failed" | Check format and data structure |

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/configurations/search` | GET | Search configurations |
| `/api/v1/configurations` | POST | Create configuration |
| `/api/v1/configurations/{id}` | GET | Get configuration |
| `/api/v1/configurations/{id}` | PUT | Update configuration |
| `/api/v1/configurations/{id}` | DELETE | Delete configuration |
| `/api/v1/configurations/export` | POST | Export configurations |
| `/api/v1/configurations/import` | POST | Import configurations |
| `/api/v1/configuration-templates` | GET | List templates |

## Support Resources

- **Full Guide**: [Configuration UI Guide](./CONFIGURATION_UI_GUIDE.md)
- **API Docs**: `/api/v1/docs`
- **Service Guide**: [Configuration Service Guide](./CONFIGURATION_SERVICE_GUIDE.md)
- **Database Schema**: [Configuration Database Schema](./CONFIGURATION_DATABASE_SCHEMA.md)

## Version

- **Component Version**: 1.0.0
- **Last Updated**: 2024
- **Compatibility**: Solar Calculator Pro v1.0+
