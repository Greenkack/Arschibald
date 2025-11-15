# shadcn/ui Sidebar - Technische Referenz

## Übersicht

Das `shadcn_sidebar`-Modul bietet eine moderne, vollständig anpassbare Sidebar-Komponente mit shadcn/ui-Design für Streamlit-Anwendungen.

## Architektur

### Klassen

#### `MenuItem`
Repräsentiert einen einzelnen Menü-Eintrag.

**Attribute:**
- `label` (str): Anzeigetext des Menü-Eintrags
- `icon` (Optional[str]): Icon (Emoji oder HTML)
- `key` (Optional[str]): Eindeutiger Schlüssel
- `callback` (Optional[Callable]): Callback-Funktion beim Klick
- `disabled` (bool): Deaktivierungs-Status

#### `MenuGroup`
Repräsentiert eine Gruppe von Menü-Einträgen.

**Attribute:**
- `title` (str): Titel der Menü-Gruppe
- `items` (List[MenuItem]): Liste von MenuItem-Objekten
- `collapsible` (bool): Ob die Gruppe kollabierbar ist
- `collapsed` (bool): Initial-Zustand (nur wenn collapsible=True)

#### `ShadcnSidebar`
Hauptklasse für Sidebar-Rendering.

**Methoden:**

##### `__init__(theme_manager: Optional[Any] = None)`
Initialisiert die Sidebar.

**Parameter:**
- `theme_manager`: Optional ThemeManager für Token-Zugriff

##### `inject_sidebar_css() -> None`
Injiziert shadcn/ui CSS für Sidebar.

##### `render_menu_item(item: MenuItem, group_key: str = "") -> bool`
Rendert einen einzelnen Menü-Eintrag.

**Parameter:**
- `item`: MenuItem-Objekt
- `group_key`: Schlüssel der Menü-Gruppe

**Returns:**
- `bool`: True wenn der Eintrag geklickt wurde

##### `render_menu_group(group: MenuGroup, group_index: int = 0) -> Optional[str]`
Rendert eine Menü-Gruppe.

**Parameter:**
- `group`: MenuGroup-Objekt
- `group_index`: Index der Gruppe

**Returns:**
- `Optional[str]`: Key des geklickten Menü-Eintrags oder None

##### `render(menu_groups: List[MenuGroup], show_dividers: bool = True, footer_content: Optional[Callable] = None) -> Optional[str]`
Rendert die komplette Sidebar.

**Parameter:**
- `menu_groups`: Liste von MenuGroup-Objekten
- `show_dividers`: Ob Trennlinien zwischen Gruppen angezeigt werden
- `footer_content`: Optional Callback für Footer-Content

**Returns:**
- `Optional[str]`: Key des geklickten Menü-Eintrags oder None

## Design-Tokens

Die Sidebar verwendet folgende Design-Tokens vom ThemeManager:

### Farben
- `colors.background`: Hintergrundfarbe der Sidebar
- `colors.foreground`: Textfarbe
- `colors.border`: Border-Farbe
- `colors.muted_foreground`: Farbe für Gruppen-Titel
- `colors.accent`: Hover-Hintergrundfarbe
- `colors.accent_foreground`: Hover-Textfarbe
- `colors.primary`: Aktiver Menü-Eintrag Hintergrund
- `colors.primary_foreground`: Aktiver Menü-Eintrag Text

### Typografie
- `typography.font_family`: Schriftart
- `typography.font_size_xs`: Schriftgröße für Gruppen-Titel
- `typography.font_size_sm`: Schriftgröße für Menü-Einträge
- `typography.font_weight_medium`: Font-Weight für Menü-Einträge
- `typography.font_weight_semibold`: Font-Weight für aktive Einträge

### Spacing
- `spacing.spacing_1` bis `spacing.spacing_4`: Abstände

### Borders
- `borders.border_width`: Border-Breite
- `borders.border_radius_md`: Border-Radius für Menü-Einträge

### Animations
- `animations.transition_base`: Transition-Timing

## CSS-Klassen

### `.shadcn-menu-group-title`
Styling für Gruppen-Titel.

### `.shadcn-menu-item`
Basis-Styling für Menü-Einträge.

**Modifiers:**
- `.active`: Aktiver Menü-Eintrag
- `.disabled`: Deaktivierter Menü-Eintrag

### `.shadcn-menu-item-icon`
Container für Icons.

### `.shadcn-menu-item-label`
Container für Label-Text.

### `.shadcn-group-header`
Header für kollabierbare Gruppen.

### `.shadcn-collapse-icon`
Icon für Kollabier-Funktion.

**Modifiers:**
- `.collapsed`: Kollabierter Zustand

### `.shadcn-sidebar-divider`
Trennlinie zwischen Gruppen.

### `.shadcn-sidebar-footer`
Footer-Bereich der Sidebar.

## State Management

Die Sidebar verwendet `st.session_state` für:

### `active_menu_item`
Speichert den Key des aktuell aktiven Menü-Eintrags.

**Typ:** `Optional[str]`

### `collapsed_groups`
Set von Keys für kollabierte Gruppen.

**Typ:** `Set[str]`

## Beispiele

### Basis-Verwendung

