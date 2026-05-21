# PV-Unterkonstruktions-Verwaltungssystem

Umfassendes Datenbank- und Berechnungssystem für PV-Montagekomponenten mit Admin-UI, dynamischen Berechnungen und Solar-Calculator-Integration.

## 📋 Übersicht

Das System besteht aus mehreren Modulen:

1. **`pv_mounting_database.py`** - SQLite-Backend mit CRUD-Operationen
2. **`admin_pv_mounting_ui.py`** - Streamlit Admin-Interface
3. **`pv_mounting_calculations.py`** - Berechnungs-Engine für Komponenten
4. **`seed_pv_database.py`** - Datenbank-Initialisierung mit Beispieldaten

## 🚀 Features

### ✅ Implementiert

- **Datenbank-Backend**
  - SQLite-Datenbank mit vollständigem Schema
  - CRUD-Operationen (Create, Read, Update, Delete)
  - Soft-Delete für sichere Datenverwaltung
  - JSON-Support für technische Spezifikationen
  - PDF-Bytes-Speicherung für Datenblätter
  - Volltextsuche über multiple Felder
  - Statistiken und Aggregationen

- **Admin-UI (Streamlit)**
  - Dashboard mit Echtzeit-Statistiken
  - Komponenten-Verwaltung mit Tabellen-Ansicht
  - Erweiterte Such- und Filterfunktionen
  - Formular zum Erstellen neuer Komponenten
  - Bearbeitungs-Interface mit PDF-Upload
  - CSV/Excel Import & Export
  - Responsive Design mit Sidebar-Navigation

- **Berechnungs-Engine**
  - Dynamische Berechnung von Dachhaken (basierend auf Dachtyp, Schneelast, Sparrenabstand)
  - Schienenlängen-Kalkulation (Portrait/Landscape, Flachdach-MiniRails)
  - End- und Mittelklemmen-Berechnung
  - Schrauben-Anzahl (abhängig von Dachtyp)
  - Kabellängen (4mm²/6mm², Rot/Schwarz)
  - Ballast-Kalkulation für Flachdächer (Windlastzonen)
  - Preset-Konfigurationen für schnelle Berechnungen

- **Datenbank-Content**
  - 25+ vordefinierte Komponenten von K2 Systems, Würth, Renusol, Schletter
  - Alle Dachtypen abgedeckt (Ziegel, Beton, Schiefer, Biber, Trapez, Flach)
  - Realistische Preise (Netto-Händlerpreise)
  - Technische Spezifikationen im JSON-Format

## 📦 Installation

### Voraussetzungen

```bash
python >= 3.10
streamlit >= 1.30.0
pandas >= 2.0.0
openpyxl >= 3.1.0
```

### Setup

1. Datenbank initialisieren und seeden:

```bash
python seed_pv_database.py
```

2. Admin-UI starten:

```bash
streamlit run admin_pv_mounting_ui.py
```

## 🎯 Verwendung

### Admin-UI

Die Streamlit-App bietet folgende Bereiche:

#### 📊 Dashboard

- Übersicht über alle Komponenten
- Statistiken nach Hersteller, Kategorie, Dachtyp
- Preisstatistiken (Min, Max, Durchschnitt)

#### 📋 Komponenten verwalten

- Tabellen-Ansicht mit Filterung
- Suche nach Produktname, Hersteller, Artikelnummer
- Filter nach Hersteller, Dachtyp, Kategorie
- Bearbeiten und Löschen von Komponenten

#### ➕ Neue Komponente

- Vollständiges Formular mit allen Feldern
- Pflichtfelder: Hersteller, Produktname, Kategorie, Dachtyp, Preis
- Optionale Felder: Material, Abmessungen, Gewicht, Garantie
- JSON-Editor für technische Spezifikationen
- PDF-Upload für Datenblätter

#### 📥 📤 Import/Export

- CSV-Import mit Fehlerbehandlung
- Excel-Import (.xlsx, .xls)
- CSV/Excel-Export mit Filtern
- Download-Button für exportierte Dateien

### Berechnungs-Engine

