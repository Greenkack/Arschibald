# Requirements Document: Erweiterte PDF-Ausgabe

## Introduction

Die erweiterte PDF-Ausgabe ist eine optionale Funktion, die es ermöglicht, zusätzliche Seiten an das Standard-8-Seiten-PDF anzuhängen. Diese Erweiterung soll Finanzierungsdetails, Produktdatenblätter, Firmendokumente und weitere relevante Informationen enthalten. Die Implementierung muss robust sein, nur echte Keys verwenden und bestehende Funktionen nicht beeinträchtigen.

**Kernziele:**

- Optionale Aktivierung in der PDF-Erstellungs-UI
- Anhängen von Zusatzseiten ab Seite 9
- Integration von Finanzierungsdetails mit allen relevanten Informationen
- Einbindung von Produktdatenblättern aus der Datenbank
- Einbindung von Firmendokumenten aus der Datenbank
- Verwendung nur echter, existierender Keys aus dem System
- Keine Beeinträchtigung bestehender 8-Seiten-Funktionalität

## Requirements

### Requirement 1: Optionale Aktivierung der erweiterten PDF-Ausgabe

**User Story:** Als Benutzer möchte ich in der PDF-UI optional die erweiterte Ausgabe aktivieren können, damit ich entscheiden kann, ob zusätzliche Seiten angehängt werden sollen.

#### Acceptance Criteria

1. WHEN die PDF-UI gerendert wird THEN soll eine Checkbox "Erweiterte PDF-Ausgabe aktivieren" angezeigt werden
2. WHEN die Checkbox aktiviert wird THEN sollen zusätzliche Optionen für die erweiterte Ausgabe sichtbar werden
3. WHEN die erweiterte Ausgabe deaktiviert ist THEN soll das Standard-8-Seiten-PDF generiert werden
4. WHEN die erweiterte Ausgabe aktiviert ist THEN sollen ab Seite 9 zusätzliche Seiten angehängt werden
5. IF die erweiterte Ausgabe aktiviert ist THEN soll die Seitennummerierung entsprechend angepasst werden (z.B. "Seite 9 von 15")

### Requirement 2: Finanzierungsdetails in erweiterter PDF

**User Story:** Als Benutzer möchte ich detaillierte Finanzierungsinformationen in die erweiterte PDF einbauen, damit Kunden alle Finanzierungsoptionen übersichtlich sehen können.

#### Acceptance Criteria

1. WHEN Finanzierungsoptionen im System konfiguriert sind THEN sollen diese in der erweiterten PDF angezeigt werden
2. WHEN eine Finanzierungsoption ausgewählt ist THEN sollen folgende Details angezeigt werden:
   - Name der Finanzierungsoption
   - Laufzeit in Monaten
   - Zinssatz
   - Monatliche Rate
   - Gesamtkosten
   - Bearbeitungsgebühr
3. WHEN mehrere Finanzierungsoptionen verfügbar sind THEN sollen diese übersichtlich in einer Tabelle dargestellt werden
4. WHEN Zahlungsmodalitäten konfiguriert sind THEN sollen Rabatte und Aufschläge korrekt berechnet und angezeigt werden
5. IF keine Finanzierungsoptionen verfügbar sind THEN soll ein entsprechender Hinweis angezeigt werden

### Requirement 3: Produktdatenblätter einbinden

**User Story:** Als Benutzer möchte ich Produktdatenblätter aus der Datenbank in die erweiterte PDF einbinden können, damit Kunden detaillierte technische Informationen erhalten.

#### Acceptance Criteria

1. WHEN Produktdatenblätter in der Datenbank gespeichert sind THEN sollen diese in der PDF-UI zur Auswahl angeboten werden
2. WHEN ein Produktdatenblatt ausgewählt wird THEN soll es als zusätzliche Seite(n) an die PDF angehängt werden
3. WHEN mehrere Produktdatenblätter ausgewählt werden THEN sollen diese in der Reihenfolge der Auswahl angehängt werden
4. WHEN ein Produktdatenblatt ein PDF ist THEN sollen dessen Seiten direkt eingebunden werden
5. IF ein Produktdatenblatt ein Bild ist THEN soll es auf einer neuen Seite zentriert dargestellt werden

