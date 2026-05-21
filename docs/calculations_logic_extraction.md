# calculations.py – Vollständige Logik-Extraktion und Migrationsleitfaden

Dieses Dokument extrahiert zu 100% die Logik und Datenflüsse aus `calculations.py` und bereitet die Migration in eine Electron/PrimeReact/TypeScript-Architektur vor. Es dient als „Single Source of Truth“ für Kontrakte (Inputs/Outputs), Nebenwirkungen, Fehlerbilder, Performance-Überlegungen und TS/IPCs.

## Überblick – Aufgaben von calculations.py

- Kern-Berechnungs-Engine für PV-Angebote und Wirtschaftlichkeit
  - Produktions-/Verbrauchsmodell Jahr 1 und mehrjährige Simulation (Degression, Strompreissteigerung, EEG-Phase, Wartung)
  - Kostenbildung: Preis-Matrix (Excel/CSV), Zusatz-/Optionalkosten, Gerüst, Sonderkosten, Speicher-Aufpreise
  - Kennzahlen: Amortisation, NPV, IRR, LCOE, ROI, PR, CO2-Äquivalente, E-Auto/Wärmepumpe Effekte
  - PVGIS-Integration mit robuster Fehlerbehandlung und Fallback auf manuelle Ertragsmodelle
  - Wartungs-/Degradations-Module und Energiepreisvergleich
- Unterstützende Klassen/Funktionen: Price-Matrix-Parsing + Cache, Formatierer, PVGIS-API, Analyseklassen
- Session-State-Backup: Ergebnisse werden optional in Streamlit `st.session_state` gespiegelt (Zeitstempel, Backup)

## Externe Abhängigkeiten und Datenquellen

- Datenbank (`database.load_admin_setting`):
  - `global_constants` (z. B. MwSt., Inflationsrate, Standard-Erträge, Verteilungsfaktoren, Flags wie `pvgis_enabled`) – robust mit Fallback
  - `price_matrix_excel_bytes` (Bytes) oder `price_matrix_csv_data` (CSV-String)
  - `feed_in_tariffs` (Teileinspeisung/Volleinspeisung, kWp-Stufen)
  - `amortization_cheat_settings` (optional; Manipulation der ausgewiesenen Amortisationszeit)
  - `pvgis_enabled` (Boolean oder Stringrepräsentation)
- Produkt-DB (`product_db.get_product_by_id`): Module, Wechselrichter, Speicher und optionale Komponenten (Kostenfelder, Modelle, Leistungsdaten)
- HTTP: `requests` zur PVGIS API
- Python: `pandas`, `numpy`, `numpy_financial` (optional, IRR), `math`, `datetime`, `json`

## Öffentliche API – Funktionen, Klassen, Nebenwirkungen

### perform_calculations(project_data, texts, errors_list, simulation_duration_user=None, electricity_price_increase_user=None) -> Dict

- Zweck: End-to-End Berechnung für ein Projekt. Gibt ein umfangreiches Ergebnis-Dict mit Kennzahlen, Arrays und Artefakt-Platzhaltern zurück.
- Inputs (Kontrakt):
  - `project_data: Dict`
    - `customer_data` (z. B. `type`, `income_tax_rate_percent`)
    - `project_details`:
      - Verbrauch/Preis: `annual_consumption_kwh_yr`, `consumption_heating_kwh_yr`, `electricity_price_kwh`
      - Geometrie/Lage: `roof_orientation` (z. B. Süd/Ost/…), `roof_inclination_deg`, `latitude`, `longitude`
      - Komponenten: `module_quantity`, `selected_module_id`, `selected_inverter_id`
      - Speicher: `include_storage`, `selected_storage_id`, `selected_storage_storage_power_kw` (Kapazität in kWh; Name historisch)
      - Bau: `free_roof_area_sqm`, `building_height_gt_7m`
      - Einspeisung: `feed_in_type` („Teileinspeisung“|„Volleinspeisung“)
      - Optionen: `include_additional_components`, diverse `selected_*_id`
      - Zukunftsszenarien: `future_ev`, `future_hp`, `verschattungsverlust_pct`
    - `economic_data`:
      - `simulation_period_years`, `electricity_price_increase_annual_percent`
  - `texts: Dict[str, str]` – Übersetzung/Fehlermeldungen (robuste Defaults)
  - `errors_list: List[str]` – wird von der Funktion weiter befüllt (Side-Effect)
  - `simulation_duration_user: Optional[int]` – UI-Override für Laufzeit
  - `electricity_price_increase_user: Optional[float]` – UI-Override für Preissteigerung
