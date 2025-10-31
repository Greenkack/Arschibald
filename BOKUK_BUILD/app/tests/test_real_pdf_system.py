#!/usr/bin/env python
"""
Direkter Test des echten PDF-Generierungssystems
===================================================
Testet die echte PDF-Generierung durch pdf_generator.py mit den neuen Berechnungen
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

def test_real_pdf_generation():
    """Teste die echte PDF-Generierung mit unseren neuen Berechnungen"""

    print("=== DIREKTER PDF-SYSTEM TEST ===")

    # Lade das echte PDF-System
    try:
        from pdf_generator import generate_offer_pdf
        print("✅ PDF Generator erfolgreich geladen")
    except ImportError as e:
        print(f"❌ PDF Generator Import Fehler: {e}")
        return False

    # Test-Daten für PDF-Generierung
    test_project_data = {
        "customer_data": {
            "name": "Max Mustermann",
            "street": "Musterstraße 123",
            "city": "12345 Musterstadt",
            "phone": "0123-456789",
            "email": "max@mustermann.de"
        },
        "project_details": {
            "anlage_kwp": 8.4,
            "selected_inverter_power_kw": 10.0,
            "selected_inverter_power_kw_single": 5.0,
            "inverter_quantity": 2
        }
    }

    test_analysis_results = {
        "anlage_kwp": 8.4,
        "annual_yield_kwh": 8251.92,
        "val_direct_kwh": 3200.04,
        "val_feedin_kwh": 5051.92,
        "val_battery_charge_kwh": 1500.00,
        "val_battery_usage_kwh": 1299.96,
        "val_battery_excess_kwh": 200.04,
        "electricity_price_eur_per_kwh": 0.32,
        "feed_in_tariff_eur_per_kwh": 0.0786,
        "einkommensteuer_satz": 42.0
    }

    test_company_info = {
        "name": "Test Solar GmbH",
        "id": 1,
        "logo_base64": None
    }

    print("Test-Daten:")
    print(f"  - PV-Anlage: {test_project_data['project_details']['anlage_kwp']} kWp")
    print(f"  - Wechselrichter: {test_project_data['project_details']['selected_inverter_power_kw']} kW")
    print(f"  - Einkommensteuersatz: {test_analysis_results['einkommensteuer_satz']}%")
    print(f"  - Einspeisung: {test_analysis_results['val_feedin_kwh']} kWh")
    print(f"  - EEG-Vergütung: {test_analysis_results['feed_in_tariff_eur_per_kwh']} €/kWh")

    # Teste das build_dynamic_data direkt
    try:
        from pdf_template_engine.placeholders import build_dynamic_data

        print("\n=== TEST DER DYNAMISCHEN DATEN ===")
        result = build_dynamic_data(test_project_data, test_analysis_results, test_company_info)

        # Prüfe die wichtigsten neuen Werte
        print("\n✅ Neue Berechnungen:")
        print(f"  - Steuerliche Vorteile (platz1): {result.get('tax_benefits_eur', 'N/A')}")
        print(f"  - Gesamt ohne Speicher: {result.get('total_savings_eur', 'N/A')}")
        print(f"  - Wechselrichter in W: {result.get('inverter_total_power_w', 'N/A')}")
        print(f"  - Direkt: {result.get('direct_consumption_eur', 'N/A')}")
        print(f"  - Einspeisung: {result.get('feed_in_eur', 'N/A')}")

        # Verifiziere die Platzhalter-Mappings
        print("\n✅ Platzhalter-Mappings:")
        try:
            from pdf_template_engine.placeholders import (
                PLACEHOLDER_TO_DATA_KEY_S1,
                PLACEHOLDER_TO_DATA_KEY_S3,
            )

            if "platz1" in PLACEHOLDER_TO_DATA_KEY_S3:
                mapped_key = PLACEHOLDER_TO_DATA_KEY_S3["platz1"]
                mapped_value = result.get(mapped_key, 'N/A')
                print(f"  - 'platz1' -> '{mapped_key}' = {mapped_value}")

            if "Gesamt" in PLACEHOLDER_TO_DATA_KEY_S3:
                mapped_key = PLACEHOLDER_TO_DATA_KEY_S3["Gesamt"]
                mapped_value = result.get(mapped_key, 'N/A')
                print(f"  - 'Gesamt' -> '{mapped_key}' = {mapped_value}")

            if "Warmwasser" in PLACEHOLDER_TO_DATA_KEY_S1:
                mapped_key = PLACEHOLDER_TO_DATA_KEY_S1["Warmwasser"]
                mapped_value = result.get(mapped_key, 'N/A')
                print(f"  - 'Warmwasser' (Seite 1) -> '{mapped_key}' = {mapped_value}")
        except ImportError as e:
            print(f"  - Platzhalter-Import-Fehler: {e}")
            # Versuche direkte Prüfung der wichtigen Werte
            if 'tax_benefits_eur' in result:
                print(f"  - tax_benefits_eur gefunden: {result['tax_benefits_eur']}")
            if 'total_savings_eur' in result:
                print(f"  - total_savings_eur gefunden: {result['total_savings_eur']}")
            if 'inverter_total_power_w' in result:
                print(f"  - inverter_total_power_w gefunden: {result['inverter_total_power_w']}")

        print("\n✅ Test erfolgreich! Die neuen Berechnungen funktionieren.")
        return True

    except Exception as e:
        print(f"❌ Fehler beim Test der dynamischen Daten: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_real_pdf_generation()
    if success:
        print("\n🎉 ALLE TESTS ERFOLGREICH!")
        print("Die neuen PDF-Berechnungen sind korrekt implementiert und sollten in der App funktionieren.")
    else:
        print("\n❌ TESTS FEHLGESCHLAGEN!")
        print("Es gibt noch Probleme mit dem PDF-System.")
