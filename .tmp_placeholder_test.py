import sys

sys.path.append(r"c:/123456/corba")
from pdf_template_engine import placeholders

print("OK mapping size:", len(placeholders.PLACEHOLDER_MAPPING))

project_data = {
    "customer_data": {"first_name":"Max","last_name":"Mustermann"},
    "project_details": {
        "module_quantity": 10,
        "selected_module_capacity_w": 400,
        "selected_module_name": "AlphaSolar 450W",
        "selected_inverter_name": "PowerMax 5K",
        "include_storage": True,
        "selected_storage_name": "EnergyCell 10kWh",
        "selected_storage_storage_power_kw": 10.0
    }
}
analysis_results = {
    "annual_pv_production_kwh": 8250,
    "self_supply_rate_percent": 54,
    "self_consumption_percent": 42,
    "lcoe_euro_per_kwh": 0.089,
    "irr_percent": 12.7,
    "savings_20y_with_battery_eur": 36958,
    "savings_20y_without_battery_eur": 29150
}
company_info = {
    "name":"ACME Solar","street":"Musterweg 1","zip_code":"12345",
    "city":"Berlin","phone":"01234","email":"info@example.com"
}

res = placeholders.build_dynamic_data(project_data, analysis_results, company_info)
keys_sample = sorted([k for k in res.keys() if k.startswith(("module_","inverter_","storage_"))])
print("Keys sample:", keys_sample)
print("anlage_kwp:", res.get("anlage_kwp"))
print("lcoe:", res.get("lcoe_cent_per_kwh"))
