from pdf_template_engine.placeholders import build_dynamic_data

project_data = {
    'customer_data': {'first_name': 'A', 'last_name': 'B'},
    'project_details': {
        'module_quantity': 20,
        'selected_module_name': 'Neostar 2S+ 455W',
        'selected_inverter_name': 'Sun2000 10KTL-M1 10 kW Wechselrichter',
        'selected_storage_name': 'ECS4100 -H3 12,09 kWh Stromspeicher',
        'include_storage': True,
    },
}

res = build_dynamic_data(project_data, analysis_results={})

keys = [
    'module_manufacturer',
    'module_model',
    'module_power_per_panel_watt',
    'module_cell_technology',
    'module_structure',
    'module_cell_type',
    'module_version',
    'module_guarantee_combined',
    'inverter_manufacturer',
    'inverter_model',
    'inverter_power_watt',
    'inverter_type',
    'inverter_phases',
    'inverter_shading_management',
    'inverter_backup_capable',
    'inverter_smart_home_integration',
    'inverter_guarantee_text',
    'storage_manufacturer',
    'storage_model',
    'storage_capacity_kwh',
    'storage_cell_technology',
    'storage_extension_module_size_kwh',
    'storage_max_size_kwh',
    'storage_outdoor_capability',
    'storage_warranty_text']

for k in keys:
    print(f"{k}: {res.get(k)}")