### Requirement 4: Firmendokumente einbinden

**User Story:** Als Benutzer möchte ich Firmendokumente aus der Datenbank in die erweiterte PDF einbinden können, damit Kunden zusätzliche Informationen wie AGBs, Garantiebedingungen etc. erhalten.

#### Acceptance Criteria

1. WHEN Firmendokumente in der Datenbank gespeichert sind THEN sollen diese in der PDF-UI zur Auswahl angeboten werden
2. WHEN ein Firmendokument ausgewählt wird THEN soll es als zusätzliche Seite(n) an die PDF angehängt werden
3. WHEN mehrere Firmendokumente ausgewählt werden THEN sollen diese in der Reihenfolge der Auswahl angehängt werden
4. WHEN ein Firmendokument ein PDF ist THEN sollen dessen Seiten direkt eingebunden werden
5. IF ein Firmendokument ein anderes Format ist THEN soll es entsprechend konvertiert oder als Anhang behandelt werden

### Requirement 5: Verwendung echter Keys aus dem System

**User Story:** Als Entwickler möchte ich sicherstellen, dass nur echte, existierende Keys verwendet werden, damit keine falschen oder erfundenen Daten in der PDF erscheinen.

#### Acceptance Criteria

1. WHEN Daten für die PDF generiert werden THEN sollen nur Keys aus `PLACEHOLDER_MAPPING` oder dem `DynamicKeyManager` verwendet werden
2. WHEN ein Key nicht existiert THEN soll ein Fallback-Wert oder eine Warnung verwendet werden, aber kein erfundener Key
3. WHEN Finanzierungsdaten verwendet werden THEN sollen diese aus `payment_terms` und `financing_options` stammen
4. WHEN Produktdaten verwendet werden THEN sollen diese aus der `products` Tabelle stammen
5. IF ein Key fehlt THEN soll dies im Log dokumentiert werden, aber die PDF-Generierung nicht abbrechen

### Requirement 6: Robuste Fehlerbehandlung

**User Story:** Als System möchte ich robust mit fehlenden oder fehlerhaften Daten umgehen, damit die PDF-Generierung nicht abstürzt.

#### Acceptance Criteria

1. WHEN ein Produktdatenblatt nicht gefunden wird THEN soll eine Warnung geloggt und die Generierung fortgesetzt werden
2. WHEN ein Firmendokument nicht geladen werden kann THEN soll eine Warnung geloggt und die Generierung fortgesetzt werden
3. WHEN Finanzierungsdaten fehlen THEN soll ein entsprechender Hinweis in der PDF angezeigt werden
4. WHEN ein PDF-Merge fehlschlägt THEN soll ein Fallback auf die Standard-8-Seiten-PDF erfolgen
5. IF kritische Fehler auftreten THEN soll eine aussagekräftige Fehlermeldung angezeigt werden

### Requirement 7: Seitennummerierung und Navigation

**User Story:** Als Benutzer möchte ich, dass die Seitennummerierung in der erweiterten PDF korrekt ist, damit die Navigation einfach ist.

#### Acceptance Criteria

1. WHEN die erweiterte PDF generiert wird THEN soll die Seitennummerierung durchgehend von 1 bis N laufen
2. WHEN zusätzliche Seiten angehängt werden THEN soll der Footer "Seite X von Y" korrekt anzeigen
3. WHEN ein Inhaltsverzeichnis generiert wird THEN sollen alle Abschnitte mit korrekten Seitenzahlen aufgelistet werden
4. WHEN Produktdatenblätter mehrseitig sind THEN sollen deren Seiten in die Gesamtzählung einbezogen werden
5. IF die PDF mehr als 20 Seiten hat THEN soll eine Warnung angezeigt werden (Performance-Hinweis)

### Requirement 8: Konfigurierbare Reihenfolge der Zusatzseiten

