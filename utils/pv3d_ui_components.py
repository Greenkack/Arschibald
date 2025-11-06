"""
3D PV-Visualisierung UI-Komponenten

Dieses Modul enthält alle UI-Rendering-Funktionen für die 3D-Visualisierung.
Jede Funktion rendert einen spezifischen UI-Bereich und gibt die Benutzereingaben zurück.

Alle UI-Elemente sind mit Tooltips und Hilfe-Texten ausgestattet für bessere Benutzerführung.
"""

import streamlit as st
from typing import Dict, Any, List, Tuple, Optional
from utils.pv3d import (
    BuildingDims,
    LayoutConfig,
    AdvancedLayoutConfig,
    ModuleTransform,
    ModuleGroup
)
from utils.pv3d_performance import (
    debounced_slider,
    debounced_number_input,
    lazy_expander,
    monitor_performance
)
from utils.pv3d_help import (
    get_tooltip,
    show_contextual_help,
    show_success_message,
    show_warning_message
)


def _get_default_dimensions(building_type: str) -> Tuple[float, float, float]:
    """
    Gibt Standard-Dimensionen basierend auf Gebäudeart zurück.
    
    Args:
        building_type: Art des Gebäudes
        
    Returns:
        Tuple mit (Länge, Breite, Höhe) in Metern
    """
    defaults = {
        "Einfamilienhaus": (12.0, 10.0, 3.0),
        "Mehrfamilienhaus": (20.0, 15.0, 3.0),
        "Gewerbe": (30.0, 20.0, 4.0),
        "Industrie": (50.0, 30.0, 5.0)
    }
    return defaults.get(building_type, (12.0, 10.0, 3.0))


