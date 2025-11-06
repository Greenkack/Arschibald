# Design Document: 3D PV-Visualisierung - Kritische Bugfixes

## Overview

Dieses Design-Dokument beschreibt die technische Lösung für vier kritische Bugs im 3D-Visualisierungssystem:

1. **Falsche Modulanzahl** - Grid-Positionierung platziert nicht die korrekte Anzahl
2. **Module im Dach eingebettet** - Keine sichtbare Aufständerung auf geneigten Dächern
3. **Optimierungs-Assistent defekt** - Funktion fehlt oder ist fehlerhaft
4. **PDF-Screenshot Integration defekt** - Screenshot wird nicht in PDF eingefügt

## Architecture

### Betroffene Module

```
utils/
├── pv3d_plotly.py          # Grid-Positionierung, Modul-Platzierung
├── pv3d.py                 # Optimierungs-Funktionen
└── pdf_visual_inject.py    # PDF-Integration

solar_3d_view_module.py     # UI und Button-Handler
pdf_generator.py            # PDF-Generierung
```

### Datenfluss

```
Benutzer klickt "Visualisierung aktualisieren"
    ↓
calculate_grid_positions() → KORRIGIERT: Exakte Anzahl Positionen
    ↓
create_pv_module_3d() → KORRIGIERT: Mounting Height für geneigte Dächer
    ↓
build_plotly_scene() → Vollständige 3D-Szene
    ↓
Plotly Figure → Interaktiver 3D-Viewer

Benutzer klickt "Optimierung starten"
    ↓
optimize_layout() → NEU IMPLEMENTIERT: Generiert Konfigurationen
    ↓
evaluate_config() → NEU IMPLEMENTIERT: Bewertet Konfigurationen
    ↓
Top 3 Konfigurationen → UI-Anzeige

Benutzer klickt "3D-Screenshot erstellen"
    ↓
render_plotly_image_bytes() → PNG-Bytes
    ↓
st.session_state["pdf_3d_screenshot"] → Speichern
    ↓
PDF-Generator → KORRIGIERT: Liest aus Session State
    ↓
make_pv3d_image_flowable() → ReportLab Image
    ↓
PDF mit 3D-Bild
```

## Components and Interfaces

### 1. Grid-Positionierung (pv3d_plotly.py)

#### Problem
Die Funktion `calculate_grid_positions()` berechnet nicht die korrekte Anzahl Positionen.


#### Aktuelle Implementierung (FEHLERHAFT)
```python
def calculate_grid_positions(length, width, count, spacing_x=0.25, spacing_y=0.25):
    # Problem: Berechnet max. mögliche Module, nicht die gewünschte Anzahl
    margin = 0.5
    available_length = length - 2 * margin
    available_width = width - 2 * margin
    
    modules_x = max(1, int(available_length / (PV_W + spacing_x)))
    modules_y = max(1, int(available_width / (PV_H + spacing_y)))
    
    # Problem: Gibt alle möglichen Positionen zurück, nicht nur 'count'
    for row in range(modules_y):
        for col in range(modules_x):
            if len(positions) >= count:
                break
            # ...
```

#### Korrigierte Implementierung
```python
def calculate_grid_positions(length, width, count, spacing_x=0.25, spacing_y=0.25):
    """
    Berechnet EXAKT 'count' Grid-Positionen (oder weniger wenn nicht genug Platz).
    
    FIX: Korrekte Berechnung mit Zentrierung und exakter Anzahl.
    """
    positions = []
    margin = 0.5  # 50cm Randabstand
    
    # Verfügbare Fläche
    available_length = length - 2 * margin
    available_width = width - 2 * margin
    
    # Maximale Anzahl Module die passen
    max_modules_x = max(1, int((available_length + spacing_x) / (PV_W + spacing_x)))
    max_modules_y = max(1, int((available_width + spacing_y) / (PV_H + spacing_y)))
    max_total = max_modules_x * max_modules_y
    
    # Warnung wenn nicht genug Platz
    if count > max_total:
        print(f"⚠️ WARNUNG: Nur {max_total} von {count} Modulen passen!")
        count = max_total
    
    # Berechne optimales Layout für 'count' Module
    # Versuche möglichst quadratisches Layout
    best_layout = None
    min_waste = float('inf')
    
    for cols in range(1, max_modules_x + 1):
        rows = math.ceil(count / cols)
        if rows <= max_modules_y:
            waste = (cols * rows) - count
            if waste < min_waste:
                min_waste = waste
                best_layout = (cols, rows)
    
    if not best_layout:
        # Fallback: Maximale Spalten
        best_layout = (max_modules_x, math.ceil(count / max_modules_x))
    
    modules_x, modules_y = best_layout
    
    # Berechne tatsächliche Grid-Größe
    total_width_x = modules_x * PV_W + (modules_x - 1) * spacing_x
    total_width_y = modules_y * PV_H + (modules_y - 1) * spacing_y
    
    # Zentriere Grid
    start_x = -total_width_x / 2
    start_y = -total_width_y / 2
    
    # Erstelle EXAKT 'count' Positionen
    for row in range(modules_y):
        for col in range(modules_x):
            if len(positions) >= count:
                break
            
            x = start_x + col * (PV_W + spacing_x) + PV_W / 2
            y = start_y + row * (PV_H + spacing_y) + PV_H / 2
            positions.append((x, y))
        
        if len(positions) >= count:
            break
    
    print(f"✓ Grid-Positionierung: {len(positions)} von {count} Modulen platziert")
    return positions
```

