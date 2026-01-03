"""
Unit Tests for calculate_z_position() Function

Phase 1 - Task 2.1: Erstelle Unit Tests für calculate_z_position()

This test suite validates the critical bugfix for module placement on pitched roofs.
It tests all 5 roof types with various parameters and edge cases.

Requirements Tested:
    - 1.1: Module auf Satteldach direkt auf geneigte Dachflächen platzieren
    - 1.2: Module auf Walmdach parallel zur Dachfläche ausrichten
    - 1.3: Module auf Pultdach mit Dachneigung ausrichten
    - 1.4: Module auf Flachdach mit Aufständerung platzieren
    - 1.5: Z-Position basierend auf Dachgeometrie und Y-Position berechnen
    - 1.6: Korrekte Neigung entsprechend Dachtyp anwenden
"""

import pytest
import math
from utils.pv3d_placement_handler import calculate_z_position


class TestFlachdach:
    """Test Flachdach (Flat Roof) - Constant Z-position"""
    
    def test_flachdach_constant_height(self):
        """Requirement 1.4: Flachdach should have constant Z-position (0.30m)"""
        roof_width = 10.0
        y_positions = [-5.0, -2.5, 0.0, 2.5, 5.0]
        
        z_values = [
            calculate_z_position("Flachdach", 0.0, roof_width, y)
            for y in y_positions
        ]
        
        # All Z values should be identical (0.30m for Aufständerung)
        assert all(z == 0.30 for z in z_values), \
            f"Flachdach should have constant Z=0.30m, got {z_values}"
    
    def test_flachdach_case_insensitive(self):
        """Test that roof type matching is case-insensitive"""
        roof_types = ["Flachdach", "flachdach", "FLACHDACH", "FlAcHdAcH"]
        
        for roof_type in roof_types:
            z = calculate_z_position(roof_type, 0.0, 10.0, 0.0)
            assert z == 0.30, \
                f"Roof type '{roof_type}' should return 0.30m, got {z:.3f}m"
    
    def test_flachdach_ignores_pitch(self):
        """Flachdach should ignore roof_pitch parameter"""
        roof_pitches = [0.0, 15.0, 30.0, 45.0]
        
        for pitch in roof_pitches:
            z = calculate_z_position("Flachdach", pitch, 10.0, 0.0)
            assert z == 0.30, \
                f"Flachdach with pitch={pitch}° should still return 0.30m, got {z:.3f}m"


class TestSatteldach:
    """Test Satteldach (Gable Roof) - Z increases from eave to ridge"""
    
    def test_satteldach_z_increases_with_y(self):
        """Requirement 1.1: Z should increase from eave to ridge"""
        roof_width = 10.0
        roof_pitch = 35.0
        y_positions = [-5.0, -2.5, 0.0, 2.5, 5.0]
        
        z_values = [
            calculate_z_position("Satteldach", roof_pitch, roof_width, y)
            for y in y_positions
        ]
        
        # Z should increase monotonically
        for i in range(len(z_values) - 1):
            assert z_values[i] < z_values[i + 1], \
                f"Z should increase: z[{i}]={z_values[i]:.3f} >= z[{i+1}]={z_values[i+1]:.3f}"
    
    def test_satteldach_mathematical_formula(self):
        """Requirement 1.5: Verify mathematical formula z = base_z + (y + roof_width/2) * tan(pitch)"""
        roof_width = 10.0
        roof_pitch = 35.0
        base_z = 0.15
        
        # Test at eave (y = -roof_width/2)
        y_eave = -roof_width / 2
        z_eave = calculate_z_position("Satteldach", roof_pitch, roof_width, y_eave)
        expected_z_eave = base_z  # At eave, offset is 0
        assert abs(z_eave - expected_z_eave) < 0.001, \
            f"At eave: expected {expected_z_eave:.3f}m, got {z_eave:.3f}m"
        
        # Test at ridge (y = roof_width/2)
        y_ridge = roof_width / 2
        z_ridge = calculate_z_position("Satteldach", roof_pitch, roof_width, y_ridge)
        expected_z_ridge = base_z + roof_width * math.tan(math.radians(roof_pitch))
        assert abs(z_ridge - expected_z_ridge) < 0.001, \
            f"At ridge: expected {expected_z_ridge:.3f}m, got {z_ridge:.3f}m"
        
        # Test at center (y = 0)
        y_center = 0.0
        z_center = calculate_z_position("Satteldach", roof_pitch, roof_width, y_center)
        expected_z_center = base_z + (roof_width / 2) * math.tan(math.radians(roof_pitch))
        assert abs(z_center - expected_z_center) < 0.001, \
            f"At center: expected {expected_z_center:.3f}m, got {z_center:.3f}m"
    
    def test_satteldach_zero_pitch(self):
        """Edge case: Zero pitch should return base_z"""
        z = calculate_z_position("Satteldach", 0.0, 10.0, 0.0)
        assert z == 0.15, \
            f"Satteldach with 0° pitch should return base_z=0.15m, got {z:.3f}m"
    
    def test_satteldach_extreme_pitch(self):
        """Edge case: Extreme pitch angles"""
        roof_width = 10.0
        
        # Very steep roof (60°)
        z_steep = calculate_z_position("Satteldach", 60.0, roof_width, roof_width / 2)
        expected_steep = 0.15 + roof_width * math.tan(math.radians(60.0))
        assert abs(z_steep - expected_steep) < 0.001, \
            f"Steep roof (60°): expected {expected_steep:.3f}m, got {z_steep:.3f}m"
        
        # Very shallow roof (5°)
        z_shallow = calculate_z_position("Satteldach", 5.0, roof_width, roof_width / 2)
        expected_shallow = 0.15 + roof_width * math.tan(math.radians(5.0))
        assert abs(z_shallow - expected_shallow) < 0.001, \
            f"Shallow roof (5°): expected {expected_shallow:.3f}m, got {z_shallow:.3f}m"