**User Story:** Als Benutzer möchte ich die Reihenfolge der Zusatzseiten konfigurieren können, damit ich die Struktur der PDF anpassen kann.

#### Acceptance Criteria

1. WHEN die erweiterte PDF-UI geöffnet wird THEN soll eine Drag-and-Drop-Liste für die Reihenfolge der Zusatzseiten angezeigt werden
2. WHEN die Reihenfolge geändert wird THEN soll diese in der Session gespeichert werden
3. WHEN die PDF generiert wird THEN sollen die Zusatzseiten in der konfigurierten Reihenfolge angehängt werden
4. WHEN eine Vorlage gespeichert wird THEN soll die Reihenfolge mit gespeichert werden
5. IF keine Reihenfolge konfiguriert ist THEN soll eine Standard-Reihenfolge verwendet werden (Finanzierung → Produktdatenblätter → Firmendokumente)

### Requirement 9: Performance-Optimierung

**User Story:** Als System möchte ich die PDF-Generierung performant halten, damit auch erweiterte PDFs schnell erstellt werden.

#### Acceptance Criteria

1. WHEN große Produktdatenblätter eingebunden werden THEN sollen diese effizient gemerged werden
2. WHEN mehrere Dokumente angehängt werden THEN soll dies in einem Durchgang erfolgen
3. WHEN Bilder eingebunden werden THEN sollen diese auf eine angemessene Größe skaliert werden
4. WHEN die PDF mehr als 50 Seiten hat THEN soll eine Warnung angezeigt werden
5. IF die Generierung länger als 30 Sekunden dauert THEN soll ein Timeout-Mechanismus greifen

### Requirement 10: Keine Beeinträchtigung bestehender Funktionen

**User Story:** Als Benutzer möchte ich, dass die Standard-8-Seiten-PDF-Funktionalität unverändert bleibt, damit keine Regression entsteht.

#### Acceptance Criteria

1. WHEN die erweiterte Ausgabe deaktiviert ist THEN soll die Standard-PDF exakt wie bisher generiert werden
2. WHEN bestehende Tests ausgeführt werden THEN sollen diese weiterhin erfolgreich sein
3. WHEN die Standard-PDF generiert wird THEN soll die Performance unverändert sein
4. WHEN Fehler in der erweiterten Ausgabe auftreten THEN soll ein Fallback auf die Standard-PDF erfolgen
5. IF neue Funktionen hinzugefügt werden THEN sollen diese optional und abwärtskompatibel sein

### Requirement 11: Optimierte PDF-Erstellungs-UI

**User Story:** Als Benutzer möchte ich eine übersichtliche und intuitive UI für die PDF-Erstellung, damit ich schnell und einfach alle Optionen konfigurieren kann.

#### Acceptance Criteria

1. WHEN die PDF-UI geöffnet wird THEN soll sie in logische Abschnitte unterteilt sein (Basis-Einstellungen, Inhalte, Erweiterte Optionen)
2. WHEN viele Optionen verfügbar sind THEN sollen diese in Expander-Bereichen gruppiert sein
3. WHEN eine Option ausgewählt wird THEN soll eine Vorschau oder Beschreibung angezeigt werden
4. WHEN Vorlagen gespeichert werden THEN sollen diese mit aussagekräftigen Namen und Beschreibungen versehen werden können
5. IF die UI komplex wird THEN soll eine Suchfunktion für Optionen verfügbar sein

### Requirement 12: Diagramme und Visualisierungen optional einbinden

**User Story:** Als Benutzer möchte ich alle verfügbaren Diagramme und Visualisierungen optional in die PDF einbinden können, damit Kunden umfassende visuelle Informationen erhalten.

#### Acceptance Criteria

