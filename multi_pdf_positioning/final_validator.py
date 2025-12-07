"""
Final Validation Module for Multi-PDF Positioning System

This module provides comprehensive validation for all 48 generated YML files:
- Complete test run of the entire workflow
- Validation of all generated YML files
- Generation of final validation report
- Comparison with original files

Requirements: Task 12.2
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime

# Import components
from multi_pdf_positioning.yml_parser import YMLParser, YMLElement
from multi_pdf_positioning.validation_system import ValidationSystem, ValidationReport
from multi_pdf_positioning.main_workflow import main as run_workflow, WorkflowSummary
from multi_pdf_positioning.config import (
    PDF_DIR, YML_DIR, OUTPUT_DIR, FIRMEN, SEITEN
)


@dataclass
class FileValidationResult:
    """
    Validation result for a single YML file.
    
    Attributes:
        firma: Firma number
        seite: Seite number
        filename: YML filename
        exists: Whether file exists
        valid_format: Whether YML format is valid
        elements_count: Number of elements in file
        positions_valid: Whether all positions are valid
        no_collisions: Whether there are no collisions
        attributes_preserved: Whether non-position attributes are preserved
        errors: List of error messages
        warnings: List of warning messages
    """
    firma: int
    seite: int
    filename: str
    exists: bool = False
    valid_format: bool = False
    elements_count: int = 0
    positions_valid: bool = False
    no_collisions: bool = False
    attributes_preserved: bool = False
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    @property
    def is_valid(self) -> bool:
        """Check if file is completely valid."""
        return (
            self.exists and
            self.valid_format and
            self.positions_valid and
            self.no_collisions and
            len(self.errors) == 0
        )


@dataclass
class FinalValidationReport:
    """
    Final validation report for all files.
    
    Attributes:
        timestamp: Report generation timestamp
        total_files: Total number of files validated
        valid_files: Number of valid files
        invalid_files: Number of invalid files
        total_elements: Total number of elements across all files
        total_errors: Total number of errors
        total_warnings: Total number of warnings
        file_results: List of FileValidationResult objects
        workflow_summary: WorkflowSummary from test run
        comparison_results: Comparison with original files
    """
    timestamp: datetime
    total_files: int
    valid_files: int
    invalid_files: int
    total_elements: int
    total_errors: int
    total_warnings: int
    file_results: List[FileValidationResult] = field(default_factory=list)
    workflow_summary: Optional[Dict[str, Any]] = None
    comparison_results: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'total_files': self.total_files,
            'valid_files': self.valid_files,
            'invalid_files': self.invalid_files,
            'total_elements': self.total_elements,
            'total_errors': self.total_errors,
            'total_warnings': self.total_warnings,
            'file_results': [asdict(r) for r in self.file_results],
            'workflow_summary': self.workflow_summary,
            'comparison_results': self.comparison_results
        }


class FinalValidator:
    """
    Final validator for the Multi-PDF Positioning System.
    
    Performs comprehensive validation of all generated files.
    """
    
    def __init__(
        self,
        yml_dir: Optional[Path] = None,
        output_dir: Optional[Path] = None,
        original_dir: Optional[Path] = None
    ):
        """
        Initialize final validator.
        
        Args:
            yml_dir: Directory with original YML files
            output_dir: Directory with generated YML files
            original_dir: Directory with original YML files for comparison
        """
        self.yml_dir = Path(yml_dir) if yml_dir else YML_DIR
        self.output_dir = Path(output_dir) if output_dir else OUTPUT_DIR
        self.original_dir = Path(original_dir) if original_dir else self.yml_dir
        
        # Initialize components
        self.yml_parser = YMLParser()
        self.validation_system = ValidationSystem()
    
    def run_complete_test(
        self,
        firmen: Optional[List[int]] = None,
        seiten: Optional[List[int]] = None
    ) -> WorkflowSummary:
        """
        Run complete test workflow.
        
        Args:
            firmen: List of firma numbers (default: all)
            seiten: List of seite numbers (default: all)
            
        Returns:
            WorkflowSummary from test run
        """
        print("\n" + "=" * 70)
        print("RUNNING COMPLETE TEST WORKFLOW")
        print("=" * 70)
        
        # Run workflow
        summary = run_workflow(
            firmen=firmen,
            seiten=seiten,
            yml_dir=self.yml_dir,
            output_dir=self.output_dir,
            create_backup=False,  # Don't create backup during test
            validate_output=True,
            show_progress=True
        )
        
        return summary
    
    def validate_all_files(
        self,
        firmen: Optional[List[int]] = None,
        seiten: Optional[List[int]] = None
    ) -> List[FileValidationResult]:
        """
        Validate all generated YML files.
        
        Args:
            firmen: List of firma numbers (default: all)
            seiten: List of seite numbers (default: all)
            
        Returns:
            List of FileValidationResult objects
        """
        if firmen is None:
            firmen = FIRMEN
        if seiten is None:
            seiten = SEITEN
        
        print("\n" + "=" * 70)
        print("VALIDATING ALL GENERATED YML FILES")
        print("=" * 70)
        
        results = []
        total = len(firmen) * len(seiten)
        current = 0
        
        for firma in firmen:
            for seite in seiten:
                current += 1
                print(f"\r[{current}/{total}] Validating F{firma}S{seite}...", end="")
                
                result = self._validate_single_file(firma, seite)
                results.append(result)
        
        print()  # New line
        
        return results
    
    def _validate_single_file(
        self,
        firma: int,
        seite: int
    ) -> FileValidationResult:
        """
        Validate a single YML file.
        
        Args:
            firma: Firma number
            seite: Seite number
            
        Returns:
            FileValidationResult
        """
        yml_filename = f"seite{seite}_f{firma}.yml"
        if yml_filename != 0:
            yml_path = self.output_dir / yml_filename
        else:
            yml_path = 0.0
        
        result = FileValidationResult(
            firma=firma,
            seite=seite,
            filename=yml_filename
        )
        
        # Check if file exists
        if not yml_path.exists():
            result.errors.append(f"File does not exist: {yml_path}")
            return result
        
        result.exists = True
        
        try:
            # Parse YML file
            elements = self.yml_parser.parse_yml(str(yml_path))
            result.elements_count = len(elements)
            result.valid_format = True
            
            if not elements:
                result.errors.append("No elements found in YML file")
                return result
            
            # Extract positions
            positions = [elem.position for elem in elements]
            
            # Validate positions
            validation_report = self.validation_system.generate_validation_report(
                positions,
                elements,
                firma,
                seite
            )
            
            result.positions_valid = validation_report.is_valid
            
            # Check for collisions
            collision_errors = [
                e for e in validation_report.get_errors()
                if 'collision' in e.message.lower() or 'overlap' in e.message.lower()
            ]
            result.no_collisions = len(collision_errors) == 0
            
            # Collect errors and warnings
            for error in validation_report.get_errors():
                result.errors.append(error.message)
            
            for warning in validation_report.get_warnings():
                result.warnings.append(warning.message)
            
            # Check if attributes are preserved (compare with original)
            if yml_filename != 0:
                original_path = self.original_dir / yml_filename
            else:
                original_path = 0.0
            if original_path.exists():
                result.attributes_preserved = self._check_attributes_preserved(
                    original_path,
                    yml_path
                )
            else:
                result.warnings.append("Original file not found for comparison")
            
        except Exception as e:
            result.valid_format = False
            result.errors.append(f"Failed to parse YML: {str(e)}")
        
        return result
    
    def _check_attributes_preserved(
        self,
        original_path: Path,
        generated_path: Path
    ) -> bool:
        """
        Check if non-position attributes are preserved.
        
        Args:
            original_path: Path to original YML file
            generated_path: Path to generated YML file
            
        Returns:
            True if attributes are preserved
        """
        try:
            original_elements = self.yml_parser.parse_yml(str(original_path))
            generated_elements = self.yml_parser.parse_yml(str(generated_path))
            
            if len(original_elements) != len(generated_elements):
                return False
            
            # Check each element
            for orig, gen in zip(original_elements, generated_elements):
                # Check non-position attributes
                if orig.text != gen.text:
                    return False
                if orig.font != gen.font:
                    return False
                if orig.font_size != gen.font_size:
                    return False
                if orig.color != gen.color:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def compare_with_original(
        self,
        firmen: Optional[List[int]] = None,
        seiten: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Compare generated files with original files.
        
        Args:
            firmen: List of firma numbers (default: all)
            seiten: List of seite numbers (default: all)
            
        Returns:
            Dictionary with comparison results
        """
        if firmen is None:
            firmen = FIRMEN
        if seiten is None:
            seiten = SEITEN
        
        print("\n" + "=" * 70)
        print("COMPARING WITH ORIGINAL FILES")
        print("=" * 70)
        
        comparison = {
            'total_files': 0,
            'files_compared': 0,
            'position_changes': [],
            'attribute_changes': [],
            'avg_position_change': 0.0
        }
        
        total_position_change = 0.0
        
        for firma in firmen:
            for seite in seiten:
                yml_filename = f"seite{seite}_f{firma}.yml"
                if yml_filename != 0:
                    original_path = self.original_dir / yml_filename
                else:
                    original_path = 0.0
                if yml_filename != 0:
                    generated_path = self.output_dir / yml_filename
                else:
                    generated_path = 0.0
                
                comparison['total_files'] += 1
                
                if not original_path.exists() or not generated_path.exists():
                    continue
                
                try:
                    original_elements = self.yml_parser.parse_yml(str(original_path))
                    generated_elements = self.yml_parser.parse_yml(str(generated_path))
                    
                    comparison['files_compared'] += 1
                    
                    # Calculate position changes
                    for orig, gen in zip(original_elements, generated_elements):
                        # Calculate distance between positions
                        orig_center_x = (orig.position[0] + orig.position[2]) / 2
                        orig_center_y = (orig.position[1] + orig.position[3]) / 2
                        gen_center_x = (gen.position[0] + gen.position[2]) / 2
                        gen_center_y = (gen.position[1] + gen.position[3]) / 2
                        
                        distance = (
                            (gen_center_x - orig_center_x) ** 2 +
                            (gen_center_y - orig_center_y) ** 2
                        ) ** 0.5
                        
                        total_position_change += distance
                        
                        if distance > 10:  # Significant change
                            comparison['position_changes'].append({
                                'firma': firma,
                                'seite': seite,
                                'text': orig.text,
                                'distance': distance
                            })
                        
                        # Check attribute changes
                        if (orig.text != gen.text or
                            orig.font != gen.font or
                            orig.font_size != gen.font_size or
                            orig.color != gen.color):
                            comparison['attribute_changes'].append({
                                'firma': firma,
                                'seite': seite,
                                'text': orig.text
                            })
                
                except Exception as e:
                    print(f"\nWarning: Failed to compare {yml_filename}: {e}")
        
        # Calculate average position change
        if comparison['files_compared'] > 0:
            total_elements = sum(
                len(self.yml_parser.parse_yml(str(self.output_dir / f"seite{s}_f{f}.yml")))
                for f in firmen for s in seiten
                if (self.output_dir / f"seite{s}_f{f}.yml").exists()
            )
            if total_elements > 0:
                if total_elements != 0:
                    comparison['avg_position_change'] = total_position_change / total_elements
                else:
                    comparison['avg_position_change'] = 0.0
        
        return comparison
    
    def generate_final_report(
        self,
        firmen: Optional[List[int]] = None,
        seiten: Optional[List[int]] = None,
        run_test: bool = True
    ) -> FinalValidationReport:
        """
        Generate final validation report.
        
        Args:
            firmen: List of firma numbers (default: all)
            seiten: List of seite numbers (default: all)
            run_test: Whether to run complete test workflow
            
        Returns:
            FinalValidationReport
        """
        if firmen is None:
            firmen = FIRMEN
        if seiten is None:
            seiten = SEITEN
        
        print("\n" + "=" * 70)
        print("GENERATING FINAL VALIDATION REPORT")
        print("=" * 70)
        
        # Step 1: Run complete test (if requested)
        workflow_summary = None
        if run_test:
            summary = self.run_complete_test(firmen=firmen, seiten=seiten)
            workflow_summary = {
                'total_combinations': summary.total_combinations,
                'successful': summary.successful,
                'failed': summary.failed,
                'total_elements': summary.total_elements,
                'total_time': summary.total_time
            }
        
        # Step 2: Validate all files
        file_results = self.validate_all_files(firmen=firmen, seiten=seiten)
        
        # Step 3: Compare with original
        comparison_results = self.compare_with_original(firmen=firmen, seiten=seiten)
        
        # Step 4: Generate report
        valid_files = sum(1 for r in file_results if r.is_valid)
        invalid_files = len(file_results) - valid_files
        total_elements = sum(r.elements_count for r in file_results)
        total_errors = sum(len(r.errors) for r in file_results)
        total_warnings = sum(len(r.warnings) for r in file_results)
        
        report = FinalValidationReport(
            timestamp=datetime.now(),
            total_files=len(file_results),
            valid_files=valid_files,
            invalid_files=invalid_files,
            total_elements=total_elements,
            total_errors=total_errors,
            total_warnings=total_warnings,
            file_results=file_results,
            workflow_summary=workflow_summary,
            comparison_results=comparison_results
        )
        
        return report
    
    def display_report(self, report: FinalValidationReport):
        """
        Display final validation report.
        
        Args:
            report: FinalValidationReport to display
        """
        print("\n" + "=" * 70)
        print("FINAL VALIDATION REPORT")
        print("=" * 70)
        print(f"Generated: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Workflow summary
        if report.workflow_summary:
            print(f"\nWorkflow Test Run:")
            print(f"  Total combinations: {report.workflow_summary['total_combinations']}")
            print(f"  Successful: {report.workflow_summary['successful']}")
            print(f"  Failed: {report.workflow_summary['failed']}")
            print(f"  Total time: {report.workflow_summary['total_time']:.2f}s")
        
        # File validation
        print(f"\nFile Validation:")
        print(f"  Total files: {report.total_files}")
        print(f"  Valid: {report.valid_files}")
        print(f"  Invalid: {report.invalid_files}")
        print(f"  Total elements: {report.total_elements}")
        print(f"  Total errors: {report.total_errors}")
        print(f"  Total warnings: {report.total_warnings}")
        
        # Comparison results
        if report.comparison_results:
            comp = report.comparison_results
            print(f"\nComparison with Original:")
            print(f"  Files compared: {comp['files_compared']}/{comp['total_files']}")
            print(f"  Avg position change: {comp['avg_position_change']:.2f} points")
            print(f"  Significant changes: {len(comp['position_changes'])}")
            print(f"  Attribute changes: {len(comp['attribute_changes'])}")
        
        # Invalid files
        if report.invalid_files > 0:
            print(f"\nInvalid Files ({report.invalid_files}):")
            for result in report.file_results:
                if not result.is_valid:
                    print(f"\n  {result.filename}:")
                    for error in result.errors[:3]:  # Show first 3 errors
                        print(f"      Error: {error}")
        
        # Summary
        print("\n" + "=" * 70)
        if report.invalid_files == 0 and report.total_errors == 0:
            print("ALL FILES VALID - SYSTEM READY FOR DEPLOYMENT")
        elif report.invalid_files == 0:
            print(f" ALL FILES VALID BUT {report.total_warnings} WARNINGS")
        else:
            print(f"{report.invalid_files} INVALID FILES - REVIEW REQUIRED")
        print("=" * 70)
    
    def save_report(self, report: FinalValidationReport, output_file: Path):
        """
        Save report to JSON file.
        
        Args:
            report: FinalValidationReport to save
            output_file: Output file path
        """
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report.to_dict(), f, indent=2, ensure_ascii=False)
        
        print(f"\nReport saved to: {output_file}")


