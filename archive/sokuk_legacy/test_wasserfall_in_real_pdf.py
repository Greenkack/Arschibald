#!/usr/bin/env python3
"""
Test des Wasserfall-Diagramms in der echten PDF-Generierung
"""

from pdf_generator import generate_main_template_pdf_bytes
import sys
from pathlib import Path

# Füge das Projektverzeichnis zum Python-Pfad hinzu
sys.path.insert(0, str(Path(__file__).parent))


def test_real_pdf_with_waterfall():
    """Testet das Wasserfall-Diagramm in der echten PDF-Generierung"""

    print("🔧 Test des Wasserfall-Diagramms in echter PDF")
    print("=" * 50)

    # Test-Daten für die PDF-Generierung
    test_data = {
        # Grundlegende Projektdaten
        "company_name": "TommaTech GmbH",
        "customer_name": "Max Mustermann",
        "project_name": "PV-Anlage Mustermann",

        # Wasserfall-Diagramm Daten
        "einsparung_direktverbrauch_eur": "1450.75",
        "einnahmen_einspeisung_eur": "920.50",
        "vorteile_steuerfrei_eur": "380.25",
        "gesamt_ertraege_jahr_eur": "2751.50",

        # Alternative Keys (falls die obigen nicht funktionieren)
        "self_consumption_without_battery_eur": "1450.75",
        "annual_feed_in_revenue_eur": "920.50",
        "tax_benefits_eur": "380.25",
        "total_annual_savings_eur": "2751.50",

        # Weitere Daten für vollständige PDF
        "anlage_kwp": "8.5",
        "annual_pv_production_kwh": "8500",
        "self_supply_rate_percent": "65%",
        "self_consumption_percent": "45%",
        "amortization_time": "12 Jahre",
        "final_price_netto": "15500.00",
        "final_price_brutto": "18445.00",

        # Seite 6 Speicher-Relationen
        "storage_consumption_ratio_percent": "74",
        "storage_production_ratio_percent": "53",

        # Weitere Platzhalter
        "page_number": "3",
        "total_pages": "7",
        "roof_orientation": "Süd",
        "roof_inclination": "30°",
        "roof_type": "Standard",
        "electricity_price": "0.32 €/kWh",
        "feed_in_tariff": "0.082 €/kWh",
        "financing_needed": "Nein"
    }

    try:
        # Generiere PDF mit Overlay
        print("📄 Generiere PDF mit Wasserfall-Diagramm...")

        # Erstelle project_data im erwarteten Format
        project_data = {
            "customer_data": {
                "first_name": "Max",
                "last_name": "Mustermann",
                "company_name": test_data.get("company_name", "TommaTech GmbH")
            },
            "project_details": {
                "project_name": test_data.get("project_name", "PV-Anlage Test")
            }
        }

        # Erstelle analysis_results mit den Wasserfall-Daten
        analysis_results = {
            "einsparung_direktverbrauch_eur": test_data.get("einsparung_direktverbrauch_eur"),
            "einnahmen_einspeisung_eur": test_data.get("einnahmen_einspeisung_eur"),
            "vorteile_steuerfrei_eur": test_data.get("vorteile_steuerfrei_eur"),
            "gesamt_ertraege_jahr_eur": test_data.get("gesamt_ertraege_jahr_eur"),
            "self_consumption_without_battery_eur": test_data.get("self_consumption_without_battery_eur"),
            "annual_feed_in_revenue_eur": test_data.get("annual_feed_in_revenue_eur"),
            "tax_benefits_eur": test_data.get("tax_benefits_eur"),
            "total_annual_savings_eur": test_data.get("total_annual_savings_eur"),
            "storage_consumption_ratio_percent": test_data.get("storage_consumption_ratio_percent"),
            "storage_production_ratio_percent": test_data.get("storage_production_ratio_percent"),
            "anlage_kwp": test_data.get("anlage_kwp"),
            "annual_pv_production_kwh": test_data.get("annual_pv_production_kwh")}

        pdf_bytes = generate_main_template_pdf_bytes(
            project_data=project_data,
            analysis_results=analysis_results,
            result=test_data  # Zusätzliche Daten
        )

        if pdf_bytes:
            # Speichere PDF
            output_file = "test_wasserfall_real_pdf.pdf"
            with open(output_file, "wb") as f:
                f.write(pdf_bytes)

            print(f"✅ PDF erfolgreich erstellt: {output_file}")
            print(f"📦 Dateigröße: {len(pdf_bytes):,} bytes")
            print("📋 Das Wasserfall-Diagramm sollte auf Seite 3 sichtbar sein")
            print("📍 Position: Zwischen 'Neigung des Daches' und 'Art' Spalten")
            print(
                f"📊 Daten: Direktverbrauch={
                    test_data['einsparung_direktverbrauch_eur']}€, " f"Einspeisung={
                    test_data['einnahmen_einspeisung_eur']}€, " f"Steuer={
                    test_data['vorteile_steuerfrei_eur']}€")

            return True
        print("❌ PDF-Generierung fehlgeschlagen - keine Bytes erhalten")
        return False

    except Exception as e:
        print(f"❌ Fehler bei der PDF-Generierung: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_different_waterfall_values():
    """Testet verschiedene Werte für das Wasserfall-Diagramm"""

    print("\n🔧 Test verschiedener Wasserfall-Werte")
    print("=" * 40)

    test_scenarios = [
        {
            "name": "Hohe Erträge",
            "data": {
                "einsparung_direktverbrauch_eur": "2500.00",
                "einnahmen_einspeisung_eur": "1800.00",
                "vorteile_steuerfrei_eur": "650.00",
                "gesamt_ertraege_jahr_eur": "4950.00"
            }
        },
        {
            "name": "Mittlere Erträge",
            "data": {
                "einsparung_direktverbrauch_eur": "1200.00",
                "einnahmen_einspeisung_eur": "850.00",
                "vorteile_steuerfrei_eur": "320.00",
                "gesamt_ertraege_jahr_eur": "2370.00"
            }
        },
        {
            "name": "Niedrige Erträge",
            "data": {
                "einsparung_direktverbrauch_eur": "450.00",
                "einnahmen_einspeisung_eur": "280.00",
                "vorteile_steuerfrei_eur": "120.00",
                "gesamt_ertraege_jahr_eur": "850.00"
            }
        }
    ]

    base_data = {
        "company_name": "TommaTech GmbH",
        "customer_name": "Max Mustermann",
        "project_name": "PV-Anlage Test",
        "anlage_kwp": "8.5",
        "annual_pv_production_kwh": "8500",
        "self_supply_rate_percent": "65%",
        "self_consumption_percent": "45%",
        "page_number": "3",
        "total_pages": "7"
    }

    for i, scenario in enumerate(test_scenarios):
        print(f"\n📊 Szenario {i + 1}: {scenario['name']}")

        # Kombiniere Basis-Daten mit Szenario-Daten
        test_data = {**base_data, **scenario['data']}

        try:
            # Erstelle project_data im erwarteten Format
            project_data = {
                "customer_data": {
                    "first_name": "Max",
                    "last_name": "Mustermann",
                    "company_name": test_data.get(
                        "company_name",
                        "TommaTech GmbH")},
                "project_details": {
                    "project_name": test_data.get(
                        "project_name",
                        "PV-Anlage Test")}}

            # Erstelle analysis_results mit den Wasserfall-Daten
            analysis_results = {
                "einsparung_direktverbrauch_eur": test_data.get("einsparung_direktverbrauch_eur"),
                "einnahmen_einspeisung_eur": test_data.get("einnahmen_einspeisung_eur"),
                "vorteile_steuerfrei_eur": test_data.get("vorteile_steuerfrei_eur"),
                "gesamt_ertraege_jahr_eur": test_data.get("gesamt_ertraege_jahr_eur"),
                "self_consumption_without_battery_eur": test_data.get("self_consumption_without_battery_eur"),
                "annual_feed_in_revenue_eur": test_data.get("annual_feed_in_revenue_eur"),
                "tax_benefits_eur": test_data.get("tax_benefits_eur"),
                "total_annual_savings_eur": test_data.get("total_annual_savings_eur"),
                "storage_consumption_ratio_percent": test_data.get("storage_consumption_ratio_percent"),
                "storage_production_ratio_percent": test_data.get("storage_production_ratio_percent"),
                "anlage_kwp": test_data.get("anlage_kwp"),
                "annual_pv_production_kwh": test_data.get("annual_pv_production_kwh")}

            pdf_bytes = generate_main_template_pdf_bytes(
                project_data=project_data,
                analysis_results=analysis_results,
                result=test_data  # Zusätzliche Daten
            )

            if pdf_bytes:
                output_file = f"test_wasserfall_scenario_{
                    i + 1}_{
                    scenario['name'].lower().replace(
                        ' ', '_')}.pdf"
                with open(output_file, "wb") as f:
                    f.write(pdf_bytes)

                print(f"  ✅ PDF erstellt: {output_file}")
                print(f"  📦 Größe: {len(pdf_bytes):,} bytes")
                print(
                    f"  💰 Werte: {
                        scenario['data']['einsparung_direktverbrauch_eur']}€ + " f"{
                        scenario['data']['einnahmen_einspeisung_eur']}€ + " f"{
                        scenario['data']['vorteile_steuerfrei_eur']}€ = " f"{
                        scenario['data']['gesamt_ertraege_jahr_eur']}€")
            else:
                print(f"  ❌ Fehler bei Szenario {i + 1}")

        except Exception as e:
            print(f"  ❌ Fehler bei Szenario {i + 1}: {e}")


if __name__ == "__main__":
    print("🚀 Test des Wasserfall-Diagramms in echter PDF-Generierung")
    print("=" * 60)

    # Test 1: Grundlegende Funktionalität
    success = test_real_pdf_with_waterfall()

    if success:
        # Test 2: Verschiedene Werte
        test_different_waterfall_values()

        print("\n🎉 Alle Tests abgeschlossen!")
        print("📋 Überprüfen Sie die generierten PDF-Dateien:")
        print("   - test_wasserfall_real_pdf.pdf (Haupttest)")
        print("   - test_wasserfall_scenario_*.pdf (Verschiedene Szenarien)")
        print("📍 Das Wasserfall-Diagramm sollte auf Seite 3 zwischen den angegebenen Koordinaten sichtbar sein")
    else:
        print("\n❌ Grundtest fehlgeschlagen - weitere Tests übersprungen")
