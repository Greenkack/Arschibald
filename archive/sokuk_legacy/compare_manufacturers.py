#!/usr/bin/env python3
"""
Vergleiche Hersteller-Daten in der Datenbank
"""

import sys

sys.path.append('.')

try:
    from product_db import get_products_with_dynamic_keys

    # Hole alle Produkte und schaue, wie andere Hersteller ihre Daten haben
    print('=== VERGLEICH: ANDERE HERSTELLER vs SOLARFABRIK ===')
    products = get_products_with_dynamic_keys()

    # Gruppiere nach Hersteller
    by_manufacturer = {}
    for product in products:
        manufacturer = product.get('manufacturer', 'Unbekannt')
        if manufacturer not in by_manufacturer:
            by_manufacturer[manufacturer] = []
        by_manufacturer[manufacturer].append(product)

    # Zeige Beispiele von verschiedenen Herstellern
    for manufacturer, products_list in by_manufacturer.items():
        if products_list:  # Nur wenn Produkte vorhanden
            example = products_list[0]  # Erstes Produkt als Beispiel
            print(f'\n=== {manufacturer.upper()} ===')
            print(f'Produkt: {example.get("model_name", "k.A.")}')
            print(
                f'  cell_technology: "{
                    example.get(
                        "cell_technology",
                        "LEER")}"')
            print(
                f'  module_structure: "{
                    example.get(
                        "module_structure",
                        "LEER")}"')
            print(f'  cell_type: "{example.get("cell_type", "LEER")}"')
            print(f'  version: "{example.get("version", "LEER")}"')

            # Zeige auch andere relevante Felder
            other_fields = [
                'efficiency_percent',
                'warranty_years',
                'capacity_w']
            for field in other_fields:
                value = example.get(field)
                if value is not None:
                    print(f'  {field}: {value}')

        if len(by_manufacturer) > 5:  # Begrenze Ausgabe
            break

except Exception as e:
    print(f'Fehler: {e}')
    import traceback
    traceback.print_exc()
