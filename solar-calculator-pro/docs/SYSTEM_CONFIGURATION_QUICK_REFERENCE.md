# System Configuration Management - Quick Reference

## Quick Actions

### Create Configuration
1. Click "New" button
2. Fill in key, value, type
3. Set category/module
4. Click "Save"

### Edit Configuration
1. Click edit icon (pencil)
2. Modify value
3. Add change reason (optional)
4. Click "Save"

### Delete Configuration
1. Click delete icon (trash)
2. Confirm deletion

### Apply Template
1. Go to Templates tab
2. Click "Apply" on desired template
3. Confirm action

### Export Configuration
1. Click "Export" button
2. Save JSON file

### Import Configuration
1. Click "Import" button
2. Select JSON file
3. Review results

## Configuration Types

| Type | Example | Description |
|------|---------|-------------|
| string | "Hello World" | Text value |
| number | 42 | Numeric value |
| boolean | true/false | Boolean value |
| json | {"key": "value"} | JSON object |

## Categories

- **general**: Application-wide settings
- **security**: Security and authentication
- **database**: Database configuration
- **email**: Email and SMTP settings
- **backup**: Backup configuration
- **logging**: Logging settings
- **performance**: Performance optimization
- **ui**: User interface settings
- **api**: API configuration

## Modules

- **solar**: Solar calculator settings
- **heatpump**: Heat pump calculator settings
- **pdf**: PDF generation settings
- **crm**: CRM system settings
- **pricing**: Pricing and currency settings

## Key Naming Convention

Use dot notation for hierarchical keys:
```
module.feature.setting
```

Examples:
- `app.name`
- `security.session_timeout`
- `database.backup_enabled`
- `solar.default_module_efficiency`

## Common Tasks

### Change Application Language
```
Key: app.language
Value: de-DE (or en-US, fr-FR, etc.)
Type: string
Category: general
```

### Enable/Disable Caching
```
Key: performance.cache_enabled
Value: true or false
Type: boolean
Category: performance
```

### Set Session Timeout
```
Key: security.session_timeout
Value: 3600 (seconds)
Type: number
Category: security
```

### Configure Module Setting
```
Module: solar
Key: default_module_efficiency
Value: 0.20
Type: number
```

## Validation Rules

### Regex Pattern
```json
{
  "regex": "^[a-zA-Z0-9_-]+$"
}
```

### Number Range
```json
{
  "min": 0,
  "max": 100
}
```

### Enum Values
```json
{
  "enum": ["option1", "option2", "option3"]
}
```

## API Quick Reference

### Get Configuration
```bash
GET /api/v1/system-config/system/key/{key}
```

### Update Configuration
```bash
PUT /api/v1/system-config/system/{id}
Content-Type: application/json

{
  "value": "new_value"
}
```

### Search Configurations
```bash
POST /api/v1/system-config/search
Content-Type: application/json

{
  "query": "search_term",
  "category": "general"
}
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+N | New configuration |
| Ctrl+E | Export configuration |
| Ctrl+I | Import configuration |
| Ctrl+F | Search/Filter |
| Ctrl+S | Save (in dialog) |
| Esc | Close dialog |

## Status Indicators

| Icon | Meaning |
|------|---------|
| 🔒 | Sensitive data |
| 🚫 | Read-only |
| ✅ | Enabled |
| ❌ | Disabled |
| ⚠️ | System template |

## Tips

1. **Always backup** before making major changes
2. **Test in development** before applying to production
3. **Use templates** for environment-specific configurations
4. **Document changes** with meaningful change reasons
5. **Review version history** before rolling back
6. **Validate values** before saving
7. **Mark sensitive data** appropriately
8. **Use read-only** for critical settings

## Common Issues

### Can't Edit Configuration
- Check if it's marked as read-only
- Verify you have admin permissions

### Import Failed
- Verify JSON format is correct
- Check for duplicate keys
- Ensure value types match

### Template Won't Apply
- Verify template is active
- Check for conflicting configurations

### Value Not Saving
- Verify value matches type
- Check validation rules
- Review error message

## Support

- API Documentation: `/docs`
- Full Guide: `SYSTEM_CONFIGURATION_GUIDE.md`
- Admin Panel: Settings → System Configuration
