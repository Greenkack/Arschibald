"""
3D PV-Visualisierung UI-Seite

Diese Seite bietet eine interaktive 3D-Visualisierung der PV-Anlage
auf dem Gebäude mit automatischer und manueller Modul-Platzierung.
"""

import streamlit as st
from typing import Dict, Any, List, Tuple
import io

# Imports für 3D-Visualisierung
try:
    from utils.pv3d import (
        BuildingDims,
        LayoutConfig,
        build_scene,
        render_image_bytes,
        export_stl,
        export_gltf,
        _safe_get_orientation,
        _safe_get_roof_inclination_deg,
        _safe_get_roof_covering
    )
    from stpyvista import stpyvista
    PV3D_AVAILABLE = True
except ImportError:
    PV3D_AVAILABLE = False


def render_3d_view():
    """Hauptfunktion zum Rendern der 3D-Visualisierung - wird von gui.py aufgerufen"""
    _render_3d_view_impl()


def _render_3d_view_impl():

    """Interne Implementierung der 3D-Visualisierung"""
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
    # SIDEBAR - EINSTELLUNGEN
    # ============================================================================

    st.sidebar.header("⚙️ Einstellungen")

    # Gebäudedimensionen
    st.sidebar.subheader("Gebäudedimensionen")

    # Standardwerte basierend auf Gebäudeart
    default_dims = {
    "Einfamilienhaus": (10.0, 6.0, 6.0),
    "Mehrfamilienhaus": (15.0, 10.0, 9.0),
    "Wohnblock": (25.0, 15.0, 12.0)
    }
    default_length, default_width, default_height = default_dims.get(
    building_type, (10.0, 6.0, 6.0)
    )

    building_length = st.sidebar.number_input(
    "Gebäudelänge (m)",
    min_value=8.0,
    max_value=60.0,
    value=default_length,
    step=0.5,
    help="Länge des Gebäudes in Metern"
    )

    building_width = st.sidebar.number_input(
    "Gebäudebreite (m)",
    min_value=5.0,
    max_value=40.0,
    value=default_width,
    step=0.5,
    help="Breite des Gebäudes in Metern"
    )

    building_height = st.sidebar.number_input(
    "Traufhöhe (m)",
    min_value=3.0,
    max_value=20.0,
    value=default_height,
    step=0.5,
    help="Höhe der Außenwände (Traufhöhe)"
    )

    st.sidebar.divider()

    # Dachform
    st.sidebar.subheader("Dachform")

    roof_types = [
    "Flachdach",
    "Satteldach",
    "Walmdach",
    "Krüppelwalmdach",
    "Pultdach",
    "Zeltdach",
    "Sonstiges"
    ]

    selected_roof_type = st.sidebar.selectbox(
    "Dachform",
    options=roof_types,
    index=roof_types.index(roof_type) if roof_type in roof_types else 0,
    help="Wählen Sie die Dachform Ihres Gebäudes"
    )

    st.sidebar.divider()

    # Belegungsmodus
    st.sidebar.subheader("PV-Modul-Belegung")

    layout_mode = st.sidebar.radio(
    "Belegungsmodus",
    options=["Automatisch", "Manuell"],
    index=0,
    help="Automatisch: Module werden gleichmäßig verteilt. Manuell: Sie können einzelne Module entfernen."
    )

    # Flachdach-Aufständerung (nur bei Flachdach)
    mounting_type = "Süd"
    if selected_roof_type == "Flachdach":
    mounting_type = st.sidebar.selectbox(
        "Aufständerung",
        options=["Süd", "Ost-West"],
        index=0,
        help="Süd: 15° Neigung nach Süden. Ost-West: 10° Neigung alternierend."
    )

    st.sidebar.divider()

    # Platzmangel-Fallbacks
    st.sidebar.subheader("Zusätzliche Flächen")

    use_garage = st.sidebar.checkbox(
    "Garage/Carport automatisch hinzufügen",
    value=False,
    help="Fügt eine Garage hinzu, wenn Module nicht auf dem Hauptdach passen"
    )

    use_facade = st.sidebar.checkbox(
    "Fassadenbelegung aktivieren",
    value=False,
    help="Platziert Module an der Südfassade, wenn Dach und Garage nicht ausreichen"
    )

    st.sidebar.divider()

    # Manuelle Indizes-Eingabe (nur im manuellen Modus)
    removed_indices = []
    if layout_mode == "Manuell":
    st.sidebar.subheader("Manuelle Anpassung")
    
    indices_input = st.sidebar.text_area(
        "Zu entfernende Module (Indizes)",
        value="",
        height=100,
        help="Geben Sie die Indizes der zu entfernenden Module ein (komma-separiert, 0-basiert). Beispiel: 0,1,5,10"
    )
    
    # Parse Indizes
    if indices_input.strip():
        try:
            removed_indices = [
                int(idx.strip())
                for idx in indices_input.split(",")
                if idx.strip()
            ]
            st.sidebar.success(f"✓ {len(removed_indices)} Module werden entfernt")
        except ValueError:
            st.sidebar.error("❌ Ungültige Eingabe. Bitte nur Zahlen und Kommas verwenden.")
            removed_indices = []

    st.sidebar.divider()


    # ============================================================================
    # SIDEBAR - AKTIONS-BUTTONS
    # ============================================================================

    st.sidebar.subheader("Aktionen")

    # Button: Visualisierung aktualisieren
    btn_update = st.sidebar.button(
    "🔄 Visualisierung aktualisieren",
    type="primary",
    use_container_width=True,
    help="Erstellt die 3D-Visualisierung mit den aktuellen Einstellungen"
    )

    # Button: Reset
    btn_reset = st.sidebar.button(
    "↺ Reset (Auto-Belegung)",
    use_container_width=True,
    help="Setzt alle Einstellungen zurück auf automatische Belegung"
    )

    # Button: Layout speichern
    btn_save = st.sidebar.button(
    "💾 Layout speichern",
    use_container_width=True,
    help="Speichert die aktuelle Konfiguration im Session State"
    )

    # Button: Layout laden
    btn_load = st.sidebar.button(
    "📂 Layout laden",
    use_container_width=True,
    help="Lädt die gespeicherte Konfiguration aus dem Session State"
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

    if "_pv3d_plotter" not in st.session_state:
    st.session_state["_pv3d_plotter"] = None


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
    st.session_state["_pv3d_plotter"] = None
    st.sidebar.success("✓ Einstellungen zurückgesetzt")
    st.rerun()


    # Button-Logik: Layout speichern
    if btn_save:
    # Erstelle aktuelle Konfiguration
    current_config = LayoutConfig(
        mode="auto" if layout_mode == "Automatisch" else "manual",
        use_garage=use_garage,
        use_facade=use_facade,
        removed_indices=removed_indices,
        garage_dims=(6.0, 3.0, 3.0),  # Standardwerte
        offset_main_xy=(0.0, 0.0),
        offset_garage_xy=(0.0, 0.0)
    )
    
    # Speichere in Session State
    st.session_state["pv3d_layout_json"] = current_config.to_json()
    st.sidebar.success("✓ Layout gespeichert")


    # Button-Logik: Layout laden
    if btn_load:
    try:
        # Lade Konfiguration aus Session State
        loaded_config = LayoutConfig.from_json(
            st.session_state["pv3d_layout_json"]
        )
        st.sidebar.success("✓ Layout geladen")
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
    should_render = btn_update or not st.session_state["pv3d_last_rendered"]

    if should_render:
    try:
        # Erstelle BuildingDims aus Eingabefeldern
        dims = BuildingDims(
            length_m=building_length,
            width_m=building_width,
            wall_height_m=building_height
        )
        
        # Erstelle LayoutConfig aus Sidebar-Werten
        layout_config = LayoutConfig(
            mode="auto" if layout_mode == "Automatisch" else "manual",
            use_garage=use_garage,
            use_facade=use_facade,
            removed_indices=removed_indices,
            garage_dims=(6.0, 3.0, 3.0),
            offset_main_xy=(0.0, 0.0),
            offset_garage_xy=(0.0, 0.0)
        )
        
        # Zeige Fortschrittsanzeige
        with st.spinner("🔄 Erstelle 3D-Visualisierung..."):
            # Rufe build_scene() auf
            plotter, panels = build_scene(
                project_data=project_data,
                dims=dims,
                roof_type=selected_roof_type,
                module_quantity=module_quantity,
                layout_config=layout_config,
                mounting_type=mounting_type
            )
            
            # Speichere Plotter in Session State
            st.session_state["_pv3d_plotter"] = plotter
            st.session_state["_pv3d_panels"] = panels
            st.session_state["pv3d_last_rendered"] = True
            
        st.success("✓ 3D-Visualisierung erfolgreich erstellt")
        
    except Exception as e:
        st.error(f"❌ Fehler beim Erstellen der 3D-Visualisierung: {e}")
        st.info("Bitte überprüfen Sie Ihre Eingaben und versuchen Sie es erneut.")
        st.session_state["_pv3d_plotter"] = None
        st.session_state["pv3d_last_rendered"] = False



    # ============================================================================
    # HAUPTBEREICH - 2-SPALTEN-LAYOUT
    # ============================================================================

    # Erstelle Spalten mit Verhältnis 3:2 (60%:40%)
    col_viewer, col_status = st.columns([3, 2])

    # Linke Spalte: 3D-Viewer
    with col_viewer:
    st.subheader("🎨 3D-Ansicht")
    
    # Prüfe ob Plotter vorhanden
    plotter = st.session_state.get("_pv3d_plotter")
    
    if plotter is not None:
        try:
            # Zeige 3D-Viewer mit stpyvista
            stpyvista(
                plotter,
                key="pv3d_viewer",
                panel_kwargs={
                    "orientation_widget": True,
                    "interactive": True
                }
            )
        except Exception as e:
            st.error(f"❌ Fehler beim Anzeigen des 3D-Viewers: {e}")
            st.info("Bitte aktualisieren Sie die Visualisierung.")
    else:
        # Fehler-Fallback
        st.info("👆 Klicken Sie auf 'Visualisierung aktualisieren' in der Sidebar, um die 3D-Ansicht zu erstellen.")
        st.image(
            "https://via.placeholder.com/800x500/f0f0f0/666666?text=3D+Visualisierung+wird+geladen...",
            use_container_width=True
        )

    # Rechte Spalte: Status-Metriken
    with col_status:
    st.subheader("📊 Status")

    
    # Berechne geschätzte Dachkapazität
    # Vereinfachte Schätzung: Dachfläche / Modulfläche * 0.7 (Effizienzfaktor)
    roof_area = building_length * building_width
    module_area = 1.05 * 1.76  # PV_W * PV_H
    estimated_capacity = int((roof_area / module_area) * 0.7)
    
    # Berechne platzierte Module
    panels = st.session_state.get("_pv3d_panels", {})
    main_panels = len(panels.get("main", []))
    garage_panels = len(panels.get("garage", []))
    facade_panels = len(panels.get("facade", []))
    total_placed = main_panels + garage_panels + facade_panels
    
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
        delta=f"{main_panels} Dach, {garage_panels} Garage, {facade_panels} Fassade",
        help="Anzahl der tatsächlich platzierten Module"
    )
    
    st.metric(
        label="Fehlende Module",
        value=missing_modules,
        delta=f"-{missing_modules}" if missing_modules > 0 else "Alle platziert",
        delta_color="inverse",
        help="Anzahl der Module, die nicht platziert werden konnten"
    )
    
    st.metric(
        label="Geschätzte Dachkapazität",
        value=estimated_capacity,
        help="Geschätzte maximale Anzahl Module auf dem Hauptdach"
    )
    
    st.divider()
    
    # Zeige Warnung oder Erfolg
    if missing_modules > 0:
        st.warning(
            f"⚠️ {missing_modules} Module konnten nicht platziert werden.\n\n"
            "**Tipp:** Aktivieren Sie 'Garage/Carport' oder 'Fassadenbelegung' "
            "in der Sidebar, um zusätzliche Flächen zu nutzen."
        )
    else:
        st.success(
            "✅ Alle Module wurden erfolgreich platziert!"
        )
    
    # Zusätzliche Informationen
    st.info(
        f"**Gebäudedaten:**\n"
        f"- Dachform: {selected_roof_type}\n"
        f"- Ausrichtung: {orientation}\n"
        f"- Dachneigung: {roof_inclination_deg}°\n"
        f"- Dachdeckung: {roof_covering}"
    )



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
                
                layout_config = LayoutConfig(
                    mode="auto" if layout_mode == "Automatisch" else "manual",
                    use_garage=use_garage,
                    use_facade=use_facade,
                    removed_indices=removed_indices,
                    garage_dims=(6.0, 3.0, 3.0),
                    offset_main_xy=(0.0, 0.0),
                    offset_garage_xy=(0.0, 0.0)
                )
                
                # Rufe render_image_bytes() auf
                png_bytes = render_image_bytes(
                    project_data=project_data,
                    dims=dims,
                    roof_type=selected_roof_type,
                    module_quantity=module_quantity,
                    layout_config=layout_config,
                    mounting_type=mounting_type
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
                
                layout_config = LayoutConfig(
                    mode="auto" if layout_mode == "Automatisch" else "manual",
                    use_garage=use_garage,
                    use_facade=use_facade,
                    removed_indices=removed_indices,
                    garage_dims=(6.0, 3.0, 3.0),
                    offset_main_xy=(0.0, 0.0),
                    offset_garage_xy=(0.0, 0.0)
                )
                
                # Rufe export_stl() auf
                stl_bytes = export_stl(
                    project_data=project_data,
                    dims=dims,
                    roof_type=selected_roof_type,
                    module_quantity=module_quantity,
                    layout_config=layout_config,
                    mounting_type=mounting_type
                )
                
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
                
                layout_config = LayoutConfig(
                    mode="auto" if layout_mode == "Automatisch" else "manual",
                    use_garage=use_garage,
                    use_facade=use_facade,
                    removed_indices=removed_indices,
                    garage_dims=(6.0, 3.0, 3.0),
                    offset_main_xy=(0.0, 0.0),
                    offset_garage_xy=(0.0, 0.0)
                )
                
                # Rufe export_gltf() auf
                gltf_bytes = export_gltf(
                    project_data=project_data,
                    dims=dims,
                    roof_type=selected_roof_type,
                    module_quantity=module_quantity,
                    layout_config=layout_config,
                    mounting_type=mounting_type
                )
                
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
    st.caption("🏠 3D PV-Visualisierung | Powered by PyVista & stpyvista")


# When run as standalone page
if __name__ == "__main__":
    render_3d_view()
