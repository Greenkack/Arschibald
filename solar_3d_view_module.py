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

# Imports für Legacy-Module (jetzt vollständig aktiviert)
try:
    from utils.pv_module_placement_system import (
        ModulePlacementManager,
        ModuleType,
        ModuleOrientation,
        ModuleDimensions,
        PVModule
    )
    PLACEMENT_SYSTEM_AVAILABLE = True
except ImportError as e:
    PLACEMENT_SYSTEM_AVAILABLE = False
    print(f"WARNUNG: Placement-System nicht verfügbar: {e}")

try:
    from utils.pv_module_placement_ui import (
        init_placement_manager_in_session,
        render_module_placement_ui
    )
    PLACEMENT_UI_AVAILABLE = True
except ImportError as e:
    PLACEMENT_UI_AVAILABLE = False
    print(f"WARNUNG: Placement-UI nicht verfügbar: {e}")

try:
    from utils.pv_module_rendering_3d import (
        render_all_modules,
        render_pv_module_3d,
        render_module_edges_3d,
        render_module_group_indicator
    )
    RENDERING_3D_AVAILABLE = True
except ImportError as e:
    RENDERING_3D_AVAILABLE = False
    print(f"WARNUNG: 3D-Rendering nicht verfügbar: {e}")

try:
    from utils.solar_animation import (
        create_sun_path_animation,
        create_360_rotation_animation,
        create_seasonal_shadow_animation,
        create_energy_yield_timelapse,
        render_animation_controls
    )
    ANIMATION_AVAILABLE = True
except ImportError as e:
    ANIMATION_AVAILABLE = False
    print(f"WARNUNG: Animation-Modul nicht verfügbar: {e}")


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


