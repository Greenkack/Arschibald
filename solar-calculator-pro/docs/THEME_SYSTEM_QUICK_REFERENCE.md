# Theme System - Quick Reference Guide

## Overview

The Theme System provides comprehensive theming capabilities for Solar Calculator Pro, including multiple presets, custom theme creation, dark/light modes, and import/export functionality.

## Quick Start

### 1. Initialize Theme

```typescript
import { initializeTheme } from './store/themeStore';

// In your App.tsx
useEffect(() => {
  initializeTheme();
}, []);
```

### 2. Use Theme Panel

```typescript
import { ThemePanel } from './components/theme';

function SettingsPage() {
  return <ThemePanel />;
}
```

### 3. Use Dark Mode Toggle

```typescript
import { DarkModeToggle } from './components/theme';

function Header() {
  return (
    <header>
      <DarkModeToggle />
    </header>
  );
}
```

## Available Presets

| Preset | Description | Best For |
|--------|-------------|----------|
| **default** | Light blue theme | General use |
| **dark** | Dark mode theme | Low-light environments |
| **ocean** | Blue/cyan theme | Professional look |
| **forest** | Green theme | Eco-friendly feel |
| **sunset** | Orange theme | Warm, energetic feel |
| **highContrast** | High contrast theme | Accessibility |

## Using the Theme Store

```typescript
import { useThemeStore } from './store/themeStore';

function MyComponent() {
  const {
    theme,           // Current theme settings
    setTheme,        // Set complete theme
    setPreset,       // Set preset by name
    updateColors,    // Update colors only
    updateTypography,// Update typography only
    setMode,         // Set light/dark/auto mode
    resetTheme,      // Reset to default
    exportTheme,     // Export as JSON string
    importTheme,     // Import from JSON string
  } = useThemeStore();

  // Example: Change to dark mode
  setMode('dark');

  // Example: Update primary color
  updateColors({ primary: '#FF5733' });

  // Example: Switch to ocean preset
  setPreset('ocean');
}
```

## Theme Settings Structure

```typescript
interface ThemeSettings {
  mode: 'light' | 'dark' | 'auto';
  preset: string;
  colors: {
    primary: string;
    secondary: string;
    accent: string;
    background: string;
    surface: string;
    text: string;
    error: string;
    warning: string;
    success: string;
    info: string;
  };
  typography: {
    fontFamily: string;
    fontSize: 'small' | 'medium' | 'large' | 'xlarge';
    fontWeight: 'light' | 'normal' | 'medium' | 'bold';
  };
}
```

## CSS Variables

The theme system automatically generates CSS variables that can be used anywhere:

```css
.my-component {
  color: var(--color-primary);
  background: var(--color-surface);
  font-family: var(--font-family);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight);
}
```

### Available CSS Variables

**Colors:**
- `--color-primary`
- `--color-secondary`
- `--color-accent`
- `--color-background`
- `--color-surface`
- `--color-text`
- `--color-error`
- `--color-warning`
- `--color-success`
- `--color-info`

**Typography:**
- `--font-family`
- `--font-size-base`
- `--font-weight`

**PrimeReact Variables:**
- `--primary-color`
- `--surface-ground`
- `--surface-card`
- `--text-color`
- `--text-color-secondary`
- `--surface-border`

## Creating Custom Themes

### Programmatically

```typescript
import { createCustomTheme } from './theme/themePresets';

const myTheme = createCustomTheme('default', {
  colors: {
    primary: '#FF5733',
    secondary: '#33FF57',
  },
  typography: {
    fontSize: 'large',
  },
});

useThemeStore.getState().setTheme(myTheme);
```

### Using UI

1. Open Theme Panel
2. Click "Create Custom" button
3. Customize colors, typography, and mode
4. Click "Apply"

## Import/Export Themes

### Export

```typescript
const themeJson = useThemeStore.getState().exportTheme();
console.log(themeJson);
// Save to file or share with others
```

### Import

```typescript
const themeJson = '{"mode":"light","preset":"custom",...}';
useThemeStore.getState().importTheme(themeJson);
```

### Using UI

1. Open Theme Panel
2. Go to "Import/Export" tab
3. Click "Export Theme" to download or copy
4. Click "Import Theme" to upload or paste

## Dark Mode

### Toggle Programmatically

```typescript
const { theme, setMode } = useThemeStore();

// Toggle between light and dark
const newMode = theme.mode === 'dark' ? 'light' : 'dark';
setMode(newMode);
```

### Auto Mode

```typescript
// Follow system preference
setMode('auto');
```

