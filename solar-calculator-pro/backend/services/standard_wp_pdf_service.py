"""
Standard WP (Heat Pump) PDF Template System Service

This service handles the generation of standard 8-page WP PDF documents using
the template system from pdf_templates_static/notext/ and coordinates from coords_wp/.

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


class WPYMLCoordinateParser:
    """Parser for WP-specific YML coordinate files"""
    
    @staticmethod
    def parse_yml_file(yml_path: str) -> List[Dict[str, Any]]:
        """
        Parse a WP YML coordinate file and extract text positioning data.
        
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
            logger.error(f"Error parsing WP YML file {yml_path}: {e}")
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


class WPTemplateLoader:
    """Loader for WP PDF templates"""
    
    def __init__(self, template_dir: str = "pdf_templates_static/notext"):
        self.template_dir = Path(template_dir)
        
    def load_template(self, page_number: int) -> Optional[bytes]:
        """
        Load a WP template PDF for a specific page.
        
        Args:
            page_number: Page number (1-8)
            
        Returns:
            PDF bytes or None if not found
        """
        template_path = self.template_dir / f"hp_nt_{page_number:02d}.pdf"
        
        if not template_path.exists():
            logger.error(f"WP Template not found: {template_path}")
            return None
            
        try:
            with open(template_path, 'rb') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error loading WP template {template_path}: {e}")
            return None
    
    def get_all_templates(self) -> Dict[int, bytes]:
        """
        Load all 8 WP page templates.
        
        Returns:
            Dictionary mapping page numbers to PDF bytes
        """
        templates = {}
        for page_num in range(1, 9):
            template_bytes = self.load_template(page_num)
            if template_bytes:
                templates[page_num] = template_bytes
        return templates


class WPPlaceholderSystem:
    """System for managing WP-specific static and dynamic placeholders"""
    
    # Static placeholders that appear in WP templates
    STATIC_PLACEHOLDERS = {
        'ERSTELLT FÜR:': 'ERSTELLT FÜR:',
        'aus': 'aus',
        'WÄRMEPUMPE': 'WÄRMEPUMPE',
        'ANGEBOT': 'ANGEBOT',
        'erstellt am:': 'erstellt am:',
        'Angebotsnummer:': 'Angebotsnummer:',
        'COP-Wert:': 'COP-Wert:',
        'Heizkosten:': 'Heizkosten:',
        'Effizienz:': 'Effizienz:',
        'Vergleich:': 'Vergleich:',
    }
    
    # Dynamic placeholders specific to heat pump calculations
    DYNAMIC_PLACEHOLDERS = [
        'anrede_kunde',
        'kunde_vorname_und_nachname',
        'kunde_wohnort',
        'wp_leistung_kw',
        'wp_cop_wert',
        'wp_jahresarbeitszahl',
        'wp_heizkosten_jahr',
        'wp_heizkosten_monat',
        'wp_einsparung_jahr',
        'wp_einsparung_prozent',
        'wp_amortisationszeit',
        'wp_co2_einsparung',
        'wp_effizienzklasse',
        'wp_vorlauftemperatur',
        'wp_heizlast_kw',
        'wp_warmwasser_liter',
        'langes_datum_heute',
        'wp_modell_name',
        'wp_hersteller',
    ]
    
    @staticmethod
    def is_dynamic_placeholder(text: str) -> bool:
        """Check if a text element is a dynamic placeholder"""
        return text in WPPlaceholderSystem.DYNAMIC_PLACEHOLDERS
    
    @staticmethod
    def is_static_placeholder(text: str) -> bool:
        """Check if a text element is a static placeholder"""
        return text in WPPlaceholderSystem.STATIC_PLACEHOLDERS
    
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


