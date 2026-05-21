"""
Extended WP (Heat Pump) PDF Service with Optional Additional Pages

This service extends the standard 8-page WP PDF with optional additional pages (9+)
that can be dynamically activated based on user selection. Additional pages can include:
- Detailed WP calculations (COP, JAZ, heating costs)
- Additional WP-specific diagrams
- Heat pump product datasheets from database
- WP documents from database (individual per product)
- WP images from database (dynamic)
- Extended WP visualizations

Author: Kiro AI
Date: 2025-01-22
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from io import BytesIO
from dataclasses import dataclass
from enum import Enum

try:
    from pypdf import PdfReader, PdfWriter
    PYPDF_AVAILABLE = True
except ImportError:
    try:
        from PyPDF2 import PdfReader, PdfWriter
        PYPDF_AVAILABLE = True
    except ImportError:
        PYPDF_AVAILABLE = False

from .standard_wp_pdf_service import (
    StandardWPPDFService,
    WPYMLCoordinateParser,
    WPTemplateLoader,
    WPPositioningEngine,
    WPPlaceholderSystem
)

logger = logging.getLogger(__name__)


class WPComponentType(Enum):
    """Types of WP-specific components that can be added to extended PDF"""
    DETAILED_WP_CALCULATION = "detailed_wp_calculation"
    ADDITIONAL_WP_DIAGRAM = "additional_wp_diagram"
    WP_PRODUCT_DATASHEET = "wp_product_datasheet"
    WP_DOCUMENT = "wp_document"
    WP_IMAGE = "wp_image"
    EXTENDED_WP_VISUALIZATION = "extended_wp_visualization"


@dataclass
class ExtendedWPPageConfig:
    """Configuration for an extended WP page"""
    page_number: int  # Page number (9+)
    component_type: WPComponentType
    component_id: Optional[str] = None  # ID for database lookup
    title: Optional[str] = None
    enabled: bool = True


@dataclass
class WPComponentSelection:
    """User's selection of WP components to include in extended PDF"""
    include_detailed_wp_calculations: bool = False
    include_additional_wp_diagrams: bool = False
    include_wp_product_datasheets: bool = False
    include_wp_documents: bool = False
    include_wp_images: bool = False
    include_extended_wp_visualizations: bool = False
    
    # Specific WP selections
    selected_wp_diagram_types: List[str] = None
    selected_wp_product_ids: List[str] = None
    selected_wp_document_ids: List[str] = None
    selected_wp_image_ids: List[str] = None
    
    def __post_init__(self):
        if self.selected_wp_diagram_types is None:
            self.selected_wp_diagram_types = []
        if self.selected_wp_product_ids is None:
            self.selected_wp_product_ids = []
        if self.selected_wp_document_ids is None:
            self.selected_wp_document_ids = []
        if self.selected_wp_image_ids is None:
            self.selected_wp_image_ids = []


class ExtendedWPTemplateLoader(WPTemplateLoader):
    """Extended template loader for WP pages 9+"""
    
    def load_extended_wp_template(self, page_number: int) -> Optional[bytes]:
        """
        Load an extended WP template PDF for pages 9+.
        
        Args:
            page_number: Page number (9+)
            
        Returns:
            PDF bytes or None if not found
        """
        # Extended WP templates use the same naming convention
        template_path = self.template_dir / f"hp_nt_{page_number:02d}.pdf"
        
        if not template_path.exists():
            # Try generic extended WP template
            template_path = self.template_dir / "hp_nt_extended.pdf"
            
        if not template_path.exists():
            logger.warning(f"Extended WP template not found for page {page_number}")
            return None
            
        try:
            with open(template_path, 'rb') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error loading extended WP template {template_path}: {e}")
            return None


