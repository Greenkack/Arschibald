"""
Demo script for Pricing Service

This script demonstrates the key features of the Pricing Service:
- Price calculation with INDEX/MATCH logic
- Matrix management
- Matrix upload and validation
- CRUD operations
- Error handling and fallback strategies

Requirements: 1.3, 4.5, 14.1, 14.2
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.pricing_service import get_pricing_service


def print_section(title: str):
    """Print section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def demo_price_calculation():
    """Demonstrate price calculation"""
    print_section("1. Price Calculation with INDEX/MATCH Logic")
    
    service = get_pricing_service()
    
    # Test case 1: Standard calculation
    print("Test 1: Standard price calculation")
    print("  Module count: 20")
    print("  Storage model: 15kWh")
    
    result = service.calculate_price(
        module_count=20,
        storage_model="15kWh",
        enable_fallback=True
    )
    
    if result['success']:
        print(f"  ✓ Success!")
        print(f"  Base price: {result['base_price']} EUR")
        print(f"  Row used: {result['row_used']}")
        print(f"  Column used: {result['column_used']}")
        print(f"  Matrix: {result['matrix_name']}")
    else:
        print(f"  ✗ Error: {result['user_message']}")
    
    # Test case 2: No storage
    print("\nTest 2: Price without storage")
    print("  Module count: 15")
    print("  Storage model: None (kein Speicher)")
    
    result = service.calculate_price(
        module_count=15,
        storage_model=None,
        enable_fallback=True
    )
    
    if result['success']:
        print(f"  ✓ Success!")
        print(f"  Base price: {result['base_price']} EUR")
        print(f"  Column used: {result['column_used']}")
    else:
        print(f"  ✗ Error: {result['user_message']}")
    
    # Test case 3: Fallback scenario
    print("\nTest 3: Fallback scenario (module count not in matrix)")
    print("  Module count: 18 (not in matrix)")
    print("  Storage model: 15kWh")
    
    result = service.calculate_price(
        module_count=18,
        storage_model="15kWh",
        enable_fallback=True
    )
    
    if result['success']:
        print(f"  ✓ Success with fallback!")
        print(f"  Base price: {result['base_price']} EUR")
        print(f"  Row used: {result['row_used']} (floor logic)")
        if result['fallback_used']:
            print(f"  Fallback info: {result['fallback_info'].get('message', '')}")
    else:
        print(f"  ✗ Error: {result['user_message']}")


def demo_matrix_management():
    """Demonstrate matrix management"""
    print_section("2. Matrix Management")
    
    service = get_pricing_service()
    
    # List matrices
    print("Listing all matrices:")
    result = service.list_matrices()
    
    if result['success']:
        print(f"  Found {result['count']} matrices:")
        for matrix in result['matrices']:
            active = "✓ ACTIVE" if matrix['is_active'] else ""
            print(f"    - ID {matrix['id']}: {matrix['name']} {active}")
    else:
        print(f"  ✗ Error: {result.get('error', 'Unknown error')}")
    
    # Create new matrix
    print("\nCreating new matrix:")
    result = service.create_matrix(
        name="Demo Matrix",
        description="Test matrix for demonstration",
        pricing_mode="pauschal"
    )
    
    if result['success']:
        print(f"  ✓ Created matrix with ID: {result['matrix_id']}")
        demo_matrix_id = result['matrix_id']
    else:
        print(f"  ✗ Error: {result.get('error', 'Unknown error')}")
        return


def demo_matrix_upload():
    """Demonstrate matrix upload"""
    print_section("3. Matrix Upload and Validation")
    
    service = get_pricing_service()
    
    # Sample CSV data
    csv_content = """ROW_LABEL;10kWh;15kWh;20kWh;Kein Speicher
10;15000;17500;20000;12000
15;18000;20500;23000;15000
20;21000;23500;26000;18000
25;24000;26500;29000;21000
30;27000;29500;32000;24000"""
    
    print("Uploading matrix from CSV:")
    print("  Rows: 10, 15, 20, 25, 30 modules")
    print("  Columns: 10kWh, 15kWh, 20kWh, Kein Speicher")
    
    result = service.upload_matrix_csv(
        name="Uploaded Demo Matrix",
        csv_content=csv_content,
        delimiter=";"
    )
    
    if result['success']:
        print(f"  ✓ Upload successful!")
        print(f"  Matrix ID: {result['matrix_id']}")
        
        # Show validation results
        validation = result.get('validation', {})
        if validation.get('valid'):
            print(f"  ✓ Validation passed")
            info = validation.get('info', {})
            print(f"    - Rows: {info.get('total_rows', 0)}")
            print(f"    - Columns: {info.get('total_columns', 0)}")
            print(f"    - Cells: {info.get('total_cells', 0)}")
        else:
            print(f"  ✗ Validation failed:")
            for error in validation.get('errors', []):
                print(f"      - {error}")
    else:
        print(f"  ✗ Error: {result.get('error', 'Unknown error')}")