### 2. Modul-Aufständerung (pv3d_plotly.py)

#### Problem
Module werden direkt auf der Dachfläche platziert ohne sichtbaren Abstand.

#### Aktuelle Implementierung (FEHLERHAFT)
```python
def create_pv_module_3d(x, y, z, azimuth_deg=0, tilt_deg=15, ...):
    # Problem: Z-Position wird nicht angepasst für geneigte Dächer
    # Module sinken in die Dachfläche ein
```

#### Korrigierte Implementierung
```python
def create_pv_module_3d(x, y, z, azimuth_deg=0, tilt_deg=15, 
                        color="#1a1a2e", selected=False, 
                        show_mounting=True, roof_type="Flachdach"):
    """
    Erstellt ein PV-Modul mit korrekter Aufständerung.
    
    FIX: Mounting Height wird basierend auf Dachform und Neigung berechnet.
    """
    # Berechne Mounting Height
    mounting_height = 0.0
    
    if roof_type != "Flachdach" and tilt_deg > 5.0:
        # Geneigte Dächer: Sichtbare Aufständerung
        # Höhe abhängig von Neigung (min 0.1m, max 0.3m)
        mounting_height = 0.1 + (tilt_deg / 90.0) * 0.2
        mounting_height = min(0.3, mounting_height)
        
        if show_mounting:
            # Zusätzliche Höhe für Gestell-Visualisierung
            mounting_height += 0.05
    
    elif roof_type == "Flachdach" and tilt_deg > 5.0:
        # Flachdach mit Aufständerung
        mounting_height = 0.3 + (tilt_deg / 90.0) * 0.5
    
    # Erhöhe Z-Position um Mounting Height
    z += mounting_height
    
    # Rest der Funktion bleibt gleich...
    # (Rotation, Mesh-Erstellung, etc.)
```

### 3. Optimierungs-Assistent (pv3d.py)

#### Problem
Die Funktion `optimize_layout()` existiert nicht oder ist nicht implementiert.

