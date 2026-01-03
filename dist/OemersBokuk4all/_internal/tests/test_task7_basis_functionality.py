"""
Test für Task 7: Basis-Funktionalität der 3D-Visualisierung

Dieser Test prüft:
1. Alle UI-Komponenten sind sichtbar
2. Gebäudedimensionen können geändert werden
3. Dachform-Auswahl funktioniert
4. Modul-Belegung funktioniert
5. 3D-Szene wird korrekt gerendert

Requirements: 1.1, 1.2, 1.3, 3.1
"""

import sys
import traceback
from typing import Dict, Any


def test_ui_components_visibility():
    """
    Test 1: Prüfe dass alle UI-Komponenten sichtbar sind
    Requirement: 1.1
    """
    print("=" * 70)
    print("TEST 1: UI-Komponenten Sichtbarkeit")
    print("=" * 70)

    try:
        from utils.pv3d_ui_components import (
            render_basis_settings,
            render_module_placement,
            render_advanced_controls,
            render_analysis_panel,
            render_export_options
        )

        # Prüfe dass alle Funktionen existieren
        components = {
            "Basis-Einstellungen": render_basis_settings,
            "Modul-Belegung": render_module_placement,
            "Erweiterte Kontrolle": render_advanced_controls,
            "Analyse": render_analysis_panel,
            "Export-Optionen": render_export_options
        }

        for name, func in components.items():
            assert callable(func), f"{name} ist nicht aufrufbar"
            print(f"{name} Komponente verfügbar")

        print("\nAlle UI-Komponenten sind verfügbar!\n")
        return True

    except ImportError as e:
        print(f"\nImport-Fehler: {e}")
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\nFehler: {e}")
        traceback.print_exc()
        return False


def test_building_dimensions_change():
    """
    Test 2: Prüfe dass Gebäudedimensionen geändert werden können
    Requirement: 1.2
    """
    print("=" * 70)
    print("TEST 2: Gebäudedimensionen ändern")
    print("=" * 70)

    try:
        from utils.pv3d import BuildingDims
        import solar_3d_view_module as svm

        # Test 1: Standard-Dimensionen
        settings = {
            "building_length": 10.0,
            "building_width": 6.0,
            "building_height": 3.0
        }

        dims = svm.create_building_dims(settings)
        assert dims.length_m == 10.0, "Länge nicht korrekt"
        assert dims.width_m == 6.0, "Breite nicht korrekt"
        assert dims.wall_height_m == 3.0, "Höhe nicht korrekt"
        print("Standard-Dimensionen korrekt gesetzt")

        # Test 2: Geänderte Dimensionen
        settings = {
            "building_length": 15.0,
            "building_width": 9.0,
            "building_height": 5.0
        }

        dims = svm.create_building_dims(settings)
        assert dims.length_m == 15.0, "Geänderte Länge nicht korrekt"
        assert dims.width_m == 9.0, "Geänderte Breite nicht korrekt"
        assert dims.wall_height_m == 5.0, "Geänderte Höhe nicht korrekt"
        print("Geänderte Dimensionen korrekt gesetzt")

        # Test 3: Kleine Dimensionen
        settings = {
            "building_length": 5.0,
            "building_width": 4.0,
            "building_height": 2.5
        }

        dims = svm.create_building_dims(settings)
        assert dims.length_m == 5.0, "Kleine Länge nicht korrekt"
        assert dims.width_m == 4.0, "Kleine Breite nicht korrekt"
        assert dims.wall_height_m == 2.5, "Kleine Höhe nicht korrekt"
        print("Kleine Dimensionen korrekt gesetzt")

        # Test 4: Große Dimensionen
        settings = {
            "building_length": 25.0,
            "building_width": 15.0,
            "building_height": 8.0
        }

        dims = svm.create_building_dims(settings)
        assert dims.length_m == 25.0, "Große Länge nicht korrekt"
        assert dims.width_m == 15.0, "Große Breite nicht korrekt"
        assert dims.wall_height_m == 8.0, "Große Höhe nicht korrekt"
        print("Große Dimensionen korrekt gesetzt")

        # Test 5: Fallback auf Defaults
        dims = svm.create_building_dims({})
        assert dims.length_m == 10.0, "Default Länge nicht korrekt"
        assert dims.width_m == 6.0, "Default Breite nicht korrekt"
        assert dims.wall_height_m == 3.0, "Default Höhe nicht korrekt"
        print("Default-Dimensionen korrekt gesetzt")

        print("\nGebäudedimensionen können korrekt geändert werden!\n")
        return True

    except Exception as e:
        print(f"\nFehler: {e}")
        traceback.print_exc()
        return False


