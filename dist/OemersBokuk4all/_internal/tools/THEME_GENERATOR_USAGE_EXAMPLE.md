# Theme Generator - Usage Examples

## Example 1: Quick Theme Generation

Generate a blue theme in one command:

```bash
python tools/theme_generator.py --base-color "#3b82f6" --name "ocean-blue"
```

**Output:**
```
╔══════════════════════════════════════════════════════════════╗
║                    THEME PREVIEW                             ║
╠══════════════════════════════════════════════════════════════╣
║ Name: Ocean Blue                                           ║
║ Mode: Light                                                ║
╠══════════════════════════════════════════════════════════════╣
║                    COLOR PALETTE                             ║
╠══════════════════════════════════════════════════════════════╣
║ Primary:     #3b82f6                                       ║
║ Secondary:   #3adff6                                       ║
║ Accent:      #f6af3a                                       ║
...
╚══════════════════════════════════════════════════════════════╝

✅ Theme exported to: theming/themes/ocean-blue.json
```

## Example 2: Interactive Mode

For a guided experience:

```bash
python tools/theme_generator.py --interactive
```

**Interactive Session:**
```
============================================================
  SHADCN/UI THEME GENERATOR - Interactive Mode
============================================================

Enter base color (hex format, e.g., #3b82f6):
> #8b5cf6

Enter theme name (e.g., my-custom-theme):
> purple-dream

Is this a dark theme? (y/n):
> n

------------------------------------------------------------
Generating theme...
------------------------------------------------------------

[Preview displayed]

Export theme to JSON? (y/n):
> y

✅ Theme exported to: theming/themes/purple-dream.json
```

## Example 3: Dark Theme Variant

Create a dark mode version:

```bash
python tools/theme_generator.py --base-color "#8b5cf6" --name "midnight-purple" --dark
```

**Result:**
- Background: #0a0a0a (near-black)
- Foreground: #fafafa (off-white)
- All other colors optimized for dark backgrounds

## Example 4: Preview Before Exporting

Test colors without creating files:

```bash
python tools/theme_generator.py --base-color "#10b981" --name "forest-green" --preview-only
```

This shows the preview but doesn't create the JSON file.

## Example 5: Batch Generation

Generate multiple themes at once:

```bash
python tools/theme_generator.py --batch
```

**Generates:**
- shadcn-blue (light)
- shadcn-blue-dark
- shadcn-purple (light)
- shadcn-purple-dark
- shadcn-green (light)
- shadcn-amber (light)
- shadcn-red (light)
- shadcn-cyan (light)

## Example 6: Custom Output Directory

Save themes to a different location:

```bash
python tools/theme_generator.py --base-color "#ef4444" --name "crimson" --output "custom_themes"
```

## Example 7: Programmatic Usage in Python

```python
from tools.theme_generator import ThemeGenerator, ColorGenerator

# Generate a single theme
generator = ThemeGenerator("#3b82f6", "my-blue-theme", is_dark=False)

# Get the theme data
theme = generator.generate_theme()
print(theme['colors']['primary'])  # #3b82f6

# Export to JSON
filepath = generator.export_to_json()
print(f"Saved to: {filepath}")

# Show preview
preview = generator.preview_theme()
print(preview)
```

## Example 8: Color Manipulation

```python
from tools.theme_generator import ColorGenerator

base = "#3b82f6"

# Lighten and darken
lighter = ColorGenerator.lighten(base, 20)
darker = ColorGenerator.darken(base, 20)

# Get complementary color
complement = ColorGenerator.get_complementary(base)

# Get triadic colors
triadic1, triadic2 = ColorGenerator.get_triadic(base)

# Get analogous colors
analogous1, analogous2 = ColorGenerator.get_analogous(base)

print(f"Base: {base}")
print(f"Lighter: {lighter}")
print(f"Darker: {darker}")
print(f"Complementary: {complement}")
print(f"Triadic: {triadic1}, {triadic2}")
print(f"Analogous: {analogous1}, {analogous2}")
```

## Example 9: Generate Theme Variations

Create multiple variations of the same base color:

```python
from tools.theme_generator import ThemeGenerator

base_color = "#3b82f6"

# Light version
light = ThemeGenerator(base_color, "blue-light", is_dark=False)
light.export_to_json()

# Dark version
dark = ThemeGenerator(base_color, "blue-dark", is_dark=True)
dark.export_to_json()

print("✅ Generated light and dark variants")
```

## Example 10: Custom Color Palette

