"""
Test script for PDF 3D visualization integration
"""

def test_imports():
    """Test that all imports work correctly"""
    try:
        from utils.pdf_visual_inject import (
            make_pv3d_image_flowable,
            get_pv3d_png_bytes_for_pdf
        )
        from utils.pv3d import BuildingDims, LayoutConfig
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False


def test_pdf_generator_integration():
    """Test that PDF generator has the new method"""
    try:
        # Import the PDF generator
        import pdf_generator
        
        # Check if the class exists
        if not hasattr(pdf_generator, 'PDFGenerator'):
            print("✗ PDFGenerator class not found")
            return False
        
        # Create a dummy instance to check methods
        # We'll use minimal data to avoid errors
        dummy_data = {
            'offer_id': 'TEST-001',
            'date': '2025-01-01',
            'customer': {'name': 'Test Customer'},
            'items': [],
            'grand_total': 0
        }
        
        try:
            generator = pdf_generator.PDFGenerator(
                offer_data=dummy_data,
                module_order=[],
                theme_name="default",
                filename="test.pdf",
                pricing_data={}
            )
            
            # Check if the new method exists
            if hasattr(generator, '_draw_3d_visualization'):
                print("✓ _draw_3d_visualization method exists")
            else:
                print("✗ _draw_3d_visualization method not found")
                return False
            
            # Check if it's in the module map
            module_map = generator._get_module_map()
            if '3d_visualisierung' in module_map:
                print("✓ 3d_visualisierung registered in module map")
            else:
                print("✗ 3d_visualisierung not in module map")
                return False
            
            return True
            
        except Exception as e:
            print(f"✗ Error creating PDFGenerator instance: {e}")
            return False
            
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False


def test_basic_functionality():
    """Test basic functionality of the 3D visualization"""
    try:
        from utils.pv3d import BuildingDims, LayoutConfig, render_image_bytes
        
        # Create test data
        dims = BuildingDims(length_m=10.0, width_m=6.0, wall_height_m=6.0)
        layout = LayoutConfig(mode="auto")
        project_data = {}
        
        print("✓ BuildingDims and LayoutConfig created successfully")
        
        # Note: We won't actually render because it requires PyVista
        # Just check that the function exists
        if callable(render_image_bytes):
            print("✓ render_image_bytes function is callable")
        else:
            print("✗ render_image_bytes is not callable")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Error in basic functionality test: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Testing PDF 3D Visualization Integration")
    print("=" * 60)
    print()
    
    print("Test 1: Imports")
    print("-" * 60)
    test1 = test_imports()
    print()
    
    print("Test 2: PDF Generator Integration")
    print("-" * 60)
    test2 = test_pdf_generator_integration()
    print()
    
    print("Test 3: Basic Functionality")
    print("-" * 60)
    test3 = test_basic_functionality()
    print()
    
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    results = [
        ("Imports", test1),
        ("PDF Generator Integration", test2),
        ("Basic Functionality", test3)
    ]
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{name}: {status}")
    
    all_passed = all(r for _, r in results)
    print()
    if all_passed:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed")
    
    print("=" * 60)
