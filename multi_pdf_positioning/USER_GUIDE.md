# Multi-PDF Positioning System - Benutzerhandbuch

## Inhaltsverzeichnis

1. [Überblick](#überblick)
2. [Installation](#installation)
3. [Schnellstart](#schnellstart)
4. [CLI-Optionen](#cli-optionen)
5. [Anwendungsfälle](#anwendungsfälle)
6. [Positionierungs-Strategien](#positionierungs-strategien)
7. [Visualisierung](#visualisierung)
8. [Statistiken](#statistiken)
9. [Fehlerbehebung](#fehlerbehebung)

## Überblick

Das Multi-PDF Positioning System optimiert die Positionierung von Text-Elementen in PDF-Angeboten für Photovoltaik-Systeme. Es analysiert 48 PDF-Vorlagen (6 Firmen × 8 Seiten) und generiert optimierte YML-Koordinatendateien basierend auf dem jeweiligen Design.

### Hauptfunktionen

- **Automatische Positionierung**: Berechnet optimale Positionen basierend auf PDF-Design
- **6 Positionierungs-Strategien**: Individuelle Layouts für jede Firma
- **Kollisionserkennung**: Verhindert überlappende Text-Elemente
- **Validierung**: Prüft Positionen auf Gültigkeit
- **Visualisierung**: Erstellt Vergleichsbilder
- **Statistiken**: Generiert detaillierte Berichte
- **Backup & Restore**: Sichert Original-Dateien

## Installation

### Voraussetzungen

- Python 3.8 oder höher
- pip (Python Package Manager)

### Schritt 1: Repository klonen

```bash
git clone <repository-url>
cd multi-pdf-positioning
```

### Schritt 2: Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

Erforderliche Pakete:
- `PyPDF2` oder `pdfplumber` - PDF-Analyse
- `PyYAML` - YML-Verarbeitung
- `Pillow` - Bildgenerierung für Visualisierung

### Schritt 3: Konfiguration prüfen

Bearbeiten Sie `multi_pdf_positioning/config.py` und passen Sie die Pfade an:

```python
PDF_DIR = Path("C:/Users/win10/Desktop/Bokuk2 - Kopie/pdf_templates_static/multi")
YML_DIR = Path("coords_multi")
BACKUP_DIR = Path("coords_multi_backup")
OUTPUT_DIR = Path("coords_multi_output")
```

## Schnellstart

### Alle Kombinationen verarbeiten

```bash
python -m multi_pdf_positioning.cli --all
```

Dies führt folgende Schritte aus:
1. Erstellt Backup aller YML-Dateien
2. Analysiert alle 48 PDF-Vorlagen
3. Berechnet optimale Positionen
4. Generiert neue YML-Dateien
5. Validiert Ergebnisse
6. Erstellt Statistiken

### Einzelne Firma verarbeiten

```bash
python -m multi_pdf_positioning.cli --firma 1
```

### Einzelne Seite verarbeiten

```bash
python -m multi_pdf_positioning.cli --seite 1
```

### Spezifische Kombination

```bash
python -m multi_pdf_positioning.cli --firma 1 --seite 1
```

## CLI-Optionen

### Hauptoptionen

| Option | Beschreibung | Beispiel |
|--------|--------------|----------|
| `--all` | Verarbeitet alle 48 Kombinationen | `--all` |
| `--firma NUMMER` | Verarbeitet spezifische Firma(en) | `--firma 1` oder `--firma 1,2,3` |
| `--seite NUMMER` | Verarbeitet spezifische Seite(n) | `--seite 1` oder `--seite 1,2,3` |

### Analyse-Optionen

| Option | Beschreibung | Beispiel |
|--------|--------------|----------|
| `--analyze` | Nur PDF-Analyse durchführen | `--analyze` |
| `--analyze-output PFAD` | Ausgabepfad für Analyse | `--analyze-output analysis.json` |

### Generierungs-Optionen

| Option | Beschreibung | Beispiel |
|--------|--------------|----------|
| `--generate` | YML-Dateien generieren | `--generate` |
| `--output-dir PFAD` | Ausgabeverzeichnis | `--output-dir output/` |
| `--no-backup` | Kein Backup erstellen | `--no-backup` |

### Validierungs-Optionen

| Option | Beschreibung | Beispiel |
|--------|--------------|----------|
| `--validate` | Nur Validierung durchführen | `--validate` |
| `--no-validate` | Validierung überspringen | `--no-validate` |
| `--validation-report PFAD` | Validierungsbericht speichern | `--validation-report report.txt` |

### Backup-Optionen

| Option | Beschreibung | Beispiel |
|--------|--------------|----------|
| `--backup` | Backup erstellen | `--backup` |
| `--restore BACKUP_ID` | Backup wiederherstellen | `--restore backup_20250110_143000` |
| `--list-backups` | Verfügbare Backups auflisten | `--list-backups` |

### Visualisierungs-Optionen

| Option | Beschreibung | Beispiel |
|--------|--------------|----------|
| `--visualize` | Visualisierungen erstellen | `--visualize` |
| `--viz-output PFAD` | Ausgabeverzeichnis für Bilder | `--viz-output visualizations/` |
| `--viz-type TYP` | Visualisierungstyp | `--viz-type overlay` |

Verfügbare Visualisierungstypen:
- `overlay` - Überlagerung alt/neu
- `comparison` - Seite-an-Seite Vergleich
- `movement` - Bewegungspfeile
- `collision` - Kollisions-Hervorhebung
- `all` - Alle Typen (Standard)

### Statistik-Optionen

| Option | Beschreibung | Beispiel |
|--------|--------------|----------|
| `--statistics` | Statistiken generieren | `--statistics` |
| `--stats-output PFAD` | Ausgabepfad für Statistiken | `--stats-output stats.json` |
| `--stats-format FORMAT` | Ausgabeformat | `--stats-format json` |

Verfügbare Formate:
- `json` - JSON-Format
- `csv` - CSV-Format
- `txt` - Text-Format (Standard)

### Weitere Optionen

| Option | Beschreibung | Beispiel |
|--------|--------------|----------|
| `--quiet` | Keine Fortschrittsanzeige | `--quiet` |
| `--verbose` | Detaillierte Ausgabe | `--verbose` |
| `--help` | Hilfe anzeigen | `--help` |

## Anwendungsfälle

### Fall 1: Erste Optimierung durchführen

```bash
# Schritt 1: Backup erstellen
python -m multi_pdf_positioning.cli --backup

# Schritt 2: Analyse durchführen
python -m multi_pdf_positioning.cli --analyze --analyze-output analysis.json

# Schritt 3: Alle Kombinationen verarbeiten
python -m multi_pdf_positioning.cli --all

# Schritt 4: Visualisierungen erstellen
python -m multi_pdf_positioning.cli --visualize --all

# Schritt 5: Statistiken generieren
python -m multi_pdf_positioning.cli --statistics --all
```

### Fall 2: Einzelne Firma testen

```bash
# Nur Firma 1 verarbeiten
python -m multi_pdf_positioning.cli --firma 1 --visualize --statistics
```

### Fall 3: Änderungen rückgängig machen

```bash
# Verfügbare Backups anzeigen
python -m multi_pdf_positioning.cli --list-backups

# Backup wiederherstellen
python -m multi_pdf_positioning.cli --restore backup_20250110_143000
```

### Fall 4: Nur Validierung

```bash
# Bestehende YML-Dateien validieren
python -m multi_pdf_positioning.cli --validate --all --validation-report validation.txt
```

### Fall 5: Batch-Verarbeitung mit Statistiken

```bash
# Alle Firmen verarbeiten und Statistiken exportieren
python -m multi_pdf_positioning.cli --all \
  --statistics \
  --stats-output stats.json \
  --stats-format json \
  --visualize \
  --viz-output visualizations/
```

## Positionierungs-Strategien

Das System verwendet 6 verschiedene Positionierungs-Strategien, eine für jede Firma:

### Strategie 1: Header-Focused (Firma 1)

**Beschreibung**: Fokus auf Header-Bereich mit prominenter Platzierung wichtiger Werte.

**Charakteristiken**:
- Hauptüberschrift: Oben links
- Wichtige Werte (kWp, Preis): Rechts unten
- Kundeninfo: Zentriert unter Überschrift
- Symmetrische Anordnung

**Anwendung**: Ideal für formelle, professionelle Angebote

### Strategie 2: Center-Prominent (Firma 2)

**Beschreibung**: Zentrierte Hauptelemente mit Fokus auf Mitte.

**Charakteristiken**:
- Hauptüberschrift: Zentriert
- Wichtige Werte: Rechts oben
- Kundeninfo: Links oben
- Ausgewogene Verteilung

**Anwendung**: Moderne, ausgewogene Layouts

### Strategie 3: Asymmetric-Modern (Firma 3)

**Beschreibung**: Asymmetrisches, modernes Layout.

**Charakteristiken**:
- Hauptüberschrift: Rechts oben
- Wichtige Werte: Links unten
- Kundeninfo: Rechts Mitte
- Dynamische Anordnung

**Anwendung**: Kreative, auffällige Designs

### Strategie 4: Grid-Based (Firma 4)

**Beschreibung**: Strukturiertes Grid-Layout.

**Charakteristiken**:
- Elemente in 3×3 Grid verteilt
- Wichtige Werte im Zentrum
- Symmetrische Anordnung
- Klare Struktur

**Anwendung**: Übersichtliche, strukturierte Angebote

### Strategie 5: Diagonal-Flow (Firma 5)

**Beschreibung**: Diagonaler Lesefluss von links oben nach rechts unten.

**Charakteristiken**:
- Elemente folgen diagonaler Linie
- Wichtige Werte entlang Diagonale
- Dynamischer Fluss
- Natürliche Leserichtung

**Anwendung**: Dynamische, fließende Layouts

### Strategie 6: Sidebar-Layout (Firma 6)

**Beschreibung**: Zweispalten-Layout mit klarer Trennung.

**Charakteristiken**:
- Hauptinfo in linker Spalte
- Wichtige Werte in rechter Spalte
- Klare vertikale Trennung
- Strukturierte Präsentation

**Anwendung**: Informationsreiche Angebote mit klarer Struktur

## Visualisierung

Das System erstellt verschiedene Visualisierungen zur Überprüfung der Optimierungen:

### Overlay-Bild

Zeigt alte (rot) und neue (grün) Positionen überlagert.

```bash
python -m multi_pdf_positioning.cli --firma 1 --seite 1 --visualize --viz-type overlay
```

**Ausgabe**: `visualizations/f1_s1_overlay_TIMESTAMP.png`

### Vergleichsansicht

Zeigt alte und neue Positionen nebeneinander.

```bash
python -m multi_pdf_positioning.cli --firma 1 --seite 1 --visualize --viz-type comparison
```

**Ausgabe**: `visualizations/f1_s1_comparison_TIMESTAMP.png`

### Bewegungsvisualisierung

Zeigt Bewegungspfeile von alten zu neuen Positionen.

```bash
python -m multi_pdf_positioning.cli --firma 1 --seite 1 --visualize --viz-type movement
```

**Ausgabe**: `visualizations/f1_s1_movement_TIMESTAMP.png`

### Kollisions-Visualisierung

Hebt Kollisionen zwischen Elementen hervor.

```bash
python -m multi_pdf_positioning.cli --firma 1 --seite 1 --visualize --viz-type collision
```

**Ausgabe**: `visualizations/f1_s1_collision_TIMESTAMP.png`

## Statistiken

Das System generiert detaillierte Statistiken über die Optimierungen:

### Statistik-Bericht

```bash
python -m multi_pdf_positioning.cli --all --statistics --stats-output stats.txt
```

**Inhalt**:
- Gesamtstatistiken (Kombinationen, Elemente, durchschnittliche Bewegung)
- Strategie-Verteilung
- Top 10 Positions-Änderungen
- Strategie-Performance
- Kollisions-Auflösung
- Validierungs-Ergebnisse

### JSON-Export

```bash
python -m multi_pdf_positioning.cli --all --statistics --stats-format json --stats-output stats.json
```

**Struktur**:
```json
{
  "timestamp": "2025-01-10T14:30:00",
  "total_combinations": 48,
  "total_elements": 1200,
  "avg_distance_moved": 45.3,
  "strategies_used": {
    "header-focused": 8,
    "center-prominent": 8,
    ...
  },
  "strategy_statistics": [...],
  "position_changes": [...]
}
```

### CSV-Export

```bash
python -m multi_pdf_positioning.cli --all --statistics --stats-format csv --stats-output stats.csv
```

**Spalten**:
- Strategy
- Firma
- Seite
- Elements
- Avg Distance Moved
- Max Distance Moved
- Min Distance Moved
- Avg X Change
- Avg Y Change
- Collisions Before
- Collisions After
- Validation Errors
- Validation Warnings

## Fehlerbehebung

### Problem: PDF-Dateien nicht gefunden

**Symptom**: `FileNotFoundError: PDF file not found`

**Lösung**:
1. Prüfen Sie den PDF-Pfad in `config.py`
2. Stellen Sie sicher, dass alle PDF-Dateien vorhanden sind
3. Überprüfen Sie die Dateinamen-Konvention: `multi_nt_[01-08]_f[1-6].pdf`

### Problem: YML-Parsing-Fehler

**Symptom**: `ValueError: Invalid YML format`

**Lösung**:
1. Prüfen Sie die YML-Datei auf Syntaxfehler
2. Stellen Sie sicher, dass alle erforderlichen Felder vorhanden sind
3. Verwenden Sie `--validate` um spezifische Fehler zu identifizieren

### Problem: Validierungs-Fehler

**Symptom**: `Validation failed: X errors`

**Lösung**:
1. Generieren Sie einen Validierungsbericht: `--validation-report report.txt`
2. Prüfen Sie die spezifischen Fehler im Bericht
3. Häufige Probleme:
   - Positionen außerhalb der PDF-Grenzen
   - Überlappende Elemente
   - Zu kleine Abstände

### Problem: Kollisionen nach Optimierung

**Symptom**: `Collisions detected after optimization`

**Lösung**:
1. Erstellen Sie eine Kollisions-Visualisierung: `--visualize --viz-type collision`
2. Prüfen Sie die betroffenen Elemente
3. Passen Sie ggf. die Positionierungs-Strategie an

### Problem: Backup-Wiederherstellung schlägt fehl

**Symptom**: `Backup not found or corrupted`

**Lösung**:
1. Listen Sie verfügbare Backups auf: `--list-backups`
2. Prüfen Sie die Backup-ID
3. Stellen Sie sicher, dass das Backup-Verzeichnis existiert

### Problem: Visualisierung schlägt fehl

**Symptom**: `PIL.Image error` oder `Font not found`

**Lösung**:
1. Installieren Sie Pillow: `pip install Pillow`
2. Für bessere Schriftarten: Installieren Sie TrueType-Fonts
3. Das System verwendet automatisch eine Fallback-Schriftart

## Erweiterte Nutzung

### Python-API verwenden

```python
from multi_pdf_positioning.main_workflow import MainWorkflow

# Workflow erstellen
workflow = MainWorkflow(
    pdf_dir="path/to/pdfs",
    yml_dir="path/to/ymls",
    create_backup=True,
    validate_output=True
)

# Workflow ausführen
summary = workflow.run(firmen=[1, 2], seiten=[1, 2, 3])

# Ergebnisse prüfen
print(f"Successful: {summary.successful}/{summary.total_combinations}")
```

### Eigene Positionierungs-Strategie

```python
from multi_pdf_positioning.positioning_strategies import register_strategy

@register_strategy("custom-strategy")
def custom_strategy(elements, pdf_analysis):
    # Ihre Logik hier
    positions = []
    for element in elements:
        # Berechnen Sie Position
        position = (x1, y1, x2, y2)
        positions.append(position)
    return positions
```

### Batch-Verarbeitung mit Python

```python
from multi_pdf_positioning.batch_processor import BatchProcessor

processor = BatchProcessor()
results = processor.process_all(
    firmen=[1, 2, 3, 4, 5, 6],
    seiten=[1, 2, 3, 4, 5, 6, 7, 8],
    parallel=True,
    max_workers=4
)
```

## Support

Bei Fragen oder Problemen:

1. Prüfen Sie dieses Handbuch
2. Konsultieren Sie die API-Dokumentation
3. Erstellen Sie ein Issue im Repository
4. Kontaktieren Sie das Entwicklungsteam

## Changelog

### Version 1.0.0 (2025-01-10)

- Initiale Version
- 6 Positionierungs-Strategien
- Vollständige Validierung
- Visualisierungs-Tools
- Statistik-Generierung
- CLI-Interface
- Backup & Restore

---

**Letzte Aktualisierung**: 2025-01-10
**Version**: 1.0.0
