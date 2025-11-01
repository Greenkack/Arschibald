"""
3D PV-Visualisierung UI-Seite

Diese Seite bietet eine interaktive 3D-Visualisierung der PV-Anlage
auf dem Gebäude mit automatischer und manueller Modul-Platzierung.
"""

import streamlit as st
from typing import Dict, Any, List, Tuple
import io
import functools

# Imports für 3D-Visualisierung
try:
    from utils.pv3d import (
        BuildingDims,
        LayoutConfig,
        AdvancedLayoutConfig,
        ModuleTransform,
        ModuleGroup,
        detect_collisions,
        calculate_sun_position,
        calculate_shading_for_module,
        _safe_get_orientation,
        _safe_get_roof_inclination_deg,
        _safe_get_roof_covering
    )
    # Neue Plotly-basierte 3D-Visualisierung
    from utils.pv3d_plotly import build_plotly_scene
    PV3D_AVAILABLE = True
except ImportError:
    PV3D_AVAILABLE = False


# ============================================================================
# PERFORMANCE-OPTIMIERUNG: CACHING
# ============================================================================

@st.cache_data(ttl=300, show_spinner=False)
def _calculate_roof_capacity(length: float, width: float, roof_type: str) -> int:
    """
    Berechnet die geschätzte Dachkapazität (gecacht für 5 Minuten).
    
    Args:
        length: Gebäudelänge in Metern
        width: Gebäudebreite in Metern
        roof_type: Dachform
    
    Returns:
        Geschätzte Anzahl Module
    """
    roof_area = length * width
    module_area = 1.05 * 1.76  # PV_W * PV_H
    
    # Effizienzfaktor basierend auf Dachform
    efficiency_factors = {
        "Flachdach": 0.7,
        "Satteldach": 0.75,
        "Walmdach": 0.65,
        "Krüppelwalmdach": 0.65,
        "Pultdach": 0.75,
        "Zeltdach": 0.6,
        "Sonstiges": 0.7
    }
    
    efficiency = efficiency_factors.get(roof_type, 0.7)
    
    return int((roof_area / module_area) * efficiency)


@st.cache_data(ttl=60, show_spinner=False)
def _get_default_dimensions(building_type: str) -> Tuple[float, float, float]:
    """
    Gibt Standard-Dimensionen für Gebäudetyp zurück (gecacht für 1 Minute).
    
    Args:
        building_type: Typ des Gebäudes
    
    Returns:
        Tuple (Länge, Breite, Höhe) in Metern
    """
    default_dims = {
        "Einfamilienhaus": (10.0, 6.0, 6.0),
        "Mehrfamilienhaus": (15.0, 10.0, 9.0),
        "Wohnblock": (25.0, 15.0, 12.0)
    }
    return default_dims.get(building_type, (10.0, 6.0, 6.0))


@st.cache_data(ttl=300, show_spinner=False)
def _calculate_yield_forecast(
    module_count: int,
    latitude: float,
    azimuth: float,
    tilt: float,
    efficiency: float
) -> Dict[str, float]:
    """
    Berechnet Ertragsprognose für PV-Anlage (gecacht für 5 Minuten).
    
    Args:
        module_count: Anzahl der Module
        latitude: Breitengrad des Standorts
        azimuth: Azimuth-Winkel in Grad
        tilt: Neigungs-Winkel in Grad
        efficiency: Modul-Wirkungsgrad in Prozent
    
    Returns:
        Dict mit Ertragsdaten (yearly_kwh, daily_avg_kwh, etc.)
    """
    # Vereinfachte Berechnung basierend auf Standort und Ausrichtung
    # Basis: 1000 kWh/kWp pro Jahr in Deutschland
    
    module_power_kwp = 0.4  # 400W pro Modul
    total_power_kwp = module_count * module_power_kwp
    
    # Basis-Ertrag
    base_yield_kwh_per_kwp = 1000
    
    # Korrekturfaktoren
    # Azimuth-Faktor (optimal bei Süd = 0°)
    azimuth_factor = 1.0 - abs(azimuth) / 360.0 * 0.3
    
    # Neigungs-Faktor (optimal bei ~35°)
    optimal_tilt = 35.0
    tilt_factor = 1.0 - abs(tilt - optimal_tilt) / 90.0 * 0.2
    
    # Breitengrad-Faktor (Deutschland: 47-55°)
    latitude_factor = 1.0 - abs(latitude - 51.0) / 10.0 * 0.1
    
    # Effizienz-Faktor
    efficiency_factor = efficiency / 20.0  # 20% als Referenz
    
    # Gesamt-Ertrag
    yearly_kwh = (
        total_power_kwp * 
        base_yield_kwh_per_kwp * 
        azimuth_factor * 
        tilt_factor * 
        latitude_factor * 
        efficiency_factor
    )
    
    return {
        "yearly_kwh": round(yearly_kwh, 2),
        "daily_avg_kwh": round(yearly_kwh / 365, 2),
        "monthly_avg_kwh": round(yearly_kwh / 12, 2),
        "system_kwp": round(total_power_kwp, 2),
        "azimuth_factor": round(azimuth_factor, 3),
        "tilt_factor": round(tilt_factor, 3),
        "latitude_factor": round(latitude_factor, 3)
    }


def _calculate_module_yield_heatmap(
    module_positions: List[Tuple[float, float, float]],
    module_transforms: Dict[int, Any],
    latitude: float,
    efficiency: float
) -> Dict[int, float]:
    """
    Berechnet Ertragswerte für jedes Modul (für Heatmap).
    
    Args:
        module_positions: Liste der Modul-Positionen (x, y, z)
        module_transforms: Dict mit ModuleTransform-Objekten
        latitude: Breitengrad
        efficiency: Modul-Wirkungsgrad in Prozent
    
    Returns:
        Dict mit Modul-Index -> Ertrag in kWh/Jahr
    """
    module_yields = {}
    
    for idx, pos in enumerate(module_positions):
        # Hole Transform für dieses Modul (falls vorhanden)
        if idx in module_transforms:
            transform = module_transforms[idx]
            azimuth = transform.azimuth_deg
            tilt = transform.tilt_deg
        else:
            # Standard-Werte
            azimuth = 0.0
            tilt = 15.0
        
        # Berechne Ertrag für dieses einzelne Modul
        forecast = _calculate_yield_forecast(
            module_count=1,
            latitude=latitude,
            azimuth=azimuth,
            tilt=tilt,
            efficiency=efficiency
        )
        
        module_yields[idx] = forecast["yearly_kwh"]
    
    return module_yields


def render_3d_view():
    """Hauptfunktion zum Rendern der 3D-Visualisierung - wird von gui.py aufgerufen"""
    _render_3d_view_impl()


