#!/usr/bin/env python3
"""
Test der korrigierten Wasserfall-Diagramm Implementation
"""

from pdf_template_engine.dynamic_overlay import generate_overlay
from pypdf import PdfReader
import io
import sys
from pathlib import Path

# Füge das Projektverzeichnis zum Python-Pfad hinzu
sys.path.insert(0, str(Path(__file__).parent))


def test_fixed_waterfall():
    """Testet das korrigierte Wasserfall-Diagramm"""

    print("🔧 Test des korrigierten Wasserfall-Diagramms")
    print("=" * 50)

    # Test-Szenarien mit verschiedenen Daten-Kombinationen
    test_scenarios = [
        {
            "name": "Alle Werte vorhanden",
            "data": {
                "einsparung_direktverbrauch_eur": "1450.75",
                "einnahmen_einspeisung_eur": "920.50",
                "vorteile_steuerfrei_eur": "380.25",
                "gesamt_ertraege_jahr_eur": "2751.50"
            },
            "expected_bars": 4
        },
        {
            "name": "Direktverbrauch = 0",
            "data": {
                "einsparung_direktverbrauch_eur": "0",
                "einnahmen_einspeisung_eur": "920.50",
                "vorteile_steuerfrei_eur": "380.25",
                "gesamt_ertraege_jahr_eur": "1300.75"
            },
            "expected_bars": 4
        },
        {
            "name": "Nur Direktverbrauch",
            "data": {
                "einsparung_direktverbrauch_eur": "1500.00",
                "einnahmen_einspeisung_eur": "0",
                "vorteile_steuerfrei_eur": "0",
                "gesamt_ertraege_jahr_eur": "1500.00"
            },
            "expected_bars": 4
        },
        {
            "name": "Alternative Keys",
            "data": {
                "self_consumption_without_battery_eur": "1200.00",
                "annual_feed_in_revenue_eur": "800.00",
                "tax_benefits_eur": "300.00",
                "total_annual_savings_eur": "2300.00"
            },
            "expected_bars": 4
        }
    ]

    for i, scenario in enumerate(test_scenarios):
        print(f"\n=== Test {i + 1}: {scenario['name']} ===")

        # Basis-Daten für alle Tests
        dynamic_data = {
            **scenario['data'],
            "company_name": "TommaTech GmbH",
            "page_number": "3",
            "total_pages": "7"
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
                output_file = f"test_wasserfall_fixed_{
                    i + 1}_{
                    scenario['name'].lower().replace(
                        ' ', '_')}.pdf"
                with open(output_file, "wb") as f:
                    f.write(overlay_bytes)

                print(f"✅ PDF erstellt: {output_file}")
                print(f"📦 Größe: {len(overlay_bytes):,} bytes")

                # Zeige Daten-Details
                print("📊 Daten:")
                for key, value in scenario['data'].items():
                    if 'eur' in key.lower():
                        print(f"   - {key}: {value}€")

                # Prüfe PDF-Struktur
                try:
                    reader = PdfReader(io.BytesIO(overlay_bytes))
                    if len(reader.pages) >= 3:
                        print("📄 Seite 3 verfügbar für Wasserfall-Diagramm")
                except Exception as e:
                    print(f"⚠️ PDF-Struktur-Prüfung fehlgeschlagen: {e}")

            else:
                print(
                    f"❌ Overlay-Generierung fehlgeschlagen für Szenario {i + 1}")

        except Exception as e:
            print(f"❌ Fehler bei Szenario {i + 1}: {e}")
            import traceback
            traceback.print_exc()


def test_position_shift():
    """Testet die 20-Punkte-Verschiebung nach oben"""

    print("\n🔧 Test der Position-Verschiebung")
    print("=" * 35)

    # Berechne die neuen Koordinaten
    page_height = 841.8897637795277  # A4 Höhe

    # Alte Koordinaten (10 Punkte oberhalb)
    old_chart_top = page_height - (516.11 - 10)
    old_chart_bottom = page_height - (645.42 - 10)

    # Neue Koordinaten (30 Punkte oberhalb = 20 Punkte höher)
    new_chart_top = page_height - (516.11 - 30)
    new_chart_bottom = page_height - (645.42 - 30)

    print("📍 Koordinaten-Vergleich:")
    print("   Alte Position:")
    print(f"     - Oben: {old_chart_top:.1f}")
    print(f"     - Unten: {old_chart_bottom:.1f}")
    print(f"     - Höhe: {old_chart_top - old_chart_bottom:.1f}")

    print("   Neue Position (20 Punkte höher):")
    print(f"     - Oben: {new_chart_top:.1f}")
    print(f"     - Unten: {new_chart_bottom:.1f}")
    print(f"     - Höhe: {new_chart_top - new_chart_bottom:.1f}")

    print("   Verschiebung:")
    print(f"     - Oben: {new_chart_top - old_chart_top:.1f} Punkte")
    print(f"     - Unten: {new_chart_bottom - old_chart_bottom:.1f} Punkte")

    # Test mit Daten
    dynamic_data = {
        "einsparung_direktverbrauch_eur": "1000.00",
        "einnahmen_einspeisung_eur": "750.00",
        "vorteile_steuerfrei_eur": "250.00",
        "gesamt_ertraege_jahr_eur": "2000.00",
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
            output_file = "test_wasserfall_position_shift.pdf"
            with open(output_file, "wb") as f:
                f.write(overlay_bytes)

            print(f"✅ Test-PDF mit neuer Position erstellt: {output_file}")
            print("📋 Das Diagramm sollte 20 Punkte höher als vorher positioniert sein")
        else:
            print("❌ Position-Test fehlgeschlagen")

    except Exception as e:
        print(f"❌ Fehler beim Position-Test: {e}")


if __name__ == "__main__":
    print("🚀 Test der korrigierten Wasserfall-Diagramm Implementation")
    print("=" * 65)

    # Test 1: Verschiedene Daten-Szenarien
    test_fixed_waterfall()

    # Test 2: Position-Verschiebung
    test_position_shift()

    print("\n🎉 Alle Tests abgeschlossen!")
    print("📋 Überprüfen Sie die generierten PDF-Dateien:")
    print("   - Alle 4 Balken sollten sichtbar sein (auch bei Wert 0)")
    print("   - Das Diagramm sollte 20 Punkte höher positioniert sein")
    print("   - Direktverbrauch-Balken sollte immer angezeigt werden")
    print("📍 Position: Zwischen 'Neigung des Daches' und 'Art' Spalten, 20 Punkte höher")
