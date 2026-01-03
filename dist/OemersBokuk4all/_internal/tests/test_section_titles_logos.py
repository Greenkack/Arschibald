#!/usr/bin/env python3
"""
Test für erweiterte Überschriften auf Seite 4 und Logo-System
"""

from pdf_template_engine.placeholders import build_dynamic_data
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_section_titles_and_logos():
    """Teste die erweiterten Überschriften und Logo-Integration"""
    print("TESTE ERWEITERTE ÜBERSCHRIFTEN & LOGOS")
    print("=" * 60)

    # Test-Daten mit allen notwendigen Werten
    project_data = {
        "customer_data": {
            "first_name": "Max",
            "last_name": "Mustermann"
        },
        "project_details": {
            "module_quantity": 20,
            "selected_inverter_power_kw": 10.5,  # 10,5 kW = 10.500 W
            "selected_storage_capacity_kwh": 15.6  # 15,6 kWh
        },
        "selected_products": {
            "module": {
                "product_id": 1,
                "brand_name": "Huawei",
                "product_name": "SUN2000-8KTL-M1"
            },
            "inverter": {
                "product_id": 2,
                "brand_name": "GoodWe",
                "product_name": "GW8K-ET"
            },
            "storage": {
                "product_id": 3,
                "brand_name": "BYD",
                "product_name": "Battery-Box Premium HVM"
            }
        }
    }

    analysis_results = {
        "total_investment_netto": 25000,
        "anlage_kwp": 8.5,
        "annual_pv_production_kwh": 8500
    }

    company_info = {
        "name": "Solar GmbH"
    }

    print("Erstelle dynamic_data...")
    dynamic_data = build_dynamic_data(
        project_data, analysis_results, company_info)

    print("\nERWEITERTE ÜBERSCHRIFTEN:")
    section_titles = [
        ("module_section_title", "SOLARMODULE"),
        ("inverter_section_title", "WECHSELRICHTER"),
        ("storage_section_title", "BATTERIESPEICHER")
    ]

    for key, title in section_titles:
        if key in dynamic_data:
            value = dynamic_data[key]
            print(f"  {title}: '{value}'")
        else:
            print(f"  {title}: FEHLT")

    print("\n LOGO-DATEN:")
    logo_keys = [
        ("module_brand_logo_b64", "PV-Module"),
        ("inverter_brand_logo_b64", "Wechselrichter"),
        ("storage_brand_logo_b64", "Batteriespeicher")
    ]

    for key, component in logo_keys:
        if key in dynamic_data and dynamic_data[key]:
            print(
                f"  {component}: Logo vorhanden ({len(dynamic_data[key])} Zeichen)")
        else:
            print(f"  {component}: Kein Logo")

    print("\n ZUSÄTZLICHE WERTE:")
    extra_keys = [
        ("module_quantity", "Module Anzahl"),
        ("inverter_total_power_kw", "WR Gesamtleistung"),
        ("storage_capacity_kwh", "Speicher Kapazität")
    ]

    for key, label in extra_keys:
        if key in dynamic_data:
            print(f"  {label}: {dynamic_data[key]}")
        else:
            print(f"  {label}: FEHLT")

    print("\n" + "=" * 60)
    print("ZUSAMMENFASSUNG:")

    sections_ok = all(key in dynamic_data for key, _ in section_titles)
    logos_ok = all(
        key in dynamic_data and dynamic_data[key] for key,
        _ in logo_keys)

    if sections_ok:
        print("Alle erweiterten Überschriften sind verfügbar")
    else:
        print("Einige Überschriften fehlen")

    if logos_ok:
        print("Alle Logos sind verfügbar")
    else:
        print("Einige Logos fehlen (normal wenn nicht alle Hersteller Logos haben)")

    return sections_ok and logos_ok


if __name__ == "__main__":
    success = test_section_titles_and_logos()
    if success:
        print("\n TEST ERFOLGREICH!")
        print(
            "Die erweiterten Überschriften und Logos sollten jetzt in der PDF erscheinen!")
    else:
        print("\nTest teilweise erfolgreich - prüfe die Details oben")
