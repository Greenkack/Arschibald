"""
Final Validation Test Runner for KAI Agent Integration

This script runs all validation tests:
- End-to-end testing (Task 19.1)
- Performance testing (Task 19.2)
- Security audit (Task 19.3)

And generates a comprehensive validation report.
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def run_test_suite(test_file, suite_name):
    """Run a test suite and return results"""
    print_header(f"Running {suite_name}")

    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)

        return {
            "suite": suite_name,
            "passed": result.returncode == 0,
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except subprocess.TimeoutExpired:
        print(f"⚠ {suite_name} timed out after 5 minutes")
        return {
            "suite": suite_name,
            "passed": False,
            "return_code": -1,
            "error": "Timeout after 5 minutes"
        }
    except Exception as e:
        print(f"✗ Error running {suite_name}: {e}")
        return {
            "suite": suite_name,
            "passed": False,
            "return_code": -1,
            "error": str(e)
        }


def generate_validation_report(results):
    """Generate comprehensive validation report"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "test_run": "KAI Agent Final Validation",
        "results": results,
        "summary": {
            "total_suites": len(results),
            "passed_suites": sum(
                1 for r in results if r["passed"]),
            "failed_suites": sum(
                1 for r in results if not r["passed"]),
            "overall_status": "PASSED" if all(
                r["passed"] for r in results) else "FAILED"}}

    return report


def print_summary(report):
    """Print validation summary"""
    print_header("VALIDATION SUMMARY")

    summary = report["summary"]

    print(f"Total Test Suites: {summary['total_suites']}")
    print(f"Passed: {summary['passed_suites']}")
    print(f"Failed: {summary['failed_suites']}")
    print(f"\nOverall Status: {summary['overall_status']}")

    print("\nDetailed Results:")
    print("-" * 80)

    for result in report["results"]:
        status = "✓ PASSED" if result["passed"] else "✗ FAILED"
        print(f"{status:12} - {result['suite']}")

    print("-" * 80)


def main():
    """Run all validation tests"""
    print_header("KAI AGENT - FINAL VALIDATION TEST SUITE")
    print("Task 19: Final testing and validation")
    print("  - Task 19.1: End-to-end testing")
    print("  - Task 19.2: Performance testing")
    print("  - Task 19.3: Security audit")

    agent_dir = Path(__file__).parent

    # Define test suites
    test_suites = [
        {
            "file": agent_dir / "test_end_to_end.py",
            "name": "End-to-End Testing (Task 19.1)"
        },
        {
            "file": agent_dir / "test_performance.py",
            "name": "Performance Testing (Task 19.2)"
        },
        {
            "file": agent_dir / "test_security_audit.py",
            "name": "Security Audit (Task 19.3)"
        }
    ]

    # Run all test suites
    results = []
    for suite in test_suites:
        if not suite["file"].exists():
            print(f"⚠ Warning: Test file not found: {suite['file']}")
            results.append({
                "suite": suite["name"],
                "passed": False,
                "error": "Test file not found"
            })
            continue

        result = run_test_suite(suite["file"], suite["name"])
        results.append(result)

    # Generate report
    report = generate_validation_report(results)

    # Save report to file
    report_file = agent_dir / "final_validation_report.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n✓ Detailed report saved to: {report_file}")

    # Print summary
    print_summary(report)

    # Additional checks
    print_header("ADDITIONAL VALIDATION CHECKS")

    # Check documentation
    docs_to_check = [
        agent_dir / "README.md",
        agent_dir / "TROUBLESHOOTING.md",
        agent_dir / "DEPLOYMENT_GUIDE.md",
        agent_dir.parent / ".env.example"
    ]

    print("Documentation Check:")
    for doc in docs_to_check:
        if doc.exists():
            print(f"  ✓ {doc.name}")
        else:
            print(f"  ✗ {doc.name} - MISSING")

    # Check required directories
    required_dirs = [
        agent_dir / "agent",
        agent_dir / "agent" / "tools",
        agent_dir / "knowledge_base",
        agent_dir / "agent_workspace",
        agent_dir / "sandbox"
    ]

    print("\nDirectory Structure Check:")
    for dir_path in required_dirs:
        if dir_path.exists():
            print(f"  ✓ {dir_path.relative_to(agent_dir)}")
        else:
            print(f"  ✗ {dir_path.relative_to(agent_dir)} - MISSING")

    # Check key files
    key_files = [
        agent_dir / "agent" / "agent_core.py",
        agent_dir / "agent" / "config.py",
        agent_dir / "agent_ui.py",
        agent_dir / "requirements.txt"
    ]

    print("\nKey Files Check:")
    for file_path in key_files:
        if file_path.exists():
            print(f"  ✓ {file_path.relative_to(agent_dir)}")
        else:
            print(f"  ✗ {file_path.relative_to(agent_dir)} - MISSING")

    # Final verdict
    print_header("FINAL VERDICT")

    if report["summary"]["overall_status"] == "PASSED":
        print("✓✓✓ ALL VALIDATION TESTS PASSED ✓✓✓")
        print("\nThe KAI Agent integration is ready for deployment!")
        print("\nNext Steps:")
        print("  1. Review the detailed report: final_validation_report.json")
        print("  2. Follow deployment guide: DEPLOYMENT_GUIDE.md")
        print("  3. Configure API keys in .env file")
        print("  4. Build Docker sandbox: python build_sandbox.py")
        print("  5. Set up knowledge base: python setup_knowledge_base.py")
        return 0
    print("✗✗✗ VALIDATION FAILED ✗✗✗")
    print("\nSome tests did not pass. Please review the output above.")
    print("Check the detailed report: final_validation_report.json")
    return 1


if __name__ == "__main__":
    sys.exit(main())
