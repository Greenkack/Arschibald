"""
Documentation Verification Script
==================================

This script verifies that all modules, classes, and functions
in the KAI Agent system have proper documentation.

Usage:
    python verify_documentation.py
"""

import inspect
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def check_docstring(obj, name: str) -> bool:
    """
    Check if an object has a docstring.

    Args:
        obj: Object to check
        name: Name of the object

    Returns:
        True if docstring exists and is not empty
    """
    doc = inspect.getdoc(obj)
    if doc and len(doc.strip()) > 10:
        return True
    print(f"  ❌ Missing docstring: {name}")
    return False


def check_type_hints(func, name: str) -> bool:
    """
    Check if a function has type hints.

    Args:
        func: Function to check
        name: Name of the function

    Returns:
        True if function has type hints
    """
    sig = inspect.signature(func)
    has_hints = False

    # Check parameters
    for param_name, param in sig.parameters.items():
        if param_name != 'self' and param.annotation != inspect.Parameter.empty:
            has_hints = True
            break

    # Check return type
    if sig.return_annotation != inspect.Signature.empty:
        has_hints = True

    if not has_hints:
        print(f"  ⚠️  Missing type hints: {name}")

    return has_hints


def verify_module(module_name: str) -> dict:
    """
    Verify documentation for a module.

    Args:
        module_name: Name of module to verify

    Returns:
        Dictionary with verification results
    """
    print(f"\n{'=' * 60}")
    print(f"Verifying: {module_name}")
    print('=' * 60)

    try:
        module = __import__(module_name, fromlist=[''])
    except ImportError as e:
        print(f"❌ Failed to import: {e}")
        return {'success': False, 'error': str(e)}

    results = {
        'module': module_name,
        'module_doc': False,
        'functions': 0,
        'functions_documented': 0,
        'functions_typed': 0,
        'classes': 0,
        'classes_documented': 0,
    }

    # Check module docstring
    if check_docstring(module, module_name):
        results['module_doc'] = True
        print("✅ Module docstring: Present")
        print(f"\n{inspect.getdoc(module)[:200]}...\n")

    # Check functions and classes
    for name, obj in inspect.getmembers(module):
        # Skip private and imported items
        if name.startswith('_') or inspect.getmodule(obj) != module:
            continue

        if inspect.isfunction(obj):
            results['functions'] += 1
            if check_docstring(obj, f"{module_name}.{name}"):
                results['functions_documented'] += 1
            if check_type_hints(obj, f"{module_name}.{name}"):
                results['functions_typed'] += 1

        elif inspect.isclass(obj):
            results['classes'] += 1
            if check_docstring(obj, f"{module_name}.{name}"):
                results['classes_documented'] += 1

            # Check class methods
            for method_name, method in inspect.getmembers(obj):
                if (method_name.startswith('_') and
                        method_name not in ['__init__']):
                    continue
                if inspect.isfunction(method) or inspect.ismethod(method):
                    results['functions'] += 1
                    if check_docstring(
                        method,
                        f"{module_name}.{name}.{method_name}"
                    ):
                        results['functions_documented'] += 1
                    if check_type_hints(
                        method,
                        f"{module_name}.{name}.{method_name}"
                    ):
                        results['functions_typed'] += 1

    # Print summary
    print("\n📊 Summary:")
    print(f"  Functions: {results['functions']}")
    print(f"  Functions documented: {results['functions_documented']}")
    print(f"  Functions with type hints: {results['functions_typed']}")
    print(f"  Classes: {results['classes']}")
    print(f"  Classes documented: {results['classes_documented']}")

    # Calculate percentages
    if results['functions'] > 0:
        doc_pct = (results['functions_documented'] /
                   results['functions'] * 100)
        type_pct = (results['functions_typed'] /
                    results['functions'] * 100)
        print(f"  Documentation coverage: {doc_pct:.1f}%")
        print(f"  Type hint coverage: {type_pct:.1f}%")

    results['success'] = True
    return results


def main():
    """Main verification function."""
    print("=" * 60)
    print("KAI Agent Documentation Verification")
    print("=" * 60)

    # Modules to verify
    modules = [
        'config',
        'agent_ui',
        'agent.agent_core',
        'agent.errors',
        'agent.logging_config',
        'agent.security',
        'agent.tools.knowledge_tools',
        'agent.tools.coding_tools',
        'agent.tools.execution_tools',
        'agent.tools.telephony_tools',
        'agent.tools.call_protocol',
        'agent.tools.search_tools',
        'agent.tools.testing_tools',
    ]

    all_results = []

    for module_name in modules:
        result = verify_module(module_name)
        if result.get('success'):
            all_results.append(result)

    # Overall summary
    print(f"\n{'=' * 60}")
    print("OVERALL SUMMARY")
    print('=' * 60)

    total_functions = sum(r['functions'] for r in all_results)
    total_documented = sum(r['functions_documented'] for r in all_results)
    total_typed = sum(r['functions_typed'] for r in all_results)
    total_classes = sum(r['classes'] for r in all_results)
    total_classes_doc = sum(r['classes_documented'] for r in all_results)

    print(f"\nModules verified: {len(all_results)}")
    print(f"Total functions: {total_functions}")
    print(f"Functions documented: {total_documented}")
    print(f"Functions with type hints: {total_typed}")
    print(f"Total classes: {total_classes}")
    print(f"Classes documented: {total_classes_doc}")

    if total_functions > 0:
        doc_pct = total_documented / total_functions * 100
        type_pct = total_typed / total_functions * 100
        print(f"\n📈 Overall documentation coverage: {doc_pct:.1f}%")
        print(f"📈 Overall type hint coverage: {type_pct:.1f}%")

    if total_classes > 0:
        class_pct = total_classes_doc / total_classes * 100
        print(f"📈 Class documentation coverage: {class_pct:.1f}%")

    # Final verdict
    print(f"\n{'=' * 60}")
    if (total_documented == total_functions and
            total_classes_doc == total_classes):
        print("✅ ALL CODE IS FULLY DOCUMENTED!")
    else:
        print("⚠️  Some documentation is missing. See details above.")
    print('=' * 60)


if __name__ == "__main__":
    main()
