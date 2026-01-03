"""
Standalone test for Task 7.1: Modul-Hervorhebung
"""

import numpy as np
from utils.pv3d_plotly import (
    create_pv_module_3d_with_highlight,
    create_module_edges_with_glow,
    _extract_box_edges
)

def test_normal_module():
    """Test normal module without highlighting"""
    print("Testing normal module...")
    result, vertices = create_pv_module_3d_with_highlight(
        x=0.0, y=0.0, z=1.0, selected=False, hover=False
    )
    assert not isinstance(result, list), "Normal module should not be a list"
    assert vertices.shape == (8, 3), "Should have 8 vertices with 3 coordinates"
    print("✓ Normal module test passed")

def test_selected_module():
    """Test selected module with glowing edges"""
    print("Testing selected module...")
    result, vertices = create_pv_module_3d_with_highlight(
        x=0.0, y=0.0, z=1.0, selected=True, hover=False
    )
    assert isinstance(result, list), "Selected module should be a list"
    assert len(result) == 2, "Should contain mesh and edges"
    mesh, edges = result
    assert edges.mode == 'lines', "Edges should be lines"
    assert edges.line.color == '#4a90e2', "Edges should be light blue"
    assert edges.line.width == 4, "Edges should have width 4"
    assert edges.opacity == 0.9, "Edges should have opacity 0.9"
    print("✓ Selected module test passed")

def test_hover_module():
    """Test module with hover effect"""
    print("Testing hover module...")
    result, vertices = create_pv_module_3d_with_highlight(
        x=0.0, y=0.0, z=1.0, selected=False, hover=True
    )
    assert not isinstance(result, list), "Hover module should not be a list"
    assert result.lighting.ambient == 0.8, "Ambient lighting should be increased"
    assert result.opacity == 0.95, "Opacity should be 0.95"
    print("✓ Hover module test passed")

def test_edges_creation():
    """Test edge creation"""
    print("Testing edge creation...")
    vertices = np.array([
        [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
        [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1],
    ])
    edges = create_module_edges_with_glow(
        vertices, color='#ff0000', width=5, glow_intensity=0.8
    )
    assert edges.mode == 'lines', "Should be in lines mode"
    assert edges.line.color == '#ff0000', "Should be red"
    assert edges.line.width == 5, "Should have width 5"
    assert edges.opacity == 0.8, "Should have opacity 0.8"
    print("✓ Edge creation test passed")

def test_extract_edges():
    """Test edge extraction from vertices"""
    print("Testing edge extraction...")
    vertices = np.array([
        [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0],
        [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1],
    ])
    edges_x, edges_y, edges_z = _extract_box_edges(vertices)
    # 12 edges × 3 entries (start, end, None) = 36
    assert len(edges_x) == 36, f"Should have 36 X coordinates, got {len(edges_x)}"
    assert len(edges_y) == 36, f"Should have 36 Y coordinates, got {len(edges_y)}"
    assert len(edges_z) == 36, f"Should have 36 Z coordinates, got {len(edges_z)}"
    
    # Check None separators
    none_count = sum(1 for x in edges_x if x is None)
    assert none_count == 12, f"Should have 12 None values, got {none_count}"
    print("✓ Edge extraction test passed")

def test_multiple_orientations():
    """Test highlighting with different orientations"""
    print("Testing multiple orientations...")
    orientations = [(0, 15), (90, 30), (180, 45), (270, 60)]
    
    for azimuth, tilt in orientations:
        result, vertices = create_pv_module_3d_with_highlight(
            x=0.0, y=0.0, z=1.0,
            azimuth_deg=azimuth,
            tilt_deg=tilt,
            selected=True
        )
        assert isinstance(result, list), f"Orientation ({azimuth}°, {tilt}°) should be a list"
        assert not np.allclose(vertices[0], vertices[1]), "Vertices should be different"
    print("✓ Multiple orientations test passed")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("TASK 7.1: MODUL-HERVORHEBUNG TESTS")
    print("="*60 + "\n")
    
    try:
        test_normal_module()
        test_selected_module()
        test_hover_module()
        test_edges_creation()
        test_extract_edges()
        test_multiple_orientations()
        
        print("\n" + "="*60)
        print("✓ ALL TESTS PASSED (6/6)")
        print("="*60 + "\n")
        print("Task 7.1 implementation is complete and working!")
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
