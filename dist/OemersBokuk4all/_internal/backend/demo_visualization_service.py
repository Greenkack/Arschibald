"""
Demo script for 3D Visualization Service

This script demonstrates how to use the VisualizationService
to generate 3D models, calculate placements, and export models.
"""

import sys
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.visualization_service import VisualizationService


def print_section(title: str):
    """Print a section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def demo_service_availability():
    """Demo: Check service availability."""
    print_section("1. Service Availability Check")
    
    service = VisualizationService()
    available = service.is_available()
    
    print(f"3D Visualization Service Available: {available}")
    
    if available:
        print(f"  • PV Module Width: {service.pv_width}m")
        print(f"  • PV Module Height: {service.pv_height}m")
        print(f"  • PV Module Thickness: {service.pv_thickness}m")
    else:
        print("   3D visualization modules not installed")
        print("  Install with: pip install pyvista numpy")
    
    return service, available


def demo_placement_statistics():
    """Demo: Calculate placement statistics."""
    print_section("2. Placement Statistics Calculation")
    
    service = VisualizationService()
    
    # Sample data
    building_dims = {
        "length_m": 10.0,
        "width_m": 6.0,
        "wall_height_m": 6.0
    }
    
    roof_config = {
        "type": "gable",
        "angle": 30.0,
        "orientation": "south"
    }
    
    positions = [
        {"index": i, "x": i * 1.1, "y": 0.0, "z": 6.0, "azimuth": 0.0, "tilt": 30.0}
        for i in range(20)
    ]
    
    stats = service._calculate_placement_statistics(
        positions=positions,
        building_dims=building_dims,
        roof_config=roof_config
    )
    
    print("Building Dimensions:")
    print(f"  • Length: {building_dims['length_m']}m")
    print(f"  • Width: {building_dims['width_m']}m")
    print(f"  • Wall Height: {building_dims['wall_height_m']}m")
    
    print("\nPlacement Statistics:")
    print(f"  • Total Modules: {stats['total_modules']}")
    print(f"  • Total Area: {stats['total_area_m2']}m²")
    print(f"  • Roof Coverage: {stats['roof_coverage_percent']}%")
    print(f"  • Average Spacing: {stats['average_spacing_m']}m")


def demo_collision_warnings():
    """Demo: Generate collision warnings."""
    print_section("3. Collision Warning Generation")
    
    service = VisualizationService()
    
    # Sample collisions
    collisions = [
        {"type": "module_overlap", "module1": 0, "module2": 1},
        {"type": "boundary_violation", "module": 5},
        {"type": "clearance_violation", "module": 3},
        {"type": "module_overlap", "module1": 7, "module2": 8}
    ]
    
    warnings = service._generate_collision_warnings(collisions)
    
    print(f"Detected {len(collisions)} collisions:")
    for i, warning in enumerate(warnings, 1):
        print(f"  {i}. {warning}")


def demo_3d_model_generation():
    """Demo: Generate 3D model (requires pv3d modules)."""
    print_section("4. 3D Model Generation")
    
    service = VisualizationService()
    
    if not service.is_available():
        print(" Skipping: 3D visualization modules not available")
        return
    
    # Configuration
    building_dims = {
        "length_m": 12.0,
        "width_m": 8.0,
        "wall_height_m": 6.0
    }
    
    roof_config = {
        "type": "gable",
        "angle": 35.0,
        "orientation": "south",
        "covering": "Ziegel"
    }
    
    module_config = {
        "count": 24,
        "type": "standard",
        "spacing": 0.02,
        "margin": 0.5
    }
    
    print("Generating 3D model...")
    print(f"  • Building: {building_dims['length_m']}m × {building_dims['width_m']}m")
    print(f"  • Roof: {roof_config['type']}, {roof_config['angle']}°")
    print(f"  • Modules: {module_config['count']}")
    
    try:
        result = service.generate_3d_model(
            building_dims=building_dims,
            roof_config=roof_config,
            module_config=module_config,
            placement_mode="auto"
        )
        
        print("\n Model generated successfully!")
        print(f"  • Modules placed: {len(result['module_positions'])}")
        print(f"  • Total area: {result['statistics']['total_area_m2']}m²")
        print(f"  • Roof coverage: {result['statistics']['roof_coverage_percent']}%")
        
        if result['warnings']:
            print(f"\n Warnings ({len(result['warnings'])}):")
            for warning in result['warnings']:
                print(f"  • {warning}")
        
    except Exception as e:
        print(f"\n Error: {e}")


def demo_auto_placement():
    """Demo: Calculate automatic placement (requires pv3d modules)."""
    print_section("5. Automatic Placement Calculation")
    
    service = VisualizationService()
    
    if not service.is_available():
        print(" Skipping: 3D visualization modules not available")
        return
    
    building_dims = {
        "length_m": 10.0,
        "width_m": 6.0,
        "wall_height_m": 6.0
    }
    
    roof_config = {
        "type": "flat",
        "angle": 15.0,
        "orientation": "south"
    }
    
    module_config = {
        "count": 20,
        "spacing": 0.02,
        "margin": 0.5
    }
    
    print("Calculating automatic placement...")
    
    try:
        positions = service.calculate_auto_placement(
            building_dims=building_dims,
            roof_config=roof_config,
            module_config=module_config
        )
        
        print(f"\n Placement calculated: {len(positions)} modules")
        
        # Show first 3 positions
        print("\nFirst 3 module positions:")
        for pos in positions[:3]:
            print(f"  Module {pos['index']}: "
                  f"x={pos['x']:.2f}m, y={pos['y']:.2f}m, z={pos['z']:.2f}m, "
                  f"tilt={pos['tilt']:.1f}°")
        
    except Exception as e:
        print(f"\n Error: {e}")


def main():
    """Run all demos."""
    print("\n" + "=" * 70)
    print("  3D VISUALIZATION SERVICE DEMO")
    print("=" * 70)
    
    # Check availability
    service, available = demo_service_availability()
    
    # Always run these (don't require pv3d modules)
    demo_placement_statistics()
    demo_collision_warnings()
    
    # Only run if modules available
    if available:
        demo_3d_model_generation()
        demo_auto_placement()
    else:
        print_section("Additional Demos")
        print(" Additional demos require 3D visualization modules")
        print("  Install with: pip install pyvista numpy")
    
    print("\n" + "=" * 70)
    print("  Demo Complete!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
