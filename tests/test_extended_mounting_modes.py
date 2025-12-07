"""
Test für erweiterte Aufständerungs-Modi (Task 15)

Testet die neuen Mounting-Modi: south-east, south-west, custom
"""

import sys
import os

# Füge utils zum Python-Pfad hinzu
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from utils.pv3d import (
        BuildingDims,
        AdvancedLayoutConfig,
        place_panels_flat_roof,
        build_scene
    )
    import pyvista as pv
    import numpy as np
    PV3D_AVAILABLE = True
except ImportError as e:
    print(f"Import-Fehler: {e}")
    PV3D_AVAILABLE = False


def test_south_east_mounting():
    """Test Süd-Ost Aufständerung"""
    print("\n" + "="*60)
    print("TEST 1: Süd-Ost Aufständerung")
    print("="*60)
    
    if not PV3D_AVAILABLE:
        print("PyVista nicht verfügbar - Test übersprungen")
        return False
    
    try:
        # Erstelle Module mit Süd-Ost Aufständerung
        panels = place_panels_flat_roof(
            roof_length=10.0,
            roof_width=6.0,
            module_quantity=20,
            mounting_type="south-east",
            base_z=6.12
        )
        
        # Prüfe ob Module erstellt wurden
        assert len(panels) > 0, "Keine Module erstellt"
        
        # Prüfe ob Module PyVista PolyData sind
        assert all(isinstance(p, pv.PolyData) for p in panels), \
            "Module sind nicht vom Typ pv.PolyData"
        
        print(f"{len(panels)} Module mit Süd-Ost Aufständerung erstellt")
        print(f"  - Azimuth: 45° (Süd-Ost)")
        print(f"  - Neigung: 15°")
        
        return True
        
    except Exception as e:
        print(f"Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_south_west_mounting():
    """Test Süd-West Aufständerung"""
    print("\n" + "="*60)
    print("TEST 2: Süd-West Aufständerung")
    print("="*60)
    
    if not PV3D_AVAILABLE:
        print("PyVista nicht verfügbar - Test übersprungen")
        return False
    
    try:
        # Erstelle Module mit Süd-West Aufständerung
        panels = place_panels_flat_roof(
            roof_length=10.0,
            roof_width=6.0,
            module_quantity=20,
            mounting_type="south-west",
            base_z=6.12
        )
        
        # Prüfe ob Module erstellt wurden
        assert len(panels) > 0, "Keine Module erstellt"
        
        # Prüfe ob Module PyVista PolyData sind
        assert all(isinstance(p, pv.PolyData) for p in panels), \
            "Module sind nicht vom Typ pv.PolyData"
        
        print(f"{len(panels)} Module mit Süd-West Aufständerung erstellt")
        print(f"  - Azimuth: 315° (Süd-West)")
        print(f"  - Neigung: 15°")
        
        return True
        
    except Exception as e:
        print(f"Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_custom_mounting():
    """Test individueller Aufständerungs-Modus"""
    print("\n" + "="*60)
    print("TEST 3: Individueller Aufständerungs-Modus")
    print("="*60)
    
    if not PV3D_AVAILABLE:
        print("PyVista nicht verfügbar - Test übersprungen")
        return False
    
    try:
        # Test mit verschiedenen Custom-Werten
        test_cases = [
            (30.0, 20.0, "30° Azimuth, 20° Neigung"),
            (60.0, 25.0, "60° Azimuth, 25° Neigung"),
            (0.0, 10.0, "0° Azimuth (Süd), 10° Neigung"),
        ]
        
        for azimuth, tilt, description in test_cases:
            panels = place_panels_flat_roof(
                roof_length=10.0,
                roof_width=6.0,
                module_quantity=20,
                mounting_type="custom",
                custom_azimuth=azimuth,
                custom_tilt=tilt,
                base_z=6.12
            )
            
            # Prüfe ob Module erstellt wurden
            assert len(panels) > 0, f"Keine Module erstellt für {description}"
            
            # Prüfe ob Module PyVista PolyData sind
            assert all(isinstance(p, pv.PolyData) for p in panels), \
                f"Module sind nicht vom Typ pv.PolyData für {description}"
            
            print(f"{len(panels)} Module mit {description} erstellt")
        
        return True
        
    except Exception as e:
        print(f"Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_advanced_layout_config():
    """Test AdvancedLayoutConfig mit neuen Mounting-Modi"""
    print("\n" + "="*60)
    print("TEST 4: AdvancedLayoutConfig Integration")
    print("="*60)
    
    if not PV3D_AVAILABLE:
        print("PyVista nicht verfügbar - Test übersprungen")
        return False
    
    try:
        # Test 1: Süd-Ost Modus
        config1 = AdvancedLayoutConfig(
            mode="auto",
            mounting_mode="south-east"
        )
        assert config1.mounting_mode == "south-east", \
            "Mounting mode nicht korrekt gesetzt"
        print("AdvancedLayoutConfig mit south-east erstellt")
        
        # Test 2: Custom Modus
        config2 = AdvancedLayoutConfig(
            mode="auto",
            mounting_mode="custom",
            custom_azimuth=45.0,
            custom_tilt=20.0
        )
        assert config2.mounting_mode == "custom", \
            "Mounting mode nicht korrekt gesetzt"
        assert config2.custom_azimuth == 45.0, \
            "Custom azimuth nicht korrekt gesetzt"
        assert config2.custom_tilt == 20.0, \
            "Custom tilt nicht korrekt gesetzt"
        print("AdvancedLayoutConfig mit custom erstellt")
        
        # Test 3: JSON Serialisierung
        json_str = config2.to_json()
        config3 = AdvancedLayoutConfig.from_json(json_str)
        assert config3.mounting_mode == config2.mounting_mode, \
            "Mounting mode nach JSON-Roundtrip nicht identisch"
        assert config3.custom_azimuth == config2.custom_azimuth, \
            "Custom azimuth nach JSON-Roundtrip nicht identisch"
        assert config3.custom_tilt == config2.custom_tilt, \
            "Custom tilt nach JSON-Roundtrip nicht identisch"
        print("JSON Serialisierung/Deserialisierung funktioniert")
        
        return True
        
    except Exception as e:
        print(f"Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_build_scene_integration():
    """Test build_scene() mit neuen Mounting-Modi"""
    print("\n" + "="*60)
    print("TEST 5: build_scene() Integration")
    print("="*60)
    
    if not PV3D_AVAILABLE:
        print("PyVista nicht verfügbar - Test übersprungen")
        return False
    
    try:
        dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
        
        # Test mit Süd-Ost Modus
        layout = AdvancedLayoutConfig(
            mode="auto",
            mounting_mode="south-east"
        )
        
        plotter, panels = build_scene(
            project_data={},
            dims=dims,
            roof_type="Flachdach",
            module_quantity=20,
            layout_config=layout,
            off_screen=True
        )
        
        # Prüfe ob Plotter erstellt wurde
        assert plotter is not None, "Plotter nicht erstellt"
        
        # Prüfe ob Module erstellt wurden
        assert "main" in panels, "Keine main-Module im Ergebnis"
        assert len(panels["main"]) > 0, "Keine main-Module erstellt"
        
        print(f"build_scene() mit south-east erfolgreich")
        print(f"  - {len(panels['main'])} Module auf Hauptdach")
        
        # Cleanup
        plotter.close()
        
        return True
        
    except Exception as e:
        print(f"Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Führe alle Tests aus"""
    print("\n" + "="*60)
    print("ERWEITERTE AUFSTÄNDERUNGS-MODI - TEST SUITE")
    print("="*60)
    
    if not PV3D_AVAILABLE:
        print("\nPyVista nicht verfügbar - Tests können nicht ausgeführt werden")
        print("   Installiere mit: pip install pyvista vtk numpy")
        return
    
    results = []
    
    # Führe Tests aus
    results.append(("Süd-Ost Aufständerung", test_south_east_mounting()))
    results.append(("Süd-West Aufständerung", test_south_west_mounting()))
    results.append(("Individueller Modus", test_custom_mounting()))
    results.append(("AdvancedLayoutConfig", test_advanced_layout_config()))
    results.append(("build_scene() Integration", test_build_scene_integration()))
    
    # Zusammenfassung
    print("\n" + "="*60)
    print("TEST-ZUSAMMENFASSUNG")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "BESTANDEN" if result else "FEHLGESCHLAGEN"
        print(f"{status}: {name}")
    
    print(f"\n{passed}/{total} Tests bestanden")
    
    if passed == total:
        print("\n Alle Tests erfolgreich!")
        return True
    else:
        print(f"\n{total - passed} Test(s) fehlgeschlagen")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
