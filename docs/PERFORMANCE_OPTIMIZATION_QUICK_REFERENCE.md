# Performance-Optimierung - Quick Reference

## Übersicht

Dieses Dokument beschreibt die Performance-Optimierungen für die 3D-Modul-Visualisierung.

---

## Lazy Loading (LOD)

### Wann verwenden?

- Bei mehr als 50 Modulen
- Wenn Performance-Probleme auftreten
- Für schnellere Vorschau-Darstellung

### Wie verwenden?

```python
from utils.pv3d_performance import should_render_module

# In Rendering-Loop
for i, (x, y, z) in enumerate(module_positions):
    if should_render_module(i, len(module_positions), lod_threshold=50):
        mesh = create_pv_module_3d(x, y, z)
        traces.append(mesh)
```

### Parameter

- `module_index`: Index des Moduls (0-basiert)
- `total_modules`: Gesamtanzahl Module
- `lod_threshold`: Schwellwert (Standard: 50)
- `enable_lod`: LOD aktivieren (Standard: True)

### Verhalten

| Modulanzahl | LOD aktiv? | Gerendert | Reduktion |
|-------------|------------|-----------|-----------|
| ≤ 50        | Nein       | Alle      | 0%        |
| 100         | Ja         | 50        | 50%       |
| 200         | Ja         | 50        | 75%       |

---

## Batch-Rendering

### Wann verwenden?

- Bei vielen Modulen (>20)
- Für bessere Memory-Verwaltung
- Automatische LOD-Anwendung

### Wie verwenden?

```python
from utils.pv3d_performance import batch_render_modules

meshes = batch_render_modules(
    module_positions,           # Liste von (x, y, z) Tupeln
    create_pv_module_3d,        # Render-Funktion
    batch_size=20,              # Module pro Batch
    enable_lod=True,            # LOD aktivieren
    lod_threshold=50,           # LOD-Schwellwert
    # Zusätzliche Argumente für Render-Funktion:
    azimuth_deg=0,
    tilt_deg=30,
    color="#1a1a2e"
)
```

### Vorteile

- Reduziert Memory-Spikes
- Automatische LOD-Anwendung
- Error-Handling pro Modul
- Einfache Integration

---

## Caching

### 1. Mesh-Geometrie

```python
from utils.pv3d_performance import cache_module_mesh_geometry

# Wird automatisch gecacht (TTL: 5 Minuten)
geom = cache_module_mesh_geometry()

# Verwende gecachte Geometrie
vertices = geom['vertices']  # 8 Ecken
faces_i = geom['faces_i']    # Dreiecks-Indizes
```

### 2. Rotationsmatrizen

```python
from utils.pv3d_performance import get_cached_rotation_matrix

# Wird automatisch gecacht
R = get_cached_rotation_matrix(azimuth_deg=0, tilt_deg=30)

# Transformiere Vertices
transformed = (R @ vertices.T).T
```

### 3. Positionen

```python
from utils.pv3d_performance import calculate_module_positions_cached

# Wird automatisch gecacht (TTL: 1 Minute)
positions = calculate_module_positions_cached(
    length=10.0,
    width=8.0,
    count=50,
    spacing_x=0.25,
    spacing_y=0.25
)
```

---

## Cache-Management

### Statistiken abrufen

```python
from utils.pv3d_performance import get_all_cache_stats

stats = get_all_cache_stats()
print(f"Global Cache: {stats['global_cache']['size']} Einträge")
print(f"Transformation Cache: {stats['transformation_cache']['size']} Einträge")
```

### Cache leeren

```python
from utils.pv3d_performance import clear_all_caches

# Leert alle Caches
clear_all_caches()
```

### Wann Cache leeren?

- Nach Änderungen an Gebäude-Dimensionen
- Bei Speicher-Problemen
- Beim Debugging

---

## LOD-Informationen

### Abrufen

```python
from utils.pv3d_performance import get_lod_info

info = get_lod_info(total_modules=100, lod_threshold=50)
```

### Rückgabe