def render_basis_settings(project_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Rendert Basis-Einstellungen Expander für Gebäudedimensionen und Dachform.
    
    Args:
        project_data: Projektdaten aus Session State
        
    Returns:
        Dictionary mit Benutzereingaben:
        - building_length: float
        - building_width: float
        - building_height: float
        - roof_type: str
    """
    
    # Extrahiere Gebäudeart
    building_type = project_data.get("building_type", "Einfamilienhaus")
    if "project_details" in project_data:
        building_type = project_data["project_details"].get("building_type", building_type)
    
    # Extrahiere aktuellen Dachtyp
    roof_type = project_data.get("roof_type", "Flachdach")
    if "project_details" in project_data:
        roof_type = project_data["project_details"].get("roof_type", roof_type)
    
    with st.sidebar.expander("🏠 Basis-Einstellungen", expanded=True):
        # Zeige kontextbezogene Hilfe
        show_contextual_help("basis_settings")
        
        st.markdown("**Gebäudedimensionen**")
        
        # Standardwerte basierend auf Gebäudeart
        default_length, default_width, default_height = _get_default_dimensions(building_type)

        building_length = st.number_input(
            "Gebäudelänge (m)",
            min_value=8.0,
            max_value=60.0,
            value=default_length,
            step=0.5,
            help=get_tooltip("building_length"),
            key="building_length_input"
        )

        building_width = st.number_input(
            "Gebäudebreite (m)",
            min_value=5.0,
            max_value=40.0,
            value=default_width,
            step=0.5,
            help=get_tooltip("building_width"),
            key="building_width_input"
        )

        building_height = st.number_input(
            "Traufhöhe (m)",
            min_value=3.0,
            max_value=20.0,
            value=3.0,
            step=0.5,
            help=get_tooltip("building_height"),
            key="building_height_input"
        )

        st.divider()

        # Dachform
        st.markdown("**Dachform**")

        roof_types = [
            "Flachdach",
            "Satteldach",
            "Satteldach mit Gaube",
            "Walmdach",
            "Krüppelwalmdach",
            "Pultdach",
            "Zeltdach",
            "Sonstiges"
        ]

        # Verwende die letzte gespeicherte Dachform aus scene_data, falls vorhanden
        scene_data = st.session_state.get("_pv3d_scene_data", {})
        last_selected_roof = scene_data.get("roof_type", roof_type)

        selected_roof_type = st.selectbox(
            "Dachform",
            options=roof_types,
            index=roof_types.index(last_selected_roof) if last_selected_roof in roof_types else 0,
            help=get_tooltip("roof_type"),
            key="roof_type_select"
        )
    
    return {
        "building_length": building_length,
        "building_width": building_width,
        "building_height": building_height,
        "roof_type": selected_roof_type
    }


def render_module_placement(project_data: Dict[str, Any], selected_roof_type: str) -> Dict[str, Any]:
    """
    Rendert Modul-Belegung Expander für Belegungsmodus und Aufständerung.
    
    Args:
        project_data: Projektdaten aus Session State
        selected_roof_type: Ausgewählte Dachform
        
    Returns:
        Dictionary mit Benutzereingaben:
        - layout_mode: str
        - mounting_type: str
        - custom_azimuth: float
        - custom_tilt: float
        - use_garage: bool
        - use_facade: bool
        - removed_indices: List[int]
    """
    with st.sidebar.expander("⚡ Modul-Belegung", expanded=True):
        # Zeige kontextbezogene Hilfe
        show_contextual_help("module_placement")
        
        st.markdown("**Belegungsmodus**")
        
        layout_mode = st.radio(
            "Belegungsmodus",
            options=["Automatisch", "Manuell"],
            index=0,
            help=get_tooltip("layout_mode"),
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
                help=get_tooltip("mounting_type"),
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
                    help=get_tooltip("azimuth"),
                    key="custom_azimuth_slider"
                )
                
                custom_tilt = st.slider(
                    "Neigung (°)",
                    min_value=0.0,
                    max_value=90.0,
                    value=15.0,
                    step=1.0,
                    help=get_tooltip("tilt"),
                    key="custom_tilt_slider"
                )

        st.divider()

        # Platzmangel-Fallbacks
        st.markdown("**Zusätzliche Flächen**")

        use_garage = st.checkbox(
            "Garage/Carport automatisch hinzufügen",
            value=False,
            help=get_tooltip("use_garage"),
            key="use_garage_checkbox"
        )

        use_facade = st.checkbox(
            "Fassadenbelegung aktivieren",
            value=False,
            help=get_tooltip("use_facade"),
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
                help=get_tooltip("removed_indices"),
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
    
    return {
        "layout_mode": layout_mode,
        "mounting_type": mounting_type,
        "custom_azimuth": custom_azimuth,
        "custom_tilt": custom_tilt,
        "use_garage": use_garage,
        "use_facade": use_facade,
        "removed_indices": removed_indices
    }



def render_advanced_controls(
    building_length: float,
    building_width: float
) -> Dict[str, Any]:
    """
    Rendert Erweiterte Kontrolle Expander für Kollisionserkennung und Modul-Auswahl.
    
    Args:
        building_length: Gebäudelänge in Metern
        building_width: Gebäudebreite in Metern
        
    Returns:
        Dictionary mit Benutzereingaben:
        - enable_collision_detection: bool
        - selected_modules: List[int]
    """
    with st.sidebar.expander("🎛️ Erweiterte Kontrolle", expanded=False):
        # Zeige kontextbezogene Hilfe
        show_contextual_help("advanced_controls")
        
        st.markdown("**Erweiterte Optionen**")

        enable_collision_detection = st.checkbox(
            "Kollisionserkennung aktivieren",
            value=True,
            help=get_tooltip("collision_detection"),
            key="collision_detection_checkbox"
        )

        st.divider()

        # Modul-Auswahl und Bearbeitung
        st.markdown("**Modul-Auswahl & Bearbeitung**")
        st.caption("Wählen Sie einzelne Module oder Gruppen aus, um deren Eigenschaften zu bearbeiten.")
        
        # Auswahl-Modus
        selection_mode = st.radio(
            "Auswahl-Modus",
            options=["Einzeln", "Gruppe", "Bereich"],
            index=0,
            help=get_tooltip("selection_mode"),
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
                help=get_tooltip("module_index")
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
    
    return {
        "enable_collision_detection": enable_collision_detection,
        "selected_modules": selected_modules
    }



def render_analysis_panel() -> Dict[str, Any]:
    """
    Rendert Analyse Expander für Optimierung, Verschattung und Heatmap.
    
    Returns:
        Dictionary mit Benutzereingaben:
        - optimization_goal: str
        - run_optimization: bool
        - enable_shading_analysis: bool
        - hour_of_day: float
        - day_of_year: int
        - latitude: float
        - enable_sun_animation: bool
        - anim_speed: int
        - anim_start_hour: float
        - anim_end_hour: float
        - enable_yield_heatmap: bool
        - heatmap_metric: str
        - enable_yield_forecast: bool
        - electricity_price: float
        - module_efficiency: int
    """
    with st.sidebar.expander("📊 Analyse", expanded=False):
        # Zeige kontextbezogene Hilfe
        show_contextual_help("analysis")
        
        # Optimierungs-Assistent
        st.markdown("**🎯 Optimierungs-Assistent**")
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
            help=get_tooltip("optimization_goal")
        )
        
        # Button: Optimierung starten
        run_optimization = st.button(
            "🚀 Optimierung starten",
            use_container_width=True,
            help="Generiert und bewertet verschiedene Konfigurationen"
        )
        
        st.divider()

        # Verschattungs-Analyse
        st.markdown("**☀️ Verschattungs-Analyse**")
        st.caption("Analysieren Sie die Verschattung der Module zu verschiedenen Tageszeiten und Jahreszeiten.")
        
        enable_shading_analysis = st.checkbox(
            "Verschattungs-Analyse aktivieren",
            value=False,
            help=get_tooltip("shading_analysis"),
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
                help=get_tooltip("hour_of_day")
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
                help=get_tooltip("season")
            )
            
            day_of_year = season_options[selected_season]
            
            # Breitengrad-Eingabe
            latitude = st.number_input(
                "Breitengrad",
                min_value=-90.0,
                max_value=90.0,
                value=51.0,
                step=0.1,
                help=get_tooltip("latitude")
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
        
        # Sonnenverlauf-Animation
        st.markdown("**🌅 Sonnenverlauf-Animation**")
        st.caption("Animiere den Sonnenverlauf über den Tag und sehe die Verschattung in Echtzeit.")
        
        enable_sun_animation = st.checkbox(
            "Sonnenverlauf-Animation aktivieren",
            value=False,
            help=get_tooltip("sun_animation"),
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
        
        # Ertrags-Heatmap
        st.markdown("**🔥 Ertrags-Heatmap**")
        st.caption("Visualisiere das Ertragspotential jedes Moduls mit Farbcodierung.")
        
        enable_yield_heatmap = st.checkbox(
            "Ertrags-Heatmap aktivieren",
            value=False,
            help=get_tooltip("yield_heatmap"),
            key="enable_yield_heatmap_checkbox"
        )
        
        if enable_yield_heatmap:
            st.info("📊 Heatmap wird nach dem Rendern angezeigt")
            
            # Heatmap-Einstellungen
            heatmap_metric = st.selectbox(
                "Heatmap-Metrik",
                options=["Jahresertrag (kWh)", "Verschattung (%)", "Effizienz (%)"],
                index=0,
                help=get_tooltip("heatmap_metric")
            )
        else:
            heatmap_metric = "Jahresertrag (kWh)"
        
        st.divider()
        
        # Live-Ertragsprognose
        st.markdown("**⚡ Live-Ertragsprognose**")
        st.caption("Berechne den erwarteten Jahresertrag für die aktuelle Konfiguration.")
        
        enable_yield_forecast = st.checkbox(
            "Ertragsprognose aktivieren",
            value=False,
            help=get_tooltip("yield_forecast"),
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
                help=get_tooltip("electricity_price")
            )
            
            module_efficiency = st.slider(
                "Modul-Wirkungsgrad (%)",
                min_value=15,
                max_value=25,
                value=20,
                step=1,
                help=get_tooltip("module_efficiency")
            )
        else:
            electricity_price = 0.30
            module_efficiency = 20
    
    return {
        "optimization_goal": optimization_goal,
        "run_optimization": run_optimization,
        "enable_shading_analysis": enable_shading_analysis,
        "hour_of_day": hour_of_day,
        "day_of_year": day_of_year,
        "latitude": latitude,
        "enable_sun_animation": enable_sun_animation,
        "anim_speed": anim_speed,
        "anim_start_hour": anim_start_hour,
        "anim_end_hour": anim_end_hour,
        "enable_yield_heatmap": enable_yield_heatmap,
        "heatmap_metric": heatmap_metric,
        "enable_yield_forecast": enable_yield_forecast,
        "electricity_price": electricity_price,
        "module_efficiency": module_efficiency
    }



def render_export_options() -> Dict[str, Any]:
    """
    Rendert Export-Optionen Expander für alle Export-Funktionen.
    
    Returns:
        Dictionary mit Benutzereingaben:
        - export_screenshot: bool
        - screenshot_format: str
        - screenshot_resolution: Tuple[int, int]
        - export_multiview: bool
        - multiview_resolution: Tuple[int, int]
        - export_360: bool
        - animation_frames: int
        - animation_resolution: Tuple[int, int]
        - export_3d_model: bool
        - model_format: str
        - export_csv: bool
        - export_json: bool
    """
    with st.sidebar.expander("📦 Export-Optionen", expanded=False):
        # Zeige kontextbezogene Hilfe
        show_contextual_help("export")
        
        st.markdown("**Export-Funktionen**")
        st.caption("Exportieren Sie die 3D-Visualisierung in verschiedenen Formaten.")
        
        # Screenshot-Export
        st.markdown("**📷 Screenshot**")
        export_screenshot = st.checkbox(
            "Screenshot exportieren",
            value=False,
            help=get_tooltip("screenshot"),
            key="export_screenshot_checkbox"
        )
        
        if export_screenshot:
            col_format, col_res = st.columns(2)
            
            with col_format:
                screenshot_format = st.selectbox(
                    "Format",
                    options=["PNG", "JPEG"],
                    index=0,
                    help=get_tooltip("screenshot_format")
                )
            
            with col_res:
                resolution_options = {
                    "HD (1280x720)": (1280, 720),
                    "Full HD (1920x1080)": (1920, 1080),
                    "2K (2560x1440)": (2560, 1440),
                    "4K (3840x2160)": (3840, 2160)
                }
                
                selected_res = st.selectbox(
                    "Auflösung",
                    options=list(resolution_options.keys()),
                    index=1,
                    help=get_tooltip("screenshot_resolution")
                )
                
                screenshot_resolution = resolution_options[selected_res]
        else:
            screenshot_format = "PNG"
            screenshot_resolution = (1920, 1080)
        
        st.divider()
        
        # Multi-View Export
        st.markdown("**🎬 Multi-View Screenshots**")
        export_multiview = st.checkbox(
            "Multi-View Export",
            value=False,
            help=get_tooltip("multiview"),
            key="export_multiview_checkbox"
        )
        
        if export_multiview:
            multiview_res_options = {
                "Standard (1200x750)": (1200, 750),
                "HD (1600x1000)": (1600, 1000),
                "Full HD (1920x1200)": (1920, 1200)
            }
            
            selected_multiview_res = st.selectbox(
                "Multi-View Auflösung",
                options=list(multiview_res_options.keys()),
                index=0,
                help="Auflösung für Multi-View Screenshots"
            )
            
            multiview_resolution = multiview_res_options[selected_multiview_res]
        else:
            multiview_resolution = (1200, 750)
        
        st.divider()
        
        # 360° Animation
        st.markdown("**🔄 360° Animation**")
        export_360 = st.checkbox(
            "360° Animation exportieren",
            value=False,
            help=get_tooltip("animation_360"),
            key="export_360_checkbox"
        )
        
        if export_360:
            col_frames, col_anim_res = st.columns(2)
            
            with col_frames:
                animation_frames = st.slider(
                    "Frames",
                    min_value=12,
                    max_value=72,
                    value=36,
                    step=6,
                    help=get_tooltip("animation_frames")
                )
            
            with col_anim_res:
                anim_res_options = {
                    "Klein (600x450)": (600, 450),
                    "Mittel (800x600)": (800, 600),
                    "Groß (1200x900)": (1200, 900)
                }
                
                selected_anim_res = st.selectbox(
                    "Auflösung",
                    options=list(anim_res_options.keys()),
                    index=0,
                    help="Auflösung für Animation"
                )
                
                animation_resolution = anim_res_options[selected_anim_res]
        else:
            animation_frames = 36
            animation_resolution = (600, 450)
        
        st.divider()
        
        # 3D-Modell Export
        st.markdown("**🎨 3D-Modell**")
        export_3d_model = st.checkbox(
            "3D-Modell exportieren",
            value=False,
            help=get_tooltip("model_3d"),
            key="export_3d_model_checkbox"
        )
        
        if export_3d_model:
            model_format = st.selectbox(
                "3D-Format",
                options=["STL", "GLTF", "OBJ"],
                index=0,
                help=get_tooltip("model_3d")
            )
        else:
            model_format = "STL"
        
        st.divider()
        
        # Daten-Export
        st.markdown("**📊 Daten-Export**")
        
        col_csv, col_json = st.columns(2)
        
        with col_csv:
            export_csv = st.checkbox(
                "CSV Export",
                value=False,
                help=get_tooltip("export_csv"),
                key="export_csv_checkbox"
            )
        
        with col_json:
            export_json = st.checkbox(
                "JSON Export",
                value=False,
                help=get_tooltip("export_json"),
                key="export_json_checkbox"
            )
    
    return {
        "export_screenshot": export_screenshot,
        "screenshot_format": screenshot_format,
        "screenshot_resolution": screenshot_resolution,
        "export_multiview": export_multiview,
        "multiview_resolution": multiview_resolution,
        "export_360": export_360,
        "animation_frames": animation_frames,
        "animation_resolution": animation_resolution,
        "export_3d_model": export_3d_model,
        "model_format": model_format,
        "export_csv": export_csv,
        "export_json": export_json
    }
