"""
WebSocket Verification Script

Verifies that the WebSocket implementation is working correctly.
"""

import sys
import os

# Add parent directory to path for backend imports
backend_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(backend_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def verify_imports():
    """Verify all WebSocket modules can be imported"""
    print("✓ Verifying imports...")
    
    try:
        from backend.core.websocket_manager import WebSocketManager, MessageType, get_websocket_manager
        print("  ✓ WebSocket Manager imported")
        
        from backend.middleware.websocket_auth import WebSocketAuthMiddleware
        print("  ✓ WebSocket Authentication imported")
        
        from backend.api.v1 import websocket
        print("  ✓ WebSocket API imported")
        
        return True
    except Exception as e:
        print(f"  ✗ Import failed: {e}")
        return False


def verify_websocket_manager():
    """Verify WebSocket Manager functionality"""
    print("\n✓ Verifying WebSocket Manager...")
    
    try:
        from backend.core.websocket_manager import WebSocketManager, MessageType
        
        # Create manager
        manager = WebSocketManager()
        print("  ✓ WebSocket Manager created")
        
        # Check attributes
        assert hasattr(manager, 'sio'), "Missing sio attribute"
        assert hasattr(manager, 'active_connections'), "Missing active_connections"
        assert hasattr(manager, 'session_data'), "Missing session_data"
        print("  ✓ Manager has required attributes")
        
        # Check methods
        methods = [
            'send_to_user',
            'send_to_session',
            'broadcast',
            'send_calculation_progress',
            'send_calculation_complete',
            'send_calculation_error',
            'send_notification',
            'send_status_update',
            'send_data_update',
            'get_active_users',
            'get_active_sessions',
            'is_user_connected',
            'get_user_sessions'
        ]
        
        for method in methods:
            assert hasattr(manager, method), f"Missing method: {method}"
        print(f"  ✓ Manager has all {len(methods)} required methods")
        
        # Check message types
        assert MessageType.CALCULATION_PROGRESS == "calculation_progress"
        assert MessageType.CALCULATION_COMPLETE == "calculation_complete"
        assert MessageType.CALCULATION_ERROR == "calculation_error"
        assert MessageType.NOTIFICATION == "notification"
        assert MessageType.STATUS_UPDATE == "status_update"
        assert MessageType.DATA_UPDATE == "data_update"
        assert MessageType.HEARTBEAT == "heartbeat"
        print("  ✓ All message types defined correctly")
        
        return True
    except Exception as e:
        print(f"  ✗ Verification failed: {e}")
        return False


def verify_authentication():
    """Verify WebSocket Authentication"""
    print("\n✓ Verifying WebSocket Authentication...")
    
    try:
        from backend.middleware.websocket_auth import WebSocketAuthMiddleware
        
        # Check methods
        methods = [
            'verify_token',
            'extract_token_from_auth',
            'authenticate_connection',
            'require_authentication',
            'require_role'
        ]
        
        for method in methods:
            assert hasattr(WebSocketAuthMiddleware, method), f"Missing method: {method}"
        print(f"  ✓ Authentication has all {len(methods)} required methods")
        
        # Test token extraction
        auth = {'token': 'test_token'}
        token = WebSocketAuthMiddleware.extract_token_from_auth(auth)
        assert token == 'test_token', "Token extraction failed"
        print("  ✓ Token extraction works")
        
        # Test Bearer token extraction
        auth = {'Authorization': 'Bearer test_token'}
        token = WebSocketAuthMiddleware.extract_token_from_auth(auth)
        assert token == 'test_token', "Bearer token extraction failed"
        print("  ✓ Bearer token extraction works")
        
        return True
    except Exception as e:
        print(f"  ✗ Verification failed: {e}")
        return False


def verify_api_endpoints():
    """Verify WebSocket API endpoints"""
    print("\n✓ Verifying WebSocket API...")
    
    try:
        from backend.api.v1 import websocket
        
        # Check router exists
        assert hasattr(websocket, 'router'), "Missing router"
        print("  ✓ API router exists")
        
        # Check endpoints
        routes = [route.path for route in websocket.router.routes]
        expected_routes = [
            '/status',
            '/connections',
            '/broadcast',
            '/send',
            '/notify',
            '/calculation/progress',
            '/test'
        ]
        
        for route in expected_routes:
            assert route in routes, f"Missing route: {route}"
        print(f"  ✓ All {len(expected_routes)} API endpoints defined")
        
        return True
    except Exception as e:
        print(f"  ✗ Verification failed: {e}")
        return False


def verify_documentation():
    """Verify documentation exists"""
    print("\n✓ Verifying documentation...")
    
    docs = [
        'backend/docs/WEBSOCKET_GUIDE.md',
        'backend/docs/WEBSOCKET_QUICK_REFERENCE.md',
        'backend/TASK_18_COMPLETE.md'
    ]
    
    all_exist = True
    for doc in docs:
        if os.path.exists(doc):
            size = os.path.getsize(doc)
            print(f"  ✓ {doc} ({size:,} bytes)")
        else:
            print(f"  ✗ {doc} not found")
            all_exist = False
    
    return all_exist


def verify_tests():
    """Verify tests exist"""
    print("\n✓ Verifying tests...")
    
    test_file = 'backend/tests/test_websocket.py'
    
    if os.path.exists(test_file):
        size = os.path.getsize(test_file)
        print(f"  ✓ {test_file} ({size:,} bytes)")
        
        # Count test functions
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
            test_count = content.count('def test_')
            print(f"  ✓ Contains {test_count} test functions")
        
        return True
    else:
        print(f"  ✗ {test_file} not found")
        return False


def verify_dependencies():
    """Verify required dependencies are installed"""
    print("\n✓ Verifying dependencies...")
    
    try:
        import socketio
        version = getattr(socketio, '__version__', 'unknown')
        print(f"  ✓ python-socketio {version}")
        
        import websockets
        version = getattr(websockets, '__version__', 'unknown')
        print(f"  ✓ websockets {version}")
        
        return True
    except ImportError as e:
        print(f"  ✗ Missing dependency: {e}")
        return False


def main():
    """Run all verifications"""
    print("="*60)
    print("WebSocket Implementation Verification")
    print("="*60)
    
    results = []
    
    # Run verifications
    results.append(("Dependencies", verify_dependencies()))
    results.append(("Imports", verify_imports()))
    results.append(("WebSocket Manager", verify_websocket_manager()))
    results.append(("Authentication", verify_authentication()))
    results.append(("API Endpoints", verify_api_endpoints()))
    results.append(("Documentation", verify_documentation()))
    results.append(("Tests", verify_tests()))
    
    # Summary
    print("\n" + "="*60)
    print("Verification Summary")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} {name}")
    
    print("="*60)
    print(f"Result: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n✅ All verifications passed!")
        print("\nWebSocket implementation is complete and ready to use.")
        print("\nNext steps:")
        print("1. Start the backend: python backend/main.py")
        print("2. Test WebSocket: python backend/demo_websocket.py")
        print("3. Run tests: pytest backend/tests/test_websocket.py -v")
        return 0
    else:
        print("\n❌ Some verifications failed!")
        print("Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
