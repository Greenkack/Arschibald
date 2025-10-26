# Task 15: Versionierung - Visueller Leitfaden

## UI-Übersicht

### Tab-Navigation

```
┌─────────────────────────────────────────────────────────────────┐
│  ⚙️ PDF & Design Einstellungen                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  [🎨 PDF-Design] [📊 Diagramm-Farben] [🖼️ UI-Themes]           │
│  [📄 PDF-Templates] [📐 Layout-Optionen] [💾 Import/Export]    │
│  [📦 Versionierung] ← NEU                                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Version Speichern (Task 15.1)

### UI-Layout

```
┌─────────────────────────────────────────────────────────────────┐
│  📦 Versionsverwaltung                                          │
│  Speichern und verwalten Sie verschiedene Versionen            │
│  Ihrer Design-Konfigurationen.                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  💾 Neue Version speichern                                      │
│  Erstellen Sie einen Snapshot aller aktuellen Design-           │
│  Einstellungen.                                                  │
│                                                                  │
│  ┌────────────────────────────────┬──────────────────────┐     │
│  │ Versionsname                   │                      │     │
│  │ [z.B. Corporate Design v1.0  ] │ [💾 Version speichern]│     │
│  └────────────────────────────────┴──────────────────────┘     │
│                                                                  │
│  Beschreibung (optional)                                        │
│  ┌──────────────────────────────────────────────────────┐     │
│  │ Beschreiben Sie die Änderungen in dieser Version...  │     │
│  │                                                       │     │
│  └──────────────────────────────────────────────────────┘     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Workflow

```
1. Versionsname eingeben
   ↓
2. Optional: Beschreibung hinzufügen
   ↓
3. Klick auf "Version speichern"
   ↓
4. System erstellt Snapshot
   ├─ pdf_design_settings
   ├─ visualization_settings
   ├─ ui_theme_settings
   ├─ pdf_templates
   ├─ pdf_layout_options
   └─ custom_color_palettes
   ↓
5. Speicherung mit Metadaten
   ├─ name
   ├─ created_at (Timestamp)
   └─ description
   ↓
6. ✅ Erfolgsbestätigung
```

### Validierung

```
┌─────────────────────────────────────────────────────────────────┐
│  Versionsname: [                                              ] │
│                                                                  │
│  ⚠️ Validierung:                                                │
│  • Name darf nicht leer sein                                    │
│  • Name muss eindeutig sein                                     │
│                                                                  │
│  ❌ Fehler bei doppeltem Namen:                                 │
│  "⚠️ Version 'Corporate v1.0' existiert bereits.               │
│   Bitte wählen Sie einen anderen Namen."                        │
└─────────────────────────────────────────────────────────────────┘
```

## Version Laden (Task 15.2)

### Versions-Liste

```
┌─────────────────────────────────────────────────────────────────┐
│  📚 Gespeicherte Versionen                                      │
│  3 Version(en) verfügbar:                                       │
│                                                                  │
│  ▼ 📦 Corporate Design v1.0                                     │
│  ┌─────────────────────────────────────────────────────────────┤
│  │ Erstellt am: 09.01.2025 14:30                               │
│  │ Beschreibung: Initiales Corporate Design                    │
│  │                                                              │
│  │ Enthaltene Einstellungen:                                   │
│  │ - ✓ PDF-Design-Einstellungen                                │
│  │ - ✓ Diagramm-Farbkonfigurationen                            │
│  │ - ✓ UI-Theme-Einstellungen                                  │
│  │ - ✓ PDF-Template-Einstellungen                              │
│  │ - ✓ Layout-Optionen                                         │
│  │                                                              │
│  │ [📥 Version laden]  [🗑️ Löschen]                           │
│  └─────────────────────────────────────────────────────────────┘
│                                                                  │
│  ▶ 📦 Summer Campaign v2.0                                      │
│  ▶ 📦 Winter Theme v1.5                                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Bestätigungs-Dialog (Laden)

```
┌─────────────────────────────────────────────────────────────────┐
│  ⚠️ Bestätigung erforderlich                                    │
│                                                                  │
│  Möchten Sie wirklich die Version 'Corporate Design v1.0'      │
│  laden?                                                          │
│                                                                  │
│  ⚠️ Alle aktuellen Einstellungen werden überschrieben!         │
│                                                                  │
│  [✓ Ja, laden]  [✗ Abbrechen]                                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Workflow (Laden)

```
1. Expander einer Version öffnen
   ↓
2. Metadaten überprüfen
   ├─ Erstellungsdatum
   ├─ Beschreibung
   └─ Enthaltene Einstellungen
   ↓
3. Klick auf "Version laden"
   ↓
4. Bestätigungs-Dialog erscheint
   ⚠️ Warnung vor Überschreiben
   ↓
5. Benutzer bestätigt oder bricht ab
   ↓
6. Bei Bestätigung:
   ├─ Alle Einstellungen wiederherstellen
   ├─ Datenbank aktualisieren
   └─ UI neu laden
   ↓
7. ✅ Erfolgsbestätigung
   "Version 'Corporate Design v1.0' erfolgreich geladen!"
```

