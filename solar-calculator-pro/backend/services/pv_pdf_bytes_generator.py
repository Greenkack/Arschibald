"""
PV PDF Bytes Generator

This module generates PDF bytes for all PV-related data types including:
- Text and numbers with German formatting
- Charts and diagrams
- Images and 3D visualizations
- Product data from database

Requirements: 1.3, 4.5, 14.1, 14.2
Task: 115 - Standard PV PDF Dynamic Keys & PDF Bytes
"""

import logging
import io
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from pathlib import Path

# Import core PDF infrastructure
try:
    # Try relative import first (when used as module)
    from ...backend.core.pdf_bytes import (
        PDFByteMixin,
        PDFMetadata,
        PDFRenderingEngine,
        create_pdf_from_dict
    )
except (ImportError, ValueError):
    # Fall back to absolute import (when run directly)
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent))
    from backend.core.pdf_bytes import (
        PDFByteMixin,
        PDFMetadata,
        PDFRenderingEngine,
        create_pdf_from_dict
    )

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
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    from reportlab.graphics.charts.linecharts import HorizontalLineChart
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("Warning: reportlab not installed. PDF generation will be limited.")

logger = logging.getLogger(__name__)


class PVCalculationResultPDF(PDFByteMixin):
    """
    PDF generator for PV calculation results.
    
    Generates PDF bytes for calculation results with German formatting.
    """
    
    def __init__(self, calculation_data: Dict[str, Any]):
        super().__init__()
        self.calculation_data = calculation_data
        self.formatter = GermanNumberFormatter()
    
    def _get_default_title(self) -> str:
        return "PV-Anlagen Berechnungsergebnisse"
    
    def _get_default_subject(self) -> str:
        return "Photovoltaik Systemberechnung"
    
    def _render_to_pdf(self, story: List, doc):
        """Render calculation results to PDF"""
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
        story.append(Paragraph(self._get_default_title(), title_style))
        story.append(Spacer(1, 20))
        
        # System overview section
        story.append(Paragraph("Systemübersicht", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        overview_data = [
            ['Parameter', 'Wert'],
            ['Anlagengröße', self._format_system_size()],
            ['Anzahl Module', self._format_module_count()],
            ['Jahresproduktion', self._format_annual_production()],
            ['Eigenverbrauchsquote', self._format_self_consumption()],
        ]
        
        overview_table = self._create_styled_table(overview_data)
        story.append(overview_table)
        story.append(Spacer(1, 20))
        
        # Financial section
        story.append(Paragraph("Wirtschaftlichkeit", styles['Heading2']))
        story.append(Spacer(1, 10))
        
        financial_data = [
            ['Parameter', 'Wert'],
            ['Gesamtkosten', self._format_total_cost()],
            ['Amortisationszeit', self._format_payback_period()],
            ['Einsparungen (25 Jahre)', self._format_savings_25y()],
            ['CO₂-Einsparung', self._format_co2_savings()],
        ]
        
        financial_table = self._create_styled_table(financial_data)
        story.append(financial_table)
    
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
    
    def _format_system_size(self) -> str:
        size = self.calculation_data.get('system_size', 0)
        return f"{self.formatter.format(size, 2)} kWp"
    
    def _format_module_count(self) -> str:
        count = self.calculation_data.get('module_count', 0)
        return f"{count} Stück"
    
    def _format_annual_production(self) -> str:
        production = self.calculation_data.get('annual_production', 0)
        return self.formatter.format_kwh(production)
    
    def _format_self_consumption(self) -> str:
        rate = self.calculation_data.get('self_consumption_rate', 0)
        return self.formatter.format_percentage(rate)
    
    def _format_total_cost(self) -> str:
        cost = self.calculation_data.get('total_cost', 0)
        return self.formatter.format_currency(cost)
    
    def _format_payback_period(self) -> str:
        period = self.calculation_data.get('payback_period', 0)
        return self.formatter.format_years(period)
    
    def _format_savings_25y(self) -> str:
        savings = self.calculation_data.get('savings_25_years', 0)
        return self.formatter.format_currency(savings)
    
    def _format_co2_savings(self) -> str:
        co2 = self.calculation_data.get('co2_savings', 0)
        return f"{self.formatter.format(co2, 0)} kg CO₂"


class PVProductDataPDF(PDFByteMixin):
    """
    PDF generator for PV product data from database.
    """
    
    def __init__(self, product_data: Dict[str, Any]):
        super().__init__()
        self.product_data = product_data
    
    def _get_default_title(self) -> str:
        return "PV-Komponenten Datenblatt"
    
    def _get_default_subject(self) -> str:
        return "Produktinformationen"
    
    def _render_to_pdf(self, story: List, doc):
        """Render product data to PDF"""
        if not REPORTLAB_AVAILABLE:
            return
        
        styles = getSampleStyleSheet()
        
        # Title
        story.append(Paragraph(self._get_default_title(), styles['Heading1']))
        story.append(Spacer(1, 20))
        
        # Module section
        if 'module_type' in self.product_data:
            story.append(Paragraph("PV-Module", styles['Heading2']))
            story.append(Spacer(1, 10))
            
            module_data = [
                ['Eigenschaft', 'Wert'],
                ['Typ', self.product_data.get('module_type', 'N/A')],
                ['Leistung', f"{self.product_data.get('module_power', 0)} Wp"],
                ['Wirkungsgrad', f"{self.product_data.get('module_efficiency', 0)} %"],
            ]
            
            module_table = Table(module_data, colWidths=[8*cm, 8*cm])
            module_table.setStyle(self._get_table_style())
            story.append(module_table)
            story.append(Spacer(1, 20))
        
        # Inverter section
        if 'inverter_type' in self.product_data:
            story.append(Paragraph("Wechselrichter", styles['Heading2']))
            story.append(Spacer(1, 10))
            
            inverter_data = [
                ['Eigenschaft', 'Wert'],
                ['Typ', self.product_data.get('inverter_type', 'N/A')],
                ['Leistung', f"{self.product_data.get('inverter_power', 0)} kW"],
            ]
            
            inverter_table = Table(inverter_data, colWidths=[8*cm, 8*cm])
            inverter_table.setStyle(self._get_table_style())
            story.append(inverter_table)
            story.append(Spacer(1, 20))
        
        # Battery section
        if 'battery_type' in self.product_data:
            story.append(Paragraph("Batteriespeicher", styles['Heading2']))
            story.append(Spacer(1, 10))
            
            battery_data = [
                ['Eigenschaft', 'Wert'],
                ['Typ', self.product_data.get('battery_type', 'N/A')],
                ['Kapazität', f"{self.product_data.get('battery_capacity', 0)} kWh"],
            ]
            
            battery_table = Table(battery_data, colWidths=[8*cm, 8*cm])
            battery_table.setStyle(self._get_table_style())
            story.append(battery_table)
    
    def _get_table_style(self) -> TableStyle:
        """Get standard table style"""
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])


