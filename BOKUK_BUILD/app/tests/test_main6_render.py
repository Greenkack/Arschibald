import pdf_generator as pg
import sys
from pathlib import Path

# Ensure project root is on sys.path so imports from parent work
CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


project_data = {
    'customer_data': {
        'salutation': 'Herr',
        'title': '',
        'first_name': 'Max',
        'last_name': 'Mustermann',
        'address': 'Musterweg',
        'house_number': '12',
        'zip_code': '12345',
        'city': 'Musterstadt',
        'phone_mobile': '+491234567',
        'email': 'max@example.com',
    },
    'project_details': {
        'module_quantity': 20,
        'selected_module_capacity_w': 420,
        'module_manufacturer': 'JA Solar',
        'module_model': 'JAM54S31-420/MR',
        'module_cell_technology': 'Monokristallin N-Type',
        'module_structure': 'Glas-Folie',
        'module_cell_type': '108 Halbzellen',
        'module_version': 'Black Frame',
        'module_guarantee_combined': '25 Jahre Produktgarantie | 30 Jahre Leistungsgarantie',
        'selected_inverter_name': 'Huawei SUN2000-8KTL-M1',
        'selected_inverter_quantity': 1,
        'selected_inverter_power_kw': 8,
        'selected_storage_name': 'Huawei LUNA2000-7-S1-7kWh Stromspeicher',
        'include_storage': True,
        # Seite 3: Stromkosten (Monat) und Preissteigerung
        'stromkosten_haushalt_euro_monat': 150,
        'stromkosten_heizung_euro_monat': 50,
        'electricity_price_increase_annual_percent': 5,
    },
}

analysis_results = {
    'annual_pv_production_kwh': 8251.92,
    'self_supply_rate_percent': 54,
    'self_consumption_percent': 42,
    # Für Validierung/KPIs
    'total_investment_netto': 19999.99,
    'final_price': 19999.99,
}

company_info = {
    'name': 'Muster Solar GmbH',
    'street': 'Hauptstraße 1',
    'zip_code': '98765',
    'city': 'Solingen',
    'phone': '+49 555 123',
    'email': 'info@mustersolar.de',
    'website': 'https://mustersolar.de',
}


# Für Validierung: Firmendaten in project_data injizieren
project_data['company_information'] = company_info

# Render 6-Seiten-Hauptausgabe
out = pg.generate_main_template_pdf_bytes(
    project_data, analysis_results, company_info)
out_path = Path('test_main6.pdf')
if out:
    out_path.write_bytes(out)
    print('OK bytes:', len(out))
    print('Wrote:', str(out_path.resolve()))
else:
    print('Failed: no bytes')