class WPDatasheetIntegration:
    """Integration with product database for WP datasheets"""
    
    def __init__(self, database_service=None):
        self.database_service = database_service
        
    def get_wp_product_datasheet(self, product_id: str) -> Optional[bytes]:
        """
        Retrieve WP product datasheet from database.
        
        Args:
            product_id: WP Product ID
            
        Returns:
            PDF bytes of datasheet or None
        """
        if not self.database_service:
            logger.warning("Database service not available")
            return None
            
        try:
            # Query database for WP product datasheet
            datasheet = self.database_service.get_wp_product_datasheet(product_id)
            
            if datasheet and 'pdf_bytes' in datasheet:
                return datasheet['pdf_bytes']
            
            logger.warning(f"No WP datasheet found for product {product_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving WP datasheet for product {product_id}: {e}")
            return None
    
    def get_all_wp_product_datasheets(self, product_ids: List[str]) -> Dict[str, bytes]:
        """
        Retrieve multiple WP product datasheets.
        
        Args:
            product_ids: List of WP product IDs
            
        Returns:
            Dictionary mapping product IDs to PDF bytes
        """
        datasheets = {}
        for product_id in product_ids:
            datasheet_bytes = self.get_wp_product_datasheet(product_id)
            if datasheet_bytes:
                datasheets[product_id] = datasheet_bytes
        return datasheets



