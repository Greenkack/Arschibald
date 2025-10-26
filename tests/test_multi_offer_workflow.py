"""
VOLLSTÄNDIGER Test der Multi-Offer Pipeline
Simuliert GENAU den Workflow wie in der Streamlit App
"""

import logging
from copy import deepcopy
from multi_offer_generator import MultiCompanyOfferGenerator

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)


def simulate_multi_offer_workflow():
    """Simuliert den kompletten Multi-Offer Workflow"""

    print("\n" + "=" * 80)
    print("VOLLSTÄNDIGER MULTI-OFFER WORKFLOW TEST")
    print("=" * 80 + "\n")

    # 1. Generator initialisieren
    generator = MultiCompanyOfferGenerator()

    # 2. Produkte laden
    products = generator.load_all_products()
    print(f"✓ Produkte geladen:")
    print(f"  • Module: {len(products.get('module', []))}")
    print(f"  • Wechselrichter: {len(products.get('inverter', []))}")
    print(f"  • Speicher: {len(products.get('storage', []))}")

    # 3. Basis-Einstellungen (wie in Streamlit)
    base_settings = {
        "enable_product_rotation": True,
        "rotation_mode": "linear",
        "product_rotation_step": 1,
        "module_rotation_step": 1,
        "inverter_rotation_step": 1,
        "storage_rotation_step": 1,
        "include_storage": True,
        "module_quantity": 20,
        "price_increment_percent": 5,  # 5% Preissteigerung
        "price_calculation_mode": "linear"
    }

    # Basisprodukte setzen
    if products.get('module'):
        base_settings['selected_module_id'] = products['module'][0].get('id')
        print(
            f"\n✓ Basis-Modul: {
                products['module'][0].get('model_name')} (ID: {
                base_settings['selected_module_id']})")

    if products.get('inverter'):
        base_settings['selected_inverter_id'] = products['inverter'][0].get(
            'id')
        print(
            f"✓ Basis-Wechselrichter: {
                products['inverter'][0].get('model_name')} (ID: {
                base_settings['selected_inverter_id']})")

    if products.get('storage'):
        base_settings['selected_storage_id'] = products['storage'][0].get('id')
        print(
            f"✓ Basis-Speicher: {
                products['storage'][0].get('model_name')} (ID: {
                base_settings['selected_storage_id']})")

    print("\n" + "-" * 80)
    print("ROTATIONS-TEST FÜR 5 FIRMEN")
    print("-" * 80 + "\n")

    # 4. Rotation für 5 Firmen testen
    for i in range(5):
        print(f"\n{'=' * 60}")
        print(f"FIRMA {i + 1}")
        print(f"{'=' * 60}")

        # Rotierte Einstellungen abrufen (wie in generate_multi_offers)
        company_settings = generator.get_rotated_products_for_company(
            i, base_settings)

        print(f"\n📦 Rotierte Produkt-IDs:")
        print(f"  • Modul-ID: {company_settings.get('selected_module_id')}")
        print(
            f"  • Wechselrichter-ID: {company_settings.get('selected_inverter_id')}")
        print(
            f"  • Speicher-ID: {company_settings.get('selected_storage_id')}")

        # Produkte laden um zu sehen, was ausgewählt wurde
        print(f"\n📦 Ausgewählte Produkte:")

        from product_db import get_product_by_id

        module = get_product_by_id(company_settings.get('selected_module_id'))
        if module:
            print(
                f"  • Modul: {
                    module.get('brand')} {
                    module.get('model_name')} ({
                    module.get('capacity_w')}W)")

        inverter = get_product_by_id(
            company_settings.get('selected_inverter_id'))
        if inverter:
            print(
                f"  • Wechselrichter: {
                    inverter.get('brand')} {
                    inverter.get('model_name')} ({
                    inverter.get('power_kw')}kW)")

        storage = get_product_by_id(
            company_settings.get('selected_storage_id'))
        if storage:
            cap = storage.get('max_kwh_capacity') or (
                storage.get('capacity_w', 0) / 1000)
            print(
                f"  • Speicher: {
                    storage.get('brand')} {
                    storage.get('model_name')} ({cap}kWh)")

        # Preisstaffelung simulieren
        print(f"\n💰 Preisstaffelung:")

        # Mock-Berechnungsergebnisse
        mock_calc_results = {
            'total_investment_netto': 20000.00,
            'total_investment_brutto': 23800.00,
            'module_cost_total': 8000.00,
            'inverter_cost_total': 3000.00,
            'storage_cost_total': 7000.00,
            'amortization_time_years': 12.5
        }

        print(
            f"  Vor Staffelung: {
                mock_calc_results['total_investment_netto']:.2f} €")

        # Preisstaffelung anwenden
        scaled_results = generator.apply_price_scaling(
            i, base_settings, deepcopy(mock_calc_results))

        print(
            f"  Nach Staffelung: {
                scaled_results['total_investment_netto']:.2f} €")

        if i > 0:
            diff = scaled_results['total_investment_netto'] - \
                mock_calc_results['total_investment_netto']
            diff_percent = (
                diff / mock_calc_results['total_investment_netto']) * 100
            print(f"  Differenz: +{diff:.2f} € (+{diff_percent:.1f}%)")

    print("\n" + "=" * 80)
    print("✓ WORKFLOW TEST ABGESCHLOSSEN")
    print("=" * 80)

    # Zusammenfassung
    print("\n📊 ZUSAMMENFASSUNG:")
    print(f"  • Rotationsstatus:")
    for category, state in generator.rotation_state.items():
        used_count = len(state.get('used_ids', []))
        used_brands = len(state.get('used_brands', []))
        print(
            f"    - {category}: {used_count} Produkt(e), {used_brands} Marke(n)")

    print("\n💡 ERWARTETES VERHALTEN:")
    print("  1. Jede Firma sollte VERSCHIEDENE Produkte haben")
    print("  2. Bevorzugt VERSCHIEDENE Marken")
    print("  3. Preise sollten steigen: 0%, +5%, +10%, +15%, +20%")
    print()


if __name__ == "__main__":
    simulate_multi_offer_workflow()