- Side-Effects:
  - Greift auf Admin-Settings/Produkt-DB zu
  - Kann `requests.get` an PVGIS senden
  - Schreibt (falls verfügbar) in `st.session_state` Backups: `calculation_results`, `calculation_results_backup`, `calculation_timestamp`
  - Erweitert `errors_list` mit Hinweisen/Fehlern
- Erfolgs-/Fehlerverhalten:
  - Robust gegen fehlende Settings/DB; harte Fallbacks auf Dummy/Defaults
  - PVGIS-Fehler werden abgefangen; Rückfall auf manuelle Ertragsberechnung
  - IRR: Wenn `numpy_financial` fehlt/Fehler, wird IRR `NaN` gesetzt und Hinweis erzeugt

#### Berechnungs-Pipeline (vereinfacht)

1) Admin-Settings laden; Preis-Matrix (Excel/CSV) via Cache parsen; Einspeisevergütungen bereitstellen
2) Projekt-Merkmale erfassen; `anlage_kwp` aus `module_quantity` x Modul-Watt berechnen
3) PV-Erträge:
   - Wenn `pvgis_enabled` und Koordinaten ok: PVGIS anfragen und nutzen
   - Sonst: manuelle Ertragsberechnung via Lookup (Ausrichtung/Neigung), monatliche Verteilung
   - Globale Ertragsanpassung anwenden
4) Verbrauchsmodell (monatliche Verteilung) und Eigenverbrauch (direkt + Speicher)
5) Energiebilanz Monat/Jahr: Einspeisung, Netzbezug, Eigenverbrauchsummen
6) Kostenbildung:
   - Matrix-Grundpreis je Modulanzahl und Spalte (Speicher-Modell oder „Ohne Speicher“)
   - Zusatzkosten: Module/WR/Accessoires/Sonstiges/Gerüst/Sonder-/Optionalkomponenten
   - Speicher-Aufpreis aus DB addieren, wenn Matrix „Ohne Speicher“ (oder kein Matrixpreis) und Speicher ausgewählt
   - Summen: `subtotal_netto`, Bonus, `total_investment_netto`, MwSt.→`total_investment_brutto`
7) Jahr-1 Wirtschaftlichkeit: Stromkosteneinsparung, Einspeiseerlös (Teile/Volleinspeisung), evtl. Steuer-Vorteil
8) Amortisation, optionaler „Cheat“-Override aus Admin-Settings
9) Mehrjahressimulation: Degradation, Strompreissteigerung, EEG-Phase, Wartung, Steuer; Cashflows/Jahr, kumuliert
10) NPV, IRR, LCOE, ROI, PR, AfA/Restwert, Alternativanlage-Vergleich
11) CO2-Effekte, EV/WP, Kostenhochrechnung ohne PV
12) Erweiterte Analysen/Monitore: Break-Even-Szenarien, Energiepreisvergleich, Degradation, Wartungsplan
13) Chart-Byte-Platzhalter initialisieren (None), diverse KPI-Ableitungen (Eigenverbrauch-, Speicheranteile)
14) Session-State-Backup

#### Wichtige Ergebnis-Keys (Auszug, gruppiert)

- Quelle/Settings:
  - `price_matrix_source_type` („Excel“|„CSV“|„Keine“)
  - `price_matrix_loaded_successfully: bool`
  - `simulation_period_years_effective: int`
  - `electricity_price_increase_rate_effective_percent: float`
  - `vat_rate_percent: float`
- Anlage/Ertrag:
  - `anlage_kwp: float`
  - `annual_pv_production_kwh: float`
  - `monthly_productions_sim: List[float]` (Monat 1..12, Jahr 1)
  - `specific_annual_yield_kwh_per_kwp: float`
  - `pvgis_data_used: bool`, `pvgis_source: str`
