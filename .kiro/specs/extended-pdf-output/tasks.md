# Implementation Plan: Erweiterte PDF-Ausgabe

## Overview

Dieser Implementierungsplan erweitert das bestehende 8-Seiten-PDF-System um optionale Zusatzfunktionen. Die Standard-PDF-Ausgabe bleibt vollständig unverändert und funktionsfähig. Alle neuen Features sind optional und werden nur aktiviert, wenn der Benutzer dies explizit wünscht.

**WICHTIG:** Die normale/standard PDF-Ausgabe wird NICHT angetasst! Sie funktioniert einwandfrei und bleibt unverändert.

---

## Tasks

- [x] 1. Erstelle Extended PDF Generator Modul (NEUE Datei)

  - Erstelle neue Datei `extended_pdf_generator.py`
  - Implementiere `ExtendedPDFGenerator` Hauptklasse
  - Implementiere `FinancingPageGenerator` Klasse
  - Implementiere `ProductDatasheetMerger` Klasse
  - Implementiere `CompanyDocumentMerger` Klasse
  - Implementiere `ChartPageGenerator` Klasse
  - Keine Änderungen an bestehenden PDF-Dateien
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 2. Erweitere PDF-UI mit optionaler Extended-Output-Sektion

  - [x] 2.1 Füge Extended-Output-Toggle in `pdf_ui.py` hinzu

    - Füge Checkbox "Erweiterte PDF-Ausgabe aktivieren" hinzu
    - Standard: deaktiviert (False)
    - Nur sichtbar wenn aktiviert
    - _Requirements: 1.1, 1.2_
  
  - [x] 2.2 Implementiere Finanzierungsdetails-Auswahl

    - Erstelle Expander "Finanzierungsdetails"
    - Lade Finanzierungsoptionen aus `payment_terms`
    - Zeige verfügbare Optionen zur Auswahl
    - _Requirements: 2.1, 2.2, 2.3_
  
  - [x] 2.3 Implementiere Produktdatenblatt-Auswahl

    - Erstelle Expander "Produktdatenblätter"
    - Lade Produkte mit Datenblättern aus DB
    - Multi-Select für Produktauswahl
    - _Requirements: 3.1, 3.2, 3.3_
  
  - [x] 2.4 Implementiere Firmendokument-Auswahl

    - Erstelle Expander "Firmendokumente"
    - Lade Firmendokumente aus DB
    - Multi-Select für Dokumentauswahl
    - _Requirements: 4.1, 4.2, 4.3_
  
  - [x] 2.5 Implementiere kategorisierte Diagramm-Auswahl

    - Erstelle Expander "Diagramme & Visualisierungen"
    - Gruppiere Diagramme nach Kategorien
    - Implementiere Tab-Navigation für Kategorien
    - Füge "Alle auswählen/abwählen" Buttons hinzu
    - Implementiere Vorschau-Funktion
    - _Requirements: 12.1, 12.2, 12.3, 14.1, 14.2, 15.1_

- [x] 3. Implementiere Finanzierungsseiten-Generator

  - [x] 3.1 Erstelle `FinancingPageGenerator` Klasse

    - Implementiere `generate()` Methode
    - Implementiere `_get_financing_options()` mit echten Keys
    - Verwende nur Keys aus `payment_terms` Admin-Settings
    - _Requirements: 2.1, 2.2, 5.1, 5.2_
  
  - [x] 3.2 Implementiere Finanzierungsübersicht-Seite

    - Zeichne Titel und Untertitel
    - Erstelle Finanzierungsoptionen-Boxen
    - Zeige Laufzeit, Zinssatz, monatliche Rate
    - _Requirements: 2.2, 2.3_
  
  - [x] 3.3 Implementiere detaillierte Finanzierungsberechnung

    - Implementiere Annuitätenformel für monatliche Raten
    - Erstelle Berechnungstabelle
    - Zeige Gesamtkosten und Zinskosten
    - _Requirements: 2.2, 2.3, 2.4_

- [x] 4. Implementiere Produktdatenblatt-Merger

  - [x] 4.1 Erstelle `ProductDatasheetMerger` Klasse

    - Implementiere `merge()` Methode
    - Implementiere `_load_datasheet()` mit echten DB-Queries
    - Verwende `product_db.get_product_by_id()`
    - _Requirements: 3.1, 3.2, 5.1, 5.2_
  
  - [x] 4.2 Implementiere PDF-Merge für Datenblätter

    - Lade PDF-Datenblätter aus Dateisystem
    - Merge alle Seiten in Output-PDF
    - Fehlerbehandlung für fehlende Dateien
    - _Requirements: 3.3, 3.4, 6.1, 6.2_
  
  - [x] 4.3 Implementiere Bild-zu-PDF-Konvertierung

    - Konvertiere Bild-Datenblätter zu PDF
    - Zentriere Bilder auf Seite
    - Skaliere auf angemessene Größe
    - _Requirements: 3.5, 9.3_

