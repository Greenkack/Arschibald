"""
Batch Processing Module for Multi-PDF Positioning System

This module provides batch processing capabilities with:
- Processing of all 48 combinations
- Optional parallel processing for improved performance
- Comprehensive logging for each step
- Error handling and recovery

Requirements: All (Task 9.2)
"""

import logging
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Callable
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from dataclasses import dataclass, field

# Import workflow components
from multi_pdf_positioning.yml_parser import YMLParser, YMLElement
from multi_pdf_positioning.pdf_analyzer import PDFAnalyzer, PDFAnalysis
from multi_pdf_positioning.position_calculator import PositionCalculator
from multi_pdf_positioning.yml_generator import YMLGenerator
from multi_pdf_positioning.validation_system import ValidationSystem, ValidationReport
from multi_pdf_positioning.config import (
    PDF_DIR, YML_DIR, OUTPUT_DIR, FIRMEN, SEITEN, LOG_FILE
)


@dataclass
class BatchResult:
    """
    Result of batch processing.
    
    Attributes:
        firma: Firma number
        seite: Seite number
        success: Whether processing was successful
        elements_count: Number of elements processed
        processing_time: Time taken (in seconds)
        validation_passed: Whether validation passed
        error_message: Error message (if failed)
        warnings: List of warning messages
    """
    firma: int
    seite: int
    success: bool
    elements_count: int = 0
    processing_time: float = 0.0
    validation_passed: bool = False
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)


@dataclass
class BatchSummary:
    """
    Summary of batch processing.
    
    Attributes:
        total_processed: Total number of combinations processed
        successful: Number of successful processings
        failed: Number of failed processings
        total_elements: Total number of elements processed
        total_time: Total execution time (in seconds)
        avg_time_per_combination: Average time per combination
        results: List of BatchResult objects
        parallel_processing: Whether parallel processing was used
        worker_count: Number of parallel workers (if applicable)
    """
    total_processed: int
    successful: int
    failed: int
    total_elements: int
    total_time: float
    avg_time_per_combination: float
    results: List[BatchResult]
    parallel_processing: bool = False
    worker_count: int = 1