## Version Löschen (Task 15.3)

### Bestätigungs-Dialog (Löschen)

```
┌─────────────────────────────────────────────────────────────────┐
│  ⚠️ Bestätigung erforderlich                                    │
│                                                                  │
│  Möchten Sie wirklich die Version 'Corporate Design v1.0'      │
│  löschen?                                                        │
│                                                                  │
│  ⚠️ Diese Aktion kann nicht rückgängig gemacht werden!         │
│                                                                  │
│  [✓ Ja, löschen]  [✗ Abbrechen]                                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Workflow (Löschen)

```
1. Expander einer Version öffnen
   ↓
2. Klick auf "Löschen"
   ↓
3. Bestätigungs-Dialog erscheint
   ⚠️ Warnung vor permanenter Löschung
   ↓
4. Benutzer bestätigt oder bricht ab
   ↓
5. Bei Bestätigung:
   ├─ Version aus Datenbank entfernen
   ├─ Versions-Dictionary aktualisieren
   └─ UI neu laden
   ↓
6. ✅ Erfolgsbestätigung
   "Version 'Corporate Design v1.0' erfolgreich gelöscht!"
```

## Hilfe-Sektion

```
┌─────────────────────────────────────────────────────────────────┐
│  ▼ ℹ️ Hilfe zur Versionsverwaltung                             │
│  ┌─────────────────────────────────────────────────────────────┤
│  │ Wie funktioniert die Versionsverwaltung?                    │
│  │                                                              │
│  │ Version speichern:                                          │
│  │ • Erstellt einen Snapshot aller aktuellen Design-           │
│  │   Einstellungen                                              │
│  │ • Geben Sie einen eindeutigen Namen ein                     │
│  │ • Optional können Sie eine Beschreibung hinzufügen          │
│  │                                                              │
│  │ Version laden:                                              │
│  │ • Stellt alle Einstellungen einer gespeicherten Version     │
│  │   wieder her                                                 │
│  │ • ⚠️ Alle aktuellen Einstellungen werden überschrieben     │
│  │ • Eine Bestätigung ist erforderlich                         │
│  │                                                              │
│  │ Version löschen:                                            │
│  │ • Löscht eine gespeicherte Version permanent                │
│  │ • Diese Aktion kann nicht rückgängig gemacht werden         │
│  │ • Eine Bestätigung ist erforderlich                         │
│  │                                                              │
│  │ Was wird gespeichert?                                       │
│  │ • PDF-Design-Einstellungen                                  │
│  │ • Diagramm-Farbkonfigurationen                              │
│  │ • UI-Theme-Einstellungen                                    │
│  │ • PDF-Template-Einstellungen                                │
│  │ • Layout-Optionen                                           │
│  │                                                              │
│  │ Best Practices:                                             │
│  │ • Speichern Sie regelmäßig Versionen vor größeren           │
│  │   Änderungen                                                 │
│  │ • Verwenden Sie aussagekräftige Namen                       │
│  │ • Fügen Sie Beschreibungen hinzu                            │
│  │ • Behalten Sie wichtige Versionen als Backup                │
│  └─────────────────────────────────────────────────────────────┘
└─────────────────────────────────────────────────────────────────┘
```

## Datenfluss

### Speichern

```
┌──────────────┐
│   Benutzer   │
└──────┬───────┘
       │ Versionsname + Beschreibung
       ↓
┌──────────────────────────────┐
│  render_version_management() │
└──────┬───────────────────────┘
       │ Snapshot erstellen
       ↓
┌──────────────────────────────┐
│ _create_settings_snapshot()  │
│                              │
│ • load_setting() für jeden   │
│   Einstellungs-Key           │
│ • Sammelt alle Werte         │
└──────┬───────────────────────┘
       │ Snapshot-Dictionary
       ↓
┌──────────────────────────────┐
│  Metadaten hinzufügen        │
│  • name                      │
│  • created_at (Timestamp)    │
│  • description               │
└──────┬───────────────────────┘
       │ Vollständige Version
       ↓
┌──────────────────────────────┐
│  save_setting()              │
│  'design_config_versions'    │
└──────┬───────────────────────┘
       │
       ↓
┌──────────────┐
│  Datenbank   │
└──────────────┘
```

### Laden

```
┌──────────────┐
│   Benutzer   │
└──────┬───────┘
       │ Version auswählen + bestätigen
       ↓
┌──────────────────────────────┐
│  render_version_management() │
└──────┬───────────────────────┘
       │ Version laden
       ↓
┌──────────────────────────────┐
│     _load_version()          │
│                              │
│ • Iteriert durch alle        │
│   Einstellungs-Keys          │
│ • save_setting() für jeden   │
└──────┬───────────────────────┘
       │ Erfolg/Fehler
       ↓
┌──────────────────────────────┐
│  UI neu laden (st.rerun())   │
└──────┬───────────────────────┘
       │
       ↓
