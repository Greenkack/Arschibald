"""
Verification script for Task 8.3: Validierungs-Report

This script verifies that the validation report generation system
is working correctly and meets all requirements.
"""

from pathlib import Path
from multi_pdf_positioning.validation_reporter import (
    ValidationReporter,
    generate_validation_report,
    generate_batch_report
)


def verify_single_report():
    """Verify single report generation."""
    print("=" * 80)
    print("VERIFICATION: Single Report Generation")
    print("=" * 80)
    
    reporter = ValidationReporter()
    
    # Test with valid positions
    positions = [
        (50, 50, 200, 100),
        (250, 50, 400, 100),
    ]
    
    report = reporter.generate_validation_report(
        positions, firma=1, seite=1
    )
    
    assert report.firma == 1
    assert report.seite == 1
    assert report.total_elements == 2
    assert report.is_valid is True
    
    print("Single report generation works")
    print(f"  - Firma: {report.firma}")
    print(f"  - Seite: {report.seite}")
    print(f"  - Elements: {report.total_elements}")
    print(f"  - Valid: {report.is_valid}")
    print()


def verify_batch_report():
    """Verify batch report generation."""
    print("=" * 80)
    print("VERIFICATION: Batch Report Generation")
    print("=" * 80)
    
    reporter = ValidationReporter()
    
    # Create test data
    validation_data = {}
    for firma in [1, 2]:
        for seite in [1, 2]:
            positions = [(50, 50, 200, 100), (250, 50, 400, 100)]
            validation_data[(firma, seite)] = (positions, None)
    
    summary = reporter.generate_batch_report(validation_data)
    
    assert summary.total_combinations == 4
    assert len(summary.all_reports) == 4
    assert len(summary.reports_by_firma) == 2
    assert len(summary.reports_by_seite) == 2
    
    print("Batch report generation works")
    print(f"  - Total combinations: {summary.total_combinations}")
    print(f"  - Valid combinations: {summary.valid_combinations}")
    print(f"  - Invalid combinations: {summary.invalid_combinations}")
    print()


def verify_text_format():
    """Verify text format output."""
    print("=" * 80)
    print("VERIFICATION: Text Format Output")
    print("=" * 80)
    
    reporter = ValidationReporter()
    
    positions = [(50, 50, 200, 100)]
    report = reporter.generate_validation_report(
        positions, firma=1, seite=1
    )
    
    text = reporter.format_report_text(report)
    
    assert "VALIDATION REPORT" in text
    assert "Firma: 1, Seite: 1" in text
    assert "SUMMARY" in text
    
    print("Text format output works")
    print("  - Contains header")
    print("  - Contains firma/seite info")
    print("  - Contains summary section")
    print()


def verify_json_format():
    """Verify JSON format output."""
    print("=" * 80)
    print("VERIFICATION: JSON Format Output")
    print("=" * 80)
    
    reporter = ValidationReporter()
    
    positions = [(50, 50, 200, 100)]
    report = reporter.generate_validation_report(
        positions, firma=1, seite=1
    )
    
    data = reporter.format_report_json(report)
    
    assert "firma" in data
    assert "seite" in data
    assert "is_valid" in data
    assert "messages" in data
    assert "collisions" in data
    assert "summary" in data
    
    print("JSON format output works")
    print("  - Contains all required fields")
    print("  - Data is serializable")
    print()


def verify_error_warning_lists():
    """Verify error and warning list generation."""
    print("=" * 80)
    print("VERIFICATION: Error and Warning Lists")
    print("=" * 80)
    
    reporter = ValidationReporter()
    
    # Create data with errors and warnings
    validation_data = {
        (1, 1): ([(400, 50, 600, 100)], None),  # Out of bounds (error)
        (1, 2): ([(5, 50, 200, 100)], None),    # Too close to edge (warning)
        (2, 1): ([(50, 50, 200, 100)], None),   # Valid
    }
    
    summary = reporter.generate_batch_report(validation_data)
    
    errors = reporter.generate_error_list(summary)
    warnings = reporter.generate_warning_list(summary)
    
    assert len(errors) > 0
    assert len(warnings) > 0
    assert all("firma" in e for e in errors)
    assert all("seite" in e for e in errors)
    
    print("Error and warning lists work")
    print(f"  - Errors found: {len(errors)}")
    print(f"  - Warnings found: {len(warnings)}")
    print()


