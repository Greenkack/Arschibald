# Internationalization (i18n) Implementation Guide

## Architecture Overview

The i18n system consists of three main layers:

1. **Frontend Layer** - React components with i18next
2. **Backend Layer** - FastAPI with translation management
3. **Database Layer** - PostgreSQL/SQLite for translation storage

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                      │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐       │
│  │ i18next    │  │ Formatter  │  │ RTL Support│       │
│  │ Provider   │  │ Utils      │  │ Utils      │       │
│  └────────────┘  └────────────┘  └────────────┘       │
└─────────────────────────────────────────────────────────┘
                          │
                          │ HTTP/WebSocket
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   Backend (FastAPI)                      │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐       │
│  │ i18n API   │  │ i18n       │  │ Translation│       │
│  │ Endpoints  │  │ Service    │  │ Models     │       │
│  └────────────┘  └────────────┘  └────────────┘       │
└─────────────────────────────────────────────────────────┘
                          │
                          │ SQLAlchemy
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    Database                              │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐       │
│  │translations│  │user_lang   │  │translation │       │
│  │            │  │_preferences│  │_history    │       │
│  └────────────┘  └────────────┘  └────────────┘       │
└─────────────────────────────────────────────────────────┘
```

## Setup Instructions

### 1. Install Dependencies

```bash
# Frontend
cd frontend
npm install i18next react-i18next i18next-browser-languagedetector i18next-http-backend

# Backend
cd backend
pip install fastapi sqlalchemy pydantic
```

### 2. Initialize Database

```bash
cd backend
python migrations/add_i18n_tables.py
```

### 3. Configure i18next

The configuration is already set up in `frontend/src/i18n/i18nConfig.ts`. To customize:

```typescript
i18n.init({
  fallbackLng: 'de',  // Change default language
  debug: false,        // Enable for development
  // ... other options
});
```

### 4. Wrap App with i18n Provider

```typescript
// frontend/src/main.tsx
import './i18n/i18nConfig';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

## Component Integration

### Basic Usage

```typescript
import { useTranslation } from 'react-i18next';

export const MyComponent: React.FC = () => {
  const { t, i18n } = useTranslation();

  return (
    <div>
      <h1>{t('common.welcome')}</h1>
      <p>{t('solar.system_size')}: {t('units.kwp')}</p>
      <button onClick={() => i18n.changeLanguage('en')}>
        English
      </button>
    </div>
  );
};
```

### With Interpolation

```typescript
const { t } = useTranslation();

// Translation: "Welcome, {{name}}!"
<p>{t('welcome_message', { name: user.name })}</p>
```

### With Pluralization

```typescript
// Translation keys:
// "item": "item"
// "item_plural": "items"

<p>{t('item', { count: items.length })}</p>
```

### With HTML

```typescript
import { Trans } from 'react-i18next';

// Translation: "Click <strong>here</strong> to continue"
<Trans i18nKey="click_here">
  Click <strong>here</strong> to continue
</Trans>
```

## Locale Formatting

### Number Formatting

```typescript
import { useLocaleFormatter } from '../utils/localeFormatter';

const formatter = useLocaleFormatter();

// Basic number
formatter.formatNumber(1234.56);

// With custom decimals
formatter.formatNumber(1234.567, { maximumFractionDigits: 3 });

// Currency
formatter.formatCurrency(16999, 'EUR');

// Percentage
formatter.formatPercent(85.5, 1);
```

### Date Formatting

```typescript
// Full date
formatter.formatDate(new Date());

// Custom format
formatter.formatDate(new Date(), {
  year: 'numeric',
  month: 'short',
  day: 'numeric'
});

// Time
formatter.formatTime(new Date());

// Relative time
formatter.formatRelativeTime(new Date('2025-11-20'));
// Output: "4 days ago"
```

### Unit Formatting

```typescript
// Energy
formatter.formatEnergy(12500, 'kWh');

// Area
formatter.formatArea(50.5);

// Angle
formatter.formatAngle(30);

// Duration
formatter.formatDuration(25, 'years');
```

## RTL Support

### Component-Level RTL

```typescript
import { useRTL } from '../utils/rtlSupport';

export const MyComponent: React.FC = () => {
  const { isRTL, direction, textAlign, getStyles } = useRTL();

  return (
    <div style={getStyles()}>
      <p>This text aligns correctly for RTL</p>
    </div>
  );
};
```

### Conditional Styling

```typescript
const { isRTL, getSpacingDirection } = useRTL();

const styles = {
  [`margin${getSpacingDirection('left')}`]: '1rem',
  // Becomes marginRight for RTL, marginLeft for LTR
};
```

### CSS RTL Support

```css
/* Automatic RTL support */
[dir='rtl'] .my-component {
  text-align: right;
  direction: rtl;
}

[dir='ltr'] .my-component {
  text-align: left;
  direction: ltr;
}

/* Logical properties (preferred) */
.my-component {
  margin-inline-start: 1rem;  /* Auto-flips for RTL */
  padding-inline-end: 0.5rem;
}
```

## Translation Management

### Admin Interface

The translation management interface provides:

1. **View Translations** - Browse all translations by namespace
2. **Edit Translations** - Update translations for all languages
3. **Add New Keys** - Create new translation keys
4. **Export** - Download all translations as ZIP
5. **Import** - Upload translations from ZIP/JSON
6. **Statistics** - View completion percentage per language

### Programmatic Management

