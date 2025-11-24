# User Preferences System - Complete Guide

## Overview

The User Preferences System provides a comprehensive solution for managing user-specific settings across the application. It supports persistence, synchronization across devices, import/export functionality, and easy reset to defaults.

## Features

### 1. Preference Management
- **Create**: Add new preferences
- **Read**: Retrieve preferences by category or key
- **Update**: Modify existing preferences
- **Delete**: Remove preferences (revert to defaults)

### 2. Persistence
- Automatic saving to database
- Cross-session persistence
- User-specific settings

### 3. Synchronization
- Sync preferences across multiple devices
- Conflict resolution
- Device tracking

### 4. Import/Export
- Export preferences to JSON file
- Import preferences from JSON file
- Overwrite or merge options

### 5. Reset Functionality
- Reset individual preferences
- Reset entire categories
- Reset all preferences to defaults

## Architecture

### Backend Components

#### Models
- **UserPreference**: Stores individual user preferences
- **PreferenceTemplate**: Reusable preference sets
- **PreferenceSync**: Tracks cross-device synchronization

#### Service Layer
- **PreferenceService**: Core business logic
  - CRUD operations
  - Bulk updates
  - Import/export
  - Synchronization
  - Template management

#### API Endpoints
```
GET    /api/v1/preferences/                    # Get all preferences
GET    /api/v1/preferences/category/{category} # Get by category
GET    /api/v1/preferences/{category}/{key}    # Get specific preference
POST   /api/v1/preferences/                    # Create preference
PUT    /api/v1/preferences/{category}/{key}    # Update preference
PUT    /api/v1/preferences/bulk                # Bulk update
DELETE /api/v1/preferences/{category}/{key}    # Delete preference
POST   /api/v1/preferences/reset               # Reset preferences
GET    /api/v1/preferences/export/all          # Export preferences
POST   /api/v1/preferences/import              # Import preferences
POST   /api/v1/preferences/sync                # Sync preferences
GET    /api/v1/preferences/statistics          # Get statistics
POST   /api/v1/preferences/search              # Search preferences
GET    /api/v1/preferences/templates           # Get templates
POST   /api/v1/preferences/templates           # Create template
POST   /api/v1/preferences/templates/{id}/apply # Apply template
```

### Frontend Components

#### Hook: usePreferences
```typescript
const {
  preferences,        // All preferences
  loading,           // Loading state
  error,             // Error state
  getPreference,     // Get single preference
  setPreference,     // Set single preference
  bulkUpdate,        // Update multiple preferences
  resetPreference,   // Reset single preference
  resetCategory,     // Reset category
  resetAll,          // Reset all preferences
  exportPreferences, // Export to JSON
  importPreferences, // Import from JSON
  syncPreferences,   // Sync across devices
  refresh,           // Reload preferences
} = usePreferences();
```

#### Component: UserPreferences
Full-featured UI for managing preferences with tabs for different categories.

## Default Preferences

### UI Category
```json
{
  "theme": "light",
  "language": "de",
  "sidebar_collapsed": false,
  "items_per_page": 25,
  "date_format": "DD.MM.YYYY",
  "time_format": "HH:mm"
}
```

### Calculation Category
```json
{
  "auto_save": true,
  "default_location": "Berlin",
  "precision": 2,
  "show_advanced_options": false
}
```

### PDF Category
```json
{
  "default_template": "standard",
  "auto_download": true,
  "include_charts": true,
  "compression_level": "medium"
}
```

### Notifications Category
```json
{
  "enabled": true,
  "sound": true,
  "desktop": true,
  "email": false
}
```

## Usage Examples

### Backend Usage

#### Get User Preferences
```python
from backend.services.preference_service import PreferenceService

service = PreferenceService(db)
preferences = service.get_all_preferences(user_id)

# Access specific preference
theme = preferences['ui']['theme']['value']
```

#### Update Preference
```python
from backend.models.preference_schemas import PreferenceUpdate

service.update_preference(
    user_id=1,
    category='ui',
    key='theme',
    update=PreferenceUpdate(value='dark')
)
```

#### Bulk Update
```python
updates = [
    {'category': 'ui', 'key': 'theme', 'value': 'dark'},
    {'category': 'ui', 'key': 'language', 'value': 'en'},
    {'category': 'calculation', 'key': 'precision', 'value': 3}
]

service.bulk_update_preferences(user_id=1, preferences=updates)
```

#### Export/Import
```python
# Export
export_data = service.export_preferences(user_id=1)

# Import
from backend.models.preference_schemas import PreferenceImport

import_data = PreferenceImport(
    version="1.0",
    preferences=export_data.preferences,
    overwrite_existing=True
)

service.import_preferences(user_id=1, import_data=import_data)
```

### Frontend Usage

