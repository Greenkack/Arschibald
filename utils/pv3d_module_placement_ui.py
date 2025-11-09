"""
PV-Modul Platzierungs-UI Komponente

Dieses Modul stellt UI-Komponenten für die Modul-Belegung bereit.
"""

import streamlit as st
from typing import Dict, Any


def render_module_placement_panel(
    module_quantity: int,
    roof_area: float,
    current_placed: int = 0
) -> Dict[str, Any]:
    """
    Rendert das Modul-Belegungs-Panel mit Statistiken und Steuerungs-Buttons.

    Args:
        module_quantity: Gewünschte Anzahl Module
        roof_area: Verfügbare Dachfläche in m²
        current_placed: Aktuell platzierte Module

    Returns:
        Dictionary mit Button-States:
        - auto_place_clicked: bool
        - manual_add_clicked: bool
        - remove_selected_clicked: bool
        - reset_all_clicked: bool
        - show_grid: bool
        - show_numbers: bool
    
    Requirements:
        - 11.1: Validate inputs
        - 11.2: Error handling
        - 11.4: Meaningful error messages
    """
    # Initialisiere Rückgabe-Dictionary
    actions = {
        "auto_place_clicked": False,
        "manual_add_clicked": False,
        "remove_selected_clicked": False,
        "reset_all_clicked": False,
        "show_grid": False,
        "show_numbers": False
    }
    
    # Requirement 11.1: Validate inputs
    try:
        # Validate module_quantity
        if not isinstance(module_quantity, (int, float)):
            st.error(
                f"❌ Fehler: Ungültiger Typ für Modulanzahl "
                f"(erwartet: Zahl, erhalten: {type(module_quantity).__name__})"
            )
            return actions
        
        module_quantity = int(module_quantity)
        if module_quantity < 0:
            st.warning(
                f"⚠️ Warnung: Negative Modulanzahl ({module_quantity}) "
                "wird auf 0 gesetzt"
            )
            module_quantity = 0
        
        # Validate roof_area
        if not isinstance(roof_area, (int, float)):
            st.error(
                f"❌ Fehler: Ungültiger Typ für Dachfläche "
                f"(erwartet: Zahl, erhalten: {type(roof_area).__name__})"
            )
            return actions
        
        if roof_area < 0:
            st.warning(
                f"⚠️ Warnung: Negative Dachfläche ({roof_area:.2f}m²) "
                "wird auf 0 gesetzt"
            )
            roof_area = 0
        
        # Validate current_placed
        if not isinstance(current_placed, (int, float)):
            st.warning(
                f"⚠️ Warnung: Ungültiger Typ für platzierte Module, "
                "wird auf 0 gesetzt"
            )
            current_placed = 0
        
        current_placed = int(current_placed)
        if current_placed < 0:
            current_placed = 0
            
    except Exception as validation_error:
        # Requirement 11.2, 11.4: Error handling with meaningful messages
        st.error(
            f"❌ Fehler bei der Eingabe-Validierung: "
            f"{str(validation_error)}"
        )
        return actions

    # Requirement 11.3: Try-Catch around UI rendering
    try:
        # Erstelle Expander-Panel
        with st.expander("🔲 Modul-Belegung", expanded=True):

            # Berechne Statistiken
            if module_quantity > 0:
                coverage_percent = (current_placed / module_quantity * 100)
            else:
                coverage_percent = 0
            coverage_percent = min(coverage_percent, 100)  # Maximal 100%

        # Statistik-Anzeige in 3 Spalten
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                label="Gewünscht",
                value=f"{module_quantity}",
                help="Anzahl der gewünschten Module"
            )

        with col2:
            delta_val = None
            if current_placed != module_quantity:
                delta_val = f"{current_placed - module_quantity}"
            st.metric(
                label="Platziert",
                value=f"{current_placed}",
                delta=delta_val,
                help="Anzahl der aktuell platzierten Module"
            )

        with col3:
            st.metric(
                label="Abdeckung",
                value=f"{coverage_percent:.1f}%",
                help="Prozentsatz der platzierten Module"
            )

        # Fortschrittsbalken
        progress_text = (
            f"Belegungsfortschritt: {current_placed} von "
            f"{module_quantity} Modulen"
        )
        st.progress(coverage_percent / 100, text=progress_text)

        st.divider()

        # Haupt-Buttons in 2 Spalten
        btn_col1, btn_col2 = st.columns(2)

        with btn_col1:
            # Primary Button: Automatisch belegen
            auto_help = "Platziert Module automatisch auf der Dachfläche"
            if st.button(
                "🎯 Automatisch belegen",
                type="primary",
                use_container_width=True,
                help=auto_help
            ):
                # Setze Trigger im Session State
                st.session_state["trigger_auto_placement"] = True
                actions["auto_place_clicked"] = True

        with btn_col2:
            # Reset Button
            if st.button(
                "🔄 Alle zurücksetzen",
                use_container_width=True,
                help="Entfernt alle platzierten Module"
            ):
                actions["reset_all_clicked"] = True

        # Optionale manuelle Steuerungs-Buttons
        # (für zukünftige Erweiterung)
        # Diese werden in späteren Tasks implementiert
        st.divider()

        manual_col1, manual_col2 = st.columns(2)

        with manual_col1:
            if st.button(
                "➕ Modul hinzufügen",
                use_container_width=True,
                disabled=True,
                help="Manuelle Platzierung (in Entwicklung)"
            ):
                actions["manual_add_clicked"] = True

        with manual_col2:
            if st.button(
                "➖ Ausgewählte entfernen",
                use_container_width=True,
                disabled=True,
                help="Entfernt ausgewählte Module (in Entwicklung)"
            ):
                actions["remove_selected_clicked"] = True

        st.divider()

        # Visualisierungs-Optionen
        st.subheader("Visualisierungs-Optionen")

        opt_col1, opt_col2 = st.columns(2)

        with opt_col1:
            show_grid = st.checkbox(
                "Raster anzeigen",
                value=st.session_state.get("show_placement_grid", False),
                help="Zeigt ein Raster zur Orientierung an",
                disabled=True  # Wird in späteren Tasks implementiert
            )
            actions["show_grid"] = show_grid
            if show_grid != st.session_state.get(
                "show_placement_grid", False
            ):
                st.session_state["show_placement_grid"] = show_grid

        with opt_col2:
            show_numbers = st.checkbox(
                "Modul-Nummern anzeigen",
                value=st.session_state.get("show_module_numbers", False),
                help="Zeigt Nummern auf den Modulen an",
                disabled=True  # Wird in späteren Tasks implementiert
            )
            actions["show_numbers"] = show_numbers
            if show_numbers != st.session_state.get(
                "show_module_numbers", False
            ):
                st.session_state["show_module_numbers"] = show_numbers

        # Info-Box mit zusätzlichen Informationen
        if current_placed > 0:
            info_text = (
                f"ℹ️ **Platzierungs-Info:**\n\n"
                f"- Dachfläche: {roof_area:.2f} m²\n"
                f"- Module platziert: {current_placed}\n"
                f"- Belegungsgrad: {coverage_percent:.1f}%"
            )
            st.info(info_text)
        else:
            tip_text = (
                "💡 **Tipp:** Klicken Sie auf 'Automatisch belegen' "
                "um Module optimal auf der Dachfläche zu platzieren."
            )
            st.info(tip_text)
    
    except Exception as render_error:
        # Requirement 11.2, 11.4: Error handling with meaningful messages
        st.error(
            f"❌ Fehler beim Rendern des Modul-Belegungs-Panels: "
            f"{str(render_error)}"
        )
        print(f"UI Rendering Error: {render_error}")
        import traceback
        traceback.print_exc()

    return actions
