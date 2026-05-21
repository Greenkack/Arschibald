# 3D-Visualisierung Fix - Modul-Belegung & Fehlende Funktionen

## Probleme identifiziert:

1. **Module werden NICHT auf Dach gerendert**
   - `pv_placement_manager` wird nie initialisiert
   - Fallback-Grid-Logik wird übersprungen
   - Module erscheinen nicht in 3D-Ansicht

2. **Buttons für Modul-Belegung fehlen**
   - UI-Komponenten werden nicht vollständig gerendert
   - `render_advanced_controls()` fehlt Modul-Auswahl-Buttons
   - Keine interaktive Modul-Selektion möglich

3. **Fehlende Funktionen**
   - Keine Modul-Auswahl via Click
   - Keine Modul-Manipulation (Verschieben, Drehen)
   - Keine Gruppen-Operationen

## Root Cause Analysis:

### Problem 1: ModulePlacementManager nie initialisiert

**Datei:** `utils/pv3d_plotly.py` Zeile 1186-1203

```python
# AKTUELL (FEHLERHAFT):
try:
    import streamlit as st
    if hasattr(st, 'session_state') and 'pv_placement_manager' in st.session_state:
        manager = st.session_state.pv_placement_manager
        
        if len(manager.modules) > 0:
            # Rendere Module
            ...
        else:
            # Fallback Grid (wird nie erreicht wenn Manager leer!)
            ...
    else:
        # Fallback Grid (wird nie erreicht wenn Manager nicht existiert!)
        ...
```

**Problem:** 
- `pv_placement_manager` wird nirgendwo erstellt!
- Ohne Manager: Fallback-Grid wird NICHT aufgerufen
- Resultat: KEINE Module werden gerendert!

### Problem 2: UI-Komponenten unvollständig

**Datei:** `utils/pv3d_ui_components.py` Zeile 318-400

```python
# render_advanced_controls() hat:
# - Auswahl-Modus Radio
# - Einzelauswahl per Index
# - ABER: Keine Buttons zum Ausw<br/>ählen/Abwählen sichtbar!
# - ABER: Keine Gruppe-Auswahl UI!
# - ABER: Keine Bereich-Auswahl UI!
```

**Problem:**
- Buttons werden in Bedingung `if selection_mode == "Einzeln"` erstellt
- Aber columns `col_select, col_deselect` werden erstellt aber nicht genutzt!
- Buttons existieren im Code aber werden nicht gerendert!

### Problem 3: Keine Initialisierung

**Datei:** `solar_3d_view_module.py`

```python
# ModulePlacementManager wird NIE erstellt!
# Session State 'pv_placement_manager' wird NIE initialisiert!
```

## Fix-Strategie:

### Fix 1: ModulePlacementManager initialisieren

**In:** `solar_3d_view_module.py` nach Zeile 310

```python
def _initialize_placement_manager(
    module_quantity: int,
    dims: BuildingDims,
    roof_type: str,
    module_base_z: float,
    default_tilt: float
) -> None:
    """Initialisiert ModulePlacementManager mit Grid-Positionen"""
    from utils.pv_module_placement_system import ModulePlacementManager, PVModule, ModuleType
    
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
```

### Fix 2: Buttons sichtbar machen

**In:** `utils/pv3d_ui_components.py` Zeile 350-380

```python
# Nach col_select, col_deselect = st.columns(2)

with col_select:
    if st.button("➕ Auswählen", key="select_single_module", use_container_width=True):
        if single_index not in selected_modules:
            selected_modules.append(single_index)
            st.session_state.pv3d_selected_modules = selected_modules
            st.success(f"✓ Modul {single_index} ausgewählt")
            st.rerun()

with col_deselect:
    if st.button("➖ Abwählen", key="deselect_single_module", use_container_width=True):
        if single_index in selected_modules:
            selected_modules.remove(single_index)
            st.session_state.pv3d_selected_modules = selected_modules
            st.success(f"✓ Modul {single_index} abgewählt")
            st.rerun()
```

### Fix 3: Gruppe & Bereich UI hinzufügen

**In:** `utils/pv3d_ui_components.py` nach Zeile 380