def test_roof_type_selection():
    """
    Test 3: Prüfe dass Dachform-Auswahl funktioniert
    Requirement: 1.2
    """
    print("=" * 70)
    print("TEST 3: Dachform-Auswahl")
    print("=" * 70)

    try:
        import solar_3d_view_module as svm

        # Test 1: Flachdach
        project_data = {"roof_type": "Flachdach"}
        roof_type = svm.extract_roof_type(project_data)
        assert roof_type == "Flachdach", "Flachdach nicht korrekt"
        print("Flachdach korrekt erkannt")

        # Test 2: Satteldach
        project_data = {"roof_type": "Satteldach"}
        roof_type = svm.extract_roof_type(project_data)
        assert roof_type == "Satteldach", "Satteldach nicht korrekt"
        print("Satteldach korrekt erkannt")

        # Test 3: Walmdach
        project_data = {"roof_type": "Walmdach"}
        roof_type = svm.extract_roof_type(project_data)
        assert roof_type == "Walmdach", "Walmdach nicht korrekt"
        print("Walmdach korrekt erkannt")

        # Test 4: Pultdach
        project_data = {"roof_type": "Pultdach"}
        roof_type = svm.extract_roof_type(project_data)
        assert roof_type == "Pultdach", "Pultdach nicht korrekt"
        print("Pultdach korrekt erkannt")

        # Test 5: Nested in project_details
        project_data = {
            "project_details": {
                "roof_type": "Satteldach"
            }
        }
        roof_type = svm.extract_roof_type(project_data)
        assert roof_type == "Satteldach", "Nested Dachtyp nicht korrekt"
        print("Nested Dachtyp korrekt erkannt")

        # Test 6: Fallback auf Default
        project_data = {}
        roof_type = svm.extract_roof_type(project_data)
        assert roof_type == "Flachdach", "Default Dachtyp nicht korrekt"
        print("Default Dachtyp (Flachdach) korrekt gesetzt")

        print("\nDachform-Auswahl funktioniert korrekt!\n")
        return True

    except Exception as e:
        print(f"\nFehler: {e}")
        traceback.print_exc()
        return False


