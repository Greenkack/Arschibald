"""
Complete Agent Integration Test Suite
======================================

This script runs all integration tests to verify that the agent
system is properly integrated into the main application.

Test Suites:
1. Isolation Tests (test_agent_isolation.py)
2. Dependency Tests (test_agent_dependencies.py)
"""

import sys
import subprocess
from datetime import datetime


def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(title.center(70))
    print("=" * 70 + "\n")


def run_test_suite(test_file, suite_name):
    """Run a test suite and return success status."""
    print_header(f"Running {suite_name}")

    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            timeout=60
        )

        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        print(f"❌ {suite_name} timed out after 60 seconds")
        return False

    except Exception as e:
        print(f"❌ Error running {suite_name}: {e}")
        return False


def main():
    """Run all integration tests."""
    print_header("COMPLETE AGENT INTEGRATION TEST SUITE")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Track results
    results = {}

    # Run isolation tests
    results['Isolation Tests'] = run_test_suite(
        'test_agent_isolation.py',
        'Isolation Tests'
    )

    # Run dependency tests
    results['Dependency Tests'] = run_test_suite(
        'test_agent_dependencies.py',
        'Dependency Tests'
    )

    # Print final summary
    print_header("FINAL INTEGRATION TEST SUMMARY")

    print("Test Suite Results:")
    print("-" * 70)

    total_suites = len(results)
    passed_suites = sum(1 for v in results.values() if v)

    for suite_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {suite_name:.<50} {status}")

    print("-" * 70)
    print(f"Total: {passed_suites}/{total_suites} test suites passed")
    print()

    # Overall result
    if passed_suites == total_suites:
        print("🎉 ALL INTEGRATION TESTS PASSED! 🎉")
        print()
        print("The KAI Agent system is successfully integrated into the")
        print("Bokuk2 application with proper isolation and dependency")
        print("management.")
        print()
        print("✅ No database conflicts")
        print("✅ State management separated")
        print("✅ No interference with existing features")
        print("✅ Error isolation validated")
        print("✅ All dependencies properly managed")
        print("✅ No version conflicts detected")
        print()
        print("The agent is ready to use!")
        print()
        print("To start the application:")
        print("  streamlit run gui.py")
        print()
        print("Then click 'A.G.E.N.T.' in the sidebar menu.")

        return 0
    else:
        print("❌ SOME INTEGRATION TESTS FAILED")
        print()
        print("Please review the test output above and fix the issues.")
        print()
        failed_suites = [
            name for name,
            passed in results.items() if not passed]
        print("Failed test suites:")
        for suite in failed_suites:
            print(f"  - {suite}")

        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        print_header(
            f"Test run completed: {
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n❌ Test run interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
