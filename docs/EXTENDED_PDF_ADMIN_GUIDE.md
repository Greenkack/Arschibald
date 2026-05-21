# Extended PDF Admin Guide

## Administrator-Handbuch: PDF & Design-Einstellungen

### Inhaltsverzeichnis

1. [Einführung](#einführung)
2. [Zugriff auf Admin-Einstellungen](#zugriff-auf-admin-einstellungen)
3. [PDF-Design-Einstellungen](#pdf-design-einstellungen)
4. [Diagramm-Farbeinstellungen](#diagramm-farbeinstellungen)
5. [UI-Theme-Verwaltung](#ui-theme-verwaltung)
6. [PDF-Template-Verwaltung](#pdf-template-verwaltung)
7. [Layout-Optionen](#layout-optionen)
8. [Import/Export von Konfigurationen](#importexport-von-konfigurationen)
9. [Versionierung](#versionierung)
10. [Best Practices](#best-practices)

---

## Einführung

Als Administrator haben Sie Zugriff auf erweiterte Einstellungen für die PDF-Generierung und das Design der Anwendung. Diese Einstellungen ermöglichen es Ihnen:

- Das Aussehen der PDFs anzupassen (Farben, Schriften, Logos)
- Diagrammfarben global oder individuell zu konfigurieren
- UI-Themes zu verwalten
- PDF-Templates zu erstellen und zu verwalten
- Design-Konfigurationen zu exportieren und importieren
- Verschiedene Design-Versionen zu speichern

**Wichtig:** Alle Änderungen wirken sich auf alle Benutzer aus. Testen Sie Änderungen sorgfältig, bevor Sie sie produktiv einsetzen.

---

## Zugriff auf Admin-Einstellungen

### Navigation

1. Melden Sie sich mit Administrator-Rechten an
2. Navigieren Sie zu **Admin-Panel**
3. Wählen Sie **PDF & Design-Einstellungen**
4. Es öffnet sich die Admin-Einstellungsseite mit mehreren Tabs

### Verfügbare Tabs

- **PDF-Design**: Farben, Schriften, Logos für PDFs
- **Diagramm-Farben**: Globale und individuelle Diagrammfarben
- **UI-Themes**: Themes für die Benutzeroberfläche
- **PDF-Templates**: Verwaltung von PDF-Vorlagen
- **Layout-Optionen**: Aktivierung/Deaktivierung von Layouts
- **Import/Export**: Konfigurationen sichern und wiederherstellen
- **Versionen**: Design-Versionen verwalten

![Admin-Einstellungen Übersicht](screenshots/admin_overview.png)

---

## PDF-Design-Einstellungen

### Übersicht

Im Tab **"PDF-Design"** können Sie das Aussehen aller generierten PDFs anpassen.

### Farbeinstellungen

#### Primärfarbe

- **Verwendung**: Überschriften, Akzente, wichtige Elemente
- **Standard**: #1E3A8A (Dunkelblau)
- **Empfehlung**: Verwenden Sie Ihre Corporate-Identity-Farbe

**Konfiguration:**

1. Klicken Sie auf den Farbwähler neben "Primärfarbe"
2. Wählen Sie eine Farbe aus der Palette oder geben Sie einen Hex-Code ein
3. Die Vorschau wird automatisch aktualisiert
4. Klicken Sie auf "Speichern"

#### Sekundärfarbe

- **Verwendung**: Tabellen, Hintergründe, sekundäre Elemente
- **Standard**: #3B82F6 (Hellblau)
- **Empfehlung**: Sollte zur Primärfarbe passen

![Farbeinstellungen](screenshots/color_settings.png)

### Schriftart-Einstellungen

#### Verfügbare Schriftarten

- Helvetica (Standard)
- Helvetica-Bold
- Times-Roman
- Courier
- Custom (wenn hochgeladen)

#### Schriftgrößen

| Element | Standard | Empfohlen | Verwendung |
|---------|----------|-----------|------------|
| H1 | 18pt | 16-20pt | Hauptüberschriften |
| H2 | 14pt | 12-16pt | Unterüberschriften |
| Body | 10pt | 9-11pt | Fließtext |
| Small | 8pt | 7-9pt | Fußnoten, Kleingedrucktes |

**Konfiguration:**

1. Wählen Sie die Schriftart aus dem Dropdown
2. Passen Sie die Schriftgrößen mit den Number-Inputs an
3. Prüfen Sie die Vorschau
4. Speichern Sie die Änderungen

### Logo-Einstellungen

#### Logo-Position

- **Links**: Logo links oben (Standard)
- **Rechts**: Logo rechts oben
- **Zentriert**: Logo mittig oben

**Konfiguration:**

1. Wählen Sie die Position aus dem Dropdown
2. Die Vorschau zeigt die neue Position
3. Speichern Sie die Änderung

#### Logo hochladen

1. Klicken Sie auf "Logo hochladen"
2. Wählen Sie eine Bilddatei (PNG, JPG, SVG)
3. Empfohlene Größe: 200x80 Pixel
4. Das Logo wird automatisch skaliert

### Footer-Einstellungen

#### Footer-Format

- **Standard**: "Seite X von Y"
- **Mit Datum**: "Seite X von Y | [Datum]"
- **Custom**: Eigener Text

**Custom Footer:**

1. Wählen Sie "Custom" aus dem Dropdown
2. Geben Sie Ihren Text ein
3. Verwenden Sie Platzhalter:
   - `{page}`: Aktuelle Seitenzahl
   - `{total}`: Gesamtseitenzahl
   - `{date}`: Aktuelles Datum
   - `{company}`: Firmenname

Beispiel: `{company} | Seite {page}/{total} | {date}`

### Wasserzeichen

#### Aktivierung

1. Aktivieren Sie die Checkbox "Wasserzeichen aktivieren"
2. Geben Sie den Wasserzeichen-Text ein (z.B. "ENTWURF")
3. Stellen Sie die Transparenz ein (0-100%)
4. Empfohlen: 10-20% für dezente Wasserzeichen

**Verwendung:**

- Entwürfe: "ENTWURF" oder "DRAFT"
- Vertraulich: "VERTRAULICH"
- Kopien: "KOPIE"

### Live-Vorschau

Die Live-Vorschau zeigt:

- Erste Seite des PDFs mit aktuellen Einstellungen
- Farben, Schriften, Logo-Position
- Footer-Format
- Wasserzeichen (falls aktiviert)

**Hinweis:** Die Vorschau wird automatisch bei jeder Änderung aktualisiert.

### Speichern und Zurücksetzen

**Speichern:**

- Klicken Sie auf "Einstellungen speichern"
- Änderungen werden sofort für alle Benutzer aktiv
- Eine Bestätigung wird angezeigt

**Zurücksetzen:**

- Klicken Sie auf "Auf Standard zurücksetzen"
- Alle Einstellungen werden auf Standardwerte zurückgesetzt
- Eine Bestätigung ist erforderlich

---

## Diagramm-Farbeinstellungen

### Übersicht

Im Tab **"Diagramm-Farben"** können Sie die Farben aller Diagramme und Visualisierungen anpassen.

### Globale Farbeinstellungen

#### Primäre Diagrammfarben

Definieren Sie bis zu 6 Hauptfarben, die für alle Diagramme verwendet werden:

1. **Farbe 1**: Hauptdatenreihe (Standard: Blau)
2. **Farbe 2**: Zweite Datenreihe (Standard: Grün)
3. **Farbe 3**: Dritte Datenreihe (Standard: Orange)
4. **Farbe 4**: Vierte Datenreihe (Standard: Rot)
5. **Farbe 5**: Fünfte Datenreihe (Standard: Lila)
6. **Farbe 6**: Sechste Datenreihe (Standard: Gelb)

**Konfiguration:**

1. Klicken Sie auf den Farbwähler für jede Farbe
2. Wählen Sie die gewünschte Farbe
3. Die Vorschau zeigt ein Beispieldiagramm mit den neuen Farben
4. Speichern Sie die Änderungen

![Globale Diagrammfarben](screenshots/global_chart_colors.png)

#### Speicherort

Globale Farben werden in `admin_settings` unter `visualization_settings.global_chart_colors` gespeichert.

### Farbpaletten-Bibliothek

#### Vordefinierte Paletten

**1. Corporate (Blau-Grau)**

- Professionell und seriös
- Farben: #1E3A8A, #3B82F6, #60A5FA, #93C5FD, #DBEAFE, #F3F4F6
- Empfohlen für: Geschäftskunden, offizielle Dokumente

**2. Eco (Grün-Töne)**

- Nachhaltig und umweltfreundlich
- Farben: #065F46, #059669, #10B981, #34D399, #6EE7B7, #A7F3D0
- Empfohlen für: Nachhaltigkeitsberichte, Umweltprojekte

**3. Energy (Orange-Gelb)**

- Energiegeladen und dynamisch
- Farben: #C2410C, #EA580C, #F97316, #FB923C, #FCD34D, #FDE68A
- Empfohlen für: Energieberichte, Solarprojekte

**4. Professional (Dunkelblau-Grau)**

- Konservativ und vertrauenswürdig
- Farben: #1E293B, #334155, #475569, #64748B, #94A3B8, #CBD5E1
- Empfohlen für: Banken, Versicherungen, Behörden

**5. Colorful (Bunte Palette)**

- Lebendig und auffällig
- Farben: #DC2626, #EA580C, #CA8A04, #16A34A, #2563EB, #9333EA
- Empfohlen für: Präsentationen, Marketing

**6. Monochrome (Graustufen)**

- Minimalistisch und elegant
- Farben: #000000, #404040, #737373, #A3A3A3, #D4D4D4, #F5F5F5
- Empfohlen für: Schwarz-Weiß-Druck, minimalistische Designs

**7. Accessible (Farbenblind-freundlich)**

- Barrierefrei und gut unterscheidbar
- Farben: #0173B2, #DE8F05, #029E73, #CC78BC, #CA9161, #949494
- Empfohlen für: Barrierefreie Dokumente, öffentliche Einrichtungen

#### Palette anwenden

1. Wählen Sie eine Palette aus der Liste
2. Klicken Sie auf "Vorschau anzeigen"
3. Prüfen Sie die Beispieldiagramme
4. Klicken Sie auf "Palette anwenden"
5. Alle globalen Farben werden überschrieben

![Farbpaletten](screenshots/color_palettes.png)

#### Eigene Palette erstellen

1. Konfigurieren Sie die 6 globalen Farben nach Ihren Wünschen
2. Klicken Sie auf "Als Palette speichern"
3. Geben Sie einen Namen ein (z.B. "Firmenfarben 2025")
4. Die Palette wird zur Bibliothek hinzugefügt
5. Sie können sie später wiederverwenden

### Individuelle Diagramm-Konfiguration

#### Übersicht

Für jedes Diagramm können Sie individuelle Farben festlegen, die die globalen Einstellungen überschreiben.

#### Diagramm auswählen

1. Wählen Sie eine Kategorie aus dem Dropdown:
   - Wirtschaftlichkeit
   - Produktion & Verbrauch
   - Eigenverbrauch & Autarkie
   - Finanzielle Analyse
   - CO2 & Umwelt
   - Vergleiche & Szenarien

2. Wählen Sie ein spezifisches Diagramm aus der Liste

#### Farbkonfiguration

Für jedes Diagramm können Sie konfigurieren:

**Farbschema:**

- **Global**: Verwendet die globalen Farben (Standard)
- **Custom**: Verwendet individuelle Farben

**Custom-Farben:**

- Primärfarbe: Hauptdatenreihe
- Sekundärfarbe: Zweite Datenreihe
- Hintergrundfarbe: Diagrammhintergrund
- Gitterfarbe: Gitterlinien
- Textfarbe: Beschriftungen und Achsen

**Beispiel-Konfiguration für "Kumulierter Cashflow":**

1. Wählen Sie Kategorie "Wirtschaftlichkeit"
2. Wählen Sie "Kumulierter Cashflow"
3. Wählen Sie Farbschema "Custom"
4. Primärfarbe: #10B981 (Grün für positive Werte)
5. Sekundärfarbe: #EF4444 (Rot für negative Werte)
6. Speichern

![Individuelle Diagrammfarben](screenshots/individual_chart_colors.png)

#### Auf Global zurücksetzen

1. Wählen Sie das Diagramm
2. Klicken Sie auf "Auf Global zurücksetzen"
3. Das Diagramm verwendet wieder die globalen Farben
4. Custom-Einstellungen werden gelöscht

### Vorschau-Funktion

Die Vorschau zeigt:

- Beispieldiagramm mit aktuellen Farben
- Alle Datenreihen
- Legende und Beschriftungen
- Gitterlinien und Achsen

**Echtzeit-Update:**

- Änderungen werden sofort in der Vorschau sichtbar
- Keine Speicherung erforderlich für Vorschau
- Erst beim Klick auf "Speichern" werden Änderungen übernommen

### Best Practices für Diagrammfarben

1. **Kontrast beachten**: Farben sollten gut unterscheidbar sein
2. **Barrierefreiheit**: Verwenden Sie farbenblind-freundliche Paletten
3. **Corporate Identity**: Nutzen Sie Ihre Firmenfarben
4. **Konsistenz**: Verwenden Sie ähnliche Farben für ähnliche Daten
5. **Druck beachten**: Testen Sie Farben im Schwarz-Weiß-Druck

---

## UI-Theme-Verwaltung

### Übersicht

Im Tab **"UI-Themes"** können Sie das Aussehen der gesamten Benutzeroberfläche anpassen.

### Verfügbare Themes

#### 1. Light Theme (Standard)

- Heller Hintergrund, dunkler Text
- Gut lesbar bei Tageslicht
- Standard für die meisten Benutzer

#### 2. Dark Theme

- Dunkler Hintergrund, heller Text
- Augenschonend bei wenig Licht
- Modern und elegant

#### 3. Corporate Theme

- Anpassbar an Firmenfarben
- Professionelles Erscheinungsbild
- Empfohlen für Unternehmenseinsatz

#### 4. High Contrast Theme

- Maximaler Kontrast für Barrierefreiheit
- Große Schriften
- Empfohlen für Sehbehinderte

### Theme aktivieren

1. Wählen Sie ein Theme aus dem Dropdown
2. Klicken Sie auf "Vorschau anzeigen"
3. Die Vorschau zeigt alle UI-Elemente im neuen Theme
4. Klicken Sie auf "Theme aktivieren"
5. Das Theme wird für alle Benutzer aktiv

![Theme-Auswahl](screenshots/theme_selection.png)

### Theme anpassen (Corporate Theme)

#### Farben konfigurieren

**Primärfarbe:**

- Hauptfarbe der Anwendung
- Buttons, Links, Akzente
- Standard: #1E3A8A

**Sekundärfarbe:**

- Unterstützende Farbe
- Hover-Effekte, sekundäre Buttons
- Standard: #3B82F6

**Hintergrundfarbe:**

- Haupthintergrund der Seiten
- Standard: #FFFFFF

**Textfarbe:**

- Haupttextfarbe
- Standard: #000000

**Akzentfarbe:**

- Hervorhebungen, Warnungen
- Standard: #F59E0B

#### Konfiguration

1. Wählen Sie "Corporate Theme"
2. Klicken Sie auf "Theme bearbeiten"
3. Passen Sie alle Farben an
4. Prüfen Sie die Vorschau
5. Klicken Sie auf "Theme speichern"
6. Geben Sie einen Namen ein (z.B. "Firmen-Theme 2025")

### Theme-Vorschau

Die Vorschau zeigt:

- Buttons in verschiedenen Zuständen
- Textfelder und Inputs
- Tabellen und Listen
- Navigationsleiste
- Sidebar
- Karten und Container

**HTML-Vorschau:**

```html
<div style="background: {background_color}; color: {text_color}">
  <button style="background: {primary_color}">Primär-Button</button>
  <button style="background: {secondary_color}">Sekundär-Button</button>
  <a style="color: {accent_color}">Link</a>
</div>
```

### Theme exportieren

1. Wählen Sie das Theme
2. Klicken Sie auf "Theme exportieren"
3. Eine JSON-Datei wird heruntergeladen
4. Sie können das Theme auf anderen Installationen importieren

### Theme importieren

1. Klicken Sie auf "Theme importieren"
2. Wählen Sie eine Theme-JSON-Datei
3. Das Theme wird validiert
4. Klicken Sie auf "Importieren"
5. Das Theme wird zur Liste hinzugefügt

---

## PDF-Template-Verwaltung

### Übersicht

Im Tab **"PDF-Templates"** können Sie verschiedene PDF-Vorlagen verwalten.

### Template-Struktur

Ein PDF-Template besteht aus:

- **Name**: Eindeutiger Name des Templates
- **Beschreibung**: Kurze Beschreibung
- **Vorschau-Bild**: Thumbnail des Templates
- **PDF-Hintergründe**: 8 PDF-Dateien für Seiten 1-8
- **Koordinaten-Dateien**: 8 YML-Dateien mit Textpositionen

### Template-Liste

Die Liste zeigt:

- Alle verfügbaren Templates
- Aktives Template (markiert)
- Vorschau-Bilder
- Beschreibungen

![Template-Liste](screenshots/template_list.png)

### Template aktivieren

1. Wählen Sie ein Template aus der Liste
2. Klicken Sie auf "Details anzeigen"
3. Prüfen Sie die Vorschau
4. Klicken Sie auf "Template aktivieren"
5. Das Template wird für alle neuen PDFs verwendet

### Neues Template hinzufügen

#### Schritt 1: Template-Informationen

1. Klicken Sie auf "Neues Template hinzufügen"
2. Geben Sie einen Namen ein (z.B. "Modern Blue 2025")
3. Geben Sie eine Beschreibung ein
4. Laden Sie ein Vorschau-Bild hoch (PNG, 400x300px)

#### Schritt 2: PDF-Hintergründe hochladen

Für jede Seite (1-8):

1. Klicken Sie auf "Seite X hochladen"
2. Wählen Sie eine PDF-Datei
3. Die PDF sollte eine einzelne Seite im A4-Format sein
4. Wiederholen Sie für alle 8 Seiten

**Anforderungen:**

- Format: PDF
- Seitengröße: A4 (210 x 297 mm)
- Auflösung: Mindestens 300 DPI
- Dateigröße: Maximal 5 MB pro Seite

#### Schritt 3: Koordinaten-Dateien hochladen

Für jede Seite (1-8):

1. Klicken Sie auf "Koordinaten Seite X hochladen"
2. Wählen Sie eine YML-Datei
3. Die YML-Datei definiert Textpositionen

**YML-Format:**

```yaml
# Beispiel: seite1.yml
title:
  x: 50
  y: 100
  font_size: 18
  
customer_name:
  x: 50
  y: 150
  font_size: 12
  
# ... weitere Felder
```

#### Schritt 4: Template speichern

1. Prüfen Sie alle Eingaben
2. Klicken Sie auf "Template speichern"
3. Das Template wird validiert
4. Bei Erfolg wird es zur Liste hinzugefügt

### Template bearbeiten

1. Wählen Sie ein Template aus der Liste
2. Klicken Sie auf "Bearbeiten"
3. Ändern Sie die gewünschten Felder
4. Laden Sie neue Dateien hoch (optional)
5. Speichern Sie die Änderungen

### Template löschen

1. Wählen Sie ein Template aus der Liste
2. Klicken Sie auf "Löschen"
3. Bestätigen Sie die Löschung
4. **Achtung**: Das aktive Template kann nicht gelöscht werden

### Template validieren

Die Validierung prüft:

- Alle 8 PDF-Dateien vorhanden
- Alle 8 YML-Dateien vorhanden
- PDF-Dateien im A4-Format
- YML-Dateien syntaktisch korrekt
- Alle erforderlichen Felder in YML definiert

**Validierung starten:**

1. Wählen Sie ein Template
2. Klicken Sie auf "Validieren"
3. Fehler werden angezeigt
4. Beheben Sie Fehler und validieren Sie erneut

---

## Layout-Optionen

### Übersicht

Im Tab **"Layout-Optionen"** können Sie verschiedene PDF-Layouts aktivieren oder deaktivieren.

### Verfügbare Layouts

#### 1. Standard-Layout (8 Seiten)

- **Status**: Immer aktiviert (kann nicht deaktiviert werden)
- **Beschreibung**: Standard-PDF mit 8 Seiten
- **Verwendung**: Normale Angebote

#### 2. Erweiterte Layouts

- **Status**: Optional aktivierbar
- **Beschreibung**: PDF mit Zusatzseiten
- **Verwendung**: Detaillierte Angebote mit Finanzierung, Datenblättern, etc.

#### 3. Kompakt-Layout

- **Status**: Optional aktivierbar
- **Beschreibung**: Reduzierte PDF mit 4-6 Seiten
- **Verwendung**: Schnelle Übersichtsangebote

#### 4. Custom-Layout

- **Status**: Optional aktivierbar
- **Beschreibung**: Frei konfigurierbares Layout
- **Verwendung**: Spezielle Anforderungen

### Layout aktivieren/deaktivieren

1. Wählen Sie ein Layout aus der Liste
2. Aktivieren Sie die Checkbox "Aktiviert"
3. Optional: Aktivieren Sie "Als Standard"
4. Klicken Sie auf "Speichern"

![Layout-Optionen](screenshots/layout_options.png)

### Standard-Layout festlegen

1. Wählen Sie ein Layout
2. Aktivieren Sie "Als Standard"
3. Speichern Sie die Änderung
4. Dieses Layout wird automatisch vorausgewählt

**Hinweis**: Nur ein Layout kann als Standard markiert sein.

### Layout-Konfiguration

Für jedes Layout können Sie konfigurieren:

- **Name**: Anzeigename
- **Beschreibung**: Kurze Beschreibung
- **Aktiviert**: Verfügbar für Benutzer
- **Als Standard**: Automatisch vorausgewählt
- **Reihenfolge**: Position in der Liste

---

## Import/Export von Konfigurationen

### Übersicht

Im Tab **"Import/Export"** können Sie alle Design-Konfigurationen sichern und wiederherstellen.

### Export

#### Was wird exportiert?

- PDF-Design-Einstellungen (Farben, Schriften, Logos)
- Diagramm-Farbkonfigurationen (global und individuell)
- UI-Theme-Einstellungen
- Custom-Farbpaletten
- Layout-Konfigurationen

#### Export durchführen

1. Klicken Sie auf "Konfiguration exportieren"
2. Wählen Sie die zu exportierenden Bereiche:
   - ☑ PDF-Design
   - ☑ Diagramm-Farben
   - ☑ UI-Themes
   - ☑ Farbpaletten
   - ☑ Layouts
3. Klicken Sie auf "Export starten"
4. Eine JSON-Datei wird heruntergeladen
5. Dateiname: `design_config_[Datum].json`

![Export-Funktion](screenshots/export_config.png)

#### Export-Datei

Die JSON-Datei enthält:

```json
{
  "version": "1.0.0",
  "export_date": "2025-01-09T10:30:00",
  "pdf_design": {
    "colors": {...},
    "fonts": {...},
    "logo": {...}
  },
  "chart_colors": {
    "global": [...],
    "individual": {...}
  },
  "ui_themes": [...],
  "color_palettes": [...],
  "layouts": [...]
}
```

### Import

#### Import durchführen

1. Klicken Sie auf "Konfiguration importieren"
2. Wählen Sie eine JSON-Datei
3. Die Datei wird validiert
4. Es wird eine Vorschau der Änderungen angezeigt
5. Wählen Sie die zu importierenden Bereiche
6. Klicken Sie auf "Import bestätigen"
7. **Achtung**: Bestehende Einstellungen werden überschrieben

![Import-Funktion](screenshots/import_config.png)

#### Validierung

Die Validierung prüft:

- JSON-Syntax korrekt
- Version kompatibel
- Alle erforderlichen Felder vorhanden
- Werte im gültigen Bereich
- Keine Konflikte mit bestehenden Daten

**Bei Fehlern:**

- Detaillierte Fehlermeldung wird angezeigt
- Import wird abgebrochen
- Keine Änderungen werden vorgenommen

#### Selektiver Import

Sie können wählen, welche Bereiche importiert werden:

- Nur PDF-Design
- Nur Diagramm-Farben
- Nur UI-Themes
- Alle Bereiche

**Beispiel**: Import nur der Diagrammfarben, ohne PDF-Design zu ändern.

### Backup-Strategie

**Empfohlen:**

1. Exportieren Sie regelmäßig Ihre Konfiguration
2. Speichern Sie Exports mit Datum im Dateinamen
3. Bewahren Sie mindestens 3 Versionen auf
4. Testen Sie Imports auf einer Testinstallation

---

## Versionierung

### Übersicht

Im Tab **"Versionen"** können Sie verschiedene Design-Versionen speichern und verwalten.

### Version speichern

#### Snapshot erstellen

1. Klicken Sie auf "Neue Version speichern"
2. Geben Sie einen Versionsnamen ein (z.B. "Sommer-Design 2025")
3. Optional: Geben Sie eine Beschreibung ein
4. Klicken Sie auf "Version speichern"
5. Ein Snapshot aller aktuellen Einstellungen wird erstellt

![Version speichern](screenshots/save_version.png)

#### Was wird gespeichert?

- Alle PDF-Design-Einstellungen
- Alle Diagramm-Farbkonfigurationen
- Aktives UI-Theme
- Alle Custom-Farbpaletten
- Layout-Konfigurationen
- Zeitstempel und Benutzer

### Versionen-Liste

Die Liste zeigt:

- Versionsname
- Beschreibung
- Erstellungsdatum
- Erstellt von (Benutzer)
- Aktionen (Laden, Löschen)

### Version laden

1. Wählen Sie eine Version aus der Liste
2. Klicken Sie auf "Details anzeigen"
3. Prüfen Sie die Vorschau der Einstellungen
4. Klicken Sie auf "Version laden"
5. Bestätigen Sie die Wiederherstellung
6. Alle Einstellungen werden auf diese Version zurückgesetzt

**Achtung**: Aktuelle Einstellungen werden überschrieben. Speichern Sie ggf. vorher eine neue Version.

### Version löschen

1. Wählen Sie eine Version aus der Liste
2. Klicken Sie auf "Löschen"
3. Bestätigen Sie die Löschung
4. Die Version wird permanent gelöscht

**Hinweis**: Die aktuell geladene Version kann nicht gelöscht werden.

### Version vergleichen

1. Wählen Sie zwei Versionen aus der Liste
2. Klicken Sie auf "Versionen vergleichen"
3. Es wird eine Übersicht der Unterschiede angezeigt
4. Sie können sehen, welche Einstellungen sich geändert haben

### Automatische Versionen

Das System erstellt automatisch Versionen:

- Bei jedem Import einer Konfiguration
- Vor jedem Zurücksetzen auf Standard
- Einmal täglich (wenn Änderungen vorhanden)

**Automatische Versionen** sind mit "(Auto)" gekennzeichnet.

---

## Best Practices

### Allgemeine Empfehlungen

1. **Testen Sie Änderungen**: Prüfen Sie neue Einstellungen auf einer Testinstallation
2. **Erstellen Sie Backups**: Exportieren Sie regelmäßig Ihre Konfiguration
3. **Verwenden Sie Versionen**: Speichern Sie wichtige Design-Stände
4. **Dokumentieren Sie Änderungen**: Nutzen Sie aussagekräftige Versionsnamen
5. **Kommunizieren Sie Updates**: Informieren Sie Benutzer über Design-Änderungen

### Corporate Identity

1. **Verwenden Sie Firmenfarben**: Passen Sie Primär- und Sekundärfarbe an
2. **Laden Sie Ihr Logo hoch**: Verwenden Sie Ihr offizielles Logo
3. **Erstellen Sie ein Corporate Theme**: Einheitliches Erscheinungsbild
4. **Definieren Sie Farbpaletten**: Konsistente Diagrammfarben
5. **Erstellen Sie Templates**: Professionelle PDF-Vorlagen

### Performance

1. **Optimieren Sie Logos**: Verwenden Sie komprimierte Bilder
2. **Begrenzen Sie Farbpaletten**: Maximal 10 Custom-Paletten
3. **Löschen Sie ungenutzte Versionen**: Halten Sie die Datenbank schlank
4. **Verwenden Sie Standard-Schriften**: Custom-Fonts verlangsamen die Generierung

### Barrierefreiheit

1. **Verwenden Sie kontrastreiche Farben**: Mindestens 4.5:1 Kontrast
2. **Testen Sie mit High Contrast Theme**: Prüfen Sie Lesbarkeit
3. **Verwenden Sie Accessible-Farbpalette**: Farbenblind-freundlich
4. **Vermeiden Sie reine Farbcodierung**: Nutzen Sie auch Formen/Muster

### Wartung

1. **Regelmäßige Reviews**: Prüfen Sie Einstellungen quartalsweise
2. **Aktualisieren Sie Templates**: Halten Sie Vorlagen aktuell
3. **Bereinigen Sie alte Versionen**: Löschen Sie veraltete Snapshots
4. **Testen Sie nach Updates**: Prüfen Sie Einstellungen nach System-Updates

---

## Fehlerbehebung

### Problem: Änderungen werden nicht angezeigt

**Lösung:**

- Leeren Sie den Browser-Cache (Strg+F5)
- Melden Sie sich ab und wieder an
- Prüfen Sie, ob Änderungen gespeichert wurden

### Problem: Import schlägt fehl

**Lösung:**

- Prüfen Sie die JSON-Syntax
- Stellen Sie sicher, dass die Version kompatibel ist
- Prüfen Sie die Fehlermeldung für Details
- Versuchen Sie einen selektiven Import

### Problem: Vorschau wird nicht geladen

**Lösung:**

- Aktualisieren Sie die Seite
- Prüfen Sie Ihre Internetverbindung
- Deaktivieren Sie Browser-Erweiterungen
- Versuchen Sie einen anderen Browser

### Problem: Template-Validierung schlägt fehl

**Lösung:**

- Prüfen Sie, ob alle 8 PDF-Dateien vorhanden sind
- Prüfen Sie, ob alle 8 YML-Dateien vorhanden sind
- Stellen Sie sicher, dass PDFs im A4-Format sind
- Prüfen Sie die YML-Syntax

### Problem: Farben werden nicht korrekt angezeigt

**Lösung:**

- Prüfen Sie den Hex-Code (muss mit # beginnen)
- Stellen Sie sicher, dass der Wert 6 Zeichen hat
- Verwenden Sie den Farbwähler statt manueller Eingabe
- Speichern Sie die Änderungen

---

## Kontakt und Support

Bei Fragen oder Problemen:

- Konsultieren Sie diese Anleitung
- Prüfen Sie die Fehlermeldungen
- Kontaktieren Sie den technischen Support
- Erstellen Sie ein Backup vor größeren Änderungen

**Version:** 1.0.0  
**Stand:** Januar 2025  
**Zielgruppe:** Administratoren
