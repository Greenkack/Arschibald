# CSS Generator - Quick Reference

## Schnellstart

```python
from theming import ThemeManager

# Theme Manager initialisieren
theme_manager = ThemeManager()
theme_manager.set_theme("shadcn-default")

# CSS generieren
css = theme_manager.generate_css()

# In Streamlit injizieren
import streamlit as st
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
```

## API

### CSSGenerator

```python
from theming import CSSGenerator

css_gen = CSSGenerator(theme)
css_gen.generate_css_variables()      # CSS-Variablen
css_gen.generate_component_styles()   # Component-Styles
css_gen.generate_utility_classes()    # Utility-Klassen
css_gen.generate_full_css()           # Vollständiges CSS
```

### ThemeManager

```python
from theming import ThemeManager

tm = ThemeManager()
tm.set_theme("shadcn-dark")
css = tm.generate_css()  # Convenience-Methode
```

## CSS-Variablen

### Colors
```css
--background, --foreground
--primary, --primary-foreground
--secondary, --secondary-foreground
--accent, --accent-foreground
--success, --warning, --error, --info
--muted, --muted-foreground
--border, --input, --ring
--chart-1, --chart-2, --chart-3, --chart-4, --chart-5
```

### Typography
```css
--font-family, --font-family-mono
--font-size-xs, --font-size-sm, --font-size-base, --font-size-lg, --font-size-xl, --font-size-2xl
--font-weight-normal, --font-weight-medium, --font-weight-semibold, --font-weight-bold
--line-height-tight, --line-height-normal, --line-height-relaxed
```

### Spacing
```css
--spacing-0, --spacing-1, --spacing-2, --spacing-3, --spacing-4
--spacing-6, --spacing-8, --spacing-12, --spacing-16
```

### Shadows
```css
--shadow-sm, --shadow-md, --shadow-lg, --shadow-xl
```

### Borders
```css
--border-width
--border-radius-sm, --border-radius-md, --border-radius-lg, --border-radius-full
```

### Animations
```css
--transition-fast, --transition-base, --transition-slow
--easing-default
```

## Utility-Klassen

### Spacing
```css
.p-0, .p-1, .p-2, .p-3, .p-4, .p-6, .p-8
.px-0, .px-1, .px-2, .px-3, .px-4, .px-6, .px-8
.py-0, .py-1, .py-2, .py-3, .py-4, .py-6, .py-8
.m-0, .m-1, .m-2, .m-3, .m-4, .m-6, .m-8
```

### Typography
```css
.text-xs, .text-sm, .text-base, .text-lg, .text-xl, .text-2xl
.font-normal, .font-medium, .font-semibold, .font-bold
```

### Colors
```css
.text-foreground, .text-muted, .text-primary, .text-success, .text-warning, .text-error, .text-info
.bg-background, .bg-muted, .bg-primary, .bg-secondary, .bg-accent
```

### Borders
```css
.border, .border-t, .border-b, .border-l, .border-r
.rounded-sm, .rounded-md, .rounded-lg, .rounded-full
```

### Shadows
```css
.shadow-sm, .shadow-md, .shadow-lg, .shadow-xl
```

### Transitions
```css
.transition-fast, .transition-base, .transition-slow
```

## Gestylte Komponenten

- ✓ Buttons (`.stButton`)
- ✓ Text Input (`.stTextInput`)
- ✓ Number Input (`.stNumberInput`)
- ✓ Text Area (`.stTextArea`)
- ✓ Selectbox (`.stSelectbox`)
- ✓ MultiSelect (`.stMultiSelect`)
- ✓ Slider (`.stSlider`)
- ✓ Checkbox (`.stCheckbox`)
- ✓ Radio (`.stRadio`)
- ✓ Tabs (`.stTabs`)
- ✓ Expander (`.streamlit-expanderHeader`)

## Beispiele

### Custom Card
```python
st.markdown("""
    <div class="p-6 bg-background border rounded-lg shadow-md">
        <h3 class="text-xl font-bold text-foreground">Title</h3>
        <p class="text-sm text-muted">Content</p>
    </div>
""", unsafe_allow_html=True)
```

### Alert Box
```python
st.markdown("""
    <div class="p-4 bg-accent border-l-4 rounded-md">
        <p class="text-sm font-medium">Alert message</p>
    </div>
""", unsafe_allow_html=True)
```

### Badge
```python
st.markdown("""
    <span class="px-2 py-1 bg-primary text-primary-foreground 
                 text-xs font-medium rounded-full">
        Badge
    </span>
""", unsafe_allow_html=True)
```

## Performance

- **CSS-Größe:** ~13 KB
- **Generierungszeit:** < 10ms
- **Caching:** Empfohlen mit `@st.cache_data`

```python
@st.cache_data
def get_theme_css(theme_name: str) -> str:
    tm = ThemeManager()
    tm.set_theme(theme_name)
    return tm.generate_css()
```

## Siehe auch

- [Vollständige Dokumentation](./CSS_GENERATOR_REFERENCE.md)
- [Theme Manager Reference](./THEME_MANAGER_REFERENCE.md)
- [Usage Example](./USAGE_EXAMPLE.md)
