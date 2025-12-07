"""
Streamlit UI für PV-Modul-Platzierung
======================================

Interaktive UI für manuelle und automatische PV-Modul-Platzierung
mit vollständiger Transformations-Kontrolle.
"""

import streamlit as st
import plotly.graph_objects as go
from typing import Optional, Dict, Any, List
import json
import base64

from utils.pv_module_placement_system import (
    ModulePlacementManager,
    ModuleType,
    ModuleOrientation,
    ModuleDimensions,
    PVModule,
)
from utils.pv_module_rendering_3d import (
    render_all_modules,
    render_module_group_indicator,
    render_roof_surface_wireframe,
    create_grid_helper,
    render_placement_statistics,
    create_module_transform_gizmo,
)


def init_placement_manager_in_session():
    """Initialisiert den ModulePlacementManager in st.session_state"""
    if "pv_placement_manager" not in st.session_state:
        st.session_state.pv_placement_manager = ModulePlacementManager()
    
    if "pv_placement_mode" not in st.session_state:
        st.session_state.pv_placement_mode = "automatic"  # automatic, manual, edit
    
    if "pv_selected_module_id" not in st.session_state:
        st.session_state.pv_selected_module_id = None
    
    if "pv_show_grid" not in st.session_state:
        st.session_state.pv_show_grid = True
    
    if "pv_show_gizmo" not in st.session_state:
        st.session_state.pv_show_gizmo = True