- [x] 5. Implementiere Firmendokument-Merger

  - [x] 5.1 Erstelle `CompanyDocumentMerger` Klasse

    - Implementiere `merge()` Methode
    - Implementiere `_load_document()` mit echten DB-Queries
    - Verwende `database.get_company_document_file_path()`
    - _Requirements: 4.1, 4.2, 5.1, 5.2_
  
  - [x] 5.2 Implementiere PDF-Merge für Dokumente

    - Lade Dokumente aus Dateisystem
    - Merge alle Seiten in Output-PDF
    - Fehlerbehandlung für fehlende Dateien
    - _Requirements: 4.3, 4.4, 6.1, 6.2_

- [x] 6. Implementiere Chart-Page-Generator

  - [x] 6.1 Erstelle `ChartPageGenerator` Klasse

    - Implementiere `generate()` Methode
    - Implementiere Layout-Optionen (1, 2, 4 pro Seite)
    - Verwende nur echte Chart-Keys aus `analysis_results`
    - _Requirements: 12.1, 12.2, 12.3, 5.1, 5.2_
  
  - [x] 6.2 Implementiere "Ein Diagramm pro Seite" Layout

    - Zeichne Diagramm-Titel
    - Zeichne Diagramm mit maximaler Größe
    - Behalte Seitenverhältnis bei
    - _Requirements: 12.3, 13.1, 13.2_
  
  - [x] 6.3 Implementiere "Zwei Diagramme pro Seite" Layout

    - Teile Seite in zwei Bereiche (oben/unten)
    - Zeichne Diagramme in jeweiligen Bereichen
    - _Requirements: 12.3, 17.1, 17.2_
  
  - [x] 6.4 Implementiere "Vier Diagramme pro Seite" Layout

    - Teile Seite in 2x2 Grid
    - Zeichne Diagramme in Grid-Zellen
    - _Requirements: 12.3, 17.1, 17.2_
  
  - [x] 6.5 Implementiere Diagramm-Namen-Mapping

    - Erstelle Mapping von Chart-Keys zu freundlichen Namen
    - Verwende exakte Keys aus `pdf_generator.py`
    - Keine erfundenen Keys
    - _Requirements: 5.1, 5.2, 5.3_
-

- [x] 7. Integriere Extended PDF Generator in Haupt-PDF-Flow

  - [x] 7.1 Erweitere `generate_offer_pdf()` in `pdf_generator.py`

    - Prüfe ob `extended_output_enabled` in Optionen
    - Wenn False: Standard-8-Seiten-PDF (unverändert)
    - Wenn True: Generiere Extended Pages und merge
    - _Requirements: 1.3, 1.4, 10.1, 10.2_
  
  - [x] 7.2 Implementiere PDF-Merge-Funktion

    - Merge Base-PDF (8 Seiten) mit Extended Pages
    - Update Seitennummerierung
    - Behalte alle Metadaten
    - _Requirements: 7.1, 7.2, 7.3_
  
  - [x] 7.3 Implementiere Fallback-Mechanismus

    - Bei Fehler in Extended Generation: Fallback auf Base-PDF
    - Logge Fehler aber breche nicht ab
    - Zeige Warnung in UI
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 10.4_

- [x] 8. Erstelle Admin-Settings-UI für PDF & Design (NEUE Datei)

  - Erstelle neue Datei `admin_pdf_settings_ui.py`
  - Implementiere `render_pdf_settings_ui()` Hauptfunktion
  - Implementiere Tab-Navigation für Einstellungsbereiche
  - Keine Änderungen an bestehenden Admin-UIs
  - _Requirements: 21.1, 21.2, 11.1_

- [x] 9. Implementiere PDF-Design-Einstellungen UI

  - [x] 9.1 Implementiere Farbauswahl

    - Color Picker für Primär- und Sekundärfarbe
    - Speichere in `pdf_design_settings`
    - _Requirements: 24.1, 24.2_
  
  - [x] 9.2 Implementiere Schriftart-Einstellungen

    - Dropdown für Schriftart-Auswahl
    - Number Inputs für Schriftgrößen
    - _Requirements: 24.1, 24.2_
  
  - [x] 9.3 Implementiere Logo & Layout-Einstellungen

    - Dropdown für Logo-Position
    - Dropdown für Footer-Format
    - Text Input für Custom Footer
    - _Requirements: 24.1, 24.2_
  
  - [x] 9.4 Implementiere Wasserzeichen-Einstellungen

    - Checkbox für Aktivierung
    - Text Input für Wasserzeichen-Text
    - Slider für Transparenz
    - _Requirements: 24.1, 24.2_
  
  - [x] 9.5 Implementiere Live-Vorschau

    - Zeige Vorschau mit aktuellen Einstellungen
    - Update bei Änderungen
    - _Requirements: 28.1, 28.2, 28.3_

