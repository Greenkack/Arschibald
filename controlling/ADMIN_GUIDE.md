# Employee Controlling System - Administratorhandbuch

## Willkommen

Dieses Handbuch erklärt die Administration und Konfiguration des Employee Controlling Systems. Als Administrator sind Sie verantwortlich für die Verwaltung von Mitarbeitern, Positionen, Kriterien und Benachrichtigungseinstellungen.

## 🔐 Zugriff

### Admin-Bereich öffnen

1. Öffnen Sie die Hauptanwendung
2. Wählen Sie im Hauptmenü **"Administration & Verwaltung"**
3. Geben Sie das Admin-Passwort ein
4. Wählen Sie den Tab **"Controlling Einstellungen"**

### Sicherheit

- Das Admin-Passwort wird zentral verwaltet
- Ändern Sie das Passwort regelmäßig
- Geben Sie das Passwort nicht an Endbenutzer weiter
- Alle Admin-Aktionen werden protokolliert

## 📋 Übersicht der Admin-Tabs

Das Controlling Admin-Panel besteht aus 5 Tabs:

1. **👥 Mitarbeiter**: Mitarbeiterverwaltung
2. **💼 Positionen**: Positionsverwaltung
3. **📊 Auswertungskriterien**: Kriterienverwaltung
4. **🔗 Zuordnungen**: Position-Kriterien-Zuordnung
5. **🔔 Benachrichtigungen**: Schwellenwert-Konfiguration

## 👥 Mitarbeiterverwaltung

### Mitarbeiter erstellen

1. Wechseln Sie zum Tab **"👥 Mitarbeiter"**
2. Klicken Sie auf **"Neuen Mitarbeiter anlegen"**
3. Füllen Sie das Formular aus:

**Pflichtfelder:**
- **Vorname**: Vorname des Mitarbeiters
- **Nachname**: Nachname des Mitarbeiters
- **Wohnort**: Stadt/Ort des Wohnsitzes
- **Geburtsdatum**: Geburtsdatum (für Altersberechnung)
- **Position**: Wählen Sie eine Position aus
- **Eintrittsdatum**: Datum des Arbeitsbeginns

**Optionale Felder:**
- **Telefonnummer**: Kontaktnummer
- **E-Mail**: E-Mail-Adresse

4. Klicken Sie auf **"Mitarbeiter erstellen"**
5. Eine Erfolgsmeldung bestätigt die Erstellung

### Automatische Berechnungen

Das System berechnet automatisch:
- **Alter**: Wird aus dem Geburtsdatum berechnet
- **Arbeitstage**: Wird aus dem Eintrittsdatum berechnet

Diese Werte werden bei jedem Zugriff neu berechnet und sind immer aktuell.

### Mitarbeiter bearbeiten

1. Wählen Sie einen Mitarbeiter aus der Liste
2. Klicken Sie auf **"Bearbeiten"**
3. Ändern Sie die gewünschten Felder
4. Klicken Sie auf **"Änderungen speichern"**

**Hinweis:** Das Eintrittsdatum sollte nur in Ausnahmefällen geändert werden, da es die Berechnung der Arbeitstage beeinflusst.

### Mitarbeiter archivieren

1. Wählen Sie einen Mitarbeiter aus der Liste
2. Klicken Sie auf **"Archivieren"**
3. Bestätigen Sie die Archivierung

**Was passiert beim Archivieren:**
- Der Mitarbeiter wird als inaktiv markiert
- Historische Daten bleiben erhalten
- Der Mitarbeiter erscheint nicht mehr in Dropdown-Listen
- Gespeicherte Berichte bleiben zugänglich

**Wichtig:** Archivieren Sie Mitarbeiter statt sie zu löschen, um historische Daten zu bewahren.

### Mitarbeiter reaktivieren

1. Aktivieren Sie die Option **"Archivierte Mitarbeiter anzeigen"**
2. Wählen Sie einen archivierten Mitarbeiter
3. Klicken Sie auf **"Reaktivieren"**
4. Der Mitarbeiter ist wieder aktiv

### Mitarbeiter löschen

**⚠️ Vorsicht:** Das Löschen ist endgültig und sollte nur in Ausnahmefällen erfolgen!