class TestPultdach:
    """Test Pultdach (Shed Roof) - Z increases linearly"""
    
    def test_pultdach_z_increases_linearly(self):
        """Requirement 1.3: Z should increase linearly from front to back"""
        roof_width = 10.0
        roof_pitch = 25.0
        y_positions = [-5.0, -2.5, 0.0, 2.5, 5.0]
        
        z_values = [
            calculate_z_position("Pultdach", roof_pitch, roof_width, y)
            for y in y_positions
        ]
        
        # Z should increase monotonically
        for i in range(len(z_values) - 1):
            assert z_values[i] < z_values[i + 1], \
                f"Z should increase: z[{i}]={z_values[i]:.3f} >= z[{i+1}]={z_values[i+1]:.3f}"
        
        # Check linearity: differences should be equal
        differences = [z_values[i + 1] - z_values[i] for i in range(len(z_values) - 1)]
        avg_diff = sum(differences) / len(differences)
        for diff in differences:
            assert abs(diff - avg_diff) < 0.001, \
                f"Differences should be equal (linear): {differences}"
    
    def test_pultdach_same_formula_as_satteldach(self):
        """Pultdach uses same formula as Satteldach"""
        roof_width = 10.0
        roof_pitch = 25.0
        y_position = 2.5
        
        z_pultdach = calculate_z_position("Pultdach", roof_pitch, roof_width, y_position)
        z_satteldach = calculate_z_position("Satteldach", roof_pitch, roof_width, y_position)
        
        assert z_pultdach == z_satteldach, \
            f"Pultdach and Satteldach should use same formula: {z_pultdach:.3f} != {z_satteldach:.3f}"


class TestWalmdach:
    """Test Walmdach (Hip Roof) - Similar to Satteldach"""
    
    def test_walmdach_z_increases_with_y(self):
        """Requirement 1.2: Z should increase from eave to ridge"""
        roof_width = 10.0
        roof_pitch = 30.0
        y_positions = [-5.0, -2.5, 0.0, 2.5, 5.0]
        
        z_values = [
            calculate_z_position("Walmdach", roof_pitch, roof_width, y)
            for y in y_positions
        ]
        
        # Z should increase monotonically
        for i in range(len(z_values) - 1):
            assert z_values[i] < z_values[i + 1], \
                f"Z should increase: z[{i}]={z_values[i]:.3f} >= z[{i+1}]={z_values[i+1]:.3f}"
    
    def test_krueppelwalmdach(self):
        """Test Krüppelwalmdach variant"""
        roof_width = 10.0
        roof_pitch = 30.0
        y_position = 2.5
        
        z_walmdach = calculate_z_position("Walmdach", roof_pitch, roof_width, y_position)
        z_krueppel = calculate_z_position("Krüppelwalmdach", roof_pitch, roof_width, y_position)
        
        assert z_walmdach == z_krueppel, \
            f"Walmdach and Krüppelwalmdach should use same formula: {z_walmdach:.3f} != {z_krueppel:.3f}"


