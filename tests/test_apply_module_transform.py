"""
Test für apply_module_transform() Funktion (Task 11.4)
"""

import sys
sys.path.insert(0, '.')

from utils.pv3d import apply_module_transform, ModuleTransform, make_panel
import numpy as np

# Prüfe ob PyVista verfügbar ist
try:
    import pyvista as pv
    PYVISTA_AVAILABLE = True
except ImportError:
    PYVISTA_AVAILABLE = False
    print("WARNUNG: PyVista nicht verfügbar, Tests werden übersprungen")


def test_apply_module_transform_basic():
    """Test: Grundlegende Transformation ohne Offsets"""
    if not PYVISTA_AVAILABLE:
        print("Test 1: Übersprungen (PyVista nicht verfügbar)")
        return
    
    print("Test 1: Grundlegende Transformation ohne Offsets...")
    
    base_position = (5.0, 3.0, 6.0)
    transform = ModuleTransform(
        index=0,
        azimuth_deg=0.0,
        tilt_deg=0.0,
        offset_x=0.0,
        offset_y=0.0,
        offset_z=0.0
    )
    
    panel = apply_module_transform(base_position, transform)
    
    # Prüfe dass Panel erstellt wurde
    assert panel is not None
    assert hasattr(panel, 'points')
    assert len(panel.points) > 0
    
    # Prüfe dass Panel-Zentrum nahe der Basis-Position ist
    center = panel.center
    assert abs(center[0] - base_position[0]) < 0.1
    assert abs(center[1] - base_position[1]) < 0.1
    assert abs(center[2] - base_position[2]) < 0.1
    
    print(f"  Panel-Zentrum: ({center[0]:.2f}, {center[1]:.2f}, {center[2]:.2f})")
    print("Grundlegende Transformation funktioniert")


def test_apply_module_transform_with_offsets():
    """Test: Transformation mit Positions-Offsets"""
    if not PYVISTA_AVAILABLE:
        print("\nTest 2: Übersprungen (PyVista nicht verfügbar)")
        return
    
    print("\nTest 2: Transformation mit Positions-Offsets...")
    
    base_position = (10.0, 5.0, 8.0)
    transform = ModuleTransform(
        index=0,
        azimuth_deg=0.0,
        tilt_deg=0.0,
        offset_x=1.5,
        offset_y=-0.5,
        offset_z=0.3
    )
    
    panel = apply_module_transform(base_position, transform)
    
    # Erwartete finale Position
    expected_x = base_position[0] + transform.offset_x  # 10.0 + 1.5 = 11.5
    expected_y = base_position[1] + transform.offset_y  # 5.0 - 0.5 = 4.5
    expected_z = base_position[2] + transform.offset_z  # 8.0 + 0.3 = 8.3
    
    # Prüfe Panel-Zentrum
    center = panel.center
    assert abs(center[0] - expected_x) < 0.1
    assert abs(center[1] - expected_y) < 0.1
    assert abs(center[2] - expected_z) < 0.1
    
    print(f"  Basis-Position: {base_position}")
    print(f"  Offsets: ({transform.offset_x}, {transform.offset_y}, {transform.offset_z})")
    print(f"  Finale Position: ({center[0]:.2f}, {center[1]:.2f}, {center[2]:.2f})")
    print("Transformation mit Offsets funktioniert")


def test_apply_module_transform_with_azimuth():
    """Test: Transformation mit Azimuth-Rotation"""
    if not PYVISTA_AVAILABLE:
        print("\nTest 3: Übersprungen (PyVista nicht verfügbar)")
        return
    
    print("\nTest 3: Transformation mit Azimuth-Rotation...")
    
    base_position = (0.0, 0.0, 5.0)
    
    # Test verschiedene Azimuth-Werte
    azimuths = [0.0, 90.0, 180.0, 270.0]
    
    for azimuth in azimuths:
        transform = ModuleTransform(
            index=0,
            azimuth_deg=azimuth,
            tilt_deg=0.0
        )
        
        panel = apply_module_transform(base_position, transform)
        
        # Prüfe dass Panel erstellt wurde
        assert panel is not None
        assert len(panel.points) > 0
        
        print(f"  Azimuth {azimuth}°: Panel erstellt mit {len(panel.points)} Punkten")
    
    print("Azimuth-Rotation funktioniert für alle Richtungen")