#### Basic Usage
```typescript
import { usePreferences } from '../hooks/usePreferences';

function MyComponent() {
  const { getPreference, setPreference } = usePreferences();

  // Get preference
  const theme = getPreference('ui', 'theme', 'light');

  // Set preference
  const handleThemeChange = async (newTheme: string) => {
    await setPreference('ui', 'theme', newTheme);
  };

  return (
    <select value={theme} onChange={(e) => handleThemeChange(e.target.value)}>
      <option value="light">Light</option>
      <option value="dark">Dark</option>
    </select>
  );
}
```

#### Export Preferences
```typescript
const { exportPreferences } = usePreferences();

const handleExport = async () => {
  const data = await exportPreferences();
  const blob = new Blob([data], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = 'preferences.json';
  link.click();
};
```

#### Import Preferences
```typescript
const { importPreferences } = usePreferences();

const handleImport = async (file: File) => {
  const text = await file.text();
  await importPreferences(text, true); // true = overwrite existing
};
```

#### Reset Preferences
```typescript
const { resetCategory, resetAll } = usePreferences();

// Reset specific category
await resetCategory('ui');

// Reset all preferences
await resetAll();
```

## Data Types

Preferences support the following data types:
- **string**: Text values
- **number**: Numeric values (integer or float)
- **boolean**: True/false values
- **object**: JSON objects
- **array**: JSON arrays

## Synchronization

### How It Works
1. User makes changes on Device A
2. Changes are saved to database
3. User opens app on Device B
4. App syncs preferences from database
5. Device B now has same preferences as Device A

### Manual Sync
```typescript
const { syncPreferences } = usePreferences();

await syncPreferences(
  'device-unique-id',
  'My Laptop'
);
```

### Automatic Sync
Preferences are automatically synced when:
- User logs in
- App starts
- Preferences are modified

## Templates

### Create Template
```python
from backend.models.preference_schemas import PreferenceTemplateCreate

template = PreferenceTemplateCreate(
    name="Dark Mode Professional",
    description="Dark theme with professional settings",
    category="ui",
    preferences={
        "theme": {"value": "dark", "data_type": "string"},
        "sidebar_collapsed": {"value": false, "data_type": "boolean"},
        "items_per_page": {"value": 50, "data_type": "number"}
    }
)

service.create_template(template)
```

### Apply Template
```python
service.apply_template(user_id=1, template_id=1)
```

## Best Practices

### 1. Use Appropriate Data Types
```typescript
// Good
setPreference('calculation', 'precision', 2);

// Bad
setPreference('calculation', 'precision', "2");
```

### 2. Provide Default Values
```typescript
const theme = getPreference('ui', 'theme', 'light'); // 'light' is default
```

### 3. Handle Errors
```typescript
try {
  await setPreference('ui', 'theme', 'dark');
} catch (error) {
  console.error('Failed to update preference:', error);
  // Show user-friendly error message
}
```

### 4. Batch Updates
```typescript
// Good - single API call
await bulkUpdate([
  { category: 'ui', key: 'theme', value: 'dark' },
  { category: 'ui', key: 'language', value: 'en' }
]);

// Bad - multiple API calls
await setPreference('ui', 'theme', 'dark');
await setPreference('ui', 'language', 'en');
```

### 5. Use Categories
Organize preferences into logical categories:
- `ui`: User interface settings
- `calculation`: Calculation-related settings
- `pdf`: PDF generation settings
- `notifications`: Notification settings
- `security`: Security settings
- `privacy`: Privacy settings

## Troubleshooting

### Preferences Not Saving
1. Check user authentication
2. Verify database connection
3. Check browser console for errors
4. Verify API endpoint is accessible

### Sync Not Working
1. Check device ID is unique
2. Verify user is logged in
3. Check network connection
4. Verify sync endpoint is accessible

### Import Failing
1. Verify JSON format is correct
2. Check file size (max 1MB)
3. Verify all required fields are present
4. Check data types match

## Security Considerations

1. **Authentication Required**: All preference endpoints require authentication
2. **User Isolation**: Users can only access their own preferences
3. **Input Validation**: All inputs are validated before saving
4. **SQL Injection Prevention**: Using parameterized queries
5. **XSS Prevention**: Values are sanitized before display

## Performance Optimization

1. **Caching**: Preferences are cached in frontend state
2. **Lazy Loading**: Only load preferences when needed
3. **Bulk Operations**: Use bulk update for multiple changes
4. **Indexing**: Database indexes on user_id, category, and key

## Migration Guide

### From localStorage to Database
```typescript
// Old way
localStorage.setItem('theme', 'dark');
const theme = localStorage.getItem('theme');

// New way
await setPreference('ui', 'theme', 'dark');
const theme = getPreference('ui', 'theme');
```

### From Streamlit session_state
```python
# Old way
st.session_state.theme = 'dark'
theme = st.session_state.get('theme', 'light')

# New way
service.update_preference(user_id, 'ui', 'theme', PreferenceUpdate(value='dark'))
preferences = service.get_all_preferences(user_id)
theme = preferences['ui']['theme']['value']
```

## API Reference

See [API Documentation](./API_DOCUMENTATION.md) for complete API reference.

## Support

For issues or questions:
1. Check this documentation
2. Review API documentation
3. Check application logs
4. Contact support team
