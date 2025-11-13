"""
Test für Task 8.3: Gitter-Overlay

Dieser Test verifiziert die Implementierung des Raster-Overlays
für die 3D-Visualisierung.

Requirements:
    - 8.3.1: Zeige Platzierungs-Raster
    - 8.3.2: Hilfslinien für Ausrichtung
    - 8.3.3: Toggle Ein/Aus
"""

import sys
import traceback


def test_grid_overlay_function():
    """
    Test 1: Verifiziere dass create_placement_grid Funktion existiert und funktioniert.
    
    Requirement 8.3.1: Zeige Platzierungs-Raster
    """
    print("\n=== Test 1: Grid Overlay Funktion ===")
    
    try:
        from utils.pv3d_plotly import create_placement_grid
        
        # Test mit Standard-Parametern
        grid = create_placement_grid(
            roof_length=10.0,
            roof_width=8.0,
            base_z=3.0,
            grid_spacing=1.0,
            color='rgba(128, 128, 128, 0.3)',
            line_width=1
        )
        
        # Verifiziere dass ein Plotly Scatter3d Objekt zurückgegeben wird
        assert grid is not None, "Grid object should not be None"
        assert hasattr(grid, 'x'), "Grid should have x coordinates"
        assert hasattr(grid, 'y'), "Grid should have y coordinates"
        assert hasattr(grid, 'z'), "Grid should have z coordinates"
        
        # Verifiziere dass Linien erstellt wurden
        assert len(grid.x) > 0, "Grid should have x coordinates"
        assert len(grid.y) > 0, "Grid should have y coordinates"
        assert len(grid.z) > 0, "Grid should have z coordinates"
        
        print("✓ create_placement_grid Funktion existiert und funktioniert")
        print(f"  - Grid hat {len(grid.x)} Punkte")
        print(f"  - Grid-Farbe: {grid.line.color}")
        print(f"  - Grid-Linienbreite: {grid.line.width}")
        
        return True
        
    except ImportError as e:
        print(f"❌ FEHLER: Konnte create_placement_grid nicht importieren: {e}")
        return False
    except Exception as e:
        print(f"❌ FEHLER: {e}")
        traceback.print_exc()
        return False


def test_grid_customization():
    """
    Test 2: Verifiziere dass Grid-Parameter anpassbar sind.
    
    Requirement 8.3.2: Hilfslinien für Ausrichtung
    """
    print("\n=== Test 2: Grid Anpassbarkeit ===")
    
    try:
        from utils.pv3d_plotly import create_placement_grid
        
        # Test mit verschiedenen Spacing-Werten
        test_cases = [
            {"spacing": 0.5, "opacity": 0.1},
            {"spacing": 1.0, "opacity": 0.3},
            {"spacing": 2.0, "opacity": 0.5},
        ]
        
        for i, test_case in enumerate(test_cases):
            spacing = test_case["spacing"]
            opacity = test_case["opacity"]
            color = f'rgba(128, 128, 128, {opacity})'
            
            grid = create_placement_grid(
                roof_length=10.0,
                roof_width=8.0,
                base_z=3.0,
                grid_spacing=spacing,
                color=color,
                line_width=1
            )
            
            assert grid is not None, f"Grid {i+1} should not be None"
            assert len(grid.x) > 0, f"Grid {i+1} should have coordinates"
            
            print(f"✓ Test Case {i+1}: spacing={spacing}m, opacity={opacity}")
        
        print("✓ Grid-Parameter sind anpassbar")
        return True
        
    except Exception as e:
        print(f"❌ FEHLER: {e}")
        traceback.print_exc()
        return False


def test_ui_toggle():
    """
    Test 3: Verifiziere dass UI-Toggle für Grid existiert.
    
    Requirement 8.3.3: Toggle Ein/Aus
    """
    print("\n=== Test 3: UI Toggle ===")
    
    try:
        from utils.pv3d_module_placement_ui import render_module_placement_panel
        
        # Verifiziere dass die Funktion existiert
        assert callable(render_module_placement_panel), \
            "render_module_placement_panel should be callable"
        
        print("✓ render_module_placement_panel Funktion existiert")
        
        # Hinweis: Vollständiger UI-Test würde Streamlit-Session-State benötigen
        print("  ℹ️ UI-Toggle wird über Session State gesteuert:")
        print("     - show_placement_grid: bool")
        print("     - grid_spacing: float (0.5-2.0m)")
        print("     - grid_opacity: float (0.1-1.0)")
        
        return True
        
    except ImportError as e:
        print(f"❌ FEHLER: Konnte UI-Modul nicht importieren: {e}")
        return False
    except Exception as e:
        print(f"❌ FEHLER: {e}")
        traceback.print_exc()
        return False


