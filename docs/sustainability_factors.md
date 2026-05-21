# Nachhaltigkeitskennzahlen – Emissionsfaktoren und Berechnungslogik

Dieses Dokument fasst die in `pdf_template_engine/placeholders.py` verwendeten Annahmen für die Berechnung der Nachhaltigkeitskennzahlen zusammen. Die Faktoren lassen sich über `analysis_results` überschreiben; ohne Angabe greifen die folgenden Standardwerte.

## Emissionsfaktoren

| Kenngröße | Symbol | Standardwert | Quelle / Begründung |
|-----------|--------|--------------|---------------------|
| Strommix (Bezug aus dem öffentlichen Netz) | $EF_{\text{grid}}$ | 0,363 kg CO$_2$/kWh | Umweltbundesamt 2023 – deutscher Strommix |
| Stromeinspeisung (verdrängter Mix) | $EF_{\text{export}}$ | 0,363 kg CO$_2$/kWh | identisch zum Strommix, solange kein spezieller Grünstromvertrag vorliegt |
| Photovoltaik Lebenszyklus | $EF_{\text{pv}}$ | 0,0358 kg CO$_2$/kWh | Meta-Analyse Fraunhofer ISE 2022 |
| Äquivalente Fahrleistung Pkw | $F_{\text{car}}$ | 0,142 kg CO$_2$/km | Durchschnittlicher deutscher Pkw-Flottenwert |
| Baumäquivalent | $F_{\text{tree}}$ | 21,8 kg CO$_2$/Baum·Jahr | Durchschnittliche jährliche CO$_2$-Bindung einer heimischen Buche |

## Berechnungsformel

Die jährliche Einsparung von Treibhausgasen wird als Differenz zwischen dem konventionellen Strommix und der PV-Erzeugung berechnet:

$$
\text{CO}_2^{\text{saved}} = (E_{\text{self}} \cdot EF_{\text{grid}}) + (E_{\text{export}} \cdot EF_{\text{export}}) - (E_{\text{prod}} \cdot EF_{\text{pv}})
$$

* $E_{\text{prod}}$ – Jahresproduktion der PV-Anlage (kWh)
* $E_{\text{self}}$ – direkter Eigenverbrauch (kWh)
* $E_{\text{export}}$ – Netzeinspeisung (kWh). Fehlt der Wert, wird aus Analyse- oder Projekt-Daten die bestmögliche Alternative gezogen.

Zusatzkennzahlen:

* **Prozentuale Reduktion**: Vergleich mit einem Haushalts-Baseline-Wert (Standard 6.904 kg CO$_2$/a, konfigurierbar über `analysis_results` oder Projektdaten).
* **Äquivalente Pkw-Kilometer**: $\text{CO}_2^{\text{saved}} / F_{\text{car}}$.
* **Baumäquivalent**: $\text{CO}_2^{\text{saved}} / F_{\text{tree}}$.

## Datenquellen und Fallbacks

1. **Primärquelle**: `analysis_results` enthält in der Regel die Simulationsergebnisse (`annual_pv_production_kwh`, `direct_self_consumption_kwh`, `grid_feed_in_kwh`).
2. **Sekundärquelle**: `project_details` oder `project_data` liefern Werte für ältere Projekte.
3. **Fallback**: Wenn keine Einspeisung hinterlegt ist, wird angenommen, dass Produktion = Eigenverbrauch (konservativ, führt zu Null-Einsparung aus Export).

Alle Zwischenergebnisse werden über Debug-Logs ausgegeben (`DEBUG SEITE5 SUSTAINABILITY`), um Unstimmigkeiten schnell sichtbar zu machen.
