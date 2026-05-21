#!/usr/bin/env python3
"""
Überprüft die Werte verschiedener Hersteller für Module
"""

from product_db import list_products


def check_manufacturer_values():
    """Überprüft die Werte verschiedener Hersteller"""

    products = list_products(category="Modul")

    # Suche nach verschiedenen Herstellern
    manufacturers = [
        'trina',
        'viessmann',
        'solarfabrik',
        'jinko',
        'longi',
        'canadian']

    for manufacturer in manufacturers:
        print(f"\n=== {manufacturer.upper()} PRODUKTE ===")

        matching_products = [
            p for p in products
            if manufacturer.lower() in p.get('brand', '').lower()
            or manufacturer.lower() in p.get('model_name', '').lower()
        ]

        if matching_products:
            for i, product in enumerate(matching_products[:3]):  # Nur erste 3
                print(
                    f"  {
                        i +
                        1}. {
                        product.get(
                            'brand',
                            'N/A')} - {
                        product.get(
                            'model_name',
                            'N/A')}")
                print(
                    f"     Zellentechnologie: {
                        product.get(
                            'cell_technology',
                            'N/A')}")
                print(
                    f"     Modulaufbau: {
                        product.get(
                            'module_structure',
                            'N/A')}")
                print(f"     Zellentyp: {product.get('cell_type', 'N/A')}")
                print(f"     Version: {product.get('version', 'N/A')}")
                print()
        else:
            print("  Keine Produkte gefunden")


if __name__ == "__main__":
    check_manufacturer_values()
