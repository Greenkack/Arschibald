"""
Test für die 3D PV-Visualisierung UI-Seite

Dieser Test prüft die grundlegende Struktur und Imports der UI-Seite.
"""

import sys
import os

# Füge das Projekt-Root zum Python-Path hinzu
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_imports():
    """Teste ob alle erforderlichen Module importiert werden können."""
    try:
        # Teste pv3d Module
        from utils.pv3d import (
            BuildingDims,
            LayoutConfig,
            build_scene,
            render_image_bytes,
            export_stl,
            export_gltf,
            _safe_get_orientation,
            _safe_get_roof_inclination_deg,
            _safe_get_roof_covering
        )
        print("utils.pv3d Module erfolgreich importiert")
        return True
    except ImportError as e:
        print(f"Import-Fehler: {e}")
        return False


def test_building_dims():
    """Teste BuildingDims Datenklasse."""
    try:
        from utils.pv3d import BuildingDims
        
        # Teste Default-Werte
        dims = BuildingDims()
        assert dims.length_m == 10.0
        assert dims.width_m == 6.0
        assert dims.wall_height_m == 6.0
        print("BuildingDims Default-Werte korrekt")
        
        # Teste Custom-Werte
        dims = BuildingDims(length_m=15.0, width_m=8.0, wall_height_m=7.0)
        assert dims.length_m == 15.0
        assert dims.width_m == 8.0
        assert dims.wall_height_m == 7.0
        print("BuildingDims Custom-Werte korrekt")
        
        return True
    except Exception as e:
        print(f"BuildingDims Test fehlgeschlagen: {e}")
        return False


def test_layout_config():
    """Teste LayoutConfig Datenklasse."""
    try:
        from utils.pv3d import LayoutConfig
        
        # Teste Default-Werte
        config = LayoutConfig()
        assert config.mode == "auto"
        assert config.use_garage is False
        assert config.use_facade is False
        assert config.removed_indices == []
        print("LayoutConfig Default-Werte korrekt")
        
        # Teste JSON-Serialisierung
        json_str = config.to_json()
        assert isinstance(json_str, str)
        assert "auto" in json_str
        print("LayoutConfig to_json() funktioniert")
        
        # Teste JSON-Deserialisierung
        config2 = LayoutConfig.from_json(json_str)
        assert config2.mode == config.mode
        assert config2.use_garage == config.use_garage
        print("LayoutConfig from_json() funktioniert")
        
        return True
    except Exception as e:
        print(f"LayoutConfig Test fehlgeschlagen: {e}")
        return False


def test_data_extraction():
    """Teste Datenextraktions-Funktionen."""
    try:
        from utils.pv3d import (
            _safe_get_orientation,
            _safe_get_roof_inclination_deg,
            _safe_get_roof_covering
        )
        
        # Teste mit leeren Daten
        orientation = _safe_get_orientation({})
        assert orientation == "Süd"  # Fallback
        print("_safe_get_orientation Fallback funktioniert")
        
        # Teste mit vollständigen Daten
        project_data = {
            "project_details": {
                "roof_orientation": "Ost",
                "roof_inclination_deg": 35.0,
                "roof_covering_type": "Ziegel"
            }
        }
        
        orientation = _safe_get_orientation(project_data)
        assert orientation == "Ost"
        print("_safe_get_orientation mit Daten funktioniert")
        
        inclination = _safe_get_roof_inclination_deg(project_data)
        assert inclination == 35.0
        print("_safe_get_roof_inclination_deg funktioniert")
        
        covering = _safe_get_roof_covering(project_data)
        assert covering == "Ziegel"
        print("_safe_get_roof_covering funktioniert")
        
        return True
    except Exception as e:
        print(f"Datenextraktions-Test fehlgeschlagen: {e}")
        return False


def test_ui_file_exists():
    """Teste ob die UI-Datei existiert."""
    ui_file = "pages/solar_3d_view.py"
    if os.path.exists(ui_file):
        print(f"UI-Datei existiert: {ui_file}")
        
        # Prüfe Dateigröße
        size = os.path.getsize(ui_file)
        print(f"  Dateigröße: {size} Bytes ({size // 1024} KB)")
        
        # Prüfe ob Datei nicht leer ist
        if size > 1000:
            print("UI-Datei hat sinnvolle Größe")
            return True
        else:
            print("UI-Datei ist zu klein")
            return False
    else:
        print(f"UI-Datei nicht gefunden: {ui_file}")
        return False


def main():
    """Führe alle Tests aus."""
    print("=" * 60)
    print("3D PV-Visualisierung UI-Seite - Test Suite")
    print("=" * 60)
    print()
    
    tests = [
        ("Import-Test", test_imports),
        ("BuildingDims-Test", test_building_dims),
        ("LayoutConfig-Test", test_layout_config),
        ("Datenextraktions-Test", test_data_extraction),
        ("UI-Datei-Test", test_ui_file_exists)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n{name}:")
        print("-" * 60)
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"Unerwarteter Fehler: {e}")
            results.append((name, False))
    
    # Zusammenfassung
    print("\n" + "=" * 60)
    print("Zusammenfassung:")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "BESTANDEN" if result else "FEHLGESCHLAGEN"
        print(f"{name}: {status}")
    
    print()
    print(f"Gesamt: {passed}/{total} Tests bestanden ({passed*100//total}%)")
    
    if passed == total:
        print("\n🎉 Alle Tests erfolgreich!")
        return 0
    else:
        print(f"\n{total - passed} Test(s) fehlgeschlagen")
        return 1


if __name__ == "__main__":
    exit(main())
