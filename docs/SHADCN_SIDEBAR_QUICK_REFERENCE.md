# shadcn/ui Sidebar - Quick Reference

## Installation

```python
from utils.shadcn_sidebar import (
    ShadcnSidebar,
    MenuGroup,
    MenuItem,
    create_sidebar_menu
)
```

## Schnellstart

### Einfache Sidebar

```python
sidebar = ShadcnSidebar()

groups = [
    MenuGroup(
        title="Navigation",
        items=[
            MenuItem("Home", icon="🏠", key="home"),
            MenuItem("About", icon="ℹ️", key="about"),
        ]
    )
]

selected = sidebar.render(groups)
```

## MenuItem

### Basis

```python
MenuItem(
    label="Dashboard",
    icon="📊",
    key="dashboard"
)
```

### Mit Callback

```python
def on_click():
    st.success("Geklickt!")

MenuItem(
    label="Button",
    icon="🔘",
    key="btn",
    callback=on_click
)
```

### Deaktiviert

```python
MenuItem(
    label="Bald verfügbar",
    icon="🔒",
    key="soon",
    disabled=True
)
```

## MenuGroup

### Basis

```python
MenuGroup(
    title="Hauptmenü",
    items=[
        MenuItem("Item 1", key="i1"),
        MenuItem("Item 2", key="i2"),
    ]
)
```

### Kollabierbar

```python
MenuGroup(
    title="Erweitert",
    items=[...],
    collapsible=True,
    collapsed=True  # Initial kollabiert
)
```

## ShadcnSidebar

### Initialisierung

```python
# Ohne ThemeManager
sidebar = ShadcnSidebar()

# Mit ThemeManager
sidebar = ShadcnSidebar(theme_manager)
```

### Rendering

```python
# Basis
selected = sidebar.render(groups)

# Ohne Trennlinien
selected = sidebar.render(groups, show_dividers=False)

# Mit Footer
def footer():
    st.caption("Version 1.0")

selected = sidebar.render(groups, footer_content=footer)
```

## Convenience-Funktion

```python
selected = create_sidebar_menu(
    menu_groups=groups,
    theme_manager=theme_manager,
    show_dividers=True
)
```

## Vordefinierte Menüs

### Standard-Menü

```python
from utils.shadcn_sidebar import get_default_menu

sidebar.render(get_default_menu())
```

### Solar-Rechner-Menü

```python
from utils.shadcn_sidebar import get_solar_calculator_menu

sidebar.render(get_solar_calculator_menu())
```

## Aktiven Eintrag prüfen

```python
selected = sidebar.render(groups)

if selected == "home":
    st.write("Home-Seite")
elif selected == "about":
    st.write("About-Seite")
```

## Session State

### Aktiver Eintrag

```python
# Lesen
active = st.session_state.get('active_menu_item')

# Setzen
st.session_state.active_menu_item = "dashboard"
```

### Kollabierte Gruppen

```python
# Lesen
collapsed = st.session_state.get('collapsed_groups', set())

# Gruppe kollabieren
st.session_state.collapsed_groups.add("group_0_Erweitert")

# Gruppe expandieren
st.session_state.collapsed_groups.discard("group_0_Erweitert")
```

## Styling

### Custom CSS

```python
st.markdown("""
<style>
.shadcn-menu-item {
    font-size: 1rem;
}
</style>
""", unsafe_allow_html=True)
```

### Theme-Tokens

Die Sidebar verwendet automatisch Theme-Tokens:
- `colors.primary` - Aktiver Eintrag
- `colors.accent` - Hover-Effekt
- `colors.border` - Trennlinien
- `typography.font_family` - Schriftart
- `spacing.*` - Abstände

## Beispiele

### Vollständiges Beispiel

```python
import streamlit as st
from utils.shadcn_sidebar import ShadcnSidebar, MenuGroup, MenuItem

# Initialisiere Sidebar
sidebar = ShadcnSidebar()

# Definiere Menü
groups = [
    MenuGroup(
        title="Hauptmenü",
        items=[
            MenuItem("Dashboard", icon="📊", key="dashboard"),
            MenuItem("Projekte", icon="📁", key="projects"),
            MenuItem("Berichte", icon="📈", key="reports"),
        ]
    ),
    MenuGroup(
        title="Einstellungen",
        items=[
            MenuItem("Profil", icon="👤", key="profile"),
            MenuItem("Themes", icon="🎨", key="themes"),
        ]
    )
]

# Rendere Sidebar
with st.sidebar:
    selected = sidebar.render(groups)

# Hauptbereich
if selected == "dashboard":
    st.title("Dashboard")
    st.write("Willkommen!")
elif selected == "projects":
    st.title("Projekte")
    st.write("Ihre Projekte")
# ... weitere Seiten
```

### Mit Navigation

```python
def navigate_to(page):
    st.session_state.current_page = page
    st.rerun()

groups = [
    MenuGroup(
        title="Navigation",
        items=[
            MenuItem(
                "Home",
                icon="🏠",
                key="home",
                callback=lambda: navigate_to("home")
            ),
            MenuItem(
                "Settings",
                icon="⚙️",
                key="settings",
                callback=lambda: navigate_to("settings")
            ),
        ]
    )
]

sidebar.render(groups)
```

### Dynamisches Menü

```python
def get_dynamic_menu():
    items = [MenuItem("Home", icon="🏠", key="home")]
    
    # Füge Admin-Eintrag nur für Admins hinzu
    if st.session_state.get('is_admin'):
        items.append(
            MenuItem("Admin", icon="⚙️", key="admin")
        )
    
    return [MenuGroup(title="Menü", items=items)]

sidebar.render(get_dynamic_menu())
```

## Tipps

1. **Eindeutige Keys:** Jeder MenuItem braucht einen eindeutigen `key`
2. **Icons:** Verwende Emojis oder HTML für Icons
3. **Callbacks:** Halte Callbacks leichtgewichtig
4. **Caching:** Cache Menü-Konfigurationen mit `@st.cache_data`
5. **Theme:** Nutze ThemeManager für konsistentes Styling

## Häufige Fehler

### ❌ Fehlende Keys

```python
# Falsch
MenuItem("Home")  # Kein key

# Richtig
MenuItem("Home", key="home")
```

### ❌ Doppelte Keys

```python
# Falsch
items=[
    MenuItem("Item", key="item"),
    MenuItem("Item", key="item"),  # Doppelter key
]

# Richtig
items=[
    MenuItem("Item 1", key="item1"),
    MenuItem("Item 2", key="item2"),
]
```

### ❌ Schwere Callbacks

```python
# Falsch
def heavy_callback():
    # Lange Berechnung
    time.sleep(5)

# Richtig
def light_callback():
    st.session_state.trigger_calculation = True
```

## Siehe auch

- [Vollständige Referenz](../utils/SHADCN_SIDEBAR_REFERENCE.md)
- [Theme System](../theming/THEME_SELECTOR_QUICK_REFERENCE.md)
- [Komponenten](../components/CARD_QUICK_REFERENCE.md)