- [x] 10. Implementiere Diagramm-Farbeinstellungen UI

  - [x] 10.1 Implementiere globale Farbeinstellungen

    - Color Picker für 6 globale Farben
    - Speichere in `visualization_settings.global_chart_colors`
    - _Requirements: 25.1, 25.2, 25.3, 25.4_
  
  - [x] 10.2 Implementiere Farbpaletten-Bibliothek

    - Zeige vordefinierte Paletten (Corporate, Eco, Energy, Accessible)
    - "Palette anwenden" Button
    - Color Swatches für Vorschau
    - _Requirements: 27.1, 27.2, 27.3_
  
  - [x] 10.3 Implementiere individuelle Diagramm-Konfiguration

    - Kategorie-Auswahl für Diagramme
    - Diagramm-Auswahl innerhalb Kategorie
    - "Globale Farben verwenden" Toggle
    - Custom-Farben für jedes Diagramm
    - "Auf Global zurücksetzen" Button
    - _Requirements: 26.1, 26.2, 26.3, 26.4, 26.5_
-

- [x] 11. Implementiere UI-Theme-Einstellungen

  - [x] 11.1 Implementiere Theme-Auswahl

    - Dropdown für verfügbare Themes
    - "Theme aktivieren" Button
    - _Requirements: 22.1, 22.2_
  
  - [x] 11.2 Implementiere Theme-Vorschau

    - HTML-Vorschau mit Theme-Farben
    - Zeige alle Theme-Elemente
    - _Requirements: 28.1, 28.2, 28.4_
  
  - [x] 11.3 Implementiere Theme-Editor

    - Color Picker für alle Theme-Farben
    - "Theme speichern" Button
    - _Requirements: 22.2, 22.3, 22.4_

- [x] 12. Implementiere PDF-Template-Verwaltung UI

  - [x] 12.1 Implementiere Template-Auswahl

    - Dropdown für verfügbare Templates
    - "Template aktivieren" Button
    - _Requirements: 23.1, 23.2, 23.4_
  
  - [x] 12.2 Implementiere Template-Details-Anzeige

    - Zeige Name, Beschreibung
    - Zeige Dateipfade
    - _Requirements: 23.2, 23.3_

  - [x] 12.3 Implementiere "Neues Template hinzufügen"

    - Text Inputs für Template-Informationen
    - Text Inputs für Dateipfade
    - "Template hinzufügen" Button
    - _Requirements: 23.2, 23.3, 23.5_

- [-] 13. Implementiere Layout-Optionen-Verwaltung UI

  - [x] 13.1 Implementiere Layout-Liste

    - Zeige alle verfügbaren Layouts
    - Expander für jedes Layout
    - _Requirements: 21.2, 21.3, 21.4_
  
  - [x] 13.2 Implementiere Layout-Konfiguration

    - Checkbox "Aktiviert"
    - Checkbox "Als Standard"
    - "Speichern" Button
    - _Requirements: 21.2, 21.3, 21.4, 21.5_

- [x] 14. Implementiere Import/Export für Design-Konfigurationen

  - [x] 14.1 Implementiere Export-Funktion

    - Sammle alle Design-Einstellungen
    - Erstelle JSON-Datei
    - Download-Button
    - _Requirements: 29.1, 29.2_
  
  - [x] 14.2 Implementiere Import-Funktion

    - File Upload für JSON
    - Validierung der Konfiguration
    - Bestätigungs-Dialog
    - Überschreibe Einstellungen
    - _Requirements: 29.3, 29.4, 29.5_

- [x] 15. Implementiere Versionierung von Design-Konfigurationen

  - [x] 15.1 Implementiere Version-Speichern

    - Input für Versionsname
    - Snapshot aller Einstellungen
    - Speichere in `design_config_versions`
    - _Requirements: 30.1, 30.5_
  
  - [x] 15.2 Implementiere Version-Laden

    - Dropdown für verfügbare Versionen
    - "Version laden" Button
    - Wiederherstellung aller Einstellungen
    - _Requirements: 30.2, 30.3_
  
  - [x] 15.3 Implementiere Version-Löschen

    - "Version löschen" Button
    - Bestätigungs-Dialog
    - _Requirements: 30.4_