def test_apply_module_transform_with_tilt():
    """Test: Transformation mit Neigungs-Rotation"""
    if not PYVISTA_AVAILABLE:
        print("\nTest 4: Übersprungen (PyVista nicht verfügbar)")
        return
    
    print("\nTest 4: Transformation mit Neigungs-Rotation...")
    
    base_position = (0.0, 0.0, 5.0)
    
    # Test verschiedene Neigungs-Werte
    tilts = [0.0, 15.0, 30.0, 45.0, 90.0]
    
    for tilt in tilts:
        transform = ModuleTransform(
            index=0,
            azimuth_deg=0.0,
            tilt_deg=tilt
        )
        
        panel = apply_module_transform(base_position, transform)
        
        # Prüfe dass Panel erstellt wurde
        assert panel is not None
        assert len(panel.points) > 0
        
        print(f"  Neigung {tilt}°: Panel erstellt mit {len(panel.points)} Punkten")
    
    print("Neigungs-Rotation funktioniert für alle Winkel")


def test_apply_module_transform_combined():
    """Test: Kombinierte Transformation (Azimuth + Tilt + Offsets)"""
    if not PYVISTA_AVAILABLE:
        print("\nTest 5: Übersprungen (PyVista nicht verfügbar)")
        return
    
    print("\nTest 5: Kombinierte Transformation...")
    
    base_position = (8.0, 4.0, 6.0)
    transform = ModuleTransform(
        index=0,
        azimuth_deg=135.0,
        tilt_deg=25.0,
        offset_x=2.0,
        offset_y=-1.0,
        offset_z=0.5
    )
    
    panel = apply_module_transform(base_position, transform)
    
    # Prüfe dass Panel erstellt wurde
    assert panel is not None
    assert len(panel.points) > 0
    
    # Erwartete finale Position (mit Offsets)
    expected_x = base_position[0] + transform.offset_x
    expected_y = base_position[1] + transform.offset_y
    expected_z = base_position[2] + transform.offset_z
    
    center = panel.center
    
    # Prüfe Position (mit etwas Toleranz wegen Rotation)
    assert abs(center[0] - expected_x) < 0.5
    assert abs(center[1] - expected_y) < 0.5
    assert abs(center[2] - expected_z) < 0.5
    
    print(f"  Azimuth: {transform.azimuth_deg}°")
    print(f"  Neigung: {transform.tilt_deg}°")
    print(f"  Offsets: ({transform.offset_x}, {transform.offset_y}, {transform.offset_z})")
    print(f"  Panel-Zentrum: ({center[0]:.2f}, {center[1]:.2f}, {center[2]:.2f})")
    print("Kombinierte Transformation funktioniert")


def test_apply_module_transform_vs_make_panel():
    """Test: Vergleich mit make_panel() ohne Offsets"""
    if not PYVISTA_AVAILABLE:
        print("\nTest 6: Übersprungen (PyVista nicht verfügbar)")
        return
    
    print("\nTest 6: Vergleich mit make_panel()...")
    
    position = (5.0, 3.0, 7.0)
    azimuth = 45.0
    tilt = 20.0
    
    # Erstelle Panel mit make_panel()
    panel1 = make_panel(position, yaw_deg=azimuth, tilt_deg=tilt)
    
    # Erstelle Panel mit apply_module_transform() (ohne Offsets)
    transform = ModuleTransform(
        index=0,
        azimuth_deg=azimuth,
        tilt_deg=tilt,
        offset_x=0.0,
        offset_y=0.0,
        offset_z=0.0
    )
    panel2 = apply_module_transform(position, transform)
    
    # Vergleiche Zentren (sollten identisch sein)
    center1 = panel1.center
    center2 = panel2.center
    
    assert abs(center1[0] - center2[0]) < 0.01
    assert abs(center1[1] - center2[1]) < 0.01
    assert abs(center1[2] - center2[2]) < 0.01
    
    print(f"  make_panel() Zentrum: ({center1[0]:.2f}, {center1[1]:.2f}, {center1[2]:.2f})")
    print(f"  apply_module_transform() Zentrum: ({center2[0]:.2f}, {center2[1]:.2f}, {center2[2]:.2f})")
    print("Beide Methoden erzeugen identische Ergebnisse (ohne Offsets)")


