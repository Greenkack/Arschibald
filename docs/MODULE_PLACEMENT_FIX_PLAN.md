# Modul-Belegung - Sofort-Fix Plan

## Diagnose der Hauptprobleme

Nach Analyse der Code-Basis wurden folgende kritische Probleme identifiziert:

### Problem 1: Module werden nicht zur Szene hinzugefügt
**Ursache**: In `build_plotly_scene()` fehlt möglicherweise der Code zum Hinzufügen der Module
**Fix**: Stelle sicher dass `create_pv_module_3d()` aufgerufen wird und Meshes zur `fig.data` hinzugefügt werden

### Problem 2: Keine Buttons für Modul-Belegung
**Ursache**: UI-Komponenten haben keine Action-Buttons
**Fix**: Füge Buttons in `utils/pv3d_ui_components.py` hinzu

### Problem 3: Grid-Berechnung funktioniert nicht
**Ursache**: `calculate_grid_positions()` gibt möglicherweise leere oder falsche Positionen zurück
**Fix**: Implementiere robuste Grid-Berechnung neu

## Sofort-Maßnahmen (Nächste 30 Minuten)

### Fix 1: Modul-Belegungs-Panel mit Buttons erstellen

Datei: `utils/pv3d_module_placement_ui.py` (NEU)

```python
import streamlit as st
from typing import Dict, Any, List, Tuple

def render_module_placement_panel(
    module_quantity: int,
    roof_area: float,
    current_placed: int = 0
) -> Dict[str, Any]:
    """
    Rendert Modul-Belegungs-Panel mit allen Buttons.
    
    Returns:
        Dictionary mit:
        - auto_place_clicked: bool
        - manual_add_clicked: bool
        - remove_selected_clicked: bool
        - reset_all_clicked: bool
        - show_grid: bool
    """
    with st.sidebar.expander("🔲 Modul-Belegung", expanded=True):
        st.markdown("### Modul-Platzierung")
        
        # Statistiken
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Gewünscht", module_quantity)
        
        with col2:
            st.metric("Platziert", current_placed)
        
        with col3:
            coverage = (current_placed / module_quantity * 100) if module_quantity > 0 else 0
            st.metric("Abdeckung", f"{coverage:.0f}%")
        
        # Fortschrittsbalken
        progress = min(1.0, current_placed / module_quantity) if module_quantity > 0 else 0
        st.progress(progress)
        
        st.divider()
        
        # Automatische Belegung
        st.markdown("**🎯 Automatische Belegung**")
        auto_place_clicked = st.button(
            "Automatisch belegen",
            key="btn_auto_place_modules",
            use_container_width=True,
            type="primary",
            help="Platziert Module automatisch optimal auf der Dachfläche"
        )
        
        if auto_place_clicked:
            st.session_state["trigger_auto_placement"] = True
            st.info("🔄 Module werden automatisch platziert...")
            st.rerun()
        
        st.divider()
        
        # Manuelle Belegung
        st.markdown("**✋ Manuelle Belegung**")
        
        col_add, col_remove = st.columns(2)
        
        with col_add:
            manual_add_clicked = st.button(
                "➕ Hinzufügen",
                key="btn_manual_add_module",
                use_container_width=True,
                help="Fügt ein Modul an ausgewählter Position hinzu"
            )
        
        with col_remove:
            remove_selected_clicked = st.button(
                "➖ Entfernen",
                key="btn_remove_selected_modules",
                use_container_width=True,
                help="Entfernt ausgewählte Module"
            )
        
        reset_all_clicked = st.button(
            "🔄 Alle zurücksetzen",
            key="btn_reset_all_modules",
            use_container_width=True,
            help="Entfernt alle platzierten Module"
        )
        
        st.divider()
        
        # Hilfsoptionen
        st.markdown("**⚙️ Optionen**")
        
        show_grid = st.checkbox(
            "Raster anzeigen",
            value=True,
            key="show_placement_grid",
            help="Zeigt Platzierungs-Raster zur Orientierung"
        )
        
        show_numbers = st.checkbox(
            "Modul-Nummern anzeigen",
            value=False,
            key="show_module_numbers",
            help="Zeigt Nummer auf jedem Modul"
        )
    
    return {
        "auto_place_clicked": auto_place_clicked,
        "manual_add_clicked": manual_add_clicked,
        "remove_selected_clicked": remove_selected_clicked,
        "reset_all_clicked": reset_all_clicked,
        "show_grid": show_grid,
        "show_numbers": show_numbers
    }
```

### Fix 2: Robuste Grid-Berechnung

Datei: `utils/pv3d_grid_calculator.py` (NEU)