- Verbrauch/Energieflüsse Jahr 1:
  - `total_consumption_kwh_yr`, `monthly_consumption_sim`
  - `monthly_direct_self_consumption_kwh`
  - `monthly_storage_charge_kwh`, `monthly_storage_discharge_for_sc_kwh`
  - `monthly_feed_in_kwh`, `monthly_grid_bezug_kwh`
  - `eigenverbrauch_pro_jahr_kwh`, `netzeinspeisung_kwh`, `grid_bezug_kwh`
- Kosten:
  - `base_matrix_price_netto`, `total_additional_costs_netto`, `subtotal_netto`
  - Einzelkosten: `cost_modules_aufpreis_netto`, `cost_inverter_aufpreis_netto`, `cost_storage_aufpreis_product_db_netto`, `cost_accessories_aufpreis_netto`, `cost_misc_netto`, `cost_scaffolding_netto`, `cost_custom_netto`, `total_optional_components_cost_netto` (+ pro Option z. B. `cost_wallbox_aufpreis_netto` …)
  - `total_investment_netto`, `total_investment_brutto`
- Jahr-1 Nutzen/Erträge:
  - `einspeiseverguetung_ct_per_kwh`, `einspeiseverguetung_eur_per_kwh`
  - `annual_feed_in_revenue_year1`
  - `annual_electricity_cost_savings_self_consumption_year1`
  - `tax_benefit_feed_in_year1`
  - `annual_financial_benefit_year1`
  - `amortization_time_years` (+ optional `amortization_time_years_original` bei Cheat)
- Simulation über Jahre (Laufzeit = `simulation_period_years_effective`):
  - `annual_productions_sim`, `annual_benefits_sim`, `annual_maintenance_costs_sim`
  - `annual_cash_flows_sim` (Jahre 1..N), `cumulative_cash_flows_sim` (inkl. Jahr 0)
  - `annual_elec_prices_sim`, `annual_feed_in_tariffs_sim`, `annual_revenue_from_feed_in_sim`
- Finanz-KPIs:
  - `npv_value`, `npv_per_kwp`
  - `irr_percent` (NaN wenn nicht berechenbar/Dependency fehlt)
  - `lcoe_euro_per_kwh`, `effektiver_pv_strompreis_ct_kwh`
  - `simple_roi_percent`
  - `performance_ratio_percent`
  - AfA/Restwert: `afa_linear_pa_eur`, `restwert_anlage_eur_nach_laufzeit`
  - Alternativanlage: `alternativanlage_kapitalwert_eur`
- CO2 und Äquivalente:
  - `annual_co2_savings_kg`, `co2_equivalent_trees_per_year`, `co2_equivalent_car_km_per_year`, `co2_equivalent_flights_muc_pmi_per_year`
  - `co2_avoidance_cost_euro_per_tonne`
- Speicher-bezogen:
  - `speichergrad_deckungsgrad_speicher_pct`, `optimale_speichergröße_kwh_geschaetzt` (exact Key: `optimale_speichergröße_kwh_geschaetzt` mit „ö“? In Code: `optimale_speichergröße_kwh_geschaetzt` ist als `optimale_speichergröse…` auf Deutsch mit Umlaut „ö“ geschrieben? Tatsächlich im Code: `optimale_speichergröße_kwh_geschaetzt` → hier: `optimale_speichergröße_kwh_geschaetzt`. Anmerkung: Im Code: `optimale_speichergröße_kwh_geschaetzt` ist `optimale_speichergröße_kwh_geschaetzt` mittels `"optimale_speichergröße_kwh_geschaetzt"`? Tatsächlich lautet der Key: `optimale_speichergröße_kwh_geschaetzt`. Beim TS-Mapping ASCII-normalisieren.)
  - `notstromkapazitaet_kwh_pro_tag`, `batterie_lebensdauer_geschaetzt_jahre`
- E-Auto/Wärmepumpe:
  - `eauto_ladung_durch_pv_kwh`, `pv_deckungsgrad_wp_pct`
- Prognosen ohne PV:
  - `annual_costs_hochrechnung_values`, `annual_costs_hochrechnung_jahre_effektiv`, `annual_costs_hochrechnung_steigerung_effektiv_prozent`
  - `total_projected_costs_with_increase`, `total_projected_costs_without_increase`
- Erweiterte Module/Analysen:
  - `break_even_scenarios` (aus BreakEvenAnalysis)
  - `energy_price_comparison` (aus EnergyPriceComparison)
  - `degradation_analysis` (aus TechnicalDegradation)
  - `maintenance_schedule` (aus MaintenanceMonitoring)