def validate_final_system(
    firmen: Optional[List[int]] = None,
    seiten: Optional[List[int]] = None,
    run_test: bool = True,
    output_file: Optional[Path] = None
) -> FinalValidationReport:
    """
    Convenience function to validate the final system.
    
    Args:
        firmen: List of firma numbers (default: all)
        seiten: List of seite numbers (default: all)
        run_test: Whether to run complete test workflow
        output_file: Optional output file for report
        
    Returns:
        FinalValidationReport
        
    Example:
        >>> # Validate all files
        >>> report = validate_final_system()
        
        >>> # Validate specific combinations
        >>> report = validate_final_system(firmen=[1, 2], seiten=[1, 2, 3])
        
        >>> # Validate without running test
        >>> report = validate_final_system(run_test=False)
    """
    validator = FinalValidator()
    report = validator.generate_final_report(
        firmen=firmen,
        seiten=seiten,
        run_test=run_test
    )
    
    validator.display_report(report)
    
    if output_file:
        validator.save_report(report, output_file)
    
    return report


if __name__ == "__main__":
    # Run final validation
    print("\n=== Final Validator Demo ===\n")
    
    # Validate all files
    report = validate_final_system(
        run_test=True,
        output_file=Path("multi_pdf_positioning/final_validation_report.json")
    )
    
    # Exit with appropriate code
    import sys
    sys.exit(0 if report.invalid_files == 0 else 1)
