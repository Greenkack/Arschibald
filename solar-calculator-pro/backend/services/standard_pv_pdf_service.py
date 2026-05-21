"""
Standard PV PDF Template System Service

This service handles the generation of standard 8-page PV PDF documents using
the template system from pdf_templates_static/notext/ and coordinates from coords/.

Author: Kiro AI
Date: 2025-01-22
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from io import BytesIO

try:
    from pypdf import PdfReader, PdfWriter
    PYPDF_AVAILABLE = True
except ImportError:
    try:
        from PyPDF2 import PdfReader, PdfWriter
        PYPDF_AVAILABLE = True
    except ImportError:
        PYPDF_AVAILABLE = False

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.colors import HexColor
    from reportlab.lib.units import mm
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

logger = logging.getLogger(__name__)


class YMLCoordinateParser:
    """Parser for YML coordinate files"""
    
    @staticmethod
    def parse_yml_file(yml_path: str) -> List[Dict[str, Any]]:
        """
        Parse a YML coordinate file and extract text positioning data.
        
        Args:
            yml_path: Path to the YML file
            
        Returns:
            List of dictionaries containing text elements with their properties
        """
        try:
            with open(yml_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse the custom YML format (not standard YAML)
            elements = []
            blocks = content.split('----------------------------------------')
            
            for block in blocks:
                if not block.strip():
                    continue
                    
                element = {}
                lines = block.strip().split('\n')
                
                for line in lines:
                    if ':' not in line:
                        continue
                        
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key == 'Text':
                        element['text'] = value
                    elif key == 'Position':
                        # Parse position tuple (x1, y1, x2, y2)
                        coords = value.strip('()').split(',')
                        if len(coords) == 4:
                            element['position'] = {
                                'x': float(coords[0]),
                                'y': float(coords[1]),
                                'x2': float(coords[2]),
                                'y2': float(coords[3])
                            }
                    elif key == 'Schriftart':
                        element['font'] = value
                    elif key == 'Schriftgröße':
                        element['font_size'] = float(value)
                    elif key == 'Farbe':
                        element['color'] = int(value)
                
                if element:
                    elements.append(element)
            
            return elements
            
        except Exception as e:
            logger.error(f"Error parsing YML file {yml_path}: {e}")
            return []
    
    @staticmethod
    def color_int_to_hex(color_int: int) -> str:
        """
        Convert integer color to hex color string.
        
        Args:
            color_int: Integer representation of color
            
        Returns:
            Hex color string (e.g., '#FF0000')
        """
        # Convert integer to RGB
        r = (color_int >> 16) & 0xFF
        g = (color_int >> 8) & 0xFF
        b = color_int & 0xFF
        return f'#{r:02X}{g:02X}{b:02X}'


class TemplateLoader:
    """Loader for PDF templates"""
    
    def __init__(self, template_dir: str = "pdf_templates_static/notext"):
        self.template_dir = Path(template_dir)
        
    def load_template(self, page_number: int) -> Optional[bytes]:
        """
        Load a template PDF for a specific page.
        
        Args:
            page_number: Page number (1-8)
            
        Returns:
            PDF bytes or None if not found
        """
        template_path = self.template_dir / f"nt_nt_{page_number:02d}.pdf"
        
        if not template_path.exists():
            logger.error(f"Template not found: {template_path}")
            return None
            
        try:
            with open(template_path, 'rb') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error loading template {template_path}: {e}")
            return None
    
    def get_all_templates(self) -> Dict[int, bytes]:
        """
        Load all 8 page templates.
        
        Returns:
            Dictionary mapping page numbers to PDF bytes
        """
        templates = {}
        for page_num in range(1, 9):
            template_bytes = self.load_template(page_num)
            if template_bytes:
                templates[page_num] = template_bytes
        return templates


class PlaceholderSystem:
    """System for managing static and dynamic placeholders"""
    
    # Static placeholders that appear in templates
    STATIC_PLACEHOLDERS = {
        'ERSTELLT FÜR:': 'ERSTELLT FÜR:',
        'aus': 'aus',
        'PHOTOVOLTAIK': 'PHOTOVOLTAIK',
        'ANGEBOT': 'ANGEBOT',
        'erstellt am:': 'erstellt am:',
        'Angebotsnummer:': 'Angebotsnummer:',
    }
    
    # Dynamic placeholders that get replaced with actual data
    DYNAMIC_PLACEHOLDERS = [
        'anrede_kunde',
        'kunde_vorname_und_nachname',
        'kunde_wohnort',
        'kWp_anlage_anlage',
        'langes_datum_heute',
    ]
    
    @staticmethod
    def is_dynamic_placeholder(text: str) -> bool:
        """Check if a text element is a dynamic placeholder"""
        return text in PlaceholderSystem.DYNAMIC_PLACEHOLDERS
    
    @staticmethod
    def is_static_placeholder(text: str) -> bool:
        """Check if a text element is a static placeholder"""
        return text in PlaceholderSystem.STATIC_PLACEHOLDERS
    
    @staticmethod
    def replace_placeholder(placeholder: str, data: Dict[str, Any]) -> str:
        """
        Replace a placeholder with actual data.
        
        Args:
            placeholder: Placeholder name
            data: Dictionary containing the actual values
            
        Returns:
            Replaced value or original placeholder if not found
        """
        if placeholder in data:
            return str(data[placeholder])
        return placeholder


class PositioningEngine:
    """Engine for positioning text elements on PDF pages"""
    
    def __init__(self):
        self.page_width, self.page_height = A4
        
    def create_overlay(
        self,
        elements: List[Dict[str, Any]],
        data: Dict[str, Any]
    ) -> bytes:
        """
        Create a PDF overlay with positioned text elements.
        
        Args:
            elements: List of text elements with positioning data
            data: Dictionary containing values for dynamic placeholders
            
        Returns:
            PDF bytes of the overlay
        """
        if not REPORTLAB_AVAILABLE:
            logger.error("ReportLab not available")
            return b''
            
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        
        for element in elements:
            text = element.get('text', '')
            position = element.get('position')
            font = element.get('font', 'Helvetica')
            font_size = element.get('font_size', 11)
            color_int = element.get('color', 0)
            
            if not position or not text:
                continue
            
            # Replace dynamic placeholders
            if PlaceholderSystem.is_dynamic_placeholder(text):
                text = PlaceholderSystem.replace_placeholder(text, data)
            
            # Skip empty text
            if not text or text.strip() == '':
                continue
            
            # Convert color
            try:
                color_hex = YMLCoordinateParser.color_int_to_hex(color_int)
                color = HexColor(color_hex)
            except:
                color = HexColor('#000000')
            
            # Set font and color
            try:
                c.setFont(font, font_size)
                c.setFillColor(color)
            except:
                c.setFont('Helvetica', font_size)
                c.setFillColor(HexColor('#000000'))
            
            # Draw text at position
            # Note: PDF coordinates are from bottom-left, YML might be from top-left
            x = position['x']
            y = self.page_height - position['y']  # Convert from top-left to bottom-left
            
            c.drawString(x, y, text)
        
        c.save()
        buffer.seek(0)
        return buffer.read()
    
    def merge_overlay_with_template(
        self,
        template_bytes: bytes,
        overlay_bytes: bytes
    ) -> bytes:
        """
        Merge an overlay PDF with a template PDF.
        
        Args:
            template_bytes: Template PDF bytes
            overlay_bytes: Overlay PDF bytes
            
        Returns:
            Merged PDF bytes
        """
        if not PYPDF_AVAILABLE:
            logger.error("PyPDF not available")
            return template_bytes
            
        try:
            template_pdf = PdfReader(BytesIO(template_bytes))
            overlay_pdf = PdfReader(BytesIO(overlay_bytes))
            
            writer = PdfWriter()
            
            # Merge first page of template with first page of overlay
            template_page = template_pdf.pages[0]
            overlay_page = overlay_pdf.pages[0]
            
            template_page.merge_page(overlay_page)
            writer.add_page(template_page)
            
            output = BytesIO()
            writer.write(output)
            output.seek(0)
            return output.read()
            
        except Exception as e:
            logger.error(f"Error merging overlay with template: {e}")
            return template_bytes


class StandardPVPDFService:
    """
    Main service for generating standard 8-page PV PDF documents.
    
    This service orchestrates the entire PDF generation process:
    1. Load YML coordinates for all 8 pages
    2. Load PDF templates for all 8 pages
    3. Replace placeholders with actual data
    4. Position elements on each page
    5. Merge overlays with templates
    6. Combine all pages into final PDF
    """
    
    def __init__(
        self,
        template_dir: str = "pdf_templates_static/notext",
        coords_dir: str = "coords"
    ):
        self.template_loader = TemplateLoader(template_dir)
        self.coords_dir = Path(coords_dir)
        self.positioning_engine = PositioningEngine()
        
    def load_page_coordinates(self, page_number: int) -> List[Dict[str, Any]]:
        """
        Load coordinates for a specific page.
        
        Args:
            page_number: Page number (1-8)
            
        Returns:
            List of text elements with positioning data
        """
        yml_path = self.coords_dir / f"seite{page_number}.yml"
        
        if not yml_path.exists():
            logger.warning(f"Coordinates file not found: {yml_path}")
            return []
            
        return YMLCoordinateParser.parse_yml_file(str(yml_path))
    
    def generate_page(
        self,
        page_number: int,
        data: Dict[str, Any]
    ) -> Optional[bytes]:
        """
        Generate a single PDF page with data.
        
        Args:
            page_number: Page number (1-8)
            data: Dictionary containing values for placeholders
            
        Returns:
            PDF bytes for the page or None if generation failed
        """
        # Load template
        template_bytes = self.template_loader.load_template(page_number)
        if not template_bytes:
            return None
        
        # Load coordinates
        elements = self.load_page_coordinates(page_number)
        if not elements:
            logger.warning(f"No coordinates found for page {page_number}, using template only")
            return template_bytes
        
        # Create overlay with positioned text
        overlay_bytes = self.positioning_engine.create_overlay(elements, data)
        
        # Merge overlay with template
        merged_bytes = self.positioning_engine.merge_overlay_with_template(
            template_bytes,
            overlay_bytes
        )
        
        return merged_bytes
    
    def generate_complete_pdf(
        self,
        data: Dict[str, Any],
        include_pages: Optional[List[int]] = None
    ) -> bytes:
        """
        Generate complete 8-page PDF document.
        
        Args:
            data: Dictionary containing all values for placeholders
            include_pages: Optional list of page numbers to include (default: all 8 pages)
            
        Returns:
            Complete PDF bytes
        """
        if include_pages is None:
            include_pages = list(range(1, 9))
        
        if not PYPDF_AVAILABLE:
            logger.error("PyPDF not available, cannot generate PDF")
            return b''
        
        writer = PdfWriter()
        
        for page_num in include_pages:
            page_bytes = self.generate_page(page_num, data)
            if page_bytes:
                try:
                    page_pdf = PdfReader(BytesIO(page_bytes))
                    writer.add_page(page_pdf.pages[0])
                except Exception as e:
                    logger.error(f"Error adding page {page_num}: {e}")
        
        output = BytesIO()
        writer.write(output)
        output.seek(0)
        return output.read()
    
    def generate_pdf_with_german_formatting(
        self,
        calculation_data: Dict[str, Any],
        customer_data: Dict[str, Any],
        pricing_data: Dict[str, Any]
    ) -> bytes:
        """
        Generate PDF with German number formatting for prices.
        
        Args:
            calculation_data: Solar calculation results
            customer_data: Customer information
            pricing_data: Pricing information with German formatting
            
        Returns:
            Complete PDF bytes
        """
        # Merge all data
        data = {
            **customer_data,
            **calculation_data,
            **pricing_data
        }
        
        # Format prices with German formatting (e.g., 16.999,00 €)
        if 'total_price' in data and isinstance(data['total_price'], (int, float)):
            data['total_price'] = self._format_german_currency(data['total_price'])
        
        return self.generate_complete_pdf(data)
    
    @staticmethod
    def _format_german_currency(amount: float) -> str:
        """
        Format currency amount in German format.
        
        Args:
            amount: Amount to format
            
        Returns:
            Formatted string (e.g., "16.999,00 €")
        """
        # Format with 2 decimal places
        formatted = f"{amount:,.2f}"
        # Replace comma with temporary marker
        formatted = formatted.replace(',', '|')
        # Replace dot with comma (German decimal separator)
        formatted = formatted.replace('.', ',')
        # Replace temporary marker with dot (German thousands separator)
        formatted = formatted.replace('|', '.')
        return f"{formatted} €"


# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize service
    service = StandardPVPDFService()
    
    # Sample data
    sample_data = {
        'anrede_kunde': 'Herr',
        'kunde_vorname_und_nachname': 'Max Mustermann',
        'kunde_wohnort': 'Berlin',
        'kWp_anlage_anlage': '10,5 kWp',
        'langes_datum_heute': '22. Januar 2025',
        'total_price': 16999.00
    }
    
    # Generate PDF
    pdf_bytes = service.generate_complete_pdf(sample_data)
    
    if pdf_bytes:
        # Save to file for testing
        output_path = "test_standard_pv_pdf.pdf"
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        logger.info(f"PDF generated successfully: {output_path}")
    else:
        logger.error("Failed to generate PDF")