1. WHEN Berechnungsergebnisse Diagramme enthalten THEN sollen diese in der PDF-UI zur Auswahl angeboten werden
2. WHEN ein Diagramm ausgewählt wird THEN soll es als hochauflösendes Bild in die PDF eingebunden werden
3. WHEN mehrere Diagramme ausgewählt werden THEN sollen diese auf separaten Seiten oder in einem Grid-Layout angezeigt werden
4. WHEN 2D-Diagramme verfügbar sind THEN sollen folgende optional einbindbar sein:
   - Monatliche Produktion vs. Verbrauch
   - Stromkosten-Hochrechnung
   - Kumulierter Cashflow
   - Verbrauchsdeckung (Kreisdiagramm)
   - PV-Nutzung (Kreisdiagramm)
5. WHEN 3D-Diagramme verfügbar sind THEN sollen folgende optional einbindbar sein:
   - Tagesproduktion (3D)
   - Wochenproduktion (3D)
   - Jahresproduktion (3D-Balken)
   - Projektrendite-Matrix (3D)
   - Einspeisevergütung (3D)
   - Produktion vs. Verbrauch (3D)
   - Tarifvergleich (3D)
   - CO2-Ersparnis vs. Wert (3D)
   - Investitionsnutzwert (3D)
   - Speicherwirkung (3D)
   - Eigenverbrauch vs. Einspeisung (3D)
   - Stromkostensteigerung (3D)
   - Eigenverbrauchsgrad (3D)
   - ROI-Vergleich (3D)
   - Szenarienvergleich (3D)
   - Vorher/Nachher Stromkosten (3D)
   - Einnahmenprognose (3D)
6. WHEN PV-Visuals verfügbar sind THEN sollen folgende optional einbindbar sein:
   - Jahresproduktion
   - Break-Even-Analyse
   - Amortisationsdiagramm
7. IF ein Diagramm nicht verfügbar ist THEN soll es ausgegraut und mit Hinweis angezeigt werden

### Requirement 13: Diagramm-Qualität und Formatierung

**User Story:** Als Benutzer möchte ich, dass Diagramme in hoher Qualität und optimal formatiert in die PDF eingebunden werden, damit sie professionell aussehen.

#### Acceptance Criteria

1. WHEN ein Diagramm eingebunden wird THEN soll es mit mindestens 300 DPI Auflösung gerendert werden
2. WHEN ein Diagramm zu groß ist THEN soll es automatisch auf die Seitengröße skaliert werden (unter Beibehaltung des Seitenverhältnisses)
3. WHEN mehrere Diagramme auf einer Seite platziert werden THEN sollen diese in einem Grid-Layout (2x2 oder 3x2) angeordnet werden
4. WHEN ein Diagramm eine Überschrift hat THEN soll diese über dem Diagramm angezeigt werden
5. IF ein Diagramm eine Legende hat THEN soll diese lesbar und gut positioniert sein

### Requirement 14: Kategorisierung und Filterung von Diagrammen

**User Story:** Als Benutzer möchte ich Diagramme nach Kategorien filtern können, damit ich schnell die gewünschten Visualisierungen finde.

#### Acceptance Criteria

1. WHEN die Diagramm-Auswahl geöffnet wird THEN sollen Diagramme in Kategorien gruppiert sein:
   - Wirtschaftlichkeit (Cashflow, ROI, Break-Even, etc.)
   - Produktion & Verbrauch (Monatlich, Täglich, Jährlich)
   - Eigenverbrauch & Autarkie (Verbrauchsdeckung, PV-Nutzung, Speicherwirkung)
   - Finanzielle Analyse (Stromkosten, Einspeisevergütung, Einnahmen)
   - CO2 & Umwelt (CO2-Einsparung, Umweltbeitrag)
   - Vergleiche & Szenarien (Tarifvergleich, Szenarienvergleich, Vorher/Nachher)
2. WHEN eine Kategorie ausgewählt wird THEN sollen nur Diagramme dieser Kategorie angezeigt werden
3. WHEN "Alle auswählen" für eine Kategorie geklickt wird THEN sollen alle Diagramme dieser Kategorie ausgewählt werden
4. WHEN eine Suchfunktion verfügbar ist THEN soll nach Diagrammnamen gesucht werden können
5. IF keine Diagramme in einer Kategorie verfügbar sind THEN soll die Kategorie ausgegraut sein