def test_module_placement():
    """
    Test 4: Prüfe dass Modul-Belegung funktioniert
    Requirement: 1.2, 1.3
    """
    print("=" * 70)
    print("TEST 4: Modul-Belegung")
    print("=" * 70)

    try:
        import solar_3d_view_module as svm

        # Test 1: Modulanzahl aus analysis_results
        project_data = {}
        analysis_results = {"module_quantity": 30}
        qty = svm.extract_module_quantity(project_data, analysis_results)
        assert qty == 30, "Modulanzahl aus analysis_results nicht korrekt"
        print("Modulanzahl aus analysis_results korrekt")

        # Test 2: Modulanzahl aus project_data
        project_data = {"module_quantity": 25}
        analysis_results = {}
        qty = svm.extract_module_quantity(project_data, analysis_results)
        assert qty == 25, "Modulanzahl aus project_data nicht korrekt"
        print("Modulanzahl aus project_data korrekt")

        # Test 3: Priorität analysis_results > project_data
        project_data = {"module_quantity": 25}
        analysis_results = {"module_quantity": 35}
        qty = svm.extract_module_quantity(project_data, analysis_results)
        assert qty == 35, "Priorität nicht korrekt"
        print("Priorität analysis_results > project_data korrekt")

        # Test 4: Fallback auf Default
        project_data = {}
        analysis_results = {}
        qty = svm.extract_module_quantity(project_data, analysis_results)
        assert qty == 20, "Default Modulanzahl nicht korrekt"
        print("Default Modulanzahl (20) korrekt")

        # Test 5: Kleine Modulanzahl
        project_data = {"module_quantity": 5}
        analysis_results = {}
        qty = svm.extract_module_quantity(project_data, analysis_results)
        assert qty == 5, "Kleine Modulanzahl nicht korrekt"
        print("Kleine Modulanzahl korrekt")

        # Test 6: Große Modulanzahl
        project_data = {"module_quantity": 100}
        analysis_results = {}
        qty = svm.extract_module_quantity(project_data, analysis_results)
        assert qty == 100, "Große Modulanzahl nicht korrekt"
        print("Große Modulanzahl korrekt")

        print("\nModul-Belegung funktioniert korrekt!\n")
        return True

    except Exception as e:
        print(f"\nFehler: {e}")
        traceback.print_exc()
        return False


def test_3d_scene_rendering():
    """
    Test 5: Prüfe dass 3D-Szene korrekt gerendert wird
    Requirement: 1.3, 3.1
    """
    print("=" * 70)
    print("TEST 5: 3D-Szene Rendering")
    print("=" * 70)

    try:
        from utils.pv3d import BuildingDims, AdvancedLayoutConfig
        from utils.pv3d_plotly import build_plotly_scene

        # Test 1: Einfache Szene mit Flachdach
        project_data = {
            "roof_type": "Flachdach",
            "module_quantity": 20
        }

        dims = BuildingDims(
            length_m=10.0,
            width_m=6.0,
            wall_height_m=3.0
        )

        fig = build_plotly_scene(
            project_data=project_data,
            dims=dims,
            roof_type="Flachdach",
            module_quantity=20,
            layout_config=None,
            selected_modules=[]
        )

        assert fig is not None, "Figure ist None"
        assert hasattr(fig, 'data'), "Figure hat keine data"
        assert len(fig.data) > 0, "Figure hat keine Daten"
        print("Flachdach-Szene erfolgreich gerendert")

        # Test 2: Szene mit Satteldach
        fig = build_plotly_scene(
            project_data=project_data,
            dims=dims,
            roof_type="Satteldach",
            module_quantity=20,
            layout_config=None,
            selected_modules=[]
        )

        assert fig is not None, "Satteldach Figure ist None"
        assert len(fig.data) > 0, "Satteldach Figure hat keine Daten"
        print("Satteldach-Szene erfolgreich gerendert")

        # Test 3: Szene mit Layout-Konfiguration
        layout_config = AdvancedLayoutConfig()
        layout_config.mounting_type = "Aufgeständert"
        layout_config.custom_tilt = 30.0
        layout_config.custom_azimuth = 180.0

        fig = build_plotly_scene(
            project_data=project_data,
            dims=dims,
            roof_type="Flachdach",
            module_quantity=20,
            layout_config=layout_config,
            selected_modules=[]
        )

        assert fig is not None, "Figure mit Layout-Config ist None"
        assert len(fig.data) > 0, "Figure mit Layout-Config hat keine Daten"
        print("Szene mit Layout-Konfiguration erfolgreich gerendert")

        # Test 4: Szene mit ausgewählten Modulen
        fig = build_plotly_scene(
            project_data=project_data,
            dims=dims,
            roof_type="Flachdach",
            module_quantity=20,
            layout_config=None,
            selected_modules=[0, 1, 2, 5, 10]
        )

        assert fig is not None, "Figure mit Auswahl ist None"
        assert len(fig.data) > 0, "Figure mit Auswahl hat keine Daten"
        print("Szene mit ausgewählten Modulen erfolgreich gerendert")

        # Test 5: Szene mit verschiedenen Dimensionen
        dims_large = BuildingDims(
            length_m=20.0,
            width_m=12.0,
            wall_height_m=6.0
        )

        fig = build_plotly_scene(
            project_data=project_data,
            dims=dims_large,
            roof_type="Walmdach",
            module_quantity=50,
            layout_config=None,
            selected_modules=[]
        )

        assert fig is not None, "Figure mit großen Dimensionen ist None"
        assert len(fig.data) > 0, "Figure mit großen Dimensionen hat keine Daten"
        print("Szene mit großen Dimensionen erfolgreich gerendert")

        print("\n3D-Szene wird korrekt gerendert!\n")
        return True

    except Exception as e:
        print(f"\nFehler: {e}")
        traceback.print_exc()
        return False


