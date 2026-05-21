# Wasserfall-Diagramm Implementation - Seite 3 PDF

## Übersicht

Das Wasserfall-Diagramm wurde erfolgreich auf Seite 3 der PDF implementiert und zeigt die drei Berechnungsergebnisse:

- **Einsparung durch Direktverbrauch**
- **Einnahmen aus Einspeisevergütung**
- **Vorteile durch steuerfreie Einspeisung**
- **Gesamt Erträge pro Jahr** (als separater Gesamtbalken)

## Positionierung

Das Diagramm wurde exakt nach den angegebenen Koordinaten positioniert:

### Grenzen

- **Linker Rand**: Position der "Neigung des Daches" Spalte (X=300.48)
- **Rechter Rand**: Position des letzten Buchstabens von "Art" (X=547.50)
- **Obere Grenze**: 10 Punkte oberhalb vom "Direkt" Platzhalter (Y=506.11)
- **Untere Grenze**: 10 Punkte oberhalb von "Berechnungsgrundlagen" (Y=635.42)

### Dimensionen

- **Breite**: 247.0 Punkte
- **Höhe**: 129.3 Punkte
- **Vollständige Ausnutzung** des verfügbaren Platzes

## Design-Eigenschaften

### Farben

- **Verschiedene Blau-Töne** wie in der PDF verwendet:
  - Direktverbrauch: Dunkelblau (RGB: 0.07, 0.34, 0.60)
  - Einspeisevergütung: Mittelblau (RGB: 0.12, 0.42, 0.68)
  - Steuervorteile: Hellblau (RGB: 0.18, 0.50, 0.76)
  - Gesamt: Sehr dunkelblau (RGB: 0.05, 0.28, 0.52)

### Layout

- **3 Einzelbalken** für die Komponenten (70% der Breite)
- **1 Gesamtbalken** rechts (25% der Breite)
- **Wasserfall-Effekt** mit Verbindungslinien zwischen den Balken
- **Gestrichelte Linien** für Verbindungen (falls ReportLab-Version unterstützt)

### Beschriftung

- **Werte über den Balken** in Euro-Format (z.B. "1.450 €")
- **Labels unter den Balken** (mehrzeilig für bessere Lesbarkeit)
- **Schriftarten**: Helvetica-Bold für Werte, Helvetica für Labels

## Datenquellen

Das Diagramm unterstützt verschiedene Datenquellen-Keys für maximale Kompatibilität:

### Direktverbrauch

- `einsparung_direktverbrauch_eur`
- `self_consumption_without_battery_eur`
- `direct_consumption_savings_eur`

### Einspeisevergütung

- `einnahmen_einspeisung_eur`
- `annual_feed_in_revenue_eur`
- `feed_in_revenue_eur`

### Steuervorteile

- `vorteile_steuerfrei_eur`
- `tax_benefits_eur`
- `steuerliche_vorteile_eur`

### Gesamt

- `gesamt_ertraege_jahr_eur`
- `total_annual_savings_eur`
- `annual_total_benefits_eur`

## Fallback-Verhalten

- **Automatische Berechnung** des Gesamtwerts falls nicht direkt verfügbar
- **Demo-Werte** werden verwendet wenn keine Daten vorhanden sind:
  - Direktverbrauch: 1.200 €
  - Einspeisevergütung: 800 €
  - Steuervorteile: 300 €
  - Gesamt: 2.300 €

## Implementation Details

### Datei: `pdf_template_engine/dynamic_overlay.py`

- **Funktion**: `_draw_page3_waterfall_chart()`
- **Integration**: Automatisch auf Seite 3 gezeichnet
- **Koordinaten**: Basierend auf `coords/seite3.yml`

### Robustheit

- **Fehlerbehandlung** für fehlende Daten
- **ReportLab-Kompatibilität** für verschiedene Versionen
- **Skalierung** basierend auf Maximalwert
- **Mehrzeilige Labels** für bessere Darstellung

## Test-Ergebnisse

### Erfolgreich getestet mit

1. **Verschiedene Wertebereiche** (niedrig, mittel, hoch)
2. **Fehlende Daten** (Fallback-Verhalten)
3. **Template-Integration** (mit PDF-Hintergrund)
4. **Overlay-Generierung** (ohne Template)

### Generierte Test-Dateien

- `test_wasserfall_improved.pdf` - Verschiedene Szenarien mit Koordinaten-Raster
- `test_wasserfall_overlay.pdf` - Nur Overlay-Diagramm
- `test_wasserfall_with_template.pdf` - Mit Template-Hintergrund

## Debug-Ausgaben

Das System gibt detaillierte Debug-Informationen aus:

```
DEBUG: Wasserfall-Werte - Direkt: 1450.75€, Einspeisung: 920.5€, Steuer: 380.25€, Gesamt: 2751.5€
DEBUG: Wasserfall-Chart EXAKTE Position - Links: 300.48, Rechts: 547.5, Oben: 335.78, Unten: 206.47
DEBUG: Chart-Dimensionen - Breite: 247.0, Höhe: 129.3
DEBUG: Balken 1 (Einsparung durch Direktverbrauch): X=309.1, Y=206.5, Breite=40.3, Höhe=51.1, Wert=1450.75€
```

## Verwendung

Das Wasserfall-Diagramm wird automatisch auf Seite 3 jeder generierten PDF angezeigt, wenn entsprechende Berechnungsdaten verfügbar sind. Die Implementierung ist vollständig in das bestehende PDF-Generierungssystem integriert.

## Status: ✅ VOLLSTÄNDIG IMPLEMENTIERT

Das Wasserfall-Diagramm entspricht exakt den Anforderungen:

- ✅ Korrekte Positionierung zwischen den angegebenen Koordinaten
- ✅ Vollständige Ausnutzung des verfügbaren Platzes
- ✅ Blau-Töne wie in der PDF verwendet
- ✅ Darstellung aller drei Berechnungsergebnisse plus Gesamtwert
- ✅ Wasserfall-Effekt mit Verbindungslinien
- ✅ Robuste Datenverarbeitung und Fallback-Verhalten