class PVChartPDF(PDFByteMixin):
    """
    PDF generator for PV charts and diagrams.
    
    Supports all 10 chart types with German formatting.
    """
    
    def __init__(
        self,
        chart_type: str,
        chart_data: Dict[str, Any],
        title: str = "Diagramm"
    ):
        super().__init__()
        self.chart_type = chart_type
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
        if self.chart_type == 'PIE':
            chart = self._create_pie_chart()
        elif self.chart_type == 'BAR':
            chart = self._create_bar_chart()
        elif self.chart_type == 'LINE':
            chart = self._create_line_chart()
        else:
            # Fallback to table
            chart = self._create_data_table()
        
        if chart:
            story.append(chart)
    
    def _create_pie_chart(self) -> Drawing:
        """Create a pie chart"""
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
        
        drawing.add(pie)
        return drawing
    
    def _create_bar_chart(self) -> Drawing:
        """Create a bar chart"""
        drawing = Drawing(400, 300)
        bc = VerticalBarChart()
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
        """Create a line chart"""
        drawing = Drawing(400, 300)
        lc = HorizontalLineChart()
        lc.x = 50
        lc.y = 50
        lc.height = 200
        lc.width = 300
        
        # Get data
        data = self.chart_data.get('data', [[]])
        lc.data = data
        
        drawing.add(lc)
        return drawing
    
    def _create_data_table(self) -> Table:
        """Create a data table as fallback"""
        labels = self.chart_data.get('labels', [])
        values = self.chart_data.get('values', [])
        
        table_data = [['Kategorie', 'Wert']]
        for label, value in zip(labels, values):
            formatted_value = self.formatter.format(value, 2)
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


class PV3DVisualizationPDF(PDFByteMixin):
    """
    PDF generator for 3D visualizations.
    
    Converts 3D visualization data to PDF with images and descriptions.
    """
    
    def __init__(
        self,
        visualization_data: Dict[str, Any],
        image_path: Optional[str] = None
    ):
        super().__init__()
        self.visualization_data = visualization_data
        self.image_path = image_path
    
    def _get_default_title(self) -> str:
        return "3D-Visualisierung der PV-Anlage"
    
    def _render_to_pdf(self, story: List, doc):
        """Render 3D visualization to PDF"""
        if not REPORTLAB_AVAILABLE:
            return
        
        styles = getSampleStyleSheet()
        
        # Title
        story.append(Paragraph(self._get_default_title(), styles['Heading1']))
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
        
        # Module placement info
        if 'module_count' in self.visualization_data:
            placement_data = [
                ['Parameter', 'Wert'],
                ['Anzahl Module', str(self.visualization_data.get('module_count', 0))],
                ['Dachfläche', f"{self.visualization_data.get('roof_area', 0)} m²"],
                ['Ausrichtung', self.visualization_data.get('orientation', 'N/A')],
            ]
            
            placement_table = Table(placement_data, colWidths=[8*cm, 8*cm])
            placement_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(placement_table)