- Chart-Artefakt-Platzhalter (Bytes; hier auf None gesetzt – erzeugt in UI/Chart-Engine):
  - `monthly_prod_cons_chart_bytes`, `cumulative_cashflow_chart_bytes`, `pv_usage_chart_bytes`, `consumption_coverage_chart_bytes`, `cost_overview_chart_bytes`, `cost_projection_chart_bytes`, `break_even_scenarios_chart_bytes`, `technical_degradation_chart_bytes`, `maintenance_schedule_chart_bytes`, `energy_price_comparison_chart_bytes`
- Diverse:
  - `direktverbrauch_anteil_pv_produktion_pct`, `speichernutzung_anteil_pv_produktion_pct`
  - `verschattungsverlust_pct`
  - `calculation_errors` (Referenz auf `errors_list`)

Hinweis: Alle numerischen Felder sind robust geglättet (NaN/Inf Checks) und mit Fallbacks versehen.

### get_pvgis_data(lat, lon, peak_power_kwp, tilt, azimuth, system_loss_percent=14.0, texts=None, errors_list=None, debug_mode_enabled=False) -> Optional[Dict]

- Holt PV-Leistungsdaten von PVGIS (Monatswerte `E_m`, Jahreswerte `E_y`, `Yield_y`).
- Validiert Koordinaten/Parameter, baut GET auf Endpoint `https://re.jrc.ec.europa.eu/api/seriescalc` mit `outputformat=json` und `browser=0`.
- Fehlerfälle: HTTP/Timeout/Connection/Request/JSON-Decode → stringisierte Fehler in `errors_list`, Rückgabe `None`.
- Success: `{ monthly_production_kwh: List[12], annual_production_kwh: float, specific_yield_kwh_kwp_pa: float, pvgis_source: str }`.

### Price-Matrix Parsing und Cache

- `load_price_matrix_df_with_cache(excel_bytes, csv_content, errors_list) -> (Optional[pd.DataFrame], source: str)`
  - Bevorzugt Excel-Bytes; sonst CSV; Hash-basierter Cache (`sha256` von Bytes/CSV) verhindert wiederholtes Parsen
- `parse_module_price_matrix_excel(excel_bytes, errors_list) -> Optional[pd.DataFrame]`
  - Index „Anzahl Module“, Spalten numeric, Tausender/Komma-Korrektur, Drop leer
- `parse_module_price_matrix_csv(csv_data, errors_list) -> Optional[pd.DataFrame]`
  - `sep=';'`, `decimal=','`, `thousands='.'`, Kommentar „#“, robustes Index-Handling, Typkonvertierung

### Hilfsfunktionen

- `format_kpi_value(value, unit="", na_text_key="data_not_available_short", precision=2, texts_dict=None) -> str`
  - Flexible Formatierung inkl. deutscher Zahlenkonvention, String→Float Sanitisierung, NaN/Inf-Behandlung
- `convert_orientation_to_pvgis_azimuth(orientation_text) -> int`
  - Mappt Textausrichtungen (Süd/Ost/West/…) auf PVGIS Azimut (Süd=0, Ost=-90, West=90, Nord=180, Diagonalen etc.)

### Angebotserstellung

- `calculate_offer_details(customer_id: Optional[int]=None, project_data: Optional[Dict]=None) -> Dict`
  - Führt intern `perform_calculations` aus und baut Angebots-Dict mit Kerndaten (Invest, Einsparung, Amortisation, Komponenten)

### Erweiterte Analyse-Klassen (am Dateiende)

- `BreakEvenAnalysis`
  - ctor(investment, annual_savings, inflation_rate, electricity_price_increase)
  - `calculate_scenarios() -> Dict[str, Dict]` mit „Konservativ/Basis/Optimistisch“: years_to_break_even, total_savings_at_break_even, annual_roi_percent
- `EnergyPriceComparison`
  - ctor(current_consumption, current_price, pv_production, self_consumption, feed_in_rate)
  - `compare_tariffs(tariffs)` liefert Kosten/Ersparnis-Vergleichsliste
- `TechnicalDegradation`
  - ctor(initial_power, annual_degradation, warranty_years, warranty_power)
  - `calculate_degradation(years=25)` → Effizienz/Jahr, Degradationsraten, Garantie-Compliance
