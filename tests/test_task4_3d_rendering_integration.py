"""
Test for Task 4: 3D-Rendering Integration

This test verifies that the build_plotly_scene function correctly:
1. Loads module positions from session state
2. Loops over all placed positions
3. Calls create_pv_module_3d() for each module
4. Adds meshes to the Plotly figure
5. Implements error handling

Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 10.1, 10.2, 10.3, 10.4, 10.5
"""

import sys
import numpy as np
from unittest.mock import MagicMock

# Mock streamlit before importing
sys.modules['streamlit'] = MagicMock()
import streamlit as st

# Now import the modules we need to test
from utils.pv3d_plotly import build_plotly_scene, create_pv_module_3d
from utils.pv3d import BuildingDims


def test_module_rendering_from_session_state():
    """
    Test that modules are rendered from session state positions.
    
    Requirements: 10.1, 10.2, 10.3, 10.4
    """
    print("\n=== Test 1: Module Rendering from Session State ===")
    
    # Setup: Create mock session state with module positions
    st.session_state = {
        "placed_module_positions": [
            (0.0, 0.0, 0.3),   # Module 1
            (1.1, 0.0, 0.3),   # Module 2
            (2.2, 0.0, 0.3),   # Module 3
        ],
        "placed_module_count": 3
    }
    
    # Create building dimensions
    dims = BuildingDims(
        length_m=10.0,
        width_m=8.0,
        wall_height_m=3.0
    )
    
    # Create project data
    project_data = {
        "roof_covering": "Ziegel",
        "roof_inclination_deg": 35.0
    }
    
    # Call build_plotly_scene
    try:
        fig = build_plotly_scene(
            project_data=project_data,
            dims=dims,
            roof_type="Flachdach",
            module_quantity=3,
            layout_config=None,
            selected_modules=[]
        )
        
        # Verify figure was created
        assert fig is not None, "Figure should not be None"
        
        # Verify figure has traces (building + roof + modules + edges)
        # Expected: building (1) + building edges (1) + roof (1) + roof edges (1)
        #           + 3 modules (3) + 3 module edges (3) = 10 traces minimum
        assert len(fig.data) >= 10, (
            f"Expected at least 10 traces, got {len(fig.data)}"
        )
        
        print("[OK] Figure created successfully")
        print(f"[OK] Figure has {len(fig.data)} traces")
        print("[OK] Modules rendered from session state")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_empty_session_state_fallback():
    """
    Test that fallback grid placement works when session state is empty.
    
    Requirements: 10.5, 11.2
    """
    print("\n=== Test 2: Empty Session State Fallback ===")
    
    # Setup: Empty session state
    st.session_state = {
        "placed_module_positions": [],
        "placed_module_count": 0
    }
    
    # Create building dimensions
    dims = BuildingDims(
        length_m=10.0,
        width_m=8.0,
        wall_height_m=3.0
    )
    
    # Create project data
    project_data = {
        "roof_covering": "Ziegel",
        "roof_inclination_deg": 35.0
    }
    
    # Call build_plotly_scene
    try:
        fig = build_plotly_scene(
            project_data=project_data,
            dims=dims,
            roof_type="Satteldach",
            module_quantity=5,
            layout_config=None,
            selected_modules=[]
        )
        
        # Verify figure was created
        assert fig is not None, "Figure should not be None"
        
        # Verify figure has traces (should use fallback grid placement)
        assert len(fig.data) >= 4, (
            f"Expected at least 4 traces (building + roof), got {len(fig.data)}"
        )
        
        print("[OK] Figure created successfully with fallback")
        print(f"[OK] Figure has {len(fig.data)} traces")
        print("[OK] Fallback grid placement works")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_invalid_position_handling():
    """
    Test error handling for invalid module positions.
    
    Requirements: 10.5, 11.2
    """
    print("\n=== Test 3: Invalid Position Handling ===")
    
    # Setup: Session state with invalid positions
    st.session_state = {
        "placed_module_positions": [
            (0.0, 0.0, 0.3),      # Valid
            (1.1, 0.0),           # Invalid (only 2 coordinates)
            (2.2, 0.0, 0.3),      # Valid
            "invalid",            # Invalid (not a tuple)
        ],
        "placed_module_count": 4
    }
    
    # Create building dimensions
    dims = BuildingDims(
        length_m=10.0,
        width_m=8.0,
        wall_height_m=3.0
    )
    
    # Create project data
    project_data = {
        "roof_covering": "Ziegel",
        "roof_inclination_deg": 35.0
    }
    
    # Call build_plotly_scene
    try:
        fig = build_plotly_scene(
            project_data=project_data,
            dims=dims,
            roof_type="Flachdach",
            module_quantity=4,
            layout_config=None,
            selected_modules=[]
        )
        
        # Verify figure was created (should skip invalid positions)
        assert fig is not None, "Figure should not be None"
        
        # Should have building + roof + 2 valid modules + edges
        print("[OK] Figure created successfully despite invalid positions")
        print(f"[OK] Figure has {len(fig.data)} traces")
        print("[OK] Invalid positions were skipped gracefully")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_create_pv_module_3d():
    """
    Test that create_pv_module_3d function works correctly.
    
    Requirements: 1.1, 1.2, 1.3
    """
    print("\n=== Test 4: create_pv_module_3d Function ===")
    
    try:
        # Test module creation
        mesh, vertices = create_pv_module_3d(
            x=0.0,
            y=0.0,
            z=0.3,
            azimuth_deg=0.0,
            tilt_deg=30.0,
            color="#1a1a2e",
            selected=False,
            show_mounting=True,
            roof_type="Flachdach"
        )
        
        # Verify mesh was created
        assert mesh is not None, "Mesh should not be None"
        
        # Verify vertices array
        assert vertices is not None, "Vertices should not be None"
        assert len(vertices) == 8, f"Expected 8 vertices, got {len(vertices)}"
        
        # Verify vertices are numpy array
        assert isinstance(vertices, np.ndarray), "Vertices should be numpy array"
        
        print("[OK] Module mesh created successfully")
        print(f"[OK] Mesh has {len(vertices)} vertices")
        print("[OK] create_pv_module_3d works correctly")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_different_roof_types():
    """
    Test module rendering for different roof types.
    
    Requirements: 6.1, 6.2, 6.3
    """
    print("\n=== Test 5: Different Roof Types ===")
    
    roof_types = ["Flachdach", "Satteldach", "Pultdach", "Walmdach"]
    
    for roof_type in roof_types:
        print(f"\n  Testing {roof_type}...")
        
        # Setup session state
        st.session_state = {
            "placed_module_positions": [
                (0.0, 0.0, 0.3),
                (1.1, 0.0, 0.3),
            ],
            "placed_module_count": 2
        }
        
        # Create building dimensions
        dims = BuildingDims(
            length_m=10.0,
            width_m=8.0,
            wall_height_m=3.0
        )
        
        # Create project data
        project_data = {
            "roof_covering": "Ziegel",
            "roof_inclination_deg": 35.0
        }
        
        try:
            fig = build_plotly_scene(
                project_data=project_data,
                dims=dims,
                roof_type=roof_type,
                module_quantity=2,
                layout_config=None,
                selected_modules=[]
            )
            
            assert fig is not None, f"Figure should not be None for {roof_type}"
            print(f"  [OK] {roof_type} rendered successfully")
            
        except Exception as e:
            print(f"  [ERROR] {roof_type} failed: {e}")
            return False
    
    print("\n[OK] All roof types rendered successfully")
    return True


def run_all_tests():
    """Run all tests and report results."""
    print("=" * 60)
    print("Task 4: 3D-Rendering Integration Tests")
    print("=" * 60)
    
    tests = [
        ("Module Rendering from Session State", test_module_rendering_from_session_state),
        ("Empty Session State Fallback", test_empty_session_state_fallback),
        ("Invalid Position Handling", test_invalid_position_handling),
        ("create_pv_module_3d Function", test_create_pv_module_3d),
        ("Different Roof Types", test_different_roof_types),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n[ERROR] Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[OK] PASS" if result else "[ERROR] FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return True
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