## High Contrast Mode

```typescript
// Switch to high contrast preset
useThemeStore.getState().setPreset('highContrast');
```

## Best Practices

### 1. Use CSS Variables

```css
/* Good */
.button {
  background: var(--color-primary);
}

/* Avoid */
.button {
  background: #3B82F6;
}
```

### 2. Respect User Preferences

```typescript
// Check if user prefers dark mode
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
if (prefersDark) {
  setMode('dark');
}
```

### 3. Provide Theme Options

```typescript
// Always provide theme customization in settings
<SettingsPage>
  <ThemePanel />
</SettingsPage>
```

### 4. Test All Themes

```typescript
// Test your components with different themes
const themes = ['default', 'dark', 'ocean', 'forest', 'sunset', 'highContrast'];
themes.forEach(preset => {
  setPreset(preset);
  // Test component rendering
});
```

## Troubleshooting

### Theme Not Applying

```typescript
// Ensure theme is initialized
import { initializeTheme } from './store/themeStore';
initializeTheme();
```

### Colors Not Updating

```typescript
// Check if CSS variables are being used
// Verify in browser DevTools that CSS variables are set
console.log(getComputedStyle(document.documentElement).getPropertyValue('--color-primary'));
```

### Import Fails

```typescript
// Validate JSON format
try {
  JSON.parse(themeJson);
} catch (error) {
  console.error('Invalid theme JSON:', error);
}
```

## Performance Tips

1. **Use CSS Variables**: Faster than inline styles
2. **Minimize Theme Changes**: Avoid frequent theme switching
3. **Lazy Load Theme Panel**: Only load when needed
4. **Cache Theme**: Automatic with Zustand persist

## Accessibility

### High Contrast Mode

```typescript
// Automatically provides:
// - Higher color contrast
// - Larger font sizes
// - Bold font weights
setPreset('highContrast');
```

### Keyboard Navigation

All theme components support full keyboard navigation:
- Tab to navigate
- Enter/Space to activate
- Escape to close dialogs

### Screen Reader Support

All components include proper ARIA labels and roles.

## API Reference

### useThemeStore

```typescript
const {
  theme,                    // ThemeSettings
  isCustomThemeCreatorOpen, // boolean
  setTheme,                 // (theme: ThemeSettings) => void
  setPreset,                // (presetName: string) => void
  updateColors,             // (colors: Partial<ThemeColors>) => void
  updateTypography,         // (typography: Partial<ThemeTypography>) => void
  setMode,                  // (mode: 'light' | 'dark' | 'auto') => void
  resetTheme,               // () => void
  exportTheme,              // () => string
  importTheme,              // (themeJson: string) => void
  openCustomThemeCreator,   // () => void
  closeCustomThemeCreator,  // () => void
} = useThemeStore();
```

### themeEngine

```typescript
import { themeEngine } from './theme/themeEngine';

// Apply theme
themeEngine.applyTheme(theme);

// Get current theme
const currentTheme = themeEngine.getCurrentTheme();
```

## Examples

### Example 1: Custom Brand Theme

```typescript
const brandTheme = createCustomTheme('default', {
  colors: {
    primary: '#FF6B35',    // Brand orange
    secondary: '#004E89',  // Brand blue
    accent: '#F7B801',     // Brand yellow
  },
  typography: {
    fontFamily: 'Montserrat, sans-serif',
  },
});

useThemeStore.getState().setTheme(brandTheme);
```

### Example 2: Time-Based Theme

```typescript
function applyTimeBasedTheme() {
  const hour = new Date().getHours();
  const isDaytime = hour >= 6 && hour < 18;
  
  useThemeStore.getState().setMode(isDaytime ? 'light' : 'dark');
}

// Run on app start and every hour
applyTimeBasedTheme();
setInterval(applyTimeBasedTheme, 3600000);
```

### Example 3: User Preference Sync

```typescript
async function syncThemeWithBackend() {
  const theme = useThemeStore.getState().theme;
  
  // Save to backend
  await api.post('/api/v1/user/preferences', {
    theme: JSON.stringify(theme),
  });
}

// Load from backend
async function loadThemeFromBackend() {
  const response = await api.get('/api/v1/user/preferences');
  const theme = JSON.parse(response.data.theme);
  
  useThemeStore.getState().setTheme(theme);
}
```

## Support

For issues or questions:
1. Check this quick reference
2. Review the complete documentation
3. Check the component source code
4. Contact the development team

## Version

Theme System v1.0.0 - Task 171 Complete
