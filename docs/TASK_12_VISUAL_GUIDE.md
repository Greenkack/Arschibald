# Task 12: PDF-Template-Verwaltung UI - Visueller Leitfaden

## Übersicht

Dieser Leitfaden zeigt die implementierte PDF-Template-Verwaltung UI und ihre Funktionen.

## UI-Struktur

### Hauptansicht: PDF & Design Einstellungen

```
┌─────────────────────────────────────────────────────────────┐
│  ⚙️ PDF & Design Einstellungen                              │
├─────────────────────────────────────────────────────────────┤
│  [🎨 PDF-Design] [📊 Diagramm-Farben] [🖼️ UI-Themes]       │
│  [📄 PDF-Templates] [📐 Layout-Optionen]                    │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ 📄 PDF-Template-Verwaltung                            │ │
│  │                                                        │ │
│  │ Verwalten Sie verschiedene PDF-Templates für          │ │
│  │ unterschiedliche Angebots-Designs.                    │ │
│  │                                                        │ │
│  │ [📋 Template-Auswahl] [➕ Neues Template hinzufügen]  │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Tab 1: Template-Auswahl

### Wenn keine Templates vorhanden

```
┌─────────────────────────────────────────────────────────────┐
│ 📋 Verfügbare Templates                                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ℹ️ Noch keine Templates vorhanden.                         │
│     Fügen Sie ein neues Template im Tab                     │
│     'Neues Template hinzufügen' hinzu.                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Mit vorhandenen Templates

```
┌─────────────────────────────────────────────────────────────┐
│ 📋 Verfügbare Templates                                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ **Wählen Sie ein Template:**                                │
│                                                              │
│ ┌──────────────────────────────────────────────────────┐   │
│ │ Standard-Template                              [▼]   │   │
│ └──────────────────────────────────────────────────────┘   │
│                                                              │
│ ─────────────────────────────────────────────────────────── │
│                                                              │
│ **Template-Details:**                                       │
│                                                              │
│ ┌─────────────────────────┬──────────────────────────────┐ │
│ │ **Name:** Standard-     │ **ID:** `standard_template`  │ │
│ │           Template      │                              │ │
│ │                         │ **Erstellt:** 2025-01-09     │ │
│ │ **Beschreibung:**       │          10:00:00            │ │
│ │ Standard PDF-Template   │                              │ │
│ │ für Angebote           │                              │ │
│ │                         │                              │ │
│ │ **Status:** 🟢 Aktiv    │                              │ │
│ └─────────────────────────┴──────────────────────────────┘ │
│                                                              │
│ ─────────────────────────────────────────────────────────── │
│                                                              │
│ **Dateipfade:**                                             │
│                                                              │
│ ▶ 📁 Template-Dateien anzeigen                              │
│                                                              │
│ ─────────────────────────────────────────────────────────── │
│                                                              │
│ [✓ Template aktivieren] [🗑️ Löschen]                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Dateipfade-Expander (erweitert)

```
┌─────────────────────────────────────────────────────────────┐
│ ▼ 📁 Template-Dateien anzeigen                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ **Hintergrund-PDFs (Seite 1-8):**                          │
│                                                              │
│ ✅ Seite 1: pdf_templates_static/seite1.pdf                │
│ ✅ Seite 2: pdf_templates_static/seite2.pdf                │
│ ✅ Seite 3: pdf_templates_static/seite3.pdf                │
│ ✅ Seite 4: pdf_templates_static/seite4.pdf                │
│ ✅ Seite 5: pdf_templates_static/seite5.pdf                │
│ ✅ Seite 6: pdf_templates_static/seite6.pdf                │
│ ✅ Seite 7: pdf_templates_static/seite7.pdf                │
│ ✅ Seite 8: pdf_templates_static/seite8.pdf                │
│                                                              │
│ ─────────────────────────────────────────────────────────── │
│                                                              │
│ **Koordinaten-Dateien (YML):**                             │
│                                                              │
│ ✅ Seite 1: coords/seite1.yml                              │
│ ✅ Seite 2: coords/seite2.yml                              │
│ ✅ Seite 3: coords/seite3.yml                              │
│ ✅ Seite 4: coords/seite4.yml                              │
│ ✅ Seite 5: coords/seite5.yml                              │
│ ✅ Seite 6: coords/seite6.yml                              │
│ ✅ Seite 7: coords/seite7.yml                              │
│ ✅ Seite 8: coords/seite8.yml                              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Lösch-Bestätigung

