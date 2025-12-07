"""
Demo: shadcn/ui Integration in gui.py

Dieses Demo zeigt wie das shadcn/ui Theme System in die Haupt-App integriert wurde.
"""

import streamlit as st

# Simuliere die Integration
st.set_page_config(page_title="shadcn/ui Integration Demo", layout="wide")

st.title(" shadcn/ui Integration in gui.py")

st.markdown("""
## Übersicht

Das shadcn/ui Theme System wurde erfolgreich in die Haupt-App (gui.py) integriert.

### Implementierte Features

#### 1.  ThemeManager Initialisierung beim App-Start
- ThemeManager wird beim ersten Laden der App erstellt
- Gespeichertes Theme wird aus der Datenbank geladen
- Fallback auf Standard-Theme wenn kein Theme gespeichert ist

#### 2.  Globale CSS-Injection
- CSS wird beim App-Start automatisch injiziert
- CSS wird bei Theme-Wechsel neu generiert und injiziert
- Verwendet `st.markdown()` mit `unsafe_allow_html=True`

#### 3.  Theme-Selector in Sidebar
- Theme-Selector wird in der Sidebar unter "DESIGN" angezeigt
- Nur sichtbar wenn Feature aktiviert ist
- Live-Vorschau der Theme-Farben
- Speichert Theme-Auswahl in Datenbank

#### 4.  Feature-Flag (enable_shadcn_ui)
- Feature kann über Session State aktiviert/deaktiviert werden
- Einstellung wird in Datenbank gespeichert
- Standard: aktiviert (True)

#### 5.  Rückwärtskompatibilität
- App funktioniert auch ohne shadcn/ui Module
- Graceful Fallback bei Import-Fehlern
- Bestehende Funktionalität bleibt erhalten
- Kein Breaking Change für bestehenden Code

### Code-Struktur

```python
# Import mit Fallback
try:
    from theming.theme_manager import ThemeManager
    from theming.theme_selector_ui import render_theme_selector
    SHADCN_THEME_AVAILABLE = True
except ImportError:
    SHADCN_THEME_AVAILABLE = False

# Initialisierung beim App-Start
def initialize_shadcn_theme_system():
    if not SHADCN_THEME_AVAILABLE:
        return False
    
    # ThemeManager erstellen
    theme_manager_instance = ThemeManager()
    
    # Gespeichertes Theme laden
    saved_theme = database_module.load_admin_setting("shadcn_active_theme", None)
    
    # Theme setzen
    theme_manager_instance.set_theme(saved_theme or 'shadcn-default')
    
    # Im Session State speichern
    st.session_state.shadcn_theme_manager = theme_manager_instance
    
    # CSS injizieren
    css = theme_manager_instance.generate_css()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    
    return True

# Feature-Flag in Session State
if 'enable_shadcn_ui' not in st.session_state:
    enable_shadcn = database_module.load_admin_setting("enable_shadcn_ui", True)
    st.session_state.enable_shadcn_ui = enable_shadcn

# Initialisierung wenn Feature aktiviert
if st.session_state.enable_shadcn_ui and SHADCN_THEME_AVAILABLE:
    initialize_shadcn_theme_system()

# Theme-Selector in Sidebar
with st.sidebar:
    if st.session_state.get('enable_shadcn_ui', False) and SHADCN_THEME_AVAILABLE:
        st.markdown("---")
        st.markdown("### DESIGN")
        
        theme_manager_instance = st.session_state.get('shadcn_theme_manager')
        if theme_manager_instance:
            render_theme_selector(theme_manager_instance)
```

### Integration-Punkte in gui.py

1. **Import-Sektion** (Zeile ~130)
   - Import von ThemeManager und render_theme_selector
   - Fallback-Handling bei Import-Fehlern

2. **Hilfsfunktionen** (Zeile ~350)
   - `initialize_shadcn_theme_system()`: Initialisiert Theme System
   - `inject_shadcn_css()`: Injiziert CSS bei Theme-Wechsel

3. **Session State Init** (Zeile ~1650)
   - Feature-Flag `enable_shadcn_ui` initialisieren
   - Theme System initialisieren wenn aktiviert

4. **Sidebar** (Zeile ~1900)
   - Theme-Selector unter "DESIGN" Sektion
   - Theme-Wechsel-Handling
   - Datenbank-Persistierung

### Verwendung

#### Theme-Wechsel programmatisch
```python
# Theme wechseln
theme_manager = st.session_state.shadcn_theme_manager
theme_manager.set_theme('shadcn-dark')

# CSS neu injizieren
inject_shadcn_css()

# Rerun für Änderungen
st.rerun()
```

#### Feature aktivieren/deaktivieren
```python
# Feature deaktivieren
st.session_state.enable_shadcn_ui = False

# In Datenbank speichern
database_module.save_admin_setting("enable_shadcn_ui", False)

# Rerun
st.rerun()
```

### Testing

Teste die Integration mit:
```bash
streamlit run gui.py
```

Prüfe:
-  Theme-Selector erscheint in Sidebar
-  Theme-Wechsel funktioniert
-  CSS wird korrekt angewendet
-  Theme-Auswahl wird gespeichert
-  App funktioniert auch ohne shadcn/ui Module
```
""")

# Zeige aktuellen Status
st.markdown("---")
st.subheader(" Aktueller Status")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="shadcn/ui verfügbar",
        value=" Ja" if st.session_state.get('shadcn_theme_manager') else " Nein"
    )

with col2:
    st.metric(
        label="Feature aktiviert",
        value=" Ja" if st.session_state.get('enable_shadcn_ui', False) else " Nein"
    )

with col3:
    theme_manager = st.session_state.get('shadcn_theme_manager')
    current_theme = theme_manager.current_theme.display_name if theme_manager else "N/A"
    st.metric(
        label="Aktuelles Theme",
        value=current_theme
    )

# Zeige verfügbare Themes
if theme_manager:
    st.markdown("---")
    st.subheader(" Verfügbare Themes")
    
    themes = theme_manager.themes
    cols = st.columns(len(themes))
    
    for i, (theme_name, theme) in enumerate(themes.items()):
        with cols[i]:
            st.markdown(f"**{theme.display_name}**")
            st.color_picker(
                "Primary",
                value=theme.colors.primary,
                disabled=True,
                key=f"color_{theme_name}"
            )

# Zeige Code-Beispiele
st.markdown("---")
st.subheader(" Code-Beispiele")

with st.expander("Theme programmatisch wechseln"):
    st.code("""
# Theme wechseln
theme_manager = st.session_state.shadcn_theme_manager
theme_manager.set_theme('shadcn-ocean')

# CSS neu injizieren
from gui import inject_shadcn_css
inject_shadcn_css()

# Rerun
st.rerun()
""", language="python")

with st.expander("Feature-Flag setzen"):
    st.code("""
# Feature aktivieren
st.session_state.enable_shadcn_ui = True

# In Datenbank speichern
from database import save_admin_setting
save_admin_setting("enable_shadcn_ui", True)

# Rerun
st.rerun()
""", language="python")

with st.expander("Theme-Token abrufen"):
    st.code("""
# Theme-Manager holen
theme_manager = st.session_state.shadcn_theme_manager

# Token abrufen
primary_color = theme_manager.get_token('colors.primary')
font_family = theme_manager.get_token('typography.font_family')
spacing = theme_manager.get_token('spacing.spacing_4')

# Verwenden
st.markdown(f'<div style="color: {primary_color}">Text</div>', unsafe_allow_html=True)
""", language="python")

st.markdown("---")
st.success(" Integration abgeschlossen! Das shadcn/ui Theme System ist jetzt in gui.py integriert.")