1. Wählen Sie einen Mitarbeiter
2. Klicken Sie auf **"Löschen"**
3. Bestätigen Sie die Löschung zweimal

**Was wird gelöscht:**
- Mitarbeiterdaten
- Alle Leistungsdaten
- Alle Berichte

**Empfehlung:** Verwenden Sie stattdessen die Archivierung!

## 💼 Positionsverwaltung

### Position erstellen

1. Wechseln Sie zum Tab **"💼 Positionen"**
2. Klicken Sie auf **"Neue Position anlegen"**
3. Füllen Sie das Formular aus:

**Pflichtfelder:**
- **Name**: Eindeutiger Positionsname (z.B. "Vertriebsmitarbeiter")
- **Beschreibung**: Kurze Beschreibung der Position

4. Klicken Sie auf **"Position erstellen"**

### Position bearbeiten

1. Wählen Sie eine Position aus der Liste
2. Klicken Sie auf **"Bearbeiten"**
3. Ändern Sie Name oder Beschreibung
4. Klicken Sie auf **"Änderungen speichern"**

**Hinweis:** Der Positionsname muss eindeutig sein.

### Position löschen

**Löschschutz:** Positionen mit zugeordneten Mitarbeitern können nicht gelöscht werden!

1. Wählen Sie eine Position ohne Mitarbeiter
2. Klicken Sie auf **"Löschen"**
3. Bestätigen Sie die Löschung

**Vor dem Löschen:**
- Stellen Sie sicher, dass keine Mitarbeiter dieser Position zugeordnet sind
- Ordnen Sie ggf. Mitarbeiter einer anderen Position zu
- Beachten Sie, dass auch die Kriterien-Zuordnungen gelöscht werden

### Positionshierarchie

Empfohlene Positionen für ein Vertriebsteam:

1. **Vertriebsmitarbeiter**: Basis-Vertriebsposition
2. **Senior Vertriebsmitarbeiter**: Erfahrene Verkäufer
3. **Teamleiter Vertrieb**: Führungsposition
4. **Kundenservice**: Support-Position
5. **Vertriebsleiter**: Management-Position

## 📊 Kriterienverwaltung

### Standard-Kriterien

Das System wird mit 14 Standard-Kriterien initialisiert:

1. Kunden terminiert
2. QC bestanden
3. Storniert / kein Interesse
4. Nicht erreicht / neu terminieren
5. Technisch nicht machbar
6. Angefahrene Termine
7. Nicht angefahrene Termine
8. Verkauf
9. Folgetermin gemacht
10. Zu teuer gewesen
11. Angebot erhalten
12. Getätigte Anrufe gesamt
13. Angefahrene Termine gesamt
14. Sonstiges

**Empfehlung:** Ändern Sie die Standard-Kriterien nicht, da sie für die Quoten-Berechnungen benötigt werden.

### Benutzerdefiniertes Kriterium erstellen

1. Wechseln Sie zum Tab **"📊 Auswertungskriterien"**
2. Klicken Sie auf **"Neues Kriterium anlegen"**
3. Füllen Sie das Formular aus:

**Pflichtfelder:**
- **Name**: Eindeutiger Kriterienname
- **Beschreibung**: Erklärung des Kriteriums

**Optionale Felder:**
- **Berechnungsmethode**: SUM, AVERAGE, PERCENTAGE, RATIO
- **Einheit**: z.B. "Stück", "Euro", "Prozent"

4. Klicken Sie auf **"Kriterium erstellen"**

### Kriterium bearbeiten

1. Wählen Sie ein Kriterium aus der Liste
2. Klicken Sie auf **"Bearbeiten"**
3. Ändern Sie die gewünschten Felder
4. Klicken Sie auf **"Änderungen speichern"**

### Kriterium löschen

**⚠️ Vorsicht:** Löschen Sie keine Standard-Kriterien!

1. Wählen Sie ein benutzerdefiniertes Kriterium
2. Klicken Sie auf **"Löschen"**
3. Bestätigen Sie die Löschung

**Was wird gelöscht:**
- Das Kriterium selbst
- Alle Zuordnungen zu Positionen
- Alle erfassten Leistungsdaten für dieses Kriterium

## 🔗 Position-Kriterien-Zuordnung

### Konzept

Jede Position kann individuelle Auswertungskriterien haben. Mitarbeiter erben automatisch die Kriterien ihrer Position.

