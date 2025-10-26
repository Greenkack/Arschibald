# Requirements Document

## Introduction

Das erweiterte PDF-Ausgabesystem generiert derzeit nicht alle Dokumente, Datenblätter, individuelle Seiten und Diagramme korrekt. Es werden zwar mehr als 8 Seiten erzeugt, aber wichtige Inhalte fehlen. Die funktionierenden Codes aus dem `repair_pdf` Ordner müssen extrahiert und in die aktuelle Implementierung integriert werden, um sicherzustellen, dass alle Produktdatenblätter (einschließlich Zubehörkomponenten), Firmendokumente und Diagramme vollständig in die PDF eingebaut werden.

## Requirements

### Requirement 1: Vollständige Produktdatenblätter einbinden

**User Story:** Als Benutzer möchte ich, dass alle Produktdatenblätter (Hauptkomponenten UND Zubehör) in die erweiterte PDF-Ausgabe eingebunden werden, damit ich vollständige technische Informationen zu allen ausgewählten Produkten erhalte.

#### Acceptance Criteria

1. WHEN die erweiterte PDF generiert wird THEN SHALL das System Datenblätter für alle Hauptkomponenten (Modul, Wechselrichter, Speicher) einbinden
2. WHEN Zubehörkomponenten ausgewählt sind (Wallbox, EMS, Optimizer, Carport, Notstrom, Tierabwehr) THEN SHALL das System deren Datenblätter ebenfalls einbinden
3. WHEN `include_additional_components` aktiviert ist THEN SHALL das System alle Zubehör-IDs aus den entsprechenden Feldern extrahieren
4. WHEN ein Produkt-ID mehrfach vorkommt THEN SHALL das System Duplikate entfernen
5. WHEN ein Datenblatt-Pfad in der Datenbank vorhanden ist THEN SHALL das System den vollständigen Pfad korrekt konstruieren und die Datei anhängen

### Requirement 2: Firmendokumente korrekt einbinden

**User Story:** Als Benutzer möchte ich, dass alle ausgewählten Firmendokumente in die PDF eingebunden werden, damit ich vollständige Unternehmensinformationen im Angebot habe.

#### Acceptance Criteria

1. WHEN Firmendokument-IDs in `company_document_ids_to_include` angegeben sind THEN SHALL das System diese Dokumente aus der Datenbank laden
2. WHEN ein Firmendokument einen relativen Pfad hat THEN SHALL das System den vollständigen Pfad mit `COMPANY_DOCS_BASE_DIR_PDF_GEN` konstruieren
3. WHEN ein Dokument existiert THEN SHALL das System es an die PDF anhängen
4. WHEN ein Dokument nicht gefunden wird THEN SHALL das System dies im Debug-Log vermerken aber die Generierung fortsetzen

### Requirement 3: Diagramme und individuelle Seiten einbinden

**User Story:** Als Benutzer möchte ich, dass alle ausgewählten Diagramme und individuellen Seiten in die PDF eingebunden werden, damit ich visuelle Analysen im Angebot habe.

#### Acceptance Criteria

1. WHEN Diagramme in `selected_charts_for_pdf` ausgewählt sind THEN SHALL das System diese Diagramme generieren
2. WHEN das Chart-Layout angegeben ist THEN SHALL das System dieses Layout verwenden
3. WHEN Diagramm-Seiten generiert wurden THEN SHALL das System diese nach den Datenblättern und Dokumenten anhängen
4. WHEN die Diagramm-Generierung fehlschlägt THEN SHALL das System einen Fehler loggen aber die PDF-Generierung fortsetzen

### Requirement 4: Robuste Fehlerbehandlung

**User Story:** Als Benutzer möchte ich, dass die PDF-Generierung auch bei fehlenden Dateien oder Fehlern fortgesetzt wird, damit ich zumindest eine teilweise PDF erhalte.

#### Acceptance Criteria

1. WHEN ein Datenblatt nicht gefunden wird THEN SHALL das System dies loggen und mit den nächsten Dateien fortfahren
2. WHEN ein Firmendokument nicht gefunden wird THEN SHALL das System dies loggen und mit den nächsten Dateien fortfahren
3. WHEN die Diagramm-Generierung fehlschlägt THEN SHALL das System dies loggen und die PDF ohne Diagramme zurückgeben
4. WHEN das Anhängen einer Datei fehlschlägt THEN SHALL das System dies loggen und mit den nächsten Dateien fortfahren
5. WHEN alle Anhänge fehlschlagen THEN SHALL das System die Haupt-PDF ohne Anhänge zurückgeben

### Requirement 5: Debug-Informationen bereitstellen

**User Story:** Als Entwickler möchte ich detaillierte Debug-Informationen über den PDF-Generierungsprozess, damit ich Probleme schnell identifizieren und beheben kann.

#### Acceptance Criteria

1. WHEN Datenblätter gesucht werden THEN SHALL das System gefundene und fehlende Datenblätter loggen
2. WHEN Firmendokumente gesucht werden THEN SHALL das System gefundene und fehlende Dokumente loggen
3. WHEN Dateien angehängt werden THEN SHALL das System die Anzahl der erfolgreich angehängten Dateien loggen
4. WHEN Diagramme generiert werden THEN SHALL das System die Größe der generierten Diagramm-PDF loggen
5. WHEN Fehler auftreten THEN SHALL das System aussagekräftige Fehlermeldungen mit Kontext loggen
