# pv_visuals.py — Logik-Extraktion

Kurzüberblick: Plotly-basierte 3D-Visualisierungen für PV-Analysen mit Export als PNG-Bytes für den PDF-Einsatz. Nutzt Streamlit zur Anzeige und schreibt die erzeugten Bild-Bytes in analysis_results.

## Öffentliche Funktionen und Verträge

- get_text_pv_viz(texts, key, fallback_text?) -> str
  - Robust gegen fehlende Keys; generiert Fallback-Titel aus dem Key.

- render_yearly_production_pv_data(analysis_results, texts)
  - Input (analysis_results): monthly_productions_sim: List[12] (Floats/ints)
  - Output side-effects: analysis_results['yearly_production_chart_bytes'] = PNG-Bytes der Figur
  - Verhalten: Validiert Länge/Daten; zeigt Fallback-Figur bei Fehlern.

- render_break_even_pv_data(analysis_results, texts)
  - Input: simulation_period_years_effective: int; cumulative_cash_flows_sim: List[N+1]
  - Output: analysis_results['break_even_chart_bytes'] = PNG-Bytes
  - Verhalten: Validiert Daten (Längencheck, NaN/Inf-Filter), Fallback bei Fehlern.

- render_amortisation_pv_data(analysis_results, texts)
  - Input: simulation_period_years_effective: int; total_investment_netto: float; annual_benefits_sim: List[N]
  - Output: analysis_results['amortisation_chart_bytes'] = PNG-Bytes
  - Verhalten: Berechnet kumulierte Rückflüsse; zeigt Kosten- vs. Rückflusslinie in 3D; Fallback bei fehlenden Daten.

- render_co2_savings_visualization(analysis_results, texts)
  - Input: annual_co2_savings_kg, co2_equivalent_trees_per_year, co2_equivalent_car_km_per_year
  - Output: analysis_results['co2_savings_chart_bytes'] = PNG-Bytes
  - Verhalten: 3D-Szene mit stilisierten Symbolen (Bäume/Auto/Flugzeug) und zentraler Kennzahl; zusätzliche Metrics in UI.

- _export_plotly_fig_to_bytes_pv_viz(fig, texts) -> Optional[bytes]
  - Hilfsfunktion: to_image(format='png', scale=2, width=900, height=550); Fehler werden geschluckt (None).

## Wichtige Implementierungsdetails

- Sämtliche Werte werden defensiv in float gecastet und gegen NaN/Inf geprüft.
- Plotly 3D: Scatter3d für Linien/Marker, Achsenbeschriftungen via texts.
- UI-Schlüssel (key=...) sind eindeutig, um Streamlit-Cache-Konflikte zu vermeiden.
- Fallback-Figuren: Minimale Figure mit „Daten nicht verfügbar“ zur UI-Kohärenz und PDF-Exportrobustheit.

## Einbindung in PDF-Pipeline

- Die PNG-Bytes (…_chart_bytes) werden in pdf_generator.py als Bilder eingebettet.
- Falls to_image fehlschlägt (kaleido nicht installiert), bleibt der Wert None; pdf_generator sollte robusten Fallback haben (z. B. Platzhalterbild oder Abschnitt überspringen).

## Edge Cases

- Fehlende oder fehlerhafte analysis_results Keys -> Warnungen in UI, Fallback-Chart, None-Bytes möglich.
- Sehr große Werte: Achsenskalierung/Lesbarkeit beachten.
- Internationalisierung: get_text_pv_viz stellt sensible Default-Beschriftungen bereit.

## Migration zu Electron + PrimeReact + TypeScript

- Plotly.js im Renderer; Export als PNG
  - Option A: node-kaleido (Plotly) -> await Plotly.toImage(fig, {format, scale, width, height}).
  - Option B: Puppeteer/Screenshot.
- State-Flow: analysis_results aus dem Backend (Python) via IPC oder vollständig in TS berechnen.
- 3D-Visuals: Alternativ three.js für kundenspezifische 3D-Szenen, dann Canvas-Screenshot für PDF.

## Tests

- Unit: _export_plotly_fig_to_bytes_pv_viz gibt Bytes zurück für einfache Figur; None bei künstlichem Fehler (z. B. fig=None).
- Contract: `render_*` Funktionen schreiben jeweilige `*_chart_bytes` Keys und reagieren korrekt auf ungültige Inputs.
