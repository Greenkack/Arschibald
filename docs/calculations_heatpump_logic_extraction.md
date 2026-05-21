# calculations_heatpump.py – vollständige Logik-Extraktion

Dieses Modul bündelt Berechnungen zur Auslegung und Wirtschaftlichkeit von Wärmepumpen. Es enthält dimensionsgebende Heuristiken (Heizlast aus Gebäudedaten, Ableitung aus Jahreswärmebedarf), Auswahlhilfen (passende WP), Verbrauchs-/Kostenmodelle, sowie eine robuste Rückwärtsabschätzung des Wärmebedarfs aus Brennstoffverbräuchen.

## Hauptfunktionen und Contracts

- `calculate_building_heat_load(building_type: str, living_area_m2: float, insulation_quality: str) -> float`
  - Heizlast-Schätzung in kW basierend auf spezifischen W/m²-Werten je Gebäudetyp und einem Dämmfaktor.
  - Tabellen: `base_load_w_per_m2` für Typ (KFW40/55, Altbau saniert/unsaniert), `insulation_factor` (Gut/Mittel/Schlecht).
  - Rückgabe: kW (W→kW durch /1000).

- `recommend_heat_pump(heat_load_kw: float, available_pumps: List[Dict]) -> Dict | None`
  - Wählt aus `available_pumps` die kleinste Pumpe, deren `heating_output_kw` >= Heizlast ist; sortiert aufsteigend.
  - Rückgabe: Pumpen-Dict oder None, wenn keine passend.

- `calculate_annual_energy_consumption(heat_load_kw: float, scop: float, heating_hours: int = 1800) -> float`
  - Stromverbrauch pro Jahr in kWh: Wärmebedarf (kWh) / SCOP. Wärmebedarf = `heat_load_kw * heating_hours`.
  - Bei `scop == 0` → 0.0.

- `calculate_heatpump_economics(heatpump_data: Dict[str, Any], building_data: Dict[str, Any] = None) -> Dict[str, Any]`
  - Wirtschaftlichkeitsrechnung anhand gegebener Daten und Defaults:
    - Inputs (Fallback-Logik):
      - Heizwärme: `heating_demand` (oder aus `building_data`), kWh/Jahr
      - WP-Leistung: `heatpump_power`/`heating_power_kw`
      - COP/SCOP: `cop`/`cop_rating`
      - Preise: `electricity_price` (€/kWh), `investment_cost` (`price`)
      - Alternative Heizkosten: `alternative_fuel_price` (€/kWh), `alternative_efficiency`
    - Rechenschritte:
      - Stromverbrauch: `heating_demand / cop`
      - Stromkosten p.a.: Verbrauch × Strompreis
      - Alternative Kosten: (heating_demand / alternative_efficiency) × alternative_fuel_price
      - Einsparung p.a.: Alternative − Stromkosten
      - Amortisation: Invest / Einsparung (falls Einsparung > 0, sonst inf→None im Output)
      - 20-Jahres-Bilanz: Einsparung × 20 − Invest
    - Output: kWh, €/Jahr, Einsparung, `payback_period_years` (gerundet, None wenn inf), Total-20y, Bewertung („Wirtschaftlich“ ≤ 15J; „Bedingt“ ≤ 25J; sonst „Nicht“).

- `calculate_heatpump_sizing(building_data: Dict[str, Any]) -> Dict[str, Any]`
  - Auslegungsempfehlung aus Gebäudedaten:
    - Heizlast über `calculate_building_heat_load`
    - Warmwasser-Faktor (default 0.2) additiv zur Last
    - Empfehlung = 1.1 × Gesamtlast
    - Jahreswärmebedarf: Heizlast × `heating_hours` (default 1800)
  - Output: `heat_load_kw`, `total_load_kw`, `recommended_power_kw`, `annual_heat_demand_kwh`, und Echo der Eingaben.

## Verbrauchsbasierte Abschätzung

- Konstanten:
  - `ENERGY_CONTENT_KWH_PER_UNIT`: Öl (l→10 kWh), Gas (kWh→1), Holz (Ster→1400 kWh).
  - `EFFICIENCY_DEFAULTS_BY_SYSTEM`: typische Wirkungsgrade für Systeme (Gas/Öl/Pellets/Fernwärme/Altanlagen etc.).

- `get_default_heating_system_efficiency(heating_system: str) -> float`
  - Liefert typischen Wirkungsgrad; Default 0.85.

- `estimate_annual_heat_demand_kwh_from_consumption(consumption: Dict[str, float], heating_system: str, wood_ster_additional: float = 0.0, custom_efficiency: float | None = None) -> float`
  - Leitet Nutzwärme pro Jahr ab: Summe aus Brennstoffmengen × Energieinhalt × Wirkungsgrad (Holz separat mit 0.75 angesetzt, plus `wood_ster_additional`).
  - `custom_efficiency` überschreibt Default im Bereich 0.4..1.05.
  - Rückgabe: kWh Nutzwärme (>= 0.0).

- `estimate_heat_load_kw_from_annual_demand(annual_heat_demand_kwh: float, heating_hours: int = 1800) -> float`
  - Spitzenlast aus Jahresbedarf via Volllaststunden.

## Integration in die App

- In `heatpump_ui.py` bzw. Analyse-Workflows: sizing → WP-Auswahl → Wirtschaftlichkeit; Ergebnisse als KPIs für UI/PDF nutzbar.
- Für PDF: Relevante Kennzahlen (Verbrauch, Kosten, Einsparungen, Amortisationsjahre, Empfehlung) können auf einer optionalen Wärmepumpen-Seite dargestellt werden.

## TypeScript/Electron-Mapping

- Services in `heatpumpCalcs.ts`:
  - `calcBuildingHeatLoad(type, area, insulation): number`
  - `recommendHeatPump(heatLoad, pumps): Pump | null`
  - `annualConsumption(heatLoad, scop, hours=1800): number`
  - `economics(data, building?): EconomicsResult`
  - `sizing(building): SizingResult`
  - `estimateDemandFromConsumption(consumption, system, woodExtra=0, eff?)`
  - `heatLoadFromAnnualDemand(kwh, hours=1800)`

## Edge-Cases

- Fehlende/0-SCOP → 0-Verbrauch; Payback None.
- Negative oder Null-Eingaben werden defensiv behandelt (max(0.0, …) wo sinnvoll).
- Keine passende Pumpe → None.

## Tests (empfohlen)

- Unit: Heizlast (versch. Typ/Dämmung), Verbrauch aus SCOP, Wirtschaftlichkeit (Grenzfälle Einsparung ≤ 0), Sizing, Verbrauchsbasierte Schätzung (nur Öl, nur Gas, Holz+Zusatz), Spitzenlast aus Jahresbedarf.
- Smoke: End-to-End mit Beispiel-Building/-Heatpump aus __main__.
