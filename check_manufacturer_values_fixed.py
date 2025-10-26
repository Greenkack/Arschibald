#!/usr/bin/env python3
"""
Vergleiche die Werte zwischen verschiedenen Herstellern
"""

from product_db import get_products_with_dynamic_keys


def compare_manufacturer_values():
    products = get_products_with_dynamic_keys()

    # Finde TrinaSolar und Viessmann Produkte
    trina_products = [
        p for p in products if p.get('manufacturer') and 'trina' in p.get(
            'manufacturer', '').lower()]
    viessmann_products = [p for p in products if p.get(
        'manufacturer') and 'viessmann' in p.get('manufacturer', '').lower()]
    solarfabrik_products = [p for p in products if p.get(
        'manufacturer') and 'solarfabrik' in p.get('manufacturer', '').lower()]

    print('=== TRINASOLAR WERTE ===')
    for p in trina_products[:2]:
        print(f'Produkt: {p.get("model_name")}')
        print(f'  cell_technology: {p.get("cell_technology")}')
        print(f'  module_structure: {p.get("module_structure")}')
        print(f'  cell_type: {p.get("cell_type")}')
        print(f'  version: {p.get("version")}')
        print()

    print('=== VIESSMANN WERTE ===')
    for p in viessmann_products[:2]:
        print(f'Produkt: {p.get("model_name")}')
        print(f'  cell_technology: {p.get("cell_technology")}')
        print(f'  module_structure: {p.get("module_structure")}')
        print(f'  cell_type: {p.get("cell_type")}')
        print(f'  version: {p.get("version")}')
        print()

    print('=== SOLARFABRIK AKTUELLE WERTE ===')
    for p in solarfabrik_products[:2]:
        print(f'Produkt: {p.get("model_name")}')
        print(f'  cell_technology: {p.get("cell_technology")}')
        print(f'  module_structure: {p.get("module_structure")}')
        print(f'  cell_type: {p.get("cell_type")}')
        print(f'  version: {p.get("version")}')
        print()


if __name__ == "__main__":
    compare_manufacturer_values()
