#!/usr/bin/env python3
"""Test ob ALLE 55 Charts verfügbar sind"""

from pdf_ui import CHART_KEY_TO_FRIENDLY_NAME_MAP, check_chart_availability

# Simuliere Berechnungsergebnisse
test_results = {
    'annual_pv_production_kwh': 5000,
    'total_investment_netto': 10000,
    'annual_savings': 1200,
    'roi_years': 8.5,
    'co2_savings_tons_per_year': 2.5
}

print("🧪 VOLLSTÄNDIGER TEST: Alle 55 Charts")
print("=" * 80)

results = []
unavailable_charts = []

for chart_key in CHART_KEY_TO_FRIENDLY_NAME_MAP.keys():
    is_available = check_chart_availability(chart_key, {}, test_results)
    results.append((chart_key, is_available))

    if not is_available:
        unavailable_charts.append(chart_key)

# Statistik
available_count = sum([1 for k, v in results if v])
total_count = len(results)
percentage = (available_count * 100) // total_count

print(
    f"✅ Verfügbar:     {available_count}/{total_count} Charts ({percentage}%)")
print(f"❌ Nicht verfügbar: {len(unavailable_charts)}/{total_count} Charts")
print("=" * 80)

if unavailable_charts:
    print("\n⚠️ Noch nicht verfügbare Charts:")
    for chart_key in unavailable_charts:
        chart_name = CHART_KEY_TO_FRIENDLY_NAME_MAP.get(chart_key, chart_key)
        print(f"  ❌ {chart_key}")
        print(f"     → {chart_name}")
else:
    print("\n🎉 PERFEKT! ALLE 55 Charts sind verfügbar!")
    print("✅ 100% Chart-Verfügbarkeit erreicht!")
