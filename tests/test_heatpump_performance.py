"""
Performance-Tests für Wärmepumpen-Modul
Testet alle Berechnungsfunktionen auf < 5s Ausführungszeit
"""
import time
from typing import Any
import calculations_heatpump as hp

# Test-Daten
TEST_BUILDING = {
    'building_type': 'Altbau saniert',
    'living_area_m2': 180.0,
    'insulation_quality': 'Gut',
    'climate_zone': 'Gemäßigt',
    'persons': 4
}

TEST_HEATPUMP = {
    'manufacturer': 'Vaillant',
    'model': 'aroTHERM plus',
    'heating_power_kw': 12.0,
    'cop_rating': 4.2,
    'jaz': 4.2,
    'scop': 4.2,
    'price': 18000,
    'investment_cost_eur': 22000,
    'electricity_price_kwh': 0.32,
    'heating_demand': 15000
}

TEST_RADIATOR = {
    'radiator_area_m2': 25.0,
    'room_temperature_c': 20.0
}

TEST_PV = {
    'pv_system_size_kwp': 10.0,
    'pv_annual_yield_kwh_per_kwp': 1000.0
}


def benchmark_function(func_name: str, func, *args, **kwargs) -> dict[str, Any]:
    """Führt Funktion aus und misst Zeit"""
    start = time.perf_counter()
    try:
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        status = "[OK]" if elapsed < 1.0 else "[SLOW]" if elapsed < 5.0 else "[FAIL]"
        return {
            'name': func_name,
            'time_ms': round(elapsed * 1000, 2),
            'status': status,
            'result': result
        }
    except Exception as e:
        elapsed = time.perf_counter() - start
        return {
            'name': func_name,
            'time_ms': round(elapsed * 1000, 2),
            'status': '[ERROR]',
            'error': str(e)
        }



