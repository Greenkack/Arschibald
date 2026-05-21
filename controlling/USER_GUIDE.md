# Employee Controlling System - Benutzerhandbuch

## Willkommen

Dieses Handbuch erklärt die Verwendung des Employee Controlling Systems für Endanwender. Sie lernen, wie Sie Leistungsdaten erfassen, Berichte erstellen und Ihre Mitarbeiterleistungen analysieren.

## 📍 Navigation

1. Öffnen Sie die Hauptanwendung
2. Wählen Sie im Hauptmenü den Tab **"Controlling"**
3. Sie sehen nun die Controlling-Oberfläche mit 3 Tabs:
   - **📝 Leistungsdaten erfassen**
   - **📈 Berichte erstellen**
   - **📁 Archiv**

## 📝 Leistungsdaten erfassen

### Schritt 1: Mitarbeiter auswählen

1. Wählen Sie im Dropdown-Menü einen Mitarbeiter aus
2. Die verfügbaren Auswertungskriterien werden automatisch geladen
3. Diese Kriterien sind abhängig von der Position des Mitarbeiters

### Schritt 2: Datum wählen

1. Wählen Sie das Datum für die Leistungserfassung
2. Standardmäßig ist das heutige Datum ausgewählt
3. Sie können auch historische Daten erfassen

### Schritt 3: Leistungsdaten eingeben

1. Für jedes Kriterium sehen Sie ein Eingabefeld
2. Geben Sie die numerischen Werte ein (z.B. Anzahl der Anrufe, Verkäufe, etc.)
3. Alle Felder akzeptieren nur positive Zahlen

**Beispiel:**
- Getätigte Anrufe gesamt: 50
- Kunden terminiert: 10
- Angefahrene Termine gesamt: 8
- Verkauf: 2

### Schritt 4: Daten speichern

1. Klicken Sie auf **"Leistungsdaten speichern"**
2. Eine Erfolgsmeldung bestätigt die Speicherung
3. Die Daten sind nun in der Datenbank gespeichert

### Tipps

- ✅ Erfassen Sie Daten täglich für beste Auswertungen
- ✅ Überprüfen Sie Ihre Eingaben vor dem Speichern
- ✅ Negative Werte werden automatisch abgelehnt
- ✅ Sie können Daten für vergangene Tage nachträglich erfassen

## 📈 Berichte erstellen

### Schritt 1: Berichtstyp wählen

Wählen Sie zwischen zwei Berichtstypen:

#### Einzelmitarbeiter-Bericht
- Detaillierte Analyse eines einzelnen Mitarbeiters
- Zeigt alle Quoten und Verhältnisse
- Generiert Visualisierungen
- Unterstützt Benachrichtigungen

#### Vergleichsbericht
- Vergleicht mehrere Mitarbeiter
- Zeigt relative Leistungen
- Ideal für Team-Analysen
- Keine Benachrichtigungen

### Schritt 2: Mitarbeiter auswählen

**Für Einzelmitarbeiter-Bericht:**
- Wählen Sie einen Mitarbeiter aus dem Dropdown

**Für Vergleichsbericht:**
- Wählen Sie mehrere Mitarbeiter aus der Multi-Select-Liste
- Mindestens 2 Mitarbeiter erforderlich

### Schritt 3: Zeitraum festlegen

Wählen Sie einen der 6 verfügbaren Zeiträume:

1. **Täglich**: Nur der ausgewählte Tag
   - Ideal für tägliche Kontrolle
   - Zeigt aktuelle Leistung

2. **Wöchentlich**: Letzte 7 Tage
   - Guter Überblick über die Woche
   - Glättet tägliche Schwankungen

3. **Monatlich**: Letzter Monat
   - Standard-Auswertungszeitraum
   - Zeigt monatliche Trends

4. **Quartalsweise**: Letztes Quartal (3 Monate)
   - Langfristige Trends
   - Saisonale Analysen

5. **Jährlich**: Letztes Jahr
   - Jahresübersicht
   - Vergleich mit Vorjahren

6. **Seit Arbeitsbeginn**: Gesamte Beschäftigungszeit
   - Vollständige Historie
   - Langfristige Entwicklung

### Schritt 4: Enddatum wählen

- Wählen Sie das Enddatum für den Berichtszeitraum
- Der Startzeitpunkt wird automatisch berechnet
- Standardmäßig ist das heutige Datum ausgewählt

### Schritt 5: Bericht generieren

1. Klicken Sie auf **"Bericht generieren"**
2. Der Bericht wird erstellt (kann einige Sekunden dauern)
3. Die Ergebnisse werden angezeigt

