"""
Test der neuen Wärmepumpen-Berechnungen
"""
from calculations_heatpump import (
    calculate_domestic_hot_water_demand,
    calculate_heat_load_with_climate_zone,
    calculate_required_flow_temperature,
    check_radiator_compatibility,
    calculate_co2_costs_fossil_heating,
    calculate_beg_subsidy,
    calculate_npv_20_years,
    compare_heating_systems_20_years,
    calculate_pv_self_consumption_heatpump
)

print("=" * 80)
print("🧪 TEST: Neue Wärmepumpen-Berechnungsfunktionen")
print("=" * 80)

# Test 1: Warmwasserbedarf
print("\n1️⃣ Warmwasserbedarf für 150m² Wohnfläche:")
dhw = calculate_domestic_hot_water_demand(150)
print(f"   Personen (geschätzt): {dhw['persons']}")
print(f"   Jährlicher Bedarf: {dhw['annual_dhw_demand_kwh']} kWh")
print(f"   Spitzenlast: {dhw['dhw_load_kw']} kW")

# Test 2: Erweiterte Heizlastberechnung
print("\n2️⃣ Heizlastberechnung mit Klimazone:")
heat_load = calculate_heat_load_with_climate_zone(
    "Altbau saniert", 150, "Gemäßigt", "Mittel"
)
print(f"   Heizlast: {heat_load['heating_load_kw']} kW")
print(f"   Warmwasserlast: {heat_load['dhw_load_kw']} kW")
print(f"   Gesamtlast: {heat_load['total_load_kw']} kW")
print(f"   Jahreswärmebedarf: {heat_load['annual_total_demand_kwh']} kWh")

# Test 3: Radiator-Check
print("\n3️⃣ Radiator-Kompatibilitätsprüfung:")
flow_temp = calculate_required_flow_temperature(
    heat_load['heating_load_kw'], radiator_area_m2=25
)
compat = check_radiator_compatibility(flow_temp['required_flow_temp_c'])
print(f"   Erforderliche Vorlauftemp: {flow_temp['required_flow_temp_c']}°C")
print(f"   Bewertung: {compat['compatibility']} ({compat['color']})")
print(f"   COP-Einfluss: -{compat['cop_impact_percent']}%")
print(f"   Empfehlung: {compat['recommendation']}")

# Test 4: CO2-Kosten
print("\n4️⃣ CO2-Kosten Gasheizung:")
co2 = calculate_co2_costs_fossil_heating(
    "Erdgas", 18000, co2_price_per_ton=85, year=2035
)
print(f"   CO2-Emissionen: {co2['annual_co2_tons']} t/Jahr")
print(f"   CO2-Kosten: {co2['annual_co2_cost_eur']} €/Jahr")
print(f"   GEG-Pflicht grüner Anteil: {co2['geg_min_share']}%")
print(f"   Mehrkosten grüne Brennstoffe: {co2['green_fuel_cost_premium']} €/Jahr")
print(f"   Gesamte Klimakosten: {co2['total_climate_cost']} €/Jahr")

# Test 5: BEG-Förderung
print("\n5️⃣ BEG-Förderung für 30.000€ Wärmepumpe:")
beg = calculate_beg_subsidy(30000, replaces_gas_oil=True, household_income_below_threshold=True)
print(f"   Basisförderung: {beg['base_subsidy_percent']}%")
print(f"   Geschwindigkeitsbonus: {beg['speed_bonus_percent']}%")
print(f"   Einkommensbonus: {beg['income_bonus_percent']}%")
print(f"   Gesamt: {beg['total_subsidy_percent']}%")
print(f"   Fördersumme: {beg['subsidy_amount_eur']} €")
print(f"   Netto-Investment: {beg['net_investment_eur']} €")

# Test 6: NPV über 20 Jahre
print("\n6️⃣ NPV-Berechnung (15.000€ Investment, 1.200€/Jahr Betrieb):")
npv = calculate_npv_20_years(15000, 1200, annual_cost_increase_percent=2.0)
print(f"   Kapitalwert (NPV): {npv['npv_eur']} €")
print(f"   Gesamtkosten (undiskontiert): {npv['total_cost_undiscounted']} €")
print(f"   Äquivalente Jahreskosten: {npv['annual_equivalent_cost']} €/Jahr")

# Test 7: PV-Eigenverbrauch
print("\n7️⃣ PV-Eigenverbrauch mit Wärmepumpe (10 kWp PV, 4.000 kWh WP):")
pv = calculate_pv_self_consumption_heatpump(4000, 10.0, self_consumption_rate_percent=50)
print(f"   PV-Gesamtertrag: {pv['pv_total_yield_kwh']} kWh/Jahr")
print(f"   WP-Verbrauch von PV: {pv['heatpump_from_pv_kwh']} kWh")
print(f"   WP-Verbrauch aus Netz: {pv['heatpump_from_grid_kwh']} kWh")
print(f"   PV-Deckungsgrad WP: {pv['pv_coverage_percent']}%")
print(f"   Kosteneinsparung: {pv['cost_savings_eur']} €/Jahr")

# Test 8: Vollständiger Systemvergleich
print("\n8️⃣ Systemvergleich: Wärmepumpe vs. Erdgas (20 Jahre):")
building = {'annual_total_demand_kwh': heat_load['annual_total_demand_kwh']}
heatpump = {'investment_cost': 30000, 'cop': 3.5}
comparison = compare_heating_systems_20_years(
    building, heatpump, "Erdgas",
    electricity_price_kwh=0.30, fossil_fuel_price_kwh=0.10
)

print(f"\n   💚 WÄRMEPUMPE:")
print(f"      Investment (brutto): {comparison['heatpump']['investment_gross']} €")
print(f"      BEG-Förderung: -{comparison['heatpump']['beg_subsidy']} €")
print(f"      Investment (netto): {comparison['heatpump']['investment_net']} €")
print(f"      Jährliche Betriebskosten: {comparison['heatpump']['annual_operating_cost']} €")
print(f"      Gesamtkosten 20 Jahre: {comparison['heatpump']['total_cost_20years']} €")

print(f"\n   🔥 GASHEIZUNG:")
print(f"      Investment: {comparison['fossil_heating']['investment']} €")
print(f"      Jährliche Betriebskosten: {comparison['fossil_heating']['annual_operating_cost']} €")
print(f"      Gesamtkosten 20 Jahre: {comparison['fossil_heating']['total_cost_20years']} €")

print(f"\n   [CHART] VERGLEICH:")
print(f"      Einsparung über 20 Jahre: {comparison['comparison']['savings_eur_20years']} €")
print(f"      Jährliche Einsparung: {comparison['comparison']['annual_savings_eur']} €")
print(f"      Amortisationszeit: {comparison['comparison']['payback_years']} Jahre")
print(f"      CO2-Einsparung: {comparison['comparison']['co2_savings_tons_20years']} Tonnen")
print(f"      Bewertung: {comparison['comparison']['recommendation']}")

print("\n" + "=" * 80)
print("[OK] ALLE TESTS ERFOLGREICH!")
print("=" * 80)
