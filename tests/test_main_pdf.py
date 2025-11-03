# Ensure repo root is on path
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from pdf_generator import generate_offer_pdf

# Try to import helpers from project
try:
    from database import get_active_company
    from database import list_company_documents as db_list_company_documents_func
    from database import load_admin_setting as load_admin_setting_func
    from database import save_admin_setting as save_admin_setting_func
except Exception:
    def load_admin_setting_func(key, default=None):
        return default
    def save_admin_setting_func(key, value):
        return True
    def db_list_company_documents_func(company_id, doc_type=None):
        return []
    def get_active_company():
        return None

try:
    from product_db import get_product_by_id as get_product_by_id_func
    from product_db import list_products as list_products_func
except Exception:
    def list_products_func(*args, **kwargs): return []
    def get_product_by_id_func(*args, **kwargs): return None

import json

texts = {}
try:
    de_path = root / 'de.json'
    if de_path.exists():
        texts = json.loads(de_path.read_text(encoding='utf-8'))
except Exception:
    pass

# Minimal project data
project_data = {
    'customer_data': {
        'salutation': 'Herr',
        'first_name': 'Max',
        'last_name': 'Mustermann',
        'address': 'Musterstraße',
        'house_number': '1',
        'zip_code': '12345',
        'city': 'Musterstadt',
        'email': 'max@example.com',
        'phone_mobile': '0151 2345678',
    },
    'project_details': {
        'module_quantity': 20,
        'selected_module_capacity_w': 420,
        'selected_module_name': 'PV-Modul 420W',
        'selected_inverter_name': 'WR 5kW',
        'selected_storage_capacity_kwh': 5.1,
    }
}

analysis_results = {
    'anlage_kwp': 8.4,
    'annual_pv_production_kwh': 8252,
    'self_supply_rate_percent': 54,
    'self_consumption_percent': 42,
    'total_investment_netto': 14950.0,
}

active_company = get_active_company() or {}
company_info = active_company or {
    'name': 'DING Solar GmbH',
    'short_name': 'DING',
    'street': 'Sonnenweg 1',
    'zip_code': '20095',
    'city': 'Hamburg',
    'phone': '+49 40 123456',
    'email': 'info@ding-solar.de',
    'website': 'https://ding-solar.de',
}

inclusion_options = {
    'include_company_logo': True,
    'include_product_images': False,
    'include_all_documents': False,
}

pdf_bytes = generate_offer_pdf(
    project_data=project_data,
    analysis_results=analysis_results,
    company_info=company_info,
    company_logo_base64=company_info.get('logo_base64'),
    selected_title_image_b64=None,
    selected_offer_title_text='Angebot für Ihre Photovoltaikanlage',
    selected_cover_letter_text='Sehr geehrte Damen und Herren,\n\nHerzlichen Dank für Ihre Anfrage.',
    sections_to_include=None,
    inclusion_options=inclusion_options,
    load_admin_setting_func=load_admin_setting_func,
    save_admin_setting_func=save_admin_setting_func,
    list_products_func=list_products_func,
    get_product_by_id_func=get_product_by_id_func,
    db_list_company_documents_func=db_list_company_documents_func,
    active_company_id=active_company.get('id') if active_company else None,
    texts=texts,
    use_modern_design=True,
)

out = root / 'out_main_full_test.pdf'
if pdf_bytes:
    out.write_bytes(pdf_bytes)
    print(f'OK: wrote {out} ({len(pdf_bytes)} bytes)')
else:
    print('FAIL: no pdf bytes')
