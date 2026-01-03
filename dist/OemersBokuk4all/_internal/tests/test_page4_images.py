import os

from pdf_generator import generate_main_template_pdf_bytes

# 1x1 PNG (transparent) als Base64
png_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGMAAQAABQABDQottAAAAABJRU5ErkJggg=="

project_data = {
    'customer_data': {'first_name': 'Test', 'last_name': 'Kunde'},
    'project_details': {
        'module_quantity': 12,
        'selected_module_capacity_w': 460,
        'module_cell_technology': 'N-Type TOPCon Halfcut Bifazial',
        'module_structure': 'Glas-Glas Module',
        'module_cell_type': 'Monokristalline',
        'module_version': 'All-Black',
        'module_guarantee_combined': '30 Jahre Produktgarantie',
        # Bild-Overrides (wir akzeptieren Base64 direkt)
        'module_image_b64': png_b64,
        'inverter_image_b64': png_b64,
        'storage_image_b64': png_b64,
        # Modellnamen optional (DB wird u. U. nicht benötigt, da wir Overrides
        # setzen)
        'selected_inverter_name': 'Sun2000 10KTL-M1 10 kW',
        'selected_inverter_power_kw': 10,
        'selected_inverter_quantity': 1,
        'selected_storage_name': 'LUNA2000-7-S1-7kWh Stromspeicher',
        'selected_storage_storage_power_kw': 7.0,
        'selected_storage_power_kw': 7.0,
    }
}
analysis_results = {
    'total_investment_netto': 12345.67,
    'annual_pv_production_kwh': 5000,
    'annual_consumption_kwh': 4000,
    'storage_dod_percent': 80,
    'storage_cycles': 5000}
company_info = {'name': 'ACME GmbH'}

pdf = generate_main_template_pdf_bytes(
    project_data,
    analysis_results,
    company_info,
    additional_pdf=None)
print('main6 bytes', None if pdf is None else len(pdf))
out = 'test_page4_images.pdf'
open(out, 'wb').write(pdf)
print('wrote', out, os.path.getsize(out))
