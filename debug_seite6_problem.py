#!/usr/bin/env python3
"""
Debug-Skript für Seite 6 Problem - Keine Charts/Ergebnisse/Werte werden angezeigt
"""

import os
import sys
import traceback
from pathlib import Path

# Pfad zum Projektverzeichnis hinzufügen
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_seite6_data_generation():
    """Teste die Datengenerierung für Seite 6"""
    print("[SEARCH] Teste Seite 6 Datengenerierung...")

    try:
        # Import der benötigten Module
        from calculations import (
            calculate_storage_to_consumption_ratio,
            calculate_storage_to_production_ratio,
        )
        from pdf_template_engine.placeholders import (
            build_dynamic_data,
        )

        # Test-Daten erstellen
        test_project_data = {
            "customer_data": {
                "first_name": "Max",
                "last_name": "Mustermann",
                "email": "max@example.com",
                "phone_mobile": "0123456789",
                "address": "Musterstraße 1",
                "zip_code": "12345",
                "city": "Musterstadt"
            },
            "project_details": {
                "annual_consumption_kwh": 6000,
                "pv_modules_count": 28,
                "module_power_wp": 400,
                "storage_capacity_kwh": 12.09,
                "inverter_power_w": 10000
            }
        }

        test_analysis_results = {
            "anlage_kwp": 11.2,
            "annual_yield_kwh": 8251.92,
            "storage_capacity_kwh": 12.09,
            "self_supply_rate_percent": 54,
            "self_consumption_percent": 42
        }

        test_company_info = {
            "name": "TommaTech GmbH",
            "street": "Zeppelinstraße 14",
            "zip_code": "85748",
            "city": "Garching b. München",
            "phone": "+49 89 1250 36 860",
            "email": "mail@tommatech.de"
        }

        print("[CHART] Generiere dynamische Daten...")
        dynamic_data = build_dynamic_data(
            test_project_data,
            test_analysis_results,
            test_company_info)

        # Prüfe Seite 6 spezifische Werte
        seite6_keys = [
            'module_count_formatted',
            'inverter_power_w_formatted',
            'storage_capacity_formatted',
            'storage_consumption_ratio_percent',
            'storage_production_ratio_percent'
        ]

        print("\n📋 Seite 6 Werte:")
        for key in seite6_keys:
            value = dynamic_data.get(key, "NICHT GEFUNDEN")
            print(f"  {key}: {value}")

        # Teste Speicher-Relationen direkt
        print("\n[TOOL] Teste Speicher-Relationen direkt:")
        storage_kwh = 12.09
        daily_consumption = 6000 / 365  # ~16.44 kWh/Tag
        daily_production = 8251.92 / 365  # ~22.61 kWh/Tag

        consumption_ratio = calculate_storage_to_consumption_ratio(
            storage_kwh, daily_consumption)
        production_ratio = calculate_storage_to_production_ratio(
            storage_kwh, daily_production)

        print(f"  Speicher: {storage_kwh} kWh")
        print(f"  Tagesverbrauch: {daily_consumption:.2f} kWh")
        print(f"  Tagesproduktion: {daily_production:.2f} kWh")
        print(f"  Verbrauchsrelation: {consumption_ratio:.0f}%")
        print(f"  Produktionsrelation: {production_ratio:.0f}%")

        return True

    except Exception as e:
        print(f"[ERROR] Fehler bei Datengenerierung: {e}")
        traceback.print_exc()
        return False


def test_seite6_coords():
    """Teste die Seite 7 Koordinaten (OLD: page 6 -> NEW: page 7)"""
    print("\n🗺️ Teste Seite 7 Koordinaten (old page 6)...")

    try:
        coords_file = Path("coords/seite7.yml")
        if not coords_file.exists():
            print(f"[ERROR] Koordinatendatei nicht gefunden: {coords_file}")
            return False

        # Lade und parse Koordinaten
        from pdf_template_engine.dynamic_overlay import parse_coords_file
        elements = parse_coords_file(coords_file)

        print(f"📍 Gefundene Elemente: {len(elements)}")

        # Suche nach Seite 6 spezifischen Platzhaltern
        seite6_placeholders = [
            'X_MODULE_COUNT_FORMATTED',
            'X_INVERTER_POWER_FORMATTED',
            'X_STORAGE_CAPACITY_FORMATTED',
            'relation_tagverbrauch_prozent',
            'relation_pvproduktion_prozent'
        ]

        found_placeholders = []
        for element in elements:
            text = element.get('text', '')
            if text in seite6_placeholders:
                found_placeholders.append(text)
                print(
                    f"  [OK] Gefunden: {text} an Position {
                        element.get('position')}")

        missing = set(seite6_placeholders) - set(found_placeholders)
        if missing:
            print(f"  [ERROR] Fehlende Platzhalter: {missing}")

        return len(found_placeholders) > 0

    except Exception as e:
        print(f"[ERROR] Fehler bei Koordinaten-Test: {e}")
        traceback.print_exc()
        return False


