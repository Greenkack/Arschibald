"""
Test Task 8: Dachtyp-spezifische Logik

This test verifies that the roof-type-specific logic is correctly implemented
for Z-position calculation and tilt angle calculation.

Requirements tested:
    - 6.1: Flat roof with 0.3m elevation and 30° tilt
    - 6.2: Gable roof with 0.05m clearance and roof pitch tilt
    - 6.3: Shed roof with 0.05m clearance and roof pitch tilt
    - 6.4: Z-position calculation based on roof type
    - 6.5: Tilt angle calculation based on roof type
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.pv3d_placement_handler import (
    calculate_z_position,
    calculate_tilt_angle
)


def test_z_position_flat_roof():
    """Test Requirement 6.1: Flat roof Z-position (0.3m Aufständerung)"""
    print("Test 1: Z-position for Flachdach")
    
    z_pos = calculate_z_position("Flachdach", 0.0)
    
    assert z_pos == 0.3, f"Expected 0.3m, got {z_pos}m"
    print(f"  ✓ Flachdach Z-position: {z_pos}m (0.3m Aufständerung)")
    
    # Test case-insensitive
    z_pos_upper = calculate_z_position("FLACHDACH", 0.0)
    assert z_pos_upper == 0.3, f"Expected 0.3m, got {z_pos_upper}m"
    print(f"  ✓ Case-insensitive: {z_pos_upper}m")
    
    # Test with whitespace
    z_pos_space = calculate_z_position(" Flachdach ", 0.0)
    assert z_pos_space == 0.3, f"Expected 0.3m, got {z_pos_space}m"
    print(f"  ✓ With whitespace: {z_pos_space}m")
    
    print()


def test_z_position_gable_roof():
    """Test Requirement 6.2: Gable roof Z-position (0.05m direkt auf Dach)"""
    print("Test 2: Z-position for Satteldach")
    
    z_pos = calculate_z_position("Satteldach", 35.0)
    
    assert z_pos == 0.05, f"Expected 0.05m, got {z_pos}m"
    print(f"  ✓ Satteldach Z-position: {z_pos}m (direkt auf Dach)")
    
    # Test with different pitches (should not affect Z-position)
    z_pos_25 = calculate_z_position("Satteldach", 25.0)
    assert z_pos_25 == 0.05, f"Expected 0.05m, got {z_pos_25}m"
    print(f"  ✓ With 25° pitch: {z_pos_25}m")
    
    z_pos_45 = calculate_z_position("Satteldach", 45.0)
    assert z_pos_45 == 0.05, f"Expected 0.05m, got {z_pos_45}m"
    print(f"  ✓ With 45° pitch: {z_pos_45}m")
    
    print()


def test_z_position_shed_roof():
    """Test Requirement 6.3: Shed roof Z-position (0.05m direkt auf Dach)"""
    print("Test 3: Z-position for Pultdach")
    
    z_pos = calculate_z_position("Pultdach", 25.0)
    
    assert z_pos == 0.05, f"Expected 0.05m, got {z_pos}m"
    print(f"  ✓ Pultdach Z-position: {z_pos}m (direkt auf Dach)")
    
    print()


def test_z_position_other_roofs():
    """Test Requirement 6.4: Z-position for other roof types"""
    print("Test 4: Z-position for other roof types")
    
    roof_types = ["Walmdach", "Krüppelwalmdach", "Zeltdach", "Mansarddach"]
    
    for roof_type in roof_types:
        z_pos = calculate_z_position(roof_type, 35.0)
        assert z_pos == 0.05, f"Expected 0.05m for {roof_type}, got {z_pos}m"
        print(f"  ✓ {roof_type}: {z_pos}m")
    
    print()


def test_tilt_angle_flat_roof():
    """Test Requirement 6.1: Flat roof tilt angle (30°)"""
    print("Test 5: Tilt angle for Flachdach")
    
    tilt = calculate_tilt_angle("Flachdach", 0.0)
    
    assert tilt == 30.0, f"Expected 30.0°, got {tilt}°"
    print(f"  ✓ Flachdach tilt angle: {tilt}° (Aufständerung)")
    
    # Test that roof pitch is ignored for flat roofs
    tilt_with_pitch = calculate_tilt_angle("Flachdach", 15.0)
    assert tilt_with_pitch == 30.0, f"Expected 30.0°, got {tilt_with_pitch}°"
    print(f"  ✓ Ignores roof pitch parameter: {tilt_with_pitch}°")
    
    print()


def test_tilt_angle_pitched_roofs():
    """Test Requirement 6.5: Pitched roofs use roof pitch angle"""
    print("Test 6: Tilt angle for pitched roofs")
    
    test_cases = [
        ("Satteldach", 35.0, 35.0),
        ("Pultdach", 25.0, 25.0),
        ("Walmdach", 40.0, 40.0),
        ("Krüppelwalmdach", 30.0, 30.0),
        ("Zeltdach", 45.0, 45.0),
    ]
    
    for roof_type, pitch, expected_tilt in test_cases:
        tilt = calculate_tilt_angle(roof_type, pitch)
        assert tilt == expected_tilt, (
            f"Expected {expected_tilt}° for {roof_type}, got {tilt}°"
        )
        print(f"  ✓ {roof_type} (pitch={pitch}°): tilt={tilt}°")
    
    print()


def test_tilt_angle_zero_pitch():
    """Test edge case: Pitched roof with 0° pitch"""
    print("Test 7: Tilt angle for pitched roof with 0° pitch")
    
    tilt = calculate_tilt_angle("Satteldach", 0.0)
    
    assert tilt == 0.0, f"Expected 0.0°, got {tilt}°"
    print(f"  ✓ Satteldach with 0° pitch: {tilt}°")
    
    print()


def test_combined_logic():
    """Test combined Z-position and tilt angle logic"""
    print("Test 8: Combined Z-position and tilt angle")
    
    test_cases = [
        ("Flachdach", 0.0, 0.3, 30.0),
        ("Satteldach", 35.0, 0.05, 35.0),
        ("Pultdach", 25.0, 0.05, 25.0),
        ("Walmdach", 40.0, 0.05, 40.0),
    ]
    
    for roof_type, pitch, expected_z, expected_tilt in test_cases:
        z_pos = calculate_z_position(roof_type, pitch)
        tilt = calculate_tilt_angle(roof_type, pitch)
        
        assert z_pos == expected_z, (
            f"Expected Z={expected_z}m for {roof_type}, got {z_pos}m"
        )
        assert tilt == expected_tilt, (
            f"Expected tilt={expected_tilt}° for {roof_type}, got {tilt}°"
        )
        
        print(f"  ✓ {roof_type} (pitch={pitch}°):")
        print(f"    Z-position: {z_pos}m, Tilt: {tilt}°")
    
    print()


def test_requirements_coverage():
    """Verify all requirements are covered"""
    print("Test 9: Requirements coverage")
    
    # Requirement 6.1: Flat roof with 0.3m elevation and 30° tilt
    z_flat = calculate_z_position("Flachdach", 0.0)
    tilt_flat = calculate_tilt_angle("Flachdach", 0.0)
    assert z_flat == 0.3 and tilt_flat == 30.0
    print("  ✓ Requirement 6.1: Flat roof (0.3m, 30°)")
    
    # Requirement 6.2: Gable roof with 0.05m clearance
    z_gable = calculate_z_position("Satteldach", 35.0)
    assert z_gable == 0.05
    print("  ✓ Requirement 6.2: Gable roof (0.05m)")
    
    # Requirement 6.3: Shed roof with 0.05m clearance
    z_shed = calculate_z_position("Pultdach", 25.0)
    assert z_shed == 0.05
    print("  ✓ Requirement 6.3: Shed roof (0.05m)")
    
    # Requirement 6.4: Z-position based on roof type
    z_types = [
        calculate_z_position("Flachdach", 0.0),
        calculate_z_position("Satteldach", 35.0),
        calculate_z_position("Walmdach", 40.0)
    ]
    assert len(set(z_types)) == 2  # Should have 2 different values
    print("  ✓ Requirement 6.4: Z-position varies by roof type")
    
    # Requirement 6.5: Tilt angle based on roof type and pitch
    tilt_flat = calculate_tilt_angle("Flachdach", 0.0)
    tilt_pitched = calculate_tilt_angle("Satteldach", 35.0)
    assert tilt_flat == 30.0 and tilt_pitched == 35.0
    print("  ✓ Requirement 6.5: Tilt angle varies by roof type")
    
    print()


def run_all_tests():
    """Run all tests"""
    print("=" * 70)
    print("TASK 8: Dachtyp-spezifische Logik - Test Suite")
    print("=" * 70)
    print()
    
    try:
        test_z_position_flat_roof()
        test_z_position_gable_roof()
        test_z_position_shed_roof()
        test_z_position_other_roofs()
        test_tilt_angle_flat_roof()
        test_tilt_angle_pitched_roofs()
        test_tilt_angle_zero_pitch()
        test_combined_logic()
        test_requirements_coverage()
        
        print("=" * 70)
        print("✓ ALL TESTS PASSED!")
        print("=" * 70)
        print()
        print("Summary:")
        print("  - Z-position calculation: ✓ Working")
        print("  - Tilt angle calculation: ✓ Working")
        print("  - Flat roof logic (0.3m, 30°): ✓ Correct")
        print("  - Pitched roof logic (0.05m, roof pitch): ✓ Correct")
        print("  - All requirements (6.1-6.5): ✓ Covered")
        print()
        
        return True
        
    except AssertionError as e:
        print()
        print("=" * 70)
        print("❌ TEST FAILED!")
        print("=" * 70)
        print(f"Error: {e}")
        print()
        return False
    
    except Exception as e:
        print()
        print("=" * 70)
        print("❌ UNEXPECTED ERROR!")
        print("=" * 70)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        print()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