### Requirement 15: Vorschau-Funktion für Diagramme

**User Story:** Als Benutzer möchte ich eine Vorschau der Diagramme sehen, bevor ich sie in die PDF einbinde, damit ich die richtige Auswahl treffe.

#### Acceptance Criteria

1. WHEN ein Diagramm in der Liste angezeigt wird THEN soll ein kleines Thumbnail sichtbar sein
2. WHEN auf ein Diagramm geklickt wird THEN soll eine größere Vorschau in einem Modal angezeigt werden
3. WHEN die Vorschau geöffnet ist THEN sollen Metadaten angezeigt werden (Größe, Auflösung, Datenquelle)
4. WHEN mehrere Diagramme ausgewählt sind THEN soll eine Vorschau der PDF-Seite mit allen Diagrammen angezeigt werden
5. IF die Vorschau nicht geladen werden kann THEN soll ein Platzhalter-Bild angezeigt werden

### Requirement 16: Batch-Operationen für Diagramme

**User Story:** Als Benutzer möchte ich mehrere Diagramme gleichzeitig auswählen oder abwählen können, damit ich Zeit spare.

#### Acceptance Criteria

1. WHEN die Diagramm-Auswahl geöffnet wird THEN soll ein "Alle auswählen" Button verfügbar sein
2. WHEN "Alle auswählen" geklickt wird THEN sollen alle verfügbaren Diagramme ausgewählt werden
3. WHEN "Alle abwählen" geklickt wird THEN sollen alle Diagramme abgewählt werden
4. WHEN eine Kategorie ausgewählt ist THEN soll "Kategorie auswählen" nur Diagramme dieser Kategorie auswählen
5. IF viele Diagramme ausgewählt sind THEN soll eine Warnung angezeigt werden (z.B. "15 Diagramme ausgewählt - PDF wird groß")

### Requirement 17: Diagramm-Anordnung und Layout-Optionen

**User Story:** Als Benutzer möchte ich die Anordnung der Diagramme in der PDF konfigurieren können, damit das Layout meinen Vorstellungen entspricht.

#### Acceptance Criteria

1. WHEN Diagramme ausgewählt sind THEN soll eine Layout-Option verfügbar sein:
   - Ein Diagramm pro Seite (Vollbild)
   - Zwei Diagramme pro Seite (2x1)
   - Vier Diagramme pro Seite (2x2)
   - Sechs Diagramme pro Seite (3x2)
2. WHEN ein Layout ausgewählt wird THEN soll eine Vorschau des Layouts angezeigt werden
3. WHEN Diagramme unterschiedliche Größen haben THEN sollen sie automatisch skaliert werden
4. WHEN ein Diagramm im Hochformat ist THEN soll es entsprechend gedreht oder angepasst werden
5. IF zu viele Diagramme für das gewählte Layout vorhanden sind THEN sollen automatisch weitere Seiten erstellt werden

### Requirement 18: Speicherung von Diagramm-Vorlagen

**User Story:** Als Benutzer möchte ich meine Diagramm-Auswahl als Vorlage speichern können, damit ich sie für zukünftige PDFs wiederverwenden kann.

#### Acceptance Criteria

1. WHEN Diagramme ausgewählt sind THEN soll ein "Als Vorlage speichern" Button verfügbar sein
2. WHEN eine Vorlage gespeichert wird THEN sollen folgende Informationen gespeichert werden:
   - Ausgewählte Diagramme
   - Layout-Einstellungen
   - Reihenfolge der Diagramme
   - Kategorisierung
3. WHEN eine Vorlage geladen wird THEN sollen alle gespeicherten Einstellungen wiederhergestellt werden
4. WHEN mehrere Vorlagen existieren THEN sollen diese in einer Dropdown-Liste verfügbar sein
5. IF eine Vorlage Diagramme enthält, die nicht mehr verfügbar sind THEN soll eine Warnung angezeigt werden

### Requirement 19: Dynamische Diagramm-Generierung

**User Story:** Als System möchte ich Diagramme dynamisch aus den Berechnungsergebnissen generieren, damit immer aktuelle Daten visualisiert werden.

