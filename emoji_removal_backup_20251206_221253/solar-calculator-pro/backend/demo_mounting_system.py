"""
Demo script for 3D Mounting System Visualization

This script demonstrates all features of the mounting system service:
- Rail generation
- Clamp placement
- Roof penetrations
- Cable routing
- BOM generation
- Cost calculation
"""

import sys
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from services.mounting_system_service import (
    MountingSystemService,
    MountingType,
    RailOrientation
)


def print_section(title: str):
    """Print section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def demo_basic_usage():
    """Demonstrate basic usage"""
    print_section("DEMO 1: Basic Usage - Complete Mounting System")
    
    # Initialize service
    service = MountingSystemService()
    
    # Define a simple 2x3 module array (6 modules)
    module_positions = [
        {'id': 'module_1', 'position': {'x': 0.0, 'y': 0.0, 'z': 0.0}, 'width': 1.6, 'height': 1.0, 'orientation': 'landscape'},
        {'id': 'module_2', 'position': {'x': 1.7, 'y': 0.0, 'z': 0.0}, 'width': 1.6, 'height': 1.0, 'orientation': 'landscape'},
        {'id': 'module_3', 'position': {'x': 3.4, 'y': 0.0, 'z': 0.0}, 'width': 1.6, 'height': 1.0, 'orientation': 'landscape'},
        {'id': 'module_4', 'position': {'x': 0.0, 'y': 1.1, 'z': 0.0}, 'width': 1.6, 'height': 1.0, 'orientation': 'landscape'},
        {'id': 'module_5', 'position': {'x': 1.7, 'y': 1.1, 'z': 0.0}, 'width': 1.6, 'height': 1.0, 'orientation': 'landscape'},
        {'id': 'module_6', 'position': {'x': 3.4, 'y': 1.1, 'z': 0.0}, 'width': 1.6, 'height': 1.0, 'orientation': 'landscape'},
    ]
    
    # Create complete visualization
    visualization = service.create_complete_visualization(
        module_positions=module_positions,
        mounting_type=MountingType.PITCHED_ROOF,
        rail_orientation=RailOrientation.HORIZONTAL,
        roof_angle=30.0,
        inverter_position=(5.0, 0.5, 0.0)
    )
    
    # Print summary
    print(f"Mounting Type: {visualization.mounting_type.value}")
    print(f"Total Rails: {len(visualization.rails)}")
    print(f"Total Clamps: {len(visualization.clamps)}")
    print(f"Total Penetrations: {len(visualization.penetrations)}")
    print(f"Total Cable Routes: {len(visualization.cable_routes)}")
    print(f"Total BOM Items: {len(visualization.bom)}")
    print(f"Total Cost: €{visualization.total_cost:,.2f}")
    
    return visualization


def demo_rail_generation():
    """Demonstrate rail generation"""
    print_section("DEMO 2: Rail Generation - Horizontal vs Vertical")
    
    service = MountingSystemService()
    
    # Simple 3-module row
    modules = [
        {'id': f'module_{i}', 'position': {'x': i * 1.7, 'y': 0.0, 'z': 0.0}, 'width': 1.6, 'height': 1.0}
        for i in range(3)
    ]
    
    # Horizontal rails
    h_rails = service.generate_mounting_rails(modules, MountingType.PITCHED_ROOF, RailOrientation.HORIZONTAL)
    print(f"Horizontal Rails: {len(h_rails)}")
    for rail in h_rails:
        print(f"  - {rail.id}: {rail.length:.2f}m ({rail.orientation.value})")
    
    # Vertical rails
    v_rails = service.generate_mounting_rails(modules, MountingType.PITCHED_ROOF, RailOrientation.VERTICAL)
    print(f"\nVertical Rails: {len(v_rails)}")
    for rail in v_rails:
        print(f"  - {rail.id}: {rail.length:.2f}m ({rail.orientation.value})")


def demo_clamp_placement():
    """Demonstrate clamp placement"""
    print_section("DEMO 3: Clamp Placement")
    
    service = MountingSystemService()
    
    modules = [
        {'id': f'module_{i}', 'position': {'x': i * 1.7, 'y': 0.0, 'z': 0.0}, 'width': 1.6, 'height': 1.0}
        for i in range(4)
    ]
    
    rails = service.generate_mounting_rails(modules, MountingType.PITCHED_ROOF, RailOrientation.HORIZONTAL)
    clamps = service.generate_mounting_clamps(rails, modules)
    
    print(f"Total Clamps: {len(clamps)}")
    
    # Count by type
    from collections import Counter
    clamp_counts = Counter(clamp.clamp_type for clamp in clamps)
    
    print("\nClamp Distribution:")
    for clamp_type, count in clamp_counts.items():
        print(f"  - {clamp_type.value}: {count}")


def demo_roof_penetrations():
    """Demonstrate roof penetrations"""
    print_section("DEMO 4: Roof Penetrations - Different Mounting Types")
    
    service = MountingSystemService()
    
    modules = [
        {'id': f'module_{i}', 'position': {'x': i * 1.7, 'y': 0.0, 'z': 0.0}, 'width': 1.6, 'height': 1.0}
        for i in range(3)
    ]
    
    rails = service.generate_mounting_rails(modules, MountingType.PITCHED_ROOF, RailOrientation.HORIZONTAL)
    
    # Test different mounting types
    for mounting_type in [MountingType.PITCHED_ROOF, MountingType.FLAT_ROOF, MountingType.GROUND_MOUNT]:
        penetrations = service.generate_roof_penetrations(rails, mounting_type, 30.0)
        
        print(f"\n{mounting_type.value.upper()}:")
        print(f"  Total Penetrations: {len(penetrations)}")
        if penetrations:
            print(f"  Penetration Type: {penetrations[0].penetration_type.value}")
            print(f"  Waterproofing: {penetrations[0].waterproofing}")


def demo_cable_routing():
    """Demonstrate cable routing"""
    print_section("DEMO 5: Cable Routing")
    
    service = MountingSystemService()
    
    # 2x3 array
    modules = [
        {'id': f'module_{i}', 'position': {'x': (i % 3) * 1.7, 'y': (i // 3) * 1.1, 'z': 0.0}, 'width': 1.6, 'height': 1.0}
        for i in range(6)
    ]
    
    inverter_position = (5.0, 0.5, 0.0)
    cable_routes = service.generate_cable_routing(modules, inverter_position, MountingType.PITCHED_ROOF)
    
    print(f"Total Cable Routes: {len(cable_routes)}")
    
    dc_routes = [r for r in cable_routes if r.cable_type == "DC"]
    ac_routes = [r for r in cable_routes if r.cable_type == "AC"]
    
    print(f"\nDC Routes: {len(dc_routes)}")
    for route in dc_routes:
        print(f"  - {route.id}: {route.length:.2f}m ({len(route.waypoints)} waypoints)")
    
    print(f"\nAC Routes: {len(ac_routes)}")
    for route in ac_routes:
        print(f"  - {route.id}: {route.length:.2f}m ({len(route.waypoints)} waypoints)")
    
    total_dc_length = sum(r.length for r in dc_routes)
    total_ac_length = sum(r.length for r in ac_routes)
    print(f"\nTotal DC Cable: {total_dc_length:.2f}m")
    print(f"Total AC Cable: {total_ac_length:.2f}m")


def demo_bom_generation():
    """Demonstrate BOM generation"""
    print_section("DEMO 6: Bill of Materials (BOM)")
    
    service = MountingSystemService()
    
    # 3x4 array (12 modules)
    modules = [
        {'id': f'module_{i}', 'position': {'x': (i % 4) * 1.7, 'y': (i // 4) * 1.1, 'z': 0.0}, 'width': 1.6, 'height': 1.0}
        for i in range(12)
    ]
    
    visualization = service.create_complete_visualization(
        modules,
        MountingType.PITCHED_ROOF,
        RailOrientation.HORIZONTAL,
        30.0,
        (7.0, 1.5, 0.0)
    )
    
    print(f"Total BOM Items: {len(visualization.bom)}")
    print(f"\n{'Item ID':<12} {'Description':<40} {'Qty':<6} {'Unit':<10} {'Unit Price':<12} {'Total':<12}")
    print("-" * 100)
    
    for item in visualization.bom:
        print(f"{item.item_id:<12} {item.description:<40} {item.quantity:<6} {item.unit:<10} €{item.unit_price:<11.2f} €{item.total_price:<11.2f}")
    
    print("-" * 100)
    print(f"{'TOTAL COST':<70} €{visualization.total_cost:,.2f}")
    
    # Category breakdown
    print("\n\nCost by Category:")
    from collections import defaultdict
    category_costs = defaultdict(float)
    for item in visualization.bom:
        category_costs[item.category] += item.total_price
    
    for category, cost in sorted(category_costs.items(), key=lambda x: x[1], reverse=True):
        percentage = (cost / visualization.total_cost) * 100
        print(f"  {category:<30} €{cost:>10,.2f} ({percentage:>5.1f}%)")


def demo_cost_comparison():
    """Demonstrate cost comparison for different system sizes"""
    print_section("DEMO 7: Cost Comparison - System Size Impact")
    
    service = MountingSystemService()
    
    system_sizes = [
        ("Small (6 modules)", 6, 2, 3),
        ("Medium (12 modules)", 12, 3, 4),
        ("Large (24 modules)", 24, 4, 6),
        ("Extra Large (40 modules)", 40, 5, 8)
    ]
    
    print(f"{'System Size':<25} {'Modules':<10} {'Rails':<10} {'Clamps':<10} {'Penetrations':<15} {'Total Cost':<15}")
    print("-" * 95)
    
    for name, total_modules, rows, cols in system_sizes:
        modules = [
            {'id': f'module_{i}', 'position': {'x': (i % cols) * 1.7, 'y': (i // cols) * 1.1, 'z': 0.0}, 'width': 1.6, 'height': 1.0}
            for i in range(total_modules)
        ]
        
        visualization = service.create_complete_visualization(
            modules,
            MountingType.PITCHED_ROOF,
            RailOrientation.HORIZONTAL,
            30.0,
            (cols * 1.7 + 1, rows * 1.1 / 2, 0.0)
        )
        
        print(f"{name:<25} {total_modules:<10} {len(visualization.rails):<10} {len(visualization.clamps):<10} {len(visualization.penetrations):<15} €{visualization.total_cost:>13,.2f}")


def demo_mounting_type_comparison():
    """Demonstrate different mounting types"""
    print_section("DEMO 8: Mounting Type Comparison")
    
    service = MountingSystemService()
    
    # Same module layout for all types
    modules = [
        {'id': f'module_{i}', 'position': {'x': (i % 3) * 1.7, 'y': (i // 3) * 1.1, 'z': 0.0}, 'width': 1.6, 'height': 1.0}
        for i in range(9)
    ]
    
    mounting_types = [
        (MountingType.PITCHED_ROOF, 30.0),
        (MountingType.FLAT_ROOF, 0.0),
        (MountingType.GROUND_MOUNT, 25.0)
    ]
    
    print(f"{'Mounting Type':<20} {'Penetration Type':<20} {'Waterproofing':<15} {'Total Cost':<15}")
    print("-" * 70)
    
    for mounting_type, angle in mounting_types:
        visualization = service.create_complete_visualization(
            modules,
            mounting_type,
            RailOrientation.HORIZONTAL,
            angle,
            (5.5, 1.5, 0.0)
        )
        
        pen_type = visualization.penetrations[0].penetration_type.value if visualization.penetrations else "none"
        waterproof = "Yes" if visualization.penetrations and visualization.penetrations[0].waterproofing else "No"
        
        print(f"{mounting_type.value:<20} {pen_type:<20} {waterproof:<15} €{visualization.total_cost:>13,.2f}")


def demo_export_to_json():
    """Demonstrate exporting to JSON"""
    print_section("DEMO 9: Export to JSON")
    
    service = MountingSystemService()
    
    modules = [
        {'id': f'module_{i}', 'position': {'x': (i % 2) * 1.7, 'y': (i // 2) * 1.1, 'z': 0.0}, 'width': 1.6, 'height': 1.0}
        for i in range(4)
    ]
    
    visualization = service.create_complete_visualization(
        modules,
        MountingType.PITCHED_ROOF,
        RailOrientation.HORIZONTAL,
        30.0,
        (3.5, 1.0, 0.0)
    )
    
    # Convert to JSON-serializable format
    export_data = {
        'mounting_type': visualization.mounting_type.value,
        'total_cost': visualization.total_cost,
        'summary': {
            'total_rails': len(visualization.rails),
            'total_clamps': len(visualization.clamps),
            'total_penetrations': len(visualization.penetrations),
            'total_cable_routes': len(visualization.cable_routes),
            'total_bom_items': len(visualization.bom)
        },
        'bom': [
            {
                'item_id': item.item_id,
                'description': item.description,
                'quantity': item.quantity,
                'unit': item.unit,
                'unit_price': item.unit_price,
                'total_price': item.total_price,
                'category': item.category
            }
            for item in visualization.bom
        ]
    }
    
    json_output = json.dumps(export_data, indent=2)
    print("JSON Export (first 50 lines):")
    print("\n".join(json_output.split("\n")[:50]))
    print("\n... (truncated)")
    
    # Save to file
    output_file = Path(__file__).parent / "mounting_system_export.json"
    with open(output_file, 'w') as f:
        f.write(json_output)
    
    print(f"\nFull export saved to: {output_file}")


def main():
    """Run all demos"""
    print("\n" + "=" * 80)
    print("  3D MOUNTING SYSTEM VISUALIZATION - COMPREHENSIVE DEMO")
    print("=" * 80)
    
    try:
        demo_basic_usage()
        demo_rail_generation()
        demo_clamp_placement()
        demo_roof_penetrations()
        demo_cable_routing()
        demo_bom_generation()
        demo_cost_comparison()
        demo_mounting_type_comparison()
        demo_export_to_json()
        
        print("\n" + "=" * 80)
        print("  ALL DEMOS COMPLETED SUCCESSFULLY!")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
