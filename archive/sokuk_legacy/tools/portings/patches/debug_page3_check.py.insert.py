# === AUTO-GENERATED INSERT PATCH ===
# target_module: debug_page3_check.py
# insert_blocks follow; keep formatting unchanged

# --- REQUIRED IMPORT SUGGESTIONS (dedupe on apply) ---

# --- DEF BLOCK START: func main ---
def main():
    project_data = {
        "einspeise_art": "parts",   # Teileinspeisung
        # optional: "anlage_kwp": 9.5,
    }

    analysis_results = {
        "anlage_kwp": 9.5,
        # Seite 2
        "netzeinspeisung_kwh": 4683,
        # Speicher:
        "annual_storage_charge_kwh": 1500,  # Ladung
        "annual_storage_discharge_kwh": 905,  # Nutzung/Entladung für Eigenverbrauch
        # Monatslisten bewusst leer lassen -> Fallbacks testen
        # "monthly_storage_charge_kwh": [],
        # "monthly_storage_discharge_for_sc_kwh": [],
        # Preise:
        "electricity_price_eur_per_kwh": 0.2734,        # Kundentarif
        "einspeiseverguetung_eur_per_kwh": 0.0786,      # €/kWh
    }

    company_info = {}

    res = build_dynamic_data(project_data, analysis_results, company_info)

    keys = [
        ("direct_grid_feed_in_eur", "Einnahmen aus Einspeisevergütung"),
        ("battery_usage_savings_eur", "Einsparung durch Speichernutzung"),
        ("battery_surplus_feed_in_eur", "Einnahmen aus Batterieüberschuss"),
        ("calc_grid_feed_in_kwh_page3", "Einspeisung kWh (Seite 3)"),
        ("calc_battery_discharge_kwh_page3", "Speichernutzung kWh (Seite 3)"),
        ("calc_battery_surplus_kwh_page3", "Speicher-Überschuss kWh (Seite 3)"),
        ("total_annual_savings_eur", "Erträge pro Jahr (gesamt)"),
    ]

    print("\n=== Seite 3 – Debug-Ausgabe ===")
    for k, label in keys:
        print(f"{label:38s}: {res.get(k)}")
# --- DEF BLOCK END ---