```python
from pv_mounting_calculations import (
    ModuleConfiguration,
    RoofConfiguration,
    calculate_mounting_system
)

# Modul-Konfiguration
module_config = ModuleConfiguration(
    count=20,
    orientation="Portrait",
    rows=2
)

# Dach-Konfiguration
roof_config = RoofConfiguration(
    roof_type="Ziegeldach",
    pitch_degrees=35.0,
    rafter_spacing_mm=800.0,
    snow_load_zone=2,
    wind_load_zone=2
)

# Berechnung durchführen
result = calculate_mounting_system(
    module_config=module_config,
    roof_config=roof_config,
    manufacturer="K2 Systems",
    distance_to_inverter_m=15.0
)

# Ergebnis ausgeben
print(f"Gesamtpreis: {result.total_price_netto:.2f} €")
print(f"Komponenten: {result.total_components_count}")

for comp in result.components:
    print(f"{comp.product_name}: {comp.quantity} {comp.unit} × {comp.price_per_unit} € = {comp.total_price} €")
```

### Datenbank-API

```python
from pv_mounting_database import (
    create_component,
    read_components,
    update_component,
    delete_component
)

# Neue Komponente erstellen
component_id = create_component({
    'manufacturer': 'K2 Systems',
    'product_name': 'Test Dachhaken',
    'category': 'Dachhaken',
    'roof_type': 'Ziegeldach',
    'price_netto': 9.5,
    'unit': 'Stk',
    'specifications': {'test': 'value'}
})

# Komponenten lesen mit Filter
components = read_components(filters={
    'manufacturer': 'K2 Systems',
    'roof_type': 'Ziegeldach'
})

# Komponente aktualisieren
update_component(component_id, {
    'price_netto': 10.0
})

# Komponente löschen (Soft-Delete)
delete_component(component_id, soft_delete=True)
```

## 📊 Datenbank-Schema

### `mounting_components` Tabelle

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| id | INTEGER | Primary Key (auto-increment) |
| manufacturer | TEXT | Hersteller (K2, Würth, etc.) |
| product_name | TEXT | Produktname |
| article_number | TEXT | Artikelnummer |
| category | TEXT | Kategorie (Dachhaken, Schiene, etc.) |
| roof_type | TEXT | Dachtyp (Ziegel, Flach, etc.) |
| material | TEXT | Material (Alu, Edelstahl, etc.) |
| dimensions | TEXT | Abmessungen |
| weight_kg | REAL | Gewicht in kg |
| price_netto | REAL | Netto-Preis |
| unit | TEXT | Einheit (Stk, m, kg, etc.) |
| quantity_per_module | REAL | Durchschn. Menge pro Modul |
| compatibility | TEXT | Kompatibilitätshinweise |
| warranty_years | INTEGER | Garantie in Jahren |
| specifications | TEXT | Techn. Spezifikationen (JSON) |
| notes | TEXT | Notizen |
| pdf_bytes | BLOB | PDF-Datenblatt |
| pdf_filename | TEXT | PDF-Dateiname |
| created_at | TIMESTAMP | Erstellungsdatum |
| updated_at | TIMESTAMP | Aktualisierungsdatum |
| is_active | INTEGER | Aktiv-Status (Soft-Delete) |

## 🧮 Berechnungslogik

### Dachhaken

```
Basis: 2 Dachhaken pro Modul

Anpassungen:
- Betondach ODER Schneelastzone ≥3: 3 Dachhaken/Modul
- Sparrenabstand >900mm: +1 Dachhaken/Modul
- Flachdach: 0 Dachhaken (Ballastierung)
```

### Schienen

```
Portrait-Ausrichtung:
  Länge/Reihe = Module/Reihe × Modulbreite × 1,10 (Verschnitt)
  Gesamt = Länge/Reihe × Reihen × 2 Schienen

Flachdach:
  4 MiniRails pro Modul (statt langen Schienen)
```

### Klemmen

```
Endklemmen: 2 × 2 pro Reihe (2 Schienen × 2 Enden)
Mittelklemmen: (Module/Reihe - 1) × 2 × 2 pro Reihe
```

### Schrauben

```
Standard: 2 Schrauben pro Dachhaken
Sandwich/Biberschwanz: 3 Schrauben pro Dachhaken
```

### Kabel

