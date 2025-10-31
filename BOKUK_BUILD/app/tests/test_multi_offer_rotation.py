"""
Test-Skript zur Verifizierung der Multi-Offer Produktrotation
Zeigt an, welche Produkte für jede Firma ausgewählt werden würden
"""

import logging
from multi_offer_generator import MultiCompanyOfferGenerator

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)


def test_product_rotation():
    """Testet die Produktrotation für mehrere Firmen"""

    print("\n" + "=" * 80)
    print("TEST: Multi-Offer Produktrotation")
    print("=" * 80 + "\n")

    # Generator initialisieren
    generator = MultiCompanyOfferGenerator()

    # Produkte laden
    products = generator.load_all_products()

    print(f"📦 Verfügbare Produkte in Datenbank:")
    print(f"  • Module: {len(products.get('module', []))} Stück")
    print(f"  • Wechselrichter: {len(products.get('inverter', []))} Stück")
    print(f"  • Speicher: {len(products.get('storage', []))} Stück")
    print()

    # Beispiel-Einstellungen mit Rotation aktiviert
    base_settings = {
        "enable_product_rotation": True,
        "rotation_mode": "linear",
        "product_rotation_step": 1,
        "module_rotation_step": 1,
        "inverter_rotation_step": 1,
        "storage_rotation_step": 1,
        "include_storage": True,
        "price_increment_percent": 5,  # 5% Preissteigerung pro Firma
        "price_calculation_mode": "linear"
    }

    # Basisprodukte setzen (erste Produkte aus jeder Kategorie)
    if products.get('module'):
        base_settings['selected_module_id'] = products['module'][0].get('id')
        print(
            f"🔹 Basis-Modul: {
                products['module'][0].get('model_name')} (Marke: {
                products['module'][0].get('brand')})")

    if products.get('inverter'):
        base_settings['selected_inverter_id'] = products['inverter'][0].get(
            'id')
        print(
            f"🔹 Basis-Wechselrichter: {
                products['inverter'][0].get('model_name')} (Marke: {
                products['inverter'][0].get('brand')})")

    if products.get('storage'):
        base_settings['selected_storage_id'] = products['storage'][0].get('id')
        print(
            f"🔹 Basis-Speicher: {
                products['storage'][0].get('model_name')} (Marke: {
                products['storage'][0].get('brand')})")

    print("\n" + "-" * 80)
    print("PRODUKTROTATION FÜR 5 FIRMEN (Beispiel)")
    print("-" * 80 + "\n")

    # Rotation für 5 Firmen simulieren
    for company_idx in range(5):
        print(f"\n{'=' * 60}")
        print(f"FIRMA {company_idx + 1}")
        print(f"{'=' * 60}")

        # Rotierte Produkte abrufen
        rotated_settings = generator.get_rotated_products_for_company(
            company_idx, base_settings)

        # Produktdetails anzeigen
        print("\n📦 Ausgewählte Produkte:")

        for category, id_key in [
            ("module", "selected_module_id"),
            ("inverter", "selected_inverter_id"),
            ("storage", "selected_storage_id")
        ]:
            product_id = rotated_settings.get(id_key)
            if product_id and products.get(category):
                # Produkt in Liste finden
                product = next(
                    (p for p in products[category] if p.get('id') == product_id), None)
                if product:
                    category_name = {
                        "module": "Modul",
                        "inverter": "Wechselrichter",
                        "storage": "Speicher"}[category]
                    brand = product.get('brand') or product.get(
                        'manufacturer', '?')
                    model = product.get('model_name', 'Unbekannt')

                    # Kapazität/Leistung
                    if category == "module":
                        capacity = product.get('capacity_w', 0)
                        unit = "W"
                    elif category == "inverter":
                        capacity = product.get('power_kw', 0)
                        unit = "kW"
                    else:  # storage
                        capacity = product.get('max_kwh_capacity', 0)
                        unit = "kWh"

                    print(
                        f"  • {
                            category_name:15} → {
                            brand:20} | {
                            model:30} | {capacity} {unit}")
                else:
                    print(
                        f"  • {
                            category:15} → FEHLER: Produkt ID {product_id} nicht gefunden!")

    print("\n" + "=" * 80)
    print("✓ Test abgeschlossen")
    print("=" * 80 + "\n")

    # Rotationsstatus anzeigen
    print("\n📊 Rotationsstatus (verwendet IDs):")
    for category, state in generator.rotation_state.items():
        used_ids = state.get('used_ids', [])
        print(f"  • {category}: {len(used_ids)} Produkt(e) verwendet")

    print("\n💡 HINWEIS:")
    print("  - Jede Firma sollte UNTERSCHIEDLICHE Produkte haben")
    print("  - Wenn keine neuen Produkte verfügbar, wird das letzte wiederholt")
    print("  - Preise werden zusätzlich um 5% pro Firma gesteigert\n")


if __name__ == "__main__":
    test_product_rotation()
