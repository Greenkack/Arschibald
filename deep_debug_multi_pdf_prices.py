#!/usr/bin/env python3
"""
TIEFES DEBUG: Verfolge JEDEN Schritt der Preis-Übergabe
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Monkey-Patch placeholders.py um zu sehen was wirklich übergeben wird
original_build_dynamic_data = None

def debug_build_dynamic_data(project_data, analysis_results, company_info=None):
    """Wrapper um zu sehen was übergeben wird"""
    print(f"\n{'='*80}")
    print(f"🔍 build_dynamic_data() AUFGERUFEN")
    print(f"{'='*80}")
    
    # Prüfe project_data
    if project_data and isinstance(project_data, dict):
        project_details = project_data.get('project_details', {})
        print(f"\n📦 project_data['project_details']:")
        
        price_keys = [
            'final_offer_price_net',
            'final_price_with_provision',
            'final_price_net',
            'final_price_netto',
            'total_investment_netto',
        ]
        
        for key in price_keys:
            value = project_details.get(key)
            if value:
                print(f"   ✅ {key}: {value}")
            else:
                print(f"   ❌ {key}: FEHLT")
    else:
        print(f"\n❌ project_data ist leer oder kein Dict!")
    
    # Prüfe analysis_results
    if analysis_results and isinstance(analysis_results, dict):
        print(f"\n📊 analysis_results:")
        
        price_keys = [
            'total_investment_netto',
            'total_investment_brutto',
            'final_price_net',
            'final_price',
        ]
        
        for key in price_keys:
            value = analysis_results.get(key)
            if value:
                print(f"   ✅ {key}: {value}")
            else:
                print(f"   ❌ {key}: FEHLT")
    else:
        print(f"\n❌ analysis_results ist leer oder kein Dict!")
    
    print(f"\n{'='*80}")
    
    # Rufe die originale Funktion auf
    return original_build_dynamic_data(project_data, analysis_results, company_info)


# Patche die Funktion
try:
    from pdf_template_engine import placeholders
    original_build_dynamic_data = placeholders.build_dynamic_data
    placeholders.build_dynamic_data = debug_build_dynamic_data
    print("[OK] placeholders.build_dynamic_data gepatched!")
except Exception as e:
    print(f"[FEHLER] Konnte nicht patchen: {e}")

# Jetzt teste mit echtem Multi-Offer-Generator
from multi_offer_generator import MultiCompanyOfferGenerator
import streamlit as st

# Initialisiere Session State
if not hasattr(st, 'session_state'):
    class MockSessionState:
        def __getstate__(self):
            """Ermöglicht Pickle-Serialisierung für Session State"""
            return self.__dict__.copy()
        
        def __setstate__(self, state):
            """Ermöglicht Pickle-Deserialisierung für Session State"""
            self.__dict__.update(state)
        
        def __init__(self):
            self._data = {}
        def get(self, key, default=None):
            return self._data.get(key, default)
        def __setitem__(self, key, value):
            self._data[key] = value
        def __getitem__(self, key):
            return self._data[key]
        def __contains__(self, key):
            return key in self._data
    st.session_state = MockSessionState()

# Simuliere Multi-PDF Generierung
generator = MultiCompanyOfferGenerator()

base_settings = {
    "enable_product_rotation": True,
    "price_increment_percent": 5.0,
    "price_calculation_mode": "linear",
    "module_quantity": 20,
}

# Simuliere Kundendaten
customer_data = {
    "first_name": "Max",
    "last_name": "Mustermann",
    "address": "Teststraße 1",
    "city": "Berlin",
    "zip_code": "10115",
}

# Simuliere Firmendaten
company = {
    "id": 1,
    "name": "Test Firma GmbH",
}

print("\n" + "="*80)
print("🚀 SIMULIERE MULTI-PDF GENERIERUNG")
print("="*80)

# Basis calc_results
base_calc_results = {
    'total_investment_netto': 20000.0,
    'total_investment_brutto': 23800.0,
    'final_price_net': 20000.0,
    'annual_savings': 1500.0,
}

print(f"\n📊 Basis calc_results:")
print(f"   total_investment_netto: {base_calc_results['total_investment_netto']:,.2f} €")

# Teste Firma 2 (sollte +5% haben)
company_index = 1
print(f"\n{'='*80}")
print(f"TESTE FIRMA {company_index + 1} (sollte +5% haben)")
print(f"{'='*80}")

# 1. Preisstaffelung anwenden
print(f"\n1️⃣  Wende Preisstaffelung an...")
scaled_calc_results = generator.apply_price_scaling(company_index, base_settings, base_calc_results.copy())
print(f"   ✅ total_investment_netto: {scaled_calc_results.get('total_investment_netto'):,.2f} €")
print(f"   ✅ final_price_net: {scaled_calc_results.get('final_price_net')}")

# 2. Prepare offer_data (wie in multi_offer_generator.py)
print(f"\n2️⃣  Bereite offer_data vor...")
offer_data = {
    "customer_data": customer_data,
    "company_data": company,
    "offer_date": "19.10.2025",
    "module_quantity": 20,
}

# 3. Setze project_details (wie in multi_offer_generator.py Zeile 1175-1185)
print(f"\n3️⃣  Setze project_details...")
calc_input = {
    "project_details": {
        "module_quantity": 20,
    }
}

net_price = scaled_calc_results.get('final_price_net') or scaled_calc_results.get('total_investment_netto')
gross_price = scaled_calc_results.get('final_price_brutto') or scaled_calc_results.get('total_investment_brutto')

project_details = calc_input.get("project_details", {})
project_details["final_offer_price_net"] = net_price
project_details["final_price_with_provision"] = net_price
project_details["final_price_netto"] = net_price
project_details["final_end_preis"] = net_price
project_details["final_price_brutto"] = gross_price

print(f"   ✅ final_offer_price_net: {net_price:,.2f} €")
print(f"   ✅ final_price_with_provision: {net_price:,.2f} €")
print(f"   ✅ final_price_brutto: {gross_price:,.2f} €")

offer_data["project_details"] = project_details
offer_data["calculation_results"] = scaled_calc_results

# 4. Bereite pdf_project_data vor (wie in multi_offer_generator.py Zeile 1193-1201)
print(f"\n4️⃣  Bereite pdf_project_data vor...")
pdf_project_data = {
    "customer_data": offer_data.get("customer_data", {}),
    "project_details": project_details,
    "calculation_results": scaled_calc_results
}

print(f"   ✅ pdf_project_data erstellt")
print(f"   ✅ pdf_project_data['project_details']['final_offer_price_net']: {pdf_project_data['project_details'].get('final_offer_price_net'):,.2f} €")

# 5. Rufe build_dynamic_data auf
print(f"\n5️⃣  Rufe build_dynamic_data auf...")
print(f"   (Siehe Output oben für Details)")

try:
    result = placeholders.build_dynamic_data(
        pdf_project_data,
        scaled_calc_results,
        company
    )
    
    print(f"\n6️⃣  Ergebnis von build_dynamic_data:")
    
    price_result_keys = [
        'final_end_preis_formatted',
        'zwischensumme_preis_formatted',
        'preis_mit_mwst_formatted',
        'vat_amount_eur',
    ]
    
    for key in price_result_keys:
        value = result.get(key)
        if value:
            print(f"   ✅ {key}: {value}")
        else:
            print(f"   ❌ {key}: FEHLT")
    
    print(f"\n{'='*80}")
    print(f"🎯 FAZIT")
    print(f"{'='*80}")
    
    final_price = result.get('final_end_preis_formatted', 'FEHLT')
    print(f"\nErwarteter Preis: 21.000,00 € (+5%)")
    print(f"Tatsächlicher Preis: {final_price}")
    
    if '21' in str(final_price) or '21000' in str(final_price):
        print(f"\n✅ SUCCESS! Der Preis ist skaliert!")
    else:
        print(f"\n❌ FEHLER! Der Preis ist NICHT skaliert!")
        print(f"\n🔍 ANALYSE:")
        print(f"   1. Preisstaffelung funktioniert: {scaled_calc_results.get('total_investment_netto')} €")
        print(f"   2. project_details gesetzt: {project_details.get('final_offer_price_net')} €")
        print(f"   3. pdf_project_data übergeben: {pdf_project_data['project_details'].get('final_offer_price_net')} €")
        print(f"   4. Aber Ergebnis: {final_price}")
        print(f"\n   → build_dynamic_data() nutzt NICHT die übergebenen project_details!")
        print(f"   → ODER: Die Werte werden später überschrieben!")

except Exception as e:
    print(f"\n❌ FEHLER: {e}")
    import traceback
    traceback.print_exc()
