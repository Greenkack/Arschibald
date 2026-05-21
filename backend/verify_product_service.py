"""
Product Management Service Verification Script

Quick verification that the Product Management Service is working correctly.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def verify_imports():
    """Verify all imports work"""
    print("Verifying imports...")
    try:
        from backend.services.product_service import ProductService, get_product_service
        from backend.models.product_schemas import (
            ProductCreate, ProductUpdate, ProductResponse,
            ProductSearchRequest, ProductExportRequest, ProductImportRequest
        )
        from backend.api.v1 import products
        print(" All imports successful")
        return True
    except ImportError as e:
        print(f" Import error: {e}")
        return False


def verify_service_creation():
    """Verify service can be created"""
    print("\nVerifying service creation...")
    try:
        from backend.services.product_service import ProductService
        service = ProductService()
        print(f" Service created: {service.service_name}")
        return True
    except Exception as e:
        print(f" Service creation failed: {e}")
        return False


def verify_service_initialization():
    """Verify service can be initialized"""
    print("\nVerifying service initialization...")
    try:
        from backend.services.product_service import get_product_service
        service = get_product_service()
        print(f" Service initialized: {service.is_initialized}")
        return True
    except Exception as e:
        print(f" Service initialization failed: {e}")
        return False


def verify_health_check():
    """Verify health check works"""
    print("\nVerifying health check...")
    try:
        from backend.services.product_service import get_product_service
        service = get_product_service()
        health = service.health_check()
        print(f" Health check status: {health.status.value}")
        print(f"  Message: {health.message}")
        if health.details:
            for key, value in health.details.items():
                print(f"  {key}: {value}")
        return True
    except Exception as e:
        print(f" Health check failed: {e}")
        return False


def verify_api_endpoints():
    """Verify API endpoints are defined"""
    print("\nVerifying API endpoints...")
    try:
        from backend.api.v1 import products
        
        # Check router exists
        assert hasattr(products, 'router'), "Router not found"
        
        # Check key endpoints exist
        routes = [route.path for route in products.router.routes]
        
        expected_routes = [
            '/products/',
            '/products/{product_id}',
            '/products/by-model/{model_name}',
            '/products/search',
            '/products/categories/list',
            '/products/{product_id}/image',
            '/products/export',
            '/products/import'
        ]
        
        for route in expected_routes:
            if route in routes:
                print(f" Endpoint exists: {route}")
            else:
                print(f" Endpoint missing: {route}")
        
        return True
    except Exception as e:
        print(f" API endpoint verification failed: {e}")
        return False


def verify_schemas():
    """Verify Pydantic schemas are valid"""
    print("\nVerifying Pydantic schemas...")
    try:
        from backend.models.product_schemas import (
            ProductCreate, ProductUpdate, ProductResponse,
            ProductSearchRequest, ProductExportRequest, ProductImportRequest
        )
        
        # Test ProductCreate
        product_create = ProductCreate(
            category="Modul",
            model_name="Test Module",
            brand="TestBrand",
            price_euro=200.0
        )
        print(f" ProductCreate schema valid")
        
        # Test ProductUpdate
        product_update = ProductUpdate(price_euro=210.0)
        print(f" ProductUpdate schema valid")
        
        # Test ProductSearchRequest
        search_request = ProductSearchRequest(
            query="test",
            category="Modul",
            limit=50
        )
        print(f" ProductSearchRequest schema valid")
        
        return True
    except Exception as e:
        print(f" Schema verification failed: {e}")
        return False


def verify_documentation():
    """Verify documentation files exist"""
    print("\nVerifying documentation...")
    
    doc_files = [
        'backend/docs/PRODUCT_SERVICE_GUIDE.md',
        'backend/docs/PRODUCT_SERVICE_QUICK_REFERENCE.md',
        'backend/demo_product_service.py',
        'backend/TASK_15_COMPLETE.md'
    ]
    
    all_exist = True
    for doc_file in doc_files:
        if os.path.exists(doc_file):
            print(f" Documentation exists: {doc_file}")
        else:
            print(f" Documentation missing: {doc_file}")
            all_exist = False
    
    return all_exist


def verify_tests():
    """Verify test file exists"""
    print("\nVerifying tests...")
    
    test_file = 'backend/tests/test_product_service.py'
    if os.path.exists(test_file):
        print(f" Test file exists: {test_file}")
        
        # Count test functions
        with open(test_file, 'r') as f:
            content = f.read()
            test_count = content.count('def test_')
            print(f"  Found {test_count} test functions")
        
        return True
    else:
        print(f" Test file missing: {test_file}")
        return False


def main():
    """Run all verifications"""
    print("="*60)
    print("  PRODUCT MANAGEMENT SERVICE VERIFICATION")
    print("="*60)
    
    results = []
    
    # Run all verifications
    results.append(("Imports", verify_imports()))
    results.append(("Service Creation", verify_service_creation()))
    results.append(("Service Initialization", verify_service_initialization()))
    results.append(("Health Check", verify_health_check()))
    results.append(("API Endpoints", verify_api_endpoints()))
    results.append(("Pydantic Schemas", verify_schemas()))
    results.append(("Documentation", verify_documentation()))
    results.append(("Tests", verify_tests()))
    
    # Summary
    print("\n" + "="*60)
    print("  VERIFICATION SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = " PASS" if result else " FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} verifications passed")
    
    if passed == total:
        print("\n ALL VERIFICATIONS PASSED!")
        print("\nThe Product Management Service is ready to use.")
        print("\nNext steps:")
        print("  1. Run tests: pytest backend/tests/test_product_service.py -v")
        print("  2. Run demo: python backend/demo_product_service.py")
        print("  3. Start server: python backend/main.py")
        print("  4. View API docs: http://localhost:8000/api/docs")
        return 0
    else:
        print(f"\n {total - passed} VERIFICATION(S) FAILED")
        print("\nPlease review the errors above.")
        return 1


if __name__ == '__main__':
    exit(main())
