"""
Test für das refactorierte solar_3d_view_module.py

Dieser Test prüft, dass:
1. Alle Module korrekt importiert werden können
2. Die Hauptfunktionen verfügbar sind
3. Die Helper-Funktionen korrekt arbeiten
"""

import sys
import traceback


def test_imports():
    """Teste dass alle Module importiert werden können"""
    print("=" * 70)
    print("TEST 1: Module-Imports")
    print("=" * 70)

    try:
        import solar_3d_view_module
        print("[OK] solar_3d_view_module importiert")

        # Prüfe Hauptfunktion
        assert hasattr(solar_3d_view_module, 'render_3d_view')
        print("[OK] render_3d_view() Funktion gefunden")

        # Prüfe Helper-Funktionen
        helpers = [
            'safe_render_component',
            'get_project_data',
            'get_analysis_results',
            'extract_roof_type',
            'extract_module_quantity',
            'extract_building_type',
            'cleanup_session_state',
            'create_building_dims',
            'create_layout_config'
        ]

        for helper in helpers:
            assert hasattr(solar_3d_view_module, helper)
            print(f"[OK] {helper}() Funktion gefunden")

        print("\n[OK] Alle Imports erfolgreich!\n")
        return True

    except Exception as e:
        print(f"\n[ERROR] Import-Fehler: {e}")
        traceback.print_exc()
        return False


def test_module_availability():
    """Teste welche Module verfügbar sind"""
    print("=" * 70)
    print("TEST 2: Modul-Verfügbarkeit")
    print("=" * 70)

    try:
        import solar_3d_view_module as svm

        # Prüfe Verfügbarkeits-Flags
        flags = {
            'PV3D_AVAILABLE': svm.PV3D_AVAILABLE,
            'UI_COMPONENTS_AVAILABLE': svm.UI_COMPONENTS_AVAILABLE,
            'ANALYSIS_AVAILABLE': svm.ANALYSIS_AVAILABLE,
            'EXPORT_AVAILABLE': svm.EXPORT_AVAILABLE,
            'OPTIMIZATION_AVAILABLE': svm.OPTIMIZATION_AVAILABLE
        }

        for flag_name, flag_value in flags.items():
            status = "[OK]" if flag_value else "[WARNING]"
            print(f"{status} {flag_name}: {flag_value}")

        all_available = all(flags.values())
        if all_available:
            print("\n[OK] Alle Module verfügbar!\n")
        else:
            print("\n[WARNING] Einige Module nicht verfügbar (siehe oben)\n")

        return True

    except Exception as e:
        print(f"\n[ERROR] Fehler: {e}")
        traceback.print_exc()
        return False


def test_helper_functions():
    """Teste Helper-Funktionen mit Mock-Daten"""
    print("=" * 70)
    print("TEST 3: Helper-Funktionen")
    print("=" * 70)

    try:
        import solar_3d_view_module as svm

        # Test extract_roof_type
        project_data = {"roof_type": "Satteldach"}
        roof_type = svm.extract_roof_type(project_data)
        assert roof_type == "Satteldach"
        print("[OK] extract_roof_type() funktioniert")

        # Test extract_roof_type mit Fallback
        empty_data = {}
        roof_type = svm.extract_roof_type(empty_data)
        assert roof_type == "Flachdach"
        print("[OK] extract_roof_type() Fallback funktioniert")

        # Test extract_module_quantity
        project_data = {"module_quantity": 25}
        analysis_results = {}
        qty = svm.extract_module_quantity(project_data, analysis_results)
        assert qty == 25
        print("[OK] extract_module_quantity() funktioniert")

        # Test extract_module_quantity mit Fallback
        qty = svm.extract_module_quantity({}, {})
        assert qty == 20  # Default
        print("[OK] extract_module_quantity() Fallback funktioniert")

        # Test extract_building_type
        project_data = {"building_type": "Mehrfamilienhaus"}
        building_type = svm.extract_building_type(project_data)
        assert building_type == "Mehrfamilienhaus"
        print("[OK] extract_building_type() funktioniert")

        # Test extract_building_type mit Fallback
        building_type = svm.extract_building_type({})
        assert building_type == "Einfamilienhaus"
        print("[OK] extract_building_type() Fallback funktioniert")

        print("\n[OK] Alle Helper-Funktionen funktionieren!\n")
        return True

    except Exception as e:
        print(f"\n[ERROR] Fehler: {e}")
        traceback.print_exc()
        return False


def test_building_dims_creation():
    """Teste BuildingDims-Erstellung"""
    print("=" * 70)
    print("TEST 4: BuildingDims-Erstellung")
    print("=" * 70)

    try:
        import solar_3d_view_module as svm

        if not svm.PV3D_AVAILABLE:
            print("[WARNING] PV3D nicht verfügbar, überspringe Test")
            return True

        # Test create_building_dims
        settings = {
            "building_length": 12.0,
            "building_width": 8.0,
            "building_height": 6.0
        }

        dims = svm.create_building_dims(settings)
        assert dims.length_m == 12.0
        assert dims.width_m == 8.0
        assert dims.wall_height_m == 6.0
        print("[OK] create_building_dims() funktioniert")

        # Test mit Defaults
        dims = svm.create_building_dims({})
        assert dims.length_m == 10.0
        assert dims.width_m == 6.0
        assert dims.wall_height_m == 3.0
        print("[OK] create_building_dims() Defaults funktionieren")

        print("\n[OK] BuildingDims-Erstellung funktioniert!\n")
        return True

    except Exception as e:
        print(f"\n[ERROR] Fehler: {e}")
        traceback.print_exc()
        return False


def main():
    """Führe alle Tests aus"""
    print("\n" + "=" * 70)
    print("REFACTORED 3D MODULE TESTS")
    print("=" * 70 + "\n")

    results = []

    # Führe Tests aus
    results.append(("Imports", test_imports()))
    results.append(("Modul-Verfügbarkeit", test_module_availability()))
    results.append(("Helper-Funktionen", test_helper_functions()))
    results.append(("BuildingDims-Erstellung", test_building_dims_creation()))

    # Zusammenfassung
    print("=" * 70)
    print("ZUSAMMENFASSUNG")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "[OK] PASS" if result else "[ERROR] FAIL"
        print(f"{status}: {test_name}")

    print(f"\nErgebnis: {passed}/{total} Tests bestanden")

    if passed == total:
        print("\n🎉 Alle Tests erfolgreich!")
        return 0
    else:
        print(f"\n[WARNING] {total - passed} Test(s) fehlgeschlagen")
        return 1


if __name__ == "__main__":
    sys.exit(main())
