# Theme Selector UI - Quick Reference

Schnellreferenz für die Theme-Selector-UI-Komponente.

## Installation

```python
from theming.theme_manager import ThemeManager
from theming.theme_selector_ui import (
    render_theme_selector,
    inject_theme_css
)
```

## Basis-Setup

```python
import streamlit as st
from theming.theme_manager import ThemeManager
from theming.theme_selector_ui import render_theme_selector, inject_theme_css

# Initialisiere Theme Manager (einmal)
if 'theme_manager' not in st.session_state:
    st.session_state.theme_manager = ThemeManager()

theme_manager = st.session_state.theme_manager

# Injiziere CSS
inject_theme_css(theme_manager)

# Rendere Theme Selector in Sidebar
with st.sidebar:
    render_theme_selector(theme_manager)
```

## Features

### Mit allen Features

```python
render_theme_selector(
    theme_manager=theme_manager,
    on_theme_change=lambda name: st.toast(f"Theme: {name}"),
    show_preview=True,
    show_dark_mode_toggle=True
)
```

### Minimal

```python
render_theme_selector(theme_manager)
```

### Ohne Dark Mode Toggle

```python
render_theme_selector(
    theme_manager,
    show_dark_mode_toggle=False
)
```

### Ohne Vorschau

```python
render_theme_selector(
    theme_manager,
    show_preview=False
)
```

## Callbacks

### Einfacher Callback

```python
def on_change(theme_name: str):
    st.toast(f"✅ Theme: {theme_name}")

render_theme_selector(
    theme_manager,
    on_theme_change=on_change
)
```

### Lambda Callback

```python
render_theme_selector(
    theme_manager,
    on_theme_change=lambda name: print(f"Theme: {name}")
)
```

### Erweiterter Callback

```python
def advanced_callback(theme_name: str):
    # Benachrichtigung
    st.toast(f"Theme gewechselt zu: {theme_name}", icon="🎨")

    # Analytics
    track_event("theme_change", {"theme": theme_name})

    # Custom State
    st.session_state.last_theme_change = datetime.now()

render_theme_selector(
    theme_manager,
    on_theme_change=advanced_callback
)
```

## Utility-Funktionen

### Aktuelles Theme abrufen

```python
from theming.theme_selector_ui import get_current_theme_name

current_theme = get_current_theme_name()
st.write(f"Aktuelles Theme: {current_theme}")
```

### Dark Mode Status prüfen

```python
from theming.theme_selector_ui import is_dark_mode

if is_dark_mode():
    st.write("🌙 Dark Mode aktiv")
else:
    st.write("☀️ Light Mode aktiv")
```

## Session State

### Zugriff auf Theme-Status

```python
# Aktuelles Theme
current_theme = st.session_state.get('current_theme', 'shadcn-default')

# Dark Mode Status
dark_mode = st.session_state.get('dark_mode', False)

# Theme Manager
theme_manager = st.session_state.get('theme_manager')
```

### Manuelles Setzen

```python
# Theme setzen
st.session_state.current_theme = 'shadcn-ocean'

# Dark Mode setzen
st.session_state.dark_mode = True

# Rerun erforderlich
st.rerun()
```

## Verfügbare Themes

| Theme Name | Display Name | Beschreibung |
|------------|--------------|--------------|
| `shadcn-default` | shadcn/ui Default | Helles Standard-Theme |
| `shadcn-dark` | shadcn/ui Dark | Dunkles Theme |
| `shadcn-ocean` | shadcn/ui Ocean | Blaues Theme |
| `shadcn-forest` | shadcn/ui Forest | Grünes Theme |
| `shadcn-sunset` | shadcn/ui Sunset | Orange/Rotes Theme |

## Vollständiges Beispiel

```python
import streamlit as st
from theming.theme_manager import ThemeManager
from theming.theme_selector_ui import (
    render_theme_selector,
    inject_theme_css,
    get_current_theme_name,
    is_dark_mode
)

def main():
    st.set_page_config(page_title="My App", layout="wide")

    # Theme Manager
    if 'theme_manager' not in st.session_state:
        st.session_state.theme_manager = ThemeManager()

    theme_manager = st.session_state.theme_manager

    # CSS Injection
    inject_theme_css(theme_manager)

    # Sidebar
    with st.sidebar:
        st.title("My App")

        # Theme Selector
        render_theme_selector(
            theme_manager=theme_manager,
            on_theme_change=lambda name: st.toast(f"Theme: {name}"),
            show_preview=True,
            show_dark_mode_toggle=True
        )

    # Hauptinhalt
    st.title("Welcome")

    # Theme Info
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Theme", get_current_theme_name())
    with col2:
        st.metric("Dark Mode", "Aktiv" if is_dark_mode() else "Inaktiv")

    # Demo-Komponenten
    st.button("Click me")
    st.text_input("Enter text")

if __name__ == "__main__":
    main()
```

## Häufige Probleme

### Theme wird nicht geladen

```python
# Prüfe Theme Manager
if 'theme_manager' not in st.session_state:
    st.error("Theme Manager nicht initialisiert!")

# Prüfe verfügbare Themes
themes = theme_manager.get_available_themes()
st.write(f"Verfügbare Themes: {themes}")
```

### CSS wird nicht angewendet

```python
# Force CSS Injection
st.session_state.pop('injected_theme', None)
inject_theme_css(theme_manager)
st.rerun()
```

### Local Storage funktioniert nicht

```python
# Prüfe Query Params
query_params = st.query_params
st.write(f"Query Params: {query_params}")

# Prüfe Browser-Konsole für JavaScript-Fehler
```

## Best Practices

### ✅ Do

```python
# Theme Manager einmal initialisieren
if 'theme_manager' not in st.session_state:
    st.session_state.theme_manager = ThemeManager()

# CSS automatisch cachen lassen
inject_theme_css(theme_manager)

# Theme Selector in Sidebar
with st.sidebar:
    render_theme_selector(theme_manager)

# Callbacks verwenden
render_theme_selector(
    theme_manager,
    on_theme_change=lambda name: st.toast(f"Theme: {name}")
)
```

### ❌ Don't

```python
# Theme Manager bei jedem Rerun neu erstellen
theme_manager = ThemeManager()  # ❌

# CSS manuell injizieren
css = theme_manager.generate_css()
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)  # ❌

# Theme Selector im Hauptbereich
render_theme_selector(theme_manager)  # ❌ (sollte in Sidebar sein)
```

## Performance-Tipps

```python
# CSS wird automatisch gecacht
inject_theme_css(theme_manager)  # Erste Injection: ~50ms
inject_theme_css(theme_manager)  # Weitere: ~1ms (gecacht)

# Theme Manager wiederverwenden
theme_manager = st.session_state.theme_manager  # ✅

# Callbacks optimieren
def optimized_callback(theme_name: str):
    # Nur notwendige Operationen
    st.toast(f"Theme: {theme_name}")

render_theme_selector(
    theme_manager,
    on_theme_change=optimized_callback
)
```

## Siehe auch

- [Vollständige Referenz](THEME_SELECTOR_REFERENCE.md)
- [Theme Manager](THEME_MANAGER_REFERENCE.md)
- [CSS Generator](CSS_GENERATOR_REFERENCE.md)