def _render_3d_view_impl():

    """Interne Implementierung der 3D-Visualisierung"""
    
    # CLEANUP: Entferne alte nicht-serialisierbare Objekte aus Session State
    if "_pv3d_plotter" in st.session_state:
        del st.session_state["_pv3d_plotter"]
    
    # ============================================================================
    # DATEN LADEN
    # ============================================================================
    
    # Lade project_data aus Session State
    project_data = st.session_state.get("project_data", {})
    if not project_data:
        st.warning("⚠️ Keine Projektdaten gefunden. Bitte führen Sie zuerst die Bedarfsanalyse durch.")
        return

    # Lade analysis_results aus Session State
    analysis_results = st.session_state.get("analysis_results", {})

    # Extrahiere relevante Felder mit robusten Fallbacks
    def get_roof_type() -> str:
        """Extrahiert Dachtyp mit Fallback."""
        if "project_details" in project_data:
            roof_type = project_data["project_details"].get("roof_type")
            if roof_type:
                return str(roof_type)
        roof_type = project_data.get("roof_type")
        if roof_type:
            return str(roof_type)
        return "Flachdach"

    def get_module_quantity() -> int:
        """Extrahiert Modulanzahl mit Fallback."""
        # Primäre Quelle: analysis_results
        if analysis_results:
            module_qty = analysis_results.get("module_quantity")
            if module_qty is not None:
                try:
                    return int(module_qty)
                except (ValueError, TypeError):
                    pass
        
        # Fallback: project_data
        if project_data:
            module_qty = project_data.get("module_quantity")
            if module_qty is not None:
                try:
                    return int(module_qty)
                except (ValueError, TypeError):
                    pass
        
        # Letzter Fallback
        return 0

    def get_building_type() -> str:
        """Extrahiert Gebäudeart mit Fallback."""
        if "project_details" in project_data:
            building_type = project_data["project_details"].get("building_type")
            if building_type:
                return str(building_type)
        building_type = project_data.get("building_type")
        if building_type:
            return str(building_type)
        return "Einfamilienhaus"

    # Extrahiere Werte
    roof_type = get_roof_type()
    orientation = _safe_get_orientation(project_data) if PV3D_AVAILABLE else "Süd"
    roof_inclination_deg = _safe_get_roof_inclination_deg(project_data) if PV3D_AVAILABLE else 30.0
    roof_covering = _safe_get_roof_covering(project_data) if PV3D_AVAILABLE else "Ziegel"
    module_quantity = get_module_quantity()
    building_type = get_building_type()

    # ============================================================================
    # PRÜFE 3D-VERFÜGBARKEIT
    # ============================================================================

    if not PV3D_AVAILABLE:
        st.error("❌ 3D-Visualisierung nicht verfügbar. Bitte installieren Sie die erforderlichen Pakete:")
        st.code("pip install pyvista vtk stpyvista numpy trimesh pillow", language="bash")
        st.stop()

    # ============================================================================
    # TITEL UND BESCHREIBUNG
    # ============================================================================

    st.title("🏠 3D PV-Visualisierung")
    st.markdown("""
    Visualisieren Sie Ihre PV-Anlage in 3D. Passen Sie Gebäudedimensionen an,
    wählen Sie zwischen automatischer und manueller Modul-Platzierung und
    exportieren Sie das Modell als Bild oder 3D-Datei.
    """)

    st.divider()

    # ============================================================================
    # SIDEBAR - EINSTELLUNGEN (REORGANISIERT MIT COLLAPSIBLE SECTIONS)
    # ============================================================================

    st.sidebar.header("⚙️ Einstellungen")

    # ============================================================================
    # EXPANDER 1: BASIS-EINSTELLUNGEN
    # ============================================================================
    with st.sidebar.expander("🏠 Basis-Einstellungen", expanded=True):
        st.markdown("**Gebäudedimensionen**")
        
        # Standardwerte basierend auf Gebäudeart (gecacht)
        default_length, default_width, default_height = _get_default_dimensions(building_type)

        building_length = st.number_input(
            "Gebäudelänge (m)",
            min_value=8.0,
            max_value=60.0,
            value=default_length,
            step=0.5,
            help="Länge des Gebäudes in Metern",
            key="building_length_input"
        )

        building_width = st.number_input(
            "Gebäudebreite (m)",
            min_value=5.0,
            max_value=40.0,
            value=default_width,
            step=0.5,
            help="Breite des Gebäudes in Metern",
            key="building_width_input"
        )

        building_height = st.number_input(
            "Traufhöhe (m)",
            min_value=3.0,
            max_value=20.0,
            value=default_height,
            step=0.5,
            help="Höhe der Außenwände (Traufhöhe)",
            key="building_height_input"
        )

        st.divider()

        # Dachform
        st.markdown("**Dachform**")

        roof_types = [
            "Flachdach",
            "Satteldach",
            "Walmdach",
            "Krüppelwalmdach",
            "Pultdach",
            "Zeltdach",
            "Sonstiges"
        ]

        selected_roof_type = st.selectbox(
            "Dachform",
            options=roof_types,
            index=roof_types.index(roof_type) if roof_type in roof_types else 0,
            help="Wählen Sie die Dachform Ihres Gebäudes",
            key="roof_type_select"
        )

    # ============================================================================
    # EXPANDER 2: MODUL-BELEGUNG
    # ============================================================================
    with st.sidebar.expander("⚡ Modul-Belegung", expanded=True):
        st.markdown("**Belegungsmodus**")
        
        layout_mode = st.radio(
            "Belegungsmodus",
            options=["Automatisch", "Manuell"],
            index=0,
            help="Automatisch: Module werden gleichmäßig verteilt. Manuell: Sie können einzelne Module entfernen.",
            key="layout_mode_radio"
        )

        st.divider()

        # Flachdach-Aufständerung (nur bei Flachdach)
        mounting_type = "Süd"
        custom_azimuth = 0.0
        custom_tilt = 15.0
        
        if selected_roof_type == "Flachdach":
            st.markdown("**Aufständerung**")
            
            mounting_type = st.selectbox(
                "Aufständerungstyp",
                options=["Süd", "Ost-West", "Süd-Ost", "Süd-West", "Individuell"],
                index=0,
                help="Wählen Sie die Ausrichtung der Aufständerung für optimalen Ertrag.",
                key="mounting_type_select"
            )
            
            # Zeige custom-Eingabefelder nur bei "Individuell" Modus
            if mounting_type == "Individuell":
                st.caption("**Individuelle Parameter:**")
                
                custom_azimuth = st.slider(
                    "Azimuth (°)",
                    min_value=0.0,
                    max_value=360.0,
                    value=0.0,
                    step=5.0,
                    help="Ausrichtung: 0° = Süd, 90° = West, 180° = Nord, 270° = Ost",
                    key="custom_azimuth_slider"
                )
                
                custom_tilt = st.slider(
                    "Neigung (°)",
                    min_value=0.0,
                    max_value=90.0,
                    value=15.0,
                    step=1.0,
                    help="Neigungswinkel: 0° = horizontal, 90° = vertikal",
                    key="custom_tilt_slider"
                )

        st.divider()

        # Platzmangel-Fallbacks
        st.markdown("**Zusätzliche Flächen**")

        use_garage = st.checkbox(
            "Garage/Carport automatisch hinzufügen",
            value=False,
            help="Fügt eine Garage hinzu, wenn Module nicht auf dem Hauptdach passen",
            key="use_garage_checkbox"
        )

        use_facade = st.checkbox(
            "Fassadenbelegung aktivieren",
            value=False,
            help="Platziert Module an der Südfassade, wenn Dach und Garage nicht ausreichen",
            key="use_facade_checkbox"
        )

        st.divider()

        # Manuelle Indizes-Eingabe (nur im manuellen Modus)
        removed_indices = []
        if layout_mode == "Manuell":
            st.markdown("**Manuelle Anpassung**")
            
            indices_input = st.text_area(
                "Zu entfernende Module (Indizes)",
                value="",
                height=100,
                help="Geben Sie die Indizes der zu entfernenden Module ein (komma-separiert, 0-basiert). Beispiel: 0,1,5,10",
                key="removed_indices_input"
            )
            
            # Parse Indizes
            if indices_input.strip():
                try:
                    removed_indices = [
                        int(idx.strip())
                        for idx in indices_input.split(",")
                        if idx.strip()
                    ]
                    st.success(f"✓ {len(removed_indices)} Module werden entfernt")
                except ValueError:
                    st.error("❌ Ungültige Eingabe. Bitte nur Zahlen und Kommas verwenden.")
                    removed_indices = []

    # ============================================================================
    # EXPANDER 3: ERWEITERTE KONTROLLE
    # ============================================================================
    with st.sidebar.expander("🎛️ Erweiterte Kontrolle", expanded=False):
        st.markdown("**Erweiterte Optionen**")

        enable_collision_detection = st.checkbox(
            "Kollisionserkennung aktivieren",
            value=True,
            help="Prüft auf Überschneidungen zwischen Modulen und zeigt Warnungen an",
            key="collision_detection_checkbox"
        )

        st.divider()

        # Modul-Auswahl und Bearbeitung (jetzt Teil von Erweiterte Kontrolle)
        st.markdown("**Modul-Auswahl & Bearbeitung**")
        st.caption("Wählen Sie einzelne Module oder Gruppen aus, um deren Eigenschaften zu bearbeiten.")
        
        # Auswahl-Modus
        selection_mode = st.radio(
            "Auswahl-Modus",
            options=["Einzeln", "Gruppe", "Bereich"],
            index=0,
            help="Wählen Sie, wie Sie Module auswählen möchten",
            key="selection_mode_radio"
        )
        
        # Hole aktuelle Auswahl
        selected_modules = st.session_state.get("pv3d_selected_modules", [])
        
        # Berechne maximale Modulanzahl (geschätzt)
        roof_area = building_length * building_width
        module_area = 1.05 * 1.76  # PV_W * PV_H
        max_modules = int((roof_area / module_area) * 0.7)
        
        if selection_mode == "Einzeln":
            # Einzelauswahl per Index-Eingabe
            st.caption("Geben Sie den Index des Moduls ein (0-basiert):")
            
            single_index = st.number_input(
                "Modul-Index",
                min_value=0,
                max_value=max(0, max_modules - 1),
                value=0,
                step=1,
                help="Index des auszuwählenden Moduls (0 = erstes Modul)"
            )
            
            col_select, col_deselect = st.columns(2)
            
            with col_select:
                if st.button("➕ Auswählen", use_container_width=True):
                    if single_index not in selected_modules:
                        selected_modules.append(single_index)
                        st.session_state["pv3d_selected_modules"] = selected_modules
                        st.success(f"✓ Modul {single_index} ausgewählt")
                        st.rerun()
                    else:
                        st.info(f"Modul {single_index} ist bereits ausgewählt")
            
            with col_deselect:
                if st.button("➖ Entfernen", use_container_width=True):
                    if single_index in selected_modules:
                        selected_modules.remove(single_index)
                        st.session_state["pv3d_selected_modules"] = selected_modules
                        st.success(f"✓ Modul {single_index} entfernt")
                        st.rerun()
                    else:
                        st.info(f"Modul {single_index} ist nicht ausgewählt")
        
        elif selection_mode == "Gruppe":
            # Gruppenauswahl per Dropdown
            st.caption("Wählen Sie eine vordefinierte Gruppe aus:")
            
            # Hole Gruppen aus AdvancedLayoutConfig (falls vorhanden)
            try:
                current_config = AdvancedLayoutConfig.from_json(
                    st.session_state.get("pv3d_layout_json", "{}")
                )
                available_groups = list(current_config.module_groups.keys())
            except:
                available_groups = []
            
            # Füge Standard-Gruppen hinzu wenn keine vorhanden
            if not available_groups:
                available_groups = ["Alle Module", "Erste Hälfte", "Zweite Hälfte"]
            
            selected_group = st.selectbox(
                "Gruppe",
                options=available_groups,
                index=0,
                help="Wählen Sie eine Gruppe von Modulen aus"
            )
            
            if st.button("🔘 Gruppe auswählen", use_container_width=True):
                # Bestimme Modul-Indizes basierend auf Gruppe
                if selected_group == "Alle Module":
                    group_indices = list(range(max_modules))
                elif selected_group == "Erste Hälfte":
                    group_indices = list(range(max_modules // 2))
                elif selected_group == "Zweite Hälfte":
                    group_indices = list(range(max_modules // 2, max_modules))
                else:
                    # Hole Indizes aus gespeicherter Gruppe
                    try:
                        group_obj = current_config.module_groups.get(selected_group)
                        if group_obj:
                            group_indices = group_obj.module_indices
                        else:
                            group_indices = []
                    except:
                        group_indices = []
                
                # Setze Auswahl
                st.session_state["pv3d_selected_modules"] = group_indices
                st.success(f"✓ Gruppe '{selected_group}' ausgewählt ({len(group_indices)} Module)")
                st.rerun()
        
        elif selection_mode == "Bereich":
            # Bereichsauswahl mit Start/End-Index
            st.caption("Wählen Sie einen Bereich von Modulen aus:")
            
            col_start, col_end = st.columns(2)
            
            with col_start:
                start_index = st.number_input(
                    "Von Index",
                    min_value=0,
                    max_value=max(0, max_modules - 1),
                    value=0,
                    step=1,
                    help="Start-Index des Bereichs (inklusiv)"
                )
            
            with col_end:
                end_index = st.number_input(
                    "Bis Index",
                    min_value=0,
                    max_value=max(0, max_modules - 1),
                    value=min(9, max_modules - 1),
                    step=1,
                    help="End-Index des Bereichs (inklusiv)"
                )
            
            if st.button("🔘 Bereich auswählen", use_container_width=True):
                # Validiere Bereich
                if start_index <= end_index:
                    range_indices = list(range(start_index, end_index + 1))
                    st.session_state["pv3d_selected_modules"] = range_indices
                    st.success(f"✓ Bereich {start_index}-{end_index} ausgewählt ({len(range_indices)} Module)")
                    st.rerun()
                else:
                    st.error("❌ Start-Index muss kleiner oder gleich End-Index sein")
        
        st.divider()
        
        # Zeige aktuelle Auswahl
        if selected_modules:
            st.info(
                f"**Aktuell ausgewählt:** {len(selected_modules)} Modul(e)\n\n"
                f"Indizes: {', '.join(map(str, sorted(selected_modules)[:10]))}"
                f"{'...' if len(selected_modules) > 10 else ''}"
            )
            
            # Button zum Aufheben der Auswahl
            if st.button("🔄 Auswahl aufheben", use_container_width=True):
                st.session_state["pv3d_selected_modules"] = []
                st.success("✓ Auswahl aufgehoben")
                st.rerun()
        else:
            st.caption("Keine Module ausgewählt")

    st.sidebar.divider()

    # Eigenschaften-Panel für ausgewählte Module
    selected_modules = st.session_state.get("pv3d_selected_modules", [])
    
    if selected_modules:
        with st.sidebar.expander("🔧 Eigenschaften bearbeiten", expanded=True):
            st.markdown(f"**{len(selected_modules)} Modul(e) ausgewählt**")
            
            # Hole aktuelle Transformationen aus AdvancedLayoutConfig (falls vorhanden)
            try:
                current_config = AdvancedLayoutConfig.from_json(
                    st.session_state.get("pv3d_layout_json", "{}")
                )
            except:
                current_config = AdvancedLayoutConfig()
            
            # Zeige Eigenschaften des ersten ausgewählten Moduls als Referenz
            first_module_idx = selected_modules[0]
            
            # Hole aktuelle Transformation (falls vorhanden)
            if first_module_idx in current_config.module_transforms:
                current_transform = current_config.module_transforms[first_module_idx]
                default_azimuth = current_transform.azimuth_deg
                default_tilt = current_transform.tilt_deg
                default_offset_x = current_transform.offset_x
                default_offset_y = current_transform.offset_y
                default_offset_z = current_transform.offset_z
            else:
                # Standard-Werte
                default_azimuth = 0.0
                default_tilt = 15.0
                default_offset_x = 0.0
                default_offset_y = 0.0
                default_offset_z = 0.0
            
            st.caption(f"Referenz-Modul: #{first_module_idx}")
            
            # Zeige aktuelle Position/Eigenschaften
            with st.expander("📍 Aktuelle Eigenschaften", expanded=False):
                st.text(f"Index: {first_module_idx}")
                st.text(f"Azimuth: {default_azimuth:.1f}°")
                st.text(f"Neigung: {default_tilt:.1f}°")
                st.text(f"Offset X: {default_offset_x:.2f}m")
                st.text(f"Offset Y: {default_offset_y:.2f}m")
                st.text(f"Offset Z: {default_offset_z:.2f}m")
            
            st.divider()
            
            # Bearbeitungs-Controls
            st.subheader("Neue Werte")
            
            # Azimuth-Slider
            new_azimuth = st.slider(
                "Azimuth (°)",
                min_value=0.0,
                max_value=360.0,
                value=default_azimuth,
                step=5.0,
                help="0° = Süd, 90° = West, 180° = Nord, 270° = Ost"
            )
            
            # Neigungs-Slider
            new_tilt = st.slider(
                "Neigung (°)",
                min_value=0.0,
                max_value=90.0,
                value=default_tilt,
                step=5.0,
                help="0° = horizontal, 90° = vertikal"
            )
            
            st.caption("**Position-Offsets (relativ zur Rasterposition):**")
            
            # Offset-Eingaben in 3 Spalten
            col_x, col_y, col_z = st.columns(3)
            
            with col_x:
                new_offset_x = st.number_input(
                    "X (m)",
                    min_value=-10.0,
                    max_value=10.0,
                    value=default_offset_x,
                    step=0.1,
                    format="%.2f",
                    help="Verschiebung in X-Richtung"
                )
            
            with col_y:
                new_offset_y = st.number_input(
                    "Y (m)",
                    min_value=-10.0,
                    max_value=10.0,
                    value=default_offset_y,
                    step=0.1,
                    format="%.2f",
                    help="Verschiebung in Y-Richtung"
                )
            
            with col_z:
                new_offset_z = st.number_input(
                    "Z (m)",
                    min_value=-5.0,
                    max_value=5.0,
                    value=default_offset_z,
                    step=0.1,
                    format="%.2f",
                    help="Verschiebung in Z-Richtung (Höhe)"
                )
            
            st.divider()
            
            # Aktions-Buttons
            col_apply, col_reset = st.columns(2)
            
            with col_apply:
                if st.button("✅ Anwenden", type="primary", use_container_width=True):
                    # Wende Transformation auf alle ausgewählten Module an
                    for module_idx in selected_modules:
                        # Erstelle oder aktualisiere ModuleTransform
                        transform = ModuleTransform(
                            index=module_idx,
                            azimuth_deg=new_azimuth,
                            tilt_deg=new_tilt,
                            offset_x=new_offset_x,
                            offset_y=new_offset_y,
                            offset_z=new_offset_z
                        )
                        current_config.module_transforms[module_idx] = transform
                    
                    # Speichere aktualisierte Konfiguration
                    st.session_state["pv3d_layout_json"] = current_config.to_json()
                    
                    # Markiere als nicht gerendert (erzwingt Neuberechnung)
                    st.session_state["pv3d_last_rendered"] = False
                    
                    st.success(f"✓ Transformation auf {len(selected_modules)} Modul(e) angewendet")
                    st.info("💡 Klicken Sie auf 'Visualisierung aktualisieren' um die Änderungen zu sehen")
            
            with col_reset:
                if st.button("🔄 Zurücksetzen", use_container_width=True):
                    # Entferne Transformationen für ausgewählte Module
                    for module_idx in selected_modules:
                        if module_idx in current_config.module_transforms:
                            del current_config.module_transforms[module_idx]
                    
                    # Speichere aktualisierte Konfiguration
                    st.session_state["pv3d_layout_json"] = current_config.to_json()
                    
                    # Markiere als nicht gerendert
                    st.session_state["pv3d_last_rendered"] = False
                    
                    st.success(f"✓ Transformation für {len(selected_modules)} Modul(e) zurückgesetzt")
                    st.rerun()
            
            # Echtzeit-Vorschau-Hinweis
            st.caption(
                "💡 **Tipp:** Die Änderungen werden nach dem Klick auf 'Anwenden' "
                "und 'Visualisierung aktualisieren' sichtbar."
            )

        st.divider()

        # Modul-Gruppen-Verwaltung (jetzt Teil von Erweiterte Kontrolle)
        st.markdown("**Modul-Gruppen**")
        st.caption("Erstellen und verwalten Sie Gruppen von Modulen für gemeinsame Konfiguration.")
        st.markdown("Erstellen und verwalten Sie Gruppen von Modulen für gemeinsame Konfiguration.")
        
        # Hole aktuelle Konfiguration
        try:
            current_config = AdvancedLayoutConfig.from_json(
                st.session_state.get("pv3d_layout_json", "{}")
            )
        except:
            current_config = AdvancedLayoutConfig()
        
        # Zeige existierende Gruppen
        if current_config.module_groups:
            st.caption(f"**Existierende Gruppen:** {len(current_config.module_groups)}")
            
            # Zeige Gruppen-Liste
            for group_name, group in current_config.module_groups.items():
                with st.container():
                    col_info, col_edit, col_delete = st.columns([3, 0.5, 0.5])
                    
                    with col_info:
                        # Zeige Gruppen-Info mit Farb-Indikator
                        st.markdown(
                            f"<span style='color:{group.color};'>●</span> **{group_name}**  \n"
                            f"Module: {len(group.module_indices)} | "
                            f"Azimuth: {group.azimuth_deg:.0f}° | "
                            f"Neigung: {group.tilt_deg:.0f}°",
                            unsafe_allow_html=True
                        )
                    
                    with col_edit:
                        # Bearbeiten-Button für Gruppe
                        if st.button("✏️", key=f"edit_group_{group_name}", help=f"Gruppe '{group_name}' bearbeiten"):
                            # Setze Gruppe als ausgewählt für Bearbeitung
                            st.session_state["pv3d_editing_group"] = group_name
                            st.rerun()
                    
                    with col_delete:
                        # Lösch-Button für Gruppe
                        if st.button("🗑️", key=f"delete_group_{group_name}", help=f"Gruppe '{group_name}' löschen"):
                            # Entferne Gruppe
                            del current_config.module_groups[group_name]
                            
                            # Entferne group_id von allen Modulen in dieser Gruppe
                            for module_idx in group.module_indices:
                                if module_idx in current_config.module_transforms:
                                    current_config.module_transforms[module_idx].group_id = None
                            
                            # Speichere aktualisierte Konfiguration
                            st.session_state["pv3d_layout_json"] = current_config.to_json()
                            st.session_state["pv3d_last_rendered"] = False
                            
                            st.success(f"✓ Gruppe '{group_name}' gelöscht")
                            st.rerun()
            
            st.divider()
        else:
            st.caption("Keine Gruppen vorhanden")
            st.divider()
        
        # Gruppen-Transformation (wenn Gruppe zur Bearbeitung ausgewählt)
        editing_group_name = st.session_state.get("pv3d_editing_group")
        
        if editing_group_name and editing_group_name in current_config.module_groups:
            st.subheader(f"🔧 Gruppe bearbeiten: {editing_group_name}")
            
            editing_group = current_config.module_groups[editing_group_name]
            
            st.caption(f"**Module in Gruppe:** {len(editing_group.module_indices)}")
            st.caption(f"Indizes: {', '.join(map(str, sorted(editing_group.module_indices)[:10]))}"
                      f"{'...' if len(editing_group.module_indices) > 10 else ''}")
            
            # Transformations-Controls
            col_az, col_tilt = st.columns(2)
            
            with col_az:
                edit_azimuth = st.slider(
                    "Azimuth (°)",
                    min_value=0.0,
                    max_value=360.0,
                    value=editing_group.azimuth_deg,
                    step=5.0,
                    help="Neuer Azimuth für alle Module in der Gruppe",
                    key=f"edit_group_azimuth_{editing_group_name}"
                )
            
            with col_tilt:
                edit_tilt = st.slider(
                    "Neigung (°)",
                    min_value=0.0,
                    max_value=90.0,
                    value=editing_group.tilt_deg,
                    step=5.0,
                    help="Neue Neigung für alle Module in der Gruppe",
                    key=f"edit_group_tilt_{editing_group_name}"
                )
            
            # Aktions-Buttons
            col_apply, col_cancel = st.columns(2)
            
            with col_apply:
                if st.button("✅ Transformation anwenden", type="primary", use_container_width=True, key=f"apply_group_transform_{editing_group_name}"):
                    # Aktualisiere Gruppen-Eigenschaften
                    editing_group.azimuth_deg = edit_azimuth
                    editing_group.tilt_deg = edit_tilt
                    
                    # Wende Transformation auf alle Module in der Gruppe an
                    for module_idx in editing_group.module_indices:
                        if module_idx in current_config.module_transforms:
                            # Aktualisiere existierende Transformation
                            current_config.module_transforms[module_idx].azimuth_deg = edit_azimuth
                            current_config.module_transforms[module_idx].tilt_deg = edit_tilt
                        else:
                            # Erstelle neue Transformation
                            current_config.module_transforms[module_idx] = ModuleTransform(
                                index=module_idx,
                                azimuth_deg=edit_azimuth,
                                tilt_deg=edit_tilt,
                                offset_x=0.0,
                                offset_y=0.0,
                                offset_z=0.0,
                                group_id=editing_group_name
                            )
                    
                    # Speichere aktualisierte Konfiguration
                    st.session_state["pv3d_layout_json"] = current_config.to_json()
                    st.session_state["pv3d_last_rendered"] = False
                    
                    # Beende Bearbeitungsmodus
                    del st.session_state["pv3d_editing_group"]
                    
                    st.success(f"✓ Transformation auf Gruppe '{editing_group_name}' ({len(editing_group.module_indices)} Module) angewendet")
                    st.info("💡 Klicken Sie auf 'Visualisierung aktualisieren' um die Änderungen zu sehen")
                    st.rerun()
            
            with col_cancel:
                if st.button("❌ Abbrechen", use_container_width=True, key=f"cancel_group_edit_{editing_group_name}"):
                    # Beende Bearbeitungsmodus ohne Änderungen
                    del st.session_state["pv3d_editing_group"]
                    st.rerun()
            
            # Vorschau-Hinweis
            st.caption(
                "💡 **Vorschau:** Die Änderungen werden nach dem Anwenden und "
                "Aktualisieren der Visualisierung sichtbar."
            )
            
            st.divider()
        
        # Neue Gruppe erstellen
        st.subheader("➕ Neue Gruppe erstellen")
        
        # Eingabefeld für Gruppen-Name
        new_group_name = st.text_input(
            "Gruppen-Name",
            value="",
            placeholder="z.B. Süddach, Ostdach, Westdach",
            help="Geben Sie einen eindeutigen Namen für die Gruppe ein",
            key="new_group_name_input"
        )
        
        # Eingabefeld für Modul-Indizes
        new_group_indices = st.text_area(
            "Modul-Indizes (komma-separiert)",
            value="",
            placeholder="z.B. 0,1,2,3,4,5",
            height=80,
            help="Geben Sie die Indizes der Module ein, die zur Gruppe gehören sollen (0-basiert, komma-separiert)",
            key="new_group_indices_input"
        )
        
        # Optionale Gruppen-Eigenschaften
        col_azimuth, col_tilt = st.columns(2)
        
        with col_azimuth:
            new_group_azimuth = st.number_input(
                "Azimuth (°)",
                min_value=0.0,
                max_value=360.0,
                value=0.0,
                step=5.0,
                help="Standard-Azimuth für alle Module in der Gruppe",
                key="new_group_azimuth_input"
            )
        
        with col_tilt:
            new_group_tilt = st.number_input(
                "Neigung (°)",
                min_value=0.0,
                max_value=90.0,
                value=15.0,
                step=5.0,
                help="Standard-Neigung für alle Module in der Gruppe",
                key="new_group_tilt_input"
            )
        
        # Farb-Auswahl für Gruppe
        group_color_options = {
            "Schwarz": "#000000",
            "Rot": "#ff0000",
            "Grün": "#00ff00",
            "Blau": "#0000ff",
            "Gelb": "#ffff00",
            "Orange": "#ff8800",
            "Lila": "#8800ff",
            "Türkis": "#00ffff"
        }
        
        selected_color_name = st.selectbox(
            "Gruppen-Farbe",
            options=list(group_color_options.keys()),
            index=0,
            help="Wählen Sie eine Farbe für die visuelle Darstellung der Gruppe",
            key="new_group_color_input"
        )
        
        new_group_color = group_color_options[selected_color_name]
        
        # Button: Gruppe erstellen
        if st.button("✅ Gruppe erstellen", type="primary", use_container_width=True, key="create_group_button"):
            # Validiere Eingaben
            errors = []
            
            if not new_group_name.strip():
                errors.append("Gruppen-Name darf nicht leer sein")
            elif new_group_name in current_config.module_groups:
                errors.append(f"Gruppe '{new_group_name}' existiert bereits")
            
            if not new_group_indices.strip():
                errors.append("Modul-Indizes dürfen nicht leer sein")
            else:
                # Parse Indizes
                try:
                    indices = [
                        int(idx.strip())
                        for idx in new_group_indices.split(",")
                        if idx.strip()
                    ]
                    
                    if not indices:
                        errors.append("Keine gültigen Modul-Indizes gefunden")
                    elif any(idx < 0 for idx in indices):
                        errors.append("Modul-Indizes müssen >= 0 sein")
                    
                except ValueError:
                    errors.append("Ungültige Modul-Indizes. Bitte nur Zahlen und Kommas verwenden.")
                    indices = []
            
            # Zeige Fehler oder erstelle Gruppe
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                # Erstelle ModuleGroup-Objekt
                new_group = ModuleGroup(
                    name=new_group_name.strip(),
                    module_indices=indices,
                    azimuth_deg=new_group_azimuth,
                    tilt_deg=new_group_tilt,
                    color=new_group_color
                )
                
                # Füge Gruppe zur Konfiguration hinzu
                current_config.module_groups[new_group_name.strip()] = new_group
                
                # Erstelle/aktualisiere ModuleTransform für jedes Modul in der Gruppe
                for module_idx in indices:
                    if module_idx in current_config.module_transforms:
                        # Aktualisiere existierende Transformation
                        current_config.module_transforms[module_idx].group_id = new_group_name.strip()
                        current_config.module_transforms[module_idx].azimuth_deg = new_group_azimuth
                        current_config.module_transforms[module_idx].tilt_deg = new_group_tilt
                    else:
                        # Erstelle neue Transformation
                        current_config.module_transforms[module_idx] = ModuleTransform(
                            index=module_idx,
                            azimuth_deg=new_group_azimuth,
                            tilt_deg=new_group_tilt,
                            offset_x=0.0,
                            offset_y=0.0,
                            offset_z=0.0,
                            group_id=new_group_name.strip()
                        )
                
                # Speichere aktualisierte Konfiguration
                st.session_state["pv3d_layout_json"] = current_config.to_json()
                st.session_state["pv3d_last_rendered"] = False
                
                st.success(f"✓ Gruppe '{new_group_name}' mit {len(indices)} Modulen erstellt")
                st.info("💡 Klicken Sie auf 'Visualisierung aktualisieren' um die Änderungen zu sehen")
                
                # Leere Eingabefelder (durch Rerun)
                st.rerun()
        
        st.divider()
        
        # Gruppen-Templates
        st.subheader("📋 Gruppen-Templates")
        st.caption("Wenden Sie vordefinierte Templates mit optimalen Ausrichtungen an.")
        
        # Template-Definitionen
        template_definitions = {
            "Süddach": {
                "azimuth": 0.0,
                "tilt": 35.0,
                "color": "#ff8800",
                "description": "Optimale Ausrichtung nach Süden (0°)"
            },
            "Ostdach": {
                "azimuth": 270.0,
                "tilt": 35.0,
                "color": "#ffff00",
                "description": "Ausrichtung nach Osten (270°)"
            },
            "Westdach": {
                "azimuth": 90.0,
                "tilt": 35.0,
                "color": "#00ffff",
                "description": "Ausrichtung nach Westen (90°)"
            },
            "Norddach": {
                "azimuth": 180.0,
                "tilt": 35.0,
                "color": "#8800ff",
                "description": "Ausrichtung nach Norden (180°)"
            }
        }
        
        # Template-Auswahl
        selected_template = st.selectbox(
            "Template auswählen",
            options=list(template_definitions.keys()),
            index=0,
            help="Wählen Sie ein vordefiniertes Template für die Gruppen-Erstellung",
            key="group_template_select"
        )
        
        # Zeige Template-Details
        template = template_definitions[selected_template]
        st.info(
            f"**{selected_template}**\n\n"
            f"{template['description']}\n\n"
            f"• Azimuth: {template['azimuth']:.0f}°\n"
            f"• Neigung: {template['tilt']:.0f}°\n"
            f"• Farbe: <span style='color:{template['color']};'>●</span>",
            icon="ℹ️"
        )
        
        # Template-Name und Indizes
        template_group_name = st.text_input(
            "Gruppen-Name für Template",
            value=selected_template,
            placeholder=f"z.B. {selected_template}",
            help="Name für die neue Gruppe (kann angepasst werden)",
            key="template_group_name_input"
        )
        
        template_group_indices = st.text_area(
            "Modul-Indizes (komma-separiert)",
            value="",
            placeholder="z.B. 0,1,2,3,4,5",
            height=80,
            help="Geben Sie die Indizes der Module ein, die zur Template-Gruppe gehören sollen",
            key="template_group_indices_input"
        )
        
        # Button: Template anwenden
        if st.button("✨ Template anwenden", type="primary", use_container_width=True, key="apply_template_button"):
            # Validiere Eingaben
            errors = []
            
            if not template_group_name.strip():
                errors.append("Gruppen-Name darf nicht leer sein")
            elif template_group_name.strip() in current_config.module_groups:
                errors.append(f"Gruppe '{template_group_name.strip()}' existiert bereits")
            
            if not template_group_indices.strip():
                errors.append("Modul-Indizes dürfen nicht leer sein")
            else:
                # Parse Indizes
                try:
                    indices = [
                        int(idx.strip())
                        for idx in template_group_indices.split(",")
                        if idx.strip()
                    ]
                    
                    if not indices:
                        errors.append("Keine gültigen Modul-Indizes gefunden")
                    elif any(idx < 0 for idx in indices):
                        errors.append("Modul-Indizes müssen >= 0 sein")
                    
                except ValueError:
                    errors.append("Ungültige Modul-Indizes. Bitte nur Zahlen und Kommas verwenden.")
                    indices = []
            
            # Zeige Fehler oder erstelle Gruppe mit Template
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                # Erstelle ModuleGroup-Objekt mit Template-Werten
                new_group = ModuleGroup(
                    name=template_group_name.strip(),
                    module_indices=indices,
                    azimuth_deg=template['azimuth'],
                    tilt_deg=template['tilt'],
                    color=template['color']
                )
                
                # Füge Gruppe zur Konfiguration hinzu
                current_config.module_groups[template_group_name.strip()] = new_group
                
                # Erstelle/aktualisiere ModuleTransform für jedes Modul in der Gruppe
                for module_idx in indices:
                    if module_idx in current_config.module_transforms:
                        # Aktualisiere existierende Transformation
                        current_config.module_transforms[module_idx].group_id = template_group_name.strip()
                        current_config.module_transforms[module_idx].azimuth_deg = template['azimuth']
                        current_config.module_transforms[module_idx].tilt_deg = template['tilt']
                    else:
                        # Erstelle neue Transformation
                        current_config.module_transforms[module_idx] = ModuleTransform(
                            index=module_idx,
                            azimuth_deg=template['azimuth'],
                            tilt_deg=template['tilt'],
                            offset_x=0.0,
                            offset_y=0.0,
                            offset_z=0.0,
                            group_id=template_group_name.strip()
                        )
                
                # Speichere aktualisierte Konfiguration
                st.session_state["pv3d_layout_json"] = current_config.to_json()
                st.session_state["pv3d_last_rendered"] = False
                
                st.success(f"✓ Template '{selected_template}' als Gruppe '{template_group_name.strip()}' mit {len(indices)} Modulen angewendet")
                st.info("💡 Klicken Sie auf 'Visualisierung aktualisieren' um die Änderungen zu sehen")
                
                # Leere Eingabefelder (durch Rerun)
                st.rerun()

    # ============================================================================
    # EXPANDER 4: ANALYSE
    # ============================================================================
    with st.sidebar.expander("📊 Analyse", expanded=False):
        # Optimierungs-Assistent
        st.markdown("**🎯 Optimierungs-Assistent**")
        st.caption("Lassen Sie das System automatisch die beste Konfiguration für Ihre Anforderungen finden.")
        st.caption("Lassen Sie das System automatisch die beste Konfiguration für Ihre Anforderungen finden.")
        
        # Optimierungs-Ziel auswählen
        optimization_goal = st.radio(
            "Optimierungs-Ziel",
            options=["max_modules", "max_yield", "balanced"],
            format_func=lambda x: {
                "max_modules": "Maximale Modulanzahl",
                "max_yield": "Maximaler Ertrag",
                "balanced": "Ausgewogen"
            }[x],
            index=1,  # Default: max_yield
            help="Wählen Sie das Optimierungsziel:\n"
                 "- Maximale Modulanzahl: Platziert so viele Module wie möglich\n"
                 "- Maximaler Ertrag: Optimiert für höchste Energieausbeute\n"
                 "- Ausgewogen: Balance zwischen Anzahl und Ertrag"
        )
        
        # Button: Optimierung starten
        btn_optimize = st.button(
            "🚀 Optimierung starten",
            use_container_width=True,
            help="Generiert und bewertet verschiedene Konfigurationen"
        )
        
        # Optimierung durchführen
        if btn_optimize:
            with st.spinner("Optimiere Konfigurationen..."):
                try:
                    # Importiere Optimierungs-Funktionen
                    from utils.pv3d import optimize_layout
                    
                    # Erstelle BuildingDims (bereits am Anfang importiert)
                    dims = BuildingDims(
                        length_m=building_length,
                        width_m=building_width,
                        wall_height_m=building_height
                    )
                    
                    # Führe Optimierung durch
                    top_configs = optimize_layout(
                        building_dims=dims,
                        target_modules=module_quantity,
                        roof_type=roof_type,
                        optimization_goal=optimization_goal
                    )
                    
                    # Speichere Ergebnisse in Session State (serialisierbar)
                    # Konvertiere Konfigurationen in JSON-Strings, Scores als float
                    import json
                    serializable_results = [
                        (config.to_json() if hasattr(config, 'to_json') else json.dumps(config), float(score))
                        for config, score in top_configs
                    ]
                    st.session_state["optimization_results"] = serializable_results
                    st.session_state["optimization_goal"] = optimization_goal
                    
                    st.success(f"✓ Optimierung abgeschlossen! {len(top_configs)} Konfigurationen gefunden.")
                    
                except Exception as e:
                    st.error(f"❌ Fehler bei der Optimierung: {e}")
        
        # Zeige Optimierungs-Ergebnisse
        if "optimization_results" in st.session_state and st.session_state["optimization_results"]:
            st.markdown("---")
            st.markdown("**Top 3 Konfigurationen:**")
            
            top_configs = st.session_state["optimization_results"]
            
            # Zeige jede Konfiguration mit Score
            # AdvancedLayoutConfig ist bereits im Top-Level importiert
            for i, (config, score) in enumerate(top_configs, 1):
                # Falls serialisiert (JSON-String), zurückkonvertieren
                try:
                    if isinstance(config, str):
                        config = AdvancedLayoutConfig.from_json(config)
                except Exception:
                    # Fallback: leave as-is
                    pass

                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        # Beschreibung der Konfiguration
                        config_name = f"Konfiguration {i}"
                        if config.mounting_mode == "south":
                            config_desc = "Süd-Aufständerung"
                        elif config.mounting_mode == "east-west":
                            config_desc = "Ost-West-Aufständerung"
                        elif config.mounting_mode == "south-east":
                            config_desc = "Süd-Ost-Aufständerung"
                        elif config.use_garage and config.use_facade:
                            config_desc = "Gemischt (Garage + Fassade)"
                        else:
                            config_desc = "Benutzerdefiniert"
                        
                        st.markdown(f"**{i}. {config_desc}**")
                        st.caption(f"Score: {score:.1f}/100")
                    
                    with col2:
                        # Button: Konfiguration übernehmen
                        if st.button(
                            "Übernehmen",
                            key=f"apply_config_{i}",
                            use_container_width=True
                        ):
                            # Übernehme Konfiguration
                            st.session_state["pv3d_layout_json"] = config.to_json()
                            
                            # Aktualisiere UI-Werte
                            st.session_state["layout_mode"] = "Automatisch" if config.mode == "auto" else "Manuell"
                            st.session_state["use_garage"] = config.use_garage
                            st.session_state["use_facade"] = config.use_facade
                            st.session_state["mounting_mode"] = config.mounting_mode
                            
                            st.success(f"✓ Konfiguration {i} übernommen!")
                            st.rerun()
                    
                    # Zeige Details
                    with st.expander("Details anzeigen"):
                        st.write(f"- Aufständerung: {config.mounting_mode}")
                        st.write(f"- Garage: {'Ja' if config.use_garage else 'Nein'}")
                        st.write(f"- Fassade: {'Ja' if config.use_facade else 'Nein'}")
                        if config.mounting_mode == "custom":
                            st.write(f"- Azimuth: {config.custom_azimuth:.1f}°")
                            st.write(f"- Neigung: {config.custom_tilt:.1f}°")
    
        st.divider()

        # Verschattungs-Analyse (jetzt Teil von Analyse)
        st.markdown("**☀️ Verschattungs-Analyse**")
        st.caption("Analysieren Sie die Verschattung der Module zu verschiedenen Tageszeiten und Jahreszeiten.")
        
        enable_shading_analysis = st.checkbox(
            "Verschattungs-Analyse aktivieren",
            value=False,
            help="Färbt Module basierend auf Verschattungsgrad ein",
            key="enable_shading_checkbox"
        )
        
        if enable_shading_analysis:
            # Tageszeit-Slider
            hour_of_day = st.slider(
                "Tageszeit (Uhr)",
                min_value=6.0,
                max_value=20.0,
                value=12.0,
                step=0.5,
                help="Wählen Sie die Tageszeit für die Verschattungs-Analyse"
            )
            
            # Jahreszeit-Selectbox
            season_options = {
                "Sommer (21. Juni)": 172,
                "Winter (21. Dezember)": 355,
                "Frühling/Herbst (21. März/Sept.)": 80
            }
            
            selected_season = st.selectbox(
                "Jahreszeit",
                options=list(season_options.keys()),
                index=0,
                help="Wählen Sie die Jahreszeit für die Sonnenstandsberechnung"
            )
            
            day_of_year = season_options[selected_season]
            
            # Breitengrad-Eingabe
            latitude = st.number_input(
                "Breitengrad",
                min_value=-90.0,
                max_value=90.0,
                value=51.0,
                step=0.1,
                help="Breitengrad des Standorts (Standard: 51.0 für Deutschland)"
            )
            
            st.caption(
                f"💡 Sonnenstand wird für {selected_season} um {hour_of_day:.1f} Uhr "
                f"am Breitengrad {latitude:.1f}° berechnet."
            )
        else:
            # Default-Werte wenn deaktiviert
            hour_of_day = 12.0
            day_of_year = 172
            latitude = 51.0
        
        st.divider()
        
        # ========================================================================
        # NEU: SONNENVERLAUF-ANIMATION
        # ========================================================================
        st.markdown("**🌅 Sonnenverlauf-Animation**")
        st.caption("Animiere den Sonnenverlauf über den Tag und sehe die Verschattung in Echtzeit.")
        
        enable_sun_animation = st.checkbox(
            "Sonnenverlauf-Animation aktivieren",
            value=False,
            help="Zeigt eine Animation des Sonnenverlaufs über den Tag",
            key="enable_sun_animation_checkbox"
        )
        
        if enable_sun_animation:
            st.info("🎬 Animation wird nach dem Rendern verfügbar sein")
            
            # Animation-Einstellungen
            anim_speed = st.slider(
                "Animations-Geschwindigkeit",
                min_value=1,
                max_value=10,
                value=5,
                help="Höhere Werte = schnellere Animation"
            )
            
            anim_start_hour = st.slider(
                "Start-Uhrzeit",
                min_value=6.0,
                max_value=18.0,
                value=6.0,
                step=1.0,
                help="Startzeit der Animation"
            )
            
            anim_end_hour = st.slider(
                "End-Uhrzeit",
                min_value=8.0,
                max_value=20.0,
                value=20.0,
                step=1.0,
                help="Endzeit der Animation"
            )
        else:
            anim_speed = 5
            anim_start_hour = 6.0
            anim_end_hour = 20.0
        
        st.divider()
        
        # ========================================================================
        # NEU: ERTRAGS-HEATMAP
        # ========================================================================
        st.markdown("**🔥 Ertrags-Heatmap**")
        st.caption("Visualisiere das Ertragspotential jedes Moduls mit Farbcodierung.")
        
        enable_yield_heatmap = st.checkbox(
            "Ertrags-Heatmap aktivieren",
            value=False,
            help="Färbt Module basierend auf ihrem Ertragspotential (Grün=hoch, Rot=niedrig)",
            key="enable_yield_heatmap_checkbox"
        )
        
        if enable_yield_heatmap:
            st.info("📊 Heatmap wird nach dem Rendern angezeigt")
            
            # Heatmap-Einstellungen
            heatmap_metric = st.selectbox(
                "Heatmap-Metrik",
                options=["Jahresertrag (kWh)", "Verschattung (%)", "Effizienz (%)"],
                index=0,
                help="Wählen Sie die Metrik für die Farbcodierung"
            )
        else:
            heatmap_metric = "Jahresertrag (kWh)"
        
        st.divider()
        
        # ========================================================================
        # NEU: LIVE-ERTRAGSPROGNOSE
        # ========================================================================
        st.markdown("**⚡ Live-Ertragsprognose**")
        st.caption("Berechne den erwarteten Jahresertrag für die aktuelle Konfiguration.")
        
        enable_yield_forecast = st.checkbox(
            "Ertragsprognose aktivieren",
            value=False,
            help="Zeigt detaillierte Ertragsprognose für die aktuelle Konfiguration",
            key="enable_yield_forecast_checkbox"
        )
        
        if enable_yield_forecast:
            st.info("💡 Prognose wird nach dem Rendern berechnet")
            
            # Prognose-Einstellungen
            electricity_price = st.number_input(
                "Strompreis (€/kWh)",
                min_value=0.10,
                max_value=1.00,
                value=0.30,
                step=0.01,
                help="Aktueller Strompreis für Wirtschaftlichkeitsberechnung"
            )
            
            module_efficiency = st.slider(
                "Modul-Wirkungsgrad (%)",
                min_value=15,
                max_value=25,
                value=20,
                step=1,
                help="Wirkungsgrad der PV-Module"
            )
        else:
            electricity_price = 0.30
            module_efficiency = 20

    # ============================================================================
    # CHANGE DETECTION (vor Aktions-Buttons)
    # ============================================================================
    
    # Berechne aktuellen Settings-Hash für Change Detection
    import hashlib
    import json
    
    current_settings = {
        "building_length": building_length,
        "building_width": building_width,
        "building_height": building_height,
        "roof_type": selected_roof_type,
        "layout_mode": layout_mode,
        "mounting_type": mounting_type,
        "custom_azimuth": custom_azimuth,
        "custom_tilt": custom_tilt,
        "use_garage": use_garage,
        "use_facade": use_facade,
        "removed_indices": removed_indices,
        "enable_collision_detection": enable_collision_detection
    }
    
    current_settings_str = json.dumps(current_settings, sort_keys=True)
    current_settings_hash = hashlib.md5(current_settings_str.encode()).hexdigest()
    
    # Prüfe ob sich Settings geändert haben
    settings_changed = (
        st.session_state.get("pv3d_last_settings_hash") is not None and
        st.session_state.get("pv3d_last_settings_hash") != current_settings_hash
    )

    # ============================================================================
    # SIDEBAR - AKTIONS-BUTTONS
    # ============================================================================

    st.sidebar.divider()
    st.sidebar.subheader("🎬 Aktionen")

    # Auto-Update Checkbox
    auto_update = st.sidebar.checkbox(
        "🔄 Automatische Aktualisierung",
        value=st.session_state.get("pv3d_auto_update", False),
        help="Aktualisiert die 3D-Visualisierung automatisch bei Änderungen der Einstellungen",
        key="auto_update_checkbox"
    )
    
    # Speichere Auto-Update Präferenz
    st.session_state["pv3d_auto_update"] = auto_update
    
    # Zeige Hinweis wenn Auto-Update aktiv ist
    if auto_update and settings_changed:
        st.sidebar.info("⏳ Einstellungen geändert - Aktualisierung wird vorbereitet...")

    # Button: Visualisierung aktualisieren (nur wenn Auto-Update deaktiviert)
    btn_update = False
    if not auto_update:
        btn_update = st.sidebar.button(
            "🔄 Visualisierung aktualisieren",
            type="primary",
            use_container_width=True,
            help="Erstellt die 3D-Visualisierung mit den aktuellen Einstellungen",
            key="btn_update_viz"
        )
    else:
        st.sidebar.caption("💡 Auto-Update ist aktiv - manuelle Aktualisierung nicht erforderlich")

    # Button: Reset
    btn_reset = st.sidebar.button(
        "↺ Reset (Auto-Belegung)",
        use_container_width=True,
        help="Setzt alle Einstellungen zurück auf automatische Belegung",
        key="btn_reset_viz"
    )

    # Button: Layout speichern
    btn_save = st.sidebar.button(
        "💾 Layout speichern",
        use_container_width=True,
        help="Speichert die aktuelle Konfiguration im Session State",
        key="btn_save_layout"
    )

    # Button: Layout laden
    btn_load = st.sidebar.button(
        "📂 Layout laden",
        use_container_width=True,
        help="Lädt die gespeicherte Konfiguration aus dem Session State",
        key="btn_load_layout"
    )



    # ============================================================================
    # SESSION STATE MANAGEMENT
    # ============================================================================

    # Initialisiere Session State Variablen
    if "pv3d_layout_json" not in st.session_state:
        default_config = LayoutConfig()
        st.session_state["pv3d_layout_json"] = default_config.to_json()

    if "pv3d_last_rendered" not in st.session_state:
        st.session_state["pv3d_last_rendered"] = False

    # NICHT in session_state speichern - pyvista.Plotter ist nicht serialisierbar
    # Stattdessen: Plotter wird jedes Mal neu erstellt wenn nötig
    
    # Initialisiere Modul-Auswahl Session State
    if "pv3d_selected_modules" not in st.session_state:
        st.session_state["pv3d_selected_modules"] = []
    
    # Initialisiere Auto-Update und Debouncing State
    if "pv3d_auto_update" not in st.session_state:
        st.session_state["pv3d_auto_update"] = False
    
    if "pv3d_last_settings_hash" not in st.session_state:
        st.session_state["pv3d_last_settings_hash"] = None


    # Button-Logik: Reset
    if btn_reset:
        # Setze auf Default-Konfiguration zurück
        default_config = LayoutConfig(
            mode="auto",
            use_garage=False,
            use_facade=False,
            removed_indices=[],
            garage_dims=(6.0, 3.0, 3.0),
            offset_main_xy=(0.0, 0.0),
            offset_garage_xy=(0.0, 0.0)
        )
        st.session_state["pv3d_layout_json"] = default_config.to_json()
        st.session_state["pv3d_last_rendered"] = False
        # Plotter wird automatisch neu erstellt - keine Speicherung nötig
        st.sidebar.success("✓ Einstellungen zurückgesetzt")
        st.rerun()


    # Button-Logik: Layout speichern
    if btn_save:
        # Erstelle aktuelle Konfiguration
        # Konvertiere mounting_type zu internem Format
        mounting_mode_map = {
            "Süd": "south",
            "Ost-West": "east-west",
            "Süd-Ost": "south-east",
            "Süd-West": "south-west",
            "Individuell": "custom"
        }
        mounting_mode = mounting_mode_map.get(mounting_type, "south")
        
        if enable_collision_detection or enable_shading_analysis:
            current_config = AdvancedLayoutConfig(
                mode="auto" if layout_mode == "Automatisch" else "manual",
                use_garage=use_garage,
                use_facade=use_facade,
                removed_indices=removed_indices,
                garage_dims=(6.0, 3.0, 3.0),
                offset_main_xy=(0.0, 0.0),
                offset_garage_xy=(0.0, 0.0),
                mounting_mode=mounting_mode,
                custom_azimuth=custom_azimuth,
                custom_tilt=custom_tilt,
                enable_collision_detection=enable_collision_detection,
                enable_shading_analysis=enable_shading_analysis
            )
        else:
            current_config = AdvancedLayoutConfig(
                mode="auto" if layout_mode == "Automatisch" else "manual",
                use_garage=use_garage,
                use_facade=use_facade,
                removed_indices=removed_indices,
                garage_dims=(6.0, 3.0, 3.0),
                offset_main_xy=(0.0, 0.0),
                offset_garage_xy=(0.0, 0.0),
                mounting_mode=mounting_mode,
                custom_azimuth=custom_azimuth,
                custom_tilt=custom_tilt,
                enable_collision_detection=False,
                enable_shading_analysis=False
            )
        
        # Speichere in Session State
        st.session_state["pv3d_layout_json"] = current_config.to_json()
        st.sidebar.success("✓ Layout gespeichert")


    # Button-Logik: Layout laden
    if btn_load:
        try:
            # Versuche zuerst AdvancedLayoutConfig zu laden
            try:
                loaded_config = AdvancedLayoutConfig.from_json(
                    st.session_state["pv3d_layout_json"]
                )
                config_type = "Erweitert"
            except (ValueError, KeyError):
                # Fallback auf LayoutConfig
                loaded_config = LayoutConfig.from_json(
                    st.session_state["pv3d_layout_json"]
                )
                config_type = "Standard"
            
            st.sidebar.success(f"✓ Layout geladen ({config_type})")
            st.sidebar.info(
                f"Modus: {loaded_config.mode}, "
                f"Garage: {loaded_config.use_garage}, "
                f"Fassade: {loaded_config.use_facade}"
            )
        except (ValueError, KeyError) as e:
            st.sidebar.error(f"❌ Fehler beim Laden: {e}")



    # ============================================================================
    # 3D-RENDERING-LOGIK
    # ============================================================================

    # Prüfe Render-Trigger
    # Rendere wenn:
    # 1. Button geklickt wurde
    # 2. Noch nie gerendert wurde
    # 3. Auto-Update aktiv ist UND Settings haben sich geändert
    should_render = (
        btn_update or 
        not st.session_state["pv3d_last_rendered"] or
        (auto_update and settings_changed)
    )

    if should_render:
        # Zeige Loading-Spinner während Neuberechnung
        with st.spinner("🔄 Erstelle 3D-Visualisierung..."):
            try:
                # Erstelle BuildingDims aus Eingabefeldern
                dims = BuildingDims(
                    length_m=building_length,
                    width_m=building_width,
                    wall_height_m=building_height
                )
                
                # Erstelle LayoutConfig aus Sidebar-Werten
                # Verwende AdvancedLayoutConfig wenn Kollisionserkennung oder Verschattungsanalyse aktiviert ist
                # Konvertiere mounting_type zu internem Format
                mounting_mode_map = {
                    "Süd": "south",
                    "Ost-West": "east-west",
                    "Süd-Ost": "south-east",
                    "Süd-West": "south-west",
                    "Individuell": "custom"
                }
                mounting_mode = mounting_mode_map.get(mounting_type, "south")
                
                if enable_collision_detection or enable_shading_analysis:
                    layout_config = AdvancedLayoutConfig(
                        mode="auto" if layout_mode == "Automatisch" else "manual",
                        use_garage=use_garage,
                        use_facade=use_facade,
                        removed_indices=removed_indices,
                        garage_dims=(6.0, 3.0, 3.0),
                        offset_main_xy=(0.0, 0.0),
                        offset_garage_xy=(0.0, 0.0),
                        mounting_mode=mounting_mode,
                        custom_azimuth=custom_azimuth,
                        custom_tilt=custom_tilt,
                        enable_collision_detection=enable_collision_detection,
                        enable_shading_analysis=enable_shading_analysis
                    )
                else:
                    # Verwende AdvancedLayoutConfig auch für normale Fälle, um mounting_mode zu unterstützen
                    layout_config = AdvancedLayoutConfig(
                        mode="auto" if layout_mode == "Automatisch" else "manual",
                        use_garage=use_garage,
                        use_facade=use_facade,
                        removed_indices=removed_indices,
                        garage_dims=(6.0, 3.0, 3.0),
                        offset_main_xy=(0.0, 0.0),
                        offset_garage_xy=(0.0, 0.0),
                        mounting_mode=mounting_mode,
                        custom_azimuth=custom_azimuth,
                        custom_tilt=custom_tilt,
                        enable_collision_detection=False,
                        enable_shading_analysis=False
                    )
                
                # Hole ausgewählte Module aus Session State
                selected_modules = st.session_state.get("pv3d_selected_modules", [])
                
                # Berechne Sonnenposition für Shading-Analyse (falls aktiviert)
                sun_azimuth, sun_elevation = None, None
                if enable_shading_analysis:
                    sun_azimuth, sun_elevation = calculate_sun_position(
                        latitude=latitude,
                        day_of_year=day_of_year,
                        hour=hour_of_day
                    )
                
                # Speichere Scene-Daten (keine Plotter-Objekte mehr!)
                st.session_state["_pv3d_scene_data"] = {
                    "collisions": [],  # Kollisionserkennung später hinzufügen
                    "shading_values": {},  # Verschattungswerte später hinzufügen
                    "sun_position": (sun_azimuth, sun_elevation) if enable_shading_analysis else None,
                    "building_dims": {
                        "length_m": dims.length_m,
                        "width_m": dims.width_m,
                        "wall_height_m": dims.wall_height_m
                    },
                    "layout_config_json": layout_config.to_json() if hasattr(layout_config, 'to_json') else None,
                    "roof_type": selected_roof_type,
                    "roof_covering": roof_covering,
                    "project_data": project_data,
                    "module_quantity": module_quantity,
                    "selected_modules": selected_modules
                }
                st.session_state["pv3d_last_rendered"] = True
                
                # Speichere aktuellen Settings-Hash
                st.session_state["pv3d_last_settings_hash"] = current_settings_hash
                
                # Zeige Erfolgsmeldung
                if auto_update:
                    st.success("✓ 3D-Visualisierung automatisch aktualisiert")
                else:
                    st.success("✓ 3D-Visualisierung erfolgreich erstellt")
                
            except Exception as e:
                st.error(f"❌ Fehler beim Erstellen der 3D-Visualisierung: {e}")
                st.info("Bitte überprüfen Sie Ihre Eingaben und versuchen Sie es erneut.")
                # Lösche Scene-Daten bei Fehler
                if "_pv3d_scene_data" in st.session_state:
                    del st.session_state["_pv3d_scene_data"]
                st.session_state["pv3d_last_rendered"] = False



    # ============================================================================
    # HAUPTBEREICH - 2-SPALTEN-LAYOUT
    # ============================================================================

    # Erstelle Spalten mit Verhältnis 3:2 (60%:40%)
    col_viewer, col_status = st.columns([3, 2])

    # Linke Spalte: 3D-Viewer
    with col_viewer:
        with st.expander("🎨 3D-Ansicht", expanded=True):
            # Prüfe ob Scene-Daten vorhanden sind
            scene_data = st.session_state.get("_pv3d_scene_data")
        
            if scene_data is not None:
                try:
                    # Rekonstruiere BuildingDims
                    bd = scene_data["building_dims"]
                    dims = BuildingDims(
                        length_m=bd["length_m"],
                        width_m=bd["width_m"],
                        wall_height_m=bd["wall_height_m"]
                    )
                    
                    # Rekonstruiere LayoutConfig
                    layout_config_json = scene_data.get("layout_config_json")
                    if layout_config_json:
                        try:
                            layout_config = AdvancedLayoutConfig.from_json(layout_config_json)
                        except:
                            layout_config = LayoutConfig.from_json(layout_config_json)
                    else:
                        layout_config = LayoutConfig()
                    
                    # Hole module_quantity
                    module_quantity = scene_data.get("module_quantity", 20)
                    
                    # Erstelle Plotly 3D-Szene
                    fig = build_plotly_scene(
                        project_data=scene_data.get("project_data", {}),
                        dims=dims,
                        roof_type=scene_data.get("roof_type", "Flachdach"),
                        module_quantity=module_quantity,
                        layout_config=layout_config,
                        selected_modules=scene_data.get("selected_modules", [])
                    )
                    
                    # Zeige Plotly Figure in Streamlit
                    st.plotly_chart(fig, use_container_width=True)
                    
                except Exception as e:
                    st.error(f"❌ Fehler beim Anzeigen der 3D-Visualisierung: {e}")
                    import traceback
                    st.code(traceback.format_exc())
            else:
                st.info("👆 Klicken Sie auf '🎨 3D-Visualisierung erstellen/aktualisieren' um die 3D-Ansicht zu generieren.")

    # Rechte Spalte: Status-Metriken
    with col_status:
        with st.expander("📊 Status", expanded=False):
            # Berechne geschätzte Dachkapazität (gecacht)
            estimated_capacity = _calculate_roof_capacity(
                building_length, 
                building_width, 
                selected_roof_type
            )
            
            # Hole Modulanzahl aus Scene-Daten
            scene_data = st.session_state.get("_pv3d_scene_data", {})
            total_placed = scene_data.get("module_quantity", 0)
            
            # Berechne fehlende Module
            missing_modules = max(0, module_quantity - total_placed)
            
            # Zeige Metriken
            st.metric(
                label="Gewählte Module",
                value=module_quantity,
                help="Anzahl der Module aus der Bedarfsanalyse"
            )
            
            st.metric(
                label="Platzierte Module",
                value=total_placed,
                help="Anzahl der tatsächlich platzierten Module"
            )
            
            st.metric(
                label="Geschätzte Dachkapazität",
                value=estimated_capacity,
                help="Geschätzte maximale Anzahl Module auf dem Hauptdach"
            )
            
            st.divider()
            
            # Zeige Erfolg
            if total_placed > 0:
                st.success(
                    f"✅ {total_placed} Module wurden visualisiert!"
                )
            
            # Kollisionserkennung-Status
            collision_pairs = scene_data.get("collisions", [])
            if collision_pairs and len(collision_pairs) > 0:
                st.divider()
                st.error(
                    f"⚠️ **Kollisionen erkannt: {len(collision_pairs)}**\n\n"
                    f"Kollidierende Modul-Paare:\n"
                )
                
                # Zeige erste 10 Kollisionen
                for i, (idx1, idx2) in enumerate(collision_pairs[:10]):
                    st.text(f"  • Module {idx1} ↔ {idx2}")
                
                if len(collision_pairs) > 10:
                    st.text(f"  ... und {len(collision_pairs) - 10} weitere")
                
                st.caption(
                    "💡 **Tipp:** Passen Sie die Modul-Positionen an oder entfernen Sie "
                    "kollidierende Module im manuellen Modus."
                )
            
            # Verschattungs-Analyse-Status
            shading_values = scene_data.get("shading_values", {})
            if shading_values and len(shading_values) > 0:
                st.divider()
                
                # Berechne Statistiken
                shading_list = list(shading_values.values())
                min_shading = min(shading_list)
                max_shading = max(shading_list)
                avg_shading = sum(shading_list) / len(shading_list)
                
                # Zähle Module nach Verschattungsgrad
                no_shading = sum(1 for v in shading_list if v < 10.0)
                partial_shading = sum(1 for v in shading_list if 10.0 <= v < 75.0)
                full_shading = sum(1 for v in shading_list if v >= 75.0)
                
                # Hole Sonnenposition
                sun_position = scene_data.get("sun_position", (180.0, 45.0))
                sun_azimuth, sun_elevation = sun_position
                
                st.info(
                    f"☀️ **Verschattungs-Analyse**\n\n"
                    f"**Sonnenstand:**\n"
                    f"- Azimuth: {sun_azimuth:.1f}° (0°=N, 90°=O, 180°=S, 270°=W)\n"
                    f"- Elevation: {sun_elevation:.1f}° (0°=Horizont, 90°=Zenit)\n\n"
                    f"**Verschattungsgrad:**\n"
                    f"- Minimum: {min_shading:.1f}%\n"
                    f"- Maximum: {max_shading:.1f}%\n"
                    f"- Durchschnitt: {avg_shading:.1f}%\n\n"
                    f"**Module nach Verschattung:**\n"
                    f"- 🟢 Keine (<10%): {no_shading}\n"
                    f"- 🟡 Teilweise (10-75%): {partial_shading}\n"
                    f"- 🔴 Stark (≥75%): {full_shading}"
                )
                
                # Zeige Tabelle mit Verschattungswerten
                st.divider()
                st.markdown("**📊 Detaillierte Verschattungswerte**")
                st.caption("Verschattungsgrad pro Modul:")
                
                # Erstelle DataFrame für bessere Darstellung
                import pandas as pd
                
                # Sortiere nach Verschattungsgrad (absteigend)
                sorted_shading = sorted(
                    shading_values.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
                
                # Zeige Top 20 am stärksten verschattete Module
                display_count = min(20, len(sorted_shading))
                
                df_data = []
                for idx, shading_pct in sorted_shading[:display_count]:
                    # Bestimme Farb-Emoji
                    if shading_pct < 10.0:
                        emoji = "🟢"
                    elif shading_pct < 75.0:
                        emoji = "🟡"
                    else:
                        emoji = "🔴"
                    
                    df_data.append({
                        "Modul": f"{emoji} #{idx}",
                        "Verschattung": f"{shading_pct:.1f}%"
                    })
                
                if df_data:
                    df = pd.DataFrame(df_data)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    if len(sorted_shading) > display_count:
                        st.caption(f"... und {len(sorted_shading) - display_count} weitere Module")
                else:
                    st.caption("Keine Verschattungsdaten verfügbar.")
            
            # Zusätzliche Informationen
            st.info(
                f"**Gebäudedaten:**\n"
                f"- Dachform: {selected_roof_type}\n"
                f"- Ausrichtung: {orientation}\n"
                f"- Dachneigung: {roof_inclination_deg}°\n"
                f"- Dachdeckung: {roof_covering}"
            )
            
            # ====================================================================
            # NEU: LIVE-ERTRAGSPROGNOSE ANZEIGE
            # ====================================================================
            if enable_yield_forecast and total_placed > 0:
                st.divider()
                st.subheader("⚡ Ertragsprognose")
                
                # Berechne Prognose
                try:
                    # Verwende Durchschnittswerte für Azimuth/Tilt
                    avg_azimuth = 0.0  # Süd
                    avg_tilt = roof_inclination_deg if selected_roof_type != "Flachdach" else 15.0
                    
                    forecast = _calculate_yield_forecast(
                        module_count=total_placed,
                        latitude=latitude if enable_shading_analysis else 51.0,
                        azimuth=avg_azimuth,
                        tilt=avg_tilt,
                        efficiency=module_efficiency
                    )
                    
                    # Zeige Metriken
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric(
                            "Jahresertrag",
                            f"{forecast['yearly_kwh']:,.0f} kWh",
                            help="Erwarteter Jahresertrag der Anlage"
                        )
                        
                        st.metric(
                            "Anlagengröße",
                            f"{forecast['system_kwp']:.2f} kWp",
                            help="Installierte Leistung"
                        )
                    
                    with col2:
                        st.metric(
                            "Tagesertrag Ø",
                            f"{forecast['daily_avg_kwh']:.1f} kWh",
                            help="Durchschnittlicher Tagesertrag"
                        )
                        
                        # Berechne Ersparnis
                        yearly_savings = forecast['yearly_kwh'] * electricity_price
                        st.metric(
                            "Ersparnis/Jahr",
                            f"{yearly_savings:,.0f} €",
                            help=f"Bei {electricity_price:.2f} €/kWh"
                        )
                    
                    # Zeige Optimierungs-Faktoren
                    st.divider()
                    st.markdown("**📊 Optimierungs-Faktoren**")
                    
                    st.write(f"**Azimuth-Faktor:** {forecast['azimuth_factor']:.1%}")
                    st.progress(forecast['azimuth_factor'])
                    
                    st.write(f"**Neigungs-Faktor:** {forecast['tilt_factor']:.1%}")
                    st.progress(forecast['tilt_factor'])
                    
                    st.write(f"**Standort-Faktor:** {forecast['latitude_factor']:.1%}")
                    st.progress(forecast['latitude_factor'])
                    
                    st.caption("💡 Werte nahe 100% bedeuten optimale Bedingungen")
                    
                except Exception as e:
                    st.error(f"❌ Fehler bei Ertragsprognose: {e}")
            
            # ====================================================================
            # NEU: ERTRAGS-HEATMAP ANZEIGE
            # ====================================================================
            if enable_yield_heatmap and total_placed > 0:
                st.divider()
                st.subheader("🔥 Ertrags-Heatmap")
                
                try:
                    # Hole Modul-Positionen
                    from utils.pv3d import grid_positions
                    positions_2d = grid_positions(
                        area_length=building_length,
                        area_width=building_width
                    )
                    
                    base_z = building_height + 0.12
                    positions_3d = [(x, y, base_z) for x, y in positions_2d[:total_placed]]
                    
                    # Hole Transformationen
                    try:
                        current_config = AdvancedLayoutConfig.from_json(
                            st.session_state.get("pv3d_layout_json", "{}")
                        )
                        transforms = current_config.module_transforms
                    except:
                        transforms = {}
                    
                    # Berechne Heatmap
                    module_yields = _calculate_module_yield_heatmap(
                        module_positions=positions_3d,
                        module_transforms=transforms,
                        latitude=latitude if enable_shading_analysis else 51.0,
                        efficiency=module_efficiency
                    )
                    
                    if module_yields:
                        # Statistiken
                        yields = list(module_yields.values())
                        min_yield = min(yields)
                        max_yield = max(yields)
                        avg_yield = sum(yields) / len(yields)
                        
                        st.write(f"**Ertragsspanne:** {min_yield:.0f} - {max_yield:.0f} kWh/Jahr")
                        st.write(f"**Durchschnitt:** {avg_yield:.0f} kWh/Jahr")
                        
                        # Zeige Top 5 und Bottom 5 Module
                        sorted_modules = sorted(module_yields.items(), key=lambda x: x[1], reverse=True)
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.caption("**🏆 Top 5 Module:**")
                            for idx, yield_val in sorted_modules[:5]:
                                st.text(f"Modul #{idx}: {yield_val:.0f} kWh/Jahr")
                        
                        with col2:
                            st.caption("**⚠️ Schwächste 5 Module:**")
                            for idx, yield_val in sorted_modules[-5:]:
                                st.text(f"Modul #{idx}: {yield_val:.0f} kWh/Jahr")
                        
                        st.caption("💡 Tipp: Schwache Module ggf. neu positionieren oder entfernen")
                    
                except Exception as e:
                    st.error(f"❌ Fehler bei Heatmap: {e}")
            
            # ====================================================================
            # NEU: SONNENVERLAUF-ANIMATION STEUERUNG
            # ====================================================================
            if enable_sun_animation:
                st.divider()
                st.subheader("🌅 Sonnenverlauf")
                
                st.info("🎬 Animation-Steuerung wird nach dem Rendern verfügbar sein")
                
                # Placeholder für Animation-Controls
                st.caption(f"⏱️ Animation: {anim_start_hour:.0f}:00 - {anim_end_hour:.0f}:00 Uhr")
                st.caption(f"⚡ Geschwindigkeit: {anim_speed}x")



    # ============================================================================
    # EXPORT-BEREICH
    # ============================================================================

    st.divider()

    st.subheader("💾 Export")

    # Erstelle 3 Spalten für Export-Buttons
    export_col1, export_col2, export_col3 = st.columns(3)

    # Screenshot (PNG) Export
    with export_col1:
        if st.button("📸 Screenshot (PNG)", use_container_width=True):
            try:
                with st.spinner("Erstelle Screenshot..."):
                    # Erstelle BuildingDims und LayoutConfig
                    dims = BuildingDims(
                        length_m=building_length,
                        width_m=building_width,
                        wall_height_m=building_height
                    )
                    
                    # Konvertiere mounting_type zu internem Format
                    mounting_mode_map = {
                        "Süd": "south",
                        "Ost-West": "east-west",
                        "Süd-Ost": "south-east",
                        "Süd-West": "south-west",
                        "Individuell": "custom"
                    }
                    mounting_mode = mounting_mode_map.get(mounting_type, "south")
                    
                    layout_config = AdvancedLayoutConfig(
                        mode="auto" if layout_mode == "Automatisch" else "manual",
                        use_garage=use_garage,
                        use_facade=use_facade,
                        removed_indices=removed_indices,
                        garage_dims=(6.0, 3.0, 3.0),
                        offset_main_xy=(0.0, 0.0),
                        offset_garage_xy=(0.0, 0.0),
                        mounting_mode=mounting_mode,
                        custom_azimuth=custom_azimuth,
                        custom_tilt=custom_tilt,
                        enable_collision_detection=False,
                        enable_shading_analysis=False
                    )
                    
                    # Rufe render_image_bytes() auf
                    png_bytes = render_image_bytes(
                        project_data=project_data,
                        dims=dims,
                        roof_type=selected_roof_type,
                        module_quantity=module_quantity,
                        layout_config=layout_config
                    )
                    
                    if png_bytes:
                        # Zeige Download-Button
                        st.download_button(
                            label="⬇️ PNG herunterladen",
                            data=png_bytes,
                            file_name="pv_3d_visualisierung.png",
                            mime="image/png",
                            use_container_width=True
                        )
                        st.success("✓ Screenshot erstellt")
                    else:
                        st.error("❌ Screenshot konnte nicht erstellt werden")
                        
            except Exception as e:
                st.error(f"❌ Fehler beim Erstellen des Screenshots: {e}")

    # STL Export
    with export_col2:
        if st.button("📦 STL exportieren", use_container_width=True):
            try:
                with st.spinner("Erstelle STL-Datei..."):
                    # Erstelle BuildingDims und LayoutConfig
                    dims = BuildingDims(
                        length_m=building_length,
                        width_m=building_width,
                        wall_height_m=building_height
                    )
                    
                    # Konvertiere mounting_type zu internem Format
                    mounting_mode_map = {
                        "Süd": "south",
                        "Ost-West": "east-west",
                        "Süd-Ost": "south-east",
                        "Süd-West": "south-west",
                        "Individuell": "custom"
                    }
                    mounting_mode = mounting_mode_map.get(mounting_type, "south")
                    
                    layout_config = AdvancedLayoutConfig(
                        mode="auto" if layout_mode == "Automatisch" else "manual",
                        use_garage=use_garage,
                        use_facade=use_facade,
                        removed_indices=removed_indices,
                        garage_dims=(6.0, 3.0, 3.0),
                        offset_main_xy=(0.0, 0.0),
                        offset_garage_xy=(0.0, 0.0),
                        mounting_mode=mounting_mode,
                        custom_azimuth=custom_azimuth,
                        custom_tilt=custom_tilt,
                        enable_collision_detection=False,
                        enable_shading_analysis=False
                    )
                    
                    # Rufe export_stl() auf
                    import tempfile
                    import os
                    
                    # Erstelle temporäre Datei für STL
                    with tempfile.NamedTemporaryFile(mode='wb', suffix='.stl', delete=False) as tmp_file:
                        tmp_filepath = tmp_file.name
                    
                    # Exportiere STL
                    success = export_stl(
                        project_data=project_data,
                        dims=dims,
                        roof_type=selected_roof_type,
                        module_quantity=module_quantity,
                        layout_config=layout_config,
                        filepath=tmp_filepath
                    )
                    
                    # Lese STL-Bytes
                    stl_bytes = None
                    if success and os.path.exists(tmp_filepath):
                        with open(tmp_filepath, 'rb') as f:
                            stl_bytes = f.read()
                        # Lösche temporäre Datei
                        try:
                            os.unlink(tmp_filepath)
                        except:
                            pass
                    
                    if stl_bytes:
                        # Zeige Download-Button
                        st.download_button(
                            label="⬇️ STL herunterladen",
                            data=stl_bytes,
                            file_name="pv_3d_modell.stl",
                            mime="application/octet-stream",
                            use_container_width=True
                        )
                        st.success("✓ STL-Datei erstellt")
                    else:
                        st.error("❌ STL-Export fehlgeschlagen")
                        
            except Exception as e:
                st.error(f"❌ Fehler beim STL-Export: {e}")

    # glTF Export
    with export_col3:
        if st.button("🎨 glTF (.glb)", use_container_width=True):
            try:
                with st.spinner("Erstelle glTF-Datei..."):
                    # Erstelle BuildingDims und LayoutConfig
                    dims = BuildingDims(
                        length_m=building_length,
                        width_m=building_width,
                        wall_height_m=building_height
                    )
                    
                    # Konvertiere mounting_type zu internem Format
                    mounting_mode_map = {
                        "Süd": "south",
                        "Ost-West": "east-west",
                        "Süd-Ost": "south-east",
                        "Süd-West": "south-west",
                        "Individuell": "custom"
                    }
                    mounting_mode = mounting_mode_map.get(mounting_type, "south")
                    
                    layout_config = AdvancedLayoutConfig(
                        mode="auto" if layout_mode == "Automatisch" else "manual",
                        use_garage=use_garage,
                        use_facade=use_facade,
                        removed_indices=removed_indices,
                        garage_dims=(6.0, 3.0, 3.0),
                        offset_main_xy=(0.0, 0.0),
                        offset_garage_xy=(0.0, 0.0),
                        mounting_mode=mounting_mode,
                        custom_azimuth=custom_azimuth,
                        custom_tilt=custom_tilt,
                        enable_collision_detection=False,
                        enable_shading_analysis=False
                    )
                    
                    # Rufe export_gltf() auf
                    import tempfile
                    import os
                    
                    # Erstelle temporäre Datei für glTF
                    with tempfile.NamedTemporaryFile(mode='wb', suffix='.glb', delete=False) as tmp_file:
                        tmp_filepath = tmp_file.name
                    
                    # Exportiere glTF
                    success = export_gltf(
                        project_data=project_data,
                        dims=dims,
                        roof_type=selected_roof_type,
                        module_quantity=module_quantity,
                        layout_config=layout_config,
                        filepath=tmp_filepath
                    )
                    
                    # Lese glTF-Bytes
                    gltf_bytes = None
                    if success and os.path.exists(tmp_filepath):
                        with open(tmp_filepath, 'rb') as f:
                            gltf_bytes = f.read()
                        # Lösche temporäre Datei
                        try:
                            os.unlink(tmp_filepath)
                        except:
                            pass
                    
                    if gltf_bytes:
                        # Zeige Download-Button
                        st.download_button(
                            label="⬇️ glTF herunterladen",
                            data=gltf_bytes,
                            file_name="pv_3d_modell.glb",
                            mime="model/gltf-binary",
                            use_container_width=True
                        )
                        st.success("✓ glTF-Datei erstellt")
                    else:
                        st.error("❌ glTF-Export fehlgeschlagen")
                        
            except Exception as e:
                st.error(f"❌ Fehler beim glTF-Export: {e}")

    # ============================================================================
    # ERWEITERTE EXPORT-FUNKTIONEN (TASK 18.5)
    # ============================================================================

    st.divider()

    with st.expander("📦 Erweiterte Exports", expanded=False):
        st.markdown("### Zusätzliche Export-Optionen")
        
        # Importiere neue Export-Funktionen
        from utils.pv3d import (
            export_module_details_csv,
            export_layout_json,
            import_layout_json,
            export_multi_view_screenshots,
            export_360_animation
        )
        
        # Erstelle 2 Spalten für erweiterte Exports
        adv_col1, adv_col2 = st.columns(2)
        
        # ====================================================================
        # CSV-EXPORT (Modul-Details)
        # ====================================================================
        with adv_col1:
            st.subheader("📊 CSV-Export")
            st.caption("Exportiert Modul-Details (Position, Azimuth, Neigung)")
            
            if st.button("📄 CSV erstellen", key="csv_export", use_container_width=True):
                try:
                    with st.spinner("Erstelle CSV-Datei..."):
                        # Erstelle BuildingDims und LayoutConfig
                        dims = BuildingDims(
                            length_m=building_length,
                            width_m=building_width,
                            wall_height_m=building_height
                        )
                        
                        # Konvertiere mounting_type zu internem Format
                        mounting_mode_map = {
                            "Süd": "south",
                            "Ost-West": "east-west",
                            "Süd-Ost": "south-east",
                            "Süd-West": "south-west",
                            "Individuell": "custom"
                        }
                        mounting_mode = mounting_mode_map.get(mounting_type, "south")
                        
                        layout_config = AdvancedLayoutConfig(
                            mode="auto" if layout_mode == "Automatisch" else "manual",
                            use_garage=use_garage,
                            use_facade=use_facade,
                            removed_indices=removed_indices,
                            garage_dims=(6.0, 3.0, 3.0),
                            offset_main_xy=(0.0, 0.0),
                            offset_garage_xy=(0.0, 0.0),
                            mounting_mode=mounting_mode,
                            custom_azimuth=custom_azimuth,
                            custom_tilt=custom_tilt,
                            enable_collision_detection=False,
                            enable_shading_analysis=False
                        )
                        
                        # Berechne Modul-Positionen
                        from utils.pv3d import grid_positions
                        positions_2d = grid_positions(
                            area_length=building_length,
                            area_width=building_width
                        )
                        
                        # Konvertiere zu 3D-Positionen
                        base_z = building_height + 0.12  # Auf Dach
                        positions_3d = [(x, y, base_z) for x, y in positions_2d[:module_quantity]]
                        
                        # Erstelle CSV
                        csv_string = export_module_details_csv(
                            module_transforms=layout_config.module_transforms,
                            module_positions=positions_3d,
                            shading_values=None,  # Optional: Verschattungswerte
                            filepath=None  # Nur String zurückgeben
                        )
                        
                        if csv_string:
                            # Zeige Download-Button
                            st.download_button(
                                label="⬇️ CSV herunterladen",
                                data=csv_string,
                                file_name="pv_module_details.csv",
                                mime="text/csv",
                                use_container_width=True
                            )
                            st.success("✓ CSV-Datei erstellt")
                        else:
                            st.error("❌ CSV-Export fehlgeschlagen")
                            
                except Exception as e:
                    st.error(f"❌ Fehler beim CSV-Export: {e}")
        
        # ====================================================================
        # JSON-EXPORT/IMPORT (Layout-Konfiguration)
        # ====================================================================
        with adv_col2:
            st.subheader("💾 JSON-Export/Import")
            st.caption("Speichert/Lädt komplette Layout-Konfiguration")
            
            # JSON-Export
            if st.button("📥 JSON exportieren", key="json_export", use_container_width=True):
                try:
                    with st.spinner("Erstelle JSON-Datei..."):
                        # Konvertiere mounting_type zu internem Format
                        mounting_mode_map = {
                            "Süd": "south",
                            "Ost-West": "east-west",
                            "Süd-Ost": "south-east",
                            "Süd-West": "south-west",
                            "Individuell": "custom"
                        }
                        mounting_mode = mounting_mode_map.get(mounting_type, "south")
                        
                        layout_config = AdvancedLayoutConfig(
                            mode="auto" if layout_mode == "Automatisch" else "manual",
                            use_garage=use_garage,
                            use_facade=use_facade,
                            removed_indices=removed_indices,
                            garage_dims=(6.0, 3.0, 3.0),
                            offset_main_xy=(0.0, 0.0),
                            offset_garage_xy=(0.0, 0.0),
                            mounting_mode=mounting_mode,
                            custom_azimuth=custom_azimuth,
                            custom_tilt=custom_tilt,
                            enable_collision_detection=False,
                            enable_shading_analysis=False
                        )
                        
                        # Exportiere JSON
                        json_string = export_layout_json(
                            layout_config=layout_config,
                            filepath=None  # Nur String zurückgeben
                        )
                        
                        if json_string:
                            # Zeige Download-Button
                            st.download_button(
                                label="⬇️ JSON herunterladen",
                                data=json_string,
                                file_name="pv_layout_config.json",
                                mime="application/json",
                                use_container_width=True
                            )
                            st.success("✓ JSON-Datei erstellt")
                        else:
                            st.error("❌ JSON-Export fehlgeschlagen")
                            
                except Exception as e:
                    st.error(f"❌ Fehler beim JSON-Export: {e}")
            
            # JSON-Import
            st.caption("JSON-Konfiguration laden:")
            uploaded_json = st.file_uploader(
                "JSON-Datei hochladen",
                type=['json'],
                key="json_import",
                label_visibility="collapsed"
            )
            
            if uploaded_json is not None:
                try:
                    # Lese JSON-Datei
                    json_string = uploaded_json.read().decode('utf-8')
                    
                    # Importiere Konfiguration
                    imported_config = import_layout_json(json_string=json_string)
                    
                    # Speichere in Session State
                    st.session_state["pv3d_layout_json"] = imported_config.to_json()
                    
                    st.success("✓ JSON-Konfiguration geladen! Klicken Sie auf 'Layout laden' in der Sidebar.")
                    
                except Exception as e:
                    st.error(f"❌ Fehler beim JSON-Import: {e}")
        
        st.divider()
        
        # ====================================================================
        # MULTI-VIEW SCREENSHOTS
        # ====================================================================
        st.subheader("📷 Multi-View Screenshots")
        st.caption("Erstellt Screenshots aus 4 Perspektiven (Isometrisch, Top, Süd, Ost)")
        
        if st.button("🎬 Multi-View erstellen", key="multiview_export", use_container_width=True):
            try:
                with st.spinner("Erstelle Multi-View Screenshots... Dies kann einige Sekunden dauern."):
                    # Erstelle BuildingDims und LayoutConfig
                    dims = BuildingDims(
                        length_m=building_length,
                        width_m=building_width,
                        wall_height_m=building_height
                    )
                    
                    # Konvertiere mounting_type zu internem Format
                    mounting_mode_map = {
                        "Süd": "south",
                        "Ost-West": "east-west",
                        "Süd-Ost": "south-east",
                        "Süd-West": "south-west",
                        "Individuell": "custom"
                    }
                    mounting_mode = mounting_mode_map.get(mounting_type, "south")
                    
                    layout_config = AdvancedLayoutConfig(
                        mode="auto" if layout_mode == "Automatisch" else "manual",
                        use_garage=use_garage,
                        use_facade=use_facade,
                        removed_indices=removed_indices,
                        garage_dims=(6.0, 3.0, 3.0),
                        offset_main_xy=(0.0, 0.0),
                        offset_garage_xy=(0.0, 0.0),
                        mounting_mode=mounting_mode,
                        custom_azimuth=custom_azimuth,
                        custom_tilt=custom_tilt,
                        enable_collision_detection=False,
                        enable_shading_analysis=False
                    )
                    
                    # Erstelle temporäres Verzeichnis für ZIP
                    import tempfile
                    import os
                    
                    with tempfile.TemporaryDirectory() as tmp_dir:
                        # Exportiere Multi-View Screenshots
                        views = export_multi_view_screenshots(
                            project_data=project_data,
                            dims=dims,
                            roof_type=selected_roof_type,
                            module_quantity=module_quantity,
                            layout_config=layout_config,
                            output_dir=tmp_dir,
                            base_filename="pv_3d"
                        )
                        
                        # Lese ZIP-Datei
                        zip_filepath = os.path.join(tmp_dir, "pv_3d_multi_view.zip")
                        
                        if os.path.exists(zip_filepath):
                            with open(zip_filepath, 'rb') as f:
                                zip_bytes = f.read()
                            
                            # Zeige Download-Button
                            st.download_button(
                                label="⬇️ ZIP herunterladen",
                                data=zip_bytes,
                                file_name="pv_3d_multi_view.zip",
                                mime="application/zip",
                                use_container_width=True
                            )
                            st.success(f"✓ Multi-View Screenshots erstellt ({len(views)} Ansichten)")
                        else:
                            st.error("❌ Multi-View Export fehlgeschlagen")
                        
            except Exception as e:
                st.error(f"❌ Fehler beim Multi-View Export: {e}")
        
        st.divider()
        
        # ====================================================================
        # 360° ANIMATION
        # ====================================================================
        st.subheader("🎥 360° Animation")
        st.caption("Erstellt eine animierte GIF-Datei mit 360° Rotation")
        
        # Animation-Einstellungen
        anim_col1, anim_col2 = st.columns(2)
        
        with anim_col1:
            anim_frames = st.slider(
                "Anzahl Frames",
                min_value=12,
                max_value=72,
                value=36,
                step=6,
                help="Mehr Frames = flüssigere Animation, aber größere Datei"
            )
        
        with anim_col2:
            anim_duration = st.slider(
                "Frame-Dauer (ms)",
                min_value=50,
                max_value=500,
                value=100,
                step=50,
                help="Kürzere Dauer = schnellere Animation"
            )
        
        if st.button("🎬 Animation erstellen", key="animation_export", use_container_width=True):
            try:
                with st.spinner(f"Erstelle 360° Animation mit {anim_frames} Frames... Dies kann 1-2 Minuten dauern."):
                    # Erstelle BuildingDims und LayoutConfig
                    dims = BuildingDims(
                        length_m=building_length,
                        width_m=building_width,
                        wall_height_m=building_height
                    )
                    
                    # Konvertiere mounting_type zu internem Format
                    mounting_mode_map = {
                        "Süd": "south",
                        "Ost-West": "east-west",
                        "Süd-Ost": "south-east",
                        "Süd-West": "south-west",
                        "Individuell": "custom"
                    }
                    mounting_mode = mounting_mode_map.get(mounting_type, "south")
                    
                    layout_config = AdvancedLayoutConfig(
                        mode="auto" if layout_mode == "Automatisch" else "manual",
                        use_garage=use_garage,
                        use_facade=use_facade,
                        removed_indices=removed_indices,
                        garage_dims=(6.0, 3.0, 3.0),
                        offset_main_xy=(0.0, 0.0),
                        offset_garage_xy=(0.0, 0.0),
                        mounting_mode=mounting_mode,
                        custom_azimuth=custom_azimuth,
                        custom_tilt=custom_tilt,
                        enable_collision_detection=False,
                        enable_shading_analysis=False
                    )
                    
                    # Erstelle temporäre Datei für GIF
                    import tempfile
                    import os
                    
                    with tempfile.NamedTemporaryFile(mode='wb', suffix='.gif', delete=False) as tmp_file:
                        tmp_filepath = tmp_file.name
                    
                    # Exportiere 360° Animation
                    gif_bytes = export_360_animation(
                        project_data=project_data,
                        dims=dims,
                        roof_type=selected_roof_type,
                        module_quantity=module_quantity,
                        layout_config=layout_config,
                        filepath=tmp_filepath,
                        frames=anim_frames,
                        resolution=(800, 600),
                        duration_ms=anim_duration
                    )
                    
                    # Lese GIF-Bytes
                    if gif_bytes and os.path.exists(tmp_filepath):
                        with open(tmp_filepath, 'rb') as f:
                            gif_bytes = f.read()
                        
                        # Lösche temporäre Datei
                        try:
                            os.unlink(tmp_filepath)
                        except:
                            pass
                        
                        # Zeige Download-Button
                        st.download_button(
                            label="⬇️ GIF herunterladen",
                            data=gif_bytes,
                            file_name="pv_3d_animation_360.gif",
                            mime="image/gif",
                            use_container_width=True
                        )
                        st.success(f"✓ 360° Animation erstellt ({anim_frames} Frames)")
                    else:
                        st.error("❌ Animation-Export fehlgeschlagen")
                        
            except Exception as e:
                st.error(f"❌ Fehler beim Animation-Export: {e}")



    # ============================================================================
    # HILFE-SEKTION
    # ============================================================================

    st.divider()

    with st.expander("ℹ️ Datenquelle (App-Bindung)"):
        st.markdown("""
        ### Woher kommen die Daten?
        
        Die 3D-Visualisierung nutzt automatisch Daten aus Ihrer Bedarfsanalyse und dem Solarkalkulator:
        
        #### 🏠 Gebäudedaten
        - **Ausrichtung:** Aus `project_data["project_details"]["roof_orientation"]`
        - **Dachneigung:** Aus `project_data["project_details"]["roof_inclination_deg"]`
        - **Dachdeckung:** Aus `project_data["project_details"]["roof_covering_type"]`
        - **Dachform:** Aus `project_data["project_details"]["roof_type"]`
        
        #### ⚡ PV-Anlagen-Daten
        - **Modulanzahl:** Aus `analysis_results["module_quantity"]` (primär) oder `project_data["module_quantity"]` (Fallback)
        - **Systemgröße:** Aus `analysis_results["system_kwp"]`
        
        #### 🎨 Anpassungen
        Sie können die Gebäudedimensionen in der Sidebar manuell anpassen, um die Visualisierung
        an Ihr spezifisches Gebäude anzupassen. Die Dachform und andere Parameter werden automatisch
        aus Ihren vorherigen Eingaben übernommen.
        
        #### 💡 Tipp
        Wenn Sie Änderungen an der Bedarfsanalyse vornehmen, kehren Sie zu dieser Seite zurück
        und klicken Sie auf "Visualisierung aktualisieren", um die 3D-Ansicht zu aktualisieren.
        """)

    st.divider()

    # Footer
    st.caption("🏠 3D PV-Visualisierung | Powered by Ömer")


# When run as standalone page
if __name__ == "__main__":
    render_3d_view()
