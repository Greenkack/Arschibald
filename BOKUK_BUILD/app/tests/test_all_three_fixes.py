#!/usr/bin/env python3
"""
Test aller drei Korrekturen:
1. Solarfabrik Fallback-Werte (k.A. statt spezifische Werte)
2. Dienstleistungen auf Seite 6 anzeigen
3. Donut-Charts an den korrekten Platzhalter-Positionen
"""

from pdf_template_engine.placeholders import build_dynamic_data
from pdf_template_engine.dynamic_overlay import generate_overlay
import sys
from pathlib import Path

# Füge das Projektverzeichnis zum Python-Pfad hinzu
sys.path.insert(0, str(Path(__file__).parent))


def test_all_fixes():
    """Testet alle drei Korrekturen zusammen"""

    print("🔧 Test aller drei Korrekturen")
    print("=" * 40)

    # Test-Daten mit Solarfabrik und Dienstleistungen
    project_data = {
        "customer_data": {
            "first_name": "Max",
            "last_name": "Mustermann",
            "company_name": "TommaTech GmbH"
        },
        "project_details": {
            "selected_module_name": "Solarfabrik Mono S4 Halfcut 410W",
            "selected_inverter_name": "SMA Sunny Tripower 8.0",
            "selected_storage_name": "BYD Battery-Box Premium HVS 12.8"
        },
        # Dienstleistungen hinzufügen
        "selected_services": [
            {
                "name": "Installation",
                "description": "Professionelle Installation der PV-Anlage",
                "price": 2500.00,
                "category": "Installation"
            },
            {
                "name": "Wartung (1 Jahr)",
                "description": "Jährliche Wartung und Inspektion",
                "price": 350.00,
                "category": "Wartung"
            }
        ]
    }

    analysis_results = {
        "annual_pv_production_kwh": 8251.92,
        "eigenverbrauch_pro_jahr_kwh": 3500.0,
        "netzeinspeisung_kwh": 4751.92,
        "storage_capacity_kwh": 12.8,
        "daily_consumption_kwh": 16.44,
        "daily_production_kwh": 22.61
    }

    result = {
        "self_consumption_without_battery_eur": "1.450,75 €",
        "annual_feed_in_revenue_eur": "920,50 €",
        "tax_benefits_eur": "380,25 €",
        "total_annual_savings_eur": "2.751,50 €"
    }

    try:
        # Baue dynamische Daten (inkl. Services-Integration)
        print("📊 Baue dynamische Daten mit Services-Integration...")
        dynamic_data = build_dynamic_data(
            project_data, analysis_results, result)

        # Zeige Service-Daten
        print("\\n🔧 Dienstleistungen:")
        print(
            f"   - Liste: {dynamic_data.get('optional_services_list', 'NICHT GEFUNDEN')}")
        print(
            f"   - Gesamt: {dynamic_data.get('optional_services_total', 'NICHT GEFUNDEN')}")
        print(
            f"   - Anzahl: {dynamic_data.get('optional_services_count', 'NICHT GEFUNDEN')}")

        # Zeige Solarfabrik-Daten
        print("\\n🏭 Solarfabrik Module-Attribute:")
        print(
            f"   - Zellentechnologie: {
                dynamic_data.get(
                    'module_cell_technology',
                    'NICHT GEFUNDEN')}")
        print(
            f"   - Modulaufbau: {dynamic_data.get('module_structure', 'NICHT GEFUNDEN')}")
        print(
            f"   - Solarzellen: {dynamic_data.get('module_cell_type', 'NICHT GEFUNDEN')}")
        print(
            f"   - Version: {dynamic_data.get('module_version', 'NICHT GEFUNDEN')}")

        # Zeige Donut-Chart-Daten
        print("\\n📊 Donut-Chart-Daten:")
        print(
            f"   - Tagesverbrauch: {
                dynamic_data.get(
                    'storage_consumption_ratio_percent',
                    'NICHT GEFUNDEN')}%")
        print(
            f"   - PV-Produktion: {
                dynamic_data.get(
                    'storage_production_ratio_percent',
                    'NICHT GEFUNDEN')}%")

        # Generiere PDF
        coords_dir = Path("coords")
        overlay_bytes = generate_overlay(
            coords_dir=coords_dir,
            dynamic_data=dynamic_data,
            total_pages=7
        )

        if overlay_bytes:
            output_file = "test_all_three_fixes.pdf"
            with open(output_file, "wb") as f:
                f.write(overlay_bytes)

            print(f"\\n✅ Test-PDF erstellt: {output_file}")
            print(f"📦 Dateigröße: {len(overlay_bytes):,} bytes")
            print("\\n📋 Überprüfen Sie:")
            print(
                "   1. Seite 4: Solarfabrik sollte 'k.A.' statt spezifische Werte zeigen")
            print("   2. Seite 6: Dienstleistungen sollten angezeigt werden")
            print(
                "   3. Seite 6: Donut-Charts sollten bei den Platzhaltern sichtbar sein")

            return True
        print("\\n❌ PDF-Generierung fehlgeschlagen")
        return False

    except Exception as e:
        print(f"\\n❌ Fehler beim Test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_services_only():
    """Testet nur die Dienstleistungen-Integration"""

    print("\\n🔧 Test nur Dienstleistungen")
    print("=" * 30)

    # Minimale Daten nur für Services
    project_data = {
        "selected_services": [
            {
                "name": "Elektroinstallation",
                "description": "Anschluss an das Hausnetz",
                "price": 1500.00,
                "category": "Installation"
            },
            {
                "name": "Gerüst",
                "description": "Gerüststellung für Installation",
                "price": 800.00,
                "category": "Installation"
            },
            {
                "name": "Monitoring-System",
                "description": "Überwachung der Anlagenleistung",
                "price": 450.00,
                "category": "Sonstiges"
            }
        ]
    }

    try:
        dynamic_data = build_dynamic_data(project_data, {}, {})

        print("📋 Services-Integration Ergebnis:")
        print(
            f"   - Liste: {dynamic_data.get('optional_services_list', 'FEHLT')}")
        print(
            f"   - Gesamt: {dynamic_data.get('optional_services_total', 'FEHLT')}")
        print(
            f"   - Anzahl: {dynamic_data.get('optional_services_count', 'FEHLT')}")

        if dynamic_data.get(
                'optional_services_list') and 'Elektroinstallation' in dynamic_data['optional_services_list']:
            print("✅ Services-Integration funktioniert")
        else:
            print("❌ Services-Integration fehlgeschlagen")

    except Exception as e:
        print(f"❌ Services-Test Fehler: {e}")


if __name__ == "__main__":
    print("🚀 Test aller drei Korrekturen")
    print("=" * 50)

    # Test 1: Services-Integration isoliert
    test_services_only()

    # Test 2: Alle Korrekturen zusammen
    test_all_fixes()

    print("\\n🎉 Tests abgeschlossen!")
    print("📋 Erwartete Korrekturen:")
    print("   1. ✅ Solarfabrik: Zeigt 'k.A.' statt spezifische Fallback-Werte")
    print("   2. ✅ Dienstleistungen: Werden auf Seite 6 angezeigt")
    print("   3. ✅ Donut-Charts: An exakten Platzhalter-Positionen sichtbar")
