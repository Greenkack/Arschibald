# Task 14: Import/Export - Verifikations-Checkliste

## Übersicht

Diese Checkliste hilft bei der manuellen Verifikation der Import/Export-Funktionalität.

## Voraussetzungen

- [ ] Streamlit-Anwendung läuft
- [ ] Admin-Panel ist zugänglich
- [ ] Datenbank ist verfügbar
- [ ] Schreibrechte für Downloads vorhanden

## Test 1: Export-Funktion (Task 14.1)

### 1.1 UI-Zugriff

- [ ] Admin-Panel öffnen
- [ ] "PDF & Design Einstellungen" auswählen
- [ ] Tab "💾 Import/Export" ist sichtbar
- [ ] Tab öffnet sich ohne Fehler

### 1.2 Export-Sektion

- [ ] Export-Sektion ist auf der linken Seite
- [ ] Überschrift "📤 Export" ist sichtbar
- [ ] Beschreibungstext ist vorhanden
- [ ] Expander "📋 Was wird exportiert?" ist vorhanden

### 1.3 Export-Inhalt

- [ ] Expander öffnen
- [ ] Liste zeigt alle Einstellungsbereiche:
  - [ ] PDF-Design-Einstellungen
  - [ ] Diagramm-Farbkonfigurationen
  - [ ] UI-Theme-Einstellungen
  - [ ] PDF-Template-Einstellungen
  - [ ] Layout-Optionen
  - [ ] Custom-Farbpaletten

### 1.4 Export-Prozess

- [ ] Button "📥 Konfiguration exportieren" klicken
- [ ] Erfolgsmeldung erscheint
- [ ] Download-Button "💾 JSON-Datei herunterladen" erscheint
- [ ] Expander "👁️ Vorschau der exportierten Daten" erscheint

### 1.5 Export-Vorschau

- [ ] Vorschau-Expander öffnen
- [ ] JSON-Daten werden angezeigt
- [ ] Alle Einstellungsbereiche sind enthalten
- [ ] `_metadata` ist vorhanden mit:
  - [ ] `export_date`
  - [ ] `version`
  - [ ] `description`

### 1.6 Download

- [ ] Download-Button klicken
- [ ] Datei wird heruntergeladen
- [ ] Dateiname enthält Zeitstempel (z.B. `design_config_20251009_133525.json`)
- [ ] Datei ist im JSON-Format
- [ ] Datei kann mit Texteditor geöffnet werden

### 1.7 Export-Datenintegrität

- [ ] JSON-Datei öffnen
- [ ] Alle erwarteten Keys sind vorhanden
- [ ] Werte entsprechen aktuellen Einstellungen
- [ ] Keine fehlenden oder null-Werte (außer wenn erwartet)
- [ ] Metadaten sind korrekt

## Test 2: Import-Funktion (Task 14.2)

### 2.1 Import-Sektion

- [ ] Import-Sektion ist auf der rechten Seite
- [ ] Überschrift "📥 Import" ist sichtbar
- [ ] Beschreibungstext ist vorhanden
- [ ] File-Upload ist vorhanden

### 2.2 Datei-Upload

- [ ] "JSON-Datei auswählen" klicken
- [ ] Datei-Dialog öffnet sich
- [ ] Nur .json Dateien werden akzeptiert
- [ ] Exportierte Datei auswählen
- [ ] Datei wird hochgeladen

### 2.3 Automatische Validierung

- [ ] Nach Upload startet Validierung automatisch
- [ ] Bei gültiger Datei: Erfolgsmeldung erscheint
- [ ] Bei ungültiger Datei: Fehlermeldung erscheint

### 2.4 Datei-Informationen (bei gültiger Datei)

- [ ] Expander "ℹ️ Datei-Informationen" erscheint
- [ ] Export-Datum wird angezeigt
- [ ] Version wird angezeigt
- [ ] Beschreibung wird angezeigt

### 2.5 Import-Vorschau

- [ ] Expander "📋 Was wird importiert?" erscheint
- [ ] Anzahl der Einstellungsbereiche wird angezeigt
- [ ] Liste aller zu importierenden Bereiche wird angezeigt
- [ ] Alle Bereiche haben ✓-Symbol

### 2.6 Daten-Vorschau

- [ ] Expander "👁️ Vorschau der importierten Daten" erscheint
- [ ] JSON-Daten werden angezeigt (ohne Metadaten)
- [ ] Daten sind lesbar und korrekt formatiert

