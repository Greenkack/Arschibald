# Implementation Plan - Preismatrix-Erweiterung

## Übersicht

Diese Implementierung erweitert die Preismatrix-Funktionalität um eine vollständige INDEX-basierte Preisberechnung als Alternative zur Standardberechnung.

## Tasks

- [x] 1. Datenbank-Schema und Admin-Settings erweitern



  - Admin-Setting `pricing_calculation_mode` hinzufügen mit Werten "standard" | "matrix"
  - Getter/Setter-Funktionen in `database.py` implementieren
  - Default-Wert auf "standard" setzen für Rückwärtskompatibilität





  - _Requirements: 3.1, 3.2, 3.3, 8.1_

- [x] 2. Admin-Panel UI für Preisberechnungsmodus




  - [x] 2.1 Neue Sektion in "Erweiterte Einstellungen" erstellen

    - Radio-Button-Gruppe für Modus-Auswahl
    - Beschreibung der beiden Modi anzeigen
    - Speichern-Button mit Bestätigung
    - _Requirements: 3.1, 3.2_


  - [x] 2.2 Modus-Umschaltung implementieren

    - Laden des aktuellen Modus aus Datenbank
    - Speichern der Auswahl in Datenbank
    - Erfolgs-/Fehlermeldungen anzeigen
    - _Requirements: 3.3, 3.4, 3.5_

  - [x] 2.3 Validierung vor Aktivierung der Preismatrix

    - Prüfen ob aktive Preismatrix vorhanden
    - Warnung anzeigen wenn Matrix leer oder ungültig
    - Hinweis auf Matrix-Konfiguration
    - _Requirements: 7.1, 8.1_

- [x] 3. Excel Grid UI - Text/Zahlen-Eingabe erweitern





  - [x] 3.1 Zellen-Validierung für gemischte Eingabe


    - Funktion `_validate_cell_input_mixed()` erstellen
    - Text-Eingabe ohne Zahlen-Konvertierung erlauben
    - Typ-Erkennung (text, number, formula) implementieren
    - _Requirements: 1.1, 1.2, 1.3_

  - [x] 3.2 Cell-Modell für Text erweitern


    - `Cell.data_type` um "text" erweitern
    - `Cell.raw_input` für ursprüngliche Eingabe nutzen
    - Speicherung in Datenbank anpassen
    - _Requirements: 1.3, 1.4_

  - [x] 3.3 UI-Anpassungen für Text-Eingabe


    - Formelleiste für Text-Eingabe optimieren
    - Keine automatische Formatierung bei Text
    - Visuelle Unterscheidung Text vs. Zahl
    - _Requirements: 1.1, 1.2_

- [x] 4. Preismatrix-Struktur validieren und dokumentieren









  - [x] 4.1 Validierungs-Funktion erstellen


    - Spalte A muss numerische Werte enthalten (Modulanzahl)
    - Zeile 1 muss Text-Werte enthalten (Speichermodelle)
    - Mindestens eine "Kein Speicher" Spalte erforderlich
    - Preis-Zellen müssen Zahlen oder leer sein
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 7.1_

  - [x] 4.2 Hilfe-Text und Beispiel-Matrix


    - Dokumentation für Matrix-Struktur erstellen
    - Beispiel-Matrix mit Dummy-Daten bereitstellen
    - Tooltip-Hilfe in Excel Grid UI einbauen
    - _Requirements: 2.1, 2.2, 2.5_

- [x] 5. Preismatrix-Lookup-Logik implementieren





  - [x] 5.1 Modulanzahl-Suche mit Floor-Logik


    - Funktion `find_module_count_row()` erstellen
    - Exakte Übereinstimmung bevorzugen
    - Bei fehlender Zahl: Nächst-kleinere verwenden (Floor)
    - Fehler wenn keine passende Zeile gefunden
    - _Requirements: 4.1, 4.4, 7.2_

  - [x] 5.2 Speichermodell-Suche

    - Funktion `find_storage_column()` erstellen
    - Exakte Übereinstimmung mit Modellname
    - Bei `None`: "Kein Speicher" Spalte suchen
    - Fehler wenn Modell nicht gefunden
    - _Requirements: 4.2, 4.3, 7.3_

  - [x] 5.3 Preis-Lookup an Kreuzung

    - Funktion `lookup_price_by_intersection()` erstellen
    - Wert an (row, col) Kreuzung abrufen
    - Validierung: Muss Zahl sein
    - Fehler bei leerer oder ungültiger Zelle
    - _Requirements: 4.4, 4.6, 7.4, 7.5_

  - [x] 5.4 Haupt-Lookup-Funktion

    - Funktion `calculate_price_from_matrix()` erstellen
    - Kombiniert alle Lookup-Schritte
    - Gibt strukturiertes Ergebnis zurück
    - Umfassende Fehlerbehandlung
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_

