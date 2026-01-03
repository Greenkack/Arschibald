# Theme Selector UI - Referenz

Vollständige Referenz für die Theme-Selector-UI-Komponente.

## Übersicht

Die Theme-Selector-UI bietet eine vollständige Lösung für Theme-Verwaltung in Streamlit-Apps:

- 🎨 **Live Theme-Wechsel** ohne Seiten-Reload
- 🌙 **Dark Mode Toggle** für schnellen Wechsel zwischen Hell/Dunkel
- 👁️ **Live-Vorschau** der Theme-Farben
- 💾 **Local Storage Persistierung** der Theme-Auswahl
- 🔄 **Session State Integration**
- 📞 **Callback-Support** für Theme-Wechsel-Events

## Klassen

### ThemeSelectorUI

Haupt-UI-Komponente für Theme-Auswahl.

```python
class ThemeSelectorUI:
    def __init__(self, theme_manager: ThemeManager)
    def render(
        self,
        on_theme_change: Optional[Callable[[str], None]] = None,
        show_preview: bool = True,
        show_dark_mode_toggle: bool = True
    ) -> None
```

#### Parameter

- `theme_manager`: ThemeManager-Instanz
- `on_theme_change`: Callback-Funktion die bei Theme-Wechsel aufgerufen wird
- `show_preview`: Zeigt Live-Vorschau der Theme-Farben (default: True)
- `show_dark_mode_toggle`: Zeigt Dark Mode Toggle (default: True)

#### Beispiel

```python
from theming.theme_manager import ThemeManager
from theming.theme_selector_ui import ThemeSelectorUI

theme_manager = ThemeManager()
selector = ThemeSelectorUI(theme_manager)

def on_theme_change(theme_name: str):
    print(f"Theme gewechselt zu: {theme_name}")

selector.render(
    on_theme_change=on_theme_change,
    show_preview=True,
    show_dark_mode_toggle=True
)
```

## Funktionen

### render_theme_selector()

Convenience-Funktion zum Rendern des Theme-Selectors.

```python
def render_theme_selector(
    theme_manager: ThemeManager,
    on_theme_change: Optional[Callable[[str], None]] = None,
    show_preview: bool = True,
    show_dark_mode_toggle: bool = True
) -> None
```

#### Beispiel

```python
from theming.theme_selector_ui import render_theme_selector

with st.sidebar:
    render_theme_selector(
        theme_manager=theme_manager,
        on_theme_change=lambda name: st.toast(f"Theme: {name}")
    )
```

### inject_theme_css()

Injiziert Theme-CSS in die App. Sollte einmal beim App-Start aufgerufen werden.

```python
def inject_theme_css(theme_manager: ThemeManager) -> None
```

#### Beispiel

```python
from theming.theme_selector_ui import inject_theme_css

# Beim App-Start
inject_theme_css(theme_manager)
```

### get_current_theme_name()

Gibt den Namen des aktuellen Themes zurück.

```python
def get_current_theme_name() -> str
```

#### Beispiel

```python
from theming.theme_selector_ui import get_current_theme_name

current_theme = get_current_theme_name()
print(f"Aktuelles Theme: {current_theme}")
```

### is_dark_mode()

Prüft ob Dark Mode aktiv ist.

```python
def is_dark_mode() -> bool
```

#### Beispiel

```python
from theming.theme_selector_ui import is_dark_mode

if is_dark_mode():
    print("Dark Mode ist aktiv")
```

## Features im Detail

### 1. Live Theme-Wechsel

Der Theme-Wechsel erfolgt ohne vollständigen Seiten-Reload:

```python
# Theme wird sofort gewechselt
render_theme_selector(theme_manager)

# Callback wird aufgerufen
def on_change(theme_name: str):
    st.toast(f"✅ Theme: {theme_name}")

render_theme_selector(
    theme_manager,
    on_theme_change=on_change
)
```

### 2. Dark Mode Toggle

Schneller Wechsel zwischen Hell und Dunkel:

```python
# Mit Dark Mode Toggle
render_theme_selector(
    theme_manager,
    show_dark_mode_toggle=True
)

# Prüfe Dark Mode Status
if is_dark_mode():
    st.write("Dark Mode aktiv")
```

### 3. Live-Vorschau

Zeigt die wichtigsten Theme-Farben:

```python
# Mit Vorschau
render_theme_selector(
    theme_manager,
    show_preview=True
)

# Ohne Vorschau
render_theme_selector(
    theme_manager,
    show_preview=False
)
```

### 4. Local Storage Persistierung

Theme-Auswahl wird automatisch im Browser gespeichert:

```python
# Automatische Persistierung
render_theme_selector(theme_manager)

# Theme wird beim nächsten Besuch wiederhergestellt
```

### 5. Session State Integration

Theme-Status wird in Streamlit Session State gespeichert:

```python
# Zugriff auf Session State
current_theme = st.session_state.get('current_theme')
dark_mode = st.session_state.get('dark_mode')

# Manuelles Setzen
st.session_state.current_theme = 'shadcn-ocean'
st.session_state.dark_mode = True
```

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
    st.set_page_config(
        page_title="My App",
        page_icon="🎨",
        layout="wide"
    )

    # Initialisiere Theme Manager (einmal)
    if 'theme_manager' not in st.session_state:
        st.session_state.theme_manager = ThemeManager()

    theme_manager = st.session_state.theme_manager

    # Injiziere CSS (automatisch gecacht)
    inject_theme_css(theme_manager)

    # Sidebar mit Theme Selector
    with st.sidebar:
        st.title("My App")

        # Theme Selector mit Callback
        def on_theme_change(theme_name: str):
            st.toast(f"✅ Theme: {theme_name}", icon="🎨")

        render_theme_selector(
            theme_manager=theme_manager,
            on_theme_change=on_theme_change,
            show_preview=True,
            show_dark_mode_toggle=True
        )

    # Hauptinhalt
    st.title("Welcome to My App")

    # Zeige aktuelles Theme
    current_theme = get_current_theme_name()
    st.write(f"Aktuelles Theme: {current_theme}")

    if is_dark_mode():
        st.write("🌙 Dark Mode ist aktiv")

    # Deine App-Inhalte...
    st.button("Click me")
    st.text_input("Enter text")

if __name__ == "__main__":
    main()
```

## Session State Variablen

Der Theme Selector verwendet folgende Session State Variablen:

| Variable | Typ | Beschreibung |
|----------|-----|--------------|
| `current_theme` | str | Name des aktuellen Themes |
| `dark_mode` | bool | Dark Mode Status |
| `shadcn_theme_loaded` | bool | Flag ob Theme aus Local Storage geladen wurde |
| `injected_theme` | str | Name des zuletzt injizierten Themes |
| `theme_manager` | ThemeManager | ThemeManager-Instanz |

## Local Storage Keys

Folgende Keys werden im Browser Local Storage verwendet:

| Key | Typ | Beschreibung |
|-----|-----|--------------|
| `shadcn_theme` | string | Name des gespeicherten Themes |
| `shadcn_dark_mode` | string | Dark Mode Status ("true"/"false") |

## Callbacks

### on_theme_change Callback

Wird aufgerufen wenn das Theme gewechselt wird:

```python
def on_theme_change(theme_name: str) -> None:
    """
    Args:
        theme_name: Name des neuen Themes
    """
    print(f"Theme gewechselt zu: {theme_name}")

    # Beispiel: Analytics tracken
    track_event("theme_change", {"theme": theme_name})

    # Beispiel: Benachrichtigung anzeigen
    st.toast(f"✅ Theme: {theme_name}")

    # Beispiel: Custom-Logik
    if theme_name == "shadcn-dark":
        st.session_state.custom_setting = "dark_value"
