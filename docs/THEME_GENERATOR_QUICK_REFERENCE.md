# Theme Generator - Quick Reference

## Quick Start

### Interactive Mode (Easiest)
```bash
python tools/theme_generator.py --interactive
```

### Generate Single Theme
```bash
python tools/theme_generator.py --base-color "#3b82f6" --name "my-theme"
```

### Generate Dark Theme
```bash
python tools/theme_generator.py --base-color "#8b5cf6" --name "purple-dark" --dark
```

### Batch Generate
```bash
python tools/theme_generator.py --batch
```

## Common Commands

| Command | Description |
|---------|-------------|
| `-i, --interactive` | Interactive mode with prompts |
| `-c, --base-color` | Base color (hex format) |
| `-n, --name` | Theme name (kebab-case) |
| `-d, --dark` | Generate dark theme |
| `-o, --output` | Output directory |
| `-p, --preview-only` | Preview without exporting |
| `-b, --batch` | Generate multiple themes |

## Programmatic Usage

```python
from tools.theme_generator import ThemeGenerator

# Create and export theme
generator = ThemeGenerator("#3b82f6", "my-theme", is_dark=False)
filepath = generator.export_to_json()
```

## Color Operations

```python
from tools.theme_generator import ColorGenerator

# Lighten/Darken
lighter = ColorGenerator.lighten("#3b82f6", 20)
darker = ColorGenerator.darken("#3b82f6", 20)

# Color harmonies
complementary = ColorGenerator.get_complementary("#3b82f6")
triadic1, triadic2 = ColorGenerator.get_triadic("#3b82f6")
analogous1, analogous2 = ColorGenerator.get_analogous("#3b82f6")
```

## Generated Theme Structure

```
{
  "name": "theme-name",
  "colors": {
    "primary": "base color",
    "secondary": "analogous color",
    "accent": "complementary color",
    "success/warning/error": "semantic colors",
    "chart_1-5": "chart colors"
  },
  "typography": { ... },
  "spacing": { ... },
  "shadows": { ... },
  "borders": { ... },
  "animations": { ... }
}
```

## Color Theory Cheat Sheet

- **Complementary**: Opposite on color wheel (180°)
- **Triadic**: Three colors evenly spaced (120°)
- **Analogous**: Adjacent colors (±30°)
- **Split-Complementary**: Base + two adjacent to complement

## Best Practices

✅ Use brand colors as base  
✅ Test with actual UI components  
✅ Use kebab-case for names  
✅ Generate both light and dark variants  
✅ Preview before exporting  

❌ Avoid overly saturated colors  
❌ Don't use spaces in theme names  
❌ Don't skip the preview step  

## Examples

### Blue Theme
```bash
python tools/theme_generator.py -c "#3b82f6" -n "ocean-blue"
```

### Purple Dark Theme
```bash
python tools/theme_generator.py -c "#8b5cf6" -n "midnight-purple" -d
```

### Green Theme (Preview Only)
```bash
python tools/theme_generator.py -c "#10b981" -n "forest-green" -p
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Colors clash | Try different base color |
| Poor contrast | Adjust base color lightness |
| Theme not loading | Check filename matches theme name |

## See Also

- [Complete Reference](../tools/THEME_GENERATOR_REFERENCE.md)
- [Theme System](../theming/THEME_SELECTOR_REFERENCE.md)
- [Demo Script](../demo_theme_generator.py)
