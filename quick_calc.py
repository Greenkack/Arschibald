# quick_calc.py
# Modul für den Schnellberechnung Tab (B)


from collections.abc import Iterable

import streamlit as st

from ui_state_manager import keep_session_state_alive, register_persistent_keys

# Importiere benötigte Funktionen/Daten (falls Schnellberechnung darauf
# zugreift)
try:
    # Beispiel: Wenn Schnellberechnung Produktpreise nachschlagen soll
    # from product_db import lookup_product_price
    # Beispiel: Wenn Schnellberechnung Admin Settings braucht
    # from database import load_admin_setting
    quick_calc_dependencies_available = True
except ImportError as e:
    st.error(
        f"FEHLER: Benötigte Module für Schnellberechnung konnten nicht geladen werden: {e}")
    quick_calc_dependencies_available = False
    # Definiere Dummy Funktionen, falls Import fehlschlägt
    # def lookup_product_price(model_name): return 0.0


# KORREKTUR: render_quick_calc Funktion mit korrekter Signatur, die
# **kwargs akzeptiert
# KORREKTUR: **kwargs hinzugefügt
def render_quick_calc(texts: dict[str, str], **kwargs):
    """
    Rendert den Schnellberechnung Tab (B) der Streamlit Anwendung.
    Ermöglicht einfache, schnelle Kalkulationen.

    Args:
        texts: Dictionary mit den lokalisierten Texten.
        **kwargs: Zusätzliche Keyword-Argumente, z.B. 'module_name' von gui.py.
    """
    # Der Header wird in gui.py gesetzt, aber hier kann der Modulname aus
    # kwargs geholt werden, falls nötig
    module_name = kwargs.get(
        'module_name',
        texts.get(
            "menu_item_quick_calc",
            "A.G.E.N.T."))

    # --- Hier kommt die Logik für die Schnellberechnung hin ---
    # st.write(f"Willkommen im {module_name} Bereich.") # Beispiel Nutzung des
    # übergebenen Namens

    _stabilize_navigation_state()

    st.info(
        texts.get(
            "quick_calc_info",
            "Hier wird der A.G.E.N.T. demnächst eigenständig zahlreiche Aufgaben übernehmen."))  # Neuer Text Schlüssel

    # Beispiel-Eingaben für Schnellberechnung (Platzhalter)
    # required_power_kwp = st.number_input(texts.get("quick_calc_power_input", "Gewünschte PV-Leistung (kWp)"), min_value=1.0, max_value=100.0, value=5.0, step=0.5)
    # estimated_consumption = st.number_input(texts.get("quick_calc_consumption_input", "Geschätzter Jahresverbrauch (kWh)"), min_value=1000, max_value=50000, value=4000, step=100)

    # TODO: Implementieren Sie hier die Schnellberechnungslogik
    # Sie kann vereinfachte Formeln oder Lookups nutzen, aber keine detaillierte Eingabe wie in Tab A.
    # Beispiel einer sehr simplen Schätzung:
    # estimated_cost = required_power_kwp * texts.get("quick_calc_euro_per_kwp", 1500) # Annahme: 1500€/kWp als Admin Setting oder Standard
    # estimated_production = required_power_kwp *
    # texts.get("quick_calc_kwh_per_kwp", 950) # Annahme: 950kWh/kWp als
    # Standard

    # if st.button(texts.get("quick_calc_calculate_button", "Berechnen")):
    #    st.subheader(texts.get("quick_calc_results_header", "Ergebnisse Schnellberechnung"))
    #    st.write(f"- {texts.get('quick_calc_estimated_cost', 'Geschätzte Kosten')}: {estimated_cost:.2f} €")
    #    st.write(f"- {texts.get('quick_calc_estimated_production', 'Geschätzte Jahresproduktion')}: {estimated_production:.2f} kWh")
    #    st.info(texts.get("quick_calc_details_note", "Detaillierte Berechnung und Wirtschaftlichkeitsanalyse finden Sie im Tab A."))

    # Entfernen Sie dies, wenn Sie die Logik implementieren


def _stabilize_navigation_state() -> None:
    """Sichert die Navigation-Session-Keys gegen unerwünschtes Zurücksetzen."""
    nav_keys: Iterable[str] = (
        "nav_lock_enabled",
        "selected_page_key_sui",
        "selected_page_key_prev",
        "last_rendered_page_key",
        "nav_event",
        "nav_history",
    )
    existing_keys = [key for key in nav_keys if key in st.session_state]
    if not existing_keys:
        return

    register_persistent_keys(existing_keys)
    keep_session_state_alive(existing_keys)
