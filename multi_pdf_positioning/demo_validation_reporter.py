"""
Demo script for Validation Reporter Module

This script demonstrates how to use the validation reporter to generate
comprehensive validation reports for single and batch validations.
"""

from pathlib import Path
from multi_pdf_positioning.validation_reporter import ValidationReporter
from multi_pdf_positioning.yml_parser import YMLElement


def demo_single_report():
    """Demonstrate generating a single validation report."""
    print("=" * 80)
    print("DEMO: Single Validation Report")
    print("=" * 80)
    print()
    
    reporter = ValidationReporter()
    
    # Example 1: Valid positions
    print("Example 1: Valid Positions")
    print("-" * 80)
    
    positions = [
        (50, 50, 200, 100),
        (250, 50, 400, 100),
        (50, 150, 200, 200),
    ]
    
    report = reporter.generate_validation_report(
        positions, firma=1, seite=1
    )
    
    print(reporter.format_report_text(report))
    print()
    
    # Example 2: Positions with collision
    print("Example 2: Positions with Collision")
    print("-" * 80)
    
    positions = [
        (50, 50, 200, 100),
        (100, 75, 250, 125),  # Overlaps with first
        (300, 300, 400, 400),
    ]
    
    report = reporter.generate_validation_report(
        positions, firma=1, seite=2
    )
    
    print(reporter.format_report_text(report))
    print()
    
    # Example 3: Positions out of bounds
    print("Example 3: Positions Out of Bounds")
    print("-" * 80)
    
    positions = [
        (50, 50, 200, 100),
        (400, 50, 600, 100),  # Exceeds page width
        (50, 800, 200, 900),  # Exceeds page height
    ]
    
    report = reporter.generate_validation_report(
        positions, firma=2, seite=1
    )
    
    print(reporter.format_report_text(report))
    print()


def demo_batch_report():
    """Demonstrate generating a batch validation report."""
    print("=" * 80)
    print("DEMO: Batch Validation Report")
    print("=" * 80)
    print()
    
    reporter = ValidationReporter()
    
    # Create validation data for multiple firma/seite combinations
    validation_data = {}
    
    # Firma 1, Seite 1: Valid
    validation_data[(1, 1)] = (
        [
            (50, 50, 200, 100),
            (250, 50, 400, 100),
            (50, 150, 200, 200),
        ],
        None
    )
    
    # Firma 1, Seite 2: Has collision
    validation_data[(1, 2)] = (
        [
            (50, 50, 200, 100),
            (100, 75, 250, 125),
        ],
        None
    )
    
    # Firma 1, Seite 3: Valid
    validation_data[(1, 3)] = (
        [
            (50, 50, 200, 100),
            (250, 150, 400, 200),
        ],
        None
    )
    
    # Firma 2, Seite 1: Out of bounds
    validation_data[(2, 1)] = (
        [
            (50, 50, 200, 100),
            (400, 50, 600, 100),
        ],
        None
    )
    
    # Firma 2, Seite 2: Valid
    validation_data[(2, 2)] = (
        [
            (50, 50, 200, 100),
            (250, 50, 400, 100),
        ],
        None
    )
    
    # Firma 2, Seite 3: Too close to edge
    validation_data[(2, 3)] = (
        [
            (5, 50, 200, 100),
            (250, 50, 400, 100),
        ],
        None
    )
    
    # Generate batch report
    summary = reporter.generate_batch_report(validation_data)
    
    # Print formatted summary
    print(reporter.format_batch_summary_text(summary))
    print()


def demo_error_and_warning_lists():
    """Demonstrate generating error and warning lists."""
    print("=" * 80)
    print("DEMO: Error and Warning Lists")
    print("=" * 80)
    print()
    
    reporter = ValidationReporter()
    
    # Create validation data with various issues
    validation_data = {
        (1, 1): ([(400, 50, 600, 100)], None),              # Out of bounds (error)
        (1, 2): ([(5, 50, 200, 100)], None),                # Too close to edge (warning)
        (2, 1): ([(50, 50, 200, 100), (100, 75, 250, 125)], None),  # Collision (error)
        (2, 2): ([(50, 50, 200, 100)], None),               # Valid
    }
    
    summary = reporter.generate_batch_report(validation_data)
    
    # Generate lists
    errors = reporter.generate_error_list(summary)
    warnings = reporter.generate_warning_list(summary)
    collisions = reporter.generate_collision_list(summary)
    
    # Print errors
    print(f"ERRORS ({len(errors)})")
    print("-" * 80)
    for error in errors:
        print(f"  Firma {error['firma']}, Seite {error['seite']}: {error['message']}")
    print()
    
    # Print warnings
    print(f"WARNINGS ({len(warnings)})")
    print("-" * 80)
    for warning in warnings:
        print(f"  Firma {warning['firma']}, Seite {warning['seite']}: {warning['message']}")
    print()
    
    # Print collisions
    print(f"COLLISIONS ({len(collisions)})")
    print("-" * 80)
    for collision in collisions:
        print(f"  Firma {collision['firma']}, Seite {collision['seite']}: "
              f"Elements {collision['element1_index']} and {collision['element2_index']}")
    print()


