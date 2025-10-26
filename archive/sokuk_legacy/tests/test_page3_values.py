# tools/test_page3_values.py
import sys
from pathlib import Path

THIS = Path(__file__).resolve()
ROOT = THIS.parents[1]  # ...\corba_best-main
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "pdf_template_engine"))

try:
    from pdf_template_engine.placeholders import build_dynamic_data
except Exception:
    from placeholders import build_dynamic_data


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
