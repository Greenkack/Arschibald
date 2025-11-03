#!/usr/bin/env python3
"""Test ob alle Charts jetzt verfügbar sind"""

from pdf_ui import check_chart_availability

# Simuliere Berechnungsergebnisse
test_results = {
    'annual_pv_production_kwh': 5000,
    'total_investment_netto': 10000,
    'annual_savings': 1200
}

# Teste die 2 problematischen Charts + ein paar normale
test_keys = [
    'battery_usage_chart_bytes',
    'scenario_comparison_chart_bytes', 
    'scenario_comparison_switcher_chart_bytes',
    'storage_effect_switcher_chart_bytes',
    'monthly_prod_cons_chart_bytes',
    'cost_projection_chart_bytes'
]

print("🧪 TEST: Chart-Verfügbarkeit")
print("=" * 60)

results = []
for key in test_keys:
    is_available = check_chart_availability(key, {}, test_results)
    results.append((key, is_available))
    status = "✅ VERFÜGBAR" if is_available else "❌ NICHT VERFÜGBAR"
    print(f"{status:20} | {key}")

print("=" * 60)
available_count = sum([1 for k, v in results if v])
print(f"Gesamt: {available_count}/{len(results)} verfügbar ({available_count*100//len(results)}%)")

if available_count == len(results):
    print("\n🎉 PERFEKT! Alle getesteten Charts sind verfügbar!")
else:
    print(f"\n⚠️ {len(results) - available_count} Charts noch nicht verfügbar")