```python
{
    'enabled': True,              # LOD aktiv?
    'skip_factor': 2,             # Jeden N-ten rendern
    'rendered_count': 50,         # Anzahl gerendert
    'skipped_count': 50,          # Anzahl übersprungen
    'reduction_percent': 50.0     # Prozentuale Reduktion
}
```

### UI-Anzeige

```python
if info['enabled']:
    st.info(f"🎯 LOD aktiv: {info['rendered_count']} von {total_modules} Modulen gerendert ({info['reduction_percent']:.0f}% Reduktion)")
```

---

## Performance-Monitoring

### Decorator verwenden

```python
from utils.pv3d_performance import monitor_performance

@monitor_performance("module_rendering")
def render_all_modules():
    # ... Rendering-Code ...
    pass
```

### Statistiken abrufen

```python
from utils.pv3d_performance import get_performance_stats

stats = get_performance_stats()
for operation, timing in stats.items():
    print(f"{operation}: {timing['avg']*1000:.2f}ms (avg)")
```

---

## Best Practices

### 1. Immer LOD verwenden bei >50 Modulen

```python
# ✅ Gut
if should_render_module(i, total, lod_threshold=50):
    render_module()

# ❌ Schlecht
render_module()  # Rendert immer alle
```

### 2. Batch-Rendering für viele Module

```python
# ✅ Gut
meshes = batch_render_modules(positions, render_func, batch_size=20)

# ❌ Schlecht
meshes = [render_func(*pos) for pos in positions]  # Memory-Spike
```

### 3. Gecachte Funktionen verwenden

```python
# ✅ Gut
geom = cache_module_mesh_geometry()  # Gecacht
R = get_cached_rotation_matrix(0, 30)  # Gecacht

# ❌ Schlecht
# Geometrie jedes Mal neu berechnen
```

### 4. Cache-Statistiken monitoren

```python
# ✅ Gut
stats = get_all_cache_stats()
if stats['global_cache']['size'] > 80:
    clear_all_caches()  # Speicher freigeben
```

---

## Troubleshooting

### Problem: Module werden nicht gerendert

**Lösung**: LOD deaktivieren für Debugging

```python
meshes = batch_render_modules(
    positions, 
    render_func,
    enable_lod=False  # Alle Module rendern
)
```

### Problem: Zu viele Module übersprungen

**Lösung**: LOD-Threshold erhöhen

```python
meshes = batch_render_modules(
    positions, 
    render_func,
    lod_threshold=100  # Mehr Module rendern
)
```

### Problem: Cache zu groß

**Lösung**: Cache leeren oder TTL reduzieren

```python
clear_all_caches()
```

### Problem: Performance immer noch schlecht

**Lösung**: Batch-Größe reduzieren

```python
meshes = batch_render_modules(
    positions, 
    render_func,
    batch_size=10  # Kleinere Batches
)
```

---

## Beispiel: Vollständige Integration

```python
from utils.pv3d_performance import (
    batch_render_modules,
    get_lod_info,
    get_all_cache_stats
)

def render_pv_modules(positions, roof_type, roof_pitch):
    """Rendert PV-Module mit Performance-Optimierungen"""
    
    # LOD-Info für UI
    lod_info = get_lod_info(len(positions), lod_threshold=50)
    if lod_info['enabled']:
        st.info(f"🎯 LOD aktiv: {lod_info['rendered_count']} von {len(positions)} Modulen")
    
    # Batch-Rendering mit LOD
    meshes = batch_render_modules(
        positions,
        create_pv_module_3d,
        batch_size=20,
        enable_lod=True,
        lod_threshold=50,
        # Render-Parameter
        roof_type=roof_type,
        azimuth_deg=0,
        tilt_deg=roof_pitch if roof_type != "Flachdach" else 30
    )
    
    # Cache-Statistiken (optional)
    if st.checkbox("Zeige Cache-Statistiken"):
        stats = get_all_cache_stats()
        st.json(stats)
    
    return meshes
```

---

## Weitere Informationen

- Vollständige Dokumentation: `TASK_9_PERFORMANCE_OPTIMIZATION_COMPLETE.md`
- Tests: `test_task9_performance_optimization.py`
- Implementierung: `utils/pv3d_performance.py`