### 2.7 Warnung und Bestätigung

- [ ] Warnung "⚠️ Achtung: Der Import überschreibt..." wird angezeigt
- [ ] Bestätigungs-Checkbox ist vorhanden
- [ ] Checkbox ist standardmäßig nicht aktiviert
- [ ] Import-Button ist deaktiviert

### 2.8 Import-Prozess

- [ ] Bestätigungs-Checkbox aktivieren
- [ ] Import-Button wird aktiviert
- [ ] Button "✓ Konfiguration importieren" klicken
- [ ] Erfolgsmeldung erscheint
- [ ] Seite wird automatisch neu geladen

### 2.9 Import-Verifikation

- [ ] Nach Reload: Einstellungen prüfen
- [ ] PDF-Design-Einstellungen wurden übernommen
- [ ] Diagramm-Farben wurden übernommen
- [ ] UI-Theme wurde übernommen
- [ ] Alle importierten Werte sind korrekt

## Test 3: Validierung

### 3.1 Ungültige JSON-Datei

- [ ] Textdatei mit ungültigem JSON erstellen
- [ ] Datei hochladen
- [ ] Fehlermeldung "Fehler beim Parsen der JSON-Datei" erscheint
- [ ] Import-Button bleibt deaktiviert

### 3.2 Leere Konfiguration

- [ ] JSON-Datei mit `{}` erstellen
- [ ] Datei hochladen
- [ ] Fehlermeldung "Ungültige Konfigurationsdatei!" erscheint
- [ ] Expander "🔍 Validierungsfehler" erscheint
- [ ] Fehler "Keine gültigen Einstellungen gefunden" wird angezeigt

### 3.3 Ungültige Datentypen

- [ ] JSON-Datei mit falschen Datentypen erstellen (z.B. `"global_chart_colors": "not a list"`)
- [ ] Datei hochladen
- [ ] Validierungsfehler wird angezeigt
- [ ] Spezifischer Fehler wird genannt

### 3.4 Fehlende Keys

- [ ] JSON-Datei ohne erforderliche Keys erstellen
- [ ] Datei hochladen
- [ ] Validierungsfehler wird angezeigt
- [ ] Import wird verhindert

## Test 4: Fehlerbehandlung

### 4.1 Export-Fehler

- [ ] Datenbank-Verbindung unterbrechen (simuliert)
- [ ] Export versuchen
- [ ] Fehlermeldung erscheint
- [ ] Anwendung stürzt nicht ab

### 4.2 Import-Fehler

- [ ] Schreibrechte entziehen (simuliert)
- [ ] Import versuchen
- [ ] Fehlermeldung erscheint
- [ ] Anwendung stürzt nicht ab

### 4.3 Große Dateien

- [ ] Sehr große JSON-Datei erstellen (> 1 MB)
- [ ] Datei hochladen
- [ ] Upload funktioniert oder Fehlermeldung erscheint
- [ ] Keine Performance-Probleme

## Test 5: Benutzerfreundlichkeit

### 5.1 Hilfe-Sektion

- [ ] Expander "ℹ️ Hilfe & Informationen" öffnen
- [ ] Hilfetext ist vorhanden und verständlich
- [ ] Alle Funktionen werden erklärt
- [ ] Verwendungszwecke werden genannt
- [ ] Hinweise sind hilfreich

### 5.2 Fehlermeldungen

- [ ] Alle Fehlermeldungen sind klar und verständlich
- [ ] Fehlermeldungen enthalten hilfreiche Informationen
- [ ] Keine technischen Jargon-Begriffe (außer wenn nötig)

### 5.3 Erfolgsmeldungen

- [ ] Erfolgsmeldungen sind positiv formuliert
- [ ] Nächste Schritte werden genannt
- [ ] Keine verwirrenden Meldungen

### 5.4 UI-Layout

- [ ] Zwei-Spalten-Layout ist übersichtlich
- [ ] Export und Import sind klar getrennt
- [ ] Buttons sind gut sichtbar
- [ ] Expander sind sinnvoll eingesetzt

## Test 6: Datenintegrität

### 6.1 Vollständiger Zyklus

- [ ] Aktuelle Einstellungen notieren
- [ ] Einstellungen exportieren
- [ ] Einstellungen ändern
- [ ] Exportierte Datei importieren
- [ ] Einstellungen wurden wiederhergestellt
- [ ] Alle Werte sind identisch mit Notizen

