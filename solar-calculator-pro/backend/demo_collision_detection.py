"""
Collision Detection Service Demo

This script demonstrates the collision detection functionality.
"""

from backend.services.collision_detection_service import (
    CollisionDetectionService,
    Obstacle,
    BoundingBox
)


def demo_module_collisions():
    """Demonstrate module-to-module collision detection."""
    print("=" * 80)
    print("DEMO 1: Module-to-Module Collision Detection")
    print("=" * 80)
    
    service = CollisionDetectionService()
    
    # Scenario 1: No collisions
    print("\nScenario 1: Well-spaced modules (no collisions)")
    modules_ok = [
        {"x": 0.0, "y": 0.0, "z": 6.0, "azimuth": 0.0, "tilt": 30.0},
        {"x": 2.0, "y": 0.0, "z": 6.0, "azimuth": 0.0, "tilt": 30.0},
        {"x": 4.0, "y": 0.0, "z": 6.0, "azimuth": 0.0, "tilt": 30.0}
    ]
    collisions = service.detect_module_collisions(modules_ok)
    print(f"Collisions found: {len(collisions)}")
    
    # Scenario 2: Overlapping modules
    print("\nScenario 2: Overlapping modules")
    modules_overlap = [
        {"x": 0.0, "y": 0.0, "z": 6.0, "azimuth": 0.0, "tilt": 30.0},
        {"x": 0.5, "y": 0.0, "z": 6.0, "azimuth": 0.0, "tilt": 30.0}  # Too close
    ]
    collisions = service.detect_module_collisions(modules_overlap)
    print(f"Collisions found: {len(collisions)}")
    for collision in collisions:
        print(f"  - {collision.description}")
        print(f"    Severity: {collision.severity}")
        print(f"    Overlap: {collision.overlap_percentage:.1f}%")
        print(f"    Suggestion: {collision.suggestion}")


def demo_obstacle_collisions():
    """Demonstrate module-to-obstacle collision detection."""
    print("\n" + "=" * 80)
    print("DEMO 2: Module-to-Obstacle Collision Detection")
    print("=" * 80)
    
    service = CollisionDetectionService()
    
    modules = [
        {"x": 0.0, "y": 0.0, "z": 6.0, "azimuth": 0.0, "tilt": 30.0},
     