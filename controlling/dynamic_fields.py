"""
Controlling System Dynamic Fields Module

Provides dynamic field generation based on criteria and comprehensive
PDF bytes support for all exports.

This module ensures all input fields are dynamically generated and all
exports support PDF bytes format.
"""

import logging
import io
from typing import List, Dict, Any, Optional, Callable
from datetime import date, datetime
from sqlalchemy.orm import Session

# PDF support
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, Image
    )
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

logger = logging.getLogger(__name__)


class DynamicFieldGenerator:
    """
    Generates dynamic input fields based on criteria configuration.
    
    This ensures all input fields are dynamically created based on the
    actual criteria assigned to positions, making the system flexible
    and maintainable.
    """
    
    def __init__(self, db: Session):
        """
        Initialize dynamic field generator.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def generate_performance_fields(
        self,
        criteria: List[Any],
        layout: str = "columns",
        num_columns: int = 2
    ) -> Dict[str, Any]:
        """
        Generate dynamic performance input fields.
        
        Args:
            criteria: List of criterion objects
            layout: Layout type ("columns", "rows", "grid")
            num_columns: Number of columns for column layout
        
        Returns:
            Dictionary mapping criterion IDs to field configurations
        """
        fields = {}
        
        for criterion in criteria:
            field_config = {
                "id": criterion.id,
                "name": criterion.name,
                "description": criterion.description or "",
                "calculation_method": criterion.calculation_method.value,
                "input_type": self._determine_input_type(criterion),
                "validation": self._get_validation_rules(criterion),
                "default_value": 0.0,
                "min_value": 0.0,
                "max_value": None,
                "step": 1.0,
                "required": False
            }
            
            fields[criterion.id] = field_config
        
        return fields
    
    def _determine_input_type(self, criterion: Any) -> str:
        """
        Determine appropriate input type for criterion.
        
        Args:
            criterion: Criterion object
        
        Returns:
            Input type string
        """
        calc_method = criterion.calculation_method.value
        
        if calc_method == "PERCENTAGE":
            return "percentage"
        elif calc_method == "RATIO":
            return "ratio"
        else:
            return "number"
    
    def _get_validation_rules(self, criterion: Any) -> Dict[str, Any]:
        """
        Get validation rules for criterion.
        
        Args:
            criterion: Criterion object
        
        Returns:
            Dictionary of validation rules
        """
        calc_method = criterion.calculation_method.value
        
        rules = {
            "required": False,
            "min": 0.0,
            "max": None,
            "type": "float"
        }
        
        if calc_method == "PERCENTAGE":
            rules["max"] = 100.0
            rules["message"] = "Wert muss zwischen 0 und 100 liegen"
        
        return rules
    
    def generate_filter_fields(
        self,
        employees: List[Any]
    ) -> Dict[str, List[str]]:
        """
        Generate dynamic filter fields based on employee data.
        
        Args:
            employees: List of employee objects
        
        Returns:
            Dictionary of filter options
        """
        filters = {
            "positions": set(),
            "cities": set(),
            "names": []
        }
        
        for emp in employees:
            if emp.position:
                filters["positions"].add(emp.position.name)
            if emp.city:
                filters["cities"].add(emp.city)
            filters["names"].append(emp.full_name)
        
        # Convert sets to sorted lists
        return {
            "positions": sorted(list(filters["positions"])),
            "cities": sorted(list(filters["cities"])),
            "names": sorted(filters["names"])
        }
    
    def generate_report_fields(
        self,
        report_types: List[str]
    ) -> Dict[str, Any]:
        """
        Generate dynamic report configuration fields.
        
        Args:
            report_types: List of available report types
        
        Returns:
            Dictionary of report field configurations
        """
        return {
            "report_type": {
                "options": report_types,
                "default": report_types[0] if report_types else None,
                "required": True
            },
            "date_range": {
                "start_date": {
                    "type": "date",
                    "default": date.today(),
                    "max": date.today()
                },
                "end_date": {
                    "type": "date",
                    "default": date.today(),
                    "max": date.today()
                }
            },
            "employees": {
                "type": "multiselect",
                "min_selections": 1,
                "max_selections": 10
            }
        }


class PDFBytesExporter:
    """
    Comprehensive PDF bytes exporter for all controlling data.
    
    This ensures all results and data can be exported as PDF bytes,
    providing a consistent export interface across the system.
    """
    
    def __init__(self):
        """Initialize PDF bytes exporter."""
        if not REPORTLAB_AVAILABLE:
            raise ImportError(
                "reportlab is required for PDF export. "
                "Install with: pip install reportlab"
            )
        
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom PDF styles."""
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#366092'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        # Heading style
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#366092'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Subheading style
        self.subheading_style = ParagraphStyle(
            'CustomSubheading',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#366092'),
            spaceAfter=8,
            spaceBefore=8
        )
        
        # Normal text style
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6
        )
        
        # Bold text style
        self.bold_style = ParagraphStyle(
            'CustomBold',
            parent=self.styles['Normal'],
            fontSize=11,
            fontName='Helvetica-Bold',
            spaceAfter=6
        )
    
    def export_report_to_pdf_bytes(
        self,
        report_data: Dict[str, Any],
        include_charts: bool = False,
        chart_images: Optional[List[bytes]] = None
    ) -> bytes:
        """
        Export report to PDF bytes.
        
        Args:
            report_data: Report data dictionary
            include_charts: Whether to include chart images
            chart_images: List of chart images as bytes
        
        Returns:
            PDF file as bytes
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        elements = []
        
        # Title
        title = report_data.get("employee_name", "Controlling Report")
        elements.append(Paragraph(title, self.title_style))
        elements.append(Spacer(1, 0.5*cm))
        
        # Metadata section
        elements.append(Paragraph("Berichtsinformationen", self.heading_style))
        metadata = self._create_metadata_table(report_data)
        elements.append(metadata)
        elements.append(Spacer(1, 1*cm))
        
        # Quotas section
        if "quotas" in report_data:
            elements.append(Paragraph("Leistungsquoten", self.heading_style))
            quotas_table = self._create_quotas_table(report_data)
            elements.append(quotas_table)
            elements.append(Spacer(1, 1*cm))
        
        # Charts section
        if include_charts and chart_images:
            elements.append(PageBreak())
            elements.append(Paragraph("Visualisierungen", self.heading_style))
            for chart_bytes in chart_images:
                try:
                    img = Image(io.BytesIO(chart_bytes), width=15*cm, height=10*cm)
                    elements.append(img)
                    elements.append(Spacer(1, 0.5*cm))
                except Exception as e:
                    logger.warning(f"Failed to add chart image: {e}")
        
        # Raw data section
        if "aggregated_data" in report_data:
            elements.append(PageBreak())
            elements.append(Paragraph("Rohdaten", self.heading_style))
            raw_data_table = self._create_raw_data_table(report_data)
            elements.append(raw_data_table)
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
    
    def _create_metadata_table(self, report_data: Dict[str, Any]) -> Table:
        """Create metadata table for PDF."""
        data = [
            ["Mitarbeiter:", report_data.get("employee_name", "N/A")],
            ["Position:", report_data.get("position", "N/A")],
            ["Berichtstyp:", report_data.get("report_type", "N/A")],
            [
                "Zeitraum:",
                f"{report_data.get('start_date', 'N/A')} bis "
                f"{report_data.get('end_date', 'N/A')}"
            ],
            ["Erstellt am:", report_data.get("generated_at", "N/A")]
        ]
        
        table = Table(data, colWidths=[5*cm, 12*cm])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F0F0F0')),
        ]))
        
        return table
    
    def _create_quotas_table(self, report_data: Dict[str, Any]) -> Table:
        """Create quotas table for PDF."""
        quotas = report_data.get("quotas", {})
        ratios = report_data.get("ratio_descriptions", {})
        
        data = [["Quote", "Wert", "Verhältnis"]]
        
        for quota_name, quota_value in quotas.items():
            data.append([
                quota_name,
                f"{quota_value:.2f}%",
                ratios.get(quota_name, "")
            ])
        
        table = Table(data, colWidths=[7*cm, 3*cm, 7*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#366092')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        return table
    
    def _create_raw_data_table(self, report_data: Dict[str, Any]) -> Table:
        """Create raw data table for PDF."""
        aggregated_data = report_data.get("aggregated_data", {})
        raw_data = aggregated_data.get("raw_data", {})
        
        data = [["Kriterium", "Wert"]]
        
        for criterion_name, value in raw_data.items():
            data.append([criterion_name, str(value)])
        
        table = Table(data, colWidths=[12*cm, 5*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#366092')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        return table
    
    def export_employee_list_to_pdf_bytes(
        self,
        employees: List[Any]
    ) -> bytes:
        """
        Export employee list to PDF bytes.
        
        Args:
            employees: List of employee objects
        
        Returns:
            PDF file as bytes
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        elements = []
        
        # Title
        elements.append(Paragraph("Mitarbeiterliste", self.title_style))
        elements.append(Spacer(1, 0.5*cm))
        
        # Employee table
        data = [[
            "Name",
            "Position",
            "Wohnort",
            "Alter",
            "Arbeitsbeginn",
            "Tage beschäftigt"
        ]]
        
        for emp in employees:
            data.append([
                emp.full_name,
                emp.position.name if emp.position else "N/A",
                emp.city,
                str(emp.age),
                emp.start_date.isoformat(),
                str(emp.days_employed)
            ])
        
        table = Table(data, colWidths=[4*cm, 3*cm, 3*cm, 2*cm, 3*cm, 2*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#366092')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        elements.append(table)
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
    
    def export_comparison_report_to_pdf_bytes(
        self,
        comparison_data: Dict[str, Any]
    ) -> bytes:
        """
        Export comparison report to PDF bytes.
        
        Args:
            comparison_data: Comparison report data
        
        Returns:
            PDF file as bytes
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        elements = []
        
        # Title
        elements.append(Paragraph("Mitarbeitervergleich", self.title_style))
        elements.append(Spacer(1, 0.5*cm))
        
        # Metadata
        metadata_text = f"""
        <b>Berichtstyp:</b> {comparison_data.get('report_type', 'N/A')}<br/>
        <b>Zeitraum:</b> {comparison_data.get('start_date')} bis \
{comparison_data.get('end_date')}<br/>
        <b>Anzahl Mitarbeiter:</b> {comparison_data.get('employee_count', 0)}<br/>
        <b>Erstellt am:</b> {comparison_data.get('generated_at', 'N/A')}
        """
        elements.append(Paragraph(metadata_text, self.normal_style))
        elements.append(Spacer(1, 1*cm))
        
        # Comparison table
        employee_reports = comparison_data.get("employee_reports", [])
        
        if employee_reports:
            # Get all quota names from first report
            first_report = employee_reports[0]
            quota_names = list(first_report.get("quotas", {}).keys())
            
            # Build table header
            header = ["Mitarbeiter", "Position"] + quota_names
            data = [header]
            
            # Build table rows
            for emp_report in employee_reports:
                row = [
                    emp_report.get("employee_name", "N/A"),
                    emp_report.get("position", "N/A")
                ]
                
                quotas = emp_report.get("quotas", {})
                for quota_name in quota_names:
                    quota_value = quotas.get(quota_name, 0.0)
                    row.append(f"{quota_value:.1f}%")
                
                data.append(row)
            
            # Calculate column widths dynamically
            num_cols = len(header)
            col_width = 17 / num_cols  # Total width 17cm
            col_widths = [col_width * cm] * num_cols
            
            table = Table(data, colWidths=col_widths)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#366092')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            
            elements.append(table)
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()


# Export all public classes
__all__ = [
    'DynamicFieldGenerator',
    'PDFBytesExporter'
]
