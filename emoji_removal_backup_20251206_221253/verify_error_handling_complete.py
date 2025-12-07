"""
Verification Script for Task 24: Error Handling und Robustheit

This script verifies that all components of the error handling system
are properly implemented and working.
"""

import sys
from pathlib import Path


def verify_files_exist():
    """Verify all required files exist"""
    print("=" * 70)
    print("VERIFYING FILE STRUCTURE")
    print("=" * 70)
    
    required_files = [
        "theming/theme_errors.py",
        "theming/error_handler.py",
        "theming/error_dashboard.py",
        "theming/ERROR_HANDLING_REFERENCE.md",
        "theming/ERROR_HANDLING_QUICK_START.md",
        "docs/ERROR_HANDLING_QUICK_REFERENCE.md",
        "demo_error_handling.py",
        "tests/test_error_handling.py",
        "TASK_24_ERROR_HANDLING_COMPLETE.md"
    ]
    
    all_exist = True
    for filepath in required_files:
        path = Path(filepath)
        exists = path.exists()
        status = "✅" if exists else "❌"
        print(f"{status} {filepath}")
        if not exists:
            all_exist = False
    
    print()
    return all_exist


def verify_imports():
    """Verify all imports work correctly"""
    print("=" * 70)
    print("VERIFYING IMPORTS")
    print("=" * 70)
    
    try:
        # Import exception hierarchy
        from theming.theme_errors import (
            ThemeError,
            ThemeLoadError,
            ThemeValidationError,
            ThemeNotFoundError,
            CSSGenerationError,
            CSSInjectionError,
            ComponentRenderError,
            TokenNotFoundError,
            ThemeFileError,
            ThemeCacheError,
            ThemeStateError
        )
        print("✅ Exception hierarchy imports")
        
        # Import error handler
        from theming.error_handler import (
            ErrorHandler,
            get_error_handler,
            set_error_handler
        )
        print("✅ Error handler imports")
        
        # Import dashboard (may fail if streamlit not available)
        try:
            from theming.error_dashboard import (
                render_error_dashboard,
                render_error_summary_widget,
                render_inline_error_notification,
                render_error_toast
            )
            print("✅ Error dashboard imports")
        except ImportError as e:
            print(f"⚠️  Error dashboard imports (Streamlit not available: {e})")
        
        # Import from main package
        from theming import (
            ThemeError as TE,
            ErrorHandler as EH,
            get_error_handler as geh
        )
        print("✅ Main package exports")
        
        print()
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print()
        return False


def verify_exception_hierarchy():
    """Verify exception hierarchy works correctly"""
    print("=" * 70)
    print("VERIFYING EXCEPTION HIERARCHY")
    print("=" * 70)
    
    from theming.theme_errors import (
        ThemeError,
        ThemeLoadError,
        ThemeValidationError,
        ComponentRenderError
    )
    
    try:
        # Test base exception
        error = ThemeError("Test error", details={'key': 'value'})
        assert error.message == "Test error"
        assert error.details == {'key': 'value'}
        print("✅ ThemeError base class")
        
        # Test ThemeLoadError
        error = ThemeLoadError("theme", "reason", details={'path': '/test'})
        assert error.theme_name == "theme"
        assert error.reason == "reason"
        assert "theme" in str(error)
        print("✅ ThemeLoadError")
        
        # Test ThemeValidationError
        error = ThemeValidationError("theme", ["error1", "error2"])
        assert error.theme_name == "theme"
        assert len(error.validation_errors) == 2
        print("✅ ThemeValidationError")
        
        # Test ComponentRenderError
        error = ComponentRenderError("Card", "Missing props")
        assert error.component_name == "Card"
        assert error.reason == "Missing props"
        print("✅ ComponentRenderError")
        
        # Test inheritance
        assert isinstance(ThemeLoadError("t", "r"), ThemeError)
        assert isinstance(ThemeLoadError("t", "r"), Exception)
        print("✅ Exception inheritance")
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ Exception hierarchy test failed: {e}")
        print()
        return False


