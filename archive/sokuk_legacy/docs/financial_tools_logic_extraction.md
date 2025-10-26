# financial_tools.py — vollständige Logik-Extraktion

Ziel: Finanzfunktionen und -vergleiche für PV-Projekte dokumentieren. Enthält Annuitätenkredit, Leasing, Abschreibung, Contracting und Vergleich/Empfehlung.

## Überblick

- Rolle: Reine Berechnungsbibliothek für Finanzoptionen (UI-agnostisch, teilweise mit `streamlit`-Hinweisen für Live-Apps).
- Hauptfunktionen:
  - `calculate_annuity(principal, annual_interest_rate, duration_years)`
  - `calculate_leasing_costs(total_investment, leasing_factor, duration_months, residual_value_percent=1.0)`
  - `calculate_depreciation(initial_value, useful_life_years, method='linear')`
  - `calculate_financing_comparison(investment, annual_interest_rate, duration_years, leasing_factor)`
  - `calculate_capital_gains_tax(profit, tax_rate=26.375)`
  - `calculate_contracting_costs(base_fee, consumption_price, consumed_kwh, period_years=1)`

## Funktionskatalog und Kontrakte

- `calculate_annuity(principal: float, annual_interest_rate: float, duration_years: int) -> Dict`
  - Input: Darlehenssumme (>0), Zinssatz (% ≥0), Laufzeit (Jahre >0)
  - Output: `{ monatliche_rate, gesamtzinsen, gesamtkosten, effective_rate, tilgungsplan[], laufzeit_monate }`
  - Fehler: bei ungültigen Inputs `{ "error": "Ungültige Eingabeparameter" }`
  - Hinweise: Tilgungsplan monatlich, Zinsanteil fallend, Tilgung steigend; zinsfrei-Fall implementiert.

- `calculate_leasing_costs(total_investment: float, leasing_factor: float, duration_months: int, residual_value_percent: float=1.0) -> Dict`
  - Input: Investition, Leasingfaktor (%/Monat), Laufzeit (Monate), Restwert (%)
  - Output: `{ monatliche_rate, gesamtkosten, restwert, effektive_kosten, kostenvorteil_vs_kauf }`
  - Fehler: `{ "error": "Ungültige Parameter" }`

- `calculate_depreciation(initial_value: float, useful_life_years: int, method='linear') -> Dict`
  - Input: Anschaffungswert, Nutzungsdauer, Methode
  - Output: `{ methode, jaehrliche_abschreibung, gesamtabschreibung, abschreibungsplan[], steuerersparnis_30_prozent }`
  - Anm.: Implementiert ist die lineare Methode; Platz für Erweiterung (degressiv) vorgesehen.

- `calculate_financing_comparison(investment, annual_interest_rate, duration_years, leasing_factor) -> Dict`
  - Kombiniert Kredit, Leasing und Cash-Kauf (Opportunitätskosten) und liefert `{ kredit, leasing, cash_kauf, empfehlung }`.
  - Empfehlung über `_get_financing_recommendation(...)` → beste Kostenvariante.

- `calculate_capital_gains_tax(profit: float, tax_rate: float=26.375) -> Dict`
  - Input: Gewinn, Steuer (%).
  - Output: `{ brutto_gewinn, steuer, netto_gewinn, steuer_rate, steuer_optimierung_tipps[] }`.

- `calculate_contracting_costs(base_fee: float, consumption_price: float, consumed_kwh: float, period_years: int=1) -> Dict`
  - Output: Jahres- und Laufzeitkosten, effektiver kWh-Preis, Laufzeitjahre.

## Datenflüsse

- Eigenständig (keine DB), wird von UI/Analysis/PDF genutzt:
  - Analysis/Streamlit kann Ergebnisse direkt anzeigen oder in `analysis_results` einspeisen (z. B. Cashflows/ROI-Seite im PDF).
  - `pdf_generator` konsumiert ggf. Tabellen/Summen als Text-/Tabellenelemente.

## Edge-Cases und Validierung

- Null- oder Negativwerte → Fehlerdict statt Exception.
- Zinsfrei-Fall in Annuität: monatliche Rate = Principal/Monate, Zinsen = 0.
- Division-by-zero-Schutz in kWh-Kosten (`consumed_kwh > 0`).

## Migration: Electron + TypeScript

- Portierung 1:1 als Utility-Module:
  - `annuity(principal: number, apr: number, years: number): { monthlyPayment, totalInterest, schedule[] }`
  - `leasingCosts(investment: number, factorPct: number, months: number, residualPct: number)`
  - `depreciationLinear(initial: number, years: number)`
  - `financingComparison(...)` mit Empfehlung.
- Tests in Jest: Happy/Edge-Cases, deterministische Rundungen auf 2 Nachkommastellen.

## Tests (skizziert)

- Annuität: 20.000 €, 4% p.a., 10 Jahre → Rate ~202,49 €, Restschuld ~0 am Ende.
- Leasing: 20.000 €, 1,5%/Monat, 36 Monate, 10% Restwert → effektive_kosten plausibel.
- Depreciation linear: 10.000 €, 10 Jahre → 1.000 €/Jahr, kumuliert korrekt.
- Contracting: Grundgebühr 15 €/Monat, 0,35 €/kWh, 4.000 kWh, 2 Jahre → Effektivpreis.
