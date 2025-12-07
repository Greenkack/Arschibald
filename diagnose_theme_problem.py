"""
 THEME SYSTEM DIAGNOSE
Dieses Script zeigt dir GENAU, warum das Theme System nicht sichtbar ist.
"""

import streamlit as st
import sys
from pathlib import Path

st.set_page_config(page_title=" Theme System Diagnose", layout="wide")

st.title(" Theme System Diagnose")
st.markdown("---")

# Test 1: Python Path
st.header("1⃣ Python Environment")
st.code(f"Python: {sys.version}")
st.code(f"Working Dir: {Path.cwd()}")

# Test 2: Imports
st.header("2⃣ Import Tests")

try:
    from theming.theme_manager import ThemeManager
    st.success(" ThemeManager kann importiert werden")
    
    # Erstelle Theme Manager
    tm = ThemeManager()
    themes = list(tm.themes.keys())
    st.success(f" {len(themes)} Themes gefunden: {', '.join(themes)}")
    
    # Zeige aktuelles Theme
    current = tm.get_current_theme()
    st.info(f" Aktuelles Theme: {current}")
    
except ImportError as e:
    st.error(f" Import-Fehler: {e}")
    st.stop()
except Exception as e:
    st.error(f" Fehler beim Erstellen: {e}")
    st.stop()

# Test 3: Session State
st.header("3⃣ Session State Check")

if 'enable_shadcn_ui' in st.session_state:
    flag_value = st.session_state.enable_shadcn_ui
    if flag_value:
        st.success(f" enable_shadcn_ui = {flag_value}")
    else:
        st.error(f" enable_shadcn_ui = {flag_value}")
else:
    st.warning(" enable_shadcn_ui nicht in session_state")
    st.info("Setze jetzt auf True...")
    st.session_state.enable_shadcn_ui = True

# Test 4: Theme Anwendung
st.header("4⃣ Theme Anwendung Test")

col1, col2 = st.columns(2)

with col1:
    selected_theme = st.selectbox(
        "Wähle ein Theme:",
        themes,
        key="theme_selector"
    )

with col2:
    if st.button(" Theme JETZT anwenden", type="primary"):
        try:
            tm.set_theme(selected_theme)
            css = tm.generate_css()
            st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
            st.success(f" Theme '{selected_theme}' wurde angewendet!")
            st.balloons()
        except Exception as e:
            st.error(f" Fehler beim Anwenden: {e}")

# Test 5: CSS Vorschau
st.header("5⃣ CSS Vorschau")

if st.checkbox("Zeige generierten CSS Code"):
    try:
        css = tm.generate_css()
        st.code(css[:500] + "...", language="css")
        st.info(f"CSS Länge: {len(css)} Zeichen")
    except Exception as e:
        st.error(f" Fehler: {e}")

# Test 6: Live Demo
st.header("6⃣ Live Demo")

st.markdown("### Wenn das Theme funktioniert, sollten diese Elemente gestylt sein:")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Metric Test", "42", "+10%")
    
with col2:
    st.button("Button Test")
    
with col3:
    st.selectbox("Select Test", ["Option 1", "Option 2"])

st.text_input("Input Test", placeholder="Tippe hier...")
st.slider("Slider Test", 0, 100, 50)

# Test 7: Datei-Check
st.header("7⃣ Datei-Struktur Check")

files_to_check = [
    "theming/theme_manager.py",
    "theming/theme_tokens.py",
    "theming/css_generator.py",
    "theming/themes/shadcn-default.json",
    "theming/themes/shadcn-dark.json",
    "gui.py"
]

for file_path in files_to_check:
    if Path(file_path).exists():
        st.success(f" {file_path}")
    else:
        st.error(f" {file_path} FEHLT!")

# Zusammenfassung
st.markdown("---")
st.header(" Zusammenfassung")

if 'enable_shadcn_ui' in st.session_state and st.session_state.enable_shadcn_ui:
    st.success(" Feature Flag ist aktiviert")
else:
    st.error(" Feature Flag ist NICHT aktiviert")

st.info("""
**Nächste Schritte:**
1. Wenn alle Tests  sind, funktioniert das Theme System
2. Klicke auf "Theme JETZT anwenden" um ein Theme zu aktivieren
3. Wenn es immer noch nicht in gui.py sichtbar ist, liegt das Problem in der Integration
""")
