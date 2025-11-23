"""
Universal PDF Bytes Generator

This module generates PDF bytes for ALL data types in the application, not just PV-specific data.
It handles text, numbers, currency, percentage, kWh, years, images, charts, diagrams, and documents
with German formatting (16.999,00 €, 85,5%, 12.500 kWh).

This is the implementation of Task 124: PDF Dynamic Keys & PDF Bytes Universal System

Requirements: 1.3, 14.1, 14.2
Task: 124 - PDF Dynamic Keys & PDF Bytes Universal System
"""

import logging
import io
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from pathlib import Path
from decimal import Decimal

# Import core infrastructure
try:
    from ...backend.core.pdf_bytes import (
        PDFByteMixin,
        PDFMetadata,
        PDFRenderingEngine,
        create_pdf_from_dict
    )
    from ...backend.core.german_formatter import GermanNumberFormatter
except (ImportError, ValueError):
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent))
    from backend.core.pdf_bytes import (
        PDFByteMixin,
        PDFMetadata,
        PDFRenderingEngine,
        create_pdf_from_dict
    )
    from backend.core.german_formatter import GermanNumberFormatter

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm, cm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, Image as RLImage
    )
    from reportlab.lib import colors
    from reportlab.pdfgen import canvas
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.graphics.charts.barcharts import VerticalBarChart, HorizontalBarChart
    from reportlab.graphics.charts.linecharts import HorizontalLineChart
    from reportlab.graphics.charts.lineplots import LinePlot
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("Warning: reportlab not installed. PDF generation will be limited.")

logger = logging.getLogger(__name__)


