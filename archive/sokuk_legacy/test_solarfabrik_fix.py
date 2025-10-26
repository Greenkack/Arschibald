#!/usr/bin/env python3
"""
Test the corrected Solarfabrik data
"""

import sys

sys.path.append('.')

try:
    from product_db import get_products_with_dynamic_keys

    # Teste die korrigierten Solarfabrik-Daten
    print('=== KORRIGIERTE SOLARFABRIK DATEN ===')
    products = get_products_with_dynamic_keys()
    solarfabrik_products = [p for p in products if p.get(
        'manufacturer') and 'solarfabrik' in p.get('manufacturer', '').lower()]

    for product in solarfabrik_products[:2]:  # Nur erste 2 zeigen
        print(f'Produkt: {product["model_name"]}')
        print(f'  Zelltechnologie: {product.get("cell_technology", "k.A.")}')
        print(f'  Modulaufbau: {product.get("module_structure", "k.A.")}')
        print(f'  Zelltyp: {product.get("cell_type", "k.A.")}')
        print(f'  Version: {product.get("version", "k.A.")}')
        print()

except Exception as e:
    print(f'Fehler: {e}')
    import traceback
    traceback.print_exc()