#### Acceptance Criteria

1. WHEN Berechnungsergebnisse aktualisiert werden THEN sollen Diagramme automatisch neu generiert werden
2. WHEN ein Diagramm nicht generiert werden kann THEN soll ein Fallback-Bild oder Platzhalter verwendet werden
3. WHEN Diagramme gecacht werden THEN soll der Cache bei Datenänderungen invalidiert werden
4. WHEN Diagramme in die PDF eingebunden werden THEN sollen sie als hochauflösende PNG oder SVG exportiert werden
5. IF die Diagramm-Generierung fehlschlägt THEN soll dies geloggt werden, aber die PDF-Generierung fortgesetzt werden

### Requirement 20: Accessibility und Barrierefreiheit

**User Story:** Als Benutzer mit Sehbehinderung möchte ich, dass Diagramme mit Alt-Text versehen sind, damit ich die Informationen auch ohne visuelle Darstellung verstehen kann.

#### Acceptance Criteria

1. WHEN ein Diagramm in die PDF eingebunden wird THEN soll es mit einem beschreibenden Alt-Text versehen werden
2. WHEN ein Diagramm komplex ist THEN soll eine Textbeschreibung der wichtigsten Datenpunkte hinzugefügt werden
3. WHEN Farben in Diagrammen verwendet werden THEN sollen diese auch für Farbenblinde unterscheidbar sein
4. WHEN Diagramme Legenden haben THEN sollen diese klar lesbar und gut positioniert sein
5. IF ein Diagramm nicht barrierefrei ist THEN soll eine Warnung im Log erscheinen

### Requirement 21: Globale Einstellungen für PDF-Layouts und Themes

**User Story:** Als Administrator möchte ich in den Einstellungen PDF-Layouts und UI-Themes aktivieren/deaktivieren können, damit ich die Anwendung an unsere Corporate Identity anpassen kann.

#### Acceptance Criteria

1. WHEN die Admin-Einstellungen geöffnet werden THEN soll ein Bereich "PDF & UI Einstellungen" verfügbar sein
2. WHEN PDF-Layout-Optionen konfiguriert werden THEN sollen folgende Optionen verfügbar sein:
   - Standard-Layout (8 Seiten)
   - Erweiterte Layouts (mit Zusatzseiten)
   - Kompakt-Layout (reduzierte Seiten)
   - Custom-Layout (frei konfigurierbar)
3. WHEN ein Layout aktiviert wird THEN soll es in der PDF-UI zur Auswahl stehen
4. WHEN ein Layout deaktiviert wird THEN soll es in der PDF-UI nicht mehr sichtbar sein
5. IF kein Layout aktiviert ist THEN soll das Standard-Layout automatisch aktiviert werden

### Requirement 22: UI-Theme-System

**User Story:** Als Administrator möchte ich verschiedene UI-Themes für die Anwendung konfigurieren können, damit die Oberfläche zu unserer Marke passt.

#### Acceptance Criteria

1. WHEN die Theme-Einstellungen geöffnet werden THEN sollen vordefinierte Themes verfügbar sein:
   - Light Theme (Standard)
   - Dark Theme
   - Corporate Theme (anpassbar)
   - High Contrast Theme (Barrierefreiheit)
2. WHEN ein Theme ausgewählt wird THEN sollen folgende Elemente angepasst werden:
   - Primärfarbe
   - Sekundärfarbe
   - Hintergrundfarbe
   - Textfarbe
   - Akzentfarbe
3. WHEN ein Custom-Theme erstellt wird THEN sollen alle Farben individuell einstellbar sein
4. WHEN ein Theme gespeichert wird THEN soll es für alle Benutzer verfügbar sein
5. IF ein Theme gelöscht wird THEN soll automatisch auf das Standard-Theme zurückgefallen werden

### Requirement 23: PDF-Template-Auswahl und -Verwaltung

**User Story:** Als Administrator möchte ich verschiedene PDF-Templates verwalten und auswählen können, damit unterschiedliche Angebots-Designs möglich sind.