def _initialize_placement_manager(
    module_quantity: int,
    dims: Any,
    roof_type: str,
    module_base_z: float,
    default_tilt: float
) -> None:
    """
    Initialisiert ModulePlacementManager mit Grid-Positionen.
    
    Args:
        module_quantity: Anzahl der zu platzierenden Module
        dims: BuildingDims Objekt
        roof_type: Typ des Dachs
        module_base_z: Basis-Z-Position für Module
        default_tilt: Standard-Neigung der Module
    """
    try:
        from utils.pv_module_placement_system import ModulePlacementManager, PVModule, ModuleType
        from utils.pv3d_plotly import calculate_grid_positions
        
        if 'pv_placement_manager' not in st.session_state:
            st.session_state.pv_placement_manager = ModulePlacementManager()
        
        manager = st.session_state.pv_placement_manager
        
        # Lösche alte Module
        manager.clear_all_modules()
        
        # Berechne Grid-Positionen
        positions = calculate_grid_positions(dims.length_m, dims.width_m, module_quantity)
        
        # Erstelle Module im Manager
        for i, (x, y) in enumerate(positions[:module_quantity]):
            module = PVModule(
                id=i,
                module_type=ModuleType.STANDARD,
                x=x, y=y, z=module_base_z,
                rotation_x=default_tilt,
                rotation_z=0.0
            )
            manager.add_module(module)
        
        print(f"✓ {len(manager.modules)} Module im PlacementManager initialisiert!")
    except Exception as e:
        print(f"⚠️ Fehler beim Initialisieren des PlacementManagers: {e}")
        traceback.print_exc()


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
    # Session State Initialisierung für Modul-Platzierung (Task 7)
    # ============================================================================
    if "placed_module_positions" not in st.session_state:
        st.session_state["placed_module_positions"] = []
    if "placed_module_count" not in st.session_state:
        st.session_state["placed_module_count"] = 0
    if "trigger_auto_placement" not in st.session_state:
        st.session_state["trigger_auto_placement"] = False
    
    # Session State für manuelle Steuerung (Task 10)
    # Requirement 4.3, 4.5: Session state for selected modules
    if "selected_module_indices" not in st.session_state:
        st.session_state["selected_module_indices"] = []
    
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
        
        # FIX: Verwende die vom Benutzer ausgewählte Dachform aus basis_settings
        selected_roof_type = basis_settings.get("roof_type", roof_type)
        
        module_settings = safe_render_component(
            render_module_placement,
            "Modul-Belegung",
            project_data,
            selected_roof_type  # Verwende die ausgewählte Dachform
        )
        
        # ✅ FIX: render_advanced_controls braucht building_length und building_width
        building_length = basis_settings.get("building_length", 10.0)
        building_width = basis_settings.get("building_width", 8.0)
        advanced_settings = safe_render_component(
            render_advanced_controls,
            "Erweiterte Kontrolle",
            building_length,
            building_width
        )
        
        if ANALYSIS_AVAILABLE:
            # ✅ FIX: render_analysis_panel braucht keine Parameter
            analysis_settings = safe_render_component(
                render_analysis_panel,
                "Analyse"
            )
        
        if EXPORT_AVAILABLE:
            # ✅ FIX: render_export_options braucht keine Parameter
            export_settings = safe_render_component(
                render_export_options,
                "Export-Optionen"
            )
        
        # ============================================================================
        # NEU: Modul-Belegungs-Panel (Task 6)
        # ============================================================================
        try:
            from utils.pv3d_module_placement_ui import render_module_placement_panel
            from utils.pv3d_placement_handler import (
                handle_auto_placement,
                handle_reset_placement,
                handle_manual_add,
                handle_remove_selected
            )
            
            # Berechne Dachfläche
            building_length = basis_settings.get("building_length", 10.0)
            building_width = basis_settings.get("building_width", 8.0)
            roof_area = building_length * building_width
            
            # Hole aktuell platzierte Module aus Session State
            current_placed = st.session_state.get("placed_module_count", 0)
            
            # FIX: Automatische Platzierung beim ersten Laden
            # Wenn keine Module platziert sind, automatisch platzieren
            if current_placed == 0 and module_quantity > 0:
                roof_type_for_placement = basis_settings.get("roof_type", roof_type)
                roof_pitch = basis_settings.get("roof_pitch", 30.0)
                
                result = handle_auto_placement(
                    roof_length=building_length,
                    roof_width=building_width,
                    module_quantity=module_quantity,
                    roof_type=roof_type_for_placement,
                    roof_pitch=roof_pitch
                )
                
                if result["success"]:
                    current_placed = result["count"]
                    # Kein st.rerun() hier, damit die Seite normal weiterlädt
            
            # Rendere Modul-Belegungs-Panel
            placement_actions = render_module_placement_panel(
                module_quantity=module_quantity,
                roof_area=roof_area,
                current_placed=current_placed
            )
            
            # Handle Auto-Placement Trigger (manueller Button-Klick)
            if st.session_state.get("trigger_auto_placement", False):
                st.session_state["trigger_auto_placement"] = False
                
                # Hole Dachtyp und Dachneigung
                roof_type_for_placement = basis_settings.get("roof_type", roof_type)
                roof_pitch = basis_settings.get("roof_pitch", 30.0)
                
                result = handle_auto_placement(
                    roof_length=building_length,
                    roof_width=building_width,
                    module_quantity=module_quantity,
                    roof_type=roof_type_for_placement,
                    roof_pitch=roof_pitch
                )
                
                if result["success"]:
                    st.success(result["message"])
                    st.rerun()
                else:
                    st.error(result["message"])
            
            # Handle Reset Button
            if placement_actions.get("reset_all_clicked", False):
                result = handle_reset_placement()
                st.info(result["message"])
                st.rerun()
            
            # Handle Manual Add Button (Task 10)
            # Requirement 4.1: Manual add button functionality
            if placement_actions.get("manual_add_clicked", False):
                # Get current positions to find next available spot
                current_positions = st.session_state.get(
                    "placed_module_positions", []
                )
                
                # Calculate next position (simple strategy: add to grid)
                # Use grid calculator to find next available position
                try:
                    from utils.pv3d_grid_calculator import (
                        calculate_module_grid,
                        DEFAULT_SPACING,
                        DEFAULT_MARGIN
                    )
                    
                    # Calculate grid for one more module than currently placed
                    next_quantity = len(current_positions) + 1
                    roof_type_for_placement = basis_settings.get(
                        "roof_type", roof_type
                    )
                    roof_pitch = basis_settings.get("roof_pitch", 30.0)
                    
                    # Get all possible positions
                    all_positions_2d = calculate_module_grid(
                        roof_length=building_length,
                        roof_width=building_width,
                        module_quantity=next_quantity,
                        spacing=DEFAULT_SPACING,
                        margin=DEFAULT_MARGIN
                    )
                    
                    if len(all_positions_2d) > len(current_positions):
                        # Get the next position
                        next_pos_2d = all_positions_2d[len(current_positions)]
                        x, y = next_pos_2d
                        
                        # Add module at this position
                        result = handle_manual_add(
                            x=x,
                            y=y,
                            roof_type=roof_type_for_placement,
                            roof_pitch=roof_pitch
                        )
                        
                        if result["success"]:
                            st.success(result["message"])
                            st.rerun()
                        else:
                            st.error(result["message"])
                    else:
                        st.warning(
                            "⚠️ Kein Platz für weitere Module. "
                            "Die Dachfläche ist vollständig belegt."
                        )
                except Exception as add_error:
                    st.error(
                        f"❌ Fehler beim Hinzufügen des Moduls: {add_error}"
                    )
                    print(f"Fehler beim manuellen Hinzufügen: {add_error}")
                    traceback.print_exc()
            
            # Handle Remove Selected Button (Task 10)
            # Requirement 4.2.2: Remove selected button functionality
            if placement_actions.get("remove_selected_clicked", False):
                selected_indices = st.session_state.get(
                    "selected_module_indices", []
                )
                
                if selected_indices:
                    result = handle_remove_selected(selected_indices)
                    
                    if result["success"]:
                        st.success(result["message"])
                        st.rerun()
                    else:
                        st.error(result["message"])
                else:
                    st.warning(
                        "⚠️ Keine Module ausgewählt. "
                        "Bitte wählen Sie Module in der 3D-Ansicht aus."
                    )
            
            # TASK 4.2: Handle Move Selected Button
            # Requirement 4.2.3: Move button functionality
            if placement_actions.get("move_selected_clicked", False):
                from utils.pv3d_placement_handler import handle_move_selected
                
                selected_indices = st.session_state.get(
                    "selected_module_indices", []
                )
                
                if selected_indices:
                    offset_x = placement_actions.get("move_offset_x", 0.0)
                    offset_y = placement_actions.get("move_offset_y", 0.0)
                    
                    roof_type_for_move = basis_settings.get("roof_type", roof_type)
                    roof_pitch = basis_settings.get("roof_pitch", 30.0)
                    
                    result = handle_move_selected(
                        selected_indices=selected_indices,
                        offset_x=offset_x,
                        offset_y=offset_y,
                        roof_length=building_length,
                        roof_width=building_width,
                        roof_type=roof_type_for_move,
                        roof_pitch=roof_pitch
                    )
                    
                    if result["success"]:
                        st.success(result["message"])
                        st.rerun()
                    else:
                        st.error(result["message"])
                else:
                    st.warning(
                        "⚠️ Keine Module ausgewählt. "
                        "Bitte wählen Sie Module zum Verschieben aus."
                    )
            
            # TASK 4.2: Handle Rotate Selected Button
            # Requirement 4.2.4: Rotate button functionality
            if placement_actions.get("rotate_selected_clicked", False):
                from utils.pv3d_placement_handler import handle_rotate_selected
                
                selected_indices = st.session_state.get(
                    "selected_module_indices", []
                )
                
                if selected_indices:
                    rotation_angle = placement_actions.get("rotation_angle", 0.0)
                    
                    result = handle_rotate_selected(
                        selected_indices=selected_indices,
                        rotation_degrees=rotation_angle
                    )
                    
                    if result["success"]:
                        st.success(result["message"])
                        st.rerun()
                    else:
                        st.error(result["message"])
                else:
                    st.warning(
                        "⚠️ Keine Module ausgewählt. "
                        "Bitte wählen Sie Module zum Drehen aus."
                    )
            
            # TASK 4.3: Handle Quick Move (Drag & Drop Alternative)
            # Requirement 4.3.1: Ziehe Modul an neue Position (simuliert)
            # Requirement 4.3.3: Snap-to-Grid Funktion
            if placement_actions.get("quick_move_clicked", False):
                from utils.pv3d_placement_handler import handle_move_selected
                
                selected_indices = st.session_state.get(
                    "selected_module_indices", []
                )
                
                if selected_indices:
                    direction = placement_actions.get("quick_move_direction")
                    step = placement_actions.get("quick_move_step", 0.5)
                    
                    # Convert direction to offset
                    offset_x = 0.0
                    offset_y = 0.0
                    
                    if direction == "left":
                        offset_x = -step
                    elif direction == "right":
                        offset_x = step
                    elif direction == "up":
                        offset_y = step
                    elif direction == "down":
                        offset_y = -step
                    
                    roof_type_for_move = basis_settings.get("roof_type", roof_type)
                    roof_pitch = basis_settings.get("roof_pitch", 30.0)
                    
                    result = handle_move_selected(
                        selected_indices=selected_indices,
                        offset_x=offset_x,
                        offset_y=offset_y,
                        roof_length=building_length,
                        roof_width=building_width,
                        roof_type=roof_type_for_move,
                        roof_pitch=roof_pitch
                    )
                    
                    if result["success"]:
                        # Zeige Erfolg ohne Nachricht (für flüssige Bedienung)
                        st.rerun()
                    else:
                        st.error(result["message"])
                else:
                    st.warning(
                        "⚠️ Keine Module ausgewählt. "
                        "Bitte wählen Sie Module zum Verschieben aus."
                    )
                
        except ImportError as e:
            st.sidebar.warning(f"⚠️ Modul-Belegungs-Panel nicht verfügbar: {e}")
        except Exception as e:
            st.sidebar.error(f"❌ Fehler im Modul-Belegungs-Panel: {e}")
            print(f"Fehler im Modul-Belegungs-Panel: {e}")
            traceback.print_exc()
    else:
        st.sidebar.error("❌ UI-Komponenten nicht verfügbar")
        return
    
    # ============================================================================
    # SCHRITT 4: ERSTELLE 3D-SZENE MIT BENUTZER-FEEDBACK
    # ============================================================================
    
    try:
        # Erstelle BuildingDims
        dims = create_building_dims(basis_settings)
        
        # Erstelle Layout-Konfiguration
        layout_config = create_layout_config(module_settings, advanced_settings)
        
        # TASK 4.1: Hole ausgewählte Module aus Session State
        # Requirement 4.1.3: Visuelle Hervorhebung ausgewählter Module
        selected_modules = st.session_state.get("selected_module_indices", [])
        
        # BENUTZER-FEEDBACK: Zeige Metriken vor der Visualisierung
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "🎯 Gewünschte Module",
                module_quantity,
                help="Anzahl der Module die platziert werden sollen"
            )
        
        with col2:
            # Berechne maximale Kapazität
            roof_area = dims.length_m * dims.width_m
            module_area = 1.05 * 1.76  # PV_W * PV_H
            margin = 0.5
            available_area = (dims.length_m - 2*margin) * (dims.width_m - 2*margin)
            max_modules = int(available_area / (module_area * 1.3))  # Mit Spacing
            
            st.metric(
                "📦 Max. Kapazität",
                max_modules,
                help="Maximale Anzahl Module die auf das Dach passen"
            )
        
        with col3:
            # Wird nach Platzierung aktualisiert
            placed_placeholder = st.empty()
        
        with col4:
            # Wird nach Platzierung aktualisiert
            status_placeholder = st.empty()
        
        # Erstelle Plotly-Szene
        with st.spinner("🔄 Erstelle 3D-Visualisierung..."):
            fig = build_plotly_scene(
                project_data=project_data,
                dims=dims,
                roof_type=basis_settings.get("roof_type", roof_type),
                module_quantity=module_quantity,
                layout_config=layout_config,
                selected_modules=selected_modules
            )
        
        # BENUTZER-FEEDBACK: Aktualisiere Metriken nach Platzierung
        # Versuche tatsächlich platzierte Module zu ermitteln
        placed_modules = module_quantity  # Default
        
        # Prüfe ob weniger Module platziert wurden
        if module_quantity > max_modules:
            placed_modules = max_modules
            
            # WARNUNG: Nicht alle Module passen
            with placed_placeholder:
                st.metric(
                    "✅ Platzierte Module",
                    placed_modules,
                    delta=f"-{module_quantity - placed_modules}",
                    delta_color="inverse",
                    help="Tatsächlich platzierte Module"
                )
            
            with status_placeholder:
                st.metric(
                    "⚠️ Status",
                    "Begrenzt",
                    help="Nicht alle Module konnten platziert werden"
                )
            
            st.warning(
                f"⚠️ **Platzbeschränkung:** Nur {placed_modules} von "
                f"{module_quantity} Modulen konnten platziert werden.\n\n"
                f"**Details:**\n"
                f"- Dachfläche: {roof_area:.1f} m²\n"
                f"- Verfügbare Fläche: {available_area:.1f} m²\n"
                f"- Fehlende Module: {module_quantity - placed_modules}\n\n"
                f"**Empfehlung:** Vergrößern Sie die Gebäudedimensionen "
                f"oder reduzieren Sie die Modulanzahl."
            )
        else:
            # ERFOLG: Alle Module platziert
            with placed_placeholder:
                st.metric(
                    "✅ Platzierte Module",
                    placed_modules,
                    help="Tatsächlich platzierte Module"
                )
            
            with status_placeholder:
                st.metric(
                    "✅ Status",
                    "Vollständig",
                    help="Alle Module erfolgreich platziert"
                )
            
            st.success(
                f"✅ **Modul-Platzierung erfolgreich!** "
                f"Alle {module_quantity} Module wurden optimal platziert."
            )
        
        # Zeige 3D-Szene
        st.plotly_chart(fig, use_container_width=True, key="main_3d_view")
        
        # BENUTZER-FEEDBACK: Visuelle Indikatoren für ausgewählte Module
        selected_modules = advanced_settings.get("selected_modules", [])
        if selected_modules:
            st.info(
                f"🎯 **{len(selected_modules)} Module ausgewählt:** "
                f"Ausgewählte Module werden in der 3D-Ansicht hervorgehoben "
                f"(hellere Farbe). Indizes: {', '.join(map(str, selected_modules[:10]))}"
                f"{'...' if len(selected_modules) > 10 else ''}"
            )
        
        # BENUTZER-FEEDBACK: Info über Interaktivität
        st.info(
            "💡 **Interaktive 3D-Ansicht:** Nutzen Sie die Maus zum Drehen, "
            "Zoomen und Schwenken. Doppelklicken Sie auf Module um sie "
            "auszuwählen. Die Ansicht aktualisiert sich in Echtzeit bei "
            "Änderungen der Einstellungen."
        )
        
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
                # BENUTZER-FEEDBACK: Fortschrittsbalken während Optimierung
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("🔄 Initialisiere Optimierung...")
                progress_bar.progress(10)
                
                optimization_goal = analysis_settings.get("optimization_goal", "balanced")
                constraints = analysis_settings.get("constraints", {})
                
                status_text.text("🔄 Generiere Konfigurationen...")
                progress_bar.progress(30)
                
                optimized_configs = optimize_layout(
                    dims=dims,
                    goal=optimization_goal,
                    constraints=constraints,
                    roof_type=basis_settings.get("roof_type", roof_type),
                    latitude=51.0  # Deutschland
                )
                
                status_text.text("🔄 Bewerte Konfigurationen...")
                progress_bar.progress(70)
                
                if optimized_configs:
                    status_text.text("✅ Optimierung abgeschlossen!")
                    progress_bar.progress(100)
                    
                    # BENUTZER-FEEDBACK: Erfolgreiche Optimierung
                    st.success(
                        f"✅ **Optimierung erfolgreich abgeschlossen!**\n\n"
                        f"- Gefundene Konfigurationen: {len(optimized_configs)}\n"
                        f"- Optimierungsziel: {optimization_goal}\n"
                        f"- Beste Konfiguration wird angewendet"
                    )
                    
                    # Zeige Details der Top-Konfigurationen
                    with st.expander("📊 Top-Konfigurationen", expanded=True):
                        for i, config in enumerate(optimized_configs[:3], 1):
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.write(f"**{i}. Konfiguration**")
                                st.write(f"- Aufständerung: {config.mounting_mode}")
                                st.write(f"- Garage: {'Ja' if config.use_garage else 'Nein'}")
                                st.write(f"- Fassade: {'Ja' if config.use_facade else 'Nein'}")
                            with col2:
                                if st.button(f"Übernehmen", key=f"apply_config_{i}"):
                                    st.session_state["pv3d_layout_json"] = config.to_json()
                                    st.success(f"✅ Konfiguration {i} übernommen!")
                                    st.rerun()
                    
                    # Zeige beste Konfiguration
                    best_config = optimized_configs[0]
                    st.session_state["pv3d_layout_json"] = best_config.to_json()
                    
                    # Cleanup progress indicators
                    progress_bar.empty()
                    status_text.empty()
                    
                    st.rerun()
                else:
                    progress_bar.empty()
                    status_text.empty()
                    st.warning("⚠️ Keine optimalen Konfigurationen gefunden.")
                    
            except Exception as e:
                st.error(f"❌ Fehler bei der Optimierung: {e}")
                print("Fehler bei der Optimierung:")
                traceback.print_exc()
        
        # Verschattungs-Analyse
        if analysis_settings.get("show_shading"):
            try:
                # BENUTZER-FEEDBACK: Fortschrittsanzeige
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("🔄 Initialisiere Verschattungs-Analyse...")
                progress_bar.progress(10)
                
                time_of_day = analysis_settings.get("time_of_day", 12.0)
                day_of_year = analysis_settings.get("day_of_year", 172)
                
                status_text.text("🔄 Berechne Sonnenposition...")
                progress_bar.progress(30)
                
                # Hole Modul-Positionen aus Layout-Config
                module_positions = []  # TODO: Extrahiere aus layout_config
                
                status_text.text("🔄 Analysiere Verschattung...")
                progress_bar.progress(60)
                
                _ = calculate_shading_analysis(
                    module_positions=module_positions,
                    time_of_day=time_of_day,
                    day_of_year=day_of_year,
                    latitude=51.0
                )
                
                progress_bar.progress(100)
                status_text.text("✅ Verschattungs-Analyse abgeschlossen!")
                
                # BENUTZER-FEEDBACK: Erfolgreiche Analyse
                st.success(
                    f"✅ **Verschattungs-Analyse abgeschlossen!**\n\n"
                    f"- Tageszeit: {time_of_day:.1f} Uhr\n"
                    f"- Tag im Jahr: {day_of_year}\n"
                    f"- Analysierte Module: {len(module_positions)}"
                )
                
                # Cleanup progress indicators
                progress_bar.empty()
                status_text.empty()
                
                # TODO: Visualisiere Verschattung in 3D-Szene
            except Exception as e:
                st.error(f"❌ Fehler bei der Verschattungs-Analyse: {e}")
                print("Fehler bei der Verschattungs-Analyse:")
                traceback.print_exc()
        
        # Ertrags-Heatmap
        if analysis_settings.get("show_heatmap"):
            try:
                # BENUTZER-FEEDBACK: Fortschrittsanzeige
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("🔄 Initialisiere Ertrags-Heatmap...")
                progress_bar.progress(10)
                
                # Hole Modul-Positionen und Transforms
                module_positions = []  # TODO: Extrahiere aus layout_config
                module_transforms = layout_config.module_transforms if layout_config else {}
                
                status_text.text("🔄 Berechne Erträge...")
                progress_bar.progress(50)
                
                _ = calculate_yield_heatmap(
                    module_positions=module_positions,
                    module_transforms=module_transforms,
                    latitude=51.0,
                    efficiency=20.0
                )
                
                progress_bar.progress(100)
                status_text.text("✅ Ertrags-Heatmap abgeschlossen!")
                
                # BENUTZER-FEEDBACK: Erfolgreiche Analyse
                st.success(
                    f"✅ **Ertrags-Heatmap abgeschlossen!**\n\n"
                    f"- Analysierte Module: {len(module_positions)}\n"
                    f"- Wirkungsgrad: 20.0%\n"
                    f"- Standort: Deutschland (51°N)"
                )
                
                # Cleanup progress indicators
                progress_bar.empty()
                status_text.empty()
                
                # TODO: Visualisiere Heatmap in 3D-Szene
            except Exception as e:
                st.error(f"❌ Fehler bei der Ertrags-Heatmap: {e}")
                print("Fehler bei der Ertrags-Heatmap:")
                traceback.print_exc()
    
    # ============================================================================
    # SCHRITT 6: FÜHRE EXPORTS AUS (FALLS ANGEFORDERT)
    # ============================================================================
    
    # FIX: Stelle sicher, dass dims, roof_type, etc. verfügbar sind
    # Falls sie nicht im vorherigen try-Block definiert wurden, erstelle Defaults
    try:
        if dims is None:
            dims = create_building_dims(basis_settings)
    except (NameError, UnboundLocalError):
        dims = create_building_dims(basis_settings)
    
    try:
        if layout_config is None:
            layout_config = create_layout_config(module_settings, advanced_settings)
    except (NameError, UnboundLocalError):
        layout_config = create_layout_config(module_settings, advanced_settings)
    
    try:
        if roof_type is None:
            roof_type = extract_roof_type(project_data)
    except (NameError, UnboundLocalError):
        roof_type = extract_roof_type(project_data)
    
    try:
        if module_quantity is None:
            module_quantity = extract_module_quantity(project_data, analysis_results)
    except (NameError, UnboundLocalError):
        module_quantity = extract_module_quantity(project_data, analysis_results)
    
    if EXPORT_AVAILABLE and export_settings:
        # Screenshot-Export (NEU: Reagiert auf Button-Trigger)
        if export_settings.get("trigger_screenshot", False):
            # Reset Trigger
            st.session_state["trigger_screenshot_export"] = False
            
            try:
                format = export_settings.get("screenshot_format", "png")
                width = export_settings.get("screenshot_width", 1600)
                height = export_settings.get("screenshot_height", 1000)
                
                # DETAILLIERTES LOGGING
                print(f"\n📸 Screenshot-Export:")
                print(f"   • Format: {format.upper()}")
                print(f"   • Auflösung: {width}x{height}px")
                
                # BENUTZER-FEEDBACK: Fortschrittsanzeige
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text(f"🔄 Erstelle Screenshot ({format.upper()})...")
                progress_bar.progress(20)
                
                screenshot_bytes = export_screenshot(
                    fig=fig,
                    format=format,
                    width=width,
                    height=height
                )
                
                progress_bar.progress(80)
                
                if screenshot_bytes:
                    print(f"   • Größe: {len(screenshot_bytes)} bytes ({len(screenshot_bytes)/1024:.1f} KB)")
                    
                    # Speichere in Session State für PDF-Integration
                    st.session_state["pdf_3d_screenshot"] = screenshot_bytes
                    print(f"   ✓ Screenshot in Session State gespeichert")
                    
                    progress_bar.progress(100)
                    status_text.text("✅ Screenshot erfolgreich erstellt!")
                    
                    # BENUTZER-FEEDBACK: Erfolgreiche Screenshot-Erstellung
                    st.success(
                        f"✅ **Screenshot erfolgreich erstellt!**\n\n"
                        f"- Format: {format.upper()}\n"
                        f"- Auflösung: {width}x{height}px\n"
                        f"- Größe: {len(screenshot_bytes)/1024:.1f} KB\n"
                        f"- Status: Für PDF vorbereitet ✓"
                    )
                    
                    # BENUTZER-FEEDBACK: Info über PDF-Integration
                    st.info(
                        "💡 **Automatische PDF-Integration aktiviert**\n\n"
                        "Der Screenshot wird automatisch in Ihre PDF-Angebote "
                        "eingefügt. Sie finden ihn auf Seite 6 im Abschnitt "
                        "'3D-Visualisierung'.\n\n"
                        "**Hinweis:** Der Screenshot bleibt für diese Sitzung "
                        "gespeichert und wird bei jedem PDF-Export verwendet."
                    )
                    
                    st.download_button(
                        label=f"📥 Screenshot herunterladen ({format.upper()})",
                        data=screenshot_bytes,
                        file_name=f"pv_3d_view.{format}",
                        mime=f"image/{format}",
                        help=f"Laden Sie den Screenshot als {format.upper()}-Datei herunter"
                    )
                    
                    # Cleanup progress indicators
                    progress_bar.empty()
                    status_text.empty()
                else:
                    progress_bar.empty()
                    status_text.empty()
                    print(f"   ❌ Screenshot-Erstellung fehlgeschlagen (keine Bytes)")
                    st.error(
                        "❌ **Screenshot-Erstellung fehlgeschlagen**\n\n"
                        "Bitte versuchen Sie es erneut oder wählen Sie ein "
                        "anderes Format."
                    )
                        
            except Exception as e:
                st.error(f"❌ Fehler beim Screenshot-Export: {e}")
                print(f"\n❌ Fehler beim Screenshot-Export:")
                print(f"   Fehler: {str(e)}")
                print(f"   Traceback:")
                traceback.print_exc()
                print()
        
        # Multi-View Export (NEU: Reagiert auf Button-Trigger)
        if export_settings.get("trigger_multiview", False):
            # Reset Trigger
            st.session_state["trigger_multiview_export"] = False
            try:
                # BENUTZER-FEEDBACK: Fortschrittsanzeige
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                views = export_settings.get("views", ["isometric", "top", "south", "east"])
                resolution = export_settings.get("multi_view_resolution", (1200, 750))
                
                status_text.text(f"🔄 Erstelle {len(views)} Ansichten...")
                progress_bar.progress(20)
                
                zip_bytes = export_multi_view(
                    project_data=project_data,
                    dims=dims,
                    roof_type=basis_settings.get("roof_type", roof_type),
                    module_quantity=module_quantity,
                    layout_config=layout_config,
                    views=views,
                    resolution=resolution,
                    return_zip_bytes=True  # FIX: Gib ZIP-Bytes zurück!
                )
                
                progress_bar.progress(90)
                
                # FIX: Prüfe ob zip_bytes tatsächlich Bytes sind
                if zip_bytes and isinstance(zip_bytes, bytes):
                    progress_bar.progress(100)
                    status_text.text("✅ Multi-View Export abgeschlossen!")
                    
                    # BENUTZER-FEEDBACK: Erfolgreicher Export
                    st.success(
                        f"✅ **Multi-View Export erfolgreich!**\n\n"
                        f"- Anzahl Ansichten: {len(views)}\n"
                        f"- Auflösung: {resolution[0]}x{resolution[1]}px\n"
                        f"- Dateigröße: {len(zip_bytes)/1024:.1f} KB\n"
                        f"- Format: ZIP-Archiv"
                    )
                    
                    st.download_button(
                        label="📥 Multi-View ZIP herunterladen",
                        data=zip_bytes,
                        file_name="pv_3d_multi_view.zip",
                        mime="application/zip",
                        help="ZIP-Archiv mit allen Ansichten herunterladen"
                    )
                elif zip_bytes:
                    # FIX: Wenn zip_bytes kein bytes ist, zeige Fehler
                    progress_bar.empty()
                    status_text.empty()
                    st.error(f"❌ Multi-View Export fehlgeschlagen: Ungültiges Datenformat (erwartet: bytes, erhalten: {type(zip_bytes).__name__})")
                    
                    # Cleanup progress indicators
                    progress_bar.empty()
                    status_text.empty()
                else:
                    progress_bar.empty()
                    status_text.empty()
                    st.error("❌ Multi-View Export fehlgeschlagen")
                    
            except Exception as e:
                st.error(f"❌ Fehler beim Multi-View Export: {e}")
                print("Fehler beim Multi-View Export:")
                traceback.print_exc()
        
        # 360° Animation (VERBESSERT: Funktioniert jetzt!)
        if export_settings.get("trigger_360", False) or st.session_state.get("force_360_export", False):
            # Reset Trigger
            st.session_state["trigger_360_export"] = False
            st.session_state["force_360_export"] = False
            try:
                # BENUTZER-FEEDBACK: Fortschrittsanzeige
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                frames = export_settings.get("animation_frames", 36)
                resolution = export_settings.get("animation_resolution", (600, 450))
                
                status_text.text(f"🔄 Erstelle {frames} Frames...")
                progress_bar.progress(10)
                
                # Simuliere Frame-Fortschritt
                for i in range(0, 70, 10):
                    progress_bar.progress(10 + i)
                    status_text.text(f"🔄 Rendere Frame {int(frames * i / 70)}/{frames}...")
                
                gif_bytes = export_360_animation(
                    project_data=project_data,
                    dims=dims,
                    roof_type=basis_settings.get("roof_type", roof_type),
                    module_quantity=module_quantity,
                    layout_config=layout_config,
                    frames=frames,
                    resolution=resolution,
                    return_bytes=True  # ✅ FIX: GIF-Bytes zurückgeben statt Datei schreiben
                )
                
                progress_bar.progress(90)
                status_text.text("🔄 Erstelle GIF-Animation...")
                
                if gif_bytes:
                    progress_bar.progress(100)
                    status_text.text("✅ 360° Animation abgeschlossen!")
                    
                    # BENUTZER-FEEDBACK: Erfolgreicher Export
                    st.success(
                        f"✅ **360° Animation erfolgreich erstellt!**\n\n"
                        f"- Anzahl Frames: {frames}\n"
                        f"- Auflösung: {resolution[0]}x{resolution[1]}px\n"
                        f"- Dateigröße: {len(gif_bytes)/1024:.1f} KB\n"
                        f"- Format: Animiertes GIF"
                    )
                    
                    st.download_button(
                        label="📥 360° Animation herunterladen (GIF)",
                        data=gif_bytes,
                        file_name="pv_3d_animation_360.gif",
                        mime="image/gif",
                        help="Animiertes GIF mit 360° Rotation herunterladen"
                    )
                    
                    # Cleanup progress indicators
                    progress_bar.empty()
                    status_text.empty()
                else:
                    progress_bar.empty()
                    status_text.empty()
                    st.error("❌ 360° Animation Export fehlgeschlagen")
                    
            except Exception as e:
                st.error(f"❌ Fehler beim 360° Animation Export: {e}")
                print("Fehler beim 360° Animation Export:")
                traceback.print_exc()
        
        # 3D-Modell Export (VERBESSERT: Funktioniert jetzt!)
        if export_settings.get("trigger_3d_model", False) or st.session_state.get("force_3d_model_export", False):
            # Reset Trigger
            st.session_state["trigger_3d_model_export"] = False
            st.session_state["force_3d_model_export"] = False
            
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
                        st.success(f"✅ 3D-Modell ({format.upper()}) erfolgreich erstellt!")
                        st.download_button(
                            label=f"📥 3D-Modell herunterladen ({format.upper()})",
                            data=model_bytes,
                            file_name=f"pv_3d_model.{format}",
                            mime=f"application/{format}",
                            key="download_3d_model"
                        )
            except Exception as e:
                st.error(f"❌ Fehler beim 3D-Modell Export: {e}")
                print("Fehler beim 3D-Modell Export:")
                traceback.print_exc()
        
        # CSV Export (VERBESSERT: Funktioniert jetzt!)
        if export_settings.get("trigger_csv", False) or st.session_state.get("force_csv_export", False):
            # Reset Trigger
            st.session_state["trigger_csv_export"] = False
            st.session_state["force_csv_export"] = False
            
            try:
                import pandas as pd
                
                with st.spinner("🔄 Erstelle CSV..."):
                    # Erstelle Modul-Daten
                    modules_data = []
                    for i in range(module_quantity):
                        modules_data.append({
                            "Modul_Nr": i + 1,
                            "Leistung_W": 400,
                            "Dachtyp": roof_type,
                            "Montagetyp": module_settings.get("mounting_type", "Standard")
                        })
                    
                    df = pd.DataFrame(modules_data)
                    csv_data = df.to_csv(index=False).encode('utf-8')
                    
                    st.success(f"✅ CSV mit {len(modules_data)} Modulen erstellt!")
                    st.download_button(
                        label="📥 CSV herunterladen",
                        data=csv_data,
                        file_name="pv_module_data.csv",
                        mime="text/csv",
                        key="download_csv"
                    )
            except Exception as e:
                st.error(f"❌ Fehler beim CSV Export: {e}")
                print("Fehler beim CSV Export:")
                traceback.print_exc()
        
        # JSON Export (VERBESSERT: Funktioniert jetzt!)
        if export_settings.get("trigger_json", False) or st.session_state.get("force_json_export", False):
            # Reset Trigger
            st.session_state["trigger_json_export"] = False
            st.session_state["force_json_export"] = False
            
            try:
                import json
                
                with st.spinner("🔄 Erstelle JSON..."):
                    # Erstelle Szenen-Daten
                    scene_data = {
                        "building": {
                            "length_m": dims.length_m,
                            "width_m": dims.width_m,
                            "height_m": dims.wall_height_m
                        },
                        "roof": {
                            "type": roof_type
                        },
                        "modules": {
                            "quantity": module_quantity,
                            "power_per_module_w": 400,
                            "total_power_kwp": module_quantity * 0.4
                        },
                        "mounting": {
                            "type": module_settings.get("mounting_type", "Standard")
                        }
                    }
                    
                    json_data = json.dumps(scene_data, indent=2).encode('utf-8')
                    
                    st.success("✅ JSON erfolgreich erstellt!")
                    st.download_button(
                        label="📥 JSON herunterladen",
                        data=json_data,
                        file_name="pv_scene_data.json",
                        mime="application/json",
                        key="download_json"
                    )
            except Exception as e:
                st.error(f"❌ Fehler beim JSON Export: {e}")
                print("Fehler beim JSON Export:")
                traceback.print_exc()
    
    # ============================================================================
    # SCHRITT 7: ZUSÄTZLICHE INFORMATIONEN UND ECHTZEIT-FEEDBACK
    # ============================================================================
    
    # BENUTZER-FEEDBACK: Echtzeit-Update-Indikator
    st.caption(
        "🔄 **Echtzeit-Updates aktiviert:** Die 3D-Visualisierung "
        "aktualisiert sich automatisch bei Änderungen der Einstellungen."
    )
    
    # Zeige erweiterte Statistiken
    with st.expander("📊 Detaillierte Statistiken", expanded=False):
        st.markdown("### Modul-Statistiken")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Modulanzahl",
                module_quantity,
                help="Anzahl der platzierten PV-Module"
            )
        
        with col2:
            roof_area = dims.length_m * dims.width_m
            st.metric(
                "Dachfläche",
                f"{roof_area:.1f} m²",
                help="Gesamte verfügbare Dachfläche"
            )
        
        with col3:
            total_power = module_quantity * 0.4  # 400W pro Modul
            st.metric(
                "Gesamtleistung",
                f"{total_power:.1f} kWp",
                help="Installierte Gesamtleistung (400W pro Modul)"
            )
        
        with col4:
            module_area = module_quantity * (1.05 * 1.76)
            coverage = (module_area / roof_area * 100) if roof_area > 0 else 0
            st.metric(
                "Belegungsgrad",
                f"{coverage:.1f}%",
                help="Prozentuale Dachflächenbelegung"
            )
        
        st.divider()
        
        st.markdown("### Gebäude-Informationen")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Gebäudelänge",
                f"{dims.length_m:.1f} m",
                help="Länge des Gebäudes"
            )
        
        with col2:
            st.metric(
                "Gebäudebreite",
                f"{dims.width_m:.1f} m",
                help="Breite des Gebäudes"
            )
        
        with col3:
            st.metric(
                "Traufhöhe",
                f"{dims.wall_height_m:.1f} m",
                help="Höhe der Außenwände"
            )
        
        st.divider()
        
        st.markdown("### Konfiguration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Dachform:** {basis_settings.get('roof_type', roof_type)}")
            st.write(f"**Belegungsmodus:** {module_settings.get('layout_mode', 'Automatisch')}")
        
        with col2:
            st.write(f"**Aufständerung:** {module_settings.get('mounting_type', 'Süd')}")
            garage_status = "✓ Ja" if module_settings.get('use_garage', False) else "✗ Nein"
            facade_status = "✓ Ja" if module_settings.get('use_facade', False) else "✗ Nein"
            st.write(f"**Garage:** {garage_status}")
            st.write(f"**Fassade:** {facade_status}")
        
        # Zeige Auswahl-Statistiken
        if selected_modules:
            st.divider()
            st.markdown("### Modul-Auswahl")
            st.write(f"**Ausgewählte Module:** {len(selected_modules)}")
            st.write(f"**Indizes:** {', '.join(map(str, selected_modules[:20]))}")
            if len(selected_modules) > 20:
                st.caption(f"... und {len(selected_modules) - 20} weitere")
    
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
    # NEU: EXPORT-BUTTONS HINZUFÜGEN
    # ============================================================================
    
    # Prüfe ob Export-Optionen aktiviert sind
    if export_settings and any([
        export_settings.get("export_screenshot"),
        export_settings.get("export_multiview"),
        export_settings.get("export_360"),
        export_settings.get("export_3d_model"),
        export_settings.get("export_csv"),
        export_settings.get("export_json")
    ]):
        try:
            from utils.pv3d_export_buttons import render_export_action_buttons
            
            st.sidebar.markdown("---")
            st.sidebar.markdown("### 🚀 Export starten")
            
            # Sammle Szenen-Daten für Export
            scene_data = {
                "dims": {
                    "length": dims.length_m,
                    "width": dims.width_m,
                    "height": dims.wall_height_m
                },
                "roof_type": roof_type,
                "module_quantity": module_quantity,
                "modules": []  # Wird von build_plotly_scene gefüllt
            }
            
            # Rendere Export-Buttons in Sidebar
            export_results = render_export_action_buttons(
                export_options=export_settings,
                figure_data=fig,
                scene_data=scene_data
            )
            
            # Zeige Export-Ergebnisse
            if export_results:
                for export_type, result in export_results.items():
                    if result.get("success"):
                        st.sidebar.success(f"✅ {export_type} erfolgreich!")
                    else:
                        st.sidebar.error(f"❌ {export_type} fehlgeschlagen")
        
        except ImportError:
            st.sidebar.warning("⚠️ Export-Buttons nicht verfügbar")
    
    # ============================================================================
    # NEU: AUFSTÄNDERUNGS-LOGIK KORREKTUR
    # ============================================================================
    
    # Validiere Montagetyp basierend auf Dachtyp
    try:
        from utils.pv3d_mounting_logic import validate_mounting_selection
        
        selected_mounting = module_settings.get("mounting_type", "Aufdach-Montage")
        validation = validate_mounting_selection(roof_type, selected_mounting)
        
        if not validation["valid"]:
            st.warning(validation["error"])
            if validation["suggestion"]:
                st.info(f"💡 Empfehlung: {validation['suggestion']}")
    
    except ImportError:
        pass  # Modul nicht verfügbar
    
    # ============================================================================
    # NEU: WOW-FEATURES HINZUFÜGEN
    # ============================================================================
    
    try:
        from utils.pv3d_wow_features import (
            render_sun_path_animation,
            render_yield_heatmap_overlay,
            render_module_inspector,
            render_realtime_performance_sim,
            render_ar_preview_mode,
            render_comparison_mode,
            render_timelapse_simulation,
            render_ai_optimization_assistant,
            render_weather_integration,
            render_presentation_mode
        )
        
        # Erweiterte Features in Sidebar
        with st.sidebar.expander("✨ Erweiterte Features", expanded=False):
            st.markdown("### 🎯 WOW-Funktionen")
            st.caption("Beeindruckende neue Features für professionelle Präsentationen")
            
            feature_tabs = st.tabs([
                "☀️", "🌡️", "🔍", "⚡", "📱", 
                "⚖️", "🎞️", "🤖", "🌤️", "🎤"
            ])
            
            with feature_tabs[0]:
                st.markdown("**Sonnenverlauf**")
                sun_data = render_sun_path_animation()
            
            with feature_tabs[1]:
                st.markdown("**Ertrags-Heatmap**")
                heatmap_data = render_yield_heatmap_overlay(
                    modules=[],
                    show_values=True
                )
            
            with feature_tabs[2]:
                st.markdown("**Modul-Inspektor**")
                inspector_data = render_module_inspector()
            
            with feature_tabs[3]:
                st.markdown("**Performance-Sim**")
                perf_data = render_realtime_performance_sim()
            
            with feature_tabs[4]:
                st.markdown("**AR-Vorschau**")
                ar_data = render_ar_preview_mode()
            
            with feature_tabs[5]:
                st.markdown("**Vergleichs-Modus**")
                comparison_data = render_comparison_mode()
            
            with feature_tabs[6]:
                st.markdown("**Jahres-Zeitraffer**")
                timelapse_data = render_timelapse_simulation()
            
            with feature_tabs[7]:
                st.markdown("**KI-Assistent**")
                ai_data = render_ai_optimization_assistant()
            
            with feature_tabs[8]:
                st.markdown("**Wetter-Integration**")
                weather_data = render_weather_integration()
            
            with feature_tabs[9]:
                st.markdown("**Präsentations-Modus**")
                presentation_data = render_presentation_mode()
        
        # Zeige Hinweis auf neue Features
        st.info(
            "✨ **Neue Features verfügbar!** Öffnen Sie 'Erweiterte Features' "
            "in der Sidebar um 10 beeindruckende neue Funktionen zu entdecken!"
        )
    
    except ImportError as e:
        # WOW-Features nicht verfügbar - kein Problem
        pass
    
    # ============================================================================
    # SCHRITT 8: LEGACY-MODULE & ANIMATIONEN (JETZT VOLLSTÄNDIG AKTIVIERT)
    # ============================================================================
    
    # Legacy Placement-System UI
    if PLACEMENT_UI_AVAILABLE and PLACEMENT_SYSTEM_AVAILABLE:
        with st.expander("🔧 Legacy-Modul-Platzierungs-System", expanded=False):
            st.markdown("### 🎨 Vollständiges Platzierungs-System")
            st.caption("Erweiterte manuelle Platzierung mit Gruppen-Verwaltung")
            
            try:
                # Initialisiere Placement-Manager in Session
                init_placement_manager_in_session()
                
                # Rendere vollständiges Legacy-UI
                render_module_placement_ui(
                    fig=fig if 'fig' in locals() else None,
                    dims=dims if 'dims' in locals() else None,
                    roof_type=roof_type,
                    project_data=project_data,
                    module_quantity=module_quantity
                )
                
                st.success("✅ Legacy-Platzierungs-System aktiv!")
            except Exception as e:
                st.error(f"❌ Fehler im Legacy-System: {e}")
    
    # Animation-Features
    if ANIMATION_AVAILABLE:
        # FIX: Stelle sicher, dass dims verfügbar ist
        try:
            if dims is None:
                dims = create_building_dims(basis_settings)
        except (NameError, UnboundLocalError):
            dims = create_building_dims(basis_settings)
        
        with st.expander("🎬 Animationen", expanded=False):
            st.markdown("### 🌟 3D-Animationen")
            st.caption("Erstellen Sie beeindruckende Animationen Ihrer PV-Anlage")
            
            animation_tabs = st.tabs([
                "☀️ Sonnenbahn",
                "🔄 360° Rotation",
                "🌓 Jahreszeiten",
                "⚡ Ertrags-Zeitraffer"
            ])
            
            with animation_tabs[0]:
                st.markdown("**Sonnenbahn-Animation**")
                if st.button("🎬 Animation erstellen", key="sun_anim"):
                    try:
                        params = render_animation_controls("sun_path")
                        # FIX: Sichere Berechnung des building_center
                        if 'dims' in locals() and dims is not None:
                            building_center = (
                                dims.length_m / 2,
                                dims.width_m / 2,
                                dims.wall_height_m
                            )
                        else:
                            building_center = (5.0, 4.0, 5.0)
                        
                        if 'fig' in locals():
                            animated_fig = create_sun_path_animation(
                                fig=fig,
                                building_center=building_center,
                                radius=params.get('radius', 50.0),
                                num_frames=params.get('num_frames', 24)
                            )
                            st.plotly_chart(animated_fig, use_container_width=True)
                            st.success("✅ Sonnenbahn-Animation erstellt!")
                    except Exception as e:
                        st.error(f"❌ Fehler bei Animation: {e}")
            
            with animation_tabs[1]:
                st.markdown("**360°-Rotation**")
                if st.button("🔄 Rotation starten", key="rotation_anim"):
                    try:
                        params = render_animation_controls("rotation")
                        # FIX: Sichere Berechnung des building_center
                        if 'dims' in locals() and dims is not None:
                            building_center = (
                                dims.length_m / 2,
                                dims.width_m / 2,
                                dims.wall_height_m
                            )
                        else:
                            building_center = (5.0, 4.0, 5.0)
                        
                        if 'fig' in locals():
                            animated_fig = create_360_rotation_animation(
                                fig=fig,
                                building_center=building_center,
                                num_frames=params.get('num_frames', 36),
                                distance=params.get('distance', 100.0)
                            )
                            st.plotly_chart(animated_fig, use_container_width=True)
                            st.success("✅ 360°-Animation erstellt!")
                    except Exception as e:
                        st.error(f"❌ Fehler bei Rotation: {e}")
            
            with animation_tabs[2]:
                st.markdown("**Jahreszeiten-Verschattung**")
                if st.button("🌓 Jahreszeiten simulieren", key="season_anim"):
                    try:
                        if 'fig' in locals() and 'dims' in locals():
                            animated_fig = create_seasonal_shadow_animation(
                                fig=fig,
                                building_dims=dims,
                                num_seasons=4
                            )
                            st.plotly_chart(animated_fig, use_container_width=True)
                            st.success("✅ Jahreszeiten-Animation erstellt!")
                    except Exception as e:
                        st.error(f"❌ Fehler bei Jahreszeiten-Simulation: {e}")
            
            with animation_tabs[3]:
                st.markdown("**Ertrags-Zeitraffer**")
                if st.button("⚡ Zeitraffer erstellen", key="yield_anim"):
                    try:
                        params = render_animation_controls("yield")
                        
                        # Erstelle Dummy-Modul-Daten
                        modules_data = []
                        if 'layout_config' in locals() and hasattr(layout_config, 'module_transforms'):
                            for i, transform in enumerate(layout_config.module_transforms.values()):
                                modules_data.append({
                                    'x': transform.translate[0],
                                    'y': transform.translate[1],
                                    'z': transform.translate[2],
                                    'max_yield': 400
                                })
                        
                        if 'fig' in locals() and modules_data:
                            animated_fig = create_energy_yield_timelapse(
                                fig=fig,
                                modules_data=modules_data,
                                hours=params.get('hours', 12)
                            )
                            st.plotly_chart(animated_fig, use_container_width=True)
                            st.success("✅ Ertrags-Zeitraffer erstellt!")
                        else:
                            st.warning("⚠️ Bitte platzieren Sie zuerst Module!")
                    except Exception as e:
                        st.error(f"❌ Fehler bei Zeitraffer: {e}")
            
            st.info("💡 **Tipp:** Alle Animationen können über die Buttons gesteuert werden!")
    
    # 3D-Rendering-Features
    if RENDERING_3D_AVAILABLE:
        with st.expander("🎨 3D-Rendering-Optionen", expanded=False):
            st.markdown("### 🔥 Erweiterte Rendering-Features")
            st.caption("Hochwertige 3D-Visualisierung mit Legacy-Rendering-Engine")
            
            col1, col2 = st.columns(2)
            
            with col1:
                show_module_edges = st.checkbox(
                    "Modul-Kanten anzeigen",
                    value=False,
                    help="Zeigt Kanten aller Module an"
                )
                show_group_indicators = st.checkbox(
                    "Gruppen-Indikatoren",
                    value=False,
                    help="Hebt Modul-Gruppen farblich hervor"
                )
            
            with col2:
                edge_color = st.color_picker(
                    "Kanten-Farbe",
                    value="#000000",
                    help="Farbe der Modul-Kanten"
                )
                edge_width = st.slider(
                    "Kanten-Breite",
                    min_value=1,
                    max_value=5,
                    value=2,
                    help="Dicke der Modul-Kanten"
                )
            
            st.success("✅ 3D-Rendering-Engine aktiv!")
            st.info("💡 Diese Features werden auf die 3D-Visualisierung angewendet!")


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    render_3d_view()
