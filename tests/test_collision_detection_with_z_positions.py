"""
Collision Detection Tests with New Z-Positions

Phase 1 - Task 2.3: Kollisions-Tests

This test suite verifies that the collision detection system works correctly
with the new Z-position calculation for pitched roofs. It ensures that:
1. Modules don't fall through roof surfaces
2. Modules don't float above roof surfaces
3. Collision detection works with varying Z-positions

Requirements Tested:
    - 1.5: Z-Position basierend auf Dachgeometrie und Y-Position berechnen
    - 1.6: Korrekte Neigung entsprechend Dachtyp anwenden
    - 7.1: Check for module-to-module overlap
    - 7.2: Check for roof edge violation
    - 7.3: Display warning when collision detected
    - 7.4: Prevent placement when collision detected
"""

import sys
from pathlib import Path
import pytest
from pytest import approx

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.pv3d_placement_handler import (  # noqa: E402
    calculate_z_position,
    check_module_collision,
    PV_W,
    PV_H,
    DEFAULT_MARGIN
)


class TestModuleOnRoofSurface:
    """Test that modules are correctly positioned ON the roof surface"""
    
    def test_flachdach_modules_above_surface(self):
        """Flachdach: All modules should be at 0.30m (not 0.0m)"""
        roof_width = 10.0
        y_positions = [-4.0, -2.0, 0.0, 2.0, 4.0]
        
        for y in y_positions:
            z = calculate_z_position("Flachdach", 0.0, roof_width, y)
            assert z == approx(0.30), \
                f"Flachdach module at y={y} should be at 0.30m (Aufständerung), got {z:.3f}m"
            assert z > 0.0, \
                f"Module should be ABOVE roof surface (z > 0), got {z:.3f}m"
    
    def test_satteldach_modules_above_base(self):
        """Satteldach: All modules should be above base_z (0.15m)"""
        roof_width = 10.0
        roof_pitch = 35.0
        y_positions = [-5.0, -2.5, 0.0, 2.5, 5.0]
        
        for y in y_positions:
            z = calculate_z_position("Satteldach", roof_pitch, roof_width, y)
            assert z >= 0.15, \
                f"Satteldach module at y={y} should be >= base_z (0.15m), got {z:.3f}m"
    
    def test_modules_dont_sink_below_roof(self):
        """No module should have negative Z-position"""
        roof_types = ["Flachdach", "Satteldach", "Pultdach", "Walmdach", "Zeltdach"]
        roof_width = 10.0
        roof_pitch = 35.0
        
        for roof_type in roof_types:
            for y in [-5.0, 0.0, 5.0]:
                z = calculate_z_position(roof_type, roof_pitch, roof_width, y)
                assert z >= 0.0, \
                    f"{roof_type} module at y={y} has negative Z ({z:.3f}m) - sinking below roof!"


class TestModuleBoundaryCollision:
    """Test collision detection at roof boundaries with new Z-positions"""
    
    def test_module_within_bounds_no_collision(self):
        """Module well within roof boundaries should have no collision"""
        roof_length = 12.0
        roof_width = 10.0
        
        # Module at center
        new_position = (0.0, 0.0, 0.30)
        existing_positions = []
        
        result = check_module_collision(
            new_position=new_position,
            existing_positions=existing_positions,
            roof_length=roof_length,
            roof_width=roof_width,
            margin=DEFAULT_MARGIN,
            orientation="portrait"
        )
        
        assert not result["collision"], \
            f"Module at center should not collide: {result['message']}"
        assert result["type"] == "none"
    
    def test_module_at_edge_with_margin(self):
        """Module at edge (respecting margin) should not collide"""
        roof_length = 12.0
        roof_width = 10.0
        margin = DEFAULT_MARGIN
        
        # Calculate position at edge with margin
        # Module center should be at: edge - margin - module_half_width
        edge_x = roof_length / 2
        module_half_width = PV_W / 2
        safe_x = edge_x - margin - module_half_width
        
        new_position = (safe_x, 0.0, 0.30)
        existing_positions = []
        
        result = check_module_collision(
            new_position=new_position,
            existing_positions=existing_positions,
            roof_length=roof_length,
            roof_width=roof_width,
            margin=margin,
            orientation="portrait"
        )
        
        assert not result["collision"], \
            f"Module at safe edge position should not collide: {result['message']}"
    
    def test_module_beyond_edge_collision(self):
        """Module extending beyond roof edge should collide"""
        roof_length = 12.0
        roof_width = 10.0
        
        # Position module so it extends beyond right edge
        edge_x = roof_length / 2
        module_half_width = PV_W / 2
        beyond_x = edge_x + 0.1  # 10cm beyond safe position
        
        new_position = (beyond_x, 0.0, 0.30)
        existing_positions = []
        
        result = check_module_collision(
            new_position=new_position,
            existing_positions=existing_positions,
            roof_length=roof_length,
            roof_width=roof_width,
            margin=DEFAULT_MARGIN,
            orientation="portrait"
        )
        
        assert result["collision"], \
            "Module beyond edge should collide"
        assert result["type"] == "boundary", \
            f"Should be boundary collision, got {result['type']}"


