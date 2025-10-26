# Extended PDF User Guide

## Benutzerhandbuch: Erweiterte PDF-Ausgabe

### Inhaltsverzeichnis

1. [Einführung](#einführung)
2. [Aktivierung der erweiterten PDF-Ausgabe](#aktivierung-der-erweiterten-pdf-ausgabe)
3. [Finanzierungsdetails hinzufügen](#finanzierungsdetails-hinzufügen)
4. [Produktdatenblätter einbinden](#produktdatenblätter-einbinden)
5. [Firmendokumente einbinden](#firmendokumente-einbinden)
6. [Diagramme und Visualisierungen auswählen](#diagramme-und-visualisierungen-auswählen)
7. [Layout-Optionen für Diagramme](#layout-optionen-für-diagramme)
8. [PDF generieren und herunterladen](#pdf-generieren-und-herunterladen)
9. [Fehlerbehebung](#fehlerbehebung)
10. [Tipps und Best Practices](#tipps-und-best-practices)

---

## Einführung

Die erweiterte PDF-Ausgabe ermöglicht es Ihnen, zusätzliche Seiten an Ihr Standard-Angebot anzuhängen. Diese Zusatzseiten können enthalten:

- **Finanzierungsdetails**: Übersicht über Finanzierungsoptionen mit monatlichen Raten
- **Produktdatenblätter**: Technische Datenblätter der verwendeten Produkte
- **Firmendokumente**: AGBs, Garantiebedingungen, Zertifikate
- **Diagramme**: Alle verfügbaren Visualisierungen aus der Analyse

**Wichtig:** Die erweiterte PDF-Ausgabe ist optional. Wenn Sie sie nicht aktivieren, wird wie gewohnt das Standard-8-Seiten-PDF erstellt.

---

## Aktivierung der erweiterten PDF-Ausgabe

### Schritt 1: PDF-Erstellungsseite öffnen

1. Navigieren Sie zur PDF-Erstellung in der Anwendung
2. Wählen Sie Ihr Projekt und Ihre Berechnung aus
3. Scrollen Sie zum Bereich "PDF-Optionen"

### Schritt 2: Erweiterte Ausgabe aktivieren

1. Suchen Sie die Checkbox **"🔧 Erweiterte PDF-Ausgabe aktivieren"**
2. Aktivieren Sie die Checkbox durch Anklicken
3. Es erscheinen nun zusätzliche Optionen für die erweiterte Ausgabe

![Aktivierung der erweiterten PDF-Ausgabe](screenshots/extended_pdf_activation.png)

**Hinweis:** Wenn die Checkbox nicht aktiviert ist, wird nur das Standard-PDF generiert.

---

## Finanzierungsdetails hinzufügen

### Übersicht

Die Finanzierungsdetails zeigen Ihren Kunden alle verfügbaren Finanzierungsoptionen mit:

- Laufzeit in Monaten/Jahren
- Zinssatz
- Monatliche Rate
- Gesamtkosten
- Zinsbelastung

### Aktivierung

1. Klappen Sie den Bereich **"💰 Finanzierungsdetails"** auf
2. Aktivieren Sie die Checkbox **"Finanzierungsoptionen einbinden"**
3. Die Finanzierungsseiten werden automatisch generiert

![Finanzierungsdetails aktivieren](screenshots/financing_options.png)

### Was wird angezeigt?

**Seite 1: Finanzierungsübersicht**

- Titel und Einleitung
- Übersicht aller verfügbaren Finanzierungsoptionen
- Für jede Option: Name, Beschreibung, Laufzeit, Zinssatz, monatliche Rate

**Seite 2: Detaillierte Berechnung**

- Finanzierungsbetrag
- Laufzeit
- Zinssatz
- Monatliche Rate
- Gesamtzahlung
- Zinskosten gesamt

### Voraussetzungen

- Finanzierungsoptionen müssen im Admin-Bereich konfiguriert sein
- Mindestens eine Finanzierungsoption muss aktiviert sein

---

## Produktdatenblätter einbinden

### Übersicht

Produktdatenblätter sind technische Dokumente, die detaillierte Informationen über die verwendeten Produkte enthalten (z.B. PV-Module, Wechselrichter, Speicher).

### Auswahl der Datenblätter

1. Klappen Sie den Bereich **"📄 Produktdatenblätter"** auf
2. Es werden alle Produkte angezeigt, für die Datenblätter verfügbar sind
3. Wählen Sie die gewünschten Produkte aus der Liste aus
4. Sie können mehrere Datenblätter gleichzeitig auswählen

![Produktdatenblätter auswählen](screenshots/product_datasheets.png)

### Unterstützte Formate

- **PDF-Datenblätter**: Werden direkt eingebunden (alle Seiten)
- **Bild-Datenblätter**: Werden auf einer Seite zentriert dargestellt

### Reihenfolge

Die Datenblätter werden in der Reihenfolge angehängt, in der Sie sie auswählen.

### Tipps

- Wählen Sie nur die wichtigsten Datenblätter aus, um die PDF nicht zu groß zu machen
- Prüfen Sie vor der Generierung, ob die Datenblätter aktuell sind
- Bei mehrseitigen Datenblättern werden alle Seiten eingebunden

---

## Firmendokumente einbinden

### Übersicht

Firmendokumente sind allgemeine Dokumente Ihres Unternehmens wie:

- Allgemeine Geschäftsbedingungen (AGB)
- Garantiebedingungen
- Zertifikate
- Referenzen
- Firmenpräsentation

### Auswahl der Dokumente

1. Klappen Sie den Bereich **"🏢 Firmendokumente"** auf
2. Es werden alle verfügbaren Firmendokumente angezeigt
3. Wählen Sie die gewünschten Dokumente aus der Liste aus
4. Sie können mehrere Dokumente gleichzeitig auswählen

![Firmendokumente auswählen](screenshots/company_documents.png)

### Verwaltung von Firmendokumenten

Firmendokumente werden im Admin-Bereich verwaltet:

1. Navigieren Sie zu **Admin → Firmendokumente**
2. Laden Sie neue Dokumente hoch
3. Geben Sie jedem Dokument einen aussagekräftigen Namen
4. Aktivieren Sie die Dokumente für die Verwendung in PDFs

### Best Practices

- Fügen Sie AGBs immer am Ende hinzu
- Halten Sie Dokumente aktuell
- Verwenden Sie aussagekräftige Dateinamen
- Prüfen Sie die Dateigröße (große Dokumente verlängern die Generierungszeit)

---

## Diagramme und Visualisierungen auswählen

### Übersicht

Die Anwendung erstellt automatisch zahlreiche Diagramme und Visualisierungen aus Ihrer Berechnung. Sie können auswählen, welche davon in die PDF eingebunden werden sollen.

### Kategorien von Diagrammen

Die Diagramme sind in folgende Kategorien unterteilt:

#### 1. Wirtschaftlichkeit

- Kumulierter Cashflow
- Stromkosten-Hochrechnung
- Break-Even-Analyse
- Amortisationsdiagramm
- ROI-Vergleich
- Projektrendite-Matrix

#### 2. Produktion & Verbrauch

- Monatliche Produktion vs. Verbrauch
- Jahresproduktion
- Tagesproduktion (3D)
- Wochenproduktion (3D)
- Produktion vs. Verbrauch (3D)

#### 3. Eigenverbrauch & Autarkie

- Verbrauchsdeckung (Kreisdiagramm)
- PV-Nutzung (Kreisdiagramm)
- Speicherwirkung (3D)
- Eigenverbrauch vs. Einspeisung (3D)
- Eigenverbrauchsgrad (3D)

#### 4. Finanzielle Analyse

- Einspeisevergütung (3D)
- Einnahmenprognose (3D)
- Tarifvergleich (3D)
- Stromkostensteigerung (3D)

#### 5. CO2 & Umwelt

- CO2-Ersparnis vs. Wert (3D)

#### 6. Vergleiche & Szenarien

- Szenarienvergleich (3D)
- Vorher/Nachher Stromkosten (3D)
- Investitionsnutzwert (3D)

### Auswahl von Diagrammen

1. Klappen Sie den Bereich **"📊 Diagramme & Visualisierungen"** auf
2. Wählen Sie eine Kategorie aus den Tabs
3. Aktivieren Sie die gewünschten Diagramme durch Anklicken der Checkboxen
4. Nutzen Sie die Buttons für schnelle Auswahl:
   - **"Alle auswählen"**: Wählt alle Diagramme der aktuellen Kategorie
   - **"Alle abwählen"**: Entfernt alle Auswahlen

![Diagramme auswählen](screenshots/chart_selection.png)

### Vorschau-Funktion

- Klicken Sie auf das Augen-Symbol (👁️) neben einem Diagramm
- Es öffnet sich eine Vorschau des Diagramms
- So können Sie vor der Generierung prüfen, ob das Diagramm relevant ist

### Batch-Operationen

**Alle Diagramme auswählen:**

1. Wechseln Sie zum Tab **"Alle"**
2. Klicken Sie auf **"Alle auswählen"**
3. Alle verfügbaren Diagramme werden ausgewählt

**Alle Diagramme abwählen:**

1. Wechseln Sie zum Tab **"Alle"**
2. Klicken Sie auf **"Alle abwählen"**
3. Alle Auswahlen werden entfernt

### Hinweise

- Ausgegraut Diagramme sind nicht verfügbar (z.B. wenn keine Daten vorhanden sind)
- Die Anzahl der ausgewählten Diagramme wird unten angezeigt
- Bei vielen Diagrammen wird eine Warnung angezeigt (PDF wird groß)

---

## Layout-Optionen für Diagramme

### Verfügbare Layouts

Sie können wählen, wie die Diagramme auf den Seiten angeordnet werden:

#### 1. Ein Diagramm pro Seite (Vollbild)

- **Vorteil**: Maximale Größe und Detailgenauigkeit
- **Nachteil**: Viele Seiten bei vielen Diagrammen
- **Empfohlen für**: Wichtige Hauptdiagramme, komplexe 3D-Visualisierungen

![Ein Diagramm pro Seite](screenshots/layout_one_per_page.png)

#### 2. Zwei Diagramme pro Seite (2x1)

- **Vorteil**: Gute Balance zwischen Größe und Seitenanzahl
- **Nachteil**: Etwas weniger Detailgenauigkeit
- **Empfohlen für**: Standard-Verwendung, Mix aus verschiedenen Diagrammen

![Zwei Diagramme pro Seite](screenshots/layout_two_per_page.png)

#### 3. Vier Diagramme pro Seite (2x2)

- **Vorteil**: Kompakte Darstellung, wenige Seiten
- **Nachteil**: Kleinere Diagramme, weniger Details sichtbar
- **Empfohlen für**: Übersichtsseiten, viele ähnliche Diagramme

![Vier Diagramme pro Seite](screenshots/layout_four_per_page.png)

### Layout auswählen

1. Im Bereich **"📊 Diagramme & Visualisierungen"**
2. Wählen Sie das gewünschte Layout aus dem Dropdown **"Layout"**
3. Das Layout wird auf alle ausgewählten Diagramme angewendet

### Automatische Seitenumbrüche

- Wenn mehr Diagramme ausgewählt sind als auf eine Seite passen, werden automatisch weitere Seiten erstellt
- Beispiel: 10 Diagramme mit Layout "Vier pro Seite" = 3 Seiten (4+4+2)

---

## PDF generieren und herunterladen

### Generierung starten

1. Nachdem Sie alle gewünschten Optionen ausgewählt haben
2. Scrollen Sie nach unten zum Button **"PDF generieren"**
3. Klicken Sie auf den Button
4. Ein Fortschrittsbalken zeigt den Generierungsstatus

![PDF wird generiert](screenshots/pdf_generation.png)

### Generierungsdauer

Die Dauer hängt von der Anzahl der ausgewählten Elemente ab:

- **Nur Finanzierung**: ~2-3 Sekunden
- **Mit Datenblättern**: ~5-10 Sekunden
- **Mit vielen Diagrammen**: ~10-20 Sekunden
- **Vollständige erweiterte PDF**: ~20-30 Sekunden

### Warnungen und Fehler

**Warnungen (gelb):**

- Einzelne Elemente konnten nicht geladen werden
- PDF wurde trotzdem erstellt, aber einige Inhalte fehlen
- Beispiel: "Produktdatenblatt für Produkt 5 nicht gefunden"

**Fehler (rot):**

- Kritischer Fehler bei der Generierung
- Es wird automatisch auf das Standard-PDF zurückgefallen
- Beispiel: "Erweiterte PDF-Generierung fehlgeschlagen. Standard-PDF wird verwendet."

### Download

1. Nach erfolgreicher Generierung erscheint der Download-Button
2. Klicken Sie auf **"PDF herunterladen"**
3. Die PDF wird in Ihrem Browser heruntergeladen
4. Dateiname: `Angebot_[Kundename]_[Datum].pdf`

### Vorschau

- Einige Browser zeigen eine Vorschau der PDF an
- Sie können die PDF vor dem Download prüfen
- Nutzen Sie die Zoom-Funktion für Details

---

## Fehlerbehebung

### Problem: Erweiterte Optionen werden nicht angezeigt

**Lösung:**

- Prüfen Sie, ob die Checkbox "Erweiterte PDF-Ausgabe aktivieren" aktiviert ist
- Aktualisieren Sie die Seite (F5)
- Prüfen Sie Ihre Berechtigungen

### Problem: Keine Finanzierungsoptionen verfügbar

**Lösung:**

- Finanzierungsoptionen müssen im Admin-Bereich konfiguriert sein
- Kontaktieren Sie Ihren Administrator
- Prüfen Sie, ob mindestens eine Option aktiviert ist

### Problem: Produktdatenblätter fehlen

**Lösung:**

- Prüfen Sie, ob für die Produkte Datenblätter hochgeladen wurden
- Gehen Sie zu Admin → Produktdatenbank
- Laden Sie fehlende Datenblätter hoch

### Problem: Diagramme werden nicht angezeigt

**Lösung:**

- Stellen Sie sicher, dass die Berechnung abgeschlossen ist
- Prüfen Sie, ob Diagramme in der Analyse sichtbar sind
- Aktualisieren Sie die Berechnung

### Problem: PDF-Generierung dauert sehr lange

**Lösung:**

- Reduzieren Sie die Anzahl der ausgewählten Diagramme
- Wählen Sie ein kompakteres Layout (4 pro Seite)
- Prüfen Sie die Größe der Datenblätter
- Warten Sie geduldig (bis zu 30 Sekunden ist normal)

### Problem: PDF ist zu groß

**Lösung:**

- Reduzieren Sie die Anzahl der Diagramme
- Entfernen Sie große Datenblätter
- Verwenden Sie komprimierte Datenblätter
- Wählen Sie nur die wichtigsten Elemente

### Problem: Fehler "Erweiterte PDF-Generierung fehlgeschlagen"

**Lösung:**

- Es wird automatisch das Standard-PDF erstellt
- Prüfen Sie die Fehlermeldung für Details
- Versuchen Sie es mit weniger Optionen
- Kontaktieren Sie den Support bei wiederholten Fehlern

---

## Tipps und Best Practices

### Für optimale Ergebnisse

1. **Weniger ist mehr**: Wählen Sie nur relevante Diagramme aus
2. **Logische Reihenfolge**: Finanzierung → Datenblätter → Diagramme → Dokumente
3. **Zielgruppe beachten**: Technische Kunden = mehr Diagramme, Privatkunden = weniger
4. **Dateigröße im Blick**: Große PDFs sind schwer zu versenden
5. **Vorschau nutzen**: Prüfen Sie Diagramme vor der Auswahl

### Empfohlene Konfigurationen

**Für Privatkunden:**

- Finanzierungsdetails: ✓
- 5-8 wichtigste Diagramme (Wirtschaftlichkeit, Produktion)
- Layout: 2 pro Seite
- AGBs als Firmendokument

**Für Geschäftskunden:**

- Finanzierungsdetails: ✓
- 10-15 Diagramme (alle Kategorien)
- Layout: 2 pro Seite
- Alle relevanten Datenblätter
- Zertifikate und Referenzen

**Für technische Präsentationen:**

- Alle Diagramme
- Layout: 1 pro Seite
- Alle Datenblätter
- Technische Dokumente

### Zeitersparnis

- **Vorlagen erstellen**: Speichern Sie häufig verwendete Konfigurationen
- **Batch-Auswahl**: Nutzen Sie "Alle auswählen" für Kategorien
- **Standard-Layout**: Definieren Sie ein Standard-Layout für Ihr Team

### Qualitätssicherung

- Prüfen Sie die generierte PDF vor dem Versand
- Achten Sie auf vollständige Seitenzahlen
- Kontrollieren Sie die Lesbarkeit der Diagramme
- Testen Sie die PDF auf verschiedenen Geräten

---

## Häufig gestellte Fragen (FAQ)

**F: Kann ich die Reihenfolge der Zusatzseiten ändern?**
A: Ja, die Reihenfolge ist: Finanzierung → Datenblätter → Firmendokumente → Diagramme. Diese Reihenfolge ist fest, aber Sie können einzelne Bereiche weglassen.

**F: Werden die Seitenzahlen automatisch angepasst?**
A: Ja, die Seitennummerierung läuft durchgehend von Seite 1 bis zur letzten Seite.

**F: Kann ich eigene Diagramme hinzufügen?**
A: Nein, es können nur die automatisch generierten Diagramme verwendet werden. Für eigene Grafiken nutzen Sie Firmendokumente.

**F: Wie groß darf die PDF maximal sein?**
A: Es gibt keine feste Grenze, aber wir empfehlen maximal 50 Seiten und 20 MB für gute Performance.

**F: Kann ich die erweiterte PDF als Standard festlegen?**
A: Nein, die erweiterte PDF muss jedes Mal manuell aktiviert werden. Dies verhindert versehentlich große PDFs.

**F: Werden meine Einstellungen gespeichert?**
A: Die Einstellungen werden für die aktuelle Sitzung gespeichert, aber nicht dauerhaft. Nutzen Sie Vorlagen für häufig verwendete Konfigurationen.

---

## Kontakt und Support

Bei Fragen oder Problemen:

- Konsultieren Sie diese Anleitung
- Prüfen Sie die Fehlermeldungen
- Kontaktieren Sie Ihren Administrator
- Wenden Sie sich an den technischen Support

**Version:** 1.0.0  
**Stand:** Januar 2025
