# PROBLEM GEFUNDEN: Diagramme werden nicht übergeben

## Debug-Ausgabe zeigt das Problem

```
selected_charts_for_pdf_opt: []    <-- LEER!!!
inclusion_options keys: [..., 'selected_charts_for_pdf', ...]
```

**Das Problem:**

- Der Key `'selected_charts_for_pdf'` existiert in `inclusion_options`
- ABER der Wert ist leer: `[]`
- Das bedeutet: Die Charts werden in der UI ausgewählt, aber nicht korrekt gespeichert!

## Root Cause

In `pdf_ui.py` werden die Charts innerhalb des Formulars ausgewählt, aber die Werte werden nicht beim Submit in den Session State übernommen!

Das ist das gleiche Problem wie bei der `extended_output_enabled` Checkbox - die Werte müssen beim Submit explizit gespeichert werden.

## Lösung

Die Charts werden in `pdf_ui.py` in einer Liste gespeichert, die beim Submit übernommen werden muss.

Ich muss prüfen, wo die Charts gespeichert werden und sicherstellen, dass sie beim Submit korrekt übernommen werden.

---

**Status:** Problem identifiziert - Charts werden nicht übergeben  
**Nächster Schritt:** Chart-Auswahl-Logik in pdf_ui.py korrigieren