## 📊 Bericht verstehen

### Metadaten

Oben im Bericht sehen Sie:
- **Mitarbeiter**: Name des/der Mitarbeiter(s)
- **Zeitraum**: Berichtszeitraum (z.B. "Monatlich")
- **Von - Bis**: Genaue Datumsangaben
- **Erstellt am**: Erstellungszeitpunkt

### Quoten

Die Quoten zeigen prozentuale Auswertungen:

**Beispiel:**
- **Abschlussquote: 25.0%**
  - Bedeutung: Jeder 4. angefahrene Termin führt zu einem Verkauf
  - Berechnung: (Verkauf / Angefahrene Termine gesamt) × 100

- **Terminvereinbarungsquote: 20.0%**
  - Bedeutung: Jeder 5. Anruf führt zu einem Termin
  - Berechnung: (Kunden terminiert / Getätigte Anrufe gesamt) × 100

### Verhältnisse

Unter jeder Quote sehen Sie eine verständliche Beschreibung:
- "Jeder 4. angefahrene Termin ist ein Verkauf"
- "Jeder 5. Anruf führt zu einem Termin"

Diese Verhältnisse machen die Zahlen greifbarer.

### Visualisierungen

Der Bericht enthält automatisch generierte Charts:

1. **Balkendiagramm**: Vergleich aller Quoten
   - Zeigt relative Stärken und Schwächen
   - Farbcodiert nach Wert

2. **Säulendiagramm**: Zeitliche Entwicklung
   - Zeigt Trends über den Zeitraum
   - Ideal für Vergleiche

3. **Donut-Chart**: Verteilung der Aktivitäten
   - Zeigt Anteile verschiedener Kategorien
   - Übersichtliche Darstellung

### Benachrichtigungen

Nach der Berichtserstellung sehen Sie möglicherweise Benachrichtigungen:

- **✅ Erfolg (Grün)**: Ziele wurden erreicht oder übertroffen
- **⚠️ Warnung (Gelb)**: Werte liegen unter Mindestschwellen
- **ℹ️ Info (Blau)**: Hinweise auf auffällige Werte

**Beispiel:**
> ✅ **Ziel erreicht! - Max Mustermann**
>
> Hervorragende Leistung! Die Abschlussquote von 35.0% liegt über dem Ziel von 30.0%.

## 💾 Bericht speichern

### Automatisches Speichern

Jeder generierte Bericht wird automatisch im Archiv gespeichert.

### Manuelles Exportieren

Sie können Berichte in verschiedenen Formaten exportieren:

#### JSON-Export
1. Klicken Sie auf **"Als JSON exportieren"**
2. Die Datei wird heruntergeladen
3. Enthält alle Rohdaten und Metadaten
4. Ideal für Weiterverarbeitung

#### Excel-Export
1. Klicken Sie auf **"Als Excel exportieren"**
2. Die Datei wird heruntergeladen
3. Enthält formatierte Tabellen
4. Ideal für Präsentationen

#### PDF-Export
1. Klicken Sie auf **"Als PDF exportieren"**
2. Die Datei wird heruntergeladen
3. Enthält alle Visualisierungen
4. Ideal für Archivierung

## 📁 Archiv

### Gespeicherte Berichte anzeigen

1. Wechseln Sie zum Tab **"📁 Archiv"**
2. Sie sehen eine Liste aller gespeicherten Berichte
3. Berichte sind nach Erstellungsdatum sortiert (neueste zuerst)

### Berichte filtern

Verwenden Sie die Filter-Optionen:

**Nach Mitarbeiter:**
- Wählen Sie einen oder mehrere Mitarbeiter
- Zeigt nur Berichte für diese Mitarbeiter

**Nach Zeitraum:**
- Wählen Sie einen Berichtstyp (Täglich, Wöchentlich, etc.)
- Zeigt nur Berichte dieses Typs

**Nach Datum:**
- Wählen Sie einen Datumsbereich
- Zeigt nur Berichte aus diesem Zeitraum

### Bericht laden

1. Klicken Sie auf einen Bericht in der Liste
2. Der Bericht wird geladen und angezeigt
3. Sie sehen alle ursprünglichen Daten und Visualisierungen
4. Sie können den Bericht erneut exportieren

### Bericht löschen

1. Klicken Sie auf das Löschen-Symbol neben einem Bericht
2. Bestätigen Sie die Löschung
3. Der Bericht wird dauerhaft entfernt

**⚠️ Achtung:** Gelöschte Berichte können nicht wiederhergestellt werden!

## 🎯 Best Practices

### Tägliche Routine