#### Neue Implementierung
```python
def optimize_layout(
    building_dims: BuildingDims,
    target_modules: int,
    roof_type: str,
    optimization_goal: str = "balanced"
) -> List[Tuple[AdvancedLayoutConfig, float]]:
    """
    Generiert und bewertet verschiedene PV-Layout-Konfigurationen.
    
    Args:
        building_dims: Gebäudedimensionen
        target_modules: Gewünschte Modulanzahl
        roof_type: Dachform
        optimization_goal: "max_modules", "max_yield", oder "balanced"
    
    Returns:
        Liste von (Konfiguration, Score) Tupeln, sortiert nach Score
    """
    configurations = []
    
    # Strategie 1: Süd-Aufständerung
    config1 = AdvancedLayoutConfig(
        mode="auto",
        mounting_mode="south",
        custom_azimuth=0.0,
        custom_tilt=15.0
    )
    score1 = evaluate_config(config1, building_dims, target_modules, optimization_goal)
    configurations.append((config1, score1))
    
    # Strategie 2: Ost-West-Aufständerung
    config2 = AdvancedLayoutConfig(
        mode="auto",
        mounting_mode="east-west",
        custom_azimuth=0.0,
        custom_tilt=10.0
    )
    score2 = evaluate_config(config2, building_dims, target_modules, optimization_goal)
    configurations.append((config2, score2))
    
    # Strategie 3: Süd-Ost
    config3 = AdvancedLayoutConfig(
        mode="auto",
        mounting_mode="south-east",
        custom_azimuth=45.0,
        custom_tilt=15.0
    )
    score3 = evaluate_config(config3, building_dims, target_modules, optimization_goal)
    configurations.append((config3, score3))
    
    # Strategie 4: Gemischt (mit Garage und Fassade)
    config4 = AdvancedLayoutConfig(
        mode="auto",
        use_garage=True,
        use_facade=True,
        mounting_mode="south"
    )
    score4 = evaluate_config(config4, building_dims, target_modules, optimization_goal)
    configurations.append((config4, score4))
    
    # Sortiere nach Score (höchster zuerst)
    configurations.sort(key=lambda x: x[1], reverse=True)
    
    # Gebe Top 3 zurück
    return configurations[:3]


def evaluate_config(
    config: AdvancedLayoutConfig,
    building_dims: BuildingDims,
    target_modules: int,
    goal: str
) -> float:
    """
    Bewertet eine Konfiguration basierend auf Optimierungsziel.
    
    Returns:
        Score von 0-100
    """
    score = 0.0
    
    # Berechne geschätzte Modulanzahl für diese Konfiguration
    roof_area = building_dims.length_m * building_dims.width_m
    module_area = 1.05 * 1.76
    
    # Effizienzfaktor basierend auf Mounting Mode
    efficiency_factors = {
        "south": 0.75,
        "east-west": 0.65,  # Weniger Platz wegen Reihenabstand
        "south-east": 0.70,
        "south-west": 0.70
    }
    efficiency = efficiency_factors.get(config.mounting_mode, 0.70)
    
    # Zusätzliche Kapazität durch Garage/Fassade
    if config.use_garage:
        efficiency += 0.15
    if config.use_facade:
        efficiency += 0.10
    
    estimated_modules = int((roof_area / module_area) * efficiency)
    
    # Bewertung basierend auf Ziel
    if goal == "max_modules":
        # Maximiere Modulanzahl
        score += min(100, (estimated_modules / target_modules) * 100)
        
    elif goal == "max_yield":
        # Maximiere Ertrag (Süd-Ausrichtung bevorzugt)
        module_score = min(100, (estimated_modules / target_modules) * 70)
        
        # Ausrichtungs-Bonus
        orientation_bonus = 0
        if config.mounting_mode == "south":
            orientation_bonus = 30
        elif config.mounting_mode in ["south-east", "south-west"]:
            orientation_bonus = 20
        elif config.mounting_mode == "east-west":
            orientation_bonus = 15
        
        score = module_score + orientation_bonus
        
    elif goal == "balanced":
        # Ausgewogen
        module_score = min(100, (estimated_modules / target_modules) * 60)
        
        orientation_bonus = 0
        if config.mounting_mode == "south":
            orientation_bonus = 25
        elif config.mounting_mode in ["south-east", "south-west"]:
            orientation_bonus = 20
        elif config.mounting_mode == "east-west":
            orientation_bonus = 15
        
        # Bonus für einfache Konfiguration (ohne Garage/Fassade)
        simplicity_bonus = 0
        if not config.use_garage and not config.use_facade:
            simplicity_bonus = 15
        
        score = module_score + orientation_bonus + simplicity_bonus
    
    return min(100.0, max(0.0, score))
```

### 4. PDF-Screenshot-Integration

#### Problem
Screenshot wird erstellt aber nicht in PDF eingefügt.

#### Aktuelle Implementierung (FEHLERHAFT)
```python
# In solar_3d_view_module.py
if st.button("📸 3D-Screenshot erstellen"):
    png_bytes = render_plotly_image_bytes(...)
    # Problem: Wird nicht in Session State gespeichert
    st.download_button("Download PNG", png_bytes)
```

#### Korrigierte Implementierung

**In solar_3d_view_module.py:**
```python
if st.button("📸 3D-Screenshot erstellen"):
    try:
        # Erstelle Screenshot
        png_bytes = render_plotly_image_bytes(
            project_data=project_data,
            dims=dims,
            roof_type=selected_roof_type,
            module_quantity=module_quantity,
            layout_config=current_config
        )
        
        if png_bytes:
            # WICHTIG: Speichere in Session State für PDF
            st.session_state["pdf_3d_screenshot"] = png_bytes
            
            # Download-Button
            st.download_button(
                "📥 PNG herunterladen",
                data=png_bytes,
                file_name="3d_visualization.png",
                mime="image/png"
            )
            
            st.success("✓ Screenshot erstellt und für PDF vorbereitet!")
            st.info(
                "💡 Der Screenshot wird automatisch auf Seite 6 des PDF-Angebots "
                "eingefügt, wenn Sie das PDF erstellen."
            )
        else:
            st.error("❌ Screenshot-Erstellung fehlgeschlagen")
            
    except Exception as e:
        st.error(f"❌ Fehler beim Screenshot: {e}")
```

