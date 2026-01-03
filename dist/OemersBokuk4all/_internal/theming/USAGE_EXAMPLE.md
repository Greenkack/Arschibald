# Theme System Usage Example

## Quick Start

```python
from theming import ThemeManager

# Initialize the theme manager
theme_manager = ThemeManager()

# Set a theme
theme_manager.set_theme('shadcn-default')

# Access design tokens
primary_color = theme_manager.get_token('colors.primary')
font_family = theme_manager.get_token('typography.font_family')
spacing = theme_manager.get_token('spacing.spacing_4')

print(f"Primary Color: {primary_color}")
print(f"Font Family: {font_family}")
print(f"Spacing: {spacing}")
```

## Available Themes

The system includes 5 predefined themes:

1. **shadcn-default** - Classic light theme with neutral colors
2. **shadcn-dark** - Dark mode with high contrast
3. **shadcn-ocean** - Ocean blue theme for a calm, professional look
4. **shadcn-forest** - Forest green theme for eco-friendly applications
5. **shadcn-sunset** - Warm sunset orange theme for energetic designs

## Switching Themes

```python
# Get list of available themes
themes = theme_manager.get_available_themes()
print(f"Available themes: {themes}")

# Switch to a different theme
theme_manager.set_theme('shadcn-ocean')

# Get display names for UI
display_names = theme_manager.get_theme_display_names()
# Returns: {'shadcn-default': 'shadcn/ui Default', ...}
```

## Accessing Theme Tokens

Theme tokens are organized into categories:

### Colors
```python
background = theme_manager.get_token('colors.background')
foreground = theme_manager.get_token('colors.foreground')
primary = theme_manager.get_token('colors.primary')
success = theme_manager.get_token('colors.success')
error = theme_manager.get_token('colors.error')
```

### Typography
```python
font_family = theme_manager.get_token('typography.font_family')
font_size_base = theme_manager.get_token('typography.font_size_base')
font_weight_bold = theme_manager.get_token('typography.font_weight_bold')
line_height = theme_manager.get_token('typography.line_height_normal')
```

### Spacing
```python
spacing_sm = theme_manager.get_token('spacing.spacing_2')
spacing_md = theme_manager.get_token('spacing.spacing_4')
spacing_lg = theme_manager.get_token('spacing.spacing_8')
```

### Shadows
```python
shadow_sm = theme_manager.get_token('shadows.shadow_sm')
shadow_md = theme_manager.get_token('shadows.shadow_md')
shadow_lg = theme_manager.get_token('shadows.shadow_lg')
```

### Borders
```python
border_width = theme_manager.get_token('borders.border_width')
border_radius = theme_manager.get_token('borders.border_radius_lg')
```

### Animations
```python
transition = theme_manager.get_token('animations.transition_base')
easing = theme_manager.get_token('animations.easing_default')
```

## Working with Theme Objects

```python
# Get the current theme object
current_theme = theme_manager.current_theme

# Access theme properties directly
print(f"Theme Name: {current_theme.name}")
print(f"Display Name: {current_theme.display_name}")

# Access token categories
colors = current_theme.colors
typography = current_theme.typography

# Convert theme to dictionary
theme_dict = current_theme.to_dict()
```

## Error Handling

```python
# The system includes fallback mechanisms
try:
    theme_manager = ThemeManager()
except FileNotFoundError:
    print("Theme directory not found")
except ValueError:
    print("No themes available")

# Get fallback theme if needed
fallback = theme_manager.get_fallback_theme()
```

## Next Steps

This theme system infrastructure is ready for:
- CSS generation (Task 2)
- Theme selector UI (Task 3)
- Component styling (Tasks 4-9)
- Integration with Streamlit app (Task 16)
