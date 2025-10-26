# Requirements Document

## Introduction

Die Preismatrix-Funktion im Solar Calculator zeigt derzeit falsche Preise an und erkennt Batteriespeicher-Modelle nicht korrekt. Die Matrix soll wie eine Excel INDEX/MATCH Funktion arbeiten, wobei die Anzahl der PV-Module die Zeile und das gewählte Batteriespeicher-Modell die Spalte bestimmt. Der Schnittpunkt dieser beiden Werte ergibt den schlüsselfertigen Pauschalpreis der PV-Anlage inklusive Installation, Montage und Genehmigungen.

## Requirements

### Requirement 1

**User Story:** Als Benutzer des Solar Calculators möchte ich, dass die Preismatrix den korrekten schlüsselfertigen Preis basierend auf der gewählten Modulanzahl und dem Batteriespeicher-Modell anzeigt, damit ich eine genaue Kostenberechnung erhalte.

#### Acceptance Criteria

1. WHEN ich eine Anzahl von PV-Modulen im Solar Calculator wähle THEN soll das System die entsprechende Zeile in der Preismatrix identifizieren
2. WHEN ich ein Batteriespeicher-Modell auswähle THEN soll das System die entsprechende Spalte in der Preismatrix identifizieren
3. WHEN ich "kein Speicher" wähle THEN soll das System die Spalte "ohne Speicher" verwenden
4. WHEN beide Werte (Modulanzahl und Speicher) gewählt sind THEN soll das System den Preis am Schnittpunkt von Zeile und Spalte zurückgeben
5. IF die Preismatrix-Datei (price_matrix.xlsx oder price_matrix.csv) im data-Ordner vorhanden ist THEN soll das System diese korrekt laden und verwenden

### Requirement 2

**User Story:** Als Administrator möchte ich Preismatrix-Dateien (XLSX oder CSV) hochladen können, damit die aktuellen Preise im System verfügbar sind.

#### Acceptance Criteria

1. WHEN ich eine price_matrix.xlsx oder price_matrix.csv Datei im Admin-Bereich hochlade THEN soll diese im data-Ordner gespeichert werden
2. WHEN die Datei hochgeladen wird THEN soll das System die Struktur validieren (erste Spalte = Modulanzahl, weitere Spalten = Speicher-Modelle, letzte Spalte = "ohne Speicher")
3. IF eine neue Preismatrix hochgeladen wird THEN soll die vorherige Version überschrieben werden
4. WHEN die Datei erfolgreich hochgeladen wurde THEN soll eine Bestätigung angezeigt werden

### Requirement 3

**User Story:** Als Entwickler möchte ich, dass alle Preismatrix-Referenzen im Code konsolidiert sind, damit keine widersprüchlichen oder veralteten Implementierungen existieren.

#### Acceptance Criteria

1. WHEN das System nach Preismatrix-Logik sucht THEN soll nur eine zentrale Implementierung verwendet werden
2. IF mehrere Preismatrix-Implementierungen gefunden werden THEN sollen diese entfernt oder konsolidiert werden
3. WHEN die Preismatrix geladen wird THEN soll das System sowohl XLSX als auch CSV Formate unterstützen
4. IF die Preismatrix-Datei nicht gefunden wird THEN soll eine aussagekräftige Fehlermeldung angezeigt werden

### Requirement 4

**User Story:** Als Benutzer möchte ich, dass die Preisberechnung nach der INDEX/MATCH Logik funktioniert (wie in Excel), damit die Preise konsistent und korrekt sind.

#### Acceptance Criteria

1. WHEN die Modulanzahl gewählt wird THEN soll das System einen MATCH auf die erste Spalte der geladenen Preismatrix durchführen
2. WHEN das Speicher-Modell gewählt wird THEN soll das System einen MATCH auf die erste Zeile der geladenen Preismatrix durchführen
3. WHEN beide Indizes gefunden sind THEN soll das System den INDEX-Wert am Schnittpunkt zurückgeben
4. IF ein Wert nicht in der Matrix gefunden wird THEN soll eine Fehlermeldung angezeigt werden
5. WHEN "kein Speicher" gewählt ist THEN soll automatisch die letzte Spalte ("ohne Speicher") verwendet werden

### Requirement 5

**User Story:** Als Benutzer möchte ich, dass zusätzliche Kosten für Zubehör und Rabatte korrekt zum Basis-Matrixpreis hinzugefügt oder abgezogen werden, damit der Endpreis alle gewählten Optionen widerspiegelt.

#### Acceptance Criteria

1. WHEN ich Zubehör im Solar Calculator auswähle THEN sollen diese Kosten zum Matrixpreis hinzugefügt werden
2. WHEN ich Rabatte anwende THEN sollen diese vom Matrixpreis abgezogen werden
3. WHEN der Endpreis berechnet wird THEN soll die Formel sein: Matrixpreis + Zubehörkosten - Rabatte
4. IF keine zusätzlichen Kosten oder Rabatte gewählt sind THEN soll nur der Matrixpreis angezeigt werden
5. WHEN sich die Auswahl ändert THEN soll der Preis in Echtzeit aktualisiert werden