```python
from tools.theme_generator import ThemeGenerator, ColorGenerator

# Start with a base
generator = ThemeGenerator("#3b82f6", "custom-blue", False)

# Generate palette
palette = generator.generate_color_palette()

# Customize specific colors
palette.accent = ColorGenerator.rotate_hue(palette.primary, 90)
palette.secondary = ColorGenerator.lighten(palette.primary, 30)

# Use the custom palette
theme = generator.generate_theme()
print(f"Custom accent: {palette.accent}")
```

## Example 11: Brand Color Theme

Create a theme matching your brand:

```bash
# Your brand color
python tools/theme_generator.py --base-color "#FF6B35" --name "brand-orange"

# Dark variant for your brand
python tools/theme_generator.py --base-color "#FF6B35" --name "brand-orange-dark" --dark
```

## Example 12: Seasonal Themes

```bash
# Spring theme
python tools/theme_generator.py --base-color "#10b981" --name "spring-green"

# Summer theme
python tools/theme_generator.py --base-color "#06b6d4" --name "summer-cyan"

# Autumn theme
python tools/theme_generator.py --base-color "#f59e0b" --name "autumn-amber"

# Winter theme
python tools/theme_generator.py --base-color "#3b82f6" --name "winter-blue" --dark
```

## Example 13: Industry-Specific Themes

```bash
# Finance (professional blue)
python tools/theme_generator.py --base-color "#1e40af" --name "finance-blue"

# Healthcare (calming green)
python tools/theme_generator.py --base-color "#059669" --name "healthcare-green"

# Energy (vibrant yellow)
python tools/theme_generator.py --base-color "#eab308" --name "energy-yellow"

# Technology (modern purple)
python tools/theme_generator.py --base-color "#7c3aed" --name "tech-purple"
```

## Example 14: Testing Multiple Colors

```python
from tools.theme_generator import ThemeGenerator

# Test different base colors
test_colors = [
    ("#3b82f6", "blue"),
    ("#8b5cf6", "purple"),
    ("#10b981", "green"),
    ("#f59e0b", "amber"),
    ("#ef4444", "red"),
]

for color, name in test_colors:
    generator = ThemeGenerator(color, f"test-{name}", False)
    preview = generator.preview_theme()
    print(preview)
    print("\n" + "="*70 + "\n")
```

## Example 15: Integration with Theme Manager

```python
from tools.theme_generator import ThemeGenerator
from theming.theme_manager import ThemeManager

# Generate a new theme
generator = ThemeGenerator("#3b82f6", "new-blue", False)
filepath = generator.export_to_json()

# Load it in the theme manager
theme_manager = ThemeManager()
theme_manager.load_themes()  # Reload to include new theme
theme_manager.set_theme("new-blue")

print(f"✅ Generated and loaded theme: new-blue")
```

## Tips for Best Results

1. **Choose Saturated Colors**: Colors with 40-60% saturation work best
2. **Test Both Modes**: Generate both light and dark variants
3. **Preview First**: Always use `--preview-only` to check colors
4. **Brand Consistency**: Use your brand's primary color as base
5. **Accessibility**: Ensure good contrast (tool handles this automatically)

## Common Use Cases

### Use Case 1: Rebranding
```bash
# Old brand color: #1e40af
# New brand color: #3b82f6
python tools/theme_generator.py --base-color "#3b82f6" --name "new-brand"
python tools/theme_generator.py --base-color "#3b82f6" --name "new-brand-dark" --dark
```

### Use Case 2: A/B Testing
```bash
# Variant A (Blue)
python tools/theme_generator.py --base-color "#3b82f6" --name "variant-a"

# Variant B (Purple)
python tools/theme_generator.py --base-color "#8b5cf6" --name "variant-b"
```

### Use Case 3: Client Customization
```bash
# Generate theme for each client
python tools/theme_generator.py --base-color "#CLIENT_COLOR" --name "client-name"
```

## Troubleshooting

### Problem: Colors look washed out
**Solution**: Increase saturation of base color

```python
from tools.theme_generator import ColorGenerator
saturated = ColorGenerator.saturate("#3b82f6", 20)
# Use saturated color as base
```

### Problem: Poor contrast
**Solution**: The tool automatically calculates contrasting foreground colors, but you can adjust the base color's lightness

```python
# Make base color darker for better contrast
darker = ColorGenerator.darken("#3b82f6", 10)
```

### Problem: Theme not appearing in app
**Solution**: Ensure the JSON file is in `theming/themes/` and reload the theme manager

```python
theme_manager.load_themes()  # Reload themes
```
