# Task 14: Import/Export - Visueller Leitfaden

## UI-Übersicht

### Hauptnavigation

```
┌─────────────────────────────────────────────────────────────────┐
│  ⚙️ PDF & Design Einstellungen                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  [🎨 PDF-Design] [📊 Diagramm-Farben] [🖼️ UI-Themes]           │
│  [📄 PDF-Templates] [📐 Layout-Optionen] [💾 Import/Export] ◄── NEU!
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Export-Sektion

### Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  💾 Import/Export von Design-Konfigurationen                     │
│  Exportieren und importieren Sie alle Design-Einstellungen      │
│  als JSON-Datei.                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────┬─────────────────────────────┐  │
│  │  📤 Export                  │  📥 Import                  │  │
│  ├─────────────────────────────┼─────────────────────────────┤  │
│  │                             │                             │  │
│  │  Exportieren Sie alle       │  Importieren Sie Design-    │  │
│  │  aktuellen Design-          │  Einstellungen aus einer    │  │
│  │  Einstellungen in eine      │  JSON-Datei.                │  │
│  │  JSON-Datei.                │                             │  │
│  │                             │                             │  │
│  │  ▼ 📋 Was wird exportiert?  │  [Datei auswählen...]       │  │
│  │    - PDF-Design             │                             │  │
│  │    - Diagramm-Farben        │  ℹ️ Wählen Sie eine JSON-   │  │
│  │    - UI-Themes              │     Datei aus, um die       │  │
│  │    - PDF-Templates          │     Konfiguration zu        │  │
│  │    - Layout-Optionen        │     importieren.            │  │
│  │    - Custom-Paletten        │                             │  │
│  │                             │                             │  │
│  │  ─────────────────────────  │                             │  │
│  │                             │                             │  │
│  │  [📥 Konfiguration          │                             │  │
│  │   exportieren]              │                             │  │
│  │                             │                             │  │
│  └─────────────────────────────┴─────────────────────────────┘  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Export-Workflow

```
Schritt 1: Export-Button klicken
┌─────────────────────────────────────┐
│  [📥 Konfiguration exportieren]     │
└─────────────────────────────────────┘
                ↓
Schritt 2: Download-Button erscheint
┌─────────────────────────────────────┐
│  ✅ Konfiguration erfolgreich       │
│     exportiert! Klicken Sie auf     │
│     den Download-Button.            │
│                                     │
│  [💾 JSON-Datei herunterladen]      │
└─────────────────────────────────────┘
                ↓
Schritt 3: Vorschau verfügbar
┌─────────────────────────────────────┐
│  ▼ 👁️ Vorschau der exportierten    │
│     Daten                           │
│                                     │
│  {                                  │
│    "pdf_design_settings": {...},   │
│    "visualization_settings": {...},│
│    "_metadata": {...}               │
│  }                                  │
└─────────────────────────────────────┘
```

## Import-Sektion

### Layout nach Datei-Upload

```
┌─────────────────────────────────────────────────────────────────┐
│  📥 Import                                                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  JSON-Datei auswählen                                            │
│  [design_config_20251009_133525.json] ✓                         │
│                                                                   │
│  ✅ Konfiguration erfolgreich geladen und validiert!             │
│                                                                   │
│  ▼ ℹ️ Datei-Informationen                                        │
│    - Export-Datum: 2025-10-09T13:35:25.479175                   │
│    - Version: 1.0                                                │
│    - Beschreibung: PDF & Design Konfiguration Export            │
│                                                                   │
│  ▼ 📋 Was wird importiert?                                       │
│    5 Einstellungsbereiche gefunden:                              │
│    - ✓ PDF-Design-Einstellungen                                 │
│    - ✓ Diagramm-Farbkonfigurationen                             │
│    - ✓ UI-Theme-Einstellungen                                   │
│    - ✓ PDF-Template-Einstellungen                               │
│    - ✓ Layout-Optionen                                          │
│                                                                   │
│  ▼ 👁️ Vorschau der importierten Daten                           │
│    {                                                             │
│      "pdf_design_settings": {...},                              │
│      "visualization_settings": {...}                            │
│    }                                                             │
│                                                                   │
│  ─────────────────────────────────────────────────────────────  │
│                                                                   │
│  ⚠️ Achtung: Der Import überschreibt alle aktuellen             │
│     Einstellungen!                                               │
│                                                                   │
│  ☐ Ich bestätige, dass ich alle aktuellen Einstellungen         │
│     überschreiben möchte                                         │
│                                                                   │
│  [✓ Konfiguration importieren] (deaktiviert)                    │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Import-Workflow