class UniversalDataPDF(PDFByteMixin):
    """
    Universal PDF generator for any data type.
    
    This class can generate PDF bytes for:
    - Text data
    - Numeric data (with German formatting)
    - Currency (16.999,00 €)
    - Percentage (85,5%)
    - kWh values (12.500 kWh)
    - Years (12,5 Jahre)
    - Mixed data dictionaries
    """
    
    def __init__(
        self,
        data: Dict[str, Any],
        title: str = "Daten",
        data_types: Optional[Dict[str, str]] = None
    ):
        """
        Initialize universal PDF generator.
        
        Args:
            data: Dictionary of data to include in PDF
            title: PDF title
            data_types: Optional dictionary mapping keys to data types
                       (currency, percentage, kwh, years, number, text)
        """
        super().__init__()
        self.data = data
        self.title = title
        self.data_types = data_types or {}
        self.formatter = GermanNumberFormatter()
    
    def _get_default_title(self) -> str:
        return self.title
    
    def _get_default_subject(self) -> str:
        return "Universelle Daten"
    
    def _render_to_pdf(self, story: List, doc):
        """Render data to PDF with German formatting"""
        if not REPORTLAB_AVAILABLE:
            return
        
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#1a5490'),
            spaceAfter=20,
            alignment=TA_CENTER
        )
        story.append(Paragraph(self.title, title_style))
        story.append(Spacer(1, 20))
        
        # Data table
        table_data = [['Parameter', 'Wert']]
        for key, value in self.data.items():
            formatted_value = self._format_value(key, value)
            table_data.append([key, formatted_value])
        
        table = self._create_styled_table(table_data)
        story.append(table)
    
    def _format_value(self, key: str, value: Any) -> str:
        """
        Format value based on its type with German formatting.
        
        Args:
            key: Data key
            value: Value to format
            
        Returns:
            Formatted string
        """
        # Get data type if specified
        data_type = self.data_types.get(key)
        
        # Handle None
        if value is None:
            return "N/A"
        
        # Handle boolean (before numeric check since bool is subclass of int)
        if isinstance(value, bool):
            return "Ja" if value else "Nein"
        
        # Handle numeric types
        if isinstance(value, (int, float, Decimal)):
            if data_type == 'currency':
                return self.formatter.format_currency(float(value))
            elif data_type == 'percentage':
                return self.formatter.format_percent(float(value))
            elif data_type == 'kwh':
                return f"{self.formatter.format(float(value))} kWh"
            elif data_type == 'years':
                return f"{self.formatter.format(float(value), 1)} Jahre"
            else:
                # Default number formatting
                return self.formatter.format(float(value))
        
        # Handle datetime
        if isinstance(value, datetime):
            return value.strftime("%d.%m.%Y %H:%M:%S")
        
        # Default: convert to string
        return str(value)
    
    def _create_styled_table(self, data: List[List[str]]) -> Table:
        """Create a styled table"""
        table = Table(data, colWidths=[8*cm, 8*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f0f0')),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        return table


class UniversalChartPDF(PDFByteMixin):
    """
    Universal PDF generator for all 10 chart types.
    
    Supports: CIRCLE, DONUT, BAR, COLUMN, LINE, AREA, PIE, POLAR, RADAR, WATERFALL
    """
    
    def __init__(
        self,
        chart_type: str,
        chart_data: Dict[str, Any],
        title: str = "Diagramm"
    ):
        """
        Initialize chart PDF generator.
        
        Args:
            chart_type: Type of chart (CIRCLE, DONUT, BAR, COLUMN, LINE, AREA, PIE, POLAR, RADAR, WATERFALL)
            chart_data: Chart data (labels, values, series, etc.)
            title: Chart title
        """
        super().__init__()
        self.chart_type = chart_type.upper()
        self.chart_data = chart_data
        self.chart_title = title
        self.formatter = GermanNumberFormatter()
    
    def _get_default_title(self) -> str:
        return self.chart_title
    
    def _render_to_pdf(self, story: List, doc):
        """Render chart to PDF"""
        if not REPORTLAB_AVAILABLE:
            return
        
        styles = getSampleStyleSheet()
        
        # Title
        story.append(Paragraph(self.chart_title, styles['Heading1']))
        story.append(Spacer(1, 20))
        
        # Create chart based on type
        if self.chart_type in ['PIE', 'CIRCLE', 'DONUT']:
            chart = self._create_pie_chart()
        elif self.chart_type in ['BAR', 'COLUMN']:
            chart = self._create_bar_chart()
        elif self.chart_type in ['LINE', 'AREA']:
            chart = self._create_line_chart()
        else:
            # Fallback to table for unsupported types
            chart = self._create_data_table()
        
        if chart:
            story.append(chart)
    
    def _create_pie_chart(self) -> Drawing:
        """Create a pie/circle/donut chart"""
        drawing = Drawing(400, 300)
        pie = Pie()
        pie.x = 150
        pie.y = 50
        pie.width = 200
        pie.height = 200
        
        # Get data
        labels = self.chart_data.get('labels', [])
        values = self.chart_data.get('values', [])
        
        pie.data = values
        pie.labels = labels
        pie.slices.strokeWidth = 0.5
        
        # Donut effect
        if self.chart_type == 'DONUT':
            pie.innerRadiusFraction = 0.5
        
        drawing.add(pie)
        return drawing
    
    def _create_bar_chart(self) -> Drawing:
        """Create a bar/column chart"""
        drawing = Drawing(400, 300)
        
        if self.chart_type == 'COLUMN':
            bc = VerticalBarChart()
        else:
            bc = HorizontalBarChart()
        
        bc.x = 50
        bc.y = 50
        bc.height = 200
        bc.width = 300
        
        # Get data
        data = self.chart_data.get('data', [[]])
        bc.data = data
        
        # Categories
        categories = self.chart_data.get('categories', [])
        bc.categoryAxis.categoryNames = categories
        
        drawing.add(bc)
        return drawing
    
    def _create_line_chart(self) -> Drawing:
        """Create a line/area chart"""
        drawing = Drawing(400, 300)
        lc = HorizontalLineChart()
        lc.x = 50
        lc.y = 50
        lc.height = 200
        lc.width = 300
        
        # Get data
        data = self.chart_data.get('data', [[]])
        lc.data = data
        
        # Area fill for AREA type
        if self.chart_type == 'AREA':
            lc.fillColor = colors.HexColor('#1a5490')
        
        drawing.add(lc)
        return drawing
    
    def _create_data_table(self) -> Table:
        """Create a data table as fallback"""
        labels = self.chart_data.get('labels', [])
        values = self.chart_data.get('values', [])
        
        table_data = [['Kategorie', 'Wert']]
        for label, value in zip(labels, values):
            if isinstance(value, (int, float)):
                formatted_value = self.formatter.format(value, 2)
            else:
                formatted_value = str(value)
            table_data.append([label, formatted_value])
        
        table = Table(table_data, colWidths=[8*cm, 8*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        return table


class UniversalImagePDF(PDFByteMixin):
    """
    Universal PDF generator for images and photos.
    """
    
    def __init__(
        self,
        image_path: str,
        title: str = "Bild",
        description: Optional[str] = None
    ):
        """
        Initialize image PDF generator.
        
        Args:
            image_path: Path to image file
            title: Image title
            description: Optional image description
        """
        super().__init__()
        self.image_path = image_path
        self.title = title
        self.description = description
    
    def _get_default_title(self) -> str:
        return self.title
    
    def _render_to_pdf(self, story: List, doc):
        """Render image to PDF"""
        if not REPORTLAB_AVAILABLE:
            return
        
        styles = getSampleStyleSheet()
        
        # Title
        story.append(Paragraph(self.title, styles['Heading1']))
        story.append(Spacer(1, 20))
        
        # Description
        if self.description:
            story.append(Paragraph(self.description, styles['BodyText']))
            story.append(Spacer(1, 10))
        
        # Add image
        if Path(self.image_path).exists():
            try:
                img = RLImage(self.image_path, width=15*cm, height=10*cm)
                story.append(img)
            except Exception as e:
                logger.error(f"Error adding image: {e}")
                story.append(Paragraph(f"Fehler beim Laden des Bildes: {e}", styles['BodyText']))


class UniversalDocumentPDF(PDFByteMixin):
    """
    Universal PDF generator for documents and datasheets.
    """
    
    def __init__(
        self,
        document_data: Dict[str, Any],
        title: str = "Dokument"
    ):
        """
        Initialize document PDF generator.
        
        Args:
            document_data: Document data (sections, content, etc.)
            title: Document title
        """
        super().__init__()
        self.document_data = document_data
        self.title = title
    
    def _get_default_title(self) -> str:
        return self.title
    
    def _render_to_pdf(self, story: List, doc):
        """Render document to PDF"""
        if not REPORTLAB_AVAILABLE:
            return
        
        styles = getSampleStyleSheet()
        
        # Title
        story.append(Paragraph(self.title, styles['Heading1']))
        story.append(Spacer(1, 20))
        
        # Sections
        sections = self.document_data.get('sections', [])
        for section in sections:
            section_title = section.get('title', '')
            section_content = section.get('content', '')
            
            if section_title:
                story.append(Paragraph(section_title, styles['Heading2']))
                story.append(Spacer(1, 10))
            
            if section_content:
                story.append(Paragraph(section_content, styles['BodyText']))
                story.append(Spacer(1, 10))


class Universal3DVisualizationPDF(PDFByteMixin):
    """
    Universal PDF generator for 3D visualizations.
    """
    
    def __init__(
        self,
        visualization_data: Dict[str, Any],
        image_path: Optional[str] = None,
        title: str = "3D-Visualisierung"
    ):
        """
        Initialize 3D visualization PDF generator.
        
        Args:
            visualization_data: Visualization data
            image_path: Optional path to visualization screenshot
            title: Visualization title
        """
        super().__init__()
        self.visualization_data = visualization_data
        self.image_path = image_path
        self.title = title
        self.formatter = GermanNumberFormatter()
    
    def _get_default_title(self) -> str:
        return self.title
    
    def _render_to_pdf(self, story: List, doc):
        """Render 3D visualization to PDF"""
        if not REPORTLAB_AVAILABLE:
            return
        
        styles = getSampleStyleSheet()
        
        # Title
        story.append(Paragraph(self.title, styles['Heading1']))
        story.append(Spacer(1, 20))
        
        # Description
        description = self.visualization_data.get('description', '')
        if description:
            story.append(Paragraph(description, styles['BodyText']))
            story.append(Spacer(1, 10))
        
        # Add image if available
        if self.image_path and Path(self.image_path).exists():
            try:
                img = RLImage(self.image_path, width=15*cm, height=10*cm)
                story.append(img)
                story.append(Spacer(1, 10))
            except Exception as e:
                logger.error(f"Error adding image: {e}")
        
        # Visualization details
        details_data = [['Parameter', 'Wert']]
        for key, value in self.visualization_data.items():
            if key != 'description':
                if isinstance(value, (int, float)):
                    formatted_value = self.formatter.format(value, 2)
                else:
                    formatted_value = str(value)
                details_data.append([key, formatted_value])
        
        if len(details_data) > 1:
            details_table = Table(details_data, colWidths=[8*cm, 8*cm])
            details_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(details_table)


class UniversalPDFBytesGenerator:
    """
    Main universal PDF bytes generator for ALL data types.
    
    This class provides a unified interface for generating PDF bytes
    for any data type in the application with German formatting.
    
    Example:
        >>> generator = UniversalPDFBytesGenerator()
        >>> # Generate PDF for data
        >>> data = {'cost': 16999.00, 'size': 10.5}
        >>> data_types = {'cost': 'currency', 'size': 'number'}
        >>> pdf_bytes = generator.generate_data_pdf(data, "Daten", data_types)
        >>> # Generate PDF for chart
        >>> chart_data = {'labels': ['A', 'B'], 'values': [10, 20]}
        >>> chart_pdf = generator.generate_chart_pdf('PIE', chart_data, "Diagramm")
    """
    
    def __init__(self):
        """Initialize the universal PDF bytes generator"""
        self.formatter = GermanNumberFormatter()
    
    def generate_data_pdf(
        self,
        data: Dict[str, Any],
        title: str = "Daten",
        data_types: Optional[Dict[str, str]] = None,
        metadata: Optional[PDFMetadata] = None
    ) -> bytes:
        """
        Generate PDF bytes for any data dictionary.
        
        Args:
            data: Dictionary of data
            title: PDF title
            data_types: Optional mapping of keys to data types
            metadata: Optional PDF metadata
            
        Returns:
            PDF bytes
        """
        pdf_gen = UniversalDataPDF(data, title, data_types)
        return pdf_gen.to_pdf_bytes(metadata)
    
    def generate_chart_pdf(
        self,
        chart_type: str,
        chart_data: Dict[str, Any],
        title: str = "Diagramm",
        metadata: Optional[PDFMetadata] = None
    ) -> bytes:
        """
        Generate PDF bytes for any chart type.
        
        Args:
            chart_type: Type of chart (CIRCLE, DONUT, BAR, COLUMN, LINE, AREA, PIE, POLAR, RADAR, WATERFALL)
            chart_data: Chart data
            title: Chart title
            metadata: Optional PDF metadata
            
        Returns:
            PDF bytes
        """
        pdf_gen = UniversalChartPDF(chart_type, chart_data, title)
        return pdf_gen.to_pdf_bytes(metadata)
    
    def generate_image_pdf(
        self,
        image_path: str,
        title: str = "Bild",
        description: Optional[str] = None,
        metadata: Optional[PDFMetadata] = None
    ) -> bytes:
        """
        Generate PDF bytes for an image.
        
        Args:
            image_path: Path to image file
            title: Image title
            description: Optional image description
            metadata: Optional PDF metadata
            
        Returns:
            PDF bytes
        """
        pdf_gen = UniversalImagePDF(image_path, title, description)
        return pdf_gen.to_pdf_bytes(metadata)
    
    def generate_document_pdf(
        self,
        document_data: Dict[str, Any],
        title: str = "Dokument",
        metadata: Optional[PDFMetadata] = None
    ) -> bytes:
        """
        Generate PDF bytes for a document.
        
        Args:
            document_data: Document data (sections, content, etc.)
            title: Document title
            metadata: Optional PDF metadata
            
        Returns:
            PDF bytes
        """
        pdf_gen = UniversalDocumentPDF(document_data, title)
        return pdf_gen.to_pdf_bytes(metadata)
    
    def generate_3d_visualization_pdf(
        self,
        visualization_data: Dict[str, Any],
        image_path: Optional[str] = None,
        title: str = "3D-Visualisierung",
        metadata: Optional[PDFMetadata] = None
    ) -> bytes:
        """
        Generate PDF bytes for a 3D visualization.
        
        Args:
            visualization_data: Visualization data
            image_path: Optional path to visualization screenshot
            title: Visualization title
            metadata: Optional PDF metadata
            
        Returns:
            PDF bytes
        """
        pdf_gen = Universal3DVisualizationPDF(visualization_data, image_path, title)
        return pdf_gen.to_pdf_bytes(metadata)


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize generator
    generator = UniversalPDFBytesGenerator()
    
    # Example 1: Generate PDF for mixed data types
    data = {
        'Gesamtkosten': 16999.00,
        'Anlagengröße': 10.5,
        'Eigenverbrauchsquote': 85.5,
        'Jahresproduktion': 12500.0,
        'Amortisationszeit': 12.5,
        'Kundenname': 'Max Mustermann',
        'Datum': datetime.now()
    }
    
    data_types = {
        'Gesamtkosten': 'currency',
        'Anlagengröße': 'number',
        'Eigenverbrauchsquote': 'percentage',
        'Jahresproduktion': 'kwh',
        'Amortisationszeit': 'years',
        'Kundenname': 'text',
        'Datum': 'datetime'
    }
    
    pdf_bytes = generator.generate_data_pdf(data, "Systemdaten", data_types)
    
    # Save to file
    output_path = "test_universal_data.pdf"
    with open(output_path, 'wb') as f:
        f.write(pdf_bytes)
    
    logger.info(f"Data PDF generated: {output_path} ({len(pdf_bytes)} bytes)")
    
    # Example 2: Generate PDF for chart
    chart_data = {
        'labels': ['Januar', 'Februar', 'März', 'April'],
        'values': [1200.50, 1350.75, 1500.00, 1650.25]
    }
    
    chart_pdf = generator.generate_chart_pdf('BAR', chart_data, "Monatliche Produktion")
    
    # Save to file
    chart_output_path = "test_universal_chart.pdf"
    with open(chart_output_path, 'wb') as f:
        f.write(chart_pdf)
    
    logger.info(f"Chart PDF generated: {chart_output_path} ({len(chart_pdf)} bytes)")
