#!/usr/bin/env python3
"""
Fix Solarfabrik product data in database
"""

import sys

sys.path.append('.')

try:
    from product_db import get_products_with_dynamic_keys, update_product

    # Hole alle Solarfabrik-Produkte
    print('=== SOLARFABRIK PRODUKTE ===')
    products = get_products_with_dynamic_keys()
    solarfabrik_products = [p for p in products if p.get(
        'manufacturer') and 'solarfabrik' in p.get('manufacturer', '').lower()]

    print(f'Gefunden: {len(solarfabrik_products)} Solarfabrik-Produkte')

    for product in solarfabrik_products:
        print(
            f'ID: {
                product["id"]}, Name: {
                product["model_name"]}, Hersteller: {
                product["manufacturer"]}')
        print(f'  cell_technology: {product.get("cell_technology", "LEER")}')
        print(f'  module_structure: {product.get("module_structure", "LEER")}')
        print(f'  cell_type: {product.get("cell_type", "LEER")}')
        print()

        # Korrigiere die Daten
        update_data = {
            'cell_technology': 'Monokristallin',
            'module_structure': 'Glas-Folie',
            'cell_type': 'Monokristalline Siliziumzellen',
            'version': 'Standard'
        }

        result = update_product(product['id'], update_data)
        print(
            f'Update für ID {
                product["id"]}: {
                "✅ Erfolg" if result else "❌ Fehler"}')
        print()

except Exception as e:
    print(f'Fehler: {e}')
    import traceback
    traceback.print_exc()