class TestModuleToModuleCollision:
    """Test module-to-module collision with varying Z-positions"""
    
    def test_no_collision_with_spacing(self):
        """Modules with proper spacing should not collide"""
        roof_length = 12.0
        roof_width = 10.0
        
        # Two modules with 1m spacing
        module1 = (0.0, -2.0, 0.30)
        module2 = (0.0, 2.0, 0.30)
        
        result = check_module_collision(
            new_position=module2,
            existing_positions=[module1],
            roof_length=roof_length,
            roof_width=roof_width,
            margin=DEFAULT_MARGIN,
            orientation="portrait"
        )
        
        assert not result["collision"], \
            f"Modules with 4m spacing should not collide: {result['message']}"
    
    def test_collision_when_overlapping(self):
        """Overlapping modules should collide"""
        roof_length = 12.0
        roof_width = 10.0
        
        # Two modules at same position
        module1 = (0.0, 0.0, 0.30)
        module2 = (0.0, 0.0, 0.35)  # Different Z but same X, Y
        
        result = check_module_collision(
            new_position=module2,
            existing_positions=[module1],
            roof_length=roof_length,
            roof_width=roof_width,
            margin=DEFAULT_MARGIN,
            orientation="portrait"
        )
        
        assert result["collision"], \
            "Overlapping modules should collide"
        assert result["type"] == "module", \
            f"Should be module collision, got {result['type']}"
    
    def test_collision_detection_ignores_z_difference(self):
        """Collision detection should work in XY plane (ignore Z)"""
        roof_length = 12.0
        roof_width = 10.0
        
        # Two modules at same XY but different Z (pitched roof scenario)
        module1 = (0.0, -2.0, 0.20)  # Lower on roof
        module2 = (0.0, -2.0, 0.50)  # Higher on roof (same XY position)
        
        result = check_module_collision(
            new_position=module2,
            existing_positions=[module1],
            roof_length=roof_length,
            roof_width=roof_width,
            margin=DEFAULT_MARGIN,
            orientation="portrait"
        )
        
        assert result["collision"], \
            "Modules at same XY should collide regardless of Z"
        assert result["type"] == "module"


class TestPitchedRoofCollisions:
    """Test collision detection specifically for pitched roofs with varying Z"""
    
    def test_satteldach_modules_with_different_z(self):
        """Satteldach: Modules at different Y (and thus different Z) should not collide if spaced"""
        roof_length = 12.0
        roof_width = 10.0
        roof_pitch = 35.0
        
        # Module at eave (low Z)
        y1 = -4.0
        z1 = calculate_z_position("Satteldach", roof_pitch, roof_width, y1)
        module1 = (0.0, y1, z1)
        
        # Module at ridge (high Z)
        y2 = 4.0
        z2 = calculate_z_position("Satteldach", roof_pitch, roof_width, y2)
        module2 = (0.0, y2, z2)
        
        # Verify Z values are different
        assert z2 > z1, \
            f"Ridge module should be higher than eave module: z1={z1:.3f}, z2={z2:.3f}"
        
        # Check collision (should not collide due to Y spacing)
        result = check_module_collision(
            new_position=module2,
            existing_positions=[module1],
            roof_length=roof_length,
            roof_width=roof_width,
            margin=DEFAULT_MARGIN,
            orientation="portrait"
        )
        
        assert not result["collision"], \
            f"Modules with 8m Y-spacing should not collide: {result['message']}"
    
    def test_pultdach_linear_z_progression(self):
        """Pultdach: Verify Z increases linearly and collision detection works"""
        roof_length = 12.0
        roof_width = 10.0
        roof_pitch = 25.0
        
        # Place modules along Y-axis
        y_positions = [-4.0, -2.0, 0.0, 2.0, 4.0]
        modules = []
        
        for y in y_positions:
            z = calculate_z_position("Pultdach", roof_pitch, roof_width, y)
            modules.append((0.0, y, z))
        
        # Verify Z increases
        for i in range(len(modules) - 1):
            assert modules[i + 1][2] > modules[i][2], \
                f"Z should increase: z[{i}]={modules[i][2]:.3f} >= z[{i+1}]={modules[i+1][2]:.3f}"
        
        # Check that properly spaced modules don't collide
        for i, module in enumerate(modules[1:], 1):
            result = check_module_collision(
                new_position=module,
                existing_positions=modules[:i],
                roof_length=roof_length,
                roof_width=roof_width,
                margin=DEFAULT_MARGIN,
                orientation="portrait"
            )
            
            assert not result["collision"], \
                f"Module {i} should not collide with previous modules: {result['message']}"