**Beispiel:**
- **Vertriebsmitarbeiter**: Alle 14 Standard-Kriterien
- **Kundenservice**: Nur Anrufe, Termine, Zufriedenheit
- **Teamleiter**: Alle Kriterien + zusätzliche Management-Kriterien

### Kriterien zuordnen

1. Wechseln Sie zum Tab **"🔗 Zuordnungen"**
2. Wählen Sie eine Position aus dem Dropdown
3. Sie sehen zwei Listen:
   - **Verfügbare Kriterien**: Noch nicht zugeordnet
   - **Zugeordnete Kriterien**: Bereits zugeordnet

4. Wählen Sie Kriterien aus der Liste "Verfügbare Kriterien"
5. Klicken Sie auf **"Ausgewählte Kriterien zuordnen"**
6. Die Kriterien werden zur Position hinzugefügt

### Kriterien entfernen

1. Wählen Sie eine Position
2. Wählen Sie Kriterien aus der Liste "Zugeordnete Kriterien"
3. Klicken Sie auf **"Ausgewählte Kriterien entfernen"**
4. Die Kriterien werden von der Position entfernt

**⚠️ Achtung:** Das Entfernen von Kriterien löscht keine historischen Daten, aber Mitarbeiter dieser Position können keine neuen Daten für diese Kriterien mehr erfassen.

### Alle Kriterien zuordnen

1. Wählen Sie eine Position
2. Klicken Sie auf **"Alle Kriterien zuordnen"**
3. Alle verfügbaren Kriterien werden der Position zugeordnet

### Alle Kriterien entfernen

1. Wählen Sie eine Position
2. Klicken Sie auf **"Alle Kriterien entfernen"**
3. Bestätigen Sie die Aktion
4. Alle Kriterien werden von der Position entfernt

### Best Practices

**Vertriebspositionen:**
- Ordnen Sie alle Standard-Kriterien zu
- Fügen Sie positionsspezifische Kriterien hinzu

**Support-Positionen:**
- Fokus auf Anrufe und Kundenzufriedenheit
- Weniger Verkaufs-Kriterien

**Management-Positionen:**
- Alle Kriterien für Übersicht
- Zusätzliche Management-Kriterien

## 🔔 Benachrichtigungsverwaltung

### Konzept

Das Benachrichtigungssystem überwacht Quoten und generiert automatische Benachrichtigungen bei Über- oder Unterschreitung von Schwellenwerten.

### Benachrichtigungstypen

1. **✅ Erfolg (Grün)**: Ziele erreicht oder übertroffen
2. **⚠️ Warnung (Gelb)**: Werte unter Mindestschwellen
3. **ℹ️ Info (Blau)**: Hinweise auf auffällige Werte
4. **❌ Fehler (Rot)**: Kritische Probleme

### Standard-Schwellenwerte

Das System wird mit folgenden Standard-Schwellenwerten initialisiert:

**Erfolgs-Benachrichtigungen (Über Schwellenwert):**
- Abschlussquote > 30%
- Terminvereinbarungsquote > 20%
- QC bestanden Quote > 90%

**Warnungs-Benachrichtigungen (Unter Schwellenwert):**
- Abschlussquote < 15%
- Terminvereinbarungsquote < 10%
- Termine-Anfahrquote < 70%

**Info-Benachrichtigungen (Über Schwellenwert):**
- Nicht interessierte Kunden Quote > 30%
- Zu teuer Quote > 25%

### Schwellenwert hinzufügen

1. Wechseln Sie zum Tab **"🔔 Benachrichtigungen"**
2. Klicken Sie auf **"Neuen Schwellenwert hinzufügen"**
3. Füllen Sie das Formular aus:

**Pflichtfelder:**
- **Quote**: Wählen Sie eine Quote aus (z.B. "Abschlussquote")
- **Schwellenwert**: Prozentwert (0-100)
- **Schwellenwert-Typ**: 
  - **Über**: Benachrichtigung bei Überschreitung
  - **Unter**: Benachrichtigung bei Unterschreitung
- **Benachrichtigungs-Typ**: Erfolg, Info, Warnung, Fehler
- **Nachrichtenvorlage**: Text mit Platzhaltern