```python
import numpy as np
from typing import List, Tuple

# Modul-Dimensionen (aus pv3d.py)
PV_W = 1.05  # Breite in Metern
PV_H = 1.76  # Höhe in Metern

def calculate_module_grid(
    roof_length: float,
    roof_width: float,
    module_quantity: int,
    spacing: float = 0.05,
    margin: float = 0.3
) -> List[Tuple[float, float]]:
    """
    Berechnet optimale Grid-Positionen für Module.
    
    Args:
        roof_length: Länge des Dachs in Metern
        roof_width: Breite des Dachs in Metern
        module_quantity: Gewünschte Anzahl Module
        spacing: Abstand zwischen Modulen in Metern
        margin: Randabstand in Metern
    
    Returns:
        Liste von (x, y) Positionen
    """
    positions = []
    
    # Verfügbare Fläche nach Abzug der Ränder
    available_length = roof_length - 2 * margin
    available_width = roof_width - 2 * margin
    
    # Berechne wie viele Module in jede Richtung passen
    modules_per_row = int(available_length / (PV_W + spacing))
    modules_per_col = int(available_width / (PV_H + spacing))
    
    # Maximale Anzahl Module die passen
    max_modules = modules_per_row * modules_per_col
    
    # Begrenze auf gewünschte Anzahl
    target_modules = min(module_quantity, max_modules)
    
    # Berechne tatsächliche Anzahl Reihen und Spalten
    if target_modules <= modules_per_row:
        # Alle Module in eine Reihe
        actual_rows = 1
        actual_cols = target_modules
    else:
        # Mehrere Reihen
        actual_rows = int(np.ceil(target_modules / modules_per_row))
        actual_cols = modules_per_row
    
    # Startposition (zentriert)
    start_x = -roof_length / 2 + margin + PV_W / 2
    start_y = -roof_width / 2 + margin + PV_H / 2
    
    # Generiere Positionen
    placed = 0
    for row in range(actual_rows):
        for col in range(actual_cols):
            if placed >= target_modules:
                break
            
            x = start_x + col * (PV_W + spacing)
            y = start_y + row * (PV_H + spacing)
            
            positions.append((x, y))
            placed += 1
        
        if placed >= target_modules:
            break
    
    return positions
```

### Fix 3: Modul-Platzierungs-Handler

Datei: `utils/pv3d_placement_handler.py` (NEU)

```python
import streamlit as st
from typing import Dict, Any, List, Tuple
from utils.pv3d_grid_calculator import calculate_module_grid

def handle_auto_placement(
    roof_length: float,
    roof_width: float,
    module_quantity: int,
    roof_type: str
) -> Dict[str, Any]:
    """
    Führt automatische Modul-Platzierung durch.
    
    Returns:
        Dictionary mit:
        - success: bool
        - positions: List[Tuple[float, float, float]]
        - count: int
        - message: str
    """
    try:
        # Berechne Grid-Positionen
        grid_positions = calculate_module_grid(
            roof_length=roof_length,
            roof_width=roof_width,
            module_quantity=module_quantity
        )
        
        # Konvertiere zu 3D-Positionen (füge Z hinzu)
        # Z-Position hängt vom Dachtyp ab
        if roof_type == "Flachdach":
            base_z = 0.3  # Aufständerung
        else:
            base_z = 0.05  # Direkt auf Dach
        
        positions_3d = [(x, y, base_z) for x, y in grid_positions]
        
        # Speichere in Session State
        st.session_state["placed_module_positions"] = positions_3d
        st.session_state["placed_module_count"] = len(positions_3d)
        
        return {
            "success": True,
            "positions": positions_3d,
            "count": len(positions_3d),
            "message": f"✅ {len(positions_3d)} Module erfolgreich platziert!"
        }
    
    except Exception as e:
        return {
            "success": False,
            "positions": [],
            "count": 0,
            "message": f"❌ Fehler: {e}"
        }


def handle_reset_placement() -> Dict[str, Any]:
    """Setzt alle platzierten Module zurück."""
    st.session_state["placed_module_positions"] = []
    st.session_state["placed_module_count"] = 0
    
    return {
        "success": True,
        "message": "🔄 Alle Module wurden entfernt"
    }
```

## Integration in solar_3d_view_module.py

```python
# Nach render_export_options() hinzufügen:

# NEU: Modul-Belegungs-Panel
try:
    from utils.pv3d_module_placement_ui import render_module_placement_panel
    from utils.pv3d_placement_handler import handle_auto_placement, handle_reset_placement
    
    # Berechne Dachfläche
    roof_area = dims.length_m * dims.width_m
    current_placed = st.session_state.get("placed_module_count", 0)
    
    # Rendere Panel
    placement_actions = render_module_placement_panel(
        module_quantity=module_quantity,
        roof_area=roof_area,
        current_placed=current_placed
    )
    
    # Handle Auto-Placement Trigger
    if st.session_state.get("trigger_auto_placement", False):
        st.session_state["trigger_auto_placement"] = False
        
        result = handle_auto_placement(
            roof_length=dims.length_m,
            roof_width=dims.width_m,
            module_quantity=module_quantity,
            roof_type=roof_type
        )
        
        if result["success"]:
            st.success(result["message"])
        else:
            st.error(result["message"])
    
    # Handle Reset
    if placement_actions.get("reset_all_clicked"):
        result = handle_reset_placement()
        st.info(result["message"])
        st.rerun()

except ImportError:
    st.sidebar.warning("⚠️ Modul-Belegungs-Panel nicht verfügbar")
```

## Nächste Schritte

1. ✅ Erstelle die 3 neuen Dateien
2. ✅ Integriere in solar_3d_view_module.py
3. ✅ Teste automatische Belegung
4. ✅ Füge Module zur 3D-Szene hinzu
5. ✅ Teste Sichtbarkeit

## Erwartetes Ergebnis

- ✅ Sidebar zeigt "🔲 Modul-Belegung" Panel
- ✅ Button "Automatisch belegen" ist sichtbar
- ✅ Klick auf Button platziert Module
- ✅ Module sind in 3D-Ansicht sichtbar
- ✅ Statistiken zeigen korrekte Anzahl
