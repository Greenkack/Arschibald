# Design Document: 3D PV-Visualisierung

## Overview

Das 3D-Visualisierungstool ist ein vollständig integriertes Modul für die Streamlit-App "Arschibald", das eine realistische, interaktive Darstellung von Gebäuden mit PV-Modulbelegung ermöglicht. Das System nutzt PyVista/VTK für 3D-Rendering und stpyvista für die Streamlit-Integration.

### Hauptziele

1. **Dynamische Modellgenerierung**: Automatische Erstellung von 3D-Gebäudemodellen basierend auf Benutzereingaben
2. **Interaktive PV-Planung**: Automatische und manuelle Platzierung von PV-Modulen
3. **Nahtlose Integration**: Vollständige Anbindung an bestehende App-Daten (project_data, analysis_results)
4. **PDF-Export**: Automatische Einbettung von 3D-Screenshots in PDF-Angebote
5. **Performance**: Flüssiges Rendering ohne Beeinträchtigung der restlichen App

### Technologie-Stack

- **3D-Rendering**: PyVista (>= 0.43.10) mit VTK (>= 9.3.0)
- **Streamlit-Integration**: stpyvista (>= 0.1.4)
- **Geometrie-Verarbeitung**: NumPy (>= 1.26), trimesh (>= 4.4.9)
- **PDF-Integration**: ReportLab (>= 4.2.2), pikepdf (>= 9.0.0)
- **Bildverarbeitung**: Pillow (für PNG-Konvertierung)

## Architecture

### Modulstruktur

```
streamlit_app/
├── utils/
│   ├── pv3d.py                    # Kern-3D-Engine
│   └── pdf_visual_inject.py       # PDF-Integration
└── pages/
    └── solar_3d_view.py           # UI-Seite

pdf_template_engine/
└── (Integration in bestehende PDF-Pipeline)
```

### Datenfluss

```
Benutzer-Eingabe (Bedarfsanalyse/Solarkalkulator)
    ↓
st.session_state.project_data
st.session_state.analysis_results
    ↓
pv3d.build_scene() → PyVista Plotter
    ↓
stpyvista() → Interaktiver 3D-Viewer (Browser)
    ↓
pv3d.render_image_bytes() → PNG-Bytes
    ↓
pdf_visual_inject.make_pv3d_image_flowable() → ReportLab Image
    ↓
PDF-Generator → Finales PDF-Angebot
```

## Components and Interfaces

### 1. Core 3D Engine (pv3d.py)

#### Datenklassen

```python
@dataclass
class BuildingDims:
    """Gebäudedimensionen"""
    length_m: float = 10.0
    width_m: float = 6.0
    wall_height_m: float = 6.0

@dataclass
class LayoutConfig:
    """PV-Layout-Konfiguration"""
    mode: str = "auto"  # "auto" | "manual"
    use_garage: bool = False
    use_facade: bool = False
    removed_indices: List[int] = None
    garage_dims: Tuple[float, float, float] = (6.0, 3.0, 3.0)
    offset_main_xy: Tuple[float, float] = (0.0, 0.0)
    offset_garage_xy: Tuple[float, float] = (0.0, 0.0)
```


#### Hauptfunktionen

**build_scene()**
- **Zweck**: Erstellt die komplette 3D-Szene mit Gebäude, Dach und PV-Modulen
- **Input**: project_data, BuildingDims, roof_type, LayoutConfig, module_quantity
- **Output**: (PyVista Plotter, Dict mit Panel-Listen)
- **Logik**:
  1. Erstellt PyVista Plotter mit weißem Hintergrund
  2. Generiert Bodenplatte (3x Gebäudegröße, 0.05m dick)
  3. Erstellt Gebäudewände als Quader
  4. Generiert Dach basierend auf roof_type
  5. Rotiert Szene basierend auf Ausrichtung
  6. Platziert Kompass-Pfeil
  7. Berechnet und platziert PV-Module
  8. Fügt optional Garage und Fassadenmodule hinzu

**Dachgeometrie-Funktionen**
- `make_roof_flat()`: Flachdach als dünner Quader (0.12m)
- `make_roof_gable()`: Satteldach mit zwei geneigten Flächen
- `make_roof_hip()`: Walmdach mit vier geneigten Flächen
- `make_roof_pent()`: Pultdach als gekippte Platte
- `make_roof_pyramid()`: Zeltdach mit zentralem Gipfel

**PV-Modul-Funktionen**
- `make_panel()`: Erstellt einzelnes PV-Modul (1.05×1.76×0.04m)
- `grid_positions()`: Berechnet Rasterposit ionen für Module
- Unterstützt Rotation (yaw, tilt) für Aufständerung

