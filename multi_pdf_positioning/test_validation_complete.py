"""
Comprehensive Validation Tests for Multi-PDF Positioning System

This test suite validates all generated YML files to ensure:
- No positions are outside PDF bounds
- No overlapping elements exist
- Only positions have changed (all other attributes preserved)
- YML format is valid

Requirements covered: Task 11.3
"""

import os
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from multi_pdf_positioning.yml_parser import YMLParser, YMLElement
from multi_pdf_positioning.validation_system import ValidationSystem, ValidationReport
from multi_pdf_positioning.yml_generator import YMLGenerator


class ValidationTestSuite:
    """
    Comprehensive validation test suite for generated YML files.
    """
    
    def __init__(self, coords_dir: str = "coords_multi", backup_dir: str = "coords_multi_backup"):
        """
        Initialize the validation test suite.
        
        Args:
            coords_dir: Directory containing generated YML files
            backup_dir: Directory containing original YML backups
        """
        self.coords_dir = Path(coords_dir)
        self.backup_dir = Path(backup_dir)
        self.validator = ValidationSystem()
        self.parser = YMLParser()
        self.generator = YMLGenerator()
        
        self.test_results: Dict[str, Dict] = {}
        self.summary: Dict[str, int] = {
            "total_files": 0,
            "passed": 0,
            "failed": 0,
            "total_elements": 0,
            "total_errors": 0,
            "total_warnings": 0,
            "total_collisions": 0
        }
    
    def find_latest_backup(self) -> Path:
        """
        Find the most recent backup directory.
        
        Returns:
            Path to the latest backup directory
            
        Raises:
            FileNotFoundError: If no backup directory exists
        """
        if not self.backup_dir.exists():
            raise FileNotFoundError(f"Backup directory not found: {self.backup_dir}")
        
        # Find all backup subdirectories
        backup_dirs = [d for d in self.backup_dir.iterdir() if d.is_dir()]
        
        if not backup_dirs:
            raise FileNotFoundError(f"No backup subdirectories found in {self.backup_dir}")
        
        # Sort by name (which includes timestamp) and get the latest
        latest_backup = sorted(backup_dirs, reverse=True)[0]
        return latest_backup
    
    def get_yml_files(self) -> List[Path]:
        """
        Get all YML files to validate.
        
        Returns:
            List of Path objects for YML files
        """
        if not self.coords_dir.exists():
            return []
        
        yml_files = list(self.coords_dir.glob("seite*_f*.yml"))
        return sorted(yml_files)
    
    def test_positions_within_bounds(
        self,
        yml_file: Path
    ) -> Tuple[bool, List[str]]:
        """
        Test that all positions are within PDF bounds.
        
        Args:
            yml_file: Path to YML file to test
            
        Returns:
            Tuple of (passed, list_of_errors)
        """
        errors = []
        
        try:
            # Parse YML file
            elements = self.parser.parse_yml(str(yml_file))
            
            # Extract positions
            positions = [elem.position for elem in elements]
            
            # Validate positions
            report = self.validator.validate_positions(positions, elements)
            
            # Check for boundary errors
            for msg in report.get_errors():
                if any(keyword in msg.message.lower() for keyword in 
                      ['exceeds', 'negative', 'invalid']):
                    errors.append(msg.message)
            
            return len(errors) == 0, errors
            
        except Exception as e:
            errors.append(f"Exception during bounds test: {str(e)}")
            return False, errors
    
    def test_no_overlaps(
        self,
        yml_file: Path
    ) -> Tuple[bool, List[str]]:
        """
        Test that no elements overlap.
        
        Args:
            yml_file: Path to YML file to test
            
        Returns:
            Tuple of (passed, list_of_errors)
        """
        errors = []
        
        try:
            # Parse YML file
            elements = self.parser.parse_yml(str(yml_file))
            
            # Extract positions
            positions = [elem.position for elem in elements]
            
            # Detect collisions
            collisions = self.validator.detect_collisions(positions)
            
            if collisions:
                errors.append(f"Found {len(collisions)} collision(s)")
                for collision in collisions[:5]:  # Show first 5
                    errors.append(
                        f"  Elements {collision.element1_index} and "
                        f"{collision.element2_index} overlap "
                        f"({collision.overlap_area:.2f} sq pts)"
                    )
            
            return len(collisions) == 0, errors
            
        except Exception as e:
            errors.append(f"Exception during overlap test: {str(e)}")
            return False, errors
    
    def test_only_positions_changed(
        self,
        yml_file: Path,
        original_file: Path
    ) -> Tuple[bool, List[str]]:
        """
        Test that only positions have changed compared to original.
        
        Args:
            yml_file: Path to generated YML file
            original_file: Path to original YML file
            
        Returns:
            Tuple of (passed, list_of_errors)
        """
        errors = []
        
        try:
            # Parse both files
            generated_elements = self.parser.parse_yml(str(yml_file))
            original_elements = self.parser.parse_yml(str(original_file))
            
            # Check element count
            if len(generated_elements) != len(original_elements):
                errors.append(
                    f"Element count mismatch: "
                    f"original={len(original_elements)}, "
                    f"generated={len(generated_elements)}"
                )
                return False, errors
            
            # Compare each element
            for i, (gen, orig) in enumerate(zip(generated_elements, original_elements)):
                # Text must be identical
                if gen.text != orig.text:
                    errors.append(
                        f"Element {i}: Text changed from '{orig.text}' to '{gen.text}'"
                    )
                
                # Font must be identical
                if gen.font != orig.font:
                    errors.append(
                        f"Element {i}: Font changed from '{orig.font}' to '{gen.font}'"
                    )
                
                # Font size must be identical
                if gen.font_size != orig.font_size:
                    errors.append(
                        f"Element {i}: Font size changed from {orig.font_size} "
                        f"to {gen.font_size}"
                    )
                
                # Color must be identical
                if gen.color != orig.color:
                    errors.append(
                        f"Element {i}: Color changed from {orig.color} to {gen.color}"
                    )
            
            return len(errors) == 0, errors
            
        except Exception as e:
            errors.append(f"Exception during comparison test: {str(e)}")
            return False, errors
    
    def test_yml_format_valid(
        self,
        yml_file: Path
    ) -> Tuple[bool, List[str]]:
        """
        Test that YML format is valid.
        
        Args:
            yml_file: Path to YML file to test
            
        Returns:
            Tuple of (passed, list_of_errors)
        """
        errors = []
        
        try:
            # Try to parse the file
            elements = self.parser.parse_yml(str(yml_file))
            
            # Validate elements
            is_valid, validation_errors = self.parser.validate_elements()
            
            if not is_valid:
                errors.extend(validation_errors)
            
            # Check that we got some elements
            if len(elements) == 0:
                errors.append("No elements found in YML file")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            errors.append(f"Exception during format validation: {str(e)}")
            return False, errors
    
    def validate_single_file(
        self,
        yml_file: Path,
        original_file: Optional[Path] = None
    ) -> Dict:
        """
        Run all validation tests on a single YML file.
        
        Args:
            yml_file: Path to YML file to validate
            original_file: Path to original YML file for comparison
            
        Returns:
            Dictionary with test results
        """
        result = {
            "file": yml_file.name,
            "passed": True,
            "tests": {},
            "errors": [],
            "warnings": [],
            "element_count": 0,
            "collision_count": 0
        }
        
        # Test 1: Positions within bounds
        passed, errors = self.test_positions_within_bounds(yml_file)
        result["tests"]["bounds"] = passed
        if not passed:
            result["passed"] = False
            result["errors"].extend(errors)
        
        # Test 2: No overlaps
        passed, errors = self.test_no_overlaps(yml_file)
        result["tests"]["overlaps"] = passed
        if not passed:
            result["passed"] = False
            result["errors"].extend(errors)
            # Count collisions
            try:
                elements = self.parser.parse_yml(str(yml_file))
                positions = [elem.position for elem in elements]
                collisions = self.validator.detect_collisions(positions)
                result["collision_count"] = len(collisions)
            except:
                pass
        
        # Test 3: Only positions changed (if original available)
        if original_file and original_file.exists():
            passed, errors = self.test_only_positions_changed(yml_file, original_file)
            result["tests"]["attributes_preserved"] = passed
            if not passed:
                result["passed"] = False
                result["errors"].extend(errors)
        
        # Test 4: YML format valid
        passed, errors = self.test_yml_format_valid(yml_file)
        result["tests"]["format_valid"] = passed
        if not passed:
            result["passed"] = False
            result["errors"].extend(errors)
        
        # Get element count
        try:
            elements = self.parser.parse_yml(str(yml_file))
            result["element_count"] = len(elements)
        except:
            result["element_count"] = 0
        
        # Generate validation report
        try:
            elements = self.parser.parse_yml(str(yml_file))
            positions = [elem.position for elem in elements]
            
            # Extract firma and seite from filename
            # Format: seite[1-8]_f[1-6].yml
            import re
            match = re.match(r'seite(\d+)_f(\d+)\.yml', yml_file.name)
            if match:
                seite = int(match.group(1))
                firma = int(match.group(2))
            else:
                seite = None
                firma = None
            
            report = self.validator.generate_validation_report(
                positions, elements, firma, seite
            )
            
            result["warnings"] = [msg.message for msg in report.get_warnings()]
            
        except Exception as e:
            result["errors"].append(f"Failed to generate validation report: {str(e)}")
        
        return result
    
    def validate_all_files(self) -> Dict:
        """
        Validate all YML files in the coords directory.
        
        Returns:
            Dictionary with complete validation results
        """
        print("\n" + "=" * 70)
        print("COMPREHENSIVE VALIDATION TEST SUITE")
        print("=" * 70)
        
        # Get YML files
        yml_files = self.get_yml_files()
        
        if not yml_files:
            print(f"\n[ERROR] No YML files found in {self.coords_dir}")
            return {"error": "No YML files found"}
        
        print(f"\nFound {len(yml_files)} YML files to validate")
        
        # Try to find backup directory for comparison
        try:
            backup_path = self.find_latest_backup()
            print(f"Using backup: {backup_path}")
        except FileNotFoundError as e:
            print(f"Warning: {e}")
            print("Skipping attribute preservation tests")
            backup_path = None
        
        print("\n" + "-" * 70)
        print("Running validation tests...")
        print("-" * 70)
        
        # Validate each file
        for yml_file in yml_files:
            print(f"\nValidating: {yml_file.name}")
            
            # Find corresponding original file
            original_file = None
            if backup_path:
                if yml_file != 0:
                    original_file = backup_path / yml_file.name
                else:
                    original_file = 0.0
            
            # Run validation
            result = self.validate_single_file(yml_file, original_file)
            self.test_results[yml_file.name] = result
            
            # Update summary
            self.summary["total_files"] += 1
            self.summary["total_elements"] += result["element_count"]
            self.summary["total_collisions"] += result["collision_count"]
            
            if result["passed"]:
                self.summary["passed"] += 1
                print(f"  [OK] PASSED")
            else:
                self.summary["failed"] += 1
                print(f"  [ERROR] FAILED")
                self.summary["total_errors"] += len(result["errors"])
                
                # Show first few errors
                for error in result["errors"][:3]:
                    print(f"    - {error}")
                if len(result["errors"]) > 3:
                    print(f"    ... and {len(result["errors"]) - 3} more errors")
            
            if result["warnings"]:
                self.summary["total_warnings"] += len(result["warnings"])
                print(f"  ⚠ {len(result['warnings'])} warning(s)")
        
        return self.generate_report()
    
    def generate_report(self) -> Dict:
        """
        Generate a comprehensive validation report.
        
        Returns:
            Dictionary with complete report data
        """
        print("\n" + "=" * 70)
        print("VALIDATION SUMMARY")
        print("=" * 70)
        
        print(f"\nFiles Tested: {self.summary['total_files']}")
        print(f"  [OK] Passed: {self.summary['passed']}")
        print(f"  [ERROR] Failed: {self.summary['failed']}")
        
        print(f"\nElements Validated: {self.summary['total_elements']}")
        print(f"Total Errors: {self.summary['total_errors']}")
        print(f"Total Warnings: {self.summary['total_warnings']}")
        print(f"Total Collisions: {self.summary['total_collisions']}")
        
        # Calculate pass rate
        if self.summary['total_files'] > 0:
            pass_rate = (self.summary['passed'] / self.summary['total_files']) * 100
            print(f"\nPass Rate: {pass_rate:.1f}%")
        
        # Show failed files
        failed_files = [
            name for name, result in self.test_results.items()
            if not result["passed"]
        ]
        
        if failed_files:
            print(f"\nFailed Files ({len(failed_files)}):")
            for name in failed_files:
                print(f"  - {name}")
                result = self.test_results[name]
                print(f"    Errors: {len(result['errors'])}")
                print(f"    Collisions: {result['collision_count']}")
        
        # Show files with warnings
        warning_files = [
            name for name, result in self.test_results.items()
            if result["warnings"]
        ]
        
        if warning_files:
            print(f"\nFiles with Warnings ({len(warning_files)}):")
            for name in warning_files[:10]:  # Show first 10
                result = self.test_results[name]
                print(f"  - {name}: {len(result['warnings'])} warning(s)")
        
        print("\n" + "=" * 70)
        
        # Overall result
        if self.summary['failed'] == 0:
            print("[OK] ALL VALIDATION TESTS PASSED")
        else:
            print(f"[ERROR] {self.summary['failed']} FILE(S) FAILED VALIDATION")
        
        print("=" * 70)
        
        # Create report dictionary
        report = {
            "summary": self.summary,
            "test_results": self.test_results,
            "failed_files": failed_files,
            "warning_files": warning_files,
            "overall_passed": self.summary['failed'] == 0
        }
        
        return report
    
    def save_report(self, output_file: str = "multi_pdf_positioning/validation_report.json"):
        """
        Save validation report to JSON file.
        
        Args:
            output_file: Path to output JSON file
        """
        report = {
            "summary": self.summary,
            "test_results": self.test_results
        }
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n[OK] Report saved to: {output_file}")


def run_validation_tests(
    coords_dir: str = "coords_multi",
    backup_dir: str = "coords_multi_backup",
    save_report: bool = True
) -> bool:
    """
    Run comprehensive validation tests on all YML files.
    
    Args:
        coords_dir: Directory containing generated YML files
        backup_dir: Directory containing original YML backups
        save_report: Whether to save report to JSON file
        
    Returns:
        True if all tests passed, False otherwise
    """
    suite = ValidationTestSuite(coords_dir, backup_dir)
    report = suite.validate_all_files()
    
    if save_report:
        suite.save_report()
    
    return report.get("overall_passed", False)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Comprehensive validation tests for Multi-PDF Positioning System"
    )
    parser.add_argument(
        "--coords-dir",
        default="coords_multi",
        help="Directory containing generated YML files"
    )
    parser.add_argument(
        "--backup-dir",
        default="coords_multi_backup",
        help="Directory containing original YML backups"
    )
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save report to JSON file"
    )
    
    args = parser.parse_args()
    
    # Run validation tests
    success = run_validation_tests(
        coords_dir=args.coords_dir,
        backup_dir=args.backup_dir,
        save_report=not args.no_save
    )
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