**In pdf_generator.py:**
```python
def _add_3d_visualization_section(self, project_data):
    """Fügt 3D-Visualisierung hinzu (Seite 6)."""
    
    # Prüfe ob Screenshot in Session State vorhanden
    png_bytes = st.session_state.get("pdf_3d_screenshot")
    
    if png_bytes:
        try:
            # Konvertiere PNG-Bytes zu ReportLab Image
            from io import BytesIO
            from reportlab.platypus import Image
            
            img_buffer = BytesIO(png_bytes)
            
            # Erstelle Image mit 17cm Breite, Höhe automatisch
            img = Image(img_buffer, width=17*cm, height=10.625*cm)
            
            self.story.append(img)
            self.story.append(Spacer(1, 0.5*cm))
            self.story.append(Paragraph(
                "Abb.: 3D-Visualisierung der geplanten PV-Anlage",
                self.styles["Normal"]
            ))
            
            print("✓ 3D-Screenshot in PDF eingefügt")
            
        except Exception as e:
            print(f"⚠️ Fehler beim Einfügen des 3D-Screenshots: {e}")
            # Fallback: Platzhalter-Text
            self.story.append(Paragraph(
                "3D-Visualisierung konnte nicht geladen werden.",
                self.styles["Normal"]
            ))
    else:
        print("ℹ️ Kein 3D-Screenshot vorhanden, überspringe Sektion")
        # Optional: Platzhalter-Text
        self.story.append(Paragraph(
            "3D-Visualisierung: Bitte erstellen Sie einen Screenshot "
            "in der 3D-Ansicht.",
            self.styles["Normal"]
        ))
```

## Error Handling

### Logging-Strategie

Alle kritischen Funktionen loggen detaillierte Informationen:

```python
# Grid-Positionierung
print(f"Grid-Positionierung:")
print(f"  Dachgröße: {length}m x {width}m")
print(f"  Gewünschte Module: {count}")
print(f"  Max. mögliche Module: {max_total}")
print(f"  Platzierte Module: {len(positions)}")
if count > len(positions):
    print(f"  ⚠️ WARNUNG: {count - len(positions)} Module passen nicht!")

# Modul-Aufständerung
print(f"Modul-Platzierung:")
print(f"  Dachform: {roof_type}")
print(f"  Neigung: {tilt_deg}°")
print(f"  Mounting Height: {mounting_height}m")
print(f"  Z-Position: {z}m")

# Optimierung
print(f"Optimierung:")
print(f"  Ziel: {optimization_goal}")
print(f"  Generierte Konfigurationen: {len(configurations)}")
for i, (config, score) in enumerate(configurations, 1):
    print(f"  {i}. {config.mounting_mode}: Score {score:.1f}")

# PDF-Integration
print(f"PDF-Screenshot:")
print(f"  Größe: {len(png_bytes)} bytes")
print(f"  In Session State: {'Ja' if png_bytes else 'Nein'}")
```

## Testing Strategy

### Unit Tests

1. **test_grid_positions_exact_count()** - Prüft exakte Modulanzahl
2. **test_mounting_height_calculation()** - Prüft Mounting Height für verschiedene Dachformen
3. **test_optimize_layout()** - Prüft Generierung von Konfigurationen
4. **test_evaluate_config()** - Prüft Score-Berechnung
5. **test_pdf_screenshot_integration()** - Prüft Session State und PDF-Einfügung

### Integration Tests

1. **test_full_workflow_flat_roof()** - Kompletter Workflow für Flachdach
2. **test_full_workflow_gabled_roof()** - Kompletter Workflow für Satteldach
3. **test_optimization_workflow()** - Optimierung von Start bis Übernahme
4. **test_pdf_generation_with_screenshot()** - PDF-Generierung mit 3D-Bild

## Performance Considerations

- Grid-Positionierung: O(n) statt O(n²) durch direkte Berechnung
- Optimierung: Nur 4 Konfigurationen statt exhaustive Suche
- PDF-Integration: Screenshot wird nur einmal erstellt und wiederverwendet

## Deployment

Keine zusätzlichen Dependencies erforderlich. Alle Fixes nutzen bestehende Bibliotheken.
