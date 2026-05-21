# Requirements Document: 3D PV-Visualisierung - Kritische Bugfixes

## Introduction

Dieses Dokument definiert die Anforderungen für die Behebung kritischer Bugs im 3D-Visualisierungssystem. Das System hat derzeit vier Hauptprobleme, die die Funktionalität stark beeinträchtigen und behoben werden müssen.

## Glossary

- **System**: Das 3D-Visualisierungstool für PV-Planung
- **Benutzer**: Der Anwender der Streamlit-App
- **PV-Modul**: Photovoltaik-Solarmodul mit Standardmaßen (1.05m × 1.76m × 0.04m)
- **Grid-Positionierung**: Algorithmus zur Berechnung der Modul-Positionen auf der Dachfläche
- **Aufständerung**: Montagesystem für PV-Module mit Neigung
- **Mounting Height**: Höhe der Aufständerung über der Dachfläche
- **Optimierungs-Assistent**: Funktion zur automatischen Generierung optimaler Konfigurationen
- **PDF-Integration**: Einbettung von 3D-Screenshots in PDF-Angebote

## Requirements

### Requirement 1: Korrekte Modulanzahl-Platzierung

**User Story:** Als Benutzer möchte ich, dass das System EXAKT die gewünschte Anzahl von Modulen platziert, damit meine Planung korrekt ist.

#### Acceptance Criteria

1. WHEN der Benutzer 20 Module wählt UND genug Platz vorhanden ist, THE System SHALL exakt 20 Module platzieren
2. THE System SHALL die Grid-Positionierungs-Funktion so korrigieren dass sie die korrekte Anzahl Positionen zurückgibt
3. THE System SHALL Randabstände von 0.5m berücksichtigen
4. THE System SHALL Modul-Zwischenräume von 0.25m berücksichtigen
5. THE System SHALL die verfügbare Fläche korrekt berechnen: (Länge - 2×Rand) × (Breite - 2×Rand)
6. THE System SHALL die Anzahl Module pro Reihe berechnen: floor((verfügbare_Breite + Spacing) / (Modul_Breite + Spacing))
7. THE System SHALL die Anzahl Reihen berechnen: floor((verfügbare_Länge + Spacing) / (Modul_Höhe + Spacing))
8. THE System SHALL Module zentriert auf der Dachfläche positionieren
9. WHEN nicht genug Platz vorhanden ist, THE System SHALL so viele Module wie möglich platzieren UND eine Warnung anzeigen
10. THE System SHALL die tatsächlich platzierte Modulanzahl korrekt in der UI anzeigen

### Requirement 2: Sichtbare Modul-Aufständerung auf geneigten Dächern

**User Story:** Als Benutzer möchte ich, dass Module auf geneigten Dächern sichtbar aufgeständert sind, damit ich die Montage realistisch sehen kann.

#### Acceptance Criteria

1. WHEN die Dachform Satteldach ist, THE System SHALL Module mit sichtbarem Abstand zur Dachfläche platzieren
2. WHEN die Dachform Walmdach ist, THE System SHALL Module mit sichtbarem Abstand zur Dachfläche platzieren
3. WHEN die Dachform Pultdach ist, THE System SHALL Module mit sichtbarem Abstand zur Dachfläche platzieren
4. WHEN die Dachform Zeltdach ist, THE System SHALL Module mit sichtbarem Abstand zur Dachfläche platzieren
5. WHEN die Dachform Krüppelwalmdach ist, THE System SHALL Module mit sichtbarem Abstand zur Dachfläche platzieren
6. THE System SHALL eine Mounting-Height von mindestens 0.1m für geneigte Dächer verwenden
7. THE System SHALL die Mounting-Height basierend auf Dachneigung berechnen: min(0.3m, Dachneigung_deg / 90 × 0.5m)
8. THE System SHALL Module parallel zur Dachfläche ausrichten ABER mit Z-Offset für Sichtbarkeit
9. THE System SHALL sicherstellen dass Module NICHT in die Dachfläche einsinken
10. THE System SHALL optionale Montage-Gestelle visualisieren wenn show_mounting=True

### Requirement 3: Funktionsfähiger Optimierungs-Assistent

**User Story:** Als Benutzer möchte ich, dass der Optimierungs-Assistent funktioniert und mir optimale Konfigurationen vorschlägt, damit ich die beste Lösung finde.

#### Acceptance Criteria

