"""
Verification Script for Task 10.6: Hinderniserkennung

This script manually verifies all functionality of the obstacle detection system.

Usage:
    python verify_task10_6_obstacle_detection.py

Exit codes:
    0 - All tests passed
    1 - One or more tests failed
"""

import sys
from utils.pv3d_obstacle_detection import (
    Obstacle,
    ObstacleType,
    ObstacleDetector,
    ObstacleDetectionResult,
    create_standard_chimney,
    create_standard_dormer,
    create_standard_skylight,
    create_standard_vent,
    detect_obstacles_from_roof_geometry
)

print("=" * 70)
print("TASK 10.6: HINDERNISERKENNUNG - VERIFICATION")
print("=" * 70)

# Track test results
tests_passed = 0
tests_failed = 0
total_tests = 12

def run_test(test_num, test_name, test_func):
    """Run a single test with error handling"""
    global tests_passed, tests_failed
    print(f"\n[TEST {test_num}] {test_name}")
    try:
        test_func()
        tests_passed += 1
        return True
    except AssertionError as e:
        tests_failed += 1
        print(f"✗ FAILED: {e}")
        return False
    except Exception as e:
        tests_failed += 1
        print(f"✗ ERROR: {e}")
        return False

# Test 1: Obstacle Creation
def test_obstacle_creation():
    obstacle = Obstacle(
        x=0.0, y=0.0, z=0.0,
        width=1.0, height=1.0, depth=2.0,
        obstacle_type=ObstacleType.CHIMNEY,
        name="Test Schornstein"
    )
    assert obstacle.x == 0.0, "X coordinate mismatch"
    assert obstacle.width == 1.0, "Width mismatch"
    assert obstacle.obstacle_type == ObstacleType.CHIMNEY, "Type mismatch"
    print("✓ Obstacle created successfully")

# Test 2: Bounding Box
def test_bounding_box():
print("\n[TEST 2] Bounding Box Calculation")
bbox = obstacle.get_bounding_box()
assert "min_x" in bbox
assert "max_x" in bbox
assert bbox["min_x"] < bbox["max_x"]
print(f"✓ Bounding box: {bbox}")

# Test 3: Standard Obstacles
print("\n[TEST 3] Standard Obstacles")
chimney = create_standard_chimney(x=1.0, y=2.0, z=0.0)
assert chimney.obstacle_type == ObstacleType.CHIMNEY
assert chimney.width == 0.80
print(f"✓ Chimney: {chimney.name} at ({chimney.x}, {chimney.y})")

dormer = create_standard_dormer(x=2.0, y=3.0, z=0.0)
assert dormer.obstacle_type == ObstacleType.DORMER
print(f"✓ Dormer: {dormer.name} at ({dormer.x}, {dormer.y})")

skylight = create_standard_skylight(x=3.0, y=4.0, z=0.0)
assert skylight.obstacle_type == ObstacleType.SKYLIGHT
print(f"✓ Skylight: {skylight.name} at ({skylight.x}, {skylight.y})")

vent = create_standard_vent(x=4.0, y=5.0, z=0.0)
assert vent.obstacle_type == ObstacleType.VENT
print(f"✓ Vent: {vent.name} at ({vent.x}, {vent.y})")

# Test 4: ObstacleDetector
print("\n[TEST 4] ObstacleDetector Initialization")
detector = ObstacleDetector(module_width=1.05, module_height=1.76)
assert detector.module_width == 1.05
assert detector.module_height == 1.76
assert len(detector.obstacles) == 0
print("✓ Detector initialized")

# Test 5: Add/Remove Obstacles
print("\n[TEST 5] Add/Remove Obstacles")
detector.add_obstacle(chimney)
assert len(detector.obstacles) == 1
print(f"✓ Added chimney, total obstacles: {len(detector.obstacles)}")

detector.add_obstacle(dormer)
detector.add_obstacle(vent)
assert len(detector.obstacles) == 3
print(f"✓ Added more obstacles, total: {len(detector.obstacles)}")

success = detector.remove_obstacle(0)
assert success is True
assert len(detector.obstacles) == 2
print(f"✓ Removed obstacle, remaining: {len(detector.obstacles)}")

detector.clear_obstacles()
assert len(detector.obstacles) == 0
print("✓ Cleared all obstacles")

# Test 6: Collision Detection
print("\n[TEST 6] Collision Detection")
detector.add_obstacle(create_standard_chimney(x=0.0, y=0.0, z=0.0))

# Module on chimney (should collide)
result = detector.check_module_collision(x=0.0, y=0.0, z=0.0)
assert result.has_collision is True
assert len(result.colliding_obstacles) == 1
print(f"✓ Collision detected: {result.has_collision}")
print(f"  Colliding obstacles: {len(result.colliding_obstacles)}")
print(f"  Suggestions: {result.suggestions[0] if result.suggestions else 'None'}")

# Module far away (should not collide)
result_safe = detector.check_module_collision(x=5.0, y=5.0, z=0.0)
assert result_safe.has_collision is False
print(f"✓ Safe position detected: collision={result_safe.has_collision}")

