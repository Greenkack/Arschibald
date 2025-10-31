#!/usr/bin/env python3
"""
Test um zu sehen, was für Solarfabrik in der Datenbank verfügbar ist
"""


def test_solarfabrik_database():
    print('=== SOLARFABRIK DATENBANK TEST ===')

    try:
        # Importiere die DB-Funktionen
        from product_attributes import get_attribute_value, list_attributes
        from product_db import (
            get_product_by_model_name,
            get_product_id_by_model_name,
            list_products,
        )

        # Suche nach Solarfabrik-Produkten
        print("1. Suche nach Solarfabrik-Produkten...")
        all_products = list_products()
        solarfabrik_products = []

        for product in all_products:
            if product and isinstance(product, dict):
                name = str(product.get('model_name', '')).lower()
                brand = str(product.get('brand', '')).lower()
                if 'solarfabrik' in name or 'solarfabrik' in brand:
                    solarfabrik_products.append(product)

        print(f"Gefundene Solarfabrik-Produkte: {len(solarfabrik_products)}")

        if solarfabrik_products:
            # Nimm das erste Solarfabrik-Produkt als Beispiel
            example_product = solarfabrik_products[0]
            print(
                f"\\nBeispiel-Produkt: {example_product.get('model_name', 'Unknown')}")
            print(f"Produkt-ID: {example_product.get('id', 'Unknown')}")

            # Zeige alle verfügbaren Felder
            print("\\n2. Verfügbare Felder im Produkt:")
            for key, value in example_product.items():
                if value not in (None, ""):
                    print(f"  {key}: {value}")

            # Teste Attribute-Tabelle
            product_id = example_product.get('id')
            if product_id:
                print(
                    f"\\n3. Attribute aus Attribute-Tabelle für ID {product_id}:")
                try:
                    all_attrs = list_attributes(product_id)
                    print(f"Verfügbare Attribute: {all_attrs}")

                    # Teste spezifische Attribute
                    test_attributes = [
                        'cell_technology',
                        'technology',
                        'pv_cell_technology',
                        'zelltechnologie',
                        'module_structure',
                        'structure',
                        'modulaufbau',
                        'aufbau',
                        'cell_type',
                        'cells',
                        'zelltyp',
                        'solarzellen',
                        'version',
                        'series',
                        'generation']

                    found_attrs = {}
                    for attr in test_attributes:
                        value = get_attribute_value(product_id, attr)
                        if value not in (None, ""):
                            found_attrs[attr] = value

                    if found_attrs:
                        print("Gefundene Attribute-Werte:")
                        for attr, value in found_attrs.items():
                            print(f"  {attr}: {value}")
                    else:
                        print("Keine Attribute-Werte gefunden")

                except Exception as e:
                    print(f"Fehler beim Laden der Attribute: {e}")
        else:
            print("Keine Solarfabrik-Produkte in der Datenbank gefunden")

    except ImportError as e:
        print(f"Import-Fehler: {e}")
        print("Datenbank-Module nicht verfügbar")
    except Exception as e:
        print(f"Fehler: {e}")


if __name__ == "__main__":
    test_solarfabrik_database()
    print()
    print("🔍 NÄCHSTE SCHRITTE:")
    print("1. Führe diesen Test aus, um zu sehen, was in der DB verfügbar ist")
    print("2. Schaue dir die Debug-Ausgaben in der PDF-Generierung an")
    print("3. Verwende die echten DB-Werte statt Hardcoded-Fallbacks")