**Export-Funktionen**
- `render_image_bytes()`: Off-Screen Screenshot als PNG-Bytes
- `export_stl()`: 3D-Modell als STL-Datei
- `export_gltf()`: 3D-Modell als glTF/glb-Datei

#### Hilfsfunktionen

**Datenextraktion (robust mit Fallbacks)**
- `_safe_get_orientation()`: Liest Ausrichtung aus project_data
- `_safe_get_roof_inclination_deg()`: Liest Dachneigung
- `_safe_get_roof_covering()`: Liest Dachdeckung
- `_roof_color_from_covering()`: Mappt Deckung zu Farbe

**Geometrie-Primitives**
- `make_box()`: Erstellt Quader mit Origin-Kontrolle
- `_deg_to_rad()`: Grad zu Radiant Konvertierung

### 2. UI-Seite (solar_3d_view.py)

#### Seitenstruktur

```
Streamlit Page: "3D PV-Visualisierung"
├── Sidebar (Einstellungen)
│   ├── Gebäudedimensionen (Länge, Breite, Höhe)
│   ├── Dachform-Auswahl
│   ├── Belegungsmodus (Auto/Manuell)
│   ├── Flachdach-Aufständerung
│   ├── Platzmangel-Fallback (Garage, Fassade)
│   ├── Manuelle Indizes-Eingabe
│   └── Aktionen (Aktualisieren, Reset, Speichern, Laden)
├── Hauptbereich (2 Spalten)
│   ├── Linke Spalte (60%): 3D-Viewer
│   └── Rechte Spalte (40%): Status & Export
│       ├── Metriken (Gewählt, Platziert, Fehlend)
│       ├── Warnungen/Erfolg
│       └── Export-Buttons (Screenshot, STL, glTF)
└── Expandable: Datenquellen-Info
```

#### Session State Management

```python
# Initialisierung
if "pv3d_layout_json" not in st.session_state:
    st.session_state["pv3d_layout_json"] = LayoutConfig().to_json()

if "pv3d_last_rendered" not in st.session_state:
    st.session_state["pv3d_last_rendered"] = False

if "_pv3d_plotter" not in st.session_state:
    st.session_state["_pv3d_plotter"] = None
```

#### Interaktionslogik

1. **Initialisierung**: Liest project_data und analysis_results
2. **Eingabe-Verarbeitung**: Sammelt Dimensionen, Dachform, Modus
3. **Rendering-Trigger**: Button-Klick oder erste Anzeige
4. **Szenen-Erstellung**: Ruft build_scene() auf
5. **Viewer-Anzeige**: Nutzt stpyvista() für interaktive Darstellung
6. **Status-Update**: Berechnet und zeigt Kapazität/Fehlende Module
7. **Export-Handling**: Generiert Downloads bei Button-Klick

### 3. PDF-Integration (pdf_visual_inject.py)

#### Funktionen

**make_pv3d_image_flowable()**
- **Zweck**: Erstellt ReportLab Image-Objekt für PDF
- **Input**: project_data, BuildingDims, roof_type, module_quantity, LayoutConfig, width_cm
- **Output**: ReportLab Image Flowable oder None
- **Prozess**:
  1. Ruft render_image_bytes() auf
  2. Konvertiert PNG-Bytes zu BytesIO
  3. Erstellt Image mit Breite width_cm und Höhe (width_cm * 0.62)
  4. Gibt Image-Flowable zurück

**get_pv3d_png_bytes_for_pdf()**
- **Zweck**: Direkte PNG-Bytes für flexible PDF-Integration
- **Output**: PNG-Bytes (1600×1000 px, isometrische Ansicht)

#### Integration in bestehenden PDF-Generator

```python
# In pdf_generator.py oder Template-Engine
from streamlit_app.utils.pdf_visual_inject import make_pv3d_image_flowable
from streamlit_app.utils.pv3d import BuildingDims, LayoutConfig

# Während Story-Aufbau
dims = BuildingDims(length_m=10, width_m=6, wall_height_m=6)
layout = LayoutConfig(mode="auto")
roof_type = project_data.get("project_details", {}).get("roof_type", "Flachdach")
module_qty = analysis_results.get("module_quantity", 0)

flow = make_pv3d_image_flowable(
    project_data, dims, roof_type, module_qty, layout, width_cm=17.0
)
if flow:
    Story.append(flow)
    Story.append(Paragraph(
        "Abb.: 3D-Visualisierung der geplanten PV-Belegung",
        styles["Normal"]
    ))
```

## Data Models

### project_data Struktur (Eingabe)