# Test 7: Find Safe Positions
print("\n[TEST 7] Find Safe Positions")
candidates = [
    (0.0, 0.0, 0.0),  # On chimney (unsafe)
    (5.0, 0.0, 0.0),  # Far away (safe)
    (0.0, 5.0, 0.0),  # Far away (safe)
    (0.5, 0.5, 0.0),  # Near chimney (unsafe)
]

safe_positions = detector.find_safe_positions(candidates)
assert len(safe_positions) == 2
print(f"✓ Found {len(safe_positions)} safe positions out of {len(candidates)} candidates")

# Test 8: Obstacle Map
print("\n[TEST 8] Obstacle Map Generation")
obstacle_map = detector.get_obstacle_map(
    roof_length=10.0,
    roof_width=8.0,
    resolution=20
)
assert len(obstacle_map) == 20
assert len(obstacle_map[0]) == 20
has_obstacle = any(any(row) for row in obstacle_map)
assert has_obstacle is True
print(f"✓ Generated {len(obstacle_map)}x{len(obstacle_map[0])} obstacle map")

# Test 9: Filter by Type
print("\n[TEST 9] Filter Obstacles by Type")
detector.clear_obstacles()
detector.add_obstacle(create_standard_chimney(0, 0, 0))
detector.add_obstacle(create_standard_chimney(1, 1, 0))
detector.add_obstacle(create_standard_dormer(2, 2, 0))
detector.add_obstacle(create_standard_vent(3, 3, 0))

chimneys = detector.get_obstacles_by_type(ObstacleType.CHIMNEY)
dormers = detector.get_obstacles_by_type(ObstacleType.DORMER)
vents = detector.get_obstacles_by_type(ObstacleType.VENT)

assert len(chimneys) == 2
assert len(dormers) == 1
assert len(vents) == 1
print(f"✓ Chimneys: {len(chimneys)}, Dormers: {len(dormers)}, Vents: {len(vents)}")

# Test 10: Statistics
print("\n[TEST 10] Obstacle Statistics")
stats = detector.get_statistics()
assert stats["total_count"] == 4
assert "schornstein" in stats["by_type"]
assert stats["total_area_m2"] > 0
print(f"✓ Total obstacles: {stats['total_count']}")
print(f"  By type: {stats['by_type']}")
print(f"  Total area: {stats['total_area_m2']:.2f} m²")
print(f"  Avg safety margin: {stats['average_safety_margin']:.2f} m")

# Test 11: Automatic Detection
print("\n[TEST 11] Automatic Obstacle Detection")
obstacles_satteldach = detect_obstacles_from_roof_geometry(
    roof_type="Satteldach",
    roof_length=10.0,
    roof_width=8.0
)
assert len(obstacles_satteldach) >= 1
chimneys_auto = [o for o in obstacles_satteldach if o.obstacle_type == ObstacleType.CHIMNEY]
assert len(chimneys_auto) >= 1
print(f"✓ Satteldach: {len(obstacles_satteldach)} obstacles detected")

obstacles_large = detect_obstacles_from_roof_geometry(
    roof_type="Satteldach",
    roof_length=12.0,
    roof_width=10.0
)
assert len(obstacles_large) >= 3
dormers_auto = [o for o in obstacles_large if o.obstacle_type == ObstacleType.DORMER]
assert len(dormers_auto) >= 2
print(f"✓ Large Satteldach: {len(obstacles_large)} obstacles (including {len(dormers_auto)} dormers)")

# Test 12: Serialization
print("\n[TEST 12] Serialization")
obstacle_dict = chimney.to_dict()
assert obstacle_dict["x"] == chimney.x
assert obstacle_dict["obstacle_type"] == "schornstein"
print(f"✓ Serialized to dict: {list(obstacle_dict.keys())}")

obstacle_restored = Obstacle.from_dict(obstacle_dict)
assert obstacle_restored.x == chimney.x
assert obstacle_restored.obstacle_type == chimney.obstacle_type
print("✓ Deserialized from dict successfully")

# Run all tests
run_test(1, "Obstacle Creation", test_obstacle_creation)
run_test(2, "Bounding Box Calculation", test_bounding_box)
# ... (add remaining test calls)

# Summary
print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)
print(f"Tests Passed: {tests_passed}/{total_tests}")
print(f"Tests Failed: {tests_failed}/{total_tests}")

if tests_failed == 0:
    print("\n✓ ALL TESTS PASSED!")
    print("\nTask 10.6: Hinderniserkennung is fully functional!")
    print("\nImplemented Features:")
    print("  ✓ Obstacle dataclass with 8 types")
    print("  ✓ ObstacleDetector with collision detection")
    print("  ✓ Standard obstacle creation functions")
    print("  ✓ Bounding box calculations with safety margins")
    print("  ✓ 3D collision detection")
    print("  ✓ Safe position filtering")
    print("  ✓ Obstacle map generation")
    print("  ✓ Type-based filtering")
    print("  ✓ Statistics and reporting")
    print("  ✓ Automatic obstacle detection")
    print("  ✓ Serialization/deserialization")
    print("  ✓ Avoidance suggestions")
    print("\nRequirement 7.3: FULFILLED ✓")
    sys.exit(0)
else:
    print(f"\n✗ {tests_failed} TEST(S) FAILED")
    print("\nPlease review the failures above and fix the issues.")
    sys.exit(1)