class TestEdgeCasesWithZPositions:
    """Test edge cases combining Z-position calculation and collision detection"""
    
    def test_module_at_extreme_y_positions(self):
        """Test modules at extreme Y positions (near roof edges)"""
        roof_length = 12.0
        roof_width = 10.0
        roof_pitch = 35.0
        
        # Module at front edge
        y_front = -roof_width / 2 + 1.0  # 1m from edge
        z_front = calculate_z_position("Satteldach", roof_pitch, roof_width, y_front)
        module_front = (0.0, y_front, z_front)
        
        # Module at back edge
        y_back = roof_width / 2 - 1.0  # 1m from edge
        z_back = calculate_z_position("Satteldach", roof_pitch, roof_width, y_back)
        module_back = (0.0, y_back, z_back)
        
        # Both should be valid (no collision)
        result_front = check_module_collision(
            new_position=module_front,
            existing_positions=[],
            roof_length=roof_length,
            roof_width=roof_width,
            margin=DEFAULT_MARGIN,
            orientation="portrait"
        )
        
        result_back = check_module_collision(
            new_position=module_back,
            existing_positions=[module_front],
            roof_length=roof_length,
            roof_width=roof_width,
            margin=DEFAULT_MARGIN,
            orientation="portrait"
        )
        
        assert not result_front["collision"], \
            f"Front edge module should not collide: {result_front['message']}"
        assert not result_back["collision"], \
            f"Back edge module should not collide: {result_back['message']}"
    
    def test_zero_pitch_behaves_like_flat_roof(self):
        """Satteldach with 0° pitch should behave like flat roof"""
        roof_width = 10.0
        
        # Calculate Z for multiple Y positions with 0° pitch
        y_positions = [-4.0, 0.0, 4.0]
        z_values = [
            calculate_z_position("Satteldach", 0.0, roof_width, y)
            for y in y_positions
        ]
        
        # All Z values should be the same (base_z = 0.15)
        assert all(z == approx(0.15) for z in z_values), \
            f"0° pitch should produce constant Z (0.15m), got {z_values}"
    
    def test_very_steep_roof_collision(self):
        """Test collision detection on very steep roof (60°)"""
        roof_length = 12.0
        roof_width = 10.0
        roof_pitch = 60.0
        
        # Two modules with minimal Y spacing
        y1 = 0.0
        z1 = calculate_z_position("Satteldach", roof_pitch, roof_width, y1)
        module1 = (0.0, y1, z1)
        
        y2 = 0.5  # Only 50cm apart
        z2 = calculate_z_position("Satteldach", roof_pitch, roof_width, y2)
        module2 = (0.0, y2, z2)
        
        # Should collide due to close Y spacing
        result = check_module_collision(
            new_position=module2,
            existing_positions=[module1],
            roof_length=roof_length,
            roof_width=roof_width,
            margin=DEFAULT_MARGIN,
            orientation="portrait"
        )
        
        assert result["collision"], \
            "Modules 50cm apart should collide (module height is 1.76m)"


