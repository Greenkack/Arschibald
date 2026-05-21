# Design Document: Multi-PDF Positioning Optimization

## Overview

Dieses System analysiert 48 PDF-Vorlagen (6 Firmen × 8 Seiten) und optimiert die Positionierung von Text-Elementen in den entsprechenden YML-Koordinatendateien. Das Ziel ist es, für jede Firma und jede Seite eine individuelle, design-optimierte Positionierung zu erstellen, die das jeweilige Layout, die Farben und Formen der PDF-Vorlage optimal nutzt.

### Kernprinzipien

1. **Nur Positionen ändern**: Ausschließlich die Koordinaten (x1, y1, x2, y2) werden modifiziert
2. **Design-getrieben**: Positionierungen basieren auf der visuellen Analyse der PDF-Vorlagen
3. **Individuelle Layouts**: Jede Firma-Seiten-Kombination erhält eine einzigartige Positionierung
4. **Nicht-destruktiv**: Original-Dateien werden gesichert, alle anderen Attribute bleiben erhalten

## Architecture

### Komponenten-Übersicht

```
┌─────────────────────────────────────────────────────────────┐
│                    Multi-PDF Positioning System              │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐      ┌──────────────────┐            │
│  │  PDF Analyzer    │      │  YML Parser      │            │
│  │                  │      │                  │            │
│  │  - Extract       │      │  - Read YML      │            │
│  │    metadata      │      │  - Parse         │            │
│  │  - Analyze       │      │    structure     │            │
│  │    colors        │      │  - Preserve      │            │
│  │  - Detect        │      │    attributes    │            │
│  │    regions       │      │                  │            │
│  └────────┬─────────┘      └────────┬─────────┘            │
│           │                         │                       │
│           └────────┬────────────────┘                       │
│                    │                                        │
│           ┌────────▼─────────┐                             │
│           │  Position        │                             │
│           │  Calculator      │                             │
│           │                  │                             │
│           │  - Design rules  │                             │
│           │  - Layout grid   │                             │
│           │  - Collision     │                             │
│           │    detection     │                             │
│           │  - Optimization  │                             │
│           └────────┬─────────┘                             │
│                    │                                        │
│           ┌────────▼─────────┐                             │
│           │  YML Generator   │                             │
│           │                  │                             │
│           │  - Update        │                             │
│           │    positions     │                             │
│           │  - Preserve      │                             │
│           │    format        │                             │
│           │  - Validate      │                             │
│           └────────┬─────────┘                             │
│                    │                                        │
│           ┌────────▼─────────┐                             │
│           │  Backup Manager  │                             │
│           │  & Validator     │                             │
│           └──────────────────┘                             │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. PDF Analyzer

**Zweck**: Analysiert PDF-Vorlagen und extrahiert Design-Informationen

**Eingabe**:
- PDF-Dateipfad: `C:\Users\win10\Desktop\Bokuk2 - Kopie\pdf_templates_static\multi\multi_nt_[01-08]_f[1-6].pdf`

**Ausgabe**:
```python
{
    "firma": 1,
    "seite": 1,
    "page_size": {"width": 595, "height": 842},
    "design_regions": [
        {
            "type": "header",
            "bounds": {"x1": 0, "y1": 0, "x2": 595, "y2": 150},
            "dominant_color": "#007BFF",
            "suggested_text_color": "#FFFFFF"
        },
        {
            "type": "content",
            "bounds": {"x1": 50, "y1": 150, "x2": 545, "y2": 700},
            "dominant_color": "#FFFFFF",
            "suggested_text_color": "#000000"
        }
    ],
    "visual_elements": [
        {"type": "shape", "position": [100, 200, 200, 300], "color": "#FF5733"}
    ],
    "safe_zones": [
        {"x1": 50, "y1": 70, "x2": 545, "y2": 800}
    ]
}
```

**Methoden**:
- `analyze_pdf(pdf_path)`: Hauptanalyse-Funktion
- `extract_colors(pdf_path)`: Extrahiert Farbpalette
- `detect_regions(pdf_path)`: Identifiziert Layout-Bereiche
- `find_safe_zones(pdf_path)`: Bestimmt sichere Text-Bereiche

### 2. YML Parser

**Zweck**: Liest und parst YML-Koordinatendateien

**Eingabe**:
- YML-Dateipfad: `coords_multi/seite[1-8]_f[1-6].yml`

**Ausgabe**:
```python
[
    {
        "text": "ERSTELLT FÜR:",
        "position": (48.0, 70.0, 220.0, 87.0),
        "font": "Helvetica-Bold",
        "font_size": 20.0,
        "color": 30920,
        "index": 0  # Reihenfolge in der Datei
    },
    {
        "text": "kunde_vorname_und_nachname",
        "position": (90.0, 87.0, 220.0, 105.0),
        "font": "Helvetica-Bold",
        "font_size": 14.0,
        "color": 3487029,
        "index": 1
    }
]
```

**Methoden**:
- `parse_yml(yml_path)`: Parst YML-Datei
- `extract_elements()`: Extrahiert alle Text-Elemente
- `preserve_structure()`: Behält Original-Struktur bei

### 3. Position Calculator

**Zweck**: Berechnet optimale Positionen basierend auf Design-Analyse

**Eingabe**:
- PDF-Analyse-Daten
- Aktuelle YML-Elemente
- Firmen- und Seiten-Nummer

**Positionierungs-Strategien**:

#### Strategie 1: Header-Focused (Firma 1, Seite 1)
- Hauptüberschrift: Oben links
- Wichtige Werte (kWp): Rechts unten
- Kundeninfo: Zentriert unter Überschrift

#### Strategie 2: Center-Prominent (Firma 2, Seite 1)
- Hauptüberschrift: Zentriert
- Wichtige Werte (kWp): Rechts oben
- Kundeninfo: Links oben

#### Strategie 3: Asymmetric-Modern (Firma 3, Seite 1)
- Hauptüberschrift: Rechts oben
- Wichtige Werte (kWp): Links unten
- Kundeninfo: Rechts Mitte

#### Strategie 4: Grid-Based (Firma 4, Seite 1)
- Elemente in 3x3 Grid verteilt
- Wichtige Werte in Zentrum
- Symmetrische Anordnung

#### Strategie 5: Diagonal-Flow (Firma 5, Seite 1)
- Elemente diagonal von links oben nach rechts unten
- Wichtige Werte folgen diagonaler Linie

#### Strategie 6: Sidebar-Layout (Firma 6, Seite 1)
- Hauptinfo in linker Spalte
- Wichtige Werte in rechter Spalte
- Klare vertikale Trennung

**Methoden**:
- `calculate_positions(pdf_analysis, yml_elements, firma, seite)`: Hauptberechnung
- `apply_strategy(strategy_name, elements)`: Wendet Positionierungs-Strategie an
- `check_collisions(positions)`: Prüft Überlappungen
- `optimize_spacing(positions)`: Optimiert Abstände
- `ensure_bounds(position)`: Stellt sicher, dass Position in PDF-Grenzen liegt

**Positionierungs-Regeln**:

```python
POSITIONING_RULES = {
    "min_margin": 10,  # Mindestabstand zum Rand
    "min_spacing": 5,  # Mindestabstand zwischen Elementen
    "page_width": 595,
    "page_height": 842,
    "importance_weights": {
        "ERSTELLT FÜR:": 0.9,
        "PHOTOVOLTAIK": 0.95,
        "ANGEBOT": 1.0,
        "kWp_anlage_anlage": 1.0,
        "kunde_vorname_und_nachname": 0.85
    }
}
```

### 4. YML Generator

**Zweck**: Generiert aktualisierte YML-Dateien mit neuen Positionen

**Eingabe**:
- Original YML-Elemente
- Neue Positionen vom Position Calculator

**Ausgabe**:
- Aktualisierte YML-Datei mit identischer Struktur, nur geänderten Positionen

**Methoden**:
- `generate_yml(elements, new_positions, output_path)`: Generiert YML
- `format_position(x1, y1, x2, y2)`: Formatiert Position-Tuple
- `preserve_formatting()`: Behält Original-Formatierung bei
- `validate_output()`: Validiert generierte Datei

**YML-Format-Beispiel**:
```yaml
Text: ERSTELLT FÜR:
Position: (48.0, 70.0, 220.0, 87.0)
Schriftart: Helvetica-Bold
Schriftgröße: 20.0
Farbe: 30920
----------------------------------------
```

### 5. Backup Manager

**Zweck**: Sichert Original-Dateien vor Änderungen

**Methoden**:
- `create_backup(yml_files)`: Erstellt Backup aller YML-Dateien
- `restore_backup(backup_id)`: Stellt Backup wieder her
- `list_backups()`: Listet verfügbare Backups
- `validate_backup(backup_path)`: Prüft Backup-Integrität

**Backup-Struktur**:
```
coords_multi_backup/
├── backup_2025-01-10_14-30-00/
│   ├── seite1_f1.yml
│   ├── seite1_f2.yml
│   └── ...
└── backup_2025-01-10_15-45-00/
    └── ...
