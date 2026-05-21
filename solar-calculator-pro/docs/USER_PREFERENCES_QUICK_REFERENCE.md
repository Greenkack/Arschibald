# User Preferences - Quick Reference

## Quick Start

### Frontend Hook
```typescript
import { usePreferences } from '../hooks/usePreferences';

const { getPreference, setPreference } = usePreferences();

// Get
const theme = getPreference('ui', 'theme', 'light');

// Set
await setPreference('ui', 'theme', 'dark');
```

### Backend Service
```python
from backend.services.preference_service import PreferenceService

service = PreferenceService(db)

# Get all
prefs = service.get_all_preferences(user_id)

# Update
service.update_preference(user_id, 'ui', 'theme', PreferenceUpdate(value='dark'))
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/preferences/` | Get all preferences |
| GET | `/api/v1/preferences/category/{category}` | Get by category |
| GET | `/api/v1/preferences/{category}/{key}` | Get specific |
| POST | `/api/v1/preferences/` | Create |
| PUT | `/api/v1/preferences/{category}/{key}` | Update |
| PUT | `/api/v1/preferences/bulk` | Bulk update |
| DELETE | `/api/v1/preferences/{category}/{key}` | Delete |
| POST | `/api/v1/preferences/reset` | Reset |
| GET | `/api/v1/preferences/export/all` | Export |
| POST | `/api/v1/preferences/import` | Import |
| POST | `/api/v1/preferences/sync` | Sync |

## Default Categories

### UI
- `theme`: "light" | "dark" | "auto"
- `language`: "de" | "en"
- `sidebar_collapsed`: boolean
- `items_per_page`: number
- `date_format`: string
- `time_format`: string

### Calculation
- `auto_save`: boolean
- `default_location`: string
- `precision`: number
- `show_advanced_options`: boolean

### PDF
- `default_template`: "standard" | "extended" | "minimal"
- `auto_download`: boolean
- `include_charts`: boolean
- `compression_level`: "none" | "low" | "medium" | "high"

### Notifications
- `enabled`: boolean
- `sound`: boolean
- `desktop`: boolean
- `email`: boolean

## Common Operations

### Get Preference
```typescript
const value = getPreference('category', 'key', defaultValue);
```

### Set Preference
```typescript
await setPreference('category', 'key', value);
```

### Bulk Update
```typescript
await bulkUpdate([
  { category: 'ui', key: 'theme', value: 'dark' },
  { category: 'ui', key: 'language', value: 'en' }
]);
```

### Reset
```typescript
await resetPreference('ui', 'theme');      // Single
await resetCategory('ui');                  // Category
await resetAll();                           // All
```

### Export/Import
```typescript
const json = await exportPreferences();
await importPreferences(json, overwrite);
```

### Sync
```typescript
await syncPreferences(deviceId, deviceName);
```

## Data Types

- `string`: Text values
- `number`: Numeric values
- `boolean`: True/false
- `object`: JSON objects
- `array`: JSON arrays

## Component Usage

```typescript
import { UserPreferences } from '../components/settings/UserPreferences';

<UserPreferences />
```

## Error Handling

```typescript
try {
  await setPreference('ui', 'theme', 'dark');
} catch (error) {
  console.error('Failed:', error);
}
```

## Best Practices

1. ✅ Use appropriate data types
2. ✅ Provide default values
3. ✅ Handle errors gracefully
4. ✅ Use bulk updates for multiple changes
5. ✅ Organize into logical categories
6. ✅ Cache frequently accessed preferences

## Files

### Backend
- `models/preference_models.py` - Database models
- `models/preference_schemas.py` - Pydantic schemas
- `services/preference_service.py` - Business logic
- `api/v1/preferences.py` - API endpoints
- `migrations/add_preference_tables.py` - Database migration

### Frontend
- `hooks/usePreferences.ts` - React hook
- `components/settings/UserPreferences.tsx` - UI component
- `components/settings/UserPreferences.css` - Styles

### Documentation
- `docs/USER_PREFERENCES_GUIDE.md` - Complete guide
- `docs/USER_PREFERENCES_QUICK_REFERENCE.md` - This file