- [x] 16. Implementiere Fehlerbehandlung und Logging

  - [x] 16.1 Erstelle `ExtendedPDFLogger` Klasse

    - Implementiere `log_error()` Methode
    - Implementiere `log_warning()` Methode
    - Implementiere `get_summary()` Methode
    - _Requirements: 6.1, 6.2, 6.5_
  
  - [x] 16.2 Integriere Logging in alle Komponenten

    - Logge Fehler bei Datei-Laden
    - Logge Warnungen bei fehlenden Daten
    - Logge Info bei erfolgreichen Operationen
    - _Requirements: 6.1, 6.2, 6.3, 6.4_
  
  - [x] 16.3 Implementiere Graceful Degradation

    - Fallback auf Base-PDF bei Fehlern
    - Zeige Warnungen in UI
    - Breche nicht ab bei Teilfehlern
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 10.4_

- [x] 17. Implementiere Performance-Optimierung

  - [x] 17.1 Implementiere Chart-Caching

    - Erstelle `ChartCache` Klasse
    - Cache gerenderte Charts
    - Invalidiere bei Datenänderungen
    - _Requirements: 9.1, 9.2, 19.3_
  
  - [x] 17.2 Implementiere effizientes PDF-Merging

    - Merge in einem Durchgang
    - Vermeide mehrfaches Laden
    - _Requirements: 9.2, 9.3_
  
  - [x] 17.3 Implementiere Bild-Skalierung

    - Skaliere große Bilder vor Einbindung
    - Optimiere Auflösung (300 DPI)
    - _Requirements: 9.3, 13.1, 13.2_

- [x] 18. Erstelle Unit Tests

  - [x] 18.1 Teste Extended PDF Options Parsing

    - Teste Optionen-Dictionary
    - Teste Default-Werte

    - _Requirements: 8.1_
  
  - [x] 18.2 Teste Financing Page Generation

    - Teste mit echten Finanzierungsdaten
    - Teste Berechnungen
    - _Requirements: 2.1, 2.2, 2.3_
  
  - [x] 18.3 Teste Chart Layout Generierung

    - Teste 1, 2, 4 pro Seite Layouts
    - Teste Seitenanzahl
    - _Requirements: 12.3, 17.1, 17.2_
  
  - [x] 18.4 Teste Fehlerbehandlung

    - Teste Fallback bei fehlenden Dateien
    - Teste Fallback bei Fehlern
    - _Requirements: 6.1, 6.2, 6.3_

- [x] 19. Erstelle Integrationstests

  - [x] 19.1 Teste vollständige Extended PDF Generierung

    - Teste mit allen Optionen aktiviert
    - Prüfe Seitenanzahl
    - Prüfe Inhalt
    - _Requirements: 1.1, 1.2, 1.3, 1.4_
  
  - [x] 19.2 Teste Standard-PDF bleibt unverändert

    - Generiere PDF mit `extended_output_enabled=False`
    - Vergleiche mit vorherigem Standard-PDF
    - Stelle sicher: KEINE Änderungen
    - _Requirements: 10.1, 10.2, 10.3_

  - [x] 19.3 Teste Performance

    - Messe Generierungszeit
    - Prüfe < 30 Sekunden für typische Extended PDF
    - _Requirements: 9.1, 9.4_

- [x] 20. Dokumentation und Finalisierung

  - [x] 20.1 Dokumentiere neue Module

    - Docstrings für alle Klassen
    - Docstrings für alle Methoden
    - Beispiele für Verwendung
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_
  
  - [x] 20.2 Erstelle Benutzer-Dokumentation

    - Anleitung für Extended PDF Aktivierung
    - Anleitung für Design-Einstellungen
    - Screenshots der UI
    - _Requirements: 11.1, 11.2_
  
  - [x] 20.3 Erstelle Admin-Dokumentation

    - Anleitung für Theme-Verwaltung
    - Anleitung für Template-Verwaltung
    - Anleitung für Farbkonfiguration
    - _Requirements: 21.1, 22.1, 23.1, 24.1, 25.1, 26.1_

---

## Notes

- **KRITISCH:** Die normale/standard PDF-Ausgabe (8 Seiten) wird NICHT angetasst!
- **KRITISCH:** Alle neuen Features sind optional und standardmäßig deaktiviert
- **KRITISCH:** Nur echte Keys aus dem System verwenden (keine erfundenen)
- **WICHTIG:** Fehlerbehandlung mit Fallback auf Standard-PDF
- **WICHTIG:** Performance-Optimierung durch Caching
- **WICHTIG:** Umfassende Tests für Rückwärtskompatibilität
- **REMINDER:** Neue Dateien erstellen, bestehende nicht ändern (außer Integration)
