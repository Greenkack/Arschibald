# shadcn/ui GUI Integration - Quick Reference

## Schnellstart

### Theme System aktivieren

```python
# In gui.py - automatisch beim App-Start
st.session_state.enable_shadcn_ui = True
```

### Theme wechseln

```python
# Theme-Manager holen
theme_manager = st.session_state.shadcn_theme_manager

# Theme setzen
theme_manager.set_theme('shadcn-dark')

# CSS neu injizieren
from gui import inject_shadcn_css
inject_shadcn_css()

# Rerun
st.rerun()
```

### Theme-Token abrufen

```python
theme_manager = st.session_state.shadcn_theme_manager

# Farben
primary = theme_manager.get_token('colors.primary')
background = theme_manager.get_token('colors.background')

# Typography
font = theme_manager.get_token('typography.font_family')
size = theme_manager.get_token('typography.font_size_base')

# Spacing
padding = theme_manager.get_token('spacing.spacing_4')
```

## Verfügbare Themes

| Theme Name | Display Name | Beschreibung |
|------------|--------------|--------------|
| `shadcn-default` | shadcn/ui Default | Helles Standard-Theme |
| `shadcn-dark` | shadcn/ui Dark | Dunkles Theme |
| `shadcn-ocean` | Ocean Blue | Blau-Töne |
| `shadcn-forest` | Forest Green | Grün-Töne |
| `shadcn-sunset` | Sunset Orange | Orange-Töne |

## Session State Variablen

| Variable | Typ | Beschreibung |
|----------|-----|--------------|
| `enable_shadcn_ui` | bool | Feature-Flag |
| `shadcn_theme_manager` | ThemeManager | Theme-Manager-Instanz |
| `shadcn_css_injected` | bool | CSS injiziert? |
| `shadcn_theme_changed` | bool | Theme gewechselt? |

## Datenbank-Einstellungen

| Setting Key | Typ | Standard | Beschreibung |
|-------------|-----|----------|--------------|
| `enable_shadcn_ui` | bool | True | Feature aktiviert? |
| `shadcn_active_theme` | str | 'shadcn-default' | Aktives Theme |

## Funktionen

### `initialize_shadcn_theme_system()`

Initialisiert das Theme System beim App-Start.

**Returns:** `bool` - True bei Erfolg

**Beispiel:**
```python
if initialize_shadcn_theme_system():
    print("Theme System initialisiert")
```

### `inject_shadcn_css()`

Injiziert CSS in die App.

**Beispiel:**
```python
inject_shadcn_css()
```

## Komponenten verwenden

### Card

```python
from components.card import Card

theme_manager = st.session_state.shadcn_theme_manager
card = Card(theme_manager)

card.render(
    title="Titel",
    content="Inhalt",
    variant="elevated"
)
```

### Alert

```python
from components.alert import Alert

alert = Alert(theme_manager)
alert.render(
    message="Nachricht",
    type="success"
)
```

### Badge

```python
from components.badge import Badge

badge = Badge(theme_manager)
badge.render(
    text="Neu",
    variant="primary"
)
```

## Sidebar Integration

```python
with st.sidebar:
    if st.session_state.get('enable_shadcn_ui', False):
        theme_manager = st.session_state.shadcn_theme_manager
        if theme_manager:
            from theming.theme_selector_ui import render_theme_selector
            render_theme_selector(theme_manager)
```

## Admin-Panel

```python
# Feature aktivieren/deaktivieren
enable = st.checkbox("shadcn/ui aktivieren", value=True)
st.session_state.enable_shadcn_ui = enable
save_admin_setting("enable_shadcn_ui", enable)

# Theme setzen
theme = st.selectbox("Theme", options=['shadcn-default', 'shadcn-dark'])
theme_manager.set_theme(theme)
save_admin_setting("shadcn_active_theme", theme)
```

## Troubleshooting

### Theme-Selector erscheint nicht
```python
# Prüfen
print(st.session_state.get('enable_shadcn_ui'))
print(SHADCN_THEME_AVAILABLE)
```

### CSS wird nicht angewendet
```python
# Neu injizieren
inject_shadcn_css()
st.rerun()
```

### Theme-Wechsel funktioniert nicht
```python
# Flag setzen
st.session_state.shadcn_theme_changed = True
st.rerun()
```

## Best Practices

✅ **DO:**
- Feature-Flag prüfen vor Verwendung
- Theme-Token verwenden statt hardcoded Werte
- Graceful Fallbacks implementieren
- Logging verwenden

❌ **DON'T:**
- CSS bei jedem Rerun injizieren
- Hardcoded Farben verwenden
- Theme-Manager direkt importieren (aus Session State holen)
- Feature ohne Fallback verwenden

## Code-Snippets

### Custom-Komponente mit Theme

```python
def my_component():
    theme_manager = st.session_state.get('shadcn_theme_manager')
    
    if theme_manager:
        primary = theme_manager.get_token('colors.primary')
        st.markdown(f'<div style="color: {primary}">Themed</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div>Fallback</div>', unsafe_allow_html=True)
```

### Theme-Wechsel mit Callback

```python
def on_theme_change(theme_name):
    theme_manager = st.session_state.shadcn_theme_manager
    theme_manager.set_theme(theme_name)
    inject_shadcn_css()
    save_admin_setting("shadcn_active_theme", theme_name)
    st.rerun()

st.selectbox(
    "Theme",
    options=['shadcn-default', 'shadcn-dark'],
    on_change=on_theme_change
)
```

### Feature-Flag mit Persistierung

```python
def toggle_shadcn_ui(enabled):
    st.session_state.enable_shadcn_ui = enabled
    save_admin_setting("enable_shadcn_ui", enabled)
    
    if enabled:
        initialize_shadcn_theme_system()
    
    st.rerun()

st.toggle(
    "shadcn/ui aktivieren",
    value=st.session_state.get('enable_shadcn_ui', True),
    on_change=toggle_shadcn_ui
)
```

## Links

- [Vollständige Dokumentation](./SHADCN_GUI_INTEGRATION.md)
- [Theme System](./THEME_SYSTEM_REFERENCE.md)
- [Component Library](./COMPONENT_LIBRARY.md)
