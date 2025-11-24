# Internationalization (i18n) Quick Reference

## Overview

The Solar Calculator Pro application includes comprehensive internationalization support with:
- **9 supported languages** (German, English, French, Spanish, Italian, Polish, Dutch, Arabic, Hebrew)
- **RTL (Right-to-Left) support** for Arabic and Hebrew
- **Locale-specific formatting** for numbers, currencies, dates
- **Translation management** interface for admins
- **Dynamic language switching** without page reload

## Quick Start

### Using Translations in Components

```typescript
import { useTranslation } from 'react-i18next';

function MyComponent() {
  const { t } = useTranslation();
  
  return (
    <div>
      <h1>{t('common.welcome')}</h1>
      <p>{t('solar.roof_area')}</p>
    </div>
  );
}
```

### Using Locale Formatting

```typescript
import { useLocaleFormatter } from '../utils/localeFormatter';

function PriceDisplay({ price }: { price: number }) {
  const formatter = useLocaleFormatter();
  
  return (
    <div>
      <span>{formatter.formatCurrency(price)}</span>
      {/* German: 16.999,00 € */}
      {/* English: €16,999.00 */}
    </div>
  );
}
```

### Language Switcher

```typescript
import { LanguageSwitcher } from '../components/i18n/LanguageSwitcher';

function Header() {
  return (
    <header>
      <LanguageSwitcher variant="dropdown" showFlag={true} />
    </header>
  );
}
```

## Supported Languages

| Code | Language | Native Name | RTL | Flag |
|------|----------|-------------|-----|------|
| de   | German   | Deutsch     | No  | 🇩🇪   |
| en   | English  | English     | No  | 🇬🇧   |
| fr   | French   | Français    | No  | 🇫🇷   |
| es   | Spanish  | Español     | No  | 🇪🇸   |
| it   | Italian  | Italiano    | No  | 🇮🇹   |
| pl   | Polish   | Polski      | No  | 🇵🇱   |
| nl   | Dutch    | Nederlands  | No  | 🇳🇱   |
| ar   | Arabic   | العربية     | Yes | 🇸🇦   |
| he   | Hebrew   | עברית       | Yes | 🇮🇱   |

## Translation Keys Structure

```
common.{key}          - Common UI elements (save, cancel, etc.)
navigation.{key}      - Navigation menu items
solar.{key}           - Solar calculator specific
heatpump.{key}        - Heat pump calculator specific
pricing.{key}         - Pricing related
pdf.{key}             - PDF generation
crm.{key}             - CRM features
products.{key}        - Product management
admin.{key}           - Administration
errors.{key}          - Error messages
validation.{key}      - Form validation messages
units.{key}           - Units (kWh, m², etc.)
dates.{key}           - Date-related strings
messages.{key}        - Success/info messages
```

## Formatting Functions

### Numbers
```typescript
formatter.formatNumber(1234.56)
// German: 1.234,56
// English: 1,234.56
```

### Currency
```typescript
formatter.formatCurrency(16999, 'EUR')
// German: 16.999,00 €
// English: €16,999.00
```

### Percentage
```typescript
formatter.formatPercent(85.5)
// German: 85,5%
// English: 85.5%
```

### Dates
```typescript
formatter.formatDate(new Date())
// German: 24. November 2025
// English: November 24, 2025
```

### Energy Units
```typescript
formatter.formatEnergy(12500, 'kWh')
// 12.500 kWh (German)
// 12,500 kWh (English)
```

## RTL Support

### Checking RTL
```typescript
import { useRTL } from '../utils/rtlSupport';

function MyComponent() {
  const { isRTL, direction, textAlign } = useRTL();
  
  return (
    <div dir={direction} style={{ textAlign }}>
      Content
    </div>
  );
}
```

### RTL-Aware Styling
```typescript
const { getSpacingDirection } = useRTL();

// Automatically flips left/right based on language
const marginSide = getSpacingDirection('left'); // 'right' for RTL
```

## Translation Management

### Admin Interface
Access the translation management interface at `/admin/translations`

Features:
- View all translations
- Edit translations for all languages
- Add new translation keys
- Export translations (ZIP)
- Import translations (ZIP/JSON)
- View missing translations
- Auto-translate (with external API)

### API Endpoints

```
GET    /api/v1/i18n/translations          - Get all translations
GET    /api/v1/i18n/{lang}/{namespace}    - Get resource for i18next
POST   /api/v1/i18n/translations          - Create translation
PUT    /api/v1/i18n/translations          - Update translation
DELETE /api/v1/i18n/translations/{key}    - Delete translation
GET    /api/v1/i18n/export                - Export translations
POST   /api/v1/i18n/import                - Import translations
GET    /api/v1/i18n/languages             - Get supported languages
PUT    /api/v1/i18n/user/language         - Update user language
GET    /api/v1/i18n/missing               - Get missing translations
POST   /api/v1/i18n/auto-translate        - Auto-translate
GET    /api/v1/i18n/statistics            - Get statistics
```

## Adding New Languages

1. Add language to `supportedLanguages` in `i18nConfig.ts`
2. Create translation file: `locales/{code}.json`
3. Import in `i18nConfig.ts`
4. Add to backend `SUPPORTED_LANGUAGES` in `i18n_config.py`
5. Populate translations via admin interface

## Best Practices

1. **Always use translation keys** - Never hardcode text
2. **Use namespaces** - Organize translations logically
3. **Provide context** - Use descriptive key names
4. **Test RTL** - Always test with Arabic or Hebrew
5. **Use locale formatting** - Never format numbers/dates manually
6. **Keep keys consistent** - Follow naming conventions
7. **Document new keys** - Add comments for complex translations

## Common Patterns

### Pluralization
```typescript
t('items', { count: 5 })
// Uses plural rules for current language
```

### Interpolation
```typescript
t('welcome_user', { name: 'John' })
// "Welcome, John!"
```

### Nested Keys
```typescript
t('solar.roof_area')
// Accesses nested structure
```

### Default Values
```typescript
t('missing.key', 'Default text')
// Shows default if key missing
```

## Troubleshooting

### Translations not loading
- Check browser console for errors
- Verify backend API is running
- Check network tab for failed requests

### RTL layout issues
- Ensure `dir` attribute is set on root element
- Use logical properties (start/end) instead of left/right
- Test with browser RTL mode

### Formatting issues
- Verify locale is correctly set
- Check browser locale support
- Use `Intl` API for consistency

## Performance Tips

1. **Lazy load translations** - Load namespaces on demand
2. **Cache translations** - Use localStorage
3. **Minimize API calls** - Batch translation updates
4. **Use suspense** - Show loading state while loading
5. **Preload common** - Load common namespace early

## Resources

- [i18next Documentation](https://www.i18next.com/)
- [React i18next](https://react.i18next.com/)
- [Intl API](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl)
- [RTL Styling Guide](https://rtlstyling.com/)
