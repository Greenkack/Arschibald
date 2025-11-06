"""
3D PV-Visualisierung UI-Seite (Refactored)

Diese Seite bietet eine interaktive 3D-Visualisierung der PV-Anlage
auf dem Gebäude mit automatischer und manueller Modul-Platzierung.

REFACTORED: Die Funktionalität wurde in separate Module aufgeteilt:
- utils/pv3d_ui_components.py: UI-Rendering-Funktionen
- utils/pv3d_analysis.py: Analyse-Funktionen
- utils/pv3d_export.py: Export-Funktionen
- utils/pv3d_optimization.py: Optimierungs-Funktionen
"""

import streamlit as st
from typing import Dict, Any, Optional
import traceback

# Imports für 3D-Visualisierung
try:
    from utils.pv3d import BuildingDims, AdvancedLayoutConfig
    from utils.pv3d_plotly import build_plotly_scene
    PV3D_AVAILABLE = True
except ImportError as e:
    PV3D_AVAILABLE = False
    print(f"WARNUNG: 3D-Visualisierung nicht verfügbar: {e}")
except Exception as e:
    PV3D_AVAILABLE = False
    print(f"FEHLER beim Laden der 3D-Visualisierung: {e}")

# Imports für neue Module
try:
    from utils.pv3d_ui_components import (
        render_basis_settings,
        render_module_placement,
        render_advanced_controls,
        render_analysis_panel,
        render_export_options
    )
    UI_COMPONENTS_AVAILABLE = True
except ImportError as e:
    UI_COMPONENTS_AVAILABLE = False
    print(f"WARNUNG: UI-Komponenten nicht verfügbar: {e}")

try:
    from utils.pv3d_analysis import (
        calculate_shading_analysis,
        calculate_yield_heatmap
    )
    ANALYSIS_AVAILABLE = True
except ImportError as e:
    ANALYSIS_AVAILABLE = False
    print(f"WARNUNG: Analyse-Modul nicht verfügbar: {e}")

try:
    from utils.pv3d_export import (
        export_screenshot,
        export_multi_view,
        export_360_animation,
        export_3d_model
    )
    EXPORT_AVAILABLE = True
except ImportError as e:
    EXPORT_AVAILABLE = False
    print(f"WARNUNG: Export-Modul nicht verfügbar: {e}")

try:
    from utils.pv3d_optimization import optimize_layout
    OPTIMIZATION_AVAILABLE = True
except ImportError as e:
    OPTIMIZATION_AVAILABLE = False
    print(f"WARNUNG: Optimierungs-Modul nicht verfügbar: {e}")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def safe_render_component(render_func, component_name: str, *args, **kwargs) -> Dict[str, Any]:
    """
    Wrapper für sichere UI-Komponenten-Rendering mit Fehlerbehandlung.
    
    Args:
        render_func: Die zu rendernde Funktion
        component_name: Name der Komponente für Fehlermeldungen
        *args, **kwargs: Argumente für die Funktion
    
    Returns:
        Dictionary mit Benutzereingaben oder leeres Dict bei Fehler
    """
    try:
        return render_func(*args, **kwargs)
    except Exception as e:
        st.error(f"❌ Fehler beim Laden von {component_name}: {e}")
        print(f"Fehler in {component_name}:")
        traceback.print_exc()
        return {}


def get_project_data() -> Dict[str, Any]:
    """
    Lädt project_data aus Session State mit Fehlerbehandlung.
    
    Returns:
        project_data Dictionary oder leeres Dict
    """
    project_data = st.session_state.get("project_data", {})
    if not project_data:
        st.warning("⚠️ Keine Projektdaten gefunden. Bitte führen Sie zuerst die Bedarfsanalyse durch.")
    return project_data


def get_analysis_results() -> Dict[str, Any]:
    """
    Lädt analysis_results aus Session State.
    
    Returns:
        analysis_results Dictionary oder leeres Dict
    """
    return st.session_state.get("analysis_results", {})


def extract_roof_type(project_data: Dict[str, Any]) -> str:
    """
    Extrahiert Dachtyp aus project_data mit Fallback.
    
    Args:
        project_data: Projektdaten
    
    Returns:
        Dachtyp als String
    """
    if "project_details" in project_data:
        roof_type = project_data["project_details"].get("roof_type")
        if roof_type:
            return str(roof_type)
    roof_type = project_data.get("roof_type")
    if roof_type:
        return str(roof_type)
    return "Flachdach"