def verify_error_handler():
    """Verify error handler functionality"""
    print("=" * 70)
    print("VERIFYING ERROR HANDLER")
    print("=" * 70)
    
    from theming.error_handler import ErrorHandler, get_error_handler
    from theming.theme_errors import ThemeLoadError
    
    try:
        # Test initialization
        handler = ErrorHandler()
        assert handler.error_count == 0
        assert len(handler.error_history) == 0
        print("✅ ErrorHandler initialization")
        
        # Test error handling
        error = ValueError("Test error")
        handler.handle_error(error, notify_user=False)
        assert handler.error_count == 1
        assert len(handler.error_history) == 1
        print("✅ Basic error handling")
        
        # Test fallback mechanism
        fallback_called = False
        def fallback():
            nonlocal fallback_called
            fallback_called = True
            return "fallback"
        
        error = ThemeLoadError("test", "reason")
        result = handler.handle_theme_load_error("test", error, fallback)
        assert fallback_called
        assert result == "fallback"
        print("✅ Fallback mechanism")
        
        # Test automatic recovery
        call_count = 0
        def recovery():
            nonlocal call_count
            call_count += 1
            return "recovered"
        
        result = handler._attempt_recovery("test_op", recovery)
        assert result == "recovered"
        assert call_count == 1
        print("✅ Automatic recovery")
        
        # Test error report
        report = handler.get_error_report()
        assert 'total_errors' in report
        assert 'error_types' in report
        assert 'recent_errors' in report
        print("✅ Error reporting")
        
        # Test global handler
        global_handler = get_error_handler()
        assert global_handler is not None
        print("✅ Global error handler")
        
        # Test history limit
        handler.max_history_size = 5
        for i in range(10):
            handler.handle_error(ValueError(f"Error {i}"), notify_user=False)
        assert len(handler.error_history) == 5
        print("✅ History size limit")
        
        # Test clear history
        handler.clear_history()
        assert len(handler.error_history) == 0
        print("✅ Clear history")
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ Error handler test failed: {e}")
        import traceback
        traceback.print_exc()
        print()
        return False


def verify_documentation():
    """Verify documentation exists and is complete"""
    print("=" * 70)
    print("VERIFYING DOCUMENTATION")
    print("=" * 70)
    
    docs = {
        "theming/ERROR_HANDLING_REFERENCE.md": [
            "Exception Hierarchy",
            "Error Handler",
            "Error Dashboard",
            "Integration Examples",
            "Best Practices"
        ],
        "docs/ERROR_HANDLING_QUICK_REFERENCE.md": [
            "Quick Start",
            "Common Patterns",
            "Exception Types"
        ],
        "theming/ERROR_HANDLING_QUICK_START.md": [
            "Installation",
            "Basic Usage",
            "Common Patterns"
        ]
    }
    
    all_complete = True
    for doc_path, required_sections in docs.items():
        path = Path(doc_path)
        if not path.exists():
            print(f"❌ {doc_path} not found")
            all_complete = False
            continue
        
        content = path.read_text(encoding='utf-8')
        missing_sections = []
        
        for section in required_sections:
            if section.lower() not in content.lower():
                missing_sections.append(section)
        
        if missing_sections:
            print(f"⚠️  {doc_path} missing sections: {', '.join(missing_sections)}")
            all_complete = False
        else:
            print(f"✅ {doc_path}")
    
    print()
    return all_complete


def verify_tests():
    """Verify tests exist and can be imported"""
    print("=" * 70)
    print("VERIFYING TESTS")
    print("=" * 70)
    
    try:
        # Check if test file exists
        test_file = Path("tests/test_error_handling.py")
        if not test_file.exists():
            print("❌ Test file not found")
            return False
        
        print("✅ Test file exists")
        
        # Try to import test module
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        
        try:
            from tests import test_error_handling
            print("✅ Test module imports")
        except ImportError:
            # Alternative import method
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "test_error_handling",
                test_file
            )
            test_error_handling = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(test_error_handling)
            print("✅ Test module imports (alternative method)")
        
        # Count test classes and methods
        import inspect
        test_classes = []
        test_methods = 0
        
        for name, obj in inspect.getmembers(test_error_handling):
            if inspect.isclass(obj) and name.startswith('Test'):
                test_classes.append(name)
                for method_name, method in inspect.getmembers(obj):
                    if method_name.startswith('test_'):
                        test_methods += 1
        
        print(f"✅ Found {len(test_classes)} test classes")
        print(f"✅ Found {test_methods} test methods")
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ Test verification failed: {e}")
        print()
        return False


def main():
    """Run all verifications"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 10 + "TASK 24: ERROR HANDLING VERIFICATION" + " " * 21 + "║")
    print("╚" + "=" * 68 + "╝")
    print()
    
    results = {
        "File Structure": verify_files_exist(),
        "Imports": verify_imports(),
        "Exception Hierarchy": verify_exception_hierarchy(),
        "Error Handler": verify_error_handler(),
        "Documentation": verify_documentation(),
        "Tests": verify_tests()
    }
    
    # Summary
    print("=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    
    for category, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {category}")
    
    print()
    
    all_passed = all(results.values())
    
    if all_passed:
        print("╔" + "=" * 68 + "╗")
        print("║" + " " * 15 + "✅ ALL VERIFICATIONS PASSED ✅" + " " * 22 + "║")
        print("║" + " " * 68 + "║")
        print("║" + " " * 10 + "Task 24 is COMPLETE and ready for use!" + " " * 17 + "║")
        print("╚" + "=" * 68 + "╝")
        return 0
    else:
        print("╔" + "=" * 68 + "╗")
        print("║" + " " * 15 + "❌ SOME VERIFICATIONS FAILED ❌" + " " * 19 + "║")
        print("║" + " " * 68 + "║")
        print("║" + " " * 10 + "Please review the errors above." + " " * 26 + "║")
        print("╚" + "=" * 68 + "╝")
        return 1


if __name__ == "__main__":
    sys.exit(main())