class WPPositioningEngine:
    """Engine for positioning text elements on WP PDF pages"""
    
    def __init__(self):
        self.page_width, self.page_height = A4
        
    def create_overlay(
        self,
        elements: List[Dict[str, Any]],
        data: Dict[str, Any]
    ) -> bytes:
        """
        Create a PDF overlay with positioned text elements for WP.
        
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
            if WPPlaceholderSystem.is_dynamic_placeholder(text):
                text = WPPlaceholderSystem.replace_placeholder(text, data)
            
            # Skip empty text
            if not text or text.strip() == '':
                continue
            
            # Convert color
            try:
                color_hex = WPYMLCoordinateParser.color_int_to_hex(color_int)
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
        Merge an overlay PDF with a WP template PDF.
        
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
            logger.error(f"Error merging WP overlay with template: {e}")
            return template_bytes


class StandardWPPDFService:
    """
    Main service for generating standard 8-page WP (Heat Pump) PDF documents.
    
    This service orchestrates the entire WP PDF generation process:
    1. Load YML coordinates for all 8 pages from coords_wp/
    2. Load PDF templates for all 8 pages (hp_nt_01.pdf to hp_nt_08.pdf)
    3. Replace placeholders with actual WP calculation data
    4. Position elements on each page
    5. Merge overlays with templates
    6. Combine all pages into final PDF
    
    Content includes:
    - WP-specific calculations (COP values, heating costs, efficiency)
    - Comparison charts
    - Technical specifications
    - Cost analysis
    - Environmental impact
    """
    
    def __init__(
        self,
        template_dir: str = "pdf_templates_static/notext",
        coords_dir: str = "coords_wp"
    ):
        self.template_loader = WPTemplateLoader(template_dir)
        self.coords_dir = Path(coords_dir)
        self.positioning_engine = WPPositioningEngine()
        
    def load_page_coordinates(self, page_number: int) -> List[Dict[str, Any]]:
        """
        Load WP coordinates for a specific page.
        
        Args:
            page_number: Page number (1-8)
            
        Returns:
            List of text elements with positioning data
        """
        yml_path = self.coords_dir / f"wp_seite{page_number}.yml"
        
        if not yml_path.exists():
            logger.warning(f"WP Coordinates file not found: {yml_path}")
            return []
            
        return WPYMLCoordinateParser.parse_yml_file(str(yml_path))
    
    def generate_page(
        self,
        page_number: int,
        data: Dict[str, Any]
    ) -> Optional[bytes]:
        """
        Generate a single WP PDF page with data.
        
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
            logger.warning(f"No WP coordinates found for page {page_number}, using template only")
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
        Generate complete 8-page WP PDF document.
        
        Args:
            data: Dictionary containing all values for placeholders
            include_pages: Optional list of page numbers to include (default: all 8 pages)
            
        Returns:
            Complete PDF bytes
        """
        if include_pages is None:
            include_pages = list(range(1, 9))
        
        if not PYPDF_AVAILABLE:
            logger.error("PyPDF not available, cannot generate WP PDF")
            return b''
        
        writer = PdfWriter()
        
        for page_num in include_pages:
            page_bytes = self.generate_page(page_num, data)
            if page_bytes:
                try:
                    page_pdf = PdfReader(BytesIO(page_bytes))
                    writer.add_page(page_pdf.pages[0])
                except Exception as e:
                    logger.error(f"Error adding WP page {page_num}: {e}")
        
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
        Generate WP PDF with German number formatting for prices and values.
        
        Args:
            calculation_data: Heat pump calculation results
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
        
        # Format heating costs
        if 'wp_heizkosten_jahr' in data and isinstance(data['wp_heizkosten_jahr'], (int, float)):
            data['wp_heizkosten_jahr'] = self._format_german_currency(data['wp_heizkosten_jahr'])
        
        if 'wp_heizkosten_monat' in data and isinstance(data['wp_heizkosten_monat'], (int, float)):
            data['wp_heizkosten_monat'] = self._format_german_currency(data['wp_heizkosten_monat'])
        
        # Format savings
        if 'wp_einsparung_jahr' in data and isinstance(data['wp_einsparung_jahr'], (int, float)):
            data['wp_einsparung_jahr'] = self._format_german_currency(data['wp_einsparung_jahr'])
        
        # Format COP value
        if 'wp_cop_wert' in data and isinstance(data['wp_cop_wert'], (int, float)):
            data['wp_cop_wert'] = self._format_german_decimal(data['wp_cop_wert'])
        
        # Format JAZ (Jahresarbeitszahl)
        if 'wp_jahresarbeitszahl' in data and isinstance(data['wp_jahresarbeitszahl'], (int, float)):
            data['wp_jahresarbeitszahl'] = self._format_german_decimal(data['wp_jahresarbeitszahl'])
        
        # Format power values
        if 'wp_leistung_kw' in data and isinstance(data['wp_leistung_kw'], (int, float)):
            data['wp_leistung_kw'] = f"{self._format_german_decimal(data['wp_leistung_kw'])} kW"
        
        if 'wp_heizlast_kw' in data and isinstance(data['wp_heizlast_kw'], (int, float)):
            data['wp_heizlast_kw'] = f"{self._format_german_decimal(data['wp_heizlast_kw'])} kW"
        
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
    
    @staticmethod
    def _format_german_decimal(value: float, decimals: int = 2) -> str:
        """
        Format decimal value in German format.
        
        Args:
            value: Value to format
            decimals: Number of decimal places
            
        Returns:
            Formatted string (e.g., "4,5" or "3.500,25")
        """
        # Format with specified decimal places
        formatted = f"{value:,.{decimals}f}"
        # Replace comma with temporary marker
        formatted = formatted.replace(',', '|')
        # Replace dot with comma (German decimal separator)
        formatted = formatted.replace('.', ',')
        # Replace temporary marker with dot (German thousands separator)
        formatted = formatted.replace('|', '.')
        return formatted


# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize service
    service = StandardWPPDFService()
    
    # Sample WP data
    sample_data = {
        'anrede_kunde': 'Herr',
        'kunde_vorname_und_nachname': 'Max Mustermann',
        'kunde_wohnort': 'Berlin',
        'wp_leistung_kw': 12.5,
        'wp_cop_wert': 4.5,
        'wp_jahresarbeitszahl': 4.2,
        'wp_heizkosten_jahr': 1250.00,
        'wp_heizkosten_monat': 104.17,
        'wp_einsparung_jahr': 2500.00,
        'wp_einsparung_prozent': '66,7%',
        'wp_amortisationszeit': '8 Jahre',
        'wp_co2_einsparung': '4.500 kg/Jahr',
        'wp_effizienzklasse': 'A+++',
        'wp_vorlauftemperatur': '35°C',
        'wp_heizlast_kw': 10.0,
        'wp_warmwasser_liter': 300,
        'langes_datum_heute': '22. Januar 2025',
        'wp_modell_name': 'Viessmann Vitocal 200-S',
        'wp_hersteller': 'Viessmann',
        'total_price': 18999.00
    }
    
    # Generate PDF
    pdf_bytes = service.generate_pdf_with_german_formatting(
        calculation_data=sample_data,
        customer_data=sample_data,
        pricing_data=sample_data
    )
    
    if pdf_bytes:
        # Save to file for testing
        output_path = "test_standard_wp_pdf.pdf"
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        logger.info(f"WP PDF generated successfully: {output_path}")
    else:
        logger.error("Failed to generate WP PDF")
