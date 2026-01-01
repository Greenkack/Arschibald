#!/usr/bin/env python3
"""
Test der SUPER SICHTBAREN Seite 6 Donut-Charts
"""

import sys
from pathlib import Path

from pdf_template_engine.dynamic_overlay import generate_overlay

# Füge das Projektverzeichnis zum Python-Pfad hinzu
sys.path.insert(0, str(Path(__file__).parent))


def test_super_visible_donuts():
    """Testet die SUPER SICHTBAREN Donut-Charts auf Seite 6"""

    print("Test der SUPER SICHTBAREN Seite 6 Donut-Charts")
    print("=" * 55)

    # Test-Daten mit hohen Werten für maximale Sichtbarkeit
    dynamic_data = {
        # HOHE Werte für maximale Sichtbarkeit
        "storage_consumption_ratio_percent": "85",
        "storage_production_ratio_percent": "75",

        # Basis-Daten
        "company_name": "TommaTech GmbH",

        # Minimale Wasserfall-Daten für Seite 3
        "self_consumption_without_battery_eur": "1000,00 €",
        "annual_feed_in_revenue_eur": "500,00 €",
        "tax_benefits_eur": "200,00 €",
        "total_annual_savings_eur": "1700,00 €"
    }

    try:
        # Generiere Overlay
        coords_dir = Path("coords")

        print("Test-Daten für maximale Sichtbarkeit:")
        print(
            f"   - Speicher zu Tagesverbrauch: {dynamic_data['storage_consumption_ratio_percent']}%")
        print(
            f"   - Speicher zu PV-Produktion: {dynamic_data['storage_production_ratio_percent']}%")
        print(" Position: MITTE DER SEITE für maximale Sichtbarkeit")
        print(" Größe: SEHR GROß (Radius 50/30)")
        print("Farben: REINES ROT und REINES BLAU")
        print(" Extras: Schwarzer Rahmen und Titel")

        overlay_bytes = generate_overlay(
            coords_dir=coords_dir,
            dynamic_data=dynamic_data,
            total_pages=7
        )

        if overlay_bytes:
            output_file = "test_seite6_super_visible.pdf"
            with open(output_file, "wb") as f:
                f.write(overlay_bytes)

            print(
                f"\nPDF mit SUPER SICHTBAREN Donut-Charts erstellt: {output_file}")
            print(f"Dateigröße: {len(overlay_bytes):,} bytes")
            print(" Die Charts sollten jetzt DEFINITIV sichtbar sein auf Seite 6:")
            print("    Linker Chart: Tagesverbrauch (85%) - REINES ROT")
            print("    Rechter Chart: PV-Produktion (75%) - REINES BLAU")
            print("    Schwarzer Rahmen um beide Charts")
            print("   Titel: 'SPEICHER-RELATIONEN'")

            return True
        print("\nOverlay-Generierung fehlgeschlagen")
        return False

    except Exception as e:
        print(f"\nFehler beim Test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_extreme_values():
    """Testet mit extremen Werten für maximale Sichtbarkeit"""

    print("\nTest mit extremen Werten")
    print("=" * 30)

    extreme_data = {
        # EXTREME Werte
        "storage_consumption_ratio_percent": "100",
        "storage_production_ratio_percent": "100",
        "company_name": "TommaTech GmbH",

        # Minimale andere Daten
        "self_consumption_without_battery_eur": "2000,00 €",
        "annual_feed_in_revenue_eur": "1000,00 €",
        "tax_benefits_eur": "400,00 €",
        "total_annual_savings_eur": "3400,00 €"
    }

    try:
        coords_dir = Path("coords")

        print("Extreme Test-Daten:")
        print(
            f"   - Tagesverbrauch: {extreme_data['storage_consumption_ratio_percent']}% (VOLL)")
        print(
            f"   - PV-Produktion: {extreme_data['storage_production_ratio_percent']}% (VOLL)")

        overlay_bytes = generate_overlay(
            coords_dir=coords_dir,
            dynamic_data=extreme_data,
            total_pages=7
        )

        if overlay_bytes:
            output_file = "test_seite6_extreme_values.pdf"
            with open(output_file, "wb") as f:
                f.write(overlay_bytes)

            print(f"Extreme-PDF erstellt: {output_file}")
            print(" Beide Charts sollten komplett gefüllt sein (100%)")
        else:
            print("Extreme-Test fehlgeschlagen")

    except Exception as e:
        print(f"Fehler beim Extreme-Test: {e}")


if __name__ == "__main__":
    print("Test der SUPER SICHTBAREN Seite 6 Donut-Charts")
    print("=" * 60)

    # Test 1: Super sichtbare Charts
    success = test_super_visible_donuts()

    if success:
        # Test 2: Extreme Werte
        test_extreme_values()

        print("\n Tests abgeschlossen!")
        print(" Falls die Charts IMMER NOCH nicht sichtbar sind:")
        print("   1. Überprüfen Sie Seite 6 der generierten PDFs")
        print("   2. Die Charts sind jetzt in der MITTE der Seite")
        print("   3. Sie haben einen schwarzen Rahmen und Titel")
        print("   4. Sie sind SEHR GROß (Radius 50)")
        print("   5. Sie sind ROT und BLAU für maximale Sichtbarkeit")
    else:
        print("\nTest fehlgeschlagen")
