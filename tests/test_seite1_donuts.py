#!/usr/bin/env python3
"""
Test der Donut-Charts auf Seite 1 (zum Testen der Sichtbarkeit)
"""

from pdf_template_engine.dynamic_overlay import generate_overlay
import sys
from pathlib import Path

# Füge das Projektverzeichnis zum Python-Pfad hinzu
sys.path.insert(0, str(Path(__file__).parent))


def test_seite1_donuts():
    """Testet die Donut-Charts auf Seite 1 für maximale Sichtbarkeit"""

    print("🔧 Test der Donut-Charts auf Seite 1 (Sichtbarkeitstest)")
    print("=" * 60)

    # Test-Daten mit sehr sichtbaren Werten
    dynamic_data = {
        # Donut-Charts Daten
        "storage_consumption_ratio_percent": "85",  # Hoher Wert für gute Sichtbarkeit
        "storage_production_ratio_percent": "65",   # Hoher Wert für gute Sichtbarkeit

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

        print("📊 Test-Daten für maximale Sichtbarkeit:")
        print(
            f"   - Speicher zu Tagesverbrauch: {dynamic_data['storage_consumption_ratio_percent']}%")
        print(
            f"   - Speicher zu PV-Produktion: {dynamic_data['storage_production_ratio_percent']}%")
        print("📍 Position: Seite 1, links unten, unterhalb 'TECHNISCHE SPEZIFIKATIONEN'")
        print(
            "🎨 Design: Große Charts (Radius 40/25), rote und blaue Farben, schwarze Labels")

        overlay_bytes = generate_overlay(
            coords_dir=coords_dir,
            dynamic_data=dynamic_data,
            total_pages=7
        )

        if overlay_bytes:
            output_file = "test_seite1_donuts_sichtbarkeit.pdf"
            with open(output_file, "wb") as f:
                f.write(overlay_bytes)

            print(
                f"\n✅ PDF mit Seite 1 Test-Donut-Charts erstellt: {output_file}")
            print(f"📦 Dateigröße: {len(overlay_bytes):,} bytes")
            print("📋 Überprüfen Sie Seite 1 für die Test-Donut-Charts:")
            print("   - Oberer Chart (ROT): Speicher zu Tagesverbrauch (85%)")
            print("   - Unterer Chart (BLAU): Speicher zu PV-Produktion (65%)")
            print("   - Position: Links unten auf der Seite")
            print("   - Labels: 'Test: Tagesverbrauch' und 'Test: PV-Produktion'")

            return True
        print("\n❌ Overlay-Generierung fehlgeschlagen")
        return False

    except Exception as e:
        print(f"\n❌ Fehler beim Test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_verschiedene_werte():
    """Testet verschiedene Werte auf Seite 1"""

    print("\n🔧 Test verschiedener Werte auf Seite 1")
    print("=" * 40)

    test_scenarios = [
        {
            "name": "Maximale Werte",
            "consumption": "100",
            "production": "95"
        },
        {
            "name": "Mittlere Werte",
            "consumption": "50",
            "production": "40"
        },
        {
            "name": "Niedrige Werte",
            "consumption": "15",
            "production": "10"
        },
        {
            "name": "Nur ein Chart",
            "consumption": "0",
            "production": "75"
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
                output_file = f"test_seite1_donuts_{
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
    print("🚀 Test der Donut-Charts auf Seite 1 (Sichtbarkeitstest)")
    print("=" * 65)

    # Test 1: Basis-Sichtbarkeitstest
    success = test_seite1_donuts()

    if success:
        # Test 2: Verschiedene Werte
        test_verschiedene_werte()

        print("\n🎉 Alle Tests abgeschlossen!")
        print("📋 Die Donut-Charts sollten jetzt auf Seite 1 sichtbar sein:")
        print("   ✅ Position: Links unten, unterhalb 'TECHNISCHE SPEZIFIKATIONEN'")
        print("   ✅ Große Größe (Radius 40/25) für maximale Sichtbarkeit")
        print("   ✅ Rote und blaue Farben für hohen Kontrast")
        print("   ✅ Schwarze Labels für beste Lesbarkeit")
        print("📍 Falls sichtbar: Problem war die Position auf Seite 6")
        print("📍 Falls nicht sichtbar: Problem liegt an der Donut-Zeichnung selbst")
    else:
        print("\n❌ Basis-Test fehlgeschlagen - weitere Tests übersprungen")
