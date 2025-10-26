# === AUTO-GENERATED INSERT PATCH ===
# target_module: tools/test_page3_values.py
# insert_blocks follow; keep formatting unchanged

# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---

# --- DEF BLOCK START: func test_page3_values_baseline ---
def test_page3_values_baseline():
    project_data = {"einspeise_art": "parts"}
    analysis_results = {
        "anlage_kwp": 9.5,
        "netzeinspeisung_kwh": 4683,
        "annual_storage_charge_kwh": 1500,
        "annual_storage_discharge_kwh": 905,
        "electricity_price_eur_per_kwh": 0.2734,
        "einspeiseverguetung_eur_per_kwh": 0.0786,
    }
    res = build_dynamic_data(project_data, analysis_results, {})
    assert res.get("direct_grid_feed_in_eur") == "368,08 €"
    assert res.get("battery_usage_savings_eur") == "247,43 €"
    assert res.get("battery_surplus_feed_in_eur") == "46,77 €"
    assert res.get("calc_grid_feed_in_kwh_page3") == "4.683 kWh"
    assert res.get("calc_battery_discharge_kwh_page3") == "905 kWh"
    assert res.get("calc_battery_surplus_kwh_page3") == "595 kWh"
    assert res.get("total_annual_savings_eur") == "662,28 €"
# --- DEF BLOCK END ---
