#!/usr/bin/env python3
"""
Test des Wasserfall-Diagramms mit den korrekten dynamischen Keys
"""

from pdf_template_engine.dynamic_overlay import generate_overlay
from pypdf import PdfReader
import io
import sys
from pathlib import Path

# Füge das Projektverzeichnis zum Python-Pfad hinzu
sys.path.insert(0, str(Path(__file__).parent))


def test_correct_dynamic_keys():
    """Testet das Wasserfall-Diagramm mit den korrekten dynamischen Keys aus dem System"""

    print("[TOOL] Test mit korrekten dynamischen Keys")
    print("=" * 40)

    # Test-Szenarien mit den ECHTEN Keys aus dem System
    test_scenarios = [
        {
            "name": "Vollständige Berechnungsergebnisse",
            "data": {
                # ECHTE KEYS aus calculations.py und placeholders.py:
                "self_consumption_without_battery_eur": "1.450,75 €",  # Direktverbrauch -> "Direkt"
                # Einspeisevergütung -> "Einspeisung"
                "annual_feed_in_revenue_eur": "920,50 €",
                # Steuervorteile -> "platz1"
                "tax_benefits_eur": "380,25 €",
                "total_annual_savings_eur": "2.751,50 €",              # Gesamt -> "Gesamt"
            }
        },
        {
            "name": "Nur Direktverbrauch (andere Werte 0)",
            "data": {
                "self_consumption_without_battery_eur": "1.800,00 €",
                "annual_feed_in_revenue_eur": "0,00 €",
                "tax_benefits_eur": "0,00 €",
                "total_annual_savings_eur": "1.800,00 €",
            }
        },
        {
            "name": "Hohe Einspeisevergütung",
            "data": {
                "self_consumption_without_battery_eur": "800,00 €",
                "annual_feed_in_revenue_eur": "2.200,00 €",
                "tax_benefits_eur": "924,00 €",
                "total_annual_savings_eur": "3.924,00 €",
            }
        },
        {
            "name": "Niedrige Werte",
            "data": {
                "self_consumption_without_battery_eur": "450,50 €",
                "annual_feed_in_revenue_eur": "280,75 €",
                "tax_benefits_eur": "117,92 €",
                "total_annual_savings_eur": "849,17 €",
            }
        }
    ]

    for i, scenario in enumerate(test_scenarios):
        print(f"\n=== Test {i + 1}: {scenario['name']} ===")

        # Basis-Daten für alle Tests
        dynamic_data = {
            **scenario['data'],
            "company_name": "TommaTech GmbH",
            "page_number": "3",
            "total_pages": "7",

            # Zusätzliche Daten für vollständige PDF
            "anlage_kwp": "8,5 kWp",
            "annual_pv_production_kwh": "8.251,92 kWh",
            "self_supply_rate_percent": "65%",
            "self_consumption_percent": "45%",
        }

        try:
            # Generiere Overlay
            coords_dir = Path("coords")
            overlay_bytes = generate_overlay(
                coords_dir=coords_dir,
                dynamic_data=dynamic_data,
                total_pages=7
            )

            if overlay_bytes:
                # Speichere Test-PDF
                output_file = f"test_wasserfall_correct_{
                    i + 1}_{
                    scenario['name'].lower().replace(
                        ' ', '_').replace(
                        '(', '').replace(
                        ')', '')}.pdf"
                with open(output_file, "wb") as f:
                    f.write(overlay_bytes)

                print(f"[OK] PDF erstellt: {output_file}")
                print(f"[PACKAGE] Größe: {len(overlay_bytes):,} bytes")

                # Zeige verwendete Werte
                print("[CHART] Wasserfall-Werte:")
                print(
                    f"   - Direktverbrauch: {scenario['data']['self_consumption_without_battery_eur']}")
                print(
                    f"   - Einspeisevergütung: {scenario['data']['annual_feed_in_revenue_eur']}")
                print(
                    f"   - Steuervorteile: {scenario['data']['tax_benefits_eur']}")
                print(
                    f"   - Gesamt: {scenario['data']['total_annual_savings_eur']}")

                # Prüfe PDF-Struktur
                try:
                    reader = PdfReader(io.BytesIO(overlay_bytes))
                    if len(reader.pages) >= 3:
                        print(
                            "[FILE] Seite 3 verfügbar - Wasserfall-Diagramm sollte sichtbar sein")
                except Exception as e:
                    print(f"[WARNING] PDF-Struktur-Prüfung fehlgeschlagen: {e}")

            else:
                print(
                    f"[ERROR] Overlay-Generierung fehlgeschlagen für Szenario {i + 1}")

        except Exception as e:
            print(f"[ERROR] Fehler bei Szenario {i + 1}: {e}")
            import traceback
            traceback.print_exc()


def test_position_verification():
    """Verifiziert die 20-Punkte-Verschiebung nach oben"""

    print("\n[SEARCH] Verifikation der Position (20 Punkte höher)")
    print("=" * 45)

    # Test-Daten
    dynamic_data = {
        "self_consumption_without_battery_eur": "1.200,00 €",
        "annual_feed_in_revenue_eur": "800,00 €",
        "tax_benefits_eur": "336,00 €",
        "total_annual_savings_eur": "2.336,00 €",
        "company_name": "TommaTech GmbH"
    }

    try:
        coords_dir = Path("coords")
        overlay_bytes = generate_overlay(
            coords_dir=coords_dir,
            dynamic_data=dynamic_data,
            total_pages=7
        )

        if overlay_bytes:
            output_file = "test_wasserfall_position_verification.pdf"
            with open(output_file, "wb") as f:
                f.write(overlay_bytes)

            print(f"[OK] Position-Test-PDF erstellt: {output_file}")
            print(
                "📍 Das Diagramm sollte 20 Punkte höher als in der ursprünglichen Version sein")
            print("[CHART] Alle 4 Balken sollten sichtbar sein:")
            print("   1. Direktverbrauch: 1.200,00 €")
            print("   2. Einspeisevergütung: 800,00 €")
            print("   3. Steuervorteile: 336,00 €")
            print("   4. Gesamt: 2.336,00 €")
        else:
            print("[ERROR] Position-Test fehlgeschlagen")

    except Exception as e:
        print(f"[ERROR] Fehler beim Position-Test: {e}")


if __name__ == "__main__":
    print("[LAUNCH] Test des Wasserfall-Diagramms mit korrekten dynamischen Keys")
    print("=" * 65)

    # Test 1: Verschiedene Werte-Szenarien
    test_correct_dynamic_keys()

    # Test 2: Position-Verifikation
    test_position_verification()

    print("\n🎉 Alle Tests abgeschlossen!")
    print("📋 Überprüfen Sie die generierten PDF-Dateien:")
    print("   [OK] Alle 4 Balken sollten sichtbar sein (inklusive Direktverbrauch)")
    print("   [OK] Das Diagramm sollte 20 Punkte höher positioniert sein")
    print("   [OK] Echte dynamische Werte aus dem System werden verwendet")
    print("📍 Keys verwendet:")
    print("   - self_consumption_without_battery_eur (Direktverbrauch)")
    print("   - annual_feed_in_revenue_eur (Einspeisevergütung)")
    print("   - tax_benefits_eur (Steuervorteile)")
    print("   - total_annual_savings_eur (Gesamt)")
