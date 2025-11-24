# Accessibility Quick Reference

## Quick Start

### Enable Accessibility Features

1. Go to **Settings** → **Accessibility**
2. Configure your preferences
3. Click **Save Preferences**

### Keyboard Shortcuts

Press `Shift + ?` to view all keyboard shortcuts

## Common Tasks

### Navigate with Keyboard

| Action | Shortcut |
|--------|----------|
| Next element | `Tab` |
| Previous element | `Shift + Tab` |
| Activate button/link | `Enter` or `Space` |
| Close dialog | `Escape` |
| Open search | `Ctrl + /` |
| Save | `Ctrl + S` |

### Use Screen Reader

1. Enable **Screen Reader Optimized** in settings
2. Navigate with `Tab` key
3. Listen for announcements on page changes
4. Form errors are announced automatically

### Adjust Visual Settings

- **High Contrast**: Settings → Accessibility → High Contrast Mode
- **Font Size**: Settings → Accessibility → Font Size slider (75%-200%)
- **Reduced Motion**: Settings → Accessibility → Reduced Motion

## Hooks Reference

### useKeyboardNavigation

```typescript
const { containerRef, focusFirst } = useKeyboardNavigation({
  shortcuts: [{ key: 's', ctrl: true, handler: save }],
  enableFocusTrap: true,
});
```

### useScreenReader

```typescript
const { announce, getFieldAriaProps } = useScreenReader();

announce('Action completed');
const props = getFieldAriaProps('Email', error, 'Enter email', true);
```

### useFocusManagement

```typescript
const { containerRef, focusFirst, isFocusVisible } = useFocusManagement({
  trapFocus: true,
  restoreFocus: true,
});
```

## Components

### AccessibilitySettings

```typescript
import { AccessibilitySettings } from '@/components/accessibility/AccessibilitySettings';

<AccessibilitySettings />
```

### KeyboardShortcutsHelp

```typescript
import { KeyboardShortcutsHelp } from '@/components/accessibility/KeyboardShortcutsHelp';

<KeyboardShortcutsHelp />
```

## Audit Tool

```typescript
import { accessibilityAuditor } from '@/utils/accessibilityAudit';

const result = accessibilityAuditor.audit();
console.log('Errors:', result.summary.errors);
```

## WCAG Compliance

- **Level**: AA
- **Version**: WCAG 2.1
- **Coverage**: All perceivable, operable, understandable, and robust criteria

## Support

- **Email**: accessibility@solarcalculatorpro.com
- **Docs**: `/docs/ACCESSIBILITY_FEATURES_GUIDE.md`
- **Issues**: GitHub with `accessibility` label
