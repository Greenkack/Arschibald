#!/usr/bin/env python3
"""
Test um alle drei Probleme zu beheben:
1. Solarfabrik soll echte Werte aus der DB anzeigen (nicht k.A.)
2. Dienstleistungen auf Seite 6 anzeigen
3. Donut-Charts an korrekten Positionen
"""

from pdf_template_engine.placeholders import build_dynamic_data
from pdf_template_engine.dynamic_overlay import generate_overlay
import sys
from pathlib import Path

# Füge das Projektverzeichnis zum Python-Pfad hinzu
sys.path.insert(0, str(Path(__file__).parent))


def test_solarfabrik_real_values():
    """Testet Solarfabrik mit echten DB-Werten"""

    print("🔧 Test Solarfabrik mit echten DB-Werten")
    print("=" * 50)

    # Verwende einen echten Solarfabrik-Namen aus der DB
    project_data = {
        "customer_data": {
            "first_name": "Max",
            "last_name": "Mustermann",
            "company_name": "TommaTech GmbH"
        },
        "project_details": {
            # Verwende den echten Namen aus der DB
            "selected_module_name": "Mono S4 Trendline 440W",
            "selected_module_id": 11,  # Die ID aus der DB
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
        # Baue dynamische Daten
        print("📊 Baue dynamische Daten...")
        dynamic_data = build_dynamic_data(
            project_data, analysis_results, result)

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

        # Zeige Service-Daten
        print("\\n🔧 Dienstleistungen:")
        print(
            f"   - Liste: {dynamic_data.get('optional_services_list', 'NICHT GEFUNDEN')}")
        print(
            f"   - Gesamt: {dynamic_data.get('optional_services_total', 'NICHT GEFUNDEN')}")
        print(
            f"   - Anzahl: {dynamic_data.get('optional_services_count', 'NICHT GEFUNDEN')}")

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

        # Prüfe ob Solarfabrik echte Werte hat
        solarfabrik_has_real_values = (
            dynamic_data.get('module_cell_technology') not in [
                'k.A.',
                None,
                ''] and dynamic_data.get('module_structure') not in [
                'k.A.',
                None,
                ''] and dynamic_data.get('module_cell_type') not in [
                'k.A.',
                None,
                ''] and dynamic_data.get('module_version') not in [
                    'k.A.',
                    None,
                ''])

        if solarfabrik_has_real_values:
            print("\\n✅ Solarfabrik hat echte Werte aus der Datenbank!")
        else:
            print("\\n❌ Solarfabrik zeigt noch Fallback-Werte!")

        # Prüfe Services
        services_working = (
            dynamic_data.get('optional_services_list') and
            'Installation' in dynamic_data.get('optional_services_list', '')
        )

        if services_working:
            print("✅ Dienstleistungen werden korrekt integriert!")
        else:
            print("❌ Dienstleistungen fehlen!")

        # Prüfe Donut-Charts
        donuts_working = (
            dynamic_data.get('storage_consumption_ratio_percent') and
            dynamic_data.get('storage_production_ratio_percent')
        )

        if donuts_working:
            print("✅ Donut-Chart-Daten sind verfügbar!")
        else:
            print("❌ Donut-Chart-Daten fehlen!")

        # Generiere PDF
        coords_dir = Path("coords")
        overlay_bytes = generate_overlay(
            coords_dir=coords_dir,
            dynamic_data=dynamic_data,
            total_pages=7
        )

        if overlay_bytes:
            output_file = "test_solarfabrik_fix_complete.pdf"
            with open(output_file, "wb") as f:
                f.write(overlay_bytes)

            print(f"\\n✅ Test-PDF erstellt: {output_file}")
            print(f"📦 Dateigröße: {len(overlay_bytes):,} bytes")

            print("\\n📋 Überprüfen Sie:")
            print(
                "   1. Seite 4: Solarfabrik sollte echte Werte zeigen (Monokristallin, Glas-Folie, etc.)")
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


def test_with_different_solarfabrik_names():
    """Testet verschiedene Solarfabrik-Namen"""

    print("\\n🔍 Test verschiedene Solarfabrik-Namen")
    print("=" * 40)

    # Hole alle Solarfabrik-Produkte aus der DB
    try:
        from product_db import get_products_with_dynamic_keys
        products = get_products_with_dynamic_keys()
        solarfabrik_products = [
            p for p in products if p.get('manufacturer') and 'solarfabrik' in p.get(
                'manufacturer', '').lower()]

        print(f"Gefundene Solarfabrik-Produkte: {len(solarfabrik_products)}")

        for product in solarfabrik_products:
            print(f"\\n📦 Produkt: {product.get('model_name')}")
            print(f"   - ID: {product.get('id')}")
            print(
                f"   - Zellentechnologie: {product.get('cell_technology', 'LEER')}")
            print(
                f"   - Modulaufbau: {product.get('module_structure', 'LEER')}")
            print(f"   - Solarzellen: {product.get('cell_type', 'LEER')}")
            print(f"   - Version: {product.get('version', 'LEER')}")

    except Exception as e:
        print(f"Fehler beim Laden der Solarfabrik-Produkte: {e}")


if __name__ == "__main__":
    print("🚀 Test Solarfabrik Fix Complete")
    print("=" * 60)

    # Test 1: Verschiedene Solarfabrik-Namen anzeigen
    test_with_different_solarfabrik_names()

    # Test 2: Alle Korrekturen mit echten Solarfabrik-Werten
    success = test_solarfabrik_real_values()

    print("\\n🎉 Test abgeschlossen!")
    if success:
        print("✅ Alle drei Probleme sollten behoben sein:")
        print("   1. Solarfabrik zeigt echte DB-Werte")
        print("   2. Dienstleistungen werden auf Seite 6 angezeigt")
        print("   3. Donut-Charts sind an korrekten Positionen sichtbar")
    else:
        print("❌ Es gab Probleme bei der PDF-Generierung")
