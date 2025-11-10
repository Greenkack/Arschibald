# Requirements Document

## Introduction

Dieses Projekt optimiert die Positionierung von dynamischen und statischen Textelementen in Multi-PDF-Angeboten für Photovoltaik-Systeme. Es gibt 6 verschiedene Firmenvorlagen mit jeweils 8 Seiten (48 PDFs insgesamt). Jede Vorlage hat ein einzigartiges Design mit unterschiedlichen Formen, Farben und Layouts. Die Koordinaten für Textelemente werden in YML-Dateien gespeichert und müssen individuell an das jeweilige Design angepasst werden, um eine optimale visuelle Präsentation zu erreichen.

## Glossary

- **Multi-PDF-System**: Das System zur Generierung von mehrseitigen PDF-Angeboten mit verschiedenen Firmenvorlagen
- **PDF-Vorlage**: Eine statische PDF-Datei ohne Text (nur Design/Formen), benannt als `multi_nt_[Seite]_f[Firma].pdf`
- **YML-Koordinatendatei**: YAML-Datei mit Positionsangaben für Text-Elemente, benannt als `seite[Seite]_f[Firma].yml`
- **Dynamischer Wert**: Variable Textelemente wie Kundenname, kWp-Anzahl, Datum (z.B. `kunde_vorname_und_nachname`, `kWp_anlage_anlage`)
- **Statischer Wert**: Feste Textelemente wie Überschriften, Labels (z.B. "ERSTELLT FÜR:", "PHOTOVOLTAIK", "ANGEBOT")
- **Design-Element**: Visuelle Komponenten in der PDF-Vorlage wie Formen, Farbbereiche, Linien
- **Positionskoordinaten**: Rechteck-Koordinaten im Format (x1, y1, x2, y2) für die Platzierung von Text
- **Firmenvorlage**: Eine komplette Set von 8 Seiten für eine spezifische Firma (f1 bis f6)

## Requirements

### Requirement 1: PDF-Vorlagen-Analyse

**User Story:** Als Entwickler möchte ich alle 48 PDF-Vorlagen analysieren, damit ich die Design-Charakteristiken jeder Vorlage verstehe und optimale Positionierungen bestimmen kann.

#### Acceptance Criteria

1. WHEN THE PDF_Analysis_Tool ausgeführt wird, THE Multi-PDF-System SHALL alle 48 PDF-Dateien aus dem Verzeichnis `C:\Users\win10\Desktop\Bokuk2 - Kopie\pdf_templates_static\multi` einlesen
2. FOR EACH PDF-Vorlage, THE Multi-PDF-System SHALL Design-Merkmale extrahieren, einschließlich Farbverteilung, Formpositionen und verfügbare Textbereiche
3. THE Multi-PDF-System SHALL eine strukturierte Analyse-Ausgabe generieren, die für jede Firma und Seite die Design-Charakteristiken dokumentiert
4. THE Multi-PDF-System SHALL Unterschiede zwischen Firmenvorlagen identifizieren und dokumentieren
5. THE Multi-PDF-System SHALL die Analyse-Ergebnisse in einem maschinenlesbaren Format speichern

### Requirement 2: YML-Koordinaten-Struktur

**User Story:** Als Entwickler möchte ich die aktuelle YML-Struktur verstehen, damit ich weiß, welche Elemente neu positioniert werden müssen, ohne deren Inhalt zu verändern.

#### Acceptance Criteria

1. THE Multi-PDF-System SHALL alle vorhandenen YML-Dateien aus dem Verzeichnis `coords_multi` einlesen
2. FOR EACH YML-Datei, THE Multi-PDF-System SHALL alle Text-Elemente mit ihren vollständigen Attributen (Text, Position, Schriftart, Schriftgröße, Farbe) extrahieren
3. THE Multi-PDF-System SHALL die Reihenfolge der Text-Elemente in der YML-Datei beibehalten
4. THE Multi-PDF-System SHALL alle Attribute außer Position unverändert übernehmen
5. THE Multi-PDF-System SHALL die YML-Formatierung und Struktur exakt replizieren

### Requirement 3: Design-basierte Positionierungs-Regeln

**User Story:** Als Designer möchte ich, dass Text-Elemente basierend auf dem PDF-Design optimal positioniert werden, damit die Angebote professionell und visuell ansprechend aussehen.

#### Acceptance Criteria

1. FOR EACH Firmenvorlage, THE Multi-PDF-System SHALL individuelle Positionierungs-Regeln basierend auf Design-Elementen definieren
2. WHEN ein Design-Element einen bestimmten Farbbereich hat, THE Multi-PDF-System SHALL Text-Elemente so positionieren, dass sie mit diesem Bereich harmonieren
3. THE Multi-PDF-System SHALL wichtige dynamische Werte (wie kWp-Anzahl, Preis) in visuell prominenten Bereichen platzieren
4. THE Multi-PDF-System SHALL sicherstellen, dass Text-Elemente nicht mit Design-Formen überlappen
5. THE Multi-PDF-System SHALL Abstände und Ausrichtungen basierend auf dem Grid-System der jeweiligen Vorlage berechnen