```
┌─────────────────────────────────────────────────────────────┐
│ ⚠️ Möchten Sie das Template 'Standard-Template'             │
│    wirklich löschen?                                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ [Ja, löschen]                    [Abbrechen]                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Tab 2: Neues Template hinzufügen

```
┌─────────────────────────────────────────────────────────────┐
│ ➕ Neues Template hinzufügen                                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ Erstellen Sie ein neues PDF-Template mit benutzerdefinierten│
│ Hintergründen und Koordinaten.                              │
│                                                              │
│ **1. Template-Informationen:**                              │
│                                                              │
│ ┌──────────────────────────┬──────────────────────────────┐ │
│ │ Template-Name *          │ Template-ID *                │ │
│ │ ┌──────────────────────┐ │ ┌──────────────────────────┐ │ │
│ │ │ z.B. Standard-       │ │ │ z.B. standard_template   │ │ │
│ │ │ Template             │ │ │                          │ │ │
│ │ └──────────────────────┘ │ └──────────────────────────┘ │ │
│ └──────────────────────────┴──────────────────────────────┘ │
│                                                              │
│ Beschreibung                                                │
│ ┌──────────────────────────────────────────────────────────┐│
│ │ Beschreiben Sie das Template...                          ││
│ │                                                          ││
│ └──────────────────────────────────────────────────────────┘│
│                                                              │
│ ─────────────────────────────────────────────────────────── │
│                                                              │
│ **2. Hintergrund-PDFs (Seite 1-8):**                       │
│ Geben Sie die Dateipfade zu den PDF-Hintergründen für      │
│ jede Seite an.                                              │
│                                                              │
│ ┌──────────────────────────┬──────────────────────────────┐ │
│ │ Seite 1                  │ Seite 2                      │ │
│ │ ┌──────────────────────┐ │ ┌──────────────────────────┐ │ │
│ │ │ pdf_templates_static/│ │ │ pdf_templates_static/    │ │ │
│ │ │ seite1.pdf           │ │ │ seite2.pdf               │ │ │
│ │ └──────────────────────┘ │ └──────────────────────────┘ │ │
│ └──────────────────────────┴──────────────────────────────┘ │
│                                                              │
│ ┌──────────────────────────┬──────────────────────────────┐ │
│ │ Seite 3                  │ Seite 4                      │ │
│ │ ┌──────────────────────┐ │ ┌──────────────────────────┐ │ │
│ │ │ ...                  │ │ │ ...                      │ │ │
│ │ └──────────────────────┘ │ └──────────────────────────┘ │ │
│ └──────────────────────────┴──────────────────────────────┘ │
│                                                              │
│ [... Seiten 5-8 ...]                                        │
│                                                              │
│ ─────────────────────────────────────────────────────────── │
│                                                              │
│ **3. Koordinaten-Dateien (YML, Seite 1-8):**               │
│ Geben Sie die Dateipfade zu den YML-Koordinatendateien     │
│ für jede Seite an.                                          │
│                                                              │
│ ┌──────────────────────────┬──────────────────────────────┐ │
│ │ Seite 1                  │ Seite 2                      │ │
│ │ ┌──────────────────────┐ │ ┌──────────────────────────┐ │ │
│ │ │ coords/seite1.yml    │ │ │ coords/seite2.yml        │ │ │
│ │ └──────────────────────┘ │ └──────────────────────────┘ │ │
│ └──────────────────────────┴──────────────────────────────┘ │
│                                                              │
│ [... Seiten 3-8 ...]                                        │
│                                                              │
│ ─────────────────────────────────────────────────────────── │
│                                                              │
│ **4. Template hinzufügen:**                                 │
│                                                              │
│ [➕ Template hinzufügen] [🔄 Formular zurücksetzen]         │
│                                                              │
│ ▶ ℹ️ Hilfe zu Template-Dateipfaden                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Hilfe-Expander (erweitert)

```
┌─────────────────────────────────────────────────────────────┐
│ ▼ ℹ️ Hilfe zu Template-Dateipfaden                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ **Hintergrund-PDFs:**                                       │
│ - Pfade relativ zum Projekt-Root angeben                   │
│ - Beispiel: `pdf_templates_static/seite1.pdf`             │
│ - PDFs sollten im A4-Format sein                           │
│                                                              │
│ **Koordinaten-Dateien:**                                    │
│ - YML-Dateien mit Textpositionen                           │
│ - Beispiel: `coords/seite1.yml`                            │
│ - Format: `key: [x, y, width, height]`                     │
│                                                              │
│ **Tipps:**                                                  │
│ - Verwenden Sie konsistente Pfadstrukturen                 │
│ - Stellen Sie sicher, dass alle Dateien existieren         │
│ - Testen Sie das Template nach dem Hinzufügen              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Validierungs-Fehler

```
┌─────────────────────────────────────────────────────────────┐
│ ❌ Template-Name ist erforderlich                           │
│ ❌ Template-ID darf nur Kleinbuchstaben, Zahlen und         │
│    Unterstriche enthalten                                   │
│ ❌ Mindestens ein Hintergrund-PDF muss angegeben werden     │
└─────────────────────────────────────────────────────────────┘
```

### Erfolgs-Meldung

```
┌─────────────────────────────────────────────────────────────┐
│ ✅ Template 'Standard-Template' erfolgreich hinzugefügt!    │
└─────────────────────────────────────────────────────────────┘
```

## Interaktions-Fluss

### Template aktivieren

```
1. Benutzer öffnet "Template-Auswahl"
   ↓
