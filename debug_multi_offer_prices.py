#!/usr/bin/env python3
"""
Debug-Script: Simuliert die echte Multi-Offer-Pipeline
"""

from product_db import get_product_by_id, list_products
from calculations import perform_calculations
from copy import deepcopy
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


def simulate_multi_offer_generation():
    """Simuliert die echte Multi-Offer-Generierung"""

    print("=" * 100)
    print("DEBUG: MULTI-OFFER PIPELINE SIMULATION")
    print("=" * 100)

    # Produkte laden
    modules = list_products('module')
    inverters = list_products('inverter')
    storage = list_products('storage')

    if not modules or not inverters or not storage:
        print("❌ FEHLER: Keine Produkte gefunden!")
        return

    print(
        f"\n✓ Produkte geladen: {
            len(modules)} Module, {
            len(inverters)} Wechselrichter, {
                len(storage)} Speicher")

    # Basis-Konfiguration (wie von Streamlit übergeben)
    base_project_data = {
        "project_details": {
            "module_quantity": 20,
            "include_storage": True,
            "annual_consumption_kwh": 4500,
            "roof_orientation": "Süd",
            "roof_tilt_deg": 30,
            "latitude": 48.0,
            "longitude": 11.0,
            # Basis-Produkte (Firma 1)
            "selected_module_id": modules[0]['id'],
            "selected_inverter_id": inverters[0]['id'],
            "selected_storage_id": storage[0]['id']
        },
        "customer_data": {
            "first_name": "Test",
            "last_name": "Kunde",
            "electricity_price_ct_per_kwh": 30.0
        }
    }

    # Simuliere 5 Firmen mit Produktrotation
    firms = [{"name": "Firma 1",
              "module_id": modules[0]['id'],
              "inverter_id": inverters[0]['id'],
              "storage_id": storage[0]['id']},
             {"name": "Firma 2",
              "module_id": modules[5]['id'],
              "inverter_id": inverters[10]['id'],
              "storage_id": storage[5]['id']},
             {"name": "Firma 3",
              "module_id": modules[10]['id'],
              "inverter_id": inverters[20]['id'],
              "storage_id": storage[10]['id']},
             {"name": "Firma 4",
              "module_id": modules[1]['id'],
              "inverter_id": inverters[5]['id'],
              "storage_id": storage[3]['id']},
             {"name": "Firma 5",
              "module_id": modules[6]['id'],
              "inverter_id": inverters[15]['id'],
              "storage_id": storage[8]['id']},
             ]

    results = []

    for company_index, firm in enumerate(firms):
        print(f"\n{'=' * 100}")
        print(f"{firm['name']} (Index: {company_index})")
        print(f"{'=' * 100}")

        # Produkte abrufen
        module = get_product_by_id(firm['module_id'])
        inverter = get_product_by_id(firm['inverter_id'])
        storage_unit = get_product_by_id(firm['storage_id'])

        print("📦 Produkte:")
        print(
            f"   Modul:         {
                module.get('model_name') if module else 'N/A'} ({
                module.get(
                    'price_euro',
                    0):.2f} €)")
        print(
            f"   Wechselrichter: {
                inverter.get('model_name') if inverter else 'N/A'} ({
                inverter.get(
                    'price_euro',
                    0):.2f} €)")
        print(
            f"   Speicher:      {
                storage_unit.get('model_name') if storage_unit else 'N/A'} ({
                storage_unit.get(
                    'price_euro',
                    0):.2f} €)")

        # Projekt-Daten mit rotierten Produkten
        calc_input = deepcopy(base_project_data)
        calc_input["project_details"]["selected_module_id"] = firm['module_id']
        calc_input["project_details"]["selected_inverter_id"] = firm['inverter_id']
        calc_input["project_details"]["selected_storage_id"] = firm['storage_id']

        # Berechnung durchführen (wie in multi_offer_generator.py)
        calculation_errors = []
        print("\n🔄 Führe Berechnung durch...")

        recalculated_results = perform_calculations(
            calc_input, {}, calculation_errors)

        if recalculated_results:
            total_netto = recalculated_results.get('total_investment_netto', 0)
            base_price = recalculated_results.get('base_matrix_price_netto', 0)

            print("\n💰 BERECHNUNGSERGEBNISSE:")
            print(f"   Basis-Preis:        {base_price:>12.2f} €")
            print(f"   Gesamt Netto:       {total_netto:>12.2f} €")

            # Produktpreis-Logs extrahieren
            product_price_logs = [
                e for e in calculation_errors if 'Preis aus DB' in e or 'Produktdatenbank' in e]
            if product_price_logs:
                print("\n   📋 Produktpreis-Berechnung:")
                for log in product_price_logs:
                    print(f"      {log}")

            results.append({
                'firm': firm['name'],
                'total_netto': total_netto,
                'base_price': base_price,
                'module': module.get('model_name') if module else 'N/A'
            })
        else:
            print("\n❌ Berechnung fehlgeschlagen!")
            if calculation_errors:
                print(f"   Fehler: {calculation_errors[:3]}")

    # Vergleich
    print(f"\n{'=' * 100}")
    print("VERGLEICH ALLER FIRMEN")
    print(f"{'=' * 100}\n")

    for res in results:
        print(f"{res['firm']}: {res['module'][:40]:40} → Basis: {res['base_price']:>10.2f} €, Gesamt: {res['total_netto']:>10.2f} €")

    # Analyse
    base_prices = [r['base_price'] for r in results]
    total_prices = [r['total_netto'] for r in results]

    unique_base = set(base_prices)
    unique_total = set(total_prices)

    print(f"\n{'=' * 100}")
    print("ANALYSE")
    print(f"{'=' * 100}")

    if len(unique_base) == 1:
        print(
            f"❌ PROBLEM: Alle Basis-Preise sind GLEICH: {base_prices[0]:.2f} €")
        print("   → Produktpreise werden NICHT berücksichtigt!")
    else:
        print(f"✅ ERFOLG: {len(unique_base)} verschiedene Basis-Preise")
        print(
            f"   → Spanne: {
                min(base_prices):.2f} € bis {
                max(base_prices):.2f} € (Diff: {
                max(base_prices) -
                min(base_prices):.2f} €)")

    if len(unique_total) == 1:
        print(
            f"❌ PROBLEM: Alle Gesamt-Preise sind GLEICH: {total_prices[0]:.2f} €")
    else:
        print(f"✅ ERFOLG: {len(unique_total)} verschiedene Gesamt-Preise")
        print(
            f"   → Spanne: {
                min(total_prices):.2f} € bis {
                max(total_prices):.2f} € (Diff: {
                max(total_prices) -
                min(total_prices):.2f} €)")

    print(f"{'=' * 100}\n")


if __name__ == "__main__":
    simulate_multi_offer_generation()