class BatchLogger:
    """
    Logging system for batch processing.
    
    Provides structured logging with different levels and automatic
    file and console output.
    """
    
    def __init__(self, log_file: Optional[Path] = None, log_level: str = "INFO"):
        """
        Initialize batch logger.
        
        Args:
            log_file: Path to log file (uses default if None)
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        """
        self.log_file = log_file if log_file else LOG_FILE
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        
        # Ensure log directory exists
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Configure logging
        self._configure_logging()
    
    def _configure_logging(self):
        """Configure logging with file and console handlers."""
        # Create logger
        self.logger = logging.getLogger("batch_processor")
        self.logger.setLevel(self.log_level)
        
        # Remove existing handlers
        self.logger.handlers = []
        
        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        
        # File handler
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)  # Only INFO and above to console
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
    
    def info(self, message: str):
        """Log info message."""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error message."""
        self.logger.error(message)
    
    def debug(self, message: str):
        """Log debug message."""
        self.logger.debug(message)
    
    def log_step(self, step: str, firma: int, seite: int, message: str):
        """
        Log a processing step for a specific combination.
        
        Args:
            step: Step name (e.g., "PARSE", "ANALYZE", "CALCULATE")
            firma: Firma number
            seite: Seite number
            message: Log message
        """
        self.logger.info(f"[{step}] F{firma}S{seite}: {message}")
    
    def log_result(self, result: BatchResult):
        """
        Log a batch result.
        
        Args:
            result: BatchResult to log
        """
        status = "SUCCESS" if result.success else "FAILED"
        self.logger.info(
            f"[RESULT] F{result.firma}S{result.seite}: {status} - "
            f"{result.elements_count} elements in {result.processing_time:.2f}s"
        )
        
        if result.error_message:
            self.logger.error(
                f"F{result.firma}S{result.seite}: {result.error_message}"
            )
        
        for warning in result.warnings:
            self.logger.warning(
                f"F{result.firma}S{result.seite}: {warning}"
            )


class BatchProcessor:
    """
    Batch processor for processing all 48 firma-seite combinations.
    
    Supports both sequential and parallel processing with comprehensive
    logging and error handling.
    """
    
    def __init__(
        self,
        pdf_dir: Optional[Path] = None,
        yml_dir: Optional[Path] = None,
        output_dir: Optional[Path] = None,
        parallel: bool = False,
        max_workers: Optional[int] = None,
        log_file: Optional[Path] = None,
        log_level: str = "INFO"
    ):
        """
        Initialize batch processor.
        
        Args:
            pdf_dir: Directory containing PDF templates
            yml_dir: Directory containing YML coordinate files
            output_dir: Directory for output files
            parallel: Whether to use parallel processing
            max_workers: Maximum number of parallel workers (None = auto)
            log_file: Path to log file
            log_level: Logging level
        """
        self.pdf_dir = Path(pdf_dir) if pdf_dir else PDF_DIR
        self.yml_dir = Path(yml_dir) if yml_dir else YML_DIR
        self.output_dir = Path(output_dir) if output_dir else OUTPUT_DIR
        
        self.parallel = parallel
        self.max_workers = max_workers
        
        # Initialize logger
        self.logger = BatchLogger(log_file, log_level)
        
        # Initialize components
        self.yml_parser = YMLParser()
        self.pdf_analyzer = PDFAnalyzer(str(self.pdf_dir))
        self.position_calculator = PositionCalculator()
        self.yml_generator = YMLGenerator()
        self.validation_system = ValidationSystem()
        
        # Cache for PDF analyses
        self.pdf_analyses: Dict[Tuple[int, int], PDFAnalysis] = {}
        
        # Results
        self.results: List[BatchResult] = []
    
    def process_all(
        self,
        firmen: Optional[List[int]] = None,
        seiten: Optional[List[int]] = None
    ) -> BatchSummary:
        """
        Process all specified firma-seite combinations.
        
        Args:
            firmen: List of firma numbers (default: all)
            seiten: List of seite numbers (default: all)
            
        Returns:
            BatchSummary with processing results
        """
        start_time = datetime.now()
        
        # Use defaults if not specified
        if firmen is None:
            firmen = FIRMEN
        if seiten is None:
            seiten = SEITEN
        
        total = len(firmen) * len(seiten)
        
        self.logger.info("=" * 70)
        self.logger.info("BATCH PROCESSING STARTED")
        self.logger.info("=" * 70)
        self.logger.info(f"Total combinations: {total}")
        self.logger.info(f"Firmen: {firmen}")
        self.logger.info(f"Seiten: {seiten}")
        self.logger.info(f"Parallel processing: {self.parallel}")
        if self.parallel:
            workers = self.max_workers or (len(firmen) * len(seiten) // 4)
            self.logger.info(f"Max workers: {workers}")
        self.logger.info("=" * 70)
        
        # Pre-analyze all PDFs
        self.logger.info("\n[PHASE 1] Analyzing PDF templates...")
        self._analyze_all_pdfs(firmen, seiten)
        self.logger.info(f"Analyzed {len(self.pdf_analyses)} PDFs")
        
        # Process combinations
        self.logger.info("\n[PHASE 2] Processing combinations...")
        if self.parallel:
            self._process_parallel(firmen, seiten)
        else:
            self._process_sequential(firmen, seiten)
        
        # Generate summary
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        summary = self._generate_summary(total_time)
        
        # Log summary
        self._log_summary(summary)
        
        return summary
    
    def _analyze_all_pdfs(self, firmen: List[int], seiten: List[int]):
        """
        Pre-analyze all PDF templates.
        
        Args:
            firmen: List of firma numbers
            seiten: List of seite numbers
        """
        for firma in firmen:
            for seite in seiten:
                pdf_filename = f"multi_nt_{seite:02d}_f{firma}.pdf"
                if pdf_filename != 0:
                    pdf_path = self.pdf_dir / pdf_filename
                else:
                    pdf_path = 0.0
                
                try:
                    analysis = self.pdf_analyzer.analyze_pdf(str(pdf_path))
                    self.pdf_analyses[(firma, seite)] = analysis
                    self.logger.debug(f"Analyzed {pdf_filename}")
                except Exception as e:
                    self.logger.error(f"Failed to analyze {pdf_filename}: {e}")
    
    def _process_sequential(self, firmen: List[int], seiten: List[int]):
        """
        Process combinations sequentially.
        
        Args:
            firmen: List of firma numbers
            seiten: List of seite numbers
        """
        total = len(firmen) * len(seiten)
        current = 0
        
        for firma in firmen:
            for seite in seiten:
                current += 1
                self.logger.info(f"\nProcessing {current}/{total}: F{firma}S{seite}")
                
                result = self._process_single(firma, seite)
                self.results.append(result)
                self.logger.log_result(result)
    
    def _process_parallel(self, firmen: List[int], seiten: List[int]):
        """
        Process combinations in parallel.
        
        Args:
            firmen: List of firma numbers
            seiten: List of seite numbers
        """
        # Create list of all combinations
        combinations = [(f, s) for f in firmen for s in seiten]
        total = len(combinations)
        
        # Determine number of workers
        if self.max_workers:
            workers = self.max_workers
        else:
            # Auto-determine: use 1/4 of combinations or 4, whichever is larger
            workers = max(4, total // 4)
            workers = min(workers, 8)  # Cap at 8 workers
        
        self.logger.info(f"Using {workers} parallel workers")
        
        # Process in parallel using ThreadPoolExecutor
        # (ThreadPoolExecutor is better for I/O-bound tasks like file operations)
        with ThreadPoolExecutor(max_workers=workers) as executor:
            # Submit all tasks
            future_to_combination = {
                executor.submit(self._process_single, firma, seite): (firma, seite)
                for firma, seite in combinations
            }
            
            # Process completed tasks
            completed = 0
            for future in as_completed(future_to_combination):
                firma, seite = future_to_combination[future]
                completed += 1
                
                try:
                    result = future.result()
                    self.results.append(result)
                    
                    status = "" if result.success else ""
                    self.logger.info(
                        f"[{completed}/{total}] {status} F{firma}S{seite} - "
                        f"{result.processing_time:.2f}s"
                    )
                    
                except Exception as e:
                    self.logger.error(
                        f"[{completed}/{total}] F{firma}S{seite} - "
                        f"Exception: {e}"
                    )
                    
                    # Create error result
                    result = BatchResult(
                        firma=firma,
                        seite=seite,
                        success=False,
                        error_message=str(e)
                    )
                    self.results.append(result)
    
    def _process_single(self, firma: int, seite: int) -> BatchResult:
        """
        Process a single firma-seite combination.
        
        Args:
            firma: Firma number
            seite: Seite number
            
        Returns:
            BatchResult with processing results
        """
        start_time = datetime.now()
        
        result = BatchResult(
            firma=firma,
            seite=seite,
            success=False
        )
        
        try:
            # Step 1: Parse YML
            yml_filename = f"seite{seite}_f{firma}.yml"
            if yml_filename != 0:
                yml_path = self.yml_dir / yml_filename
            else:
                yml_path = 0.0
            
            self.logger.log_step("PARSE", firma, seite, f"Parsing {yml_filename}")
            elements = self.yml_parser.parse_yml(str(yml_path))
            result.elements_count = len(elements)
            
            if not elements:
                result.error_message = "No elements found in YML"
                return result
            
            # Step 2: Get PDF analysis
            self.logger.log_step("ANALYZE", firma, seite, "Getting PDF analysis")
            pdf_analysis = self.pdf_analyses.get((firma, seite))
            
            if not pdf_analysis:
                result.error_message = "PDF analysis not available"
                return result
            
            # Step 3: Calculate positions
            self.logger.log_step("CALCULATE", firma, seite, "Calculating positions")
            new_positions = self.position_calculator.calculate_positions(
                elements,
                pdf_analysis,
                strategy=f"firma{firma}"
            )
            
            if len(new_positions) != len(elements):
                result.error_message = (
                    f"Position count mismatch: {len(new_positions)} != {len(elements)}"
                )
                return result
            
            # Step 4: Generate YML
            if yml_filename != 0:
                output_path = self.output_dir / yml_filename
            else:
                output_path = 0.0
            self.logger.log_step("GENERATE", firma, seite, f"Generating {yml_filename}")
            
            self.yml_generator.generate_yml(
                elements,
                new_positions,
                str(output_path),
                str(yml_path)
            )
            
            # Step 5: Validate
            self.logger.log_step("VALIDATE", firma, seite, "Validating output")
            validation_report = self.validation_system.generate_validation_report(
                new_positions,
                elements,
                firma,
                seite
            )
            
            result.validation_passed = validation_report.is_valid
            
            # Collect warnings
            for warning in validation_report.get_warnings():
                result.warnings.append(warning.message)
            
            if not validation_report.is_valid:
                errors = validation_report.get_errors()
                result.error_message = f"{len(errors)} validation errors"
                for error in errors[:3]:  # Log first 3 errors
                    self.logger.error(
                        f"F{firma}S{seite} Validation: {error.message}"
                    )
            
            result.success = True
            
        except Exception as e:
            result.error_message = str(e)
            result.success = False
            self.logger.error(f"F{firma}S{seite} Exception: {e}")
        
        finally:
            end_time = datetime.now()
            result.processing_time = (end_time - start_time).total_seconds()
        
        return result
    
    def _generate_summary(self, total_time: float) -> BatchSummary:
        """
        Generate batch processing summary.
        
        Args:
            total_time: Total execution time
            
        Returns:
            BatchSummary with statistics
        """
        successful = sum(1 for r in self.results if r.success)
        failed = len(self.results) - successful
        total_elements = sum(r.elements_count for r in self.results)
        
        if len != 0:
            avg_time = total_time / len(self.results) if self.results else 0
        else:
            avg_time = 0.0
        
        summary = BatchSummary(
            total_processed=len(self.results),
            successful=successful,
            failed=failed,
            total_elements=total_elements,
            total_time=total_time,
            avg_time_per_combination=avg_time,
            results=self.results,
            parallel_processing=self.parallel,
            worker_count=self.max_workers or 1
        )
        
        return summary
    
    def _log_summary(self, summary: BatchSummary):
        """
        Log batch processing summary.
        
        Args:
            summary: BatchSummary to log
        """
        self.logger.info("\n" + "=" * 70)
        self.logger.info("BATCH PROCESSING SUMMARY")
        self.logger.info("=" * 70)
        self.logger.info(f"Total processed: {summary.total_processed}")
        self.logger.info(f"Successful: {summary.successful}")
        self.logger.info(f"Failed: {summary.failed}")
        self.logger.info(f"Total elements: {summary.total_elements}")
        self.logger.info(f"Total time: {summary.total_time:.2f}s")
        self.logger.info(f"Avg time per combination: {summary.avg_time_per_combination:.2f}s")
        
        if summary.parallel_processing:
            self.logger.info(f"Parallel workers: {summary.worker_count}")
        
        # Log failed combinations
        if summary.failed > 0:
            self.logger.info(f"\nFailed combinations ({summary.failed}):")
            for result in summary.results:
                if not result.success:
                    self.logger.info(
                        f"  F{result.firma}S{result.seite}: {result.error_message}"
                    )
        
        # Log validation issues
        validation_warnings = sum(
            len(r.warnings) for r in summary.results
        )
        if validation_warnings > 0:
            self.logger.info(f"\nTotal validation warnings: {validation_warnings}")
        
        self.logger.info("=" * 70)
        
        # Final status
        if summary.successful == summary.total_processed:
            self.logger.info("\nAll combinations processed successfully!")
        elif summary.successful > 0:
            self.logger.info(
                f"\n⚠ Partially successful: {summary.successful}/"
                f"{summary.total_processed}"
            )
        else:
            self.logger.info("\nBatch processing failed")


def process_all_combinations(
    firmen: Optional[List[int]] = None,
    seiten: Optional[List[int]] = None,
    parallel: bool = False,
    max_workers: Optional[int] = None,
    pdf_dir: Optional[Path] = None,
    yml_dir: Optional[Path] = None,
    output_dir: Optional[Path] = None,
    log_file: Optional[Path] = None,
    log_level: str = "INFO"
) -> BatchSummary:
    """
    Convenience function to process all combinations.
    
    Args:
        firmen: List of firma numbers (default: all)
        seiten: List of seite numbers (default: all)
        parallel: Whether to use parallel processing
        max_workers: Maximum number of parallel workers
        pdf_dir: Directory containing PDF templates
        yml_dir: Directory containing YML coordinate files
        output_dir: Directory for output files
        log_file: Path to log file
        log_level: Logging level
        
    Returns:
        BatchSummary with processing results
        
    Example:
        >>> # Process all combinations sequentially
        >>> summary = process_all_combinations()
        
        >>> # Process with parallel processing
        >>> summary = process_all_combinations(parallel=True, max_workers=4)
        
        >>> # Process specific firmen
        >>> summary = process_all_combinations(firmen=[1, 2, 3])
    """
    processor = BatchProcessor(
        pdf_dir=pdf_dir,
        yml_dir=yml_dir,
        output_dir=output_dir,
        parallel=parallel,
        max_workers=max_workers,
        log_file=log_file,
        log_level=log_level
    )
    
    return processor.process_all(firmen=firmen, seiten=seiten)


if __name__ == "__main__":
    # Example: Process all combinations with parallel processing
    print("\n=== Batch Processor Demo ===\n")
    
    # Process with parallel processing
    summary = process_all_combinations(
        parallel=True,
        max_workers=4,
        log_level="INFO"
    )
    
    # Display results
    print(f"\nProcessing complete:")
    print(f"  Total: {summary.total_processed}")
    print(f"  Successful: {summary.successful}")
    print(f"  Failed: {summary.failed}")
    print(f"  Time: {summary.total_time:.2f}s")
    print(f"  Avg: {summary.avg_time_per_combination:.2f}s per combination")
    
    # Exit with appropriate code
    sys.exit(0 if summary.failed == 0 else 1)