2. Benutzer wählt Template aus Dropdown
   ↓
3. Template-Details werden angezeigt
   ↓
4. Benutzer klickt "✓ Template aktivieren"
   ↓
5. Template wird in Datenbank als aktiv markiert
   ↓
6. Erfolgs-Meldung wird angezeigt
   ↓
7. UI wird aktualisiert (Status: 🟢 Aktiv)
```

### Neues Template hinzufügen

```
1. Benutzer öffnet "Neues Template hinzufügen"
   ↓
2. Benutzer füllt Template-Informationen aus
   ↓
3. Benutzer gibt Dateipfade ein
   ↓
4. Benutzer klickt "➕ Template hinzufügen"
   ↓
5. System validiert Eingaben
   ├─ Fehler → Fehler-Meldungen anzeigen
   └─ OK → Template in Datenbank speichern
       ↓
       Erfolgs-Meldung anzeigen
       ↓
       Formular zurücksetzen
```

### Template löschen

```
1. Benutzer wählt Template aus
   ↓
2. Benutzer klickt "🗑️ Löschen"
   ↓
3. Bestätigungs-Dialog wird angezeigt
   ↓
4. Benutzer bestätigt oder bricht ab
   ├─ Abbrechen → Dialog schließen
   └─ Bestätigen → Template aus Datenbank löschen
       ↓
       Wenn aktiv: active_template_id auf None setzen
       ↓
       Erfolgs-Meldung anzeigen
       ↓
       UI aktualisieren
```

## Status-Indikatoren

### Template-Status

- 🟢 **Aktiv** - Template ist derzeit aktiv
- ⚪ **Inaktiv** - Template ist verfügbar aber nicht aktiv

### Datei-Existenz

- ✅ **Existiert** - Datei wurde gefunden
- ❌ **Fehlt** - Datei existiert nicht

## Besondere Features

### 1. Automatische Validierung

- Echtzeit-Validierung der Template-ID
- Prüfung auf Duplikate
- Format-Validierung (nur lowercase, Zahlen, Unterstriche)

### 2. Datei-Existenz-Prüfung

- Automatische Prüfung aller Dateipfade
- Visuelle Indikatoren für fehlende Dateien
- Hilft bei der Fehlersuche

### 3. Sicherheits-Features

- Bestätigungs-Dialog beim Löschen
- Verhindert versehentliches Löschen
- Klare Warnung vor irreversibler Aktion

### 4. Benutzerfreundlichkeit

- Hilfe-Sektion mit Tipps
- Platzhalter-Text in Eingabefeldern
- Tooltips für alle Felder
- Formular-Reset-Funktion

## Technische Details

### Datenbank-Speicherung

```python
# Gespeichert in admin_settings Tabelle
{
    'key': 'pdf_templates',
    'value': {
        'templates': [...],
        'active_template_id': 'standard_template'
    }
}
```

### Template-ID Format

```
Gültig:   standard_template, template_1, my_template_2025
Ungültig: Standard-Template, template-1, my template
```

### Dateipfad-Format

```
Relativ zum Projekt-Root:
  pdf_templates_static/seite1.pdf
  coords/seite1.yml
```

## Zusammenfassung

Die PDF-Template-Verwaltung UI bietet:

✅ **Intuitive Bedienung** - Klare Tab-Struktur und logischer Aufbau  
✅ **Vollständige Funktionalität** - Auswählen, Aktivieren, Hinzufügen, Löschen  
✅ **Robuste Validierung** - Verhindert fehlerhafte Eingaben  
✅ **Hilfreiche Feedback** - Status-Indikatoren und Meldungen  
✅ **Sicherheit** - Bestätigungs-Dialoge für kritische Aktionen  
✅ **Benutzerfreundlichkeit** - Hilfe-Sektionen und Tooltips  

Die Implementierung erfüllt alle Requirements (23.1-23.5) und bietet eine professionelle Lösung für die Template-Verwaltung.