```python
{
    "project_details": {
        "roof_type": str,              # "Flachdach", "Satteldach", etc.
        "roof_orientation": str,        # "Süd", "Ost", "West", "Nord"
        "roof_inclination_deg": float,  # 0-90
        "roof_covering_type": str,      # "Ziegel", "Beton", etc.
        "free_roof_area_m2": float,     # Optional
        # ... weitere Felder
    },
    "module_quantity": int,  # Fallback wenn nicht in analysis_results
    # ... weitere Felder
}
```

### analysis_results Struktur (Eingabe)

```python
{
    "module_quantity": int,  # Primäre Quelle für Modulanzahl
    "system_kwp": float,
    "annual_pv_production_kwh": float,
    # ... weitere Berechnungsergebnisse
}
```

### LayoutConfig (Intern)

```python
{
    "mode": "auto" | "manual",
    "use_garage": bool,
    "use_facade": bool,
    "removed_indices": [int, ...],  # 0-basierte Indizes
    "garage_dims": (float, float, float),  # (L, B, H)
    "offset_main_xy": (float, float),
    "offset_garage_xy": (float, float)
}
```

### Scene Output (build_scene Return)

```python
(
    plotter: pv.Plotter,  # PyVista Plotter-Objekt
    panels: {
        "main": [pv.PolyData, ...],     # Module auf Hauptdach
        "garage": [pv.PolyData, ...],   # Module auf Garage
        "facade": [pv.PolyData, ...]    # Module an Fassade
    }
)
```

## Error Handling

### Fehlerklassen und Behandlung

1. **Daten-Fehler**
   - Fehlende/ungültige project_data: Fallback auf Standardwerte
   - Fehlende module_quantity: Warnung + 0 Module
   - Ungültige Dimensionen: Clipping auf gültige Bereiche

2. **Rendering-Fehler**
   - PyVista-Fehler: Try-Catch mit Fehlermeldung
   - Off-Screen Rendering fehlgeschlagen: Leere Bytes zurückgeben
   - WebGL nicht verfügbar: Browser-Warnung

3. **Export-Fehler**
   - Screenshot fehlgeschlagen: Fehlermeldung, kein Download
   - STL/glTF Export fehlgeschlagen: Fehlermeldung
   - PDF-Integration fehlgeschlagen: PDF ohne Bild fortsetzen

### Fehlerbehandlungs-Pattern

```python
try:
    plotter, panels = build_scene(...)
    stpyvista(plotter, key="pv3d_viewer")
except Exception as e:
    st.error(f"3D-Visualisierung konnte nicht geladen werden: {e}")
    st.info("Bitte überprüfen Sie Ihre Eingaben und versuchen Sie es erneut.")
finally:
    if plotter:
        try:
            plotter.close()
        except:
            pass
```

## Testing Strategy

### Unit Tests

1. **Geometrie-Funktionen**
   - Test make_box() mit verschiedenen Dimensionen
   - Test Dachformen (flat, gable, hip, pent, pyramid)
   - Test make_panel() mit Rotation

2. **Datenextraktion**
   - Test _safe_get_* Funktionen mit vollständigen Daten
   - Test mit fehlenden Keys (Fallbacks)
   - Test mit ungültigen Werten

3. **Layout-Konfiguration**
   - Test LayoutConfig.to_json() / from_json()
   - Test mit verschiedenen Parameterkombinationen

### Integration Tests

1. **Szenen-Erstellung**
   - Test build_scene() mit verschiedenen Dachtypen
   - Test automatische Modul-Platzierung
   - Test manuelle Modul-Entfernung
   - Test Garage-Hinzufügung
   - Test Fassaden-Belegung

2. **PDF-Integration**
   - Test render_image_bytes() Ausgabe
   - Test make_pv3d_image_flowable() mit ReportLab
   - Test PDF-Generierung mit 3D-Bild

3. **UI-Integration**
   - Test Streamlit-Seite lädt ohne Fehler
   - Test Button-Interaktionen
   - Test Session State Persistenz

### Performance Tests

1. **Rendering-Geschwindigkeit**
   - Szenen-Erstellung < 1 Sekunde
   - Off-Screen Screenshot < 2 Sekunden
   - UI-Update < 500ms

2. **Speicher-Nutzung**
   - Plotter-Objekte werden korrekt freigegeben
   - Keine Memory Leaks bei wiederholtem Rendering

3. **Skalierbarkeit**
   - Test mit 10, 50, 100 Modulen
   - Test mit komplexen Dachformen

### Manuelle Tests

1. **Browser-Kompatibilität**
   - Chrome, Firefox, Edge, Safari
   - WebGL-Unterstützung prüfen

