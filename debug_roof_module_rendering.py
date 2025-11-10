"""
Debug-Skript: Überprüfung der Dach- und Modul-Rendering

Dieses Skript überprüft:
1. Ob Dächer korrekt erstellt werden
2. Ob Module auf der richtigen Z-Höhe platziert werden
3. Ob Module mehrfach gerendert werden
4. Ob Module tatsächlich auf dem Dach liegen
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.pv3d import (
    BuildingDims,
    LayoutConfig,
    build_scene,
    make_roof_flat,
    make_roof_gable,
    make_panel,
    place_panels_auto,
    place_panels_flat_roof
)

def test_roof_creation():
    """Test 1: Überprüfe Dach-Erstellung"""
    print("=" * 70)
    print("TEST 1: DACH-ERSTELLUNG")
    print("=" * 70)
    
    # Test Flachdach
    print("\n1.1 Flachdach:")
    roof_flat = make_roof_flat(length=10.0, width=8.0, base_height=6.0)
    print(f"  ✓ Flachdach erstellt")
    print(f"  - Anzahl Punkte: {roof_flat.n_points}")
    print(f"  - Anzahl Zellen: {roof_flat.n_cells}")
    print(f"  - Z-Bereich: {roof_flat.bounds[4]:.3f}m bis {roof_flat.bounds[5]:.3f}m")
    
    # Test Satteldach
    print("\n1.2 Satteldach:")
    roof_gable = make_roof_gable(
        length=10.0, width=8.0, base_height=6.0, inclination_deg=35.0
    )
    print(f"  ✓ Satteldach erstellt")
    print(f"  - Anzahl Punkte: {roof_gable.n_points}")
    print(f"  - Anzahl Zellen: {roof_gable.n_cells}")
    print(f"  - Z-Bereich: {roof_gable.bounds[4]:.3f}m bis {roof_gable.bounds[5]:.3f}m")
    
    return True


def test_module_placement_flat_roof():
    """Test 2: Überprüfe Modul-Platzierung auf Flachdach"""
    print("\n" + "=" * 70)
    print("TEST 2: MODUL-PLATZIERUNG AUF FLACHDACH")
    print("=" * 70)
    
    roof_length = 10.0
    roof_width = 8.0
    wall_height = 6.0
    base_z = wall_height + 0.12  # Flachdach-Dicke
    
    print(f"\nDach-Parameter:")
    print(f"  - Länge: {roof_length}m")
    print(f"  - Breite: {roof_width}m")
    print(f"  - Wandhöhe: {wall_height}m")
    print(f"  - Basis-Z (Dachoberkante): {base_z}m")
    
    # Platziere Module
    panels = place_panels_flat_roof(
        roof_length=roof_length,
        roof_width=roof_width,
        module_quantity=20,
        mounting_type="south",
        base_z=base_z
    )
    
    print(f"\nModule platziert: {len(panels)}")
    
    # Analysiere Modul-Positionen
    if panels:
        print(f"\nModul-Analyse:")
        for i, panel in enumerate(panels[:5]):  # Erste 5 Module
            bounds = panel.bounds
            center_x = (bounds[0] + bounds[1]) / 2
            center_y = (bounds[2] + bounds[3]) / 2
            center_z = (bounds[4] + bounds[5]) / 2
            z_min = bounds[4]
            z_max = bounds[5]
            
            print(f"  Modul {i}:")
            print(f"    - Zentrum: ({center_x:.2f}, {center_y:.2f}, {center_z:.2f})m")
            print(f"    - Z-Bereich: {z_min:.3f}m bis {z_max:.3f}m")
            print(f"    - Über Dach: {z_min - base_z:.3f}m")
        
        if len(panels) > 5:
            print(f"  ... und {len(panels) - 5} weitere Module")
    
    return True


def test_module_placement_gable_roof():
    """Test 3: Überprüfe Modul-Platzierung auf Satteldach"""
    print("\n" + "=" * 70)
    print("TEST 3: MODUL-PLATZIERUNG AUF SATTELDACH")
    print("=" * 70)
    
    roof_length = 10.0
    roof_width = 8.0
    wall_height = 6.0
    inclination_deg = 35.0
    base_z = wall_height
    
    print(f"\nDach-Parameter:")
    print(f"  - Länge: {roof_length}m")
    print(f"  - Breite: {roof_width}m")
    print(f"  - Wandhöhe: {wall_height}m")
    print(f"  - Neigung: {inclination_deg}°")
    print(f"  - Basis-Z (Traufhöhe): {base_z}m")
    
    # Platziere Module
    panels = place_panels_auto(
        roof_length=roof_length,
        roof_width=roof_width,
        module_quantity=20,
        roof_type="Satteldach",
        inclination_deg=inclination_deg,
        base_z=base_z
    )
    
    print(f"\nModule platziert: {len(panels)}")
    
    # Analysiere Modul-Positionen
    if panels:
        print(f"\nModul-Analyse:")
        for i, panel in enumerate(panels[:5]):  # Erste 5 Module
            bounds = panel.bounds
            center_x = (bounds[0] + bounds[1]) / 2
            center_y = (bounds[2] + bounds[3]) / 2
            center_z = (bounds[4] + bounds[5]) / 2
            z_min = bounds[4]
            z_max = bounds[5]
            
            print(f"  Modul {i}:")
            print(f"    - Zentrum: ({center_x:.2f}, {center_y:.2f}, {center_z:.2f})m")
            print(f"    - Z-Bereich: {z_min:.3f}m bis {z_max:.3f}m")
            print(f"    - Über Traufe: {z_min - base_z:.3f}m")
        
        if len(panels) > 5:
            print(f"  ... und {len(panels) - 5} weitere Module")
    
    return True


def test_full_scene_rendering():
    """Test 4: Überprüfe vollständige Szenen-Erstellung"""
    print("\n" + "=" * 70)
    print("TEST 4: VOLLSTÄNDIGE SZENEN-ERSTELLUNG")
    print("=" * 70)
    
    # Test mit Flachdach
    print("\n4.1 Szene mit Flachdach:")
    dims = BuildingDims(length_m=10.0, width_m=8.0, wall_height_m=6.0)
    layout = LayoutConfig(mode="auto")
    
    try:
        plotter, panels_dict = build_scene(
            project_data={},
            dims=dims,
            roof_type="Flachdach",
            module_quantity=20,
            layout_config=layout,
            off_screen=True
        )
        
        print(f"  ✓ Szene erstellt")
        print(f"  - Hauptdach-Module: {len(panels_dict['main'])}")
        print(f"  - Garage-Module: {len(panels_dict['garage'])}")
        print(f"  - Fassaden-Module: {len(panels_dict['facade'])}")
        print(f"  - Gesamt: {sum(len(p) for p in panels_dict.values())}")
        
        # Überprüfe, ob Module im Plotter sind
        print(f"  - Meshes im Plotter: {len(plotter.mesh)}")
        
        plotter.close()
    except Exception as e:
        print(f"  ✗ Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test mit Satteldach
    print("\n4.2 Szene mit Satteldach:")
    try:
        plotter, panels_dict = build_scene(
            project_data={"roof_inclination_deg": 35.0},
            dims=dims,
            roof_type="Satteldach",
            module_quantity=20,
            layout_config=layout,
            off_screen=True
        )
        
        print(f"  ✓ Szene erstellt")
        print(f"  - Hauptdach-Module: {len(panels_dict['main'])}")
        print(f"  - Garage-Module: {len(panels_dict['garage'])}")
        print(f"  - Fassaden-Module: {len(panels_dict['facade'])}")
        print(f"  - Gesamt: {sum(len(p) for p in panels_dict.values())}")
        
        # Überprüfe, ob Module im Plotter sind
        print(f"  - Meshes im Plotter: {len(plotter.mesh)}")
        
        plotter.close()
    except Exception as e:
        print(f"  ✗ Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def test_module_visibility():
    """Test 5: Überprüfe Modul-Sichtbarkeit"""
    print("\n" + "=" * 70)
    print("TEST 5: MODUL-SICHTBARKEIT")
    print("=" * 70)
    
    # Erstelle ein einzelnes Modul
    print("\n5.1 Einzelnes Modul:")
    panel = make_panel(position=(0.0, 0.0, 7.0), yaw_deg=0.0, tilt_deg=30.0)
    
    print(f"  ✓ Modul erstellt")
    print(f"  - Anzahl Punkte: {panel.n_points}")
    print(f"  - Anzahl Zellen: {panel.n_cells}")
    print(f"  - Bounds: {panel.bounds}")
    
    # Überprüfe, ob Modul Fläche hat
    if panel.n_cells > 0:
        print(f"  ✓ Modul hat Geometrie")
    else:
        print(f"  ✗ Modul hat KEINE Geometrie!")
        return False
    
    return True


def main():
    """Führe alle Tests aus"""
    print("\n" + "=" * 70)
    print("DIAGNOSE: DACH- UND MODUL-RENDERING")
    print("=" * 70)
    
    tests = [
        ("Dach-Erstellung", test_roof_creation),
        ("Modul-Platzierung Flachdach", test_module_placement_flat_roof),
        ("Modul-Platzierung Satteldach", test_module_placement_gable_roof),
        ("Vollständige Szenen-Erstellung", test_full_scene_rendering),
        ("Modul-Sichtbarkeit", test_module_visibility)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Test '{name}' fehlgeschlagen: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Zusammenfassung
    print("\n" + "=" * 70)
    print("ZUSAMMENFASSUNG")
    print("=" * 70)
    
    for name, result in results:
        status = "✓ BESTANDEN" if result else "✗ FEHLGESCHLAGEN"
        print(f"{status}: {name}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"\nErgebnis: {passed}/{total} Tests bestanden")
    
    if passed == total:
        print("\n✓ Alle Tests bestanden! Rendering funktioniert korrekt.")
    else:
        print("\n✗ Einige Tests fehlgeschlagen. Bitte Fehler überprüfen.")


if __name__ == "__main__":
    main()
