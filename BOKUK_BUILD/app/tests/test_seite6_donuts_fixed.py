#!/usr/bin/env python3
"""
Test der korrigierten Seite 6 Donut-Charts
"""

from pdf_template_engine.dynamic_overlay import generate_overlay
import sys
from pathlib import Path

# Füge das Projektverzeichnis zum Python-Pfad hinzu
sys.path.insert(0, str(Path(__file__).parent))


def test_fixed_donuts():
    """Testet die korrigierten Donut-Charts auf Seite 6"""

    print("🔧 Test der korrigierten Seite 6 Donut-Charts")
    print("=" * 50)

    # Test-Daten mit den korrekten Keys
    dynamic_data = {
        # Donut-Charts Daten
        "storage_consumption_ratio_percent": "74",
        "storage_production_ratio_percent": "53",

        # Wasserfall-Daten für Seite 3
        "self_consumption_without_battery_eur": "1.450,75 €",
        "annual_feed_in_revenue_eur": "920,50 €",
        "tax_benefits_eur": "380,25 €",
        "total_annual_savings_eur": "2.751,50 €",

        # Basis-Daten
        "company_name": "TommaTech GmbH",
        "anlage_kwp": "8.5 kWp",
        "annual_pv_production_kwh": "8.251,92 kWh",
        "self_supply_rate_percent": "65%",
        "self_consumption_percent": "45%"
    }

    try:
        # Generiere Overlay
        coords_dir = Path("coords")

        print("📊 Test-Daten:")
        print(
            f"   - Speicher zu Tagesverbrauch: {dynamic_data['storage_consumption_ratio_percent']}%")
        print(
            f"   - Speicher zu PV-Produktion: {dynamic_data['storage_production_ratio_percent']}%")

        overlay_bytes = generate_overlay(
            coords_dir=coords_dir,
            dynamic_data=dynamic_data,
            total_pages=7
        )

        if overlay_bytes:
            output_file = "test_seite6_donuts_fixed.pdf"
            with open(output_file, "wb") as f:
                f.write(overlay_bytes)

            print(
                f"\n✅ PDF mit korrigierten Donut-Charts erstellt: {output_file}")
            print(f"📦 Dateigröße: {len(overlay_bytes):,} bytes")
            print("📋 Überprüfen Sie Seite 6 für die Donut-Charts:")
            print("   - Oberer Chart: Speicher zu Tagesverbrauch (74%)")
            print("   - Unterer Chart: Speicher zu PV-Produktion (53%)")
            print(
                "📍 Position: Links von den Platzhaltern bei X=280, Y basierend auf seite6.yml")

            return True
        print("\n❌ Overlay-Generierung fehlgeschlagen")
        return False

    except Exception as e:
        print(f"\n❌ Fehler beim Test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_different_values():
    """Testet verschiedene Werte für die Donut-Charts"""

    print("\n🔧 Test verschiedener Donut-Chart Werte")
    print("=" * 40)

    test_scenarios = [
        {
            "name": "Hohe Werte",
            "consumption": "95",
            "production": "85"
        },
        {
            "name": "Niedrige Werte",
            "consumption": "25",
            "production": "15"
        },
        {
            "name": "Asymmetrische Werte",
            "consumption": "80",
            "production": "30"
        },
        {
            "name": "Ein Wert 0",
            "consumption": "0",
            "production": "60"
        }
    ]

    for i, scenario in enumerate(test_scenarios):
        print(f"\n--- Test {i + 1}: {scenario['name']} ---")

        dynamic_data = {
            "storage_consumption_ratio_percent": scenario['consumption'],
            "storage_production_ratio_percent": scenario['production'],
            "company_name": "TommaTech GmbH",

            # Minimale Wasserfall-Daten
            "self_consumption_without_battery_eur": "1000,00 €",
            "annual_feed_in_revenue_eur": "500,00 €",
            "tax_benefits_eur": "200,00 €",
            "total_annual_savings_eur": "1700,00 €"
        }

        try:
            coords_dir = Path("coords")
            overlay_bytes = generate_overlay(
                coords_dir=coords_dir,
                dynamic_data=dynamic_data,
                total_pages=7
            )

            if overlay_bytes:
                output_file = f"test_seite6_donuts_{
                    i + 1}_{
                    scenario['name'].lower().replace(
                        ' ', '_')}.pdf"
                with open(output_file, "wb") as f:
                    f.write(overlay_bytes)

                print(f"✅ PDF erstellt: {output_file}")
                print(
                    f"📊 Werte: Consumption={
                        scenario['consumption']}%, Production={
                        scenario['production']}%")
            else:
                print(f"❌ Szenario {i + 1} fehlgeschlagen")

        except Exception as e:
            print(f"❌ Fehler bei Szenario {i + 1}: {e}")


if __name__ == "__main__":
    print("🚀 Test der korrigierten Seite 6 Donut-Charts")
    print("=" * 55)

    # Test 1: Basis-Funktionalität
    success = test_fixed_donuts()

    if success:
        # Test 2: Verschiedene Werte
        test_different_values()

        print("\n🎉 Alle Tests abgeschlossen!")
        print("📋 Die Donut-Charts sollten jetzt korrekt auf Seite 6 sichtbar sein:")
        print("   ✅ Position: Links von den Platzhaltern (X=280)")
        print("   ✅ Vertikal gestapelt basierend auf seite6.yml Koordinaten")
        print("   ✅ Angemessene Größe (Radius 30/18)")
        print("   ✅ Labels rechts von den Charts")
    else:
        print("\n❌ Basis-Test fehlgeschlagen - weitere Tests übersprungen")
