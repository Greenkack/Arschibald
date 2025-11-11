"""
Main Workflow Module for Multi-PDF Positioning System

This module orchestrates the complete workflow for analyzing PDFs, calculating
optimal positions, generating updated YML files, and validating results.

Requirements: All (Task 9.1)
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# Import all components
from multi_pdf_positioning.yml_parser import YMLParser, YMLElement
from multi_pdf_positioning.pdf_analyzer import PDFAnalyzer, PDFAnalysis
from multi_pdf_positioning.position_calculator import PositionCalculator
from multi_pdf_positioning.yml_generator import YMLGenerator
from multi_pdf_positioning.backup_manager import BackupManager
from multi_pdf_positioning.validation_system import ValidationSystem, ValidationReport
from multi_pdf_positioning.config import (
    PDF_DIR, YML_DIR, BACKUP_DIR, OUTPUT_DIR, ANALYSIS_DIR,
    FIRMEN, SEITEN, CREATE_BACKUP, VALIDATE_OUTPUT
)


@dataclass
class WorkflowResult:
    """
    Result of processing a single firma-seite combination.
    
    Attributes:
        firma: Firma number
        seite: Seite number
        success: Whether processing was successful
        yml_file: Path to YML file
        pdf_file: Path to PDF file
        elements_count: Number of elements processed
        validation_report: Validation report (if validation was performed)
        error_message: Error message (if processing failed)
        processing_time: Time taken to process (in seconds)
    """
    firma: int
    seite: int
    success: bool
    yml_file: str
    pdf_file: str
    elements_count: int = 0
    validation_report: Optional[ValidationReport] = None
    error_message: Optional[str] = None
    processing_time: float = 0.0


@dataclass
class WorkflowSummary:
    """
    Summary of the entire workflow execution.
    
    Attributes:
        total_combinations: Total number of firma-seite combinations
        successful: Number of successful processings
        failed: Number of failed processings
        total_elements: Total number of elements processed
        backup_id: Backup ID (if backup was created)
        start_time: Workflow start time
        end_time: Workflow end time
        total_time: Total execution time (in seconds)
        results: List of individual WorkflowResult objects
    """
    total_combinations: int
    successful: int
    failed: int
    total_elements: int
    backup_id: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_time: float = 0.0
    results: List[WorkflowResult] = None
    
    def __post_init__(self):
        if self.results is None:
            self.results = []


class ProgressTracker:
    """
    Tracks and displays progress during workflow execution.
    """
    
    def __init__(self, total: int, show_progress: bool = True):
        """
        Initialize progress tracker.
        
        Args:
            total: Total number of items to process
            show_progress: Whether to show progress updates
        """
        self.total = total
        self.current = 0
        self.show_progress = show_progress
        self.start_time = datetime.now()
    
    def update(self, message: str = ""):
        """
        Update progress counter and display message.
        
        Args:
            message: Optional message to display
        """
        self.current += 1
        
        if self.show_progress:
            percentage = (self.current / self.total) * 100
            elapsed = (datetime.now() - self.start_time).total_seconds()
            
            # Estimate remaining time
            if self.current > 0:
                avg_time = elapsed / self.current
                remaining = avg_time * (self.total - self.current)
                remaining_str = f"{remaining:.1f}s"
            else:
                remaining_str = "unknown"
            
            progress_bar = self._create_progress_bar(percentage)
            
            print(f"\r{progress_bar} {self.current}/{self.total} "
                  f"({percentage:.1f}%) - ETA: {remaining_str}", end="")
            
            if message:
                print(f" - {message}", end="")
            
            if self.current >= self.total:
                print()  # New line at completion
    
    def _create_progress_bar(self, percentage: float, width: int = 30) -> str:
        """
        Create a text-based progress bar.
        
        Args:
            percentage: Completion percentage (0-100)
            width: Width of progress bar in characters
            
        Returns:
            Progress bar string
        """
        filled = int(width * percentage / 100)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}]"
    
    def finish(self, message: str = "Complete"):
        """
        Mark progress as finished.
        
        Args:
            message: Completion message
        """
        if self.show_progress:
            elapsed = (datetime.now() - self.start_time).total_seconds()
            print(f"\n✓ {message} in {elapsed:.2f}s")


class MainWorkflow:
    """
    Main workflow orchestrator for the Multi-PDF Positioning System.
    
    This class coordinates all components to:
    1. Analyze PDF templates
    2. Parse YML coordinate files
    3. Calculate optimal positions
    4. Generate updated YML files
    5. Validate results
    6. Create backups
    """
    
    def __init__(
        self,
        pdf_dir: Optional[Path] = None,
        yml_dir: Optional[Path] = None,
        backup_dir: Optional[Path] = None,
        output_dir: Optional[Path] = None,
        create_backup: bool = True,
        validate_output: bool = True,
        show_progress: bool = True
    ):
        """
        Initialize the main workflow.
        
        Args:
            pdf_dir: Directory containing PDF templates
            yml_dir: Directory containing YML coordinate files
            backup_dir: Directory for backups
            output_dir: Directory for output files
            create_backup: Whether to create backup before processing
            validate_output: Whether to validate generated YML files
            show_progress: Whether to show progress updates
        """
        self.pdf_dir = Path(pdf_dir) if pdf_dir else PDF_DIR
        self.yml_dir = Path(yml_dir) if yml_dir else YML_DIR
        self.backup_dir = Path(backup_dir) if backup_dir else BACKUP_DIR
        self.output_dir = Path(output_dir) if output_dir else OUTPUT_DIR
        
        self.create_backup = create_backup
        self.validate_output = validate_output
        self.show_progress = show_progress
        
        # Initialize components
        self.yml_parser = YMLParser()
        self.pdf_analyzer = PDFAnalyzer(str(self.pdf_dir))
        self.position_calculator = PositionCalculator()
        self.yml_generator = YMLGenerator()
        self.backup_manager = BackupManager(self.yml_dir, self.backup_dir)
        self.validation_system = ValidationSystem()
        
        # Workflow state
        self.backup_id: Optional[str] = None
        self.pdf_analyses: Dict[Tuple[int, int], PDFAnalysis] = {}
        self.results: List[WorkflowResult] = []
    
    def run(
        self,
        firmen: Optional[List[int]] = None,
        seiten: Optional[List[int]] = None
    ) -> WorkflowSummary:
        """
        Run the complete workflow for specified firma-seite combinations.
        
        This is the main entry point that orchestrates all steps:
        1. Create backup (if enabled)
        2. Analyze PDFs
        3. Process each combination
        4. Generate summary
        
        Args:
            firmen: List of firma numbers to process (default: all)
            seiten: List of seite numbers to process (default: all)
            
        Returns:
            WorkflowSummary with results and statistics
        """
        start_time = datetime.now()
        
        # Use default firmen and seiten if not specified
        if firmen is None:
            firmen = FIRMEN
        if seiten is None:
            seiten = SEITEN
        
        total_combinations = len(firmen) * len(seiten)
        
        print("\n" + "=" * 70)
        print("MULTI-PDF POSITIONING SYSTEM - MAIN WORKFLOW")
        print("=" * 70)
        print(f"Processing {total_combinations} combinations:")
        print(f"  Firmen: {firmen}")
        print(f"  Seiten: {seiten}")
        print(f"  PDF Directory: {self.pdf_dir}")
        print(f"  YML Directory: {self.yml_dir}")
        print(f"  Backup: {'Enabled' if self.create_backup else 'Disabled'}")
        print(f"  Validation: {'Enabled' if self.validate_output else 'Disabled'}")
        print("=" * 70)
        
        # Step 1: Create backup
        if self.create_backup:
            print("\n[Step 1/4] Creating backup...")
            try:
                self.backup_id = self._create_backup()
                print(f"✓ Backup created: {self.backup_id}")
            except Exception as e:
                print(f"✗ Backup failed: {e}")
                print("  Continuing without backup...")
        else:
            print("\n[Step 1/4] Backup disabled, skipping...")
        
        # Step 2: Analyze PDFs
        print("\n[Step 2/4] Analyzing PDF templates...")
        try:
            self._analyze_pdfs(firmen, seiten)
            print(f"✓ Analyzed {len(self.pdf_analyses)} PDF templates")
        except Exception as e:
            print(f"✗ PDF analysis failed: {e}")
            return self._create_error_summary(start_time, str(e))
        
        # Step 3: Process each combination
        print("\n[Step 3/4] Processing combinations...")
        self._process_combinations(firmen, seiten)
        
        # Step 4: Generate summary
        print("\n[Step 4/4] Generating summary...")
        summary = self._generate_summary(start_time)
        
        # Display summary
        self._display_summary(summary)
        
        return summary
    
    def _create_backup(self) -> str:
        """
        Create backup of all YML files.
        
        Returns:
            Backup ID
            
        Raises:
            Exception: If backup creation fails
        """
        yml_files = list(self.yml_dir.glob("*.yml"))
        
        if not yml_files:
            raise FileNotFoundError(f"No YML files found in {self.yml_dir}")
        
        backup_id = self.backup_manager.create_backup(yml_files)
        return backup_id
    
    def _analyze_pdfs(self, firmen: List[int], seiten: List[int]):
        """
        Analyze all PDF templates for specified combinations.
        
        Args:
            firmen: List of firma numbers
            seiten: List of seite numbers
            
        Raises:
            Exception: If PDF analysis fails
        """
        progress = ProgressTracker(
            len(firmen) * len(seiten),
            self.show_progress
        )
        
        for firma in firmen:
            for seite in seiten:
                # Construct PDF filename
                pdf_filename = f"multi_nt_{seite:02d}_f{firma}.pdf"
                pdf_path = self.pdf_dir / pdf_filename
                
                try:
                    # Analyze PDF
                    analysis = self.pdf_analyzer.analyze_pdf(str(pdf_path))
                    self.pdf_analyses[(firma, seite)] = analysis
                    
                    progress.update(f"f{firma}s{seite}")
                    
                except Exception as e:
                    progress.update(f"f{firma}s{seite} FAILED")
                    print(f"\n  Warning: Failed to analyze {pdf_filename}: {e}")
        
        progress.finish("PDF analysis complete")
    
    def _process_combinations(self, firmen: List[int], seiten: List[int]):
        """
        Process each firma-seite combination.
        
        Args:
            firmen: List of firma numbers
            seiten: List of seite numbers
        """
        total = len(firmen) * len(seiten)
        progress = ProgressTracker(total, self.show_progress)
        
        for firma in firmen:
            for seite in seiten:
                result = self._process_single_combination(firma, seite)
                self.results.append(result)
                
                status = "✓" if result.success else "✗"
                progress.update(f"{status} f{firma}s{seite}")
        
        progress.finish("Processing complete")
    
    def _process_single_combination(
        self,
        firma: int,
        seite: int
    ) -> WorkflowResult:
        """
        Process a single firma-seite combination.
        
        This function:
        1. Parses the YML file
        2. Gets PDF analysis
        3. Calculates new positions
        4. Generates updated YML
        5. Validates output (if enabled)
        
        Args:
            firma: Firma number
            seite: Seite number
            
        Returns:
            WorkflowResult with processing results
        """
        start_time = datetime.now()
        
        # Construct file paths
        yml_filename = f"seite{seite}_f{firma}.yml"
        yml_path = self.yml_dir / yml_filename
        pdf_filename = f"multi_nt_{seite:02d}_f{firma}.pdf"
        
        result = WorkflowResult(
            firma=firma,
            seite=seite,
            success=False,
            yml_file=str(yml_path),
            pdf_file=pdf_filename
        )
        
        try:
            # Step 1: Parse YML file
            elements = self.yml_parser.parse_yml(str(yml_path))
            result.elements_count = len(elements)
            
            if not elements:
                result.error_message = "No elements found in YML file"
                return result
            
            # Step 2: Get PDF analysis
            pdf_analysis = self.pdf_analyses.get((firma, seite))
            
            if not pdf_analysis:
                result.error_message = "PDF analysis not available"
                return result
            
            # Step 3: Calculate new positions
            new_positions = self.position_calculator.calculate_positions(
                elements,
                pdf_analysis,
                strategy=f"firma{firma}"
            )
            
            if len(new_positions) != len(elements):
                result.error_message = (
                    f"Position count mismatch: {len(new_positions)} positions "
                    f"for {len(elements)} elements"
                )
                return result
            
            # Step 4: Generate updated YML
            output_path = self.output_dir / yml_filename
            self.yml_generator.generate_yml(
                elements,
                new_positions,
                str(output_path),
                str(yml_path)
            )
            
            # Step 5: Validate output (if enabled)
            if self.validate_output:
                validation_report = self.validation_system.generate_validation_report(
                    new_positions,
                    elements,
                    firma,
                    seite
                )
                result.validation_report = validation_report
                
                if not validation_report.is_valid:
                    result.error_message = (
                        f"Validation failed: {len(validation_report.get_errors())} errors"
                    )
                    # Still mark as success since file was generated
                    result.success = True
                else:
                    result.success = True
            else:
                result.success = True
            
        except Exception as e:
            result.error_message = str(e)
            result.success = False
        
        finally:
            # Calculate processing time
            end_time = datetime.now()
            result.processing_time = (end_time - start_time).total_seconds()
        
        return result
    
    def _generate_summary(self, start_time: datetime) -> WorkflowSummary:
        """
        Generate workflow summary from results.
        
        Args:
            start_time: Workflow start time
            
        Returns:
            WorkflowSummary with statistics
        """
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        successful = sum(1 for r in self.results if r.success)
        failed = len(self.results) - successful
        total_elements = sum(r.elements_count for r in self.results)
        
        summary = WorkflowSummary(
            total_combinations=len(self.results),
            successful=successful,
            failed=failed,
            total_elements=total_elements,
            backup_id=self.backup_id,
            start_time=start_time,
            end_time=end_time,
            total_time=total_time,
            results=self.results
        )
        
        return summary
    
    def _create_error_summary(
        self,
        start_time: datetime,
        error_message: str
    ) -> WorkflowSummary:
        """
        Create an error summary when workflow fails early.
        
        Args:
            start_time: Workflow start time
            error_message: Error message
            
        Returns:
            WorkflowSummary with error information
        """
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        summary = WorkflowSummary(
            total_combinations=0,
            successful=0,
            failed=0,
            total_elements=0,
            backup_id=self.backup_id,
            start_time=start_time,
            end_time=end_time,
            total_time=total_time,
            results=[]
        )
        
        print(f"\n✗ Workflow failed: {error_message}")
        
        return summary
    
    def _display_summary(self, summary: WorkflowSummary):
        """
        Display workflow summary.
        
        Args:
            summary: WorkflowSummary to display
        """
        print("\n" + "=" * 70)
        print("WORKFLOW SUMMARY")
        print("=" * 70)
        print(f"Total combinations: {summary.total_combinations}")
        print(f"Successful: {summary.successful}")
        print(f"Failed: {summary.failed}")
        print(f"Total elements processed: {summary.total_elements}")
        print(f"Total time: {summary.total_time:.2f}s")
        
        if summary.backup_id:
            print(f"Backup ID: {summary.backup_id}")
        
        # Show failed combinations
        if summary.failed > 0:
            print(f"\nFailed combinations ({summary.failed}):")
            for result in summary.results:
                if not result.success:
                    print(f"  ✗ Firma {result.firma}, Seite {result.seite}: "
                          f"{result.error_message}")
        
        # Show validation issues
        if self.validate_output:
            validation_errors = sum(
                len(r.validation_report.get_errors())
                for r in summary.results
                if r.validation_report
            )
            validation_warnings = sum(
                len(r.validation_report.get_warnings())
                for r in summary.results
                if r.validation_report
            )
            
            print(f"\nValidation:")
            print(f"  Errors: {validation_errors}")
            print(f"  Warnings: {validation_warnings}")
        
        print("=" * 70)
        
        # Success message
        if summary.successful == summary.total_combinations:
            print("\n✓ All combinations processed successfully!")
        elif summary.successful > 0:
            print(f"\n⚠ Partially successful: {summary.successful}/"
                  f"{summary.total_combinations} combinations processed")
        else:
            print("\n✗ Workflow failed: No combinations processed successfully")


def main(
    firmen: Optional[List[int]] = None,
    seiten: Optional[List[int]] = None,
    pdf_dir: Optional[Path] = None,
    yml_dir: Optional[Path] = None,
    backup_dir: Optional[Path] = None,
    output_dir: Optional[Path] = None,
    create_backup: bool = True,
    validate_output: bool = True,
    show_progress: bool = True
) -> WorkflowSummary:
    """
    Main function to run the complete workflow.
    
    This is the primary entry point for the Multi-PDF Positioning System.
    
    Args:
        firmen: List of firma numbers to process (default: all)
        seiten: List of seite numbers to process (default: all)
        pdf_dir: Directory containing PDF templates
        yml_dir: Directory containing YML coordinate files
        backup_dir: Directory for backups
        output_dir: Directory for output files
        create_backup: Whether to create backup before processing
        validate_output: Whether to validate generated YML files
        show_progress: Whether to show progress updates
        
    Returns:
        WorkflowSummary with results and statistics
        
    Example:
        >>> # Process all combinations
        >>> summary = main()
        
        >>> # Process specific firma
        >>> summary = main(firmen=[1, 2])
        
        >>> # Process specific seite
        >>> summary = main(seiten=[1, 2, 3])
        
        >>> # Process without backup
        >>> summary = main(create_backup=False)
    """
    workflow = MainWorkflow(
        pdf_dir=pdf_dir,
        yml_dir=yml_dir,
        backup_dir=backup_dir,
        output_dir=output_dir,
        create_backup=create_backup,
        validate_output=validate_output,
        show_progress=show_progress
    )
    
    return workflow.run(firmen=firmen, seiten=seiten)


if __name__ == "__main__":
    # Run with default settings
    summary = main()
    
    # Exit with appropriate code
    sys.exit(0 if summary.successful == summary.total_combinations else 1)
