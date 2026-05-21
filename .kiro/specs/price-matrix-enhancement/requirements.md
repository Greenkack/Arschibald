# Requirements Document - Preismatrix-Erweiterung

## Einleitung

Diese Spezifikation beschreibt die Erweiterung der Preismatrix-Funktionalität im Solar-Kalkulationssystem. Die Preismatrix soll als alternative Preisberechnungsmethode dienen, bei der Preise basierend auf der Anzahl der Module und dem gewählten Batteriespeichermodell aus einer vordefinierten Matrix abgerufen werden. Diese Methode ersetzt die standardmäßige Einzelprodukt-Kalkulation vollständig, wenn sie aktiviert ist.

## Glossar

- **Preismatrix**: Eine zweidimensionale Tabelle, die schlüsselfertige Preise für PV-Anlagen basierend auf Modulanzahl (Zeilen) und Speichermodell (Spalten) enthält
- **Excel-Grid-System**: Das bestehende Excel-ähnliche Eingabesystem für die Preismatrix
- **Solarcalculator**: Das Hauptberechnungsmodul für PV-Anlagen-Preise
- **Admin-Panel**: Der Verwaltungsbereich für Systemeinstellungen
- **INDEX-Formel**: Eine Lookup-Funktion, die den Preis an der Kreuzung von Zeile (Modulanzahl) und Spalte (Speichermodell) findet
- **Schlüsselfertige Preise**: Komplette Endpreise ohne zusätzliche Aufschläge oder Berechnungen
- **Standardberechnung**: Die bisherige Methode der Preiskalkulation basierend auf Einzelproduktpreisen

## Anforderungen

### Anforderung 1: Text- und Zahleneingabe in Preismatrix

**User Story:** Als Administrator möchte ich sowohl Text als auch Zahlen in die Preismatrix-Zellen eingeben können, damit ich Produktmodelle als Spaltenüberschriften und Modulanzahlen als Zeilenüberschriften definieren kann.

#### Acceptance Criteria

1. WHEN der Administrator eine Zelle in der Preismatrix auswählt, THEN THE Excel-Grid-System SHALL die Eingabe von alphanumerischen Zeichen, Zahlen und Sonderzeichen ermöglichen

2. WHEN der Administrator Text in eine Zelle eingibt, THEN THE Excel-Grid-System SHALL den Text ohne Konvertierung oder Validierung als Zahlentyp speichern

3. WHEN der Administrator numerische Werte in eine Zelle eingibt, THEN THE Excel-Grid-System SHALL die Werte als Zahlen für Berechnungen speichern

4. WHEN der Administrator die Preismatrix speichert, THEN THE Excel-Grid-System SHALL sowohl Text- als auch Zahlenwerte in der Datenbank persistieren

### Anforderung 2: Strukturierte Preismatrix mit Kopfzeile und Kopfspalte

**User Story:** Als Administrator möchte ich eine strukturierte Preismatrix mit Produktmodellen in der ersten Zeile und Modulanzahlen in der ersten Spalte erstellen, damit das System automatisch die richtigen Preise zuordnen kann.

#### Acceptance Criteria

1. WHEN der Administrator die Preismatrix öffnet, THEN THE Excel-Grid-System SHALL die erste Zeile (Zeile 1) für Speichermodell-Namen reservieren

2. WHEN der Administrator die Preismatrix öffnet, THEN THE Excel-Grid-System SHALL die erste Spalte (Spalte A) für Modulanzahl-Werte reservieren

3. WHEN der Administrator Speichermodell-Namen in Zeile 1 eingibt, THEN THE Excel-Grid-System SHALL diese als Spaltenüberschriften behandeln

4. WHEN der Administrator Modulanzahlen in Spalte A eingibt, THEN THE Excel-Grid-System SHALL diese als Zeilenüberschriften behandeln

5. WHEN der Administrator eine Spalte mit "Kein Speicher" oder ähnlichem Text benennt, THEN THE Excel-Grid-System SHALL diese Spalte für Konfigurationen ohne Batteriespeicher verwenden

### Anforderung 3: Preisberechnungsmodus im Admin-Panel

**User Story:** Als Administrator möchte ich im Admin-Panel zwischen Standardberechnung und Preismatrix-Berechnung wählen können, damit ich die für mein Geschäftsmodell passende Kalkulationsmethode aktivieren kann.

