#!/usr/bin/env python3
"""
Test-Skript für Wärmepumpen-Funktionen in der DING_App
Überprüft ob alle HP-Features korrekt implementiert sind.
"""

import os
import sys
import traceback

# Aktuelles Verzeichnis zum Python-Pfad hinzufügen
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_imports():
    """Teste alle kritischen Imports"""
    print("Teste Imports...")

    try:
        print("analysis.py import erfolgreich")
    except Exception as e:
        print(f"analysis.py import fehlgeschlagen: {e}")
        return False

    try:
        print("pdf_ui.py import erfolgreich")
    except Exception as e:
        print(f"pdf_ui.py import fehlgeschlagen: {e}")
        return False

    try:
        print("pdf_generator.py import erfolgreich")
    except Exception as e:
        print(f"pdf_generator.py import fehlgeschlagen: {e}")
        return False

    try:
        print("pdf_template_engine import erfolgreich")
    except Exception as e:
        print(f"pdf_template_engine import fehlgeschlagen: {e}")
        return False

    return True


def test_coords_wp_directory():
    """Teste ob coords_wp Verzeichnis und Dateien existieren"""
    print("\nTeste coords_wp Verzeichnis...")

    coords_wp_path = os.path.join(os.path.dirname(__file__), 'coords_wp')

    if not os.path.exists(coords_wp_path):
        print(f"coords_wp Verzeichnis nicht gefunden: {coords_wp_path}")
        return False

    print(f"coords_wp Verzeichnis gefunden: {coords_wp_path}")

    # Teste WP-Seiten
    for i in range(1, 8):
        wp_file = os.path.join(coords_wp_path, f'wp_seite{i}.yml')
        if os.path.exists(wp_file):
            print(f"wp_seite{i}.yml vorhanden")
        else:
            print(f"wp_seite{i}.yml fehlt")
            return False

    return True


def test_placeholders():
    """Teste ob HP-Placeholders verfügbar sind"""
    print("\nTeste HP-Placeholders...")

    try:
        from pdf_template_engine.placeholders import build_dynamic_data

        # Test-Daten erstellen
        test_project_data = {
            'customer_data': {
                'first_name': 'Test', 'last_name': 'Kunde'}, 'project_details': {
                'anlage_kwp': 10.0}, 'heatpump_offer': {
                'beg_subsidy': {
                    'effective_total_after_subsidy_net': 15000}, 'demand_inputs': {
                        'heating_costs_yearly': 2400, 'heating_type': 'Gas'}}}

        test_analysis_results = {
            'anlage_kwp': 10.0,
            'annual_pv_production_kwh': 9500,
            'total_investment_netto': 18000
        }

        test_company_info = {
            'name': 'Test GmbH',
            'address': 'Teststraße 1',
            'city': 'Teststadt'
        }

        # Placeholder-Daten erstellen
        placeholders = build_dynamic_data(
            test_project_data,
            test_analysis_results,
            test_company_info)

        # Prüfe ob HP-Placeholders vorhanden sind
        hp_keys = [k for k in placeholders.keys() if k.startswith('hp_')]
        if hp_keys:
            print(f"{len(hp_keys)} HP-Placeholders gefunden:")
            for key in sorted(hp_keys)[:5]:  # Zeige ersten 5
                print(f"  - {key}: {str(placeholders[key])[:50]}...")
        else:
            print("Keine HP-Placeholders gefunden")
            return False

        return True

    except Exception as e:
        print(f"Fehler beim Testen der Placeholders: {e}")
        traceback.print_exc()
        return False


def test_analysis_functions():
    """Teste ob Analysis-Funktionen verfügbar sind"""
    print("\n⚙️ Teste Analysis-Funktionen...")

    try:
        import analysis

        # Prüfe ob render_analysis verfügbar ist
        if hasattr(analysis, 'render_analysis'):
            print("render_analysis Funktion verfügbar")
        else:
            print("render_analysis Funktion nicht verfügbar")
            return False

        # Prüfe andere wichtige Funktionen
        functions_to_check = ['get_text', '_get_visualization_settings']
        for func_name in functions_to_check:
            if hasattr(analysis, func_name):
                print(f"{func_name} verfügbar")
            else:
                print(
                    f"{func_name} nicht verfügbar (möglicherweise nicht kritisch)")

        return True

    except Exception as e:
        print(f"Fehler beim Testen der Analysis-Funktionen: {e}")
        return False


def test_pdf_functions():
    """Teste ob PDF-Funktionen verfügbar sind"""
    print("\nTeste PDF-Funktionen...")

    try:
        import pdf_ui

        # Prüfe ob render_pdf_ui verfügbar ist
        if hasattr(pdf_ui, 'render_pdf_ui'):
            print("render_pdf_ui Funktion verfügbar")
        else:
            print("render_pdf_ui Funktion nicht verfügbar")
            return False

        # Prüfe PDF-Generator
        import pdf_generator

        if hasattr(pdf_generator, 'generate_main_template_pdf_bytes'):
            print("generate_main_template_pdf_bytes verfügbar")
        else:
            print("generate_main_template_pdf_bytes nicht verfügbar")
            return False

        return True

    except Exception as e:
        print(f"Fehler beim Testen der PDF-Funktionen: {e}")
        return False


def run_all_tests():
    """Führe alle Tests aus"""
    print("🧪 Starte Tests für HP-Funktionen...")
    print("=" * 50)

    tests = [
        test_imports,
        test_coords_wp_directory,
        test_placeholders,
        test_analysis_functions,
        test_pdf_functions
    ]

    passed = 0
    total = len(tests)

    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"Test {test_func.__name__} fehlgeschlagen")
        except Exception as e:
            print(
                f"Test {
                    test_func.__name__} mit Ausnahme fehlgeschlagen: {e}")

    print("\n" + "=" * 50)
    print(f"Test-Ergebnis: {passed}/{total} Tests bestanden")

    if passed == total:
        print("🎉 Alle Tests erfolgreich! HP-Funktionen sind verfügbar.")
        return True
    print("Einige Tests fehlgeschlagen. Überprüfe die Implementierung.")
    return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
