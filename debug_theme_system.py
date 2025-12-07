"""
Debug-Script um zu sehen was im Session State ist
"""

import streamlit as st

st.title(" Theme System Debug")

st.markdown("---")

# Zeige alle Session State Keys
st.subheader("Session State Keys")
all_keys = list(st.session_state.keys())
shadcn_keys = [k for k in all_keys if 'shadcn' in k.lower() or 'theme' in k.lower()]

if shadcn_keys:
    st.success(f" {len(shadcn_keys)} Theme-bezogene Keys gefunden:")
    for key in shadcn_keys:
        value = st.session_state[key]
        st.write(f"- **{key}**: {type(value).__name__}")
        if key == 'enable_shadcn_ui':
            if value:
                st.success(f"   {key} = {value}")
            else:
                st.error(f"   {key} = {value} (DEAKTIVIERT!)")
else:
    st.warning(" Keine Theme-bezogenen Keys gefunden!")

st.markdown("---")

# Prüfe Imports
st.subheader("Import-Status")
try:
    from theming.theme_manager import ThemeManager
    st.success(" ThemeManager importierbar")
except ImportError as e:
    st.error(f" ThemeManager nicht importierbar: {e}")

try:
    from theming.theme_logger import get_theme_logger
    st.success(" ThemeLogger importierbar")
except ImportError as e:
    st.error(f" ThemeLogger nicht importierbar: {e}")

try:
    from theming.monitoring_dashboard import render_compact_monitoring
    st.success(" Monitoring Dashboard importierbar")
except ImportError as e:
    st.error(f" Monitoring Dashboard nicht importierbar: {e}")

st.markdown("---")

# Zeige alle Keys (optional)
with st.expander("Alle Session State Keys anzeigen"):
    st.json({k: str(type(st.session_state[k]).__name__) for k in sorted(all_keys)})

st.markdown("---")

# Force Enable Button
st.subheader("Force Enable")
if st.button(" Theme-System JETZT aktivieren"):
    st.session_state.enable_shadcn_ui = True
    st.success(" enable_shadcn_ui auf True gesetzt!")
    st.info("Bitte App neu laden (F5) damit die Änderung wirksam wird.")
    st.rerun()