def extract_module_quantity(
    project_data: Dict[str, Any],
    analysis_results: Dict[str, Any]
) -> int:
    """
    Extrahiert Modulanzahl mit Fallback und Logging.
    
    Args:
        project_data: Projektdaten
        analysis_results: Analyseergebnisse
    
    Returns:
        Modulanzahl als Integer
    """
    # Primäre Quelle: analysis_results
    if analysis_results:
        module_qty = analysis_results.get("module_quantity")
        if module_qty is not None:
            try:
                qty = int(module_qty)
                print(f"✓ Modulanzahl aus analysis_results: {qty}")
                return qty
            except (ValueError, TypeError):
                print(f"⚠️ Ungültige Modulanzahl in analysis_results: {module_qty}")
    
    # Fallback: project_data
    if project_data:
        module_qty = project_data.get("module_quantity")
        if module_qty is not None:
            try:
                qty = int(module_qty)
                print(f"✓ Modulanzahl aus project_data: {qty}")
                return qty
            except (ValueError, TypeError):
                print(f"⚠️ Ungültige Modulanzahl in project_data: {module_qty}")
    
    # Letzter Fallback: 20 Module
    print("⚠️ Keine Modulanzahl gefunden, verwende Default: 20")
    return 20


def extract_building_type(project_data: Dict[str, Any]) -> str:
    """
    Extrahiert Gebäudeart aus project_data mit Fallback.
    
    Args:
        project_data: Projektdaten
    
    Returns:
        Gebäudeart als String
    """
    if "project_details" in project_data:
        building_type = project_data["project_details"].get("building_type")
        if building_type:
            return str(building_type)
    building_type = project_data.get("building_type")
    if building_type:
        return str(building_type)
    return "Einfamilienhaus"


def cleanup_session_state():
    """
    Entfernt alte nicht-serialisierbare Objekte aus Session State.
    """
    keys_to_remove = ["_pv3d_plotter"]
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]


def create_building_dims(settings: Dict[str, Any]) -> BuildingDims:
    """
    Erstellt BuildingDims-Objekt aus UI-Einstellungen.
    
    Args:
        settings: Dictionary mit building_length, building_width, building_height
    
    Returns:
        BuildingDims-Objekt
    """
    return BuildingDims(
        length_m=settings.get("building_length", 10.0),
        width_m=settings.get("building_width", 6.0),
        wall_height_m=settings.get("building_height", 3.0)
    )


def create_layout_config(
    module_settings: Dict[str, Any],
    advanced_settings: Dict[str, Any]
) -> Optional[AdvancedLayoutConfig]:
    """
    Erstellt AdvancedLayoutConfig aus UI-Einstellungen.
    
    Args:
        module_settings: Dictionary mit Modul-Einstellungen
        advanced_settings: Dictionary mit erweiterten Einstellungen
    
    Returns:
        AdvancedLayoutConfig-Objekt oder None
    """
    try:
        # Hole gespeicherte Konfiguration aus Session State
        layout_json = st.session_state.get("pv3d_layout_json", "{}")
        if layout_json and layout_json != "{}":
            config = AdvancedLayoutConfig.from_json(layout_json)
        else:
            config = AdvancedLayoutConfig()
        
        # Aktualisiere mit neuen Einstellungen
        if "mounting_type" in module_settings:
            config.mounting_type = module_settings["mounting_type"]
        
        if "custom_azimuth" in module_settings:
            config.custom_azimuth = module_settings["custom_azimuth"]
        
        if "custom_tilt" in module_settings:
            config.custom_tilt = module_settings["custom_tilt"]
        
        if "use_garage" in module_settings:
            config.use_garage = module_settings["use_garage"]
        
        if "use_facade" in module_settings:
            config.use_facade = module_settings["use_facade"]
        
        if "removed_indices" in module_settings:
            config.removed_indices = module_settings["removed_indices"]
        
        # Speichere aktualisierte Konfiguration
        st.session_state["pv3d_layout_json"] = config.to_json()
        
        return config
    except Exception as e:
        print(f"Fehler beim Erstellen der Layout-Konfiguration: {e}")
        return None


# ============================================================================
# MAIN RENDER FUNCTION
# ============================================================================

