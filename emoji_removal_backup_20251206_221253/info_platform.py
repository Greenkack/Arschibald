# info_platform.py
# Modul für den Controlling Tab - Integration des Employee Controlling Systems

import streamlit as st
import logging
import traceback

logger = logging.getLogger(__name__)

# Dependencies für künftige Features
info_platform_dependencies_available = True


def render_info_platform(texts: dict[str, str] = None, **kwargs):
    """
    Rendert den Controlling Tab der Streamlit Anwendung.
    Zeigt das Employee Controlling System an.

    Args:
      texts: Dictionary mit den lokalisierten Texten (optional).
      **kwargs: Zusätzliche Keyword-Argumente, z.B. 'module_name' von gui.py.
    """
    # Try to import and render controlling UI dynamically
    try:
        from controlling_ui import render_controlling_page

        # Render the controlling page
        render_controlling_page()

    except ImportError as e:
        logger.error(f"Failed to import controlling_ui: {e}")
        st.error(
            "❌ Das Employee Controlling System konnte nicht "
            "geladen werden."
        )
        st.warning(
            "**Import-Fehler:** Das Controlling-Modul ist nicht "
            "verfügbar. Bitte stellen Sie sicher, dass alle "
            "erforderlichen Module installiert sind."
        )

        with st.expander("🔍 Technische Details"):
            st.code(f"ImportError: {str(e)}")
            st.code(traceback.format_exc())

        st.info(
            "**Mögliche Lösungen:**\n\n"
            "1. Prüfen Sie, ob `controlling_ui.py` existiert\n"
            "2. Installieren Sie Abhängigkeiten: "
            "`pip install -r requirements.txt`\n"
            "3. Initialisieren Sie die Datenbank: "
            "`python controlling/database.py`"
        )

    except Exception as e:
        logger.error(f"Error rendering controlling page: {e}")
        st.error(f"❌ Fehler beim Laden des Controlling-Systems: {str(e)}")

        with st.expander("🔍 Technische Details"):
            st.code(traceback.format_exc())

        st.info(
            "Bitte kontaktieren Sie den Administrator, wenn dieser Fehler "
            "weiterhin auftritt."
        )
