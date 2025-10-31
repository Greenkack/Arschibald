#!/usr/bin/env python3
"""
Aktualisiert Solarfabrik-Produkte um die gleichen Werte wie TrinaSolar zu haben
"""

from product_db import get_products_with_dynamic_keys, update_product


def fix_solarfabrik_values():
    """Aktualisiert Solarfabrik um die gleichen Werte wie TrinaSolar zu haben"""

    print('=== SOLARFABRIK WERTE ANPASSEN ===')

    products = get_products_with_dynamic_keys()

    # Hole TrinaSolar-Referenzwerte
    trina_products = [
        p for p in products if p.get('manufacturer') and 'trina' in p.get(
            'manufacturer', '').lower()]
    if not trina_products:
        print("❌ Keine TrinaSolar-Produkte gefunden!")
        return False

    # Verwende die Werte vom ersten TrinaSolar-Produkt als Referenz
    reference_product = trina_products[0]
    reference_values = {
        'cell_technology': reference_product.get('cell_technology'),
        'module_structure': reference_product.get('module_structure'),
        'cell_type': reference_product.get('cell_type'),
        'version': reference_product.get('version')
    }

    print(
        f"📋 Referenz-Werte von TrinaSolar '{reference_product.get('model_name')}':")
    for key, value in reference_values.items():
        print(f"   {key}: {value}")

    # Hole alle Solarfabrik-Produkte
    solarfabrik_products = [p for p in products if p.get(
        'manufacturer') and 'solarfabrik' in p.get('manufacturer', '').lower()]

    print(
        f"\\n🔧 Aktualisiere {
            len(solarfabrik_products)} Solarfabrik-Produkte...")

    success_count = 0
    for product in solarfabrik_products:
        product_id = product.get('id')
        product_name = product.get('model_name')

        print(f"\\n📦 Aktualisiere: {product_name} (ID: {product_id})")

        # Zeige alte Werte
        print("   Alte Werte:")
        print(f"     cell_technology: {product.get('cell_technology')}")
        print(f"     module_structure: {product.get('module_structure')}")
        print(f"     cell_type: {product.get('cell_type')}")
        print(f"     version: {product.get('version')}")

        try:
            # Aktualisiere mit TrinaSolar-Werten
            success = update_product(product_id, reference_values)

            if success:
                print("   ✅ Erfolgreich aktualisiert!")
                success_count += 1
            else:
                print("   ❌ Aktualisierung fehlgeschlagen!")

        except Exception as e:
            print(f"   ❌ Fehler: {e}")

    print(
        f"\\n🎉 {success_count}/{
            len(solarfabrik_products)} Solarfabrik-Produkte erfolgreich aktualisiert!")

    return success_count == len(solarfabrik_products)


def verify_solarfabrik_values():
    """Überprüft ob Solarfabrik jetzt die gleichen Werte wie TrinaSolar hat"""

    print("\\n🔍 VERIFIKATION: Solarfabrik-Werte nach Update")
    print("=" * 50)

    products = get_products_with_dynamic_keys()

    # Hole TrinaSolar-Referenzwerte
    trina_products = [
        p for p in products if p.get('manufacturer') and 'trina' in p.get(
            'manufacturer', '').lower()]
    reference_product = trina_products[0] if trina_products else None

    if not reference_product:
        print("❌ Keine TrinaSolar-Referenz gefunden!")
        return False

    # Hole Solarfabrik-Produkte
    solarfabrik_products = [p for p in products if p.get(
        'manufacturer') and 'solarfabrik' in p.get('manufacturer', '').lower()]

    print(f"📋 TrinaSolar Referenz: {reference_product.get('model_name')}")
    print(f"   cell_technology: {reference_product.get('cell_technology')}")
    print(f"   module_structure: {reference_product.get('module_structure')}")
    print(f"   cell_type: {reference_product.get('cell_type')}")
    print(f"   version: {reference_product.get('version')}")

    all_match = True
    for product in solarfabrik_products:
        print(f"\\n📦 Solarfabrik: {product.get('model_name')}")

        matches = {
            'cell_technology': product.get('cell_technology') == reference_product.get('cell_technology'),
            'module_structure': product.get('module_structure') == reference_product.get('module_structure'),
            'cell_type': product.get('cell_type') == reference_product.get('cell_type'),
            'version': product.get('version') == reference_product.get('version')}

        for key, matches_ref in matches.items():
            status = "✅" if matches_ref else "❌"
            print(f"   {key}: {product.get(key)} {status}")
            if not matches_ref:
                all_match = False

    if all_match:
        print(
            "\\n🎉 Alle Solarfabrik-Produkte haben jetzt die gleichen Werte wie TrinaSolar!")
    else:
        print("\\n❌ Einige Solarfabrik-Produkte haben noch abweichende Werte!")

    return all_match


if __name__ == "__main__":
    print("🚀 Solarfabrik-Werte an TrinaSolar anpassen")
    print("=" * 60)

    # Schritt 1: Aktualisiere Solarfabrik-Werte
    success = fix_solarfabrik_values()

    if success:
        # Schritt 2: Verifikation
        verify_solarfabrik_values()
    else:
        print("❌ Aktualisierung fehlgeschlagen!")

    print("\\n✅ Jetzt sollte Solarfabrik in der PDF die gleichen Werte wie TrinaSolar anzeigen!")