**Platzhalter in Nachrichtenvorlagen:**
- `{quota_value}`: Aktueller Quotenwert
- `{threshold_value}`: Schwellenwert
- `{employee_name}`: Name des Mitarbeiters (automatisch)

**Beispiel:**
```
Quote: Abschlussquote
Schwellenwert: 35.0
Typ: Über
Benachrichtigung: Erfolg
Vorlage: Exzellente Leistung! Die Abschlussquote von {quota_value:.1f}% 
         übertrifft das Ziel von {threshold_value:.1f}% deutlich.
```

4. Klicken Sie auf **"Schwellenwert erstellen"**

### Schwellenwert bearbeiten

1. Wählen Sie einen Schwellenwert aus der Liste
2. Klicken Sie auf **"Bearbeiten"**
3. Ändern Sie die gewünschten Felder
4. Klicken Sie auf **"Änderungen speichern"**

### Schwellenwert löschen

1. Wählen Sie einen Schwellenwert
2. Klicken Sie auf **"Löschen"**
3. Bestätigen Sie die Löschung

### Schwellenwert-Strategien

**Motivations-Strategie:**
- Niedrige Erfolgs-Schwellenwerte (leicht erreichbar)
- Viele positive Benachrichtigungen
- Fokus auf Erfolge

**Performance-Strategie:**
- Hohe Erfolgs-Schwellenwerte (anspruchsvoll)
- Strenge Warnungen
- Fokus auf Verbesserung

**Balanced-Strategie:**
- Moderate Schwellenwerte
- Mix aus Erfolgen und Warnungen
- Realistische Ziele

### Best Practices

**Schwellenwerte festlegen:**
- Analysieren Sie historische Daten
- Setzen Sie realistische Ziele
- Passen Sie Schwellenwerte regelmäßig an

**Nachrichtenvorlagen:**
- Verwenden Sie klare, verständliche Sprache
- Seien Sie spezifisch
- Bieten Sie Kontext

**Benachrichtigungs-Balance:**
- Nicht zu viele Benachrichtigungen (Überlastung)
- Nicht zu wenige Benachrichtigungen (keine Wirkung)
- Fokus auf wichtige Metriken

## 🔧 Wartung & Optimierung

### Regelmäßige Aufgaben

**Täglich:**
- Überprüfen Sie neue Mitarbeiter-Registrierungen
- Kontrollieren Sie Benachrichtigungen

**Wöchentlich:**
- Überprüfen Sie Datenqualität
- Analysieren Sie Benachrichtigungs-Häufigkeit

**Monatlich:**
- Überprüfen Sie Position-Kriterien-Zuordnungen
- Passen Sie Schwellenwerte an
- Archivieren Sie ausgeschiedene Mitarbeiter

**Quartalsweise:**
- Analysieren Sie System-Performance
- Überprüfen Sie Kriterien-Relevanz
- Schulen Sie neue Administratoren

### Datenqualität sicherstellen

**Mitarbeiterdaten:**
- Überprüfen Sie Vollständigkeit
- Aktualisieren Sie Kontaktdaten
- Korrigieren Sie Fehler zeitnah

**Positionsdaten:**
- Halten Sie Beschreibungen aktuell
- Überprüfen Sie Kriterien-Zuordnungen
- Entfernen Sie veraltete Positionen

**Leistungsdaten:**
- Überwachen Sie Erfassungs-Konsistenz
- Identifizieren Sie Ausreißer
- Schulen Sie Benutzer bei Fehlern

### Performance-Optimierung

**Datenbank:**
- Archivieren Sie alte Berichte
- Löschen Sie Test-Daten
- Optimieren Sie regelmäßig

**Benachrichtigungen:**
- Deaktivieren Sie ungenutzte Schwellenwerte
- Konsolidieren Sie ähnliche Benachrichtigungen
- Optimieren Sie Nachrichtenvorlagen

## 📊 Reporting & Analyse

### Admin-Berichte

Als Administrator sollten Sie regelmäßig folgende Berichte erstellen:

**Team-Übersicht:**
- Vergleichsbericht aller Mitarbeiter
- Monatlicher Zeitraum
- Identifizierung von Top-Performern

**Positions-Analyse:**
- Vergleich nach Positionen
- Quartalsweiser Zeitraum
- Bewertung der Kriterien-Zuordnungen