#### Acceptance Criteria

1. WHEN die Template-Verwaltung geöffnet wird THEN sollen alle verfügbaren PDF-Templates aufgelistet werden
2. WHEN ein neues Template hochgeladen wird THEN sollen folgende Informationen erfasst werden:
   - Template-Name
   - Beschreibung
   - Vorschau-Bild
   - Template-Dateien (PDF-Hintergründe für Seite 1-8)
   - Koordinaten-Dateien (YML für Textpositionen)
3. WHEN ein Template ausgewählt wird THEN soll es in der PDF-Generierung verwendet werden
4. WHEN mehrere Templates existieren THEN sollen diese in der PDF-UI zur Auswahl stehen
5. IF ein Template fehlerhaft ist THEN soll eine Validierung dies erkennen und melden

### Requirement 24: PDF-Design-Einstellungen funktionsfähig machen

**User Story:** Als Administrator möchte ich die PDF-Design-Einstellungen vollständig nutzen können, damit ich das Aussehen der PDFs anpassen kann.

#### Acceptance Criteria

1. WHEN die PDF-Design-Einstellungen geöffnet werden THEN sollen folgende Optionen verfügbar sein:
   - Primärfarbe (für Überschriften, Akzente)
   - Sekundärfarbe (für Tabellen, Hintergründe)
   - Schriftart (Auswahl aus verfügbaren Fonts)
   - Schriftgrößen (H1, H2, Body, Small)
   - Logo-Position (links, rechts, zentriert)
   - Footer-Format (mit/ohne Seitenzahl, Custom-Text)
2. WHEN eine Farbe geändert wird THEN soll eine Live-Vorschau angezeigt werden
3. WHEN Einstellungen gespeichert werden THEN sollen diese sofort in neuen PDFs angewendet werden
4. WHEN Einstellungen zurückgesetzt werden THEN sollen die Standard-Werte wiederhergestellt werden
5. IF ungültige Werte eingegeben werden THEN soll eine Validierung dies verhindern

### Requirement 25: Globale Diagramm-Farbeinstellungen

**User Story:** Als Administrator möchte ich die Farben aller Diagramme global einstellen können, damit sie zur Corporate Identity passen.

#### Acceptance Criteria

1. WHEN die Diagramm-Farbeinstellungen geöffnet werden THEN sollen folgende Optionen verfügbar sein:
   - Primäre Diagrammfarbe
   - Sekundäre Diagrammfarbe
   - Farbpalette (Auswahl aus vordefinierten Paletten)
   - Custom-Farbpalette (bis zu 10 Farben)
2. WHEN eine Farbpalette ausgewählt wird THEN sollen alle Diagramme diese Farben verwenden
3. WHEN eine Custom-Palette erstellt wird THEN soll eine Vorschau aller Diagramm-Typen angezeigt werden
4. WHEN Farben geändert werden THEN sollen diese in `visualization_settings` in `admin_settings` gespeichert werden
5. IF keine Farbeinstellungen vorhanden sind THEN sollen Standard-Plotly-Farben verwendet werden

### Requirement 26: Individuelle Diagramm-Farbkonfiguration

**User Story:** Als Administrator möchte ich für jedes Diagramm individuell Farben einstellen können, damit ich maximale Kontrolle über das Design habe.

#### Acceptance Criteria

1. WHEN die individuelle Diagramm-Konfiguration geöffnet wird THEN sollen alle Diagramm-Typen aufgelistet werden
2. WHEN ein Diagramm ausgewählt wird THEN sollen folgende Optionen verfügbar sein:
   - Diagramm-Typ (Bar, Line, Pie, 3D, etc.)
   - Farbschema (Global, Custom)
   - Primärfarbe (für Hauptdaten)
   - Sekundärfarbe (für Vergleichsdaten)
   - Hintergrundfarbe
   - Gitterfarbe
   - Textfarbe