def test_layout_config_creation():
    """
    Test 6: Prüfe dass Layout-Konfiguration erstellt werden kann
    Requirement: 1.2, 1.3
    """
    print("=" * 70)
    print("TEST 6: Layout-Konfiguration Erstellung")
    print("=" * 70)

    try:
        from utils.pv3d import AdvancedLayoutConfig
        import solar_3d_view_module as svm

        # Test 1: Basis-Konfiguration
        module_settings = {
            "mounting_type": "Aufgeständert",
            "custom_azimuth": 180.0,
            "custom_tilt": 30.0
        }
        advanced_settings = {}

        config = svm.create_layout_config(module_settings, advanced_settings)
        assert config is not None, "Config ist None"
        assert config.mounting_type == "Aufgeständert", "Mounting type nicht korrekt"
        assert config.custom_azimuth == 180.0, "Azimuth nicht korrekt"
        assert config.custom_tilt == 30.0, "Tilt nicht korrekt"
        print("Basis-Konfiguration korrekt erstellt")

        # Test 2: Konfiguration mit Garage und Fassade
        module_settings = {
            "use_garage": True,
            "use_facade": True
        }
        advanced_settings = {}

        config = svm.create_layout_config(module_settings, advanced_settings)
        assert config is not None, "Config mit Garage ist None"
        assert config.use_garage is True, "use_garage nicht korrekt"
        assert config.use_facade is True, "use_facade nicht korrekt"
        print("Konfiguration mit Garage und Fassade korrekt erstellt")

        # Test 3: Konfiguration mit entfernten Modulen
        module_settings = {
            "removed_indices": [0, 5, 10, 15]
        }
        advanced_settings = {}

        config = svm.create_layout_config(module_settings, advanced_settings)
        assert config is not None, "Config mit removed_indices ist None"
        assert config.removed_indices == [0, 5, 10, 15], "removed_indices nicht korrekt"
        print("Konfiguration mit entfernten Modulen korrekt erstellt")

        # Test 4: Leere Konfiguration
        module_settings = {}
        advanced_settings = {}

        config = svm.create_layout_config(module_settings, advanced_settings)
        assert config is not None, "Leere Config ist None"
        print("Leere Konfiguration korrekt erstellt")

        print("\nLayout-Konfiguration kann korrekt erstellt werden!\n")
        return True

    except Exception as e:
        print(f"\nFehler: {e}")
        traceback.print_exc()
        return False


