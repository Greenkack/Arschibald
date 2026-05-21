"""
Verification Script for Task 3: Database Setup and Configuration

Verifies that all components of the database setup are correctly implemented.
This script checks file existence, imports, and basic functionality.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

def check_file_exists(filepath: str) -> bool:
    """Check if a file exists"""
    # Remove 'backend/' prefix if running from backend directory
    if filepath.startswith('backend/'):
        filepath = filepath[8:]
    path = Path(filepath)
    exists = path.exists()
    status = "✓" if exists else "✗"
    print(f"  {status} {filepath}")
    return exists

def check_import(module_path: str, items: list) -> bool:
    """Check if imports work"""
    try:
        module = __import__(module_path, fromlist=items)
        for item in items:
            if not hasattr(module, item):
                print(f"  ✗ {module_path}.{item} - Not found")
                return False
        print(f"  ✓ {module_path} - All imports successful")
        return True
    except Exception as e:
        print(f"  ✗ {module_path} - Import failed: {e}")
        return False

def main():
    print("\n" + "="*80)
    print("TASK 3: DATABASE SETUP AND CONFIGURATION - VERIFICATION")
    print("="*80)
    
    all_checks_passed = True
    
    # Check 1: Core Files
    print("\n1. Checking Core Files...")
    files_to_check = [
        "backend/core/database.py",
        "backend/core/dependencies.py",
        "backend/core/config.py",
        "backend/alembic.ini",
        "backend/alembic/env.py",
        "backend/alembic/script.py.mako",
        "backend/alembic/README",
    ]
    for filepath in files_to_check:
        if not check_file_exists(filepath):
            all_checks_passed = False
    
    # Check 2: Documentation Files
    print("\n2. Checking Documentation Files...")
    doc_files = [
        "backend/docs/DATABASE_SETUP_GUIDE.md",
        "backend/docs/DATABASE_QUICK_REFERENCE.md",
        "backend/TASK_3_COMPLETE.md",
    ]
    for filepath in doc_files:
        if not check_file_exists(filepath):
            all_checks_passed = False
    
    # Check 3: Test and Demo Files
    print("\n3. Checking Test and Demo Files...")
    test_files = [
        "backend/tests/test_database_setup.py",
        "backend/demo_database_setup.py",
    ]
    for filepath in test_files:
        if not check_file_exists(filepath):
            all_checks_passed = False
    
    # Check 4: Database Module Imports (Sync only, no async packages required)
    print("\n4. Checking Database Module Imports...")
    try:
        from backend.core.database import (
            engine,
            SessionLocal,
            get_db,
            Base,
            init_db,
            check_db_connection,
            get_db_stats,
            transaction,
        )
        print("  ✓ Sync database imports successful")
    except Exception as e:
        print(f"  ✗ Sync database imports failed: {e}")
        all_checks_passed = False
    
    # Check 5: Dependencies Module Imports
    print("\n5. Checking Dependencies Module Imports...")
    try:
        from backend.core.dependencies import (
            get_database_session,
            get_pagination_params,
            PaginationParams,
            BatchOperationContext,
        )
        print("  ✓ Dependencies imports successful")
    except Exception as e:
        print(f"  ✗ Dependencies imports failed: {e}")
        all_checks_passed = False
    
    # Check 6: Config Updates
    print("\n6. Checking Configuration Updates...")
    try:
        from backend.core.config import settings
        required_attrs = [
            'DATABASE_URL',
            'DATABASE_ECHO',
            'DATABASE_POOL_SIZE',
            'DATABASE_MAX_OVERFLOW',
            'DATABASE_POOL_TIMEOUT',
            'DATABASE_POOL_RECYCLE',
        ]
        missing = [attr for attr in required_attrs if not hasattr(settings, attr)]
        if missing:
            print(f"  ✗ Missing config attributes: {missing}")
            all_checks_passed = False
        else:
            print("  ✓ All database config attributes present")
    except Exception as e:
        print(f"  ✗ Config check failed: {e}")
        all_checks_passed = False
    
    # Check 7: Database Models
    print("\n7. Checking Database Models...")
    try:
        from backend.models.database_models import (
            User,
            Customer,
            Project,
            SolarCalculation,
            Product,
            Offer,
            Task,
        )
        print("  ✓ All database models imported successfully")
    except Exception as e:
        print(f"  ✗ Model imports failed: {e}")
        all_checks_passed = False
    
    # Check 8: Basic Functionality
    print("\n8. Checking Basic Functionality...")
    try:
        from backend.core.database import engine, SessionLocal, Base
        
        # Check engine
        if engine is not None:
            print("  ✓ Database engine created")
        else:
            print("  ✗ Database engine is None")
            all_checks_passed = False
        
        # Check session factory
        if SessionLocal is not None:
            print("  ✓ Session factory created")
        else:
            print("  ✗ Session factory is None")
            all_checks_passed = False
        
        # Check Base
        if Base is not None and hasattr(Base, 'metadata'):
            print("  ✓ Base class created with metadata")
        else:
            print("  ✗ Base class invalid")
            all_checks_passed = False
        
        # Test connection
        if check_db_connection():
            print("  ✓ Database connection successful")
        else:
            print("  ✗ Database connection failed")
            all_checks_passed = False
        
        # Test session creation
        db = SessionLocal()
        db.close()
        print("  ✓ Session creation and closure successful")
        
    except Exception as e:
        print(f"  ✗ Functionality check failed: {e}")
        all_checks_passed = False
    
    # Check 9: Transaction Management
    print("\n9. Checking Transaction Management...")
    try:
        from backend.core.database import transaction, SessionLocal
        db = SessionLocal()
        try:
            with transaction(db) as tx:
                # Just test that the context manager works
                pass
            print("  ✓ Transaction context manager works")
        finally:
            db.close()
    except Exception as e:
        print(f"  ✗ Transaction management failed: {e}")
        all_checks_passed = False
    
    # Check 10: Pagination
    print("\n10. Checking Pagination...")
    try:
        from backend.core.dependencies import get_pagination_params, PaginationParams
        params = get_pagination_params(skip=10, limit=50)
        if isinstance(params, PaginationParams):
            print("  ✓ Pagination params created successfully")
            if params.skip == 10 and params.limit == 50:
                print("  ✓ Pagination params have correct values")
            else:
                print("  ✗ Pagination params have incorrect values")
                all_checks_passed = False
        else:
            print("  ✗ Pagination params type incorrect")
            all_checks_passed = False
    except Exception as e:
        print(f"  ✗ Pagination check failed: {e}")
        all_checks_passed = False
    
    # Check 11: Requirements File
    print("\n11. Checking Requirements File...")
    try:
        with open("requirements.txt", "r") as f:
            content = f.read()
            required_packages = ['aiosqlite', 'asyncpg', 'aiomysql', 'greenlet']
            missing = [pkg for pkg in required_packages if pkg not in content]
            if missing:
                print(f"  ⚠ Missing packages in requirements.txt: {missing}")
                print("  ℹ These packages need to be installed for async support")
            else:
                print("  ✓ All async database packages listed in requirements.txt")
    except Exception as e:
        print(f"  ✗ Requirements file check failed: {e}")
        all_checks_passed = False
    
    # Final Summary
    print("\n" + "="*80)
    if all_checks_passed:
        print("✅ ALL CHECKS PASSED - Task 3 Implementation Verified!")
        print("\nNext Steps:")
        print("  1. Install async packages: pip install aiosqlite asyncpg aiomysql greenlet")
        print("  2. Initialize database: python -c 'from backend.core.database import init_db; init_db()'")
        print("  3. Create migration: alembic revision --autogenerate -m 'Initial migration'")
        print("  4. Apply migration: alembic upgrade head")
        print("  5. Run tests: pytest backend/tests/test_database_setup.py -v")
        print("  6. Run demo: python backend/demo_database_setup.py")
    else:
        print("❌ SOME CHECKS FAILED - Please review the errors above")
    print("="*80 + "\n")
    
    return 0 if all_checks_passed else 1

if __name__ == "__main__":
    sys.exit(main())