def demo_summaries_by_firma_and_seite():
    """Demonstrate generating summaries by firma and seite."""
    print("=" * 80)
    print("DEMO: Summaries by Firma and Seite")
    print("=" * 80)
    print()
    
    reporter = ValidationReporter()
    
    # Create validation data
    validation_data = {}
    
    for firma in [1, 2, 3]:
        for seite in [1, 2, 3]:
            # Make some combinations invalid
            if (firma == 1 and seite == 1) or (firma == 2 and seite == 2):
                # Invalid: collision
                positions = [
                    (50, 50, 200, 100),
                    (100, 75, 250, 125),
                ]
            else:
                # Valid
                positions = [
                    (50, 50, 200, 100),
                    (250, 50, 400, 100),
                ]
            
            validation_data[(firma, seite)] = (positions, None)
    
    summary = reporter.generate_batch_report(validation_data)
    
    # Generate summaries
    firma_summaries = reporter.generate_summary_by_firma(summary)
    seite_summaries = reporter.generate_summary_by_seite(summary)
    
    # Print firma summaries
    print("SUMMARY BY FIRMA")
    print("-" * 80)
    for firma, stats in sorted(firma_summaries.items()):
        print(f"\nFirma {firma}:")
        print(f"  Total seiten: {stats['total_seiten']}")
        print(f"  Valid seiten: {stats['valid_seiten']}")
        print(f"  Invalid seiten: {stats['invalid_seiten']}")
        print(f"  Total errors: {stats['total_errors']}")
        print(f"  Total warnings: {stats['total_warnings']}")
        print(f"  Total collisions: {stats['total_collisions']}")
        if stats['invalid_seite_numbers']:
            print(f"  Invalid seite numbers: {stats['invalid_seite_numbers']}")
    print()
    
    # Print seite summaries
    print("SUMMARY BY SEITE")
    print("-" * 80)
    for seite, stats in sorted(seite_summaries.items()):
        print(f"\nSeite {seite}:")
        print(f"  Total firmen: {stats['total_firmen']}")
        print(f"  Valid firmen: {stats['valid_firmen']}")
        print(f"  Invalid firmen: {stats['invalid_firmen']}")
        print(f"  Total errors: {stats['total_errors']}")
        print(f"  Total warnings: {stats['total_warnings']}")
        print(f"  Total collisions: {stats['total_collisions']}")
        if stats['invalid_firma_numbers']:
            print(f"  Invalid firma numbers: {stats['invalid_firma_numbers']}")
    print()


def demo_save_reports():
    """Demonstrate saving reports to files."""
    print("=" * 80)
    print("DEMO: Saving Reports to Files")
    print("=" * 80)
    print()
    
    reporter = ValidationReporter()
    output_dir = Path("multi_pdf_positioning/validation_reports_demo")
    
    # Create single report
    positions = [
        (50, 50, 200, 100),
        (100, 75, 250, 125),  # Collision
    ]
    
    report = reporter.generate_validation_report(
        positions, firma=1, seite=1
    )
    
    # Save single report in both formats
    reporter.save_report_text(report, output_dir / "report_f1_s1.txt")
    reporter.save_report_json(report, output_dir / "report_f1_s1.json")
    
    print(f"[OK] Saved single report to:")
    print(f"  - {output_dir / 'report_f1_s1.txt'}")
    print(f"  - {output_dir / 'report_f1_s1.json'}")
    print()
    
    # Create batch report
    validation_data = {
        (1, 1): ([(50, 50, 200, 100), (100, 75, 250, 125)], None),
        (1, 2): ([(50, 50, 200, 100)], None),
        (2, 1): ([(400, 50, 600, 100)], None),
        (2, 2): ([(50, 50, 200, 100)], None),
    }
    
    summary = reporter.generate_batch_report(validation_data)
    
    # Save batch summary in both formats
    reporter.save_batch_summary_text(summary, output_dir / "batch_summary.txt")
    reporter.save_batch_summary_json(summary, output_dir / "batch_summary.json")
    
    print(f"[OK] Saved batch summary to:")
    print(f"  - {output_dir / 'batch_summary.txt'}")
    print(f"  - {output_dir / 'batch_summary.json'}")
    print()
    
    print(f"All reports saved to: {output_dir}")
    print()


def demo_with_yml_elements():
    """Demonstrate validation with YMLElement context."""
    print("=" * 80)
    print("DEMO: Validation with YMLElement Context")
    print("=" * 80)
    print()
    
    reporter = ValidationReporter()
    
    # Create positions and corresponding elements
    positions = [
        (50, 50, 200, 100),
        (100, 75, 250, 125),  # Collision
    ]
    
    elements = [
        YMLElement(
            text="ERSTELLT FÜR:",
            position=positions[0],
            font="Helvetica-Bold",
            font_size=20.0,
            color=30920,
            index=0
        ),
        YMLElement(
            text="kunde_vorname_und_nachname",
            position=positions[1],
            font="Helvetica",
            font_size=14.0,
            color=3487029,
            index=1
        ),
    ]
    
    report = reporter.generate_validation_report(
        positions, elements, firma=1, seite=1
    )
    
    print(reporter.format_report_text(report))
    print()
    
    print("Note: Error messages include element text for better context")
    print()


def main():
    """Run all demos."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "VALIDATION REPORTER DEMO" + " " * 34 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    
    # Run demos
    demo_single_report()
    input("Press Enter to continue to batch report demo...")
    print()
    
    demo_batch_report()
    input("Press Enter to continue to error/warning lists demo...")
    print()
    
    demo_error_and_warning_lists()
    input("Press Enter to continue to summaries demo...")
    print()
    
    demo_summaries_by_firma_and_seite()
    input("Press Enter to continue to save reports demo...")
    print()
    
    demo_save_reports()
    input("Press Enter to continue to YMLElement context demo...")
    print()
    
    demo_with_yml_elements()
    
    print("=" * 80)
    print("[OK] All demos completed successfully!")
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()
