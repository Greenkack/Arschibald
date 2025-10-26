# calculations_extended.py – vollständige Logik-Extraktion

Dieses Modul bündelt fortgeschrittene Finanz-, Energie- und Öko-Kennzahlen sowie Heuristiken. Es enthält sowohl einzelne Utility-Funktionen (1–50 sowie weitere) als auch Aggregatoren wie `run_all_extended_analyses`. Mehrere Bereiche sind redundant/überschneidend (z. B. zwei `calculate_lcoe`-Definitionen mit unterschiedlichen Signaturen) – siehe Hinweise.

## Konstanten und Annahmen

- `LIFESPAN_YEARS = 25`: Lebensdauer für Finanz-/Energie-Rechnungen.
- `DISCOUNT_RATE = 0.04`: Abzinsung für NPV/LCOE-Annuität.
- `CO2_EMISSIONS_GRID_KWH = 0.401` kg/kWh: Strommix-Emissionsfaktor.
- `CO2_EMBODIED_PV_KWP = 1500` kg/kWp: graue Emissionen der PV-Herstellung.

## Kernfunktionen (früher Block)

- `calculate_dynamic_payback_period(investment, initial_annual_savings, price_increase_percent) -> float`
  - Jährliche Einsparung wächst mit Preissteigerung; Iteration bis Investitionssumme erreicht; Sicherheitsabbruch > 50 Jahre; unterjährige Feinjustierung.

- `calculate_net_present_value(investment, annual_savings) -> float`
  - NPV = NPV der gleichbleibenden Cashflows über 25 Jahre minus Investition.

- `calculate_internal_rate_of_return(investment, annual_savings) -> float`
  - IRR über Cashflow [-investment, annual_savings × 25] in Prozent; bei Fehler 0.

## Block „50 Berechnungen“ (1–50)

Auszug und Kategorien:

- Grundlagen/KPIs: Jahresertrag, LCOE (€/kWh), Eigenverbrauchsquote, Autarkie, Amortisation, jährliche Ersparnis, Einspeisevergütung, Gesamtertrag, CO2-Ersparnis, effektiver Strompreis.
- Finanzmathematik: NPV, IRR, Alternativanlage, kumulierte Ersparnisse, Speicherdeckungsgrad, Degradation, Preissteigerung, Dachflächennutzung, Break-Even, Szenarienvergleich (Platzhalter).
- Technische KPIs: PR, spezifischer Ertrag, flächenspezifischer Ertrag, Modulwirkungsgrad, Verschattung, DC/AC-Verhältnis, Temperaturkorrektur, Degradationsertrag, Wartungskosten, Speicher-EV-Zuwachs.
- Speicher/Last/Finanzierung: Speichergröße (Heuristik), Lastverschiebung, PV-Deckung Wärmepumpe, ROE, Kapitaldienstfähigkeit, Restwert, lineare AfA, Kosten nach Förderung, Netzanschlusskosten, PV vs. Balkonvergleich.
- Lebensdauer/Risiko/Spezial: WR-Degradation, Notstromfähigkeit, Batterielebensdauer, EV-Ladeprofil, kumulierte CO2-Einsparung, Inflationsausgleich, Investitionsszenarien (Platzhalter), Anlagenerweiterung, Risikoanalyse, Peak-Shaving.

Alle Funktionen folgen einfachen Formeln mit defensiven Divisionen (0-Checks) und liefern Float-Ergebnisse (teils in Prozent, teils in absoluten Einheiten). Einige Rückgaben verwenden `float('inf')` als Signal (z. B. Amortisation bei 0 Einsparungen).

## Spätere Zusatzfunktionen (weitere Finanz-/Öko-Auswertungen)

- `calculate_profitability_index(investment, annual_savings) -> float`
  - PI = NPV künftiger Cashflows / Investment; nutzt `DISCOUNT_RATE` und 25 Jahre.

- `calculate_lcoe(investment, annual_production_kwh) -> float`
  - LCOE als Cent/kWh via Annuitätenfaktor auf Investition; Achtung: Namens-/Signatur-Kollision mit früherer LCOE (€/kWh). Diese hier rechnet in Cent/kWh und verwendet Annuität.

