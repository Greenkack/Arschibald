"""
Verification Script for Task 8: Dachtyp-spezifische Logik

This script demonstrates the roof-type-specific logic implementation
and verifies that all requirements are met.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.pv3d_placement_handler import (
    calculate_z_position,
    calculate_tilt_angle
)


def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{title}")
    print("-" * 70)


def verify_flat_roof():
    """Verify flat roof logic (Requirement 6.1)"""
    print_section("Requirement 6.1: Flachdach (Flat Roof)")
    
    roof_type = "Flachdach"
    roof_pitch = 0.0
    
    z_pos = calculate_z_position(roof_type, roof_pitch)
    tilt = calculate_tilt_angle(roof_type, roof_pitch)
    
    print(f"  Roof Type: {roof_type}")
    print(f"  Roof Pitch: {roof_pitch}°")
    print(f"  → Z-Position: {z_pos}m (Expected: 0.3m)")
    print(f"  → Tilt Angle: {tilt}° (Expected: 30°)")
    
    assert z_pos == 0.3, "Flat roof Z-position should be 0.3m"
    assert tilt == 30.0, "Flat roof tilt should be 30°"
    
    print("  PASSED: Flat roof with 0.3m elevation and 30° tilt")


def verify_gable_roof():
    """Verify gable roof logic (Requirement 6.2)"""
    print_section("Requirement 6.2: Satteldach (Gable Roof)")
    
    roof_type = "Satteldach"
    roof_pitch = 35.0
    
    z_pos = calculate_z_position(roof_type, roof_pitch)
    tilt = calculate_tilt_angle(roof_type, roof_pitch)
    
    print(f"  Roof Type: {roof_type}")
    print(f"  Roof Pitch: {roof_pitch}°")
    print(f"  → Z-Position: {z_pos}m (Expected: 0.05m)")
    print(f"  → Tilt Angle: {tilt}° (Expected: {roof_pitch}°)")
    
    assert z_pos == 0.05, "Gable roof Z-position should be 0.05m"
    assert tilt == roof_pitch, "Gable roof tilt should match roof pitch"
    
    print("  PASSED: Gable roof with 0.05m clearance and roof pitch tilt")


def verify_shed_roof():
    """Verify shed roof logic (Requirement 6.3)"""
    print_section("Requirement 6.3: Pultdach (Shed Roof)")
    
    roof_type = "Pultdach"
    roof_pitch = 25.0
    
    z_pos = calculate_z_position(roof_type, roof_pitch)
    tilt = calculate_tilt_angle(roof_type, roof_pitch)
    
    print(f"  Roof Type: {roof_type}")
    print(f"  Roof Pitch: {roof_pitch}°")
    print(f"  → Z-Position: {z_pos}m (Expected: 0.05m)")
    print(f"  → Tilt Angle: {tilt}° (Expected: {roof_pitch}°)")
    
    assert z_pos == 0.05, "Shed roof Z-position should be 0.05m"
    assert tilt == roof_pitch, "Shed roof tilt should match roof pitch"
    
    print("  PASSED: Shed roof with 0.05m clearance and roof pitch tilt")


def verify_z_position_calculation():
    """Verify Z-position calculation (Requirement 6.4)"""
    print_section("Requirement 6.4: Z-Position Based on Roof Type")
    
    roof_types = [
        ("Flachdach", 0.0, 0.3),
        ("Satteldach", 35.0, 0.05),
        ("Pultdach", 25.0, 0.05),
        ("Walmdach", 40.0, 0.05),
        ("Krüppelwalmdach", 30.0, 0.05),
        ("Zeltdach", 45.0, 0.05),
    ]
    
    for roof_type, pitch, expected_z in roof_types:
        z_pos = calculate_z_position(roof_type, pitch)
        status = "" if z_pos == expected_z else ""
        print(f"  {status} {roof_type:20s} → Z={z_pos}m (Expected: {expected_z}m)")
        assert z_pos == expected_z, f"Z-position mismatch for {roof_type}"
    
    print("  PASSED: Z-position varies correctly by roof type")


def verify_tilt_angle_calculation():
    """Verify tilt angle calculation (Requirement 6.5)"""
    print_section("Requirement 6.5: Tilt Angle Based on Roof Type")
    
    roof_types = [
        ("Flachdach", 0.0, 30.0),
        ("Satteldach", 35.0, 35.0),
        ("Pultdach", 25.0, 25.0),
        ("Walmdach", 40.0, 40.0),
        ("Krüppelwalmdach", 30.0, 30.0),
        ("Zeltdach", 45.0, 45.0),
    ]
    
    for roof_type, pitch, expected_tilt in roof_types:
        tilt = calculate_tilt_angle(roof_type, pitch)
        status = "" if tilt == expected_tilt else ""
        print(f"  {status} {roof_type:20s} (pitch={pitch:4.1f}°) → tilt={tilt}°")
        assert tilt == expected_tilt, f"Tilt angle mismatch for {roof_type}"
    
    print("  PASSED: Tilt angle varies correctly by roof type")


def demonstrate_visual_comparison():
    """Demonstrate visual comparison of different roof types"""
    print_section("Visual Comparison of Roof Types")
    
    print("\n  Flachdach (Flat Roof):")
    print("       /‾‾‾‾‾‾‾\\  ← Module (30° tilted)")
    print("      /         \\")
    print("     /__________\\  ← Mounting frame (0.3m high)")
    print("      ← Roof surface")
    
    print("\n  Satteldach (Gable Roof):")
    print("        /‾‾‾‾‾‾‾\\  ← Module (parallel to roof)")
    print("       /         \\")
    print("      /___________\\ ← Roof surface (35° tilted)")
    print("     /             \\")
    print("    /_______________\\")
    
    print("\n  Pultdach (Shed Roof):")
    print("          /‾‾‾‾‾‾‾\\  ← Module (parallel to roof)")
    print("         /         \\")
    print("        /___________\\ ← Roof surface (25° tilted)")
    print("       /")
    print("      /")
    print("     /")


def main():
    """Run all verification tests"""
    print_header("Task 8: Dachtyp-spezifische Logik - Verification")
    
    try:
        verify_flat_roof()
        verify_gable_roof()
        verify_shed_roof()
        verify_z_position_calculation()
        verify_tilt_angle_calculation()
        demonstrate_visual_comparison()
        
        print_header("ALL VERIFICATIONS PASSED!")
        
        print("\nSummary:")
        print("  Requirement 6.1: Flat roof logic (0.3m, 30°)")
        print("  Requirement 6.2: Gable roof logic (0.05m, roof pitch)")
        print("  Requirement 6.3: Shed roof logic (0.05m, roof pitch)")
        print("  Requirement 6.4: Z-position calculation")
        print("  Requirement 6.5: Tilt angle calculation")
        print("\n  Task 8 is fully implemented and verified!")
        print()
        
        return True
        
    except AssertionError as e:
        print_header("VERIFICATION FAILED!")
        print(f"\nError: {e}\n")
        return False
    
    except Exception as e:
        print_header("UNEXPECTED ERROR!")
        print(f"\nError: {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