1. WHEN der Benutzer "Optimierung starten" klickt, THE System SHALL verschiedene Konfigurationen generieren
2. THE System SHALL die Funktion optimize_layout() implementieren
3. THE System SHALL mindestens 4 verschiedene Strategien testen: Süd, Ost-West, Süd-Ost, Gemischt
4. THE System SHALL jede Konfiguration nach Kriterien bewerten: Modulanzahl, Verschattung, Ausrichtung
5. THE System SHALL einen Score von 0-100 für jede Konfiguration berechnen
6. THE System SHALL die Top 3 Konfigurationen sortiert nach Score zurückgeben
7. THE System SHALL für jede Konfiguration Details anzeigen: Aufständerung, Garage, Fassade, Score
8. WHEN der Benutzer "Übernehmen" klickt, THE System SHALL die gewählte Konfiguration aktivieren
9. THE System SHALL die UI-Werte entsprechend der übernommenen Konfiguration aktualisieren
10. THE System SHALL eine Erfolgsmeldung anzeigen nach Übernahme

### Requirement 4: Funktionierende PDF-Screenshot-Integration

**User Story:** Als Benutzer möchte ich, dass 3D-Screenshots automatisch in mein PDF-Angebot eingefügt werden, damit der Kunde eine visuelle Darstellung erhält.

#### Acceptance Criteria

1. WHEN der Benutzer "3D-Screenshot erstellen" klickt, THE System SHALL einen Screenshot generieren
2. THE System SHALL den Screenshot als PNG-Bytes speichern
3. THE System SHALL den Screenshot in st.session_state["pdf_3d_screenshot"] speichern
4. THE System SHALL die Funktion make_pv3d_image_flowable() korrekt implementieren
5. THE System SHALL den Screenshot aus Session State in PDF-Generator übergeben
6. WHEN der PDF-Generator aufgerufen wird, THE System SHALL prüfen ob ein Screenshot vorhanden ist
7. WHEN ein Screenshot vorhanden ist, THE System SHALL diesen auf Seite 6 im Platzhalter "3d_visuals" einfügen
8. THE System SHALL das Seitenverhältnis 16:10 für PDF-Bilder verwenden
9. THE System SHALL eine Bildbreite von 17cm im PDF verwenden
10. WHEN das Rendering fehlschlägt, THE System SHALL das PDF ohne Bild fortsetzen UND eine Warnung loggen

### Requirement 5: Robuste Fehlerbehandlung und Logging

**User Story:** Als Entwickler möchte ich detaillierte Logs und Fehlerbehandlung, damit ich Probleme schnell identifizieren und beheben kann.

#### Acceptance Criteria

1. THE System SHALL alle kritischen Funktionen mit try-except Blöcken absichern
2. THE System SHALL aussagekräftige Fehlermeldungen in der UI anzeigen
3. THE System SHALL detaillierte Fehler in die Konsole loggen mit Traceback
4. THE System SHALL bei Grid-Positionierung loggen: gewünschte Anzahl, berechnete Anzahl, Warnung bei Differenz
5. THE System SHALL bei Modul-Platzierung loggen: Dachform, Mounting-Height, Z-Position
6. THE System SHALL bei Optimierung loggen: generierte Konfigurationen, Scores, gewählte Konfiguration
7. THE System SHALL bei PDF-Integration loggen: Screenshot-Größe, Erfolg/Fehler, Einfügeposition
8. THE System SHALL Warnungen anzeigen wenn Funktionen nicht verfügbar sind
9. THE System SHALL Fallback-Werte verwenden wenn Daten fehlen
10. THE System SHALL die App-Funktionalität bei Fehlern nicht blockieren

### Requirement 6: Verbesserte Benutzer-Feedback

**User Story:** Als Benutzer möchte ich klares Feedback über den Status meiner Aktionen, damit ich weiß was passiert.

#### Acceptance Criteria

1. THE System SHALL eine Erfolgsmeldung anzeigen nach erfolgreicher Modul-Platzierung
2. THE System SHALL eine Warnung anzeigen wenn nicht alle Module passen
3. THE System SHALL die Anzahl platzierter Module vs. gewünschte Module anzeigen
4. THE System SHALL einen Fortschrittsbalken anzeigen während Optimierung läuft
5. THE System SHALL eine Erfolgsmeldung anzeigen nach erfolgreicher Optimierung
6. THE System SHALL eine Erfolgsmeldung anzeigen nach Screenshot-Erstellung
7. THE System SHALL eine Info-Meldung anzeigen über PDF-Integration
8. THE System SHALL Tooltips für alle wichtigen Eingabefelder bereitstellen
9. THE System SHALL visuelle Indikatoren für ausgewählte Module zeigen
10. THE System SHALL Echtzeit-Updates der 3D-Visualisierung ermöglichen