def demo_crud_operations():
    """Demonstrate CRUD operations"""
    print_section("4. CRUD Operations")
    
    service = get_pricing_service()
    
    # Get active matrix
    result = service.list_matrices()
    if not result['success'] or result['count'] == 0:
        print("  No matrices available for CRUD demo")
        return
    
    # Find active matrix or use first one
    matrix_id = None
    for matrix in result['matrices']:
        if matrix['is_active']:
            matrix_id = matrix['id']
            break
    
    if not matrix_id:
        matrix_id = result['matrices'][0]['id']
    
    print(f"Using matrix ID: {matrix_id}")
    
    # Add row
    print("\nAdding row:")
    result = service.add_row(
        matrix_id=matrix_id,
        label="35"
    )
    
    if result['success']:
        print(f"  ✓ {result['message']}")
        row_id = result['row_id']
    else:
        print(f"  ✗ Error: {result.get('error', 'Unknown error')}")
        return
    
    # Add column
    print("\nAdding column:")
    result = service.add_column(
        matrix_id=matrix_id,
        label="25kWh"
    )
    
    if result['success']:
        print(f"  ✓ {result['message']}")
        column_id = result['column_id']
    else:
        print(f"  ✗ Error: {result.get('error', 'Unknown error')}")
        return
    
    # Set cell value
    print("\nSetting cell value:")
    result = service.set_cell_value(
        matrix_id=matrix_id,
        row_id=row_id,
        column_id=column_id,
        value=30000.00,
        data_type="number"
    )
    
    if result['success']:
        print(f"  ✓ {result['message']}")
    else:
        print(f"  ✗ Error: {result.get('error', 'Unknown error')}")


def demo_error_handling():
    """Demonstrate error handling"""
    print_section("5. Error Handling and Fallback Strategies")
    
    service = get_pricing_service()
    
    # Test 1: Invalid module count
    print("Test 1: Invalid module count (negative)")
    result = service.calculate_price(
        module_count=-5,
        storage_model="15kWh"
    )
    
    if not result['success']:
        print(f"  ✓ Error caught correctly")
        print(f"  Error type: {result.get('error_type', 'unknown')}")
        print(f"  User message: {result.get('user_message', 'No message')}")
    
    # Test 2: Module count not in matrix
    print("\nTest 2: Module count not in matrix (with fallback)")
    result = service.calculate_price(
        module_count=999,
        storage_model="15kWh",
        enable_fallback=True
    )
    
    if result['success'] and result['fallback_used']:
        print(f"  ✓ Fallback successful")
        print(f"  Fallback strategy: {result['fallback_info'].get('fallback_type', 'unknown')}")
        print(f"  Message: {result['fallback_info'].get('message', '')}")
    elif not result['success']:
        print(f"  ✗ Error: {result.get('user_message', 'Unknown error')}")
        if result.get('suggestions'):
            print(f"  Suggestions:")
            for suggestion in result['suggestions']:
                print(f"    - {suggestion}")


def demo_cache_management():
    """Demonstrate cache management"""
    print_section("6. Cache Management")
    
    service = get_pricing_service()
    
    # Get cache stats
    print("Cache statistics:")
    stats = service.get_cache_stats()
    print(f"  Cache size: {stats['cache_size']}")
    print(f"  Cache keys: {len(stats['cache_keys'])}")
    
    # Clear cache
    print("\nClearing cache:")
    result = service.clear_cache()
    
    if result['success']:
        print(f"  ✓ {result['message']}")
    else:
        print(f"  ✗ Error: {result.get('error', 'Unknown error')}")


def main():
    """Run all demos"""
    print("\n" + "=" * 80)
    print("  PRICING SERVICE DEMONSTRATION")
    print("  Requirements: 1.3, 4.5, 14.1, 14.2")
    print("=" * 80)
    
    try:
        demo_price_calculation()
        demo_matrix_management()
        demo_matrix_upload()
        demo_crud_operations()
        demo_error_handling()
        demo_cache_management()
        
        print("\n" + "=" * 80)
        print("  DEMONSTRATION COMPLETE")
        print("=" * 80 + "\n")
        
    except Exception as e:
        print(f"\n✗ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
