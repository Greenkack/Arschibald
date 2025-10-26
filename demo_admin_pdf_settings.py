"""
Demo für admin_pdf_settings_ui.py

Zeigt die Admin-Settings-UI in einer Streamlit-App
"""

import streamlit as st

from admin_pdf_settings_ui import render_pdf_settings_ui

# Set page config
st.set_page_config(
    page_title="PDF & Design Einstellungen Demo",
    page_icon="⚙️",
    layout="wide"
)

# Render the UI
render_pdf_settings_ui()

# Add footer
st.markdown("---")
st.markdown("""
**Demo-Modus**

Diese Demo zeigt die Grundstruktur der Admin-Settings-UI.
Die einzelnen Funktionen werden in den folgenden Tasks implementiert:
- Task 9: PDF-Design-Einstellungen
- Task 10: Diagramm-Farbeinstellungen
- Task 11: UI-Theme-System
- Task 12: PDF-Template-Verwaltung
- Task 13: Layout-Optionen
""")
