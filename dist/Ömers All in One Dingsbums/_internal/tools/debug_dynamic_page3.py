from pdf_template_engine.placeholders import build_dynamic_data

project_data = {
    "einspeise_art": "parts",
    "annual_consumption_kwh": 6000,
}
analysis_results = {
    "anlage_kwp": 9.5,
    "annual_pv_production_kwh": 6000,
    "annual_consumption_kwh": 6000,
    "direct_self_consumption_kwh": 2236,
    "grid_feed_in_kwh": 1836,
    "battery_charge_kwh": 4920,
    "battery_discharge_for_sc_kwh": 1279,
}
company_info = {}

res = build_dynamic_data(project_data, analysis_results, company_info)
for k in [
    "annual_feed_in_revenue_eur",
    "self_consumption_without_battery_eur",
    "direct_grid_feed_in_eur",
    "battery_usage_savings_eur",
    "battery_surplus_feed_in_eur",
    "total_annual_savings_eur",
    "calc_battery_surplus_kwh_page3",
    "calc_grid_feed_in_kwh_page3"
]:
    print(k, res.get(k))
