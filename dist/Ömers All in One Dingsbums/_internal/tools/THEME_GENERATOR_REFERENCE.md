# Theme Generator Tool - Complete Reference

## Overview

The Theme Generator Tool automatically creates complete shadcn/ui themes from a single base color. It calculates complementary colors, accent colors, and generates all necessary design tokens for a fully functional theme.

## Features

- ✅ **Automatic Color Generation**: Generate complete color palettes from a single base color
- ✅ **Color Harmony Algorithms**: Complementary, triadic, analogous, and split-complementary colors
- ✅ **Light & Dark Mode Support**: Generate both light and dark theme variants
- ✅ **Chart Colors**: Automatically generate harmonious chart color palettes
- ✅ **JSON Export**: Export themes in the correct format for immediate use
- ✅ **Interactive Mode**: User-friendly CLI for theme creation
- ✅ **Batch Generation**: Generate multiple themes at once
- ✅ **Preview Mode**: See theme colors before exporting

## Installation

No additional dependencies required. The tool uses only Python standard library.

## Usage

### 1. Interactive Mode (Recommended for Beginners)

```bash
python tools/theme_generator.py --interactive
```

This will guide you through:
1. Entering a base color
2. Choosing a theme name
3. Selecting light or dark mode
4. Previewing the generated theme
5. Optionally exporting to JSON

### 2. Command-Line Mode

#### Generate a Light Theme

```bash
python tools/theme_generator.py --base-color "#3b82f6" --name "my-blue-theme"
```

#### Generate a Dark Theme

```bash
python tools/theme_generator.py --base-color "#8b5cf6" --name "my-purple-dark" --dark
```

#### Preview Only (No Export)

```bash
python tools/theme_generator.py --base-color "#10b981" --name "green" --preview-only
```

#### Custom Output Directory

```bash
python tools/theme_generator.py --base-color "#ef4444" --name "red" --output "custom_themes"
```

### 3. Batch Mode

Generate multiple predefined themes at once:

```bash
python tools/theme_generator.py --batch
```

This generates:
- shadcn-blue (light)
- shadcn-blue-dark
- shadcn-purple (light)
- shadcn-purple-dark
- shadcn-green (light)
- shadcn-amber (light)
- shadcn-red (light)
- shadcn-cyan (light)

### 4. Programmatic Usage

```python
from tools.theme_generator import ThemeGenerator

# Create generator
generator = ThemeGenerator(
    base_color="#3b82f6",
    theme_name="my-custom-theme",
    is_dark=False
)

# Generate theme data
theme = generator.generate_theme()

# Export to JSON
filepath = generator.export_to_json("theming/themes")

# Get preview
preview = generator.preview_theme()
print(preview)
```

## API Reference

### ColorGenerator Class

Provides color manipulation utilities.

#### Methods

##### `hex_to_rgb(hex_color: str) -> Tuple[int, int, int]`
Converts hex color to RGB tuple.

```python
rgb = ColorGenerator.hex_to_rgb("#3b82f6")
# Returns: (59, 130, 246)
```

##### `rgb_to_hex(rgb: Tuple[int, int, int]) -> str`
Converts RGB tuple to hex color.

```python
hex_color = ColorGenerator.rgb_to_hex((59, 130, 246))
# Returns: "#3b82f6"
```

##### `lighten(hex_color: str, amount: float) -> str`
Lightens a color by the specified amount (0-100).

```python
lighter = ColorGenerator.lighten("#3b82f6", 20)
# Returns: "#6ba3f8"
```

##### `darken(hex_color: str, amount: float) -> str`
Darkens a color by the specified amount (0-100).

```python
darker = ColorGenerator.darken("#3b82f6", 20)
# Returns: "#2563eb"
```

##### `saturate(hex_color: str, amount: float) -> str`
Increases color saturation (0-100).

```python
saturated = ColorGenerator.saturate("#3b82f6", 20)
```

##### `desaturate(hex_color: str, amount: float) -> str`
Decreases color saturation (0-100).

```python
desaturated = ColorGenerator.desaturate("#3b82f6", 20)
```

##### `rotate_hue(hex_color: str, degrees: float) -> str`
Rotates the hue by specified degrees (0-360).