### 6.2 Teilweise Konfiguration

- [ ] JSON-Datei mit nur einem Einstellungsbereich erstellen
- [ ] Datei importieren
- [ ] Nur dieser Bereich wurde überschrieben
- [ ] Andere Bereiche bleiben unverändert

### 6.3 Metadaten

- [ ] Metadaten werden beim Export hinzugefügt
- [ ] Metadaten werden beim Import ignoriert (nicht gespeichert)
- [ ] Metadaten beeinflussen Import nicht

## Test 7: Performance

### 7.1 Export-Performance

- [ ] Export-Zeit messen
- [ ] Export dauert < 1 Sekunde
- [ ] Keine spürbaren Verzögerungen

### 7.2 Import-Performance

- [ ] Import-Zeit messen
- [ ] Import dauert < 2 Sekunden
- [ ] Reload erfolgt schnell

### 7.3 Validierungs-Performance

- [ ] Validierungs-Zeit messen
- [ ] Validierung dauert < 0.5 Sekunden
- [ ] Keine spürbaren Verzögerungen

## Test 8: Sicherheit

### 8.1 Code-Injection

- [ ] JSON-Datei mit JavaScript-Code erstellen
- [ ] Datei importieren
- [ ] Code wird nicht ausgeführt
- [ ] Nur Daten werden importiert

### 8.2 SQL-Injection

- [ ] JSON-Datei mit SQL-Befehlen erstellen
- [ ] Datei importieren
- [ ] SQL wird nicht ausgeführt
- [ ] Daten werden sicher gespeichert

### 8.3 Bestätigung

- [ ] Import ohne Bestätigung versuchen
- [ ] Import-Button bleibt deaktiviert
- [ ] Import ist nicht möglich

## Test 9: Edge Cases

### 9.1 Sehr lange Strings

- [ ] JSON-Datei mit sehr langen Strings erstellen
- [ ] Datei importieren
- [ ] Import funktioniert oder Validierungsfehler

### 9.2 Sonderzeichen

- [ ] JSON-Datei mit Sonderzeichen (Umlaute, Emojis) erstellen
- [ ] Datei importieren
- [ ] Sonderzeichen werden korrekt übernommen

### 9.3 Leere Werte

- [ ] JSON-Datei mit leeren Strings/Arrays erstellen
- [ ] Datei importieren
- [ ] Leere Werte werden akzeptiert oder abgelehnt (je nach Validierung)

## Test 10: Kompatibilität

### 10.1 Browser-Kompatibilität

- [ ] Chrome: Alle Funktionen testen
- [ ] Firefox: Alle Funktionen testen
- [ ] Safari: Alle Funktionen testen
- [ ] Edge: Alle Funktionen testen

### 10.2 Mobile Geräte

- [ ] Smartphone: UI ist responsive
- [ ] Tablet: UI ist responsive
- [ ] Touch-Bedienung funktioniert

### 10.3 Betriebssysteme

- [ ] Windows: Download funktioniert
- [ ] macOS: Download funktioniert
- [ ] Linux: Download funktioniert

## Zusammenfassung

### Kritische Tests (müssen bestehen)

- [ ] Export erstellt gültige JSON-Datei
- [ ] Import übernimmt alle Einstellungen korrekt
- [ ] Validierung verhindert ungültige Importe
- [ ] Bestätigung ist erforderlich
- [ ] Keine Datenverluste

### Wichtige Tests (sollten bestehen)

- [ ] Fehlermeldungen sind hilfreich
- [ ] Performance ist akzeptabel
- [ ] UI ist benutzerfreundlich
- [ ] Hilfe-Sektion ist vorhanden

### Optionale Tests (nice to have)

- [ ] Mobile Ansicht funktioniert
- [ ] Alle Browser werden unterstützt
- [ ] Edge Cases werden behandelt

## Ergebnis

**Datum:** _________________

**Tester:** _________________

**Status:**

- [ ] ✅ Alle kritischen Tests bestanden
- [ ] ✅ Alle wichtigen Tests bestanden
- [ ] ✅ Optionale Tests bestanden

**Notizen:**
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________

**Freigabe:**

- [ ] Task 14 ist vollständig implementiert und getestet
- [ ] Bereit für Produktion

**Unterschrift:** _________________
