"""
Validation Report Generator Module for Multi-PDF Positioning System

This module provides comprehensive validation reporting functionality,
including batch validation reports, summaries per firma and seite,
and various output formats.

Requirements covered:
- 6.4: Validation reporting
- 6.5: Warning and error documentation
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import json
from datetime import datetime
from collections import defaultdict

from multi_pdf_positioning.validation_system import (
    ValidationSystem,
    ValidationReport,
    ValidationLevel,
    ValidationMessage
)
from multi_pdf_positioning.yml_parser import YMLElement


@dataclass
class BatchValidationSummary:
    """
    Summary of validation results across multiple firma/seite combinations.
    
    Attributes:
        timestamp: When the batch validation was performed
        total_combinations: Total number of firma/seite combinations validated
        valid_combinations: Number of valid combinations
        invalid_combinations: Number of invalid combinations
        total_errors: Total number of errors across all combinations
        total_warnings: Total number of warnings across all combinations
        total_collisions: Total number of collisions across all combinations
        reports_by_firma: Reports grouped by firma
        reports_by_seite: Reports grouped by seite
        all_reports: All individual validation reports
    """
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    total_combinations: int = 0
    valid_combinations: int = 0
    invalid_combinations: int = 0
    total_errors: int = 0
    total_warnings: int = 0
    total_collisions: int = 0
    reports_by_firma: Dict[int, List[ValidationReport]] = field(default_factory=dict)
    reports_by_seite: Dict[int, List[ValidationReport]] = field(default_factory=dict)
    all_reports: List[ValidationReport] = field(default_factory=list)


class ValidationReporter:
    """
    Comprehensive validation report generator.
    
    This class generates detailed validation reports for individual
    firma/seite combinations as well as batch summaries across
    multiple combinations.
    """
    
    def __init__(self, validator: Optional[ValidationSystem] = None):
        """
        Initialize the validation reporter.
        
        Args:
            validator: Optional ValidationSystem instance (creates default if None)
        """
        self.validator = validator or ValidationSystem()
    
    def generate_validation_report(
        self,
        positions: List[Tuple[float, float, float, float]],
        elements: Optional[List[YMLElement]] = None,
        firma: Optional[int] = None,
        seite: Optional[int] = None
    ) -> ValidationReport:
        """
        Generate a comprehensive validation report for a single combination.
        
        Args:
            positions: List of position tuples (x1, y1, x2, y2)
            elements: Optional list of YMLElement objects for context
            firma: Optional firma number
            seite: Optional seite number
            
        Returns:
            ValidationReport with all validation results
            
        Requirements: 6.4, 6.5
        """
        return self.validator.generate_validation_report(
            positions, elements, firma, seite
        )
    
    def generate_batch_report(
        self,
        validation_data: Dict[Tuple[int, int], Tuple[List[Tuple], Optional[List[YMLElement]]]]
    ) -> BatchValidationSummary:
        """
        Generate a batch validation report for multiple firma/seite combinations.
        
        Args:
            validation_data: Dictionary mapping (firma, seite) tuples to
                           (positions, elements) tuples
                           
        Returns:
            BatchValidationSummary with aggregated results
            
        Requirements: 6.4, 6.5
        """
        summary = BatchValidationSummary()
        summary.total_combinations = len(validation_data)
        
        # Initialize grouping dictionaries
        summary.reports_by_firma = defaultdict(list)
        summary.reports_by_seite = defaultdict(list)
        
        # Validate each combination
        for (firma, seite), (positions, elements) in validation_data.items():
            report = self.generate_validation_report(
                positions, elements, firma, seite
            )
            
            # Add to all reports
            summary.all_reports.append(report)
            
            # Group by firma and seite
            summary.reports_by_firma[firma].append(report)
            summary.reports_by_seite[seite].append(report)
            
            # Update counters
            if report.is_valid:
                summary.valid_combinations += 1
            else:
                summary.invalid_combinations += 1
            
            summary.total_errors += len(report.get_errors())
            summary.total_warnings += len(report.get_warnings())
            summary.total_collisions += len(report.collisions)
        
        return summary
    
    def format_report_text(
        self,
        report: ValidationReport,
        include_details: bool = True
    ) -> str:
        """
        Format a validation report as human-readable text.
        
        Args:
            report: ValidationReport to format
            include_details: Whether to include detailed messages
            
        Returns:
            Formatted report string
            
        Requirements: 6.4, 6.5
        """
        return self.validator.format_report(report)
    
    def format_batch_summary_text(
        self,
        summary: BatchValidationSummary,
        include_per_firma: bool = True,
        include_per_seite: bool = True
    ) -> str:
        """
        Format a batch validation summary as human-readable text.
        
        Args:
            summary: BatchValidationSummary to format
            include_per_firma: Whether to include per-firma breakdown
            include_per_seite: Whether to include per-seite breakdown
            
        Returns:
            Formatted summary string
            
        Requirements: 6.4, 6.5
        """
        lines = []
        lines.append("=" * 80)
        lines.append("BATCH VALIDATION SUMMARY")
        lines.append("=" * 80)
        lines.append(f"Timestamp: {summary.timestamp}")
        lines.append("")
        
        # Overall statistics
        lines.append("OVERALL STATISTICS")
        lines.append("-" * 80)
        lines.append(f"  Total combinations validated: {summary.total_combinations}")
        lines.append(f"  Valid combinations: {summary.valid_combinations} "
                    f"({summary.valid_combinations / summary.total_combinations * 100:.1f}%)")
        lines.append(f"  Invalid combinations: {summary.invalid_combinations} "
                    f"({summary.invalid_combinations / summary.total_combinations * 100:.1f}%)")
        lines.append(f"  Total errors: {summary.total_errors}")
        lines.append(f"  Total warnings: {summary.total_warnings}")
        lines.append(f"  Total collisions: {summary.total_collisions}")
        lines.append("")
        
        # Per-firma breakdown
        if include_per_firma and summary.reports_by_firma:
            lines.append("BREAKDOWN BY FIRMA")
            lines.append("-" * 80)
            
            for firma in sorted(summary.reports_by_firma.keys()):
                reports = summary.reports_by_firma[firma]
                valid_count = sum(1 for r in reports if r.is_valid)
                error_count = sum(len(r.get_errors()) for r in reports)
                warning_count = sum(len(r.get_warnings()) for r in reports)
                collision_count = sum(len(r.collisions) for r in reports)
                
                lines.append(f"\n  Firma {firma}:")
                lines.append(f"    Seiten validated: {len(reports)}")
                lines.append(f"    Valid: {valid_count}/{len(reports)}")
                lines.append(f"    Errors: {error_count}")
                lines.append(f"    Warnings: {warning_count}")
                lines.append(f"    Collisions: {collision_count}")
                
                # List invalid seiten
                invalid_seiten = [r.seite for r in reports if not r.is_valid]
                if invalid_seiten:
                    lines.append(f"    Invalid seiten: {', '.join(map(str, invalid_seiten))}")
            
            lines.append("")
        
        # Per-seite breakdown
        if include_per_seite and summary.reports_by_seite:
            lines.append("BREAKDOWN BY SEITE")
            lines.append("-" * 80)
            
            for seite in sorted(summary.reports_by_seite.keys()):
                reports = summary.reports_by_seite[seite]
                valid_count = sum(1 for r in reports if r.is_valid)
                error_count = sum(len(r.get_errors()) for r in reports)
                warning_count = sum(len(r.get_warnings()) for r in reports)
                collision_count = sum(len(r.collisions) for r in reports)
                
                lines.append(f"\n  Seite {seite}:")
                lines.append(f"    Firmen validated: {len(reports)}")
                lines.append(f"    Valid: {valid_count}/{len(reports)}")
                lines.append(f"    Errors: {error_count}")
                lines.append(f"    Warnings: {warning_count}")
                lines.append(f"    Collisions: {collision_count}")
                
                # List invalid firmen
                invalid_firmen = [r.firma for r in reports if not r.is_valid]
                if invalid_firmen:
                    lines.append(f"    Invalid firmen: {', '.join(map(str, invalid_firmen))}")
            
            lines.append("")
        
        # List all invalid combinations
        invalid_reports = [r for r in summary.all_reports if not r.is_valid]
        if invalid_reports:
            lines.append("INVALID COMBINATIONS")
            lines.append("-" * 80)
            for report in invalid_reports:
                lines.append(f"  Firma {report.firma}, Seite {report.seite}:")
                lines.append(f"    Errors: {len(report.get_errors())}")
                lines.append(f"    Warnings: {len(report.get_warnings())}")
                lines.append(f"    Collisions: {len(report.collisions)}")
            lines.append("")
        
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def format_report_json(self, report: ValidationReport) -> Dict:
        """
        Format a validation report as JSON-serializable dictionary.
        
        Args:
            report: ValidationReport to format
            
        Returns:
            Dictionary representation of the report
            
        Requirements: 6.4
        """
        return {
            "firma": report.firma,
            "seite": report.seite,
            "timestamp": report.timestamp,
            "is_valid": report.is_valid,
            "total_elements": report.total_elements,
            "summary": report.summary,
            "messages": [
                {
                    "level": msg.level.value,
                    "message": msg.message,
                    "element_index": msg.element_index,
                    "position": msg.position,
                    "details": msg.details
                }
                for msg in report.messages
            ],
            "collisions": [
                {
                    "element1_index": c.element1_index,
                    "element2_index": c.element2_index,
                    "element1_position": c.element1_position,
                    "element2_position": c.element2_position,
                    "overlap_area": c.overlap_area,
                    "overlap_rect": c.overlap_rect
                }
                for c in report.collisions
            ]
        }
    
    def format_batch_summary_json(self, summary: BatchValidationSummary) -> Dict:
        """
        Format a batch validation summary as JSON-serializable dictionary.
        
        Args:
            summary: BatchValidationSummary to format
            
        Returns:
            Dictionary representation of the summary
            
        Requirements: 6.4
        """
        return {
            "timestamp": summary.timestamp,
            "total_combinations": summary.total_combinations,
            "valid_combinations": summary.valid_combinations,
            "invalid_combinations": summary.invalid_combinations,
            "total_errors": summary.total_errors,
            "total_warnings": summary.total_warnings,
            "total_collisions": summary.total_collisions,
            "reports_by_firma": {
                firma: [self.format_report_json(r) for r in reports]
                for firma, reports in summary.reports_by_firma.items()
            },
            "reports_by_seite": {
                seite: [self.format_report_json(r) for r in reports]
                for seite, reports in summary.reports_by_seite.items()
            }
        }
    
    def save_report_text(
        self,
        report: ValidationReport,
        output_path: Path,
        include_details: bool = True
    ):
        """
        Save a validation report to a text file.
        
        Args:
            report: ValidationReport to save
            output_path: Path to output file
            include_details: Whether to include detailed messages
            
        Requirements: 6.4
        """
        text = self.format_report_text(report, include_details)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text, encoding='utf-8')
    
    def save_report_json(
        self,
        report: ValidationReport,
        output_path: Path
    ):
        """
        Save a validation report to a JSON file.
        
        Args:
            report: ValidationReport to save
            output_path: Path to output file
            
        Requirements: 6.4
        """
        data = self.format_report_json(report)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
    
    def save_batch_summary_text(
        self,
        summary: BatchValidationSummary,
        output_path: Path,
        include_per_firma: bool = True,
        include_per_seite: bool = True
    ):
        """
        Save a batch validation summary to a text file.
        
        Args:
            summary: BatchValidationSummary to save
            output_path: Path to output file
            include_per_firma: Whether to include per-firma breakdown
            include_per_seite: Whether to include per-seite breakdown
            
        Requirements: 6.4
        """
        text = self.format_batch_summary_text(
            summary, include_per_firma, include_per_seite
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text, encoding='utf-8')
    
    def save_batch_summary_json(
        self,
        summary: BatchValidationSummary,
        output_path: Path
    ):
        """
        Save a batch validation summary to a JSON file.
        
        Args:
            summary: BatchValidationSummary to save
            output_path: Path to output file
            
        Requirements: 6.4
        """
        data = self.format_batch_summary_json(summary)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
    
    def generate_error_list(
        self,
        summary: BatchValidationSummary
    ) -> List[Dict]:
        """
        Generate a list of all errors across all reports.
        
        Args:
            summary: BatchValidationSummary to extract errors from
            
        Returns:
            List of error dictionaries with firma, seite, and error details
            
        Requirements: 6.5
        """
        errors = []
        
        for report in summary.all_reports:
            for error in report.get_errors():
                errors.append({
                    "firma": report.firma,
                    "seite": report.seite,
                    "level": error.level.value,
                    "message": error.message,
                    "element_index": error.element_index,
                    "position": error.position,
                    "details": error.details
                })
        
        return errors
    
    def generate_warning_list(
        self,
        summary: BatchValidationSummary
    ) -> List[Dict]:
        """
        Generate a list of all warnings across all reports.
        
        Args:
            summary: BatchValidationSummary to extract warnings from
            
        Returns:
            List of warning dictionaries with firma, seite, and warning details
            
        Requirements: 6.5
        """
        warnings = []
        
        for report in summary.all_reports:
            for warning in report.get_warnings():
                warnings.append({
                    "firma": report.firma,
                    "seite": report.seite,
                    "level": warning.level.value,
                    "message": warning.message,
                    "element_index": warning.element_index,
                    "position": warning.position,
                    "details": warning.details
                })
        
        return warnings
    
    def generate_collision_list(
        self,
        summary: BatchValidationSummary
    ) -> List[Dict]:
        """
        Generate a list of all collisions across all reports.
        
        Args:
            summary: BatchValidationSummary to extract collisions from
            
        Returns:
            List of collision dictionaries with firma, seite, and collision details
            
        Requirements: 6.5
        """
        collisions = []
        
        for report in summary.all_reports:
            for collision in report.collisions:
                collisions.append({
                    "firma": report.firma,
                    "seite": report.seite,
                    "element1_index": collision.element1_index,
                    "element2_index": collision.element2_index,
                    "element1_position": collision.element1_position,
                    "element2_position": collision.element2_position,
                    "overlap_area": collision.overlap_area,
                    "overlap_rect": collision.overlap_rect
                })
        
        return collisions
    
    def generate_summary_by_firma(
        self,
        summary: BatchValidationSummary
    ) -> Dict[int, Dict]:
        """
        Generate summary statistics grouped by firma.
        
        Args:
            summary: BatchValidationSummary to summarize
            
        Returns:
            Dictionary mapping firma numbers to summary statistics
            
        Requirements: 6.4
        """
        firma_summaries = {}
        
        for firma, reports in summary.reports_by_firma.items():
            firma_summaries[firma] = {
                "total_seiten": len(reports),
                "valid_seiten": sum(1 for r in reports if r.is_valid),
                "invalid_seiten": sum(1 for r in reports if not r.is_valid),
                "total_errors": sum(len(r.get_errors()) for r in reports),
                "total_warnings": sum(len(r.get_warnings()) for r in reports),
                "total_collisions": sum(len(r.collisions) for r in reports),
                "invalid_seite_numbers": [r.seite for r in reports if not r.is_valid]
            }
        
        return firma_summaries
    
    def generate_summary_by_seite(
        self,
        summary: BatchValidationSummary
    ) -> Dict[int, Dict]:
        """
        Generate summary statistics grouped by seite.
        
        Args:
            summary: BatchValidationSummary to summarize
            
        Returns:
            Dictionary mapping seite numbers to summary statistics
            
        Requirements: 6.4
        """
        seite_summaries = {}
        
        for seite, reports in summary.reports_by_seite.items():
            seite_summaries[seite] = {
                "total_firmen": len(reports),
                "valid_firmen": sum(1 for r in reports if r.is_valid),
                "invalid_firmen": sum(1 for r in reports if not r.is_valid),
                "total_errors": sum(len(r.get_errors()) for r in reports),
                "total_warnings": sum(len(r.get_warnings()) for r in reports),
                "total_collisions": sum(len(r.collisions) for r in reports),
                "invalid_firma_numbers": [r.firma for r in reports if not r.is_valid]
            }
        
        return seite_summaries


# Convenience functions
def generate_validation_report(
    positions: List[Tuple[float, float, float, float]],
    elements: Optional[List[YMLElement]] = None,
    firma: Optional[int] = None,
    seite: Optional[int] = None
) -> ValidationReport:
    """
    Convenience function to generate a validation report.
    
    Args:
        positions: List of position tuples (x1, y1, x2, y2)
        elements: Optional list of YMLElement objects
        firma: Optional firma number
        seite: Optional seite number
        
    Returns:
        ValidationReport with all validation results
    """
    reporter = ValidationReporter()
    return reporter.generate_validation_report(positions, elements, firma, seite)


def generate_batch_report(
    validation_data: Dict[Tuple[int, int], Tuple[List[Tuple], Optional[List[YMLElement]]]]
) -> BatchValidationSummary:
    """
    Convenience function to generate a batch validation report.
    
    Args:
        validation_data: Dictionary mapping (firma, seite) tuples to
                       (positions, elements) tuples
                       
    Returns:
        BatchValidationSummary with aggregated results
    """
    reporter = ValidationReporter()
    return reporter.generate_batch_report(validation_data)


if __name__ == "__main__":
    # Example usage
    print("\n=== Validation Reporter Demo ===\n")
    
    # Create reporter
    reporter = ValidationReporter()
    
    # Example: Single report
    print("--- Single Report Example ---")
    test_positions = [
        (50, 50, 200, 100),
        (100, 75, 250, 125),  # Overlaps with first
        (300, 300, 400, 400),
    ]
    
    report = reporter.generate_validation_report(
        test_positions,
        firma=1,
        seite=1
    )
    
    print(reporter.format_report_text(report))
    
    # Example: Batch report
    print("\n--- Batch Report Example ---")
    validation_data = {}
    
    # Simulate data for 2 firmen x 2 seiten
    for firma in [1, 2]:
        for seite in [1, 2]:
            # Create some test positions
            if firma == 1 and seite == 1:
                # Invalid: has collision
                positions = [
                    (50, 50, 200, 100),
                    (100, 75, 250, 125),
                ]
            elif firma == 2 and seite == 1:
                # Invalid: out of bounds
                positions = [
                    (50, 50, 200, 100),
                    (400, 50, 600, 100),
                ]
            else:
                # Valid
                positions = [
                    (50, 50, 200, 100),
                    (250, 50, 400, 100),
                    (50, 150, 200, 200),
                ]
            
            validation_data[(firma, seite)] = (positions, None)
    
    batch_summary = reporter.generate_batch_report(validation_data)
    
    print(reporter.format_batch_summary_text(batch_summary))
    
    # Example: Save reports
    print("\n--- Saving Reports ---")
    output_dir = Path("multi_pdf_positioning/validation_reports")
    
    # Save single report
    reporter.save_report_text(
        report,
        output_dir / "report_f1_s1.txt"
    )
    reporter.save_report_json(
        report,
        output_dir / "report_f1_s1.json"
    )
    
    # Save batch summary
    reporter.save_batch_summary_text(
        batch_summary,
        output_dir / "batch_summary.txt"
    )
    reporter.save_batch_summary_json(
        batch_summary,
        output_dir / "batch_summary.json"
    )
    
    print(f"Reports saved to: {output_dir}")
    
    # Example: Generate lists
    print("\n--- Error and Warning Lists ---")
    errors = reporter.generate_error_list(batch_summary)
    warnings = reporter.generate_warning_list(batch_summary)
    collisions = reporter.generate_collision_list(batch_summary)
    
    print(f"Total errors: {len(errors)}")
    print(f"Total warnings: {len(warnings)}")
    print(f"Total collisions: {len(collisions)}")
    
    # Example: Summaries by firma and seite
    print("\n--- Summaries ---")
    firma_summaries = reporter.generate_summary_by_firma(batch_summary)
    seite_summaries = reporter.generate_summary_by_seite(batch_summary)
    
    print("\nBy Firma:")
    for firma, stats in firma_summaries.items():
        print(f"  Firma {firma}: {stats['valid_seiten']}/{stats['total_seiten']} valid")
    
    print("\nBy Seite:")
    for seite, stats in seite_summaries.items():
        print(f"  Seite {seite}: {stats['valid_firmen']}/{stats['total_firmen']} valid")
    
    print("\n✓ Validation Reporter module ready")
