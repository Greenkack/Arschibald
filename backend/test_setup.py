"""
Simple test script to verify backend setup

Run this to test if the backend can start successfully.
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir.parent))

def test_imports():
    """Test that all core modules can be imported"""
    print("Testing imports...")
    
    try:
        from backend.core.config import settings
        print(" Config imported successfully")
        print(f"  - App Name: {settings.APP_NAME}")
        print(f"  - Host: {settings.HOST}")
        print(f"  - Port: {settings.PORT}")
    except Exception as e:
        print(f" Failed to import config: {e}")
        return False
    
    try:
        from backend.core.database import engine, Base, get_db
        print(" Database module imported successfully")
    except Exception as e:
        print(f" Failed to import database: {e}")
        return False
    
    try:
        from backend.middleware.error_handler import APIError, setup_error_handlers
        print(" Middleware imported successfully")
    except Exception as e:
        print(f" Failed to import middleware: {e}")
        return False
    
    try:
        from backend.main import app
        print(" Main app imported successfully")
    except Exception as e:
        print(f" Failed to import main app: {e}")
        return False
    
    return True


def test_health_endpoint():
    """Test the health endpoint"""
    print("\nTesting health endpoint...")
    
    try:
        from fastapi.testclient import TestClient
        from backend.main import app
        
        client = TestClient(app)
        response = client.get("/health")
        
        if response.status_code == 200:
            print(" Health endpoint working")
            print(f"  Response: {response.json()}")
            return True
        else:
            print(f" Health endpoint returned status {response.status_code}")
            return False
    except Exception as e:
        print(f" Failed to test health endpoint: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Backend Setup Verification")
    print("=" * 60)
    
    all_passed = True
    
    # Test imports
    if not test_imports():
        all_passed = False
    
    # Test health endpoint
    if not test_health_endpoint():
        all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print(" All tests passed! Backend setup is working correctly.")
        print("\nYou can now start the server with:")
        print("  python backend/main.py")
        print("\nOr with uvicorn:")
        print("  uvicorn backend.main:app --reload")
    else:
        print(" Some tests failed. Please check the errors above.")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