def test_placeholder_mapping():
    """Teste das Platzhalter-Mapping für Seite 6"""
    print("\n🔗 Teste Platzhalter-Mapping...")

    try:
        from pdf_template_engine.placeholders import PLACEHOLDER_MAPPING

        seite6_mappings = {
            'X_MODULE_COUNT_FORMATTED': 'module_count_formatted',
            'X_INVERTER_POWER_FORMATTED': 'inverter_power_w_formatted',
            'X_STORAGE_CAPACITY_FORMATTED': 'storage_capacity_formatted',
            'relation_tagverbrauch_prozent': 'storage_consumption_ratio_percent',
            'relation_pvproduktion_prozent': 'storage_production_ratio_percent'}

        print("[SEARCH] Prüfe Mappings:")
        all_good = True
        for placeholder, expected_key in seite6_mappings.items():
            actual_key = PLACEHOLDER_MAPPING.get(placeholder)
            if actual_key == expected_key:
                print(f"  [OK] {placeholder} -> {actual_key}")
            else:
                print(
                    f"  [ERROR] {placeholder} -> {actual_key} (erwartet: {expected_key})")
                all_good = False

        return all_good

    except Exception as e:
        print(f"[ERROR] Fehler bei Mapping-Test: {e}")
        traceback.print_exc()
        return False


def test_pdf_generation():
    """Teste die PDF-Generierung für Seite 6"""
    print("\n[FILE] Teste PDF-Generierung...")

    try:
        # Prüfe ob Template-PDFs existieren (OLD: page 6 -> NEW: page 7)
        template_path = Path("pdf_templates_static/notext/nt_nt_07.pdf")
        if not template_path.exists():
            print(f"[ERROR] Template-PDF nicht gefunden: {template_path}")
            return False

        print(f"[OK] Template-PDF gefunden: {template_path}")

        # Teste Overlay-Generierung
        from pdf_template_engine.dynamic_overlay import generate_overlay
        from pdf_template_engine.placeholders import build_dynamic_data

        # Test-Daten
        test_project_data = {
            "project_details": {
                "annual_consumption_kwh": 6000,
                "pv_modules_count": 28,
                "storage_capacity_kwh": 12.09
            }
        }

        test_analysis_results = {
            "annual_yield_kwh": 8251.92
        }

        coords_dir = Path("coords")
        dynamic_data = build_dynamic_data(
            test_project_data, test_analysis_results, {})

        print("[DESIGN] Generiere Overlay...")
        overlay_bytes = generate_overlay(
            coords_dir, dynamic_data, total_pages=6)

        if overlay_bytes and len(overlay_bytes) > 0:
            print(f"[OK] Overlay generiert: {len(overlay_bytes)} bytes")
            return True
        print("[ERROR] Overlay-Generierung fehlgeschlagen")
        return False

    except Exception as e:
        print(f"[ERROR] Fehler bei PDF-Generierung: {e}")
        traceback.print_exc()
        return False


def main():
    """Hauptfunktion für Debug-Tests"""
    print("[LAUNCH] Seite 6 Debug-Analyse startet...\n")

    tests = [
        ("Platzhalter-Mapping", test_placeholder_mapping),
        ("Seite 6 Koordinaten", test_seite6_coords),
        ("Datengenerierung", test_seite6_data_generation),
        ("PDF-Generierung", test_pdf_generation)
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n{'=' * 50}")
        print(f"Test: {test_name}")
        print('=' * 50)

        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"[ERROR] Test '{test_name}' fehlgeschlagen: {e}")
            results.append((test_name, False))

    # Zusammenfassung
    print(f"\n{'=' * 50}")
    print("ZUSAMMENFASSUNG")
    print('=' * 50)

    passed = 0
    for test_name, result in results:
        status = "[OK] BESTANDEN" if result else "[ERROR] FEHLGESCHLAGEN"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\nErgebnis: {passed}/{len(results)} Tests bestanden")

    if passed < len(results):
        print("\n[TOOL] EMPFOHLENE MASSNAHMEN:")
        print("1. Prüfe ob alle benötigten Dateien existieren")
        print("2. Überprüfe die Platzhalter-Mappings in placeholders.py")
        print("3. Stelle sicher dass die Berechnungsfunktionen korrekt arbeiten")
        print("4. Teste die PDF-Template-Engine Komponenten einzeln")


if __name__ == "__main__":
    main()