3. WHEN Custom-Farben eingestellt werden THEN sollen diese die globalen Einstellungen überschreiben
4. WHEN "Auf Global zurücksetzen" geklickt wird THEN sollen die globalen Farben wiederhergestellt werden
5. IF ein Diagramm mehrere Datenreihen hat THEN sollen für jede Reihe individuelle Farben einstellbar sein

### Requirement 27: Farbpaletten-Bibliothek

**User Story:** Als Administrator möchte ich aus einer Bibliothek vordefinierter Farbpaletten wählen können, damit ich schnell professionelle Designs anwenden kann.

#### Acceptance Criteria

1. WHEN die Farbpaletten-Bibliothek geöffnet wird THEN sollen folgende Paletten verfügbar sein:
   - Corporate (Blau-Grau-Töne)
   - Eco (Grün-Töne für Nachhaltigkeit)
   - Energy (Orange-Gelb-Töne)
   - Professional (Dunkelblau-Grau)
   - Colorful (Bunte Palette)
   - Monochrome (Graustufen)
   - Accessible (Farbenblind-freundlich)
2. WHEN eine Palette ausgewählt wird THEN soll eine Vorschau mit Beispiel-Diagrammen angezeigt werden
3. WHEN eine Palette angewendet wird THEN sollen alle Diagramme diese Farben verwenden
4. WHEN eine Custom-Palette erstellt wird THEN soll sie zur Bibliothek hinzugefügt werden können
5. IF eine Palette gelöscht wird THEN soll eine Bestätigung erforderlich sein

### Requirement 28: Echtzeit-Vorschau für Design-Änderungen

**User Story:** Als Administrator möchte ich eine Echtzeit-Vorschau sehen, wenn ich Design-Einstellungen ändere, damit ich das Ergebnis sofort beurteilen kann.

#### Acceptance Criteria

1. WHEN Design-Einstellungen geändert werden THEN soll eine Live-Vorschau aktualisiert werden
2. WHEN Diagramm-Farben geändert werden THEN soll ein Beispiel-Diagramm mit den neuen Farben angezeigt werden
3. WHEN PDF-Design-Einstellungen geändert werden THEN soll eine Vorschau der ersten PDF-Seite angezeigt werden
4. WHEN ein Theme gewechselt wird THEN soll die gesamte UI sofort aktualisiert werden
5. IF die Vorschau nicht geladen werden kann THEN soll ein Platzhalter angezeigt werden

### Requirement 29: Import/Export von Design-Konfigurationen

**User Story:** Als Administrator möchte ich Design-Konfigurationen exportieren und importieren können, damit ich sie zwischen Installationen teilen kann.

#### Acceptance Criteria

1. WHEN die Export-Funktion verwendet wird THEN sollen folgende Daten exportiert werden:
   - PDF-Design-Einstellungen
   - Diagramm-Farbkonfigurationen
   - UI-Theme-Einstellungen
   - Custom-Farbpaletten
2. WHEN ein Export erstellt wird THEN soll eine JSON-Datei heruntergeladen werden
3. WHEN eine Konfiguration importiert wird THEN soll eine Validierung durchgeführt werden
4. WHEN der Import erfolgreich ist THEN sollen alle Einstellungen überschrieben werden (mit Bestätigung)
5. IF der Import fehlschlägt THEN soll eine detaillierte Fehlermeldung angezeigt werden

### Requirement 30: Versionierung von Design-Konfigurationen

**User Story:** Als Administrator möchte ich verschiedene Versionen von Design-Konfigurationen speichern können, damit ich zwischen verschiedenen Designs wechseln kann.

#### Acceptance Criteria

1. WHEN eine Design-Konfiguration gespeichert wird THEN soll sie mit einem Namen und einer Versionsnummer versehen werden
2. WHEN mehrere Versionen existieren THEN sollen diese in einer Liste angezeigt werden
3. WHEN eine ältere Version geladen wird THEN sollen alle Einstellungen dieser Version wiederhergestellt werden
4. WHEN eine Version gelöscht wird THEN soll eine Bestätigung erforderlich sein
5. IF keine Versionen vorhanden sind THEN soll automatisch eine "Default v1.0" Version erstellt werden
