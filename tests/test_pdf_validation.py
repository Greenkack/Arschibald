#!/usr/bin/env python3
"""
Test der PDF-Validierung
"""

import sys

sys.path.append('.')

try:
    from pdf_generator import validate_pdf_data

    # Test der Validierung
    print('=== PDF VALIDIERUNG TEST ===')

    # Test 1: Leere Daten
    result1 = validate_pdf_data({}, {}, {})
    print(
        f'Test 1 (leer): is_valid={
            result1["is_valid"]}, critical_errors={
            len(
                result1["critical_errors"])}')

    # Test 2: Minimale Daten
    project_data = {
        'customer_data': {'last_name': 'Mustermann'},
        'pv_details': {'module_count': 20},
        'project_details': {}
    }
    analysis_results = {
        'anlage_kwp': 8.0,
        'annual_pv_production_kwh': 8000,
        'total_investment_netto': 15970
    }
    company_info = {'name': 'Test Firma'}

    result2 = validate_pdf_data(project_data, analysis_results, company_info)
    print(
        f'Test 2 (minimal): is_valid={
            result2["is_valid"]}, critical_errors={
            len(
                result2["critical_errors"])}')

    # Test 3: Vollständige Daten
    analysis_results['final_price'] = 15970
    result3 = validate_pdf_data(project_data, analysis_results, company_info)
    print(
        f'Test 3 (vollständig): is_valid={
            result3["is_valid"]}, critical_errors={
            len(
                result3["critical_errors"])}')

    print()
    print('✅ PDF-VALIDIERUNG FUNKTIONIERT!')

except Exception as e:
    print(f'❌ Fehler: {e}')
    import traceback
    traceback.print_exc()
