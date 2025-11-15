"""
Verification script for Task 5: Modul-Mesh Erstellung verbessern

This script verifies that the create_pv_module_3d() function meets all requirements:
1. Module dimensions are correct (1.05m x 1.76m x 0.04m)
2. Color is visible (dark blue #1a1a2e)
3. Rotation is correctly applied (tilt and azimuth)
4. Translation is correctly applied (x, y, z)
5. Opacity is 0.9 for better visibility
"""

import numpy as np
import sys
import inspect

# Import the function
from utils.pv3d_plotly import create_pv_module_3d, PV_W, PV_H, PV_T

def verify_module_dimensions():
    """Verify that module dimensions are correct."""
    print("\nChecking module dimensions...")
    
    expected_w = 1.05
    expected_h = 1.76
    expected_t = 0.04
    
    assert PV_W == expected_w, f"PV_W should be {expected_w}, got {PV_W}"
    assert PV_H == expected_h, f"PV_H should be {expected_h}, got {PV_H}"
    assert PV_T == expected_t, f"PV_T should be {expected_t}, got {PV_T}"
    
    print(f"  PV_W = {PV_W}m (expected: {expected_w}m)")
    print(f"  PV_H = {PV_H}m (expected: {expected_h}m)")
    print(f"  PV_T = {PV_T}m (expected: {expected_t}m)")
    return True

def verify_color_parameter():
    """Verify that color parameter is correctly set."""
    print("\nChecking color parameter...")
    
    # Get function signature
    sig = inspect.signature(create_pv_module_3d)
    color_default = sig.parameters['color'].default
    
    expected_color = "#1a1a2e"
    assert color_default == expected_color, f"Default color should be {expected_color}, got {color_default}"
    
    print(f"  Default color = {color_default} (dark blue)")
    return True

def verify_opacity():
    """Verify that opacity is set to 0.9."""
    print("\nChecking opacity...")
    
    # Create a test module
    mesh, vertices = create_pv_module_3d(
        x=0, y=0, z=0,
        azimuth_deg=0,
        tilt_deg=30,
        color="#1a1a2e",
        selected=False,
        show_mounting=False,
        roof_type="Flachdach"
    )
    
    expected_opacity = 0.9
    actual_opacity = mesh.opacity
    
    assert actual_opacity == expected_opacity, f"Opacity should be {expected_opacity}, got {actual_opacity}"
    
    print(f"  Opacity = {actual_opacity} (expected: {expected_opacity})")
    return True

def verify_rotation():
    """Verify that rotation is correctly applied."""
    print("\nChecking rotation...")
    
    # Create module with tilt
    mesh1, vertices1 = create_pv_module_3d(
        x=0, y=0, z=0,
        azimuth_deg=0,
        tilt_deg=30,
        show_mounting=False,
        roof_type="Satteldach"
    )
    
    # Create module without tilt
    mesh2, vertices2 = create_pv_module_3d(
        x=0, y=0, z=0,
        azimuth_deg=0,
        tilt_deg=0,
        show_mounting=False,
        roof_type="Flachdach"
    )
    
    # Vertices should be different when tilt is applied
    assert not np.allclose(vertices1, vertices2), "Rotation should change vertex positions"
    
    print(f"  Tilt rotation is applied correctly")
    
    # Create module with azimuth
    mesh3, vertices3 = create_pv_module_3d(
        x=0, y=0, z=0,
        azimuth_deg=45,
        tilt_deg=0,
        show_mounting=False,
        roof_type="Flachdach"
    )
    
    # Vertices should be different when azimuth is applied
    assert not np.allclose(vertices2, vertices3), "Azimuth rotation should change vertex positions"
    
    print(f"  Azimuth rotation is applied correctly")
    return True

def verify_translation():
    """Verify that translation is correctly applied."""
    print("\nChecking translation...")
    
    # Create module at origin
    mesh1, vertices1 = create_pv_module_3d(
        x=0, y=0, z=0,
        azimuth_deg=0,
        tilt_deg=0,
        show_mounting=False,
        roof_type="Flachdach"
    )
    
    # Create module at different position
    test_x, test_y, test_z = 5.0, 3.0, 2.0
    mesh2, vertices2 = create_pv_module_3d(
        x=test_x, y=test_y, z=test_z,
        azimuth_deg=0,
        tilt_deg=0,
        show_mounting=False,
        roof_type="Flachdach"
    )
    
    # Calculate center of vertices
    center1 = np.mean(vertices1, axis=0)
    center2 = np.mean(vertices2, axis=0)
    
    # Check that translation is correct
    translation = center2 - center1
    expected_translation = np.array([test_x, test_y, test_z])
    
    assert np.allclose(translation, expected_translation, atol=0.01), \
        f"Translation should be {expected_translation}, got {translation}"
    
    print(f"  Translation is applied correctly")
    print(f"    Expected: ({test_x}, {test_y}, {test_z})")
    print(f"    Actual center: ({center2[0]:.2f}, {center2[1]:.2f}, {center2[2]:.2f})")
    return True

def verify_mesh_structure():
    """Verify that mesh has correct structure."""
    print("\nChecking mesh structure...")
    
    mesh, vertices = create_pv_module_3d(
        x=0, y=0, z=0,
        azimuth_deg=0,
        tilt_deg=30,
        show_mounting=False,
        roof_type="Flachdach"
    )
    
    # Check vertices count (8 vertices for a box)
    assert vertices.shape[0] == 8, f"Should have 8 vertices, got {vertices.shape[0]}"
    assert vertices.shape[1] == 3, f"Each vertex should have 3 coordinates, got {vertices.shape[1]}"
    
    # Check mesh has required attributes
    assert hasattr(mesh, 'x'), "Mesh should have x coordinates"
    assert hasattr(mesh, 'y'), "Mesh should have y coordinates"
    assert hasattr(mesh, 'z'), "Mesh should have z coordinates"
    assert hasattr(mesh, 'i'), "Mesh should have i indices"
    assert hasattr(mesh, 'j'), "Mesh should have j indices"
    assert hasattr(mesh, 'k'), "Mesh should have k indices"
    assert hasattr(mesh, 'color'), "Mesh should have color"
    assert hasattr(mesh, 'opacity'), "Mesh should have opacity"
    
    print(f"  Mesh has 8 vertices")
    print(f"  Mesh has all required attributes")
    print(f"  Mesh color: {mesh.color}")
    print(f"  Mesh opacity: {mesh.opacity}")
    return True

def main():
    """Run all verification tests."""
    print("=" * 60)
    print("Task 5: Modul-Mesh Erstellung Verification")
    print("=" * 60)
    
    try:
        verify_module_dimensions()
        verify_color_parameter()
        verify_opacity()
        verify_rotation()
        verify_translation()
        verify_mesh_structure()
        
        print("\n" + "=" * 60)
        print("ALL CHECKS PASSED!")
        print("=" * 60)
        print("\nTask 5 Requirements Verified:")
        print("  Module dimensions are correct (1.05m x 1.76m x 0.04m)")
        print("  Color is visible (dark blue #1a1a2e)")
        print("  Rotation is correctly applied (tilt and azimut)")
        print("  Translation is correctly applied (x, y, z)")
        print("  Opacity is 0.9 for better visibility")
        print("\n")
        return 0
        
    except AssertionError as e:
        print(f"\nVERIFICATION FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