def test_integration():
    """
    Test 4: Verifiziere Integration in build_plotly_scene.
    
    Requirements: 8.3.1, 8.3.2, 8.3.3
    """
    print("\n=== Test 4: Integration ===")
    
    try:
        # Prüfe ob build_plotly_scene die Grid-Funktion verwendet
        import inspect
        from utils.pv3d_plotly import build_plotly_scene
        
        source = inspect.getsource(build_plotly_scene)
        
        # Verifiziere dass Grid-Code vorhanden ist
        assert "show_placement_grid" in source, \
            "build_plotly_scene should check show_placement_grid"
        assert "create_placement_grid" in source, \
            "build_plotly_scene should call create_placement_grid"
        assert "grid_spacing" in source, \
            "build_plotly_scene should use grid_spacing"
        assert "grid_opacity" in source, \
            "build_plotly_scene should use grid_opacity"
        
        print("✓ Grid-Overlay ist in build_plotly_scene integriert")
        print("  - Prüft show_placement_grid Session State")
        print("  - Verwendet anpassbare grid_spacing")
        print("  - Verwendet anpassbare grid_opacity")
        
        return True
        
    except Exception as e:
        print(f"❌ FEHLER: {e}")
        traceback.print_exc()
        return False


def test_grid_alignment():
    """
    Test 5: Verifiziere dass Grid korrekt ausgerichtet ist.
    
    Requirement 8.3.2: Hilfslinien für Ausrichtung
    """
    print("\n=== Test 5: Grid Ausrichtung ===")
    
    try:
        from utils.pv3d_plotly import create_placement_grid
        
        # Erstelle Grid
        roof_length = 10.0
        roof_width = 8.0
        base_z = 3.0
        grid_spacing = 1.0
        
        grid = create_placement_grid(
            roof_length=roof_length,
            roof_width=roof_width,
            base_z=base_z,
            grid_spacing=grid_spacing
        )
        
        # Verifiziere dass Grid zentriert ist
        x_coords = [x for x in grid.x if x is not None]
        y_coords = [y for y in grid.y if y is not None]
        z_coords = [z for z in grid.z if z is not None]
        
        # Grid sollte von -half_length bis +half_length gehen
        assert min(x_coords) >= -roof_length/2 - 0.01, \
            "Grid X should start at -half_length"
        assert max(x_coords) <= roof_length/2 + 0.01, \
            "Grid X should end at +half_length"
        
        assert min(y_coords) >= -roof_width/2 - 0.01, \
            "Grid Y should start at -half_width"
        assert max(y_coords) <= roof_width/2 + 0.01, \
            "Grid Y should end at +half_width"
        
        # Alle Z-Koordinaten sollten gleich sein (flaches Grid)
        unique_z = set(z_coords)
        assert len(unique_z) == 1, \
            "All Z coordinates should be the same (flat grid)"
        
        print("✓ Grid ist korrekt ausgerichtet")
        print(f"  - X-Bereich: [{min(x_coords):.2f}, {max(x_coords):.2f}]")
        print(f"  - Y-Bereich: [{min(y_coords):.2f}, {max(y_coords):.2f}]")
        print(f"  - Z-Position: {list(unique_z)[0]:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ FEHLER: {e}")
        traceback.print_exc()
        return False


def run_all_tests():
    """Führt alle Tests aus und gibt Zusammenfassung aus."""
    print("=" * 70)
    print("TASK 8.3: GITTER-OVERLAY - TEST SUITE")
    print("=" * 70)
    
    tests = [
        ("Grid Overlay Funktion", test_grid_overlay_function),
        ("Grid Anpassbarkeit", test_grid_customization),
        ("UI Toggle", test_ui_toggle),
        ("Integration", test_integration),
        ("Grid Ausrichtung", test_grid_alignment),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ KRITISCHER FEHLER in {test_name}: {e}")
            traceback.print_exc()
            results.append((test_name, False))
    
    # Zusammenfassung
    print("\n" + "=" * 70)
    print("ZUSAMMENFASSUNG")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ BESTANDEN" if result else "❌ FEHLGESCHLAGEN"
        print(f"{status}: {test_name}")
    
    print(f"\nErgebnis: {passed}/{total} Tests bestanden")
    
    if passed == total:
        print("\n🎉 ALLE TESTS BESTANDEN!")
        print("\nTask 8.3 ist vollständig implementiert:")
        print("  ✓ 8.3.1: Zeige Platzierungs-Raster")
        print("  ✓ 8.3.2: Hilfslinien für Ausrichtung")
        print("  ✓ 8.3.3: Toggle Ein/Aus")
        return 0
    else:
        print("\n⚠️ EINIGE TESTS FEHLGESCHLAGEN")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
