"""
Test script for pytest execution tools.

This script tests the testing tools without requiring the full agent setup.
"""

from agent.tools.testing_tools import (
    analyze_test_failures,
    extract_failure_details,
    generate_test_summary,
    parse_pytest_output,
)
import os
import sys

# Add Agent directory to path
sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(
            os.path.abspath(__file__)),
        'agent'))


def test_parse_pytest_output():
    """Test parsing of pytest output."""
    print("=" * 60)
    print("Test 1: Parse pytest output")
    print("=" * 60)

    sample_output = """
============================= test session starts ==============================
collected 5 items

test_example.py::test_addition PASSED                                    [ 20%]
test_example.py::test_subtraction PASSED                                 [ 40%]
test_example.py::test_multiplication FAILED                              [ 60%]
test_example.py::test_division PASSED                                    [ 80%]
test_example.py::test_modulo PASSED                                      [100%]

=================================== FAILURES ===================================
FAILED test_example.py::test_multiplication - AssertionError: assert 6 == 5
========================= 4 passed, 1 failed in 0.12s ==========================
"""

    result = parse_pytest_output(sample_output)

    print(f"Total tests: {result['total_tests']}")
    print(f"Passed: {result['passed']}")
    print(f"Failed: {result['failed']}")
    print(f"Duration: {result['duration']}")
    print(f"Number of failures: {len(result['failures'])}")
    print(f"\nSummary:\n{result['summary']}")
    print()


def test_extract_failure_details():
    """Test extraction of failure details."""
    print("=" * 60)
    print("Test 2: Extract failure details")
    print("=" * 60)

    sample_output = """
FAILED test_example.py::test_multiplication - AssertionError: assert 6 == 5
    def test_multiplication():
        result = multiply(2, 3)
>       assert result == 5
E       AssertionError: assert 6 == 5

FAILED test_example.py::test_division - ZeroDivisionError: division by zero
"""

    failures = extract_failure_details(sample_output)

    print(f"Found {len(failures)} failures:")
    for i, failure in enumerate(failures, 1):
        print(f"\n{i}. {failure['test_name']}")
        print(f"   File: {failure['file']}")
        print(f"   Error Type: {failure['error_type']}")
        print(f"   Error Message: {failure['error_message']}")
    print()


def test_analyze_test_failures():
    """Test failure analysis."""
    print("=" * 60)
    print("Test 3: Analyze test failures")
    print("=" * 60)

    failures = [
        {
            'test_name': 'test_addition',
            'file': 'test_math.py',
            'error_type': 'AssertionError',
            'error_message': 'assert 5 == 6',
            'traceback': 'assert result == 6'
        },
        {
            'test_name': 'test_get_value',
            'file': 'test_dict.py',
            'error_type': 'KeyError',
            'error_message': "'missing_key'",
            'traceback': "data['missing_key']"
        }
    ]

    analysis = analyze_test_failures(failures)
    print(analysis)
    print()


def test_execute_pytest_simple():
    """Test simple pytest execution."""
    print("=" * 60)
    print("Test 4: Execute pytest (simple)")
    print("=" * 60)

    # Create a simple test file in the sandbox
    test_code = """
def test_simple_pass():
    assert 1 + 1 == 2

def test_simple_fail():
    assert 1 + 1 == 3
"""

    print("This test would execute pytest in the Docker sandbox.")
    print("Skipping actual execution to avoid Docker dependency in this test.")
    print("To test fully, ensure Docker is running and execute:")
    print(
        "  result = execute_pytest_in_sandbox.invoke({'path': 'test_file.py'})")
    print()


def test_generate_test_summary():
    """Test summary generation."""
    print("=" * 60)
    print("Test 5: Generate test summary")
    print("=" * 60)

    result = {
        'total_tests': 10,
        'passed': 7,
        'failed': 2,
        'errors': 0,
        'skipped': 1,
        'duration': '1.23s',
        'failures': [
            {
                'test_name': 'test_example',
                'file': 'test_file.py',
                'error_type': 'AssertionError',
                'error_message': 'Expected 5, got 6',
                'traceback': 'assert result == 5'
            }
        ]
    }

    summary = generate_test_summary(result)
    print(summary)
    print()


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Testing Tools Test Suite")
    print("=" * 60 + "\n")

    try:
        test_parse_pytest_output()
        test_extract_failure_details()
        test_analyze_test_failures()
        test_generate_test_summary()
        test_execute_pytest_simple()

        print("=" * 60)
        print("All tests completed successfully!")
        print("=" * 60)
        print("\nNote: Full integration test with Docker requires:")
        print("1. Docker running")
        print("2. kai_agent-sandbox image built")
        print("3. Test files in the sandbox workspace")

    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