#### Acceptance Criteria

1. WHEN der Administrator den Admin-Panel-Bereich "Erweiterte Einstellungen" öffnet, THEN THE Admin-Panel SHALL eine Option zur Auswahl des Preisberechnungsmodus anzeigen

2. WHEN der Administrator die Preisberechnungsmodus-Option anzeigt, THEN THE Admin-Panel SHALL zwei Auswahlmöglichkeiten bereitstellen: "Standardberechnung (Einzelprodukte)" und "Preismatrix (Schlüsselfertige Preise)"

3. WHEN der Administrator einen Preisberechnungsmodus auswählt, THEN THE Admin-Panel SHALL die Auswahl in der Datenbank speichern

4. WHEN der Administrator die Einstellungen speichert, THEN THE Admin-Panel SHALL eine Bestätigung anzeigen und die Änderungen sofort aktivieren

5. WHEN das System startet, THEN THE Admin-Panel SHALL den zuletzt gespeicherten Preisberechnungsmodus laden und anwenden

### Anforderung 4: INDEX-basierte Preisabfrage im Solarcalculator

**User Story:** Als System möchte ich bei aktivierter Preismatrix-Berechnung den Preis automatisch aus der Matrix abrufen, damit der Benutzer den korrekten schlüsselfertigen Preis erhält.

#### Acceptance Criteria

1. WHEN der Preisberechnungsmodus "Preismatrix" aktiv ist AND der Benutzer eine Modulanzahl wählt, THEN THE Solarcalculator SHALL die entsprechende Zeile in Spalte A der Preismatrix identifizieren

2. WHEN der Preisberechnungsmodus "Preismatrix" aktiv ist AND der Benutzer ein Speichermodell wählt, THEN THE Solarcalculator SHALL die entsprechende Spalte in Zeile 1 der Preismatrix identifizieren

3. WHEN der Preisberechnungsmodus "Preismatrix" aktiv ist AND der Benutzer kein Speichermodell wählt, THEN THE Solarcalculator SHALL die Spalte "Kein Speicher" in der Preismatrix identifizieren

4. WHEN der Solarcalculator Zeile und Spalte identifiziert hat, THEN THE Solarcalculator SHALL den Wert an der Kreuzung (z.B. D14) als Endpreis abrufen

5. IF der abgerufene Wert keine gültige Zahl ist, THEN THE Solarcalculator SHALL eine Fehlermeldung anzeigen mit dem Hinweis auf fehlende Preisdaten

6. WHEN der Solarcalculator einen gültigen Preis abruft, THEN THE Solarcalculator SHALL diesen Preis als finalen Anlagenpreis verwenden

### Anforderung 5: Deaktivierung der Standardberechnung bei aktiver Preismatrix

**User Story:** Als System möchte ich bei aktivierter Preismatrix alle Standardberechnungen deaktivieren, damit keine zusätzlichen Kosten oder Aufschläge zum schlüsselfertigen Preis hinzugefügt werden.

#### Acceptance Criteria

1. WHEN der Preisberechnungsmodus "Preismatrix" aktiv ist, THEN THE Solarcalculator SHALL alle Einzelprodukt-Preisberechnungen deaktivieren

2. WHEN der Preisberechnungsmodus "Preismatrix" aktiv ist, THEN THE Solarcalculator SHALL keine automatischen Aufschläge für Montage, Installation oder andere Standardkosten hinzufügen

3. WHEN der Preisberechnungsmodus "Preismatrix" aktiv ist, THEN THE Solarcalculator SHALL keine Mehrkosten für Standardkomponenten berechnen

4. WHEN der Preisberechnungsmodus "Preismatrix" aktiv ist, THEN THE Solarcalculator SHALL den Preismatrix-Preis als Basispreis ohne Modifikationen verwenden

5. WHEN der Preisberechnungsmodus "Standardberechnung" aktiv ist, THEN THE Solarcalculator SHALL die Preismatrix ignorieren und die normale Einzelprodukt-Kalkulation durchführen

### Anforderung 6: Zusatzkosten für Sonderprodukte und Extras