```
Pro Farbe (Rot/Schwarz):
  Module × 1m + Distanz_WR + 30m Reserve
```

### Ballast (Flachdach)

```
Windlastzone 1: 15 kg/Modul
Windlastzone 2: 20 kg/Modul
Windlastzone 3: 25 kg/Modul
Windlastzone 4: 30 kg/Modul
```

## 🗂️ Dateistruktur

```
Bokuk2 - Kopie/
├── pv_mounting_database.py          # Backend-Datenbank
├── admin_pv_mounting_ui.py          # Streamlit Admin-UI
├── pv_mounting_calculations.py      # Berechnungs-Engine
├── seed_pv_database.py              # Datenbank-Seed-Script
├── PV_MOUNTING_SYSTEM_README.md     # Diese Datei
├── data/
│   └── pv_mounting_components.db    # SQLite-Datenbank (erstellt beim ersten Start)
└── unterkonstruktion_pv/
    └── Komponenten für PV-Montagesysteme je Dachtyp.md
```

## 🔧 Konfiguration

### Konstanten anpassen

In `admin_pv_mounting_ui.py`:

```python
MANUFACTURERS = ["K2 Systems", "Würth", "Prefa", "Schletter", "Renusol"]
ROOF_TYPES = ["Ziegeldach", "Betondach", "Schieferdach", ...]
CATEGORIES = ["Dachhaken", "Montageschiene", ...]
```

### Datenbank-Pfad ändern

In `pv_mounting_database.py`:

```python
DB_PATH = Path(__file__).parent / "data" / "pv_mounting_components.db"
```

## 📖 Beispiele

### CSV-Import

Erstelle `komponenten.csv`:

```csv
manufacturer,product_name,category,roof_type,price_netto,unit,quantity_per_module
K2 Systems,Test Haken,Dachhaken,Ziegeldach,9.5,Stk,2.0
Würth,Test Schiene,Montageschiene,Ziegeldach,5.0,m,1.2
```

Dann in der Admin-UI: **Import/Export** → CSV auswählen → Hochladen

### Preset-Konfigurationen verwenden

```python
from pv_mounting_calculations import get_preset_configurations, calculate_mounting_system

presets = get_preset_configurations()

# Klein-Anlage verwenden
klein = presets["Klein (10 Module, Ziegeldach)"]

result = calculate_mounting_system(
    module_config=klein["module_config"],
    roof_config=klein["roof_config"],
    manufacturer="K2 Systems"
)
```

## 🐛 Fehlerbehebung

### Datenbank wird nicht erstellt

```bash
# Manuelle Initialisierung
python -c "from pv_mounting_database import initialize_database; initialize_database()"
```

### Streamlit startet nicht

```bash
# Port ändern
streamlit run admin_pv_mounting_ui.py --server.port 8502
```

### Import-Fehler bei CSV

- Prüfe, ob alle Pflichtfelder vorhanden sind
- Encoding auf UTF-8 setzen
- Spaltentrennzeichen: Komma (,)

## 🎯 TODO / Roadmap

- [x] Datenbank-Backend mit CRUD
- [x] Admin-UI mit Streamlit
- [x] Berechnungs-Engine
- [x] CSV/Excel Import/Export
- [x] PDF-Anhänge
- [ ] Solar-Calculator-Integration
- [ ] PDF-Export für Angebote
- [ ] Integration in gui.py
- [ ] Automatische Komponentenauswahl
- [ ] Multi-Hersteller-Vergleich
- [ ] Preiskalkulation mit Aufschlag

## 📝 Changelog

### Version 1.0.0 (2025-11-06)

- ✨ Initiale Implementierung
- ✅ Vollständiges CRUD-Backend
- ✅ Streamlit Admin-UI
- ✅ Dynamische Berechnungen
- ✅ 25+ vordefinierte Komponenten
- ✅ CSV/Excel Import/Export
- ✅ PDF-Anhang-Support

## 👥 Autoren

- **Bokuk2 System** - Entwicklung & Implementierung

## 📄 Lizenz

Internes Projekt - Alle Rechte vorbehalten

---

**Hinweis**: Preise und technische Daten basieren auf Herstellerangaben aus 2025 und dienen als Richtwerte für Kalkulationen.
