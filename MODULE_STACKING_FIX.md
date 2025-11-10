# Modul-Stapelung Fix

## Problem

Alle Module werden an einer Stelle übereinander gestapelt, anstatt auf der Dachfläche verteilt zu werden.

## Diagnose

Die Grid-Berechnung funktioniert korrekt:
- ✅ 20 unterschiedliche Positionen werden berechnet
- ✅ X-Koordinaten variieren von -4.95m bis +4.95m (Spanne: 9.90m)
- ✅ Y-Koordinaten variieren von -0.91m bis +0.90m (Spanne: 1.81m)
- ✅ Z-Koordinaten sind alle gleich (0.050m für Satteldach)

## Mögliche Ursachen

1. **Session State nicht initialisiert**: Beim ersten Laden sind keine Positionen im Session State
2. **Automatische Platzierung wird nicht ausgeführt**: Der "Automatisch belegen" Button muss manuell geklickt werden
3. **Positionen werden nicht korrekt aus Session State gelesen**: Beim Rendering werden falsche Positionen verwendet

## Lösung

Die Module sollten automatisch platziert werden, wenn:
1. Die Seite zum ersten Mal geladen wird
2. Der Benutzer die Modulanzahl ändert
3. Der Benutzer die Dachform ändert

Aktuell müssen Benutzer manuell auf "Automatisch belegen" klicken.

## Empfohlene Fixes

### Option 1: Automatische Platzierung beim ersten Laden
Füge automatische Platzierung hinzu, wenn Session State leer ist:

```python
# In solar_3d_view_module.py nach Session State Initialisierung
if not st.session_state.get("placed_module_positions"):
    # Automatisch platzieren beim ersten Laden
    result = handle_auto_placement(
        roof_length=building_length,
        roof_width=building_width,
        module_quantity=module_quantity,
        roof_type=roof_type,
        roof_pitch=roof_pitch
    )
```

### Option 2: Fallback-Rendering
Wenn keine Positionen im Session State sind, verwende Grid-Berechnung als Fallback:

```python
# In utils/pv3d_plotly.py build_plotly_scene()
placed_positions = st.session_state.get("placed_module_positions", [])

if not placed_positions:
    # Fallback: Berechne Positionen on-the-fly
    from utils.pv3d_grid_calculator import calculate_module_grid
    grid_2d = calculate_module_grid(dims.length_m, dims.width_m, module_quantity)
    z_pos = calculate_z_position(roof_type)
    placed_positions = [(x, y, z_pos) for x, y in grid_2d]
```

### Option 3: Bessere UI-Hinweise
Zeige deutlichen Hinweis, dass Benutzer auf "Automatisch belegen" klicken müssen:

```python
if not st.session_state.get("placed_module_positions"):
    st.warning("⚠️ Keine Module platziert! Klicken Sie auf 'Automatisch belegen' um Module zu platzieren.")
```

## Nächste Schritte

1. Implementiere Option 1 (Automatische Platzierung beim ersten Laden)
2. Füge Option 3 hinzu als zusätzlichen Hinweis
3. Teste mit verschiedenen Dachformen und Modulanzahlen