- `MaintenanceMonitoring`
  - ctor(components, installation_date)
  - `generate_maintenance_schedule()` → nächste Wartungen, Prioritäten, Jahreskosten

### AdvancedCalculationsIntegrator (im Kopfbereich der Datei)

Stellt optionale/erweiterte Analysen bereit. Enthaltene Methoden (Auszug) und Rückgaben:

- `_calculate_degradation(base_data)` → Verlauf, Energieverlust, final performance
- `_calculate_shading(base_data)` → Verschattungsmatrix, Jahresverlust, optimale Stunden
- `_calculate_grid_interaction(base_data)` → Einspeisung/Bezug, Eigenverbrauch, Autarkie
- `_calculate_battery_cycles(base_data)` → Zyklen, Lebensdauer, Kapazitätsverlauf
- `_calculate_weather_impact(base_data)` → Wetterverteilung/Faktoren, Produktionsverlust
- `_calculate_maintenance(base_data)` → 10-Jahres-Plan, jährliche Summen
- `_calculate_carbon_footprint(base_data)` → Herstell-/Jahres-CO2, Amortisation
- `_calculate_peak_shaving(base_data)` → Lastspitzenreduktion und Kostenersparnis
- `_calculate_dynamic_pricing(base_data)` → Arbitrageertrag mit Speicher
- `_calculate_energy_independence(base_data)` → Autarkie-Entwicklung, Kostenverlauf
- `calculate_recycling_potential(calc_results, project_data)` → Materialwerte, Recyclingquote, CO2
- Mehrere Convenience-„calculate_*“-Stubs für zukünftige Erweiterungen

Diese Integrator-Methoden sind unabhängig von `perform_calculations`, können aber mit dessen Ergebnissen/Projektparametern gespeist werden.

## Preisbildung – detaillierte Regeln (Matrix + Auf-/Abschläge)

- Matrix-Zeilenwahl: größte Zeile `<= module_quantity`
- Spaltenwahl:
  - Wenn Speicher gewählt und die Spalte mit dem Speichermodell vorhanden und numerisch → nutze diese Spalte
  - Sonst Fallback: Spalte „Ohne Speicher“ (lokalisierter Text über `texts["no_storage_option_for_matrix"]`)
  - Wenn keine Preise gefunden → Grundpreis 0 EUR und Fehlerhinweis
- Pauschalpreis-Erkennung: Wenn Matrixpreis > 0 und Spalte bestimmt → Zusatzpreise (Module/WR/Zubehör/Sonstige) entfallen
- Speicher-Aufpreis aus Produkt-DB wird nur addiert, wenn Matrix-Spalte „Ohne Speicher“ genutzt wurde oder kein Matrixpreis existiert
- Weitere Kosten:
  - Gerüst: `free_roof_area_sqm * scaffolding_cost_per_sqm_gt_7m_netto` bei `building_height_gt_7m`
  - `custom_costs_netto` (manuell)
  - Optionalkomponenten: Map `selected_*_id` → `cost_*_aufpreis_netto`; Summe in `total_optional_components_cost_netto`
- Summen: `subtotal_netto` → `- one_time_bonus_eur` → `total_investment_netto` → Brutto mit `vat_rate_percent`

## Ertrags-/Verbrauchsmodell und Speicherlogik (Jahr 1)

- Produktion:
  - PVGIS (präferiert bei aktivem Flag + Koordinaten) oder manuelles Lookup nach Ausrichtung/Neigung mit Monatverteilung
  - Globale Ertragsanpassung `global_yield_adjustment_percent` wird auf Jahr-1 Produktion/Monate angewandt
- Verbrauchsverteilung: aus `monthly_consumption_distribution` (validiert, normalisiert)
- Eigenverbrauch:
  - Direktverbrauch = min(Produktion*`direct_self_consumption_factor_of_production`, Verbrauch) je Monat
  - Speicher (falls aktiv):
    - max. monatlich ladbare Energie = `storage_capacity_kwh * (storage_cycles_per_year/12)`
    - Laden: bis min(Überschuss, theoretisches Brutto-Limit/Wirkungsgrad), Netto im Speicher = Brutto*`storage_efficiency`
    - Entladen: min(Netto-Ladung, Restverbrauch nach Direktverbrauch)
  - Rest: Einspeisung/Netzbezug

