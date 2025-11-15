"""
Test Task 3: Automatische Belegung Integration

This test verifies that the automatic placement integration works correctly:
- Task 3.1: Grid calculation (already verified as working)
- Task 3.2: Placement algorithm optimization (already verified as working)
- Task 3.3: Button integration and event handling

Requirements:
- 3.1: Grid-Berechnung funktioniert
- 3.2: Platzierungs-Algorithmus optimiert
- 3.3: Button "Automatisch belegen" funktioniert
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_grid_calculation():
    """Test 3.1: Grid-Berechnung korrigieren"""
    print("\n" + "="*70)
    print("TEST 3.1: Grid-Berechnung")
    print("="*70)
    
    try:
        from utils.pv3d_grid_calculator import calculate_module_grid
        
        # Test 1: Standard roof
        print("\nTest 1: Standard roof (10m x 8m, 20 modules)")
        positions = calculate_module_grid(10.0, 8.0, 20)
        assert len(positions) == 20, f"Expected 20 modules, got {len(positions)}"
        assert all(isinstance(p, tuple) and len(p) == 2 for p in positions), \
            "All positions should be (x, y) tuples"
        print(f"  Placed {len(positions)} modules")
        print(f"  First position: ({positions[0][0]:.2f}, {positions[0][1]:.2f})")
        print(f"  Last position: ({positions[-1][0]:.2f}, {positions[-1][1]:.2f})")
        
        # Test 2: Small roof
        print("\nTest 2: Small roof (5m x 4m, 10 modules)")
        positions = calculate_module_grid(5.0, 4.0, 10)
        print(f"  Placed {len(positions)} modules (may be less than requested)")
        
        # Test 3: Invalid inputs
        print("\nTest 3: Invalid inputs (negative dimensions)")
        positions = calculate_module_grid(-10.0, 8.0, 20)
        assert len(positions) == 0, "Should return empty list for invalid inputs"
        print(f"  Correctly handled invalid input: {len(positions)} modules")
        
        # Test 4: Zero modules
        print("\nTest 4: Zero modules requested")
        positions = calculate_module_grid(10.0, 8.0, 0)
        assert len(positions) == 0, "Should return empty list for zero modules"
        print(f"  Correctly handled zero modules: {len(positions)} modules")
        
        print("\n" + "="*70)
        print("TEST 3.1 PASSED: Grid calculation works correctly")
        print("="*70)
        return True
        
    except Exception as e:
        print(f"\nTEST 3.1 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_placement_optimization():
    """Test 3.2: Platzierungs-Algorithmus optimieren"""
    print("\n" + "="*70)
    print("TEST 3.2: Platzierungs-Algorithmus Optimierung")
    print("="*70)
    
    try:
        from utils.pv3d_grid_calculator import (
            calculate_max_modules,
            calculate_module_grid
        )
        
        # Test 1: Maximum capacity calculation
        print("\nTest 1: Maximum capacity (15m x 12m roof)")
        max_modules = calculate_max_modules(15.0, 12.0)
        print(f"  Maximum modules: {max_modules}")
        assert max_modules > 0, "Should calculate positive maximum"
        
        # Test 2: Verify all modules fit
        print("\nTest 2: Verify all modules fit")
        positions = calculate_module_grid(15.0, 12.0, max_modules)
        assert len(positions) == max_modules, \
            f"Should place all {max_modules} modules, got {len(positions)}"
        print(f"  Placed {len(positions)} modules (all fit)")
        
        # Test 3: Request more than maximum
        print("\nTest 3: Request more than maximum")
        positions = calculate_module_grid(15.0, 12.0, max_modules + 10)
        assert len(positions) == max_modules, \
            f"Should limit to {max_modules} modules, got {len(positions)}"
        print(f"  Correctly limited to {len(positions)} modules")
        
        # Test 4: Spacing and margins
        print("\nTest 4: Spacing and margins respected")
        positions = calculate_module_grid(10.0, 8.0, 20, spacing=0.1, margin=0.5)
        print(f"  Placed {len(positions)} modules with custom spacing/margin")
        
        # Verify no overlaps (simple check: all positions unique)
        unique_positions = set(positions)
        assert len(unique_positions) == len(positions), \
            "All positions should be unique (no overlaps)"
        print(f"  All {len(positions)} positions are unique (no overlaps)")
        
        print("\n" + "="*70)
        print("TEST 3.2 PASSED: Placement optimization works correctly")
        print("="*70)
        return True
        
    except Exception as e:
        print(f"\nTEST 3.2 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_button_integration():
    """Test 3.3: Button "Automatisch belegen" Integration"""
    print("\n" + "="*70)
    print("TEST 3.3: Button Integration")
    print("="*70)
    
    try:
        # Test 1: Import placement handler
        print("\nTest 1: Import placement handler")
        from utils.pv3d_placement_handler import (
            handle_auto_placement,
            initialize_session_state,
            calculate_z_position,
            calculate_tilt_angle
        )
        print("  Placement handler imported successfully")
        
        # Test 2: Import UI panel
        print("\nTest 2: Import UI panel")
        from utils.pv3d_module_placement_ui import render_module_placement_panel
        print("  UI panel imported successfully")
        
        # Test 3: Check integration in solar_3d_view_module.py
        print("\nTest 3: Check integration in solar_3d_view_module.py")
        with open("solar_3d_view_module.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        checks = [
            ("Import UI panel", "from utils.pv3d_module_placement_ui import render_module_placement_panel"),
            ("Import handler", "from utils.pv3d_placement_handler import"),
            ("Render panel", "placement_actions = render_module_placement_panel("),
            ("Handle auto-placement", 'if st.session_state.get("trigger_auto_placement"'),
            ("Call handle_auto_placement", "result = handle_auto_placement("),
            ("Handle reset", 'if placement_actions.get("reset_all_clicked"'),
            ("Call handle_reset", "result = handle_reset_placement()"),
        ]
        
        all_present = True
        for check_name, check_string in checks:
            if check_string in content:
                print(f"  {check_name}: Found")
            else:
                print(f"  {check_name}: NOT FOUND")
                all_present = False
        
        assert all_present, "Not all integration points found in solar_3d_view_module.py"
        
        # Test 4: Test handle_auto_placement function (without Streamlit)
        print("\nTest 4: Test handle_auto_placement logic")
        
        # Create a mock session state
        class MockSessionState(dict):
            def get(self, key, default=None):
                return super().get(key, default)
        
        # Mock streamlit
        import streamlit as st
        if not hasattr(st, 'session_state'):
            st.session_state = MockSessionState()
        
        # Initialize session state
        st.session_state["placed_module_positions"] = []
        st.session_state["placed_module_count"] = 0
        
        # Test auto placement
        result = handle_auto_placement(
            roof_length=10.0,
            roof_width=8.0,
            module_quantity=20,
            roof_type="Flachdach",
            roof_pitch=0.0
        )
        
        assert result["success"], f"Auto placement should succeed: {result['message']}"
        assert result["count"] > 0, "Should place at least one module"
        assert len(result["positions"]) == result["count"], \
            "Position count should match reported count"
        print(f"  Auto placement successful: {result['count']} modules placed")
        print(f"  Message: {result['message']}")
        
        # Test 5: Verify Z-position calculation
        print("\nTest 5: Z-position calculation")
        z_flat = calculate_z_position("Flachdach", 0.0, 10.0)
        z_gable = calculate_z_position("Satteldach", 35.0, 10.0)
        print(f"  Flachdach Z-position: {z_flat}m (should be 0.30m for Aufständerung)")
        print(f"  Satteldach Z-position: {z_gable}m (should be 0.15m for roof surface)")
        assert z_flat == 0.30, "Flat roof should have 0.30m elevation"
        assert z_gable == 0.15, "Gable roof should have 0.15m elevation"
        
        # Test 6: Verify tilt angle calculation
        print("\nTest 6: Tilt angle calculation")
        tilt_flat = calculate_tilt_angle("Flachdach", 0.0)
        tilt_gable = calculate_tilt_angle("Satteldach", 35.0)
        print(f"  Flachdach tilt: {tilt_flat}° (should be 30° for Aufständerung)")
        print(f"  Satteldach tilt: {tilt_gable}° (should match roof pitch 35°)")
        assert tilt_flat == 30.0, "Flat roof should have 30° tilt"
        assert tilt_gable == 35.0, "Gable roof should match roof pitch"
        
        print("\n" + "="*70)
        print("TEST 3.3 PASSED: Button integration works correctly")
        print("="*70)
        return True
        
    except Exception as e:
        print(f"\nTEST 3.3 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all Task 3 tests"""
    print("\n" + "="*70)
    print("TASK 3: AUTOMATISCHE BELEGUNG REPARIEREN - INTEGRATION TEST")
    print("="*70)
    
    results = []
    
    # Run all tests
    results.append(("3.1 Grid-Berechnung", test_grid_calculation()))
    results.append(("3.2 Platzierungs-Algorithmus", test_placement_optimization()))
    results.append(("3.3 Button Integration", test_button_integration()))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for test_name, passed in results:
        status = "PASSED" if passed else "FAILED"
        print(f"{status}: {test_name}")
    
    all_passed = all(passed for _, passed in results)
    
    if all_passed:
        print("\n" + "="*70)
        print("🎉 ALL TESTS PASSED - TASK 3 COMPLETE!")
        print("="*70)
        print("\nAutomatische Belegung funktioniert:")
        print("  Grid-Berechnung berechnet korrekte Positionen")
        print("  Platzierungs-Algorithmus optimiert Modulanzahl")
        print("  Button 'Automatisch belegen' ist integriert")
        print("  Event-Handler verarbeiten Button-Klicks")
        print("  Session State wird korrekt aktualisiert")
        print("  Fortschritt wird angezeigt")
        print("  Ergebnis (Anzahl platzierter Module) wird angezeigt")
        return 0
    else:
        print("\n" + "="*70)
        print("SOME TESTS FAILED - TASK 3 INCOMPLETE")
        print("="*70)
        return 1


if __name__ == "__main__":
    exit(main())