- [x] 6. Solarcalculator - Preismatrix-Integration






  - [x] 6.1 Modus-Prüfung implementieren
    - Preisberechnungsmodus aus Datenbank laden
    - Verzweigung zwischen Standard und Matrix
    - UI-Hinweis auf aktiven Modus

    - _Requirements: 4.1, 5.1, 5.5_

  - [x] 6.2 Matrix-Preisberechnung

    - Funktion `get_total_price_with_matrix_mode()` erstellen
    - Basispreis aus Matrix abrufen
    - NUR Sonderprodukte/Extras/Dienstleistungen addieren
    - KEINE Standard-Aufschläge (Montage, Installation)
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 6.1, 6.2, 6.3, 6.4_

  - [x] 6.3 UI-Anpassungen für Matrix-Modus


    - Preisaufschlüsselung anzeigen (Basis + Extras)
    - Matrix-Info anzeigen (welche Zeile/Spalte verwendet)
    - Hinweis dass Standard-Aufschläge deaktiviert sind
    - _Requirements: 6.6_

  - [x] 6.4 Standard-Berechnung deaktivieren


    - Einzelprodukt-Preise ignorieren im Matrix-Modus
    - Montage-/Installations-Aufschläge deaktivieren
    - Nur explizite Extras berücksichtigen
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [x] 7. Zusatzkosten-Logik für Sonderprodukte





  - [x] 7.1 Sonderprodukte identifizieren


    - Kennzeichnung von Sonderprodukten in Produktdatenbank
    - Filter-Funktion für Sonderprodukte
    - _Requirements: 6.1, 6.2, 6.3_

  - [x] 7.2 Extras und Dienstleistungen


    - Zusätzliche Dienstleistungen erfassen
    - Extras-Preise berechnen
    - Rabatte und Aufpreise anwenden
    - _Requirements: 6.4, 6.5_

  - [x] 7.3 Preisaufschlüsselung


    - Detaillierte Aufschlüsselung erstellen
    - Basispreis (Matrix) + Extras separat anzeigen
    - Gesamtpreis berechnen
    - _Requirements: 6.6_

- [ ] 8. Fehlerbehandlung und Validierung
  - [ ] 8.1 Fehler-Typen definieren
    - Matrix nicht gefunden
    - Modulanzahl nicht in Matrix
    - Speichermodell nicht in Matrix
    - Zelle leer oder ungültig
    - Zelle enthält Text statt Zahl
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

  - [ ] 8.2 Benutzerfreundliche Fehlermeldungen
    - Klare Fehlertexte formulieren
    - Lösungsvorschläge anbieten
    - Hinweise auf Matrix-Konfiguration
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

  - [ ] 8.3 Fallback-Mechanismen
    - Bei Fehler: Warnung anzeigen
    - Optional: Fallback auf Standardberechnung
    - Admin-Benachrichtigung bei kritischen Fehlern
    - _Requirements: 8.5_

- [ ] 9. Rückwärtskompatibilität sicherstellen
  - [ ] 9.1 Bestehende Funktionen testen
    - Standardberechnung muss unverändert funktionieren
    - Keine Breaking Changes in APIs
    - Datenbank-Migration ohne Datenverlust
    - _Requirements: 8.1, 8.2, 8.3, 8.4_

  - [ ] 9.2 Default-Verhalten
    - Standard-Modus als Default
    - Bestehende Installationen nicht beeinflussen
    - Opt-in für Preismatrix-Modus
    - _Requirements: 8.2, 8.5_

- [ ]* 10. Testing und Qualitätssicherung
  - [ ]* 10.1 Unit Tests für Lookup-Logik
    - Test: Exakte Modulanzahl-Übereinstimmung
    - Test: Floor-Logik bei fehlender Modulanzahl
    - Test: Speichermodell-Suche
    - Test: "Kein Speicher" Fallback
    - Test: Ungültige Eingaben

  - [ ]* 10.2 Integrationstests
    - Test: End-to-End Preisberechnung im Matrix-Modus
    - Test: Modus-Umschaltung
    - Test: Fehlerszenarien
    - Test: Rückwärtskompatibilität

  - [ ]* 10.3 Manuelle Tests
    - Test: Admin-Panel UI
    - Test: Excel Grid Text-Eingabe
    - Test: Solarcalculator mit verschiedenen Konfigurationen
    - Test: Fehler-UI und Meldungen

- [ ]* 11. Dokumentation
  - [ ]* 11.1 Benutzer-Dokumentation
    - Anleitung zur Preismatrix-Konfiguration
    - Beispiele für Matrix-Struktur
    - Erklärung der beiden Modi

  - [ ]* 11.2 Entwickler-Dokumentation
    - API-Dokumentation für neue Funktionen
    - Architektur-Diagramme
    - Code-Kommentare