```python
rotated = ColorGenerator.rotate_hue("#3b82f6", 90)
```

##### `get_complementary(hex_color: str) -> str`
Returns the complementary color (180° rotation).

```python
complementary = ColorGenerator.get_complementary("#3b82f6")
# Returns: "#f6a93b"
```

##### `get_triadic(hex_color: str) -> Tuple[str, str]`
Returns triadic colors (120° and 240° rotations).

```python
triadic1, triadic2 = ColorGenerator.get_triadic("#3b82f6")
# Returns: ("#3bf682", "#823bf6")
```

##### `get_analogous(hex_color: str) -> Tuple[str, str]`
Returns analogous colors (±30° rotations).

```python
analogous1, analogous2 = ColorGenerator.get_analogous("#3b82f6")
```

##### `get_split_complementary(hex_color: str) -> Tuple[str, str]`
Returns split-complementary colors (150° and 210° rotations).

```python
split1, split2 = ColorGenerator.get_split_complementary("#3b82f6")
```

### ThemeGenerator Class

Generates complete themes from a base color.

#### Constructor

```python
ThemeGenerator(base_color: str, theme_name: str, is_dark: bool = False)
```

**Parameters:**
- `base_color`: Hex color code (e.g., "#3b82f6")
- `theme_name`: Theme identifier (e.g., "my-custom-theme")
- `is_dark`: Whether to generate a dark theme variant

#### Methods

##### `generate_color_palette() -> ColorPalette`
Generates a complete color palette from the base color.

```python
palette = generator.generate_color_palette()
print(palette.primary)      # Base color
print(palette.secondary)    # Analogous color
print(palette.accent)       # Complementary color
print(palette.success)      # Green
print(palette.warning)      # Amber
print(palette.error)        # Red
print(palette.info)         # Base color
```

##### `generate_chart_colors(palette: ColorPalette) -> List[str]`
Generates harmonious chart colors.

```python
chart_colors = generator.generate_chart_colors(palette)
# Returns: List of 5 hex colors
```

##### `generate_theme() -> Dict`
Generates the complete theme dictionary.

```python
theme = generator.generate_theme()
# Returns: Complete theme with colors, typography, spacing, etc.
```

##### `export_to_json(output_dir: str = "theming/themes") -> str`
Exports the theme to a JSON file.

```python
filepath = generator.export_to_json()
# Returns: Path to exported file
```

##### `preview_theme() -> str`
Returns a formatted preview of the theme.

```python
preview = generator.preview_theme()
print(preview)
```

## Color Theory

### How Colors Are Generated

1. **Primary Color**: Your base color
2. **Secondary Color**: Analogous color (-30° hue rotation)
3. **Accent Color**: Complementary color (180° hue rotation)
4. **Chart Colors**: Combination of primary, accent, and triadic colors

### Color Harmonies

- **Complementary**: Colors opposite on the color wheel (180°)
- **Triadic**: Three colors evenly spaced (120° apart)
- **Analogous**: Adjacent colors on the wheel (±30°)
- **Split-Complementary**: Base + two colors adjacent to complement

### Light vs Dark Mode