def test_apply_module_transform_multiple_modules():
    """Test: Mehrere Module mit verschiedenen Transformationen"""
    if not PYVISTA_AVAILABLE:
        print("\nTest 7: Übersprungen (PyVista nicht verfügbar)")
        return
    
    print("\nTest 7: Mehrere Module mit verschiedenen Transformationen...")
    
    # Definiere Basis-Positionen (Raster)
    base_positions = [
        (0.0, 0.0, 5.0),
        (2.0, 0.0, 5.0),
        (4.0, 0.0, 5.0),
        (0.0, 2.0, 5.0),
        (2.0, 2.0, 5.0)
    ]
    
    # Definiere verschiedene Transformationen
    transforms = [
        ModuleTransform(index=0, azimuth_deg=0.0, tilt_deg=15.0),
        ModuleTransform(index=1, azimuth_deg=90.0, tilt_deg=20.0),
        ModuleTransform(index=2, azimuth_deg=180.0, tilt_deg=25.0),
        ModuleTransform(index=3, azimuth_deg=270.0, tilt_deg=30.0),
        ModuleTransform(index=4, azimuth_deg=45.0, tilt_deg=35.0, offset_x=0.5)
    ]
    
    panels = []
    for base_pos, transform in zip(base_positions, transforms):
        panel = apply_module_transform(base_pos, transform)
        panels.append(panel)
        
        assert panel is not None
        assert len(panel.points) > 0
    
    print(f"  {len(panels)} Module erfolgreich erstellt")
    print("Mehrere Module mit verschiedenen Transformationen funktionieren")


def test_apply_module_transform_with_group_id():
    """Test: Transformation mit Gruppen-ID"""
    if not PYVISTA_AVAILABLE:
        print("\nTest 8: Übersprungen (PyVista nicht verfügbar)")
        return
    
    print("\nTest 8: Transformation mit Gruppen-ID...")
    
    base_position = (5.0, 5.0, 6.0)
    transform = ModuleTransform(
        index=0,
        azimuth_deg=90.0,
        tilt_deg=25.0,
        group_id="south_roof"
    )
    
    panel = apply_module_transform(base_position, transform)
    
    # Prüfe dass Panel erstellt wurde
    assert panel is not None
    assert len(panel.points) > 0
    
    # Gruppen-ID wird nicht im Panel gespeichert, aber Transform sollte sie haben
    assert transform.group_id == "south_roof"
    
    print(f"  Modul mit Gruppen-ID '{transform.group_id}' erstellt")
    print("Transformation mit Gruppen-ID funktioniert")


def main():
    """Führe alle Tests aus"""
    print("=" * 70)
    print("apply_module_transform() Tests (Task 11.4)")
    print("=" * 70)
    
    if not PYVISTA_AVAILABLE:
        print("\nWARNUNG: PyVista nicht verfügbar")
        print("Tests werden übersprungen")
        print("=" * 70)
        return True
    
    try:
        test_apply_module_transform_basic()
        test_apply_module_transform_with_offsets()
        test_apply_module_transform_with_azimuth()
        test_apply_module_transform_with_tilt()
        test_apply_module_transform_combined()
        test_apply_module_transform_vs_make_panel()
        test_apply_module_transform_multiple_modules()
        test_apply_module_transform_with_group_id()
        
        print("\n" + "=" * 70)
        print("ALLE TESTS ERFOLGREICH")
        print("=" * 70)
        return True
        
    except AssertionError as e:
        print(f"\nTEST FEHLGESCHLAGEN: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\nUNERWARTETER FEHLER: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
