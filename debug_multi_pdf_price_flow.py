#!/usr/bin/env python3
"""
DEBUG: Multi-PDF Preise - Wo gehen die skalierten Preise verloren?
"""

from multi_offer_generator import MultiCompanyOfferGenerator
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def debug_price_flow():
    """Debuggt den kompletten Preis-Flow"""

    print("\n" + "=" * 80)
    print("🔍 DEBUG: Multi-PDF Preis-Flow")
    print("=" * 80)

    generator = MultiCompanyOfferGenerator()

    # Simuliere 3 Firmen
    base_settings = {
        "enable_product_rotation": True,
        "product_rotation_step": 1,
        "price_increment_percent": 5.0,  # 5% pro Firma
        "price_calculation_mode": "linear"
    }

    base_calc_results = {
        'total_investment_netto': 20000.0,
        'total_investment_brutto': 23800.0,
        'final_price_net': 20000.0,
        'final_price_brutto': 23800.0,
        'amortization_time_years': 10.0,
    }

    print("\n📊 Basis-Berechnungsergebnisse:")
    print(
        f"   total_investment_netto: {
            base_calc_results['total_investment_netto']:,.2f} €")
    print(
        f"   final_price_net: {
            base_calc_results.get(
                'final_price_net',
                'N/A')}")

    for i in range(3):
        print(f"\n{'=' * 80}")
        print(f"FIRMA {i + 1}")
        print(f"{'=' * 80}")

        # 1. Preisstaffelung anwenden
        scaled_results = generator.apply_price_scaling(
            i, base_settings, base_calc_results.copy())

        print("\n1️⃣  NACH apply_price_scaling():")
        print(
            f"   total_investment_netto: {
                scaled_results.get(
                    'total_investment_netto',
                    'FEHLT'):,.2f}")
        print(
            f"   total_investment_brutto: {
                scaled_results.get(
                    'total_investment_brutto',
                    'FEHLT'):,.2f}")
        print(
            f"   final_price_net: {
                scaled_results.get(
                    'final_price_net',
                    'FEHLT')}")
        print(
            f"   final_price_with_provision: {
                scaled_results.get(
                    'final_price_with_provision',
                    'FEHLT')}")

        # 2. Was würde in project_details geschrieben?
        net_price = scaled_results.get(
            'final_price_net') or scaled_results.get('total_investment_netto')
        gross_price = scaled_results.get(
            'final_price_brutto') or scaled_results.get('total_investment_brutto')

        print("\n2️⃣  Was würde in project_details geschrieben:")
        print(f"   final_offer_price_net: {net_price:,.2f} €")
        print(f"   final_price_with_provision: {net_price:,.2f} €")
        print(f"   final_price_brutto: {gross_price:,.2f} €")

        # 3. Simuliere was placeholders.py sehen würde
        mock_project_details = {
            'final_offer_price_net': net_price,
            'final_price_with_provision': net_price,
            'final_price_netto': net_price,
            'final_price_brutto': gross_price,
        }

        print("\n3️⃣  Was placeholders.py aus project_details holen würde:")
        print(
            f"   final_price_with_provision: {
                mock_project_details.get(
                    'final_price_with_provision',
                    'FEHLT'):,.2f} €")

        # 4. Prüfe ob analysis_results auch skaliert ist
        print("\n4️⃣  Was placeholders.py aus analysis_results holen würde:")
        print(
            f"   total_investment_netto: {
                scaled_results.get(
                    'total_investment_netto',
                    'FEHLT'):,.2f} €")

        # 5. Zeige den Unterschied
        price_increase = (
            (net_price / base_calc_results['total_investment_netto']) - 1) * 100
        print("\n✅ RESULTAT:")
        print(
            f"   Basis: {
                base_calc_results['total_investment_netto']:,.2f} €")
        print(f"   Skaliert: {net_price:,.2f} € (+{price_increase:.1f}%)")

    print(f"\n{'=' * 80}")
    print("🔍 ANALYSE")
    print(f"{'=' * 80}")
    print("""
Das Problem könnte sein:

1. ✅ apply_price_scaling() funktioniert → scaled_results hat richtige Preise
2. ✅ project_details wird korrekt gesetzt → hat skalierte Preise
3. ❓ placeholders.py: Nutzt es project_details oder analysis_results?

Wenn placeholders.py analysis_results nutzt statt project_details:
   → analysis_results hat NICHT die skalierten Preise!
   → Alle PDFs zeigen gleichen Preis

LÖSUNG:
   placeholders.py muss project_details VOR analysis_results prüfen!
    """)


if __name__ == "__main__":
    debug_price_flow()
