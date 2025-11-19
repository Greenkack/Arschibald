"""
Verification Script for API Documentation

This script verifies that all API documentation components are properly configured.
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).resolve().parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

def verify_documentation():
    """Verify all documentation components"""
    
    print("="*70)
    print("API Documentation Verification")
    print("="*70)
    print()
    
    # 1. Check custom OpenAPI schema
    print("1. Checking custom OpenAPI schema...")
    try:
        # Add parent directory to path for imports
        parent_dir = backend_dir.parent
        if str(parent_dir) not in sys.path:
            sys.path.insert(0, str(parent_dir))
        
        from backend.core.api_documentation import custom_openapi_schema, get_common_responses
        print("   ✓ Custom OpenAPI schema module loaded")
        print("   ✓ custom_openapi_schema function available")
        print("   ✓ get_common_responses helper available")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    print()
    
    # 2. Check documentation files
    print("2. Checking documentation files...")
    docs_dir = backend_dir / "docs"
    required_files = [
        "API_DOCUMENTATION.md",
        "API_QUICK_REFERENCE.md",
        "postman_collection.json"
    ]
    
    for file_name in required_files:
        file_path = docs_dir / file_name
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"   ✓ {file_name} ({size:,} bytes)")
        else:
            print(f"   ✗ {file_name} not found")
            return False
    print()
    
    # 3. Check examples
    print("3. Checking API usage examples...")
    examples_dir = backend_dir / "examples"
    example_file = examples_dir / "api_usage_examples.py"
    
    if example_file.exists():
        size = example_file.stat().st_size
        print(f"   ✓ api_usage_examples.py ({size:,} bytes)")
        
        # Check if it can be imported
        try:
            sys.path.insert(0, str(examples_dir))
            from api_usage_examples import SolarCalculatorAPIClient
            print("   ✓ SolarCalculatorAPIClient class available")
            
            # Check methods
            methods = [
                'login', 'calculate_solar', 'create_project', 
                'list_projects', 'calculate_price', 'generate_pdf',
                'list_products', 'create_customer'
            ]
            for method in methods:
                if hasattr(SolarCalculatorAPIClient, method):
                    print(f"   ✓ Method: {method}")
                else:
                    print(f"   ✗ Method missing: {method}")
        except Exception as e:
            print(f"   ✗ Error importing examples: {e}")
            return False
    else:
        print(f"   ✗ api_usage_examples.py not found")
        return False
    print()
    
    # 4. Check Postman collection structure
    print("4. Checking Postman collection structure...")
    try:
        import json
        postman_file = docs_dir / "postman_collection.json"
        with open(postman_file, 'r', encoding='utf-8') as f:
            collection = json.load(f)
        
        print(f"   ✓ Collection name: {collection['info']['name']}")
        print(f"   ✓ Collection version: {collection['info']['version']}")
        print(f"   ✓ Number of folders: {len(collection['item'])}")
        
        # Count total requests
        total_requests = 0
        for folder in collection['item']:
            if 'item' in folder:
                total_requests += len(folder['item'])
            else:
                total_requests += 1
        
        print(f"   ✓ Total requests: {total_requests}")
        
        # List folders
        print("   ✓ Folders:")
        for folder in collection['item']:
            if 'item' in folder:
                print(f"      - {folder['name']} ({len(folder['item'])} requests)")
            else:
                print(f"      - {folder['name']} (single request)")
    except Exception as e:
        print(f"   ✗ Error checking Postman collection: {e}")
        return False
    print()
    
    # 5. Check main.py integration
    print("5. Checking main.py integration...")
    try:
        main_file = backend_dir / "main.py"
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'from backend.core.api_documentation import custom_openapi_schema' in content:
            print("   ✓ Custom OpenAPI schema imported in main.py")
        else:
            print("   ✗ Custom OpenAPI schema not imported in main.py")
            return False
        
        if 'app.openapi = lambda: custom_openapi_schema(app)' in content:
            print("   ✓ Custom OpenAPI schema configured in main.py")
        else:
            print("   ✗ Custom OpenAPI schema not configured in main.py")
            return False
    except Exception as e:
        print(f"   ✗ Error checking main.py: {e}")
        return False
    print()
    
    # 6. Summary
    print("="*70)
    print("✓ All API documentation components verified successfully!")
    print("="*70)
    print()
    print("Documentation Access Points:")
    print("  • Swagger UI:        http://localhost:8000/api/docs")
    print("  • ReDoc:             http://localhost:8000/api/redoc")
    print("  • OpenAPI Schema:    http://localhost:8000/api/openapi.json")
    print("  • Health Check:      http://localhost:8000/health")
    print()
    print("Documentation Files:")
    print("  • Full Documentation: backend/docs/API_DOCUMENTATION.md")
    print("  • Quick Reference:    backend/docs/API_QUICK_REFERENCE.md")
    print("  • Postman Collection: backend/docs/postman_collection.json")
    print("  • Python Examples:    backend/examples/api_usage_examples.py")
    print()
    print("To start the server:")
    print("  cd backend")
    print("  python main.py")
    print()
    
    return True


if __name__ == "__main__":
    success = verify_documentation()
    sys.exit(0 if success else 1)