class GermanNumberFormatter:
    """German number formatter (duplicate for convenience)"""
    
    @staticmethod
    def format(value: float, decimals: int = 2) -> str:
        formatted = f"{value:,.{decimals}f}"
        return formatted.replace(',', 'X').replace('.', ',').replace('X', '.')
    
    @staticmethod
    def format_currency(value: float) -> str:
        formatted = GermanNumberFormatter.format(value, 2)
        return f"{formatted} €"
    
    @staticmethod
    def format_kwh(value: float) -> str:
        formatted = GermanNumberFormatter.format(value, 2)
        return f"{formatted} kWh"
    
    @staticmethod
    def format_percentage(value: float) -> str:
        formatted = GermanNumberFormatter.format(value, 2)
        return f"{formatted} %"
    
    @staticmethod
    def format_years(value: float) -> str:
        formatted = GermanNumberFormatter.format(value, 1)
        return f"{formatted} Jahre"


class PVPDFBytesGenerator:
    """
    Main generator for all PV PDF bytes.
    
    This class provides a unified interface for generating PDF bytes
    for all PV-related data types.
    """
    
    def __init__(self):
        self.formatter = GermanNumberFormatter()
    
    def generate_calculation_pdf(
        self,
        calculation_data: Dict[str, Any],
        metadata: Optional[PDFMetadata] = None
    ) -> bytes:
        """
        Generate PDF bytes for calculation results.
        
        Args:
            calculation_data: Calculation results
            metadata: Optional PDF metadata
            
        Returns:
            PDF bytes
        """
        pdf_gen = PVCalculationResultPDF(calculation_data)
        return pdf_gen.to_pdf_bytes(metadata)
    
    def generate_product_pdf(
        self,
        product_data: Dict[str, Any],
        metadata: Optional[PDFMetadata] = None
    ) -> bytes:
        """
        Generate PDF bytes for product data.
        
        Args:
            product_data: Product information
            metadata: Optional PDF metadata
            
        Returns:
            PDF bytes
        """
        pdf_gen = PVProductDataPDF(product_data)
        return pdf_gen.to_pdf_bytes(metadata)
    
    def generate_chart_pdf(
        self,
        chart_type: str,
        chart_data: Dict[str, Any],
        title: str = "Diagramm",
        metadata: Optional[PDFMetadata] = None
    ) -> bytes:
        """
        Generate PDF bytes for charts.
        
        Args:
            chart_type: Type of chart (PIE, BAR, LINE, etc.)
            chart_data: Chart data
            title: Chart title
            metadata: Optional PDF metadata
            
        Returns:
            PDF bytes
        """
        pdf_gen = PVChartPDF(chart_type, chart_data, title)
        return pdf_gen.to_pdf_bytes(metadata)
    
    def generate_3d_visualization_pdf(
        self,
        visualization_data: Dict[str, Any],
        image_path: Optional[str] = None,
        metadata: Optional[PDFMetadata] = None
    ) -> bytes:
        """
        Generate PDF bytes for 3D visualizations.
        
        Args:
            visualization_data: Visualization data
            image_path: Optional path to visualization image
            metadata: Optional PDF metadata
            
        Returns:
            PDF bytes
        """
        pdf_gen = PV3DVisualizationPDF(visualization_data, image_path)
        return pdf_gen.to_pdf_bytes(metadata)
    
    def generate_combined_pdf(
        self,
        calculation_data: Dict[str, Any],
        product_data: Dict[str, Any],
        chart_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[PDFMetadata] = None
    ) -> bytes:
        """
        Generate combined PDF with all data types.
        
        Args:
            calculation_data: Calculation results
            product_data: Product information
            chart_data: Optional chart data
            metadata: Optional PDF metadata
            
        Returns:
            PDF bytes
        """
        # This would combine multiple PDF generators
        # For now, return calculation PDF
        return self.generate_calculation_pdf(calculation_data, metadata)


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize generator
    generator = PVPDFBytesGenerator()
    
    # Sample calculation data
    calculation_data = {
        'system_size': 10.5,
        'module_count': 30,
        'annual_production': 12500.0,
        'self_consumption_rate': 85.5,
        'payback_period': 12.5,
        'total_cost': 16999.00,
        'savings_25_years': 45000.00,
        'co2_savings': 125000.0
    }
    
    # Generate PDF
    pdf_bytes = generator.generate_calculation_pdf(calculation_data)
    
    # Save to file
    output_path = "test_pv_calculation.pdf"
    with open(output_path, 'wb') as f:
        f.write(pdf_bytes)
    
    logger.info(f"PDF generated: {output_path} ({len(pdf_bytes)} bytes)")
    
    # Sample product data
    product_data = {
        'module_type': 'Trina Solar TSM-400W',
        'module_power': 400,
        'module_efficiency': 20.5,
        'inverter_type': 'SMA Sunny Tripower 10.0',
        'inverter_power': 10.0,
        'battery_type': 'BYD Battery-Box Premium HVS 10.2',
        'battery_capacity': 10.2
    }
    
    # Generate product PDF
    product_pdf_bytes = generator.generate_product_pdf(product_data)
    
    # Save to file
    product_output_path = "test_pv_products.pdf"
    with open(product_output_path, 'wb') as f:
        f.write(product_pdf_bytes)
    
    logger.info(f"Product PDF generated: {product_output_path} ({len(product_pdf_bytes)} bytes)")