**User Story:** Als System möchte ich bei aktivierter Preismatrix nur für explizite Sonderprodukte, Extras und Dienstleistungen zusätzliche Kosten berechnen, damit der Kunde einen transparenten Endpreis erhält.

#### Acceptance Criteria

1. WHEN der Preisberechnungsmodus "Preismatrix" aktiv ist AND der Benutzer Sonderprodukte auswählt, THEN THE Solarcalculator SHALL die Kosten dieser Sonderprodukte zum Preismatrix-Preis addieren

2. WHEN der Preisberechnungsmodus "Preismatrix" aktiv ist AND der Benutzer zusätzliche Dienstleistungen auswählt, THEN THE Solarcalculator SHALL die Kosten dieser Dienstleistungen zum Preismatrix-Preis addieren

3. WHEN der Preisberechnungsmodus "Preismatrix" aktiv ist AND der Benutzer Extras oder Sonderwünsche auswählt, THEN THE Solarcalculator SHALL die Kosten dieser Extras zum Preismatrix-Preis addieren

4. WHEN der Preisberechnungsmodus "Preismatrix" aktiv ist AND der Administrator Rabatte gewährt, THEN THE Solarcalculator SHALL die Rabatte vom Gesamtpreis abziehen

5. WHEN der Preisberechnungsmodus "Preismatrix" aktiv ist AND der Administrator Aufpreise definiert, THEN THE Solarcalculator SHALL die Aufpreise zum Gesamtpreis addieren

6. WHEN der Solarcalculator Zusatzkosten berechnet, THEN THE Solarcalculator SHALL eine detaillierte Preisaufschlüsselung anzeigen mit Preismatrix-Basispreis und allen Zusatzkosten

### Anforderung 7: Validierung und Fehlerbehandlung

**User Story:** Als Administrator möchte ich klare Fehlermeldungen erhalten, wenn die Preismatrix nicht korrekt konfiguriert ist, damit ich Probleme schnell beheben kann.

#### Acceptance Criteria

1. WHEN der Administrator die Preismatrix-Berechnung aktiviert AND die Preismatrix ist leer, THEN THE Admin-Panel SHALL eine Warnung anzeigen mit dem Hinweis auf fehlende Preisdaten

2. WHEN der Solarcalculator eine Modulanzahl sucht AND diese nicht in Spalte A existiert, THEN THE Solarcalculator SHALL eine Fehlermeldung anzeigen: "Modulanzahl [X] nicht in Preismatrix gefunden"

3. WHEN der Solarcalculator ein Speichermodell sucht AND dieses nicht in Zeile 1 existiert, THEN THE Solarcalculator SHALL eine Fehlermeldung anzeigen: "Speichermodell [Y] nicht in Preismatrix gefunden"

4. WHEN der Solarcalculator einen Preis abruft AND die Zelle ist leer, THEN THE Solarcalculator SHALL eine Fehlermeldung anzeigen: "Kein Preis für diese Kombination definiert"

5. WHEN der Solarcalculator einen Preis abruft AND die Zelle enthält Text statt einer Zahl, THEN THE Solarcalculator SHALL eine Fehlermeldung anzeigen: "Ungültiger Preiswert in Preismatrix"

### Anforderung 8: Rückwärtskompatibilität und Systemstabilität

**User Story:** Als Entwickler möchte ich sicherstellen, dass die Preismatrix-Erweiterung keine negativen Auswirkungen auf bestehende Funktionen hat, damit das System stabil und zuverlässig bleibt.

#### Acceptance Criteria

1. WHEN die Preismatrix-Funktionalität implementiert wird, THEN THE System SHALL alle bestehenden Funktionen ohne Beeinträchtigung weiter ausführen

2. WHEN der Preisberechnungsmodus "Standardberechnung" aktiv ist, THEN THE Solarcalculator SHALL exakt wie vor der Implementierung funktionieren

3. WHEN die Preismatrix-Verwaltung bereits existiert, THEN THE System SHALL die bestehende Verwaltungsfunktionalität unverändert beibehalten

4. WHEN neue Funktionen hinzugefügt werden, THEN THE System SHALL keine bestehenden Datenstrukturen oder APIs brechen

5. WHEN Fehler in der Preismatrix-Berechnung auftreten, THEN THE System SHALL auf die Standardberechnung zurückfallen können ohne Systemabsturz
