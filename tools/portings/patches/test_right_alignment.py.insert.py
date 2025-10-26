# === AUTO-GENERATED INSERT PATCH ===
# target_module: test_right_alignment.py
# insert_blocks follow; keep formatting unchanged

# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---
from pdf_template_engine.placeholders import build_dynamic_data


# --- DEF BLOCK START: func test_right_aligned_values ---
def test_right_aligned_values():
    """Teste die Werte für rechtsbündige Ausrichtung"""

    project_data = {"einspeise_art": "parts"}
    analysis_results = {
        "anlage_kwp": 9.5,
        "netzeinspeisung_kwh": 4683,
        "annual_storage_charge_kwh": 1500,
        "annual_storage_discharge_kwh": 905,
        "electricity_price_eur_per_kwh": 0.2734,
        "einspeiseverguetung_eur_per_kwh": 0.0786,
    }

    result = build_dynamic_data(project_data, analysis_results, {})

    print("=== Werte die jetzt rechtsbündig ausgerichtet werden ===")
    print(f"Direkt: '{result.get('self_consumption_without_battery_eur')}'")
    print(f"Einspeisung: '{result.get('direct_grid_feed_in_eur')}'")
    print(f"Speichernutzung: '{result.get('battery_usage_savings_eur')}'")
    print(f"Überschuss: '{result.get('battery_surplus_feed_in_eur')}'")
    print(f"Gesamt: '{result.get('total_annual_savings_eur')}'")

    print("\n=== Bedarfsanalyse-Werte die bereits rechtsbündig waren ===")
    print(f"NOSW (Ausrichtung): '{result.get('orientation_text')}'")
    print(f"Neigung: '{result.get('roof_inclination_text')}'")
    print(f"Art (Dach): '{result.get('roof_type')}'")
    print(f"EEG: '{result.get('feed_in_tariff_text')}'")
# --- DEF BLOCK END ---