```python
from utils.shadcn_sidebar import ShadcnSidebar, MenuGroup, MenuItem

sidebar = ShadcnSidebar()

groups = [
    MenuGroup(
        title="Navigation",
        items=[
            MenuItem(label="Home", icon="🏠", key="home"),
            MenuItem(label="About", icon="ℹ️", key="about"),
        ]
    )
]

selected = sidebar.render(groups)
if selected:
    st.write(f"Ausgewählt: {selected}")
```

### Mit Callbacks

```python
def on_dashboard_click():
    st.success("Dashboard wurde geöffnet!")

groups = [
    MenuGroup(
        title="Hauptmenü",
        items=[
            MenuItem(
                label="Dashboard",
                icon="📊",
                key="dashboard",
                callback=on_dashboard_click
            ),
        ]
    )
]

sidebar.render(groups)
```

### Kollabierbare Gruppen

```python
groups = [
    MenuGroup(
        title="Erweitert",
        items=[
            MenuItem(label="Option 1", key="opt1"),
            MenuItem(label="Option 2", key="opt2"),
        ],
        collapsible=True,
        collapsed=True  # Initial kollabiert
    )
]

sidebar.render(groups)
```

### Mit Footer

```python
def render_footer():
    st.markdown("---")
    st.caption("Version 1.0.0")
    st.caption("© 2024 Firma")

sidebar.render(groups, footer_content=render_footer)
```

### Deaktivierte Einträge

```python
groups = [
    MenuGroup(
        title="Features",
        items=[
            MenuItem(label="Verfügbar", icon="✅", key="available"),
            MenuItem(
                label="Bald verfügbar",
                icon="🔒",
                key="coming_soon",
                disabled=True
            ),
        ]
    )
]

sidebar.render(groups)
```

### Convenience-Funktion

```python
from utils.shadcn_sidebar import create_sidebar_menu, MenuGroup, MenuItem

groups = [
    MenuGroup(
        title="Navigation",
        items=[
            MenuItem("Home", icon="🏠", key="home"),
            MenuItem("About", icon="ℹ️", key="about"),
        ]
    )
]

selected = create_sidebar_menu(groups)
```

### Vordefinierte Menüs

```python
from utils.shadcn_sidebar import (
    ShadcnSidebar,
    get_default_menu,
    get_solar_calculator_menu
)

sidebar = ShadcnSidebar()

# Standard-Menü
selected = sidebar.render(get_default_menu())

# Oder Solar-Rechner-Menü
selected = sidebar.render(get_solar_calculator_menu())
```

## Integration mit ThemeManager

```python
from theming import ThemeManager
from utils.shadcn_sidebar import ShadcnSidebar, MenuGroup, MenuItem

# Initialisiere ThemeManager
theme_manager = ThemeManager()
theme_manager.set_theme('shadcn-default')

# Erstelle Sidebar mit Theme
sidebar = ShadcnSidebar(theme_manager)

groups = [
    MenuGroup(
        title="Menü",
        items=[
            MenuItem("Item 1", key="item1"),
            MenuItem("Item 2", key="item2"),
        ]
    )
]

sidebar.render(groups)
```

## Anpassung

### Custom Icons

Icons können als Emoji oder HTML verwendet werden:

```python
# Emoji
MenuItem(label="Home", icon="🏠", key="home")

# HTML
MenuItem(
    label="Settings",
    icon='<svg>...</svg>',
    key="settings"
)
```

### Custom Styling

Zusätzliches CSS kann über `st.markdown()` injiziert werden:

```python
st.markdown("""
<style>
.shadcn-menu-item {
    /* Custom styles */
}
</style>
""", unsafe_allow_html=True)
```

## Performance

### Best Practices

1. **Menü-Konfiguration cachen:**
   ```python
   @st.cache_data
   def get_menu_config():
       return [MenuGroup(...)]
   ```

2. **Callbacks sparsam verwenden:**
   - Callbacks sollten leichtgewichtig sein
   - Schwere Operationen in separate Funktionen auslagern

3. **Session State effizient nutzen:**
   - Nur notwendige Daten speichern
   - Regelmäßig aufräumen

## Troubleshooting

### Problem: Menü-Einträge reagieren nicht

**Lösung:** Stelle sicher, dass jeder MenuItem einen eindeutigen `key` hat.

### Problem: Styling wird nicht angewendet

**Lösung:** Prüfe ob `inject_sidebar_css()` aufgerufen wird (automatisch in `render()`).

### Problem: ThemeManager nicht gefunden

**Lösung:** Stelle sicher, dass ThemeManager in `st.session_state` gespeichert ist:
```python
st.session_state.theme_manager = ThemeManager()
```

### Problem: Aktiver Zustand geht verloren

**Lösung:** `active_menu_item` wird in `st.session_state` gespeichert und bleibt erhalten.

## API-Änderungen

### Version 1.0.0
- Initial Release
- Basis-Funktionalität
- Theme-Integration
- Kollabierbare Gruppen

## Siehe auch

- [Theme System Reference](../theming/THEME_MANAGER_REFERENCE.md)
- [CSS Generator Reference](../theming/CSS_GENERATOR_REFERENCE.md)
- [Component Base Reference](../components/SHADCN_BASE_REFERENCE.md)