```

## Styling

Der Theme Selector verwendet die Theme-Tokens für konsistentes Styling:

```python
# Farb-Swatches in der Vorschau
.color-swatch {
    height: 40px;
    border-radius: 6px;
    border: 1px solid #e0e0e0;
}

# Grid-Layout für Farben
.color-preview {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
}
```

## Best Practices

### 1. Theme Manager Initialisierung

Initialisiere den Theme Manager nur einmal:

```python
# ✅ Gut
if 'theme_manager' not in st.session_state:
    st.session_state.theme_manager = ThemeManager()

# ❌ Schlecht
theme_manager = ThemeManager()  # Bei jedem Rerun neu
```

### 2. CSS Injection

Injiziere CSS nur einmal (wird automatisch gecacht):

```python
# ✅ Gut
inject_theme_css(theme_manager)  # Automatisches Caching

# ❌ Schlecht
css = theme_manager.generate_css()
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
```

### 3. Sidebar Platzierung

Platziere den Theme Selector in der Sidebar:

```python
# ✅ Gut
with st.sidebar:
    render_theme_selector(theme_manager)

# ❌ Schlecht
render_theme_selector(theme_manager)  # Im Hauptbereich
```

### 4. Callback-Verwendung

Verwende Callbacks für Theme-Wechsel-Events:

```python
# ✅ Gut
def on_change(theme_name: str):
    st.toast(f"Theme: {theme_name}")

render_theme_selector(
    theme_manager,
    on_theme_change=on_change
)

# ✅ Auch gut (Lambda)
render_theme_selector(
    theme_manager,
    on_theme_change=lambda name: st.toast(f"Theme: {name}")
)
```

## Troubleshooting

### Theme wird nicht geladen

```python
# Prüfe ob Theme Manager initialisiert ist
if 'theme_manager' not in st.session_state:
    st.error("Theme Manager nicht initialisiert")

# Prüfe verfügbare Themes
themes = theme_manager.get_available_themes()
st.write(f"Verfügbare Themes: {themes}")
```

### CSS wird nicht angewendet

```python
# Prüfe ob CSS injiziert wurde
if 'injected_theme' in st.session_state:
    st.write(f"Injiziertes Theme: {st.session_state.injected_theme}")
else:
    st.warning("CSS noch nicht injiziert")

# Force CSS Injection
st.session_state.pop('injected_theme', None)
inject_theme_css(theme_manager)
```

### Local Storage funktioniert nicht

```python
# Prüfe Browser-Konsole für JavaScript-Fehler
# Prüfe ob Query Params gesetzt sind
query_params = st.query_params
st.write(f"Query Params: {query_params}")
```

## Performance

### CSS Caching

CSS wird automatisch gecacht und nur bei Theme-Wechsel neu generiert:

```python
# Erste Injection: ~50ms
inject_theme_css(theme_manager)

# Weitere Injections: ~1ms (gecacht)
inject_theme_css(theme_manager)
```

### Rerun-Optimierung

Theme-Wechsel löst nur einen Rerun aus:

```python
# Optimiert: Ein Rerun pro Theme-Wechsel
render_theme_selector(theme_manager)
```

## Erweiterungen

### Custom Themes hinzufügen

```python
# Erstelle neue Theme-Datei
# theming/themes/my-custom-theme.json

# Theme wird automatisch erkannt
theme_manager.load_themes()
```

### Custom Callback-Logik

```python
def advanced_callback(theme_name: str):
    # Analytics
    track_theme_change(theme_name)

    # Benachrichtigung
    st.toast(f"Theme: {theme_name}")

    # Custom State
    st.session_state.last_theme_change = datetime.now()

    # API Call
    save_user_preference(user_id, theme_name)

render_theme_selector(
    theme_manager,
    on_theme_change=advanced_callback
)
```

## Siehe auch

- [Theme Manager Referenz](THEME_MANAGER_REFERENCE.md)
- [CSS Generator Referenz](CSS_GENERATOR_REFERENCE.md)
- [Theme Tokens Referenz](THEME_TOKENS_REFERENCE.md)