## Mehrjahressimulation und Finanzen

- Produktion pro Jahr: Jahr-1-Produktion mit `annual_module_degradation_percent` abgesenkt
- Aufteilung Eigenverbrauch/Einspeisung wird proportional zur Produktionsänderung skaliert
- Strompreis: Jahr-1 `electricity_price_kwh` mit jährlicher Steigerung
- Einspeisetarif: fix für EEG-Dauer; danach Marktwert-Strom
- Wartung: feste/variable Kosten mit jährlicher Steigerung (Default an Inflation gekoppelt)
- Cashflows: (Kostenersparnis + Einspeiseerlös + evtl. Steuer) – Wartung
- KPIs:
  - NPV: Diskontsatz = `loan_interest_rate_percent`
  - IRR: `numpy_financial.irr` auf Cashflows inkl. Invest in Jahr 0; Exceptions → NaN
  - LCOE: (Invest + diskontierte Opex) / diskontierte Produktion
  - ROI (einfach): Jahr-1 Nutzen / Invest
  - PR: `specific_annual_yield_kwh_per_kwp` vs. Referenz; fallback auf Default
  - AfA linear und Restwert
  - Alternative Anlage: Endwert bei Zinssatz `alternative_investment_interest_rate_percent`

## Fehlerbehandlung, Edge-Cases, Guards

- PVGIS:
  - Ungültige Koordinaten/Peakpower → Fehlertext + None
  - HTTP/Timeout/Connection/JSON → Fehlertexte; debug-limitierte Response-Ausschnitte
  - Unvollständige Daten (z. B. 0 kWh Jahresertrag) → Hinweis, Fallback manuell
- Price-Matrix:
  - Leere/fehlerhafte Dateien → Fehlertexte und Result: `price_matrix_loaded_successfully = False`
  - Fehlende Zeile/Spalte → definierte Fehler; Grundpreis 0 EUR
  - String-Zahlen werden robust in Floats transformiert (Tausender/Dezimalersatz)
- Finanzen:
  - Division durch 0 → Inf/NaN werden in Anzeigen abgefedert (Formatierer) und als Inf intern belassen, wo sinnvoll
  - Fehlende Dependencies (`numpy_financial`) → `irr_percent = NaN` + Hinweis
- Speicher:
  - cycles/year = 0 oder unbekannte Zyklen → Lebensdauer auf inf oder Fallback gesetzt
- Verteilungen:
  - Monatliche Verteilungsfaktoren werden validiert und normalisiert; invalid → fallback uniform
- Session-State nicht vorhanden → Backup übersprungen (silent)

## Integration in UI und PDF

- Analysis-UI konsumiert die Ergebnis-Keys (u. a. Produktionen/Verbräuche, Kosten, KPIs, Simulationen)
- Chart-Bytes werden hier nur als Platzhalter gesetzt – die UI erstellt/füllt sie
- PDF-Pipeline nutzt u. a. `anlage_kwp`, `annual_pv_production_kwh`, `total_investment_netto/brutto`, Einspeise-/Kosten-Listen, Simulationen

## TypeScript/Electron Mappings (Services, Interfaces, IPC)

Hinweis: Umlaute in Keys für TS-Modelle ASCII-normalisieren (z. B. `optimale_speichergröße_kwh_geschaetzt` → `optimalStorageSizeKwhEstimated`).

- Interfaces (Auszug):
  - Project
    - customerData: { type: 'Privat'|'Gewerblich'; incomeTaxRatePercent?: number }
    - projectDetails: {
        annualConsumptionKwhYr?: number; consumptionHeatingKwhYr?: number;
        electricityPriceKwh?: number; moduleQuantity?: number;
        selectedModuleId?: number; selectedInverterId?: number;
        includeStorage?: boolean; selectedStorageId?: number; storageCapacityKwh?: number;
        freeRoofAreaSqm?: number; buildingHeightGt7m?: boolean;
        roofOrientation?: string; roofInclinationDeg?: number;
        latitude?: number; longitude?: number; feedInType?: 'Teileinspeisung'|'Volleinspeisung';
        includeAdditionalComponents?: boolean; selectedWallboxId?: number; selectedEmsId?: number; ...
      }
    - economicData: { simulationPeriodYears?: number; electricityPriceIncreaseAnnualPercent?: number }
  - Texts: Record<string, string>
  - CalculationResult: strongly typed Partial with groups (production, consumption, costs, kpis, simulation, co2, storage, extras)

