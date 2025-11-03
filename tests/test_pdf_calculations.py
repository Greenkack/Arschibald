#!/usr/bin/env python3
"""
Test-Skript für die neuen PDF-Berechnungen:
1. Steuerliche Vorteile
2. Gesamtersparnisse
3. Wechselrichterformat
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "pdf_template_engine"))

from pdf_template_engine.placeholders import build_dynamic_data


def test_new_calculations():
    print("=== Test der neuen PDF-Berechnungen ===\n")

    # Test-Daten
    project_data = {
        "anlage_kwp": 8.4,
        "income_tax_rate": 42,  # 42% Einkommensteuer
        "inverter_total_power_kw": 10.0,  # Hier auch hinzufügen
        "project_details": {
            "inverter_total_power_kw": 10.0,
            "income_tax_rate": 42
        },
        "customer_name": "Max Mustermann",
        "customer_city_zip": "12345 Berlin"
    }

    analysis_results = {
        "annual_pv_production_kwh": 8251.92,
        "annual_self_consumption_kwh": 3200,
        "annual_grid_feed_in_kwh": 5051.92,
        "annual_battery_charge_kwh": 1500,
        "annual_battery_discharge_kwh": 1300,
        "strompreis_cent_pro_kwh": 32,
        "eeg_verguetung_cent_pro_kwh": 7.86,
        # Bessere Schlüssel für die Berechnung
        "monthly_direct_self_consumption_kwh": [266.67] * 12,  # 3200 kWh/Jahr
        "monthly_feed_in_kwh": [420.99] * 12,  # 5051.92 kWh/Jahr
        "netzeinspeisung_kwh": 5051.92,  # Jahreseinspeisung
        "annual_storage_charge_kwh": 1500,
        "annual_storage_discharge_kwh": 1300,
        "monthly_storage_charge_kwh": [125] * 12,  # 1500 kWh/Jahr
        "monthly_storage_discharge_for_sc_kwh": [108.33] * 12,  # 1300 kWh/Jahr
        "inverter_total_power_kw": 10.0,
        "einspeiseverguetung_eur_per_kwh": 0.0786,  # 7.86 ct/kWh
        "aktueller_strompreis_fuer_hochrechnung_euro_kwh": 0.32  # 32 ct/kWh
    }

    company_info = {
        "company_name": "TommaTech GmbH",
        "company_street": "Zeppelinstraße 14"
    }

    print("Test-Eingabedaten:")
    print(f"- PV-Anlage: {project_data['anlage_kwp']} kWp")
    print(f"- Einkommensteuersatz: {project_data['income_tax_rate']}%")
    print(f"- Wechselrichterleistung: {analysis_results['inverter_total_power_kw']} kW")
    print(f"- Jährliche Einspeisung: {analysis_results['annual_grid_feed_in_kwh']} kWh")
    print(f"- EEG-Vergütung: {analysis_results['eeg_verguetung_cent_pro_kwh']} ct/kWh")
    print(f"- Strompreis: {analysis_results['strompreis_cent_pro_kwh']} ct/kWh")
    print()

    # Berechnung durchführen
    try:
        result = build_dynamic_data(project_data, analysis_results, company_info)

        print("=== ERGEBNISSE ===")
        print()

        print("1. Steuerliche Vorteile:")
        print(f"   - Einspeisung: {result.get('annual_feed_in_revenue_eur', 'N/A')}")
        print(f"   - Steuerliche Vorteile (platz1): {result.get('tax_benefits_eur', 'N/A')}")
        print()

        print("2. Gesamtersparnisse-Berechnung:")
        print(f"   - Direkt: {result.get('self_consumption_without_battery_eur', 'N/A')}")
        print(f"   - Einspeisung: {result.get('annual_feed_in_revenue_eur', 'N/A')}")
        print(f"   - Steuervorteile: {result.get('tax_benefits_eur', 'N/A')}")
        print(f"   - Speichernutzung: {result.get('battery_usage_savings_eur', 'N/A')}")
        print(f"   - Speicherüberschuss: {result.get('battery_surplus_feed_in_eur', 'N/A')}")
        print(f"   - GESAMT: {result.get('total_annual_savings_eur', 'N/A')}")
        print()

        print("3. Wechselrichterformat:")
        print(f"   - kW (für Seite 4): {result.get('inverter_total_power_kw', 'N/A')}")
        print(f"   - W (für Seite 1): {result.get('inverter_total_power_w', 'N/A')}")
        print()

        print("=== PLATZHALTER-MAPPINGS ===")
        print(f"   'Direkt' -> {result.get('self_consumption_without_battery_eur', 'N/A')}")
        print(f"   'Einspeisung' -> {result.get('annual_feed_in_revenue_eur', 'N/A')}")
        print(f"   'platz1' -> {result.get('tax_benefits_eur', 'N/A')}")
        print(f"   'Gesamt' -> {result.get('total_annual_savings_eur', 'N/A')}")
        print(f"   'Warmwasser' -> {result.get('inverter_total_power_w', 'N/A')}")

        print("\n✅ Test erfolgreich abgeschlossen!")

    except Exception as e:
        print(f"❌ Fehler beim Test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_new_calculations()