```

## Data Models

### PDFAnalysis
```python
@dataclass
class PDFAnalysis:
    firma: int
    seite: int
    page_size: Dict[str, float]
    design_regions: List[DesignRegion]
    visual_elements: List[VisualElement]
    safe_zones: List[SafeZone]
    color_palette: List[str]
```

### YMLElement
```python
@dataclass
class YMLElement:
    text: str
    position: Tuple[float, float, float, float]
    font: str
    font_size: float
    color: int
    index: int  # Original position in file
```

### PositionStrategy
```python
@dataclass
class PositionStrategy:
    name: str
    firma: int
    seite: int
    layout_type: str  # "header-focused", "center-prominent", etc.
    anchor_points: Dict[str, Tuple[float, float]]
    spacing_rules: Dict[str, float]
```

## Error Handling

### Fehlertypen

1. **PDF-Analyse-Fehler**
   - PDF nicht gefunden
   - PDF beschädigt
   - Keine Design-Elemente erkennbar

2. **YML-Parsing-Fehler**
   - YML-Datei nicht gefunden
   - Ungültiges YML-Format
   - Fehlende erforderliche Felder

3. **Positionierungs-Fehler**
   - Position außerhalb der PDF-Grenzen
   - Überlappende Text-Elemente
   - Zu wenig Platz für Text

4. **Validierungs-Fehler**
   - Generierte YML ungültig
   - Backup fehlgeschlagen
   - Schreibrechte fehlen

### Fehlerbehandlung-Strategie

```python
try:
    # PDF-Analyse
    pdf_analysis = analyze_pdf(pdf_path)
