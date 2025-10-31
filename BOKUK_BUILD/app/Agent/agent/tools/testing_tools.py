"""
Testing Tools for KAI Agent
============================

Provides automated testing capabilities using pytest in Docker sandbox.
Enables Test-Driven Development (TDD) workflow.

Requirements: 8.1, 8.2, 8.3, 8.4, 8.5
"""

import re
import time
from typing import Dict, List, Any
from langchain_core.tools import tool
from agent.tools.execution_tools import run_terminal_command_in_sandbox

# Import logging utilities
from agent.logging_config import get_logger, log_tool_execution

# Get logger for this module
logger = get_logger(__name__)


def parse_pytest_output(output: str) -> Dict[str, Any]:
    """
    Parse pytest output to extract test results.

    Args:
        output: Raw pytest output string

    Returns:
        Dictionary containing:
            - total_tests: Total number of tests
            - passed: Number of passed tests
            - failed: Number of failed tests
            - errors: Number of errors
            - skipped: Number of skipped tests
            - duration: Test execution duration
            - failures: List of failure details
            - summary: Formatted summary string

    Requirements: 8.2, 8.3
    """
    result = {
        'total_tests': 0,
        'passed': 0,
        'failed': 0,
        'errors': 0,
        'skipped': 0,
        'duration': '0s',
        'failures': [],
        'summary': ''
    }

    try:
        # Extract summary line (e.g., "5 passed, 2 failed in 1.23s")
        pattern = (
            r'=+\s*(\d+)\s+passed(?:,\s*(\d+)\s+failed)?'
            r'(?:,\s*(\d+)\s+error)?(?:,\s*(\d+)\s+skipped)?'
            r'\s+in\s+([\d.]+s)\s*=+'
        )
        summary_match = re.search(pattern, output)

        if summary_match:
            result['passed'] = int(summary_match.group(1))
            result['failed'] = int(summary_match.group(2) or 0)
            result['errors'] = int(summary_match.group(3) or 0)
            result['skipped'] = int(summary_match.group(4) or 0)
            result['duration'] = summary_match.group(5)
            total = (result['passed'] + result['failed'] +
                     result['errors'] + result['skipped'])
            result['total_tests'] = total

        # Extract failure details
        result['failures'] = extract_failure_details(output)

        # Generate summary
        result['summary'] = generate_test_summary(result)

    except Exception as e:
        logger.warning(f"Error parsing pytest output: {e}")
        result['summary'] = "Could not parse test results"

    return result


def extract_failure_details(output: str) -> List[Dict[str, str]]:
    """
    Extract detailed information about test failures.

    Args:
        output: Raw pytest output string

    Returns:
        List of dictionaries containing failure details:
            - test_name: Name of the failed test
            - file: File containing the test
            - error_type: Type of error (e.g., AssertionError)
            - error_message: Error message
            - traceback: Relevant traceback snippet

    Requirements: 8.3, 8.4
    """
    failures = []

    try:
        # Pattern to match FAILED lines
        pattern = (
            r'FAILED\s+([\w/.]+)::([\w_]+)\s*-\s*([\w]+):\s*'
            r'(.+?)(?=\n|$)'
        )

        for match in re.finditer(pattern, output):
            file_path = match.group(1)
            test_name = match.group(2)
            error_type = match.group(3)
            error_message = match.group(4).strip()

            # Try to extract traceback
            traceback = ""
            tb_pattern = (
                rf'{re.escape(test_name)}.*?\n(.*?)(?=FAILED|=+|$)'
            )
            traceback_match = re.search(tb_pattern, output, re.DOTALL)
            if traceback_match:
                # Limit length
                traceback = traceback_match.group(1).strip()[:200]

            failures.append({
                'test_name': test_name,
                'file': file_path,
                'error_type': error_type,
                'error_message': error_message,
                'traceback': traceback
            })

    except Exception as e:
        logger.warning(f"Error extracting failure details: {e}")

    return failures


def generate_test_summary(result: Dict[str, Any]) -> str:
    """
    Generate a formatted summary of test results.

    Args:
        result: Parsed test result dictionary

    Returns:
        Formatted summary string

    Requirements: 8.2
    """
    summary_lines = [
        "=" * 60,
        "TEST RESULTS SUMMARY",
        "=" * 60,
        f"Total Tests: {result['total_tests']}",
        f"✓ Passed: {result['passed']}",
        f"✗ Failed: {result['failed']}",
    ]

    if result['errors'] > 0:
        summary_lines.append(f"⚠ Errors: {result['errors']}")

    if result['skipped'] > 0:
        summary_lines.append(f"⊘ Skipped: {result['skipped']}")

    summary_lines.append(f"Duration: {result['duration']}")
    summary_lines.append("=" * 60)

    # Add failure details if any
    if result['failures']:
        summary_lines.append("\nFAILURE DETAILS:")
        summary_lines.append("-" * 60)
        for i, failure in enumerate(result['failures'], 1):
            test_name = failure['test_name']
            file_name = failure['file']
            summary_lines.append(f"\n{i}. {test_name} ({file_name})")
            error_type = failure['error_type']
            error_msg = failure['error_message']
            summary_lines.append(f"   Error: {error_type}: {error_msg}")
            if failure.get('traceback'):
                tb = failure['traceback'][:100]
                summary_lines.append(f"   Traceback: {tb}...")

    return "\n".join(summary_lines)