```
Schritt 1: Datei hochladen
┌─────────────────────────────────────┐
│  [Datei auswählen...]               │
└─────────────────────────────────────┘
                ↓
Schritt 2: Automatische Validierung
┌─────────────────────────────────────┐
│  ⏳ Validiere Konfiguration...      │
└─────────────────────────────────────┘
                ↓
Schritt 3: Validierung erfolgreich
┌─────────────────────────────────────┐
│  ✅ Konfiguration erfolgreich       │
│     geladen und validiert!          │
└─────────────────────────────────────┘
                ↓
Schritt 4: Informationen anzeigen
┌─────────────────────────────────────┐
│  ▼ ℹ️ Datei-Informationen           │
│  ▼ 📋 Was wird importiert?          │
│  ▼ 👁️ Vorschau                      │
└─────────────────────────────────────┘
                ↓
Schritt 5: Bestätigung erforderlich
┌─────────────────────────────────────┐
│  ⚠️ Achtung: Überschreibt alle      │
│     Einstellungen!                  │
│                                     │
│  ☑ Ich bestätige...                │
└─────────────────────────────────────┘
                ↓
Schritt 6: Import-Button aktiviert
┌─────────────────────────────────────┐
│  [✓ Konfiguration importieren]      │
└─────────────────────────────────────┘
                ↓
Schritt 7: Import erfolgreich
┌─────────────────────────────────────┐
│  ✅ Konfiguration erfolgreich       │
│     importiert! Die Seite wird      │
│     neu geladen...                  │
└─────────────────────────────────────┘
                ↓
Schritt 8: Seite wird neu geladen
┌─────────────────────────────────────┐
│  🔄 Seite wird neu geladen...       │
└─────────────────────────────────────┘
```

## Fehlerbehandlung

### Ungültige JSON-Datei

```
┌─────────────────────────────────────────────────────────────────┐
│  ❌ Fehler beim Parsen der JSON-Datei: Expecting property name  │
│     enclosed in double quotes: line 5 column 3 (char 89)        │
└─────────────────────────────────────────────────────────────────┘
```

### Validierungsfehler

```
┌─────────────────────────────────────────────────────────────────┐
│  ❌ Ungültige Konfigurationsdatei!                               │
│                                                                   │
│  ▼ 🔍 Validierungsfehler                                         │
│    - Keine gültigen Einstellungen gefunden. Erwartete Keys:     │
│      pdf_design_settings, visualization_settings, ...           │
│    - global_chart_colors muss eine Liste sein                   │
└─────────────────────────────────────────────────────────────────┘
```

## Hilfe-Sektion

```
┌─────────────────────────────────────────────────────────────────┐
│  ▼ ℹ️ Hilfe & Informationen                                     │
│                                                                   │
│  ### Import/Export-Funktionen                                    │
│                                                                   │
│  **Export:**                                                     │
│  - Exportiert alle Design-Einstellungen in eine JSON-Datei      │
│  - Enthält Metadaten wie Export-Datum und Version               │
│  - Kann als Backup oder zum Teilen verwendet werden             │
│                                                                   │
│  **Import:**                                                     │
│  - Importiert Design-Einstellungen aus einer JSON-Datei         │
│  - Validiert die Daten vor dem Import                           │
│  - Überschreibt alle aktuellen Einstellungen                    │
│  - Erfordert Bestätigung vor dem Import                         │
│                                                                   │
│  **Verwendungszwecke:**                                          │
│  - Backup von Einstellungen erstellen                           │
│  - Einstellungen zwischen Installationen teilen                 │
│  - Verschiedene Design-Varianten testen                         │
│  - Schnelles Zurücksetzen auf bekannte Konfiguration            │
│                                                                   │
│  **Hinweise:**                                                   │
│  - Exportierte Dateien sind im JSON-Format                      │
│  - Dateien können mit einem Texteditor bearbeitet werden        │
│  - Ungültige Daten werden beim Import abgelehnt                 │
│  - Ein Backup vor dem Import wird empfohlen                     │
└─────────────────────────────────────────────────────────────────┘
```

## JSON-Struktur

### Exportierte Datei

