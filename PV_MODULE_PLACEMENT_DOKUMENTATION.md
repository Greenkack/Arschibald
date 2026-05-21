# PV-Modul Platzierungs-System - Dokumentation

## 🎯 Übersicht

Vollständiges System für **automatische und manuelle PV-Modul-Platzierung** mit umfassenden Transformations- und Bearbeitungsfunktionen.

## ✨ Implementierte Features

### 1. ✅ Modul-Typen

- **Monokristallin (Schwarz)**: Höherer Wirkungsgrad, schwarze Farbe (#1a1a1a)
- **Polykristallin (Blau)**: Günstiger, blaue Farbe (#1e3a8a)
- Wählbar in UI und API

### 2. ✅ Automatische Vollbelegung

- **Algorithmus**: Intelligente Grid-Platzierung basierend auf Dachfläche
- **Parameter**:
  - Maximale Modulanzahl (aus Solarcalculator)
  - Modulabmessungen (Breite, Höhe, Dicke)
  - Orientierung (Landscape/Portrait)
  - Abstand zwischen Modulen (2cm standard)
  - Randabstand (10cm standard)
- **Dachtyp-Unterstützung**:
  - ✅ Flachdach (vollständig implementiert)
  - ⏳ Satteldach (Basis vorhanden)
  - ⏳ Weitere Dachtypen (Vorbereitet)

### 3. ✅ Manuelle Platzierung

- **Einzelmodul hinzufügen**: Position (X, Y, Z) frei wählbar
- **Schnell-Aktionen**:
  - Zufällige Platzierung (5 Module)
  - Alle Module löschen
- **Modul-Konfiguration**:
  - Modultyp wählbar
  - Orientierung wählbar

### 4. ✅ Umfassende Transformationen

Jedes Modul kann vollständig transformiert werden:

#### 📍 Position (Translation)

- X, Y, Z Koordinaten präzise einstellbar
- Schnell-Verschiebung mit konfigurierbarer Schrittweite
- 6 Richtungs-Buttons: X+, X-, Y+, Y-, Z+, Z-

#### 🔄 Rotation (3 Achsen)

- **X-Achse (Neigung)**: Modul-Neigung einstellen
- **Y-Achse**: Seitliche Drehung
- **Z-Achse (Drehung)**: Horizontale Rotation
- Schnell-Rotation mit 5°-45° Schritten
- 6 Rotations-Buttons pro Achse

#### 🎨 Eigenschaften

- **Modultyp ändern**: Mono ↔ Poly
- **Orientierung wechseln**: Landscape ↔ Portrait
- **Name**: Optional benennbar
- **Notizen**: Freitext-Feld für Anmerkungen
- **Lock-Status**: Module können gesperrt werden

### 5. ✅ Gruppenverwaltung

- **Gruppen erstellen**: Aus ausgewählten Modulen
- **Gruppen-Transformationen**: Alle Module gleichzeitig bearbeiten
- **Visueller Indikator**: Bounding Box mit Gruppenfarbe
- **Gruppen sperren**: Schutz vor versehentlichem Verändern

### 6. ✅ Dachflächen-Verwaltung

- **RoofSurface-Klasse**: Verwaltet verfügbare Dachflächen
- **Geometrie**: 3D-Polygon-Vertices
- **Neigung & Ausrichtung**: Tilt und Azimuth-Winkel
- **Modul-Zuordnung**: Tracking welche Module auf welcher Fläche

### 7. ✅ Speichern/Laden

- **JSON-Export**: Vollständiges Layout als JSON
- **JSON-Import**: Layouts wiederherstellen
- **Session State**: Automatische Persistierung während der Session
- **Metadaten**: Alle Transformationen, Gruppen, Eigenschaften

### 8. ✅ 3D-Rendering

- **Plotly Mesh3d**: Hochqualitatives 3D-Rendering
- **Beleuchtung**: Realistic lighting model
- **Kanten**: Schwarze Konturen für bessere Sichtbarkeit
- **Hover-Info**: Detaillierte Modul-Informationen
- **Interaktiv**: Rotation, Zoom, Pan

### 9. ✅ UI-Features

- **Tab-Layout**: 5 Tabs für verschiedene Funktionen
  1. ⚙️ Automatisch - Vollbelegung
  2. 🎨 Manuell - Einzelplatzierung
  3. ✏️ Bearbeiten - Transformationen
  4. 📊 Übersicht - Statistiken
  5. 💾 Speichern/Laden - Persistierung
- **Grid-Helper**: Optionales Hilfs-Grid
- **Transform-Gizmo**: Achsen für ausgewählte Module
- **Live-Statistiken**: In 3D-Szene eingeblendet

### 10. ✅ Statistiken

- **Gesamt-Module**: Anzahl platzierter Module
- **Gesamtleistung**: In kWp
- **Gesamt-Fläche**: In m²
- **Typen-Verteilung**: Mono vs. Poly
- **Gruppen-Anzahl**: Anzahl Gruppen

### 11. ✅ Neues Dachmodell

- **Satteldach mit Gaube**: Vollständig implementiert
  - Hauptdach mit Aussparung
  - Gaube als separates Dach
  - Konfigurierbare Parameter:
    - Gauben-Breite
    - Gauben-Höhe
    - Gauben-Tiefe (Herausragen)
    - Position entlang der Dachfläche

### 12. ✅ PDF-Integration

- **Screenshot-Button**: Unter Gebäudedaten
- **Base64-Konvertierung**: Automatisch für PDF
- **Session State**: Speicherung für PDF-Erstellung
- **Platzhalter**: '3d_visuals' in seite6.yml
- **Position**: (65.158, 670.898, 429.334, 836.805) Punkte

## 📁 Datei-Struktur

```
utils/
├── pv_module_placement_system.py  # ⭐ Kern-System
│   ├── ModuleType (Enum)           # Mono/Poly
│   ├── ModuleOrientation (Enum)    # Landscape/Portrait
│   ├── ModuleDimensions            # Abmessungen
│   ├── ModuleTransform3D           # 3D-Transformation
│   ├── PVModule                    # Einzelnes Modul
│   ├── ModuleGroup                 # Gruppen-Verwaltung
│   ├── RoofSurface                 # Dachflächen
│   └── ModulePlacementManager      # Zentrale Verwaltung
│
├── pv_module_rendering_3d.py      # ⭐ 3D-Rendering
│   ├── render_pv_module_3d()       # Einzelmodul
│   ├── render_module_edges_3d()    # Kanten
│   ├── render_all_modules()        # Alle Module
│   ├── render_module_group_indicator() # Gruppen
│   ├── render_roof_surface_wireframe() # Dachflächen
│   ├── create_grid_helper()        # Hilfs-Grid
│   ├── render_placement_statistics() # Stats in 3D
│   └── create_module_transform_gizmo() # Achsen-Gizmo
│
├── pv_module_placement_ui.py      # ⭐ Streamlit UI
│   ├── init_placement_manager_in_session()
│   └── render_module_placement_ui() # Haupt-UI
│
├── pv3d_plotly.py                 # ⭐ Erweitert
│   ├── create_gabled_roof_with_dormer() # NEU!
│   └── build_plotly_scene()        # Integriert
│
└── pv3d.py                        # Original (unverändert)
```

## 🚀 Verwendung

### Initialisierung

```python
from utils.pv_module_placement_system import (
    ModulePlacementManager,
    ModuleType,
    ModuleOrientation,
    ModuleDimensions
)

# Manager erstellen
manager = ModulePlacementManager()
```

### Automatische Platzierung

```python
# Dachfläche definieren
vertices = [
    (-10, -5, 5),  # Ecken des Daches
    (10, -5, 5),
    (10, 5, 5),
    (-10, 5, 5),
]

surface = manager.add_roof_surface(
    name="Hauptdach",
    roof_type="Flachdach",
    vertices_3d=vertices,
    tilt_deg=15.0,
    azimuth_deg=0.0
)

# Module automatisch platzieren
dimensions = ModuleDimensions(width=1.722, height=1.134, thickness=0.035, power_wp=400)

placed = manager.auto_place_modules_on_surface(
    surface_id=surface.id,
    max_count=50,
    module_type=ModuleType.MONOCRYSTALLINE,
    dimensions=dimensions,
    orientation=ModuleOrientation.LANDSCAPE,
    spacing=0.02,  # 2cm
    margin=0.10    # 10cm
)

print(f"{placed} Module platziert!")
```

### Manuelle Platzierung

```python
# Einzelnes Modul hinzufügen
module = manager.add_module(
    x=0.0, y=0.0, z=5.5,
    module_type=ModuleType.POLYCRYSTALLINE,
    orientation=ModuleOrientation.PORTRAIT
)

# Modul transformieren
module.transform.rotation_x = 15.0  # Neigung
module.transform.rotation_z = 45.0  # Drehung

# Position ändern
manager.translate_module(module.id, dx=1.0, dy=0.5, dz=0.0)

# Rotation
manager.rotate_module(module.id, axis='z', angle_deg=90.0)
```

### Gruppen

```python
# Gruppe erstellen
group = manager.create_group(
    name="Südseite",
    module_ids=[1, 2, 3, 4]
)

# Alle Module der Gruppe auswählen
manager.select_group(group.id)

# Alle ausgewählten transformieren
manager.translate_selected(dx=0.0, dy=0.0, dz=0.5)
manager.rotate_selected(axis='x', angle_deg=5.0)
```

### Speichern/Laden

```python
# Speichern
json_data = manager.to_json()
with open("layout.json", "w") as f:
    f.write(json_data)

# Laden
with open("layout.json", "r") as f:
    json_data = f.read()
    manager = ModulePlacementManager.from_json(json_data)
```

### 3D-Rendering

```python
from utils.pv_module_rendering_3d import render_all_modules
import plotly.graph_objects as go

fig = go.Figure()

# Gebäude und Dach (existing code)
# ...

# Module rendern
module_traces = render_all_modules(manager, show_edges=True)
for trace in module_traces:
    fig.add_trace(trace)

fig.show()
```

### Streamlit Integration

```python
import streamlit as st
from utils.pv_module_placement_ui import render_module_placement_ui

# In Streamlit-App
fig = go.Figure()
# ... Gebäude/Dach hinzufügen ...

# Modul-Platzierungs-UI rendern
render_module_placement_ui(
    fig=fig,
    dims=building_dims,
    roof_type="Satteldach mit Gaube",
    project_data=project_data
)

# Figure anzeigen
st.plotly_chart(fig, use_container_width=True)
```

## 📊 Statistiken

```python
stats = manager.get_statistics()

print(f"Module: {stats['total_modules']}")
print(f"Leistung: {stats['total_power_kwp']:.2f} kWp")
print(f"Fläche: {stats['total_area_m2']:.1f} m²")
print(f"Mono: {stats['monocrystalline_count']}")
print(f"Poly: {stats['polycrystalline_count']}")
```

## 🎨 Farben

- **Monokristallin**: `#1a1a1a` (Dunkel-Schwarz)
- **Polykristallin**: `#1e3a8a` (Dunkel-Blau)
- **Ausgewählt**: 50% heller
- **Gesperrt**: 70% Transparenz
- **Kanten**: Schwarz, 1-2px

## 🔧 Konfiguration

### Standard-Werte

```python
DEFAULT_MODULE_WIDTH = 1.722    # m
DEFAULT_MODULE_HEIGHT = 1.134   # m
DEFAULT_MODULE_THICKNESS = 0.035 # m
DEFAULT_MODULE_POWER = 400      # Wp
DEFAULT_SPACING = 0.02          # m (2cm)
DEFAULT_MARGIN = 0.10           # m (10cm)
```

### Anpassung

```python
# Eigene Dimensionen
custom_dims = ModuleDimensions(
    width=1.8,
    height=1.2,
    thickness=0.04,
    power_wp=450
)

# Eigene Parameter
manager.auto_place_modules_on_surface(
    # ...
    spacing=0.05,  # 5cm Abstand
    margin=0.15    # 15cm Rand
)
```

## ⚠️ Bekannte Einschränkungen

1. **Dachtypen**: Automatische Platzierung aktuell nur für Flachdach vollständig
2. **Kollisionserkennung**: Noch nicht implementiert (Module können sich überschneiden)
3. **Optimierung**: Keine automatische Optimierung nach Verschattung/Ertrag
4. **Performance**: Bei >200 Modulen kann Rendering langsam werden

## 🔮 Geplante Features

- [ ] Automatische Platzierung für alle Dachtypen
- [ ] Kollisionserkennung und -vermeidung
- [ ] Verschattungs-Analyse pro Modul
- [ ] Ertrag-Optimierung basierend auf Position
- [ ] Snap-to-Grid für präzise Platzierung
- [ ] Multi-Surface Unterstützung (mehrere Dachflächen gleichzeitig)
- [ ] Undo/Redo für Transformationen
- [ ] Keyboard-Shortcuts für schnellere Bedienung

## 🐛 Fehlerbehebung

### Import-Fehler

```python
# Wenn "KeyError: 'utils.pv3d_plotly'" auftritt:
import importlib
import sys

if 'utils.pv3d_plotly' in sys.modules:
    importlib.reload(sys.modules['utils.pv3d_plotly'])
```

### Modul nicht sichtbar

- Prüfe Z-Position (muss über Dach sein)
- Prüfe Transparenz (is_locked = False)
- Prüfe Farbe (nicht weiß auf weiß)

### Performance-Probleme

- Reduziere Modulanzahl
- Deaktiviere Grid-Helper
- Deaktiviere Transform-Gizmo
- Reduziere Screenshot-Auflösung

## 📝 Changelog

### Version 1.0.0 (2025-11-02)

- ✅ Vollständiges Platzierungs-System implementiert
- ✅ Mono/Poly Module mit Farben
- ✅ Automatische Vollbelegung (Flachdach)
- ✅ Manuelle Platzierung mit voller Transformations-Kontrolle
- ✅ Gruppenverwaltung
- ✅ Speichern/Laden als JSON
- ✅ 3D-Rendering mit Plotly
- ✅ Umfassende Streamlit UI (5 Tabs)
- ✅ Satteldach mit Gaube Modell
- ✅ PDF-Screenshot-Integration
- ✅ Live-Statistiken in 3D

## 👥 Verwendung im Projekt

Das System ist vollständig in `solar_3d_view_module.py` integriert und wird automatisch geladen, wenn die 3D-Visualisierung geöffnet wird.

### Zugriff in Session State

```python
# Manager aus Session holen
manager = st.session_state.pv_placement_manager

# Alle Module abrufen
modules = manager.get_all_modules()

# Für PDF-Export
screenshot_b64 = st.session_state.pdf_dynamic_data.get("pv_3d_screenshot_b64")
```

## 📚 Weitere Ressourcen

- `utils/pv3d.py` - Original 3D-System (Referenz)
- `utils/pv3d_plotly.py` - Plotly-Rendering
- `coords/seite6.yml` - PDF-Platzhalter Konfiguration
- `pdf_template_engine/dynamic_overlay.py` - PDF-Rendering

---

**Entwickelt für**: Bokuk2 PV-Angebots-System
**Version**: 1.0.0
**Datum**: 2025-11-02