### Requirement 4: Individuelle Positionierung pro Firma und Seite

**User Story:** Als Benutzer möchte ich, dass jede Firmenvorlage und jede Seite eine einzigartige Positionierung hat, damit die Vielfalt der Designs optimal genutzt wird.

#### Acceptance Criteria

1. THE Multi-PDF-System SHALL für jede Kombination aus Firma und Seite (48 Kombinationen) eine individuelle Positionierung generieren
2. THE Multi-PDF-System SHALL sicherstellen, dass keine zwei Firmenvorlagen identische Positionierungen für dieselbe Seite haben
3. WHEN Seite 1 von Firma 1 analysiert wird, THE Multi-PDF-System SHALL eine andere Positionierung generieren als für Seite 1 von Firma 2
4. THE Multi-PDF-System SHALL die Einzigartigkeit jeder Positionierung validieren
5. THE Multi-PDF-System SHALL Positionierungs-Varianten dokumentieren

### Requirement 5: YML-Datei-Generierung

**User Story:** Als Entwickler möchte ich, dass das System automatisch optimierte YML-Dateien generiert, damit ich die neuen Koordinaten direkt verwenden kann.

#### Acceptance Criteria

1. THE Multi-PDF-System SHALL für jede der 48 Kombinationen die bestehende YML-Datei aktualisieren
2. THE Multi-PDF-System SHALL das bestehende YML-Format exakt beibehalten (Text, Position, Schriftart, Schriftgröße, Farbe)
3. THE Multi-PDF-System SHALL alle Text-Werte, Schriftarten, Schriftgrößen und Farben unverändert lassen
4. THE Multi-PDF-System SHALL ausschließlich die Positions-Koordinaten (x1, y1, x2, y2) basierend auf der Design-Analyse ändern
5. THE Multi-PDF-System SHALL keine neuen Text-Elemente hinzufügen oder bestehende entfernen

### Requirement 6: Validierung und Qualitätssicherung

**User Story:** Als Qualitätssicherer möchte ich, dass alle generierten Positionierungen validiert werden, damit keine Text-Elemente außerhalb der PDF-Grenzen oder überlappend platziert werden.

#### Acceptance Criteria

1. THE Multi-PDF-System SHALL für jede generierte Position prüfen, dass sie innerhalb der PDF-Grenzen liegt (0-595 für Breite, 0-842 für Höhe bei A4)
2. THE Multi-PDF-System SHALL Überlappungen zwischen Text-Elementen erkennen und vermeiden
3. THE Multi-PDF-System SHALL sicherstellen, dass Text-Elemente ausreichend Abstand zu PDF-Rändern haben (mindestens 10 Punkte)
4. THE Multi-PDF-System SHALL eine Validierungs-Report generieren, der alle Prüfungen dokumentiert
5. WHEN eine Validierung fehlschlägt, THE Multi-PDF-System SHALL eine Warnung ausgeben und alternative Positionen vorschlagen

### Requirement 7: Dokumentation und Visualisierung

**User Story:** Als Benutzer möchte ich die Unterschiede zwischen den Positionierungen visualisieren können, damit ich die Optimierungen nachvollziehen kann.

#### Acceptance Criteria

1. THE Multi-PDF-System SHALL für jede Firma einen Vergleich zwischen alter und neuer Positionierung generieren
2. THE Multi-PDF-System SHALL eine visuelle Darstellung der Positionierungen erstellen (z.B. als Overlay-Bild)
3. THE Multi-PDF-System SHALL eine Zusammenfassung der Änderungen pro Seite und Firma dokumentieren
4. THE Multi-PDF-System SHALL Statistiken über Positionierungs-Variationen bereitstellen
5. THE Multi-PDF-System SHALL eine Benutzer-Dokumentation erstellen, die die Positionierungs-Logik erklärt

### Requirement 8: Backup und Wiederherstellung

**User Story:** Als Administrator möchte ich die Original-YML-Dateien sichern, damit ich bei Bedarf zur ursprünglichen Konfiguration zurückkehren kann.

#### Acceptance Criteria

1. BEFORE das System YML-Dateien überschreibt, THE Multi-PDF-System SHALL ein Backup aller Original-Dateien erstellen
2. THE Multi-PDF-System SHALL Backups mit Zeitstempel versehen und in einem separaten Verzeichnis speichern
3. THE Multi-PDF-System SHALL eine Wiederherstellungs-Funktion bereitstellen
4. THE Multi-PDF-System SHALL die Integrität der Backup-Dateien validieren
5. THE Multi-PDF-System SHALL eine Liste aller verfügbaren Backups anzeigen können
