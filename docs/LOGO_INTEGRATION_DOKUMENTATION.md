# LOGO_INTEGRATION_DOKUMENTATION.md

# 🎨 Logo-Management und PDF-Integration

## Überblick

Diese Implementierung ermöglicht es, Hersteller-Logos in der Produktverwaltung zu verwalten und diese automatisch in PDF-Seite 4 basierend auf den ausgewählten Produkten einzubauen.

## 📁 Neue Dateien

### Kern-Module

- **`admin_logo_management_ui.py`** - Streamlit UI für Logo-Verwaltung (CRUD)
- **`admin_logo_positions_ui.py`** - Admin-Interface für Logo-Positionierung
- **`pdf_logo_integration.py`** - PDF-Integration und Logo-Rendering
- **`migrate_logo_database.py`** - Datenbank-Migration für neue Features
- **`test_logo_integration.py`** - Vollständige Test-Suite

### Erweiterte Module

- **`brand_logo_db.py`** - Erweitert um Positionierung und erweiterte Funktionen
- **`admin_panel.py`** - Neuer "Logo-Verwaltung" Tab hinzugefügt
- **`pdf_template_engine/placeholders.py`** - Logo-Platzhalter integriert
- **`pdf_template_engine/dynamic_overlay.py`** - Logo-Rendering für Seite 4
- **`coords/seite4.yml`** - Logo-Platzhalter hinzugefügt

## 🚀 Features

### 1. Logo-Verwaltung im Admin-Panel

- **Upload**: Unterstützt PNG, JPG, JPEG, SVG, GIF, WEBP (max. 5MB)
- **CRUD**: Vollständige Verwaltung (Create, Read, Update, Delete)
- **Vorschau**: Live-Vorschau der hochgeladenen Logos
- **Hersteller-Integration**: Automatische Erkennung von Herstellern aus der Produktdatenbank

### 2. Positions-Management

- **Koordinaten-Editor**: Präzise Positionierung auf PDF-Seite 4
- **Standard-Positionen**: Vorkonfigurierte Positionen für Module, WR, Speicher
- **Live-Vorschau**: Koordinaten-Übersicht und Export-Funktion
- **Admin-Settings**: Persistente Speicherung der Positionen

### 3. PDF-Integration

- **Dynamisches Rendering**: Logos werden basierend auf gewählten Produkten eingebaut
- **Proportionale Skalierung**: Automatische Anpassung der Logo-Größe
- **Fallback-Handling**: Graceful degradation wenn Logos fehlen
- **Multi-Format-Support**: PNG, JPG optimal unterstützt

## 📊 Datenbank-Schema

### Tabelle: `brand_logos`

```sql
CREATE TABLE brand_logos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    brand_name TEXT NOT NULL UNIQUE,          -- Hersteller-Name
    logo_base64 TEXT,                         -- Logo als Base64
    logo_format TEXT,                         -- Bildformat (PNG, JPG, etc.)
    file_size_bytes INTEGER DEFAULT 0,        -- Dateigröße
    logo_position_x REAL DEFAULT 0,           -- X-Position auf PDF
    logo_position_y REAL DEFAULT 0,           -- Y-Position auf PDF  
    logo_width REAL DEFAULT 100,              -- Logo-Breite
    logo_height REAL DEFAULT 50,              -- Logo-Höhe
    is_active INTEGER DEFAULT 1,              -- Aktiv/Inaktiv Status
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔧 Konfiguration

### Logo-Positionen (Standard)

```python
DEFAULT_LOGO_POSITIONS = {
    "modul": {
        "x": 520, "y": 180, 
        "width": 60, "height": 30
    },
    "wechselrichter": {
        "x": 520, "y": 370,
        "width": 60, "height": 30  
    },
    "batteriespeicher": {
        "x": 520, "y": 560,
        "width": 60, "height": 30
    }
}
```

### Admin-Settings

- **`pdf_logo_positions`** - Gespeicherte Logo-Positionen
- Überschreibt Standard-Positionen wenn konfiguriert

## 🎯 Workflow

### 1. Logo hochladen

1. Admin-Panel → Logo-Verwaltung → Upload
2. Hersteller auswählen oder neu eingeben
3. Logo-Datei auswählen (PNG, JPG empfohlen)
4. Upload und automatische Validierung

### 2. Positionen konfigurieren

1. Admin-Panel → Logo-Verwaltung → Positionen
2. X/Y-Koordinaten für jede Kategorie einstellen
3. Breite/Höhe der Logo-Bereiche definieren
4. Speichern und testen mit PDF-Generierung

### 3. PDF-Generierung

1. Produkte in der App auswählen
2. PDF generieren (Seite 4)
3. Logos werden automatisch basierend auf Herstellern eingebaut
4. Fallback-Text wenn Logo nicht verfügbar

## 🔧 API-Referenz

### Brand Logo DB

```python
# Logo hinzufügen/aktualisieren
add_brand_logo(brand_name, logo_base64, logo_format, 
               file_size_bytes, position_x, position_y, width, height)