def run_performance_tests():
    """Führt alle Performance-Tests aus"""
    print("=" * 80)
    print("WAERMEPUMPEN PERFORMANCE TESTS")
    print("=" * 80)
    print(f"Ziel: Alle Funktionen < 5000ms (optimal < 1000ms)")
    print()

    results = []

    # 1. Heizlastberechnung
    print("Test 1: Heizlastberechnung...")
    r1 = benchmark_function(
        "calculate_building_heat_load",
        hp.calculate_building_heat_load,
        TEST_BUILDING['building_type'],
        TEST_BUILDING['living_area_m2'],
        TEST_BUILDING['insulation_quality']
    )
    results.append(r1)
    print(f"   {r1['status']} {r1['time_ms']}ms")

    # 2. Heizlast mit Klimazone
    print("Test 2: Heizlast mit Klimazone...")
    r2 = benchmark_function(
        "calculate_heat_load_with_climate_zone",
        hp.calculate_heat_load_with_climate_zone,
        TEST_BUILDING['building_type'],
        TEST_BUILDING['living_area_m2'],
        TEST_BUILDING['climate_zone'],
        TEST_BUILDING['insulation_quality'],
        TEST_BUILDING['persons']
    )
    results.append(r2)
    print(f"   {r2['status']} {r2['time_ms']}ms")

    # 3. Warmwasserbedarf
    print("Test 3: Warmwasserbedarf...")
    r3 = benchmark_function(
        "calculate_domestic_hot_water_demand",
        hp.calculate_domestic_hot_water_demand,
        TEST_BUILDING['living_area_m2'],
        TEST_BUILDING['persons']
    )
    results.append(r3)
    print(f"   {r3['status']} {r3['time_ms']}ms")

    # 4. Radiator-Vorlauftemperatur
    print(" Test 4: Radiator-Vorlauftemperatur...")
    heat_load = r1['result'] if 'result' in r1 else 12.0
    r4 = benchmark_function(
        "calculate_required_flow_temperature",
        hp.calculate_required_flow_temperature,
        heat_load,
        TEST_RADIATOR['radiator_area_m2'],
        TEST_RADIATOR['room_temperature_c']
    )
    results.append(r4)
    print(f"   {r4['status']} {r4['time_ms']}ms")

    # 5. Radiator-Kompatibilität
    print(" Test 5: Radiator-Kompatibilität...")
    flow_temp = r4['result'] if 'result' in r4 else 55.0
    r5 = benchmark_function(
        "check_radiator_compatibility",
        hp.check_radiator_compatibility,
        flow_temp,
        70.0,  # heatpump_max_temp_c
        55.0   # optimal_temp_c
    )
    results.append(r5)
    print(f"   {r5['status']} {r5['time_ms']}ms")

    # 6. BEG-Förderung
    print(" Test 6: BEG-Förderung...")
    r6 = benchmark_function(
        "calculate_beg_subsidy",
        hp.calculate_beg_subsidy,
        TEST_HEATPUMP['investment_cost_eur'],
        True,
        False
    )
    results.append(r6)
    print(f"   {r6['status']} {r6['time_ms']}ms")

    # 7. CO2-Kosten
    print(" Test 7: CO2-Kosten fossile Heizung...")
    r7 = benchmark_function(
        "calculate_co2_costs_fossil_heating",
        hp.calculate_co2_costs_fossil_heating,
        "Erdgas",
        15000.0,
        70.0,
        0.15
    )
    results.append(r7)
    print(f"   {r7['status']} {r7['time_ms']}ms")

    # 8. Grüne Brennstoff-Mehrkosten
    print(" Test 8: Grüne Brennstoff-Mehrkosten...")
    r8 = benchmark_function(
        "calculate_green_fuel_premium",
        hp.calculate_green_fuel_premium,
        "Erdgas",
        15000.0,
        0.30
    )
    results.append(r8)
    print(f"   {r8['status']} {r8['time_ms']}ms")

    # 9. NPV 20 Jahre
    print(" Test 9: NPV-Berechnung 20 Jahre...")
    r9 = benchmark_function(
        "calculate_npv_20_years",
        hp.calculate_npv_20_years,
        15000.0,
        1500.0,
        2.0,
        3.0
    )
    results.append(r9)
    print(f"   {r9['status']} {r9['time_ms']}ms")

    # 10. PV-Eigenverbrauch
    print(" Test 10: PV-Eigenverbrauch...")
    r10 = benchmark_function(
        "calculate_pv_self_consumption_heatpump",
        hp.calculate_pv_self_consumption_heatpump,
        3500.0,
        TEST_PV['pv_system_size_kwp'],
        TEST_PV['pv_annual_yield_kwh_per_kwp'],
        30.0,
        0.32,
        0.08
    )
    results.append(r10)
    print(f"   {r10['status']} {r10['time_ms']}ms")

    # 11. Systemvergleich 20 Jahre (komplex!)
    print(" Test 11: Systemvergleich 20 Jahre...")
    building_for_compare = {
        'annual_heat_demand_kwh': 15000
    }
    heatpump_for_compare = {
        'investment_cost_eur': 22000,
        'jaz': 4.2,
        'electricity_price_kwh': 0.32
    }
    r11 = benchmark_function(
        "compare_heating_systems_20_years",
        hp.compare_heating_systems_20_years,
        building_for_compare,
        heatpump_for_compare,
        "Gasheizung"
    )
    results.append(r11)
    print(f"   {r11['status']} {r11['time_ms']}ms")

    print()
    print("=" * 80)
    print(" ZUSAMMENFASSUNG")
    print("=" * 80)

    # Statistiken
    total_time = sum(r['time_ms'] for r in results)
    if len != 0:
        avg_time = total_time / len(results)
    else:
        avg_time = 0.0
    max_time = max(results, key=lambda x: x['time_ms'])
    min_time = min(results, key=lambda x: x['time_ms'])

    ok_count = sum(1 for r in results if '[OK]' in r['status'])
    slow_count = sum(1 for r in results if '[SLOW]' in r['status'])
    fail_count = sum(1 for r in results if '[FAIL]' in r['status'] or '[ERROR]' in r['status'])

    print(f"Funktionen getestet: {len(results)}")
    print(f"  [OK] Schnell (<1s): {ok_count}")
    print(f"  [SLOW] Langsam (1-5s): {slow_count}")
    print(f"  [FAIL] Zu langsam (>5s) / Fehler: {fail_count}")
    print()
    print(f"Gesamt-Zeit: {total_time:.2f}ms ({total_time/1000:.2f}s)")
    print(f"Durchschnitt: {avg_time:.2f}ms")
    print(f"Schnellste: {min_time['name']} ({min_time['time_ms']}ms)")
    print(f"Langsamste: {max_time['name']} ({max_time['time_ms']}ms)")
    print()

    # Bewertung
    if fail_count == 0 and slow_count == 0:
        print("[PASSED] ALLE TESTS BESTANDEN - Exzellente Performance!")
    elif fail_count == 0:
        print("[WARNING] ALLE TESTS UNTER 5s - Performance akzeptabel")
    else:
        print(f"[FAILED] {fail_count} Tests fehlgeschlagen - Details:")
        for r in results:
            if '[FAIL]' in r['status'] or '[ERROR]' in r['status']:
                error_msg = r.get('error', 'Unknown error')
                print(f"  - {r['name']}: {error_msg}")

    print("=" * 80)

    return results


if __name__ == "__main__":
    run_performance_tests()