┌──────────────┐
│  Datenbank   │
│  (aktualisiert)│
└──────────────┘
```

## Session State Management

### Bestätigungs-Dialoge

```
┌─────────────────────────────────────────────────────────────────┐
│  Session State für Dialoge                                      │
│                                                                  │
│  Laden-Bestätigung:                                             │
│  st.session_state.confirm_load_version = "Version Name"         │
│                                                                  │
│  Löschen-Bestätigung:                                           │
│  st.session_state.confirm_delete_version = "Version Name"       │
│                                                                  │
│  Workflow:                                                       │
│  1. Button-Klick setzt Session State                            │
│  2. st.rerun() lädt UI neu                                      │
│  3. Dialog wird angezeigt                                       │
│  4. Bei Bestätigung: Aktion ausführen + State löschen           │
│  5. Bei Abbruch: State löschen                                  │
│  6. st.rerun() lädt UI neu                                      │
└─────────────────────────────────────────────────────────────────┘
```

## Fehlerbehandlung

### Validierung

```
┌─────────────────────────────────────────────────────────────────┐
│  Eingabe-Validierung                                            │
│                                                                  │
│  Versionsname:                                                  │
│  ✓ Nicht leer                                                   │
│  ✓ Eindeutig                                                    │
│  ✓ Keine Sonderzeichen (optional)                               │
│                                                                  │
│  Fehlerbehandlung:                                              │
│  • Try-Catch für Datenbankoperationen                           │
│  • Benutzerfreundliche Fehlermeldungen                          │
│  • Fallback auf sichere Standardwerte                           │
│  • Logging von Fehlern                                          │
└─────────────────────────────────────────────────────────────────┘
```

### Fehlermeldungen

```
┌─────────────────────────────────────────────────────────────────┐
│  Mögliche Fehlermeldungen                                       │
│                                                                  │
│  ⚠️ "Version 'Name' existiert bereits."                        │
│  → Benutzer muss anderen Namen wählen                           │
│                                                                  │
│  ❌ "Fehler beim Speichern der Version."                        │
│  → Datenbankfehler, Aktion wiederholen                          │
│                                                                  │
│  ❌ "Fehler beim Laden der Version."                            │
│  → Datenbankfehler, Aktion wiederholen                          │
│                                                                  │
│  ❌ "Version nicht gefunden."                                   │
│  → Version wurde zwischenzeitlich gelöscht                      │
│                                                                  │
│  ❌ "Fehler beim Löschen der Version."                          │
│  → Datenbankfehler, Aktion wiederholen                          │
└─────────────────────────────────────────────────────────────────┘
```

## Beispiel-Szenarien

### Szenario 1: Neues Corporate Design

```
1. Administrator erstellt neues Corporate Design
   ├─ Primärfarbe: #1E3A8A
   ├─ Sekundärfarbe: #3B82F6
   └─ Schriftart: Helvetica

2. Speichert als Version "Corporate Design v1.0"
   └─ Beschreibung: "Initiales Corporate Design für Launch 2025"

3. Später: Experimentiert mit neuen Farben
   ├─ Primärfarbe: #FF0000
   └─ Sekundärfarbe: #00FF00

4. Nicht zufrieden → Lädt "Corporate Design v1.0"
   └─ Alle Einstellungen wiederhergestellt

5. ✅ Zurück zum bewährten Design
```

### Szenario 2: Saisonale Designs

```
1. Administrator erstellt "Summer Campaign v1.0"
   ├─ Helle, warme Farben
   └─ Sommerliche Diagrammfarben

2. Speichert Version

3. Erstellt "Winter Theme v1.0"
   ├─ Kühle, dunkle Farben
   └─ Winterliche Diagrammfarben

4. Speichert Version

5. Wechselt zwischen Versionen je nach Saison
   └─ Einfacher Wechsel per Klick
```

### Szenario 3: A/B-Testing

```
1. Administrator erstellt "Design A - Klassisch"
   └─ Konservatives Design

2. Erstellt "Design B - Modern"
   └─ Modernes, mutiges Design

3. Testet beide Designs mit Kunden
   └─ Wechselt zwischen Versionen

4. Entscheidet sich für "Design B"
   └─ Löscht "Design A"

5. ✅ Optimales Design gefunden
```

## Zusammenfassung

Die Versionsverwaltung bietet:

✅ **Einfache Bedienung**

- Intuitive UI mit klaren Workflows
- Bestätigungs-Dialoge für Sicherheit
- Hilfe-Sektion für Unterstützung

✅ **Vollständige Funktionalität**

- Speichern mit Metadaten
- Laden mit Wiederherstellung
- Löschen mit Bestätigung

✅ **Sicherheit**

- Validierung von Eingaben
- Warnungen vor Überschreiben
- Bestätigungen für kritische Aktionen

✅ **Flexibilität**

- Beliebig viele Versionen
- Aussagekräftige Namen und Beschreibungen
- Einfacher Wechsel zwischen Designs