1. **Morgens**: Überprüfen Sie die Benachrichtigungen vom Vortag
2. **Mittags**: Erfassen Sie Zwischenstände (optional)
3. **Abends**: Erfassen Sie die finalen Leistungsdaten des Tages
4. **Wöchentlich**: Erstellen Sie einen Wochenbericht zur Kontrolle

### Monatliche Auswertung

1. Erstellen Sie am Monatsende einen Monatsbericht
2. Vergleichen Sie mit dem Vormonat
3. Identifizieren Sie Trends und Muster
4. Exportieren Sie den Bericht für Ihre Unterlagen

### Quartalsweise Analyse

1. Erstellen Sie einen Quartalsbericht
2. Vergleichen Sie mehrere Mitarbeiter
3. Identifizieren Sie Top-Performer
4. Leiten Sie Maßnahmen ab

## 💡 Tipps & Tricks

### Effiziente Dateneingabe

- Bereiten Sie Ihre Daten vor dem Öffnen der App vor
- Nutzen Sie eine Strichliste während des Tages
- Erfassen Sie Daten in einem Rutsch am Ende des Tages

### Aussagekräftige Berichte

- Wählen Sie den passenden Zeitraum für Ihre Fragestellung
- Nutzen Sie Vergleichsberichte für Team-Analysen
- Exportieren Sie wichtige Berichte für Präsentationen

### Benachrichtigungen nutzen

- Achten Sie auf Warnungen und reagieren Sie zeitnah
- Feiern Sie Erfolge (grüne Benachrichtigungen)
- Nutzen Sie Info-Benachrichtigungen für Optimierungen

### Archiv organisieren

- Löschen Sie veraltete Test-Berichte
- Exportieren Sie wichtige Berichte regelmäßig
- Nutzen Sie Filter für schnellen Zugriff

## ❓ Häufige Fragen

### Kann ich Daten nachträglich ändern?

Ja, erfassen Sie einfach neue Daten für das gleiche Datum. Die alten Werte werden überschrieben.

### Warum sehe ich keine Kriterien für einen Mitarbeiter?

Der Mitarbeiter hat möglicherweise keine Position zugeordnet, oder die Position hat keine Kriterien. Kontaktieren Sie Ihren Administrator.

### Warum werden keine Benachrichtigungen angezeigt?

Benachrichtigungen werden nur für Einzelmitarbeiter-Berichte generiert, nicht für Vergleichsberichte.

### Kann ich Berichte für andere Mitarbeiter erstellen?

Ja, Sie können Berichte für alle Mitarbeiter im System erstellen.

### Wie lange werden Berichte gespeichert?

Berichte werden unbegrenzt gespeichert, bis Sie sie manuell löschen.

### Kann ich mehrere Berichte gleichzeitig exportieren?

Nein, Berichte müssen einzeln exportiert werden.

### Was bedeutet "Seit Arbeitsbeginn"?

Dieser Zeitraum umfasst alle Daten seit dem Eintrittsdatum des Mitarbeiters.

## 🆘 Probleme lösen

### Fehlermeldung: "Keine Daten verfügbar"

**Ursache:** Für den gewählten Zeitraum wurden keine Leistungsdaten erfasst.

**Lösung:** Erfassen Sie zunächst Leistungsdaten oder wählen Sie einen anderen Zeitraum.

### Fehlermeldung: "Mitarbeiter nicht gefunden"

**Ursache:** Der Mitarbeiter wurde möglicherweise archiviert oder gelöscht.

**Lösung:** Kontaktieren Sie Ihren Administrator.

### Visualisierungen werden nicht angezeigt

**Ursache:** Möglicherweise ein Browser-Problem oder fehlende Daten.

**Lösung:**
1. Aktualisieren Sie die Seite (F5)
2. Versuchen Sie einen anderen Browser
3. Überprüfen Sie, ob Daten vorhanden sind

### Export funktioniert nicht

**Ursache:** Browser-Einstellungen blockieren Downloads.

**Lösung:**
1. Überprüfen Sie Ihre Browser-Einstellungen
2. Erlauben Sie Downloads von dieser Website
3. Versuchen Sie einen anderen Browser

## 📞 Support

Bei weiteren Fragen oder Problemen:

1. Konsultieren Sie das [Admin-Handbuch](ADMIN_GUIDE.md) für erweiterte Funktionen
2. Kontaktieren Sie Ihren System-Administrator
3. Wenden Sie sich an das Support-Team

---

**Version:** 1.0.0
**Letzte Aktualisierung:** Dezember 2025
**Teil des Employee Controlling Systems**
