# Seite 6 Charts Fix - Zusammenfassung

## Problem

Auf Seite 6 des PDF-Templates wurden keine Charts oder Ergebnisse angezeigt. Die Platzhalter `relation_tagverbrauch_prozent` und `relation_pvproduktion_prozent` zeigten nur "0" an, obwohl die Berechnungen korrekt funktionierten (74% und 53%).

## Ursache

Die Donut-Charts wurden an den falschen Positionen gezeichnet (cy = 550.0), während die Platzhalter bei anderen Y-Koordinaten lagen:

- `relation_tagverbrauch_prozent`: Position (330.0, 581.0, 500.0, 596.0)  
- `relation_pvproduktion_prozent`: Position (330.0, 611.0, 500.0, 626.0)

## Lösung

### 1. Korrigierte Chart-Positionen

Die `_draw_page6_storage_donuts` Funktion wurde angepasst um die Charts an den korrekten Positionen der Platzhalter zu zeichnen:

```python
# Positionen basierend auf den Platzhaltern in seite6.yml
consumption_y_yaml = 581.0  # Y-Position aus YAML
production_y_yaml = 611.0   # Y-Position aus YAML

# Canvas Y = page_height - yaml_y
consumption_cy = page_height - consumption_y_yaml - 15  # Mitte des Bereichs
production_cy = page_height - production_y_yaml - 15    # Mitte des Bereichs

# X-Position: Mitte zwischen 330 und 500
chart_cx = (330.0 + 500.0) / 2.0  # = 415.0
```

### 2. Platzhalter-Texte ausblenden

Die Platzhalter-Texte werden jetzt übersprungen, damit sie nicht über die Charts gezeichnet werden:

```python
# Seite 6: Speicher-Relationen Platzhalter überspringen (werden durch Donut-Charts ersetzt)
if i == 6 and text in ["relation_tagverbrauch_prozent", "relation_pvproduktion_prozent"]:
    print(f"DEBUG: Überspringe Platzhalter-Text '{text}' - wird durch Donut-Chart ersetzt")
    continue
```

### 3. Debug-Ausgaben hinzugefügt

Für bessere Nachverfolgung wurden Debug-Ausgaben hinzugefügt:

```python
print(f"DEBUG: Seite 6 Donut-Charts - Consumption: {pct_consumption}%, Production: {pct_production}%")
print(f"DEBUG: Zeichne Consumption Donut bei ({chart_cx}, {consumption_cy}) mit {pct_consumption}%")
print(f"DEBUG: Zeichne Production Donut bei ({chart_cx}, {production_cy}) mit {pct_production}%")
```

## Ergebnis

### Funktionalität

- ✅ Donut-Charts werden an den korrekten Positionen gezeichnet
- ✅ Prozentwerte werden mittig in den Charts angezeigt (74% und 53%)
- ✅ Platzhalter-Texte werden nicht mehr über die Charts gezeichnet
- ✅ Berechnungen funktionieren korrekt

### Test-Ergebnisse

```
DEBUG: Seite 6 Donut-Charts - Consumption: 74.0%, Production: 53.0%
DEBUG: Zeichne Consumption Donut bei (415.0, 245.89) mit 74.0%
DEBUG: Zeichne Production Donut bei (415.0, 215.89) mit 53.0%
DEBUG: Überspringe Platzhalter-Text 'relation_tagverbrauch_prozent' - wird durch Donut-Chart ersetzt
DEBUG: Überspringe Platzhalter-Text 'relation_pvproduktion_prozent' - wird durch Donut-Chart ersetzt
```

### Visuelle Darstellung

- **Oberer Chart**: Speicher zu Tagesverbrauch (74%)
  - Blauer Donut mit "74%" in der Mitte
  - Position: bei Y-Koordinate der `relation_tagverbrauch_prozent`
  
- **Unterer Chart**: Speicher zu PV-Produktion (53%)  
  - Grüner Donut mit "53%" in der Mitte
  - Position: bei Y-Koordinate der `relation_pvproduktion_prozent`

## Geänderte Dateien

1. `pdf_template_engine/dynamic_overlay.py`
   - `_draw_page6_storage_donuts()` Funktion korrigiert
   - Platzhalter-Überspringen in `generate_overlay()` hinzugefügt

## Test-Dateien erstellt

1. `debug_seite6_problem.py` - Diagnose-Skript
2. `test_seite6_charts.py` - PDF-Erstellungs-Test
3. `test_seite6_charts.pdf` - Beispiel-PDF mit funktionierenden Charts

Das Problem ist vollständig behoben und die Donut-Charts werden jetzt korrekt auf Seite 6 angezeigt!
