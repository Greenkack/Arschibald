# PDF Services Selection - Requirements Document

## Introduction

Diese Spezifikation definiert die Anforderungen für eine dynamische Dienstleistungsauswahl in der PDF-Generierung. Das System soll es Benutzern ermöglichen, Standard- und optionale Dienstleistungen für die PDF-Ausgabe zu konfigurieren, wobei Standard-Services automatisch aktiviert sind und optionale Services manuell ausgewählt werden können.

## Requirements

### Requirement 1: Service Classification System

**User Story:** Als Benutzer möchte ich zwischen Standard- und optionalen Dienstleistungen unterscheiden können, damit ich weiß, welche Services automatisch in der PDF enthalten sind.

#### Acceptance Criteria

1. WHEN das System Dienstleistungen lädt THEN sollen Standard-Services (is_standard=True) mit ⭐ Symbol gekennzeichnet werden
2. WHEN das System Dienstleistungen lädt THEN sollen optionale Services (is_standard=False) mit 🔧 Symbol gekennzeichnet werden
3. WHEN ein Service als Standard markiert ist THEN soll er automatisch für PDF-Generierung aktiviert sein
4. WHEN ein Service als optional markiert ist THEN soll er standardmäßig deaktiviert sein

### Requirement 2: Dynamic Service Selection UI

**User Story:** Als Benutzer möchte ich eine übersichtliche Benutzeroberfläche haben, um Services für die PDF-Generierung auszuwählen, damit ich flexibel bestimmen kann, welche Leistungen im Angebot erscheinen.

#### Acceptance Criteria

1. WHEN die PDF-UI geladen wird THEN soll ein "Dienstleistungen" Bereich angezeigt werden
2. WHEN Standard-Services angezeigt werden THEN sollen sie bereits angekreuzt sein
3. WHEN optionale Services angezeigt werden THEN sollen sie nicht angekreuzt sein
4. WHEN ich eine Checkbox ankreuze THEN soll der Service für PDF-Generierung aktiviert werden
5. WHEN ich eine Checkbox abwähle THEN soll der Service aus der PDF-Generierung entfernt werden
6. WHEN Services angezeigt werden THEN sollen sie nach pdf_order sortiert sein

### Requirement 3: Service Information Display

**User Story:** Als Benutzer möchte ich detaillierte Informationen zu jedem Service sehen, damit ich fundierte Entscheidungen über die Auswahl treffen kann.

#### Acceptance Criteria

1. WHEN ein Service angezeigt wird THEN sollen Name, Kategorie, Preis und Berechnungseinheit sichtbar sein
2. WHEN ein Service eine Beschreibung hat THEN soll diese als Tooltip oder Zusatztext angezeigt werden
3. WHEN Services gruppiert werden THEN sollen sie nach Kategorien organisiert sein
4. WHEN der Preis 0.00 € beträgt THEN soll "Kostenlos" oder "Inklusive" angezeigt werden

### Requirement 4: PDF Integration

**User Story:** Als Benutzer möchte ich, dass ausgewählte Services automatisch in die generierte PDF übernommen werden, damit das Angebot alle gewünschten Leistungen enthält.

#### Acceptance Criteria

1. WHEN eine PDF generiert wird THEN sollen nur aktivierte Services einbezogen werden
2. WHEN Services in der PDF erscheinen THEN sollen sie nach pdf_order sortiert sein
3. WHEN ein Service Kosten verursacht THEN sollen diese in der Preisberechnung berücksichtigt werden
4. WHEN ein Service kostenlos ist THEN soll er trotzdem in der Leistungsübersicht erscheinen
5. WHEN Services berechnet werden THEN soll die korrekte Berechnungseinheit (kWp, Pauschal, etc.) verwendet werden

### Requirement 5: Session State Management

**User Story:** Als Benutzer möchte ich, dass meine Service-Auswahl während der Session gespeichert wird, damit ich nicht bei jeder Änderung neu auswählen muss.

#### Acceptance Criteria

1. WHEN ich Services auswähle THEN sollen diese in der Session gespeichert werden
2. WHEN ich zwischen verschiedenen Bereichen der Anwendung wechsle THEN soll meine Auswahl erhalten bleiben
3. WHEN ich die Anwendung neu lade THEN sollen Standard-Services wieder aktiviert sein
4. WHEN ich eine neue Berechnung starte THEN sollen die zuletzt gewählten Services als Basis dienen

### Requirement 6: Real-time Price Updates

**User Story:** Als Benutzer möchte ich sofort sehen, wie sich die Auswahl von Services auf den Gesamtpreis auswirkt, damit ich die Kostenauswirkungen verstehe.

#### Acceptance Criteria

1. WHEN ich einen Service aktiviere THEN soll sich der Gesamtpreis sofort aktualisieren
2. WHEN ich einen Service deaktiviere THEN soll sich der Gesamtpreis sofort reduzieren
3. WHEN Services mit kWp-Berechnung aktiviert werden THEN soll die Anlagengröße berücksichtigt werden
4. WHEN Pauschal-Services aktiviert werden THEN soll der Festpreis addiert werden
5. WHEN die Preisberechnung aktualisiert wird THEN sollen alle abhängigen UI-Elemente aktualisiert werden

### Requirement 7: Error Handling and Validation

**User Story:** Als Benutzer möchte ich klare Fehlermeldungen erhalten, wenn Probleme bei der Service-Auswahl auftreten, damit ich weiß, wie ich diese beheben kann.

#### Acceptance Criteria

1. WHEN Services nicht geladen werden können THEN soll eine aussagekräftige Fehlermeldung angezeigt werden
2. WHEN die Datenbankverbindung fehlschlägt THEN soll ein Fallback-Modus aktiviert werden
3. WHEN ungültige Service-Daten vorliegen THEN sollen diese übersprungen und protokolliert werden
4. WHEN die PDF-Generierung fehlschlägt THEN soll der Benutzer über das Problem informiert werden
5. WHEN Services fehlerhafte Preise haben THEN sollen Standardwerte verwendet werden

### Requirement 8: Performance Optimization

**User Story:** Als Benutzer möchte ich, dass die Service-Auswahl schnell und responsiv funktioniert, auch bei vielen verfügbaren Services.

#### Acceptance Criteria

1. WHEN die Service-Liste geladen wird THEN soll dies in unter 2 Sekunden erfolgen
2. WHEN ich Services auswähle THEN soll die UI sofort reagieren
3. WHEN viele Services vorhanden sind THEN soll die Liste paginiert oder gefiltert werden können
4. WHEN die Preisberechnung erfolgt THEN soll diese optimiert und gecacht werden
5. WHEN die PDF generiert wird THEN sollen nur die notwendigen Service-Daten übertragen werden
