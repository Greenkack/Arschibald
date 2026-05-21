"""
Tests for Validation Reporter Module

This module tests the validation report generation functionality,
including single reports, batch reports, and various output formats.
"""

import pytest
from pathlib import Path
import json
import tempfile
import shutil

from multi_pdf_positioning.validation_reporter import (
    ValidationReporter,
    BatchValidationSummary,
    generate_validation_report,
    generate_batch_report
)
from multi_pdf_positioning.validation_system import ValidationLevel
from multi_pdf_positioning.yml_parser import YMLElement


class TestValidationReporter:
    """Test suite for ValidationReporter class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.reporter = ValidationReporter()
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_generate_single_report_valid(self):
        """Test generating a report for valid positions."""
        positions = [
            (50, 50, 200, 100),
            (250, 50, 400, 100),
            (50, 150, 200, 200),
        ]
        
        report = self.reporter.generate_validation_report(
            positions, firma=1, seite=1
        )
        
        assert report.firma == 1
        assert report.seite == 1
        assert report.total_elements == 3
        assert report.is_valid is True
        assert len(report.collisions) == 0
    
    def test_generate_single_report_with_collision(self):
        """Test generating a report with collisions."""
        positions = [
            (50, 50, 200, 100),
            (100, 75, 250, 125),  # Overlaps with first
        ]
        
        report = self.reporter.generate_validation_report(
            positions, firma=1, seite=1
        )
        
        assert report.is_valid is False
        assert len(report.collisions) > 0
        assert len(report.get_errors()) > 0
    
    def test_generate_single_report_out_of_bounds(self):
        """Test generating a report with out-of-bounds positions."""
        positions = [
            (50, 50, 200, 100),
            (400, 50, 600, 100),  # Exceeds page width
        ]
        
        report = self.reporter.generate_validation_report(
            positions, firma=1, seite=1
        )
        
        assert report.is_valid is False
        errors = report.get_errors()
        assert len(errors) > 0
        assert any("exceeds page width" in e.message for e in errors)
    
    def test_generate_single_report_with_elements(self):
        """Test generating a report with YMLElement context."""
        positions = [
            (50, 50, 200, 100),
            (250, 50, 400, 100),
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
        
        report = self.reporter.generate_validation_report(
            positions, elements, firma=1, seite=1
        )
        
        assert report.total_elements == 2
        assert report.is_valid is True
    
    def test_generate_batch_report(self):
        """Test generating a batch validation report."""
        validation_data = {}
        
        # Create test data for 2 firmen x 2 seiten
        for firma in [1, 2]:
            for seite in [1, 2]:
                if firma == 1 and seite == 1:
                    # Invalid: has collision
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
        
        summary = self.reporter.generate_batch_report(validation_data)
        
        assert summary.total_combinations == 4
        assert summary.valid_combinations == 3
        assert summary.invalid_combinations == 1
        assert len(summary.all_reports) == 4
    
    def test_batch_report_grouping(self):
        """Test that batch reports are correctly grouped by firma and seite."""
        validation_data = {}
        
        for firma in [1, 2]:
            for seite in [1, 2]:
                positions = [(50, 50, 200, 100)]
                validation_data[(firma, seite)] = (positions, None)
        
        summary = self.reporter.generate_batch_report(validation_data)
        
        # Check grouping by firma
        assert len(summary.reports_by_firma) == 2
        assert len(summary.reports_by_firma[1]) == 2
        assert len(summary.reports_by_firma[2]) == 2
        
        # Check grouping by seite
        assert len(summary.reports_by_seite) == 2
        assert len(summary.reports_by_seite[1]) == 2
        assert len(summary.reports_by_seite[2]) == 2
    
    def test_format_report_text(self):
        """Test formatting a report as text."""
        positions = [
            (50, 50, 200, 100),
            (100, 75, 250, 125),  # Collision
        ]
        
        report = self.reporter.generate_validation_report(
            positions, firma=1, seite=1
        )
        
        text = self.reporter.format_report_text(report)
        
        assert "VALIDATION REPORT" in text
        assert "Firma: 1, Seite: 1" in text
        assert "ERRORS" in text
        assert "COLLISIONS" in text
    
    def test_format_batch_summary_text(self):
        """Test formatting a batch summary as text."""
        validation_data = {
            (1, 1): ([(50, 50, 200, 100)], None),
            (1, 2): ([(50, 50, 200, 100)], None),
        }
        
        summary = self.reporter.generate_batch_report(validation_data)
        text = self.reporter.format_batch_summary_text(summary)
        
        assert "BATCH VALIDATION SUMMARY" in text
        assert "OVERALL STATISTICS" in text
        assert "BREAKDOWN BY FIRMA" in text
        assert "BREAKDOWN BY SEITE" in text
    
    def test_format_report_json(self):
        """Test formatting a report as JSON."""
        positions = [(50, 50, 200, 100)]
        
        report = self.reporter.generate_validation_report(
            positions, firma=1, seite=1
        )
        
        data = self.reporter.format_report_json(report)
        
        assert data["firma"] == 1
        assert data["seite"] == 1
        assert data["is_valid"] is True
        assert "messages" in data
        assert "collisions" in data
        assert "summary" in data
    
    def test_format_batch_summary_json(self):
        """Test formatting a batch summary as JSON."""
        validation_data = {
            (1, 1): ([(50, 50, 200, 100)], None),
            (1, 2): ([(50, 50, 200, 100)], None),
        }
        
        summary = self.reporter.generate_batch_report(validation_data)
        data = self.reporter.format_batch_summary_json(summary)
        
        assert data["total_combinations"] == 2
        assert "reports_by_firma" in data
        assert "reports_by_seite" in data
    
    def test_save_report_text(self):
        """Test saving a report to a text file."""
        positions = [(50, 50, 200, 100)]
        report = self.reporter.generate_validation_report(
            positions, firma=1, seite=1
        )
        
        output_path = self.temp_dir / "report.txt"
        self.reporter.save_report_text(report, output_path)
        
        assert output_path.exists()
        content = output_path.read_text(encoding='utf-8')
        assert "VALIDATION REPORT" in content
    
    def test_save_report_json(self):
        """Test saving a report to a JSON file."""
        positions = [(50, 50, 200, 100)]
        report = self.reporter.generate_validation_report(
            positions, firma=1, seite=1
        )
        
        output_path = self.temp_dir / "report.json"
        self.reporter.save_report_json(report, output_path)
        
        assert output_path.exists()
        data = json.loads(output_path.read_text(encoding='utf-8'))
        assert data["firma"] == 1
        assert data["seite"] == 1
    
    def test_save_batch_summary_text(self):
        """Test saving a batch summary to a text file."""
        validation_data = {
            (1, 1): ([(50, 50, 200, 100)], None),
        }
        
        summary = self.reporter.generate_batch_report(validation_data)
        output_path = self.temp_dir / "summary.txt"
        self.reporter.save_batch_summary_text(summary, output_path)
        
        assert output_path.exists()
        content = output_path.read_text(encoding='utf-8')
        assert "BATCH VALIDATION SUMMARY" in content
    
    def test_save_batch_summary_json(self):
        """Test saving a batch summary to a JSON file."""
        validation_data = {
            (1, 1): ([(50, 50, 200, 100)], None),
        }
        
        summary = self.reporter.generate_batch_report(validation_data)
        output_path = self.temp_dir / "summary.json"
        self.reporter.save_batch_summary_json(summary, output_path)
        
        assert output_path.exists()
        data = json.loads(output_path.read_text(encoding='utf-8'))
        assert data["total_combinations"] == 1
    
    def test_generate_error_list(self):
        """Test generating a list of all errors."""
        validation_data = {
            (1, 1): ([(400, 50, 600, 100)], None),  # Out of bounds
            (1, 2): ([(50, 50, 200, 100)], None),   # Valid
        }
        
        summary = self.reporter.generate_batch_report(validation_data)
        errors = self.reporter.generate_error_list(summary)
        
        assert len(errors) > 0
        assert all("firma" in e for e in errors)
        assert all("seite" in e for e in errors)
        assert all("message" in e for e in errors)
    
    def test_generate_warning_list(self):
        """Test generating a list of all warnings."""
        validation_data = {
            (1, 1): ([(5, 50, 200, 100)], None),    # Too close to edge
            (1, 2): ([(50, 50, 200, 100)], None),   # Valid
        }
        
        summary = self.reporter.generate_batch_report(validation_data)
        warnings = self.reporter.generate_warning_list(summary)
        
        assert len(warnings) > 0
        assert all("firma" in w for w in warnings)
        assert all("seite" in w for w in warnings)
    
    def test_generate_collision_list(self):
        """Test generating a list of all collisions."""
        validation_data = {
            (1, 1): ([(50, 50, 200, 100), (100, 75, 250, 125)], None),  # Collision
            (1, 2): ([(50, 50, 200, 100)], None),                       # Valid
        }
        
        summary = self.reporter.generate_batch_report(validation_data)
        collisions = self.reporter.generate_collision_list(summary)
        
        assert len(collisions) > 0
        assert all("firma" in c for c in collisions)
        assert all("seite" in c for c in collisions)
        assert all("element1_index" in c for c in collisions)
        assert all("element2_index" in c for c in collisions)
    
    def test_generate_summary_by_firma(self):
        """Test generating summary statistics by firma."""
        validation_data = {
            (1, 1): ([(50, 50, 200, 100), (100, 75, 250, 125)], None),  # Invalid
            (1, 2): ([(50, 50, 200, 100)], None),                       # Valid
            (2, 1): ([(50, 50, 200, 100)], None),                       # Valid
        }
        
        summary = self.reporter.generate_batch_report(validation_data)
        firma_summaries = self.reporter.generate_summary_by_firma(summary)
        
        assert 1 in firma_summaries
        assert 2 in firma_summaries
        
        # Firma 1 has 2 seiten, 1 valid, 1 invalid
        assert firma_summaries[1]["total_seiten"] == 2
        assert firma_summaries[1]["valid_seiten"] == 1
        assert firma_summaries[1]["invalid_seiten"] == 1
        
        # Firma 2 has 1 seite, 1 valid
        assert firma_summaries[2]["total_seiten"] == 1
        assert firma_summaries[2]["valid_seiten"] == 1
    
    def test_generate_summary_by_seite(self):
        """Test generating summary statistics by seite."""
        validation_data = {
            (1, 1): ([(50, 50, 200, 100), (100, 75, 250, 125)], None),  # Invalid
            (2, 1): ([(50, 50, 200, 100)], None),                       # Valid
            (1, 2): ([(50, 50, 200, 100)], None),                       # Valid
        }
        
        summary = self.reporter.generate_batch_report(validation_data)
        seite_summaries = self.reporter.generate_summary_by_seite(summary)
        
        assert 1 in seite_summaries
        assert 2 in seite_summaries
        
        # Seite 1 has 2 firmen, 1 valid, 1 invalid
        assert seite_summaries[1]["total_firmen"] == 2
        assert seite_summaries[1]["valid_firmen"] == 1
        assert seite_summaries[1]["invalid_firmen"] == 1
        
        # Seite 2 has 1 firma, 1 valid
        assert seite_summaries[2]["total_firmen"] == 1
        assert seite_summaries[2]["valid_firmen"] == 1


class TestConvenienceFunctions:
    """Test suite for convenience functions."""
    
    def test_generate_validation_report_function(self):
        """Test the convenience function for generating a report."""
        positions = [(50, 50, 200, 100)]
        
        report = generate_validation_report(positions, firma=1, seite=1)
        
        assert report.firma == 1
        assert report.seite == 1
        assert report.is_valid is True
    
    def test_generate_batch_report_function(self):
        """Test the convenience function for generating a batch report."""
        validation_data = {
            (1, 1): ([(50, 50, 200, 100)], None),
            (1, 2): ([(50, 50, 200, 100)], None),
        }
        
        summary = generate_batch_report(validation_data)
        
        assert summary.total_combinations == 2
        assert summary.valid_combinations == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