except PDFNotFoundError:
    log_error("PDF nicht gefunden", pdf_path)
    skip_to_next()
except PDFCorruptedError:
    log_error("PDF beschädigt", pdf_path)
    use_fallback_analysis()

try:
    # Position berechnen
    new_positions = calculate_positions(pdf_analysis, yml_elements)
except PositionOutOfBoundsError as e:
    log_warning("Position außerhalb Grenzen", e.position)
    adjust_position_to_bounds(e.position)
except CollisionDetectedError as e:
    log_warning("Überlappung erkannt", e.elements)
    resolve_collision(e.elements)
```

## Testing Strategy

### Unit Tests

1. **PDF Analyzer Tests**
   - Test PDF-Metadaten-Extraktion
   - Test Farb-Analyse
   - Test Region-Erkennung

2. **YML Parser Tests**
   - Test YML-Parsing
   - Test Struktur-Erhaltung
   - Test Attribut-Extraktion

3. **Position Calculator Tests**
   - Test jede Positionierungs-Strategie
   - Test Kollisions-Erkennung
   - Test Grenzen-Validierung

4. **YML Generator Tests**
   - Test YML-Generierung
   - Test Format-Erhaltung
   - Test Position-Update

### Integration Tests

1. **End-to-End Test**
   - Vollständiger Durchlauf für eine Firma-Seiten-Kombination
   - Validierung der generierten YML-Datei
   - Vergleich mit Original

2. **Batch Processing Test**
   - Verarbeitung aller 48 Kombinationen
   - Performance-Messung
   - Fehlerbehandlung

### Validierungs-Tests

1. **Position Validation**
   - Alle Positionen innerhalb PDF-Grenzen
   - Keine Überlappungen
   - Ausreichende Abstände

2. **YML Validation**
   - Gültiges YML-Format
   - Alle Attribute erhalten
   - Korrekte Reihenfolge

## Performance Considerations

### Optimierungen

1. **Parallel Processing**
   - Verarbeitung mehrerer PDFs gleichzeitig
   - Thread-Pool für PDF-Analyse

2. **Caching**
   - Cache PDF-Analyse-Ergebnisse
   - Cache YML-Parsing-Ergebnisse

3. **Batch Operations**
   - Gruppierte Datei-Operationen
   - Minimierung von Disk I/O

### Geschätzte Laufzeit

- PDF-Analyse: ~2-3 Sekunden pro PDF
- YML-Parsing: ~0.1 Sekunden pro YML
- Position-Berechnung: ~0.5 Sekunden pro Kombination
- YML-Generierung: ~0.2 Sekunden pro YML

**Gesamt für 48 Kombinationen**: ~3-5 Minuten

## Deployment

### Voraussetzungen

- Python 3.8+
- PyPDF2 oder pdfplumber für PDF-Analyse
- PyYAML für YML-Verarbeitung
- Pillow für visuelle Analyse (optional)

### Installation

```bash
pip install pypdf2 pyyaml pillow
```

### Ausführung

```bash
python multi_pdf_positioning.py --analyze --generate --validate
```

### Konfiguration

```python
CONFIG = {
    "pdf_dir": "C:\\Users\\win10\\Desktop\\Bokuk2 - Kopie\\pdf_templates_static\\multi",
    "yml_dir": "coords_multi",
    "backup_dir": "coords_multi_backup",
    "firmen": [1, 2, 3, 4, 5, 6],
    "seiten": [1, 2, 3, 4, 5, 6, 7, 8],
    "create_backup": True,
    "validate_output": True
}
```
