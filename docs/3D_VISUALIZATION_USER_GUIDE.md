# 3D PV-Visualisierung - Benutzerhandbuch

## Übersicht

Die 3D PV-Visualisierung ermöglicht es Ihnen, Photovoltaik-Anlagen interaktiv zu planen und zu visualisieren. Dieses Handbuch führt Sie durch alle Funktionen und zeigt Ihnen, wie Sie das Beste aus dem Tool herausholen.

## Inhaltsverzeichnis

1. [Erste Schritte](#erste-schritte)
2. [Basis-Einstellungen](#basis-einstellungen)
3. [Modul-Belegung](#modul-belegung)
4. [Erweiterte Kontrolle](#erweiterte-kontrolle)
5. [Analyse-Funktionen](#analyse-funktionen)
6. [Export-Optionen](#export-optionen)
7. [Tipps & Tricks](#tipps--tricks)
8. [Häufige Probleme](#häufige-probleme)

---

## Erste Schritte

### Was Sie benötigen

- Grundlegende Gebäudedaten (Länge, Breite, Höhe)
- Dachform Ihres Gebäudes
- Gewünschte Modulanzahl oder Leistung

### Schnellstart

1. Öffnen Sie die 3D-Visualisierung über das Hauptmenü
2. Geben Sie die Gebäudedimensionen ein
3. Wählen Sie die Dachform aus
4. Passen Sie die Modul-Belegung an
5. Nutzen Sie die Analyse-Funktionen zur Optimierung
6. Exportieren Sie Ihre Konfiguration

---

## Basis-Einstellungen

### Gebäudedimensionen

#### Gebäudelänge
- **Bereich:** 8-60 Meter
- **Empfehlung:** Messen Sie die längste Seite Ihres Gebäudes
- **Beispiel:** Einfamilienhaus typisch 12m, Gewerbe 30m

#### Gebäudebreite
- **Bereich:** 5-40 Meter
- **Empfehlung:** Messen Sie die kürzere Seite
- **Beispiel:** Einfamilienhaus typisch 10m, Gewerbe 20m

#### Traufhöhe
- **Bereich:** 3-20 Meter
- **Definition:** Höhe der Außenwände (nicht Firsthöhe!)
- **Empfehlung:** Messen Sie vom Boden bis zur Dachkante
- **Beispiel:** Einfamilienhaus 3m, Mehrfamilienhaus 6-9m

### Dachformen

#### Flachdach
- **Beschreibung:** Horizontales oder leicht geneigtes Dach (0-10°)
- **Besonderheit:** Ermöglicht Aufständerung in verschiedenen Ausrichtungen
- **Optimal für:** Gewerbegebäude, moderne Architektur

#### Satteldach
- **Beschreibung:** Klassisches Dach mit zwei geneigten Flächen
- **Besonderheit:** Zwei nutzbare Dachflächen (Nord/Süd)
- **Optimal für:** Einfamilienhäuser, traditionelle Gebäude

#### Satteldach mit Gaube
- **Beschreibung:** Satteldach mit zusätzlichen Dachaufbauten
- **Besonderheit:** Komplexere Geometrie, weniger nutzbare Fläche
- **Optimal für:** Wohngebäude mit Dachgeschoss

#### Walmdach
- **Beschreibung:** Dach mit vier geneigten Flächen
- **Besonderheit:** Vier nutzbare Dachflächen, aber kleinere Einzelflächen
- **Optimal für:** Villen, repräsentative Gebäude

#### Pultdach
- **Beschreibung:** Einseitig geneigtes Dach
- **Besonderheit:** Eine große nutzbare Fläche
- **Optimal für:** Moderne Architektur, Anbauten

---

## Modul-Belegung

### Belegungsmodus

#### Automatisch
- **Funktion:** System verteilt Module gleichmäßig
- **Vorteil:** Schnell und einfach
- **Nachteil:** Keine individuelle Anpassung
- **Empfohlen für:** Erste Planung, Standard-Layouts

#### Manuell
- **Funktion:** Sie können einzelne Module entfernen
- **Vorteil:** Präzise Kontrolle über jedes Modul
- **Nachteil:** Zeitaufwendiger
- **Empfohlen für:** Feinabstimmung, Hindernisse umgehen

### Aufständerung (nur Flachdach)

#### Süd-Ausrichtung
- **Azimuth:** 0° (Süden)
- **Neigung:** 15-30°
- **Ertrag:** Maximal
- **Empfohlen für:** Optimale Energieausbeute

#### Ost-West-Ausrichtung
- **Azimuth:** 90° / 270° (Ost/West)
- **Neigung:** 10-15°
- **Ertrag:** Gleichmäßig über den Tag
- **Empfohlen für:** Eigenverbrauchsoptimierung

#### Süd-Ost / Süd-West
- **Azimuth:** 45° / 315°
- **Neigung:** 15-25°
- **Ertrag:** Kompromiss zwischen Süd und Ost-West
- **Empfohlen für:** Flexible Nutzung

#### Individuell
- **Azimuth:** 0-360° frei wählbar
- **Neigung:** 0-90° frei wählbar
- **Empfohlen für:** Spezielle Anforderungen, Experimente

### Zusätzliche Flächen

#### Garage/Carport
- **Funktion:** Fügt automatisch eine Garage hinzu
- **Wann:** Wenn Module nicht auf Hauptdach passen
- **Größe:** 6m x 3m (Standard)
- **Position:** Neben dem Hauptgebäude

#### Fassadenbelegung
- **Funktion:** Platziert Module an der Südfassade
- **Wann:** Als letzte Option bei Platzmangel
- **Neigung:** 90° (vertikal)
- **Ertrag:** Ca. 70% im Vergleich zu Dach

---

## Erweiterte Kontrolle

### Kollisionserkennung

#### Funktion
- Prüft automatisch auf Überschneidungen zwischen Modulen
- Zeigt Warnungen bei Konflikten an
- Verhindert unrealistische Konfigurationen

#### Wann deaktivieren?
- Bei experimentellen Layouts
- Wenn Sie bewusst dichte Belegung testen
- Bei bekannten False-Positives

### Modul-Auswahl & Bearbeitung

#### Einzelauswahl
**Schritt-für-Schritt:**
1. Wählen Sie "Einzeln" als Auswahl-Modus
2. Geben Sie den Index des Moduls ein (0 = erstes Modul)
3. Klicken Sie auf "➕ Auswählen"
4. Das Modul wird in der 3D-Ansicht hervorgehoben

**Beispiel:**
- Modul 0: Erstes Modul links oben
- Modul 5: Sechstes Modul in der Reihenfolge

#### Gruppenauswahl
**Schritt-für-Schritt:**
1. Wählen Sie "Gruppe" als Auswahl-Modus
2. Wählen Sie eine vordefinierte Gruppe aus
3. Klicken Sie auf "🔘 Gruppe auswählen"
4. Alle Module der Gruppe werden ausgewählt

**Verfügbare Gruppen:**
- Alle Module: Wählt alle platzierten Module
- Erste Hälfte: Wählt die ersten 50% der Module
- Zweite Hälfte: Wählt die letzten 50% der Module
- Benutzerdefinierte Gruppen: Ihre gespeicherten Gruppen

#### Bereichsauswahl
**Schritt-für-Schritt:**
1. Wählen Sie "Bereich" als Auswahl-Modus
2. Geben Sie Start-Index ein (z.B. 0)
3. Geben Sie End-Index ein (z.B. 9)
4. Klicken Sie auf "🔘 Bereich auswählen"
5. Module 0-9 werden ausgewählt

**Beispiel:**
- Von 0 bis 9: Erste 10 Module
- Von 10 bis 19: Module 11-20

---

## Analyse-Funktionen

### Optimierungs-Assistent

#### Maximale Modulanzahl
**Ziel:** Platziert so viele Module wie möglich
**Strategie:**
- Nutzt alle verfügbaren Flächen
- Minimiert Abstände zwischen Modulen
- Ignoriert Ertragsverluste durch ungünstige Ausrichtung

**Empfohlen für:**
- Maximale Leistung gewünscht
- Große verfügbare Flächen
- Niedrige Strompreise

#### Maximaler Ertrag
**Ziel:** Optimiert für höchste Energieausbeute
**Strategie:**
- Bevorzugt optimale Ausrichtungen (Süd)
- Vermeidet verschattete Bereiche
- Optimiert Neigungswinkel

**Empfohlen für:**
- Wirtschaftlichkeit im Fokus
- Einspeisevergütung
- Langfristige Planung

#### Ausgewogen
**Ziel:** Balance zwischen Anzahl und Ertrag
**Strategie:**
- Kompromiss zwischen Modulanzahl und Ertrag
- Berücksichtigt praktische Aspekte
- Realistische Konfiguration

**Empfohlen für:**
- Standardfall
- Unsichere Anforderungen
- Erste Planung

### Verschattungs-Analyse

#### Funktion
Berechnet die Verschattung jedes Moduls basierend auf:
- Tageszeit (6-20 Uhr)
- Jahreszeit (Sommer/Winter/Frühling-Herbst)
- Breitengrad (Standort)
- Gebäudegeometrie

#### Interpretation
- **Grün:** Keine Verschattung (0-10%)
- **Gelb:** Leichte Verschattung (10-30%)
- **Orange:** Mittlere Verschattung (30-60%)
- **Rot:** Starke Verschattung (60-100%)

#### Anwendung
**Schritt-für-Schritt:**
1. Aktivieren Sie "Verschattungs-Analyse"
2. Wählen Sie Tageszeit (z.B. 12:00 Uhr)
3. Wählen Sie Jahreszeit (z.B. Sommer)
4. Geben Sie Breitengrad ein (z.B. 51.0 für Deutschland)
5. Module werden entsprechend eingefärbt

**Tipps:**
- Testen Sie verschiedene Tageszeiten
- Vergleichen Sie Sommer vs. Winter
- Identifizieren Sie kritische Bereiche

### Sonnenverlauf-Animation

#### Funktion
Animiert den Sonnenverlauf über den Tag und zeigt die Verschattung in Echtzeit.

#### Einstellungen
- **Geschwindigkeit:** 1-10 (höher = schneller)
- **Start-Uhrzeit:** 6-18 Uhr
- **End-Uhrzeit:** 8-20 Uhr

#### Anwendung
**Schritt-für-Schritt:**
1. Aktivieren Sie "Sonnenverlauf-Animation"
2. Stellen Sie Geschwindigkeit ein (empfohlen: 5)
3. Wählen Sie Zeitbereich (z.B. 6-20 Uhr)
4. Animation startet nach dem Rendern

**Nutzen:**
- Verstehen Sie Verschattungsmuster
- Identifizieren Sie Problemzeiten
- Optimieren Sie Modul-Platzierung

### Ertrags-Heatmap

#### Funktion
Visualisiert das Ertragspotential jedes Moduls mit Farbcodierung.

#### Metriken
- **Jahresertrag (kWh):** Erwartete Energieproduktion
- **Verschattung (%):** Durchschnittliche Verschattung
- **Effizienz (%):** Relative Effizienz zum Optimum

#### Interpretation
- **Dunkelgrün:** Höchster Ertrag (90-100%)
- **Hellgrün:** Guter Ertrag (70-90%)
- **Gelb:** Mittlerer Ertrag (50-70%)
- **Orange:** Niedriger Ertrag (30-50%)
- **Rot:** Sehr niedriger Ertrag (<30%)

#### Anwendung
**Schritt-für-Schritt:**
1. Aktivieren Sie "Ertrags-Heatmap"
2. Wählen Sie Metrik (z.B. Jahresertrag)
3. Heatmap wird nach dem Rendern angezeigt
4. Identifizieren Sie schwache Module

**Optimierung:**
- Entfernen Sie rote Module (sehr niedriger Ertrag)
- Priorisieren Sie grüne Bereiche
- Passen Sie Ausrichtung an

### Live-Ertragsprognose

#### Funktion
Berechnet den erwarteten Jahresertrag für die aktuelle Konfiguration.

#### Parameter
- **Strompreis:** 0.10-1.00 €/kWh (Standard: 0.30 €/kWh)
- **Modul-Wirkungsgrad:** 15-25% (Standard: 20%)

#### Ausgabe
- Jahresertrag in kWh
- Jahresersparnis in €
- CO₂-Einsparung in kg
- Amortisationszeit in Jahren

#### Anwendung
**Schritt-für-Schritt:**
1. Aktivieren Sie "Ertragsprognose"
2. Geben Sie aktuellen Strompreis ein
3. Wählen Sie Modul-Wirkungsgrad
4. Prognose wird nach dem Rendern berechnet

---

## Export-Optionen

### Screenshot-Export

#### Formate
- **PNG:** Verlustfrei, größere Dateien, beste Qualität
- **JPEG:** Komprimiert, kleinere Dateien, gute Qualität

#### Auflösungen
- **HD (1280x720):** Für Web, E-Mail
- **Full HD (1920x1080):** Standard, beste Balance
- **2K (2560x1440):** Hohe Qualität, Präsentationen
- **4K (3840x2160):** Maximale Qualität, Druck

#### Anwendung
**Schritt-für-Schritt:**
1. Aktivieren Sie "Screenshot exportieren"
2. Wählen Sie Format (PNG empfohlen)
3. Wählen Sie Auflösung (Full HD empfohlen)
4. Screenshot wird automatisch heruntergeladen

### Multi-View Screenshots

#### Funktion
Erstellt Screenshots aus 4 Perspektiven:
- Isometrisch (3D-Ansicht)
- Top (Draufsicht)
- Süd (Südansicht)
- Ost (Ostansicht)

#### Ausgabe
ZIP-Datei mit 4 Bildern

#### Anwendung
**Schritt-für-Schritt:**
1. Aktivieren Sie "Multi-View Export"
2. Wählen Sie Auflösung
3. ZIP-Datei wird heruntergeladen
4. Entpacken Sie die Datei

**Nutzen:**
- Vollständige Dokumentation
- Verschiedene Perspektiven
- Präsentationen

### 360° Animation

#### Funktion
Erstellt eine 360° Rotation als GIF-Animation.

#### Einstellungen
- **Frames:** 12-72 (mehr = flüssiger, größere Datei)
- **Auflösung:** Klein/Mittel/Groß

#### Empfehlungen
- **Web:** 36 Frames, Klein (600x450)
- **Präsentation:** 48 Frames, Mittel (800x600)
- **Druck:** 72 Frames, Groß (1200x900)

#### Anwendung
**Schritt-für-Schritt:**
1. Aktivieren Sie "360° Animation exportieren"
2. Wählen Sie Frames (36 empfohlen)
3. Wählen Sie Auflösung
4. GIF wird heruntergeladen

**Hinweis:** Erstellung kann 30-60 Sekunden dauern

### 3D-Modell Export

#### Formate
- **STL:** Für 3D-Druck, CAD-Software
- **GLTF:** Für Web-Visualisierung, AR/VR
- **OBJ:** Universelles Format, 3D-Software

#### Anwendung
**Schritt-für-Schritt:**
1. Aktivieren Sie "3D-Modell exportieren"
2. Wählen Sie Format
3. Modell wird heruntergeladen

**Verwendung:**
- Import in CAD-Software
- 3D-Druck von Modellen
- Weitere Bearbeitung

### Daten-Export

#### CSV-Export
**Inhalt:**
- Modul-Index
- Position (X, Y, Z)
- Ausrichtung (Azimuth, Neigung)
- Ertragsprognose
- Verschattung

**Verwendung:**
- Excel-Analyse
- Datenbank-Import
- Weitere Berechnungen

#### JSON-Export
**Inhalt:**
- Vollständige Layout-Konfiguration
- Alle Einstellungen
- Modul-Transformationen
- Gruppen-Definitionen

**Verwendung:**
- Backup der Konfiguration
- Import in andere Tools
- Versionskontrolle

---

## Tipps & Tricks

### Performance-Optimierung

#### Bei vielen Modulen (>50)
- Deaktivieren Sie Kollisionserkennung während der Planung
- Nutzen Sie "Automatisch" Modus für erste Platzierung
- Aktivieren Sie Analysen nur bei Bedarf

#### Bei langsamer Hardware
- Reduzieren Sie Export-Auflösungen
- Verwenden Sie weniger Animations-Frames
- Schließen Sie nicht benötigte Expander

### Workflow-Empfehlungen

#### Schnelle Planung (5 Minuten)
1. Gebäudedaten eingeben
2. Dachform wählen
3. Optimierungs-Assistent nutzen (Ausgewogen)
4. Screenshot exportieren

#### Detaillierte Planung (30 Minuten)
1. Gebäudedaten präzise eingeben
2. Dachform und Aufständerung optimieren
3. Verschattungs-Analyse durchführen
4. Ertrags-Heatmap prüfen
5. Schwache Module entfernen
6. Optimierungs-Assistent nutzen (Max. Ertrag)
7. Multi-View Export erstellen
8. Daten als CSV/JSON sichern

#### Professionelle Planung (1-2 Stunden)
1. Alle Gebäudedaten vermessen
2. Verschiedene Dachformen testen
3. Verschattungs-Analyse für alle Jahreszeiten
4. Sonnenverlauf-Animation prüfen
5. Ertrags-Heatmap optimieren
6. Mehrere Konfigurationen vergleichen
7. Beste Konfiguration auswählen
8. Vollständige Dokumentation exportieren

### Häufige Optimierungen

#### Ertrag maximieren
1. Nutzen Sie Süd-Ausrichtung
2. Optimale Neigung: 30-35° (Deutschland)
3. Vermeiden Sie verschattete Bereiche
4. Entfernen Sie Module mit <50% Ertrag

#### Kosten minimieren
1. Nutzen Sie nur Hauptdach (keine Garage/Fassade)
2. Standardisierte Ausrichtung
3. Weniger, aber effizientere Module
4. Einfache Montage-Systeme

#### Eigenverbrauch optimieren
1. Ost-West-Ausrichtung auf Flachdach
2. Gleichmäßige Produktion über den Tag
3. Mittlere Modulanzahl
4. Kombination mit Speicher

---

## Häufige Probleme

### Module werden nicht angezeigt

**Ursachen:**
- Gebäudedimensionen zu klein
- Dachform nicht kompatibel
- Fehler in der Konfiguration

**Lösungen:**
1. Prüfen Sie Gebäudedimensionen (min. 8x5m)
2. Wählen Sie andere Dachform
3. Setzen Sie Konfiguration zurück
4. Aktivieren Sie "Garage/Carport"

### Kollisionswarnungen

**Ursachen:**
- Module überschneiden sich
- Zu dichte Belegung
- Fehlerhafte Transformationen

**Lösungen:**
1. Deaktivieren Sie Kollisionserkennung temporär
2. Vergrößern Sie Abstände
3. Nutzen Sie Optimierungs-Assistent
4. Entfernen Sie problematische Module

### Export funktioniert nicht

**Ursachen:**
- Browser blockiert Download
- Zu große Datei
- Fehler in der Konfiguration

**Lösungen:**
1. Erlauben Sie Downloads im Browser
2. Reduzieren Sie Auflösung/Frames
3. Versuchen Sie anderen Export-Format
4. Aktualisieren Sie die Seite

### Verschattungs-Analyse zeigt keine Farben

**Ursachen:**
- Analyse nicht aktiviert
- Fehler in Berechnung
- Alle Module gleich verschattet

**Lösungen:**
1. Aktivieren Sie "Verschattungs-Analyse"
2. Wählen Sie andere Tageszeit
3. Prüfen Sie Breitengrad-Eingabe
4. Aktualisieren Sie die Visualisierung

### Performance-Probleme

**Ursachen:**
- Zu viele Module (>100)
- Zu hohe Export-Auflösung
- Langsame Hardware
- Viele Analysen gleichzeitig

**Lösungen:**
1. Reduzieren Sie Modulanzahl
2. Deaktivieren Sie nicht benötigte Analysen
3. Schließen Sie andere Browser-Tabs
4. Verwenden Sie niedrigere Auflösungen
5. Aktivieren Sie nur eine Analyse gleichzeitig

---

## Glossary

### Fachbegriffe

**Azimuth:** Horizontale Ausrichtung in Grad (0° = Süd, 90° = West, 180° = Nord, 270° = Ost)

**Neigung/Tilt:** Vertikaler Winkel zur Horizontalen (0° = flach, 90° = senkrecht)

**Traufhöhe:** Höhe der Außenwände vom Boden bis zur Dachkante

**Firsthöhe:** Höchster Punkt des Daches

**Aufständerung:** Montagesystem für Flachdächer, das Module in optimalen Winkel neigt

**Verschattung:** Reduzierung der Sonneneinstrahlung durch Hindernisse

**Ertragspotential:** Erwartete Energieproduktion eines Moduls

**Wirkungsgrad:** Verhältnis von erzeugter Energie zu eingestrahlter Sonnenenergie

**kWp:** Kilowatt Peak - Nennleistung unter Standardbedingungen

**kWh:** Kilowattstunde - Energiemenge

---

## Support & Feedback

Bei Fragen oder Problemen:
1. Konsultieren Sie dieses Handbuch
2. Prüfen Sie die Tooltips in der Anwendung
3. Kontaktieren Sie den Support

**Viel Erfolg bei Ihrer PV-Planung!** ☀️