- Services:
  - PriceMatrixService
    - parseExcel(bytes) => Matrix; parseCsv(text) => Matrix; pickPrice(moduleCount, storageName|noStorage)
  - PVGISService
    - getData({lat, lon, kwp, tilt, azimuth, systemLossPercent}) => { monthly, annual, specificYield, source }
  - CalculationsService
    - `performCalculations(project: Project, texts: Texts, options?: { durationYears?: number; priceIncreasePct?: number }): Promise<CalculationResult>`
  - FinanceService
    - npv(cashflows, rate), irr(cashflows), lcoe(invest, opex[], production[])
  - DegradationService, MaintenanceService, EnergyPriceComparisonService, BreakEvenService

- IPC (Beispiele):
  - `calc/perform` → req: Project + options; res: CalculationResult
  - `pvgis/fetch` → req: {lat,lon,kwp,tilt,azimuth,loss}; res: PVGISData
  - `matrix/parseExcel`|`matrix/parseCsv` → Matrix JSON
  - `finance/npv|irr|lcoe` → Zahlen

## Qualitätssicherung und Performance

- Price-Matrix Cache: Hash-basiert; erneutes Parsen vermeiden
- Netzaufrufe: PVGIS mit Timeout (25s) und defensiver Fehlerbehandlung
- Zahlenrobustheit: String-Zahlen säubern, NaN/Inf abfedern
- Quick Gates (lokal prüfbar):
  - Syntax/Lint: Python-Datei validierbar, keine unbenutzten Imports im Doc-Kontext
  - Smoke-Test: `calculate_offer_details()` mit Dummy-Daten liefert sinnvolle Struktur und keine Ausnahmen

## Tests – Empfehlungen (Python/TS)

- Parser-Tests: CSV/Excel Varianten (Indexspalte/Formatabweichungen), leere Dateien → Fehlertexte
- PVGIS-Tests: Mock der HTTP-Responses für Happy/Fehlerfälle; Validierung Mapping (E_m/E_y/Yield_y)
- Speicher-Logik: Grenzfälle (0 Kapazität, 0 Effizienz, hohe Zyklen, Teil-/Volllastmonat)
- Finanzen: NPV/IRR/LCOE gegen Referenzwerte; `numpy_financial` Abwesenheit simulieren
- Simulation: Degradation & EEG-Wechsel nach N Jahren korrekt
- Konsistenz: Summe Monatswerte = Jahreswerte; Prozentanteile 0..100

## Migrations-Backlog (konkret)

- TS-Modelle für CalculationResult erstellen; Umlaute/Feldnamen vereinheitlichen
- IPC-Routen implementieren und in Renderer konsumieren (PrimeReact Tabs/Charts)
- Price-Matrix-Upload/Parsing an Admin-UI anbinden
- Optional: IRR-Implementierung ohne numpy_financial (Newton-Verfahren) für Node-Seite
- Fallback-Strategie für PVGIS-Ausfall im Electron-Kontext (Offline-Cache, lokales Profil)

## Anmerkungen zur Terminologie

- „Speicher“: Im Code wird die ausgewählte Kapazität aus `selected_storage_storage_power_kw` gelesen, ist aber eine Energie (kWh). In TS als `storageCapacityKwh` abbilden.
- Keys mit Umlauten sollten beim TS-Mapping ASCII-normalisiert werden.

## Akzeptanzkriterien (Done-Definition für Migration)

- Ein TS/Electron-Service kann `performCalculations` semantisch nachbilden und alle oben genannten Ergebnisgruppen liefern.
- Mindestens folgende KPIs sind vorhanden und korrekt befüllt: `anlage_kwp`, `annual_pv_production_kwh`, `total_investment_netto/brutto`, `annual_financial_benefit_year1`, `amortization_time_years`, `npv_value`, `irr_percent` (oder begründet NaN), `lcoe_euro_per_kwh`, `self_supply_rate_percent`.
- Price-Matrix-Fälle (mit/ohne Speicher, fehlende Spalten) sind abgedeckt.
- PVGIS-Integration ist optional, mit manuellem Fallback.