class WPDocumentIntegration:
    """Integration with database for WP documents"""
    
    def __init__(self, database_service=None):
        self.database_service = database_service
        
    def get_wp_document(self, document_id: str) -> Optional[bytes]:
        """
        Retrieve WP document from database.
        
        Args:
            document_id: Document ID
            
        Returns:
            PDF bytes of document or None
        """
        if not self.database_service:
            logger.warning("Database service not available")
            return None
            
        try:
            # Query database for WP document
            document = self.database_service.get_wp_document(document_id)
            
            if document and 'pdf_bytes' in document:
                return document['pdf_bytes']
            
            logger.warning(f"No WP document found with ID {document_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving WP document {document_id}: {e}")
            return None
    
    def get_wp_product_documents(self, product_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve all documents associated with a WP product.
        
        Args:
            product_id: WP Product ID
            
        Returns:
            List of document metadata dictionaries
        """
        if not self.database_service:
            return []
            
        try:
            return self.database_service.get_wp_product_documents(product_id)
        except Exception as e:
            logger.error(f"Error retrieving WP documents for product {product_id}: {e}")
            return []


class WPImageIntegration:
    """Integration with database for WP images"""
    
    def __init__(self, database_service=None):
        self.database_service = database_service
        
    def get_wp_image(self, image_id: str) -> Optional[bytes]:
        """
        Retrieve WP image from database and convert to PDF.
        
        Args:
            image_id: Image ID
            
        Returns:
            PDF bytes containing the image or None
        """
        if not self.database_service:
            logger.warning("Database service not available")
            return None
            
        try:
            # Query database for WP image
            image = self.database_service.get_wp_image(image_id)
            
            if image and 'image_bytes' in image:
                # Convert image to PDF
                return self._image_to_pdf(image['image_bytes'])
            
            logger.warning(f"No WP image found with ID {image_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving WP image {image_id}: {e}")
            return None
    
    def _image_to_pdf(self, image_bytes: bytes) -> bytes:
        """
        Convert image bytes to PDF.
        
        Args:
            image_bytes: Image data
            
        Returns:
            PDF bytes containing the image
        """
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.utils import ImageReader
            from PIL import Image
            
            # Load image
            img = Image.open(BytesIO(image_bytes))
            
            # Create PDF
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            
            # Calculate dimensions to fit on page
            page_width, page_height = A4
            img_width, img_height = img.size
            
            # Scale image to fit page with margins
            margin = 50
            max_width = page_width - 2 * margin
            max_height = page_height - 2 * margin
            
            scale = min(max_width / img_width, max_height / img_height)
            scaled_width = img_width * scale
            scaled_height = img_height * scale
            
            # Center image on page
            x = (page_width - scaled_width) / 2
            y = (page_height - scaled_height) / 2
            
            # Draw image
            img_reader = ImageReader(BytesIO(image_bytes))
            c.drawImage(img_reader, x, y, scaled_width, scaled_height)
            
            c.save()
            buffer.seek(0)
            return buffer.read()
            
        except Exception as e:
            logger.error(f"Error converting WP image to PDF: {e}")
            return b''



class ExtendedWPCalculationGenerator:
    """Generator for extended WP calculation pages"""
    
    def __init__(self, positioning_engine: WPPositioningEngine):
        self.positioning_engine = positioning_engine
        
    def generate_detailed_wp_calculation_page(
        self,
        calculation_data: Dict[str, Any],
        template_bytes: bytes
    ) -> bytes:
        """
        Generate a page with detailed WP calculations.
        
        Args:
            calculation_data: Detailed WP calculation results
            template_bytes: Template PDF bytes
            
        Returns:
            PDF bytes with WP calculations
        """
        # Create overlay with WP calculation details
        elements = self._create_wp_calculation_elements(calculation_data)
        overlay_bytes = self.positioning_engine.create_overlay(elements, calculation_data)
        
        # Merge with template
        return self.positioning_engine.merge_overlay_with_template(
            template_bytes,
            overlay_bytes
        )
    
    def _create_wp_calculation_elements(
        self,
        calculation_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Create text elements for detailed WP calculations.
        
        Args:
            calculation_data: WP calculation data
            
        Returns:
            List of text elements with positioning
        """
        elements = []
        
        # Title
        elements.append({
            'text': 'Detaillierte Wärmepumpen-Berechnungen',
            'position': {'x': 50, 'y': 50, 'x2': 550, 'y2': 70},
            'font': 'Helvetica-Bold',
            'font_size': 16,
            'color': 0x000000
        })
        
        # WP-specific calculation details
        y_offset = 100
        wp_keys = [
            'wp_cop_wert', 'wp_jahresarbeitszahl', 'wp_heizkosten_jahr',
            'wp_heizkosten_monat', 'wp_einsparung_jahr', 'wp_vorlauftemperatur',
            'wp_heizlast_kw', 'wp_warmwasser_liter', 'wp_effizienzklasse'
        ]
        
        for key in wp_keys:
            if key in calculation_data:
                value = calculation_data[key]
                elements.append({
                    'text': f"{key}: {value}",
                    'position': {'x': 50, 'y': y_offset, 'x2': 550, 'y2': y_offset + 20},
                    'font': 'Helvetica',
                    'font_size': 11,
                    'color': 0x000000
                })
                y_offset += 25
        
        return elements



class ExtendedWPVisualizationGenerator:
    """Generator for extended WP visualization pages"""
    
    def __init__(self, positioning_engine: WPPositioningEngine):
        self.positioning_engine = positioning_engine
        
    def generate_wp_visualization_page(
        self,
        visualization_data: Dict[str, Any],
        template_bytes: bytes
    ) -> bytes:
        """
        Generate a page with extended WP visualizations.
        
        Args:
            visualization_data: WP visualization data
            template_bytes: Template PDF bytes
            
        Returns:
            PDF bytes with WP visualizations
        """
        # This would integrate with WP visualization service
        # For now, return template with title
        elements = [{
            'text': 'Erweiterte Wärmepumpen-Visualisierungen',
            'position': {'x': 50, 'y': 50, 'x2': 550, 'y2': 70},
            'font': 'Helvetica-Bold',
            'font_size': 16,
            'color': 0x000000
        }]
        
        overlay_bytes = self.positioning_engine.create_overlay(elements, visualization_data)
        
        return self.positioning_engine.merge_overlay_with_template(
            template_bytes,
            overlay_bytes
        )


class ExtendedWPPDFService:
    """
    Service for generating extended WP (Heat Pump) PDF documents with optional additional pages.
    
    This service extends StandardWPPDFService to support:
    - Standard 8 pages (1-8) using base WP logic
    - Optional additional pages (9+) dynamically activated
    - WP component selection system
    - Database integration for WP datasheets, documents, and images
    - Dynamic page generation based on user selection
    - WP-specific content (COP, JAZ, heating costs, efficiency)
    """
    
    def __init__(
        self,
        template_dir: str = "pdf_templates_static/notext",
        coords_dir: str = "coords_wp",
        database_service=None
    ):
        # Initialize base WP service for standard pages
        self.standard_wp_service = StandardWPPDFService(template_dir, coords_dir)
        
        # Initialize extended WP components
        self.extended_wp_template_loader = ExtendedWPTemplateLoader(template_dir)
        self.coords_dir = Path(coords_dir)
        self.positioning_engine = WPPositioningEngine()
        
        # Initialize WP integrations
        self.wp_datasheet_integration = WPDatasheetIntegration(database_service)
        self.wp_document_integration = WPDocumentIntegration(database_service)
        self.wp_image_integration = WPImageIntegration(database_service)
        
        # Initialize WP generators
        self.wp_calculation_generator = ExtendedWPCalculationGenerator(self.positioning_engine)
        self.wp_visualization_generator = ExtendedWPVisualizationGenerator(self.positioning_engine)
        
    def generate_extended_wp_pdf(
        self,
        data: Dict[str, Any],
        component_selection: WPComponentSelection
    ) -> bytes:
        """
        Generate extended WP PDF with standard pages plus optional additional pages.
        
        Args:
            data: Dictionary containing all values for WP placeholders
            component_selection: User's selection of WP components to include
            
        Returns:
            Complete PDF bytes
        """
        if not PYPDF_AVAILABLE:
            logger.error("PyPDF not available, cannot generate WP PDF")
            return b''
        
        writer = PdfWriter()
        
        # Step 1: Generate standard 8 WP pages
        logger.info("Generating standard 8 WP pages...")
        standard_wp_pdf_bytes = self.standard_wp_service.generate_complete_pdf(data)
        
        if standard_wp_pdf_bytes:
            try:
                standard_wp_pdf = PdfReader(BytesIO(standard_wp_pdf_bytes))
                for page in standard_wp_pdf.pages:
                    writer.add_page(page)
                logger.info(f"Added {len(standard_wp_pdf.pages)} standard WP pages")
            except Exception as e:
                logger.error(f"Error adding standard WP pages: {e}")
                return b''
        else:
            logger.error("Failed to generate standard WP pages")
            return b''
        
        # Step 2: Generate optional additional WP pages based on selection
        current_page_number = 9
        
        # Detailed WP calculations
        if component_selection.include_detailed_wp_calculations:
            logger.info("Adding detailed WP calculations page...")
            wp_calc_page = self._generate_detailed_wp_calculations_page(
                current_page_number,
                data
            )
            if wp_calc_page:
                self._add_page_to_writer(writer, wp_calc_page)
                current_page_number += 1
        
        # Additional WP diagrams
        if component_selection.include_additional_wp_diagrams:
            logger.info("Adding additional WP diagrams...")
            for diagram_type in component_selection.selected_wp_diagram_types:
                diagram_page = self._generate_wp_diagram_page(
                    current_page_number,
                    diagram_type,
                    data
                )
                if diagram_page:
                    self._add_page_to_writer(writer, diagram_page)
                    current_page_number += 1
        
        # WP product datasheets
        if component_selection.include_wp_product_datasheets:
            logger.info("Adding WP product datasheets...")
            for product_id in component_selection.selected_wp_product_ids:
                datasheet_bytes = self.wp_datasheet_integration.get_wp_product_datasheet(product_id)
                if datasheet_bytes:
                    self._add_pdf_to_writer(writer, datasheet_bytes)
                    current_page_number += 1
        
        # WP documents
        if component_selection.include_wp_documents:
            logger.info("Adding WP documents...")
            for document_id in component_selection.selected_wp_document_ids:
                document_bytes = self.wp_document_integration.get_wp_document(document_id)
                if document_bytes:
                    self._add_pdf_to_writer(writer, document_bytes)
                    current_page_number += 1
        
        # WP images
        if component_selection.include_wp_images:
            logger.info("Adding WP images...")
            for image_id in component_selection.selected_wp_image_ids:
                image_pdf_bytes = self.wp_image_integration.get_wp_image(image_id)
                if image_pdf_bytes:
                    self._add_pdf_to_writer(writer, image_pdf_bytes)
                    current_page_number += 1
        
        # Extended WP visualizations
        if component_selection.include_extended_wp_visualizations:
            logger.info("Adding extended WP visualizations...")
            viz_page = self._generate_extended_wp_visualization_page(
                current_page_number,
                data
            )
            if viz_page:
                self._add_page_to_writer(writer, viz_page)
                current_page_number += 1
        
        # Write final WP PDF
        output = BytesIO()
        writer.write(output)
        output.seek(0)
        
        logger.info(f"Extended WP PDF generated with {current_page_number - 1} total pages")
        return output.read()
    
    def _generate_detailed_wp_calculations_page(
        self,
        page_number: int,
        data: Dict[str, Any]
    ) -> Optional[bytes]:
        """Generate detailed WP calculations page"""
        template_bytes = self.extended_wp_template_loader.load_extended_wp_template(page_number)
        if not template_bytes:
            return None
        
        return self.wp_calculation_generator.generate_detailed_wp_calculation_page(
            data,
            template_bytes
        )
    
    def _generate_wp_diagram_page(
        self,
        page_number: int,
        diagram_type: str,
        data: Dict[str, Any]
    ) -> Optional[bytes]:
        """Generate WP diagram page"""
        # This would integrate with WP chart generation service
        template_bytes = self.extended_wp_template_loader.load_extended_wp_template(page_number)
        if not template_bytes:
            return None
        
        # For now, return template with title
        elements = [{
            'text': f'WP-Diagramm: {diagram_type}',
            'position': {'x': 50, 'y': 50, 'x2': 550, 'y2': 70},
            'font': 'Helvetica-Bold',
            'font_size': 16,
            'color': 0x000000
        }]
        
        overlay_bytes = self.positioning_engine.create_overlay(elements, data)
        return self.positioning_engine.merge_overlay_with_template(
            template_bytes,
            overlay_bytes
        )
    
    def _generate_extended_wp_visualization_page(
        self,
        page_number: int,
        data: Dict[str, Any]
    ) -> Optional[bytes]:
        """Generate extended WP visualization page"""
        template_bytes = self.extended_wp_template_loader.load_extended_wp_template(page_number)
        if not template_bytes:
            return None
        
        return self.wp_visualization_generator.generate_wp_visualization_page(
            data,
            template_bytes
        )
    
    def _add_page_to_writer(self, writer: PdfWriter, page_bytes: bytes):
        """Add a single page to PDF writer"""
        try:
            page_pdf = PdfReader(BytesIO(page_bytes))
            writer.add_page(page_pdf.pages[0])
        except Exception as e:
            logger.error(f"Error adding WP page: {e}")
    
    def _add_pdf_to_writer(self, writer: PdfWriter, pdf_bytes: bytes):
        """Add all pages from a PDF to writer"""
        try:
            pdf = PdfReader(BytesIO(pdf_bytes))
            for page in pdf.pages:
                writer.add_page(page)
        except Exception as e:
            logger.error(f"Error adding WP PDF: {e}")
    
    def get_available_wp_components(
        self,
        product_ids: Optional[List[str]] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get available WP components that can be added to extended PDF.
        
        Args:
            product_ids: Optional list of WP product IDs to get specific components
            
        Returns:
            Dictionary of available WP components by type
        """
        available = {
            'wp_calculations': [
                {'id': 'detailed_cop', 'name': 'Detaillierte COP-Berechnung'},
                {'id': 'detailed_jaz', 'name': 'Detaillierte JAZ-Berechnung'},
                {'id': 'detailed_heating_costs', 'name': 'Detaillierte Heizkostenberechnung'},
                {'id': 'detailed_efficiency', 'name': 'Detaillierte Effizienzanalyse'},
            ],
            'wp_diagrams': [
                {'id': 'cop_monthly', 'name': 'Monatliche COP-Werte'},
                {'id': 'heating_cost_comparison', 'name': 'Heizkostenvergleich'},
                {'id': 'efficiency_analysis', 'name': 'Effizienzanalyse'},
                {'id': 'savings_projection', 'name': 'Einsparungsprognose'},
            ],
            'wp_datasheets': [],
            'wp_documents': [],
            'wp_images': []
        }
        
        # Get WP product-specific components if product IDs provided
        if product_ids:
            for product_id in product_ids:
                # Get WP datasheets
                datasheet = self.wp_datasheet_integration.get_wp_product_datasheet(product_id)
                if datasheet:
                    available['wp_datasheets'].append({
                        'id': product_id,
                        'name': f'WP-Datenblatt {product_id}'
                    })
                
                # Get WP documents
                documents = self.wp_document_integration.get_wp_product_documents(product_id)
                for doc in documents:
                    available['wp_documents'].append({
                        'id': doc.get('id'),
                        'name': doc.get('name', 'WP-Dokument')
                    })
        
        return available



# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize service
    service = ExtendedWPPDFService()
    
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
    
    # WP component selection
    selection = WPComponentSelection(
        include_detailed_wp_calculations=True,
        include_additional_wp_diagrams=True,
        selected_wp_diagram_types=['cop_monthly', 'heating_cost_comparison']
    )
    
    # Generate extended WP PDF
    pdf_bytes = service.generate_extended_wp_pdf(sample_data, selection)
    
    if pdf_bytes:
        output_path = "test_extended_wp_pdf.pdf"
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        logger.info(f"Extended WP PDF generated successfully: {output_path}")
    else:
        logger.error("Failed to generate extended WP PDF")
