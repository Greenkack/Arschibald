"""
Tests for Controlling System Dynamic Fields Module

Tests dynamic field generation and PDF bytes export functionality.
"""

import pytest
from datetime import date
from controlling.dynamic_fields import (
    DynamicFieldGenerator,
    PDFBytesExporter
)
from controlling.models import CalculationMethod


class MockCriterion:
    """Mock criterion for testing."""
    
    def __init__(self, id, name, description, calculation_method):
        self.id = id
        self.name = name
        self.description = description
        self.calculation_method = calculation_method


class MockEmployee:
    """Mock employee for testing."""
    
    def __init__(self, id, full_name, position_name, city, age, start_date, days_employed):
        self.id = id
        self.full_name = full_name
        self.city = city
        self.age = age
        self.start_date = start_date
        self.days_employed = days_employed
        self.position = MockPosition(position_name)


class MockPosition:
    """Mock position for testing."""
    
    def __init__(self, name):
        self.name = name


class TestDynamicFieldGenerator:
    """Test dynamic field generation."""
    
    def test_generate_performance_fields(self):
        """Test generating performance input fields."""
        criteria = [
            MockCriterion(1, "Abschlüsse", "Anzahl Abschlüsse", CalculationMethod.SUM),
            MockCriterion(2, "Termine", "Anzahl Termine", CalculationMethod.SUM),
            MockCriterion(3, "Quote", "Erfolgsquote", CalculationMethod.PERCENTAGE)
        ]
        
        field_gen = DynamicFieldGenerator(None)
        fields = field_gen.generate_performance_fields(criteria)
        
        assert len(fields) == 3
        assert 1 in fields
        assert 2 in fields
        assert 3 in fields
        
        # Check field configuration
        assert fields[1]["name"] == "Abschlüsse"
        assert fields[1]["description"] == "Anzahl Abschlüsse"
        assert fields[1]["input_type"] == "number"
        
        assert fields[3]["name"] == "Quote"
        assert fields[3]["input_type"] == "percentage"
    
    def test_generate_filter_fields(self):
        """Test generating filter fields."""
        employees = [
            MockEmployee(1, "Max Mustermann", "Verkäufer", "München", 30, date(2020, 1, 1), 1000),
            MockEmployee(2, "Anna Schmidt", "Manager", "Berlin", 35, date(2019, 1, 1), 1500),
            MockEmployee(3, "Tom Weber", "Verkäufer", "München", 28, date(2021, 1, 1), 800)
        ]
        
        field_gen = DynamicFieldGenerator(None)
        filters = field_gen.generate_filter_fields(employees)
        
        assert "positions" in filters
        assert "cities" in filters
        assert "names" in filters
        
        assert "Verkäufer" in filters["positions"]
        assert "Manager" in filters["positions"]
        
        assert "München" in filters["cities"]
        assert "Berlin" in filters["cities"]
        
        assert len(filters["names"]) == 3
    
    def test_generate_report_fields(self):
        """Test generating report configuration fields."""
        report_types = ["DAILY", "WEEKLY", "MONTHLY"]
        
        field_gen = DynamicFieldGenerator(None)
        fields = field_gen.generate_report_fields(report_types)
        
        assert "report_type" in fields
        assert "date_range" in fields
        assert "employees" in fields
        
        assert fields["report_type"]["options"] == report_types
        assert fields["report_type"]["required"] is True
        
        assert fields["date_range"]["start_date"]["type"] == "date"
        assert fields["employees"]["type"] == "multiselect"


class TestPDFBytesExporter:
    """Test PDF bytes export functionality."""
    
    def test_export_report_to_pdf_bytes(self):
        """Test exporting report to PDF bytes."""
        report_data = {
            "employee_name": "Max Mustermann",
            "position": "Verkäufer",
            "report_type": "MONTHLY",
            "start_date": "2025-01-01",
            "end_date": "2025-01-31",
            "generated_at": "2025-01-31T12:00:00",
            "quotas": {
                "Abschlussquote": 25.5,
                "Terminquote": 80.0
            },
            "ratio_descriptions": {
                "Abschlussquote": "Jeder 4. Termin ist ein Abschluss",
                "Terminquote": "4 von 5 Kontakten führen zu Terminen"
            },
            "aggregated_data": {
                "raw_data": {
                    "Abschlüsse": 10,
                    "Termine": 40
                }
            }
        }
        
        exporter = PDFBytesExporter()
        pdf_bytes = exporter.export_report_to_pdf_bytes(report_data)
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')  # PDF magic number
    
    def test_export_employee_list_to_pdf_bytes(self):
        """Test exporting employee list to PDF bytes."""
        employees = [
            MockEmployee(1, "Max Mustermann", "Verkäufer", "München", 30, date(2020, 1, 1), 1000),
            MockEmployee(2, "Anna Schmidt", "Manager", "Berlin", 35, date(2019, 1, 1), 1500)
        ]
        
        exporter = PDFBytesExporter()
        pdf_bytes = exporter.export_employee_list_to_pdf_bytes(employees)
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')
    
    def test_export_comparison_report_to_pdf_bytes(self):
        """Test exporting comparison report to PDF bytes."""
        comparison_data = {
            "report_type": "MONTHLY",
            "start_date": "2025-01-01",
            "end_date": "2025-01-31",
            "employee_count": 2,
            "generated_at": "2025-01-31T12:00:00",
            "employee_reports": [
                {
                    "employee_name": "Max Mustermann",
                    "position": "Verkäufer",
                    "quotas": {
                        "Abschlussquote": 25.5,
                        "Terminquote": 80.0
                    }
                },
                {
                    "employee_name": "Anna Schmidt",
                    "position": "Manager",
                    "quotas": {
                        "Abschlussquote": 30.0,
                        "Terminquote": 85.0
                    }
                }
            ]
        }
        
        exporter = PDFBytesExporter()
        pdf_bytes = exporter.export_comparison_report_to_pdf_bytes(comparison_data)
        
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b'%PDF')
    
    def test_pdf_exporter_initialization(self):
        """Test PDF exporter initialization."""
        exporter = PDFBytesExporter()
        
        assert exporter.styles is not None
        assert exporter.title_style is not None
        assert exporter.heading_style is not None
        assert exporter.subheading_style is not None
        assert exporter.normal_style is not None
        assert exporter.bold_style is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
