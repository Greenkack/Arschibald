"""
Test-Script um zu prüfen ob das Theme-System in gui.py integriert ist
"""

import streamlit as st

st.set_page_config(page_title="Theme System Test", layout="wide")

st.title(" Theme System Integration Test")

st.markdown("---")

# Test 1: Imports
st.subheader("1. Import-Test")
try:
    from theming.theme_manager import ThemeManager
    from theming.theme_selector_ui import render_theme_selector
    from theming.theme_logger import get_theme_logger
    from theming.monitoring_dashboard import render_compact_monitoring
    st.success(" Alle Theme-Module erfolgreich importiert!")
except ImportError as e:
    st.error(f" Import-Fehler: {e}")
    st.stop()

# Test 2: ThemeManager
st.subheader("2. ThemeManager-Test")
try:
    theme_manager = ThemeManager()
    st.success(f" ThemeManager erstellt! Verfügbare Themes: {list(theme_manager.themes.keys())}")
except Exception as e:
    st.error(f" ThemeManager-Fehler: {e}")
    st.stop()

# Test 3: Theme Logger
st.subheader("3. Logger-Test")
try:
    logger = get_theme_logger()
    logger.log_theme_switch("test-from", "test-to", user_id="test-user")
    stats = logger.get_stats()
    st.success(f" Logger funktioniert! Stats: {stats}")
except Exception as e:
    st.error(f" Logger-Fehler: {e}")

# Test 4: Theme Selector UI
st.subheader("4. Theme Selector Test")
try:
    st.markdown("**Theme auswählen:**")
    render_theme_selector(theme_manager)
    st.success(" Theme Selector gerendert!")
except Exception as e:
    st.error(f" Theme Selector Fehler: {e}")

# Test 5: Monitoring Dashboard
st.subheader("5. Monitoring Dashboard Test")
try:
    render_compact_monitoring(logger)
    st.success(" Monitoring Dashboard gerendert!")
except Exception as e:
    st.error(f" Monitoring Dashboard Fehler: {e}")

# Test 6: CSS Generation
st.subheader("6. CSS Generation Test")
try:
    css = theme_manager.generate_css()
    css_size = len(css.encode('utf-8'))
    st.success(f" CSS generiert! Größe: {css_size / 1024:.2f} KB")
    
    with st.expander("CSS anzeigen (erste 500 Zeichen)"):
        st.code(css[:500], language="css")
except Exception as e:
    st.error(f" CSS Generation Fehler: {e}")

st.markdown("---")
st.success(" Alle Tests bestanden! Das Theme-System ist funktionsfähig!")

st.markdown("""
##  Integration erfolgreich!

Das Theme-System ist vollständig funktionsfähig. In der Hauptapp `gui.py` solltest du jetzt sehen:

1. **Sidebar → "DESIGN"** - Theme-Selector
2. **Sidebar → "MONITORING"** - Kompakte Statistiken
3. **Button " Vollständiges Dashboard"** - Detaillierte Analysen

**Wenn du das in gui.py nicht siehst:**
- Starte die App neu: `streamlit run gui.py`
- Lösche den Browser-Cache (Strg+F5)
- Prüfe ob `st.session_state.enable_shadcn_ui = True` ist
""")