class TestZeltdach:
    """Test Zeltdach (Pyramid Roof) - Z increases pyramidally"""
    
    def test_zeltdach_highest_at_center(self):
        """Requirement 1.5: Z should be highest at center (pyramidal)"""
        roof_width = 10.0
        roof_pitch = 30.0
        
        # Test positions from edge to center
        y_positions = [-5.0, -2.5, 0.0, 2.5, 5.0]
        z_values = [
            calculate_z_position("Zeltdach", roof_pitch, roof_width, y)
            for y in y_positions
        ]
        
        # Center should have highest Z
        center_index = len(y_positions) // 2
        z_center = z_values[center_index]
        
        # Z at edges should be lower than center
        assert z_values[0] < z_center, \
            f"Edge Z ({z_values[0]:.3f}m) should be < center Z ({z_center:.3f}m)"
        assert z_values[-1] < z_center, \
            f"Edge Z ({z_values[-1]:.3f}m) should be < center Z ({z_center:.3f}m)"
    
    def test_zeltdach_symmetry(self):
        """Zeltdach should be symmetric around center"""
        roof_width = 10.0
        roof_pitch = 30.0
        
        # Test symmetric positions
        y_positions = [-4.0, -2.0, 0.0, 2.0, 4.0]
        z_values = [
            calculate_z_position("Zeltdach", roof_pitch, roof_width, y)
            for y in y_positions
        ]
        
        # Check symmetry: z[-i] should equal z[i]
        for i in range(len(y_positions) // 2):
            assert abs(z_values[i] - z_values[-(i + 1)]) < 0.001, \
                f"Zeltdach should be symmetric: z[{i}]={z_values[i]:.3f} != z[{-(i+1)}]={z_values[-(i+1)]:.3f}"


class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_negative_y_positions(self):
        """Test with negative Y positions (front of roof)"""
        roof_width = 10.0
        roof_pitch = 35.0
        
        z = calculate_z_position("Satteldach", roof_pitch, roof_width, -5.0)
        assert z >= 0.15, \
            f"Z should be >= base_z (0.15m), got {z:.3f}m"
    
    def test_extreme_y_positions(self):
        """Test with Y positions at roof boundaries"""
        roof_width = 10.0
        roof_pitch = 35.0
        
        # At front edge
        z_front = calculate_z_position("Satteldach", roof_pitch, roof_width, -roof_width / 2)
        assert z_front == 0.15, \
            f"At front edge, Z should be base_z (0.15m), got {z_front:.3f}m"
        
        # At back edge
        z_back = calculate_z_position("Satteldach", roof_pitch, roof_width, roof_width / 2)
        expected_back = 0.15 + roof_width * math.tan(math.radians(roof_pitch))
        assert abs(z_back - expected_back) < 0.001, \
            f"At back edge, expected {expected_back:.3f}m, got {z_back:.3f}m"
    
    def test_very_small_roof(self):
        """Test with very small roof dimensions"""
        roof_width = 1.0  # 1 meter
        roof_pitch = 35.0
        
        z = calculate_z_position("Satteldach", roof_pitch, roof_width, 0.0)
        assert z > 0.15, \
            f"Even small roofs should have Z > base_z, got {z:.3f}m"
    
    def test_very_large_roof(self):
        """Test with very large roof dimensions"""
        roof_width = 100.0  # 100 meters
        roof_pitch = 35.0
        
        z = calculate_z_position("Satteldach", roof_pitch, roof_width, roof_width / 2)
        expected = 0.15 + roof_width * math.tan(math.radians(roof_pitch))
        assert abs(z - expected) < 0.01, \
            f"Large roof: expected {expected:.3f}m, got {z:.3f}m"
    
    def test_unknown_roof_type(self):
        """Test with unknown roof type (should use fallback)"""
        z = calculate_z_position("UnknownRoofType", 35.0, 10.0, 0.0)
        assert z == 0.15, \
            f"Unknown roof type should return base_z (0.15m), got {z:.3f}m"
    
    def test_empty_roof_type(self):
        """Test with empty roof type string"""
        z = calculate_z_position("", 0.0, 10.0, 0.0)
        # Empty string should default to Flachdach
        assert z == 0.30, \
            f"Empty roof type should default to Flachdach (0.30m), got {z:.3f}m"
    
    def test_whitespace_in_roof_type(self):
        """Test that whitespace is handled correctly"""
        roof_types = [
            "  Satteldach  ",
            "Satteldach ",
            " Satteldach",
            "\tSatteldach\n"
        ]
        
        for roof_type in roof_types:
            z = calculate_z_position(roof_type, 35.0, 10.0, 0.0)
            expected = 0.15 + 5.0 * math.tan(math.radians(35.0))
            assert abs(z - expected) < 0.001, \
                f"Roof type '{repr(roof_type)}' should be normalized, got {z:.3f}m"


class TestRoofTypeVariants:
    """Test different roof type name variants"""
    
    def test_satteldach_variants(self):
        """Test Satteldach with different naming variants"""
        variants = [
            "Satteldach",
            "Satteldach mit Gaube",
            "satteldach",
            "SATTELDACH"
        ]
        
        roof_width = 10.0
        roof_pitch = 35.0
        y_position = 2.5
        
        z_values = [
            calculate_z_position(variant, roof_pitch, roof_width, y_position)
            for variant in variants
        ]
        
        # All variants should produce same result
        for i in range(len(z_values) - 1):
            assert abs(z_values[i] - z_values[i + 1]) < 0.001, \
                f"Variants should produce same Z: {z_values}"


class TestRequirementCoverage:
    """Test that all requirements are satisfied"""
    
    def test_requirement_1_1_satteldach_on_surface(self):
        """Requirement 1.1: Module auf Satteldach direkt auf geneigte Dachflächen platzieren"""
        roof_width = 10.0
        roof_pitch = 35.0
        
        # Modules at different Y positions should have different Z
        z_front = calculate_z_position("Satteldach", roof_pitch, roof_width, -4.0)
        z_back = calculate_z_position("Satteldach", roof_pitch, roof_width, 4.0)
        
        assert z_back > z_front, \
            "Modules should follow roof surface (Z increases with Y)"
    
    def test_requirement_1_2_walmdach_parallel(self):
        """Requirement 1.2: Module auf Walmdach parallel zur Dachfläche ausrichten"""
        roof_width = 10.0
        roof_pitch = 30.0
        
        # Z should vary with Y position
        z_values = [
            calculate_z_position("Walmdach", roof_pitch, roof_width, y)
            for y in [-4.0, 0.0, 4.0]
        ]
        
        assert z_values[0] < z_values[1] < z_values[2], \
            "Walmdach modules should follow roof surface"
    
    def test_requirement_1_3_pultdach_with_slope(self):
        """Requirement 1.3: Module auf Pultdach mit Dachneigung ausrichten"""
        roof_width = 10.0
        roof_pitch = 25.0
        
        # Z should increase linearly
        y_positions = [-4.0, -2.0, 0.0, 2.0, 4.0]
        z_values = [
            calculate_z_position("Pultdach", roof_pitch, roof_width, y)
            for y in y_positions
        ]
        
        # Check linear increase
        differences = [z_values[i + 1] - z_values[i] for i in range(len(z_values) - 1)]
        avg_diff = sum(differences) / len(differences)
        for diff in differences:
            assert abs(diff - avg_diff) < 0.001, \
                "Pultdach should have linear slope"
    
    def test_requirement_1_4_flachdach_with_aufstaenderung(self):
        """Requirement 1.4: Module auf Flachdach mit Aufständerung platzieren"""
        # All modules should be at 0.30m (Aufständerung height)
        z_values = [
            calculate_z_position("Flachdach", 0.0, 10.0, y)
            for y in [-5.0, 0.0, 5.0]
        ]
        
        assert all(z == 0.30 for z in z_values), \
            "Flachdach should have constant Aufständerung height (0.30m)"
    
    def test_requirement_1_5_z_based_on_geometry_and_y(self):
        """Requirement 1.5: Z-Position basierend auf Dachgeometrie und Y-Position berechnen"""
        roof_width = 10.0
        roof_pitch = 35.0
        
        # Different Y positions should produce different Z values
        y_positions = [-5.0, -2.5, 0.0, 2.5, 5.0]
        z_values = [
            calculate_z_position("Satteldach", roof_pitch, roof_width, y)
            for y in y_positions
        ]
        
        # All Z values should be different (except for Flachdach)
        assert len(set(z_values)) == len(z_values), \
            "Each Y position should produce unique Z value"
    
    def test_requirement_1_6_correct_tilt_per_roof_type(self):
        """Requirement 1.6: Korrekte Neigung entsprechend Dachtyp anwenden"""
        roof_width = 10.0
        roof_pitch = 35.0
        
        # Each roof type should use appropriate calculation
        roof_types = ["Flachdach", "Satteldach", "Pultdach", "Walmdach", "Zeltdach"]
        
        for roof_type in roof_types:
            z = calculate_z_position(roof_type, roof_pitch, roof_width, 0.0)
            assert z >= 0.15, \
                f"{roof_type} should have Z >= base_z (0.15m), got {z:.3f}m"


# Run tests with pytest
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