# Logo abrufen
get_brand_logo(brand_name) -> Dict

# Multiple Logos abrufen  
get_logos_for_brands(brand_names) -> Dict

# Logo-Position aktualisieren
update_logo_position(brand_name, position_x, position_y, width, height)

# Logo deaktivieren
deactivate_brand_logo(brand_name)
```

### PDF Integration

```python
# Hersteller aus Projektdaten extrahieren
extract_brands_from_project_data(project_data) -> Dict

# Logo-Positionen mit Admin-Settings laden
get_logo_positions_with_admin_settings() -> Dict

# Logos auf Canvas zeichnen
draw_brand_logos_on_canvas(canvas, project_data)
```

## 🧪 Testing

### Test ausführen

```bash
cd /path/to/project
python test_logo_integration.py
```

### Test-Abdeckung

- ✅ Datenbank-CRUD-Operationen
- ✅ PDF-Logo-Integration
- ✅ Platzhalter-System
- ✅ Koordinaten-Datei-Updates

### Migration ausführen

```bash
python migrate_logo_database.py
```

## 📍 Koordinatensystem

### PDF-Koordinaten (A4, 595x842 Punkte)

- **Ursprung**: Unten links (0,0)
- **X-Achse**: 0 (links) bis 595 (rechts)  
- **Y-Achse**: 0 (unten) bis 842 (oben)

### Standard-Positionen Seite 4

- **PV-Module**: X=520, Y=180 (rechts neben Modul-Text)
- **Wechselrichter**: X=520, Y=370 (rechts neben WR-Text)
- **Batteriespeicher**: X=520, Y=560 (rechts neben Speicher-Text)

## ⚠️ Wichtige Hinweise

### Bildformate

- **Empfohlen**: PNG (mit Transparenz), JPG
- **Unterstützt**: WEBP, GIF  
- **Eingeschränkt**: SVG (wird übersprungen)
- **Max. Größe**: 5MB pro Datei

### Performance

- Logos werden als Base64 in der Datenbank gespeichert
- Automatische Größen-Optimierung beim Rendering
- Lazy Loading in der Admin-UI

### Fallback-Verhalten

- Fehlende Logos werden übersprungen (kein Error)
- Ungültige Bildformate werden ignoriert
- Standard-Positionen wenn Admin-Settings fehlen

## 🔄 Updates und Wartung

### Schema-Änderungen

- Migration-Skript verwenden: `migrate_logo_database.py`
- Backup der Datenbank vor Änderungen
- Test-Suite nach Updates ausführen

### Logo-Updates

- Bestehende Logos können überschrieben werden
- Version-Historie wird nicht gespeichert
- Manuelle Backups bei wichtigen Logos empfohlen

## 📞 Support

Bei Problemen oder Fragen:

1. Test-Suite ausführen: `python test_logo_integration.py`
2. Migrations-Status prüfen: `python migrate_logo_database.py`
3. Log-Ausgaben in der Konsole überprüfen
4. Admin-Panel → Logo-Verwaltung → Statistiken für Übersicht

---

**Status**: ✅ Produktionsbereit  
**Version**: 1.0  
**Letzte Aktualisierung**: 2025-01-27