def render_module_placement_ui(fig: go.Figure, 
                               dims: Any,
                               roof_type: str,
                               project_data: Dict[str, Any],
                               module_quantity: Optional[int] = None):
    """
    Rendert die vollständige UI für Modul-Platzierung.
    
    Args:
        fig: Plotly Figure mit Gebäude und Dach
        dims: BuildingDims
        roof_type: Dachtyp
        project_data: Projekt-Daten Dictionary
        module_quantity: Anzahl Module aus Solarcalculator (optional)
    """
    init_placement_manager_in_session()
    manager = st.session_state.pv_placement_manager
    
    st.divider()
    st.subheader("PV-Modul Platzierung")
    
    # ========================================================================
    # TAB-LAYOUT
    # ========================================================================
    tabs = st.tabs([
        " Automatisch",
        "Manuell",
        " Bearbeiten",
        "Übersicht",
        " Speichern/Laden"
    ])
    
    # ========================================================================
    # TAB 1: AUTOMATISCHE PLATZIERUNG
    # ========================================================================
    with tabs[0]:
        st.markdown("### Automatische Vollbelegung")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Modul-Einstellungen**")
            
            # Modulanzahl aus verschiedenen Quellen holen (Priorität: Parameter > project_data)
            if module_quantity is not None and module_quantity > 0:
                default_count = module_quantity
            else:
                default_count = project_data.get("module_quantity", 20)
            
            # Stelle sicher dass default_count mindestens 1 ist
            if default_count <= 0:
                default_count = 20
            
            # Info für User
            st.info(f"Empfohlene Modulanzahl: **{default_count}** Module")
            
            max_modules = st.number_input(
                "Maximale Anzahl Module",
                min_value=1,
                max_value=200,
                value=default_count,
                key="pv_max_modules_input",
                help=f"Passe die Anzahl an oder übernimm den empfohlenen Wert"
            )
            
            # Modultyp auswählen
            module_type_str = st.selectbox(
                "Modultyp",
                options=["Monokristallin (Schwarz)", "Polykristallin (Blau)"],
                help="Monokristallin: höherer Wirkungsgrad, schwarze Farbe\nPolykristallin: günstiger, blaue Farbe"
            )
            module_type = (ModuleType.MONOCRYSTALLINE 
                          if "Mono" in module_type_str 
                          else ModuleType.POLYCRYSTALLINE)
            
            # Modulabmessungen (Standard: 1762×1134×30 mm)
            st.markdown("**Modul-Abmessungen**")
            module_width = st.number_input(
                "Breite (m)",
                min_value=0.5,
                max_value=3.0,
                value=1.762,  # Korrigiert: 1762mm = 1.762m
                step=0.001,
                format="%.3f",
                help="Standard-Modul: 1762 mm"
            )
            module_height = st.number_input(
                "Höhe (m)",
                min_value=0.5,
                max_value=3.0,
                value=1.134,  # Korrekt: 1134mm = 1.134m
                step=0.001,
                format="%.3f",
                help="Standard-Modul: 1134 mm"
            )
            module_thickness = st.number_input(
                "Dicke (m)",
                min_value=0.01,
                max_value=0.1,
                value=0.030,  # Korrigiert: 30mm = 0.030m
                step=0.001,
                format="%.3f",
                help="Standard-Modul: 30 mm"
            )
            module_power = st.number_input(
                "Leistung (Wp)",
                min_value=100,
                max_value=800,
                value=400,
                step=10
            )
        
        with col2:
            st.markdown("**Platzierungs-Parameter**")
            
            orientation = st.selectbox(
                "Orientierung",
                options=["Querformat (Landscape)", "Hochformat (Portrait)"],
                help="Ausrichtung der Module"
            )
            orientation_enum = (ModuleOrientation.LANDSCAPE 
                              if "Quer" in orientation 
                              else ModuleOrientation.PORTRAIT)
            
            # Aufständerungstyp (nur relevant für Flachdach)
            mounting_type = "south"  # Default
            if roof_type == "Flachdach":
                mounting_type = st.radio(
                    "Aufständerungstyp",
                    options=["south", "east_west"],
                    format_func=lambda x: " Süd-Aufständerung (15°)" if x == "south" else " Ost-West-Aufständerung (Dreieck)",
                    help="Süd: Klassische Aufständerung nach Süden. Ost-West: Module abwechselnd nach Osten und Westen für bessere Flächennutzung"
                )
            else:
                st.info(f"Aufständerung nur für Flachdächer verfügbar. Aktuell: **{roof_type}**")
            
            spacing = st.slider(
                "Abstand zwischen Modulen (cm)",
                min_value=0,
                max_value=50,
                value=2,
                help="Abstand für Wartungszwecke"
            ) / 100.0  # Konvertiere zu Metern
            
            margin = st.slider(
                "Randabstand (cm)",
                min_value=5,
                max_value=100,
                value=10,
                help="Abstand zum Dachrand"
            ) / 100.0
            
            # Info-Box
            st.info(
                f"**Modul-Fläche:** {module_width * module_height:.2f} m²\n\n"
                f"**Dach-Fläche:** {dims.length_m * dims.width_m:.2f} m²\n\n"
                f"**Dachtyp:** {roof_type}"
            )
        
        # Platzierungs-Buttons
        col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])
        
        with col_btn1:
            place_button = st.button(
                "Automatisch platzieren",
                type="primary",
                use_container_width=True
            )
        
        with col_btn2:
            # Warnung wenn max_modules = 0
            if max_modules == 0:
                st.error("Anzahl ist 0!")
        
        with col_btn3:
            if st.button(" Alles löschen", use_container_width=True):
                manager.modules.clear()
                manager.next_module_id = 1
                manager.roof_surfaces.clear()
                # WICHTIG: Lösche auch den gecachten Input-Wert
                if "pv_max_modules_input" in st.session_state:
                    del st.session_state["pv_max_modules_input"]
                st.success("Alle Module gelöscht!")
                st.rerun()
        
        # Platzierungs-Funktionalität
        if place_button:
            # Validierung: Prüfe ob max_modules > 0
            if max_modules <= 0:
                st.error("Anzahl Module muss mindestens 1 sein!")
                st.stop()
            
            with st.spinner("Platziere Module..."):
                # Lösche alte Module UND Dachflächen
                manager.modules.clear()
                manager.next_module_id = 1
                manager.roof_surfaces.clear()
                
                # Erstelle Dachfläche NEU
                # Vereinfachte Dachfläche für Flachdach
                if roof_type == "Flachdach":
                    vertices = [
                        (-dims.length_m/2, -dims.width_m/2, dims.wall_height_m),
                        (dims.length_m/2, -dims.width_m/2, dims.wall_height_m),
                        (dims.length_m/2, dims.width_m/2, dims.wall_height_m),
                        (-dims.length_m/2, dims.width_m/2, dims.wall_height_m),
                    ]
                    surface = manager.add_roof_surface(
                        name="Hauptdach",
                        roof_type=roof_type,
                        vertices_3d=vertices,
                        tilt_deg=15.0,
                        azimuth_deg=0.0
                    )
                else:
                    # Für geneigte Dächer: Vereinfachte Annahme
                    vertices = [
                        (-dims.length_m/2, -dims.width_m/2, dims.wall_height_m),
                        (dims.length_m/2, -dims.width_m/2, dims.wall_height_m),
                        (dims.length_m/2, dims.width_m/2, dims.wall_height_m + 2),
                        (-dims.length_m/2, dims.width_m/2, dims.wall_height_m + 2),
                    ]
                    surface = manager.add_roof_surface(
                        name="Hauptdach",
                        roof_type=roof_type,
                        vertices_3d=vertices,
                        tilt_deg=project_data.get("roof_inclination_deg", 35.0),
                        azimuth_deg=0.0
                    )
                
                # Debug: Zeige Dachflächen-Info
                st.write(f"DEBUG: Dachfläche erstellt")
                st.write(f"  - Typ: {roof_type}")
                st.write(f"  - Vertices: {len(vertices)}")
                st.write(f"  - Surface ID: {surface.id}")
                st.write(f"  - Gebäude: {dims.length_m}m × {dims.width_m}m × {dims.wall_height_m}m")
                
                # Erstelle Modul-Dimensionen
                dimensions = ModuleDimensions(
                    width=module_width,
                    height=module_height,
                    thickness=module_thickness,
                    power_wp=module_power
                )
                
                st.write(f"DEBUG: Starte Platzierung...")
                st.write(f"  - Surface ID: {surface.id}")
                st.write(f"  - Max Module: {max_modules}")
                st.write(f"  - Modul-Typ: {module_type}")
                st.write(f"  - Dimensionen: {module_width}x{module_height}m")
                st.write(f"  - Orientierung: {orientation_enum}")
                st.write(f"  - Aufständerung: {mounting_type}")
                
                # Automatische Platzierung
                placed_count = manager.auto_place_modules_on_surface(
                    surface_id=surface.id,
                    max_count=max_modules,
                    module_type=module_type,
                    dimensions=dimensions,
                    orientation=orientation_enum,
                    spacing=spacing,
                    margin=margin,
                    mounting_type=mounting_type
                )
                
                st.write(f"DEBUG: Platzierung abgeschlossen - {placed_count} Module")
                st.write(f"DEBUG: Manager.modules enthält jetzt {len(manager.modules)} Module")
                
                st.success(f"{placed_count} Module erfolgreich platziert!")
                
                # DEBUG: Zeige Modul-Info
                if len(manager.modules) > 0:
                    st.write(f"**DEBUG:** Manager hat jetzt {len(manager.modules)} Module:")
                    for mid, mod in list(manager.modules.items())[:3]:  # Zeige erste 3
                        st.write(f"  - Modul {mid}: Position ({mod.transform.x:.2f}, {mod.transform.y:.2f}, {mod.transform.z:.2f})")
                    
                    # WICHTIG: Rerun auslösen damit die Module in der ERSTEN Figure erscheinen
                    st.info(" Seite wird neu geladen um Module anzuzeigen...")
                    st.rerun()
                else:
                    st.warning("Keine Module platziert - prüfe Dachfläche und Parameter")
                    import traceback
                    st.code(traceback.format_exc())
    
    # ========================================================================
    # TAB 2: MANUELLE PLATZIERUNG
    # ========================================================================
    with tabs[1]:
        st.markdown("### Manuelle Modul-Platzierung")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("**Neues Modul hinzufügen**")
            
            # Position
            pos_col1, pos_col2, pos_col3 = st.columns(3)
            with pos_col1:
                new_x = st.number_input("X-Position (m)", value=0.0, step=0.1, format="%.2f", key="new_x")
            with pos_col2:
                new_y = st.number_input("Y-Position (m)", value=0.0, step=0.1, format="%.2f", key="new_y")
            with pos_col3:
                new_z = st.number_input("Z-Position (m)", value=dims.wall_height_m + 0.5, step=0.1, format="%.2f", key="new_z")
            
            # Modultyp und Orientierung
            new_type_col, new_ori_col = st.columns(2)
            with new_type_col:
                new_module_type_str = st.selectbox(
                    "Typ",
                    options=["Monokristallin", "Polykristallin"],
                    key="new_type"
                )
                new_module_type = (ModuleType.MONOCRYSTALLINE 
                                  if "Mono" in new_module_type_str 
                                  else ModuleType.POLYCRYSTALLINE)
            
            with new_ori_col:
                new_orientation_str = st.selectbox(
                    "Orientierung",
                    options=["Landscape", "Portrait"],
                    key="new_ori"
                )
                new_orientation = (ModuleOrientation.LANDSCAPE 
                                  if "Landscape" in new_orientation_str 
                                  else ModuleOrientation.PORTRAIT)
            
            if st.button(" Modul hinzufügen", use_container_width=True):
                module = manager.add_module(
                    x=new_x, y=new_y, z=new_z,
                    module_type=new_module_type,
                    orientation=new_orientation
                )
                st.success(f"Modul {module.id} hinzugefügt!")
                if "trigger_3d_update" not in st.session_state:
                    st.session_state.trigger_3d_update = 0
                st.session_state.trigger_3d_update += 1
                st.rerun()
        
        with col2:
            st.markdown("**Schnell-Aktionen**")
            
            if st.button(" Zufällig platzieren", use_container_width=True):
                import random
                for _ in range(5):
                    x = random.uniform(-dims.length_m/3, dims.length_m/3)
                    y = random.uniform(-dims.width_m/3, dims.width_m/3)
                    z = dims.wall_height_m + 0.5
                    manager.add_module(x=x, y=y, z=z)
                st.success("5 Module zufällig platziert!")
                if "trigger_3d_update" not in st.session_state:
                    st.session_state.trigger_3d_update = 0
                st.session_state.trigger_3d_update += 1
                st.rerun()
            
            if st.button("Alle löschen", use_container_width=True):
                manager.modules.clear()
                st.success("Alle Module gelöscht!")
                if "trigger_3d_update" not in st.session_state:
                    st.session_state.trigger_3d_update = 0
                st.session_state.trigger_3d_update += 1
                st.rerun()
    
    # ========================================================================
    # TAB 3: BEARBEITEN
    # ========================================================================
    with tabs[2]:
        st.markdown("### Modul bearbeiten")
        
        if not manager.modules:
            st.info("Keine Module vorhanden. Erstelle zuerst Module in den anderen Tabs.")
        else:
            # Modul auswählen
            module_ids = list(manager.modules.keys())
            selected_id = st.selectbox(
                "Modul auswählen",
                options=module_ids,
                format_func=lambda x: f"Modul {x} - {manager.modules[x].module_type.display_name}"
            )
            
            if selected_id:
                module = manager.modules[selected_id]
                
                # Bearbeitungs-Tabs
                edit_tabs = st.tabs([" Position", " Rotation", "Eigenschaften", "Löschen"])
                
                # Position
                with edit_tabs[0]:
                    st.markdown("**Position (Verschieben)**")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        edit_x = st.number_input("X", value=module.transform.x, step=0.1, format="%.2f", key=f"edit_x_{selected_id}")
                    with col2:
                        edit_y = st.number_input("Y", value=module.transform.y, step=0.1, format="%.2f", key=f"edit_y_{selected_id}")
                    with col3:
                        edit_z = st.number_input("Z", value=module.transform.z, step=0.1, format="%.2f", key=f"edit_z_{selected_id}")
                    
                    if st.button(" Position speichern", key="save_pos"):
                        module.transform.x = edit_x
                        module.transform.y = edit_y
                        module.transform.z = edit_z
                        st.success("Position aktualisiert!")
                        st.rerun()
                    
                    st.divider()
                    st.markdown("**Schnell-Verschiebung**")
                    move_col1, move_col2, move_col3 = st.columns(3)
                    with move_col1:
                        move_step = st.number_input("Schrittweite (m)", value=0.5, step=0.1, key="move_step")
                    with move_col2:
                        if st.button(" X-", key="move_x_neg"):
                            module.transform.x -= move_step
                            st.rerun()
                        if st.button(" X+", key="move_x_pos"):
                            module.transform.x += move_step
                            st.rerun()
                    with move_col3:
                        if st.button(" Y-", key="move_y_neg"):
                            module.transform.y -= move_step
                            st.rerun()
                        if st.button(" Y+", key="move_y_pos"):
                            module.transform.y += move_step
                            st.rerun()
                
                # Rotation
                with edit_tabs[1]:
                    st.markdown("**Rotation**")
                    
                    rot_col1, rot_col2, rot_col3 = st.columns(3)
                    with rot_col1:
                        edit_rot_x = st.number_input("X-Achse (Neigung)", value=module.transform.rotation_x, step=5.0, format="%.1f", key=f"rot_x_{selected_id}")
                    with rot_col2:
                        edit_rot_y = st.number_input("Y-Achse", value=module.transform.rotation_y, step=5.0, format="%.1f", key=f"rot_y_{selected_id}")
                    with rot_col3:
                        edit_rot_z = st.number_input("Z-Achse (Drehung)", value=module.transform.rotation_z, step=5.0, format="%.1f", key=f"rot_z_{selected_id}")
                    
                    if st.button(" Rotation speichern", key="save_rot"):
                        module.transform.rotation_x = edit_rot_x
                        module.transform.rotation_y = edit_rot_y
                        module.transform.rotation_z = edit_rot_z
                        st.success("Rotation aktualisiert!")
                        st.rerun()
                    
                    st.divider()
                    st.markdown("**Schnell-Rotation**")
                    rot_step = st.slider("Rotations-Schritt (°)", 5, 45, 15, key="rot_step")
                    
                    rot_quick_col1, rot_quick_col2, rot_quick_col3 = st.columns(3)
                    with rot_quick_col1:
                        if st.button(f"↻ X +{rot_step}°", key="rot_x_plus"):
                            module.transform.rotation_x += rot_step
                            st.rerun()
                        if st.button(f"↺ X -{rot_step}°", key="rot_x_minus"):
                            module.transform.rotation_x -= rot_step
                            st.rerun()
                    with rot_quick_col2:
                        if st.button(f"↻ Y +{rot_step}°", key="rot_y_plus"):
                            module.transform.rotation_y += rot_step
                            st.rerun()
                        if st.button(f"↺ Y -{rot_step}°", key="rot_y_minus"):
                            module.transform.rotation_y -= rot_step
                            st.rerun()
                    with rot_quick_col3:
                        if st.button(f"↻ Z +{rot_step}°", key="rot_z_plus"):
                            module.transform.rotation_z += rot_step
                            st.rerun()
                        if st.button(f"↺ Z -{rot_step}°", key="rot_z_minus"):
                            module.transform.rotation_z -= rot_step
                            st.rerun()
                
                # Eigenschaften
                with edit_tabs[2]:
                    st.markdown("**Modul-Eigenschaften**")
                    
                    # Typ ändern
                    new_type = st.selectbox(
                        "Modultyp ändern",
                        options=["Monokristallin (Schwarz)", "Polykristallin (Blau)"],
                        index=0 if module.module_type == ModuleType.MONOCRYSTALLINE else 1,
                        key=f"change_type_{selected_id}"
                    )
                    
                    # Orientierung wechseln
                    current_ori = "Landscape" if module.orientation == ModuleOrientation.LANDSCAPE else "Portrait"
                    new_ori = st.selectbox(
                        "Orientierung",
                        options=["Landscape", "Portrait"],
                        index=0 if current_ori == "Landscape" else 1,
                        key=f"change_ori_{selected_id}"
                    )
                    
                    # Name
                    new_name = st.text_input(
                        "Name (optional)",
                        value=module.name or "",
                        key=f"change_name_{selected_id}"
                    )
                    
                    # Notizen
                    new_notes = st.text_area(
                        "Notizen",
                        value=module.notes,
                        key=f"change_notes_{selected_id}"
                    )
                    
                    if st.button(" Eigenschaften speichern", key="save_props"):
                        module.module_type = (ModuleType.MONOCRYSTALLINE 
                                            if "Mono" in new_type 
                                            else ModuleType.POLYCRYSTALLINE)
                        module.orientation = (ModuleOrientation.LANDSCAPE 
                                            if "Landscape" in new_ori 
                                            else ModuleOrientation.PORTRAIT)
                        module.name = new_name if new_name else None
                        module.notes = new_notes
                        st.success("Eigenschaften aktualisiert!")
                        st.rerun()
                
                # Löschen
                with edit_tabs[3]:
                    st.warning(f"Modul {selected_id} löschen?")
                    st.markdown("Diese Aktion kann nicht rückgängig gemacht werden.")
                    
                    if st.button("Modul endgültig löschen", type="primary", key="delete_module"):
                        manager.remove_module(selected_id)
                        st.success(f"Modul {selected_id} gelöscht!")
                        st.rerun()
    
    # ========================================================================
    # TAB 4: ÜBERSICHT
    # ========================================================================
    with tabs[3]:
        st.markdown("### Anlagenübersicht")
        
        stats = manager.get_statistics()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Gesamt-Module", stats["total_modules"])
        with col2:
            st.metric("Gesamtleistung", f"{stats['total_power_kwp']:.2f} kWp")
        with col3:
            st.metric("Gesamt-Fläche", f"{stats['total_area_m2']:.1f} m²")
        with col4:
            st.metric("Gruppen", stats["groups_count"])
        
        st.divider()
        
        # Modul-Typen
        st.markdown("**Modul-Verteilung**")
        mono_col, poly_col = st.columns(2)
        with mono_col:
            st.info(f" **Monokristallin:** {stats['monocrystalline_count']} Module")
        with poly_col:
            st.info(f" **Polykristallin:** {stats['polycrystalline_count']} Module")
        
        # Modul-Liste (ohne Expanders wegen verschachtelter Expander-Beschränkung)
        if manager.modules:
            st.divider()
            st.markdown("**Alle Module**")
            
            # Zeige Module in kompakter Liste statt Expanders
            for i, module in enumerate(manager.get_all_modules()):
                with st.container():
                    # Header mit Hintergrundfarbe
                    st.markdown(f"**Modul {module.id}** - {module.module_type.display_name}")
                    
                    # Details in Spalten
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.caption(f" Position: ({module.transform.x:.2f}, {module.transform.y:.2f}, {module.transform.z:.2f})")
                    with col2:
                        st.caption(f" Rotation: X={module.transform.rotation_x:.1f}°, Y={module.transform.rotation_y:.1f}°, Z={module.transform.rotation_z:.1f}°")
                    with col3:
                        st.caption(f"Leistung: {module.dimensions.power_wp:.0f} Wp")
                    
                    if module.name or module.notes:
                        extra_col1, extra_col2 = st.columns(2)
                        if module.name:
                            with extra_col1:
                                st.caption(f" Name: {module.name}")
                        if module.notes:
                            with extra_col2:
                                st.caption(f"Notizen: {module.notes}")
                    
                    if i < len(manager.modules) - 1:
                        st.divider()
    
    # ========================================================================
    # TAB 5: SPEICHERN/LADEN
    # ========================================================================
    with tabs[4]:
        st.markdown("### Layout speichern/laden")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("** Layout speichern**")
            
            layout_name = st.text_input("Layout-Name", value="Mein Layout", key="save_layout_name")
            
            if st.button(" Als JSON exportieren", use_container_width=True):
                json_data = manager.to_json()
                st.download_button(
                    label=" JSON herunterladen",
                    data=json_data,
                    file_name=f"pv_layout_{layout_name.replace(' ', '_')}.json",
                    mime="application/json",
                    use_container_width=True
                )
                st.success("Export bereit!")
        
        with col2:
            st.markdown("** Layout laden**")
            
            uploaded_file = st.file_uploader(
                "JSON-Datei hochladen",
                type=["json"],
                key="load_layout_file"
            )
            
            if uploaded_file is not None:
                try:
                    json_str = uploaded_file.read().decode("utf-8")
                    loaded_manager = ModulePlacementManager.from_json(json_str)
                    
                    if st.button("Layout übernehmen", type="primary", use_container_width=True):
                        st.session_state.pv_placement_manager = loaded_manager
                        st.success("Layout erfolgreich geladen!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Fehler beim Laden: {e}")
    
    # ========================================================================
    # RENDERING DER MODULE IN DER 3D-SZENE
    # ========================================================================
    
    # Render alle Module
    module_traces = render_all_modules(manager, show_edges=True, show_selection=True)
    for trace in module_traces:
        fig.add_trace(trace)
    
    # Render Gruppen-Indikatoren
    for group_id in manager.groups:
        group_indicator = render_module_group_indicator(manager, group_id)
        if group_indicator:
            fig.add_trace(group_indicator)
    
    # Grid Helper (optional)
    if st.session_state.pv_show_grid and manager.modules:
        grid_traces = create_grid_helper(
            center=(0, 0, dims.wall_height_m),
            size=max(dims.length_m, dims.width_m),
            spacing=1.0
        )
        for trace in grid_traces:
            fig.add_trace(trace)
    
    # Statistik-Anzeige in 3D (optional)
    if manager.modules:
        stats_trace = render_placement_statistics(
            manager,
            position = (dims.length_m/2 + 2, 0, dims.wall_height_m + 2)
        )
        fig.add_trace(stats_trace)
    
    # Transform-Gizmo für ausgewähltes Modul
    if st.session_state.pv_show_gizmo:
        selected_modules = manager.get_selected_modules()
        for module in selected_modules:
            gizmo_traces = create_module_transform_gizmo(module, size=0.8)
            for trace in gizmo_traces:
                fig.add_trace(trace)
    
    # Optionen-Sidebar
    with st.sidebar:
        st.divider()
        st.markdown("### Ansichts-Optionen")
        
        st.session_state.pv_show_grid = st.checkbox(
            "Grid anzeigen",
            value=st.session_state.pv_show_grid,
            help="Zeigt Hilfs-Grid für Platzierung"
        )
        
        st.session_state.pv_show_gizmo = st.checkbox(
            "Transform-Gizmo anzeigen",
            value=st.session_state.pv_show_gizmo,
            help="Zeigt Achsen für ausgewählte Module"
        )
