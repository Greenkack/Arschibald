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
        "show_numbers": False,
        "grid_spacing": 1.0,  # TASK 8.3: Grid spacing in meters
        "grid_opacity": 0.3,  # TASK 8.3: Grid transparency
        "selection_changed": False,  # TASK 4.1: Track selection changes
        "move_selected_clicked": False,  # TASK 4.2: Move button
        "move_offset_x": 0.0,  # TASK 4.2: X offset for move
        "move_offset_y": 0.0,  # TASK 4.2: Y offset for move
        "rotate_selected_clicked": False,  # TASK 4.2: Rotate button
        "rotation_angle": 0.0,  # TASK 4.2: Rotation angle
        "quick_move_clicked": False,  # TASK 4.3: Quick move button
        "quick_move_direction": None,  # TASK 4.3: Direction (left/right/up/down)
        "quick_move_step": 0.0,  # TASK 4.3: Step size
        "snap_to_grid": True  # TASK 4.3: Snap-to-grid enabled
    }
    
    # Requirement 11.1: Validate inputs
    try:
        # Validate module_quantity
        if not isinstance(module_quantity, (int, float)):
            st.error(
                f"Fehler: Ungültiger Typ für Modulanzahl "
                f"(erwartet: Zahl, erhalten: {type(module_quantity).__name__})"
            )
            return actions
        
        module_quantity = int(module_quantity)
        if module_quantity < 0:
            st.warning(
                f"Warnung: Negative Modulanzahl ({module_quantity}) "
                "wird auf 0 gesetzt"
            )
            module_quantity = 0
        
        # Validate roof_area
        if not isinstance(roof_area, (int, float)):
            st.error(
                f"Fehler: Ungültiger Typ für Dachfläche "
                f"(erwartet: Zahl, erhalten: {type(roof_area).__name__})"
            )
            return actions
        
        if roof_area < 0:
            st.warning(
                f"Warnung: Negative Dachfläche ({roof_area:.2f}m²) "
                "wird auf 0 gesetzt"
            )
            roof_area = 0
        
        # Validate current_placed
        if not isinstance(current_placed, (int, float)):
            st.warning(
                "Warnung: Ungültiger Typ für platzierte Module, "
                "wird auf 0 gesetzt"
            )
            current_placed = 0
        
        current_placed = int(current_placed)
        if current_placed < 0:
            current_placed = 0
            
    except Exception as validation_error:
        # Requirement 11.2, 11.4: Error handling with meaningful messages
        st.error(
            f"Fehler bei der Eingabe-Validierung: "
            f"{str(validation_error)}"
        )
        return actions

    # Requirement 11.3: Try-Catch around UI rendering
    try:
        # Erstelle Expander-Panel
        with st.expander("🔲 Modul-Belegung", expanded=True):

            # Berechne Statistiken
            if module_quantity > 0:
                if module_quantity != 0:
                    coverage_percent = (current_placed / module_quantity * 100)
                else:
                    coverage_percent = 0.0
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
        if 100 != 0:
            st.progress(coverage_percent / 100, text=progress_text)
        else:
            st.progress(coverage_percent / 100, text=progress_text)

        st.divider()

        # Haupt-Buttons in 2 Spalten
        btn_col1, btn_col2 = st.columns(2)

        with btn_col1:
            # Primary Button: Automatisch belegen
            auto_help = "Platziert Module automatisch auf der Dachfläche"
            if st.button(
                "Automatisch belegen",
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

        # TASK 4.2: Manuelle Steuerungs-Buttons
        # Requirement 4.2.1: Button "Modul hinzufügen"
        # Requirement 4.2.2: Button "Modul entfernen"
        # Requirement 4.2.3: Button "Modul verschieben"
        # Requirement 4.2.4: Button "Modul drehen"
        st.divider()

        manual_col1, manual_col2 = st.columns(2)

        with manual_col1:
            # Requirement 4.2.1: Manual add button
            manual_add_help = (
                "Fügt ein Modul an der nächsten verfügbaren Position hinzu"
            )
            if st.button(
                "➕ Modul hinzufügen",
                use_container_width=True,
                disabled=False,
                help=manual_add_help
            ):
                actions["manual_add_clicked"] = True

        with manual_col2:
            # Requirement 4.2.2: Remove selected button
            selected_count = len(
                st.session_state.get("selected_module_indices", [])
            )
            remove_help = (
                f"Entfernt {selected_count} ausgewählte Module" 
                if selected_count > 0 
                else "Keine Module ausgewählt"
            )
            remove_disabled = (selected_count == 0)
            
            if st.button(
                f"➖ Ausgewählte entfernen ({selected_count})",
                use_container_width=True,
                disabled=remove_disabled,
                help=remove_help
            ):
                actions["remove_selected_clicked"] = True
        
        # TASK 4.2: Erweiterte Manipulations-Buttons
        if selected_count > 0:
            st.markdown("**Ausgewählte Module bearbeiten:**")
            
            # Requirement 4.2.3: Move button
            st.markdown("**Verschieben:**")
            move_col1, move_col2, move_col3 = st.columns(3)
            
            with move_col1:
                offset_x = st.number_input(
                    "X-Offset (m)",
                    min_value=-10.0,
                    max_value=10.0,
                    value=0.0,
                    step=0.1,
                    format="%.2f",
                    help="Verschiebung in X-Richtung (positiv = rechts)"
                )
            
            with move_col2:
                offset_y = st.number_input(
                    "Y-Offset (m)",
                    min_value=-10.0,
                    max_value=10.0,
                    value=0.0,
                    step=0.1,
                    format="%.2f",
                    help="Verschiebung in Y-Richtung (positiv = hinten)"
                )
            
            with move_col3:
                if st.button(
                    "↔️ Verschieben",
                    use_container_width=True,
                    disabled=(abs(offset_x) < 0.01 and abs(offset_y) < 0.01),
                    help=f"Verschiebt {selected_count} Module um (Δx={offset_x:.2f}m, Δy={offset_y:.2f}m)"
                ):
                    actions["move_selected_clicked"] = True
                    actions["move_offset_x"] = offset_x
                    actions["move_offset_y"] = offset_y
            
            # Requirement 4.2.4: Rotate button
            st.markdown("**Drehen:**")
            rotate_col1, rotate_col2 = st.columns(2)
            
            with rotate_col1:
                rotation_angle = st.number_input(
                    "Rotationswinkel (°)",
                    min_value=-180.0,
                    max_value=180.0,
                    value=0.0,
                    step=15.0,
                    format="%.1f",
                    help="Rotationswinkel (positiv = gegen Uhrzeigersinn)"
                )
            
            with rotate_col2:
                if st.button(
                    "🔄 Drehen",
                    use_container_width=True,
                    disabled=(abs(rotation_angle) < 1.0),
                    help=f"Dreht {selected_count} Module um {rotation_angle:.1f}°"
                ):
                    actions["rotate_selected_clicked"] = True
                    actions["rotation_angle"] = rotation_angle
            
            # TASK 4.3: Quick Move (Drag & Drop Alternative)
            # Requirement 4.3.1: Ziehe Modul an neue Position (simuliert)
            # Requirement 4.3.2: Zeige Vorschau während Drag (nicht möglich in Plotly/Streamlit)
            # Requirement 4.3.3: Snap-to-Grid Funktion
            st.markdown("**Schnell-Verschiebung:**")
            
            # Snap-to-Grid Option
            snap_to_grid = st.checkbox(
                "Snap-to-Grid aktivieren",
                value=st.session_state.get("snap_to_grid_enabled", True),
                help=(
                    "Wenn aktiviert, werden Module beim Verschieben "
                    "automatisch am Raster ausgerichtet"
                )
            )
            if snap_to_grid != st.session_state.get("snap_to_grid_enabled", True):
                st.session_state["snap_to_grid_enabled"] = snap_to_grid
            
            actions["snap_to_grid"] = snap_to_grid
            
            # Quick Move Buttons (Pfeiltasten-Simulation)
            st.markdown("**Richtungs-Tasten:**")
            quick_col1, quick_col2, quick_col3 = st.columns(3)
            
            # Bestimme Schrittweite basierend auf Snap-to-Grid
            if snap_to_grid:
                # Grid-Schrittweite: Modul-Breite + Spacing
                step_size = 1.05 + 0.05  # PV_W + DEFAULT_SPACING = 1.10m
                step_label = "1 Raster"
            else:
                # Freie Bewegung: 0.5m Schritte
                step_size = 0.5
                step_label = "0.5m"
            
            with quick_col1:
                if st.button(
                    "⬅️ Links",
                    use_container_width=True,
                    help=f"Verschiebt {selected_count} Module nach links ({step_label})"
                ):
                    actions["quick_move_clicked"] = True
                    actions["quick_move_direction"] = "left"
                    actions["quick_move_step"] = step_size
            
            with quick_col2:
                # Oben und Unten in einer Spalte
                if st.button(
                    "⬆️ Oben",
                    use_container_width=True,
                    help=f"Verschiebt {selected_count} Module nach oben ({step_label})"
                ):
                    actions["quick_move_clicked"] = True
                    actions["quick_move_direction"] = "up"
                    actions["quick_move_step"] = step_size
                
                if st.button(
                    "⬇️ Unten",
                    use_container_width=True,
                    help=f"Verschiebt {selected_count} Module nach unten ({step_label})"
                ):
                    actions["quick_move_clicked"] = True
                    actions["quick_move_direction"] = "down"
                    actions["quick_move_step"] = step_size
            
            with quick_col3:
                if st.button(
                    "➡️ Rechts",
                    use_container_width=True,
                    help=f"Verschiebt {selected_count} Module nach rechts ({step_label})"
                ):
                    actions["quick_move_clicked"] = True
                    actions["quick_move_direction"] = "right"
                    actions["quick_move_step"] = step_size
            
            # Info über Snap-to-Grid
            if snap_to_grid:
                st.info(
                    f"**Snap-to-Grid aktiv:** Module werden in "
                    f"{step_size:.2f}m Schritten verschoben und automatisch "
                    "am Raster ausgerichtet."
                )
            else:
                st.info(
                    f"**Freie Bewegung:** Module werden in "
                    f"{step_size:.2f}m Schritten verschoben ohne Raster-Ausrichtung."
                )

        st.divider()

        # TASK 4.1: Modul-Auswahl implementieren
        # Requirement 4.1.1: Click auf Modul wählt es aus
        # Requirement 4.1.2: Mehrfachauswahl mit Ctrl
        # Requirement 4.1.3: Visuelle Hervorhebung ausgewählter Module
        if current_placed > 0:
            st.subheader("Modul-Auswahl")
            
            # Zeige Info über ausgewählte Module
            selected_indices = st.session_state.get(
                "selected_module_indices", []
            )
            
            if selected_indices:
                st.info(
                    f"**{len(selected_indices)} Module ausgewählt:** "
                    f"Indizes {', '.join(map(str, selected_indices[:5]))}"
                    f"{'...' if len(selected_indices) > 5 else ''}"
                )
            else:
                st.info(
                    "Keine Module ausgewählt. Verwenden Sie die "
                    "Auswahl-Optionen unten."
                )
            
            # Requirement 4.1.2: Mehrfachauswahl mit Multiselect
            # Da Plotly in Streamlit keine direkten Click-Events unterstützt,
            # verwenden wir ein Multiselect-Widget für die Auswahl
            st.markdown("**Modul-Auswahl:**")
            
            # Erstelle Optionen für alle platzierten Module
            module_options = [f"Modul #{i+1}" for i in range(current_placed)]
            
            # Konvertiere aktuelle Auswahl zu Labels
            current_selection_labels = [
                f"Modul #{i+1}" for i in selected_indices
            ]
            
            # Multiselect für Modul-Auswahl
            # Requirement 4.1.2: Mehrfachauswahl möglich
            selected_labels = st.multiselect(
                "Wählen Sie Module aus:",
                options=module_options,
                default=current_selection_labels,
                help=(
                    "Wählen Sie ein oder mehrere Module aus. "
                    "Ausgewählte Module werden in der 3D-Ansicht "
                    "hervorgehoben (hellblau)."
                ),
                label_visibility="collapsed"
            )
            
            # Konvertiere Labels zurück zu Indizes
            new_selected_indices = [
                int(label.split("#")[1]) - 1
                for label in selected_labels
            ]
            
            # Aktualisiere Session State wenn sich Auswahl geändert hat
            if new_selected_indices != selected_indices:
                st.session_state["selected_module_indices"] = new_selected_indices
                actions["selection_changed"] = True
                st.rerun()
            
            st.divider()
            
            # Schnell-Auswahl-Buttons
            sel_col1, sel_col2, sel_col3 = st.columns(3)
            
            with sel_col1:
                # Requirement 4.1.1: Alle Module auswählen
                if st.button(
                    "Alle auswählen",
                    use_container_width=True,
                    help="Wählt alle platzierten Module aus"
                ):
                    st.session_state["selected_module_indices"] = list(
                        range(current_placed)
                    )
                    st.rerun()
            
            with sel_col2:
                # Auswahl umkehren
                if st.button(
                    "Auswahl umkehren",
                    use_container_width=True,
                    help="Kehrt die aktuelle Auswahl um"
                ):
                    all_indices = set(range(current_placed))
                    current_selected = set(selected_indices)
                    new_selection = list(all_indices - current_selected)
                    st.session_state["selected_module_indices"] = new_selection
                    st.rerun()
            
            with sel_col3:
                # Auswahl aufheben
                if st.button(
                    "Auswahl aufheben",
                    use_container_width=True,
                    disabled=(len(selected_indices) == 0),
                    help="Hebt die Auswahl aller Module auf"
                ):
                    st.session_state["selected_module_indices"] = []
                    st.rerun()
            
            # Bereichs-Auswahl
            st.markdown("**Bereichs-Auswahl:**")
            range_col1, range_col2 = st.columns(2)
            
            with range_col1:
                range_start = st.number_input(
                    "Von Modul #",
                    min_value=1,
                    max_value=current_placed,
                    value=1,
                    step=1,
                    help="Start-Modul für Bereichs-Auswahl"
                )
            
            with range_col2:
                range_end = st.number_input(
                    "Bis Modul #",
                    min_value=1,
                    max_value=current_placed,
                    value=min(5, current_placed),
                    step=1,
                    help="End-Modul für Bereichs-Auswahl"
                )
            
            if st.button(
                f"Bereich auswählen (#{range_start} bis #{range_end})",
                use_container_width=True,
                help="Wählt alle Module im angegebenen Bereich aus"
            ):
                if range_start <= range_end:
                    # Konvertiere zu 0-basierten Indizes
                    range_indices = list(range(range_start - 1, range_end))
                    st.session_state["selected_module_indices"] = range_indices
                    st.rerun()
                else:
                    st.warning(
                        "Start-Modul muss kleiner oder gleich End-Modul sein"
                    )
        
        st.divider()

        # Visualisierungs-Optionen
        st.subheader("Visualisierungs-Optionen")

        opt_col1, opt_col2 = st.columns(2)

        with opt_col1:
            # TASK 8.3: Raster-Overlay aktivieren
            # Requirement 8.3.1: Zeige Platzierungs-Raster
            # Requirement 8.3.3: Toggle Ein/Aus
            show_grid = st.checkbox(
                "Raster anzeigen",
                value=st.session_state.get("show_placement_grid", False),
                help="Zeigt ein Raster zur Orientierung auf der Dachfläche an",
                disabled=False
            )
            actions["show_grid"] = show_grid
            if show_grid != st.session_state.get(
                "show_placement_grid", False
            ):
                st.session_state["show_placement_grid"] = show_grid

        with opt_col2:
            # TASK 8.2: Modul-Nummern aktivieren
            show_numbers = st.checkbox(
                "Modul-Nummern anzeigen",
                value=st.session_state.get("show_module_numbers", False),
                help="Zeigt Nummern auf den Modulen an",
                disabled=False
            )
            actions["show_numbers"] = show_numbers
            if show_numbers != st.session_state.get(
                "show_module_numbers", False
            ):
                st.session_state["show_module_numbers"] = show_numbers
        
        # TASK 8.3: Erweiterte Raster-Einstellungen
        # Requirement 8.3.2: Hilfslinien für Ausrichtung
        if show_grid:
            st.markdown("**Raster-Einstellungen:**")
            
            grid_col1, grid_col2 = st.columns(2)
            
            with grid_col1:
                # Raster-Abstand anpassen
                grid_spacing = st.slider(
                    "Raster-Abstand (m)",
                    min_value=0.5,
                    max_value=2.0,
                    value=st.session_state.get("grid_spacing", 1.0),
                    step=0.25,
                    help="Abstand zwischen Rasterlinien in Metern"
                )
                if grid_spacing != st.session_state.get("grid_spacing", 1.0):
                    st.session_state["grid_spacing"] = grid_spacing
                actions["grid_spacing"] = grid_spacing
            
            with grid_col2:
                # Raster-Transparenz anpassen
                grid_opacity = st.slider(
                    "Raster-Transparenz",
                    min_value=0.1,
                    max_value=1.0,
                    value=st.session_state.get("grid_opacity", 0.3),
                    step=0.1,
                    help="Transparenz der Rasterlinien (0.1 = sehr transparent, 1.0 = undurchsichtig)"
                )
                if grid_opacity != st.session_state.get("grid_opacity", 0.3):
                    st.session_state["grid_opacity"] = grid_opacity
                actions["grid_opacity"] = grid_opacity
            
            # Info über Raster-Funktion
            st.caption(
                "Das Raster hilft bei der Orientierung und Ausrichtung "
                "der Module auf der Dachfläche. Die Linien zeigen die "
                "Platzierungs-Positionen an."
            )

        # Info-Box mit zusätzlichen Informationen
        if current_placed > 0:
            info_text = (
                f"**Platzierungs-Info:**\n\n"
                f"- Dachfläche: {roof_area:.2f} m²\n"
                f"- Module platziert: {current_placed}\n"
                f"- Belegungsgrad: {coverage_percent:.2f}%"
            )
            st.info(info_text)
        else:
            tip_text = (
                "**Tipp:** Klicken Sie auf 'Automatisch belegen' "
                "um Module optimal auf der Dachfläche zu platzieren."
            )
            st.info(tip_text)
    
    except Exception as render_error:
        # Requirement 11.2, 11.4: Error handling with meaningful messages
        st.error(
            f"Fehler beim Rendern des Modul-Belegungs-Panels: "
            f"{str(render_error)}"
        )
        print(f"UI Rendering Error: {render_error}")
        import traceback
        traceback.print_exc()

    return actions