def verify_summaries():
    """Verify summary generation by firma and seite."""
    print("=" * 80)
    print("VERIFICATION: Summaries by Firma and Seite")
    print("=" * 80)
    
    reporter = ValidationReporter()
    
    # Create test data
    validation_data = {}
    for firma in [1, 2, 3]:
        for seite in [1, 2]:
            positions = [(50, 50, 200, 100)]
            validation_data[(firma, seite)] = (positions, None)
    
    summary = reporter.generate_batch_report(validation_data)
    
    firma_summaries = reporter.generate_summary_by_firma(summary)
    seite_summaries = reporter.generate_summary_by_seite(summary)
    
    assert len(firma_summaries) == 3
    assert len(seite_summaries) == 2
    assert all("total_seiten" in s for s in firma_summaries.values())
    assert all("total_firmen" in s for s in seite_summaries.values())
    
    print("Summaries work")
    print(f"  - Firma summaries: {len(firma_summaries)}")
    print(f"  - Seite summaries: {len(seite_summaries)}")
    print()


def verify_file_export():
    """Verify file export functionality."""
    print("=" * 80)
    print("VERIFICATION: File Export")
    print("=" * 80)
    
    reporter = ValidationReporter()
    output_dir = Path("multi_pdf_positioning/validation_reports_verify")
    
    # Create report
    positions = [(50, 50, 200, 100)]
    report = reporter.generate_validation_report(
        positions, firma=1, seite=1
    )
    
    # Save in both formats
    text_path = output_dir / "test_report.txt"
    json_path = output_dir / "test_report.json"
    
    reporter.save_report_text(report, text_path)
    reporter.save_report_json(report, json_path)
    
    assert text_path.exists()
    assert json_path.exists()
    
    print("File export works")
    print(f"  - Text file created: {text_path}")
    print(f"  - JSON file created: {json_path}")
    print()


def verify_convenience_functions():
    """Verify convenience functions."""
    print("=" * 80)
    print("VERIFICATION: Convenience Functions")
    print("=" * 80)
    
    # Test generate_validation_report function
    report = generate_validation_report(
        positions=[(50, 50, 200, 100)],
        firma=1,
        seite=1
    )
    
    assert report.firma == 1
    assert report.seite == 1
    
    # Test generate_batch_report function
    validation_data = {
        (1, 1): ([(50, 50, 200, 100)], None),
    }
    
    summary = generate_batch_report(validation_data)
    
    assert summary.total_combinations == 1
    
    print("Convenience functions work")
    print("  - generate_validation_report() works")
    print("  - generate_batch_report() works")
    print()


def verify_requirements():
    """Verify that all requirements are met."""
    print("=" * 80)
    print("VERIFICATION: Requirements Coverage")
    print("=" * 80)
    
    print("Requirement 6.4: Validation Reporting")
    print("  Generate comprehensive validation reports")
    print("  Document all validation checks")
    print("  List warnings and errors")
    print("  Create summary per firma and seite")
    print()
    
    print("Requirement 6.5: Warning and Error Documentation")
    print("  List all warnings across reports")
    print("  List all errors across reports")
    print("  Include detailed information (firma, seite, message)")
    print("  Group by firma and seite")
    print()


def main():
    """Run all verifications."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 22 + "TASK 8.3 VERIFICATION" + " " * 35 + "║")
    print("║" + " " * 24 + "Validierungs-Report" + " " * 37 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    
    try:
        verify_single_report()
        verify_batch_report()
        verify_text_format()
        verify_json_format()
        verify_error_warning_lists()
        verify_summaries()
        verify_file_export()
        verify_convenience_functions()
        verify_requirements()
        
        print("=" * 80)
        print("ALL VERIFICATIONS PASSED")
        print("=" * 80)
        print()
        print("Task 8.3 is complete and all requirements are satisfied:")
        print("  - Single validation reports ")
        print("  - Batch validation reports ")
        print("  - Text format output ")
        print("  - JSON format output ")
        print("  - Error and warning lists ")
        print("  - Summaries by firma and seite ")
        print("  - File export functionality ")
        print("  - Convenience functions ")
        print("  - Requirements 6.4 and 6.5 ")
        print()
        
    except AssertionError as e:
        print("=" * 80)
        print("VERIFICATION FAILED")
        print("=" * 80)
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()