**Light Mode:**
- Background: White (#ffffff)
- Foreground: Near-black (#0a0a0a)
- Muted: Light gray (#f4f4f5)

**Dark Mode:**
- Background: Near-black (#0a0a0a)
- Foreground: Off-white (#fafafa)
- Muted: Dark gray (#27272a)

## Generated Theme Structure

```json
{
  "name": "theme-name",
  "display_name": "Theme Name",
  "colors": {
    "background": "#ffffff",
    "foreground": "#0a0a0a",
    "primary": "#3b82f6",
    "primary_foreground": "#fafafa",
    "secondary": "#...",
    "accent": "#...",
    "success": "#22c55e",
    "warning": "#f59e0b",
    "error": "#ef4444",
    "info": "#3b82f6",
    "chart_1": "#...",
    "chart_2": "#...",
    "chart_3": "#...",
    "chart_4": "#...",
    "chart_5": "#..."
  },
  "typography": { ... },
  "spacing": { ... },
  "shadows": { ... },
  "borders": { ... },
  "animations": { ... }
}
```

## Examples

### Example 1: Blue Theme

```bash
python tools/theme_generator.py --base-color "#3b82f6" --name "ocean-blue"
```

**Generated Colors:**
- Primary: #3b82f6 (Blue)
- Secondary: #3b5cf6 (Blue-Purple)
- Accent: #f6a93b (Orange)

### Example 2: Purple Dark Theme

```bash
python tools/theme_generator.py --base-color "#8b5cf6" --name "midnight-purple" --dark
```

**Generated Colors:**
- Primary: #8b5cf6 (Purple)
- Secondary: #5c6bf6 (Blue-Purple)
- Accent: #c6f65c (Yellow-Green)

### Example 3: Green Theme

```bash
python tools/theme_generator.py --base-color "#10b981" --name "forest-green"
```

**Generated Colors:**
- Primary: #10b981 (Green)
- Secondary: #10b95c (Green-Yellow)
- Accent: #b91081 (Magenta)

## Best Practices

### Choosing a Base Color

1. **Brand Colors**: Use your company's primary brand color
2. **Purpose**: Consider the app's purpose (finance = blue, health = green)
3. **Contrast**: Ensure good contrast with white/black backgrounds
4. **Saturation**: Avoid overly saturated colors for better readability

### Theme Naming

- Use kebab-case: `my-theme-name`
- Be descriptive: `ocean-blue`, `forest-green`, `sunset-orange`
- Include mode: `purple-dark`, `blue-light`

### Testing Themes

1. Generate the theme
2. Preview colors in the terminal
3. Export to JSON
4. Load in your app
5. Test with actual UI components
6. Adjust base color if needed

## Troubleshooting

### Issue: Colors Don't Look Good Together

**Solution**: Try a different base color or adjust the hue slightly. Colors with 40-60% saturation usually work best.

### Issue: Poor Contrast

**Solution**: The tool automatically calculates contrasting foreground colors, but you may need to adjust the base color's lightness.

### Issue: Theme Not Loading

**Solution**: Ensure the JSON file is in the correct directory (`theming/themes/`) and the theme name matches the filename.

## Advanced Usage

### Custom Color Palette

```python
from tools.theme_generator import ThemeGenerator, ColorGenerator

# Create custom palette
generator = ThemeGenerator("#3b82f6", "custom", False)
palette = generator.generate_color_palette()

# Modify colors
palette.accent = ColorGenerator.rotate_hue(palette.primary, 90)
palette.secondary = ColorGenerator.lighten(palette.primary, 30)

# Generate theme with custom palette
theme = generator.generate_theme()
```

### Batch Generate with Custom Colors

```python
from tools.theme_generator import ThemeGenerator

colors = [
    ("#3b82f6", "blue"),
    ("#8b5cf6", "purple"),
    ("#10b981", "green"),
]

for color, name in colors:
    # Light version
    gen_light = ThemeGenerator(color, f"{name}-light", False)
    gen_light.export_to_json()
    
    # Dark version
    gen_dark = ThemeGenerator(color, f"{name}-dark", True)
    gen_dark.export_to_json()
```

## Command-Line Reference

```
usage: theme_generator.py [-h] [--interactive] [--base-color BASE_COLOR]
                         [--name NAME] [--dark] [--output OUTPUT]
                         [--preview-only] [--batch]

Generate shadcn/ui themes from a base color

optional arguments:
  -h, --help            show this help message and exit
  --interactive, -i     Run in interactive mode
  --base-color BASE_COLOR, -c BASE_COLOR
                        Base color in hex format (e.g., #3b82f6)
  --name NAME, -n NAME  Theme name (e.g., my-custom-theme)
  --dark, -d            Generate dark theme variant
  --output OUTPUT, -o OUTPUT
                        Output directory for theme files
  --preview-only, -p    Only show preview, do not export
  --batch, -b           Generate multiple predefined themes
```

## See Also

- [Theme System Reference](../theming/THEME_SELECTOR_REFERENCE.md)
- [CSS Generator Reference](../theming/CSS_GENERATOR_REFERENCE.md)
- [Component Library](../components/README.md)
