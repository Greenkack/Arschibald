#!/usr/bin/env python3
"""
Debug-Skript um die echten dynamischen Daten für das Wasserfall-Diagramm zu analysieren
"""

from pdf_template_engine.dynamic_overlay import generate_overlay
import sys
from pathlib import Path

# Füge das Projektverzeichnis zum Python-Pfad hinzu
sys.path.insert(0, str(Path(__file__).parent))


def debug_dynamic_data():
    """Analysiert welche Keys tatsächlich in dynamic_data verfügbar sind"""

    print("🔍 Debug: Analyse der verfügbaren dynamic_data Keys")
    print("=" * 55)

    # Erstelle Test-Daten um zu sehen welche Keys das System generiert
    test_data = {
        # Basis-Daten
        "company_name": "TommaTech GmbH",
        "page_number": "3",
        "total_pages": "7",

        # Wasserfall-Keys die laut placeholders.py verwendet werden sollten:
        "self_consumption_without_battery_eur": "1450.75 €",  # "Direkt"
        "annual_feed_in_revenue_eur": "920.50 €",            # "Einspeisung"
        "tax_benefits_eur": "380.25 €",                      # "platz1"
        "total_annual_savings_eur": "2751.50 €",             # "Gesamt"

        # Alternative Keys falls die obigen nicht funktionieren
        "direct_grid_feed_in_eur": "920.50 €",
        "annual_feed_in_revenue_year1": "920.50 €",

        # Test verschiedene Formate
        "test_german_format": "1.450,75 €",
        "test_english_format": "1,450.75 €",
        "test_simple_format": "1450.75",
    }

    try:
        # Generiere Overlay und schaue welche Keys verwendet werden
        coords_dir = Path("coords")

        print("📊 Test-Daten die wir senden:")
        for key, value in test_data.items():
            if 'eur' in key.lower() or 'test' in key.lower():
                print(f"   {key}: {value}")

        print("\n🔧 Generiere Overlay um zu sehen welche Keys erkannt werden...")

        overlay_bytes = generate_overlay(
            coords_dir=coords_dir,
            dynamic_data=test_data,
            total_pages=8  # MIGRATION: Changed from 7 to 8
        )

        if overlay_bytes:
            output_file = "debug_wasserfall_data.pdf"
            with open(output_file, "wb") as f:
                f.write(overlay_bytes)

            print(f"✅ Debug-PDF erstellt: {output_file}")
            print(
                "📋 Schauen Sie in die Konsolen-Ausgabe nach 'DEBUG: Verfügbare dynamic_data Keys'")
            print(
                "📋 Schauen Sie auch nach 'DEBUG: Wasserfall-Werte' um zu sehen welche Werte erkannt wurden")
        else:
            print("❌ Debug-Overlay-Generierung fehlgeschlagen")

    except Exception as e:
        print(f"❌ Fehler beim Debug: {e}")
        import traceback
        traceback.print_exc()


def test_real_calculation_keys():
    """Testet mit Keys die direkt aus calculations.py kommen"""

    print("\n🔍 Test mit echten Berechnungs-Keys")
    print("=" * 40)

    # Keys die laut calculations.py tatsächlich gesetzt werden
    real_calc_data = {
        "company_name": "TommaTech GmbH",

        # Diese Keys werden in calculations.py gesetzt (Zeile 1403-1410):
        "self_consumption_without_battery_eur": "1.450,75 €",  # Direktverbrauch
        "annual_feed_in_revenue_eur": "920,50 €",              # Einspeisevergütung
        "tax_benefits_eur": "380,25 €",                        # Steuervorteile
        "total_annual_savings_eur": "2.751,50 €",              # Gesamt

        # Zusätzliche Keys die möglicherweise gesetzt werden
        "direct_grid_feed_in_eur": "920,50 €",                 # Alias für Einspeisung
        "battery_usage_savings_eur": "0,00 €",                 # Speicher-Einsparungen

        # Basis-Berechnungswerte
        "annual_pv_production_kwh": "8.251,92 kWh",
        "netzeinspeisung_kwh": "6.306,92 kWh",
        "eigenverbrauch_pro_jahr_kwh": "1.945,00 kWh",
    }

    try:
        coords_dir = Path("coords")

        print("📊 Echte Berechnungs-Daten:")
        for key, value in real_calc_data.items():
            if 'eur' in key.lower() or 'kwh' in key.lower():
                print(f"   {key}: {value}")

        overlay_bytes = generate_overlay(
            coords_dir=coords_dir,
            dynamic_data=real_calc_data,
            total_pages=8  # MIGRATION: Changed from 7 to 8
        )

        if overlay_bytes:
            output_file = "debug_real_calculation_keys.pdf"
            with open(output_file, "wb") as f:
                f.write(overlay_bytes)

            print(f"✅ Real-Calc-PDF erstellt: {output_file}")
        else:
            print("❌ Real-Calc-Test fehlgeschlagen")

    except Exception as e:
        print(f"❌ Fehler beim Real-Calc-Test: {e}")


if __name__ == "__main__":
    print("🚀 Debug der Wasserfall-Diagramm Datenquellen")
    print("=" * 50)

    # Test 1: Allgemeine Debug-Analyse
    debug_dynamic_data()

    # Test 2: Echte Berechnungs-Keys
    test_real_calculation_keys()

    print("\n📋 Zusammenfassung:")
    print("   - Schauen Sie in die Konsolen-Ausgabe nach DEBUG-Meldungen")
    print("   - Die PDFs zeigen ob die Werte korrekt erkannt werden")
    print("   - Falls Werte fehlen, müssen die Keys in der Wasserfall-Funktion angepasst werden")