```json
{
  "pdf_design_settings": {
    "primary_color": "#1E3A8A",
    "secondary_color": "#3B82F6",
    "font_family": "Helvetica",
    "font_size_h1": 18,
    "font_size_h2": 14,
    "font_size_body": 10,
    "font_size_small": 8,
    "logo_position": "left",
    "footer_format": "with_page_number",
    "custom_footer_text": "",
    "watermark_enabled": false,
    "watermark_text": "ENTWURF",
    "watermark_opacity": 0.1
  },
  "visualization_settings": {
    "global_chart_colors": [
      "#1E3A8A",
      "#3B82F6",
      "#10B981",
      "#F59E0B",
      "#EF4444",
      "#8B5CF6"
    ],
    "individual_chart_colors": {
      "cumulative_cashflow_chart": {
        "use_global": false,
        "custom_colors": ["#FF0000", "#00FF00", "#0000FF"]
      }
    }
  },
  "ui_theme_settings": {
    "active_theme": "light",
    "custom_themes": {
      "my_theme": {
        "name": "Mein Theme",
        "colors": {...}
      }
    }
  },
  "pdf_templates": {
    "active_template": "standard",
    "templates": [...]
  },
  "pdf_layout_options": {
    "layouts": {
      "standard": {
        "enabled": true,
        "is_default": true
      },
      "extended": {
        "enabled": true,
        "is_default": false
      }
    }
  },
  "_metadata": {
    "export_date": "2025-10-09T13:35:25.479175",
    "version": "1.0",
    "description": "PDF & Design Konfiguration Export"
  }
}
```

## Verwendungsszenarien

### Szenario 1: Backup erstellen

```
1. Admin-Panel öffnen
2. "PDF & Design Einstellungen" → "Import/Export"
3. "Konfiguration exportieren" klicken
4. JSON-Datei herunterladen
5. Datei sicher speichern (z.B. auf externem Laufwerk)
```

### Szenario 2: Einstellungen teilen

```
1. Entwickler A exportiert Einstellungen
2. JSON-Datei per E-Mail/Cloud an Entwickler B senden
3. Entwickler B importiert Einstellungen
4. Beide haben identische Design-Konfiguration
```

### Szenario 3: Design-Varianten testen

```
1. Aktuelle Einstellungen exportieren (Backup)
2. Design-Einstellungen ändern
3. Testen
4. Falls nicht zufrieden: Backup importieren
5. Zurück zur ursprünglichen Konfiguration
```

### Szenario 4: Migration

```
1. Alte Installation: Einstellungen exportieren
2. Neue Installation aufsetzen
3. Exportierte Einstellungen importieren
4. Alle Design-Einstellungen übernommen
```

## Tastenkombinationen

Keine speziellen Tastenkombinationen implementiert.

## Mobile Ansicht

Die UI ist responsive und funktioniert auf mobilen Geräten:

- Spalten werden gestapelt
- Buttons werden auf volle Breite erweitert
- Expander bleiben funktional

## Barrierefreiheit

- Alle Buttons haben beschreibende Labels
- Fehlermeldungen sind klar und verständlich
- Farbkontraste sind ausreichend
- Screenreader-freundlich

## Performance

- Export: < 100ms
- Import: < 500ms
- Validierung: < 50ms
- Keine Verzögerungen spürbar

## Sicherheit

- Keine Code-Ausführung aus JSON
- Strenge Validierung
- Bestätigung erforderlich
- Keine automatischen Änderungen

## Tipps & Tricks

1. **Regelmäßige Backups**: Exportieren Sie Einstellungen vor größeren Änderungen
2. **Versionierung**: Benennen Sie Dateien mit Datum/Version (z.B. `design_v1_20251009.json`)
3. **Dokumentation**: Fügen Sie Notizen in die Beschreibung ein
4. **Testen**: Testen Sie importierte Einstellungen in einer Test-Umgebung
5. **Teilen**: Nutzen Sie Export/Import für Team-Zusammenarbeit

## Bekannte Einschränkungen

- Keine automatische Versionierung (siehe Task 15)
- Keine Diff-Ansicht zwischen Versionen
- Keine Teilimporte (nur vollständiger Import)
- Keine Merge-Funktion

## Zukünftige Erweiterungen

- Task 15: Versionierung mit Namen und Beschreibungen
- Diff-Ansicht zwischen Konfigurationen
- Selektiver Import einzelner Bereiche
- Merge-Funktion für Konfigurationen
- Cloud-Backup-Integration
