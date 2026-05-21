"""
Demo script for Advanced 3D Visualization Service

This script demonstrates all features of the advanced visualization service.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.visualization_advanced_service import VisualizationAdvancedService
import json


def demo_complete_model_generation():
    """Demo: Generate complete 3D model."""
    print("\n" + "="*80)
    print("DEMO 1: Complete 3D Model Generation")
    print("="*80)
    
    viz = VisualizationAdvancedService()
    
    if not viz.is_available():
        print(" 3D visualization service not available")
        return
    
    # Define building and configuration
    building_dims = {
        "length_m": 10.0,
        "width_m": 6.0,
        "wall_height_m": 6.0
    }
    
    roof_config = {
        "type": "auto",  # Auto-detect roof type
        "angle": 15.0,
        "orientation": "south"
    }
    
    module_config = {
        "count": 20,
        "module_power_w": 400,
        "module_weight_kg": 20.0,
        "module_efficiency": 0.20,
        "min_spacing": 0.02,
        "min_edge_distance": 0.5,
        "avoid_shading": True,
        "optimize_for": "max_modules"
    }
    
    rendering_options = {
        "show_mounting": True,
        "show_labels": False,
        "color_scheme": "default",
        "lighting": "realistic"
    }
    
    print("\n Generating complete 3D model...")
    result = viz.generate_complete_3d_model(
        building_dims=building_dims,
        roof_config=roof_config,
        module_config=module_config,
        placement_mode="auto",
        rendering_options=rendering_options
    )
    
    print("\n Model generated successfully!")
    print(f"\n Statistics:")
    print(f"  - Total modules: {result['statistics']['total_modules']}")
    print(f"  - Total power: {result['statistics']['total_power_kw']} kW")
    print(f"  - Roof coverage: {result['statistics']['roof_coverage_percent']:.1f}%")
    print(f"  - Total weight: {result['statistics']['total_weight_kg']} kg")
    print(f"  - Installation time: {result['statistics']['installation_time_hours']} hours")
    
    print(f"\n Collision Detection:")
    collision = result['collision_result']
    print(f"  - Has collisions: {collision['has_collisions']}")
    print(f"  - Severity: {collision['severity']}")
    print(f"  - Recommendations: {len(collision['recommendations'])}")
    for rec in collision['recommendations']:
        print(f"    • {rec}")
    
    print(f"\n Mounting System:")
    mounting = result['mounting_result']
    print(f"  - Rails: {mounting['rail_count']}")
    print(f"  - Clamps: {mounting['clamp_count']}")
    print(f"  - Cost estimate: €{mounting['cost_estimate']:.2f}")
    
    return result


def demo_roof_detection():
    """Demo: Automatic roof type detection."""
    print("\n" + "="*80)
    print("DEMO 2: Roof Type Detection")
    print("="*80)
    
    viz = VisualizationAdvancedService()
    
    if not viz.is_available():
        print(" 3D visualization service not available")
        return
    
    building_dims = {
        "length_m": 12.0,
        "width_m": 8.0,
        "wall_height_m": 7.0
    }
    
    roof_hints = {
        "has_ridge": True,
        "symmetrical": True
    }
    
    print("\n Detecting roof type...")
    result = viz.detect_roof_type(building_dims, roof_hints)
    
    print("\n Roof detected!")
    print(f"  - Type: {result.roof_type}")
    print(f"  - Confidence: {result.confidence * 100:.1f}%")
    print(f"  - Angle: {result.angle_deg}°")
    print(f"  - Orientation: {result.orientation}")
    print(f"  - Total area: {result.area_m2:.2f} m²")
    print(f"  - Usable area: {result.usable_area_m2:.2f} m²")


def demo_collision_detection():
    """Demo: Advanced collision detection."""
    print("\n" + "="*80)
    print("DEMO 3: Collision Detection")
    print("="*80)
    
    viz = VisualizationAdvancedService()
    
    if not viz.is_available():
        print(" 3D visualization service not available")
        return
    
    # Create some test positions (some with collisions)
    module_positions = [
        {"x": 1.0, "y": 1.0, "z": 6.0, "azimuth": 0, "tilt": 15},
        {"x": 2.1, "y": 1.0, "z": 6.0, "azimuth": 0, "tilt": 15},  # OK
        {"x": 1.5, "y": 1.0, "z": 6.0, "azimuth": 0, "tilt": 15},  # Collision!
        {"x": 9.5, "y": 5.5, "z": 6.0, "azimuth": 0, "tilt": 15},  # Near edge
    ]
    
    building_dims = {
        "length_m": 10.0,
        "width_m": 6.0,
        "wall_height_m": 6.0
    }
    
    roof_config = {
        "type": "flat",
        "angle": 0.0,
        "orientation": "south"
    }
    
    print("\n Detecting collisions...")
    result = viz.detect_collisions_advanced(
        module_positions=module_positions,
        building_dims=building_dims,
        roof_config=roof_config,
        tolerance=0.01
    )
    
    print("\n Collision detection complete!")
    print(f"  - Has collisions: {result.has_collisions}")
    print(f"  - Collision count: {result.collision_count}")
    print(f"  - Severity: {result.severity}")
    
    if result.collisions:
        print(f"\n  Detected collisions:")
        for i, collision in enumerate(result.collisions, 1):
            print(f"  {i}. {collision['type']} (severity: {collision['severity']})")
    
    print(f"\n Recommendations:")
    for rec in result.recommendations:
        print(f"  • {rec}")


def demo_automatic_placement():
    """Demo: Automatic module placement with optimization."""
    print("\n" + "="*80)
    print("DEMO 4: Automatic Module Placement")
    print("="*80)
    
    viz = VisualizationAdvancedService()
    
    if not viz.is_available():
        print(" 3D visualization service not available")
        return
    
    building_dims = {
        "length_m": 10.0,
        "width_m": 6.0,
        "wall_height_m": 6.0
    }
    
    roof_config = {
        "type": "flat",
        "angle": 0.0,
        "orientation": "south"
    }
    
    module_config = {
        "count": 25,
        "module_power_w": 400,
        "min_spacing": 0.02,
        "min_edge_distance": 0.5,
        "avoid_shading": True,
        "optimize_for": "max_modules"
    }
    
    print("\n Calculating automatic placement...")
    positions = viz.calculate_automatic_placement(
        building_dims=building_dims,
        roof_config=roof_config,
        module_config=module_config
    )
    
    print(f"\n Placement calculated!")
    print(f"  - Requested modules: {module_config['count']}")
    print(f"  - Placed modules: {len(positions)}")
    print(f"  - Optimization goal: {module_config['optimize_for']}")
    
    if len(positions) < module_config['count']:
        print(f"\n  Could only place {len(positions)} of {module_config['count']} modules")
        print(f"  - Reason: Space constraints with current settings")
    
    # Show first few positions
    print(f"\n Sample positions:")
    for i, pos in enumerate(positions[:3], 1):
        print(f"  {i}. x={pos['x']:.2f}m, y={pos['y']:.2f}m, z={pos['z']:.2f}m")


def demo_mounting_system():
    """Demo: Mounting system calculation."""
    print("\n" + "="*80)
    print("DEMO 5: Mounting System Calculation")
    print("="*80)
    
    viz = VisualizationAdvancedService()
    
    if not viz.is_available():
        print(" 3D visualization service not available")
        return
    
    # Create sample positions
    module_positions = [
        {"x": i * 1.1, "y": j * 1.8, "z": 6.0, "azimuth": 0, "tilt": 15}
        for i in range(5) for j in range(4)
    ]
    
    roof_config = {
        "type": "flat",
        "angle": 0.0,
        "orientation": "south"
    }
    
    module_config = {
        "module_power_w": 400,
        "module_weight_kg": 20.0
    }
    
    print("\n Calculating mounting system...")
    result = viz.calculate_mounting_system(
        module_positions=module_positions,
        roof_config=roof_config,
        module_config=module_config
    )
    
    print("\n Mounting system calculated!")
    print(f"  - Rails: {result.rail_count}")
    print(f"  - Clamps: {result.clamp_count}")
    print(f"  - Total weight: {result.total_weight_kg} kg")
    print(f"  - Cost estimate: €{result.cost_estimate:.2f}")
    print(f"  - Installation time: {result.installation_time_hours} hours")
    
    print(f"\n Bill of Materials:")
    for item in result.bom[:5]:  # Show first 5 items
        print(f"  - {item['item']}: {item['quantity']} units @ €{item['unit_price']:.2f}")


def demo_multi_view_export():
    """Demo: Multi-view export."""
    print("\n" + "="*80)
    print("DEMO 6: Multi-View Export")
    print("="*80)
    
    print("\n Multi-view export would generate:")
    print("  - Front view (1920x1080 PNG)")
    print("  - Side view (1920x1080 PNG)")
    print("  - Top view (1920x1080 PNG)")
    print("  - Perspective view (1920x1080 PNG)")
    print("\n Each view would be returned as base64-encoded image data")
    print("  (Actual export requires scene_data from model generation)")


def demo_animation_generation():
    """Demo: Animation generation."""
    print("\n" + "="*80)
    print("DEMO 7: Animation Generation")
    print("="*80)
    
    print("\n Available animation types:")
    print("  1. 360° Rotation (60 frames, 6 seconds)")
    print("  2. Assembly Animation (shows modules being placed)")
    print("  3. Flythrough Animation (camera movement)")
    print("  4. Exploded View (component breakdown)")
    print("\n Animations are returned as base64-encoded GIF or MP4")
    print("  (Actual generation requires scene_data from model generation)")


def main():
    """Run all demos."""
    print("\n" + "="*80)
    print("3D VISUALIZATION ADVANCED SERVICE - DEMO")
    print("="*80)
    
    try:
        # Run demos
        result = demo_complete_model_generation()
        demo_roof_detection()
        demo_collision_detection()
        demo_automatic_placement()
        demo_mounting_system()
        demo_multi_view_export()
        demo_animation_generation()
        
        print("\n" + "="*80)
        print(" ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("="*80)
        print("\n For more information, see:")
        print("  - docs/VISUALIZATION_ADVANCED_GUIDE.md")
        print("  - docs/VISUALIZATION_ADVANCED_QUICK_REFERENCE.md")
        print("  - API endpoints at /api/v1/visualization/advanced/")
        
    except Exception as e:
        print(f"\n Error running demos: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