- `calculate_co2_avoidance_per_year(annual_production_kwh) -> float`
  - Tonnen CO2 pro Jahr (kg → t).

- `calculate_energy_payback_time(total_embodied_energy_kwh, annual_production_kwh) -> float`
  - Energetische Amortisationszeit.

- `calculate_co2_payback_time(pv_size_kwp, annual_production_kwh) -> float`
  - Jahre bis Ausgleich grauer Emissionen.

- `calculate_total_roi(investment, annual_savings) -> float`
  - Gesamtrendite in % über 25 Jahre.

- `calculate_annual_equity_return(investment, annual_savings) -> float`
  - Jährliche EK-Rendite in %.

- `calculate_profit_after_x_years(investment, annual_savings, years) -> float`
  - Gewinn nach X Jahren.

- `run_all_extended_analyses(offer_data: Dict[str, Any]) -> Dict[str, Any]`
  - Aggregiert zentrale KPIs: dynamische Amortis (3%/5%), NPV, IRR, PI, LCOE (Annuität/ct), CO2/Jahr (t), EPBT, CO2-Payback, ROI total, jährliche EK-Rendite, Gewinn nach 10/20 Jahren.
  - Erwartet Felder: `total_investment`, `annual_savings`, `annual_production_kwh`, `pv_size_kwp`, `total_embodied_energy_kwh`.

## Contracts und Einheiten

- Eingaben: meist Floats; bei Raten in Prozent wird Prozentzahl erwartet (nicht 0..1), außer explizit anders dokumentiert.
- Ausgaben: Prozentwerte in %, monetäre Werte in €, Energien in kWh, Emissionen kg oder t (je nach Funktion), LCOE entweder €/kWh (früher) oder ct/kWh (später) – Konvention festlegen!

## Edge-Cases und Validierung

- Division durch 0: überall abgefangen (0 oder inf je nach Kontext). IRR/NPV fangen Exceptions ab.
- Sicherheitsabbruch bei dynamischer Amortisation (> 50 Jahre).
- Doppelte Funktionsnamen: `calculate_lcoe` ist doppelt definiert – beim Import gilt die zweite Definition. Aufrufer müssen die gewünschte Variante kennen oder umbenennen (Refactor empfohlen).

## Integration in die App

- Verwendbar für erweiterte KPIs in Analyse und PDF (z. B. IRR, LCOE, Payback, ROI). Ergebnisse können in `analysis_results` gemergt werden.
- Für PDF-Placeholders: IRR als `%`, LCOE als `Cent/kWh`, Payback als `Jahre` sind konsistent mit `placeholders.build_dynamic_data`.

## TypeScript/Electron-Mapping

- Utility-Modul `extendedCalcs.ts` mit exportierten Funktionen. Für IRR/NPV Annuitäten und Diskontierung entweder `financial`-Bibliothek nutzen oder eigene Implementierungen.
- Beispielfunktionen:
  - `irr(cashflows: number[]): number` → %
  - `npv(rate: number, cashflows: number[]): number`
  - `lcoeAnnuitized(invest: number, prod: number, discount=0.04, years=25): number` → ct/kWh

## Tests (empfohlen)

- Unit: LCOE (beide Varianten), IRR (bekannter Cashflow), NPV, dynamische Amortisation (mit/ohne Preissteigerung), CO2-Payback.
- Edge: 0-Produktions-/0-Savings-Fälle, negative Inputs, lange Laufzeiten.
- Contract-Test: `run_all_extended_analyses` mit Minimal-`offer_data` gibt alle Keys ohne Exceptions zurück.

## Hinweise/Backlog

- Refactor Doppeldefinition `calculate_lcoe`: eindeutige Benennung (z. B. `calculate_lcoe_eur_per_kwh` vs. `calculate_lcoe_cent_per_kwh_annuity`).
- Die „50-Berechnungen“-Sektion enthält Platzhalter (`compare_scenarios`, `analyze_investment_scenarios`). Optional mit echter Logik füllen oder klar als Platzhalter kennzeichnen.