def analyze_test_failures(failures: List[Dict[str, str]]) -> str:
    """
    Analyze test failures and provide debugging suggestions.

    Args:
        failures: List of failure dictionaries

    Returns:
        Analysis and suggestions for fixing failures

    Requirements: 8.4, 8.5
    """
    if not failures:
        return "No failures to analyze."

    analysis_lines = [
        "=" * 60,
        "TEST FAILURE ANALYSIS",
        "=" * 60,
        f"\nFound {len(failures)} failing test(s):\n"
    ]

    for i, failure in enumerate(failures, 1):
        analysis_lines.append(f"{i}. {failure['test_name']}")
        analysis_lines.append(f"   File: {failure['file']}")
        analysis_lines.append(f"   Error Type: {failure['error_type']}")
        analysis_lines.append(f"   Message: {failure['error_message']}\n")

        # Provide specific suggestions based on error type
        error_type = failure['error_type']
        suggestions = []

        if error_type == 'AssertionError':
            suggestions.append(
                "- Check if the expected value matches the actual output"
            )
            suggestions.append(
                "- Verify the logic in the function being tested"
            )
            suggestions.append(
                "- Add debug prints to see intermediate values"
            )

        elif error_type == 'KeyError':
            suggestions.append("- Verify the key exists in the dictionary")
            suggestions.append("- Use .get() method with a default value")
            suggestions.append(
                "- Check if the dictionary is properly initialized"
            )

        elif error_type == 'AttributeError':
            suggestions.append(
                "- Check if the object has the expected attribute"
            )
            suggestions.append(
                "- Verify the object is properly initialized"
            )
            suggestions.append("- Check for None values")

        elif error_type == 'TypeError':
            suggestions.append(
                "- Check the types of arguments being passed"
            )
            suggestions.append(
                "- Verify function signatures match the calls"
            )
            suggestions.append(
                "- Check for None values where objects are expected"
            )

        elif error_type == 'ValueError':
            suggestions.append(
                "- Verify input values are in the expected range"
            )
            suggestions.append(
                "- Check for invalid conversions (e.g., string to int)"
            )
            suggestions.append("- Validate input data before processing")

        elif error_type in ['ImportError', 'ModuleNotFoundError']:
            suggestions.append("- Verify the module is installed")
            suggestions.append("- Check the import path is correct")
            suggestions.append(
                "- Ensure dependencies are in requirements.txt"
            )

        else:
            suggestions.append("- Review the error message carefully")
            suggestions.append("- Check the test logic and implementation")
            suggestions.append("- Add logging to understand the failure")

        if suggestions:
            analysis_lines.append("   Suggestions:")
            analysis_lines.extend([f"   {s}" for s in suggestions])
            analysis_lines.append("")

    analysis_lines.append("=" * 60)
    analysis_lines.append("\nDEBUGGING WORKFLOW:")
    analysis_lines.append("1. Read the error message carefully")
    analysis_lines.append("2. Examine the test code and implementation")
    analysis_lines.append("3. Form a hypothesis about the cause")
    analysis_lines.append("4. Make targeted changes to fix the issue")
    analysis_lines.append("5. Re-run tests to verify the fix")
    analysis_lines.append("=" * 60)

    return "\n".join(analysis_lines)


@tool
def execute_pytest_in_sandbox() -> str:
    """
    Execute pytest in the secure Docker sandbox to validate tests.

    This tool runs pytest with verbose output in an isolated container,
    collecting results from stdout and stderr. It's designed for
    Test-Driven Development (TDD) workflows.

    Returns:
        Test results with pass/fail status and detailed output

    Process:
        1. Execute 'pytest -v' in sandbox
        2. Capture output
        3. Parse results
        4. Return formatted summary

    Requirements: 8.1, 8.2, 8.3, 8.4, 8.5

    Example:
        >>> execute_pytest_in_sandbox()
        "--- STDOUT ---\\ntest_example.py::test_function PASSED\\n..."

    Security Notes:
        - Runs in isolated Docker container
        - Unprivileged user execution
        - Automatic cleanup after execution
    """
    start_time = time.time()
    logger.info("Starting pytest execution in sandbox")

    print("--- RUNNING PYTEST IN SANDBOX ---")

    try:
        # Execute pytest in sandbox with verbose output
        result = run_terminal_command_in_sandbox("pytest -v")

        duration = time.time() - start_time

        # Parse the output
        parsed_result = parse_pytest_output(result)

        # Check if tests passed or failed
        success = (parsed_result['failed'] == 0 and
                   parsed_result['errors'] == 0)

        if success:
            passed = parsed_result['passed']
            logger.info(
                f"Pytest execution completed successfully in "
                f"{duration:.2f}s - {passed} tests passed"
            )
        else:
            failed = parsed_result['failed']
            errors = parsed_result['errors']
            logger.warning(
                f"Pytest execution completed with failures in "
                f"{duration:.2f}s - {failed} failed, {errors} errors"
            )

        # Log tool execution
        log_tool_execution(
            logger,
            tool_name="execute_pytest_in_sandbox",
            input_summary="pytest -v",
            success=success,
            duration=duration
        )

        # Build comprehensive output
        output_lines = [
            "=" * 60,
            "PYTEST EXECUTION RESULTS",
            "=" * 60,
            "",
            "RAW OUTPUT:",
            "-" * 60,
            result,
            "",
            parsed_result['summary']
        ]

        # Add failure analysis if there are failures
        if parsed_result['failures']:
            output_lines.append("\n")
            output_lines.append(
                analyze_test_failures(parsed_result['failures'])
            )

        return "\n".join(output_lines)

    except Exception as e:
        duration = time.time() - start_time
        error_msg = f"Pytest execution failed: {str(e)}"
        logger.error(error_msg, exc_info=True)

        # Log failed tool execution
        log_tool_execution(
            logger,
            tool_name="execute_pytest_in_sandbox",
            input_summary="pytest -v",
            success=False,
            duration=duration,
            error=str(e)
        )

        return f"Fehler beim Ausführen von pytest: {e}"