2. **Benutzer-Workflows**
   - Kompletter Durchlauf: Eingabe → 3D → Export → PDF
   - Verschiedene Dachformen durchspielen
   - Manueller Modus mit Modul-Entfernung

3. **Fehlerszenarien**
   - Ungültige Eingaben
   - Extreme Werte (sehr große/kleine Gebäude)
   - Netzwerk-Unterbrechungen

## Performance Considerations

### Optimierungen

1. **Mesh-Zusammenführung**
   - Module zu kombinierten Meshes zusammenfassen
   - Reduziert Draw-Calls von N auf 1-3

2. **Lazy Loading**
   - 3D-Szene nur bei Bedarf erstellen
   - Plotter im Session State cachen

3. **Off-Screen Rendering**
   - Separate Plotter-Instanz für Screenshots
   - Keine Blockierung der UI

4. **Geometrie-Vereinfachung**
   - Einfache Primitives (Quader, Dreiecke)
   - Keine hochauflösenden Texturen

### Ressourcen-Management

1. **Plotter Lifecycle**
   ```python
   try:
       plotter = pv.Plotter(off_screen=True)
       # ... Rendering
   finally:
       plotter.close()  # Wichtig!
   ```

2. **Session State Cleanup**
   - Alte Plotter-Objekte entfernen
   - Layout-Konfiguration kompakt halten

3. **Memory Limits**
   - Max. 100 Module gleichzeitig
   - Screenshot-Auflösung begrenzt (1600×1000)

## Security Considerations

1. **Input Validation**
   - Dimensionen auf gültige Bereiche begrenzen
   - Modul-Indizes validieren
   - JSON-Parsing mit Fehlerbehandlung

2. **File Operations**
   - Export-Dateien in temporäre Verzeichnisse
   - Keine Pfad-Traversal-Angriffe

3. **Resource Limits**
   - Maximale Polygon-Anzahl begrenzen
   - Timeout für Rendering-Operationen

## Deployment Considerations

### Dependencies

```txt
# requirements.txt Ergänzungen
pyvista>=0.43.10
vtk>=9.3.0
stpyvista>=0.1.4
numpy>=1.26
trimesh>=4.4.9
reportlab>=4.2.2
pikepdf>=9.0.0
Pillow>=10.0.0
```

### System Requirements

- **Python**: 3.10+
- **Browser**: Moderner Browser mit WebGL-Unterstützung
- **RAM**: Min. 4GB (8GB empfohlen)
- **GPU**: Optional, aber empfohlen für flüssiges Rendering

### Installation

```bash
# Installation der Dependencies
pip install -r requirements.txt

# Für Linux: OpenGL-Bibliotheken
sudo apt-get install libgl1-mesa-glx libglu1-mesa

# Für macOS: Keine zusätzlichen Schritte
# Für Windows: Keine zusätzlichen Schritte
```

### Configuration

Keine spezielle Konfiguration erforderlich. Das Modul nutzt die bestehende Streamlit-Konfiguration.

## Future Enhancements

### Phase 2 (Optional)

1. **Erweiterte Interaktivität**
   - Drag & Drop für Module (Custom Streamlit Component)
   - Echtzeit-Verschattungsanalyse
   - Sonnenverlauf-Animation

2. **Zusätzliche Features**
   - Mehrere Gebäude im Modell
   - Bäume und Hindernisse
   - Geländeprofil-Import

3. **Visualisierungs-Modi**
   - Heatmap für Einstrahlung
   - Ertragsprognose pro Modul
   - Verschattungs-Simulation

4. **Export-Optionen**
   - Interaktive 3D-PDFs
   - VR/AR-Export
   - CAD-Format-Export (DXF, DWG)

### Technische Verbesserungen

1. **Performance**
   - GPU-Beschleunigung für Berechnungen
   - Level-of-Detail (LOD) System
   - Streaming für große Modelle

2. **Qualität**
   - Realistische Materialien und Texturen
   - Schatten und Beleuchtung
   - Photorealistische Rendering-Option

3. **Integration**
   - API für externe Tools
   - Import von CAD-Modellen
   - Export zu PV-Simulations-Software

## Conclusion

Das 3D-Visualisierungstool bietet eine vollständige, robuste Lösung für die interaktive PV-Planung in der Streamlit-App. Durch die modulare Architektur, klare Schnittstellen und umfassende Fehlerbehandlung ist das System wartbar, erweiterbar und performant. Die nahtlose Integration in die bestehende App-Struktur gewährleistet, dass keine negativen Auswirkungen auf andere Komponenten entstehen.