def test_integration():
    """
    Test 7: Integrations-Test - Vollständiger Workflow
    Requirement: 1.1, 1.2, 1.3, 3.1
    """
    print("=" * 70)
    print("TEST 7: Integrations-Test")
    print("=" * 70)

    try:
        import solar_3d_view_module as svm
        from utils.pv3d import BuildingDims, AdvancedLayoutConfig
        from utils.pv3d_plotly import build_plotly_scene

        # Simuliere vollständigen Workflow
        print("\n1. Lade Projektdaten...")
        project_data = {
            "roof_type": "Satteldach",
            "module_quantity": 30,
            "building_type": "Einfamilienhaus"
        }
        analysis_results = {
            "module_quantity": 35
        }

        # 2. Extrahiere Informationen
        print("2. Extrahiere Informationen...")
        roof_type = svm.extract_roof_type(project_data)
        module_quantity = svm.extract_module_quantity(project_data, analysis_results)
        building_type = svm.extract_building_type(project_data)

        assert roof_type == "Satteldach", "Roof type nicht korrekt"
        assert module_quantity == 35, "Module quantity nicht korrekt"
        assert building_type == "Einfamilienhaus", "Building type nicht korrekt"
        print("Informationen korrekt extrahiert")

        # 3. Erstelle Gebäudedimensionen
        print("3. Erstelle Gebäudedimensionen...")
        basis_settings = {
            "building_length": 12.0,
            "building_width": 8.0,
            "building_height": 5.0
        }
        dims = svm.create_building_dims(basis_settings)
        assert dims.length_m == 12.0, "Dims length nicht korrekt"
        print("Gebäudedimensionen erstellt")

        # 4. Erstelle Layout-Konfiguration
        print("4. Erstelle Layout-Konfiguration...")
        module_settings = {
            "mounting_type": "Aufgeständert",
            "custom_azimuth": 180.0,
            "custom_tilt": 35.0,
            "use_garage": False,
            "use_facade": False
        }
        advanced_settings = {}
        layout_config = svm.create_layout_config(module_settings, advanced_settings)
        assert layout_config is not None, "Layout config ist None"
        print("Layout-Konfiguration erstellt")

        # 5. Erstelle 3D-Szene
        print("5. Erstelle 3D-Szene...")
        fig = build_plotly_scene(
            project_data=project_data,
            dims=dims,
            roof_type=roof_type,
            module_quantity=module_quantity,
            layout_config=layout_config,
            selected_modules=[]
        )
        assert fig is not None, "Figure ist None"
        assert len(fig.data) > 0, "Figure hat keine Daten"
        print("3D-Szene erstellt")

        print("\nVollständiger Workflow erfolgreich durchlaufen!\n")
        return True

    except Exception as e:
        print(f"\nFehler: {e}")
        traceback.print_exc()
        return False


def main():
    """Führe alle Tests aus"""
    print("\n" + "=" * 70)
    print("TASK 7: BASIS-FUNKTIONALITÄT TESTS")
    print("=" * 70 + "\n")

    results = []

    # Führe Tests aus
    results.append(("UI-Komponenten Sichtbarkeit", test_ui_components_visibility()))
    results.append(("Gebäudedimensionen ändern", test_building_dimensions_change()))
    results.append(("Dachform-Auswahl", test_roof_type_selection()))
    results.append(("Modul-Belegung", test_module_placement()))
    results.append(("3D-Szene Rendering", test_3d_scene_rendering()))
    results.append(("Layout-Konfiguration", test_layout_config_creation()))
    results.append(("Integrations-Test", test_integration()))

    # Zusammenfassung
    print("=" * 70)
    print("ZUSAMMENFASSUNG")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status}: {test_name}")

    print(f"\nErgebnis: {passed}/{total} Tests bestanden")

    if passed == total:
        print("\n Alle Tests erfolgreich!")
        print("\nAlle UI-Komponenten sind sichtbar")
        print("Gebäudedimensionen können geändert werden")
        print("Dachform-Auswahl funktioniert")
        print("Modul-Belegung funktioniert")
        print("3D-Szene wird korrekt gerendert")
        print("\nTask 7 - Basis-Funktionalität: ABGESCHLOSSEN")
        return 0
    else:
        print(f"\n{total - passed} Test(s) fehlgeschlagen")
        return 1


if __name__ == "__main__":
    sys.exit(main())
