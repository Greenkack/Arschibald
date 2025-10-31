#!/usr/bin/env python3
# debug_page3_check.py
"""
Mini-Diagnose für Seite 3:
- Prüft die Werte für 'Einspeisung', 'Speichernutzung', 'Überschuss'
- Nutzt deine Zahlen (4683 kWh, 905 kWh, 1500 kWh, 0.2734 €/kWh, <10 kWp)
- Monatslisten bleiben leer, damit Fallbacks (Jahreswerte) greifen
"""
import sys
from pathlib import Path

# ---- Pfade so setzen, dass sowohl Paket- als auch Flat-Layout funktionieren ----
THIS_FILE = Path(__file__).resolve()
TOOLS_DIR = THIS_FILE.parent                       # ...\corba_best-main\tools
PROJ_ROOT = THIS_FILE.parents[1]                   # ...\corba_best-main

# Suchreihenfolge: Projekt-Root, pdf_template_engine/, tools/
sys.path.insert(0, str(PROJ_ROOT))
sys.path.insert(0, str(PROJ_ROOT / "pdf_template_engine"))
sys.path.insert(0, str(TOOLS_DIR))

# ---- robust importieren ----
try:
    from pdf_template_engine.placeholders import build_dynamic_data  # Paketlayout
except Exception:
    try:
        from placeholders import build_dynamic_data  # Flatlayout
    except Exception as e:
        print("Konnte build_dynamic_data nicht importieren:", e)
        sys.exit(1)


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


if __name__ == "__main__":
    main()