class TestCollisionMessages:
    """Test that collision detection provides meaningful messages"""
    
    def test_boundary_collision_message(self):
        """Boundary collision should provide clear message"""
        roof_length = 12.0
        roof_width = 10.0
        
        # Module beyond right edge
        new_position = (10.0, 0.0, 0.30)
        existing_positions = []
        
        result = check_module_collision(
            new_position=new_position,
            existing_positions=existing_positions,
            roof_length=roof_length,
            roof_width=roof_width,
            margin=DEFAULT_MARGIN,
            orientation="portrait"
        )
        
        assert result["collision"]
        assert result["type"] == "boundary"
        assert "Dachkante" in result["message"], \
            f"Message should mention 'Dachkante': {result['message']}"
    
    def test_module_collision_message(self):
        """Module collision should provide clear message with index"""
        roof_length = 12.0
        roof_width = 10.0
        
        # Two overlapping modules
        module1 = (0.0, 0.0, 0.30)
        module2 = (0.1, 0.1, 0.35)  # Very close to module1
        
        result = check_module_collision(
            new_position=module2,
            existing_positions=[module1],
            roof_length=roof_length,
            roof_width=roof_width,
            margin=DEFAULT_MARGIN,
            orientation="portrait"
        )
        
        assert result["collision"]
        assert result["type"] == "module"
        assert "überlappt" in result["message"].lower(), \
            f"Message should mention overlap: {result['message']}"
        assert result["colliding_index"] == 0, \
            f"Should identify colliding module index: {result['colliding_index']}"


class TestRequirementCoverage:
    """Verify all collision-related requirements are satisfied"""
    
    def test_requirement_7_1_module_overlap_detection(self):
        """Requirement 7.1: Check for module-to-module overlap"""
        roof_length = 12.0
        roof_width = 10.0
        
        # Create overlapping scenario
        module1 = (0.0, 0.0, 0.30)
        module2 = (0.5, 0.5, 0.35)  # Overlaps with module1
        
        result = check_module_collision(
            new_position=module2,
            existing_positions=[module1],
            roof_length=roof_length,
            roof_width=roof_width,
            margin=DEFAULT_MARGIN,
            orientation="portrait"
        )
        
        assert result["collision"], \
            "Requirement 7.1: Should detect module-to-module overlap"
        assert result["type"] == "module"
    
    def test_requirement_7_2_boundary_violation_detection(self):
        """Requirement 7.2: Check for roof edge violation"""
        roof_length = 12.0
        roof_width = 10.0
        
        # Module beyond boundary
        new_position = (10.0, 0.0, 0.30)
        existing_positions = []
        
        result = check_module_collision(
            new_position=new_position,
            existing_positions=existing_positions,
            roof_length=roof_length,
            roof_width=roof_width,
            margin=DEFAULT_MARGIN,
            orientation="portrait"
        )
        
        assert result["collision"], \
            "Requirement 7.2: Should detect boundary violation"
        assert result["type"] == "boundary"
    
    def test_requirement_7_3_warning_message(self):
        """Requirement 7.3: Display warning when collision detected"""
        roof_length = 12.0
        roof_width = 10.0
        
        # Create collision
        module1 = (0.0, 0.0, 0.30)
        module2 = (0.0, 0.0, 0.35)
        
        result = check_module_collision(
            new_position=module2,
            existing_positions=[module1],
            roof_length=roof_length,
            roof_width=roof_width,
            margin=DEFAULT_MARGIN,
            orientation="portrait"
        )
        
        assert result["collision"]
        assert "message" in result, \
            "Requirement 7.3: Should provide warning message"
        assert len(result["message"]) > 0, \
            "Requirement 7.3: Message should not be empty"
    
    def test_requirement_7_4_prevent_placement(self):
        """Requirement 7.4: Prevent placement when collision detected"""
        roof_length = 12.0
        roof_width = 10.0
        
        # Create collision scenario
        module1 = (0.0, 0.0, 0.30)
        module2 = (0.0, 0.0, 0.35)
        
        result = check_module_collision(
            new_position=module2,
            existing_positions=[module1],
            roof_length=roof_length,
            roof_width=roof_width,
            margin=DEFAULT_MARGIN,
            orientation="portrait"
        )
        
        # The collision flag should be True, which would prevent placement
        assert result["collision"] is True, \
            "Requirement 7.4: Collision flag should prevent placement"


# Run tests with pytest
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