**Trend-Analyse:**
- Einzelmitarbeiter-Berichte
- Jährlicher Zeitraum
- Langfristige Entwicklungen

### Daten exportieren

**Für Präsentationen:**
- Verwenden Sie PDF-Export
- Erstellen Sie Vergleichsberichte
- Fokus auf Visualisierungen

**Für Analysen:**
- Verwenden Sie Excel-Export
- Exportieren Sie Rohdaten
- Nutzen Sie Pivot-Tabellen

**Für Archivierung:**
- Verwenden Sie JSON-Export
- Vollständige Daten-Sicherung
- Langfristige Aufbewahrung

## 🔒 Sicherheit & Datenschutz

### Zugriffsrechte

**Administrator:**
- Vollzugriff auf alle Funktionen
- Verwaltung von Mitarbeitern, Positionen, Kriterien
- Konfiguration von Benachrichtigungen

**Benutzer:**
- Erfassung von Leistungsdaten
- Erstellung von Berichten
- Export von eigenen Berichten

### Datenschutz

**Personenbezogene Daten:**
- Mitarbeiterdaten sind geschützt
- Zugriff nur für autorisierte Personen
- DSGVO-konform

**Leistungsdaten:**
- Vertraulich behandeln
- Nicht an Dritte weitergeben
- Sichere Speicherung

### Backup & Recovery

**Regelmäßige Backups:**
- Tägliche Datenbank-Backups
- Wöchentliche Vollbackups
- Monatliche Archiv-Backups

**Recovery-Plan:**
- Dokumentieren Sie Wiederherstellungs-Prozesse
- Testen Sie Backups regelmäßig
- Halten Sie Kontakte bereit

## ❓ Häufige Admin-Fragen

### Kann ich Mitarbeiter zwischen Positionen verschieben?

Ja, bearbeiten Sie den Mitarbeiter und wählen Sie eine neue Position. Die Kriterien-Zuordnung wird automatisch aktualisiert.

### Was passiert mit Daten beim Positions-Wechsel?

Historische Daten bleiben erhalten. Der Mitarbeiter kann ab sofort nur noch Daten für die Kriterien der neuen Position erfassen.

### Kann ich Standard-Kriterien umbenennen?

Technisch ja, aber nicht empfohlen. Die Quoten-Berechnungen basieren auf den Standard-Namen.

### Wie viele Schwellenwerte kann ich erstellen?

Unbegrenzt, aber empfohlen sind 10-15 relevante Schwellenwerte pro Quote.

### Kann ich Benachrichtigungen deaktivieren?

Ja, löschen Sie einfach die entsprechenden Schwellenwerte.

### Wie oft sollte ich Schwellenwerte anpassen?

Quartalsweise oder bei signifikanten Änderungen in der Unternehmensstruktur.

## 🆘 Problemlösung

### Mitarbeiter kann nicht gelöscht werden

**Ursache:** Mitarbeiter hat zugeordnete Daten.

**Lösung:** Verwenden Sie die Archivierung statt Löschung.

### Position kann nicht gelöscht werden

**Ursache:** Position hat zugeordnete Mitarbeiter.

**Lösung:** Ordnen Sie Mitarbeiter einer anderen Position zu oder archivieren Sie sie.

### Kriterium erscheint nicht bei Mitarbeiter

**Ursache:** Kriterium ist nicht der Position des Mitarbeiters zugeordnet.

**Lösung:** Ordnen Sie das Kriterium der Position zu (Tab "Zuordnungen").

### Benachrichtigungen werden nicht angezeigt

**Ursache:** Keine Schwellenwerte konfiguriert oder Schwellenwerte nicht erreicht.

**Lösung:** Überprüfen Sie die Schwellenwert-Konfiguration im Tab "Benachrichtigungen".

## 📞 Support

Bei technischen Problemen oder Fragen:

1. Konsultieren Sie das [Benutzerhandbuch](USER_GUIDE.md)
2. Überprüfen Sie die [Benachrichtigungssystem-Dokumentation](NOTIFICATION_SYSTEM_README.md)
3. Kontaktieren Sie das Entwicklungsteam
4. Erstellen Sie ein Support-Ticket

---

**Version:** 1.0.0
**Letzte Aktualisierung:** Dezember 2025
**Teil des Employee Controlling Systems**