```python
elif selection_mode == "Gruppe":
    st.caption("Geben Sie Modul-Indizes kommagetrennt ein:")
    
    group_input = st.text_input(
        "Modul-Indizes (z.B. 0,1,2,5,10)",
        value="",
        help="Kommagetrennte Liste von Modul-Indizes",
        key="group_selection_input"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("➕ Gruppe auswählen", key="select_group", use_container_width=True):
            try:
                indices = [int(i.strip()) for i in group_input.split(",") if i.strip()]
                for idx in indices:
                    if idx not in selected_modules and 0 <= idx < max_modules:
                        selected_modules.append(idx)
                st.session_state.pv3d_selected_modules = selected_modules
                st.success(f"✓ {len(indices)} Module ausgewählt")
                st.rerun()
            except ValueError:
                st.error("❌ Ungültige Eingabe!")
    
    with col2:
        if st.button("➖ Gruppe abwählen", key="deselect_group", use_container_width=True):
            try:
                indices = [int(i.strip()) for i in group_input.split(",") if i.strip()]
                for idx in indices:
                    if idx in selected_modules:
                        selected_modules.remove(idx)
                st.session_state.pv3d_selected_modules = selected_modules
                st.success(f"✓ {len(indices)} Module abgewählt")
                st.rerun()
            except ValueError:
                st.error("❌ Ungültige Eingabe!")

elif selection_mode == "Bereich":
    st.caption("Definieren Sie einen rechteckigen Bereich:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        start_index = st.number_input(
            "Start-Index",
            min_value=0,
            max_value=max(0, max_modules - 1),
            value=0,
            step=1,
            key="range_start"
        )
    
    with col2:
        end_index = st.number_input(
            "End-Index",
            min_value=0,
            max_value=max(0, max_modules - 1),
            value=min(9, max_modules - 1),
            step=1,
            key="range_end"
        )
    
    col_sel, col_desel = st.columns(2)
    
    with col_sel:
        if st.button("➕ Bereich auswählen", key="select_range", use_container_width=True):
            for idx in range(start_index, end_index + 1):
                if idx not in selected_modules and idx < max_modules:
                    selected_modules.append(idx)
            st.session_state.pv3d_selected_modules = selected_modules
            st.success(f"✓ {end_index - start_index + 1} Module ausgewählt")
            st.rerun()
    
    with col_desel:
        if st.button("➖ Bereich abwählen", key="deselect_range", use_container_width=True):
            for idx in range(start_index, end_index + 1):
                if idx in selected_modules:
                    selected_modules.remove(idx)
            st.session_state.pv3d_selected_modules = selected_modules
            st.success(f"✓ {end_index - start_index + 1} Module abgewählt")
            st.rerun()
```

### Fix 4: Integration in solar_3d_view_module.py

**Änderung in:** `_render_3d_view_impl()` nach Zeile 400

```python
# Nach: dims = create_building_dims(basis_settings)
# Vor: layout_config = create_layout_config(...)

# INITIALISIERE PLACEMENT MANAGER
_initialize_placement_manager(
    module_quantity=module_quantity,
    dims=dims,
    roof_type=basis_settings.get("roof_type", roof_type),
    module_base_z=module_base_z,  # Berechnet nach Dach-Erstellung
    default_tilt=default_tilt      # Abhängig von Dachform
)
```

## Implementierungs-Reihenfolge:

1. **solar_3d_view_module.py** - Füge `_initialize_placement_manager()` hinzu
2. **solar_3d_view_module.py** - Rufe Funktion vor `build_plotly_scene()` auf  
3. **pv3d_ui_components.py** - Fixe Buttons in `render_advanced_controls()`
4. **pv3d_ui_components.py** - Füge Gruppe & Bereich UI hinzu
5. **pv3d_plotly.py** - Entferne redundanten Fallback-Code (wird nie erreicht)

## Erwartetes Ergebnis:

✅ Module werden auf Dach gerendert
✅ Buttons für Einzel-Auswahl sichtbar  
✅ Gruppe-Auswahl funktioniert
✅ Bereich-Auswahl funktioniert
✅ Ausgewählte Module werden hervorgehoben
✅ 3D-Visualisierung komplett funktional

## Test-Plan:

1. App starten → 3D-Ansicht öffnen
2. Module sollten auf Dach erscheinen ✓
3. Sidebar → "Erweiterte Kontrolle" öffnen ✓
4. Auswahl-Modus: "Einzeln" → Buttons sichtbar ✓
5. Modul 0 auswählen → Orange hervorgehoben ✓
6. Auswahl-Modus: "Gruppe" → 0,1,2 eingeben → Buttons funktionieren ✓
7. Auswahl-Modus: "Bereich" → Start 5, End 10 → Buttons funktionieren ✓

---

**Status:** BEREIT FÜR IMPLEMENTIERUNG  
**Priorität:** 🔴 KRITISCH - Kernnfunktion defekt  
**Geschätzte Zeit:** 30-45 Min  