```typescript
// Add translation
await fetch('/api/v1/i18n/translations', {
  method: 'POST',
  body: JSON.stringify({
    key: 'new.key',
    namespace: 'common',
    translations: {
      de: 'Deutscher Text',
      en: 'English text',
    },
  }),
});

// Update translation
await fetch('/api/v1/i18n/translations', {
  method: 'PUT',
  body: JSON.stringify({
    key: 'existing.key',
    namespace: 'common',
    translations: {
      de: 'Aktualisierter Text',
      en: 'Updated text',
    },
  }),
});
```

## Backend Integration

### Using Translations in Backend

```python
from ..services.i18n_service import I18nService

def get_localized_message(db: Session, key: str, language: str) -> str:
    service = I18nService(db)
    resource = service.get_translation_resource(language, 'messages')
    return resource.get(key, key)
```

### Email Templates

```python
def send_email(user_id: int, template_key: str, db: Session):
    # Get user's language preference
    service = I18nService(db)
    language = service.get_user_language(user_id)
    
    # Get localized template
    template = service.get_translation_resource(language, 'emails')
    subject = template.get(f'{template_key}.subject')
    body = template.get(f'{template_key}.body')
    
    # Send email...
```

## Testing

### Unit Tests

```typescript
import { renderHook } from '@testing-library/react';
import { useTranslation } from 'react-i18next';

describe('i18n', () => {
  it('translates keys correctly', () => {
    const { result } = renderHook(() => useTranslation());
    expect(result.current.t('common.save')).toBe('Save');
  });

  it('handles missing keys', () => {
    const { result } = renderHook(() => useTranslation());
    expect(result.current.t('missing.key')).toBe('missing.key');
  });
});
```

### Integration Tests

```typescript
import { render, screen } from '@testing-library/react';
import { I18nextProvider } from 'react-i18next';
import i18n from './i18n/i18nConfig';

describe('MyComponent', () => {
  it('renders in German', () => {
    i18n.changeLanguage('de');
    render(
      <I18nextProvider i18n={i18n}>
        <MyComponent />
      </I18nextProvider>
    );
    expect(screen.getByText('Speichern')).toBeInTheDocument();
  });

  it('renders in English', () => {
    i18n.changeLanguage('en');
    render(
      <I18nextProvider i18n={i18n}>
        <MyComponent />
      </I18nextProvider>
    );
    expect(screen.getByText('Save')).toBeInTheDocument();
  });
});
```

## Performance Optimization

### 1. Lazy Loading Namespaces

```typescript
i18n.init({
  ns: ['common'],  // Load only common initially
  defaultNS: 'common',
});

// Load additional namespaces on demand
i18n.loadNamespaces(['solar', 'pricing']);
```

### 2. Caching

```typescript
// i18next automatically caches in localStorage
i18n.init({
  detection: {
    caches: ['localStorage'],
  },
});
```

### 3. Code Splitting

```typescript
// Lazy load translation files
const loadTranslations = async (language: string) => {
  const translations = await import(`./locales/${language}.json`);
  i18n.addResourceBundle(language, 'translation', translations);
};
```

## Migration from Streamlit

### 1. Extract Strings

```python
# Script to extract all hardcoded strings from Streamlit app
import re
import os

def extract_strings(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Find st.title, st.header, st.write, etc.
    patterns = [
        r'st\.title\(["\'](.+?)["\']\)',
        r'st\.header\(["\'](.+?)["\']\)',
        r'st\.write\(["\'](.+?)["\']\)',
    ]
    
    strings = []
    for pattern in patterns:
        matches = re.findall(pattern, content)
        strings.extend(matches)
    
    return strings
```

### 2. Create Translation Keys

```python
# Generate translation keys from extracted strings
def create_translation_key(text: str) -> str:
    # Convert "Solar Calculator" -> "solar_calculator"
    return text.lower().replace(' ', '_')
```

### 3. Populate Database

```python
# Import extracted strings into database
from backend.services.i18n_service import I18nService

def import_streamlit_strings(strings: list, db: Session):
    service = I18nService(db)
    
    for text in strings:
        key = create_translation_key(text)
        service.create_translation({
            'key': key,
            'namespace': 'common',
            'translations': {
                'de': text,  # Original German text
                'en': text,  # TODO: Translate
            },
        })
```

## Troubleshooting

### Issue: Translations not loading

**Solution:**
1. Check browser console for errors
2. Verify backend API is running
3. Check network tab for 404s
4. Ensure database has translations

### Issue: RTL layout broken

**Solution:**
1. Verify `dir` attribute on root element
2. Use logical CSS properties
3. Test with browser DevTools RTL mode
4. Check for hardcoded left/right values

### Issue: Number formatting incorrect

**Solution:**
1. Verify locale is set correctly
2. Check browser Intl support
3. Use `Intl.NumberFormat` directly
4. Test with different locales

### Issue: Missing translations

**Solution:**
1. Check translation key spelling
2. Verify namespace is loaded
3. Use fallback language
4. Check database for key

## Best Practices

1. **Consistent Naming** - Use dot notation: `namespace.category.key`
2. **Avoid Concatenation** - Use interpolation instead
3. **Context Matters** - Same word may need different translations
4. **Test RTL Early** - Don't wait until the end
5. **Use Namespaces** - Organize translations logically
6. **Document Keys** - Add comments for complex translations
7. **Version Control** - Track translation changes
8. **Professional Translation** - Use native speakers
9. **Cultural Sensitivity** - Consider cultural differences
10. **Accessibility** - Ensure screen reader compatibility

## Resources

- [i18next Documentation](https://www.i18next.com/)
- [React i18next](https://react.i18next.com/)
- [MDN Intl API](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl)
- [W3C i18n](https://www.w3.org/International/)
- [RTL Styling](https://rtlstyling.com/)
