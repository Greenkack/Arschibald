#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testet ob perform_calculations unterschiedliche Preise für verschiedene Produkte berechnet
"""

from calculations import perform_calculations
from product_db import list_products

# Test-Konfiguration


def test_price_calculation_with_different_products():
    """Testet ob verschiedene Produkte zu verschiedenen Preisen führen"""

    # Module abrufen
    modules = list_products('module')
    inverters = list_products('inverter')
    storage = list_products('storage')

    if not modules or not inverters or not storage:
        print("❌ Fehler: Keine Produkte gefunden!")
        return

    print("=" * 100)
    print("TEST: PREISBERECHNUNG MIT VERSCHIEDENEN PRODUKTEN")
    print("=" * 100)

    # Test 3 verschiedene Modul-Kombinationen
    test_configs = [
        {
            "module": modules[0],  # z.B. Aiko
            "inverter": inverters[0],
            "storage": storage[0]
        },
        {
            "module": modules[5],  # z.B. Solarfabrik
            "inverter": inverters[10],
            "storage": storage[5]
        },
        {
            "module": modules[10],  # z.B. Trina
            "inverter": inverters[20],
            "storage": storage[10]
        }
    ]

    results_list = []

    for i, config in enumerate(test_configs, 1):
        print(f"\n{'=' * 100}")
        print(f"KONFIGURATION {i}")
        print(f"{'=' * 100}")
        print(
            f"Modul:         {
                config['module'].get('model_name')} ({
                config['module'].get(
                    'price_euro',
                    0):.2f} €)")
        print(
            f"Wechselrichter: {
                config['inverter'].get('model_name')} ({
                config['inverter'].get(
                    'price_euro',
                    0):.2f} €)")
        print(
            f"Speicher:      {
                config['storage'].get('model_name')} ({
                config['storage'].get(
                    'price_euro',
                    0):.2f} €)")

        # Basis-Input für Berechnung
        calc_input = {
            "project_details": {
                "selected_module_id": config['module'].get('id'),
                "selected_inverter_id": config['inverter'].get('id'),
                "selected_storage_id": config['storage'].get('id'),
                "module_quantity": 20,
                "include_storage": True,
                "annual_consumption_kwh": 4500,
                "roof_orientation": "Süd",
                "roof_tilt_deg": 30,
                "latitude": 48.0,
                "longitude": 11.0
            },
            "customer_data": {
                "first_name": "Test",
                "last_name": "Kunde",
                "electricity_price_ct_per_kwh": 30.0
            }
        }

        errors = []
        calc_results = perform_calculations(calc_input, {}, errors)

        if calc_results:
            total_netto = calc_results.get('total_investment_netto', 0)
            total_brutto = calc_results.get('total_investment_brutto', 0)
            base_price = calc_results.get('base_matrix_price_netto', 0)

            print(f"\n📊 BERECHNUNGSERGEBNISSE:")
            print(f"   Basis-Preis:        {base_price:>12.2f} €")
            print(f"   Gesamt Netto:       {total_netto:>12.2f} €")
            print(f"   Gesamt Brutto:      {total_brutto:>12.2f} €")

            results_list.append({
                'config': i,
                'total_netto': total_netto,
                'module': config['module'].get('model_name'),
                'module_price': config['module'].get('price_euro', 0)
            })

            # Relevante Fehler/Logs ausgeben
            product_price_logs = [
                e for e in errors if 'Preis aus DB' in e or 'Produktdatenbank' in e]
            if product_price_logs:
                print(f"\n   📋 Produktpreis-Logs:")
                for log in product_price_logs:
                    print(f"      {log}")
        else:
            print(f"\n❌ Berechnung fehlgeschlagen!")
            if errors:
                print(f"   Fehler: {errors[:3]}")

    # Vergleich
    print(f"\n{'=' * 100}")
    print("VERGLEICH DER BERECHNUNGEN")
    print(f"{'=' * 100}")

    for res in results_list:
        print(
            f"Konfig {res['config']}: {res['module'][:40]:40} → {res['total_netto']:>12.2f} € (Modul: {res['module_price']:.2f} €)")

    # Analyse
    prices = [r['total_netto'] for r in results_list]
    unique_prices = set(prices)

    print(f"\n{'=' * 100}")
    if len(unique_prices) == 1:
        print("❌ PROBLEM: Alle Konfigurationen haben den GLEICHEN Preis!")
        print(f"   → Preis: {prices[0]:.2f} €")
        print("   → Produktpreise werden NICHT berücksichtigt!")
    elif len(unique_prices) == len(prices):
        print("✅ ERFOLG: Jede Konfiguration hat einen UNTERSCHIEDLICHEN Preis!")
        diff_min_max = max(prices) - min(prices)
        print(
            f"   → Preisspanne: {
                min(prices):.2f} € bis {
                max(prices):.2f} € (Differenz: {
                diff_min_max:.2f} €)")
    else:
        print(
            f"⚠️  TEILERFOLG: {
                len(unique_prices)} verschiedene Preise bei {
                len(prices)} Konfigurationen")

    print(f"{'=' * 100}\n")


if __name__ == "__main__":
    test_price_calculation_with_different_products()
