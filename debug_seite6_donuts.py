#!/usr/bin/env python3
"""
Debug-Skript für Seite 6 Donut-Charts
"""

from pdf_template_engine.dynamic_overlay import generate_overlay
import sys
from pathlib import Path

# Füge das Projektverzeichnis zum Python-Pfad hinzu
sys.path.insert(0, str(Path(__file__).parent))


def debug_seite6_donuts():
    """Debuggt die Seite 6 Donut-Charts"""

    print("🔍 Debug der Seite 6 Donut-Charts")
    print("=" * 40)

    # Test-Daten mit verschiedenen Werten
    test_scenarios = [
        {
            "name": "Explizite Werte (sollten funktionieren)",
            "data": {
                "storage_consumption_ratio_percent": "74",
                "storage_production_ratio_percent": "53",
                "company_name": "TommaTech GmbH"
            }
        },
        {
            "name": "String-Werte mit %",
            "data": {
                "storage_consumption_ratio_percent": "74%",
                "storage_production_ratio_percent": "53%",
                "company_name": "TommaTech GmbH"
            }
        },
        {
            "name": "Float-Werte",
            "data": {
                "storage_consumption_ratio_percent": 74.0,
                "storage_production_ratio_percent": 53.0,
                "company_name": "TommaTech GmbH"
            }
        },
        {
            "name": "Hohe Werte",
            "data": {
                "storage_consumption_ratio_percent": "95",
                "storage_production_ratio_percent": "85",
                "company_name": "TommaTech GmbH"
            }
        },
        {
            "name": "Niedrige Werte",
            "data": {
                "storage_consumption_ratio_percent": "25",
                "storage_production_ratio_percent": "15",
                "company_name": "TommaTech GmbH"
            }
        },
        {
            "name": "Ein Wert 0",
            "data": {
                "storage_consumption_ratio_percent": "0",
                "storage_production_ratio_percent": "45",
                "company_name": "TommaTech GmbH"
            }
        }
    ]

    for i, scenario in enumerate(test_scenarios):
        print(f"\n=== Test {i + 1}: {scenario['name']} ===")

        try:
            # Generiere Overlay
            coords_dir = Path("coords")
            overlay_bytes = generate_overlay(
                coords_dir=coords_dir,
                dynamic_data=scenario['data'],
                total_pages=8  # MIGRATION: Changed from 7 to 8
            )

            if overlay_bytes:
                output_file = f"debug_seite6_donuts_{
                    i + 1}_{
                    scenario['name'].lower().replace(
                        ' ', '_').replace(
                        '(', '').replace(
                        ')', '')}.pdf"
                with open(output_file, "wb") as f:
                    f.write(overlay_bytes)

                print(f"✅ PDF erstellt: {output_file}")
                print("📊 Input-Werte:")
                print(
                    f"   - Consumption: {scenario['data']['storage_consumption_ratio_percent']}")
                print(
                    f"   - Production: {scenario['data']['storage_production_ratio_percent']}")

            else:
                print(
                    f"❌ Overlay-Generierung fehlgeschlagen für Szenario {i + 1}")

        except Exception as e:
            print(f"❌ Fehler bei Szenario {i + 1}: {e}")
            import traceback
            traceback.print_exc()


def test_with_real_calculation_data():
    """Testet mit echten Berechnungsdaten"""

    print("\n🔍 Test mit echten Berechnungsdaten")
    print("=" * 35)

    # Simuliere echte Berechnungsdaten wie sie aus placeholders.py kommen
    # würden
    real_data = {
        "company_name": "TommaTech GmbH",

        # Basis-Daten für Speicher-Berechnung
        "storage_capacity_kwh": "12.09",
        "annual_consumption_kwh": "6000",
        "annual_pv_production_kwh": "8251.92",

        # Direkt berechnete Werte (wie sie placeholders.py setzen würde)
        # 12.09 / (6000/365) * 100 ≈ 74%
        "storage_consumption_ratio_percent": "74",
        # 12.09 / (8251.92/365) * 100 ≈ 53%
        "storage_production_ratio_percent": "53",

        # Zusätzliche Daten für vollständige PDF
        "anlage_kwp": "8.5 kWp",
        "self_supply_rate_percent": "65%",
        "self_consumption_percent": "45%",

        # Wasserfall-Daten
        "self_consumption_without_battery_eur": "1.450,75 €",
        "annual_feed_in_revenue_eur": "920,50 €",
        "tax_benefits_eur": "380,25 €",
        "total_annual_savings_eur": "2.751,50 €"
    }

    try:
        coords_dir = Path("coords")

        print("📊 Echte Berechnungsdaten:")
        for key, value in real_data.items():
            if 'storage' in key or 'ratio' in key:
                print(f"   {key}: {value}")

        overlay_bytes = generate_overlay(
            coords_dir=coords_dir,
            dynamic_data=real_data,
            total_pages=8  # MIGRATION: Changed from 7 to 8
        )

        if overlay_bytes:
            output_file = "debug_seite6_real_calculation_data.pdf"
            with open(output_file, "wb") as f:
                f.write(overlay_bytes)

            print(f"✅ Real-Data-PDF erstellt: {output_file}")
            print(
                "📋 Diese PDF sollte sowohl Wasserfall-Diagramm (Seite 3) als auch Donut-Charts (Seite 6) zeigen")
        else:
            print("❌ Real-Data-Test fehlgeschlagen")

    except Exception as e:
        print(f"❌ Fehler beim Real-Data-Test: {e}")


if __name__ == "__main__":
    print("🚀 Debug der Seite 6 Donut-Charts")
    print("=" * 40)

    # Test 1: Verschiedene Werte-Formate
    debug_seite6_donuts()

    # Test 2: Echte Berechnungsdaten
    test_with_real_calculation_data()

    print("\n📋 Zusammenfassung:")
    print("   - Schauen Sie in die Konsolen-Ausgabe nach 'DEBUG: Seite 6 Donut-Charts'")
    print("   - Die PDFs zeigen ob die Donut-Charts sichtbar sind")
    print("   - Falls Charts fehlen, liegt es an der Werte-Extraktion oder Position")
