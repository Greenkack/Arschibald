# Task 7.1: Modul-Hervorhebung - Quick Reference

## Schnellstart

### Normales Modul
```python
mesh, vertices = create_pv_module_3d_with_highlight(
    x=0.0, y=0.0, z=1.0
)
fig.add_trace(mesh)
```

### Ausgewähltes Modul (mit leuchtenden Kanten)
```python
result, vertices = create_pv_module_3d_with_highlight(
    x=0.0, y=0.0, z=1.0,
    selected=True
)
mesh, edges = result
fig.add_trace(mesh)
fig.add_trace(edges)
```

### Hover-Effekt
```python
mesh, vertices = create_pv_module_3d_with_highlight(
    x=0.0, y=0.0, z=1.0,
    hover=True
)
fig.add_trace(mesh)
```

## API

### create_pv_module_3d_with_highlight()

**Parameter:**
- `x, y, z` - Position (float)
- `selected` - Ausgewählt? (bool, default: False)
- `hover` - Hover-Effekt? (bool, default: False)
- `azimuth_deg` - Azimuth (float, default: 0)
- `tilt_deg` - Neigung (float, default: 15)
- `color` - Farbe (str, default: "#1a1a2e")

**Returns:**
- Wenn `selected=True`: `([mesh, edges], vertices)`
- Sonst: `(mesh, vertices)`

### create_module_edges_with_glow()

**Parameter:**
- `vertices` - 8x3 NumPy Array
- `color` - Farbe (str, default: "#4a90e2")
- `width` - Linienbreite (int, default: 4)
- `glow_intensity` - Opacity (float, default: 0.9)

**Returns:** `go.Scatter3d` Objekt

## Farben

| Zustand | Hex-Code |
|---------|----------|
| Normal | #1a1a2e |
| Selected (Kanten) | #4a90e2 |
| Invalid | #e74c3c |

## Tests

```bash
python test_task7_1_standalone.py
```

**Ergebnis:** 6/6 Tests bestanden ✅

## Dateien

- `utils/pv3d_plotly.py` - Implementation
- `test_task7_1_standalone.py` - Tests
- `PHASE_2_TASK_7_1_COMPLETE.md` - Vollständige Dokumentation
