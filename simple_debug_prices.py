#!/usr/bin/env python3
"""
SIMPLER DEBUG: Verfolge Preis-Uebergabe ohne Emojis
"""

from multi_offer_generator import MultiCompanyOfferGenerator
import io
import os
import sys

# UTF-8 Output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


print("\n" + "=" * 80)
print("DEEP DEBUG: Multi-PDF Preis-Flow")
print("=" * 80)

generator = MultiCompanyOfferGenerator()

base_settings = {
    "enable_product_rotation": True,
    "price_increment_percent": 5.0,
    "price_calculation_mode": "linear",
}

base_calc_results = {
    'total_investment_netto': 20000.0,
    'total_investment_brutto': 23800.0,
    'final_price_net': 20000.0,
}

print("\nBASIS-PREIS: 20.000 EUR")
print("ERWARTET Firma 2: 21.000 EUR (+5%)")
print("=" * 80)

# Teste Firma 2
company_index = 1

print("\n1. apply_price_scaling()")
scaled = generator.apply_price_scaling(
    company_index,
    base_settings,
    base_calc_results.copy())
print(f"   total_investment_netto: {scaled.get('total_investment_netto')}")
print(f"   final_price_net: {scaled.get('final_price_net')}")

print("\n2. Was wuerde in project_details geschrieben:")
net_price = scaled.get('final_price_net') or scaled.get(
    'total_investment_netto')
print(f"   final_offer_price_net: {net_price}")
print(f"   final_price_with_provision: {net_price}")

print("\n3. Test: Rufe build_dynamic_data DIREKT auf")

# Simuliere project_data wie in multi_offer_generator
project_details = {
    'final_offer_price_net': net_price,
    'final_price_with_provision': net_price,
    'final_price_net': net_price,
    'final_price_netto': net_price,
}

pdf_project_data = {
    'project_details': project_details,
    'customer_data': {
        'first_name': 'Test',
        'last_name': 'User'
    }
}

print("\n   Uebergebe an build_dynamic_data:")
print(
    f"   project_data['project_details']['final_offer_price_net'] = {net_price}")

try:
    from pdf_template_engine.placeholders import build_dynamic_data

    result = build_dynamic_data(pdf_project_data, scaled, {})

    print("\n4. Ergebnis von build_dynamic_data:")
    print(
        f"   final_end_preis_formatted: {
            result.get(
                'final_end_preis_formatted',
                'FEHLT')}")
    print(
        f"   zwischensumme_preis_formatted: {
            result.get(
                'zwischensumme_preis_formatted',
                'FEHLT')}")

    final = result.get('final_end_preis_formatted', '')

    print("\n" + "=" * 80)
    print("RESULTAT:")
    print("=" * 80)
    print("Erwartet: 21.000,00 EUR")
    print(f"Erhalten: {final}")

    # Prüfe ob richtig
    if '21' in str(final) and '000' in str(final):
        print("\nSUCCESS! Preis ist skaliert!")
    elif '20' in str(final) and '000' in str(final):
        print("\nFEHLER! Preis ist NICHT skaliert (zeigt 20.000 statt 21.000)")
        print("\nDas Problem:")
        print(f"1. Preisstaffelung funktioniert: {net_price} EUR")
        print(
            f"2. Wir uebergeben: project_details['final_offer_price_net'] = {net_price}")
        print(f"3. Aber Ergebnis zeigt: {final}")
        print("\nMOEGLICHE URSACHEN:")
        print("a) placeholders.py ignoriert project_details komplett")
        print("b) placeholders.py nutzt analysis_results statt project_details")
        print("c) Der Wert wird spaeter ueberschrieben")
        print("d) _alias_value() findet den Wert nicht in der richtigen Reihenfolge")
    else:
        print(f"\nUNKLAR - Preis hat unerwartetes Format: {final}")

except Exception as e:
    print(f"\nFEHLER beim Aufruf: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
