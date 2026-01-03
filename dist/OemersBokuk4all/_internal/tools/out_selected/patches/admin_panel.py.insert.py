# === AUTO-GENERATED INSERT PATCH ===
# target_module: admin_panel.py

# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---
import traceback

import streamlit as st


# --- DEF BLOCK START: func render_logo_management_tab ---
def render_logo_management_tab():
    """Rendert den Logo-Management-Tab im Admin-Panel"""
    try:
        from admin_logo_management_ui import render_logo_management_ui
        render_logo_management_ui()
    except ImportError as e:
        st.error(f"Logo-Management UI konnte nicht geladen werden: {e}")
        st.info("Stellen Sie sicher, dass admin_logo_management_ui.py verfügbar ist.")
    except Exception as e:
        st.error(f"Fehler beim Rendern der Logo-Management UI: {e}")
        st.text(traceback.format_exc())
# --- DEF BLOCK END ---