def render_3d_view():
    """
    Hauptfunktion zum Rendern der 3D-Visualisierung.
    
    Diese Funktion wird von gui.py aufgerufen und orchestriert alle
    UI-Komponenten, Analysen und Exports.
    """
    try:
        _render_3d_view_impl()
    except Exception as e:
        st.error(f"❌ Kritischer Fehler in der 3D-Visualisierung: {e}")
        print("Kritischer Fehler:")
        traceback.print_exc()
        
        # Zeige Debug-Informationen
        with st.expander("🔍 Debug-Informationen"):
            st.code(traceback.format_exc())


def _render_3d_view_impl():
    """
    Interne Implementierung der 3D-Visualisierung (Refactored).
    
    Diese Funktion ist stark vereinfacht und delegiert die meiste Arbeit
    an die spezialisierten Module.
    """
    
    # ============================================================================
    # SCHRITT 1: INITIALISIERUNG
    # ============================================================================
    
    # Cleanup
    cleanup_session_state()
    
    # Prüfe 3D-Verfügbarkeit
    if not PV3D_AVAILABLE:
        st.error("❌ 3D-Visualisierung nicht verfügbar. Bitte installieren Sie die erforderlichen Pakete:")
        st.code("pip install pyvista vtk stpyvista numpy trimesh pillow plotly", language="bash")
        st.stop()
    
    # Lade Daten
    project_data = get_project_data()
    if not project_data:
        return
    
    analysis_results = get_analysis_results()

    # Extrahiere Basis-Informationen
    roof_type = extract_roof_type(project_data)
    module_quantity = extract_module_quantity(project_data, analysis_results)
    
    # ============================================================================
    # SCHRITT 2: TITEL UND BESCHREIBUNG
    # ============================================================================
    
    st.title("🏠 3D PV-Visualisierung")
    st.markdown("""
    Visualisieren Sie Ihre PV-Anlage in 3D. Passen Sie Gebäudedimensionen an,
    wählen Sie zwischen automatischer und manueller Modul-Platzierung und
    exportieren Sie das Modell als Bild oder 3D-Datei.
    """)
    
    st.divider()
    
    # ============================================================================
    # SCHRITT 3: SIDEBAR - UI-KOMPONENTEN RENDERN
    # ============================================================================
    
    st.sidebar.header("⚙️ Einstellungen")
    
    # Rendere alle UI-Komponenten mit Fehlerbehandlung
    basis_settings = {}
    module_settings = {}
    advanced_settings = {}
    analysis_settings = {}
    export_settings = {}
    
    if UI_COMPONENTS_AVAILABLE:
        basis_settings = safe_render_component(
            render_basis_settings,
            "Basis-Einstellungen",
            project_data
        )
        
        module_settings = safe_render_component(
            render_module_placement,
            "Modul-Belegung",
            project_data,
            roof_type
        )
        
        advanced_settings = safe_render_component(
            render_advanced_controls,
            "Erweiterte Kontrolle",
            project_data
        )
        
        if ANALYSIS_AVAILABLE:
            analysis_settings = safe_render_component(
                render_analysis_panel,
                "Analyse",
                project_data
            )
        
        if EXPORT_AVAILABLE:
            export_settings = safe_render_component(
                render_export_options,
                "Export-Optionen",
                project_data
            )
    else:
        st.sidebar.error("❌ UI-Komponenten nicht verfügbar")
        return
    
    # ============================================================================
    # SCHRITT 4: ERSTELLE 3D-SZENE
    # ============================================================================
    
    try:
        # Erstelle BuildingDims
        dims = create_building_dims(basis_settings)
        
        # Erstelle Layout-Konfiguration
        layout_config = create_layout_config(module_settings, advanced_settings)
        
        # Hole ausgewählte Module
        selected_modules = advanced_settings.get("selected_modules", [])
        
        # Erstelle Plotly-Szene
        fig = build_plotly_scene(
            project_data=project_data,
            dims=dims,
            roof_type=basis_settings.get("roof_type", roof_type),
            module_quantity=module_quantity,
            layout_config=layout_config,
            selected_modules=selected_modules
        )
        
        # Zeige 3D-Szene
        st.plotly_chart(fig, use_container_width=True, key="main_3d_view")
        
    except Exception as e:
        st.error(f"❌ Fehler beim Erstellen der 3D-Szene: {e}")
        print("Fehler beim Erstellen der 3D-Szene:")
        traceback.print_exc()
        return
    
    # ============================================================================
    # SCHRITT 5: FÜHRE ANALYSEN AUS (FALLS AKTIVIERT)
    # ============================================================================
    
    if ANALYSIS_AVAILABLE and analysis_settings:
        # Optimierungs-Assistent
        if analysis_settings.get("run_optimization"):
            try:
                with st.spinner("🔄 Führe Optimierung durch..."):
                    optimization_goal = analysis_settings.get("optimization_goal", "balanced")
                    constraints = analysis_settings.get("constraints", {})
                    
                    optimized_configs = optimize_layout(
                        dims=dims,
                        goal=optimization_goal,
                        constraints=constraints,
                        roof_type=basis_settings.get("roof_type", roof_type),
                        latitude=51.0  # Deutschland
                    )
                    
                    if optimized_configs:
                        st.success(f"✓ Optimierung abgeschlossen! {len(optimized_configs)} Konfigurationen gefunden.")
                        
                        # Zeige beste Konfiguration
                        best_config = optimized_configs[0]
                        st.session_state["pv3d_layout_json"] = best_config.to_json()
                        st.rerun()
            except Exception as e:
                st.error(f"❌ Fehler bei der Optimierung: {e}")
                print("Fehler bei der Optimierung:")
                traceback.print_exc()
        
        # Verschattungs-Analyse
        if analysis_settings.get("show_shading"):
            try:
                with st.spinner("🔄 Berechne Verschattung..."):
                    time_of_day = analysis_settings.get("time_of_day", 12.0)
                    day_of_year = analysis_settings.get("day_of_year", 172)
                    
                    # Hole Modul-Positionen aus Layout-Config
                    module_positions = []  # TODO: Extrahiere aus layout_config
                    
                    _ = calculate_shading_analysis(
                        module_positions=module_positions,
                        time_of_day=time_of_day,
                        day_of_year=day_of_year,
                        latitude=51.0
                    )

                    st.success("✓ Verschattungs-Analyse abgeschlossen!")
                    # TODO: Visualisiere Verschattung in 3D-Szene
            except Exception as e:
                st.error(f"❌ Fehler bei der Verschattungs-Analyse: {e}")
                print("Fehler bei der Verschattungs-Analyse:")
                traceback.print_exc()
        
        # Ertrags-Heatmap
        if analysis_settings.get("show_heatmap"):
            try:
                with st.spinner("🔄 Berechne Ertrags-Heatmap..."):
                    # Hole Modul-Positionen und Transforms
                    module_positions = []  # TODO: Extrahiere aus layout_config
                    module_transforms = layout_config.module_transforms if layout_config else {}
                    
                    _ = calculate_yield_heatmap(
                        module_positions=module_positions,
                        module_transforms=module_transforms,
                        latitude=51.0,
                        efficiency=20.0
                    )

                    st.success("✓ Ertrags-Heatmap abgeschlossen!")
                    # TODO: Visualisiere Heatmap in 3D-Szene
            except Exception as e:
                st.error(f"❌ Fehler bei der Ertrags-Heatmap: {e}")
                print("Fehler bei der Ertrags-Heatmap:")
                traceback.print_exc()
    
    # ============================================================================
    # SCHRITT 6: FÜHRE EXPORTS AUS (FALLS ANGEFORDERT)
    # ============================================================================
    
    if EXPORT_AVAILABLE and export_settings:
        # Screenshot-Export
        if export_settings.get("export_screenshot"):
            try:
                format = export_settings.get("screenshot_format", "png")
                width = export_settings.get("screenshot_width", 1600)
                height = export_settings.get("screenshot_height", 1000)
                
                with st.spinner(f"🔄 Erstelle Screenshot ({format.upper()})..."):
                    screenshot_bytes = export_screenshot(
                        fig=fig,
                        format=format,
                        width=width,
                        height=height
                    )
                    
                    if screenshot_bytes:
                        st.download_button(
                            label=f"📥 Screenshot herunterladen ({format.upper()})",
                            data=screenshot_bytes,
                            file_name=f"pv_3d_view.{format}",
                            mime=f"image/{format}"
                        )
                        st.success("✓ Screenshot erstellt!")
            except Exception as e:
                st.error(f"❌ Fehler beim Screenshot-Export: {e}")
                print("Fehler beim Screenshot-Export:")
                traceback.print_exc()
        
        # Multi-View Export
        if export_settings.get("export_multi_view"):
            try:
                with st.spinner("🔄 Erstelle Multi-View Screenshots..."):
                    views = export_settings.get("views", ["isometric", "top", "south", "east"])
                    resolution = export_settings.get("multi_view_resolution", (1200, 750))
                    
                    zip_bytes = export_multi_view(
                        project_data=project_data,
                        dims=dims,
                        roof_type=basis_settings.get("roof_type", roof_type),
                        module_quantity=module_quantity,
                        layout_config=layout_config,
                        views=views,
                        resolution=resolution
                    )
                    
                    if zip_bytes:
                        st.download_button(
                            label="📥 Multi-View ZIP herunterladen",
                            data=zip_bytes,
                            file_name="pv_3d_multi_view.zip",
                            mime="application/zip"
                        )
                        st.success("✓ Multi-View Export erstellt!")
            except Exception as e:
                st.error(f"❌ Fehler beim Multi-View Export: {e}")
                print("Fehler beim Multi-View Export:")
                traceback.print_exc()
        
        # 360° Animation
        if export_settings.get("export_360"):
            try:
                with st.spinner("🔄 Erstelle 360° Animation..."):
                    frames = export_settings.get("animation_frames", 36)
                    resolution = export_settings.get("animation_resolution", (600, 450))
                    
                    gif_bytes = export_360_animation(
                        project_data=project_data,
                        dims=dims,
                        roof_type=basis_settings.get("roof_type", roof_type),
                        module_quantity=module_quantity,
                        layout_config=layout_config,
                        frames=frames,
                        resolution=resolution
                    )
                    
                    if gif_bytes:
                        st.download_button(
                            label="📥 360° Animation herunterladen (GIF)",
                            data=gif_bytes,
                            file_name="pv_3d_animation_360.gif",
                            mime="image/gif"
                        )
                        st.success("✓ 360° Animation erstellt!")
            except Exception as e:
                st.error(f"❌ Fehler beim 360° Animation Export: {e}")
                print("Fehler beim 360° Animation Export:")
                traceback.print_exc()
        
        # 3D-Modell Export
        if export_settings.get("export_3d_model"):
            try:
                format = export_settings.get("model_format", "stl")
                
                with st.spinner(f"🔄 Erstelle 3D-Modell ({format.upper()})..."):
                    model_bytes = export_3d_model(
                        project_data=project_data,
                        dims=dims,
                        roof_type=basis_settings.get("roof_type", roof_type),
                        module_quantity=module_quantity,
                        layout_config=layout_config,
                        format=format
                    )
                    
                    if model_bytes:
                        st.download_button(
                            label=f"📥 3D-Modell herunterladen ({format.upper()})",
                            data=model_bytes,
                            file_name=f"pv_3d_model.{format}",
                            mime=f"application/{format}"
                        )
                        st.success("✓ 3D-Modell erstellt!")
            except Exception as e:
                st.error(f"❌ Fehler beim 3D-Modell Export: {e}")
                print("Fehler beim 3D-Modell Export:")
                traceback.print_exc()
    
    # ============================================================================
    # SCHRITT 7: ZUSÄTZLICHE INFORMATIONEN
    # ============================================================================
    
    # Zeige Statistiken
    with st.expander("📊 Statistiken", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Modulanzahl", module_quantity)
        
        with col2:
            roof_area = dims.length_m * dims.width_m
            st.metric("Dachfläche", f"{roof_area:.1f} m²")
        
        with col3:
            total_power = module_quantity * 0.4  # 400W pro Modul
            st.metric("Gesamtleistung", f"{total_power:.1f} kWp")
    
    # Zeige Hilfe
    with st.expander("❓ Hilfe", expanded=False):
        st.markdown("""
        ### Bedienung
        
        **Basis-Einstellungen:**
        - Passen Sie die Gebäudedimensionen an Ihr Projekt an
        - Wählen Sie die passende Dachform aus
        
        **Modul-Belegung:**
        - Automatisch: Module werden gleichmäßig verteilt
        - Manuell: Entfernen Sie einzelne Module nach Bedarf
        
        **Erweiterte Kontrolle:**
        - Aktivieren Sie die Kollisionserkennung
        - Wählen Sie einzelne Module oder Gruppen aus
        - Bearbeiten Sie Modul-Eigenschaften
        
        **Analyse:**
        - Nutzen Sie den Optimierungs-Assistenten für beste Ergebnisse
        - Analysieren Sie Verschattung zu verschiedenen Tageszeiten
        - Visualisieren Sie das Ertragspotential mit der Heatmap
        
        **Export:**
        - Erstellen Sie Screenshots in verschiedenen Formaten
        - Exportieren Sie Multi-View Ansichten als ZIP
        - Generieren Sie 360° Animationen
        - Exportieren Sie 3D-Modelle für CAD-Software
        """)


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    render_3d_view()
